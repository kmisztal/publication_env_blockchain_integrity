# Methodology Decisions

This file records current decisions for later manuscript preparation. It is not a manuscript section.

## Project Positioning

Decision: position the paper primarily as a computer science / information systems contribution.

Rationale: the central comparison concerns integrity models, auditability, hash-chain linkage, provenance, permission reconstruction, and reproducible verification. Environmental monitoring is the application domain and provides realistic data characteristics.

## Dataset Choice

Decision: use OpenAQ as the first MVP dataset.

Rationale: OpenAQ provides public environmental monitoring data with realistic distributed time-series characteristics. The MVP intentionally avoids combining multiple public datasets at once.

## City And Station Selection

Decision: use Warsaw, Berlin, Paris, and Madrid with three selected monitoring locations per city.

Rationale: this creates a multi-city, multi-source dataset while keeping the experiment bounded and reproducible.

Current use in experiments: all stations are combined into one canonical dataset. The current integrity benchmark does not run separate experiments per city or station.

## Integrity Model Set

Decision: compare four core models.

- A: conventional storage only
- B: audit trail only
- C: audit trail plus hash chain
- D: audit trail plus hash chain plus provenance/permission reconstruction

Rationale: the sequence isolates the contribution of audit events, hash-chain continuity, and governance/provenance state.

## Threat Scenario Set

Decision: evaluate controlled scenarios for value modification, timestamp modification, record deletion, fake record insertion, replay, broken provenance, unauthorized correction, revoked actor key usage, missing correction reason, and delayed synchronization.

Rationale: these scenarios cover basic data manipulation, stream-continuity attacks, and governance/provenance failures relevant to environmental monitoring records.

## Scenario Repetitions

Decision: do not add scenario repetitions for the current MVP.

Rationale: one deterministic injection per applicable model/threat pair is sufficient for the current reproducible mechanism-comparison benchmark. Repetitions would support statistical robustness claims, which are outside the present MVP.

## Negative Cases And Accuracy Metrics

Decision: defer negative-case design and do not report precision, recall, F1, false-positive rate, or false-negative rate from the current run.

Rationale: those metrics require explicit negative cases and a separate evaluation design. The current benchmark reports scenario status and threat coverage.

## Not Applicable Cells

Decision: use `not_applicable` rather than blank cells in the threat-coverage matrix.

Rationale: this makes it explicit when a scenario is outside a model's implemented capability set.

## Delayed Synchronization

Decision: keep `delayed_synchronization` scoped to Model D only.

Rationale: the current implementation represents delayed synchronization as a synchronization event with event context and a maximum allowed delay threshold. This belongs to the Model D provenance/permission layer rather than the simpler storage or audit-only models.

## Smoke-Test Summaries

Decision: do not update older smoke-test summaries for cosmetic consistency.

Rationale: smoke-test summaries are tool-chain checks, not final experiment summaries. The full matrix summary and manifest are the primary review artifacts.

## Cross-Sensor Consistency

Decision: do not mix cross-sensor plausibility checking into Models A-D.

Rationale: cross-sensor comparison is a different layer. It may be implemented later as an exploratory environmental consistency module, but it should not be presented as a core blockchain/integrity mechanism.

## Full Intermittent Connectivity Simulation

Decision: defer full station/gateway chain simulation, offline queues, and central synchronization of summary hashes.

Rationale: the MVP includes a delayed-synchronization scenario, but full intermittent-connectivity simulation would be a separate extension.

## Manuscript Preparation

Decision: prepare article materials separately from manuscript text.

Rationale: the current files provide structured input for writing, but final Methods, Results, and Discussion prose should be drafted after reviewing the materials and limitations.

