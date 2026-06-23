# Proof-of-Concept Architecture

Working title: Blockchain-Based Environmental Data Integrity for Distributed Monitoring Systems

This document defines a lightweight proof-of-concept implementation to support the planned experiments. It is not a production architecture and it is not manuscript text.

## Strategic Positioning

The PoC supports a computer science / information systems paper. Environmental monitoring is used as the application domain because it provides realistic distributed, time-series, multi-actor records with provenance and trust challenges.

The PoC should emphasize:

1. Data integrity.
2. Audit trail architecture.
3. Threat modeling.
4. Provenance verification.
5. Permission-state reconstruction.
6. Controlled tampering scenarios.
7. Reproducible verification workflows.

The PoC should not attempt to evaluate:

1. Environmental engineering outcomes.
2. Sensor calibration science.
3. Pollutant-specific interpretation.
4. Environmental policy impact.
5. Field deployment claims.

## Purpose

The PoC should make the MVP experiments executable by providing:

1. Public environmental data ingestion.
2. Deterministic preprocessing.
3. Four comparable integrity models.
4. Controlled threat injection with ground-truth labels.
5. Model-specific verification workflows.
6. Threat-coverage matrix generation.
7. Metrics-ready verification outputs.

The implementation should support publication experiments without becoming a full blockchain platform.

## Preferred Stack

Core stack:

1. Python 3.
2. Pandas for ingestion and preprocessing.
3. SQLite for structured local storage.
4. JSON or JSONL for portable event logs and experiment artifacts.
5. Standard Python `hashlib` for hashing.
6. Standard Python `sqlite3` for persistence.

Optional:

1. Django dashboard for manual inspection.
2. Streamlit or static HTML reports if faster than Django.
3. NetworkX for optional provenance graph export.

Avoid for MVP:

1. Production blockchain frameworks.
2. Smart contracts.
3. Distributed consensus.
4. External message queues.
5. Heavy cryptographic key infrastructure beyond deterministic key identifiers or simple signatures.
6. Pollutant-specific analytics.
7. Sensor calibration modeling.

## System Architecture

The PoC should be organized as a local reproducible pipeline.

```text
Public Environmental Dataset
    |
    v
Data Ingestion
    |
    v
Preprocessing and Canonical Event Mapping
    |
    v
Baseline Measurement Store
    |
    v
Integrity Model Builder
    |
    +----------------+----------------+----------------+----------------+
    |                |                |                |                |
    v                v                v                v
Model A          Model B          Model C          Model D
Conventional     Audit Trail      Audit Trail      Audit Trail
Storage Only     Only             + Hash Chain     + Hash Chain
                                                   + Provenance/
                                                     Permission
                                                     Reconstruction
    |                |                |                |
    +----------------+----------------+----------------+
                     |
                     v
             Threat Injection
                     |
                     v
             Model-Specific Verifiers
                     |
                     v
             Threat-Coverage Matrix
                     |
                     v
       Verification Reports and Metrics
```

## Integrity Models

### Model A: Conventional Storage Only

Storage:

1. `measurements` table.
2. Raw source snapshot.

Verifier:

1. Schema validation.
2. Basic duplicate checks.
3. Missing-record checks only when an external baseline is available.

Expected limitation:

Model A cannot explain audit, provenance, permission, or delayed synchronization threats unless an untouched external baseline is available.

### Model B: Audit Trail Only

Storage:

1. Conventional measurement storage.
2. Append-only audit log in SQLite or JSONL.

Verifier:

1. Required audit event checks.
2. Event sequence checks.
3. Correction reason checks.
4. Basic consistency checks between measurement rows and audit events.

Expected limitation:

Model B records changes but cannot reliably detect tampering with the audit trail itself because events are not cryptographically linked.

### Model C: Audit Trail Plus Hash Chain

Storage:

1. Model B storage.
2. Deterministic payload hashes.
3. Previous block hashes.
4. Block hashes.

Verifier:

1. Payload hash recalculation.
2. Block hash recalculation.
3. Previous-hash link verification.
4. Detection of changed payloads, changed event order, inserted events, and deleted events.

Expected limitation:

Model C can detect tampering in the event chain, but it does not fully explain whether a hash-valid event was authorized by a valid actor.

### Model D: Audit Trail Plus Hash Chain Plus Provenance/Permission Reconstruction

Storage:

1. Model C storage.
2. Actor identities.
3. Sensor/gateway/operator keys.
4. Key insertion and revocation events.
5. Provenance links.
6. Correction lineage.

Verifier:

1. All Model C checks.
2. Active key-state reconstruction.
3. Actor authorization checks.
4. Correction target checks.
5. Correction reason checks.
6. Provenance reference checks.
7. Delayed synchronization checks.

Expected contribution:

Model D is the proposed architecture for explaining both tampering and governance/provenance failures.

## Threat Model

The PoC should generate and verify the following threats:

1. Value modification.
2. Timestamp modification.
3. Record deletion.
4. Fake record insertion.
5. Replay.
6. Unauthorized correction.
7. Broken provenance.
8. Revoked actor key usage.
9. Missing correction reason.
10. Delayed synchronization.

Each threat scenario should produce:

1. Tampered artifacts.
2. Ground-truth labels.
3. Scenario manifest.
4. Model-specific verifier outputs.

## Suggested Repository Layout

```text
poc/
  __init__.py
  config.py
  ingest.py
  preprocess.py
  schema.py
  storage.py
  hashing.py
  events.py
  models_integrity.py
  tamper.py
  verify.py
  coverage.py
  metrics.py
  reports.py
  cli.py

data/
  raw/
  processed/
  tampered/

outputs/
  models/
  alerts/
  coverage/
  metrics/
  reports/
```

If the paper repository should remain manuscript-only, implementation can instead be placed in `experiments/`. Decide before coding.

## Data Flow

### Step 1: Dataset Ingestion

Input:

1. Downloaded CSV/JSON extract from OpenAQ, EPA AQS, or another selected public source.
2. Dataset metadata file documenting source URL, download date, query parameters, and license notes.

Output:

1. Raw dataset under `data/raw/`.
2. Source manifest as JSON.

Implementation notes:

1. Do not depend on live API calls for every experiment run.
2. Freeze a small dataset extract for reproducibility.
3. Keep API download scripts separate from experiment scripts.

### Step 2: Preprocessing

Processing:

1. Normalize timestamps.
2. Normalize station identifiers.
3. Normalize parameter names.
4. Normalize values and units.
5. Create deterministic `record_id`.
6. Sort records by station, parameter, and timestamp.
7. Preserve original source fields as a raw JSON payload.

Output:

1. Cleaned dataset.
2. Preprocessing report.
3. Canonical measurement events.

### Step 3: Build Models A-D

Model A:

1. Store measurements only.

Model B:

1. Store measurements.
2. Store append-only audit events.

Model C:

1. Store Model B artifacts.
2. Add payload hash, previous hash, and block hash.

Model D:

1. Store Model C artifacts.
2. Add actor, key, permission, provenance, and correction-lineage events.

### Step 4: Inject Threats

For each threat:

1. Copy baseline artifacts.
2. Apply deterministic tampering.
3. Save tampered artifacts.
4. Save ground-truth labels.
5. Save scenario manifest.

### Step 5: Verify Models

For each model and threat:

1. Run model-specific verifier.
2. Export alert log.
3. Compare alerts with ground-truth labels.
4. Assign coverage status.
5. Export metrics-ready tables.

### Step 6: Generate Threat-Coverage Matrix

Rows:

1. Threats.

Columns:

1. Model A.
2. Model B.
3. Model C.
4. Model D.

Cell values:

1. Detectable.
2. Partially detectable.
3. Not detectable.
4. Requires external baseline.
5. Not applicable.

Final cell values must come from implemented verifier behavior after experiments are run.

## Data Model

### `dataset_manifest`

Fields:

1. `dataset_id`
2. `source_name`
3. `source_url`
4. `query_parameters_json`
5. `downloaded_at`
6. `raw_file_path`
7. `processed_file_path`
8. `raw_file_hash`
9. `notes`

### `measurements`

Fields:

1. `record_id`
2. `dataset_id`
3. `station_id`
4. `parameter`
5. `timestamp`
6. `value`
7. `unit`
8. `latitude`
9. `longitude`
10. `quality_flag`
11. `raw_payload_json`
12. `created_at`

### `audit_events`

Fields:

1. `event_id`
2. `model_id`
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

### `actors`

Fields:

1. `actor_id`
2. `actor_type`
3. `description`

### `keys`

Fields:

1. `key_id`
2. `actor_id`
3. `status`
4. `valid_from`
5. `valid_to`
6. `created_event_id`
7. `revoked_event_id`

### `threat_scenarios`

Fields:

1. `scenario_id`
2. `threat_type`
3. `seed`
4. `target_rate`
5. `description`
6. `created_at`

### `tampering_labels`

Fields:

1. `label_id`
2. `scenario_id`
3. `threat_type`
4. `target_record_id`
5. `target_event_id`
6. `expected_detection`
7. `details_json`

### `verification_reports`

Fields:

1. `report_id`
2. `model_id`
3. `scenario_id`
4. `verification_started_at`
5. `verification_finished_at`
6. `status`
7. `checked_events`
8. `alerts_count`
9. `report_json`

### `coverage_matrix`

Fields:

1. `matrix_id`
2. `model_id`
3. `threat_type`
4. `coverage_status`
5. `evidence_report_id`
6. `notes`

## Hashing Strategy

Use Python `hashlib.sha256` for the MVP unless there is a documented reason to use SHA-3.

Canonical serialization:

```python
json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
```

Payload hash:

1. Computed from canonical payload.
2. Used in Models C and D.

Block hash:

1. Computed from event metadata, payload hash, previous hash, and signature/key identifier.
2. Used in Models C and D.

Summary hash:

1. Optional extended feature.
2. May be used for delayed synchronization or performance experiments.

## Audit Trail Model

Audit event types:

1. `GENESIS_NETWORK`
2. `INSERT_SENSOR_KEY`
3. `REVOKE_SENSOR_KEY`
4. `INSERT_MEASUREMENT`
5. `CORRECT_MEASUREMENT`
6. `INVALIDATE_MEASUREMENT`
7. `SUMMARY_BLOCK`
8. `VERIFY_BATCH`
9. `PUBLISH_DATASET`

Correction events must include:

1. Original `record_id`.
2. Corrected field names.
3. Previous value hash.
4. Corrected value hash.
5. Correction reason.
6. Actor ID.
7. Active key ID.
8. Timestamp.

Model D reconstructs permission state from key insertion and revocation events.

## Verification Workflow

### Inputs

1. Model artifacts.
2. Scenario artifacts.
3. Tampering labels.
4. Verification configuration.

### Workflow

1. Load selected model artifacts.
2. Load selected threat scenario.
3. Run model-specific checks.
4. Emit alert records.
5. Compare alerts with labels.
6. Compute detection metrics.
7. Assign coverage status.
8. Export report and matrix entries.

### Model-Specific Checks

Model A:

1. Schema checks.
2. Optional baseline comparison.

Model B:

1. Schema checks.
2. Audit event completeness.
3. Correction reason presence.
4. Basic sequence consistency.

Model C:

1. Model B checks.
2. Payload hash recalculation.
3. Block hash recalculation.
4. Previous-hash verification.

Model D:

1. Model C checks.
2. Active key-state reconstruction.
3. Actor authorization checks.
4. Correction lineage checks.
5. Provenance reference checks.
6. Delayed synchronization checks.

### Alert Types

Use stable alert codes:

1. `SCHEMA_MISSING_FIELD`
2. `VALUE_MODIFICATION`
3. `TIMESTAMP_MODIFICATION`
4. `RECORD_DELETION`
5. `FAKE_RECORD_INSERTION`
6. `REPLAY_SUSPECTED`
7. `PAYLOAD_HASH_MISMATCH`
8. `BLOCK_HASH_MISMATCH`
9. `PREVIOUS_HASH_MISMATCH`
10. `UNKNOWN_ACTOR_KEY`
11. `REVOKED_ACTOR_KEY`
12. `UNAUTHORIZED_EVENT_TYPE`
13. `CORRECTION_TARGET_MISSING`
14. `CORRECTION_REASON_MISSING`
15. `BROKEN_PROVENANCE`
16. `DELAYED_SYNCHRONIZATION`

## Report Outputs

Each run should produce:

1. `verification_report.json`
2. `alerts.csv`
3. `metrics.csv`
4. `coverage_matrix.csv`
5. Optional Markdown report.

Reports must not be interpreted as manuscript results until experiments are intentionally executed and reviewed.

## Lightweight CLI Design

Example commands:

```text
python -m poc.cli ingest --source-file data/raw/sample.csv --dataset-id openaq_mvp
python -m poc.cli preprocess --dataset-id openaq_mvp
python -m poc.cli build-models --dataset-id openaq_mvp
python -m poc.cli tamper --scenario value_modification --rate 0.05
python -m poc.cli verify --model C --scenario value_modification
python -m poc.cli coverage --dataset-id openaq_mvp
python -m poc.cli metrics --dataset-id openaq_mvp
```

## MVP Implementation Scope

The MVP should include:

1. CSV ingestion.
2. Pandas preprocessing.
3. SQLite storage.
4. Deterministic event builder.
5. Four integrity model builders.
6. Hash-chain support for Models C and D.
7. Permission/provenance reconstruction for Model D.
8. Tampering generator for all ten threats.
9. Model-specific verifiers.
10. Threat-coverage matrix generation.
11. Metrics export.

The MVP should not include:

1. Live dashboard.
2. Production authentication.
3. Smart contracts.
4. Distributed consensus.
5. Real deployment networking.
6. Pollutant-specific interpretation.

## Optional Dashboard

If a dashboard is added, use it only for inspection:

1. Browse measurements.
2. Browse model artifacts.
3. View verification alerts.
4. View threat-coverage matrix.
5. Filter by model, threat, station, event type, and alert code.

Django is acceptable if it reuses the SQLite schema. Otherwise, a static report or Streamlit view is probably faster.

## Success Criteria

The PoC is sufficient when it can:

1. Load a small public environmental dataset extract.
2. Build Models A-D from the same canonical events.
3. Generate labeled tampered variants for all MVP threats.
4. Verify each model against each threat.
5. Export alert logs and metrics-ready tables.
6. Export a threat-coverage matrix.
7. Support the MVP experiments without manual data editing.
