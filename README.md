# Google Play Analytics Pipeline

A portfolio-ready Python pipeline that reads Google Play Console statistics from a Google Cloud Storage export, normalizes and aggregates the data, and prepares a monthly dataset for Power BI or other BI tools.

## What this demonstrates

- Google Cloud Storage integration with a service account
- Google Play Console statistics export processing
- Automated CSV ingestion
- Data cleaning and type conversion with pandas
- Monthly aggregation logic
- BI-ready dataset preparation
- Secure environment-based configuration

## Architecture

```text
Google Play Console statistics export
        ↓
Google Cloud Storage
        ↓
Python ingestion + transformation
        ↓
Monthly app-level dataset
        ↓
Power BI / Excel / database / API
```

## Aggregation logic

Daily install/uninstall measures are summed by month. Snapshot-style measures such as active device installs use a monthly maximum rather than being summed.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure these environment variables using `.env.example` as a reference:

- `GOOGLE_APPLICATION_CREDENTIALS`
- `GCP_PROJECT_ID`
- `PLAY_STATS_BUCKET`
- `PLAY_INSTALLS_PREFIX`

3. Run:

```bash
python google_play_pipeline.py
```

## Security

Never commit service-account JSON files, real bucket names, production project IDs, customer data, or credentials.

## Portfolio note

This repository is a sanitized demonstration of a production analytics pattern. Organization-specific app names, package identifiers, storage details, credentials, and endpoints have been replaced with generic examples.
