"""Build baseline artifacts for the MVP integrity models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from experiments.common.hashing import canonical_json, sha256_file
from experiments.common.paths import AUDIT_OUTPUT_DIR, CHAIN_OUTPUT_DIR, ensure_experiment_dirs
from experiments.common.schema import CANONICAL_MEASUREMENT_COLUMNS, missing_columns
from experiments.common.storage import replace_audit_events
from experiments.integrity.events import (
    MODEL_A,
    MODEL_B,
    MODEL_C,
    build_model_b_events,
    build_model_c_events,
    events_to_records,
)


def load_measurements(path: Path) -> pd.DataFrame:
    measurements = pd.read_csv(path)
    missing = missing_columns(measurements.columns)
    if missing:
        raise ValueError(f"Measurement file is missing canonical columns: {missing}")
    return measurements[CANONICAL_MEASUREMENT_COLUMNS].copy()


def build_model_a_artifact(
    *,
    dataset_id: str,
    measurements: pd.DataFrame,
    output_dir: Path = AUDIT_OUTPUT_DIR,
) -> dict[str, Any]:
    ensure_experiment_dirs()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{dataset_id}_model_a_measurements.jsonl"
    ordered = measurements.sort_values(["record_id"], kind="mergesort")
    with output_file.open("w", encoding="utf-8") as handle:
        for record in ordered.to_dict(orient="records"):
            handle.write(canonical_json(_json_ready(record)) + "\n")
    return {
        "model_id": MODEL_A,
        "dataset_id": dataset_id,
        "artifact_file": str(output_file),
        "record_count": int(len(ordered)),
        "artifact_hash_sha256": sha256_file(output_file),
    }


def build_model_b_artifact(
    *,
    dataset_id: str,
    measurements: pd.DataFrame,
    output_dir: Path = AUDIT_OUTPUT_DIR,
    database_path: Path | None = None,
) -> dict[str, Any]:
    ensure_experiment_dirs()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{dataset_id}_model_b_audit_events.jsonl"
    events = build_model_b_events(
        measurements,
        dataset_id=dataset_id,
        created_at_utc=_baseline_created_at(measurements),
    )
    records = events_to_records(events)
    with output_file.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=True) + "\n")
    if database_path is not None:
        replace_audit_events(database_path, records, model_id=MODEL_B)
    return {
        "model_id": MODEL_B,
        "dataset_id": dataset_id,
        "artifact_file": str(output_file),
        "event_count": len(records),
        "measurement_event_count": max(0, len(records) - 1),
        "artifact_hash_sha256": sha256_file(output_file),
        "sqlite_database": None if database_path is None else str(database_path),
    }


def build_model_c_artifact(
    *,
    dataset_id: str,
    measurements: pd.DataFrame,
    output_dir: Path = CHAIN_OUTPUT_DIR,
    database_path: Path | None = None,
) -> dict[str, Any]:
    ensure_experiment_dirs()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{dataset_id}_model_c_hash_chain.jsonl"
    events = build_model_c_events(
        measurements,
        dataset_id=dataset_id,
        created_at_utc=_baseline_created_at(measurements),
    )
    records = events_to_records(events)
    with output_file.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=True) + "\n")
    if database_path is not None:
        replace_audit_events(database_path, records, model_id=MODEL_C)
    terminal_hash = records[-1]["block_hash"] if records else None
    summary = {
        "model_id": MODEL_C,
        "dataset_id": dataset_id,
        "artifact_file": str(output_file),
        "event_count": len(records),
        "measurement_event_count": max(0, len(records) - 1),
        "terminal_block_hash": terminal_hash,
        "artifact_hash_sha256": sha256_file(output_file),
        "sqlite_database": None if database_path is None else str(database_path),
    }
    summary_file = output_dir / f"{dataset_id}_model_c_hash_chain_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    summary["summary_file"] = str(summary_file)
    return summary


def build_hash_chain_artifacts(
    *,
    dataset_id: str,
    measurements_file: Path,
    output_dir: Path = CHAIN_OUTPUT_DIR,
    database_path: Path | None = None,
) -> dict[str, Any]:
    measurements = load_measurements(measurements_file)
    return build_model_c_artifact(
        dataset_id=dataset_id,
        measurements=measurements,
        output_dir=output_dir,
        database_path=database_path,
    )


def build_baseline_artifacts(
    *,
    dataset_id: str,
    measurements_file: Path,
    output_dir: Path = AUDIT_OUTPUT_DIR,
    database_path: Path | None = None,
) -> dict[str, Any]:
    measurements = load_measurements(measurements_file)
    model_a = build_model_a_artifact(
        dataset_id=dataset_id,
        measurements=measurements,
        output_dir=output_dir,
    )
    model_b = build_model_b_artifact(
        dataset_id=dataset_id,
        measurements=measurements,
        output_dir=output_dir,
        database_path=database_path,
    )
    summary = {
        "dataset_id": dataset_id,
        "measurements_file": str(measurements_file),
        "model_a": model_a,
        "model_b": model_b,
    }
    summary_file = output_dir / f"{dataset_id}_baseline_models_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    summary["summary_file"] = str(summary_file)
    return summary


def _json_ready(record: dict[str, Any]) -> dict[str, Any]:
    ready: dict[str, Any] = {}
    for key, value in record.items():
        if pd.isna(value):
            ready[key] = None
        else:
            ready[key] = value
    return ready


def _baseline_created_at(measurements: pd.DataFrame) -> str:
    created_at = pd.to_datetime(measurements["created_at_utc"], utc=True).min()
    if pd.isna(created_at):
        raise ValueError("Cannot determine baseline creation timestamp from measurements")
    return created_at.isoformat().replace("+00:00", "Z")
