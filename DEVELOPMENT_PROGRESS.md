# Development Progress

Project: Blockchain-Based Environmental Data Integrity for Rural Monitoring Systems

This file tracks implementation progress for the proof-of-concept experiments. It is a development artifact, not manuscript text.

## Current Implementation Status

Last updated: 2026-06-22 03:32:30 +02:00

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
- Added configurable OpenAQ request pacing, defaulting to 55 requests per minute.
- Added handling for rate-limit remaining/reset headers when OpenAQ returns them.
- Added minimum inter-location distance for city selection.
- Added static HTML map generation from OpenAQ selection metadata.
- Replaced sector-only three-location selection with an area- and center-aware triangle search.
- Confirmed the previously downloaded Warsaw selection was nearly collinear and should be regenerated before use as the final MVP extract.
- Added paginated OpenAQ measurement downloads because the API rejects single measurement requests with `limit > 1000`.
- Improved resume behavior so failed sensor downloads are not marked complete.
- Confirmed the regenerated Warsaw-only test extract has 31,187 raw records and 31,147 canonical records after ingestion.
- Confirmed regenerated Warsaw station geometry forms a usable triangle with approximate area 360.86 km².
- Checked existing Berlin, Paris, and Madrid triangle geometries from local metadata; all contain their city center and have non-collinear areas.

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
- OpenAQ measurement requests are paginated internally in chunks of at most 1000 records.

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
  --rate-limit-per-minute 55 `
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

The `openaq_warsaw_test2` extract was generated after the area-aware selector update and is a better candidate for validating the Warsaw selection workflow:

- Raw OpenAQ records: 31,187
- Canonical records after ingestion: 31,147
- Dropped records: 40, due to missing values
- Stations: 3
- Parameters: 7
- Triangle area: approximately 360.86 km²

The full four-capital extract `openaq_capitals_2025_h2` has now been generated with the area-aware triangle selector and ingested into canonical artifacts:

- Source: OpenAQ API v3
- Query window: 2025-07-01 to 2025-12-31
- Cities: Warsaw, Berlin, Paris, Madrid
- Selected stations: 12, using 3 stations per city
- Parameters after ingestion: 9
- Input OpenAQ records: 116,361
- Canonical records after ingestion: 112,973
- Dropped records: 3,388, due to missing measurement values
- Generated map: `experiments/outputs/maps/openaq_capitals_2025_h2_sensor_map.html`
- Geometry check: each city center is inside its selected three-station triangle

These are data-preparation and reproducibility checks only. They are not threat-model results, verification outputs, or scientific findings.

## Next Development Steps

1. Run `pdm install` in the provided virtual environment.
2. Add `OPENAQ_API_KEY` locally or provide an API key file outside version control.
3. Implement baseline event construction from canonical measurements.
4. Implement Model A and Model B stores.
5. Add hash-chain construction for Models C and D.
6. Implement controlled tampering scenarios only after baseline artifacts are stable.
7. Generate threat-coverage and verification outputs only after the model implementations and tampering scripts are in place.
