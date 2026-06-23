"""Verification helpers for integrity model artifacts."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any, Iterable

from experiments.common.hashing import canonical_json, sha256_file, sha256_json
from experiments.common.paths import VERIFICATION_OUTPUT_DIR, ensure_experiment_dirs
from experiments.common.schema import CANONICAL_MEASUREMENT_COLUMNS
from experiments.integrity.events import (
    EVENT_CORRECTION_RECORDED,
    EVENT_KEY_REVOKED,
    EVENT_MEASUREMENT_RECORDED,
    EVENT_PERMISSION_GRANTED,
    EVENT_SYNCHRONIZATION_RECORDED,
    MODEL_A,
    MODEL_B,
    MODEL_C,
    MODEL_D,
    PERMISSION_CORRECT_MEASUREMENT,
    PERMISSION_INGEST_MEASUREMENT,
    reconstruct_active_keys,
)


ALERT_MISSING_FIELD = "missing_field"
ALERT_DUPLICATE_ID = "duplicate_id"
ALERT_PAYLOAD_HASH_MISMATCH = "payload_hash_mismatch"
ALERT_BLOCK_HASH_MISMATCH = "block_hash_mismatch"
ALERT_PREVIOUS_HASH_MISMATCH = "previous_hash_mismatch"
ALERT_EVENT_ID_MISMATCH = "event_id_mismatch"
ALERT_UNEXPECTED_BLOCK_HASH = "unexpected_block_hash"
ALERT_MISSING_BLOCK_HASH = "missing_block_hash"
ALERT_PERMISSION_STATE_MISMATCH = "permission_state_mismatch"
ALERT_INACTIVE_SIGNATURE_KEY = "inactive_signature_key"
ALERT_UNAUTHORIZED_EVENT_TYPE = "unauthorized_event_type"
ALERT_CORRECTION_TARGET_MISSING = "correction_target_missing"
ALERT_CORRECTION_REASON_MISSING = "correction_reason_missing"
ALERT_DELAYED_SYNCHRONIZATION = "delayed_synchronization"

EVENT_FIELDS = [
    "event_id",
    "model_id",
    "event_type",
    "event_timestamp",
    "actor_id",
    "subject_id",
    "payload_json",
    "payload_hash",
    "previous_hash",
    "block_hash",
    "signature_id",
    "source_record_id",
    "created_at_utc",
]


@dataclass(frozen=True)
class VerificationAlert:
    alert_code: str
    model_id: str
    line_number: int
    event_id: str | None
    details: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "alert_code": self.alert_code,
            "model_id": self.model_id,
            "line_number": self.line_number,
            "event_id": self.event_id,
            "details_json": json.dumps(self.details, sort_keys=True),
        }


def verify_model_artifact(
    *,
    model_id: str,
    artifact_file: Path,
    dataset_id: str,
    output_dir: Path = VERIFICATION_OUTPUT_DIR,
) -> dict[str, Any]:
    if model_id == MODEL_A:
        return verify_model_a(
            artifact_file=artifact_file,
            dataset_id=dataset_id,
            output_dir=output_dir,
        )
    if model_id in {MODEL_B, MODEL_C, MODEL_D}:
        return verify_event_model(
            model_id=model_id,
            artifact_file=artifact_file,
            dataset_id=dataset_id,
            output_dir=output_dir,
        )
    raise ValueError(f"Unsupported model_id: {model_id}")


def verify_model_a(*, artifact_file: Path, dataset_id: str, output_dir: Path) -> dict[str, Any]:
    started_at = _utc_now()
    alerts: list[VerificationAlert] = []
    seen_record_ids: set[str] = set()
    checked_records = 0
    for line_number, record in _iter_jsonl(artifact_file):
        checked_records += 1
        for field in CANONICAL_MEASUREMENT_COLUMNS:
            if field not in record:
                alerts.append(_alert(MODEL_A, line_number, None, ALERT_MISSING_FIELD, {"field": field}))
        record_id = record.get("record_id")
        if record_id in seen_record_ids:
            alerts.append(_alert(MODEL_A, line_number, record_id, ALERT_DUPLICATE_ID, {"id_type": "record_id"}))
        if record_id is not None:
            seen_record_ids.add(record_id)
    return _write_report(
        model_id=MODEL_A,
        dataset_id=dataset_id,
        artifact_file=artifact_file,
        output_dir=output_dir,
        started_at=started_at,
        checked_items=checked_records,
        alerts=alerts,
        extra={
            "artifact_hash_sha256": sha256_file(artifact_file),
            "unique_record_ids": len(seen_record_ids),
        },
    )


def verify_event_model(
    *,
    model_id: str,
    artifact_file: Path,
    dataset_id: str,
    output_dir: Path,
) -> dict[str, Any]:
    started_at = _utc_now()
    alerts: list[VerificationAlert] = []
    seen_event_ids: set[str] = set()
    previous_hash: str | None = None
    checked_events = 0
    records: list[dict[str, Any]] = []
    active_keys: dict[str, dict[str, Any]] = {}
    known_record_ids: set[str] = set()

    for line_number, event in _iter_jsonl(artifact_file):
        checked_events += 1
        records.append(event)
        alerts.extend(_validate_event_schema(model_id, line_number, event))
        event_id = event.get("event_id")
        if event_id in seen_event_ids:
            alerts.append(_alert(model_id, line_number, event_id, ALERT_DUPLICATE_ID, {"id_type": "event_id"}))
        if event_id is not None:
            seen_event_ids.add(event_id)

        payload_hash = sha256_json(event.get("payload_json"))
        if event.get("payload_hash") != payload_hash:
            alerts.append(
                _alert(
                    model_id,
                    line_number,
                    event_id,
                    ALERT_PAYLOAD_HASH_MISMATCH,
                    {"expected": payload_hash, "actual": event.get("payload_hash")},
                )
            )

        expected_block_hash = _expected_block_hash(event)
        expected_event_id = sha256_json(
            {
                **_block_input(event, payload_hash=event.get("payload_hash")),
                "block_hash": event.get("block_hash"),
            }
        )

        if model_id == MODEL_B:
            if event.get("block_hash") is not None:
                alerts.append(_alert(model_id, line_number, event_id, ALERT_UNEXPECTED_BLOCK_HASH, {}))
        else:
            if event.get("previous_hash") != previous_hash:
                alerts.append(
                    _alert(
                        model_id,
                        line_number,
                        event_id,
                        ALERT_PREVIOUS_HASH_MISMATCH,
                        {"expected": previous_hash, "actual": event.get("previous_hash")},
                    )
                )
            if event.get("block_hash") is None:
                alerts.append(_alert(model_id, line_number, event_id, ALERT_MISSING_BLOCK_HASH, {}))
            elif event.get("block_hash") != expected_block_hash:
                alerts.append(
                    _alert(
                        model_id,
                        line_number,
                        event_id,
                        ALERT_BLOCK_HASH_MISMATCH,
                        {"expected": expected_block_hash, "actual": event.get("block_hash")},
                    )
                )
            previous_hash = event.get("block_hash")

        if event.get("event_id") != expected_event_id:
            alerts.append(
                _alert(
                    model_id,
                    line_number,
                    event_id,
                    ALERT_EVENT_ID_MISMATCH,
                    {"expected": expected_event_id, "actual": event.get("event_id")},
                )
            )

        if model_id == MODEL_D:
            alerts.extend(_validate_model_d_event_state(line_number, event, active_keys, known_record_ids))

    if model_id == MODEL_D:
        reconstructed = reconstruct_active_keys(records)
        if reconstructed != active_keys:
            alerts.append(
                _alert(
                    model_id,
                    checked_events,
                    None,
                    ALERT_PERMISSION_STATE_MISMATCH,
                    {"reconstructed_keys": len(reconstructed), "streaming_keys": len(active_keys)},
                )
            )

    return _write_report(
        model_id=model_id,
        dataset_id=dataset_id,
        artifact_file=artifact_file,
        output_dir=output_dir,
        started_at=started_at,
        checked_items=checked_events,
        alerts=alerts,
        extra={
            "artifact_hash_sha256": sha256_file(artifact_file),
            "terminal_block_hash": previous_hash,
            "unique_event_ids": len(seen_event_ids),
            "active_key_count": len(active_keys) if model_id == MODEL_D else None,
        },
    )


def _validate_event_schema(model_id: str, line_number: int, event: dict[str, Any]) -> list[VerificationAlert]:
    alerts = []
    for field in EVENT_FIELDS:
        if field not in event:
            alerts.append(_alert(model_id, line_number, event.get("event_id"), ALERT_MISSING_FIELD, {"field": field}))
    return alerts


def _validate_model_d_event_state(
    line_number: int,
    event: dict[str, Any],
    active_keys: dict[str, dict[str, Any]],
    known_record_ids: set[str],
) -> list[VerificationAlert]:
    alerts: list[VerificationAlert] = []
    payload = event.get("payload_json") or {}
    event_type = event.get("event_type")
    if event_type == EVENT_PERMISSION_GRANTED:
        active_keys[payload["key_id"]] = {
            "actor_id": payload["actor_id"],
            "key_id": payload["key_id"],
            "permissions": list(payload["permissions"]),
            "valid_from": payload["valid_from"],
            "valid_to": payload.get("valid_to"),
            "status": "active",
            "created_event_id": event["event_id"],
            "revoked_event_id": None,
        }
    elif event_type == EVENT_KEY_REVOKED:
        key_id = payload["key_id"]
        if key_id in active_keys:
            del active_keys[key_id]
    elif event_type == EVENT_MEASUREMENT_RECORDED:
        alerts.extend(
            _validate_signature_permission(
                line_number,
                event,
                active_keys,
                required_permission=PERMISSION_INGEST_MEASUREMENT,
            )
        )
        record_id = payload.get("record_id") or event.get("source_record_id")
        if record_id:
            known_record_ids.add(record_id)
    elif event_type == EVENT_CORRECTION_RECORDED:
        alerts.extend(
            _validate_signature_permission(
                line_number,
                event,
                active_keys,
                required_permission=PERMISSION_CORRECT_MEASUREMENT,
            )
        )
        target_record_id = payload.get("target_record_id")
        if target_record_id not in known_record_ids:
            alerts.append(
                _alert(
                    MODEL_D,
                    line_number,
                    event.get("event_id"),
                    ALERT_CORRECTION_TARGET_MISSING,
                    {"target_record_id": target_record_id},
                )
            )
        if not str(payload.get("reason") or "").strip():
            alerts.append(
                _alert(
                    MODEL_D,
                    line_number,
                    event.get("event_id"),
                    ALERT_CORRECTION_REASON_MISSING,
                    {"target_record_id": target_record_id},
                )
            )
    elif event_type == EVENT_SYNCHRONIZATION_RECORDED:
        alerts.extend(_validate_synchronization_delay(line_number, event))
    return alerts


def _validate_synchronization_delay(line_number: int, event: dict[str, Any]) -> list[VerificationAlert]:
    payload = event.get("payload_json") or {}
    local_timestamp = payload.get("local_event_timestamp")
    synchronized_at = payload.get("synchronized_at")
    max_delay_hours = float(payload.get("max_delay_hours", 0))
    if not local_timestamp or not synchronized_at:
        return []
    observed_delay_hours = (
        pd_datetime_utc(synchronized_at) - pd_datetime_utc(local_timestamp)
    ).total_seconds() / 3600
    if observed_delay_hours > max_delay_hours:
        return [
            _alert(
                MODEL_D,
                line_number,
                event.get("event_id"),
                ALERT_DELAYED_SYNCHRONIZATION,
                {
                    "gateway_id": payload.get("gateway_id"),
                    "covered_event_id": payload.get("covered_event_id"),
                    "observed_delay_hours": round(observed_delay_hours, 6),
                    "max_delay_hours": max_delay_hours,
                },
            )
        ]
    return []


def _validate_signature_permission(
    line_number: int,
    event: dict[str, Any],
    active_keys: dict[str, dict[str, Any]],
    *,
    required_permission: str,
) -> list[VerificationAlert]:
    signature_id = event.get("signature_id")
    key_state = active_keys.get(signature_id)
    if key_state is None:
        return [
            _alert(
                MODEL_D,
                line_number,
                event.get("event_id"),
                ALERT_INACTIVE_SIGNATURE_KEY,
                {"signature_id": signature_id, "required_permission": required_permission},
            )
        ]
    if required_permission not in set(key_state.get("permissions", [])):
        return [
            _alert(
                MODEL_D,
                line_number,
                event.get("event_id"),
                ALERT_UNAUTHORIZED_EVENT_TYPE,
                {"signature_id": signature_id, "required_permission": required_permission},
            )
        ]
    return []


def _expected_block_hash(event: dict[str, Any]) -> str:
    return sha256_json(_block_input(event, payload_hash=event.get("payload_hash")))


def _block_input(event: dict[str, Any], *, payload_hash: str | None) -> dict[str, Any]:
    return {
        "model_id": event.get("model_id"),
        "event_type": event.get("event_type"),
        "event_timestamp": event.get("event_timestamp"),
        "actor_id": event.get("actor_id"),
        "subject_id": event.get("subject_id"),
        "payload_hash": payload_hash,
        "previous_hash": event.get("previous_hash"),
        "signature_id": event.get("signature_id"),
        "source_record_id": event.get("source_record_id"),
    }


def _iter_jsonl(path: Path) -> Iterable[tuple[int, dict[str, Any]]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                yield line_number, json.loads(line)


def _write_report(
    *,
    model_id: str,
    dataset_id: str,
    artifact_file: Path,
    output_dir: Path,
    started_at: str,
    checked_items: int,
    alerts: list[VerificationAlert],
    extra: dict[str, Any],
) -> dict[str, Any]:
    ensure_experiment_dirs()
    output_dir.mkdir(parents=True, exist_ok=True)
    finished_at = _utc_now()
    status = "pass" if not alerts else "fail"
    report = {
        "dataset_id": dataset_id,
        "model_id": model_id,
        "artifact_file": str(artifact_file),
        "verification_started_at": started_at,
        "verification_finished_at": finished_at,
        "status": status,
        "checked_items": checked_items,
        "alerts_count": len(alerts),
        **{key: value for key, value in extra.items() if value is not None},
    }
    report_file = output_dir / f"{dataset_id}_{model_id}_verification_report.json"
    alerts_file = output_dir / f"{dataset_id}_{model_id}_alerts.csv"
    report["report_file"] = str(report_file)
    report["alerts_file"] = str(alerts_file)
    report_file.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    _write_alerts_csv(alerts_file, alerts)
    return report


def _write_alerts_csv(path: Path, alerts: list[VerificationAlert]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["alert_code", "model_id", "line_number", "event_id", "details_json"],
        )
        writer.writeheader()
        for alert in alerts:
            writer.writerow(alert.as_dict())


def _alert(
    model_id: str,
    line_number: int,
    event_id: str | None,
    alert_code: str,
    details: dict[str, Any],
) -> VerificationAlert:
    return VerificationAlert(
        alert_code=alert_code,
        model_id=model_id,
        line_number=line_number,
        event_id=event_id,
        details=details,
    )


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def pd_datetime_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
