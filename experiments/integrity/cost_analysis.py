"""Measure storage and runtime costs for integrity-model artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

from experiments.common.paths import (
    AUDIT_OUTPUT_DIR,
    CHAIN_OUTPUT_DIR,
    COST_OUTPUT_DIR,
    METRICS_OUTPUT_DIR,
    PROCESSED_DATA_DIR,
    TAMPERED_DATA_DIR,
    VERIFICATION_OUTPUT_DIR,
    ensure_experiment_dirs,
)
from experiments.integrity.events import MODEL_A, MODEL_B, MODEL_C, MODEL_D
from experiments.integrity.models import (
    build_baseline_artifacts,
    build_hash_chain_artifacts,
    build_provenance_artifacts,
)
from experiments.integrity.verification import verify_model_artifact


MODEL_ARTIFACTS = {
    MODEL_A: AUDIT_OUTPUT_DIR / "{dataset_id}_model_a_measurements.jsonl",
    MODEL_B: AUDIT_OUTPUT_DIR / "{dataset_id}_model_b_audit_events.jsonl",
    MODEL_C: CHAIN_OUTPUT_DIR / "{dataset_id}_model_c_hash_chain.jsonl",
    MODEL_D: CHAIN_OUTPUT_DIR / "{dataset_id}_model_d_provenance_chain.jsonl",
}


def run_cost_analysis(
    *,
    dataset_id: str,
    measurements_file: Path | None = None,
    output_dir: Path = COST_OUTPUT_DIR,
) -> dict[str, Any]:
    """Measure build, storage, and verification costs for Models A-D."""

    ensure_experiment_dirs()
    output_dir.mkdir(parents=True, exist_ok=True)
    measurements_file = measurements_file or PROCESSED_DATA_DIR / f"{dataset_id}_measurements.csv"

    build_output_root = output_dir / "build_artifacts"
    build_output_root.mkdir(parents=True, exist_ok=True)
    build_rows = _measure_builds(dataset_id, measurements_file, build_output_root)
    clean_rows = _measure_clean_verification(dataset_id, output_dir / "verification_clean")
    tampered_rows = _measure_tampered_verification(dataset_id, output_dir / "verification_tampered")
    model_rows = _model_cost_rows(dataset_id, build_rows, clean_rows, tampered_rows)

    model_costs_file = output_dir / f"{dataset_id}_cost_metrics.csv"
    build_costs_file = output_dir / f"{dataset_id}_build_costs.csv"
    clean_verification_file = output_dir / f"{dataset_id}_clean_verification_costs.csv"
    tampered_verification_file = output_dir / f"{dataset_id}_tampered_verification_costs.csv"
    summary_file = output_dir / f"{dataset_id}_cost_summary.json"

    _write_csv(model_costs_file, model_rows)
    _write_csv(build_costs_file, build_rows)
    _write_csv(clean_verification_file, clean_rows)
    _write_csv(tampered_verification_file, tampered_rows)

    summary = {
        "dataset_id": dataset_id,
        "measurements_file": str(measurements_file),
        "model_costs_file": str(model_costs_file),
        "build_costs_file": str(build_costs_file),
        "clean_verification_costs_file": str(clean_verification_file),
        "tampered_verification_costs_file": str(tampered_verification_file),
        "model_count": len(model_rows),
        "tampered_verification_count": len(tampered_rows),
        "peak_memory": "TODO:EXPERIMENT_NEEDED",
        "model_costs": model_rows,
    }
    summary_file.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return {**summary, "summary_file": str(summary_file)}


def _measure_builds(dataset_id: str, measurements_file: Path, output_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    baseline_dir = output_root / "audit"
    chain_dir = output_root / "chains"
    rows.extend(
        _timed_build(
            build_id="build_baseline_a_b",
            builder=lambda: build_baseline_artifacts(
                dataset_id=dataset_id,
                measurements_file=measurements_file,
                output_dir=baseline_dir,
                database_path=None,
            ),
            model_ids=[MODEL_A, MODEL_B],
        )
    )
    rows.extend(
        _timed_build(
            build_id="build_hash_chain_c",
            builder=lambda: build_hash_chain_artifacts(
                dataset_id=dataset_id,
                measurements_file=measurements_file,
                output_dir=chain_dir,
                database_path=None,
            ),
            model_ids=[MODEL_C],
        )
    )
    rows.extend(
        _timed_build(
            build_id="build_provenance_d",
            builder=lambda: build_provenance_artifacts(
                dataset_id=dataset_id,
                measurements_file=measurements_file,
                output_dir=chain_dir,
                database_path=None,
            ),
            model_ids=[MODEL_D],
        )
    )
    return rows


def _timed_build(
    *,
    build_id: str,
    builder: Callable[[], dict[str, Any]],
    model_ids: list[str],
) -> list[dict[str, Any]]:
    started = perf_counter()
    summary = builder()
    elapsed = perf_counter() - started
    rows = []
    for model_id in model_ids:
        model_summary = _extract_model_summary(summary, model_id)
        rows.append(
            {
                "build_id": build_id,
                "model_id": model_id,
                "build_time_seconds": f"{elapsed:.6f}",
                "artifact_file": model_summary.get("artifact_file"),
                "artifact_size_bytes": _file_size(model_summary.get("artifact_file")),
                "record_or_event_count": _record_or_event_count(model_summary),
            }
        )
    return rows


def _measure_clean_verification(dataset_id: str, output_dir: Path) -> list[dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for model_id, template in MODEL_ARTIFACTS.items():
        artifact = Path(str(template).format(dataset_id=dataset_id))
        started = perf_counter()
        report = verify_model_artifact(
            dataset_id=dataset_id,
            model_id=model_id,
            artifact_file=artifact,
            output_dir=output_dir / model_id,
        )
        elapsed = perf_counter() - started
        rows.append(_verification_row(dataset_id, model_id, artifact, report, elapsed, "clean"))
    return rows


def _measure_tampered_verification(dataset_id: str, output_dir: Path) -> list[dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, artifact in enumerate(sorted(TAMPERED_DATA_DIR.glob(f"{dataset_id}_*.jsonl")), start=1):
        model_id = _model_id_from_scenario_file(dataset_id, artifact)
        if model_id is None:
            continue
        scenario_id = artifact.stem
        scenario_output_dir = output_dir / f"{index:03d}_{model_id.split('_', 1)[0].lower()}"
        started = perf_counter()
        report = verify_model_artifact(
            dataset_id=dataset_id,
            model_id=model_id,
            artifact_file=artifact,
            output_dir=scenario_output_dir,
        )
        elapsed = perf_counter() - started
        row = _verification_row(dataset_id, model_id, artifact, report, elapsed, "tampered")
        row["scenario_id"] = scenario_id
        rows.append(row)
    return rows


def _model_cost_rows(
    dataset_id: str,
    build_rows: list[dict[str, Any]],
    clean_rows: list[dict[str, Any]],
    tampered_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    for model_id, template in MODEL_ARTIFACTS.items():
        artifact = Path(str(template).format(dataset_id=dataset_id))
        count = _count_jsonl_lines(artifact)
        size = artifact.stat().st_size
        model_tampered = [row for row in tampered_rows if row["model_id"] == model_id]
        rows.append(
            {
                "dataset_id": dataset_id,
                "model_id": model_id,
                "artifact_file": str(artifact),
                "artifact_size_bytes": size,
                "record_or_event_count": count,
                "bytes_per_record_or_event": f"{size / count:.6f}" if count else "",
                "build_time_seconds": _first_value(build_rows, model_id, "build_time_seconds"),
                "clean_verification_time_seconds": _first_value(clean_rows, model_id, "verification_time_seconds"),
                "clean_alerts_count": _first_value(clean_rows, model_id, "alerts_count"),
                "tampered_verification_count": len(model_tampered),
                "tampered_verification_time_mean_seconds": _mean(model_tampered, "verification_time_seconds"),
            }
        )
    return rows


def _verification_row(
    dataset_id: str,
    model_id: str,
    artifact: Path,
    report: dict[str, Any],
    elapsed: float,
    verification_case_type: str,
) -> dict[str, Any]:
    return {
        "dataset_id": dataset_id,
        "model_id": model_id,
        "verification_case_type": verification_case_type,
        "artifact_file": str(artifact),
        "artifact_size_bytes": artifact.stat().st_size,
        "checked_items": report["checked_items"],
        "alerts_count": report["alerts_count"],
        "verification_time_seconds": f"{elapsed:.6f}",
        "report_file": report["report_file"],
        "alerts_file": report["alerts_file"],
    }


def _extract_model_summary(summary: dict[str, Any], model_id: str) -> dict[str, Any]:
    if model_id == MODEL_A:
        return summary["model_a"]
    if model_id == MODEL_B:
        return summary["model_b"]
    return summary


def _record_or_event_count(summary: dict[str, Any]) -> int:
    return int(summary.get("record_count") or summary.get("event_count") or 0)


def _file_size(path: str | None) -> int | str:
    if not path:
        return ""
    return Path(path).stat().st_size


def _model_id_from_scenario_file(dataset_id: str, artifact: Path) -> str | None:
    scenario_id = artifact.stem
    prefix = f"{dataset_id}_"
    if not scenario_id.startswith(prefix):
        return None
    suffix = scenario_id.removeprefix(prefix)
    for model_id in sorted(MODEL_ARTIFACTS, key=len, reverse=True):
        if suffix.startswith(f"{model_id}_"):
            return model_id
    return None


def _count_jsonl_lines(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def _first_value(rows: list[dict[str, Any]], model_id: str, key: str) -> Any:
    for row in rows:
        if row["model_id"] == model_id:
            return row.get(key, "")
    return ""


def _mean(rows: list[dict[str, Any]], key: str) -> str:
    if not rows:
        return ""
    values = [float(row[key]) for row in rows]
    return f"{sum(values) / len(values):.6f}"


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
