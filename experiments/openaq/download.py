"""OpenAQ v3 downloader for freezing small MVP source extracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from experiments.common.hashing import sha256_file
from experiments.common.paths import RAW_DATA_DIR, ensure_experiment_dirs


OPENAQ_API_BASE_URL = "https://api.openaq.org/v3"

CAPITAL_CITY_CENTERS = {
    "warsaw": {"display_name": "Warsaw", "iso": "PL", "latitude": 52.2297, "longitude": 21.0122},
    "berlin": {"display_name": "Berlin", "iso": "DE", "latitude": 52.5200, "longitude": 13.4050},
    "paris": {"display_name": "Paris", "iso": "FR", "latitude": 48.8566, "longitude": 2.3522},
    "madrid": {"display_name": "Madrid", "iso": "ES", "latitude": 40.4168, "longitude": -3.7038},
}


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
    resume: bool = False,
    progress: bool = False,
    max_retries: int = 4,
    retry_backoff_seconds: float = 2.0,
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
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )
    sensors = _select_sensors(
        api_key=api_key,
        locations=locations,
        limit=sensor_limit,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
        progress=progress,
    )
    raw_file = RAW_DATA_DIR / f"{dataset_id}_openaq_v3_measurements.jsonl"
    metadata_file = RAW_DATA_DIR / f"{dataset_id}_openaq_v3_download_metadata.json"
    state_file = RAW_DATA_DIR / f"{dataset_id}_openaq_v3_download_state.json"

    records = _download_measurements(
        api_key=api_key,
        sensors=sensors,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        limit=measurements_per_sensor,
        page_delay_seconds=page_delay_seconds,
        output_file=raw_file,
        state_file=state_file,
        resume=resume,
        progress=progress,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )

    downloaded_at = _utc_now_iso()

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
        "state_file_path": str(state_file),
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


def download_capital_triangle_extract(
    *,
    dataset_id: str,
    datetime_from: str,
    datetime_to: str,
    api_key: str | None = None,
    cities: list[str] | None = None,
    locations_per_city: int = 3,
    sensors_per_location: int = 3,
    city_radius_meters: int = 25_000,
    min_location_distance_meters: int = 5_000,
    candidate_locations_per_city: int = 50,
    measurements_per_sensor: int = 200,
    page_delay_seconds: float = 0.25,
    resume: bool = False,
    progress: bool = False,
    max_retries: int = 4,
    retry_backoff_seconds: float = 2.0,
) -> OpenAQDownloadSummary:
    """Download a multi-city extract using high-volume triangular station selection."""
    ensure_experiment_dirs()
    api_key = api_key or os.environ.get("OPENAQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OpenAQ API key not found. Set OPENAQ_API_KEY or pass --api-key-file."
        )

    selected_city_keys = [_normalize_city_key(city) for city in (cities or list(CAPITAL_CITY_CENTERS))]
    unknown = [city for city in selected_city_keys if city not in CAPITAL_CITY_CENTERS]
    if unknown:
        raise ValueError(f"Unsupported city names: {unknown}")

    all_locations: list[dict[str, Any]] = []
    all_sensors: list[dict[str, Any]] = []
    city_selection_reports: list[dict[str, Any]] = []

    for city_key in selected_city_keys:
        city = CAPITAL_CITY_CENTERS[city_key]
        _progress(progress, f"Scoring candidate locations for {city['display_name']}...")
        candidates = _rank_city_locations(
            api_key=api_key,
            city_key=city_key,
            city=city,
            datetime_from=datetime_from,
            datetime_to=datetime_to,
            radius_meters=city_radius_meters,
            candidate_limit=candidate_locations_per_city,
            sensors_per_location=sensors_per_location,
            page_delay_seconds=page_delay_seconds,
            progress=progress,
            max_retries=max_retries,
            retry_backoff_seconds=retry_backoff_seconds,
        )
        selected_locations = _select_triangle_locations(
            candidates=candidates,
            city=city,
            count=locations_per_city,
            min_distance_meters=min_location_distance_meters,
        )
        for selected in selected_locations:
            location = selected["location"]
            all_locations.append(location)
            for sensor in selected["selected_sensors"]:
                enriched_sensor = dict(sensor)
                enriched_sensor["city"] = {
                    "key": city_key,
                    "name": city["display_name"],
                    "center": {
                        "latitude": city["latitude"],
                        "longitude": city["longitude"],
                    },
                }
                enriched_sensor["location"] = location
                all_sensors.append(enriched_sensor)

        city_selection_reports.append(
            {
                "city": city,
                "candidate_location_count": len(candidates),
                "selected_location_count": len(selected_locations),
                "selected_locations": [
                    {
                        "location_id": item["location"].get("id"),
                        "location_name": item["location"].get("name"),
                        "distance_from_center_m": item["distance_from_center_m"],
                        "bearing_from_center_degrees": item["bearing_from_center_degrees"],
                        "measurement_score": item["measurement_score"],
                        "selected_sensor_ids": [sensor.get("id") for sensor in item["selected_sensors"]],
                    }
                    for item in selected_locations
                ],
            }
        )

    raw_file = RAW_DATA_DIR / f"{dataset_id}_openaq_v3_measurements.jsonl"
    metadata_file = RAW_DATA_DIR / f"{dataset_id}_openaq_v3_download_metadata.json"
    state_file = RAW_DATA_DIR / f"{dataset_id}_openaq_v3_download_state.json"

    records = _download_measurements(
        api_key=api_key,
        sensors=all_sensors,
        datetime_from=datetime_from,
        datetime_to=datetime_to,
        limit=measurements_per_sensor,
        page_delay_seconds=page_delay_seconds,
        output_file=raw_file,
        state_file=state_file,
        resume=resume,
        progress=progress,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )

    query_parameters = {
        "api_version": "v3",
        "selection_mode": "capital_triangles",
        "cities": selected_city_keys,
        "locations_per_city": locations_per_city,
        "sensors_per_location": sensors_per_location,
        "city_radius_meters": city_radius_meters,
        "min_location_distance_meters": min_location_distance_meters,
        "candidate_locations_per_city": candidate_locations_per_city,
        "measurements_per_sensor": measurements_per_sensor,
        "datetime_from": datetime_from,
        "datetime_to": datetime_to,
    }

    downloaded_at = _utc_now_iso()

    metadata = {
        "dataset_id": dataset_id,
        "source_name": "OpenAQ",
        "source_url": OPENAQ_API_BASE_URL,
        "downloaded_at_utc": downloaded_at,
        "query_parameters": query_parameters,
        "city_selection_reports": city_selection_reports,
        "locations": all_locations,
        "sensors": all_sensors,
        "record_count": len(records),
        "raw_file_path": str(raw_file),
        "raw_file_hash_sha256": sha256_file(raw_file),
        "state_file_path": str(state_file),
        "notes": "Frozen OpenAQ API v3 capital-triangle extract for PoC ingestion. Not an experiment result.",
    }
    metadata_file.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")

    return OpenAQDownloadSummary(
        dataset_id=dataset_id,
        raw_file_path=str(raw_file),
        metadata_file_path=str(metadata_file),
        source_url=OPENAQ_API_BASE_URL,
        location_count=len(all_locations),
        sensor_count=len(all_sensors),
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
    max_retries: int,
    retry_backoff_seconds: float,
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
    response = _api_get(
        api_key,
        "/locations",
        params,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )
    return response.get("results", [])[:limit]


def _get_locations_near_city(
    *,
    api_key: str,
    latitude: float,
    longitude: float,
    radius_meters: int,
    limit: int,
    max_retries: int,
    retry_backoff_seconds: float,
) -> list[dict[str, Any]]:
    response = _api_get(
        api_key,
        "/locations",
        {
            "coordinates": f"{latitude:.4f},{longitude:.4f}",
            "radius": radius_meters,
            "limit": limit,
            "page": 1,
            "order_by": "id",
            "sort_order": "asc",
        },
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )
    return response.get("results", [])[:limit]


def _rank_city_locations(
    *,
    api_key: str,
    city_key: str,
    city: dict[str, Any],
    datetime_from: str,
    datetime_to: str,
    radius_meters: int,
    candidate_limit: int,
    sensors_per_location: int,
    page_delay_seconds: float,
    progress: bool,
    max_retries: int,
    retry_backoff_seconds: float,
) -> list[dict[str, Any]]:
    locations = _get_locations_near_city(
        api_key=api_key,
        latitude=city["latitude"],
        longitude=city["longitude"],
        radius_meters=radius_meters,
        limit=candidate_limit,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )
    ranked: list[dict[str, Any]] = []
    for index, location in enumerate(locations, start=1):
        location_id = location.get("id")
        coordinates = location.get("coordinates") or {}
        latitude = coordinates.get("latitude")
        longitude = coordinates.get("longitude")
        if location_id is None or latitude is None or longitude is None:
            continue

        try:
            sensors_response = _api_get(
                api_key,
                f"/locations/{location_id}/sensors",
                {},
                max_retries=max_retries,
                retry_backoff_seconds=retry_backoff_seconds,
            )
        except RuntimeError as error:
            _progress(progress, f"  {city['display_name']}: skipping location {location_id}: {error}")
            continue
        sensors = sensors_response.get("results", [])
        _progress(
            progress,
            f"  {city['display_name']}: location {index}/{len(locations)} "
            f"id={location_id} sensors={len(sensors)}",
        )
        scored_sensors = []
        for sensor in sensors:
            sensor_id = sensor.get("id")
            if sensor_id is None:
                continue
            measurement_count = _measurement_count(
                api_key=api_key,
                sensor_id=sensor_id,
                datetime_from=datetime_from,
                datetime_to=datetime_to,
                max_retries=max_retries,
                retry_backoff_seconds=retry_backoff_seconds,
                progress=progress,
            )
            scored = dict(sensor)
            scored["selection_measurement_count"] = measurement_count
            scored_sensors.append(scored)
            if page_delay_seconds > 0:
                time.sleep(page_delay_seconds)

        selected_sensors = sorted(
            scored_sensors,
            key=lambda item: item.get("selection_measurement_count", 0),
            reverse=True,
        )[:sensors_per_location]
        measurement_score = sum(
            int(sensor.get("selection_measurement_count", 0))
            for sensor in selected_sensors
        )
        ranked.append(
            {
                "city_key": city_key,
                "location": location,
                "selected_sensors": selected_sensors,
                "measurement_score": measurement_score,
                "distance_from_center_m": _haversine_meters(
                    city["latitude"],
                    city["longitude"],
                    float(latitude),
                    float(longitude),
                ),
                "bearing_from_center_degrees": _bearing_degrees(
                    city["latitude"],
                    city["longitude"],
                    float(latitude),
                    float(longitude),
                ),
            }
        )
    return sorted(ranked, key=lambda item: item["measurement_score"], reverse=True)


def _measurement_count(
    *,
    api_key: str,
    sensor_id: int,
    datetime_from: str,
    datetime_to: str,
    max_retries: int,
    retry_backoff_seconds: float,
    progress: bool,
) -> int:
    try:
        response = _api_get(
            api_key,
            f"/sensors/{sensor_id}/measurements",
            {
                "datetime_from": datetime_from,
                "datetime_to": datetime_to,
                "limit": 1,
                "page": 1,
            },
            max_retries=max_retries,
            retry_backoff_seconds=retry_backoff_seconds,
        )
    except RuntimeError as error:
        _progress(progress, f"    sensor {sensor_id}: measurement count failed, score=0: {error}")
        return 0
    found = (response.get("meta") or {}).get("found")
    try:
        return int(found)
    except (TypeError, ValueError):
        return len(response.get("results", []))


def _select_triangle_locations(
    *,
    candidates: list[dict[str, Any]],
    city: dict[str, Any],
    count: int,
    min_distance_meters: int,
) -> list[dict[str, Any]]:
    if count <= 0:
        return []
    if count != 3:
        return _select_distance_filtered(candidates, count, min_distance_meters)

    sectors = [(0, 120), (120, 240), (240, 360)]
    selected: list[dict[str, Any]] = []
    selected_ids: set[Any] = set()

    for start, end in sectors:
        sector_candidates = [
            item
            for item in candidates
            if start <= item["bearing_from_center_degrees"] < end
        ]
        if not sector_candidates:
            continue
        distance_filtered = [
            item
            for item in sector_candidates
            if _is_far_enough(item, selected, min_distance_meters)
        ]
        best = max(
            distance_filtered or sector_candidates,
            key=lambda item: (
                item["measurement_score"],
                item["distance_from_center_m"],
            ),
        )
        selected.append(best)
        selected_ids.add(best["location"].get("id"))

    for item in candidates:
        if len(selected) >= count:
            break
        location_id = item["location"].get("id")
        if location_id not in selected_ids and _is_far_enough(item, selected, min_distance_meters):
            selected.append(item)
            selected_ids.add(location_id)

    for item in candidates:
        if len(selected) >= count:
            break
        location_id = item["location"].get("id")
        if location_id not in selected_ids:
            selected.append(item)
            selected_ids.add(location_id)

    return selected[:count]


def _select_distance_filtered(
    candidates: list[dict[str, Any]],
    count: int,
    min_distance_meters: int,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for item in candidates:
        if len(selected) >= count:
            break
        if _is_far_enough(item, selected, min_distance_meters):
            selected.append(item)
    for item in candidates:
        if len(selected) >= count:
            break
        if item not in selected:
            selected.append(item)
    return selected[:count]


def _is_far_enough(
    candidate: dict[str, Any],
    selected: list[dict[str, Any]],
    min_distance_meters: int,
) -> bool:
    if min_distance_meters <= 0:
        return True
    candidate_coordinates = (candidate.get("location") or {}).get("coordinates") or {}
    candidate_lat = candidate_coordinates.get("latitude")
    candidate_lon = candidate_coordinates.get("longitude")
    if candidate_lat is None or candidate_lon is None:
        return False
    for item in selected:
        coordinates = (item.get("location") or {}).get("coordinates") or {}
        lat = coordinates.get("latitude")
        lon = coordinates.get("longitude")
        if lat is None or lon is None:
            continue
        distance = _haversine_meters(float(candidate_lat), float(candidate_lon), float(lat), float(lon))
        if distance < min_distance_meters:
            return False
    return True


def _select_sensors(
    *,
    api_key: str,
    locations: list[dict[str, Any]],
    limit: int,
    max_retries: int,
    retry_backoff_seconds: float,
    progress: bool,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for location in locations:
        location_id = location.get("id")
        if location_id is None:
            continue
        try:
            response = _api_get(
                api_key,
                f"/locations/{location_id}/sensors",
                {},
                max_retries=max_retries,
                retry_backoff_seconds=retry_backoff_seconds,
            )
        except RuntimeError as error:
            _progress(progress, f"Skipping location {location_id}: {error}")
            continue
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
    output_file: Path | None = None,
    state_file: Path | None = None,
    resume: bool = False,
    progress: bool = False,
    max_retries: int = 4,
    retry_backoff_seconds: float = 2.0,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = _read_jsonl(output_file) if resume and output_file else []
    completed_sensor_ids = _read_completed_sensor_ids(state_file) if resume and state_file else set()

    if output_file is not None and not resume:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("", encoding="utf-8")
    if state_file is not None and not resume:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        _write_state(state_file, completed_sensor_ids)

    total = len(sensors)
    for index, sensor in enumerate(sensors, start=1):
        sensor_id = sensor.get("id")
        if sensor_id is None:
            continue
        sensor_key = str(sensor_id)
        if sensor_key in completed_sensor_ids:
            _progress(progress, f"Measurements {index}/{total}: sensor {sensor_id} already complete, skipping.")
            continue

        _progress(progress, f"Measurements {index}/{total}: downloading sensor {sensor_id}...")
        params = {
            "datetime_from": datetime_from,
            "datetime_to": datetime_to,
            "limit": limit,
            "page": 1,
        }
        try:
            response = _api_get(
                api_key,
                f"/sensors/{sensor_id}/measurements",
                params,
                max_retries=max_retries,
                retry_backoff_seconds=retry_backoff_seconds,
            )
        except RuntimeError as error:
            _progress(progress, f"Measurements {index}/{total}: sensor {sensor_id} failed, skipping: {error}")
            completed_sensor_ids.add(sensor_key)
            if state_file is not None:
                _write_state(state_file, completed_sensor_ids)
            continue
        sensor_records = []
        for measurement in response.get("results", []):
            enriched = dict(measurement)
            enriched["sensor"] = _trim_sensor(sensor)
            sensor_records.append(enriched)
        records.extend(sensor_records)
        completed_sensor_ids.add(sensor_key)
        if output_file is not None:
            _write_jsonl(output_file, records)
        if state_file is not None:
            _write_state(state_file, completed_sensor_ids)
        _progress(progress, f"Measurements {index}/{total}: sensor {sensor_id} records={len(sensor_records)}")
        if page_delay_seconds > 0:
            time.sleep(page_delay_seconds)
    return records


def _api_get(
    api_key: str,
    path: str,
    params: dict[str, Any],
    *,
    max_retries: int = 4,
    retry_backoff_seconds: float = 2.0,
) -> dict[str, Any]:
    query = urlencode({key: value for key, value in params.items() if value not in (None, "")})
    url = f"{OPENAQ_API_BASE_URL}{path}"
    if query:
        url = f"{url}?{query}"
    request = Request(url, headers={"X-API-Key": api_key, "Accept": "application/json"})
    retryable_statuses = {429, 500, 502, 503, 504}
    attempts = max(1, max_retries + 1)
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            last_error = RuntimeError(f"OpenAQ request failed with HTTP {error.code}: {body}")
            if error.code not in retryable_statuses or attempt >= attempts:
                raise last_error from error
            retry_after = error.headers.get("Retry-After")
            delay = _retry_delay(attempt, retry_backoff_seconds, retry_after)
            time.sleep(delay)
        except URLError as error:
            last_error = RuntimeError(f"OpenAQ request failed: {error}")
            if attempt >= attempts:
                raise last_error from error
            time.sleep(_retry_delay(attempt, retry_backoff_seconds, None))
    if last_error is not None:
        raise last_error
    raise RuntimeError("OpenAQ request failed for an unknown reason.")


def _trim_sensor(sensor: dict[str, Any]) -> dict[str, Any]:
    location = sensor.get("location", {})
    return {
        "id": sensor.get("id"),
        "name": sensor.get("name"),
        "parameter": sensor.get("parameter"),
        "selection_measurement_count": sensor.get("selection_measurement_count"),
        "city": sensor.get("city"),
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


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=True))
            handle.write("\n")


def _read_jsonl(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_state(path: Path, completed_sensor_ids: set[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "completed_sensor_ids": sorted(completed_sensor_ids),
        "updated_at_utc": _utc_now_iso(),
    }
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def _read_completed_sensor_ids(path: Path | None) -> set[str]:
    if path is None or not path.exists():
        return set()
    state = json.loads(path.read_text(encoding="utf-8"))
    return {str(sensor_id) for sensor_id in state.get("completed_sensor_ids", [])}


def _progress(enabled: bool, message: str) -> None:
    if enabled:
        print(message, file=sys.stderr, flush=True)


def _retry_delay(attempt: int, backoff_seconds: float, retry_after: str | None) -> float:
    if retry_after:
        try:
            return max(0.0, float(retry_after))
        except ValueError:
            pass
    return max(0.0, backoff_seconds * (2 ** (attempt - 1)))


def _normalize_city_key(city: str) -> str:
    aliases = {"warszawa": "warsaw", "warsaw": "warsaw"}
    key = city.strip().lower()
    return aliases.get(key, key)


def _haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6_371_000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _bearing_degrees(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)
    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    return (math.degrees(math.atan2(y, x)) + 360) % 360
