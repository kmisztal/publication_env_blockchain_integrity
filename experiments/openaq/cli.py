"""Command-line entry points for OpenAQ MVP ingestion."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from experiments.common.paths import DEFAULT_DB_PATH


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

    download = subparsers.add_parser("download", help="Freeze a small OpenAQ API v3 extract.")
    download.add_argument("--dataset-id", required=True)
    download.add_argument("--datetime-from", required=True)
    download.add_argument("--datetime-to", required=True)
    download.add_argument(
        "--selection-mode",
        choices=["country-first", "capital-triangles"],
        default="country-first",
    )
    download.add_argument("--iso", default="PL")
    download.add_argument(
        "--city",
        action="append",
        help="City for capital-triangle selection. Can be passed more than once.",
    )
    download.add_argument("--locations-per-city", type=int, default=3)
    download.add_argument("--sensors-per-location", type=int, default=3)
    download.add_argument("--city-radius-meters", type=int, default=25000)
    download.add_argument("--min-location-distance-meters", type=int, default=5000)
    download.add_argument("--candidate-locations-per-city", type=int, default=50)
    download.add_argument(
        "--parameters-id",
        action="append",
        type=int,
        help="OpenAQ parameter ID. Can be passed more than once.",
    )
    download.add_argument("--location-limit", type=int, default=3)
    download.add_argument("--sensor-limit", type=int, default=6)
    download.add_argument("--measurements-per-sensor", type=int, default=100)
    download.add_argument("--page-delay-seconds", type=float, default=0.25)
    download.add_argument("--api-key-file", type=Path)
    download.add_argument("--resume", action="store_true")
    download.add_argument("--progress", action="store_true")
    download.add_argument("--max-retries", type=int, default=4)
    download.add_argument("--retry-backoff-seconds", type=float, default=2.0)
    download.add_argument("--rate-limit-per-minute", type=int, default=55)

    map_parser = subparsers.add_parser("map", help="Generate an HTML map from OpenAQ metadata.")
    map_parser.add_argument("--metadata-file", required=True, type=Path)
    map_parser.add_argument("--output-file", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "ingest":
        from experiments.openaq.ingest import ingest_openaq_file

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

    if args.command == "download":
        from experiments.openaq.download import (
            configure_rate_limit,
            download_capital_triangle_extract,
            download_openaq_extract,
            read_api_key_file,
        )

        configure_rate_limit(args.rate_limit_per_minute)
        api_key = read_api_key_file(args.api_key_file) if args.api_key_file else None
        if args.selection_mode == "capital-triangles":
            summary = download_capital_triangle_extract(
                dataset_id=args.dataset_id,
                datetime_from=args.datetime_from,
                datetime_to=args.datetime_to,
                api_key=api_key,
                cities=args.city,
                locations_per_city=args.locations_per_city,
                sensors_per_location=args.sensors_per_location,
                city_radius_meters=args.city_radius_meters,
                min_location_distance_meters=args.min_location_distance_meters,
                candidate_locations_per_city=args.candidate_locations_per_city,
                measurements_per_sensor=args.measurements_per_sensor,
                page_delay_seconds=args.page_delay_seconds,
                resume=args.resume,
                progress=args.progress,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff_seconds,
            )
        else:
            summary = download_openaq_extract(
                dataset_id=args.dataset_id,
                datetime_from=args.datetime_from,
                datetime_to=args.datetime_to,
                api_key=api_key,
                iso=args.iso,
                parameters_id=args.parameters_id,
                location_limit=args.location_limit,
                sensor_limit=args.sensor_limit,
                measurements_per_sensor=args.measurements_per_sensor,
                page_delay_seconds=args.page_delay_seconds,
                resume=args.resume,
                progress=args.progress,
                max_retries=args.max_retries,
                retry_backoff_seconds=args.retry_backoff_seconds,
            )
        print(json.dumps(summary.as_dict(), indent=2, sort_keys=True))
        return 0

    if args.command == "map":
        from experiments.openaq.map import generate_selection_map

        output_file = generate_selection_map(
            metadata_file=args.metadata_file,
            output_file=args.output_file,
        )
        print(json.dumps({"map_file": str(output_file)}, indent=2, sort_keys=True))
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
