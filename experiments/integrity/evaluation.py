"""Compare tampering labels against verifier alerts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from experiments.common.paths import METRICS_OUTPUT_DIR, ensure_experiment_dirs


STATUS_DETECTED = "detected"
STATUS_PARTIAL = "partial"
STATUS_MISSED = "missed"
STATUS_EXPECTED_NOT_DETECTED = "expected_not_detected"
STATUS_UNEXPECTED_ALERT = "unexpected_alert"

MODEL_ORDER = [
    "A_conventional_storage",
    "B_audit_trail",
    "C_audit_hash_chain",
    "D_audit_hash_chain_provenance",
]


def evaluate_scenario(
    *,
    labels_file: Path,
    alerts_file: Path,
    output_dir: Path = METRICS_OUTPUT_DIR,
) -> dict[str, Any]:
    ensure_experiment_dirs()
    output_dir.mkdir(parents=True, exist_ok=True)
    labels_doc = json.loads(labels_file.read_text(encoding="utf-8"))
    alerts = _read_alerts(alerts_file)
    actual_codes = sorted({alert["alert_code"] for alert in alerts if alert.get("alert_code")})

    evaluations = []
    for label in labels_doc["labels"]:
        expected_codes = sorted(label.get("expected_alert_codes", []))
        status = _status(expected_codes, actual_codes)
        evaluations.append(
            {
                "label_id": label["label_id"],
                "target_index": label["target_index"],
                "target_record_id": label.get("target_record_id"),
                "target_event_id": label.get("target_event_id"),
                "expected_alert_codes": expected_codes,
                "actual_alert_codes": actual_codes,
                "status": status,
            }
        )

    scenario_id = labels_doc["scenario_id"]
    summary = {
        "scenario_id": scenario_id,
        "dataset_id": labels_doc["dataset_id"],
        "model_id": labels_doc["model_id"],
        "threat_type": labels_doc["threat_type"],
        "labels_file": str(labels_file),
        "alerts_file": str(alerts_file),
        "label_count": len(labels_doc["labels"]),
        "alerts_count": len(alerts),
        "actual_alert_codes": actual_codes,
        "status_counts": _status_counts(evaluations),
        "evaluations": evaluations,
    }
    output_file = output_dir / f"{scenario_id}_evaluation.json"
    output_file.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    summary["evaluation_file"] = str(output_file)
    return summary


def aggregate_evaluations(
    *,
    evaluation_dir: Path,
    output_dir: Path = METRICS_OUTPUT_DIR,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    ensure_experiment_dirs()
    output_dir.mkdir(parents=True, exist_ok=True)
    evaluations = _read_evaluation_files(evaluation_dir, dataset_id=dataset_id)
    scenario_rows = [_scenario_row(item) for item in evaluations]
    matrix_rows = _matrix_rows(scenario_rows)

    scenario_metrics_file = output_dir / _dataset_filename(dataset_id, "scenario_metrics.csv")
    coverage_matrix_file = output_dir / _dataset_filename(dataset_id, "threat_coverage_matrix.csv")
    summary_file = output_dir / _dataset_filename(dataset_id, "metrics_summary.json")

    _write_csv(scenario_metrics_file, scenario_rows)
    _write_csv(coverage_matrix_file, matrix_rows)

    summary = {
        "dataset_id": dataset_id,
        "evaluation_dir": str(evaluation_dir),
        "evaluation_files": [str(item["evaluation_file"]) for item in evaluations],
        "scenario_count": len(scenario_rows),
        "scenario_metrics_file": str(scenario_metrics_file),
        "threat_coverage_matrix_file": str(coverage_matrix_file),
        "status_counts": _aggregate_status_counts(scenario_rows),
        "summary_file": str(summary_file),
    }
    summary_file.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def _read_alerts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _status(expected_codes: list[str], actual_codes: list[str]) -> str:
    expected = set(expected_codes)
    actual = set(actual_codes)
    if not expected and not actual:
        return STATUS_EXPECTED_NOT_DETECTED
    if not expected and actual:
        return STATUS_UNEXPECTED_ALERT
    if expected.issubset(actual):
        return STATUS_DETECTED
    if expected.intersection(actual):
        return STATUS_PARTIAL
    return STATUS_MISSED


def _status_counts(evaluations: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        STATUS_DETECTED: 0,
        STATUS_PARTIAL: 0,
        STATUS_MISSED: 0,
        STATUS_EXPECTED_NOT_DETECTED: 0,
        STATUS_UNEXPECTED_ALERT: 0,
    }
    for item in evaluations:
        counts[item["status"]] += 1
    return counts


def _read_evaluation_files(evaluation_dir: Path, *, dataset_id: str | None) -> list[dict[str, Any]]:
    files = sorted(evaluation_dir.glob("*_evaluation.json"))
    evaluations = []
    for path in files:
        item = json.loads(path.read_text(encoding="utf-8"))
        if dataset_id and item.get("dataset_id") != dataset_id:
            continue
        item["evaluation_file"] = str(path)
        evaluations.append(item)
    if not evaluations:
        raise ValueError(f"No evaluation JSON files found in {evaluation_dir}")
    return evaluations


def _scenario_row(item: dict[str, Any]) -> dict[str, Any]:
    counts = item["status_counts"]
    label_count = int(item["label_count"])
    detected = int(counts.get(STATUS_DETECTED, 0))
    partial = int(counts.get(STATUS_PARTIAL, 0))
    missed = int(counts.get(STATUS_MISSED, 0))
    expected_not_detected = int(counts.get(STATUS_EXPECTED_NOT_DETECTED, 0))
    unexpected_alert = int(counts.get(STATUS_UNEXPECTED_ALERT, 0))
    return {
        "dataset_id": item["dataset_id"],
        "scenario_id": item["scenario_id"],
        "model_id": item["model_id"],
        "threat_type": item["threat_type"],
        "label_count": label_count,
        "alerts_count": int(item["alerts_count"]),
        "detected_count": detected,
        "partial_count": partial,
        "missed_count": missed,
        "expected_not_detected_count": expected_not_detected,
        "unexpected_alert_count": unexpected_alert,
        "scenario_status": _scenario_status(
            label_count=label_count,
            detected=detected,
            partial=partial,
            missed=missed,
            expected_not_detected=expected_not_detected,
            unexpected_alert=unexpected_alert,
        ),
        "detected_label_rate": _rate(detected, label_count),
        "detected_or_partial_label_rate": _rate(detected + partial, label_count),
        "actual_alert_codes": ";".join(item.get("actual_alert_codes", [])),
        "evaluation_file": item["evaluation_file"],
    }


def _scenario_status(
    *,
    label_count: int,
    detected: int,
    partial: int,
    missed: int,
    expected_not_detected: int,
    unexpected_alert: int,
) -> str:
    if unexpected_alert:
        return STATUS_UNEXPECTED_ALERT
    if label_count and expected_not_detected == label_count:
        return STATUS_EXPECTED_NOT_DETECTED
    if label_count and detected == label_count:
        return STATUS_DETECTED
    if detected or partial:
        return STATUS_PARTIAL
    if missed:
        return STATUS_MISSED
    return STATUS_EXPECTED_NOT_DETECTED


def _rate(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return ""
    return f"{numerator / denominator:.6f}"


def _matrix_rows(scenario_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_threat: dict[str, dict[str, str]] = {}
    for row in scenario_rows:
        threat = row["threat_type"]
        by_threat.setdefault(threat, {"threat_type": threat})
        by_threat[threat][row["model_id"]] = row["scenario_status"]

    rows = []
    for threat in sorted(by_threat):
        row = by_threat[threat]
        rows.append({"threat_type": threat, **{model_id: row.get(model_id, "") for model_id in MODEL_ORDER}})
    return rows


def _aggregate_status_counts(scenario_rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {
        STATUS_DETECTED: 0,
        STATUS_PARTIAL: 0,
        STATUS_MISSED: 0,
        STATUS_EXPECTED_NOT_DETECTED: 0,
        STATUS_UNEXPECTED_ALERT: 0,
    }
    for row in scenario_rows:
        counts[row["scenario_status"]] += 1
    return counts


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _dataset_filename(dataset_id: str | None, suffix: str) -> str:
    if dataset_id:
        return f"{dataset_id}_{suffix}"
    return suffix
