# Scientific Decisions

This file records scope and design decisions before manuscript writing starts.

## 2026-06-20

### Decision 1: Treat the paper as a cross-domain integrity framework

The paper will transfer concepts from clinical data integrity and audit trail systems into environmental monitoring systems, rather than treating blockchain as the primary scientific novelty by itself.

Rationale:

Clinical systems provide mature patterns for attributable records, timestamped changes, controlled corrections, source data verification, audit trail review, and regulatory-grade traceability. These patterns can guide environmental monitoring systems that need trustable records.

### Decision 2: Focus on distributed environmental monitoring

The target context is distributed environmental monitoring infrastructure, including public monitoring networks, multi-station sensor systems, rural deployments, and heterogeneous environmental data pipelines.

Rationale:

Distributed monitoring systems create practical integrity challenges: geographically separated sources, intermittent synchronization, heterogeneous infrastructure, and fragmented organizational responsibility. Rural monitoring remains a motivating example, but the manuscript title and main framing should not imply that the executed OpenAQ multi-city experiment validates rural field deployment.

### Decision 3: Use a hybrid architecture assumption

The working architecture should store environmental measurements off-chain and store hashes, timestamps, audit metadata, and verification anchors on-chain.

Rationale:

Full on-chain storage is likely unsuitable for high-volume sensor data and constrained monitoring infrastructure. The paper evaluates integrity anchoring rather than raw data storage on a blockchain.

### Decision 4: Report only executed empirical findings

The manuscript may report only results that come from executed artifacts under `experiments/outputs/`.

Rationale:

The OpenAQ proof-of-concept has been executed. Remaining future empirical ideas still require TODO:DATA_NEEDED or TODO:EXPERIMENT_NEEDED until implemented.

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
8. For the default three-location case, select the best combination using triangle area and whether the city center is enclosed, not only directional sectors.

The executed MVP time window is 2025-07-01 to 2025-12-31.

Rationale:

This creates a more intentional and reproducible dataset slice than arbitrary country-level selection. It also supports the paper's distributed monitoring scenario by using multiple cities and multiple monitoring locations per city while keeping the dataset bounded.

## Open Decisions

1. Select the exact target venue and verify whether computer science / information systems framing fits its scope. TODO:CITATION_NEEDED
2. Decide whether additional datasets beyond the executed OpenAQ extract are needed for a later extended study. TODO:DATA_NEEDED
3. Decide whether scenario repetitions should be added before submission. TODO:EXPERIMENT_NEEDED
4. Decide whether negative cases should be implemented to support precision, recall, F1, false-positive rate, and false-negative rate. TODO:EXPERIMENT_NEEDED
5. Decide whether signatures should remain represented as key identifiers or be implemented cryptographically in an extended version.
6. Decide which prior author works from `resources/krzysztof_misztal_citations.bib` are scientifically appropriate to cite.
7. Keep AI/ML anomaly detection out of scope unless a separate environmental plausibility layer is explicitly added.
