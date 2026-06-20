# Changelog

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
