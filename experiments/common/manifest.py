"""Dataset manifest creation for reproducible experiment inputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from experiments.common.hashing import sha256_file


@dataclass(frozen=True)
class DatasetManifest:
    dataset_id: str
    source_name: str
    source_url: str
    query_parameters: dict[str, Any]
    downloaded_at_utc: str
    raw_file_path: str
    processed_file_path: str
    raw_file_hash_sha256: str
    processed_file_hash_sha256: str
    notes: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def create_dataset_manifest(
    *,
    dataset_id: str,
    source_name: str,
    source_url: str,
    query_parameters: dict[str, Any],
    raw_file_path: Path,
    processed_file_path: Path,
    notes: str = "",
) -> DatasetManifest:
    return DatasetManifest(
        dataset_id=dataset_id,
        source_name=source_name,
        source_url=source_url,
        query_parameters=query_parameters,
        downloaded_at_utc=utc_now_iso(),
        raw_file_path=str(raw_file_path),
        processed_file_path=str(processed_file_path),
        raw_file_hash_sha256=sha256_file(raw_file_path),
        processed_file_hash_sha256=sha256_file(processed_file_path),
        notes=notes,
    )


def write_manifest(manifest: DatasetManifest, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest.as_dict(), indent=2, sort_keys=True), encoding="utf-8")
