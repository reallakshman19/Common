"""PW04 generic PR *source binding* for Relay V3.2; read-only by design.

This module is an independently testable staging boundary, NOT an issuer,
projector, owner-approval oracle, title renderer, or publisher. Its sole output
is a source-bound PR identity descriptor suitable for comparison against the
existing native DELP read-only result. The protected live adapter remains OFF.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256, sha1
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
from typing import Any, Callable, Mapping

_SHA = re.compile(r"[0-9a-f]{40}\Z")
_REF = re.compile(r"(?:[A-Za-z0-9_.-]+/)?[A-Za-z0-9_.-]+#[1-9][0-9]*\Z")
_REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
_BRANCH = re.compile(r"[A-Za-z0-9_./-]{1,200}\Z")
_MAX_GRAPH = 5_000_000
_NATIVE = (Path(__file__).resolve().parents[3] / "skills" /
           "engineering-pr-delivery-v3.2" / "scripts" / "delp_projection_v32.py")


class BindingError(ValueError):
    """Opaque safe error code: never leak private provider data in errors."""


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise BindingError(code)


def _native_structure(graph: Mapping[str, Any], repository: str) -> None:
    """Call unchanged native graph validator from same checkout, no duplicate engine."""
    try:
        spec = spec_from_file_location("_pw04_native_v32", _NATIVE)
        _require(spec is not None and spec.loader is not None, "NATIVE_V32_UNAVAILABLE")
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        module.validate_graph(graph)
        module.require_repository_match(graph, repository, live=True)
    except BindingError:
        raise
    except (OSError, AttributeError, ImportError, ValueError, TypeError, RuntimeError) as exc:
        raise BindingError("NATIVE_V32_GRAPH_REFUSED") from exc


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in pairs:
        _require(name not in result, "GRAPH_DUPLICATE_JSON_KEY")
        result[name] = value
    return result


def _git_blob_oid(raw: bytes) -> str:
    return sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def _ref_number(value: str, repository: str) -> int:
    _require(isinstance(value, str) and _REF.fullmatch(value) is not None,
             "GRAPH_REFERENCE_INVALID")
    before, suffix = value.rsplit("#", 1)
    short = repository.rsplit("/", 1)[-1]
    _require(before.lower() in (repository.lower(), short.lower()), "GRAPH_FOREIGN_REFERENCE")
    return int(suffix)


def _branch(value: Any) -> bool:
    return (isinstance(value, str) and _BRANCH.fullmatch(value) is not None and
            all(piece not in ("", ".", "..") for piece in value.split("/")))


def _repo_check(value: Any, expected_repo: str, expected_id: int) -> None:
    _require(isinstance(value, Mapping) and
             str(value.get("full_name") or "").lower() == expected_repo.lower() and
             type(value.get("id")) is int and value["id"] == expected_id,
             "PROVIDER_REPOSITORY_IDENTITY_MISMATCH")


@dataclass(frozen=True)
class PreviewPins:
    """Independently configured expected identities; pins ≠ Owner approval."""
    repository: str
    repository_id: int
    released_graph_blob_oid: str
    leaf_ref: str
    expected_pr_head_sha: str


def preview_source_binding(
    raw_graph: bytes,
    pins: PreviewPins,
    provider_repository: Mapping[str, Any],
    provider_pull: Mapping[str, Any],
    *,
    native_validate: Callable[[Mapping[str, Any], str], None] = _native_structure,
) -> dict[str, Any]:
    """Bind a selected leaf/PR against raw graph and real-shaped GET material.

    ALL inputs are observations, not trusted producer credentials. The result
    is deliberately *never* an admissible source claim or a write plan.
    External issued policy, current provider GET and independent witness are
    required before any separate production publisher is authorized.
    """
    _require(isinstance(pins.repository, str) and _REPO.fullmatch(pins.repository) is not None,
             "TARGET_REPOSITORY_INVALID")
    _require(type(pins.repository_id) is int and pins.repository_id > 0,
             "TARGET_REPOSITORY_ID_INVALID")
    _require(isinstance(pins.released_graph_blob_oid, str) and
             _SHA.fullmatch(pins.released_graph_blob_oid) is not None,
             "GRAPH_BLOB_PIN_INVALID")
    _require(isinstance(pins.expected_pr_head_sha, str) and
             _SHA.fullmatch(pins.expected_pr_head_sha) is not None,
             "PR_HEAD_PIN_INVALID")
    _ref_number(pins.leaf_ref, pins.repository)
    _require(type(raw_graph) is bytes and 0 < len(raw_graph) <= _MAX_GRAPH,
             "GRAPH_BYTES_UNAVAILABLE")
    _require(_git_blob_oid(raw_graph) == pins.released_graph_blob_oid,
             "GRAPH_BLOB_PIN_MISMATCH")
    try:
        graph = json.loads(raw_graph.decode("utf-8"), object_pairs_hook=_no_duplicate_keys,
                           parse_constant=lambda _v: (_require(False, "GRAPH_NONFINITE_JSON")))
    except BindingError:
        raise
    except (ValueError, UnicodeError, TypeError) as exc:
        raise BindingError("GRAPH_JSON_INVALID") from exc
    _require(isinstance(graph, dict) and isinstance(graph.get("programme"), dict) and
             isinstance(graph.get("nodes"), list), "GRAPH_SHAPE_INVALID")
    _require(str(graph["programme"].get("repository") or "").lower() == pins.repository.lower(),
             "GRAPH_REPOSITORY_MISMATCH")
    native_validate(graph, pins.repository)
    matches = [n for n in graph["nodes"] if isinstance(n, Mapping) and
               n.get("ref") == pins.leaf_ref]
    _require(len(matches) == 1 and matches[0].get("kind") == "LEAF", "GRAPH_LEAF_UNBOUND")
    leaf = matches[0]
    number = _ref_number(leaf.get("primary_pr"), pins.repository)
    base = graph["programme"].get("base_ref", "main")
    _require(_branch(base), "GRAPH_BASE_REF_INVALID")
    _repo_check(provider_repository, pins.repository, pins.repository_id)
    _require(isinstance(provider_pull, Mapping) and
             type(provider_pull.get("number")) is int and provider_pull["number"] == number,
             "PROVIDER_PR_IDENTITY_MISMATCH")
    head, target = provider_pull.get("head"), provider_pull.get("base")
    _require(isinstance(head, Mapping) and isinstance(target, Mapping),
             "PROVIDER_PR_ENDPOINTS_MISSING")
    _repo_check(head.get("repo"), pins.repository, pins.repository_id)
    _repo_check(target.get("repo"), pins.repository, pins.repository_id)
    _require(target.get("ref") == base, "PROVIDER_PR_WRONG_BASE")
    observed_head = head.get("sha")
    _require(isinstance(observed_head, str) and _SHA.fullmatch(observed_head) is not None,
             "PROVIDER_PR_HEAD_INVALID")
    _require(observed_head == pins.expected_pr_head_sha, "PROVIDER_PR_HEAD_MOVED")
    merged = provider_pull.get("merged")
    state, merged_at = provider_pull.get("state"), provider_pull.get("merged_at")
    _require(type(merged) is bool and state in ("open", "closed") and
             (not merged or (state == "closed" and isinstance(merged_at, str) and bool(merged_at))) and
             (merged or merged_at is None), "PROVIDER_PR_STATE_INVALID")
    # Fingerprint is NOT native DELP input_digest or an evidence receipt.
    identities = {
        "repo": pins.repository.lower(), "repo_id": pins.repository_id,
        "graph_blob": pins.released_graph_blob_oid,
        "leaf": pins.leaf_ref, "pr": number, "pr_head": observed_head,
        "pr_base": base, "pr_state": state, "pr_merged": merged,
    }
    fingerprint = "sha256:" + sha256(json.dumps(identities, sort_keys=True,
                                      separators=(",", ":")).encode()).hexdigest()
    return {
        "status": "SOURCE_BOUND_PREVIEW_NON_ADMITTING",
        "read_only": True,
        "publication_authorized": False,
        "owner_source_authenticated": False,
        "evidence_admitted": False,
        "native_projector_executed": False,
        "repository": pins.repository,
        "repository_id": pins.repository_id,
        "graph_blob_oid": pins.released_graph_blob_oid,
        "leaf_ref": pins.leaf_ref,
        "primary_pr_number": number,
        "base_ref": base,
        "observed_pr_head_sha": observed_head,
        "binding_fingerprint": fingerprint,
    }
