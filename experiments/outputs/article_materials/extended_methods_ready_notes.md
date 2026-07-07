# Extended Methods-Ready Notes

Dataset ID: `openaq_capitals_2025_h2`

This file summarizes the extended experiment implementation after the MVP run. It is not manuscript prose.

## Motivation For Extension

The MVP run demonstrated controlled threat-coverage behavior for Models A-D. The extended work addresses reviewer-facing weaknesses:

- lack of negative cases,
- lack of cost measurements,
- lack of explicit threat model,
- lack of external anchoring for privileged chain rewrite attacks.

The current extension implements negative cases, cost analysis, and threat-model artifacts. Repeated injections and Model E anchoring are still planned.

## Negative Cases

Purpose: provide non-tampering cases that allow true-negative and false-positive-rate reporting for the implemented verifier.

Implemented negative cases:

- clean baseline artifact for Model A,
- clean baseline artifact for Model B,
- clean baseline artifact for Model C,
- clean baseline artifact for Model D,
- valid Model D correction with authorized key and correction reason,
- valid Model D synchronization within the allowed delay,
- valid Model D permission grant/revocation sequence without later violation.

Generated outputs:

- `experiments/outputs/metrics/negative/openaq_capitals_2025_h2_negative_case_metrics.csv`
- `experiments/outputs/metrics/negative/openaq_capitals_2025_h2_negative_case_summary.json`
- `experiments/data/negative/`
- `experiments/outputs/verification/negative/`

Important boundary:

These negative cases support a limited false-positive-rate estimate for the implemented verifier on known-valid artifacts. They do not yet provide a full real-world specificity estimate.

## Cost Analysis

Purpose: quantify storage and runtime trade-offs across Models A-D.

Measured cost dimensions:

- artifact size,
- record/event count,
- average bytes per record/event,
- build time,
- clean-artifact verification time,
- mean tampered-artifact verification time,
- number of tampered artifacts verified per model.

Generated outputs:

- `experiments/outputs/cost/openaq_capitals_2025_h2_cost_metrics.csv`
- `experiments/outputs/cost/openaq_capitals_2025_h2_cost_summary.json`
- `experiments/outputs/cost/openaq_capitals_2025_h2_build_costs.csv`
- `experiments/outputs/cost/openaq_capitals_2025_h2_clean_verification_costs.csv`
- `experiments/outputs/cost/openaq_capitals_2025_h2_tampered_verification_costs.csv`

Peak memory is not measured in the current implementation and is marked as `TODO:EXPERIMENT_NEEDED`.

## Threat Model

Purpose: make attacker assumptions and model capabilities explicit.

Generated outputs:

- `experiments/outputs/threat_model/integrity_threat_model.json`
- `experiments/outputs/threat_model/integrity_threat_model.md`

The threat model includes:

- attacker capabilities,
- trusted components,
- out-of-scope attacks,
- mapping from threat to model capability and verifier check,
- a planned Model E row for anchored hash-chain verification.

The taxonomy relation to STRIDE/CIA/provenance remains marked as `TODO:CITATION_NEEDED`.

## Planned Model E

Model E is planned as an anchored extension:

`Audit trail + hash chain + provenance/permission reconstruction + external checkpoint anchoring`

Planned mechanism:

- periodic checkpoints every N events,
- checkpoint stores latest `block_hash`, event index, timestamp, dataset ID, and model ID,
- checkpoints are written to a separate append-only anchor manifest,
- verifier checks whether the local chain matches the external checkpoint record.

Planned scenario:

- `admin_chain_rewrite`

Current implementation status:

Model E and `admin_chain_rewrite` are not yet implemented. They are included in the threat model as planned work because they address the reviewer concern that a local hash chain without external anchoring can be rewritten by a privileged administrator.

## Repeated Injections

Current implementation status:

Repeated injections are not yet implemented.

Planned design:

- deterministic seeds,
- multiple target records,
- multiple stations/locations,
- multiple timestamps,
- repeated runs per applicable model/scenario.

Recommended first target: 10 repetitions per applicable model/scenario, then increase only if runtime remains reasonable.

