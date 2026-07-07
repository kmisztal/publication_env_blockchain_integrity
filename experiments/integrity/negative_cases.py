"""Generate and evaluate non-tampering negative cases."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import pandas as pd

from experiments.common.hashing import canonical_json, sha256_file, sha256_json
from experiments.common.paths import (
    AUDIT_OUTPUT_DIR,
    CHAIN_OUTPUT_DIR,
    METRICS_OUTPUT_DIR,
    NEGATIVE_DATA_DIR,
    VERIFICATION_OUTPUT_DIR,
    ensure_experiment_dirs,
)
from experiments.integrity.events import (
    DEFAULT_INGEST_ACTOR_ID,
    DEFAULT_INGEST_KEY_ID,
    EVENT_CORRECTION_RECORDED,
    EVENT_KEY_REVOKED,
    EVENT_MEASUREMENT_RECORDED,
    EVENT_PERMISSION_GRANTED,
    EVENT_SYNCHRONIZATION_RECORDED,
    MODEL_A,
    MODEL_B,
    MODEL_C,
    MODEL_D,
    PERMISSION_INGEST_MEASUREMENT,
    correction_payload,
    key_revocation_payload,
    make_event,
    permission_payload,
    synchronization_payload,
)
from experiments.integrity.verification import verify_model_artifact


NEGATIVE_BASELINE_CLEAN = "clean_baseline"
NEGATIVE_VALID_CORRECTION = "valid_correction"
NEGATIVE_VALID_SYNCHRONIZATION = "valid_synchronization"
NEGATIVE_VALID_GRANT_REVOCATION = "valid_permission_grant_revocation"


def run_negative_cases(
    *,
    dataset_id: str,
    output_dir: Path = NEGATIVE_DATA_DIR,
    metrics_output_dir: Path = METRICS_OUTPUT_DIR / "negative",
    verification_output_dir: Path = VERIFICATION_OUTPUT_DIR / "negative",
) -> dict[str, Any]:
    """Create and verify negative cases, then export true-negative/FPR metrics."""

    ensure_experiment_dirs()
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics_output_dir.mkdir(parents=True, exist_ok=True)
    verification_output_dir.mkdir(parents=True, exist_ok=True)

    cases = _baseline_cases(dataset_id)
    cases.extend(_valid_model_d_cases(dataset_id, output_dir))

    rows = []
    for case in cases:
        case_verification_dir = verification_output_dir / _case_output_name(case)
        report = verify_model_artifact(
            dataset_id=dataset_id,
            model_id=case["model_id"],
            artifact_file=Path(case["artifact_file"]),
            output_dir=case_verification_dir,
        )
        alerts_count = int(report["alerts_count"])
        status = "true_negative" if alerts_count == 0 else "false_positive"
        rows.append(
            {
                "dataset_id": dataset_id,
                "case_id": case["case_id"],
                "case_type": case["case_type"],
                "model_id": case["model_id"],
                "artifact_file": case["artifact_file"],
                "artifact_hash_sha256": sha256_file(Path(case["artifact_file"])),
                "verification_report": report["report_file"],
                "alerts_file": report["alerts_file"],
                "alerts_count": alerts_count,
                "status": status,
            }
        )

    metrics_file = metrics_output_dir / f"{dataset_id}_negative_case_metrics.csv"
    summary_file = metrics_output_dir / f"{dataset_id}_negative_case_summary.json"
    _write_csv(metrics_file, rows)
    summary = {
        "dataset_id": dataset_id,
        "case_count": len(rows),
        "true_negative_count": sum(1 for row in rows if row["status"] == "true_negative"),
        "false_positive_count": sum(1 for row in rows if row["status"] == "false_positive"),
        "false_positive_rate": _rate(
            sum(1 for row in rows if row["status"] == "false_positive"),
            len(rows),
        ),
        "metrics_file": str(metrics_file),
        "cases": rows,
    }
    summary_file.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return {**summary, "summary_file": str(summary_file)}


def _baseline_cases(dataset_id: str) -> list[dict[str, Any]]:
    return [
        {
            "case_id": f"{dataset_id}_{MODEL_A}_{NEGATIVE_BASELINE_CLEAN}",
            "case_type": NEGATIVE_BASELINE_CLEAN,
            "model_id": MODEL_A,
            "artifact_file": str(AUDIT_OUTPUT_DIR / f"{dataset_id}_model_a_measurements.jsonl"),
        },
        {
            "case_id": f"{dataset_id}_{MODEL_B}_{NEGATIVE_BASELINE_CLEAN}",
            "case_type": NEGATIVE_BASELINE_CLEAN,
            "model_id": MODEL_B,
            "artifact_file": str(AUDIT_OUTPUT_DIR / f"{dataset_id}_model_b_audit_events.jsonl"),
        },
        {
            "case_id": f"{dataset_id}_{MODEL_C}_{NEGATIVE_BASELINE_CLEAN}",
            "case_type": NEGATIVE_BASELINE_CLEAN,
            "model_id": MODEL_C,
            "artifact_file": str(CHAIN_OUTPUT_DIR / f"{dataset_id}_model_c_hash_chain.jsonl"),
        },
        {
            "case_id": f"{dataset_id}_{MODEL_D}_{NEGATIVE_BASELINE_CLEAN}",
            "case_type": NEGATIVE_BASELINE_CLEAN,
            "model_id": MODEL_D,
            "artifact_file": str(CHAIN_OUTPUT_DIR / f"{dataset_id}_model_d_provenance_chain.jsonl"),
        },
    ]


def _case_output_name(case: dict[str, Any]) -> str:
    model_short = case["model_id"].split("_", 1)[0].lower()
    return f"{model_short}_{case['case_type']}"


def _valid_model_d_cases(dataset_id: str, output_dir: Path) -> list[dict[str, Any]]:
    source_file = CHAIN_OUTPUT_DIR / f"{dataset_id}_model_d_provenance_chain.jsonl"
    records = _read_jsonl(source_file)
    first_measurement = _first_measurement(records)
    last_event = records[-1]
    return [
        _write_valid_case(
            dataset_id=dataset_id,
            source_records=records,
            output_dir=output_dir,
            case_type=NEGATIVE_VALID_CORRECTION,
            appended_events=[
                _valid_correction_after(last_event, target_event=first_measurement),
            ],
        ),
        _write_valid_case(
            dataset_id=dataset_id,
            source_records=records,
            output_dir=output_dir,
            case_type=NEGATIVE_VALID_SYNCHRONIZATION,
            appended_events=[
                _valid_synchronization_after(last_event),
            ],
        ),
        _write_valid_case(
            dataset_id=dataset_id,
            source_records=records,
            output_dir=output_dir,
            case_type=NEGATIVE_VALID_GRANT_REVOCATION,
            appended_events=_valid_grant_revocation_after(last_event),
        ),
    ]


def _write_valid_case(
    *,
    dataset_id: str,
    source_records: list[dict[str, Any]],
    output_dir: Path,
    case_type: str,
    appended_events: list[dict[str, Any]],
) -> dict[str, Any]:
    case_id = f"{dataset_id}_{MODEL_D}_{case_type}"
    case_file = output_dir / f"{case_id}.jsonl"
    records = list(source_records) + appended_events
    _write_jsonl(case_file, records)
    label_file = output_dir / f"{case_id}_labels.json"
    label_doc = {
        "case_id": case_id,
        "case_type": case_type,
        "dataset_id": dataset_id,
        "model_id": MODEL_D,
        "artifact_file": str(case_file),
        "artifact_hash_sha256": sha256_file(case_file),
        "expected_alert_codes": [],
        "expected_status": "true_negative",
        "appended_event_ids": [event["event_id"] for event in appended_events],
    }
    label_file.write_text(json.dumps(label_doc, indent=2, sort_keys=True), encoding="utf-8")
    return {
        "case_id": case_id,
        "case_type": case_type,
        "model_id": MODEL_D,
        "artifact_file": str(case_file),
        "labels_file": str(label_file),
    }


def _valid_correction_after(previous_event: dict[str, Any], *, target_event: dict[str, Any]) -> dict[str, Any]:
    target_payload = target_event["payload_json"]
    previous_value = target_payload["value"]
    corrected_value = float(previous_value) + 0.1
    payload = correction_payload(
        target_record_id=target_payload["record_id"],
        corrected_fields=["value"],
        previous_value_hash=sha256_json(previous_value),
        corrected_value_hash=sha256_json(corrected_value),
        reason="Valid correction negative case",
    )
    return make_event(
        model_id=MODEL_D,
        event_type=EVENT_CORRECTION_RECORDED,
        event_timestamp=previous_event["event_timestamp"],
        actor_id=DEFAULT_INGEST_ACTOR_ID,
        subject_id=target_payload["station_id"],
        payload=payload,
        source_record_id=target_payload["record_id"],
        previous_hash=previous_event["block_hash"],
        signature_id=DEFAULT_INGEST_KEY_ID,
        created_at_utc=previous_event["created_at_utc"],
        include_block_hash=True,
    ).as_dict()


def _valid_synchronization_after(previous_event: dict[str, Any]) -> dict[str, Any]:
    payload = previous_event["payload_json"]
    local_event_timestamp = previous_event["event_timestamp"]
    synchronized_at = _plus_hours(local_event_timestamp, 1)
    sync_payload = synchronization_payload(
        gateway_id=f"gateway:{payload['station_id']}",
        covered_event_id=previous_event["event_id"],
        local_event_timestamp=local_event_timestamp,
        synchronized_at=synchronized_at,
        max_delay_hours=24,
    )
    return make_event(
        model_id=MODEL_D,
        event_type=EVENT_SYNCHRONIZATION_RECORDED,
        event_timestamp=synchronized_at,
        actor_id=DEFAULT_INGEST_ACTOR_ID,
        subject_id=sync_payload["gateway_id"],
        payload=sync_payload,
        source_record_id=payload["record_id"],
        previous_hash=previous_event["block_hash"],
        signature_id=DEFAULT_INGEST_KEY_ID,
        created_at_utc=previous_event["created_at_utc"],
        include_block_hash=True,
    ).as_dict()


def _valid_grant_revocation_after(previous_event: dict[str, Any]) -> list[dict[str, Any]]:
    actor_id = "actor:negative_case_operator"
    key_id = "key:negative_case_operator:temporary"
    grant = make_event(
        model_id=MODEL_D,
        event_type=EVENT_PERMISSION_GRANTED,
        event_timestamp=previous_event["event_timestamp"],
        actor_id=actor_id,
        subject_id=actor_id,
        payload=permission_payload(
            actor_id=actor_id,
            key_id=key_id,
            permissions=[PERMISSION_INGEST_MEASUREMENT],
            valid_from=previous_event["event_timestamp"],
        ),
        previous_hash=previous_event["block_hash"],
        signature_id=DEFAULT_INGEST_KEY_ID,
        created_at_utc=previous_event["created_at_utc"],
        include_block_hash=True,
    ).as_dict()
    revocation = make_event(
        model_id=MODEL_D,
        event_type=EVENT_KEY_REVOKED,
        event_timestamp=previous_event["event_timestamp"],
        actor_id=DEFAULT_INGEST_ACTOR_ID,
        subject_id=actor_id,
        payload=key_revocation_payload(
            actor_id=actor_id,
            key_id=key_id,
            revoked_at=previous_event["event_timestamp"],
            reason="Valid temporary key revocation negative case",
        ),
        previous_hash=grant["block_hash"],
        signature_id=DEFAULT_INGEST_KEY_ID,
        created_at_utc=previous_event["created_at_utc"],
        include_block_hash=True,
    ).as_dict()
    return [grant, revocation]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(canonical_json(record) + "\n")


def _first_measurement(records: list[dict[str, Any]]) -> dict[str, Any]:
    for record in records:
        if record.get("event_type") == EVENT_MEASUREMENT_RECORDED:
            return record
    raise ValueError("No measurement event found in Model D artifact")


def _plus_hours(value: str, hours: int) -> str:
    timestamp = pd.to_datetime(value, utc=True) + pd.Timedelta(hours=hours)
    return timestamp.isoformat().replace("+00:00", "Z")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _rate(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return ""
    return f"{numerator / denominator:.6f}"
