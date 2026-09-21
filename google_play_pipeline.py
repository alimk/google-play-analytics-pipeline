"""Portfolio demo: Google Play statistics pipeline.

Reads Google Play Console statistics exported to Google Cloud Storage,
normalizes columns, aggregates daily statistics to monthly values, and
prepares a BI-friendly summary dataset.
"""

from __future__ import annotations

import io
import os
import re

import pandas as pd
from google.cloud import storage

SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "")
BUCKET_NAME = os.environ.get("PLAY_STATS_BUCKET", "")
INSTALLS_PREFIX = os.environ.get("PLAY_INSTALLS_PREFIX", "stats/installs/")

APP_NAMES = {
    "com.example.appa": "Demo App A",
    "com.example.appb": "Demo App B",
}


def validate_config() -> None:
    required = {
        "GOOGLE_APPLICATION_CREDENTIALS": SERVICE_ACCOUNT_JSON,
        "GCP_PROJECT_ID": PROJECT_ID,
        "PLAY_STATS_BUCKET": BUCKET_NAME,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


def snake_case(name: str) -> str:
    name = name.strip().replace("%", "percent")
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name)
    return re.sub(r"_+", "_", name).strip("_").lower()


def read_csv_from_gcs(client: storage.Client, blob_name: str) -> pd.DataFrame:
    blob = client.bucket(BUCKET_NAME).blob(blob_name)
    raw = blob.download_as_bytes()
    df = pd.read_csv(io.BytesIO(raw), encoding="utf-16", dtype=str)
    df.columns = [snake_case(c) for c in df.columns]
    return df


def list_blobs(client: storage.Client, prefix: str) -> list[str]:
    return sorted(b.name for b in client.list_blobs(BUCKET_NAME, prefix=prefix) if not b.name.endswith("/"))


def parse_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    for col in df.columns:
        if col in {"date", "package_name"}:
            continue
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "", regex=False), errors="coerce")
    return df


def aggregate_installs(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "date" not in df.columns:
        return df

    df = df.copy()
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df = df.drop(columns=["total_user_installs"], errors="ignore")

    numeric_cols = [c for c in df.columns if c not in {"date", "month", "package_name"}]
    snapshot_cols = [c for c in numeric_cols if "active_device" in c]
    sum_cols = [c for c in numeric_cols if c not in snapshot_cols]

    agg = {c: "sum" for c in sum_cols}
    agg.update({c: "max" for c in snapshot_cols})

    monthly = df.groupby(["month", "package_name"], as_index=False).agg(agg)
    monthly.insert(1, "app_name", monthly["package_name"].map(APP_NAMES).fillna(monthly["package_name"]))
    monthly["month"] = monthly["month"].dt.strftime("%Y-%m")
    return monthly.sort_values(["month", "app_name"]).reset_index(drop=True)


def main() -> None:
    validate_config()
    client = storage.Client(project=PROJECT_ID)

    frames = []
    for blob_name in list_blobs(client, INSTALLS_PREFIX):
        frames.append(parse_types(read_csv_from_gcs(client, blob_name)))

    raw = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    monthly = aggregate_installs(raw)

    print(f"Loaded {len(raw):,} raw rows.")
    print(f"Produced {len(monthly):,} monthly rows.")
    print(monthly.head())


if __name__ == "__main__":
    main()
