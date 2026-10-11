"""Generic V3.2 graph-bound *read-only* current-source preflight.

This is a non-frozen integration seam, NOT a GitHub transport, publisher,
evidence issuer, graph-release authority or second progress calculator.
The injected provider must have only get_issue/get_pull/get_commit_sha.
All returned observations are UNATTESTED until the separate genuine provider,
Owner source and CI policies have been evaluated.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[3]
_NATIVE = _ROOT / "skills/engineering-pr-delivery-v3.2/scripts"
if str(_NATIVE) not in sys.path:
    sys.path.insert(0, str(_NATIVE))
import delp_projection_v32 as delp

_REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_SHA = re.compile(r"^[0-9a-f]{40}$")
_REQUIRED_GETS = ("get_issue", "get_pull", "get_commit_sha")


class SourceHold(ValueError):
    """Stable bounded refusal; never include private source bodies in errors."""


def _require(ok: bool, code: str) -> None:
    if not ok:
        raise SourceHold(code)


def _ref_in_repo(ref: Any, repository: str, number: int) -> bool:
    short = repository.split("/", 1)[1] + "#" + str(number)
    return isinstance(ref, str) and ref in (short, repository + "#" + str(number))


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _read_source(
    provider: Any, *, repository: str, root_num: int, leaf_num: int,
    pr_number: int, base_ref: str, expected_head: str,
) -> dict[str, Any]:
    """One bounded logical GET pass, never a writer or a source authenticator."""
    try:
        base_sha = provider.get_commit_sha(base_ref)
        raw_root = provider.get_issue(root_num)
        raw_leaf = provider.get_issue(leaf_num)
        raw_pull = provider.get_pull(pr_number)
    except Exception as exc:
        raise SourceHold("PROVIDER_GET_UNAVAILABLE") from exc

    _require(isinstance(base_sha, str) and _SHA.fullmatch(base_sha) is not None,
             "PROVIDER_BASE_SHA_INVALID")
    issues = {}
    for number, issue in ((root_num, raw_root), (leaf_num, raw_leaf)):
        _require(isinstance(issue, Mapping) and
                 type(issue.get("number")) is int and issue["number"] == number,
                 "PROVIDER_ISSUE_IDENTITY_INVALID")
        _require(issue.get("state") in ("open", "closed") and
                 isinstance(issue.get("title"), str) and bool(issue["title"].strip()) and
                 isinstance(issue.get("body"), (str, type(None))),
                 "PROVIDER_ISSUE_SURFACE_INVALID")
        issues[number] = {
            "number": number,
            "state": issue["state"],
            "title": issue["title"],
            "body_digest": _digest(issue.get("body") or ""),
        }

    _require(isinstance(raw_pull, Mapping) and
             type(raw_pull.get("number")) is int and raw_pull["number"] == pr_number,
             "PROVIDER_PR_IDENTITY_INVALID")
    head = raw_pull.get("head")
    base = raw_pull.get("base")
    _require(isinstance(head, Mapping) and isinstance(base, Mapping) and
             isinstance(head.get("repo"), Mapping) and isinstance(base.get("repo"), Mapping),
             "PROVIDER_PR_SOURCE_INVALID")
    _require(str(head["repo"].get("full_name", "")).lower() == repository.lower(),
             "PROVIDER_HEAD_REPOSITORY_MISMATCH")
    _require(str(base["repo"].get("full_name", "")).lower() == repository.lower(),
             "PROVIDER_BASE_REPOSITORY_MISMATCH")
    _require(base.get("ref") == base_ref, "PROVIDER_BASE_REF_MISMATCH")
    _require(isinstance(head.get("sha"), str) and _SHA.fullmatch(head["sha"]) is not None,
             "PROVIDER_HEAD_SHA_INVALID")
    _require(head["sha"] == expected_head, "CANDIDATE_HEAD_MISMATCH")
    _require(raw_pull.get("state") in ("open", "closed") and
             type(raw_pull.get("merged")) is bool and
             type(raw_pull.get("draft")) is bool and
             isinstance(raw_pull.get("title"), str) and bool(raw_pull["title"].strip()) and
             isinstance(raw_pull.get("body"), (str, type(None))),
             "PROVIDER_PR_SURFACE_INVALID")
    _require(not (raw_pull["merged"] and raw_pull["state"] != "closed"),
             "PROVIDER_PR_STATE_INCONSISTENT")
    pull = {
        "number": pr_number, "state": raw_pull["state"],
        "merged": raw_pull["merged"], "draft": raw_pull["draft"],
        "head_sha": head["sha"], "base_ref": base_ref,
        "title": raw_pull["title"], "body_digest": _digest(raw_pull.get("body") or ""),
    }
    return {"base_sha": base_sha, "issues": issues, "pull": pull}


def preflight(
    *, graph: Mapping[str, Any], repository: str, leaf_ref: str,
    pr_number: int, expected_head: str, provider: Any,
) -> dict[str, Any]:
    """Reconcile two source observations against one native released graph.

    Does not prove a graph was Owner-released or that a provider is authentic.
    Deliberately supplies an *empty* ledger to native DELP: no fact is credited.
    """
    _require(isinstance(repository, str) and _REPOSITORY.fullmatch(repository) is not None,
             "REPOSITORY_SELECTION_INVALID")
    _require(isinstance(graph, Mapping) and isinstance(graph.get("programme"), Mapping) and
             str(graph["programme"].get("repository", "")).lower() == repository.lower(),
             "REPOSITORY_SELECTION_MISMATCH")
    _require(isinstance(expected_head, str) and _SHA.fullmatch(expected_head) is not None,
             "CANDIDATE_SHA_PIN_INVALID")
    _require(type(pr_number) is int and pr_number > 0, "PR_NUMBER_INVALID")
    try:
        indexed = delp.validate_graph(graph)
        report = delp.decomposition_report(graph)
    except (ValueError, TypeError, KeyError) as exc:
        raise SourceHold("NATIVE_GRAPH_INVALID") from exc
    _require(report.get("release_state") == "RELEASEABLE", "GRAPH_NOT_RELEASEABLE")
    nodes = indexed["nodes"]
    _require(isinstance(leaf_ref, str) and leaf_ref in nodes and
             nodes[leaf_ref]["kind"] == "LEAF", "LEAF_NOT_GRAPH_BOUND")
    leaf = nodes[leaf_ref]
    root = indexed["root"]
    _require(_ref_in_repo(root, repository, delp.ref_number(root)) and
             _ref_in_repo(leaf_ref, repository, delp.ref_number(leaf_ref)),
             "ISSUE_REF_REPOSITORY_MISMATCH")
    _require(_ref_in_repo(leaf.get("primary_pr"), repository, pr_number),
             "PRIMARY_PR_NOT_GRAPH_BOUND")
    _require(all(callable(getattr(provider, name, None)) for name in _REQUIRED_GETS) and
             str(getattr(provider, "repository", "")).lower() == repository.lower(),
             "PROVIDER_REPOSITORY_MISMATCH")

    base_ref = indexed["programme"].get("base_ref") or "main"
    a = _read_source(provider, repository=repository,
                     root_num=delp.ref_number(root), leaf_num=delp.ref_number(leaf_ref),
                     pr_number=pr_number, base_ref=base_ref, expected_head=expected_head)
    try:
        b = _read_source(provider, repository=repository,
                         root_num=delp.ref_number(root), leaf_num=delp.ref_number(leaf_ref),
                         pr_number=pr_number, base_ref=base_ref, expected_head=expected_head)
    except SourceHold as exc:
        # The candidate could have moved during the second read: a current
        # observation cannot claim stable identity at either time.
        if str(exc) == "CANDIDATE_HEAD_MISMATCH":
            raise SourceHold("PROVIDER_MOVED_DURING_READ") from exc
        raise
    _require(a == b, "PROVIDER_MOVED_DURING_READ")

    try:
        projection = delp.project(
            graph, [], {leaf_ref: {
                "candidate_sha": expected_head,
                "base_sha": b["base_sha"],
                "pr_state": "MERGED" if b["pull"]["merged"] else b["pull"]["state"].upper(),
            }},
        )
        selected = projection["nodes"][leaf_ref]
        root_node = projection["nodes"][root]
    except (ValueError, TypeError, KeyError) as exc:
        raise SourceHold("NATIVE_DELP_REJECTED_SOURCE") from exc

    return {
        "schema": "relay-v32-325-generic-source-preflight-v1",
        "status": "READ_ONLY_SOURCE_OBSERVED_UNATTESTED",
        "identity": {"repository": repository, "root": root,
                     "leaf": leaf_ref, "pr": leaf["primary_pr"]},
        "candidate_sha": expected_head,
        "pr_state": "MERGED" if b["pull"]["merged"] else b["pull"]["state"].upper(),
        "source_snapshot_digest": _digest(b),
        "graph_digest": delp.canonical_digest(graph),
        "native_plan_digest": projection["plan_digest"],
        "native_input_digest": projection["input_digest"],
        "native_progress": {
            "root": {k: root_node["progress"][k] for k in ("D", "E")},
            "leaf": {k: selected["progress"][k] for k in ("P", "E")},
        },
        "writes": 0,
        "source_authenticated": False,
        "evidence_admitted": False,
        "production_authorized": False,
        "automatic_successor": False,
    }
