#!/usr/bin/env python3
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
import yaml
from coordlib import dump_yaml, load_yaml, validate as schema_validate

SOURCE_HEADING = "## Precommitted exact-candidate evidence source"
LAYERS = ("l0", "l1", "l2")
LAYER_SCHEMAS = {
    "l0": "l0-task-obligation-manifest",
    "l1": "l1-baseline-obligation-manifest",
    "l2": "l2-impact-obligation-manifest",
}
BOUNDARIES = {
    "consumes_obligation_manifests": True,
    "consumes_exact_candidate_evidence": True,
    "assigns_evidence_verdict": False,
    "applies_criticality_policy": False,
    "performs_repair_invalidation": False,
    "performs_lifecycle_advance": False,
    "grants_merge_authority": False,
    "grants_production_cutover": False,
}

def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()

def object_digest(value: dict[str, Any], field: str) -> str:
    payload = dict(value)
    payload.pop(field, None)
    return canonical_digest(payload)

def _safe_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or "\\" in value:
        raise ValueError(f"unsafe repository path: {value}")
    resolved = (repo_root / path).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"repository path escapes root: {value}") from exc
    return resolved

def source_semantic_errors(source: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ids = [row["evidence_id"] for row in source["evidence_items"]]
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        errors.append("evidence ids must be globally unique: " + ", ".join(duplicates))
    paths = [source["manifests"][layer]["path"] for layer in LAYERS]
    if len(paths) != len(set(paths)):
        errors.append("L0/L1/L2 manifest paths must be distinct")
    for path in paths:
        if Path(path).is_absolute() or "\\" in path or ".." in Path(path).parts:
            errors.append(f"unsafe manifest path: {path}")
    candidate_sha = source["candidate"]["sha"]
    for item in source["evidence_items"]:
        if item["candidate_sha"] != candidate_sha:
            errors.append(
                f"{item['evidence_id']}: candidate_sha must equal source candidate sha"
            )
    return errors

def validate_source(source: Any, label: str = "exact-candidate-evidence-source") -> list[str]:
    errors = schema_validate("exact-candidate-evidence-source", source, label)
    if errors:
        return errors
    return [f"{label}: {error}" for error in source_semantic_errors(source)]

def extract_precommitted_source(markdown: str) -> dict[str, Any]:
    if not isinstance(markdown, str):
        raise ValueError("GitHub issue body must be text")
    if markdown.count(SOURCE_HEADING) != 1:
        raise ValueError("GitHub issue must contain exactly one exact-candidate evidence source heading")
    tail = markdown.split(SOURCE_HEADING, 1)[1]
    start = tail.find("```yaml")
    if start < 0:
        raise ValueError("Precommitted evidence source must use a yaml code fence")
    after = tail[start + len("```yaml"):]
    end = after.find("```")
    if end < 0:
        raise ValueError("Precommitted evidence source code fence is not closed")
    value = yaml.safe_load(after[:end].strip())
    errors = validate_source(value, "github-child-contract-source")
    if errors:
        raise ValueError("; ".join(errors))
    return value

def _manifest_digest_errors(manifest: dict[str, Any], label: str) -> list[str]:
    actual = object_digest(manifest, "manifest_digest")
    stored = manifest.get("manifest_digest")
    if stored != actual:
        return [f"{label}: manifest_digest does not match canonical content"]
    return []

def _requirements(obligation: dict[str, Any]) -> list[dict[str, Any]]:
    value = obligation["evidence_required"]
    return value if isinstance(value, list) else [value]

def load_denominator(source: dict[str, Any], repo_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifests: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    obligation_ids: list[str] = []
    requirement_ids: list[str] = []
    for layer in LAYERS:
        ref = source["manifests"][layer]
        path = _safe_path(repo_root, ref["path"])
        manifest = load_yaml(path)
        schema_errors = schema_validate(LAYER_SCHEMAS[layer], manifest, path.name)
        if schema_errors:
            raise ValueError("; ".join(schema_errors))
        digest_errors = _manifest_digest_errors(manifest, path.name)
        if digest_errors:
            raise ValueError("; ".join(digest_errors))
        if manifest["manifest_digest"] != ref["digest"]:
            raise ValueError(f"{layer}: source-declared digest does not equal manifest digest")
        manifests[layer] = manifest
        for obligation in manifest["obligations"]:
            reqs = _requirements(obligation)
            normalized = []
            for req in reqs:
                normalized.append({
                    "requirement_id": req["id"],
                    "method": req["method"],
                    "independence": req["independence"],
                    "oracle_ref": req["oracle_ref"],
                })
                requirement_ids.append(req["id"])
            rows.append({
                "layer": layer.upper(),
                "obligation_id": obligation["id"],
                "severity": obligation["severity"],
                "claim_type": obligation["claim"]["type"],
                "requirements": normalized,
            })
            obligation_ids.append(obligation["id"])
    duplicate_obligations = sorted({x for x in obligation_ids if obligation_ids.count(x) > 1})
    duplicate_requirements = sorted({x for x in requirement_ids if requirement_ids.count(x) > 1})
    if duplicate_obligations:
        raise ValueError("obligation ids must be globally unique: " + ", ".join(duplicate_obligations))
    if duplicate_requirements:
        raise ValueError("evidence requirement ids must be globally unique: " + ", ".join(duplicate_requirements))
    l2_candidate = manifests["l2"]["candidate"]
    expected = source["candidate"]
    actual = {
        "repository": l2_candidate["repository"],
        "pr_number": l2_candidate["pr_number"],
        "ref": l2_candidate["head_ref"],
        "sha": l2_candidate["head_sha"],
    }
    if actual != expected:
        raise ValueError(f"source candidate must exactly equal L2 candidate identity: {actual!r}")
    rows.sort(key=lambda row: (row["layer"], row["obligation_id"]))
    return manifests, rows

def _accounting(records: list[dict[str, Any]]) -> dict[str, int]:
    requirements = [req for row in records for req in row["requirements"]]
    with_evidence = [req for req in requirements if req["evidence_items"]]
    obligations_with = [
        row for row in records
        if any(req["evidence_items"] for req in row["requirements"])
    ]
    return {
        "obligations_with_evidence": len(obligations_with),
        "obligations_without_evidence": len(records) - len(obligations_with),
        "requirements_with_evidence": len(with_evidence),
        "requirements_without_evidence": len(requirements) - len(with_evidence),
        "evidence_item_count": sum(len(req["evidence_items"]) for req in requirements),
    }

def compile_source(source: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    errors = validate_source(source)
    if errors:
        raise ValueError("; ".join(errors))
    manifests, rows = load_denominator(source, repo_root)
    req_by_id = {
        req["requirement_id"]: req
        for row in rows
        for req in row["requirements"]
    }
    evidence_by_requirement: dict[str, list[dict[str, Any]]] = {
        rid: [] for rid in req_by_id
    }
    for item in source["evidence_items"]:
        rid = item["requirement_id"]
        if rid not in req_by_id:
            raise ValueError(f"evidence references undeclared requirement: {rid}")
        if item["method"] != req_by_id[rid]["method"]:
            raise ValueError(
                f"{item['evidence_id']}: requirement {rid} expects method "
                f"{req_by_id[rid]['method']}, got {item['method']}"
            )
        evidence_by_requirement[rid].append({
            "evidence_id": item["evidence_id"],
            "method": item["method"],
            "candidate_sha": item["candidate_sha"],
            "refs": list(item["refs"]),
            "verifier_kind": item["verifier_kind"],
            "verifier_identity": item["verifier_identity"],
        })
    records = []
    for row in rows:
        out = dict(row)
        out["requirements"] = []
        for req in row["requirements"]:
            normalized = dict(req)
            normalized["evidence_items"] = sorted(
                evidence_by_requirement[req["requirement_id"]],
                key=lambda item: item["evidence_id"],
            )
            out["requirements"].append(normalized)
        records.append(out)
    manifest_summaries = {}
    for layer in LAYERS:
        layer_records = [row for row in records if row["layer"] == layer.upper()]
        manifest_summaries[layer] = {
            "path": source["manifests"][layer]["path"],
            "digest": manifests[layer]["manifest_digest"],
            "obligation_count": len(layer_records),
            "requirement_count": sum(len(row["requirements"]) for row in layer_records),
        }
    requirement_count = sum(len(row["requirements"]) for row in records)
    ledger = {
        "schema_version": "EXACT_CANDIDATE_EVIDENCE_LEDGER_V1",
        "authority": "CLOSED_DENOMINATOR_EVIDENCE_ACCOUNTING",
        "identity": dict(source["identity"]),
        "source": {
            "kind": "CLOSED_DENOMINATOR_EVIDENCE_INPUT",
            "digest": canonical_digest(source),
        },
        "candidate": dict(source["candidate"]),
        "manifests": manifest_summaries,
        "denominator": {
            "obligation_count": len(records),
            "requirement_count": requirement_count,
        },
        "records": records,
        "accounting": _accounting(records),
        "forbidden_outcomes": list(source["forbidden_outcomes"]),
        "non_goals": list(source["non_goals"]),
        "authority_boundaries": dict(BOUNDARIES),
    }
    ledger["ledger_digest"] = object_digest(ledger, "ledger_digest")
    errors = validate_ledger_shape(ledger, "compiled-evidence-ledger")
    if errors:
        raise ValueError("; ".join(errors))
    return ledger

def ledger_semantic_errors(ledger: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if ledger["ledger_digest"] != object_digest(ledger, "ledger_digest"):
        errors.append("ledger_digest does not match canonical ledger content")
    records = ledger["records"]
    requirements = [req for row in records for req in row["requirements"]]
    if ledger["denominator"]["obligation_count"] != len(records):
        errors.append("denominator obligation_count must equal record count")
    if ledger["denominator"]["requirement_count"] != len(requirements):
        errors.append("denominator requirement_count must equal requirement record count")
    ids = [row["obligation_id"] for row in records]
    req_ids = [req["requirement_id"] for req in requirements]
    evidence = [item for req in requirements for item in req["evidence_items"]]
    evid_ids = [item["evidence_id"] for item in evidence]
    if len(ids) != len(set(ids)):
        errors.append("ledger obligation ids must be globally unique")
    if len(req_ids) != len(set(req_ids)):
        errors.append("ledger requirement ids must be globally unique")
    if len(evid_ids) != len(set(evid_ids)):
        errors.append("ledger evidence ids must be globally unique")
    candidate_sha = ledger["candidate"]["sha"]
    for req in requirements:
        for item in req["evidence_items"]:
            if item["candidate_sha"] != candidate_sha:
                errors.append(
                    f"{item['evidence_id']}: evidence candidate_sha must equal ledger candidate sha"
                )
            if item["method"] != req["method"]:
                errors.append(
                    f"{item['evidence_id']}: evidence method must equal requirement method"
                )
    if ledger["accounting"] != _accounting(records):
        errors.append("accounting must exactly equal deterministic record accounting")
    for layer in LAYERS:
        rows = [row for row in records if row["layer"] == layer.upper()]
        summary = ledger["manifests"][layer]
        if summary["obligation_count"] != len(rows):
            errors.append(f"{layer}: manifest obligation_count does not match records")
        if summary["requirement_count"] != sum(len(row["requirements"]) for row in rows):
            errors.append(f"{layer}: manifest requirement_count does not match records")
    if ledger["authority_boundaries"] != BOUNDARIES:
        errors.append("evidence-ledger authority boundaries do not match fixed contract")
    return errors

def validate_ledger_shape(value: Any, label: str = "exact-candidate-evidence-ledger") -> list[str]:
    errors = schema_validate("exact-candidate-evidence-ledger", value, label)
    if errors:
        return errors
    return [f"{label}: {error}" for error in ledger_semantic_errors(value)]

def validate_ledger(
    ledger: Any,
    source: Any | None = None,
    repo_root: Path | None = None,
    label: str = "exact-candidate-evidence-ledger",
) -> list[str]:
    errors = validate_ledger_shape(ledger, label)
    if errors:
        return errors
    if source is None or repo_root is None:
        return [f"{label}: source-bound denominator replay is required"]
    source_errors = validate_source(source, "evidence-source")
    if source_errors:
        return source_errors
    if ledger["source"]["digest"] != canonical_digest(source):
        return [f"{label}: source.digest does not match supplied source"]
    try:
        fresh = compile_source(source, repo_root)
    except Exception as exc:
        return [f"{label}: denominator replay failed: {exc}"]
    if fresh != ledger:
        errors.append(f"{label}: stored ledger does not equal fresh denominator replay")
    return errors

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile or validate closed-denominator exact-candidate evidence accounting."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    compile_parser = sub.add_parser("compile")
    compile_parser.add_argument("source")
    compile_parser.add_argument("--repo-root", default=".")
    compile_parser.add_argument("--output")
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("source")
    validate_parser.add_argument("ledger")
    validate_parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    source = load_yaml(Path(args.source))
    repo_root = Path(args.repo_root).resolve()
    if args.command == "compile":
        ledger = compile_source(source, repo_root)
        rendered = dump_yaml(ledger)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return
    ledger = load_yaml(Path(args.ledger))
    errors = validate_ledger(ledger, source, repo_root, Path(args.ledger).name)
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print(f"OK: exact-candidate evidence ledger: {args.source} + {args.ledger}")

if __name__ == "__main__":
    main()
