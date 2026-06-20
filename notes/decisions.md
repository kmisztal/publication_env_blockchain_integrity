# Scientific Decisions

This file records scope and design decisions before manuscript writing starts.

## 2026-06-20

### Decision 1: Treat the paper as a cross-domain integrity framework

The paper will transfer concepts from clinical data integrity and audit trail systems into environmental monitoring systems, rather than treating blockchain as the primary scientific novelty by itself.

Rationale:

Clinical systems provide mature patterns for attributable records, timestamped changes, controlled corrections, source data verification, audit trail review, and regulatory-grade traceability. These patterns can guide environmental monitoring systems that need trustable records.

### Decision 2: Focus on rural environmental monitoring

The target context is rural monitoring infrastructure, including air quality, water quality, and distributed environmental sensor networks.

Rationale:

Rural systems create practical integrity challenges: distributed devices, intermittent connectivity, limited maintenance access, and fragmented organizational responsibility.

### Decision 3: Use a hybrid architecture assumption

The working architecture should store environmental measurements off-chain and store hashes, timestamps, audit metadata, and verification anchors on-chain.

Rationale:

Full on-chain storage is likely unsuitable for high-volume sensor data and rural infrastructure constraints. The paper should evaluate integrity anchoring rather than raw data storage on a blockchain. TODO:EXPERIMENT_NEEDED

### Decision 4: Do not claim empirical findings yet

The manuscript must not report results until data and experiments exist.

Rationale:

Current work is at the scope and research-design stage. All future empirical needs should be marked with TODO:DATA_NEEDED or TODO:EXPERIMENT_NEEDED.

### Decision 5: Use TODO markers instead of invented support

References, datasets, and results must not be invented.

Rationale:

The repository rule is to use TODO:CITATION_NEEDED, TODO:DATA_NEEDED, and TODO:EXPERIMENT_NEEDED wherever support is still missing.

### Decision 6: Position for an Infraeco-like venue

The paper may remain potentially suitable for an Infraeco-like venue only if the venue accepts infrastructure informatics or trustworthy monitoring data systems. The primary positioning is no longer environmental engineering.

Rationale:

The strongest contribution is a computer science / information systems contribution: data integrity architecture, audit trails, threat coverage, provenance verification, and reproducible verification workflows.

### Decision 7: Treat `resources/krzysztof_misztal_citations.bib` as author background

The file `resources/krzysztof_misztal_citations.bib` should be kept in mind as context for the author's prior scientific work and possible self-citation candidates.

Rationale:

The file documents prior work that can support the author's positioning across computer vision, biometrics, mathematical modeling, data standardisation, biological or medical data analysis, and blockchain-supported laboratory data security. These entries should inform framing, but they should not be used as automatic evidence for environmental monitoring claims.

### Decision 8: Position the paper as computer science / information systems

The paper should be positioned primarily as a computer science and information systems paper. Environmental monitoring remains the application domain because it provides realistic distributed, time-series, multi-actor monitoring data with provenance and trust challenges.

Rationale:

The key research contribution is not pollutant interpretation, sensor calibration, environmental policy, or field deployment. The key contribution is the design and evaluation of integrity models, audit trail architecture, provenance/permission reconstruction, controlled tampering scenarios, and reproducible verification workflows.

### Decision 9: Redesign MVP experiments around threat coverage

The MVP experiments should compare four integrity models:

1. Conventional storage only.
2. Audit trail only.
3. Audit trail plus hash chain.
4. Audit trail plus hash chain plus provenance/permission reconstruction.

The primary output should be a threat-coverage matrix and measured verification results after experiments are executed.

Rationale:

This design produces a clearer information-systems evaluation than demonstrating one architecture alone. It allows the paper to show which threats each model can and cannot detect without claiming environmental engineering results.

### Decision 10: Select OpenAQ monitoring locations by city-centered availability and geography

The MVP OpenAQ dataset should not use the first available locations returned by the country-level API query. Instead, candidate monitoring locations should be selected around selected European capitals: Warsaw, Berlin, Paris, and Madrid.

For each city, the downloader should:

1. Search candidate OpenAQ locations within a configurable radius around the city center.
2. Score candidate locations by available measurement counts in the selected time window.
3. Select a configurable number of monitoring locations, defaulting to three per city.
4. Prefer geographically separated locations that roughly form a triangle around the city center.
5. Keep the number of selected sensors per location configurable.
6. Use a configurable minimum distance between selected locations so the three points are not clustered too closely.
7. Generate an inspection map for each download so the selected locations can be visually reviewed before experiments are interpreted.

The candidate MVP time window is 2025-07-01 to 2025-12-31. This range is not final until the downloader confirms that selected locations have sufficient measurement availability in that period.

Rationale:

This creates a more intentional and reproducible dataset slice than arbitrary country-level selection. It also supports the paper's distributed monitoring scenario by using multiple cities and multiple monitoring locations per city while keeping the dataset bounded.

## Open Decisions

1. Select the exact target venue and verify whether computer science / information systems framing fits its scope. TODO:CITATION_NEEDED
2. Select candidate public environmental datasets. TODO:DATA_NEEDED
3. Decide the exact public dataset slice for controlled tampering experiments. TODO:DATA_NEEDED
4. Decide whether delayed synchronization is included in MVP or extended experiments.
5. Decide whether signatures are represented as key identifiers or implemented cryptographically.
6. Decide which prior author works from `resources/krzysztof_misztal_citations.bib` are scientifically appropriate to cite.
7. Decide whether AI/ML anomaly detection remains fully out of scope.
