"""Batch scenario planning and execution for integrity experiments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from experiments.common.paths import (
    AUDIT_OUTPUT_DIR,
    CHAIN_OUTPUT_DIR,
    METRICS_OUTPUT_DIR,
    TAMPERED_DATA_DIR,
    VERIFICATION_OUTPUT_DIR,
)
from experiments.integrity.events import MODEL_A, MODEL_B, MODEL_C, MODEL_D
from experiments.integrity.evaluation import evaluate_scenario
from experiments.integrity.tampering import (
    THREAT_BROKEN_PROVENANCE,
    THREAT_FAKE_RECORD_INSERTION,
    THREAT_RECORD_DELETION,
    THREAT_REPLAY,
    THREAT_TIMESTAMP_MODIFICATION,
    THREAT_VALUE_MODIFICATION,
    generate_tampered_artifact,
)
from experiments.integrity.verification import verify_model_artifact


MODEL_ARTIFACTS = {
    MODEL_A: AUDIT_OUTPUT_DIR / "{dataset_id}_model_a_measurements.jsonl",
    MODEL_B: AUDIT_OUTPUT_DIR / "{dataset_id}_model_b_audit_events.jsonl",
    MODEL_C: CHAIN_OUTPUT_DIR / "{dataset_id}_model_c_hash_chain.jsonl",
    MODEL_D: CHAIN_OUTPUT_DIR / "{dataset_id}_model_d_provenance_chain.jsonl",
}

BASE_THREATS = [
    THREAT_VALUE_MODIFICATION,
    THREAT_TIMESTAMP_MODIFICATION,
    THREAT_RECORD_DELETION,
    THREAT_FAKE_RECORD_INSERTION,
    THREAT_REPLAY,
]


def plan_scenarios(dataset_id: str) -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []
    for model_id in (MODEL_A, MODEL_B, MODEL_C, MODEL_D):
        threats = list(BASE_THREATS)
        if model_id == MODEL_D:
            threats.append(THREAT_BROKEN_PROVENANCE)
        for threat_type in threats:
            artifact_file = Path(str(MODEL_ARTIFACTS[model_id]).format(dataset_id=dataset_id))
            scenarios.append(
                {
                    "dataset_id": dataset_id,
                    "model_id": model_id,
                    "threat_type": threat_type,
                    "artifact_file": str(artifact_file),
                    "scenario_id": f"{dataset_id}_{model_id}_{threat_type}",
                }
            )
    return scenarios


def run_scenarios(
    *,
    dataset_id: str,
    output_dir: Path = TAMPERED_DATA_DIR,
    verification_output_dir: Path = VERIFICATION_OUTPUT_DIR / "tampered",
    metrics_output_dir: Path = METRICS_OUTPUT_DIR / "tampered",
    verify: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    scenarios = plan_scenarios(dataset_id)
    if dry_run:
        return {
            "dataset_id": dataset_id,
            "dry_run": True,
            "scenario_count": len(scenarios),
            "scenarios": scenarios,
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    if verify:
        verification_output_dir.mkdir(parents=True, exist_ok=True)
        metrics_output_dir.mkdir(parents=True, exist_ok=True)

    generated = []
    for scenario in scenarios:
        tamper_summary = generate_tampered_artifact(
            dataset_id=dataset_id,
            model_id=scenario["model_id"],
            threat_type=scenario["threat_type"],
            artifact_file=Path(scenario["artifact_file"]),
            output_dir=output_dir,
        )
        item: dict[str, Any] = {"tampering": tamper_summary}
        if verify:
            verification = verify_model_artifact(
                model_id=scenario["model_id"],
                artifact_file=Path(tamper_summary["tampered_artifact_file"]),
                dataset_id=dataset_id,
                output_dir=verification_output_dir,
            )
            item["verification"] = verification
            item["evaluation"] = evaluate_scenario(
                labels_file=Path(tamper_summary["labels_file"]),
                alerts_file=Path(verification["alerts_file"]),
                output_dir=metrics_output_dir,
            )
        generated.append(item)

    summary = {
        "dataset_id": dataset_id,
        "dry_run": False,
        "verification_enabled": verify,
        "scenario_count": len(generated),
        "output_dir": str(output_dir),
        "verification_output_dir": str(verification_output_dir) if verify else None,
        "metrics_output_dir": str(metrics_output_dir) if verify else None,
        "scenarios": generated,
    }
    summary_file = output_dir / f"{dataset_id}_scenario_batch_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    summary["summary_file"] = str(summary_file)
    return summary
