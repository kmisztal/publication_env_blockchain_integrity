"""Default filesystem paths for local experiment artifacts."""

from __future__ import annotations

from pathlib import Path


EXPERIMENTS_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = EXPERIMENTS_ROOT / "data"
RAW_DATA_DIR = DATA_ROOT / "raw"
PROCESSED_DATA_DIR = DATA_ROOT / "processed"
TAMPERED_DATA_DIR = DATA_ROOT / "tampered"
OUTPUTS_ROOT = EXPERIMENTS_ROOT / "outputs"
AUDIT_OUTPUT_DIR = OUTPUTS_ROOT / "audit"
CHAIN_OUTPUT_DIR = OUTPUTS_ROOT / "chains"
VERIFICATION_OUTPUT_DIR = OUTPUTS_ROOT / "verification"
METRICS_OUTPUT_DIR = OUTPUTS_ROOT / "metrics"
MAP_OUTPUT_DIR = OUTPUTS_ROOT / "maps"
MANIFEST_OUTPUT_DIR = OUTPUTS_ROOT / "manifests"
DEFAULT_DB_PATH = DATA_ROOT / "experiments.sqlite"


def ensure_experiment_dirs() -> None:
    for path in (
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        TAMPERED_DATA_DIR,
        AUDIT_OUTPUT_DIR,
        CHAIN_OUTPUT_DIR,
        VERIFICATION_OUTPUT_DIR,
        METRICS_OUTPUT_DIR,
        MAP_OUTPUT_DIR,
        MANIFEST_OUTPUT_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)
