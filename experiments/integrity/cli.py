"""CLI for generic integrity model artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from experiments.common.paths import AUDIT_OUTPUT_DIR, DEFAULT_DB_PATH


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build integrity experiment artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_db = subparsers.add_parser("init-db", help="Initialize the local experiment SQLite database.")
    init_db.add_argument("--database", type=Path, default=DEFAULT_DB_PATH)

    baseline = subparsers.add_parser(
        "build-baseline",
        help="Build Model A and Model B baseline artifacts from canonical measurements.",
    )
    baseline.add_argument("--dataset-id", required=True)
    baseline.add_argument("--measurements-file", required=True, type=Path)
    baseline.add_argument("--output-dir", type=Path, default=AUDIT_OUTPUT_DIR)
    baseline.add_argument("--database", type=Path, default=DEFAULT_DB_PATH)
    baseline.add_argument("--no-sqlite", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init-db":
        from experiments.common.storage import init_db

        init_db(args.database)
        print(json.dumps({"database": str(args.database), "status": "initialized"}, indent=2))
        return 0

    if args.command == "build-baseline":
        from experiments.integrity.models import build_baseline_artifacts

        summary = build_baseline_artifacts(
            dataset_id=args.dataset_id,
            measurements_file=args.measurements_file,
            output_dir=args.output_dir,
            database_path=None if args.no_sqlite else args.database,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
