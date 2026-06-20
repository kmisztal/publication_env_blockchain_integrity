"""SQLite storage helpers for PoC experiment artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any

import pandas as pd

from experiments.common.schema import CANONICAL_MEASUREMENT_COLUMNS, missing_columns


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS dataset_manifest (
    dataset_id TEXT PRIMARY KEY,
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    query_parameters_json TEXT NOT NULL,
    downloaded_at_utc TEXT NOT NULL,
    raw_file_path TEXT NOT NULL,
    processed_file_path TEXT NOT NULL,
    raw_file_hash_sha256 TEXT NOT NULL,
    processed_file_hash_sha256 TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS measurements (
    record_id TEXT PRIMARY KEY,
    dataset_id TEXT NOT NULL,
    source_name TEXT NOT NULL,
    source_record_index INTEGER NOT NULL,
    station_id TEXT NOT NULL,
    parameter TEXT NOT NULL,
    timestamp_utc TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT,
    latitude REAL,
    longitude REAL,
    quality_flag TEXT,
    raw_payload_json TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_measurements_dataset ON measurements(dataset_id);
CREATE INDEX IF NOT EXISTS idx_measurements_station_time ON measurements(station_id, timestamp_utc);

CREATE TABLE IF NOT EXISTS audit_events (
    event_id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_timestamp TEXT NOT NULL,
    actor_id TEXT,
    subject_id TEXT,
    payload_json TEXT NOT NULL,
    payload_hash TEXT,
    previous_hash TEXT,
    block_hash TEXT,
    signature_id TEXT,
    source_record_id TEXT,
    created_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS actors (
    actor_id TEXT PRIMARY KEY,
    actor_type TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS actor_keys (
    key_id TEXT PRIMARY KEY,
    actor_id TEXT NOT NULL,
    status TEXT NOT NULL,
    valid_from TEXT NOT NULL,
    valid_to TEXT,
    created_event_id TEXT,
    revoked_event_id TEXT
);

CREATE TABLE IF NOT EXISTS tampering_labels (
    label_id TEXT PRIMARY KEY,
    scenario_id TEXT NOT NULL,
    threat_type TEXT NOT NULL,
    target_record_id TEXT,
    target_event_id TEXT,
    expected_detection TEXT,
    details_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS verification_reports (
    report_id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    scenario_id TEXT NOT NULL,
    verification_started_at TEXT NOT NULL,
    verification_finished_at TEXT NOT NULL,
    status TEXT NOT NULL,
    checked_events INTEGER NOT NULL,
    alerts_count INTEGER NOT NULL,
    report_json TEXT NOT NULL
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(db_path: Path) -> None:
    with connect(db_path) as connection:
        connection.executescript(SCHEMA_SQL)


def upsert_manifest(db_path: Path, manifest: dict[str, Any]) -> None:
    init_db(db_path)
    with connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO dataset_manifest (
                dataset_id, source_name, source_url, query_parameters_json,
                downloaded_at_utc, raw_file_path, processed_file_path,
                raw_file_hash_sha256, processed_file_hash_sha256, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(dataset_id) DO UPDATE SET
                source_name=excluded.source_name,
                source_url=excluded.source_url,
                query_parameters_json=excluded.query_parameters_json,
                downloaded_at_utc=excluded.downloaded_at_utc,
                raw_file_path=excluded.raw_file_path,
                processed_file_path=excluded.processed_file_path,
                raw_file_hash_sha256=excluded.raw_file_hash_sha256,
                processed_file_hash_sha256=excluded.processed_file_hash_sha256,
                notes=excluded.notes
            """,
            (
                manifest["dataset_id"],
                manifest["source_name"],
                manifest["source_url"],
                json.dumps(manifest["query_parameters"], sort_keys=True),
                manifest["downloaded_at_utc"],
                manifest["raw_file_path"],
                manifest["processed_file_path"],
                manifest["raw_file_hash_sha256"],
                manifest["processed_file_hash_sha256"],
                manifest.get("notes", ""),
            ),
        )


def replace_measurements(db_path: Path, measurements: pd.DataFrame, dataset_id: str) -> None:
    missing = missing_columns(measurements.columns)
    if missing:
        raise ValueError(f"Measurements are missing canonical columns: {missing}")

    init_db(db_path)
    ordered = measurements[CANONICAL_MEASUREMENT_COLUMNS].copy()
    with connect(db_path) as connection:
        connection.execute("DELETE FROM measurements WHERE dataset_id = ?", (dataset_id,))
        ordered.to_sql("measurements", connection, if_exists="append", index=False)
