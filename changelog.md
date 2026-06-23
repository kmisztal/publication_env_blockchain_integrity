# Changelog

## 2026-06-23 19:07:46 +02:00

- Added `experiments/outputs/full_matrix_summary_en.md` as an English review summary of the executed full scenario matrix.
- Added `experiments/outputs/full_matrix_summary_pl.md` as a Polish review summary of the executed full scenario matrix.
- Both summaries describe scope, output files, models, aggregate status counts, the threat-coverage matrix, model-level reading, limitations, and review questions.
- The summaries are experiment review artifacts, not manuscript sections.

## 2026-06-23 19:01:10 +02:00

- Executed the full implemented `openaq_capitals_2025_h2` scenario matrix with `run-scenarios --verify`.
- Generated tampered artifacts, per-scenario verification reports, alert CSV files, and evaluation JSON files for 24 scenarios.
- Aggregated the full scenario evaluations into `experiments/outputs/metrics/openaq_capitals_2025_h2_scenario_metrics.csv`.
- Generated the threat-coverage matrix at `experiments/outputs/metrics/openaq_capitals_2025_h2_threat_coverage_matrix.csv`.
- Generated the metrics summary at `experiments/outputs/metrics/openaq_capitals_2025_h2_metrics_summary.json`.
- Full matrix status counts: 19 `detected`, 5 `expected_not_detected`, 0 `missed`, 0 `partial`, and 0 `unexpected_alert`.
- These are measured PoC verification outputs from the implemented scenarios; manuscript interpretation remains a later step.

## 2026-06-23 18:49:24 +02:00

- Added Model D correction payload construction and `correct_measurement` permission support.
- Extended Model D verification with correction target checks, required correction reason checks, event authorization checks, and revoked-key usage checks.
- Added controlled Model D tampering scenarios for `unauthorized_correction`, `revoked_actor_key_usage`, and `missing_correction_reason`.
- Updated scenario batch verification so each scenario writes verifier outputs to a separate subdirectory, avoiding alert/report overwrites for repeated model IDs.
- Rebuilt the local Model D artifact so the baseline ingest key includes `correct_measurement`.
- Ran baseline verification for the rebuilt Model D artifact as a construction sanity check.
- Ran smoke-test generation, verification, evaluation, and aggregation for the three new Model D scenarios; these were tool-chain checks only, not a full experiment run or final threat-coverage matrix.
- Updated `experiments/README.md`, `DEVELOPMENT_PROGRESS.md`, `experiments/outputs/demo_overview.md`, and `notes/codex_tasks.md`.

## 2026-06-23 18:38:08 +02:00

- Extended `experiments/integrity/evaluation.py` with aggregate metrics table export from per-scenario evaluation JSON files.
- Added `aggregate-metrics` to `experiments.integrity.cli`.
- Added the PDM script `integrity-aggregate-metrics`.
- The aggregator writes scenario metrics CSV, threat coverage matrix CSV, and metrics summary JSON files.
- Ran one smoke-test aggregation from the existing Model C `value_modification` smoke evaluation file; this was a format check only, not a full experiment run or final threat-coverage matrix.
- Updated `experiments/README.md`, `DEVELOPMENT_PROGRESS.md`, `experiments/outputs/demo_overview.md`, and `notes/codex_tasks.md`.

## 2026-06-23 18:33:16 +02:00

- Added `experiments/integrity/evaluation.py` for comparing tampering label files against verifier alert CSV files.
- Added `evaluate` to `experiments.integrity.cli`.
- Added the PDM script `integrity-evaluate`.
- Connected `run-scenarios --verify` to produce per-scenario evaluation JSON files under `experiments/outputs/metrics/tampered/`.
- Ran one smoke-test verification and evaluation for the existing Model C `value_modification` tampered artifact; this was a tool-chain check only, not a full experiment run or threat-coverage result.
- Updated `experiments/README.md`, `DEVELOPMENT_PROGRESS.md`, `experiments/outputs/demo_overview.md`, and `notes/codex_tasks.md`.

## 2026-06-23 18:26:59 +02:00

- Added `experiments/integrity/scenarios.py` as a scenario matrix planner and optional batch runner.
- Added `run-scenarios` to `experiments.integrity.cli`.
- Added the PDM script `integrity-run-scenarios`.
- Added `--dry-run` support for previewing planned model/threat combinations without generating full scenario artifacts.
- Ran a dry run for `openaq_capitals_2025_h2`; it planned 21 implemented scenarios across Models A-D.
- Did not execute the full scenario matrix or generate threat-coverage summaries in this step.

## 2026-06-23 18:23:16 +02:00

- Added `experiments/integrity/tampering.py` as a controlled tampering artifact generator.
- Added `tamper` to `experiments.integrity.cli`.
- Added the PDM script `integrity-tamper`.
- Implemented value modification, timestamp modification, record deletion, fake record insertion, replay, and Model D broken provenance scenarios.
- Added ground-truth label JSON generation for implemented tampering scenarios.
- Ran one smoke-test tampering generation for `openaq_capitals_2025_h2`, Model C, `value_modification`; this was a generator check only, not a full experiment run or threat-coverage result.
- Documented the tampering generator workflow in `experiments/README.md` and updated `DEVELOPMENT_PROGRESS.md` and `notes/codex_tasks.md`.

## 2026-06-22 05:45:24 +02:00

- Added `experiments/integrity/verification.py` as a baseline verifier for generated Model A-D artifacts.
- Added `verify` to `experiments.integrity.cli`.
- Added the PDM script `integrity-verify`.
- Implemented schema checks, duplicate ID checks, payload hash recalculation, block hash recalculation, previous-hash verification, and Model D active-key checks.
- Generated baseline verification reports and alert CSV files for the current non-tampered `openaq_capitals_2025_h2` Model A-D artifacts.
- Treated these reports as technical sanity checks only, not threat-coverage or detection-rate results.

## 2026-06-22 05:31:51 +02:00

- Added `experiments/outputs/demo_overview.md` as a local demonstration overview of the current PoC construction state.
- Summarized the prepared OpenAQ dataset, Model A-D artifacts, and construction sanity checks.
- Explicitly marked the overview as non-results documentation without threat-coverage, verifier-output, or detection-rate claims.

## 2026-06-22 05:28:50 +02:00

- Added Model D provenance/permission event construction using a deterministic ingest actor key and permission grant event.
- Added active key-state reconstruction from permission and revocation events.
- Added `build-provenance-chain` to `experiments.integrity.cli`.
- Added the PDM script `integrity-build-provenance-chain`.
- Built local Model D artifacts for `openaq_capitals_2025_h2`: 112,975 events including one genesis event, one permission event, and 112,973 measurement events.
- Confirmed Model D JSONL line count and SQLite audit-event row count both equal 112,975.
- Ran a structural Model D check: no broken previous-hash links, terminal block hash matches the summary artifact, and all measurement events reference an active reconstructed key.
- Treated Model D construction checks as reproducibility sanity checks only, not threat-verification results.

## 2026-06-22 05:17:16 +02:00

- Added Model C hash-chain event construction using deterministic `previous_hash` and `block_hash` linkage.
- Added `build-hash-chain` to `experiments.integrity.cli`.
- Added the PDM script `integrity-build-hash-chain`.
- Built local Model C artifacts for `openaq_capitals_2025_h2`: 112,974 events including one genesis event.
- Confirmed Model C JSONL line count and SQLite audit-event row count both equal 112,974.
- Ran a structural chain check over the generated JSONL and found no broken previous-hash links; the terminal block hash matches the summary artifact.
- Treated Model C construction checks as reproducibility sanity checks only, not threat-verification results.

## 2026-06-22 04:56:54 +02:00

- Added generic integrity-model modules under `experiments/integrity/`.
- Implemented deterministic event construction for baseline genesis and measurement audit events.
- Added Model A conventional-storage artifact export and Model B audit-trail artifact export.
- Added `experiments.integrity.cli` with `init-db` and `build-baseline` commands.
- Added PDM scripts `integrity-init-db` and `integrity-build-baseline`.
- Optimized SQLite audit-event loading with direct `executemany` insertion.
- Made baseline Model B genesis timestamp deterministic by deriving it from canonical measurement metadata.
- Built local baseline artifacts for `openaq_capitals_2025_h2`: 112,973 Model A records and 112,974 Model B audit events.
- Verified Model B JSONL line count and SQLite audit-event row count both equal 112,974.
- Treated baseline artifacts as reproducibility inputs only, not scientific results or threat-verification outputs.

## 2026-06-22 04:38:23 +02:00

- Confirmed the full OpenAQ capital-triangle extract `openaq_capitals_2025_h2` was ingested from local frozen data.
- Recorded ingestion artifact summary: 116,361 input records, 112,973 canonical records, 3,388 dropped records due to missing measurement values, 12 stations, and 9 parameters.
- Confirmed generated map artifact exists at `experiments/outputs/maps/openaq_capitals_2025_h2_sensor_map.html`.
- Checked selected station triangle geometry for Warsaw, Berlin, Paris, and Madrid; each city center is inside the selected three-station triangle.
- Treated these as data-preparation checks only, not scientific results or model verification outputs.

## 2026-06-22 03:32:30 +02:00

- Inspected local OpenAQ `openaq_warsaw_test2` artifacts generated after the area-aware selector update.
- Confirmed `openaq_warsaw_test2` contains 31,187 raw records and 31,147 canonical records after ingestion; 40 records were dropped due to missing values.
- Confirmed the regenerated Warsaw selection forms a usable triangle: Piastów, Legionowo, and Otwock, with approximate area 360.86 km².
- Checked existing Berlin, Paris, and Madrid triangle geometries from local `openaq_mvp` metadata:
  - Berlin: approximate area 576.05 km², city center inside triangle.
  - Paris: approximate area 359.17 km², city center inside triangle.
  - Madrid: approximate area 281.60 km², city center inside triangle.
- These checks are data-preparation sanity checks only, not integrity experiment results.

## 2026-06-21 02:49:42 +02:00

- Fixed OpenAQ measurement downloading for requests where `--measurements-per-sensor` is greater than the API's per-request limit of 1000.
- Added internal pagination so `--measurements-per-sensor 5000` is treated as a total target per sensor and downloaded in pages of at most 1000 records.
- Improved resume behavior after failed downloads: failed sensors are no longer marked complete, and stale state is ignored when no raw output file exists.
- Documented the OpenAQ per-request measurement limit in `experiments/README.md` and `DEVELOPMENT_PROGRESS.md`.
- Did not run a new data download in this step.

## 2026-06-21 02:15:53 +02:00

- Checked the current Warsaw OpenAQ selection and confirmed it is nearly collinear: the selected points have an approximate triangle area of only 0.2 km².
- Replaced sector-only three-location selection with an area- and center-aware combination search.
- The updated selector now scores three-location combinations using measurement availability, triangle area, and whether the city center lies inside the triangle.
- Documented that the current local 2025 capital-triangle metadata should be regenerated before finalizing the MVP dataset.
- Did not run a new data download in this step.

## 2026-06-20 20:26:08 +02:00

- Added process-local OpenAQ request pacing with a default of 55 requests per minute.
- Added `--rate-limit-per-minute` to the OpenAQ downloader CLI.
- Updated `_api_get` to inspect rate-limit remaining/reset headers when OpenAQ returns them.
- Updated documentation to recommend `--rate-limit-per-minute 55` as a conservative default below the commonly documented 60 requests per minute client limit.
- Did not run a new data download in this step.

## 2026-06-20 20:14:16 +02:00

- Added retry/backoff handling for OpenAQ API HTTP 429, 500, 502, 503, and 504 responses.
- Updated OpenAQ candidate scoring to skip a failing location or sensor after retry attempts instead of aborting the entire download.
- Added `--max-retries` and `--retry-backoff-seconds` to the OpenAQ downloader CLI.
- Added `--min-location-distance-meters` to avoid selecting monitoring locations that are too close together within a city.
- Added `experiments/openaq/map.py` for generating static HTML maps from OpenAQ download metadata.
- Added `pdm run openaq-map` and `experiments/outputs/maps/` for local map inspection artifacts.
- Updated `experiments/README.md` and `DEVELOPMENT_PROGRESS.md` with distance, retry, resume, progress, and map commands.
- Did not run a new data download in this step.

## 2026-06-20 20:03:29 +02:00

- Added resumable OpenAQ measurement downloading with a per-sensor state file under `experiments/data/raw/`.
- Added `--resume` and `--progress` options to the OpenAQ downloader CLI.
- Updated the recommended capital-triangle workflow to use the candidate time window 2025-07-01 to 2025-12-31.
- Documented that the 2025 window remains subject to per-location availability checks before final dataset freeze.
- Updated `experiments/README.md`, `DEVELOPMENT_PROGRESS.md`, and `notes/decisions.md` accordingly.
- Did not run a new data download in this step.

## 2026-06-20 19:57:56 +02:00

- Added OpenAQ capital-triangle selection support for Warsaw, Berlin, Paris, and Madrid.
- Extended `experiments/openaq/download.py` to score candidate city locations by measurement availability in the requested time window.
- Added geographic selection logic that prefers three separated monitoring locations around each city center.
- Extended the OpenAQ CLI with `--selection-mode capital-triangles`, `--city`, `--locations-per-city`, `--sensors-per-location`, `--city-radius-meters`, and `--candidate-locations-per-city`.
- Updated `experiments/README.md` and `DEVELOPMENT_PROGRESS.md` with the recommended capital-triangle download workflow.
- Added Decision 10 to `notes/decisions.md` documenting city-centered, high-availability OpenAQ location selection.

## 2026-06-20 19:44:32 +02:00

- Added `experiments/openaq/API_KEY` to `.gitignore` after the local OpenAQ API key file was provided.
- Updated `DEVELOPMENT_PROGRESS.md` to document that the local API key file is ignored and must not be committed.
- Downloaded a bounded OpenAQ API v3 MVP extract for `openaq_mvp` using the local API key file.
- Initial 2026-06-01 to 2026-06-08 query returned zero measurements for the selected Polish sensors; metadata showed the selected sensors were active around 2016-2017.
- Re-ran the download for 2016-12-01 to 2016-12-08 and froze 600 raw OpenAQ measurement records locally.
- Installed PDM dependencies into the provided virtual environment, including `pandas 3.0.3`.
- Updated OpenAQ ingestion to read JSONL through `pandas.json_normalize` and to use `period.datetimeFrom.utc` for OpenAQ v3 measurement timestamps.
- Ingested the frozen OpenAQ extract into canonical measurement artifacts and SQLite: 600 records, 0 dropped records, 2 stations, and 5 parameters.
- Updated `.gitignore` for local Python cache files, `.python-version`, and `experiments/data/*.sqlite`.
- These are data-preparation artifacts only; no integrity-model verification results or threat-coverage matrix were generated.

## 2026-06-20 19:33:29 +02:00

- Added `experiments/openaq/download.py` for freezing bounded OpenAQ API v3 extracts as raw JSONL artifacts.
- Extended the OpenAQ CLI with `download`, using `OPENAQ_API_KEY` or `--api-key-file`.
- Changed OpenAQ CLI imports to be command-specific so downloader help and downloads do not require `pandas`.
- Updated OpenAQ ingestion field mapping for API v3 records, including `datetimeFrom.utc`, `sensor.parameter.*`, and `sensor.location.*` fields.
- Added a `pdm run openaq-download` script in `pyproject.toml`.
- Added `pdm.lock` for the declared PDM dependency set.
- Updated `experiments/README.md` and `DEVELOPMENT_PROGRESS.md` with the download and ingestion workflow.
- Updated `notes/codex_tasks.md` to mark OpenAQ API v3 downloader support as implemented.
- Did not download real OpenAQ data or generate experiment results in this step.

## 2026-06-20 19:22:54 +02:00

- Added `pyproject.toml` for PDM-managed experiment dependencies and scripts.
- Documented the project virtual environment path `e:\git_venv\dicella\env_blockchain_integrity\` in `experiments/README.md` and `DEVELOPMENT_PROGRESS.md`.
- Updated the OpenAQ ingestion examples to use `pdm run openaq-ingest`.
- Verified that PDM is available in the provided virtual environment as version 2.27.0.
- Verified that the provided virtual environment uses Python 3.14.0.
- Noted that `pandas` is not installed in the provided virtual environment yet; it is declared as a PDM dependency and should be installed with `pdm install`.
- Added `.venv/` to `.gitignore` because the intended environment is `e:\git_venv\dicella\env_blockchain_integrity\`, not a project-local virtual environment.
- Added `.pdm-python` to `.gitignore` because it is a local PDM interpreter selection file.

## 2026-06-20 19:16:32 +02:00

- Started the proof-of-concept experiment implementation under `experiments/`.
- Added reusable experiment utilities in `experiments/common/` for paths, deterministic hashing, canonical schema definitions, dataset manifests, and SQLite storage.
- Added OpenAQ-specific ingestion in `experiments/openaq/` for frozen local CSV, JSON, or JSONL exports, including canonical measurement normalization, deterministic `record_id` generation, raw payload preservation, preprocessing reports, and manifest creation.
- Added `experiments/README.md` with the current ingestion workflow.
- Added `DEVELOPMENT_PROGRESS.md` to track implementation status, package structure, current OpenAQ workflow, explicit non-results, and next development steps.
- Added experiment data and output directories with `.gitkeep` placeholders and updated `.gitignore` so generated data and outputs are not tracked by default.
- Updated `notes/codex_tasks.md` to mark completed Phase 0 setup and initial Phase 1 ingestion tasks.

## 2026-06-20 18:54:20 +02:00

- Updated scope across planning notes to position the paper primarily as a computer science / information systems contribution.
- De-emphasized environmental engineering outcomes, sensor calibration science, pollutant-specific interpretation, environmental policy impact, and field deployment claims.
- Redesigned the MVP experimental plan around threat coverage across four integrity models: conventional storage only, audit trail only, audit trail plus hash chain, and audit trail plus hash chain plus provenance/permission reconstruction.
- Updated `notes/poc_architecture.md` to support model comparison, threat injection, model-specific verification, and threat-coverage matrix generation.
- Updated `notes/outline.md`, `notes/paper_context.md`, and `notes/decisions.md` to align the manuscript with data integrity, audit trail architecture, provenance verification, threat modeling, controlled tampering, and reproducible proof-of-concept evaluation.

## 2026-06-20 18:37:51 +02:00

- Drafted `sections/02_related_work.tex` as a structured literature review skeleton covering environmental monitoring systems, rural IoT monitoring, environmental sensor networks, data provenance, data integrity, blockchain for environmental systems, audit trails, hash verification, and literature gaps.
- Used LaTeX-safe `TODO:CITATION_NEEDED` placeholders without inventing references.

## 2026-06-20 18:33:14 +02:00

- Compiled the manuscript to `build/main.pdf` using MiKTeX `pdflatex`.
- Copied the generated PDF to root-level `main.pdf`.
- Escaped LaTeX TODO markers with underscores in `sections/01_introduction.tex` and `sections/02_related_work.tex` so the manuscript compiles.

## 2026-06-20 18:25:38 +02:00

- Drafted `sections/01_introduction.tex` in scientific journal style, covering environmental monitoring data integrity, sensor-network challenges, provenance, blockchain-inspired audit trails, transfer from regulated environments, research gap, research question, and objectives.
- Added `TODO:CITATION_NEEDED` markers where literature support is required.

## 2026-06-20 18:19:46 +02:00

- Created `notes/poc_architecture.md` describing the lightweight proof-of-concept architecture, data flow, data model, hashing strategy, audit trail model, and verification workflow.
- Replaced the placeholder `notes/codex_tasks.md` with a detailed implementation backlog for the PoC.

## 2026-06-20 18:14:45 +02:00

- Created `notes/experimental_plan.md` with an executable MVP and extended experiment set for environmental data integrity, audit trails, hash verification, tampering detection, provenance verification, and blockchain-inspired architecture.
- Added verified candidate public data sources for OpenAQ, EPA AQS, Water Quality Portal, and NOAA/NCEI CDO without generating results or claiming dataset availability beyond source suitability.

## 2026-06-20 18:06:32 +02:00

- Renamed `BLOCKCHAIN_PANTENT.md` to `BLOCKCHAIN_PATENT.md`.
- Updated the opening note in `BLOCKCHAIN_PATENT.md` after correcting the filename.

## 2026-06-20 18:05:04 +02:00

- Reviewed blockchain patent-related PDF resources in `resources/`: `US11985227.pdf`, `Springer_Lecture_Notes_in_Computer_Science.pdf`, and `CISIM_presentaion.pdf`.
- Created `BLOCKCHAIN_PANTENT.md` summarizing the patent approach and how it can inform the environmental monitoring article.
- Identified semi-decentralized verification, summary blocks, signed transactions, permission chains, and central hash verification as reusable design concepts for the manuscript.

## 2026-06-20 01:38:26 +02:00

- Added `resources/krzysztof_misztal_citations.bib` as author background context in `notes/paper_context.md`.
- Added a scientific decision in `notes/decisions.md` to treat the author's BibTeX file as background and possible self-citation context, not as automatic evidence for environmental monitoring claims.

## 2026-06-20 01:32:35 +02:00

- Created `notes/paper_context.md` with research problem, gap, question, objectives, hypotheses, expected contribution, venue suitability, scope, and out-of-scope boundaries.
- Created `notes/decisions.md` to capture scientific direction and open research-design decisions.
- Updated `notes/outline.md` from a short section list into a detailed planning outline.
- Established repository change tracking in this `changelog.md` file.
