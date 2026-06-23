# Reviewer-Facing Limitations

This file lists limitations that should remain visible during manuscript preparation. It is not a manuscript section.

## Scope Limits

The paper should be positioned as a computer science / information systems proof-of-concept. OpenAQ is used as a realistic environmental monitoring substrate, not as a basis for environmental-domain conclusions.

The current experiment evaluates integrity mechanisms, not air-quality correctness, sensor calibration, pollution behavior, or environmental anomaly detection.

## Dataset Limits

The current MVP uses one OpenAQ extract only.

The station-selection strategy uses three monitoring locations per city to obtain a realistic distributed dataset, but the current integrity experiment does not evaluate each city or station independently.

All selected stations are combined into one canonical dataset and one global event stream per model. There are no per-station chains, per-gateway chains, or cross-sensor consistency checks in the current MVP.

## Scenario Limits

The threat scenarios are controlled and synthetic.

Each currently implemented scenario has one deterministic injection per applicable model/threat pair. Scenario repetitions across multiple target records, stations, timestamps, or random seeds are not used in the current MVP.

The current scenario set is suitable for a reproducible mechanism-comparison benchmark, but it should not be described as a statistical robustness evaluation.

## Metric Limits

The current metrics support scenario status counts and threat coverage.

Precision, recall, F1, false-positive rate, and false-negative rate should not be reported from the current run because explicit negative cases have not been defined.

`expected_not_detected` cells indicate expected model limitations, not implementation failure.

`not_applicable` cells indicate scenarios outside the implemented scope of a given model.

## Model Limits

Model A-D compare increasingly expressive integrity mechanisms. They do not include environmental plausibility checking.

`delayed_synchronization` is implemented only for Model D, because the current event representation uses Model D provenance/permission state and synchronization metadata.

Summary-block optimization, gateway-level chains, offline queues, and central synchronization of summary hashes are deferred beyond the MVP.

## Reviewer Risks To Avoid

Do not claim that blockchain detects environmental anomalies.

Do not claim real-world manipulation detection in the OpenAQ dataset.

Do not claim statistical generalization beyond the controlled scenario set.

Do not compare cities environmentally. City selection is methodological, not an environmental result.

Do not present false-positive or false-negative rates unless a negative-case benchmark is added.

## Possible Reviewer Questions

Why use environmental data if the paper is primarily about integrity mechanisms?

Suggested answer direction: environmental monitoring provides realistic distributed, time-series, multi-source records with provenance and trust challenges.

Why are there no precision/recall/F1 metrics?

Suggested answer direction: the current benchmark evaluates controlled integrity scenarios and explicit model capabilities. Precision/recall/F1 require negative cases and a different evaluation design.

Why are three stations per city not used for cross-sensor validation?

Suggested answer direction: station diversity is used to construct a realistic distributed dataset. Cross-sensor plausibility checking is a separate environmental consistency layer and is outside the current integrity-model comparison.

Why is delayed synchronization Model D only?

Suggested answer direction: the current delayed-synchronization check depends on synchronization events and reconstructed event context, which are part of the Model D governance/provenance layer.

