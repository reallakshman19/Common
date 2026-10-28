#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

import yaml
from typing import Any

from coordlib import dump_yaml, load_yaml, validate as schema_validate


class L0TaskObligationError(ValueError):
    pass


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def source_semantic_errors(source: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    claim_ids = [row["id"] for row in source["contract_claims"]]
    duplicates = sorted({cid for cid in claim_ids if claim_ids.count(cid) > 1})
    if duplicates:
        errors.append("contract claim ids must be globally unique: " + ", ".join(duplicates))

    requirement_ids: list[str] = []
    for claim in source["contract_claims"]:
        if not claim["evidence_required"]:
            errors.append(f"{claim['id']}: L0 claim requires precommitted evidence")
        for requirement in claim["evidence_required"]:
            requirement_ids.append(requirement["id"])
            if requirement["independence"] != "PRECOMMITTED":
                errors.append(
                    f"{claim['id']}.{requirement['id']}: L0 evidence must be PRECOMMITTED"
                )

    duplicate_requirements = sorted({
        rid for rid in requirement_ids if requirement_ids.count(rid) > 1
    })
    if duplicate_requirements:
        errors.append(
            "evidence requirement ids must be globally unique: "
            + ", ".join(duplicate_requirements)
        )

    producers = [row["producer"] for row in source["dependency_requirements"]]
    duplicate_producers = sorted({
        producer for producer in producers if producers.count(producer) > 1
    })
    if duplicate_producers:
        errors.append(
            "dependency producers must be unique: " + ", ".join(duplicate_producers)
        )

    return errors


def validate_source(
    source: Any,
    label: str = "l0-task-contract-source",
) -> list[str]:
    errors = schema_validate("l0-task-contract-source", source, label)
    if errors:
        return errors
    if not isinstance(source, dict):
        return [f"{label}: source must be object"]
    return [f"{label}: {error}" for error in source_semantic_errors(source)]





SOURCE_HEADING = "## Precommitted L0 source for this child"


def extract_precommitted_source(markdown: str) -> dict[str, Any]:
    if not isinstance(markdown, str):
        raise L0TaskObligationError("GitHub issue body must be text")
    heading_count = markdown.count(SOURCE_HEADING)
    if heading_count != 1:
        raise L0TaskObligationError(
            "GitHub issue must contain exactly one precommitted L0 source heading"
        )
    tail = markdown.split(SOURCE_HEADING, 1)[1]
    start = tail.find("```yaml")
    if start < 0:
        raise L0TaskObligationError("Precommitted L0 source must use a yaml code fence")
    after = tail[start + len("```yaml"):]
    end = after.find("```")
    if end < 0:
        raise L0TaskObligationError("Precommitted L0 source code fence is not closed")
    payload = after[:end].strip()
    try:
        value = yaml.safe_load(payload)
    except yaml.YAMLError as exc:
        raise L0TaskObligationError(f"Precommitted L0 source is invalid YAML: {exc}") from exc
    errors = validate_source(value, "github-child-contract-source")
    if errors:
        raise L0TaskObligationError("; ".join(errors))
    return value


def _manifest_without_digest(manifest: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(manifest)
    value.pop("manifest_digest", None)
    return value


def compile_l0(source: dict[str, Any]) -> dict[str, Any]:
    errors = validate_source(source, "l0-source")
    if errors:
        raise L0TaskObligationError("; ".join(errors))

    source_digest = canonical_digest(source)
    child_ref = source["identity"]["child_ref"]

    obligations = []
    for claim in source["contract_claims"]:
        obligation = copy.deepcopy(claim)
        obligation["source_refs"] = [child_ref]
        obligations.append(obligation)

    manifest = {
        "schema_version": "L0_TASK_OBLIGATION_MANIFEST_V1",
        "authority": "FROZEN_PREIMPLEMENTATION_EXPECTATIONS",
        "identity": copy.deepcopy(source["identity"]),
        "source": {
            "kind": "CHILD_CONTRACT_PROJECTION",
            "ref": child_ref,
            "digest": source_digest,
        },
        "freeze": {
            "state": "FROZEN",
            "basis": "CONTRACT_ONLY",
            "freeze_ref": "sha256:" + source_digest,
        },
        "one_primary_outcome": source["one_primary_outcome"],
        "obligations": obligations,
        "forbidden_outcomes": copy.deepcopy(source["forbidden_outcomes"]),
        "dependency_requirements": copy.deepcopy(source["dependency_requirements"]),
        "non_goals": copy.deepcopy(source["non_goals"]),
        "authority_boundaries": {
            "consumes_candidate_state": False,
            "consumes_implementation_evidence": False,
            "consumes_coder_rationale": False,
            "consumes_reviewer_verdict": False,
            "emits_engineering_pass": False,
            "performs_lifecycle_advance": False,
            "grants_merge_authority": False,
            "grants_production_cutover": False,
        },
        "manifest_digest": "",
    }
    manifest["manifest_digest"] = canonical_digest(_manifest_without_digest(manifest))

    errors = schema_validate(
        "l0-task-obligation-manifest",
        manifest,
        "compiled-l0-manifest",
    )
    if errors:
        raise L0TaskObligationError("; ".join(errors))
    return manifest


def manifest_semantic_errors(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    expected_digest = canonical_digest(_manifest_without_digest(manifest))
    if manifest["manifest_digest"] != expected_digest:
        errors.append("manifest_digest does not match canonical manifest content")

    ids = [row["id"] for row in manifest["obligations"]]
    duplicates = sorted({oid for oid in ids if ids.count(oid) > 1})
    if duplicates:
        errors.append("obligation ids must be globally unique: " + ", ".join(duplicates))

    requirement_ids: list[str] = []
    for obligation in manifest["obligations"]:
        if not obligation["evidence_required"]:
            errors.append(f"{obligation['id']}: frozen L0 obligation requires evidence")
        for requirement in obligation["evidence_required"]:
            requirement_ids.append(requirement["id"])
            if requirement["independence"] != "PRECOMMITTED":
                errors.append(
                    f"{obligation['id']}.{requirement['id']}: frozen L0 evidence must be PRECOMMITTED"
                )

    duplicate_requirements = sorted({
        rid for rid in requirement_ids if requirement_ids.count(rid) > 1
    })
    if duplicate_requirements:
        errors.append(
            "manifest evidence requirement ids must be globally unique: "
            + ", ".join(duplicate_requirements)
        )

    if any(manifest["authority_boundaries"].values()):
        errors.append("L0 compiler authority boundaries must all remain false")

    return errors


def validate_manifest(
    manifest: Any,
    source: Any | None,
    label: str = "l0-task-obligation-manifest",
) -> list[str]:
    errors = schema_validate("l0-task-obligation-manifest", manifest, label)
    if errors:
        return errors
    if not isinstance(manifest, dict):
        return [f"{label}: manifest must be object"]

    errors.extend(
        f"{label}: {error}"
        for error in manifest_semantic_errors(manifest)
    )

    if source is None:
        errors.append(f"{label}: source-bound replay is required")
        return errors

    source_errors = validate_source(source, "l0-source")
    if source_errors:
        errors.extend(source_errors)
        return errors

    try:
        expected = compile_l0(copy.deepcopy(source))
    except Exception as exc:
        errors.append(f"{label}: source replay failed: {exc}")
        return errors

    if manifest != expected:
        errors.append(f"{label}: stored manifest must exactly equal fresh source replay")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile or validate frozen L0 task obligations from child-contract facts only."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    compile_parser = sub.add_parser("compile")
    compile_parser.add_argument("source")
    compile_parser.add_argument("--output")

    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("source")
    validate_parser.add_argument("manifest")

    args = parser.parse_args()

    if args.command == "compile":
        source = load_yaml(Path(args.source))
        manifest = compile_l0(source)
        rendered = dump_yaml(manifest)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return

    source = load_yaml(Path(args.source))
    manifest = load_yaml(Path(args.manifest))
    errors = validate_manifest(manifest, source, Path(args.manifest).name)
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print(f"OK: frozen L0 manifest: {args.manifest}")


if __name__ == "__main__":
    main()
