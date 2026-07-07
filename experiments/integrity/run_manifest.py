"""Build reproducibility manifests for completed experiment runs."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from experiments.common.hashing import sha256_file
from experiments.common.paths import (
    AUDIT_OUTPUT_DIR,
    CHAIN_OUTPUT_DIR,
    MANIFEST_OUTPUT_DIR,
    METRICS_OUTPUT_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    TAMPERED_DATA_DIR,
    VERIFICATION_OUTPUT_DIR,
    ensure_experiment_dirs,
)
from experiments.integrity.evaluation import MODEL_ORDER


def build_experiment_run_manifest(
    *,
    dataset_id: str,
    output_dir: Path = MANIFEST_OUTPUT_DIR,
    run_label: str | None = None,
) -> dict[str, Any]:
    """Create JSON and Markdown manifests for the current local run artifacts."""

    ensure_experiment_dirs()
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics_summary = _read_json(METRICS_OUTPUT_DIR / f"{dataset_id}_metrics_summary.json")
    scenario_count = int(metrics_summary["scenario_count"])
    evaluations = _scenario_evaluations(dataset_id)

    manifest = {
        "manifest_type": "experiment_run_manifest",
        "manifest_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "dataset_id": dataset_id,
        "methodology_decisions": {
            "scenario_repetitions": "not_used_for_current_mvp",
            "older_smoke_summaries_updated": False,
            "delayed_synchronization_scope": "model_d_only",
        },
        "dataset": _dataset_section(dataset_id),
        "implementation_files": _implementation_files(),
        "integrity_models": _model_artifacts(dataset_id),
        "scenario_run": {
            "scenario_count": scenario_count,
            "evaluation_count": len(evaluations),
            "status_counts": metrics_summary["status_counts"],
            "scenarios": evaluations,
        },
        "aggregate_outputs": _aggregate_outputs(dataset_id),
        "extended_outputs": _extended_outputs(dataset_id),
    }

    filename_prefix = f"{dataset_id}_{run_label}" if run_label else dataset_id
    manifest["manifest_files"] = {
        "json": _relative(output_dir / f"{filename_prefix}_experiment_run_manifest.json"),
        "markdown": _relative(output_dir / f"{filename_prefix}_experiment_run_manifest.md"),
    }

    if len(evaluations) != scenario_count:
        manifest["warnings"] = [
            f"Metrics summary scenario_count={scenario_count}, but {len(evaluations)} evaluation files were found."
        ]
    else:
        manifest["warnings"] = []

    json_path = output_dir / f"{filename_prefix}_experiment_run_manifest.json"
    md_path = output_dir / f"{filename_prefix}_experiment_run_manifest.md"
    json_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(_markdown(manifest), encoding="utf-8")

    return {
        "dataset_id": dataset_id,
        "run_label": run_label,
        "scenario_count": scenario_count,
        "status_counts": metrics_summary["status_counts"],
        "manifest_json": str(json_path),
        "manifest_markdown": str(md_path),
        "warnings": manifest["warnings"],
    }


def _dataset_section(dataset_id: str) -> dict[str, Any]:
    processed_manifest = PROCESSED_DATA_DIR / f"{dataset_id}_manifest.json"
    preprocessing_report = PROCESSED_DATA_DIR / f"{dataset_id}_preprocessing_report.json"
    download_metadata = RAW_DATA_DIR / f"{dataset_id}_openaq_v3_download_metadata.json"
    download_state = RAW_DATA_DIR / f"{dataset_id}_openaq_v3_download_state.json"
    raw_measurements = RAW_DATA_DIR / f"{dataset_id}_openaq_v3_measurements.jsonl"
    raw_ingested = RAW_DATA_DIR / f"{dataset_id}.jsonl"
    processed_csv = PROCESSED_DATA_DIR / f"{dataset_id}_measurements.csv"
    processed_jsonl = PROCESSED_DATA_DIR / f"{dataset_id}_measurements.jsonl"

    section = {
        "source": "OpenAQ",
        "processed_manifest": _file_entry(processed_manifest),
        "preprocessing_report": _file_entry(preprocessing_report),
        "raw_measurements": _file_entry(raw_measurements),
        "raw_ingested_file": _file_entry(raw_ingested),
        "download_metadata": _file_entry(download_metadata),
        "download_state": _file_entry(download_state),
        "processed_measurements_csv": _file_entry(processed_csv),
        "processed_measurements_jsonl": _file_entry(processed_jsonl),
    }
    if preprocessing_report.exists():
        report = _read_json(preprocessing_report)
        section["record_counts"] = {
            "input_records": report.get("input_records"),
            "output_records": report.get("output_records"),
            "dropped_records": report.get("dropped_records"),
            "station_count": report.get("station_count"),
            "parameter_count": report.get("parameter_count"),
        }
    if download_metadata.exists():
        metadata = _read_json(download_metadata)
        section["selection"] = {
            "cities": [item["city"]["display_name"] for item in metadata.get("city_selection_reports", [])],
            "selected_location_count": sum(
                int(item.get("selected_location_count", 0))
                for item in metadata.get("city_selection_reports", [])
            ),
        }
        for key in ("datetime_from", "datetime_to", "selection_mode"):
            if key in metadata:
                section["selection"][key] = metadata[key]
    return section


def _model_artifacts(dataset_id: str) -> list[dict[str, Any]]:
    return [
        {
            "model_id": MODEL_ORDER[0],
            "artifact": _file_entry(AUDIT_OUTPUT_DIR / f"{dataset_id}_model_a_measurements.jsonl"),
            "summary": _file_entry(AUDIT_OUTPUT_DIR / f"{dataset_id}_baseline_models_summary.json"),
        },
        {
            "model_id": MODEL_ORDER[1],
            "artifact": _file_entry(AUDIT_OUTPUT_DIR / f"{dataset_id}_model_b_audit_events.jsonl"),
            "summary": _file_entry(AUDIT_OUTPUT_DIR / f"{dataset_id}_baseline_models_summary.json"),
        },
        {
            "model_id": MODEL_ORDER[2],
            "artifact": _file_entry(CHAIN_OUTPUT_DIR / f"{dataset_id}_model_c_hash_chain.jsonl"),
            "summary": _file_entry(CHAIN_OUTPUT_DIR / f"{dataset_id}_model_c_hash_chain_summary.json"),
        },
        {
            "model_id": MODEL_ORDER[3],
            "artifact": _file_entry(CHAIN_OUTPUT_DIR / f"{dataset_id}_model_d_provenance_chain.jsonl"),
            "summary": _file_entry(CHAIN_OUTPUT_DIR / f"{dataset_id}_model_d_provenance_chain_summary.json"),
        },
    ]


def _scenario_evaluations(dataset_id: str) -> list[dict[str, Any]]:
    evaluation_dir = METRICS_OUTPUT_DIR / "tampered"
    rows = []
    for path in sorted(evaluation_dir.glob(f"{dataset_id}_*_evaluation.json")):
        item = _read_json(path)
        scenario_id = item["scenario_id"]
        label_file = Path(item["labels_file"])
        alerts_file = Path(item["alerts_file"])
        rows.append(
            {
                "scenario_id": scenario_id,
                "model_id": item["model_id"],
                "threat_type": item["threat_type"],
                "label_count": item["label_count"],
                "alerts_count": item["alerts_count"],
                "status_counts": item["status_counts"],
                "actual_alert_codes": item.get("actual_alert_codes", []),
                "evaluation_file": _file_entry(path),
                "labels_file": _file_entry(label_file),
                "tampered_artifact": _file_entry(TAMPERED_DATA_DIR / f"{scenario_id}.jsonl"),
                "verification_report": _file_entry(
                    _verification_report_path(dataset_id, scenario_id, item["model_id"])
                ),
                "alerts_file": _file_entry(alerts_file),
            }
        )
    return rows


def _aggregate_outputs(dataset_id: str) -> dict[str, Any]:
    return {
        "scenario_metrics": _file_entry(METRICS_OUTPUT_DIR / f"{dataset_id}_scenario_metrics.csv"),
        "threat_coverage_matrix": _file_entry(METRICS_OUTPUT_DIR / f"{dataset_id}_threat_coverage_matrix.csv"),
        "metrics_summary": _file_entry(METRICS_OUTPUT_DIR / f"{dataset_id}_metrics_summary.json"),
        "full_matrix_summary_en": _file_entry(Path("experiments/outputs/full_matrix_summary_en.md")),
        "full_matrix_summary_pl": _file_entry(Path("experiments/outputs/full_matrix_summary_pl.md")),
    }


def _extended_outputs(dataset_id: str) -> dict[str, Any]:
    return {
        "negative_case_metrics": _file_entry(
            METRICS_OUTPUT_DIR / "negative" / f"{dataset_id}_negative_case_metrics.csv"
        ),
        "negative_case_summary": _file_entry(
            METRICS_OUTPUT_DIR / "negative" / f"{dataset_id}_negative_case_summary.json"
        ),
        "cost_metrics": _file_entry(Path("experiments/outputs/cost") / f"{dataset_id}_cost_metrics.csv"),
        "cost_summary": _file_entry(Path("experiments/outputs/cost") / f"{dataset_id}_cost_summary.json"),
        "threat_model_json": _file_entry(Path("experiments/outputs/threat_model/integrity_threat_model.json")),
        "threat_model_markdown": _file_entry(Path("experiments/outputs/threat_model/integrity_threat_model.md")),
        "extended_methods_ready_notes": _file_entry(
            Path("experiments/outputs/article_materials/extended_methods_ready_notes.md")
        ),
        "extended_results_ready_tables": _file_entry(
            Path("experiments/outputs/article_materials/extended_results_ready_tables.md")
        ),
    }


def _implementation_files() -> dict[str, Any]:
    paths = [
        Path("pyproject.toml"),
        Path("experiments/common/hashing.py"),
        Path("experiments/common/manifest.py"),
        Path("experiments/common/paths.py"),
        Path("experiments/common/schema.py"),
        Path("experiments/common/storage.py"),
        Path("experiments/integrity/cli.py"),
        Path("experiments/integrity/evaluation.py"),
        Path("experiments/integrity/events.py"),
        Path("experiments/integrity/models.py"),
        Path("experiments/integrity/run_manifest.py"),
        Path("experiments/integrity/scenarios.py"),
        Path("experiments/integrity/tampering.py"),
        Path("experiments/integrity/verification.py"),
        Path("experiments/openaq/cli.py"),
        Path("experiments/openaq/download.py"),
        Path("experiments/openaq/ingest.py"),
        Path("experiments/openaq/map.py"),
    ]
    return {str(path): _file_entry(path) for path in paths}


def _verification_report_path(dataset_id: str, scenario_id: str, model_id: str) -> Path:
    return VERIFICATION_OUTPUT_DIR / "tampered" / scenario_id / f"{dataset_id}_{model_id}_verification_report.json"


def _file_entry(path: Path) -> dict[str, Any]:
    normalized = path if path.is_absolute() else Path.cwd() / path
    exists = normalized.exists()
    entry: dict[str, Any] = {
        "path": _relative(normalized),
        "exists": exists,
    }
    if exists and normalized.is_file():
        entry["size_bytes"] = normalized.stat().st_size
        entry["sha256"] = sha256_file(normalized)
    return entry


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(resolved)


def _markdown(manifest: dict[str, Any]) -> str:
    status_counts = manifest["scenario_run"]["status_counts"]
    lines = [
        "# Experiment Run Manifest",
        "",
        f"Generated: `{manifest['generated_at_utc']}`",
        "",
        f"Dataset ID: `{manifest['dataset_id']}`",
        "",
        "This is a reproducibility manifest for local proof-of-concept artifacts. It is not manuscript prose.",
        "",
        "## Dataset",
        "",
        f"- Source: `{manifest['dataset']['source']}`",
        f"- Input records: `{manifest['dataset'].get('record_counts', {}).get('input_records')}`",
        f"- Canonical records: `{manifest['dataset'].get('record_counts', {}).get('output_records')}`",
        f"- Dropped records: `{manifest['dataset'].get('record_counts', {}).get('dropped_records')}`",
        f"- Selected locations: `{manifest['dataset'].get('selection', {}).get('selected_location_count')}`",
        "",
        "## Scenario Run",
        "",
        f"- Scenarios: `{manifest['scenario_run']['scenario_count']}`",
        f"- Evaluations: `{manifest['scenario_run']['evaluation_count']}`",
        f"- `detected`: `{status_counts.get('detected', 0)}`",
        f"- `expected_not_detected`: `{status_counts.get('expected_not_detected', 0)}`",
        f"- `missed`: `{status_counts.get('missed', 0)}`",
        f"- `partial`: `{status_counts.get('partial', 0)}`",
        f"- `unexpected_alert`: `{status_counts.get('unexpected_alert', 0)}`",
        "",
        "## Methodology Decisions",
        "",
        "- Scenario repetitions: `not_used_for_current_mvp`",
        "- Older smoke summaries updated: `false`",
        "- Delayed synchronization scope: `model_d_only`",
        "",
        "## Aggregate Outputs",
        "",
    ]
    for name, entry in manifest["aggregate_outputs"].items():
        lines.append(f"- `{name}`: `{entry['path']}` (`sha256={entry.get('sha256', 'missing')}`)")
    lines.extend(["", "## Extended Outputs", ""])
    for name, entry in manifest["extended_outputs"].items():
        lines.append(f"- `{name}`: `{entry['path']}` (`sha256={entry.get('sha256', 'missing')}`)")
    lines.extend(["", "## Implementation Files", ""])
    for name, entry in manifest["implementation_files"].items():
        lines.append(f"- `{name}`: `sha256={entry.get('sha256', 'missing')}`")
    lines.extend(["", "## Integrity Model Artifacts", ""])
    for model in manifest["integrity_models"]:
        lines.append(
            f"- `{model['model_id']}`: `{model['artifact']['path']}` "
            f"(`sha256={model['artifact'].get('sha256', 'missing')}`)"
        )
    lines.extend(["", "## Scenario Files", ""])
    lines.append("| Scenario | Model | Threat | Status | Artifact SHA-256 | Evaluation SHA-256 |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for scenario in manifest["scenario_run"]["scenarios"]:
        status = _scenario_status(scenario["status_counts"])
        lines.append(
            f"| `{scenario['scenario_id']}` | `{scenario['model_id']}` | `{scenario['threat_type']}` | "
            f"`{status}` | `{scenario['tampered_artifact'].get('sha256', 'missing')}` | "
            f"`{scenario['evaluation_file'].get('sha256', 'missing')}` |"
        )
    if manifest["warnings"]:
        lines.extend(["", "## Warnings", ""])
        for warning in manifest["warnings"]:
            lines.append(f"- {warning}")
    lines.append("")
    return "\n".join(lines)


def _scenario_status(status_counts: dict[str, int]) -> str:
    for status in ("detected", "partial", "missed", "expected_not_detected", "unexpected_alert"):
        count = status_counts.get(status, 0)
        if count:
            return status
    return "unknown"
