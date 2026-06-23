# Paper Context

Working title: Blockchain-Based Environmental Data Integrity for Distributed Monitoring Systems

## Scientific Direction

This publication is positioned primarily as a computer science and information systems paper. Environmental monitoring is the application domain because it provides realistic distributed, time-series, multi-actor data with provenance and trust challenges.

The intended contribution is not to claim environmental engineering outcomes, pollutant-specific insights, or field deployment performance. The intended contribution is to define and evaluate a lightweight data integrity and audit trail architecture for environmental monitoring data, inspired by regulated audit trails, hash verification, provenance verification, permission reconstruction, and controlled tampering analysis.

Primary scientific emphasis:

1. Data integrity.
2. Audit trail architecture.
3. Provenance verification.
4. Threat model.
5. Verification workflows.
6. Controlled tampering scenarios.
7. Reproducible proof-of-concept implementation.

De-emphasized topics:

1. Environmental engineering outcomes.
2. Sensor calibration science.
3. Pollutant-specific interpretation.
4. Environmental policy impact.
5. Field deployment claims.

## Author Background Context

The file `resources/krzysztof_misztal_citations.bib` should be treated as background context for the author's prior scientific work. It includes prior work related to mathematical modeling, computer vision, biometrics, clustering, medical or biological data analysis, deep learning, data standardisation, and blockchain-supported laboratory data security.

This background can inform the manuscript positioning, especially where the paper connects environmental data integrity with image/data verification, regulated data workflows, laboratory data security, and blockchain auditability.

Important boundary:

1. Entries in `resources/krzysztof_misztal_citations.bib` are not automatic evidence for environmental monitoring claims.
2. If a specific prior work from that file is used in the manuscript, it should be cited deliberately through the bibliography.
3. Claims outside those works still require TODO:CITATION_NEEDED.
4. The file may help identify relevant self-citation candidates, but it must not replace a proper related work search.

## Research Problem

Environmental monitoring systems increasingly depend on distributed sensors and public or semi-public datasets. From an information systems perspective, these systems create a difficult integrity problem: records are time-series observations, produced by multiple stations or gateways, processed by multiple actors, and sometimes corrected, delayed, replayed, or republished.

The research problem is how to compare and evaluate lightweight integrity models for detecting and explaining threats to environmental monitoring records without assuming a production blockchain network, continuous connectivity, centralized trust, or environmental field deployment.

## Research Gap

The working research gap is the lack of a clearly defined and experimentally testable information-systems framework that compares conventional storage, audit trails, hash chains, and provenance/permission reconstruction for environmental monitoring data.

Candidate gap statement:

Existing environmental sensor network work often addresses data collection, communication, calibration, analytics, or anomaly detection, while blockchain-based environmental systems often emphasize decentralization or transparency. However, there is limited comparative treatment of environmental data integrity as a threat-coverage problem: which architecture detects value modification, timestamp modification, record deletion, fake insertion, replay, unauthorized correction, broken provenance, revoked key usage, missing correction reasons, and delayed synchronization. TODO:CITATION_NEEDED

## Research Question

Primary research question:

How do increasingly expressive integrity models compare in their ability to detect and explain threats to distributed environmental monitoring records?

Supporting questions:

1. Which threats are detectable by conventional storage only?
2. What additional threat coverage is provided by an append-only audit trail?
3. What additional threat coverage is provided by combining audit trails with hash chains?
4. What additional threat coverage is provided by provenance and permission reconstruction?
5. How can these models be evaluated reproducibly using public environmental time-series data and controlled tampering scenarios?

## Research Objectives

1. Define a threat model for environmental monitoring data integrity.
2. Define four comparable integrity models: conventional storage only, audit trail only, audit trail plus hash chain, and audit trail plus hash chain plus provenance/permission reconstruction.
3. Specify verification workflows for value modification, timestamp modification, record deletion, fake insertion, replay, unauthorized correction, broken provenance, revoked actor key usage, missing correction reasons, and delayed synchronization.
4. Build a lightweight reproducible proof-of-concept using Python, Pandas, and SQLite or JSON storage.
5. Evaluate threat coverage using the executed OpenAQ environmental time-series dataset and controlled tampering scenarios.
6. Produce and report the executed threat-coverage matrix and measured verification outputs.

## Hypotheses

H1: Audit trail plus hash-chain verification detects more integrity threats than conventional storage or audit trail alone.

H2: Adding provenance and permission reconstruction increases explanatory coverage for actor-related threats, including unauthorized correction and revoked key usage.

H3: Threat-coverage matrices provide a clearer evaluation method for integrity architectures than architecture description alone.

H4: A lightweight reproducible PoC can evaluate integrity threats without requiring a production blockchain deployment or field sensor deployment.

## Expected Contribution

The expected contribution is a computer science / information systems evaluation paper with a lightweight proof-of-concept. The paper should not be framed as measuring environmental outcomes.

Expected contributions:

1. A threat model for environmental monitoring data integrity.
2. A comparison of four integrity models with increasing verification capability.
3. A threat-coverage matrix covering data, audit, provenance, permission, and synchronization threats.
4. A reproducible proof-of-concept implementation for controlled tampering experiments.
5. Verification workflows and measured outputs from the executed OpenAQ proof-of-concept.

## Target Venue Suitability

An Infraeco-like venue may still be suitable if the venue accepts information systems, infrastructure informatics, monitoring data governance, or trustworthy data architecture papers. However, the primary positioning should be computer science / information systems rather than environmental engineering.

The paper should foreground:

1. Data integrity and threat coverage.
2. Audit trail architecture.
3. Provenance and permission reconstruction.
4. Reproducible verification workflows.
5. Environmental monitoring as a realistic application domain.

Venue fit still requires confirmation against the selected venue scope, topics, and recent accepted papers. TODO:CITATION_NEEDED

## Scope

In scope:

1. Information systems architecture for environmental data integrity.
2. Audit trail models and verification workflows.
3. Threat modeling for distributed environmental time-series records.
4. Hash verification and tamper-evident event chains.
5. Provenance verification and permission-state reconstruction.
6. Controlled tampering experiments with public environmental data.
7. Reproducible proof-of-concept implementation.
8. Author background in data verification, regulated systems, and blockchain-supported laboratory data security where it helps motivate the cross-domain approach.

## Out-of-Scope Items

Out of scope for the initial manuscript:

1. Experimental results not produced by the executed proof-of-concept.
2. Environmental datasets not documented in the repository artifacts.
3. Cryptocurrency economics, token incentives, or market mechanisms.
4. Full implementation of a production blockchain network.
5. Claims of regulatory compliance for environmental systems without legal analysis.
6. Environmental engineering outcomes.
7. Sensor calibration science beyond integrity-relevant metadata.
8. Pollutant-specific interpretation.
9. Environmental policy impact claims.
10. Field deployment claims.
11. Machine learning model performance unless later connected to integrity verification or anomaly detection.

## Evidence Still Needed

1. Literature on information systems data integrity and provenance. TODO:CITATION_NEEDED
2. Literature on audit trails, tamper-evident logs, and hash verification. TODO:CITATION_NEEDED
3. Literature on blockchain-inspired data integrity architectures. TODO:CITATION_NEEDED
4. Literature on environmental monitoring as distributed time-series data infrastructure. TODO:CITATION_NEEDED
5. Additional public datasets beyond the executed OpenAQ extract, if the study is later extended. TODO:DATA_NEEDED
6. Scenario repetitions, negative cases, or additional metrics beyond the current threat-coverage matrix. TODO:EXPERIMENT_NEEDED
