# Demo Overview

Generated: 2026-06-22 05:31:51 +02:00

This file summarizes the current proof-of-concept state for demonstration purposes only.
It is not a scientific results report and does not contain threat-coverage, detection-rate, or verifier-output claims.

## Current Demonstration Scope

The current PoC can show the end-to-end construction workflow:

1. Freeze an OpenAQ extract for selected capital-city monitoring locations.
2. Normalize the raw measurements into a canonical measurement schema.
3. Build four integrity-model artifacts from the same canonical data.
4. Inspect basic construction sanity checks for hash-chain and provenance artifacts.

## Dataset Preparation Snapshot

Dataset ID: `openaq_capitals_2025_h2`

Source: OpenAQ API v3

Time window: `2025-07-01` to `2025-12-31`

Cities:

- Warsaw
- Berlin
- Paris
- Madrid

Station selection:

- 3 monitoring locations per city
- 12 monitoring locations total
- Selected locations form city-centered triangles around each city center

Preprocessing summary:

- Input OpenAQ records: 116,361
- Canonical records: 112,973
- Dropped records: 3,388
- Drop reason: missing measurement value
- Stations after ingestion: 12
- Parameters after ingestion: 9

Map artifact:

- `experiments/outputs/maps/openaq_capitals_2025_h2_sensor_map.html`

## Integrity Model Artifacts

### Model A: Conventional Storage

Purpose: canonical measurement storage without audit trail or hash-chain linkage.

Artifact:

- `experiments/outputs/audit/openaq_capitals_2025_h2_model_a_measurements.jsonl`

Current construction summary:

- Records: 112,973
- Artifact SHA-256: `a788733799f7494d10d36e89eec46f9c9610845b005943ba11f7701c96fb922c`

### Model B: Audit Trail

Purpose: append-only audit event export without hash-chain linkage.

Artifact:

- `experiments/outputs/audit/openaq_capitals_2025_h2_model_b_audit_events.jsonl`

Current construction summary:

- Events: 112,974
- Measurement events: 112,973
- Genesis events: 1
- Artifact SHA-256: `b55fd1c65eb7cd70d76ee6a229796403efc2ed126ead770af2c6b8243a61b20e`

### Model C: Audit Trail + Hash Chain

Purpose: audit events linked through `previous_hash` and `block_hash`.

Artifacts:

- `experiments/outputs/chains/openaq_capitals_2025_h2_model_c_hash_chain.jsonl`
- `experiments/outputs/chains/openaq_capitals_2025_h2_model_c_hash_chain_summary.json`

Current construction summary:

- Events: 112,974
- Measurement events: 112,973
- Genesis events: 1
- Terminal block hash: `365fb59c74a55e3d2f36c9d142a6e8f59508c94180fb0c13e5074440b02e468f`
- Artifact SHA-256: `b3a042ec4ec68efeb0219b39834a82f6c5c190d7198145c152082af88d66898e`

Construction sanity check:

- No broken previous-hash links were found in the generated artifact.
- The terminal block hash matches the summary artifact.

### Model D: Audit Trail + Hash Chain + Provenance/Permission State

Purpose: audit events linked through a hash chain, with a simple ingest actor key and reconstructed active key state.

Artifacts:

- `experiments/outputs/chains/openaq_capitals_2025_h2_model_d_provenance_chain.jsonl`
- `experiments/outputs/chains/openaq_capitals_2025_h2_model_d_provenance_chain_summary.json`

Current construction summary:

- Events: 112,975
- Measurement events: 112,973
- Permission events: 1
- Genesis events: 1
- Active reconstructed keys: 1
- Active key-state SHA-256: `10ddaa84b631d8e37e98f8a805d9ccf7b3f0348754a3c3dd4f51a2dfc0b0a453`
- Terminal block hash: `92d8a1153af4c9869ef5e043b31cb44f3e8d696ce247cba9f825d0a77e51aab6`
- Artifact SHA-256: `0e003d2775753ca248bc878e700f764f47dfcf6956772e64ee2c3cff012d0cf3`

Construction sanity check:

- No broken previous-hash links were found in the generated artifact.
- The terminal block hash matches the summary artifact.
- All measurement events reference an active reconstructed key in the generated artifact.

## What Can Be Shown Now

The current demo can show:

- The selected monitoring-location map.
- The canonical dataset preparation summary.
- Four generated model artifacts from the same canonical data.
- The difference between conventional storage, audit trail, hash-chain linkage, and provenance/permission state.
- Basic construction sanity checks for Models C and D.
- Baseline verification reports for the non-tampered Model A-D artifacts.
- The controlled tampering generator interface and one smoke-test tampered artifact.
- The scenario batch runner dry-run plan for the implemented 25-scenario matrix.
- The per-scenario evaluator interface and one smoke-test evaluation artifact.
- The metrics aggregator interface and one smoke-test aggregate table set.
- The full generated 25-scenario metrics table and threat-coverage matrix.

## Baseline Verification Artifacts

The baseline verifier has been run against the current non-tampered artifacts.

Verification reports:

- `experiments/outputs/verification/openaq_capitals_2025_h2_A_conventional_storage_verification_report.json`
- `experiments/outputs/verification/openaq_capitals_2025_h2_B_audit_trail_verification_report.json`
- `experiments/outputs/verification/openaq_capitals_2025_h2_C_audit_hash_chain_verification_report.json`
- `experiments/outputs/verification/openaq_capitals_2025_h2_D_audit_hash_chain_provenance_verification_report.json`

Alert CSV files:

- `experiments/outputs/verification/openaq_capitals_2025_h2_A_conventional_storage_alerts.csv`
- `experiments/outputs/verification/openaq_capitals_2025_h2_B_audit_trail_alerts.csv`
- `experiments/outputs/verification/openaq_capitals_2025_h2_C_audit_hash_chain_alerts.csv`
- `experiments/outputs/verification/openaq_capitals_2025_h2_D_audit_hash_chain_provenance_alerts.csv`

These baseline reports are technical sanity checks of generated artifacts. They are not controlled tampering experiments and should not be interpreted as detection-rate results.

## Scenario Evaluation Artifacts

The evaluator can compare a tampering label file with a verifier alert CSV file.

Smoke-test evaluation artifact:

- `experiments/outputs/metrics/smoke/openaq_capitals_2025_h2_C_audit_hash_chain_value_modification_evaluation.json`

The smoke-test evaluation checks the tool chain on one Model C `value_modification` artifact. It is not a full scenario matrix and should not be interpreted as a threat-coverage result.

Smoke-test aggregate artifacts:

- `experiments/outputs/metrics/smoke_aggregate/openaq_capitals_2025_h2_scenario_metrics.csv`
- `experiments/outputs/metrics/smoke_aggregate/openaq_capitals_2025_h2_threat_coverage_matrix.csv`
- `experiments/outputs/metrics/smoke_aggregate/openaq_capitals_2025_h2_metrics_summary.json`

These aggregate artifacts contain only the smoke-test scenario and are a format check, not the final threat-coverage matrix.

Model D correction/provenance smoke-test aggregate artifacts:

- `experiments/outputs/metrics/smoke_model_d_aggregate/openaq_capitals_2025_h2_scenario_metrics.csv`
- `experiments/outputs/metrics/smoke_model_d_aggregate/openaq_capitals_2025_h2_threat_coverage_matrix.csv`
- `experiments/outputs/metrics/smoke_model_d_aggregate/openaq_capitals_2025_h2_metrics_summary.json`

These aggregate artifacts contain only three Model D smoke-test scenarios: `unauthorized_correction`, `revoked_actor_key_usage`, and `missing_correction_reason`.

## Full Matrix Artifacts

The full implemented 25-scenario matrix has been executed once for `openaq_capitals_2025_h2` with verification enabled.

Generated aggregate artifacts:

- `experiments/outputs/metrics/openaq_capitals_2025_h2_scenario_metrics.csv`
- `experiments/outputs/metrics/openaq_capitals_2025_h2_threat_coverage_matrix.csv`
- `experiments/outputs/metrics/openaq_capitals_2025_h2_metrics_summary.json`

Aggregate status counts:

- `detected`: 20
- `expected_not_detected`: 5
- `missed`: 0
- `partial`: 0
- `unexpected_alert`: 0

These files are measured PoC verification outputs for the implemented scenario set. They are not manuscript prose and should still be reviewed before scientific interpretation.

## What Is Not Available Yet

The current PoC does not yet provide:

- False positive or false negative metrics.
- Scientific result claims.

The tampering generator, verifier, evaluator, metrics aggregator, and full implemented scenario matrix outputs exist. Scientific result claims and broader interpretation remain future work.
