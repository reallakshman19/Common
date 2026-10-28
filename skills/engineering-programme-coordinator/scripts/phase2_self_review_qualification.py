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
    canonical_digest as evidence_source_digest,
    object_digest as evidence_object_digest,
    validate_ledger,
    validate_ledger_shape,
)
from l0_task_obligations import (
    canonical_digest as l0_digest,
    manifest_semantic_errors as l0_manifest_semantic_errors,
    validate_manifest as validate_l0_manifest,
)
from l1_baseline_obligations import (
    canonical_digest as l1_digest,
    manifest_digest as l1_manifest_digest,
    validate_manifest as validate_l1_manifest,
)
from l2_diff_impact import (
    canonical_digest as l2_digest,
    manifest_digest as l2_manifest_digest,
    validate_manifest as validate_l2_manifest,
)
from repair_replay import (
    canonical_digest as repair_source_digest,
    compile_source as compile_repair,
    object_digest as repair_object_digest,
    validate_result as validate_repair_result,
    validate_result_shape as validate_repair_result_shape,
)
from verdict_policy import (
    canonical_digest as verdict_source_digest,
    derive_projection,
    object_digest as verdict_object_digest,
    validate_projection,
    validate_projection_shape,
)

SOURCE_HEADING = "## Precommitted P2-I qualification source"
STAGES = ("P2-S1", "P2-S2", "P2-S3", "P2-S4", "P2-S5", "P2-S6")
CASE_IDS = (
    "CLEAN-RETAINED-REAL-CHAIN",
    "GBW-L0-FROZEN-EXPECTATION-DRIFT",
    "GBW-L1-BASELINE-EXPECTATION-DRIFT",
    "GBW-L2-IMPACT-EXPECTATION-DRIFT",
    "GBW-S4-LEDGER-SEMANTIC-DRIFT",
    "GBW-S5-REPAIR-RESULT-DRIFT",
    "GBW-S6-UNKNOWN-PROMOTION",
)
BOUNDARIES = {
    "consumes_retained_real_artifacts": True,
    "applies_seed_overlays_in_memory_only": True,
    "mutates_retained_artifacts": False,
    "emits_engineering_pass": False,
    "emits_independent_review": False,
    "emits_evidence_gate_decision": False,
    "performs_lifecycle_advance": False,
    "grants_merge_authority": False,
    "grants_production_cutover": False,
}


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def object_digest(value: dict[str, Any], field: str) -> str:
    payload = copy.deepcopy(value)
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


def source_semantic_errors(source: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    cases = source["qualification_cases"]
    ids = [row["id"] for row in cases]
    if tuple(ids) != CASE_IDS:
        errors.append("qualification_cases must equal the frozen P2-I case sequence")
    clean = [row for row in cases if row["kind"] == "CLEAN_CONTROL"]
    seeded = [row for row in cases if row["kind"] == "SEEDED_GREEN_BUT_WRONG"]
    if len(clean) != 1:
        errors.append("exactly one clean control is required")
    if len(seeded) != 6:
        errors.append("exactly six seeded green-but-wrong cases are required")
    if tuple(row["stage"] for row in seeded) != STAGES:
        errors.append("seeded cases must cover P2-S1 through P2-S6 exactly once")
    if source["expected_qualification"]["stages_covered"] != list(STAGES):
        errors.append("expected stages_covered must equal P2-S1 through P2-S6")
    for group in source["retained_artifacts"].values():
        for key, value in group.items():
            if key.endswith("_path"):
                path = Path(value)
                if path.is_absolute() or chr(92) in value or ".." in path.parts:
                    errors.append(f"unsafe retained artifact path: {value}")
    return errors


def validate_source(
    source: Any,
    label: str = "phase2-self-review-qualification-source",
) -> list[str]:
    errors = schema_validate("phase2-self-review-qualification-source", source, label)
    if errors:
        return errors
    return [f"{label}: {error}" for error in source_semantic_errors(source)]


def extract_precommitted_source(markdown: str) -> dict[str, Any]:
    if not isinstance(markdown, str):
        raise ValueError("GitHub issue body must be text")
    if markdown.count(SOURCE_HEADING) != 1:
        raise ValueError("GitHub issue must contain exactly one P2-I qualification source heading")
    tail = markdown.split(SOURCE_HEADING, 1)[1]
    start = tail.find("```yaml")
    if start < 0:
        raise ValueError("Precommitted P2-I source must use a yaml code fence")
    after = tail[start + len("```yaml"):]
    end = after.find("```")
    if end < 0:
        raise ValueError("Precommitted P2-I source code fence is not closed")
    value = yaml.safe_load(after[:end].strip())
    errors = validate_source(value, "github-child-contract-source")
    if errors:
        raise ValueError("; ".join(errors))
    return value


def _load(repo_root: Path, path: str) -> dict[str, Any]:
    return load_yaml(_safe_path(repo_root, path))


def _assert_digest(label: str, actual: str, expected: str) -> None:
    if actual != expected:
        raise ValueError(f"{label}: digest mismatch: {actual} != {expected}")


def _load_retained(source: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    refs = source["retained_artifacts"]
    l0_source = _load(repo_root, refs["l0"]["source_path"])
    l0_manifest = _load(repo_root, refs["l0"]["manifest_path"])
    l1_source = _load(repo_root, refs["l1"]["source_path"])
    l1_manifest = _load(repo_root, refs["l1"]["manifest_path"])
    l2_source = _load(repo_root, refs["l2"]["source_path"])
    l2_manifest = _load(repo_root, refs["l2"]["manifest_path"])
    evidence_source = _load(repo_root, refs["evidence"]["source_path"])
    evidence_ledger = _load(repo_root, refs["evidence"]["ledger_path"])
    repair_source = _load(repo_root, refs["repair"]["source_path"])
    verdict_source = _load(repo_root, refs["verdict"]["source_path"])

    _assert_digest("L0 source", l0_digest(l0_source), refs["l0"]["source_digest"])
    _assert_digest("L0 manifest", l0_manifest["manifest_digest"], refs["l0"]["manifest_digest"])
    _assert_digest("L1 source", l1_digest(l1_source), refs["l1"]["source_digest"])
    _assert_digest("L1 manifest", l1_manifest["manifest_digest"], refs["l1"]["manifest_digest"])
    _assert_digest("L2 source", l2_digest(l2_source), refs["l2"]["source_digest"])
    _assert_digest("L2 manifest", l2_manifest["manifest_digest"], refs["l2"]["manifest_digest"])
    _assert_digest(
        "evidence source",
        evidence_source_digest(evidence_source),
        refs["evidence"]["source_digest"],
    )
    _assert_digest(
        "evidence ledger",
        evidence_ledger["ledger_digest"],
        refs["evidence"]["ledger_digest"],
    )
    _assert_digest(
        "repair source",
        repair_source_digest(repair_source),
        refs["repair"]["source_digest"],
    )
    _assert_digest(
        "verdict source",
        verdict_source_digest(verdict_source),
        refs["verdict"]["source_digest"],
    )
    return {
        "l0_source": l0_source,
        "l0_manifest": l0_manifest,
        "l1_source": l1_source,
        "l1_manifest": l1_manifest,
        "l2_source": l2_source,
        "l2_manifest": l2_manifest,
        "evidence_source": evidence_source,
        "evidence_ledger": evidence_ledger,
        "repair_source": repair_source,
        "verdict_source": verdict_source,
    }


def _clean_replay(
    source: dict[str, Any],
    repo_root: Path,
    retained: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    checks = [
        ("P2-S1", validate_l0_manifest(
            retained["l0_manifest"], retained["l0_source"]
        ), retained["l0_manifest"]["manifest_digest"]),
        ("P2-S2", validate_l1_manifest(
            retained["l1_manifest"], retained["l1_source"], repo_root
        ), retained["l1_manifest"]["manifest_digest"]),
        ("P2-S3", validate_l2_manifest(
            retained["l2_manifest"], retained["l2_source"], repo_root
        ), retained["l2_manifest"]["manifest_digest"]),
        ("P2-S4", validate_ledger(
            retained["evidence_ledger"], retained["evidence_source"], repo_root
        ), retained["evidence_ledger"]["ledger_digest"]),
    ]
    clean: list[dict[str, Any]] = []
    for stage, errors, digest in checks:
        if errors:
            raise ValueError(f"{stage} clean replay failed: {'; '.join(errors)}")
        clean.append({"stage": stage, "replay_clean": True, "artifact_digest": digest})

    repair_result = compile_repair(retained["repair_source"], repo_root)
    repair_errors = validate_repair_result(
        repair_result, retained["repair_source"], repo_root
    )
    if repair_errors:
        raise ValueError("P2-S5 clean replay failed: " + "; ".join(repair_errors))
    _assert_digest(
        "P2-S5 result",
        repair_result["result_digest"],
        source["retained_artifacts"]["repair"]["expected_result_digest"],
    )
    clean.append({
        "stage": "P2-S5",
        "replay_clean": True,
        "artifact_digest": repair_result["result_digest"],
    })

    projection = derive_projection(retained["verdict_source"], repo_root)
    verdict_errors = validate_projection(
        projection, retained["verdict_source"], repo_root
    )
    if verdict_errors:
        raise ValueError("P2-S6 clean replay failed: " + "; ".join(verdict_errors))
    _assert_digest(
        "P2-S6 projection",
        projection["projection_digest"],
        source["retained_artifacts"]["verdict"]["expected_projection_digest"],
    )
    clean.append({
        "stage": "P2-S6",
        "replay_clean": True,
        "artifact_digest": projection["projection_digest"],
    })
    return clean, repair_result, projection


def _mutation_result(
    spec: dict[str, Any],
    shallow_errors: list[str],
    bound_errors: list[str],
) -> dict[str, Any]:
    if shallow_errors:
        raise ValueError(
            f"{spec['id']}: seed is malformed rather than green-but-wrong: "
            + "; ".join(shallow_errors)
        )
    if not bound_errors:
        raise ValueError(f"{spec['id']}: source-bound validator missed seeded mutation")
    return {
        "id": spec["id"],
        "stage": spec["stage"],
        "shallow_green": True,
        "semantic_rejected": True,
        "detector": spec["expected_detector"],
        "rejection_errors": list(bound_errors),
    }


def _mutate_l0(
    spec: dict[str, Any],
    retained: dict[str, Any],
) -> dict[str, Any]:
    value = copy.deepcopy(retained["l0_manifest"])
    value["obligations"][0]["claim"]["statement"] += " [SEEDED_GREEN_BUT_WRONG]"
    payload = copy.deepcopy(value)
    payload.pop("manifest_digest", None)
    value["manifest_digest"] = l0_digest(payload)
    shallow = schema_validate("l0-task-obligation-manifest", value, spec["id"])
    shallow.extend(
        f"{spec['id']}: {error}"
        for error in l0_manifest_semantic_errors(value)
    )
    bound = validate_l0_manifest(value, retained["l0_source"], spec["id"])
    return _mutation_result(spec, shallow, bound)


def _mutate_l1(
    spec: dict[str, Any],
    repo_root: Path,
    retained: dict[str, Any],
) -> dict[str, Any]:
    value = copy.deepcopy(retained["l1_manifest"])
    value["obligations"][0]["claim"]["statement"] += " [SEEDED_GREEN_BUT_WRONG]"
    value["manifest_digest"] = l1_manifest_digest(value)
    shallow = schema_validate("l1-baseline-obligation-manifest", value, spec["id"])
    if value["manifest_digest"] != l1_manifest_digest(value):
        shallow.append(f"{spec['id']}: self digest mismatch")
    bound = validate_l1_manifest(
        value, retained["l1_source"], repo_root, spec["id"]
    )
    return _mutation_result(spec, shallow, bound)


def _mutate_l2(
    spec: dict[str, Any],
    repo_root: Path,
    retained: dict[str, Any],
) -> dict[str, Any]:
    value = copy.deepcopy(retained["l2_manifest"])
    value["obligations"][0]["claim"]["statement"] += " [SEEDED_GREEN_BUT_WRONG]"
    value["manifest_digest"] = l2_manifest_digest(value)
    shallow = schema_validate("l2-impact-obligation-manifest", value, spec["id"])
    if value["manifest_digest"] != l2_manifest_digest(value):
        shallow.append(f"{spec['id']}: self digest mismatch")
    bound = validate_l2_manifest(
        value, retained["l2_source"], repo_root, spec["id"]
    )
    return _mutation_result(spec, shallow, bound)


def _mutate_s4(
    spec: dict[str, Any],
    repo_root: Path,
    retained: dict[str, Any],
) -> dict[str, Any]:
    value = copy.deepcopy(retained["evidence_ledger"])
    first = value["records"][0]
    first["claim_type"] = (
        "BEHAVIOR" if first["claim_type"] != "BEHAVIOR" else "INVARIANT"
    )
    value["ledger_digest"] = evidence_object_digest(value, "ledger_digest")
    shallow = validate_ledger_shape(value, spec["id"])
    bound = validate_ledger(
        value, retained["evidence_source"], repo_root, spec["id"]
    )
    return _mutation_result(spec, shallow, bound)


def _mutate_s5(
    spec: dict[str, Any],
    repo_root: Path,
    retained: dict[str, Any],
    clean_result: dict[str, Any],
) -> dict[str, Any]:
    value = copy.deepcopy(clean_result)
    value["repair_delta"]["changes"][0]["path"] += ".seeded-wrong"
    value["result_digest"] = repair_object_digest(value, "result_digest")
    shallow = validate_repair_result_shape(value, spec["id"])
    bound = validate_repair_result(
        value, retained["repair_source"], repo_root, spec["id"]
    )
    return _mutation_result(spec, shallow, bound)


def _mutate_s6(
    spec: dict[str, Any],
    repo_root: Path,
    retained: dict[str, Any],
    clean_projection: dict[str, Any],
) -> dict[str, Any]:
    value = copy.deepcopy(clean_projection)
    row = next(
        record for record in value["records"]
        if record["severity"] == "CRITICAL" and record["state"] == "UNKNOWN"
    )
    row["state"] = "VERIFIED"
    for requirement in row["requirements"]:
        requirement["state"] = "VERIFIED"
    value["accounting"]["state_counts"]["UNKNOWN"] -= 1
    value["accounting"]["state_counts"]["VERIFIED"] += 1
    value["criticality"]["state_counts"]["UNKNOWN"] -= 1
    value["criticality"]["state_counts"]["VERIFIED"] += 1
    value["criticality"]["unresolved_unknown_ids"].remove(row["obligation_id"])
    value["projection_digest"] = verdict_object_digest(value, "projection_digest")
    shallow = validate_projection_shape(value, spec["id"])
    bound = validate_projection(
        value, retained["verdict_source"], repo_root, spec["id"]
    )
    return _mutation_result(spec, shallow, bound)


def compile_source(source: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    errors = validate_source(source)
    if errors:
        raise ValueError("; ".join(errors))
    retained = _load_retained(source, repo_root)
    clean, repair_result, projection = _clean_replay(source, repo_root, retained)
    specs = {
        row["stage"]: row
        for row in source["qualification_cases"]
        if row["kind"] == "SEEDED_GREEN_BUT_WRONG"
    }
    mutations = [
        _mutate_l0(specs["P2-S1"], retained),
        _mutate_l1(specs["P2-S2"], repo_root, retained),
        _mutate_l2(specs["P2-S3"], repo_root, retained),
        _mutate_s4(specs["P2-S4"], repo_root, retained),
        _mutate_s5(specs["P2-S5"], repo_root, retained, repair_result),
        _mutate_s6(specs["P2-S6"], repo_root, retained, projection),
    ]
    result = {
        "schema_version": "PHASE2_SELF_REVIEW_QUALIFICATION_RESULT_V1",
        "authority": "PHASE2_SELF_REVIEW_QUALIFICATION_EVIDENCE",
        "identity": copy.deepcopy(source["identity"]),
        "source": {"digest": canonical_digest(source)},
        "target": copy.deepcopy(source["target"]),
        "historical_lanes": {
            "pr522_stages": ["P2-S1", "P2-S2", "P2-S3", "P2-S4", "P2-S6"],
            "pr565_stages": ["P2-S5"],
            "monolithic_synthetic_candidate": False,
        },
        "clean_replay": clean,
        "mutation_cases": mutations,
        "accounting": {
            "clean_controls": 1,
            "clean_false_blocks": 0,
            "seeded_green_but_wrong": len(mutations),
            "seeded_detected": sum(row["semantic_rejected"] for row in mutations),
            "seeded_missed": sum(not row["semantic_rejected"] for row in mutations),
            "shallow_green_seeded": sum(row["shallow_green"] for row in mutations),
        },
        "qualification_status": "QUALIFIED",
        "authority_boundaries": copy.deepcopy(BOUNDARIES),
    }
    result["result_digest"] = object_digest(result, "result_digest")
    shape = validate_result_shape(result, "compiled-phase2-qualification")
    if shape:
        raise ValueError("; ".join(shape))
    return result


def result_semantic_errors(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value["result_digest"] != object_digest(value, "result_digest"):
        errors.append("result_digest does not match canonical content")
    if tuple(row["stage"] for row in value["clean_replay"]) != STAGES:
        errors.append("clean replay must cover P2-S1 through P2-S6 in order")
    mutation_ids = tuple(row["id"] for row in value["mutation_cases"])
    if mutation_ids != CASE_IDS[1:]:
        errors.append("mutation cases must equal frozen P2-I seeded case sequence")
    accounting = value["accounting"]
    qualified = (
        len(value["clean_replay"]) == 6
        and all(row["replay_clean"] for row in value["clean_replay"])
        and len(value["mutation_cases"]) == 6
        and all(row["shallow_green"] for row in value["mutation_cases"])
        and all(row["semantic_rejected"] for row in value["mutation_cases"])
        and accounting["clean_false_blocks"] == 0
        and accounting["seeded_missed"] == 0
        and accounting["seeded_detected"] == 6
        and accounting["shallow_green_seeded"] == 6
    )
    expected_status = "QUALIFIED" if qualified else "FAILED"
    if value["qualification_status"] != expected_status:
        errors.append("qualification_status does not match observed qualification facts")
    if value["authority_boundaries"] != BOUNDARIES:
        errors.append("qualification authority boundaries do not match fixed contract")
    return errors


def validate_result_shape(
    value: Any,
    label: str = "phase2-self-review-qualification-result",
) -> list[str]:
    errors = schema_validate("phase2-self-review-qualification-result", value, label)
    if errors:
        return errors
    return [f"{label}: {error}" for error in result_semantic_errors(value)]


def validate_result(
    result: Any,
    source: Any | None = None,
    repo_root: Path | None = None,
    label: str = "phase2-self-review-qualification-result",
) -> list[str]:
    errors = validate_result_shape(result, label)
    if errors:
        return errors
    if source is None or repo_root is None:
        return [f"{label}: source-bound Phase-2 qualification replay is required"]
    source_errors = validate_source(source, "phase2-qualification-source")
    if source_errors:
        return source_errors
    if result["source"]["digest"] != canonical_digest(source):
        return [f"{label}: source.digest does not match supplied source"]
    try:
        fresh = compile_source(source, repo_root)
    except Exception as exc:
        return [f"{label}: fresh qualification replay failed: {exc}"]
    if fresh != result:
        errors.append(f"{label}: stored result does not equal fresh qualification replay")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Qualify the Phase-2 self-review stack against retained real artifacts and seeded semantic mutations."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    compile_parser = sub.add_parser("compile")
    compile_parser.add_argument("source")
    compile_parser.add_argument("--repo-root", default=".")
    compile_parser.add_argument("--output")
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("source")
    validate_parser.add_argument("result")
    validate_parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    source = load_yaml(Path(args.source))
    repo_root = Path(args.repo_root).resolve()
    if args.command == "compile":
        result = compile_source(source, repo_root)
        rendered = dump_yaml(result)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return
    result = load_yaml(Path(args.result))
    errors = validate_result(result, source, repo_root, Path(args.result).name)
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print(f"OK: Phase-2 self-review qualification: {args.source} + {args.result}")


if __name__ == "__main__":
    main()
