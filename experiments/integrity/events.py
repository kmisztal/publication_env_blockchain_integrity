"""Deterministic event construction for integrity model experiments."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Iterable

import pandas as pd

from experiments.common.hashing import sha256_json


MODEL_A = "A_conventional_storage"
MODEL_B = "B_audit_trail"
MODEL_C = "C_audit_hash_chain"
MODEL_D = "D_audit_hash_chain_provenance"

EVENT_GENESIS = "genesis"
EVENT_MEASUREMENT_RECORDED = "measurement_recorded"
EVENT_PERMISSION_GRANTED = "permission_granted"
EVENT_KEY_REVOKED = "key_revoked"
EVENT_CORRECTION_RECORDED = "correction_recorded"
EVENT_RECORD_INVALIDATED = "record_invalidated"

DEFAULT_INGEST_ACTOR_ID = "actor:openaq_ingest"


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    model_id: str
    event_type: str
    event_timestamp: str
    actor_id: str | None
    subject_id: str | None
    payload_json: dict[str, Any]
    payload_hash: str
    previous_hash: str | None
    block_hash: str | None
    signature_id: str | None
    source_record_id: str | None
    created_at_utc: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "model_id": self.model_id,
            "event_type": self.event_type,
            "event_timestamp": self.event_timestamp,
            "actor_id": self.actor_id,
            "subject_id": self.subject_id,
            "payload_json": self.payload_json,
            "payload_hash": self.payload_hash,
            "previous_hash": self.previous_hash,
            "block_hash": self.block_hash,
            "signature_id": self.signature_id,
            "source_record_id": self.source_record_id,
            "created_at_utc": self.created_at_utc,
        }

    def sqlite_row(self) -> dict[str, Any]:
        row = self.as_dict()
        row["payload_json"] = row["payload_json"]
        return row


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def normalize_iso_timestamp(value: Any) -> str:
    timestamp = pd.to_datetime(value, utc=True)
    if pd.isna(timestamp):
        raise ValueError(f"Cannot normalize timestamp: {value!r}")
    return timestamp.isoformat().replace("+00:00", "Z")


def measurement_payload(row: pd.Series | dict[str, Any]) -> dict[str, Any]:
    item = dict(row)
    raw_payload = item.get("raw_payload_json") or ""
    return {
        "record_id": str(item["record_id"]),
        "dataset_id": str(item["dataset_id"]),
        "source_name": str(item["source_name"]),
        "source_record_index": int(item["source_record_index"]),
        "station_id": str(item["station_id"]),
        "parameter": str(item["parameter"]),
        "timestamp_utc": normalize_iso_timestamp(item["timestamp_utc"]),
        "value": float(item["value"]),
        "unit": None if pd.isna(item.get("unit")) else str(item.get("unit")),
        "latitude": _optional_float(item.get("latitude")),
        "longitude": _optional_float(item.get("longitude")),
        "quality_flag": None if pd.isna(item.get("quality_flag")) else str(item.get("quality_flag")),
        "raw_payload_hash": sha256_json(raw_payload),
    }


def genesis_payload(dataset_id: str, record_count: int) -> dict[str, Any]:
    return {
        "dataset_id": dataset_id,
        "record_count": record_count,
        "purpose": "baseline_event_log_start",
    }


def make_event(
    *,
    model_id: str,
    event_type: str,
    event_timestamp: str,
    payload: dict[str, Any],
    actor_id: str | None = None,
    subject_id: str | None = None,
    source_record_id: str | None = None,
    previous_hash: str | None = None,
    signature_id: str | None = None,
    created_at_utc: str | None = None,
    include_block_hash: bool = False,
) -> AuditEvent:
    payload_hash = sha256_json(payload)
    block_input = {
        "model_id": model_id,
        "event_type": event_type,
        "event_timestamp": event_timestamp,
        "actor_id": actor_id,
        "subject_id": subject_id,
        "payload_hash": payload_hash,
        "previous_hash": previous_hash,
        "signature_id": signature_id,
        "source_record_id": source_record_id,
    }
    block_hash = sha256_json(block_input) if include_block_hash else None
    event_id = sha256_json({**block_input, "block_hash": block_hash})
    return AuditEvent(
        event_id=event_id,
        model_id=model_id,
        event_type=event_type,
        event_timestamp=event_timestamp,
        actor_id=actor_id,
        subject_id=subject_id,
        payload_json=payload,
        payload_hash=payload_hash,
        previous_hash=previous_hash,
        block_hash=block_hash,
        signature_id=signature_id,
        source_record_id=source_record_id,
        created_at_utc=created_at_utc or utc_now_iso(),
    )


def build_model_b_events(
    measurements: pd.DataFrame,
    *,
    dataset_id: str,
    actor_id: str = DEFAULT_INGEST_ACTOR_ID,
    created_at_utc: str | None = None,
) -> list[AuditEvent]:
    ordered = order_measurements(measurements)
    event_created_at = created_at_utc or utc_now_iso()
    events = [
        make_event(
            model_id=MODEL_B,
            event_type=EVENT_GENESIS,
            event_timestamp=event_created_at,
            actor_id=actor_id,
            subject_id=dataset_id,
            payload=genesis_payload(dataset_id, len(ordered)),
            created_at_utc=event_created_at,
        )
    ]
    for row in ordered.to_dict(orient="records"):
        payload = measurement_payload(row)
        events.append(
            make_event(
                model_id=MODEL_B,
                event_type=EVENT_MEASUREMENT_RECORDED,
                event_timestamp=payload["timestamp_utc"],
                actor_id=actor_id,
                subject_id=payload["station_id"],
                payload=payload,
                source_record_id=payload["record_id"],
                created_at_utc=event_created_at,
            )
        )
    return events


def build_model_c_events(
    measurements: pd.DataFrame,
    *,
    dataset_id: str,
    actor_id: str = DEFAULT_INGEST_ACTOR_ID,
    created_at_utc: str | None = None,
) -> list[AuditEvent]:
    ordered = order_measurements(measurements)
    event_created_at = created_at_utc or utc_now_iso()
    events: list[AuditEvent] = []
    previous_hash: str | None = None

    genesis = make_event(
        model_id=MODEL_C,
        event_type=EVENT_GENESIS,
        event_timestamp=event_created_at,
        actor_id=actor_id,
        subject_id=dataset_id,
        payload=genesis_payload(dataset_id, len(ordered)),
        previous_hash=previous_hash,
        created_at_utc=event_created_at,
        include_block_hash=True,
    )
    events.append(genesis)
    previous_hash = genesis.block_hash

    for row in ordered.to_dict(orient="records"):
        payload = measurement_payload(row)
        event = make_event(
            model_id=MODEL_C,
            event_type=EVENT_MEASUREMENT_RECORDED,
            event_timestamp=payload["timestamp_utc"],
            actor_id=actor_id,
            subject_id=payload["station_id"],
            payload=payload,
            source_record_id=payload["record_id"],
            previous_hash=previous_hash,
            created_at_utc=event_created_at,
            include_block_hash=True,
        )
        events.append(event)
        previous_hash = event.block_hash

    return events


def order_measurements(measurements: pd.DataFrame) -> pd.DataFrame:
    return measurements.sort_values(
        ["timestamp_utc", "station_id", "parameter", "record_id"],
        kind="mergesort",
    ).reset_index(drop=True)


def events_to_records(events: Iterable[AuditEvent]) -> list[dict[str, Any]]:
    return [event.as_dict() for event in events]


def _optional_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)
