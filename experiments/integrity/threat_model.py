"""Generate machine-readable and Markdown threat-model artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from experiments.common.paths import THREAT_MODEL_OUTPUT_DIR, ensure_experiment_dirs
from experiments.integrity.events import MODEL_A, MODEL_B, MODEL_C, MODEL_D


def write_threat_model(
    *,
    output_dir: Path = THREAT_MODEL_OUTPUT_DIR,
) -> dict[str, Any]:
    ensure_experiment_dirs()
    output_dir.mkdir(parents=True, exist_ok=True)
    model = _threat_model()
    json_file = output_dir / "integrity_threat_model.json"
    md_file = output_dir / "integrity_threat_model.md"
    json_file.write_text(json.dumps(model, indent=2, sort_keys=True), encoding="utf-8")
    md_file.write_text(_markdown(model), encoding="utf-8")
    return {
        "threat_model_json": str(json_file),
        "threat_model_markdown": str(md_file),
        "threat_count": len(model["threats"]),
        "model_count": len(model["integrity_models"]),
    }


def _threat_model() -> dict[str, Any]:
    return {
        "scope": {
            "primary_domain": "computer_science_information_systems",
            "application_domain": "environmental_monitoring",
            "environmental_claims": "out_of_scope",
            "taxonomy_note": "STRIDE/CIA/provenance mapping TODO:CITATION_NEEDED",
        },
        "trusted_components": [
            "Experiment code and verifier implementation for the evaluated run",
            "Frozen local dataset extract and preprocessing manifest",
            "External anchor manifest for Model E when implemented",
            "Verification environment for local reproducibility checks",
        ],
        "attacker_capabilities": [
            "Modify stored measurement values",
            "Modify timestamps",
            "Delete records or events",
            "Insert fake records or events",
            "Replay existing records or events",
            "Use unauthorized or revoked actor keys",
            "Create correction events without required governance metadata",
            "Delay synchronization beyond allowed thresholds",
            "Rewrite a complete local hash chain when no external anchor is available",
        ],
        "out_of_scope_attacks": [
            "Cryptographic hash preimage or collision attacks",
            "Compromise of all verifier copies and all external anchors",
            "Physical sensor spoofing or calibration attacks",
            "Environmental anomaly detection",
            "Network-level denial of service",
            "Full blockchain consensus attacks",
        ],
        "integrity_models": {
            MODEL_A: "Conventional storage only",
            MODEL_B: "Audit trail only",
            MODEL_C: "Audit trail plus hash chain",
            MODEL_D: "Audit trail plus hash chain plus provenance/permission reconstruction",
            "E_anchored_hash_chain": "Planned anchored extension with external checkpoints",
        },
        "threats": [
            _threat(
                "value_modification",
                "Stored measurement value is changed after ingestion.",
                {"A": "not_expected", "B": "payload_hash", "C": "payload_hash", "D": "payload_hash"},
            ),
            _threat(
                "timestamp_modification",
                "Measurement or event timestamp is changed after ingestion.",
                {"A": "not_expected", "B": "payload_hash_event_id", "C": "payload_hash_block_hash", "D": "payload_hash_block_hash"},
            ),
            _threat(
                "record_deletion",
                "Measurement record or event is removed.",
                {"A": "not_expected", "B": "not_expected", "C": "previous_hash", "D": "previous_hash"},
            ),
            _threat(
                "fake_record_insertion",
                "Synthetic record or event is inserted.",
                {"A": "not_expected", "B": "payload_hash_event_id", "C": "previous_hash_payload_hash", "D": "previous_hash_payload_hash"},
            ),
            _threat(
                "replay",
                "Existing record or event is inserted again.",
                {"A": "duplicate_id", "B": "duplicate_id", "C": "duplicate_id_previous_hash", "D": "duplicate_id_previous_hash"},
            ),
            _threat(
                "broken_provenance",
                "Event references an unauthorized key.",
                {"A": "not_applicable", "B": "not_applicable", "C": "not_applicable", "D": "inactive_signature_key"},
            ),
            _threat(
                "unauthorized_correction",
                "Correction event is signed by a key without correction permission.",
                {"A": "not_applicable", "B": "not_applicable", "C": "not_applicable", "D": "unauthorized_event_type"},
            ),
            _threat(
                "revoked_actor_key_usage",
                "Event uses a key after revocation.",
                {"A": "not_applicable", "B": "not_applicable", "C": "not_applicable", "D": "inactive_signature_key"},
            ),
            _threat(
                "missing_correction_reason",
                "Correction event lacks the required reason.",
                {"A": "not_applicable", "B": "not_applicable", "C": "not_applicable", "D": "correction_reason_missing"},
            ),
            _threat(
                "delayed_synchronization",
                "Synchronization event exceeds the configured maximum delay.",
                {"A": "not_applicable", "B": "not_applicable", "C": "not_applicable", "D": "delayed_synchronization"},
            ),
            _threat(
                "admin_chain_rewrite",
                "Privileged attacker rewrites an earlier event and recomputes later hashes.",
                {
                    "A": "not_applicable",
                    "B": "not_applicable",
                    "C": "not_expected_without_anchor",
                    "D": "not_expected_without_anchor",
                    "E": "external_checkpoint_mismatch",
                },
            ),
        ],
    }


def _threat(threat_id: str, description: str, model_mapping: dict[str, str]) -> dict[str, Any]:
    return {
        "threat_id": threat_id,
        "description": description,
        "model_mapping": model_mapping,
    }


def _markdown(model: dict[str, Any]) -> str:
    lines = [
        "# Integrity Threat Model",
        "",
        "This file is a structured threat-model artifact for the proof-of-concept experiments.",
        "It is not manuscript prose.",
        "",
        "## Scope",
        "",
        f"- Primary domain: `{model['scope']['primary_domain']}`",
        f"- Application domain: `{model['scope']['application_domain']}`",
        f"- Environmental claims: `{model['scope']['environmental_claims']}`",
        f"- Taxonomy note: `{model['scope']['taxonomy_note']}`",
        "",
        "## Trusted Components",
        "",
    ]
    lines.extend(f"- {item}" for item in model["trusted_components"])
    lines.extend(["", "## Attacker Capabilities", ""])
    lines.extend(f"- {item}" for item in model["attacker_capabilities"])
    lines.extend(["", "## Out Of Scope Attacks", ""])
    lines.extend(f"- {item}" for item in model["out_of_scope_attacks"])
    lines.extend(["", "## Threat Mapping", ""])
    lines.append("| Threat | Description | A | B | C | D | E |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for threat in model["threats"]:
        mapping = threat["model_mapping"]
        lines.append(
            f"| `{threat['threat_id']}` | {threat['description']} | "
            f"`{mapping.get('A', '')}` | `{mapping.get('B', '')}` | `{mapping.get('C', '')}` | "
            f"`{mapping.get('D', '')}` | `{mapping.get('E', '')}` |"
        )
    lines.append("")
    return "\n".join(lines)
