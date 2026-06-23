# Experimental Plan

Working title: Blockchain-Based Environmental Data Integrity for Distributed Monitoring Systems

This file defines executable experiments for the paper. It is not manuscript text. No results are reported here.

## Strategic Positioning

The experiments should support a computer science / information systems paper. Environmental monitoring is the application domain because it provides realistic distributed, time-series, multi-actor monitoring data with provenance and trust challenges.

The experiments should emphasize:

1. Data integrity.
2. Audit trail architecture.
3. Provenance verification.
4. Threat model.
5. Verification workflows.
6. Controlled tampering scenarios.
7. Reproducible proof-of-concept implementation.

The experiments should de-emphasize:

1. Environmental engineering outcomes.
2. Sensor calibration science.
3. Pollutant-specific interpretation.
4. Environmental policy impact.
5. Field deployment claims.

## Design Constraints

1. The experiments should be executable within a few weeks.
2. Use public environmental datasets whenever possible.
3. Do not claim results until experiments are implemented and measured.
4. Use controlled tampering scenarios so ground truth is known.
5. Compare integrity models rather than only demonstrating one architecture.
6. Keep the implementation lightweight and reproducible.
7. Avoid production blockchain frameworks, smart contracts, and field deployment dependencies.

## Verified Candidate Public Data Sources

These sources were checked as real public data candidates on 2026-06-20. Final dataset selection still requires actual download and inspection.

1. OpenAQ
   - Source: https://docs.openaq.org/
   - Data type: air quality measurements.
   - Notes: Suitable for distributed time-series records with station, parameter, timestamp, and value fields.

2. US EPA Air Quality System API
   - Source: https://aqs.epa.gov/aqsweb/documents/data_api.html
   - Data type: ambient air sample data, station metadata, quality-related sample information, and QA data.
   - Notes: Strong candidate where station metadata and quality-related records are useful for provenance experiments. API key registration is required.

3. Water Quality Portal
   - Source: https://www.waterqualitydata.us/
   - Data type: water quality monitoring data.
   - Notes: Candidate extended-domain dataset after the MVP.

4. NOAA/NCEI Climate Data Online API
   - Source: https://www.ncei.noaa.gov/cdo-web/webservices/v2
   - Data type: climate and station datasets.
   - Notes: Candidate fallback for station-based time-series records.

## Recommended MVP Dataset

Use OpenAQ or EPA AQS first. The chosen data slice should be small, reproducible, and sufficient to create station-based time-series records.

Recommended properties:

1. One environmental domain, preferably air quality.
2. One to three measured parameters.
3. Multiple stations or locations.
4. A bounded time window, for example 7 to 30 days.
5. Enough records to support synthetic tampering and verification timing.

Final dataset extract: TODO:DATA_NEEDED

## Integrity Models Compared

The MVP compares four integrity models on the same dataset and the same controlled threats.

### Model A: Conventional Storage Only

Description:

Records are stored as ordinary rows in CSV, JSON, or SQLite. No append-only audit trail, hash chain, or permission reconstruction is used.

Verification capability:

1. Schema checks.
2. Basic duplicate checks.
3. Optional source row comparison if an untouched source copy is available.

Expected role:

Baseline model for showing what is not detectable when only conventional storage is used.

### Model B: Audit Trail Only

Description:

Records are stored conventionally, but create, update, correction, deletion attempt, and publication events are logged in an append-only audit table or JSONL log. Events are not hash-linked.

Verification capability:

1. Checks whether events are present.
2. Checks whether corrections have reasons.
3. Checks whether actions are recorded in the audit trail.
4. Detects some missing or inconsistent event histories if the audit trail itself is intact.

Expected role:

Shows the value and limits of audit trails without cryptographic linkage.

### Model C: Audit Trail Plus Hash Chain

Description:

Audit events are serialized deterministically and linked with previous hashes. Measurement payload hashes and event block hashes are stored.

Verification capability:

1. Recalculates payload hashes.
2. Recalculates block hashes.
3. Checks previous-hash links.
4. Detects tampering in values, timestamps, event order, deletion, and insertion when the chain is verified.

Expected role:

Shows the additional threat coverage provided by tamper-evident audit trails.

### Model D: Audit Trail Plus Hash Chain Plus Provenance/Permission Reconstruction

Description:

Model C is extended with actor identities, sensor/gateway keys, permission events, revocation events, correction lineage, and provenance checks.

Verification capability:

1. All checks from Model C.
2. Reconstructs active permissions at event time.
3. Detects revoked actor key usage.
4. Detects unauthorized correction.
5. Detects missing correction reasons.
6. Detects broken provenance references.
7. Explains whether a hash-valid event is unauthorized or provenance-invalid.

Expected role:

Primary proposed model and main architecture contribution.

## Threat Model

The experiments should evaluate the following threats:

1. Value modification.
2. Timestamp modification.
3. Record deletion.
4. Fake record insertion.
5. Replay.
6. Unauthorized correction.
7. Broken provenance.
8. Revoked actor key usage.
9. Missing correction reason.
10. Delayed synchronization.

Each threat should have:

1. A deterministic tampering procedure.
2. A ground-truth label.
3. An expected detectable/partially detectable/not detectable status for each model.
4. Measured verification outputs after execution. TODO:EXPERIMENT_NEEDED

## Primary MVP Output

The primary output should be a threat-coverage matrix.

Rows:

1. Value modification.
2. Timestamp modification.
3. Record deletion.
4. Fake record insertion.
5. Replay.
6. Unauthorized correction.
7. Broken provenance.
8. Revoked actor key usage.
9. Missing correction reason.
10. Delayed synchronization.

Columns:

1. Model A: Conventional storage only.
2. Model B: Audit trail only.
3. Model C: Audit trail plus hash chain.
4. Model D: Audit trail plus hash chain plus provenance/permission reconstruction.

Cell values:

1. Detectable.
2. Partially detectable.
3. Not detectable.
4. Requires external baseline.
5. Not applicable.

Final matrix values must be based on implemented verification behavior, not assumptions. TODO:EXPERIMENT_NEEDED

## MVP Experiment 1: Baseline Dataset and Event Construction

### Objective

Create a reproducible environmental time-series dataset extract and transform it into a common event representation used by all four integrity models.

### Input Data

Public environmental monitoring records, preferably air quality time-series data.

### Dataset Source

Recommended:

1. OpenAQ: https://docs.openaq.org/
2. EPA AQS: https://aqs.epa.gov/aqsweb/documents/data_api.html

Final dataset extract: TODO:DATA_NEEDED

### Required Preprocessing

1. Download and freeze a bounded dataset extract.
2. Normalize timestamps.
3. Normalize station identifiers.
4. Normalize parameter names and units.
5. Normalize numeric values.
6. Assign deterministic `record_id` values.
7. Preserve source rows as raw payloads.
8. Sort records deterministically.

### Experimental Procedure

1. Select a small but non-trivial data slice.
2. Create a dataset manifest with source URL, download date, query parameters, and file hashes.
3. Convert records into canonical measurement events.
4. Create synthetic actor identities for stations, gateways, operators, and reviewers.
5. Initialize all four integrity models from the same baseline events.

### Evaluation Metrics

1. Number of records ingested.
2. Number of canonical events generated.
3. Schema completeness rate.
4. Number of stations or sources represented.
5. Preprocessing failures.

### Expected Outputs

1. Frozen raw dataset.
2. Processed dataset.
3. Dataset manifest.
4. Canonical event log.
5. Initial model stores for A, B, C, and D.

### Risks

1. Public data may have missing station metadata.
2. API rate limits may slow data collection.
3. Dataset heterogeneity may expand preprocessing scope.

## MVP Experiment 2: Threat Injection

### Objective

Generate controlled tampering scenarios with known labels for all threats in the threat model.

### Input Data

Baseline dataset and model stores from MVP Experiment 1.

### Dataset Source

Same dataset extract as MVP Experiment 1. TODO:DATA_NEEDED

### Required Preprocessing

1. Freeze baseline copies.
2. Define deterministic random seed.
3. Select target records and events for each threat.
4. Define actor/key states for authorization threats.

### Experimental Procedure

1. Inject value modification.
2. Inject timestamp modification.
3. Inject record deletion.
4. Inject fake record insertion.
5. Inject replay.
6. Inject unauthorized correction.
7. Inject broken provenance.
8. Inject revoked actor key usage.
9. Inject missing correction reason.
10. Inject delayed synchronization.
11. Save tampered datasets, tampered logs, and label files.

### Evaluation Metrics

1. Number of tampered records per threat.
2. Number of tampered events per threat.
3. Label completeness rate.
4. Attack generation success rate.
5. Reproducibility check using deterministic seed.

### Expected Outputs

1. Tampered artifacts for each threat.
2. Ground-truth label file.
3. Scenario manifest.
4. Mapping between labels and affected records/events.

### Risks

1. Some threats target records while others target event logs or permission state.
2. Delayed synchronization requires a simple gateway/central verifier model.
3. Replay definitions must be precise to avoid ambiguity.

## MVP Experiment 3: Model Verification

### Objective

Run each integrity model against each threat scenario and measure which threats are detected, partially detected, or not detected.

### Input Data

Baseline and tampered artifacts from MVP Experiments 1 and 2.

### Dataset Source

Same dataset extract as MVP Experiment 1. TODO:DATA_NEEDED

### Required Preprocessing

1. Prepare model-specific verifier inputs.
2. Ensure each model receives equivalent baseline and tampered cases.
3. Load ground-truth labels.

### Experimental Procedure

1. Run Model A verifier for all threats.
2. Run Model B verifier for all threats.
3. Run Model C verifier for all threats.
4. Run Model D verifier for all threats.
5. Export alert logs for each model and scenario.
6. Compare alert logs with ground-truth labels.
7. Generate threat-coverage matrix.
8. Generate measured verification tables.

### Evaluation Metrics

1. Threat coverage status per model and threat.
2. Detection rate.
3. False positive rate.
4. False negative rate.
5. Precision.
6. Recall.
7. F1 score.
8. Alert explainability category.
9. Verification runtime.
10. Storage overhead.

### Expected Outputs

1. Threat-coverage matrix.
2. Model-by-threat verification report.
3. Detection metrics table.
4. Runtime and storage overhead table.
5. Alert logs.
6. Reproducibility manifest.

### Risks

1. Some cells may be "not detectable" by design; this is acceptable if clearly explained.
2. Model A may require an external baseline for some comparisons.
3. Metrics must not be interpreted as environmental performance.
4. Results must not be reported until experiments are actually executed.

## Extended Experiment 4: Delayed Synchronization Detail

### Objective

Evaluate delayed synchronization as a deeper rural-monitoring information-systems scenario.

### Input Data

Station-partitioned baseline and tampered data.

### Dataset Source

Same dataset extract as MVP Experiment 1. TODO:DATA_NEEDED

### Required Preprocessing

1. Partition records by station or gateway.
2. Define offline windows.
3. Define local and central verifier states.
4. Define synchronization events.

### Experimental Procedure

1. Build local gateway event logs.
2. Simulate offline periods.
3. Inject threats during offline periods.
4. Synchronize local summaries or full logs.
5. Run central verification after synchronization.
6. Compare detection behavior across Models A-D.

### Evaluation Metrics

1. Detection after synchronization.
2. Verification delay.
3. Number of unresolved conflicts.
4. Local versus central alert differences.
5. Synchronization overhead.

### Expected Outputs

1. Local gateway logs.
2. Central verifier logs.
3. Delayed synchronization threat-coverage table.

### Risks

1. This is a simulation, not a field deployment.
2. Conflict-resolution rules may add complexity.
3. Should remain extended unless MVP is stable.

## Extended Experiment 5: Second-Domain Replication

### Objective

Check whether the same integrity-model comparison can be repeated on water quality or climate station data.

### Input Data

Second public environmental dataset.

### Dataset Source

Water Quality Portal or NOAA/NCEI CDO. TODO:DATA_NEEDED

### Required Preprocessing

1. Map source fields to canonical event schema.
2. Normalize station, timestamp, parameter, value, and unit fields.
3. Preserve source-specific metadata.

### Experimental Procedure

1. Repeat MVP Experiments 1-3 on the second dataset.
2. Compare preprocessing burden and schema fit.
3. Compare threat coverage qualitatively and quantitatively after execution.

### Evaluation Metrics

1. Schema coverage rate.
2. Missing metadata rate.
3. Threat coverage matrix reproducibility.
4. Source-specific preprocessing complexity.

### Expected Outputs

1. Second-domain threat-coverage matrix.
2. Cross-domain schema mapping notes.
3. Dataset-specific limitations.

### Risks

1. This may broaden the paper too much.
2. Water quality data may require more domain-specific cleaning.
3. It should be deferred unless the MVP is complete.

## MVP Implementation Schedule

Target duration: 2 to 3 weeks.

Week 1:

1. Select and freeze dataset extract.
2. Implement common event schema.
3. Implement Model A and Model B.
4. Implement basic threat injection.

Week 2:

1. Implement Model C hash-chain verification.
2. Implement Model D provenance/permission reconstruction.
3. Complete threat injection for all ten threats.
4. Generate ground-truth labels.

Week 3:

1. Run model verification across all threats.
2. Generate threat-coverage matrix.
3. Export metrics-ready tables.
4. Review outputs before interpreting results.

## Minimum Publishable Outputs

1. Frozen dataset manifest. TODO:DATA_NEEDED
2. Common event schema.
3. Four implemented integrity models.
4. Controlled threat injection scripts.
5. Model-specific verification workflows.
6. Threat-coverage matrix. TODO:EXPERIMENT_NEEDED
7. Measured verification results. TODO:EXPERIMENT_NEEDED
8. Reproducibility package.

## What Not To Claim Yet

1. Do not claim environmental deployment success.
2. Do not claim pollutant-specific findings.
3. Do not claim sensor calibration findings.
4. Do not claim environmental policy impact.
5. Do not claim real-world attack frequency.
6. Do not claim blockchain superiority in general.
7. Do not report threat-coverage values or metrics until experiments are run.

## Open Experimental Decisions

1. Choose OpenAQ or EPA AQS as the MVP dataset. TODO:DATA_NEEDED
2. Choose exact stations, parameters, and time window. TODO:DATA_NEEDED
3. Decide whether signatures are represented as key identifiers or cryptographic signatures.
4. Decide whether delayed synchronization is included in MVP or extended experiments.
5. Decide exact cell labels for the threat-coverage matrix.
6. Decide whether second-domain replication is needed for venue fit.
