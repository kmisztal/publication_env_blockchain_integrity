"""Command-line entry points for OpenAQ MVP ingestion."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from experiments.common.paths import DEFAULT_DB_PATH
from experiments.openaq.ingest import ingest_openaq_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenAQ ingestion for PoC experiments.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="Normalize a frozen OpenAQ export.")
    ingest.add_argument("--source-file", required=True, type=Path)
    ingest.add_argument("--dataset-id", required=True)
    ingest.add_argument("--source-url", default="https://docs.openaq.org/")
    ingest.add_argument("--query-parameters-json", default="{}")
    ingest.add_argument("--database", type=Path, default=DEFAULT_DB_PATH)
    ingest.add_argument("--no-sqlite", action="store_true")
    ingest.add_argument("--no-raw-copy", action="store_true")
    ingest.add_argument("--notes", default="")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "ingest":
        query_parameters = json.loads(args.query_parameters_json)
        database_path = None if args.no_sqlite else args.database
        summary = ingest_openaq_file(
            source_file=args.source_file,
            dataset_id=args.dataset_id,
            source_url=args.source_url,
            query_parameters=query_parameters,
            database_path=database_path,
            copy_raw=not args.no_raw_copy,
            notes=args.notes,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
