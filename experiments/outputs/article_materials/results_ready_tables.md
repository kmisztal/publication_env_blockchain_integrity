# Results-Ready Tables

Dataset ID: `openaq_capitals_2025_h2`

This file collects tables and numeric outputs for later review and manuscript preparation. It is not a manuscript results section.

## Dataset Preparation Summary

| Item | Value |
| --- | ---: |
| Input OpenAQ records | `116361` |
| Canonical records after preprocessing | `112973` |
| Dropped records | `3388` |
| Selected monitoring locations | `12` |
| Cities | `4` |
| Monitoring locations per city | `3` |
| Parameters after preprocessing | `9` |

## Model Definitions

| Model | Short description | Main verification capability |
| --- | --- | --- |
| A | Conventional storage only | Schema and duplicate record checks |
| B | Audit trail only | Event payload and event identifier checks |
| C | Audit trail plus hash chain | Payload checks plus chain-continuity checks |
| D | Hash chain plus provenance and permissions | Chain checks plus actor/key, permission, correction, provenance, and delayed-synchronization checks |

## Scenario Definitions

| Scenario | Description |
| --- | --- |
| `value_modification` | Changes a measurement value in a record or event payload. |
| `timestamp_modification` | Changes the measurement timestamp and, for event models, the event timestamp. |
| `record_deletion` | Removes a measurement record or measurement event. |
| `fake_record_insertion` | Inserts a synthetic record or event with a fake identifier. |
| `replay` | Re-inserts an existing record or event, creating a duplicate identifier. |
| `broken_provenance` | Replaces a Model D signature/key reference with an unauthorized key. |
| `unauthorized_correction` | Inserts a correction event signed by a key without correction permission. |
| `revoked_actor_key_usage` | Revokes the baseline key before a subsequent event that still uses it. |
| `missing_correction_reason` | Inserts a correction event without the required correction reason. |
| `delayed_synchronization` | Inserts a synchronization event whose observed delay exceeds the allowed threshold. |

## Scenario Run Counts

| Item | Count |
| --- | ---: |
| Models compared | `4` |
| Scenarios executed | `25` |
| Scenario labels | `25` |
| Per-scenario verification outputs | `25` |
| Per-scenario evaluation outputs | `25` |

## Aggregate Status Counts

| Status | Count |
| --- | ---: |
| `detected` | `20` |
| `expected_not_detected` | `5` |
| `missed` | `0` |
| `partial` | `0` |
| `unexpected_alert` | `0` |

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

## Applicable Scenario Coverage

These counts treat `not_applicable` cells as outside a model's implemented scope and treat `expected_not_detected` as an explicit model limitation.

| Model | Applicable scenarios | Detected | Expected not detected | Missed/partial/unexpected |
| --- | ---: | ---: | ---: | ---: |
| A | `5` | `1` | `4` | `0` |
| B | `5` | `4` | `1` | `0` |
| C | `5` | `5` | `0` | `0` |
| D | `10` | `10` | `0` | `0` |

## Artifact References

| Artifact | Path |
| --- | --- |
| Scenario metrics | `experiments/outputs/metrics/openaq_capitals_2025_h2_scenario_metrics.csv` |
| Threat-coverage matrix | `experiments/outputs/metrics/openaq_capitals_2025_h2_threat_coverage_matrix.csv` |
| Metrics summary | `experiments/outputs/metrics/openaq_capitals_2025_h2_metrics_summary.json` |
| Experiment run manifest | `experiments/outputs/manifests/openaq_capitals_2025_h2_experiment_run_manifest.json` |

