"""Controlled tampering scenario generator for integrity model artifacts."""

from __future__ import annotations

from datetime import timedelta
import json
from pathlib import Path
from typing import Any

import pandas as pd

from experiments.common.hashing import canonical_json, sha256_file, sha256_json
from experiments.common.paths import TAMPERED_DATA_DIR, ensure_experiment_dirs
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


THREAT_VALUE_MODIFICATION = "value_modification"
THREAT_TIMESTAMP_MODIFICATION = "timestamp_modification"
THREAT_RECORD_DELETION = "record_deletion"
THREAT_FAKE_RECORD_INSERTION = "fake_record_insertion"
THREAT_REPLAY = "replay"
THREAT_BROKEN_PROVENANCE = "broken_provenance"
THREAT_UNAUTHORIZED_CORRECTION = "unauthorized_correction"
THREAT_REVOKED_ACTOR_KEY_USAGE = "revoked_actor_key_usage"
THREAT_MISSING_CORRECTION_REASON = "missing_correction_reason"
THREAT_DELAYED_SYNCHRONIZATION = "delayed_synchronization"

SUPPORTED_THREATS = [
    THREAT_VALUE_MODIFICATION,
    THREAT_TIMESTAMP_MODIFICATION,
    THREAT_RECORD_DELETION,
    THREAT_FAKE_RECORD_INSERTION,
    THREAT_REPLAY,
    THREAT_BROKEN_PROVENANCE,
    THREAT_UNAUTHORIZED_CORRECTION,
    THREAT_REVOKED_ACTOR_KEY_USAGE,
    THREAT_MISSING_CORRECTION_REASON,
    THREAT_DELAYED_SYNCHRONIZATION,
]


def generate_tampered_artifact(
    *,
    dataset_id: str,
    model_id: str,
    threat_type: str,
    artifact_file: Path,
    output_dir: Path = TAMPERED_DATA_DIR,
) -> dict[str, Any]:
    if threat_type not in SUPPORTED_THREATS:
        raise ValueError(f"Unsupported threat_type: {threat_type}")
    if threat_type == THREAT_BROKEN_PROVENANCE and model_id != MODEL_D:
        raise ValueError("broken_provenance currently applies only to Model D artifacts")
    if threat_type in {
        THREAT_UNAUTHORIZED_CORRECTION,
        THREAT_REVOKED_ACTOR_KEY_USAGE,
        THREAT_MISSING_CORRECTION_REASON,
        THREAT_DELAYED_SYNCHRONIZATION,
    } and model_id != MODEL_D:
        raise ValueError(f"{threat_type} currently applies only to Model D artifacts")

    ensure_experiment_dirs()
    output_dir.mkdir(parents=True, exist_ok=True)
    records = _read_jsonl(artifact_file)
    target_index = _find_target_index(records, model_id)
    labels: list[dict[str, Any]] = []

    if threat_type == THREAT_VALUE_MODIFICATION:
        _tamper_value(records[target_index], model_id)
        labels.append(_label(dataset_id, model_id, threat_type, records[target_index], target_index))
    elif threat_type == THREAT_TIMESTAMP_MODIFICATION:
        _tamper_timestamp(records[target_index], model_id)
        labels.append(_label(dataset_id, model_id, threat_type, records[target_index], target_index))
    elif threat_type == THREAT_RECORD_DELETION:
        removed = records.pop(target_index)
        labels.append(_label(dataset_id, model_id, threat_type, removed, target_index))
    elif threat_type == THREAT_FAKE_RECORD_INSERTION:
        inserted = _fake_record(records[target_index], model_id)
        records.insert(target_index + 1, inserted)
        labels.append(_label(dataset_id, model_id, threat_type, inserted, target_index + 1))
    elif threat_type == THREAT_REPLAY:
        replayed = json.loads(json.dumps(records[target_index]))
        records.insert(target_index + 1, replayed)
        labels.append(_label(dataset_id, model_id, threat_type, replayed, target_index + 1))
    elif threat_type == THREAT_BROKEN_PROVENANCE:
        records[target_index]["signature_id"] = "key:unauthorized:tampered"
        labels.append(_label(dataset_id, model_id, threat_type, records[target_index], target_index))
    elif threat_type == THREAT_UNAUTHORIZED_CORRECTION:
        inserted = _unauthorized_correction_events(records[target_index])
        insert_at = target_index + 1
        records[insert_at:insert_at] = inserted
        labels.append(_label(dataset_id, model_id, threat_type, records[insert_at + 1], insert_at + 1))
    elif threat_type == THREAT_REVOKED_ACTOR_KEY_USAGE:
        revoked_target_index = _find_last_target_index(records, model_id)
        inserted = _revocation_event_before(records[revoked_target_index - 1], records[revoked_target_index])
        records.insert(revoked_target_index, inserted)
        labels.append(_label(dataset_id, model_id, threat_type, records[revoked_target_index + 1], revoked_target_index + 1))
    elif threat_type == THREAT_MISSING_CORRECTION_REASON:
        inserted = _correction_event_after(records[target_index], reason="")
        insert_at = target_index + 1
        records.insert(insert_at, inserted)
        labels.append(_label(dataset_id, model_id, threat_type, inserted, insert_at))
    elif threat_type == THREAT_DELAYED_SYNCHRONIZATION:
        delayed_target_index = _find_last_target_index(records, model_id)
        inserted = _delayed_synchronization_event_after(records[delayed_target_index])
        insert_at = delayed_target_index + 1
        records.insert(insert_at, inserted)
        labels.append(_label(dataset_id, model_id, threat_type, inserted, insert_at))

    scenario_id = f"{dataset_id}_{model_id}_{threat_type}"
    tampered_file = output_dir / f"{scenario_id}.jsonl"
    labels_file = output_dir / f"{scenario_id}_labels.json"
    _write_jsonl(tampered_file, records)
    label_doc = {
        "scenario_id": scenario_id,
        "dataset_id": dataset_id,
        "model_id": model_id,
        "threat_type": threat_type,
        "source_artifact_file": str(artifact_file),
        "tampered_artifact_file": str(tampered_file),
        "tampered_artifact_hash_sha256": sha256_file(tampered_file),
        "labels": labels,
    }
    labels_file.write_text(json.dumps(label_doc, indent=2, sort_keys=True), encoding="utf-8")
    return {
        "scenario_id": scenario_id,
        "dataset_id": dataset_id,
        "model_id": model_id,
        "threat_type": threat_type,
        "tampered_artifact_file": str(tampered_file),
        "labels_file": str(labels_file),
        "tampered_artifact_hash_sha256": label_doc["tampered_artifact_hash_sha256"],
        "label_count": len(labels),
        "record_count": len(records),
    }


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    if not records:
        raise ValueError(f"Artifact file is empty: {path}")
    return records


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(canonical_json(record) + "\n")


def _find_target_index(records: list[dict[str, Any]], model_id: str) -> int:
    if model_id == MODEL_A:
        return 0
    for index, record in enumerate(records):
        if record.get("event_type") == EVENT_MEASUREMENT_RECORDED:
            return index
    raise ValueError(f"No measurement event found for model_id={model_id}")


def _find_last_target_index(records: list[dict[str, Any]], model_id: str) -> int:
    if model_id == MODEL_A:
        return len(records) - 1
    for index in range(len(records) - 1, -1, -1):
        if records[index].get("event_type") == EVENT_MEASUREMENT_RECORDED:
            return index
    raise ValueError(f"No measurement event found for model_id={model_id}")


def _tamper_value(record: dict[str, Any], model_id: str) -> None:
    if model_id == MODEL_A:
        record["value"] = float(record["value"]) + 1.0
    else:
        record["payload_json"]["value"] = float(record["payload_json"]["value"]) + 1.0


def _tamper_timestamp(record: dict[str, Any], model_id: str) -> None:
    if model_id == MODEL_A:
        record["timestamp_utc"] = _plus_one_minute(record["timestamp_utc"])
    else:
        record["payload_json"]["timestamp_utc"] = _plus_one_minute(record["payload_json"]["timestamp_utc"])
        record["event_timestamp"] = _plus_one_minute(record["event_timestamp"])


def _fake_record(record: dict[str, Any], model_id: str) -> dict[str, Any]:
    fake = json.loads(json.dumps(record))
    suffix = sha256_json(record)[:12]
    if model_id == MODEL_A:
        fake["record_id"] = f"fake:{suffix}"
        fake["source_record_index"] = int(fake["source_record_index"]) + 10_000_000
    else:
        fake["event_id"] = f"fake:{suffix}"
        fake["source_record_id"] = f"fake:{suffix}"
        fake["payload_json"]["record_id"] = f"fake:{suffix}"
        fake["payload_json"]["source_record_index"] = int(fake["payload_json"]["source_record_index"]) + 10_000_000
    return fake


def _unauthorized_correction_events(target_event: dict[str, Any]) -> list[dict[str, Any]]:
    actor_id = "actor:unauthorized_corrector"
    key_id = "key:unauthorized_corrector:ingest_only"
    permission = make_event(
        model_id=MODEL_D,
        event_type=EVENT_PERMISSION_GRANTED,
        event_timestamp=target_event["event_timestamp"],
        actor_id=actor_id,
        subject_id=actor_id,
        payload=permission_payload(
            actor_id=actor_id,
            key_id=key_id,
            permissions=[PERMISSION_INGEST_MEASUREMENT],
            valid_from=target_event["event_timestamp"],
        ),
        previous_hash=target_event["block_hash"],
        signature_id=key_id,
        created_at_utc=target_event["created_at_utc"],
        include_block_hash=True,
    ).as_dict()
    correction = _correction_event_after(
        permission,
        target_payload=target_event["payload_json"],
        actor_id=actor_id,
        key_id=key_id,
        reason="Unauthorized correction attempt",
    )
    return [permission, correction]


def _correction_event_after(
    previous_event: dict[str, Any],
    *,
    target_payload: dict[str, Any] | None = None,
    actor_id: str = DEFAULT_INGEST_ACTOR_ID,
    key_id: str = DEFAULT_INGEST_KEY_ID,
    reason: str | None,
) -> dict[str, Any]:
    payload = target_payload or previous_event["payload_json"]
    previous_value = payload.get("value")
    corrected_value = float(previous_value) + 0.25
    corrected_payload = correction_payload(
        target_record_id=payload["record_id"],
        corrected_fields=["value"],
        previous_value_hash=sha256_json(previous_value),
        corrected_value_hash=sha256_json(corrected_value),
        reason=reason,
    )
    return make_event(
        model_id=MODEL_D,
        event_type=EVENT_CORRECTION_RECORDED,
        event_timestamp=previous_event["event_timestamp"],
        actor_id=actor_id,
        subject_id=payload["station_id"],
        payload=corrected_payload,
        source_record_id=payload["record_id"],
        previous_hash=previous_event["block_hash"],
        signature_id=key_id,
        created_at_utc=previous_event["created_at_utc"],
        include_block_hash=True,
    ).as_dict()


def _revocation_event_before(previous_event: dict[str, Any], target_event: dict[str, Any]) -> dict[str, Any]:
    return make_event(
        model_id=MODEL_D,
        event_type=EVENT_KEY_REVOKED,
        event_timestamp=target_event["event_timestamp"],
        actor_id=DEFAULT_INGEST_ACTOR_ID,
        subject_id=DEFAULT_INGEST_ACTOR_ID,
        payload=key_revocation_payload(
            actor_id=DEFAULT_INGEST_ACTOR_ID,
            key_id=DEFAULT_INGEST_KEY_ID,
            revoked_at=target_event["event_timestamp"],
            reason="Controlled revoked-key tampering scenario",
        ),
        previous_hash=previous_event["block_hash"],
        signature_id=DEFAULT_INGEST_KEY_ID,
        created_at_utc=target_event["created_at_utc"],
        include_block_hash=True,
    ).as_dict()


def _delayed_synchronization_event_after(previous_event: dict[str, Any]) -> dict[str, Any]:
    payload = previous_event["payload_json"]
    local_event_timestamp = previous_event["event_timestamp"]
    synchronized_at = _plus_hours(local_event_timestamp, 72)
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


def _plus_one_minute(value: str) -> str:
    timestamp = pd.to_datetime(value, utc=True) + timedelta(minutes=1)
    return timestamp.isoformat().replace("+00:00", "Z")


def _plus_hours(value: str, hours: int) -> str:
    timestamp = pd.to_datetime(value, utc=True) + timedelta(hours=hours)
    return timestamp.isoformat().replace("+00:00", "Z")


def _label(
    dataset_id: str,
    model_id: str,
    threat_type: str,
    record: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    return {
        "label_id": sha256_json({"dataset_id": dataset_id, "model_id": model_id, "threat_type": threat_type, "index": index}),
        "dataset_id": dataset_id,
        "model_id": model_id,
        "threat_type": threat_type,
        "target_index": index,
        "target_record_id": _target_record_id(record, model_id),
        "target_event_id": None if model_id == MODEL_A else record.get("event_id"),
        "expected_alert_codes": _expected_alert_codes(model_id, threat_type),
    }


def _target_record_id(record: dict[str, Any], model_id: str) -> str | None:
    if model_id == MODEL_A:
        return record.get("record_id")
    payload = record.get("payload_json") or {}
    return payload.get("record_id") or record.get("source_record_id")


def _expected_alert_codes(model_id: str, threat_type: str) -> list[str]:
    if model_id == MODEL_A:
        if threat_type == THREAT_REPLAY:
            return ["duplicate_id"]
        return []
    if threat_type == THREAT_VALUE_MODIFICATION:
        return ["payload_hash_mismatch"]
    if threat_type == THREAT_TIMESTAMP_MODIFICATION:
        codes = ["payload_hash_mismatch", "event_id_mismatch"]
        if model_id in {MODEL_C, MODEL_D}:
            codes.append("block_hash_mismatch")
        return codes
    if threat_type == THREAT_RECORD_DELETION:
        return ["previous_hash_mismatch"] if model_id in {MODEL_C, MODEL_D} else []
    if threat_type == THREAT_FAKE_RECORD_INSERTION:
        codes = ["payload_hash_mismatch", "event_id_mismatch"]
        if model_id in {MODEL_C, MODEL_D}:
            codes.append("previous_hash_mismatch")
        return codes
    if threat_type == THREAT_REPLAY:
        codes = ["duplicate_id"]
        if model_id in {MODEL_C, MODEL_D}:
            codes.append("previous_hash_mismatch")
        return codes
    if threat_type == THREAT_BROKEN_PROVENANCE:
        return ["inactive_signature_key"]
    if threat_type == THREAT_UNAUTHORIZED_CORRECTION:
        return ["unauthorized_event_type"]
    if threat_type == THREAT_REVOKED_ACTOR_KEY_USAGE:
        return ["inactive_signature_key"]
    if threat_type == THREAT_MISSING_CORRECTION_REASON:
        return ["correction_reason_missing"]
    if threat_type == THREAT_DELAYED_SYNCHRONIZATION:
        return ["delayed_synchronization"]
    return []
