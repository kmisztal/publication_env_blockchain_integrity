"""CLI for generic integrity model artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from experiments.common.paths import (
    AUDIT_OUTPUT_DIR,
    CHAIN_OUTPUT_DIR,
    DEFAULT_DB_PATH,
    METRICS_OUTPUT_DIR,
    MANIFEST_OUTPUT_DIR,
    NEGATIVE_DATA_DIR,
    COST_OUTPUT_DIR,
    THREAT_MODEL_OUTPUT_DIR,
    TAMPERED_DATA_DIR,
    VERIFICATION_OUTPUT_DIR,
)
from experiments.integrity.events import MODEL_A, MODEL_B, MODEL_C, MODEL_D
from experiments.integrity.tampering import SUPPORTED_THREATS


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

    chain = subparsers.add_parser(
        "build-hash-chain",
        help="Build Model C hash-chain artifacts from canonical measurements.",
    )
    chain.add_argument("--dataset-id", required=True)
    chain.add_argument("--measurements-file", required=True, type=Path)
    chain.add_argument("--output-dir", type=Path, default=CHAIN_OUTPUT_DIR)
    chain.add_argument("--database", type=Path, default=DEFAULT_DB_PATH)
    chain.add_argument("--no-sqlite", action="store_true")

    provenance = subparsers.add_parser(
        "build-provenance-chain",
        help="Build Model D hash-chain artifacts with permission/provenance state.",
    )
    provenance.add_argument("--dataset-id", required=True)
    provenance.add_argument("--measurements-file", required=True, type=Path)
    provenance.add_argument("--output-dir", type=Path, default=CHAIN_OUTPUT_DIR)
    provenance.add_argument("--database", type=Path, default=DEFAULT_DB_PATH)
    provenance.add_argument("--no-sqlite", action="store_true")

    verify = subparsers.add_parser(
        "verify",
        help="Verify one generated integrity-model artifact.",
    )
    verify.add_argument("--dataset-id", required=True)
    verify.add_argument("--model-id", required=True, choices=[MODEL_A, MODEL_B, MODEL_C, MODEL_D])
    verify.add_argument("--artifact-file", required=True, type=Path)
    verify.add_argument("--output-dir", type=Path, default=VERIFICATION_OUTPUT_DIR)

    tamper = subparsers.add_parser(
        "tamper",
        help="Generate one controlled tampered artifact and ground-truth label file.",
    )
    tamper.add_argument("--dataset-id", required=True)
    tamper.add_argument("--model-id", required=True, choices=[MODEL_A, MODEL_B, MODEL_C, MODEL_D])
    tamper.add_argument("--threat-type", required=True, choices=SUPPORTED_THREATS)
    tamper.add_argument("--artifact-file", required=True, type=Path)
    tamper.add_argument("--output-dir", type=Path, default=TAMPERED_DATA_DIR)

    scenarios = subparsers.add_parser(
        "run-scenarios",
        help="Plan or run the implemented tampering scenarios across applicable models.",
    )
    scenarios.add_argument("--dataset-id", required=True)
    scenarios.add_argument("--output-dir", type=Path, default=TAMPERED_DATA_DIR)
    scenarios.add_argument("--verification-output-dir", type=Path, default=VERIFICATION_OUTPUT_DIR / "tampered")
    scenarios.add_argument("--metrics-output-dir", type=Path, default=METRICS_OUTPUT_DIR / "tampered")
    scenarios.add_argument("--verify", action="store_true")
    scenarios.add_argument("--dry-run", action="store_true")

    evaluate = subparsers.add_parser(
        "evaluate",
        help="Compare one tampering label file with one verifier alerts CSV.",
    )
    evaluate.add_argument("--labels-file", required=True, type=Path)
    evaluate.add_argument("--alerts-file", required=True, type=Path)
    evaluate.add_argument("--output-dir", type=Path, default=METRICS_OUTPUT_DIR)

    aggregate = subparsers.add_parser(
        "aggregate-metrics",
        help="Aggregate per-scenario evaluation JSON files into metrics tables.",
    )
    aggregate.add_argument("--evaluation-dir", required=True, type=Path)
    aggregate.add_argument("--output-dir", type=Path, default=METRICS_OUTPUT_DIR)
    aggregate.add_argument("--dataset-id")

    manifest = subparsers.add_parser(
        "run-manifest",
        help="Build a reproducibility manifest for a completed experiment run.",
    )
    manifest.add_argument("--dataset-id", required=True)
    manifest.add_argument("--output-dir", type=Path, default=MANIFEST_OUTPUT_DIR)

    negative = subparsers.add_parser(
        "negative-cases",
        help="Generate and evaluate non-tampering negative cases.",
    )
    negative.add_argument("--dataset-id", required=True)
    negative.add_argument("--output-dir", type=Path, default=NEGATIVE_DATA_DIR)
    negative.add_argument("--metrics-output-dir", type=Path, default=METRICS_OUTPUT_DIR / "negative")
    negative.add_argument("--verification-output-dir", type=Path, default=VERIFICATION_OUTPUT_DIR / "negative")

    cost = subparsers.add_parser(
        "cost-analysis",
        help="Measure artifact size, build time, and verification time for Models A-D.",
    )
    cost.add_argument("--dataset-id", required=True)
    cost.add_argument("--measurements-file", type=Path)
    cost.add_argument("--output-dir", type=Path, default=COST_OUTPUT_DIR)

    threat_model = subparsers.add_parser(
        "threat-model",
        help="Generate machine-readable and Markdown threat-model artifacts.",
    )
    threat_model.add_argument("--output-dir", type=Path, default=THREAT_MODEL_OUTPUT_DIR)
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

    if args.command == "build-hash-chain":
        from experiments.integrity.models import build_hash_chain_artifacts

        summary = build_hash_chain_artifacts(
            dataset_id=args.dataset_id,
            measurements_file=args.measurements_file,
            output_dir=args.output_dir,
            database_path=None if args.no_sqlite else args.database,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    if args.command == "build-provenance-chain":
        from experiments.integrity.models import build_provenance_artifacts

        summary = build_provenance_artifacts(
            dataset_id=args.dataset_id,
            measurements_file=args.measurements_file,
            output_dir=args.output_dir,
            database_path=None if args.no_sqlite else args.database,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    if args.command == "verify":
        from experiments.integrity.verification import verify_model_artifact

        report = verify_model_artifact(
            model_id=args.model_id,
            artifact_file=args.artifact_file,
            dataset_id=args.dataset_id,
            output_dir=args.output_dir,
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    if args.command == "tamper":
        from experiments.integrity.tampering import generate_tampered_artifact

        summary = generate_tampered_artifact(
            dataset_id=args.dataset_id,
            model_id=args.model_id,
            threat_type=args.threat_type,
            artifact_file=args.artifact_file,
            output_dir=args.output_dir,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    if args.command == "run-scenarios":
        from experiments.integrity.scenarios import run_scenarios

        summary = run_scenarios(
            dataset_id=args.dataset_id,
            output_dir=args.output_dir,
            verification_output_dir=args.verification_output_dir,
            metrics_output_dir=args.metrics_output_dir,
            verify=args.verify,
            dry_run=args.dry_run,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    if args.command == "evaluate":
        from experiments.integrity.evaluation import evaluate_scenario

        summary = evaluate_scenario(
            labels_file=args.labels_file,
            alerts_file=args.alerts_file,
            output_dir=args.output_dir,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    if args.command == "aggregate-metrics":
        from experiments.integrity.evaluation import aggregate_evaluations

        summary = aggregate_evaluations(
            evaluation_dir=args.evaluation_dir,
            output_dir=args.output_dir,
            dataset_id=args.dataset_id,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    if args.command == "run-manifest":
        from experiments.integrity.run_manifest import build_experiment_run_manifest

        summary = build_experiment_run_manifest(
            dataset_id=args.dataset_id,
            output_dir=args.output_dir,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    if args.command == "negative-cases":
        from experiments.integrity.negative_cases import run_negative_cases

        summary = run_negative_cases(
            dataset_id=args.dataset_id,
            output_dir=args.output_dir,
            metrics_output_dir=args.metrics_output_dir,
            verification_output_dir=args.verification_output_dir,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    if args.command == "cost-analysis":
        from experiments.integrity.cost_analysis import run_cost_analysis

        summary = run_cost_analysis(
            dataset_id=args.dataset_id,
            measurements_file=args.measurements_file,
            output_dir=args.output_dir,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    if args.command == "threat-model":
        from experiments.integrity.threat_model import write_threat_model

        summary = write_threat_model(output_dir=args.output_dir)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
