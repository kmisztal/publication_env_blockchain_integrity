# Proof-of-Concept Architecture

Working title: Blockchain-Based Environmental Data Integrity for Rural Monitoring Systems

This document defines a lightweight proof-of-concept implementation to support the planned experiments. It is not a production architecture and it is not manuscript text.

## Purpose

The PoC should make the experiments executable by providing:

1. Public environmental data ingestion.
2. Deterministic preprocessing.
3. A hash-chain integrity layer.
4. A lightweight audit trail.
5. Synthetic tampering generation.
6. Verification reports for integrity, provenance, and permission checks.

The implementation should support publication experiments without becoming a full blockchain platform.

## Preferred Stack

Core stack:

1. Python 3.
2. Pandas for ingestion and preprocessing.
3. SQLite for structured local storage.
4. JSON or JSONL files for portable event logs and experiment artifacts.
5. Standard Python `hashlib` for hashing.
6. Standard Python `sqlite3` for persistence.

Optional:

1. Django dashboard for manual inspection.
2. Streamlit or simple static HTML reports if faster than Django.
3. NetworkX for provenance graph export if Experiment 7 is implemented.

Avoid for MVP:

1. Production blockchain frameworks.
2. Smart contracts.
3. Distributed consensus.
4. External message queues.
5. Heavy cryptographic key infrastructure beyond deterministic key identifiers or simple signatures.

## System Architecture

The PoC should be organized as a small local pipeline.

```text
Public Dataset
    |
    v
Data Ingestion
    |
    v
Preprocessing and Normalization
    |
    v
Off-Chain Measurement Store
    |
    v
Event Builder
    |
    +-----------------------------+
    |                             |
    v                             v
Measurement Integrity Chain       Permission and Provenance Chain
    |                             |
    +-------------+---------------+
                  |
                  v
          Central Verifier
                  |
                  v
        Verification Reports
                  |
                  v
       Experiment Tables and Logs
```

## Suggested Repository Layout

This can be adjusted during implementation, but the first implementation should stay small.

```text
poc/
  __init__.py
  config.py
  ingest.py
  preprocess.py
  models.py
  storage.py
  hashing.py
  events.py
  audit.py
  tamper.py
  verify.py
  metrics.py
  reports.py
  cli.py

data/
  raw/
  processed/
  tampered/

outputs/
  chains/
  audit/
  verification/
  metrics/
```

If the paper repository should remain manuscript-only, the implementation can instead be placed in `experiments/`. Decide before coding.

## Data Flow

### Step 1: Dataset Ingestion

Input:

1. Downloaded CSV/JSON extract from OpenAQ, EPA AQS, or another selected public source.
2. Dataset metadata file documenting source URL, download date, query parameters, and license notes.

Output:

1. Raw dataset stored under `data/raw/`.
2. Source manifest stored as JSON.

Implementation notes:

1. Do not depend on live API calls for every experiment run.
2. Freeze a small dataset extract for reproducibility.
3. Keep API download scripts separate from experiment scripts.

### Step 2: Preprocessing

Input:

Raw dataset extract.

Processing:

1. Normalize timestamps.
2. Normalize station identifiers.
3. Normalize parameter names.
4. Normalize values and units.
5. Create deterministic `record_id`.
6. Sort records by station, parameter, and timestamp.
7. Preserve original source fields in a raw payload column or sidecar file.

Output:

1. Cleaned CSV/Parquet/JSONL file.
2. Preprocessing report with record counts and missing fields.

No results should be interpreted scientifically at this stage.

### Step 3: Off-Chain Measurement Store

Input:

Cleaned environmental records.

Storage:

1. SQLite table `measurements`.
2. Optional JSONL mirror for easier inspection.

Purpose:

The raw environmental values remain off-chain. The integrity chain stores hashes and metadata needed for verification.

### Step 4: Event Construction

Input:

Rows from `measurements`.

Output:

Event objects such as:

1. `GENESIS_NETWORK`
2. `INSERT_SENSOR_KEY`
3. `REVOKE_SENSOR_KEY`
4. `INSERT_MEASUREMENT`
5. `CORRECT_MEASUREMENT`
6. `INVALIDATE_MEASUREMENT`
7. `SUMMARY_BLOCK`
8. `VERIFY_BATCH`
9. `PUBLISH_DATASET`

Each event should be serialized deterministically before hashing.

### Step 5: Chain Construction

Input:

Ordered events.

Processing:

1. Serialize event payload with sorted keys.
2. Compute payload hash.
3. Attach previous block hash.
4. Compute block hash.
5. Persist block in SQLite and/or JSONL.

Output:

1. Measurement integrity chain.
2. Permission/provenance chain.
3. Optional summary blocks.

### Step 6: Tampering Generation

Input:

Clean baseline dataset and/or chain.

Processing:

1. Apply controlled synthetic attacks.
2. Preserve labels for every tampered item.
3. Generate tampered copies instead of modifying the baseline.

Output:

1. Tampered datasets.
2. Tampered chains.
3. Ground-truth labels.

### Step 7: Verification

Input:

Baseline or tampered chain, off-chain measurement store, permission chain.

Processing:

1. Recalculate payload hashes.
2. Recalculate block hashes.
3. Check previous-hash links.
4. Check required fields.
5. Check key authorization status at event time.
6. Check correction lineage.
7. Check summary-block coverage if enabled.
8. Compare alerts against ground-truth tampering labels for experiments.

Output:

1. Verification report.
2. Alert log.
3. Metrics-ready detection table.

## Data Model

### SQLite Tables

Use SQLite for transparency and reproducibility. Tables should remain simple.

#### `dataset_manifest`

Fields:

1. `dataset_id`
2. `source_name`
3. `source_url`
4. `query_parameters_json`
5. `downloaded_at`
6. `raw_file_path`
7. `processed_file_path`
8. `notes`

#### `measurements`

Fields:

1. `record_id`
2. `dataset_id`
3. `source_dataset`
4. `station_id`
5. `parameter`
6. `timestamp`
7. `value`
8. `unit`
9. `latitude`
10. `longitude`
11. `quality_flag`
12. `raw_payload_json`
13. `created_at`

#### `events`

Fields:

1. `event_id`
2. `chain_id`
3. `event_type`
4. `event_timestamp`
5. `actor_id`
6. `subject_id`
7. `payload_json`
8. `payload_hash`
9. `previous_hash`
10. `block_hash`
11. `signature_id`
12. `source_record_id`
13. `created_at`

#### `keys`

Fields:

1. `key_id`
2. `actor_id`
3. `actor_type`
4. `status`
5. `valid_from`
6. `valid_to`
7. `created_by`
8. `created_event_id`
9. `revoked_event_id`

#### `verification_reports`

Fields:

1. `report_id`
2. `chain_id`
3. `verification_started_at`
4. `verification_finished_at`
5. `status`
6. `checked_events`
7. `alerts_count`
8. `report_json`

#### `tampering_labels`

Fields:

1. `label_id`
2. `scenario_id`
3. `attack_type`
4. `target_record_id`
5. `target_event_id`
6. `expected_detection`
7. `details_json`

### JSON Event Schema

Every event should use a deterministic schema:

```json
{
  "event_id": "evt_000001",
  "chain_id": "measurement_chain",
  "event_type": "INSERT_MEASUREMENT",
  "event_timestamp": "2026-01-01T00:00:00Z",
  "actor_id": "gateway_001",
  "subject_id": "record_000001",
  "payload": {},
  "payload_hash": "computed_payload_hash",
  "previous_hash": "previous_block_hash",
  "block_hash": "computed_block_hash",
  "signature_id": "key_gateway_001"
}
```

The `payload` content depends on event type, but should always be JSON-serializable.

## Hashing Strategy

### Goals

The hashing layer should support:

1. Deterministic reproduction.
2. Detection of unauthorized record changes.
3. Detection of broken chain links.
4. Verification of off-chain raw records against stored hashes.
5. Summary-block checkpoints for extended experiments.

### Algorithm

Use Python `hashlib.sha256` for the MVP unless there is a documented reason to use SHA-3.

Rationale:

1. SHA-256 is widely available in the Python standard library.
2. The PoC goal is integrity experiment support, not cryptographic standard comparison.
3. The manuscript can later discuss algorithm choice with TODO:CITATION_NEEDED if needed.

Optional extension:

Add `sha3_256` as a configurable alternative to connect more directly with the patent-inspired background.

### Canonical Serialization

Before hashing:

1. Convert event payload to JSON.
2. Sort keys.
3. Use compact separators.
4. Normalize timestamps.
5. Avoid non-deterministic fields in the hash input unless intentionally part of the event.

Recommended Python pattern:

```python
json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
```

### Payload Hash

`payload_hash` should be computed from the canonical payload only.

Purpose:

1. Detect changes in measurement value, timestamp, station ID, unit, metadata, or correction reason.
2. Allow off-chain record verification.

### Block Hash

`block_hash` should be computed from:

1. `event_id`
2. `chain_id`
3. `event_type`
4. `event_timestamp`
5. `actor_id`
6. `subject_id`
7. `payload_hash`
8. `previous_hash`
9. `signature_id`

Purpose:

1. Detect event-level tampering.
2. Preserve chain order.
3. Link each event to prior state.

### Summary Hash

For summary blocks, compute a digest over:

1. previous summary hash,
2. ordered list of covered block hashes,
3. active key-state digest,
4. covered timestamp range,
5. summary policy.

Summary blocks should be optional in MVP and enabled for extended experiments.

## Audit Trail Model

### Principles

1. Original measurements are not overwritten.
2. Corrections are new events referencing original records.
3. Invalidations are new events referencing original records.
4. Key insertion and revocation are auditable events.
5. Verification reports are preserved as events or report records.

### Audit Event Categories

Measurement events:

1. `INSERT_MEASUREMENT`
2. `CORRECT_MEASUREMENT`
3. `INVALIDATE_MEASUREMENT`

Permission events:

1. `INSERT_SENSOR_KEY`
2. `REVOKE_SENSOR_KEY`
3. `INSERT_OPERATOR_KEY`
4. `REVOKE_OPERATOR_KEY`

Verification events:

1. `VERIFY_BATCH`
2. `SUMMARY_BLOCK`
3. `PUBLISH_DATASET`

### Correction Lineage

Each correction event must include:

1. original `record_id`,
2. corrected field names,
3. previous value hash,
4. corrected value hash,
5. correction reason,
6. actor ID,
7. active key ID,
8. timestamp.

The verifier should reject correction events that do not reference an existing original record.

### Permission State

The verifier should reconstruct permission state from the event stream:

1. Start with `GENESIS_NETWORK`.
2. Apply key insertion events.
3. Apply revocation events.
4. Check whether each measurement or correction event was submitted by an active authorized key at event time.

For MVP, real cryptographic signatures can be simplified to `signature_id` and deterministic actor-key mapping. Real signatures can be an optional extension.

## Verification Workflow

### Inputs

1. SQLite database.
2. Chain JSONL files.
3. Optional tampering labels.
4. Verification configuration.

### Workflow

1. Load chain events in order.
2. Validate schema and required fields.
3. Recalculate payload hash.
4. Recalculate block hash.
5. Check `previous_hash` against prior event.
6. Reconstruct active permission state.
7. Validate actor authorization.
8. Validate correction lineage.
9. Validate off-chain measurement hash against stored payload.
10. Validate summary blocks if enabled.
11. Emit alert records.
12. If labels are available, compute detection metrics.

### Alert Types

Use stable alert codes:

1. `SCHEMA_MISSING_FIELD`
2. `PAYLOAD_HASH_MISMATCH`
3. `BLOCK_HASH_MISMATCH`
4. `PREVIOUS_HASH_MISMATCH`
5. `UNKNOWN_ACTOR_KEY`
6. `REVOKED_ACTOR_KEY`
7. `UNAUTHORIZED_EVENT_TYPE`
8. `CORRECTION_TARGET_MISSING`
9. `CORRECTION_REASON_MISSING`
10. `SUMMARY_HASH_MISMATCH`
11. `OFFCHAIN_RECORD_MISMATCH`
12. `REPLAY_SUSPECTED`

### Report Outputs

Each verification run should produce:

1. `verification_report.json`
2. `alerts.csv`
3. optional `metrics.csv` if labels are provided,
4. optional human-readable Markdown summary.

The report must not contain interpreted manuscript results until experiments are executed and reviewed.

## Lightweight CLI Design

Use one small CLI entry point:

```text
python -m poc.cli ingest --source-file data/raw/sample.csv --dataset-id openaq_mvp
python -m poc.cli preprocess --dataset-id openaq_mvp
python -m poc.cli build-chain --dataset-id openaq_mvp
python -m poc.cli tamper --scenario value_modification --rate 0.05
python -m poc.cli verify --chain outputs/chains/baseline.jsonl
python -m poc.cli metrics --alerts outputs/verification/alerts.csv --labels data/tampered/labels.csv
```

The exact commands can change during implementation, but the workflow should remain scriptable.

## MVP Implementation Scope

The MVP should include:

1. CSV ingestion.
2. Pandas preprocessing.
3. SQLite storage.
4. Deterministic event builder.
5. Hash-chain builder.
6. Basic permission chain using key IDs.
7. Tampering generator for value, timestamp, deletion, insertion, replay, and unauthorized correction.
8. Verifier with stable alert codes.
9. Metrics generation when tampering labels are present.

The MVP should not include:

1. Live dashboard.
2. Production authentication.
3. Smart contracts.
4. Distributed consensus.
5. Real deployment networking.

## Optional Dashboard

If a dashboard is added, use it only for inspection:

1. Browse measurements.
2. Browse chain events.
3. View verification alerts.
4. View correction lineage.
5. Filter by station, event type, and alert code.

Django is acceptable if it reuses the SQLite schema. Otherwise, a static report or lightweight Streamlit view is probably faster.

## Design Risks

1. Overbuilding the PoC may delay the publication experiments.
2. Real API integration may introduce instability; use frozen extracts.
3. Signature implementation can become distracting; use key IDs first.
4. SQLite is sufficient for experiments but should not be framed as production storage.
5. Synthetic tampering must be clearly separated from real-world attack evidence.
6. Summary blocks should stay optional until baseline verification works.

## Success Criteria

The PoC is sufficient when it can:

1. Load a small public environmental dataset extract.
2. Create a deterministic measurement integrity chain.
3. Create basic audit and permission events.
4. Generate tampered variants with labels.
5. Verify clean and tampered chains.
6. Export alerts and metrics-ready tables.
7. Support the MVP experiments without manual data editing.
