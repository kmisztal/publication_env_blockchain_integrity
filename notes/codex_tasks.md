# Codex Tasks

Implementation backlog and status tracker for the proof-of-concept supporting the publication experiments.

## Current MVP Status

The current MVP experiment set is implemented and has been executed once for `openaq_capitals_2025_h2`.

Implemented MVP scope:

- OpenAQ data ingestion and preprocessing.
- Four integrity models: A, B, C, and D.
- Controlled tampering scenarios for the current threat-coverage matrix.
- Verification reports and alert CSV files.
- Per-scenario evaluation and aggregate threat-coverage matrix.
- JSON and Markdown experiment-run manifests.

Accepted MVP limitations:

- Scenario repetitions are not used in the current MVP.
- Negative-case design is not implemented, so precision, recall, F1, false-positive rate, and false-negative rate are deferred.
- `delayed_synchronization` is scoped to Model D only.
- Summary-block optimization is deferred.
- Full intermittent-connectivity simulation is deferred beyond the MVP delayed-synchronization scenario.
- Dashboard work is optional and deferred.

## Scope Guardrails

1. Keep the implementation lightweight.
2. Optimize for reproducible experiments, not production deployment.
3. Do not generate or report experimental results until the experiment run is explicitly requested.
4. Prefer Python, Pandas, SQLite, JSONL, and simple command-line scripts.
5. Treat dashboard work as optional.

## Phase 0: Repository Setup

- [x] Decide implementation folder name: `experiments/`.
- [x] Create package skeleton with `__init__.py`.
- [x] Add output folders under `experiments/`: `data/raw/`, `data/processed/`, `data/tampered/`, `outputs/chains/`, `outputs/audit/`, `outputs/verification/`, `outputs/metrics/`.
- [x] Add `.gitkeep` files where empty folders must be preserved.
- [x] Add a short `README` for running the PoC.
- [x] Confirm generated data and outputs should be gitignored, while placeholder directories stay tracked.

## Phase 1: Data Ingestion and Preprocessing

- [x] Implement CSV ingestion for a frozen public dataset extract.
- [x] Implement dataset manifest creation.
- [x] Implement preprocessing with Pandas for OpenAQ exports.
- [x] Normalize timestamps, station IDs, parameters, units, coordinates, and values.
- [x] Generate deterministic `record_id` values.
- [x] Preserve source rows as JSON payloads.
- [x] Export cleaned data to `experiments/data/processed/`.
- [x] Add preprocessing report with record counts and missing field counts.
- [x] Add an OpenAQ API v3 downloader that freezes a bounded raw JSONL extract when `OPENAQ_API_KEY` is available.

## Phase 2: Storage Layer

- [x] Create SQLite schema for `dataset_manifest`.
- [x] Create SQLite schema for `measurements`.
- [x] Create SQLite schema for `events`.
- [x] Create SQLite schema for `keys`.
- [x] Create SQLite schema for `verification_reports`.
- [x] Create SQLite schema for `tampering_labels`.
- [x] Implement storage helper functions.
- [x] Add reset/init command for local experiment database.

## Phase 3: Event and Hash Chain Core

- [x] Define event types in Python constants or enums.
- [x] Implement deterministic JSON serialization.
- [x] Implement payload hashing.
- [x] Implement block hashing.
- [x] Implement genesis event creation.
- [x] Implement measurement event creation.
- [x] Implement permission event creation.
- [x] Implement correction event creation.
- [x] Implement synchronization event creation for the MVP delayed-synchronization scenario.
- [ ] Implement invalidation event creation. Deferred; not required for the current MVP threat matrix.
- [x] Build ordered hash chain from cleaned measurements.
- [x] Export chains as JSONL.

## Phase 4: Audit Trail Model

- [x] Implement key insertion events.
- [x] Implement key revocation events.
- [x] Implement active key-state reconstruction.
- [x] Implement correction lineage fields.
- [x] Implement validation for correction target existence.
- [x] Implement validation for required correction reason.
- [x] Implement audit event export.

## Phase 5: Verification Engine

- [x] Implement schema validation.
- [x] Implement payload hash recalculation.
- [x] Implement block hash recalculation.
- [x] Implement previous-hash link verification.
- [ ] Implement off-chain measurement hash verification. Deferred; current MVP verifies generated artifacts directly.
- [x] Implement actor key authorization checks.
- [x] Implement correction lineage checks.
- [x] Implement stable alert codes.
- [x] Export `verification_report.json`.
- [x] Export `alerts.csv`.

## Phase 6: Tampering Generator

- [x] Implement value modification scenario.
- [x] Implement timestamp modification scenario.
- [x] Implement record deletion scenario.
- [x] Implement fake record insertion scenario.
- [x] Implement replay scenario.
- [x] Implement broken provenance scenario.
- [x] Implement unauthorized correction scenario.
- [x] Implement revoked actor key usage scenario.
- [x] Implement missing correction reason scenario.
- [x] Implement delayed synchronization scenario.
- [x] Generate ground-truth labels for every implemented scenario.
- [x] Save tampered datasets and labels under `data/tampered/`.

## Phase 7: Metrics

- [x] Compare verifier alerts against tampering labels.
- [x] Compute detection rate.
- [ ] Compute false positive rate. Deferred until negative cases are defined.
- [ ] Compute false negative rate. Deferred until negative cases are defined.
- [ ] Compute precision. Deferred until negative cases are defined.
- [ ] Compute recall. Deferred until negative cases are defined.
- [ ] Compute F1 score. Deferred until negative cases are defined.
- [ ] Compute attack-type-specific metrics beyond the current scenario matrix. Deferred.
- [x] Export metrics tables to `outputs/metrics/`.

## Phase 8: Summary Blocks

- [ ] Implement optional summary-block generation. Deferred extension.
- [ ] Implement summary hash calculation. Deferred extension.
- [ ] Include previous summary hash. Deferred extension.
- [ ] Include covered block hash list or digest. Deferred extension.
- [ ] Include active key-state digest. Deferred extension.
- [ ] Implement summary-block verification. Deferred extension.
- [ ] Add summary-block metrics hooks. Deferred extension.

## Phase 9: Intermittent Connectivity Simulation

- [x] Implement MVP delayed-synchronization event verification.
- [ ] Partition data by station or gateway. Deferred beyond current MVP.
- [ ] Build local gateway chains. Deferred beyond current MVP.
- [ ] Simulate offline windows. Deferred beyond current MVP.
- [ ] Queue local events during offline periods. Deferred beyond current MVP.
- [ ] Synchronize summary hashes to central verifier. Deferred beyond current MVP.
- [ ] Inject tampering during offline periods. Deferred beyond current MVP.
- [ ] Verify delayed detection after synchronization. Deferred beyond current MVP full-connectivity simulation.

## Phase 10: Reporting

- [x] Generate machine-readable verification reports.
- [x] Generate Markdown experiment summaries without manuscript interpretation.
- [x] Generate article-preparation source materials without drafting manuscript prose.
- [ ] Generate architecture diagram source if needed. Optional.
- [x] Generate experiment run manifest.
- [x] Document exact dataset extract used.

## Optional Phase 11: Dashboard

- [ ] Decide whether dashboard is needed. Optional after CLI workflow review.
- [ ] If yes, choose Django, Streamlit, or static HTML. Optional.
- [ ] Add measurement browser. Optional.
- [ ] Add chain event browser. Optional.
- [ ] Add verification alert browser. Optional.
- [ ] Add correction lineage view. Optional.
- [ ] Add filters for station, event type, and alert code. Optional.

## MVP Task Set Status

Minimum implemented tasks before reviewing publication experiment outputs:

- [x] Phase 0 repository setup.
- [x] Phase 1 ingestion and preprocessing.
- [x] Phase 2 SQLite storage.
- [x] Phase 3 event and hash-chain core for the current MVP.
- [x] Phase 4 basic audit trail.
- [x] Phase 5 verification engine for the current MVP.
- [x] Phase 6 tampering generator.
- [x] Phase 7 metrics export for scenario status and threat coverage.
- [x] Phase 10 experiment-run manifest.

Remaining MVP review tasks:

- [ ] Review `experiments/outputs/full_matrix_summary_en.md`.
- [ ] Review `experiments/outputs/full_matrix_summary_pl.md`.
- [ ] Review `experiments/outputs/manifests/openaq_capitals_2025_h2_experiment_run_manifest.md`.
- [ ] Review `experiments/outputs/article_materials/methods_ready_notes.md`.
- [ ] Review `experiments/outputs/article_materials/results_ready_tables.md`.
- [ ] Review `experiments/outputs/article_materials/reviewer_limitations.md`.
- [ ] Review `experiments/outputs/article_materials/methodology_decisions.md`.
- [ ] Decide whether current model and scenario names are final enough for manuscript preparation.
- [ ] Decide whether architecture diagrams are needed before writing manuscript sections.

## Deferred Tasks

- [ ] Invalidation event support, if invalidation becomes part of the experiment scope.
- [ ] Off-chain measurement hash verification, if artifact/source separation becomes necessary.
- [ ] Negative-case design for false positives, false negatives, precision, recall, and F1.
- [ ] Summary-block optimization if MVP is stable.
- [ ] Full intermittent-connectivity simulation beyond the current Model D delayed-synchronization scenario.
- [ ] Water-quality replication if broader domain validation is needed.
- [ ] Provenance graph export if audit visualization becomes important.
- [ ] Dashboard only after CLI workflow is reliable and a visual review tool is useful.
