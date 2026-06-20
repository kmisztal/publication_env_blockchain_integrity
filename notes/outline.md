# Blockchain-Based Environmental Data Integrity for Rural Monitoring Systems

## Working Scientific Outline

This outline is a planning structure only. It should guide manuscript development after the research scope is stable.

Strategic positioning:

This manuscript should be framed primarily as a computer science / information systems paper. Environmental monitoring is the application domain because it provides realistic distributed, time-series, multi-actor monitoring data with provenance and trust challenges. The paper should not be framed as a pure environmental engineering paper.

## 1. Introduction

Purpose:

1. Introduce environmental monitoring as a realistic distributed data integrity domain.
2. Explain why distributed sensor/time-series systems create provenance and trust challenges.
3. Motivate audit trails, hash verification, threat modeling, and verification workflows.
4. State the computer science / information systems research question and contribution.

Key claims needing support:

1. Distributed monitoring systems create data integrity and provenance challenges. TODO:CITATION_NEEDED
2. Audit trails and provenance verification are important for trustworthy information systems. TODO:CITATION_NEEDED
3. Hash chains and tamper-evident logs can support verification workflows. TODO:CITATION_NEEDED

## 2. Related Work

Planned subsections:

1. Environmental monitoring as distributed time-series information infrastructure.
2. Rural IoT and environmental sensor networks as application context.
3. Data provenance, data integrity, and trustworthiness.
4. Audit trails and tamper-evident logs.
5. Hash verification and blockchain-inspired integrity architectures.
6. Gap synthesis focused on threat coverage and model comparison.

Boundary:

This section must not invent references. Unsupported statements should use TODO:CITATION_NEEDED.

## 3. Conceptual Framework and Methodology

Purpose:

1. Define the information-systems threat model.
2. Define environmental monitoring as the application dataset domain.
3. Define four integrity models: conventional storage only, audit trail only, audit trail plus hash chain, and audit trail plus hash chain plus provenance/permission reconstruction.
4. Define threat and failure cases: value modification, timestamp modification, deletion, fake insertion, replay, unauthorized correction, broken provenance, revoked actor key usage, missing correction reason, and delayed synchronization.

Planned methodology:

1. Threat model definition.
2. Integrity model design and comparison.
3. Controlled tampering design using public environmental time-series data. TODO:DATA_NEEDED
4. Verification workflow and threat-coverage matrix generation. TODO:EXPERIMENT_NEEDED

## 4. Proposed System Architecture

Purpose:

1. Present the lightweight proof-of-concept architecture.
2. Show how the same baseline data are represented under Models A-D.
3. Explain audit events, hashes, provenance links, permission state, and verifier outputs.
4. Describe data correction, actor key revocation, delayed synchronization, and verification workflows.

Candidate components:

1. Public environmental dataset extract.
2. Canonical event mapper.
3. Conventional storage model.
4. Audit trail model.
5. Hash-chain model.
6. Provenance/permission reconstruction model.
7. Threat injector.
8. Model-specific verifiers.
9. Threat-coverage matrix generator.

## 5. Evaluation Design

Purpose:

Define how the four integrity models are evaluated against the same controlled threats without reporting results prematurely.

Candidate evaluation questions:

1. Which threats are detected by conventional storage only? TODO:EXPERIMENT_NEEDED
2. Which threats are detected by audit trail only? TODO:EXPERIMENT_NEEDED
3. Which threats are detected by audit trail plus hash chain? TODO:EXPERIMENT_NEEDED
4. Which threats require provenance/permission reconstruction? TODO:EXPERIMENT_NEEDED
5. What is the measured detection behavior and overhead for each model? TODO:EXPERIMENT_NEEDED

Candidate data sources:

1. Public air quality datasets. TODO:DATA_NEEDED
2. Public water quality datasets. TODO:DATA_NEEDED
3. Public climate station datasets if needed. TODO:DATA_NEEDED

Primary output:

1. Threat-coverage matrix for Models A-D.
2. Measured verification results after execution. TODO:EXPERIMENT_NEEDED
3. Reproducibility package.

## 6. Discussion

Planned discussion points:

1. Interpretation of threat coverage across Models A-D.
2. Trade-offs between conventional storage, audit trails, hash chains, and provenance/permission reconstruction.
3. Why environmental monitoring is a useful application domain for information-systems integrity research.
4. Reproducibility and implementation simplicity.
5. Limitations of synthetic tampering scenarios.
6. Risks of overclaiming blockchain benefits or environmental deployment outcomes.

## 7. Conclusions

Purpose:

1. Restate the research problem.
2. Summarize the information-systems contribution.
3. Identify next steps: references, dataset selection, prototype execution, and threat-coverage evaluation.

## Current Scope Boundary

The first manuscript should remain focused on data integrity architecture, threat modeling, verification workflows, controlled tampering, and reproducible proof-of-concept evaluation. It should not report experimental findings until the data and experiments exist. It should not claim environmental engineering outcomes, pollutant-specific interpretation, or field deployment success.
