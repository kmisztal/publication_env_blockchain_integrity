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

The paper should be positioned around environmental infrastructure, monitoring reliability, rural deployment constraints, and data trustworthiness.

Rationale:

This framing is more suitable for an infrastructure/environmental venue than a manuscript focused mainly on blockchain mechanics.

### Decision 7: Treat `resources/krzysztof_misztal_citations.bib` as author background

The file `resources/krzysztof_misztal_citations.bib` should be kept in mind as context for the author's prior scientific work and possible self-citation candidates.

Rationale:

The file documents prior work that can support the author's positioning across computer vision, biometrics, mathematical modeling, data standardisation, biological or medical data analysis, and blockchain-supported laboratory data security. These entries should inform framing, but they should not be used as automatic evidence for environmental monitoring claims.

## Open Decisions

1. Select the exact target venue and verify its scope. TODO:CITATION_NEEDED
2. Select candidate public environmental datasets. TODO:DATA_NEEDED
3. Decide whether the first manuscript is conceptual only or includes a small prototype evaluation. TODO:EXPERIMENT_NEEDED
4. Choose blockchain platform assumptions only after defining the evaluation needs.
5. Decide whether AI/ML anomaly detection belongs in the first version or should remain future work.
6. Decide which prior author works from `resources/krzysztof_misztal_citations.bib` are scientifically appropriate to cite.
