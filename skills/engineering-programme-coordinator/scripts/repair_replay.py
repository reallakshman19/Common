#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import yaml

from coordlib import dump_yaml, load_yaml, validate as schema_validate
from exact_candidate_evidence import compile_source as compile_evidence_ledger
from l2_diff_impact import compile_source as compile_l2

SOURCE_HEADING = "## Precommitted repair-replay source"
BOUNDARIES = {
    "consumes_repair_lineage": True,
    "consumes_prior_candidate_evidence": True,
    "performs_repair_invalidation": True,
    "replays_final_candidate": True,
    "assigns_evidence_verdict": False,
    "applies_criticality_policy": False,
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
    if path.is_absolute() or "\\" in value or ".." in path.parts:
        raise ValueError(f"unsafe repository path: {value}")
    resolved = (repo_root / path).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"repository path escapes root: {value}") from exc
    return resolved


def _git(repo_root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _require_commit(repo_root: Path, sha: str, label: str) -> None:
    result = _git(repo_root, "cat-file", "-e", f"{sha}^{{commit}}", check=False)
    if result.returncode != 0:
        raise ValueError(f"{label} Git commit is unavailable: {sha}")


def _is_ancestor(repo_root: Path, ancestor: str, descendant: str) -> bool:
    return _git(
        repo_root,
        "merge-base",
        "--is-ancestor",
        ancestor,
        descendant,
        check=False,
    ).returncode == 0


def source_semantic_errors(source: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    lineage = source["candidate_lineage"]
    if lineage["initial_sha"] == lineage["final_sha"]:
        errors.append("initial_sha and final_sha must differ")
    ids = [row["evidence_id"] for row in source["prior_evidence"]]
    if len(ids) != len(set(ids)):
        errors.append("prior evidence ids must be globally unique")
    for row in source["prior_evidence"]:
        if row["candidate_sha"] != lineage["initial_sha"]:
            errors.append(
                f"{row['evidence_id']}: prior evidence candidate_sha must equal initial_sha"
            )
    paths = [
        source["templates"]["l2_source"]["path"],
        source["templates"]["l0_manifest"]["path"],
        source["templates"]["l1_manifest"]["path"],
    ]
    if len(paths) != len(set(paths)):
        errors.append("template paths must be distinct")
    for value in paths:
        if Path(value).is_absolute() or "\\" in value or ".." in Path(value).parts:
            errors.append(f"unsafe template path: {value}")
    expected = source["expected_transition"]
    if expected["prior_evidence_invalidated"] != len(source["prior_evidence"]):
        errors.append("expected prior_evidence_invalidated must equal prior evidence count")
    return errors


def validate_source(source: Any, label: str = "repair-replay-source") -> list[str]:
    errors = schema_validate("repair-replay-source", source, label)
    if errors:
        return errors
    return [f"{label}: {error}" for error in source_semantic_errors(source)]


def extract_precommitted_source(markdown: str) -> dict[str, Any]:
    if not isinstance(markdown, str):
        raise ValueError("GitHub issue body must be text")
    if markdown.count(SOURCE_HEADING) != 1:
        raise ValueError("GitHub issue must contain exactly one repair-replay source heading")
    tail = markdown.split(SOURCE_HEADING, 1)[1]
    start = tail.find("```yaml")
    if start < 0:
        raise ValueError("Precommitted repair-replay source must use a yaml code fence")
    after = tail[start + len("```yaml"):]
    end = after.find("```")
    if end < 0:
        raise ValueError("Precommitted repair-replay source code fence is not closed")
    value = yaml.safe_load(after[:end].strip())
    errors = validate_source(value, "github-child-contract-source")
    if errors:
        raise ValueError("; ".join(errors))
    return value


def _load_digest_bound_yaml(
    repo_root: Path,
    ref: dict[str, Any],
    label: str,
) -> dict[str, Any]:
    path = _safe_path(repo_root, ref["path"])
    value = load_yaml(path)
    if canonical_digest(value) != ref["digest"]:
        raise ValueError(f"{label}: canonical digest does not match source declaration")
    return value


def _l2_source(
    template: dict[str, Any],
    source: dict[str, Any],
    head_kind: str,
) -> dict[str, Any]:
    lineage = source["candidate_lineage"]
    head_ref = lineage[f"{head_kind}_ref"]
    head_sha = lineage[f"{head_kind}_sha"]
    value = copy.deepcopy(template)
    value["identity"] = dict(source["identity"])
    value["candidate"] = {
        "repository": lineage["repository"],
        "pr_number": lineage["pr_number"],
        "base_ref": lineage["base_ref"],
        "base_sha": lineage["base_sha"],
        "head_ref": head_ref,
        "head_sha": head_sha,
        "diff_mode": lineage["diff_mode"],
    }
    return value


def _repair_delta_source(
    template: dict[str, Any],
    source: dict[str, Any],
) -> dict[str, Any]:
    lineage = source["candidate_lineage"]
    value = copy.deepcopy(template)
    value["identity"] = dict(source["identity"])
    value["candidate"] = {
        "repository": lineage["repository"],
        "pr_number": lineage["pr_number"],
        "base_ref": lineage["initial_ref"],
        "base_sha": lineage["initial_sha"],
        "head_ref": lineage["final_ref"],
        "head_sha": lineage["final_sha"],
        "diff_mode": lineage["diff_mode"],
    }
    return value


def _summary(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_sha": manifest["candidate"]["head_sha"],
        "manifest_digest": manifest["manifest_digest"],
        "changed_path_count": manifest["diff"]["changed_path_count"],
        "changed_paths_digest": manifest["diff"]["changed_paths_digest"],
        "obligation_ids": sorted(row["id"] for row in manifest["obligations"]),
    }


def _copy_manifest(repo_root: Path, temp_root: Path, ref: dict[str, Any]) -> None:
    source_path = _safe_path(repo_root, ref["path"])
    target = temp_root / ref["path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, target)


def _final_ledger(
    source: dict[str, Any],
    final_l2: dict[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    lineage = source["candidate_lineage"]
    with tempfile.TemporaryDirectory() as td:
        temp_root = Path(td)
        _copy_manifest(repo_root, temp_root, source["templates"]["l0_manifest"])
        _copy_manifest(repo_root, temp_root, source["templates"]["l1_manifest"])
        l2_path = (
            "generated/p2-s5-final-l2-manifest.yaml"
        )
        target = temp_root / l2_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(dump_yaml(final_l2), encoding="utf-8")
        evidence_source = {
            "schema_version": "EXACT_CANDIDATE_EVIDENCE_SOURCE_V1",
            "authority": "CLOSED_DENOMINATOR_EVIDENCE_INPUT",
            "identity": dict(source["identity"]),
            "candidate": {
                "repository": lineage["repository"],
                "pr_number": lineage["pr_number"],
                "ref": lineage["final_ref"],
                "sha": lineage["final_sha"],
            },
            "manifests": {
                "l0": dict(source["templates"]["l0_manifest"]),
                "l1": dict(source["templates"]["l1_manifest"]),
                "l2": {
                    "path": l2_path,
                    "digest": final_l2["manifest_digest"],
                },
            },
            "evidence_items": [],
            "forbidden_outcomes": [
                "prior candidate evidence is carried into final replay",
                "missing final evidence is dropped from denominator accounting",
                "repair replay assigns evidence verdict semantics",
            ],
            "non_goals": list(source["non_goals"]),
        }
        return compile_evidence_ledger(evidence_source, temp_root)


def compile_source(source: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    errors = validate_source(source)
    if errors:
        raise ValueError("; ".join(errors))
    lineage = source["candidate_lineage"]
    for label in ("base", "initial", "final"):
        _require_commit(repo_root, lineage[f"{label}_sha"], label)
    if not _is_ancestor(repo_root, lineage["base_sha"], lineage["initial_sha"]):
        raise ValueError("base_sha must be an ancestor of initial_sha")
    if not _is_ancestor(repo_root, lineage["initial_sha"], lineage["final_sha"]):
        raise ValueError("initial_sha must be an ancestor of final_sha")
    template = _load_digest_bound_yaml(
        repo_root,
        source["templates"]["l2_source"],
        "l2 source template",
    )
    initial_l2 = compile_l2(_l2_source(template, source, "initial"), repo_root)
    final_l2 = compile_l2(_l2_source(template, source, "final"), repo_root)
    repair_manifest = compile_l2(_repair_delta_source(template, source), repo_root)
    repair_changes = [
        dict(row["diff_observation"])
        for row in repair_manifest["obligations"]
    ]
    repair_changes.sort(key=lambda row: (row["path"], row["status"]))
    expected = source["expected_transition"]
    if [row["path"] for row in repair_changes] != sorted(expected["repair_changed_paths"]):
        raise ValueError("repair changed paths do not match precommitted transition")
    if final_l2["diff"]["changed_path_count"] != expected["final_changed_path_count"]:
        raise ValueError("final changed path count does not match precommitted transition")
    if len(final_l2["obligations"]) != expected["final_l2_obligation_count"]:
        raise ValueError("final L2 obligation count does not match precommitted transition")
    final_ledger = _final_ledger(source, final_l2, repo_root)
    if final_ledger["denominator"]["obligation_count"] != expected["final_closed_obligation_count"]:
        raise ValueError("final closed obligation count does not match precommitted transition")
    if final_ledger["denominator"]["requirement_count"] != expected["final_closed_requirement_count"]:
        raise ValueError("final closed requirement count does not match precommitted transition")
    if final_ledger["accounting"]["evidence_item_count"] != 0:
        raise ValueError("final replay must carry zero prior evidence items")
    invalidated = sorted(row["evidence_id"] for row in source["prior_evidence"])
    if len(invalidated) != expected["prior_evidence_invalidated"]:
        raise ValueError("invalidated prior evidence count does not match precommitted transition")
    if expected["carried_prior_evidence"] != 0:
        raise ValueError("P2-S5 permits no prior evidence carry-forward")
    initial_summary = _summary(initial_l2)
    final_summary = _summary(final_l2)
    result = {
        "schema_version": "REPAIR_REPLAY_RESULT_V1",
        "authority": "EXACT_REPAIR_REPLAY_PROJECTION",
        "identity": dict(source["identity"]),
        "source": {"digest": canonical_digest(source)},
        "candidate_lineage": {
            "repository": lineage["repository"],
            "pr_number": lineage["pr_number"],
            "base_sha": lineage["base_sha"],
            "initial_sha": lineage["initial_sha"],
            "final_sha": lineage["final_sha"],
        },
        "repair_delta": {
            "changed_path_count": len(repair_changes),
            "changed_paths_digest": canonical_digest(repair_changes),
            "changes": repair_changes,
        },
        "invalidation": {
            "reason": "CANDIDATE_CHANGED",
            "invalidated_evidence_ids": invalidated,
            "carried_prior_evidence_ids": [],
            "invalidated_count": len(invalidated),
            "carried_count": 0,
        },
        "initial_l2": initial_summary,
        "final_l2": final_summary,
        "final_ledger": {
            "ledger_digest": final_ledger["ledger_digest"],
            "obligation_count": final_ledger["denominator"]["obligation_count"],
            "requirement_count": final_ledger["denominator"]["requirement_count"],
            "requirements_with_evidence": final_ledger["accounting"]["requirements_with_evidence"],
            "requirements_without_evidence": final_ledger["accounting"]["requirements_without_evidence"],
            "evidence_item_count": final_ledger["accounting"]["evidence_item_count"],
        },
        "assertions": {
            "candidate_changed": True,
            "repair_descendant": True,
            "initial_final_changed_paths_equal": (
                initial_summary["changed_paths_digest"]
                == final_summary["changed_paths_digest"]
            ),
            "initial_final_obligation_ids_equal": (
                initial_summary["obligation_ids"]
                == final_summary["obligation_ids"]
            ),
            "initial_final_manifest_digest_differs": (
                initial_summary["manifest_digest"]
                != final_summary["manifest_digest"]
            ),
            "final_candidate_exact": final_summary["candidate_sha"] == lineage["final_sha"],
            "no_prior_evidence_carried": True,
        },
        "authority_boundaries": dict(BOUNDARIES),
    }
    result["result_digest"] = object_digest(result, "result_digest")
    result_errors = validate_result_shape(result, "compiled-repair-replay")
    if result_errors:
        raise ValueError("; ".join(result_errors))
    return result


def result_semantic_errors(result: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if result["result_digest"] != object_digest(result, "result_digest"):
        errors.append("result_digest does not match canonical result content")
    lineage = result["candidate_lineage"]
    if lineage["initial_sha"] == lineage["final_sha"]:
        errors.append("result candidate lineage must show a changed candidate")
    invalidation = result["invalidation"]
    if invalidation["invalidated_count"] != len(invalidation["invalidated_evidence_ids"]):
        errors.append("invalidated_count must equal invalidated evidence id count")
    if invalidation["carried_count"] != len(invalidation["carried_prior_evidence_ids"]):
        errors.append("carried_count must equal carried prior evidence id count")
    if invalidation["carried_prior_evidence_ids"]:
        errors.append("P2-S5 final replay cannot carry prior candidate evidence")
    if set(invalidation["invalidated_evidence_ids"]) & set(invalidation["carried_prior_evidence_ids"]):
        errors.append("evidence cannot be both invalidated and carried")
    if result["final_l2"]["candidate_sha"] != lineage["final_sha"]:
        errors.append("final L2 replay must bind exact final candidate")
    if result["final_ledger"]["evidence_item_count"] != 0:
        errors.append("final ledger must contain zero carried prior evidence items")
    if (
        result["final_ledger"]["requirement_count"]
        != result["final_ledger"]["requirements_without_evidence"]
    ):
        errors.append("zero-evidence final replay must retain every requirement without evidence")
    if result["authority_boundaries"] != BOUNDARIES:
        errors.append("repair replay authority boundaries do not match fixed contract")
    return errors


def validate_result_shape(
    value: Any,
    label: str = "repair-replay-result",
) -> list[str]:
    errors = schema_validate("repair-replay-result", value, label)
    if errors:
        return errors
    return [f"{label}: {error}" for error in result_semantic_errors(value)]


def validate_result(
    result: Any,
    source: Any | None = None,
    repo_root: Path | None = None,
    label: str = "repair-replay-result",
) -> list[str]:
    errors = validate_result_shape(result, label)
    if errors:
        return errors
    if source is None or repo_root is None:
        return [f"{label}: source-bound exact-object replay is required"]
    source_errors = validate_source(source, "repair-replay-source")
    if source_errors:
        return source_errors
    if result["source"]["digest"] != canonical_digest(source):
        return [f"{label}: source.digest does not match supplied source"]
    try:
        fresh = compile_source(source, repo_root)
    except Exception as exc:
        return [f"{label}: fresh repair replay failed: {exc}"]
    if fresh != result:
        errors.append(f"{label}: stored result does not equal fresh exact-object replay")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Invalidate old exact-candidate evidence and replay repaired final candidate."
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
    print(f"OK: repair replay: {args.source} + {args.result}")


if __name__ == "__main__":
    main()
