# Full Matrix Summary

Generated: 2026-06-23 19:25:16 +02:00

Dataset ID: `openaq_capitals_2025_h2`

This document summarizes the executed proof-of-concept scenario matrix. It is an experiment review artifact, not manuscript prose.

## Scope

The full implemented scenario matrix was executed with verification enabled.

- Models compared: 4
- Scenarios executed: 25
- Per-scenario labels: 25
- Per-scenario verification outputs: 25
- Per-scenario evaluation outputs: 25

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

| Model | Short description | Expanded description |
| --- | --- | --- |
| A | Conventional storage only | Stores canonical measurement records without audit events, hash-chain links, actor identity, key state, or provenance reconstruction. The verifier can check record schema and duplicate record identifiers, but it has no independent integrity evidence for modified or deleted values. |
| B | Audit trail only | Represents measurements as audit events with deterministic payload hashes and event identifiers, but events are not linked through previous-hash references. This allows detection of local event payload changes and duplicated event identifiers, but does not provide continuity checks across the event stream. |
| C | Audit trail plus hash chain | Extends Model B by linking events with `previous_hash` and `block_hash`. This adds sequence continuity, so deletion, replay insertion, and chain disruption become detectable through link verification. |
| D | Hash chain plus provenance and permissions | Extends Model C with actor/key identifiers, permission state, revocation handling, correction events, provenance checks, and delayed synchronization checks. This model can distinguish structural tampering from governance/provenance failures such as unauthorized correction or revoked key usage. |

## Scenario Descriptions

| Scenario | Short description |
| --- | --- |
| `value_modification` | Changes a measurement value in a stored record or event payload. |
| `timestamp_modification` | Changes the measurement timestamp and, for event models, the event timestamp. |
| `record_deletion` | Removes a measurement record or measurement event from the artifact. |
| `fake_record_insertion` | Inserts a synthetic record or event with a fake identifier. |
| `replay` | Re-inserts an existing record or event, creating a duplicate identifier. |
| `broken_provenance` | Replaces the Model D signature/key reference with an unauthorized key. |
| `unauthorized_correction` | Inserts a correction event signed by a key that exists but lacks correction permission. |
| `revoked_actor_key_usage` | Revokes the baseline key before a subsequent measurement event that still uses it. |
| `missing_correction_reason` | Inserts a correction event without a required reason. |
| `delayed_synchronization` | Inserts a synchronization event whose observed delay exceeds the configured maximum allowed delay. |

## Aggregate Status Counts

| Status | Count |
| --- | ---: |
| `detected` | 20 |
| `expected_not_detected` | 5 |
| `missed` | 0 |
| `partial` | 0 |
| `unexpected_alert` | 0 |

Interpretation of statuses:

- `detected`: the verifier produced the expected alert code for the injected scenario.
- `expected_not_detected`: the scenario was intentionally outside the detection capability of that model.
- `not_applicable`: the scenario was not applied to that model in the current implementation.
- `missed`: an expected alert was not produced.
- `partial`: at least one expected alert was produced, but not all expected alerts were present.
- `unexpected_alert`: an alert was produced when none was expected.

## Threat-Coverage Matrix

| Threat | Model A | Model B | Model C | Model D |
| --- | --- | --- | --- | --- |
| `broken_provenance` | `not_applicable` | `not_applicable` | `not_applicable` | `detected` |
| `delayed_synchronization` | `not_applicable` | `not_applicable` | `not_applicable` | `detected` |
| `fake_record_insertion` | `expected_not_detected` | `detected` | `detected` | `detected` |
| `missing_correction_reason` | `not_applicable` | `not_applicable` | `not_applicable` | `detected` |
| `record_deletion` | `expected_not_detected` | `expected_not_detected` | `detected` | `detected` |
| `replay` | `detected` | `detected` | `detected` | `detected` |
| `revoked_actor_key_usage` | `not_applicable` | `not_applicable` | `not_applicable` | `detected` |
| `timestamp_modification` | `expected_not_detected` | `detected` | `detected` | `detected` |
| `unauthorized_correction` | `not_applicable` | `not_applicable` | `not_applicable` | `detected` |
| `value_modification` | `expected_not_detected` | `detected` | `detected` | `detected` |

## Model-Level Reading

Model A detects only the replay scenario in this matrix, because replay creates a duplicate record identifier. It does not contain audit or hash information that would allow the verifier to detect direct value modification, timestamp modification, deletion, or fake insertion.

Model B detects value modification, timestamp modification, fake record insertion, and replay through audit-event integrity checks such as payload hash, event ID, or duplicate ID checks. It does not detect record deletion in this implementation because the audit trail is not hash-linked.

Model C detects all base scenarios implemented for Models A-C. Hash-chain linkage adds the ability to detect deletion and chain-order disruption through previous-hash checks.

Model D detects all Model C scenarios and additionally detects provenance, permission, correction, revoked-key, and delayed-synchronization failures.

## Technical Observations

- The progression from A to D shows increasing threat coverage as audit, hash-chain, and provenance/permission mechanisms are added.
- The current evaluator treats `expected_not_detected` as an expected model limitation, not as an implementation failure.
- The current matrix uses `not_applicable` for scenarios that do not belong to a model's implemented capability set.
- Some scenarios produce additional structural alerts beyond the scenario-specific expected alert. For example, several inserted events also produce `previous_hash_mismatch`. The evaluator marks a scenario as detected when the expected alert code is present.
- The matrix is scenario-based and label-based. It is not yet a statistical evaluation over repeated random injections.

## About Scenario Repetitions

By "scenario repetitions", I mean running the same threat multiple times at different target records, stations, timestamps, or random seeds. The current matrix uses one deterministic injection per applicable model/threat pair. That is enough for a reproducible MVP demonstration, but it does not estimate variability across many possible attack positions.

## Limitations

- The scenario set is controlled and synthetic.
- Each currently implemented scenario has one ground-truth label.
- False-positive rate, false-negative rate, precision, recall, and F1 require an explicit negative-case design before they should be reported.
- Results evaluate integrity-model behavior, not environmental data quality.
- The OpenAQ dataset is used as a realistic distributed environmental monitoring data source, not as evidence for environmental-domain conclusions.

## Review Questions

1. Should additional scenario repetitions be added before manuscript interpretation, or is one deterministic injection per model/threat enough for the MVP?
2. Should `not_applicable` also be written into older smoke-test summaries for consistency?
3. Should delayed synchronization remain Model D only, or should a weaker version be defined for Models B-C?
