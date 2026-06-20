# Development Progress

Project: Blockchain-Based Environmental Data Integrity for Rural Monitoring Systems

This file tracks implementation progress for the proof-of-concept experiments. It is a development artifact, not manuscript text.

## Current Implementation Status

Last updated: 2026-06-20 19:22:54 +02:00

### Completed

- Created the PoC implementation area under `experiments/`.
- Selected OpenAQ as the first MVP dataset path.
- Added minimal PDM project configuration in `pyproject.toml`.
- Added common reusable experiment modules under `experiments/common/`.
- Added OpenAQ-specific ingestion under `experiments/openaq/`.
- Added artifact directories under `experiments/data/` and `experiments/outputs/`.
- Added `.gitkeep` placeholders for empty artifact directories.
- Updated `.gitignore` so generated datasets, SQLite files, and outputs are excluded from version control by default.
- Added `experiments/README.md` with the initial ingestion workflow.
- Updated `notes/codex_tasks.md` to reflect completed setup and first ingestion tasks.

### Implemented Modules

| Path | Purpose |
| --- | --- |
| `experiments/common/hashing.py` | Deterministic JSON serialization and SHA-256 hashing helpers. |
| `experiments/common/paths.py` | Centralized experiment paths and directory creation. |
| `experiments/common/schema.py` | Canonical measurement columns and preprocessing report model. |
| `experiments/common/manifest.py` | Dataset manifest creation with raw and processed file hashes. |
| `experiments/common/storage.py` | SQLite schema initialization and measurement loading helpers. |
| `experiments/openaq/ingest.py` | OpenAQ CSV, JSON, and JSONL ingestion plus canonical normalization. |
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

Verification note:

- PDM was found in the provided venv as version `2.27.0`.
- The provided venv Python reports version `3.14.0`.
- `pandas` was not installed in the provided venv at the time of this update.
- A temporary project-local `.venv` was created by PDM during verification when the external venv was not active; `.venv/` is now ignored and should not be used as the intended project environment.

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
```

General logic belongs in `experiments/common/`. Dataset-specific parsing and field mapping belongs in dataset packages such as `experiments/openaq/`.

## Current OpenAQ Ingestion Workflow

The ingestion command expects a frozen local OpenAQ export. It does not invent or download data automatically.

```powershell
pdm run openaq-ingest `
  --source-file path\to\openaq_export.csv `
  --dataset-id openaq_mvp `
  --source-url https://docs.openaq.org/ `
  --query-parameters-json "{}"
```

Generated artifacts:

- `experiments/data/raw/<dataset_id>.<ext>`
- `experiments/data/processed/<dataset_id>_measurements.csv`
- `experiments/data/processed/<dataset_id>_measurements.jsonl`
- `experiments/data/processed/<dataset_id>_manifest.json`
- `experiments/data/processed/<dataset_id>_preprocessing_report.json`
- `experiments/data/experiments.sqlite`

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

## Next Development Steps

1. Add a small frozen OpenAQ extract selected by explicit query parameters.
2. Run `pdm install` in the provided virtual environment.
3. Run the ingestion command and inspect the generated manifest and preprocessing report.
4. Implement baseline event construction from canonical measurements.
5. Implement Model A and Model B stores.
6. Add hash-chain construction for Models C and D.
7. Implement controlled tampering scenarios only after baseline artifacts are stable.
