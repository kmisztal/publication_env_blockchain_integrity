# Codex Tasks

Implementation backlog for the proof-of-concept supporting the publication experiments.

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
- [ ] Implement correction and invalidation event creation.
- [x] Build ordered hash chain from cleaned measurements.
- [x] Export chains as JSONL.

## Phase 4: Audit Trail Model

- [x] Implement key insertion events.
- [ ] Implement key revocation events.
- [x] Implement active key-state reconstruction.
- [ ] Implement correction lineage fields.
- [ ] Implement validation for correction target existence.
- [ ] Implement validation for required correction reason.
- [x] Implement audit event export.

## Phase 5: Verification Engine

- [x] Implement schema validation.
- [x] Implement payload hash recalculation.
- [x] Implement block hash recalculation.
- [x] Implement previous-hash link verification.
- [ ] Implement off-chain measurement hash verification.
- [x] Implement actor key authorization checks.
- [ ] Implement correction lineage checks.
- [x] Implement stable alert codes.
- [x] Export `verification_report.json`.
- [x] Export `alerts.csv`.

## Phase 6: Tampering Generator

- [ ] Implement value modification scenario.
- [ ] Implement timestamp modification scenario.
- [ ] Implement record deletion scenario.
- [ ] Implement fake record insertion scenario.
- [ ] Implement replay scenario.
- [ ] Implement broken provenance scenario.
- [ ] Implement unauthorized correction scenario.
- [ ] Generate ground-truth labels for every scenario.
- [ ] Save tampered datasets and labels under `data/tampered/`.

## Phase 7: Metrics

- [ ] Compare verifier alerts against tampering labels.
- [ ] Compute detection rate.
- [ ] Compute false positive rate.
- [ ] Compute false negative rate.
- [ ] Compute precision.
- [ ] Compute recall.
- [ ] Compute F1 score.
- [ ] Compute attack-type-specific metrics.
- [ ] Export metrics tables to `outputs/metrics/`.

## Phase 8: Summary Blocks

- [ ] Implement optional summary-block generation.
- [ ] Implement summary hash calculation.
- [ ] Include previous summary hash.
- [ ] Include covered block hash list or digest.
- [ ] Include active key-state digest.
- [ ] Implement summary-block verification.
- [ ] Add summary-block metrics hooks.

## Phase 9: Intermittent Connectivity Simulation

- [ ] Partition data by station or gateway.
- [ ] Build local gateway chains.
- [ ] Simulate offline windows.
- [ ] Queue local events during offline periods.
- [ ] Synchronize summary hashes to central verifier.
- [ ] Inject tampering during offline periods.
- [ ] Verify delayed detection after synchronization.

## Phase 10: Reporting

- [ ] Generate machine-readable verification reports.
- [ ] Generate Markdown report templates without interpreting results.
- [ ] Generate architecture diagram source if needed.
- [ ] Generate experiment run manifest.
- [ ] Document exact dataset extract used.

## Optional Phase 11: Dashboard

- [ ] Decide whether dashboard is needed.
- [ ] If yes, choose Django, Streamlit, or static HTML.
- [ ] Add measurement browser.
- [ ] Add chain event browser.
- [ ] Add verification alert browser.
- [ ] Add correction lineage view.
- [ ] Add filters for station, event type, and alert code.

## MVP Task Set

Minimum tasks before running publication experiments:

- [x] Phase 0 repository setup.
- [x] Phase 1 ingestion and preprocessing.
- [x] Phase 2 SQLite storage.
- [ ] Phase 3 event and hash-chain core.
- [ ] Phase 4 basic audit trail.
- [ ] Phase 5 verification engine.
- [ ] Phase 6 tampering generator.
- [ ] Phase 7 metrics export.

## Deferred Tasks

- [ ] Summary-block optimization if MVP is stable.
- [ ] Intermittent connectivity simulation if time remains.
- [ ] Water-quality replication if broader domain validation is needed.
- [ ] Provenance graph export if audit visualization becomes important.
- [ ] Dashboard only after CLI workflow is reliable.
