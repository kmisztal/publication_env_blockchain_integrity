# Methods-Ready Notes

Dataset ID: `openaq_capitals_2025_h2`

This file is a structured source note for later manuscript writing. It is not a manuscript section.

## Study Positioning

The proof-of-concept evaluates integrity mechanisms for distributed environmental monitoring data. The environmental dataset is used as a realistic information-system substrate: distributed sources, time-series measurements, multiple parameters, and provenance-sensitive records.

The experiment should be framed primarily as a computer science / information systems evaluation. It does not claim environmental-domain findings.

## Dataset

Source: OpenAQ API v3.

Time window: `2025-07-01` to `2025-12-31`.

Cities:

- Warsaw
- Berlin
- Paris
- Madrid

Selection design:

- Three monitoring locations were selected per city.
- The selected locations were chosen to form a geographically separated triangle around the approximate city center.
- The station geometry supports a distributed-monitoring setting, but the current integrity experiment treats all stations as one combined dataset.

Canonical dataset after preprocessing:

- Input OpenAQ records: `116361`
- Canonical records: `112973`
- Dropped records: `3388`
- Drop reason in preprocessing report: missing measurement value
- Selected stations/locations: `12`
- Parameters: `9`

Important methodological note:

The current integrity models do not build independent chains per city, station, or gateway. The station diversity is used to provide a realistic multi-source dataset. It is not yet used as a separate cross-sensor validation mechanism.

## Integrity Models

Model A, conventional storage only:

- Stores canonical measurement records.
- No audit trail.
- No hash-chain linkage.
- No provenance or permission state.
- Verification is limited to schema and duplicate-record checks.

Model B, audit trail only:

- Represents measurements as audit events.
- Includes deterministic payload hashes and event identifiers.
- Does not link events with `previous_hash`.
- Supports local event-integrity checks but not stream-continuity checks.

Model C, audit trail plus hash chain:

- Extends Model B with `previous_hash` and `block_hash`.
- Supports verification of event order and chain continuity.
- Makes deletion and chain-order disruption visible to the verifier.

Model D, audit trail plus hash chain plus provenance/permission reconstruction:

- Extends Model C with actor/key identifiers, permission events, revocation events, correction events, and active key-state reconstruction.
- Adds checks for unauthorized correction, revoked key usage, missing correction reason, broken provenance, and delayed synchronization.

## Experimental Workflow

1. Download and freeze a bounded OpenAQ extract.
2. Normalize raw records into canonical measurements.
3. Build Model A-D artifacts from the same canonical dataset.
4. Generate controlled tampered artifacts for applicable model/threat pairs.
5. Verify each tampered artifact.
6. Compare verifier alerts against scenario labels.
7. Aggregate per-scenario metrics and export the threat-coverage matrix.
8. Generate a reproducibility manifest with file paths, sizes, and SHA-256 hashes.

## Scenario Set

Base scenarios used across Models A-D where applicable:

- `value_modification`
- `timestamp_modification`
- `record_deletion`
- `fake_record_insertion`
- `replay`

Model D-specific governance/provenance scenarios:

- `broken_provenance`
- `unauthorized_correction`
- `revoked_actor_key_usage`
- `missing_correction_reason`
- `delayed_synchronization`

## Status Semantics

`detected` means that the verifier produced the expected alert code for the injected scenario.

`expected_not_detected` means that the scenario was intentionally outside the detection capability of the evaluated model.

`not_applicable` means that a scenario was not applied to a model in the current implementation.

`missed`, `partial`, and `unexpected_alert` indicate potential evaluation or implementation issues.

## Reproducibility Artifacts

Primary machine-readable outputs:

- `experiments/outputs/metrics/openaq_capitals_2025_h2_scenario_metrics.csv`
- `experiments/outputs/metrics/openaq_capitals_2025_h2_threat_coverage_matrix.csv`
- `experiments/outputs/metrics/openaq_capitals_2025_h2_metrics_summary.json`
- `experiments/outputs/manifests/openaq_capitals_2025_h2_experiment_run_manifest.json`

Primary review outputs:

- `experiments/outputs/full_matrix_summary_en.md`
- `experiments/outputs/full_matrix_summary_pl.md`
- `experiments/outputs/manifests/openaq_capitals_2025_h2_experiment_run_manifest.md`

