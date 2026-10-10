"""Non-admitting V3.2 read-only preflight -> existing DELP/C6 handover bridge.

This code is NOT a source issuer, Owner graph release oracle, evidence policy,
successor authorization, custody grant or alternate DELP projector. Its sole
purpose is to verify that the existing native source-bound C6 consumer can
read the SAME provider source as the bounded V3.2 preflight.

Even a C6 result of CURRENT_READ_ONLY remains provenance-unqualified.
The returned status is always HOLD. No positive E/P/D is exposed.
"""
from __future__ import annotations

import importlib
from hashlib import sha256
from json import loads
from pathlib import Path
from sys import path as sys_path
from typing import Any, Mapping

from v32_provider_preflight import PreflightTarget, ReadOnlyGetter, inspect_v32_read_only


class _C6GetAdapter:
    """Only four GET read methods needed by native C6; intentionally no writes."""
    def __init__(self, repository: str, getter: ReadOnlyGetter):
        self.repository = repository
        self.getter = getter

    def get_issue(self, number: int) -> dict[str, Any]:
        value = self.getter.get_issue(self.repository, number)
        if not isinstance(value, Mapping):
            raise ValueError("C6_ISSUE_GET_INVALID")
        return dict(value)

    def get_commit_sha(self, ref: str) -> str:
        value = self.getter.get_commit(self.repository, ref)
        if not isinstance(value, Mapping):
            raise ValueError("C6_COMMIT_GET_INVALID")
        return str(value.get("sha") or "")

    def get_pull(self, number: int) -> dict[str, Any]:
        value = self.getter.get_pull(self.repository, number)
        if not isinstance(value, Mapping):
            raise ValueError("C6_PULL_GET_INVALID")
        return dict(value)

    def list_comments(self, number: int) -> list[dict[str, Any]]:
        value = self.getter.get_issue_comments(self.repository, number)
        if not isinstance(value, list):
            raise ValueError("C6_COMMENTS_GET_INVALID")
        return [dict(row) for row in value]


def _native_c6():
    native_dir = (Path(__file__).resolve().parents[3] /
                  "skills/engineering-pr-delivery-v3.2/scripts")
    if str(native_dir) not in sys_path:
        sys_path.insert(0, str(native_dir))
    return importlib.import_module("handover_context")


def _halt(status: str, reason: str, *, source: Mapping[str, Any] | None = None, native_attempted: bool = False, failed_stage: str | None = None) -> dict[str, Any]:
    return {
        "status": status, "reasons": [reason],
        "source_status": source.get("status") if source is not None else None,
        "native_c6_invoked": native_attempted, "failed_stage": failed_stage, "current_source_basis": None,
        "c6_reconstruction": None, "accepted_evidence_count": None,
        "writer_authorized": False, "delp_admitted": False,
        "execution_admission": "NEVER_FROM_RECONSTRUCTION",
    }


def inspect_v32_c6_read_only(
    target: PreflightTarget, getter: ReadOnlyGetter,
    *, frozen_basis: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Verify source->native-C6 connectivity; never certify positive source."""
    first = inspect_v32_read_only(target, getter)
    source = first.as_dict()
    if first.status != "HOLD_NO_APPROVED_POSITIVE_ISSUER":
        return _halt("HOLD_PREFLIGHT_SOURCE", "SOURCE_PREFLIGHT_NOT_STRUCTURALLY_CURRENT", source=source)

    native_attempted = False
    failed_stage = "REPOSITORY"
    try:
        repo = getter.get_repository(target.repository)
        if not isinstance(repo, Mapping) or repo.get("id") != target.repository_id or str(repo.get("full_name") or "").lower() != target.repository.lower():
            raise ValueError("C6_REPOSITORY_IDENTITY_MISMATCH")
        failed_stage = "DEFAULT_BRANCH"
        branch = repo.get("default_branch")
        if not isinstance(branch, str):
            raise ValueError("C6_BRANCH_MISSING")
        failed_stage = "BASE_COMMIT"
        commit = getter.get_commit(target.repository, branch)
        sha = commit.get("sha")
        if not isinstance(sha, str) or len(sha) != 40:
            raise ValueError("C6_BASE_SHA_INVALID")
        failed_stage = "GRAPH_BYTES"
        raw = getter.get_file_bytes(target.repository, target.graph_path, sha)
        if not isinstance(raw, bytes) or "sha256:" + sha256(raw).hexdigest() != first.graph_digest:
            return _halt("HOLD_MOVED_GRAPH", "GRAPH_CHANGED_AFTER_PREFLIGHT", source=source)
        failed_stage = "GRAPH_JSON"
        graph = loads(raw.decode("utf-8"))
        if not isinstance(graph, dict):
            raise ValueError("C6_GRAPH_PAYLOAD_INVALID")
        failed_stage = "NATIVE_IMPORT"
        c6 = _native_c6()
        native_attempted = True
        failed_stage = "NATIVE_EXECUTION"
        preview = c6.build_delp_source_bound_successor(
            graph, leaf_ref=target.leaf_ref,
            provider=_C6GetAdapter(target.repository, getter),
            frozen_basis=dict(frozen_basis) if frozen_basis is not None else None,
        )
        # The source can move after native C6's own double-read. The end
        # release re-read does not make this observation atomic.
        failed_stage = "POST_C6_PROVIDER"
        repo_late = getter.get_repository(target.repository)
        late_branch = repo_late.get("default_branch")
        late_sha = getter.get_commit(target.repository, branch).get("sha")
        if (repo_late.get("id") != target.repository_id or
                str(repo_late.get("full_name") or "").lower() != target.repository.lower() or
                late_branch != branch or late_sha != sha or
                getter.get_file_bytes(target.repository, target.graph_path, sha) != raw):
            return _halt("HOLD_MOVED_GRAPH", "GRAPH_CHANGED_DURING_C6_READ", source=source)
        failed_stage = "C6_DIGEST"
        digests = preview.get("digests")
        core = preview.get("delp_responsibility_core")
        if (not isinstance(digests, dict) or not isinstance(core, dict)
                or preview.get("execution_admission") != "NEVER_FROM_RECONSTRUCTION"
                or preview.get("authority_effects") != [] or
                any(digests.get(k) != core.get("digests", {}).get(k) for k in ("graph", "plan", "input"))):
            raise ValueError("C6_CORE_SOURCE_DIGEST_MISMATCH")
        return {
            "status": "HOLD_C6_RECONCILE_REQUIRED" if preview.get("currentness") == "RECONCILE_REQUIRED" else "HOLD_C6_SOURCE_UNADMITTED",
            "reasons": ["OWNER_RELEASE_AND_POSITIVE_EVIDENCE_NOT_AUTHENTICATED"],
            "source_status": first.status,
            "native_c6_invoked": True,
            "current_source_basis": dict(digests),
            "c6_reconstruction": {
                "native_source_currentness": preview.get("currentness"),
                "moved_axes": list(preview.get("moved_axes") or []),
                "basis_digest": core.get("basis_digest"),
                "owner_source_status": preview.get("owner_source_status"),
                "provider_trust": preview.get("provider_trust"),
            },
            "accepted_evidence_count": None, "writer_authorized": False,
            "delp_admitted": False,
            "execution_admission": "NEVER_FROM_RECONSTRUCTION",
        }
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RuntimeError, ImportError) as exc:
        # Native implementation can contain source labels/body; never emit
        # exception text or provider body, only an unqualified HOLD.
        return _halt("HOLD_C6_SOURCE_READ", "NATIVE_C6_SOURCE_UNAVAILABLE_OR_INVALID", source=source, native_attempted=native_attempted, failed_stage=failed_stage)
