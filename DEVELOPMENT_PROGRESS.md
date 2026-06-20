# Development Progress

Project: Blockchain-Based Environmental Data Integrity for Rural Monitoring Systems

This file tracks implementation progress for the proof-of-concept experiments. It is a development artifact, not manuscript text.

## Current Implementation Status

Last updated: 2026-06-20 20:14:16 +02:00

### Completed

- Created the PoC implementation area under `experiments/`.
- Selected OpenAQ as the first MVP dataset path.
- Added minimal PDM project configuration in `pyproject.toml`.
- Added `pdm.lock` for the declared PDM dependency set.
- Added common reusable experiment modules under `experiments/common/`.
- Added OpenAQ-specific ingestion under `experiments/openaq/`.
- Added OpenAQ API v3 download support under `experiments/openaq/download.py`.
- Added artifact directories under `experiments/data/` and `experiments/outputs/`.
- Added `.gitkeep` placeholders for empty artifact directories.
- Updated `.gitignore` so generated datasets, SQLite files, and outputs are excluded from version control by default.
- Added `experiments/README.md` with the initial ingestion workflow.
- Updated `notes/codex_tasks.md` to reflect completed setup and first ingestion tasks.
- Downloaded a bounded OpenAQ API v3 MVP extract locally using the provided API key file.
- Ingested the frozen OpenAQ MVP extract into canonical measurements and SQLite.
- Added a capital-triangle OpenAQ selection mode for Warsaw, Berlin, Paris, and Madrid.
- The capital-triangle selector scores candidate locations by measurement availability and selects geographically separated monitoring locations around each city center.
- Added resumable OpenAQ downloading with a per-sensor state file.
- Added text progress output for OpenAQ scoring and measurement download steps.
- Proposed MVP time window: 2025-07-01 to 2025-12-31, subject to per-location data availability checks.
- Added retry/backoff handling for OpenAQ HTTP 429, 500, 502, 503, and 504 responses.
- Added minimum inter-location distance for city selection.
- Added static HTML map generation from OpenAQ selection metadata.

### Implemented Modules

| Path | Purpose |
| --- | --- |
| `experiments/common/hashing.py` | Deterministic JSON serialization and SHA-256 hashing helpers. |
| `experiments/common/paths.py` | Centralized experiment paths and directory creation. |
| `experiments/common/schema.py` | Canonical measurement columns and preprocessing report model. |
| `experiments/common/manifest.py` | Dataset manifest creation with raw and processed file hashes. |
| `experiments/common/storage.py` | SQLite schema initialization and measurement loading helpers. |
| `experiments/openaq/download.py` | Bounded OpenAQ API v3 downloader using `OPENAQ_API_KEY`. |
| `experiments/openaq/ingest.py` | OpenAQ CSV, JSON, and JSONL ingestion plus canonical normalization. |
| `experiments/openaq/map.py` | Static HTML map generation from OpenAQ selection metadata. |
| `experiments/openaq/cli.py` | Lightweight CLI for OpenAQ ingestion. |

## Python Environment

Use this virtual environment:

```text
e:\git_venv\dicella\env_blockchain_integrity\
```

Package management is through PDM.

```powershell
e:\git_venv\dicella\env_blockchain_integrity\Scripts\Activate.ps1
pdm install
pdm run compile
```

If the environment is not activated, bind PDM explicitly:

```powershell
pdm use e:\git_venv\dicella\env_blockchain_integrity\Scripts\python.exe
pdm install
```

Current dependency declaration:

- `pandas>=2.0`

Current lockfile:

- `pdm.lock`

Verification note:

- PDM was found in the provided venv as version `2.27.0`.
- The provided venv Python reports version `3.14.0`.
- `pandas` was not installed in the provided venv at the time of this update; it is required for ingestion, while the OpenAQ downloader uses the Python standard library.
- A temporary project-local `.venv` was created by PDM during verification when the external venv was not active; `.venv/` is now ignored and should not be used as the intended project environment.
- The local OpenAQ API key file is expected at `experiments/openaq/API_KEY`; it is ignored by git and must not be committed.

## Minimal Implementation Structure

```text
experiments/
  README.md
  common/
    hashing.py
    manifest.py
    paths.py
    schema.py
    storage.py
  openaq/
    cli.py
    ingest.py
  data/
    raw/
    processed/
    tampered/
  outputs/
    audit/
    chains/
    verification/
    metrics/
    maps/
```

General logic belongs in `experiments/common/`. Dataset-specific parsing and field mapping belongs in dataset packages such as `experiments/openaq/`.

## Current OpenAQ Ingestion Workflow

The download command freezes a bounded OpenAQ API v3 extract when an API key is available. The ingestion command then normalizes that frozen local export.

```powershell
$env:OPENAQ_API_KEY = "your-key"
pdm run openaq-download `
  --dataset-id openaq_mvp `
  --selection-mode capital-triangles `
  --city warsaw `
  --city berlin `
  --city paris `
  --city madrid `
  --datetime-from 2025-07-01 `
  --datetime-to 2025-12-31 `
  --locations-per-city 3 `
  --sensors-per-location 3 `
  --city-radius-meters 25000 `
  --min-location-distance-meters 5000 `
  --candidate-locations-per-city 50 `
  --measurements-per-sensor 5000 `
  --max-retries 6 `
  --retry-backoff-seconds 3 `
  --resume `
  --progress
```

```powershell
pdm run openaq-map `
  --metadata-file experiments\data\raw\openaq_mvp_openaq_v3_download_metadata.json
```

```powershell
pdm run openaq-ingest `
  --source-file experiments\data\raw\openaq_mvp_openaq_v3_measurements.jsonl `
  --dataset-id openaq_mvp `
  --source-url https://api.openaq.org/v3 `
  --query-parameters-json "{""api_version"":""v3""}"
```

Generated artifacts:

- `experiments/data/raw/<dataset_id>_openaq_v3_measurements.jsonl`
- `experiments/data/raw/<dataset_id>_openaq_v3_download_metadata.json`
- `experiments/data/raw/<dataset_id>_openaq_v3_download_state.json`
- `experiments/data/processed/<dataset_id>_measurements.csv`
- `experiments/data/processed/<dataset_id>_measurements.jsonl`
- `experiments/data/processed/<dataset_id>_manifest.json`
- `experiments/data/processed/<dataset_id>_preprocessing_report.json`
- `experiments/data/experiments.sqlite`
- `experiments/outputs/maps/<dataset_id>_sensor_map.html`

These files are generated artifacts and are ignored by default, except `.gitkeep` placeholders.

## Canonical Measurement Fields

The initial canonical schema contains:

- `record_id`
- `dataset_id`
- `source_name`
- `source_record_index`
- `station_id`
- `parameter`
- `timestamp_utc`
- `value`
- `unit`
- `latitude`
- `longitude`
- `quality_flag`
- `raw_payload_json`
- `created_at_utc`

## Explicit Non-Results

No threat-coverage matrix has been generated yet.

No model verification outputs have been generated yet.

No scientific results should be reported from the current implementation alone.

Current previously downloaded data-preparation artifacts are local reproducibility inputs only and may be replaced after final city/time-window selection:

- Dataset ID: `openaq_mvp`
- Source: OpenAQ API v3
- Query window: 2016-12-01 to 2016-12-08
- Local raw measurement records downloaded: 600
- Canonical measurement records ingested: 600
- Stations represented after ingestion: 2
- Parameters represented after ingestion: 5

## Next Development Steps

1. Run `pdm install` in the provided virtual environment.
2. Add `OPENAQ_API_KEY` locally or provide an API key file outside version control.
3. Re-download the frozen OpenAQ extract using capital-triangle selection and the 2025-07-01 to 2025-12-31 candidate window.
4. Run the ingestion command and inspect the generated manifest and preprocessing report.
5. Implement baseline event construction from canonical measurements.
6. Implement Model A and Model B stores.
7. Add hash-chain construction for Models C and D.
8. Implement controlled tampering scenarios only after baseline artifacts are stable.
