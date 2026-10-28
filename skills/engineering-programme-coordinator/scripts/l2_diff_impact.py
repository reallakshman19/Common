#!/usr/bin/env python3
from __future__ import annotations
import argparse
import fnmatch
import hashlib
import json
import posixpath
import subprocess
from pathlib import Path
from typing import Any
import yaml
from coordlib import dump_yaml, load_yaml, validate as schema_validate
SOURCE_HEADING = "## Precommitted L2 impact source"
SUPPORTED_STATUSES = {"A", "D", "M", "T"}
def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()
def manifest_digest(manifest: dict[str, Any]) -> str:
    payload = dict(manifest)
    payload.pop("manifest_digest", None)
    return canonical_digest(payload)
def _safe_repo_pattern(pattern: str) -> bool:
    if not pattern or pattern.startswith("/") or "\\" in pattern:
        return False
    parts = pattern.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return False
    normalized = posixpath.normpath(pattern)
    return normalized == pattern
def source_semantic_errors(source: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    candidate = source["candidate"]
    if candidate["base_sha"] == candidate["head_sha"]:
        errors.append("candidate base_sha and head_sha must differ")
    rule_ids = [rule["id"] for rule in source["rules"]]
    duplicates = sorted({rid for rid in rule_ids if rule_ids.count(rid) > 1})
    if duplicates:
        errors.append("rule ids must be globally unique: " + ", ".join(duplicates))
    prefixes = [
        rule["evidence_requirement"]["id_prefix"]
        for rule in source["rules"]
    ]
    prefixes.append(source["unknown_policy"]["evidence_requirement"]["id_prefix"])
    duplicate_prefixes = sorted({
        prefix for prefix in prefixes if prefixes.count(prefix) > 1
    })
    if duplicate_prefixes:
        errors.append(
            "evidence requirement id prefixes must be globally unique: "
            + ", ".join(duplicate_prefixes)
        )
    for rule in source["rules"]:
        if not _safe_repo_pattern(rule["path_glob"]):
            errors.append(f"{rule['id']}: unsafe path_glob")
    return errors
def validate_source(
    source: Any,
    label: str = "l2-impact-source",
) -> list[str]:
    errors = schema_validate("l2-impact-source", source, label)
    if errors:
        return errors
    return [
        f"{label}: {error}"
        for error in source_semantic_errors(source)
    ]
def extract_precommitted_source(markdown: str) -> dict[str, Any]:
    if not isinstance(markdown, str):
        raise ValueError("GitHub issue body must be text")
    if markdown.count(SOURCE_HEADING) != 1:
        raise ValueError(
            "GitHub issue must contain exactly one precommitted L2 source heading"
        )
    tail = markdown.split(SOURCE_HEADING, 1)[1]
    start = tail.find("```yaml")
    if start < 0:
        raise ValueError("Precommitted L2 source must use a yaml code fence")
    after = tail[start + len("```yaml"):]
    end = after.find("```")
    if end < 0:
        raise ValueError("Precommitted L2 source code fence is not closed")
    payload = after[:end].strip()
    try:
        value = yaml.safe_load(payload)
    except yaml.YAMLError as exc:
        raise ValueError(
            f"Precommitted L2 source is invalid YAML: {exc}"
        ) from exc
    errors = validate_source(value, "github-child-contract-source")
    if errors:
        raise ValueError("; ".join(errors))
    return value
def _git(
    repo_root: Path,
    *args: str,
    binary: bool = False,
) -> str | bytes:
    process = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=not binary,
    )
    if process.returncode != 0:
        stderr = process.stderr
        stdout = process.stdout
        if binary:
            stderr = stderr.decode("utf-8", errors="replace")
            stdout = stdout.decode("utf-8", errors="replace")
        raise ValueError((stderr or stdout or "git command failed").strip())
    return process.stdout
def _assert_exact_commit(repo_root: Path, sha: str) -> None:
    resolved = str(_git(repo_root, "rev-parse", f"{sha}^{{commit}}")).strip()
    if resolved != sha:
        raise ValueError(
            f"declared commit resolved to {resolved}, expected {sha}"
        )
def exact_changed_paths(
    source: dict[str, Any],
    repo_root: Path,
) -> list[dict[str, str]]:
    candidate = source["candidate"]
    base_sha = candidate["base_sha"]
    head_sha = candidate["head_sha"]
    _assert_exact_commit(repo_root, base_sha)
    _assert_exact_commit(repo_root, head_sha)
    raw = _git(
        repo_root,
        "diff",
        "--name-status",
        "-z",
        "--no-renames",
        base_sha,
        head_sha,
        "--",
        binary=True,
    )
    assert isinstance(raw, bytes)
    parts = raw.split(b"\0")
    if parts and parts[-1] == b"":
        parts.pop()
    if len(parts) % 2:
        raise ValueError("unexpected git --name-status -z field count")
    changes: list[dict[str, str]] = []
    for index in range(0, len(parts), 2):
        try:
            status = parts[index].decode("utf-8")
            path = parts[index + 1].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("candidate diff contains non-UTF-8 path data") from exc
        if not status or not path:
            raise ValueError("candidate diff contains empty status/path field")
        if path.startswith("/") or "\\" in path or ".." in path.split("/"):
            raise ValueError(f"candidate diff contains unsafe path: {path}")
        changes.append({"status": status, "path": path})
    changes.sort(key=lambda row: (row["path"], row["status"]))
    paths = [row["path"] for row in changes]
    if len(paths) != len(set(paths)):
        raise ValueError(
            "NO_RENAMES_PATH_SET requires exactly one diff row per changed path"
        )
    return changes
def _path_token(path: str) -> str:
    return hashlib.sha256(path.encode("utf-8")).hexdigest()[:12].upper()
def _oracle(source: dict[str, Any], path: str) -> str:
    candidate = source["candidate"]
    return (
        f"git-diff://{candidate['base_sha']}..{candidate['head_sha']}/{path}"
    )
def compile_changes(
    source: dict[str, Any],
    changes: list[dict[str, str]],
) -> list[dict[str, Any]]:
    obligations: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for change in sorted(changes, key=lambda row: (row["path"], row["status"])):
        path = change["path"]
        status = change["status"]
        if path in seen_paths:
            raise ValueError(f"duplicate changed path: {path}")
        seen_paths.add(path)
        matches = [
            rule
            for rule in source["rules"]
            if fnmatch.fnmatchcase(path, rule["path_glob"])
        ]
        matched_rule_ids = sorted(rule["id"] for rule in matches)
        unknown_reason: str | None = None
        if status not in SUPPORTED_STATUSES:
            classification = "UNKNOWN_STATUS"
            unknown_reason = f"Unsupported diff status {status}"
        elif not matches:
            classification = "UNKNOWN_UNMAPPED"
            unknown_reason = "No precommitted impact rule matched the changed path"
        elif len(matches) > 1:
            classification = "UNKNOWN_AMBIGUOUS"
            unknown_reason = (
                "Multiple precommitted impact rules matched the changed path"
            )
        else:
            classification = "KNOWN"
        token = _path_token(path)
        oracle = _oracle(source, path)
        if classification == "KNOWN":
            rule = matches[0]
            severity = rule["severity"]
            statement = rule["impact_statement"]
            expected = rule["expected_observation"]
            green_but_wrong = rule["plausible_green_but_wrong"]
            requirement_template = rule["evidence_requirement"]
        else:
            policy = source["unknown_policy"]
            severity = policy["severity"]
            statement = (
                f"Impact for changed path {path} is UNKNOWN: {unknown_reason}."
            )
            expected = policy["expected_observation"]
            green_but_wrong = policy["plausible_green_but_wrong"]
            requirement_template = policy["evidence_requirement"]
        requirement_id = (
            f"{requirement_template['id_prefix']}-{token}"
        )
        candidate = source["candidate"]
        obligations.append({
            "id": f"L2-IMPACT-{token}",
            "severity": severity,
            "claim": {
                "type": "IMPACT",
                "statement": statement,
                "subject_refs": [path],
            },
            "expected_observation": expected,
            "plausible_green_but_wrong": green_but_wrong,
            "oracle_refs": [oracle],
            "evidence_required": {
                "id": requirement_id,
                "method": requirement_template["method"],
                "independence": "IMPACT_DERIVED",
                "oracle_ref": oracle,
            },
            "source_refs": [
                "git-diff:"
                f"{candidate['base_sha']}..{candidate['head_sha']}:"
                f"{status}:{path}"
            ],
            "impact_classification": classification,
            "matched_rule_ids": matched_rule_ids,
            "unknown_reason": unknown_reason,
            "diff_observation": {
                "status": status,
                "path": path,
            },
        })
    return obligations
def _validate_manifest_semantics(
    manifest: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if manifest["manifest_digest"] != manifest_digest(manifest):
        errors.append(
            "manifest_digest does not match canonical manifest content"
        )
    obligations = manifest["obligations"]
    if manifest["diff"]["changed_path_count"] != len(obligations):
        errors.append(
            "diff.changed_path_count must equal obligation count"
        )
    changes = [
        obligation["diff_observation"]
        for obligation in obligations
    ]
    expected_diff_digest = canonical_digest(
        sorted(changes, key=lambda row: (row["path"], row["status"]))
    )
    if manifest["diff"]["changed_paths_digest"] != expected_diff_digest:
        errors.append("changed_paths_digest does not match obligation diff rows")
    obligation_ids = [row["id"] for row in obligations]
    if len(obligation_ids) != len(set(obligation_ids)):
        errors.append("L2 obligation ids must be globally unique")
    requirement_ids = [
        row["evidence_required"]["id"]
        for row in obligations
    ]
    if len(requirement_ids) != len(set(requirement_ids)):
        errors.append("L2 evidence requirement ids must be globally unique")
    paths = [row["diff_observation"]["path"] for row in obligations]
    if len(paths) != len(set(paths)):
        errors.append("each changed path must appear exactly once")
    for row in obligations:
        oid = row["id"]
        if row["evidence_required"]["independence"] != "IMPACT_DERIVED":
            errors.append(
                f"{oid}: L2 evidence requirement must be IMPACT_DERIVED"
            )
        classification = row["impact_classification"]
        matched = row["matched_rule_ids"]
        reason = row["unknown_reason"]
        if classification == "KNOWN":
            if len(matched) != 1 or reason is not None:
                errors.append(
                    f"{oid}: KNOWN requires one matched rule and null unknown_reason"
                )
        elif classification == "UNKNOWN_UNMAPPED":
            if matched or not reason:
                errors.append(
                    f"{oid}: UNKNOWN_UNMAPPED requires no matched rule and a reason"
                )
        elif classification == "UNKNOWN_AMBIGUOUS":
            if len(matched) < 2 or not reason:
                errors.append(
                    f"{oid}: UNKNOWN_AMBIGUOUS requires multiple matched rules and a reason"
                )
        elif classification == "UNKNOWN_STATUS":
            if not reason:
                errors.append(
                    f"{oid}: UNKNOWN_STATUS requires a reason"
                )
    expected_boundaries = {
        "consumes_candidate_diff": True,
        "consumes_implementation_evidence": False,
        "consumes_coder_rationale": False,
        "consumes_reviewer_verdict": False,
        "emits_engineering_pass": False,
        "performs_lifecycle_advance": False,
        "grants_merge_authority": False,
        "grants_production_cutover": False,
    }
    if manifest["authority_boundaries"] != expected_boundaries:
        errors.append("L2 authority boundaries do not match the fixed contract")
    return errors
def validate_manifest_shape(
    manifest: Any,
    label: str = "l2-impact-obligation-manifest",
) -> list[str]:
    errors = schema_validate(
        "l2-impact-obligation-manifest",
        manifest,
        label,
    )
    if errors:
        return errors
    return [
        f"{label}: {error}"
        for error in _validate_manifest_semantics(manifest)
    ]
def compile_source(
    source: dict[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    errors = validate_source(source)
    if errors:
        raise ValueError("; ".join(errors))
    changes = exact_changed_paths(source, repo_root)
    obligations = compile_changes(source, changes)
    output = {
        "schema_version": "L2_IMPACT_OBLIGATION_MANIFEST_V1",
        "authority": "DIFF_DERIVED_IMPACT_EXPECTATIONS",
        "identity": dict(source["identity"]),
        "source": {
            "kind": "CANDIDATE_DIFF_SELECTION_CONTRACT",
            "digest": canonical_digest(source),
        },
        "candidate": dict(source["candidate"]),
        "diff": {
            "changed_path_count": len(changes),
            "changed_paths_digest": canonical_digest(changes),
        },
        "obligations": obligations,
        "forbidden_outcomes": list(source["forbidden_outcomes"]),
        "non_goals": list(source["non_goals"]),
        "authority_boundaries": {
            "consumes_candidate_diff": True,
            "consumes_implementation_evidence": False,
            "consumes_coder_rationale": False,
            "consumes_reviewer_verdict": False,
            "emits_engineering_pass": False,
            "performs_lifecycle_advance": False,
            "grants_merge_authority": False,
            "grants_production_cutover": False,
        },
    }
    output["manifest_digest"] = manifest_digest(output)
    errors = validate_manifest_shape(output, "compiled-l2-manifest")
    if errors:
        raise ValueError("; ".join(errors))
    return output
def validate_manifest(
    manifest: Any,
    source: Any | None = None,
    repo_root: Path | None = None,
    label: str = "l2-impact-obligation-manifest",
) -> list[str]:
    errors = validate_manifest_shape(manifest, label)
    if errors:
        return errors
    if source is None or repo_root is None:
        return [f"{label}: source-bound exact-diff replay is required"]
    source_errors = validate_source(source, "l2-source")
    if source_errors:
        return source_errors
    if manifest["source"]["digest"] != canonical_digest(source):
        return [f"{label}: source.digest does not match supplied source"]
    try:
        fresh = compile_source(source, repo_root)
    except Exception as exc:
        return [f"{label}: exact-diff replay failed: {exc}"]
    if fresh != manifest:
        errors.append(
            f"{label}: stored content does not equal fresh exact-diff replay"
        )
    return errors
def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compile or validate L2 impact obligations from an exact candidate diff."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    compile_parser = subparsers.add_parser("compile")
    compile_parser.add_argument("source")
    compile_parser.add_argument("--repo-root", default=".")
    compile_parser.add_argument("--output")
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("source")
    validate_parser.add_argument("manifest")
    validate_parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    source = load_yaml(Path(args.source))
    repo_root = Path(args.repo_root).resolve()
    if args.command == "compile":
        manifest = compile_source(source, repo_root)
        rendered = dump_yaml(manifest)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return
    manifest = load_yaml(Path(args.manifest))
    errors = validate_manifest(
        manifest,
        source,
        repo_root,
        Path(args.manifest).name,
    )
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print(
        "OK: L2 exact-diff replay: "
        f"{args.source} + {args.manifest}"
    )
if __name__ == "__main__":
    main()
