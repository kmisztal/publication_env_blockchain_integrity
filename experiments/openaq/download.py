"""OpenAQ v3 downloader for freezing small MVP source extracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from experiments.common.hashing import sha256_file
from experiments.common.paths import RAW_DATA_DIR, ensure_experiment_dirs


OPENAQ_API_BASE_URL = "https://api.openaq.org/v3"


@dataclass(frozen=True)
class OpenAQDownloadSummary:
    dataset_id: str
    raw_file_path: str
    metadata_file_path: str
    source_url: str
    location_count: int
    sensor_count: int
    measurement_count: int
    query_parameters: dict[str, Any]
    raw_file_hash_sha256: str
    downloaded_at_utc: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def download_openaq_extract(
    *,
    dataset_id: str,
    datetime_from: str,
    datetime_to: str,
    api_key: str | None = None,
    iso: str = "PL",
    parameters_id: list[int] | None = None,
    location_limit: int = 3,
    sensor_limit: int = 6,
    measurements_per_sensor: int = 100,
    page_delay_seconds: float = 0.25,
) -> OpenAQDownloadSummary:
    """Download a bounded OpenAQ v3 extract and freeze it as JSONL."""
    ensure_experiment_dirs()
    api_key = api_key or os.environ.get("OPENAQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OpenAQ API key not found. Set OPENAQ_API_KEY or pass --api-key-file."
        )

    query_parameters = {
        "iso": iso,
        "parameters_id": parameters_id or [],
        "location_limit": location_limit,
        "sensor_limit": sensor_limit,
        "measurements_per_sensor": measurements_per_sensor,
        "datetime_from": datetime_from,
        "datetime_to": datetime_to,
        "api_version": "v3",
    }

    locations = _get_locations(
        api_key=api_key,
        iso=iso,
        parameters_id=parameters_id,
        limit=location_limit,
    )
    sensors = _select_sensors(api_key=api_key, locations=locations, limit=sensor_limit)
    records = _download_measurements(
        api_key=api_key,
        sensors=sensors,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        limit=measurements_per_sensor,
        page_delay_seconds=page_delay_seconds,
    )

    raw_file = RAW_DATA_DIR / f"{dataset_id}_openaq_v3_measurements.jsonl"
    metadata_file = RAW_DATA_DIR / f"{dataset_id}_openaq_v3_download_metadata.json"
    downloaded_at = _utc_now_iso()

    with raw_file.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=True))
            handle.write("\n")

    metadata = {
        "dataset_id": dataset_id,
        "source_name": "OpenAQ",
        "source_url": OPENAQ_API_BASE_URL,
        "downloaded_at_utc": downloaded_at,
        "query_parameters": query_parameters,
        "locations": locations,
        "sensors": sensors,
        "record_count": len(records),
        "raw_file_path": str(raw_file),
        "raw_file_hash_sha256": sha256_file(raw_file),
        "notes": "Frozen OpenAQ API v3 extract for PoC ingestion. Not an experiment result.",
    }
    metadata_file.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")

    return OpenAQDownloadSummary(
        dataset_id=dataset_id,
        raw_file_path=str(raw_file),
        metadata_file_path=str(metadata_file),
        source_url=OPENAQ_API_BASE_URL,
        location_count=len(locations),
        sensor_count=len(sensors),
        measurement_count=len(records),
        query_parameters=query_parameters,
        raw_file_hash_sha256=metadata["raw_file_hash_sha256"],
        downloaded_at_utc=downloaded_at,
    )


def read_api_key_file(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _get_locations(
    *,
    api_key: str,
    iso: str,
    parameters_id: list[int] | None,
    limit: int,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "iso": iso,
        "limit": limit,
        "page": 1,
        "order_by": "id",
        "sort_order": "asc",
    }
    if parameters_id:
        params["parameters_id"] = ",".join(str(item) for item in parameters_id)
    response = _api_get(api_key, "/locations", params)
    return response.get("results", [])[:limit]


def _select_sensors(
    *,
    api_key: str,
    locations: list[dict[str, Any]],
    limit: int,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for location in locations:
        location_id = location.get("id")
        if location_id is None:
            continue
        response = _api_get(api_key, f"/locations/{location_id}/sensors", {})
        for sensor in response.get("results", []):
            enriched = dict(sensor)
            enriched["location"] = location
            selected.append(enriched)
            if len(selected) >= limit:
                return selected
    return selected


def _download_measurements(
    *,
    api_key: str,
    sensors: list[dict[str, Any]],
    datetime_from: str,
    datetime_to: str,
    limit: int,
    page_delay_seconds: float,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for sensor in sensors:
        sensor_id = sensor.get("id")
        if sensor_id is None:
            continue
        params = {
            "datetime_from": datetime_from,
            "datetime_to": datetime_to,
            "limit": limit,
            "page": 1,
        }
        response = _api_get(api_key, f"/sensors/{sensor_id}/measurements", params)
        for measurement in response.get("results", []):
            enriched = dict(measurement)
            enriched["sensor"] = _trim_sensor(sensor)
            records.append(enriched)
        if page_delay_seconds > 0:
            time.sleep(page_delay_seconds)
    return records


def _api_get(api_key: str, path: str, params: dict[str, Any]) -> dict[str, Any]:
    query = urlencode({key: value for key, value in params.items() if value not in (None, "")})
    url = f"{OPENAQ_API_BASE_URL}{path}"
    if query:
        url = f"{url}?{query}"
    request = Request(url, headers={"X-API-Key": api_key, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAQ request failed with HTTP {error.code}: {body}") from error
    except URLError as error:
        raise RuntimeError(f"OpenAQ request failed: {error}") from error


def _trim_sensor(sensor: dict[str, Any]) -> dict[str, Any]:
    location = sensor.get("location", {})
    return {
        "id": sensor.get("id"),
        "name": sensor.get("name"),
        "parameter": sensor.get("parameter"),
        "location": {
            "id": location.get("id"),
            "name": location.get("name"),
            "locality": location.get("locality"),
            "timezone": location.get("timezone"),
            "country": location.get("country"),
            "coordinates": location.get("coordinates"),
        },
    }


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
