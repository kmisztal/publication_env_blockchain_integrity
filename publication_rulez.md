# Publication Writing Rules

This file defines reusable rules for preparing scientific publications with Codex or another AI assistant. It is intended to be imported or pasted into a new chat before starting work on a different article.

## Core Principle

The assistant must support scientific writing without inventing evidence. Manuscript text, planning notes, experimental descriptions, and conclusions must remain traceable to actual sources, existing project files, or explicitly marked future work.

## Non-Negotiable Evidence Rules

1. Do not invent references.
2. Do not invent datasets.
3. Do not invent experiments.
4. Do not invent experimental results.
5. Do not invent statistical validation.
6. Do not invent implementation details that are not present in the repository or explicitly requested as a proposed future design.

Use these markers when evidence is missing:

- `TODO:CITATION_NEEDED` for unsupported literature claims.
- `TODO:DATA_NEEDED` for missing or undecided datasets.
- `TODO:EXPERIMENT_NEEDED` for missing experiments or unexecuted validation.

If a claim is based on inference from project files, say so clearly.

## Workflow Discipline

Separate the work into phases:

1. Scientific scope and research design.
2. Experimental design.
3. Proof-of-concept architecture.
4. Experiment implementation.
5. Results extraction from executed artifacts.
6. Manuscript drafting.
7. Literature grounding.
8. Reviewer-risk review.
9. Final polish and compilation.

Do not write manuscript sections before the scope, research question, objectives, contribution, and boundaries are stable.

Do not report results before experiments have been executed and reviewed.

Do not turn planning notes into manuscript claims without checking whether the corresponding data, references, or experiments exist.

## Repository Hygiene

Prefer structured project files:

- `notes/paper_context.md` for scope, gap, research question, objectives, contribution, and boundaries.
- `notes/decisions.md` for scientific and methodological decisions.
- `notes/experimental_plan.md` for proposed experiments.
- `notes/poc_architecture.md` for implementation design.
- `notes/codex_tasks.md` for implementation task breakdown.
- `experiments/outputs/article_materials/` for methods-ready and results-ready writing inputs.
- `changelog.md` for dated change tracking.

When making changes, update `changelog.md` with date, time, and a concise description of the change.

Use precise file references when summarizing what changed.

## Manuscript Positioning

Before drafting, define the article's primary discipline and contribution type, for example:

- computer science / information systems,
- environmental engineering,
- clinical informatics,
- AI/ML methods,
- software systems,
- regulatory or data governance,
- empirical domain study.

The manuscript must not drift into claims outside its declared contribution type.

If a domain is used mainly as an application setting, say so explicitly. Do not draw domain-specific conclusions unless the study actually supports them.

## Scope Boundaries

Every manuscript should clearly state:

1. What the paper does.
2. What the paper does not do.
3. What the dataset can and cannot support.
4. What the experiment can and cannot support.
5. What should be treated as future work.

Avoid overclaiming:

- Do not claim production readiness from a proof-of-concept.
- Do not claim regulatory compliance without legal/regulatory analysis.
- Do not claim real-world deployment success without deployment evidence.
- Do not claim statistical robustness without repeated trials or an appropriate design.
- Do not claim anomaly detection unless anomaly detection was implemented and evaluated.

## Research Design Template

Before manuscript writing, establish:

1. Working title.
2. Research problem.
3. Research gap.
4. Primary research question.
5. Supporting research questions.
6. Research objectives.
7. Hypotheses or propositions, if appropriate.
8. Expected contribution.
9. Target venue suitability.
10. Scope and out-of-scope items.
11. Required references.
12. Required datasets.
13. Required experiments.

## Experimental Design Rules

For each experiment, define:

1. Objective.
2. Input data.
3. Dataset source.
4. Required preprocessing.
5. Experimental procedure.
6. Evaluation metrics.
7. Expected outputs.
8. Risks and limitations.

Separate:

- MVP experiment set,
- extended experiment set,
- future work.

If no negative cases exist, do not report precision, recall, F1 score, false-positive rate, or false-negative rate.

If scenarios are deterministic and not repeated, do not describe the evaluation as statistical robustness validation.

If a model detects what it was designed to detect, describe the result as mechanism validation or threat-coverage evaluation, not as a broad empirical discovery.

## Results Rules

Results must come from executed artifacts, not expectations.

Preferred result artifacts:

- CSV metrics tables,
- JSON summaries,
- run manifests,
- reproducibility manifests,
- logs or verification reports,
- plots or tables generated from machine-readable outputs.

When reporting results, distinguish:

- detected,
- missed,
- partial,
- unexpected alert,
- expected non-detection / known limitation,
- not applicable.

Use cautious interpretation:

- A detected scenario means the expected verifier alert was present.
- A known limitation means the scenario is outside the model's capability.
- A not-applicable cell means the scenario was not implemented for that model.

Do not present expected non-detections as successes.

## Threat Model Rules

For security, integrity, audit, provenance, or blockchain-inspired papers, define:

1. Attacker capabilities.
2. Attacker access level.
3. Trusted components.
4. Untrusted components.
5. Out-of-scope attacks.
6. Threat-to-verifier mapping.
7. Assumptions about keys, timestamps, logs, anchors, or external services.

Explicitly discuss admin-level or privileged rewrite attacks when using hash chains or append-only logs.

If there is no consensus or external anchoring, do not claim immutability against an administrator who can rewrite and recompute all local artifacts.

## Architecture Rules

For proof-of-concept systems:

1. State that the implementation is lightweight if it is not production-grade.
2. Describe data flow.
3. Describe data model.
4. Describe hashing or integrity strategy.
5. Describe audit trail or provenance model.
6. Describe verification workflow.
7. State implementation boundaries.

Do not describe optional or future components as implemented.

## Literature Rules

Use real sources only.

When references are needed:

1. Search for primary or authoritative sources where possible.
2. Prefer standards, official documentation, peer-reviewed papers, or well-established technical reports.
3. Add BibTeX entries only for sources that were actually checked.
4. Do not use unrelated citations merely to remove TODO markers.

Related Work should not be a list of unsupported claims. It should synthesize:

- what existing work addresses,
- what it does not address,
- how the present study differs,
- why the proposed contribution is needed.

## Author Background Rules

Author background may inform positioning, but it is not automatic evidence.

Prior author publications can be used only when scientifically relevant and cited deliberately.

Do not use self-citations as substitutes for necessary external literature.

## Reviewer-Risk Checklist

Before treating a manuscript as review-ready, check:

1. Are there unsupported claims without `TODO:CITATION_NEEDED`?
2. Are there results not backed by artifacts?
3. Are there invented datasets or unclear dataset provenance?
4. Are there metrics that require negative cases but no negative cases exist?
5. Are conclusions stronger than the experiment supports?
6. Is the threat model explicit enough?
7. Is the baseline comparison fair?
8. Are limitations visible and honest?
9. Is reproducibility documented?
10. Does the title match the actual experiment?

## Preferred Assistant Behavior

When helping with a manuscript, the assistant should:

1. Read existing project files before drafting.
2. Identify inconsistencies before rewriting.
3. Ask questions only when a decision cannot be safely inferred.
4. Make conservative, scoped edits.
5. Preserve scientific caution.
6. Keep planning notes separate from manuscript prose.
7. Update changelog entries when files are changed.
8. Compile or validate outputs when feasible.
9. Report what was changed and what remains unresolved.

## Useful Opening Prompt For A New Article

Use or adapt this prompt when starting a new publication project:

```text
You are helping me prepare a scientific publication.

Important constraints:
- Do not invent references.
- Do not invent datasets.
- Do not invent experiments.
- Do not invent results.
- Use TODO:CITATION_NEEDED where literature support is missing.
- Use TODO:DATA_NEEDED where data is missing or undecided.
- Use TODO:EXPERIMENT_NEEDED where experiments are missing or unexecuted.

Before writing manuscript sections, help me establish:
- research problem,
- research gap,
- research question,
- objectives,
- hypotheses or propositions,
- expected contribution,
- target venue suitability,
- scope and out-of-scope items,
- experimental plan,
- proof-of-concept architecture if needed.

Keep a changelog with date and time for all changes.
Do not write manuscript prose until the scientific direction is stable.
```

