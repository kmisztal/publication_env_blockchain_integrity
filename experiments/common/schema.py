"""Canonical measurement schema used across dataset ingesters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


CANONICAL_MEASUREMENT_COLUMNS = [
    "record_id",
    "dataset_id",
    "source_name",
    "source_record_index",
    "station_id",
    "parameter",
    "timestamp_utc",
    "value",
    "unit",
    "latitude",
    "longitude",
    "quality_flag",
    "raw_payload_json",
    "created_at_utc",
]


@dataclass(frozen=True)
class PreprocessingReport:
    dataset_id: str
    source_name: str
    input_records: int
    output_records: int
    dropped_records: int
    station_count: int
    parameter_count: int
    missing_timestamp: int
    missing_station: int
    missing_parameter: int
    missing_value: int

    def as_dict(self) -> dict[str, object]:
        return {
            "dataset_id": self.dataset_id,
            "source_name": self.source_name,
            "input_records": self.input_records,
            "output_records": self.output_records,
            "dropped_records": self.dropped_records,
            "station_count": self.station_count,
            "parameter_count": self.parameter_count,
            "missing_timestamp": self.missing_timestamp,
            "missing_station": self.missing_station,
            "missing_parameter": self.missing_parameter,
            "missing_value": self.missing_value,
        }


def missing_columns(columns: Iterable[str]) -> list[str]:
    available = set(columns)
    return [column for column in CANONICAL_MEASUREMENT_COLUMNS if column not in available]
