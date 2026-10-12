#!/usr/bin/env python3
"""Independent v3.6 draft label/evidence contract. No network or GitHub writes."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

OUTCOME_IDS = frozenset({"O1", "O2", "O3", "O4", "O5"})
REQUIRED_LABEL_FIELDS = frozenset({
    "label_id", "label_version", "approval", "criticality",
    "owner_aim_verbatim", "outcomes", "task_aim", "done_when", "source_issue"
})
ISSUE_REF = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*$")
TASK_REF = re.compile(r"^[A-Z0-9][A-Z0-9_.-]{2,79}$")
LABEL_NAME = re.compile(r"^[A-Z][A-Z0-9-]{2,79}$")


class ContractError(ValueError):
    """Fail-closed invalid or untrustworthy input."""


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML, refusing ambiguous duplicate keys."""


def _unique_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode) -> dict:
    out = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str) or key in out:
            raise ContractError("duplicate or non-string YAML mapping key")
        out[key] = loader.construct_object(value_node)
    return out


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _unique_mapping
)


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be nonempty text")
    if "<" in value and ">" in value:
        raise ContractError(f"{field} contains an unresolved placeholder")
    return value


def validate_label(document: object, expected_id: str | None = None) -> dict:
    if not isinstance(document, dict):
        raise ContractError("label must be a YAML mapping")
    if set(document) != REQUIRED_LABEL_FIELDS:
        missing = sorted(REQUIRED_LABEL_FIELDS - set(document))
        extra = sorted(set(document) - REQUIRED_LABEL_FIELDS)
        raise ContractError(f"label fields mismatch: missing={missing}, extra={extra}")
    label_id = _text(document["label_id"], "label_id")
    if not LABEL_NAME.fullmatch(label_id) or (expected_id and label_id != expected_id):
        raise ContractError("label_id is invalid or does not match path")
    _text(document["label_version"], "label_version")
    if document["approval"] not in ("pending", "approved"):
        raise ContractError("approval must be pending or approved")
    if document["criticality"] not in ("pending", "engineering-critical", "standard"):
        raise ContractError("criticality must be pending, engineering-critical or standard")
    for field in ("owner_aim_verbatim", "task_aim", "done_when"):
        _text(document[field], field)
    if not isinstance(document["outcomes"], dict) or set(document["outcomes"]) != OUTCOME_IDS:
        raise ContractError("outcomes must define exactly O1..O5")
    for outcome_id, text in document["outcomes"].items():
        _text(text, f"outcomes.{outcome_id}")
    if not isinstance(document["source_issue"], str) or not ISSUE_REF.fullmatch(document["source_issue"]):
        raise ContractError("source_issue must be owner/repo#N")
    return dict(document)


def load_label(path: str | Path) -> dict:
    file_path = Path(path)
    if len(file_path.parts) < 3 or tuple(file_path.parts[-3:-1]) != ("relay", "AIM"):
        raise ContractError("label must be stored at relay/AIM/<WORK>.yaml")
    if file_path.suffix != ".yaml" or not LABEL_NAME.fullmatch(file_path.stem):
        raise ContractError("label path requires a valid <WORK>.yaml")
    try:
        content = file_path.read_text(encoding="utf-8")
        document = yaml.load(content, Loader=UniqueKeyLoader)
    except (OSError, yaml.YAMLError) as exc:
        raise ContractError(f"label cannot be read safely: {exc}") from exc
    return validate_label(document, expected_id=file_path.stem)


def _proof(url: str) -> str:
    value = _text(url, "Proof")
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise ContractError("Proof must be a concrete HTTPS link")
    if any(x in value.lower() for x in ("example.com", "localhost", "todo", "<", ">")):
        raise ContractError("Proof cannot be a placeholder")
    return value


def render_evidence(*, outcome: str, for_user: str, proof: str,
                    task_id: str, issue_ref: str, candidate: str,
                    tests_passed: int, tests_run: int) -> str:
    if outcome not in OUTCOME_IDS:
        raise ContractError("Outcome must be one of O1..O5")
    for_user = _text(for_user, "For the user").strip()
    proof = _proof(proof)
    if not TASK_REF.fullmatch(task_id):
        raise ContractError("invalid task ID")
    if not ISSUE_REF.fullmatch(issue_ref):
        raise ContractError("invalid child issue reference")
    candidate = _text(candidate, "candidate")
    if not isinstance(tests_passed, int) or not isinstance(tests_run, int):
        raise ContractError("test counts must be integers")
    if tests_run < 1 or not 0 <= tests_passed <= tests_run:
        raise ContractError("finished task evidence requires real bounded test counts")
    return (
        f"Outcome: {outcome}\n"
        f"For the user: {for_user}\n"
        f"Proof: {proof}\n"
        "TASK_EVIDENCE v3.6\n"
        f"Task: {task_id}\n"
        f"Child issue: {issue_ref}\n"
        f"Candidate: {candidate}\n"
        f"Tests: {tests_passed}/{tests_run}\n"
    )


def validate_evidence(text: str) -> dict:
    if not isinstance(text, str):
        raise ContractError("comment must be text")
    lines = text.splitlines()
    prefixes = ("Outcome: ", "For the user: ", "Proof: ", "TASK_EVIDENCE v3.6",
                "Task: ", "Child issue: ", "Candidate: ", "Tests: ")
    if len(lines) < 8 or not all(line.startswith(prefix) for line, prefix in zip(lines[:8], prefixes)):
        raise ContractError("evidence must start with three human-facing lines and the v3.6 block")
    if lines[3] != "TASK_EVIDENCE v3.6":
        raise ContractError("missing evidence version marker")
    outcome, for_user, proof = [lines[i].split(": ", 1)[1] for i in range(3)]
    task, issue, candidate, tests = [lines[i].split(": ", 1)[1] for i in range(4, 8)]
    match = re.fullmatch(r"([0-9]+)/([0-9]+)", tests)
    if not match:
        raise ContractError("Tests must be passed/run")
    expected = render_evidence(outcome=outcome, for_user=for_user, proof=proof,
                               task_id=task, issue_ref=issue, candidate=candidate,
                               tests_passed=int(match[1]), tests_run=int(match[2]))
    if text != expected:
        raise ContractError("noncanonical evidence comment (no unsupported trailing claims)")
    return {"outcome": outcome, "task_id": task, "issue_ref": issue, "candidate": candidate}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="v3.6 WP1: local read-only contract tooling")
    command = parser.add_subparsers(dest="command", required=True)
    check = command.add_parser("validate-label", help="validate proposed relay/AIM/<WORK>.yaml")
    check.add_argument("path")
    render = command.add_parser("render-evidence", help="format evidence; never publishes it")
    for arg in ("outcome", "for-user", "proof", "task-id", "issue-ref", "candidate"):
        render.add_argument("--" + arg, required=True)
    render.add_argument("--tests-passed", required=True, type=int)
    render.add_argument("--tests-run", required=True, type=int)
    args = parser.parse_args(argv)
    try:
        if args.command == "validate-label":
            label = load_label(args.path)
            print(json.dumps({"valid": True, "label_id": label["label_id"],
                              "version": label["label_version"],
                              "approval": label["approval"],
                              "criticality": label["criticality"]}, sort_keys=True))
        else:
            print(render_evidence(outcome=args.outcome, for_user=args.for_user,
                                  proof=args.proof, task_id=args.task_id,
                                  issue_ref=args.issue_ref, candidate=args.candidate,
                                  tests_passed=args.tests_passed, tests_run=args.tests_run), end="")
    except ContractError as exc:
        print(f"v3.6 contract error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
