"""OpenAQ ingestion and normalization for the MVP dataset path."""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
from typing import Any

import pandas as pd

from experiments.common.hashing import canonical_json, sha256_json
from experiments.common.manifest import create_dataset_manifest, utc_now_iso, write_manifest
from experiments.common.paths import PROCESSED_DATA_DIR, RAW_DATA_DIR, ensure_experiment_dirs
from experiments.common.schema import CANONICAL_MEASUREMENT_COLUMNS, PreprocessingReport
from experiments.common.storage import replace_measurements, upsert_manifest


SOURCE_NAME = "OpenAQ"


def read_openaq_source(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=True)
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            records = data.get("results") or data.get("data") or data.get("records")
            if records is None:
                records = [data]
        elif isinstance(data, list):
            records = data
        else:
            raise ValueError("Unsupported JSON root for OpenAQ source file.")
        return pd.json_normalize(records)
    raise ValueError(f"Unsupported OpenAQ source extension: {suffix}")


def normalize_openaq_dataframe(
    frame: pd.DataFrame,
    *,
    dataset_id: str,
    created_at_utc: str | None = None,
) -> tuple[pd.DataFrame, PreprocessingReport]:
    created_at_utc = created_at_utc or utc_now_iso()
    source = frame.copy()
    input_records = len(source)

    raw_payloads = [
        canonical_json(_clean_payload(row))
        for row in source.to_dict(orient="records")
    ]

    timestamp = _first_available(source, [
        "datetime.utc",
        "date.utc",
        "utc",
        "timestamp",
        "datetime",
        "date",
    ])
    station = _first_available(source, [
        "location.id",
        "locationId",
        "location_id",
        "locations_id",
        "station_id",
        "location",
        "location.name",
        "name",
        "sensor.id",
        "sensors_id",
    ])
    parameter = _first_available(source, [
        "parameter.name",
        "parameter",
        "parameters_name",
        "parameter_id",
    ])
    value = _first_available(source, ["value"])
    unit = _first_available(source, [
        "parameter.units",
        "unit",
        "units",
        "parameters_units",
    ])
    latitude = _first_available(source, [
        "coordinates.latitude",
        "latitude",
        "lat",
    ])
    longitude = _first_available(source, [
        "coordinates.longitude",
        "longitude",
        "lon",
        "lng",
    ])
    quality_flag = _first_available(source, [
        "quality_flag",
        "flag",
        "isMobile",
        "sensorType",
    ])

    parsed_timestamp = pd.to_datetime(timestamp, utc=True, errors="coerce")
    numeric_value = pd.to_numeric(value, errors="coerce")
    numeric_latitude = pd.to_numeric(latitude, errors="coerce")
    numeric_longitude = pd.to_numeric(longitude, errors="coerce")
    normalized_station = station.map(_normalize_identifier)
    normalized_parameter = parameter.astype("string").str.strip().str.lower()
    normalized_unit = unit.astype("string").str.strip()

    missing_timestamp = int(parsed_timestamp.isna().sum())
    missing_station = int(normalized_station.isna().sum() + (normalized_station == "").sum())
    missing_parameter = int(normalized_parameter.isna().sum() + (normalized_parameter == "").sum())
    missing_value = int(numeric_value.isna().sum())

    output = pd.DataFrame(
        {
            "dataset_id": dataset_id,
            "source_name": SOURCE_NAME,
            "source_record_index": range(input_records),
            "station_id": normalized_station,
            "parameter": normalized_parameter,
            "timestamp_utc": parsed_timestamp.dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "value": numeric_value,
            "unit": normalized_unit,
            "latitude": numeric_latitude,
            "longitude": numeric_longitude,
            "quality_flag": quality_flag.astype("string").fillna(""),
            "raw_payload_json": raw_payloads,
            "created_at_utc": created_at_utc,
        }
    )

    required = ["station_id", "parameter", "timestamp_utc", "value"]
    output = output.dropna(subset=required)
    output = output[(output["station_id"] != "") & (output["parameter"] != "")]
    output["record_id"] = output.apply(_record_id, axis=1)
    output = output[CANONICAL_MEASUREMENT_COLUMNS]
    output = output.sort_values(
        ["station_id", "parameter", "timestamp_utc", "record_id"],
        kind="mergesort",
    ).reset_index(drop=True)

    report = PreprocessingReport(
        dataset_id=dataset_id,
        source_name=SOURCE_NAME,
        input_records=input_records,
        output_records=len(output),
        dropped_records=input_records - len(output),
        station_count=int(output["station_id"].nunique()),
        parameter_count=int(output["parameter"].nunique()),
        missing_timestamp=missing_timestamp,
        missing_station=missing_station,
        missing_parameter=missing_parameter,
        missing_value=missing_value,
    )
    return output, report


def ingest_openaq_file(
    *,
    source_file: Path,
    dataset_id: str,
    source_url: str,
    query_parameters: dict[str, Any],
    database_path: Path | None = None,
    copy_raw: bool = True,
    notes: str = "",
) -> dict[str, Any]:
    ensure_experiment_dirs()
    source_file = source_file.resolve()
    raw_file_path = _copy_raw_source(source_file, dataset_id) if copy_raw else source_file

    frame = read_openaq_source(raw_file_path)
    measurements, report = normalize_openaq_dataframe(frame, dataset_id=dataset_id)

    processed_file = PROCESSED_DATA_DIR / f"{dataset_id}_measurements.csv"
    jsonl_file = PROCESSED_DATA_DIR / f"{dataset_id}_measurements.jsonl"
    report_file = PROCESSED_DATA_DIR / f"{dataset_id}_preprocessing_report.json"
    manifest_file = PROCESSED_DATA_DIR / f"{dataset_id}_manifest.json"

    measurements.to_csv(processed_file, index=False)
    measurements.to_json(jsonl_file, orient="records", lines=True)
    report_file.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True), encoding="utf-8")

    manifest = create_dataset_manifest(
        dataset_id=dataset_id,
        source_name=SOURCE_NAME,
        source_url=source_url,
        query_parameters=query_parameters,
        raw_file_path=raw_file_path,
        processed_file_path=processed_file,
        notes=notes,
    )
    write_manifest(manifest, manifest_file)

    if database_path is not None:
        upsert_manifest(database_path, manifest.as_dict())
        replace_measurements(database_path, measurements, dataset_id)

    return {
        "dataset_id": dataset_id,
        "raw_file": str(raw_file_path),
        "processed_csv": str(processed_file),
        "processed_jsonl": str(jsonl_file),
        "manifest": str(manifest_file),
        "preprocessing_report": str(report_file),
        "sqlite_database": str(database_path) if database_path is not None else None,
        "records": report.output_records,
        "dropped_records": report.dropped_records,
        "stations": report.station_count,
        "parameters": report.parameter_count,
    }


def _copy_raw_source(source_file: Path, dataset_id: str) -> Path:
    destination = RAW_DATA_DIR / f"{dataset_id}{source_file.suffix.lower()}"
    if source_file.resolve() != destination.resolve():
        shutil.copy2(source_file, destination)
    return destination


def _first_available(frame: pd.DataFrame, candidates: list[str]) -> pd.Series:
    for column in candidates:
        if column in frame.columns:
            return frame[column]
    return pd.Series([pd.NA] * len(frame), index=frame.index)


def _clean_payload(row: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in row.items():
        cleaned[str(key)] = _json_ready(value)
    return cleaned


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(nested) for key, nested in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if value is pd.NA:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    return value


def _normalize_identifier(value: Any) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def _record_id(row: pd.Series) -> str:
    payload = {
        "dataset_id": row["dataset_id"],
        "station_id": row["station_id"],
        "parameter": row["parameter"],
        "timestamp_utc": row["timestamp_utc"],
        "value": row["value"],
        "unit": None if pd.isna(row["unit"]) else row["unit"],
    }
    return "rec_" + sha256_json(payload)[:24]
