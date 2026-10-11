"""T02 current released graph and native DELP source reconciliation (GET-only).

No network implementation, tokens, writer, evidence issuer, reviewer grant,
or V3.2 source change lives here. The two injected providers remain caller
supplied; "current" means internally consistent provider-current observations,
not independently authenticated GitHub/Owner source or a production permit.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

from generic_source_preflight import SourceHold, _digest, _require, preflight, delp

_REVISION = re.compile(r"^[0-9a-f]{40}$")
_GRAPH_PATH = re.compile(r"^(?!/)(?!.*(?:^|/)\.\.?/)[a-zA-Z0-9_.-]+(?:/[a-zA-Z0-9_.-]+)*\.json$")
_MAX_GRAPH_BYTES = 5_000_000


def _strict_pairs(pairs):
    data = {}
    for key, value in pairs:
        _require(key not in data, "SOURCE_GRAPH_DUPLICATE_KEY")
        data[key] = value
    return data


def _reject_constant(_value):
    raise SourceHold("SOURCE_GRAPH_NONFINITE_CONSTANT")


def _canonical_graph(raw: Any) -> tuple[dict, str]:
    _require(isinstance(raw, bytes) and 0 < len(raw) <= _MAX_GRAPH_BYTES,
             "SOURCE_GRAPH_BYTES_INVALID_OR_UNBOUNDED")
    try:
        graph = json.loads(raw.decode("utf-8"),
                           object_pairs_hook=_strict_pairs,
                           parse_constant=_reject_constant)
    except (UnicodeError, ValueError, TypeError) as exc:
        if isinstance(exc, SourceHold):
            raise
        raise SourceHold("SOURCE_GRAPH_INVALID_JSON") from exc
    _require(isinstance(graph, dict), "SOURCE_GRAPH_NOT_OBJECT")
    return graph, "sha256:" + hashlib.sha256(raw).hexdigest()


def _custody_pass(graph_provider: Any, repository: str, path: str,
                  revision: str) -> tuple[dict, str, str]:
    try:
        repo = graph_provider.get_repository()
    except Exception as exc:
        raise SourceHold("GRAPH_REPOSITORY_GET_UNAVAILABLE") from exc
    _require(isinstance(repo, Mapping) and
             str(repo.get("full_name", "")).lower() == repository.lower(),
             "GRAPH_REPOSITORY_MISMATCH")
    branch = repo.get("default_branch")
    _require(isinstance(branch, str) and
             re.fullmatch(r"[A-Za-z0-9_.\-/]{1,200}", branch) is not None and
             ".." not in branch and not branch.startswith(("-", "/")),
             "GRAPH_DEFAULT_BRANCH_INVALID")
    try:
        revision_bytes = graph_provider.get_file_bytes(path, revision)
        branch_bytes = graph_provider.get_file_bytes(path, branch)
    except Exception as exc:
        raise SourceHold("SOURCE_GRAPH_GET_UNAVAILABLE") from exc
    graph, pinned_sha = _canonical_graph(revision_bytes)
    current, current_sha = _canonical_graph(branch_bytes)
    _require(pinned_sha == current_sha, "SOURCE_GRAPH_NOT_CURRENT_RELEASED")
    _require(graph == current, "SOURCE_GRAPH_NOT_CURRENT_RELEASED")
    return graph, pinned_sha, branch


class _NativeGetFacade:
    """Exact known GET methods only; native DELP sees no writable adapter."""

    def __init__(self, provider: Any):
        self.__provider = provider

    def get_commit_sha(self, ref):
        return self.__provider.get_commit_sha(ref)

    def get_pull(self, number):
        return self.__provider.get_pull(number)

    def get_issue(self, number):
        return self.__provider.get_issue(number)

    def list_comments(self, number):
        return self.__provider.list_comments(number)

    def compare(self, base, head):
        return self.__provider.compare(base, head)


def _native_snapshot(provider: Any, graph: dict) -> tuple[list[dict], dict]:
    facade = _NativeGetFacade(provider)
    try:
        ledger = delp.ledger_from_github(facade, graph)
        observed = delp.observe_github(facade, graph)
    except (ValueError, TypeError, KeyError, RuntimeError, OSError, AttributeError) as exc:
        raise SourceHold("NATIVE_SOURCE_GET_OR_LEDGER_INVALID") from exc
    return ledger, observed


def reconcile_current_source(
    *, repository: str, graph_path: str, graph_revision: str, leaf_ref: str,
    pr_number: int, expected_head: str, graph_provider: Any, provider: Any,
) -> dict:
    """Verify pinned graph equals current released branch + reconcile native reads.

    A caller must independently authenticate both injected GET providers, graph
    source authority, Owner release and actual evidence/review. This function
    cannot grant those properties by comparing caller-controlled objects.
    """
    _require(isinstance(graph_revision, str) and
             _REVISION.fullmatch(graph_revision) is not None,
             "SOURCE_GRAPH_REVISION_INVALID")
    _require(isinstance(graph_path, str) and
             len(graph_path) <= 256 and
             _GRAPH_PATH.fullmatch(graph_path) is not None,
             "SOURCE_GRAPH_PATH_INVALID")
    _require(isinstance(repository, str) and
             str(getattr(graph_provider, "repository", "")).lower() == repository.lower(),
             "GRAPH_PROVIDER_REPOSITORY_MISMATCH")
    _require(all(callable(getattr(graph_provider, n, None))
                 for n in ("get_repository", "get_file_bytes")),
             "GRAPH_PROVIDER_GET_METHODS_REQUIRED")
    _require(all(callable(getattr(provider, n, None))
                 for n in ("get_commit_sha", "get_issue", "get_pull",
                           "list_comments", "compare")),
             "NATIVE_READONLY_GET_METHODS_REQUIRED")

    graph, raw_digest, default_branch = _custody_pass(
        graph_provider, repository, graph_path, graph_revision)
    _require(str((graph.get("programme") or {}).get("base_ref") or "main") ==
             default_branch, "SOURCE_GRAPH_BASE_NOT_DEFAULT_BRANCH")
    source = preflight(graph=graph, repository=repository,
                       leaf_ref=leaf_ref, pr_number=pr_number,
                       expected_head=expected_head, provider=provider)
    ledger_a, observed_a = _native_snapshot(provider, graph)
    ledger_b, observed_b = _native_snapshot(provider, graph)
    _require(ledger_a == ledger_b and observed_a == observed_b,
             "NATIVE_LEDGER_OR_OBSERVATION_MOVED")
    leaf = observed_b.get(leaf_ref)
    _require(isinstance(leaf, Mapping) and
             leaf.get("candidate_sha") == expected_head and
             leaf.get("base_sha") is not None and
             leaf.get("pr_state") == source["pr_state"],
             "NATIVE_SELECTED_MATERIAL_MISMATCH")
    graph_after, raw_after, branch_after = _custody_pass(
        graph_provider, repository, graph_path, graph_revision)
    _require(raw_after == raw_digest and branch_after == default_branch and
             graph_after == graph, "SOURCE_GRAPH_MOVED_DURING_READ")

    try:
        projection = delp.project(graph, ledger_b, observed_b)
        core = delp.source_bound_responsibility_core(graph, projection, leaf_ref)
    except (ValueError, TypeError, KeyError, RuntimeError) as exc:
        if "RESPONSIBILITY_CORE_MATERIAL_BOUNDARY" in str(exc):
            raise SourceHold("NATIVE_RESPONSIBILITY_CORE_MATERIAL_BOUNDARY") from exc
        raise SourceHold("NATIVE_DELP_OR_CORE_INVALID") from exc
    selected = projection["nodes"][leaf_ref]
    root = projection["nodes"][projection["root"]]
    return {
        "schema": "relay-v32-325-current-source-reconciliation-v1",
        "status": "READ_ONLY_RECONCILED_UNATTESTED",
        "identity": source["identity"],
        "candidate_sha": source["candidate_sha"],
        "pr_state": source["pr_state"],
        "source_custody": {
            "repository": repository,
            "graph_path": graph_path,
            "graph_revision": graph_revision,
            "raw_blob_sha256": raw_digest,
            "current_default_branch": default_branch,
            "provider_digest": source["source_snapshot_digest"],
            "native_input_digest": projection["input_digest"],
        },
        "native_ledger": {
            "total": len(ledger_b),
            "accepted": len(ledger_b) - len(projection["rejected_facts"]),
            "rejected": len(projection["rejected_facts"]),
            "observed_digest": _digest({"ledger": ledger_b, "observations": observed_b}),
        },
        "native_progress": {
            "root": {k: root["progress"][k] for k in ("D", "E")},
            "leaf": {k: selected["progress"][k] for k in ("P", "E")},
        },
        "native_core": core,
        "writes": 0,
        "source_authenticated": False,
        "evidence_admitted": False,
        "production_authorized": False,
        "automatic_successor": False,
    }
