# Blockchain-Based Environmental Data Integrity for Distributed Monitoring Systems

## Working Scientific Outline

This outline reflects the current manuscript direction after execution of the OpenAQ proof-of-concept experiments.

Strategic positioning:

This manuscript is primarily a computer science / information systems paper. Environmental monitoring is the application domain because it provides realistic distributed, time-series, multi-source data with provenance and trust challenges. The paper should not be framed as pure environmental engineering and should not report pollutant-specific or policy conclusions.

## 1. Introduction

Purpose:

1. Introduce environmental monitoring as a realistic distributed data integrity domain.
2. Explain why distributed sensor/time-series systems create provenance and trust challenges.
3. Motivate audit trails, hash verification, threat modeling, and verification workflows.
4. State the research question around comparative threat coverage for integrity models.

Key claims needing support:

1. Distributed monitoring systems create data integrity and provenance challenges. TODO:CITATION_NEEDED
2. Audit trails and provenance verification are important for trustworthy information systems. TODO:CITATION_NEEDED
3. Hash chains and tamper-evident logs can support verification workflows. TODO:CITATION_NEEDED

## 2. Related Work

Planned subsections:

1. Environmental monitoring as distributed time-series information infrastructure.
2. Distributed and rural IoT monitoring as application context.
3. Environmental sensor networks.
4. Data provenance, data integrity, and trustworthiness.
5. Blockchain-inspired integrity architectures.
6. Audit trails and hash verification.
7. Literature gap focused on threat coverage and model comparison.

Boundary:

This section must not invent references. Unsupported statements should use TODO:CITATION_NEEDED.

## 3. Methodology

Purpose:

1. Define the information-systems study design.
2. Describe the OpenAQ API v3 dataset extract.
3. Report preprocessing counts from executed artifacts.
4. Define Models A-D.
5. Define controlled tampering scenarios and evaluation semantics.

Current dataset:

1. Dataset ID: `openaq_capitals_2025_h2`.
2. Time window: 2025-07-01 to 2025-12-31.
3. Cities: Warsaw, Berlin, Paris, Madrid.
4. Monitoring locations: 12 total, 3 per city.
5. Canonical records after preprocessing: 112,973.
6. Dropped records: 3,388.
7. Parameters after preprocessing: 9.

## 4. System Architecture

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

## 5. Evaluation Results

Purpose:

Report executed proof-of-concept results without overclaiming statistical or environmental conclusions.

Primary outputs:

1. Scenario count: 25.
2. Aggregate status counts: detected 20, expected_not_detected 5, missed 0, partial 0, unexpected_alert 0.
3. Threat-coverage matrix for Models A-D.
4. Model-level interpretation.
5. Reproducibility artifact references.

Do not report:

1. Precision, recall, F1, false-positive rate, or false-negative rate.
2. Environmental air-quality conclusions.
3. Real-world manipulation detection in OpenAQ.
4. Production blockchain deployment readiness.

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
3. Summarize the executed threat-coverage evaluation.
4. Identify next steps: references, scenario repetitions, negative cases, per-station chains, and extended synchronization experiments.

## Current Scope Boundary

The manuscript should remain focused on data integrity architecture, threat modeling, verification workflows, controlled tampering, and reproducible proof-of-concept evaluation. It should not claim environmental engineering outcomes, pollutant-specific interpretation, field deployment success, or statistical generalization beyond the implemented controlled scenarios.
