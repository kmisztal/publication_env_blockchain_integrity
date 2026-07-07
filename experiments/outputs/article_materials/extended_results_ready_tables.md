# Extended Results-Ready Tables

Dataset ID: `openaq_capitals_2025_h2`

This file collects measured outputs from the extended experiment artifacts. It is not a manuscript results section.

## Negative Case Summary

| Metric | Value |
| --- | ---: |
| Negative cases executed | `7` |
| True negatives | `7` |
| False positives | `0` |
| Limited false-positive rate | `0.000000` |

Negative cases included clean artifacts for Models A-D plus three valid Model D governance/synchronization operations.

## Negative Case Table

| Case type | Model | Alerts | Status |
| --- | --- | ---: | --- |
| `clean_baseline` | `A_conventional_storage` | `0` | `true_negative` |
| `clean_baseline` | `B_audit_trail` | `0` | `true_negative` |
| `clean_baseline` | `C_audit_hash_chain` | `0` | `true_negative` |
| `clean_baseline` | `D_audit_hash_chain_provenance` | `0` | `true_negative` |
| `valid_correction` | `D_audit_hash_chain_provenance` | `0` | `true_negative` |
| `valid_synchronization` | `D_audit_hash_chain_provenance` | `0` | `true_negative` |
| `valid_permission_grant_revocation` | `D_audit_hash_chain_provenance` | `0` | `true_negative` |

## Cost Metrics

| Model | Artifact size bytes | Records/events | Bytes per record/event | Build time s | Clean verification time s | Mean tampered verification time s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `A_conventional_storage` | `241682171` | `112973` | `2139.291432` | `194.281174` | `3.778977` | `4.163753` |
| `B_audit_trail` | `107560619` | `112974` | `952.082948` | `194.281174` | `11.937228` | `9.020966` |
| `C_audit_hash_chain` | `122134203` | `112974` | `1081.082399` | `294.323177` | `15.788794` | `9.248757` |
| `D_audit_hash_chain_provenance` | `126089123` | `112975` | `1116.079867` | `204.027212` | `11.598773` | `14.721215` |

## Cost Metric Notes

- Model A stores full canonical records and is therefore largest in this implementation.
- Model B-D event artifacts are smaller per event than Model A records because event payloads store normalized integrity payloads rather than the full canonical source-preservation fields.
- Model C has the longest measured clean verification time in this run.
- Model D has the highest mean tampered verification time because it has more applicable tampering scenarios and provenance/permission checks.
- Peak memory is not measured: `TODO:EXPERIMENT_NEEDED`.

## Threat Model Outputs

| Artifact | Path |
| --- | --- |
| Threat model JSON | `experiments/outputs/threat_model/integrity_threat_model.json` |
| Threat model Markdown | `experiments/outputs/threat_model/integrity_threat_model.md` |

Threat model scope includes 11 threats, including planned `admin_chain_rewrite` for Model E.

## Extended Artifact References

| Artifact | Path |
| --- | --- |
| Negative case metrics | `experiments/outputs/metrics/negative/openaq_capitals_2025_h2_negative_case_metrics.csv` |
| Negative case summary | `experiments/outputs/metrics/negative/openaq_capitals_2025_h2_negative_case_summary.json` |
| Cost metrics | `experiments/outputs/cost/openaq_capitals_2025_h2_cost_metrics.csv` |
| Cost summary | `experiments/outputs/cost/openaq_capitals_2025_h2_cost_summary.json` |
| Build costs | `experiments/outputs/cost/openaq_capitals_2025_h2_build_costs.csv` |
| Clean verification costs | `experiments/outputs/cost/openaq_capitals_2025_h2_clean_verification_costs.csv` |
| Tampered verification costs | `experiments/outputs/cost/openaq_capitals_2025_h2_tampered_verification_costs.csv` |

## Not Yet Implemented

The following requested extensions remain pending:

- repeated injections,
- Model E anchored hash-chain artifacts,
- `admin_chain_rewrite` scenario,
- extended threat-coverage matrix including measured Model E outputs.

These should remain marked as future or pending until implemented and executed.

