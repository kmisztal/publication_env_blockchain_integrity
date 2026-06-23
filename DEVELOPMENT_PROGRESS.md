# Development Progress

Project: Blockchain-Based Environmental Data Integrity for Rural Monitoring Systems

This file tracks implementation progress for the proof-of-concept experiments. It is a development artifact, not manuscript text.

## Current Implementation Status

Last updated: 2026-06-23 18:38:08 +02:00

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
- Added generic integrity-event construction under `experiments/integrity/`.
- Added Model A baseline artifact export for conventional canonical measurement storage.
- Added Model B audit-trail artifact export without hash-chain linkage.
- Model B genesis timestamp is derived from canonical measurement metadata so repeated builds of the same processed file are reproducible.
- Added an integrity CLI with `init-db` and `build-baseline` commands.
- Built local baseline artifacts for `openaq_capitals_2025_h2`: 112,973 Model A records and 112,974 Model B audit events including one genesis event.
- Added Model C hash-chain construction with deterministic `previous_hash` and `block_hash` linkage.
- Added the `integrity-build-hash-chain` PDM script.
- Built local Model C hash-chain artifacts for `openaq_capitals_2025_h2`: 112,974 events including one genesis event.
- Checked the generated Model C chain for broken previous-hash links; no broken links were found in the generated artifact.
- Added Model D provenance/permission chain construction with an ingest actor key and permission grant event.
- Added active key-state reconstruction from permission and revocation events.
- Added the `integrity-build-provenance-chain` PDM script.
- Built local Model D artifacts for `openaq_capitals_2025_h2`: 112,975 events including one genesis event, one permission event, and 112,973 measurement events.
- Checked the generated Model D chain for broken previous-hash links and measurement events without an active key; no issues were found in the generated artifact.
- Added a baseline verification engine under `experiments/integrity/verification.py`.
- Added `integrity-verify` CLI/PDM support for verifying a single generated artifact.
- Generated baseline verification reports and alert CSV files for Models A-D.
- Baseline verification currently checks schema, duplicate IDs, payload hashes, block hashes, previous-hash links, and Model D active-key references.
- Added a controlled tampering generator under `experiments/integrity/tampering.py`.
- Added `integrity-tamper` CLI/PDM support for generating one tampered artifact and ground-truth label file.
- Implemented value modification, timestamp modification, record deletion, fake record insertion, replay, and Model D broken provenance scenarios.
- Ran one smoke-test tampering generation for `C_audit_hash_chain` with `value_modification`; this was a generator check, not a full experiment run.
- Added a scenario batch runner under `experiments/integrity/scenarios.py`.
- Added `integrity-run-scenarios` CLI/PDM support with `--dry-run` and optional `--verify`.
- Ran a dry run for `openaq_capitals_2025_h2`; it planned 21 implemented scenarios across Models A-D without generating the full scenario matrix.
- Added a scenario evaluator under `experiments/integrity/evaluation.py`.
- Added `integrity-evaluate` CLI/PDM support for comparing tampering labels with verifier alert CSV files.
- Connected `run-scenarios --verify` to generate per-scenario evaluation JSON files under `experiments/outputs/metrics/tampered/`.
- Ran one smoke-test verification and evaluation for the previously generated Model C `value_modification` tampered artifact; this was a tool check only, not a full experiment run.
- Added aggregate metrics export for per-scenario evaluation JSON files.
- Added `integrity-aggregate-metrics` CLI/PDM support.
- Ran one smoke-test metrics aggregation from the existing smoke evaluation file; this was a format check only, not a full threat-coverage matrix.

### Implemented Modules

| Path | Purpose |
| --- | --- |
| `experiments/common/hashing.py` | Deterministic JSON serialization and SHA-256 hashing helpers. |
| `experiments/common/paths.py` | Centralized experiment paths and directory creation. |
| `experiments/common/schema.py` | Canonical measurement columns and preprocessing report model. |
| `experiments/common/manifest.py` | Dataset manifest creation with raw and processed file hashes. |
| `experiments/common/storage.py` | SQLite schema initialization and measurement loading helpers. |
| `experiments/integrity/events.py` | Deterministic event constants, payload hashes, genesis events, and measurement audit events. |
| `experiments/integrity/models.py` | Model A, Model B, Model C, and Model D artifact builders. |
| `experiments/integrity/cli.py` | CLI for initializing storage and building baseline integrity artifacts. |
| `experiments/integrity/verification.py` | Baseline verification engine for generated Model A-D artifacts. |
| `experiments/integrity/tampering.py` | Controlled tampering artifact and label generator. |
| `experiments/integrity/scenarios.py` | Scenario matrix planner and optional batch runner. |
| `experiments/integrity/evaluation.py` | Per-scenario comparison of tampering labels against verifier alerts and aggregate metrics table export. |
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
- `pandas` is available in the provided venv and is used for ingestion and baseline artifact construction.
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
  integrity/
    cli.py
    events.py
    models.py
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

## Current Integrity Baseline Workflow

After ingestion, build the first two MVP model artifacts from canonical measurements:

```powershell
pdm run integrity-build-baseline `
  --dataset-id openaq_capitals_2025_h2 `
  --measurements-file experiments\data\processed\openaq_capitals_2025_h2_measurements.csv
```

Generated baseline artifacts:

- `experiments/outputs/audit/<dataset_id>_model_a_measurements.jsonl`
- `experiments/outputs/audit/<dataset_id>_model_b_audit_events.jsonl`
- `experiments/outputs/audit/<dataset_id>_baseline_models_summary.json`

For `openaq_capitals_2025_h2`, the local baseline build produced:

- Model A records: 112,973
- Model B audit events: 112,974, including one genesis event
- SQLite audit event rows for Model B: 112,974

These files are generated artifacts and are ignored by default.

## Current Hash-Chain Workflow

Build the Model C audit trail plus hash chain:

```powershell
pdm run integrity-build-hash-chain `
  --dataset-id openaq_capitals_2025_h2 `
  --measurements-file experiments\data\processed\openaq_capitals_2025_h2_measurements.csv
```

Generated hash-chain artifacts:

- `experiments/outputs/chains/<dataset_id>_model_c_hash_chain.jsonl`
- `experiments/outputs/chains/<dataset_id>_model_c_hash_chain_summary.json`

For `openaq_capitals_2025_h2`, the local hash-chain build produced:

- Model C events: 112,974, including one genesis event
- SQLite audit event rows for Model C: 112,974
- Structural chain check: no broken previous-hash links in the generated artifact

This is a construction sanity check, not a tampering experiment or threat-detection result.

## Current Baseline Verification Workflow

Verify a generated artifact:

```powershell
pdm run integrity-verify `
  --dataset-id openaq_capitals_2025_h2 `
  --model-id C_audit_hash_chain `
  --artifact-file experiments\outputs\chains\openaq_capitals_2025_h2_model_c_hash_chain.jsonl
```

Generated verification artifacts:

- `experiments/outputs/verification/<dataset_id>_<model_id>_verification_report.json`
- `experiments/outputs/verification/<dataset_id>_<model_id>_alerts.csv`

Baseline verification has been run for the current non-tampered Model A-D artifacts. This is a technical sanity check of generated artifacts, not a tampering experiment or threat-coverage result.

## Current Tampering Generator Workflow

Generate one controlled tampered artifact and label file:

```powershell
pdm run integrity-tamper `
  --dataset-id openaq_capitals_2025_h2 `
  --model-id C_audit_hash_chain `
  --threat-type value_modification `
  --artifact-file experiments\outputs\chains\openaq_capitals_2025_h2_model_c_hash_chain.jsonl
```

Implemented threat types:

- `value_modification`
- `timestamp_modification`
- `record_deletion`
- `fake_record_insertion`
- `replay`
- `broken_provenance` for Model D

Generated tampered artifacts and labels are written under `experiments/data/tampered/`.
Correction-related scenarios remain deferred until correction and invalidation events exist.

## Current Scenario Batch Workflow

Preview the implemented scenario matrix:

```powershell
pdm run integrity-run-scenarios `
  --dataset-id openaq_capitals_2025_h2 `
  --dry-run
```

Run the implemented scenario matrix and verify each tampered artifact:

```powershell
pdm run integrity-run-scenarios `
  --dataset-id openaq_capitals_2025_h2 `
  --verify
```

When `--verify` is used, the batch runner also writes per-scenario evaluation files to `experiments/outputs/metrics/tampered/`.

The current dry-run matrix has 21 planned scenarios:

- 5 scenarios for Model A
- 5 scenarios for Model B
- 5 scenarios for Model C
- 6 scenarios for Model D, including `broken_provenance`

The full batch has not yet been executed in this step.

## Current Scenario Evaluation Workflow

Compare one tampering label file with one verifier alert CSV file:

```powershell
pdm run integrity-evaluate `
  --labels-file experiments\data\tampered\smoke\openaq_capitals_2025_h2_C_audit_hash_chain_value_modification_labels.json `
  --alerts-file experiments\outputs\verification\smoke\openaq_capitals_2025_h2_C_audit_hash_chain_alerts.csv `
  --output-dir experiments\outputs\metrics\smoke
```

The evaluator currently emits per-scenario status counts:

- `detected`
- `partial`
- `missed`
- `expected_not_detected`
- `unexpected_alert`

A smoke-test evaluation of the previously generated Model C `value_modification` artifact classified the expected payload-hash alert as `detected`. This is a tool-chain sanity check only, not a threat-coverage result.

Aggregate per-scenario evaluation files into metrics tables:

```powershell
pdm run integrity-aggregate-metrics `
  --evaluation-dir experiments\outputs\metrics\tampered `
  --output-dir experiments\outputs\metrics `
  --dataset-id openaq_capitals_2025_h2
```

Generated aggregate tables:

- `<output-dir>/<dataset_id>_scenario_metrics.csv`
- `<output-dir>/<dataset_id>_threat_coverage_matrix.csv`
- `<output-dir>/<dataset_id>_metrics_summary.json`

The current aggregate tables include scenario statuses and label-level detection rates. Precision, recall, F1, and false-positive rates remain deferred until negative-case definitions are added to the experimental design.

## Current Provenance And Permission Workflow

Build the Model D audit trail plus hash chain and active key-state reconstruction:

```powershell
pdm run integrity-build-provenance-chain `
  --dataset-id openaq_capitals_2025_h2 `
  --measurements-file experiments\data\processed\openaq_capitals_2025_h2_measurements.csv
```

Generated Model D artifacts:

- `experiments/outputs/chains/<dataset_id>_model_d_provenance_chain.jsonl`
- `experiments/outputs/chains/<dataset_id>_model_d_provenance_chain_summary.json`

For `openaq_capitals_2025_h2`, the local Model D build produced:

- Model D events: 112,975
- Measurement events: 112,973
- Permission events: 1
- Active reconstructed keys: 1
- SQLite audit event rows for Model D: 112,975
- Structural chain and active-key check: no broken links and no measurement event without an active key in the generated artifact

This is a construction sanity check, not a tampering experiment or threat-detection result.

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

Baseline model verification outputs exist for non-tampered artifacts, and one smoke-test tampered artifact has been verified and evaluated. These are tool-chain sanity checks only, not scientific threat-coverage results.

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

The Model A, Model B, Model C, and Model D artifacts plus baseline verification reports are reproducibility inputs only. They do not contain tampering scenarios, detection rates, or threat-coverage outputs.

## Next Development Steps

1. Decide when to execute the full implemented scenario matrix and whether to include immediate verification.
2. Add off-chain measurement hash verification where applicable.
3. Add correction lineage checks after correction events are implemented.
4. Generate threat-coverage summaries only after the full scenario matrix has been intentionally executed.
