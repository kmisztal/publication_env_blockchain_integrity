# Experimental Plan

Working title: Blockchain-Based Environmental Data Integrity for Rural Monitoring Systems

This file defines executable experiments for the paper. It is not manuscript text. No results are reported here.

## Design Constraints

1. The experiments should be executable within a few weeks.
2. Use public environmental datasets whenever possible.
3. Do not claim results until experiments are implemented and measured.
4. Use controlled tampering scenarios so ground truth is known.
5. Keep the blockchain component lightweight and reproducible: local hash chains, signed events, summary blocks, and verifier logic are enough for the first study.
6. Avoid building a production blockchain network unless later needed.

## Verified Candidate Public Data Sources

These sources were checked as real public data candidates on 2026-06-20. Final dataset selection still requires actual download and inspection.

1. OpenAQ
   - Source: https://docs.openaq.org/
   - Data type: air quality measurements.
   - Notes: API documentation describes querying measurements with filters such as location, parameter, and date range, plus geospatial filtering and pagination. It also notes access to the full OpenAQ archive through Open Data on AWS.

2. US EPA Air Quality System API
   - Source: https://aqs.epa.gov/aqsweb/documents/data_api.html
   - Data type: ambient air sample data, station metadata, quality-related sample information, and QA data.
   - Notes: EPA describes AQS as row-level data from the Air Quality System database. It includes sample data, daily summary data, monitor metadata, QA blanks, collocated assessments, flow-rate checks, and related services. API key registration is required.

3. Water Quality Portal
   - Source: https://www.waterqualitydata.us/
   - Data type: water quality monitoring data.
   - Notes: Candidate source for water quality measurements and station-based environmental records. Requires inspection of API export formats before final experiment selection.

4. NOAA/NCEI Climate Data Online API
   - Source: https://www.ncei.noaa.gov/cdo-web/webservices/v2
   - Data type: climate and station datasets.
   - Notes: API documentation defines datasets, stations, data categories, data types, locations, and data endpoints. Token registration may be required.

## Dataset Selection Recommendation

Recommended MVP dataset:

OpenAQ or EPA AQS air quality data should be used first because air quality measurements naturally fit the rural sensor-network framing, are time-series records, and can be converted into measurement events for hash-chain and audit-trail experiments.

Fallback:

If API access, rate limits, or data cleaning become a blocker, use a small downloaded CSV export from one verified public source and document the exact download path. TODO:DATA_NEEDED

Optional second domain:

Water Quality Portal data can be added as an extended experiment to demonstrate that the integrity architecture is not pollutant-specific. TODO:DATA_NEEDED

## Common Experimental Architecture

The experiments should share one small reproducible prototype.

### Data Model

Each environmental measurement event should include at minimum:

1. `record_id`
2. `source_dataset`
3. `station_id`
4. `sensor_or_parameter`
5. `timestamp`
6. `value`
7. `unit`
8. `latitude`
9. `longitude`
10. `ingested_at`
11. `operator_or_gateway_id`
12. `previous_hash`
13. `record_hash`
14. `event_type`
15. `signature_or_key_id`

Optional fields:

1. quality flag,
2. calibration metadata,
3. data owner or agency,
4. original source URL,
5. correction reason,
6. reviewer decision.

### Event Types

Use a patent-inspired but environmental-specific event model:

1. `GENESIS_NETWORK`
2. `INSERT_SENSOR_KEY`
3. `REVOKE_SENSOR_KEY`
4. `INSERT_MEASUREMENT`
5. `CORRECT_MEASUREMENT`
6. `INVALIDATE_MEASUREMENT`
7. `SUMMARY_BLOCK`
8. `VERIFY_BATCH`
9. `PUBLISH_DATASET`

### Integrity Layers

1. Off-chain raw dataset:
   - original public measurements stored as CSV/JSON/Parquet.

2. Measurement integrity chain:
   - one block per measurement, batch, or logical event.

3. Permission/provenance chain:
   - station keys, operator keys, revocations, correction privileges.

4. Central verifier:
   - recalculates hashes,
   - checks previous-hash links,
   - checks active keys,
   - checks timestamps,
   - reports tampering and provenance failures.

### Tampering Scenarios

Use synthetic attacks with known labels:

1. Value modification:
   - change pollutant or water-quality value.

2. Timestamp modification:
   - shift timestamp forward or backward.

3. Record deletion:
   - remove one or more events from the chain or off-chain data.

4. Record insertion:
   - insert a fake measurement without valid provenance.

5. Replay:
   - duplicate an old valid measurement under a new timestamp or station.

6. Unauthorized correction:
   - create a correction event signed by a revoked or unknown key.

7. Broken provenance:
   - change station ID, sensor ID, or source dataset metadata.

8. Summary-block mismatch:
   - alter records covered by a summary block without updating the summary.

## Minimum Publishable Experiment Set

The MVP should include three experiments. Together they are enough for a concise, realistic paper: one architecture demonstration, one tampering-detection experiment, and one audit/provenance experiment.

## Experiment 1: Hash-Chain Integrity Baseline

### Objective

Demonstrate that public environmental measurements can be transformed into an integrity-preserving event chain where unauthorized changes are detectable through hash verification.

### Input Data

Time-series environmental measurement records from one public source.

Recommended first choice:

OpenAQ air quality measurements for one pollutant, one region, and a short time window.

Alternative:

EPA AQS sample or daily summary data for one pollutant and a small set of stations.

### Dataset Source

1. OpenAQ API documentation: https://docs.openaq.org/
2. EPA AQS API documentation: https://aqs.epa.gov/aqsweb/documents/data_api.html

Final dataset extract: TODO:DATA_NEEDED

### Required Preprocessing

1. Download a bounded subset of records.
2. Normalize timestamps to one consistent format.
3. Sort by station, parameter, and timestamp.
4. Remove exact duplicate records or flag them explicitly.
5. Normalize numeric values and units.
6. Assign deterministic `record_id` values.
7. Preserve the original source row or source URL for traceability.

### Experimental Procedure

1. Select a reproducible data slice, for example one pollutant, 5 to 20 stations, and 7 to 30 days.
2. Convert each row into an `INSERT_MEASUREMENT` event.
3. Create a genesis event for the monitoring network.
4. Build a hash chain over ordered events.
5. Store raw records off-chain and store hashes plus metadata in the integrity chain.
6. Run a verifier that recalculates every hash and previous-hash link.
7. Confirm only that the verifier produces a validation report; do not report performance or success rates until the experiment is executed.

### Evaluation Metrics

1. Number of processed measurement records.
2. Number of generated integrity events.
3. Verification completion status.
4. Chain completeness rate.
5. Hash mismatch count.
6. Runtime for chain construction. TODO:EXPERIMENT_NEEDED
7. Runtime for verification. TODO:EXPERIMENT_NEEDED
8. Storage overhead ratio. TODO:EXPERIMENT_NEEDED

### Expected Outputs

1. Cleaned dataset extract.
2. Integrity event log.
3. Hash-chain file.
4. Verification report template.
5. Reproducible script or notebook.

### Risks

1. API access or rate limits may slow data collection.
2. Public data fields may vary by source.
3. Some data may lack complete station metadata.
4. Hash-chain baseline may be too obvious unless connected to audit and provenance scenarios.

## Experiment 2: Controlled Tampering Detection

### Objective

Evaluate whether the integrity chain detects known synthetic tampering scenarios in environmental measurement records.

### Input Data

The verified chain from Experiment 1.

### Dataset Source

Same dataset extract as Experiment 1. TODO:DATA_NEEDED

### Required Preprocessing

1. Freeze a clean baseline dataset.
2. Save the baseline hash-chain state.
3. Create labeled tampered copies of the dataset.
4. Define attack labels for each modified record or event.

### Experimental Procedure

1. Create synthetic tampering scenarios:
   - modify selected measurement values,
   - delete selected records,
   - insert fake records,
   - modify timestamps,
   - replay selected records,
   - change station or parameter metadata.
2. Apply each tampering scenario at controlled rates, for example 1%, 5%, and 10% of records.
3. Run the verifier on each tampered dataset.
4. Compare verifier alerts against known tampering labels.
5. Record only measured outputs after execution; do not infer results in advance.

### Evaluation Metrics

1. Tampering detection rate.
2. False positive rate.
3. False negative rate.
4. Precision.
5. Recall.
6. F1 score.
7. Detection latency measured as number of events until detection.
8. Attack-type-specific detection rate.

### Expected Outputs

1. Tampered dataset variants.
2. Ground-truth tampering label file.
3. Verifier alert reports.
4. Confusion matrix per attack type.
5. Summary table of detection metrics. TODO:EXPERIMENT_NEEDED

### Risks

1. Some attack types may be trivially detected by hash mismatch; the scientific value comes from comparing attack classes and audit interpretation.
2. If the verifier only checks hashes, it may not detect semantically plausible but authorized-looking false data.
3. Public datasets do not provide real tampering labels, so synthetic labels must be clearly described.

## Experiment 3: Audit Trail and Provenance Verification

### Objective

Demonstrate an audit-trail workflow for environmental data corrections, provenance changes, and permission checks using signed or key-identified events.

### Input Data

Baseline dataset from Experiment 1 plus synthetic audit events.

### Dataset Source

Same source as Experiment 1. TODO:DATA_NEEDED

### Required Preprocessing

1. Define operator, gateway, reviewer, and administrator identities.
2. Create key registry events:
   - insert sensor key,
   - insert operator key,
   - revoke sensor key,
   - revoke operator key.
3. Select a small subset of records for correction and invalidation workflows.
4. Define correction reasons and reviewer decisions.

### Experimental Procedure

1. Create a permission/provenance chain.
2. Add valid measurement events from authorized station or gateway keys.
3. Add valid correction events signed by authorized operators.
4. Add invalid correction attempts:
   - unknown key,
   - revoked key,
   - missing reason,
   - correction without reference to original record.
5. Add provenance changes:
   - station metadata update,
   - source dataset reference update,
   - reviewer approval or rejection.
6. Run an audit verifier that checks:
   - active key at event time,
   - event author,
   - correction lineage,
   - original record preservation,
   - mandatory metadata fields,
   - revocation effects.

### Evaluation Metrics

1. Percentage of events with complete provenance.
2. Number of valid corrections accepted.
3. Number of invalid corrections rejected.
4. Unauthorized event detection rate.
5. Missing metadata detection rate.
6. Correction lineage completeness rate.
7. Audit report completeness.

### Expected Outputs

1. Audit event log.
2. Permission/provenance chain.
3. Correction lineage table.
4. Rejected-event report.
5. Audit-trail verification report.

### Risks

1. Synthetic audit events must be presented as experimental design, not real environmental agency workflow.
2. Permission rules may become too complex for the first paper.
3. The experiment can drift into access-control engineering rather than environmental integrity if not kept focused.

## Extended Experiment Set

These experiments are valuable if time remains after the MVP.

## Experiment 4: Summary-Block Verification Efficiency

### Objective

Evaluate whether summary blocks reduce verification work while preserving tampering detection for environmental measurement chains.

### Input Data

Baseline integrity chain from Experiment 1 and tampered variants from Experiment 2.

### Dataset Source

Same source as Experiment 1. TODO:DATA_NEEDED

### Required Preprocessing

1. Define summary-block intervals:
   - fixed number of records,
   - hourly blocks,
   - daily blocks,
   - synchronization batch blocks.
2. Generate summary blocks containing:
   - previous summary hash,
   - hashes of covered measurement blocks,
   - active key state digest,
   - timestamp range.

### Experimental Procedure

1. Build full-chain verification baseline.
2. Build summary-block verification variants.
3. Run verification on clean and tampered chains.
4. Compare full verification against summary-assisted verification.
5. Test tampering before and after summary block generation.

### Evaluation Metrics

1. Verification runtime.
2. Number of hashes recalculated.
3. Storage overhead.
4. Detection rate by attack type.
5. Missed tampering count.
6. Summary block size.
7. Verification cost per 1,000 records.

### Expected Outputs

1. Summary-block event logs.
2. Runtime comparison table.
3. Storage overhead table.
4. Detection comparison table. TODO:EXPERIMENT_NEEDED

### Risks

1. Small datasets may not show meaningful runtime differences.
2. Summary blocks may complicate explanation.
3. If implemented poorly, summary blocks may reduce audit granularity.

## Experiment 5: Intermittent Connectivity and Delayed Synchronization

### Objective

Model rural monitoring constraints by testing whether local chains can preserve integrity during offline periods and synchronize later with a central verifier.

### Input Data

Time-series environmental data split by station or simulated station groups.

### Dataset Source

OpenAQ, EPA AQS, or NOAA/NCEI station data. TODO:DATA_NEEDED

### Required Preprocessing

1. Partition records by station or region.
2. Define simulated offline windows.
3. Create local chain segments for each station or gateway.
4. Define central synchronization intervals.

### Experimental Procedure

1. Assign records to local gateway chains.
2. Simulate offline periods by preventing central synchronization.
3. Continue local event generation during offline windows.
4. Synchronize hashes and summary blocks after reconnection.
5. Inject tampering during offline windows.
6. Run central verification after synchronization.

### Evaluation Metrics

1. Offline records preserved.
2. Synchronization success rate.
3. Tampering detection after reconnection.
4. Verification delay.
5. Number of unresolved chain conflicts.
6. Central verifier storage overhead.

### Expected Outputs

1. Local chain files per simulated gateway.
2. Central verifier synchronization log.
3. Offline-window tampering report.
4. Connectivity scenario table.

### Risks

1. Connectivity is simulated, not measured in a real rural network.
2. Conflict-resolution policy may require more design than expected.
3. Reviewers may ask for real deployment evidence; position this as a controlled simulation.

## Experiment 6: Cross-Domain Replication with Water Quality Data

### Objective

Test whether the same integrity architecture can be applied to a second environmental domain.

### Input Data

Water quality records from a public source.

### Dataset Source

Water Quality Portal: https://www.waterqualitydata.us/

Final data extract: TODO:DATA_NEEDED

### Required Preprocessing

1. Identify a small set of stations and parameters.
2. Normalize measurement fields.
3. Normalize units and timestamps.
4. Map water-quality metadata to the common event schema.
5. Preserve source-specific fields separately.

### Experimental Procedure

1. Repeat Experiment 1 on water quality records.
2. Repeat a subset of Experiment 2 tampering attacks.
3. Compare schema fit and preprocessing burden against air quality data.

### Evaluation Metrics

1. Schema coverage rate.
2. Missing metadata rate.
3. Chain construction success rate.
4. Tampering detection metrics for selected attacks.
5. Preprocessing complexity, measured as number of source-specific transformations.

### Expected Outputs

1. Water-quality event schema mapping.
2. Water-quality integrity chain.
3. Cross-domain applicability notes.
4. Comparison table against the air-quality MVP.

### Risks

1. Water-quality data may have more heterogeneous parameters and units.
2. Station metadata may require additional cleaning.
3. This experiment may broaden the paper too much if the MVP is not complete.

## Experiment 7: Provenance Graph Export

### Objective

Represent measurement, correction, station, operator, and verification relationships as a provenance graph for audit review.

### Input Data

Audit event log from Experiment 3.

### Dataset Source

Derived from MVP dataset plus synthetic audit events. TODO:DATA_NEEDED

### Required Preprocessing

1. Convert events into nodes and edges.
2. Define node types:
   - measurement,
   - station,
   - sensor key,
   - operator,
   - correction,
   - verification report,
   - summary block.
3. Define edge types:
   - authored_by,
   - measured_at,
   - corrects,
   - verified_by,
   - covered_by_summary,
   - derived_from.

### Experimental Procedure

1. Generate a provenance graph from audit events.
2. Query correction lineage for selected records.
3. Query records affected by revoked keys.
4. Query records covered by failed verification reports.
5. Export graph summary for audit review.

### Evaluation Metrics

1. Number of nodes and edges.
2. Correction lineage query success.
3. Revoked-key impact query success.
4. Failed-verification traceability.
5. Graph generation runtime.

### Expected Outputs

1. Provenance graph file.
2. Query examples.
3. Audit traceability report.

### Risks

1. Graph modeling may distract from the core hash verification contribution.
2. Requires careful explanation to avoid becoming a separate paper.

## MVP Implementation Schedule

Target duration: 2 to 3 weeks.

Week 1:

1. Select one public dataset source.
2. Download and freeze a small data extract.
3. Implement preprocessing and event schema.
4. Implement baseline hash-chain builder.

Week 2:

1. Implement verifier.
2. Implement controlled tampering generator.
3. Implement detection metrics.
4. Implement audit/provenance events.

Week 3:

1. Clean scripts and outputs.
2. Run MVP experiments.
3. Produce tables and figures.
4. Decide whether summary-block experiment can be included.

## Minimum Publishable Outputs

1. Dataset extraction script and frozen dataset description. TODO:DATA_NEEDED
2. Environmental integrity event schema.
3. Hash-chain construction prototype.
4. Tampering generator with ground truth labels.
5. Verification engine.
6. Audit/provenance event model.
7. Tables for detection metrics and overhead after execution. TODO:EXPERIMENT_NEEDED
8. Architecture figure based on semi-decentralized rural monitoring.

## Recommended MVP Scope

Use the following minimum set:

1. Experiment 1: Hash-Chain Integrity Baseline.
2. Experiment 2: Controlled Tampering Detection.
3. Experiment 3: Audit Trail and Provenance Verification.

This set is realistic because it requires one public dataset, one local prototype, and synthetic integrity attacks with known labels. It supports claims about feasibility and verification behavior, but it does not require a deployed blockchain network or real rural sensor infrastructure.

## Recommended Extended Scope

If time remains, add:

1. Experiment 4: Summary-Block Verification Efficiency.
2. Experiment 5: Intermittent Connectivity and Delayed Synchronization.

Only add Experiment 6 or 7 if the paper needs broader generality or stronger audit-trail visualization.

## What Not To Claim Yet

1. Do not claim environmental deployment success.
2. Do not claim real-world tampering detection without real tampering cases.
3. Do not claim regulatory compliance.
4. Do not claim blockchain superiority over all conventional databases.
5. Do not claim rural operational robustness unless connectivity simulation is performed.
6. Do not report any performance or detection results until the experiments are run.

## Open Experimental Decisions

1. Choose OpenAQ or EPA AQS as the MVP dataset. TODO:DATA_NEEDED
2. Choose pollutant, region, and time window. TODO:DATA_NEEDED
3. Decide whether to include signatures or key identifiers only in the MVP.
4. Decide whether summary blocks are MVP or extended.
5. Decide whether water-quality replication is needed for venue fit.
6. Decide whether source code should be packaged as supplementary material.
