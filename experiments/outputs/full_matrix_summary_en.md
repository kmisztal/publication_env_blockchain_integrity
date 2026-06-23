# Full Matrix Summary

Generated: 2026-06-23 19:07:46 +02:00

Dataset ID: `openaq_capitals_2025_h2`

This document summarizes the executed proof-of-concept scenario matrix. It is an experiment review artifact, not manuscript prose.

## Scope

The full implemented scenario matrix was executed with verification enabled.

- Models compared: 4
- Scenarios executed: 24
- Per-scenario labels: 24
- Per-scenario verification outputs: 24
- Per-scenario evaluation outputs: 24

Workflow:

1. Generate controlled tampered artifacts.
2. Verify each tampered artifact.
3. Compare verifier alerts against tampering labels.
4. Aggregate scenario-level metrics.
5. Export the threat-coverage matrix.

## Output Files

- Scenario metrics: `experiments/outputs/metrics/openaq_capitals_2025_h2_scenario_metrics.csv`
- Threat-coverage matrix: `experiments/outputs/metrics/openaq_capitals_2025_h2_threat_coverage_matrix.csv`
- Metrics summary: `experiments/outputs/metrics/openaq_capitals_2025_h2_metrics_summary.json`
- Per-scenario evaluations: `experiments/outputs/metrics/tampered/`
- Per-scenario verification reports and alert CSV files: `experiments/outputs/verification/tampered/`
- Tampered artifacts and labels: `experiments/data/tampered/`

## Models

| Model | Description |
| --- | --- |
| A | Conventional canonical measurement storage only |
| B | Audit trail without hash-chain linkage |
| C | Audit trail with hash-chain linkage |
| D | Audit trail with hash-chain linkage plus provenance and permission-state reconstruction |

## Aggregate Status Counts

| Status | Count |
| --- | ---: |
| `detected` | 19 |
| `expected_not_detected` | 5 |
| `missed` | 0 |
| `partial` | 0 |
| `unexpected_alert` | 0 |

Interpretation of statuses:

- `detected`: the verifier produced the expected alert code for the injected scenario.
- `expected_not_detected`: the scenario was intentionally outside the detection capability of that model.
- `missed`: an expected alert was not produced.
- `partial`: at least one expected alert was produced, but not all expected alerts were present.
- `unexpected_alert`: an alert was produced when none was expected.

## Threat-Coverage Matrix

| Threat | Model A | Model B | Model C | Model D |
| --- | --- | --- | --- | --- |
| `broken_provenance` |  |  |  | `detected` |
| `fake_record_insertion` | `expected_not_detected` | `detected` | `detected` | `detected` |
| `missing_correction_reason` |  |  |  | `detected` |
| `record_deletion` | `expected_not_detected` | `expected_not_detected` | `detected` | `detected` |
| `replay` | `detected` | `detected` | `detected` | `detected` |
| `revoked_actor_key_usage` |  |  |  | `detected` |
| `timestamp_modification` | `expected_not_detected` | `detected` | `detected` | `detected` |
| `unauthorized_correction` |  |  |  | `detected` |
| `value_modification` | `expected_not_detected` | `detected` | `detected` | `detected` |

Blank cells mean that the scenario was not applicable to that model in the current implementation.

## Model-Level Reading

Model A detects only the replay scenario in this matrix, because replay creates a duplicate record identifier. It does not contain audit or hash information that would allow the verifier to detect direct value modification, timestamp modification, deletion, or fake insertion.

Model B detects value modification, timestamp modification, fake record insertion, and replay through audit-event integrity checks such as payload hash, event ID, or duplicate ID checks. It does not detect record deletion in this implementation because the audit trail is not hash-linked.

Model C detects all base scenarios implemented for Models A-C. Hash-chain linkage adds the ability to detect deletion and chain-order disruption through previous-hash checks.

Model D detects all Model C scenarios and additionally detects provenance and permission failures: broken provenance, unauthorized correction, revoked actor key usage, and missing correction reason.

## Technical Observations

- The progression from A to D shows increasing threat coverage as audit, hash-chain, and provenance/permission mechanisms are added.
- The current evaluator treats `expected_not_detected` as an expected model limitation, not as an implementation failure.
- Some scenarios produce additional structural alerts beyond the scenario-specific expected alert. For example, several inserted events also produce `previous_hash_mismatch`. The evaluator marks a scenario as detected when the expected alert code is present.
- The matrix is scenario-based and label-based. It is not yet a statistical evaluation over repeated random injections.

## Limitations

- The scenario set is controlled and synthetic.
- Each currently implemented scenario has one ground-truth label.
- Delayed synchronization has not yet been implemented.
- False-positive rate, false-negative rate, precision, recall, and F1 require an explicit negative-case design before they should be reported.
- Results evaluate integrity-model behavior, not environmental data quality.
- The OpenAQ dataset is used as a realistic distributed environmental monitoring data source, not as evidence for environmental-domain conclusions.

## Review Questions

1. Is the distinction between `detected` and `expected_not_detected` clear enough?
2. Should blank cells remain blank, or should they be rendered as `not_applicable` in future outputs?
3. Should additional scenario repetitions be added before manuscript interpretation?
4. Should `delayed_synchronization` be implemented before freezing the MVP experiment set?
