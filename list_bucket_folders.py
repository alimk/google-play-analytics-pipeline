#!/usr/bin/env python3
"""List report folders available in a configured Google Play GCS bucket."""

import os
from google.cloud import storage

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "")
BUCKET_NAME = os.environ.get("PLAY_STATS_BUCKET", "")


def main() -> None:
    if not PROJECT_ID or not BUCKET_NAME:
        raise RuntimeError("Set GCP_PROJECT_ID and PLAY_STATS_BUCKET first.")

    client = storage.Client(project=PROJECT_ID)
    blobs = client.list_blobs(BUCKET_NAME, delimiter="/")
    _ = list(blobs)
    for prefix in sorted(blobs.prefixes):
        print(prefix)


if __name__ == "__main__":
    main()
