#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from coordlib import dump_yaml, load_yaml, validate as schema_validate
from exact_candidate_evidence import (
    validate_ledger as validate_exact_evidence_ledger,
    validate_source as validate_exact_evidence_source,
)

SOURCE_HEADING = "## Precommitted verdict-policy source"
STATES = ("VERIFIED", "REFUTED", "UNKNOWN", "NOT_APPLICABLE", "WAIVER")
REQUIREMENT_STATES = ("VERIFIED", "REFUTED", "UNKNOWN")
FIXED_POLICY = {
    "critical_severity": "CRITICAL",
    "unresolved_states": ["REFUTED", "UNKNOWN"],
    "not_applicable_counts_as_verified": False,
    "waiver_counts_as_verified": False,
    "waiver_requires_owner_authority": True,
}
BOUNDARIES = {
    "consumes_verdict_free_ledger": True,
    "consumes_exact_evidence_evaluations": True,
    "assigns_evidence_verdict": True,
    "applies_criticality_policy": True,
    "emits_aggregate_pass": False,
    "emits_evidence_gate_decision": False,
    "performs_repair_invalidation": False,
    "performs_lifecycle_advance": False,
    "grants_merge_authority": False,
    "grants_production_cutover": False,
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def object_digest(value: dict[str, Any], field: str) -> str:
    payload = dict(value)
    payload.pop(field, None)
    return canonical_digest(payload)


def _safe_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or chr(92) in value or ".." in path.parts:
        raise ValueError(f"unsafe repository path: {value}")
    resolved = (repo_root / path).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"repository path escapes root: {value}") from exc
    return resolved


def _zero_counts() -> dict[str, int]:
    return {state: 0 for state in STATES}


def source_semantic_errors(source: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if source["criticality_policy"] != FIXED_POLICY:
        errors.append("criticality_policy must equal the fixed P2-S6 policy")

    eval_ids = [row["evidence_id"] for row in source["evidence_evaluations"]]
    if len(eval_ids) != len(set(eval_ids)):
        errors.append("evidence evaluations must contain unique evidence_id values")

    candidate_sha = source["ledger_basis"]["candidate"]["sha"]
    for row in source["evidence_evaluations"]:
        if row["candidate_sha"] != candidate_sha:
            errors.append(
                f"{row['evidence_id']}: candidate_sha must equal ledger basis candidate"
            )

    disposition_ids = [row["obligation_id"] for row in source["dispositions"]]
    if len(disposition_ids) != len(set(disposition_ids)):
        errors.append("dispositions must contain unique obligation_id values")
    for row in source["dispositions"]:
        if row["state"] == "WAIVER" and row["authority_kind"] != "OWNER_DECISION":
            errors.append(
                f"{row['obligation_id']}: WAIVER requires OWNER_DECISION authority"
            )

    refs = [
        source["ledger_basis"]["evidence_source"],
        source["ledger_basis"]["evidence_ledger"],
    ]
    for ref in refs:
        value = ref["path"]
        path = Path(value)
        if path.is_absolute() or chr(92) in value or ".." in path.parts:
            errors.append(f"unsafe ledger basis path: {value}")

    expected = source["expected_projection"]
    if sum(expected["state_counts"].values()) != expected["obligation_count"]:
        errors.append("expected state_counts must sum to obligation_count")
    critical = expected["critical"]
    critical_count = critical["obligation_count"]
    if sum(critical[state] for state in STATES) != critical_count:
        errors.append("expected critical state counts must sum to critical obligation_count")
    if expected["unresolved_critical_refuted"] != critical["REFUTED"]:
        errors.append("expected unresolved_critical_refuted must equal critical REFUTED")
    if expected["unresolved_critical_unknown"] != critical["UNKNOWN"]:
        errors.append("expected unresolved_critical_unknown must equal critical UNKNOWN")
    if expected["waived_critical"] != critical["WAIVER"]:
        errors.append("expected waived_critical must equal critical WAIVER")
    if expected["not_applicable_critical"] != critical["NOT_APPLICABLE"]:
        errors.append(
            "expected not_applicable_critical must equal critical NOT_APPLICABLE"
        )
    return errors


def validate_source(source: Any, label: str = "verdict-policy-source") -> list[str]:
    errors = schema_validate("verdict-policy-source", source, label)
    if errors:
        return errors
    return [f"{label}: {error}" for error in source_semantic_errors(source)]


def extract_precommitted_source(markdown: str) -> dict[str, Any]:
    if not isinstance(markdown, str):
        raise ValueError("GitHub issue body must be text")
    if markdown.count(SOURCE_HEADING) != 1:
        raise ValueError("GitHub issue must contain exactly one verdict-policy source heading")
    tail = markdown.split(SOURCE_HEADING, 1)[1]
    start = tail.find("```yaml")
    if start < 0:
        raise ValueError("Precommitted verdict-policy source must use a yaml code fence")
    after = tail[start + len("```yaml"):]
    end = after.find("```")
    if end < 0:
        raise ValueError("Precommitted verdict-policy source code fence is not closed")
    value = yaml.safe_load(after[:end].strip())
    errors = validate_source(value, "github-child-contract-source")
    if errors:
        raise ValueError("; ".join(errors))
    return value


def _load_basis(
    source: dict[str, Any],
    repo_root: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    basis = source["ledger_basis"]
    evidence_source_path = _safe_path(
        repo_root,
        basis["evidence_source"]["path"],
    )
    evidence_ledger_path = _safe_path(
        repo_root,
        basis["evidence_ledger"]["path"],
    )
    evidence_source = load_yaml(evidence_source_path)
    ledger = load_yaml(evidence_ledger_path)

    source_errors = validate_exact_evidence_source(
        evidence_source,
        evidence_source_path.name,
    )
    if source_errors:
        raise ValueError("; ".join(source_errors))
    if canonical_digest(evidence_source) != basis["evidence_source"]["digest"]:
        raise ValueError("evidence source digest does not match P2-S6 basis")

    if ledger.get("ledger_digest") != basis["evidence_ledger"]["digest"]:
        raise ValueError("evidence ledger digest does not match P2-S6 basis")
    ledger_errors = validate_exact_evidence_ledger(
        ledger,
        evidence_source,
        repo_root,
        evidence_ledger_path.name,
    )
    if ledger_errors:
        raise ValueError("; ".join(ledger_errors))

    candidate = basis["candidate"]
    if ledger["candidate"] != candidate:
        raise ValueError("ledger candidate does not equal P2-S6 candidate basis")
    if evidence_source["candidate"] != candidate:
        raise ValueError("evidence source candidate does not equal P2-S6 candidate basis")
    return evidence_source, ledger


def _index_ledger(
    ledger: dict[str, Any],
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, str],
]:
    obligations: dict[str, dict[str, Any]] = {}
    evidence: dict[str, dict[str, Any]] = {}
    evidence_to_obligation: dict[str, str] = {}
    for record in ledger["records"]:
        oid = record["obligation_id"]
        if oid in obligations:
            raise ValueError(f"duplicate ledger obligation id: {oid}")
        obligations[oid] = record
        for requirement in record["requirements"]:
            rid = requirement["requirement_id"]
            for item in requirement["evidence_items"]:
                eid = item["evidence_id"]
                if eid in evidence:
                    raise ValueError(f"duplicate ledger evidence id: {eid}")
                evidence[eid] = {
                    "requirement_id": rid,
                    "item": item,
                }
                evidence_to_obligation[eid] = oid
    return obligations, evidence, evidence_to_obligation


def _cross_validate_inputs(
    source: dict[str, Any],
    ledger: dict[str, Any],
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    obligations, evidence, evidence_to_obligation = _index_ledger(ledger)
    evaluations: dict[str, dict[str, Any]] = {}
    candidate_sha = source["ledger_basis"]["candidate"]["sha"]
    for row in source["evidence_evaluations"]:
        eid = row["evidence_id"]
        target = evidence.get(eid)
        if target is None:
            raise ValueError(f"evaluation references absent evidence item: {eid}")
        item = target["item"]
        if row["requirement_id"] != target["requirement_id"]:
            raise ValueError(f"{eid}: evaluation requirement_id does not match ledger")
        if row["candidate_sha"] != item["candidate_sha"]:
            raise ValueError(f"{eid}: evaluation candidate_sha does not match evidence")
        if row["candidate_sha"] != candidate_sha:
            raise ValueError(f"{eid}: evaluation candidate_sha does not match candidate basis")
        if row["basis_ref"] not in item["refs"]:
            raise ValueError(f"{eid}: evaluation basis_ref is not retained evidence provenance")
        evaluations[eid] = row

    dispositions: dict[str, dict[str, Any]] = {}
    for row in source["dispositions"]:
        oid = row["obligation_id"]
        if oid not in obligations:
            raise ValueError(f"disposition references unknown obligation: {oid}")
        if row["state"] == "WAIVER" and row["authority_kind"] != "OWNER_DECISION":
            raise ValueError(f"{oid}: WAIVER requires OWNER_DECISION authority")
        evaluated_for_obligation = [
            eid
            for eid in evaluations
            if evidence_to_obligation[eid] == oid
        ]
        if evaluated_for_obligation:
            raise ValueError(
                f"{oid}: disposition cannot coexist with evaluated evidence"
            )
        dispositions[oid] = row
    return evaluations, dispositions


def _requirement_state(outcomes: list[str]) -> str:
    if "CONTRADICTS" in outcomes:
        return "REFUTED"
    if "SATISFIES" in outcomes:
        return "VERIFIED"
    return "UNKNOWN"


def _obligation_state(requirement_states: list[str]) -> str:
    if "REFUTED" in requirement_states:
        return "REFUTED"
    if requirement_states and all(state == "VERIFIED" for state in requirement_states):
        return "VERIFIED"
    return "UNKNOWN"


def _expected_errors(
    source: dict[str, Any],
    projection: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    expected = source["expected_projection"]
    accounting = projection["accounting"]
    critical = projection["criticality"]
    if accounting["obligation_count"] != expected["obligation_count"]:
        errors.append("retained obligation_count differs from expected projection")
    if accounting["state_counts"] != expected["state_counts"]:
        errors.append("retained state_counts differ from expected projection")
    expected_critical = dict(expected["critical"])
    expected_critical_count = expected_critical.pop("obligation_count")
    if critical["obligation_count"] != expected_critical_count:
        errors.append("retained critical obligation_count differs from expected projection")
    if critical["state_counts"] != expected_critical:
        errors.append("retained critical state_counts differ from expected projection")
    if len(critical["unresolved_refuted_ids"]) != expected["unresolved_critical_refuted"]:
        errors.append("retained unresolved critical REFUTED count differs from expected")
    if len(critical["unresolved_unknown_ids"]) != expected["unresolved_critical_unknown"]:
        errors.append("retained unresolved critical UNKNOWN count differs from expected")
    if len(critical["waiver_ids"]) != expected["waived_critical"]:
        errors.append("retained critical WAIVER count differs from expected")
    if len(critical["not_applicable_ids"]) != expected["not_applicable_critical"]:
        errors.append("retained critical NOT_APPLICABLE count differs from expected")
    return errors


def derive_projection(
    source: dict[str, Any],
    repo_root: Path,
    *,
    enforce_expected: bool = True,
) -> dict[str, Any]:
    source_errors = validate_source(source)
    if source_errors:
        raise ValueError("; ".join(source_errors))
    _, ledger = _load_basis(source, repo_root)
    evaluations, dispositions = _cross_validate_inputs(source, ledger)

    records: list[dict[str, Any]] = []
    for record in ledger["records"]:
        oid = record["obligation_id"]
        requirement_rows: list[dict[str, Any]] = []
        requirement_states: list[str] = []
        for requirement in record["requirements"]:
            evidence_rows: list[dict[str, Any]] = []
            outcomes: list[str] = []
            for item in requirement["evidence_items"]:
                evaluation = evaluations.get(item["evidence_id"])
                output_item = copy.deepcopy(item)
                if evaluation is None:
                    output_item["evaluation_outcome"] = None
                    output_item["evaluation_basis_ref"] = None
                else:
                    output_item["evaluation_outcome"] = evaluation["outcome"]
                    output_item["evaluation_basis_ref"] = evaluation["basis_ref"]
                    outcomes.append(evaluation["outcome"])
                evidence_rows.append(output_item)
            state = _requirement_state(outcomes)
            requirement_states.append(state)
            requirement_rows.append({
                "requirement_id": requirement["requirement_id"],
                "method": requirement["method"],
                "independence": requirement["independence"],
                "oracle_ref": requirement["oracle_ref"],
                "state": state,
                "evidence_items": evidence_rows,
            })

        disposition = dispositions.get(oid)
        if disposition is None:
            state = _obligation_state(requirement_states)
            output_disposition = None
        else:
            state = disposition["state"]
            output_disposition = {
                key: disposition[key]
                for key in (
                    "state",
                    "basis_ref",
                    "authority_kind",
                    "authority_ref",
                    "reason",
                )
            }
        records.append({
            "layer": record["layer"],
            "obligation_id": oid,
            "severity": record["severity"],
            "claim_type": record["claim_type"],
            "state": state,
            "disposition": output_disposition,
            "requirements": requirement_rows,
        })

    records.sort(key=lambda row: (row["layer"], row["obligation_id"]))
    state_counts = _zero_counts()
    for row in records:
        state_counts[row["state"]] += 1

    critical_rows = [
        row for row in records
        if row["severity"] == FIXED_POLICY["critical_severity"]
    ]
    critical_counts = _zero_counts()
    for row in critical_rows:
        critical_counts[row["state"]] += 1

    projection = {
        "schema_version": "VERDICT_PROJECTION_V1",
        "authority": "EVIDENCE_VERDICT_AND_CRITICALITY_PROJECTION",
        "identity": dict(source["identity"]),
        "source": {"digest": canonical_digest(source)},
        "candidate": dict(source["ledger_basis"]["candidate"]),
        "ledger_basis": {
            "evidence_source_digest": source["ledger_basis"]["evidence_source"]["digest"],
            "evidence_ledger_digest": source["ledger_basis"]["evidence_ledger"]["digest"],
        },
        "records": records,
        "accounting": {
            "obligation_count": len(records),
            "state_counts": state_counts,
        },
        "criticality": {
            "obligation_count": len(critical_rows),
            "state_counts": critical_counts,
            "unresolved_refuted_ids": sorted(
                row["obligation_id"]
                for row in critical_rows
                if row["state"] == "REFUTED"
            ),
            "unresolved_unknown_ids": sorted(
                row["obligation_id"]
                for row in critical_rows
                if row["state"] == "UNKNOWN"
            ),
            "not_applicable_ids": sorted(
                row["obligation_id"]
                for row in critical_rows
                if row["state"] == "NOT_APPLICABLE"
            ),
            "waiver_ids": sorted(
                row["obligation_id"]
                for row in critical_rows
                if row["state"] == "WAIVER"
            ),
        },
        "authority_boundaries": dict(BOUNDARIES),
    }
    projection["projection_digest"] = object_digest(
        projection,
        "projection_digest",
    )
    shape_errors = validate_projection_shape(
        projection,
        "compiled-verdict-projection",
    )
    if shape_errors:
        raise ValueError("; ".join(shape_errors))
    if enforce_expected:
        expected_errors = _expected_errors(source, projection)
        if expected_errors:
            raise ValueError("; ".join(expected_errors))
    return projection


def projection_semantic_errors(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value["projection_digest"] != object_digest(value, "projection_digest"):
        errors.append("projection_digest does not match canonical projection content")

    records = value["records"]
    ids = [row["obligation_id"] for row in records]
    if len(ids) != len(set(ids)):
        errors.append("projection obligation ids must be unique")

    state_counts = _zero_counts()
    for row in records:
        state_counts[row["state"]] += 1
        disposition = row["disposition"]
        requirement_states = [req["state"] for req in row["requirements"]]
        if row["state"] == "VERIFIED":
            if not requirement_states or not all(
                state == "VERIFIED" for state in requirement_states
            ):
                errors.append(f"{row['obligation_id']}: invalid VERIFIED obligation")
            if disposition is not None:
                errors.append(f"{row['obligation_id']}: VERIFIED cannot have disposition")
        elif row["state"] == "REFUTED":
            if "REFUTED" not in requirement_states:
                errors.append(f"{row['obligation_id']}: REFUTED requires refuted requirement")
            if disposition is not None:
                errors.append(f"{row['obligation_id']}: REFUTED cannot have disposition")
        elif row["state"] == "UNKNOWN":
            if disposition is not None:
                errors.append(f"{row['obligation_id']}: UNKNOWN cannot have disposition")
        elif row["state"] in {"NOT_APPLICABLE", "WAIVER"}:
            if disposition is None or disposition["state"] != row["state"]:
                errors.append(f"{row['obligation_id']}: disposition state mismatch")
            if row["state"] == "WAIVER" and disposition is not None:
                if disposition["authority_kind"] != "OWNER_DECISION":
                    errors.append(f"{row['obligation_id']}: WAIVER requires OWNER_DECISION")

    accounting = value["accounting"]
    if accounting["obligation_count"] != len(records):
        errors.append("accounting obligation_count does not match records")
    if accounting["state_counts"] != state_counts:
        errors.append("accounting state_counts do not match records")

    critical_rows = [row for row in records if row["severity"] == "CRITICAL"]
    critical_counts = _zero_counts()
    for row in critical_rows:
        critical_counts[row["state"]] += 1
    criticality = value["criticality"]
    if criticality["obligation_count"] != len(critical_rows):
        errors.append("criticality obligation_count does not match CRITICAL records")
    if criticality["state_counts"] != critical_counts:
        errors.append("criticality state_counts do not match CRITICAL records")

    expected_lists = {
        "unresolved_refuted_ids": sorted(
            row["obligation_id"] for row in critical_rows if row["state"] == "REFUTED"
        ),
        "unresolved_unknown_ids": sorted(
            row["obligation_id"] for row in critical_rows if row["state"] == "UNKNOWN"
        ),
        "not_applicable_ids": sorted(
            row["obligation_id"]
            for row in critical_rows
            if row["state"] == "NOT_APPLICABLE"
        ),
        "waiver_ids": sorted(
            row["obligation_id"] for row in critical_rows if row["state"] == "WAIVER"
        ),
    }
    for key, expected in expected_lists.items():
        if criticality[key] != expected:
            errors.append(f"criticality {key} does not match CRITICAL records")

    if value["authority_boundaries"] != BOUNDARIES:
        errors.append("verdict projection authority boundaries do not match fixed contract")
    return errors


def validate_projection_shape(
    value: Any,
    label: str = "verdict-projection",
) -> list[str]:
    errors = schema_validate("verdict-projection", value, label)
    if errors:
        return errors
    return [f"{label}: {error}" for error in projection_semantic_errors(value)]


def validate_projection(
    projection: Any,
    source: Any | None = None,
    repo_root: Path | None = None,
    label: str = "verdict-projection",
) -> list[str]:
    errors = validate_projection_shape(projection, label)
    if errors:
        return errors
    if source is None or repo_root is None:
        return [f"{label}: source-bound verdict replay is required"]
    source_errors = validate_source(source, "verdict-policy-source")
    if source_errors:
        return source_errors
    if projection["source"]["digest"] != canonical_digest(source):
        return [f"{label}: source.digest does not match supplied source"]
    try:
        fresh = derive_projection(source, repo_root)
    except Exception as exc:
        return [f"{label}: fresh verdict replay failed: {exc}"]
    if fresh != projection:
        errors.append(f"{label}: stored projection does not equal fresh verdict replay")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Derive exact-candidate evidence verdicts and criticality facts."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    compile_parser = sub.add_parser("compile")
    compile_parser.add_argument("source")
    compile_parser.add_argument("--repo-root", default=".")
    compile_parser.add_argument("--output")
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("source")
    validate_parser.add_argument("projection")
    validate_parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    source = load_yaml(Path(args.source))
    repo_root = Path(args.repo_root).resolve()
    if args.command == "compile":
        projection = derive_projection(source, repo_root)
        rendered = dump_yaml(projection)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return

    projection = load_yaml(Path(args.projection))
    errors = validate_projection(
        projection,
        source,
        repo_root,
        Path(args.projection).name,
    )
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print(f"OK: verdict policy: {args.source} + {args.projection}")


if __name__ == "__main__":
    main()
