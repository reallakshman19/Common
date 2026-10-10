"""Observe native V3.2 comment claims; NEVER issue or admit evidence.

Uses the actual frozen V3.2 block parser and fact schema validator, not an
independently invented parser/calculator.  Author association and declared
programme.fact_authors are *structural issuer labels*, not proof that a CI,
reviewer, R3, original Owner source or verification reference is authentic.

All outputs are aggregate only; comment bodies and author identities are not
emitted. This module must not be connected to the production DELP ledger as an
eligibility gate without a separately approved native V3.2 issuer/policy.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Mapping, Sequence

_NATIVE_PATH = (
    Path(__file__).resolve().parents[3] /
    "skills" / "engineering-pr-delivery-v3.2" / "scripts" /
    "delp_projection_v32.py"
)


class NativeClaimAuditError(ValueError):
    """The native parser/contract or provider payload could not be trusted."""


def _native() -> Any:
    spec = importlib.util.spec_from_file_location("_v32_readonly_native_claim_parser", _NATIVE_PATH)
    if spec is None or spec.loader is None:
        raise NativeClaimAuditError("NATIVE_V32_PARSER_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def audit_native_comment_claims(
    *,
    graph: Mapping[str, Any],
    leaf_ref: str,
    candidate_sha: str,
    comments: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Inspect what the provider said, not whether its claims earn E.

    A structurally valid COMPLETE/VERIFIED claim, even from a native trusted
    author, remains UNATTESTED. No external evidence link is fetched, no
    native DELP state/project() is called and no status/title is written.
    """
    programme = graph.get("programme")
    if not isinstance(programme, Mapping):
        raise NativeClaimAuditError("CLAIM_AUDIT_GRAPH_PROGRAMME_INVALID")
    specified = programme.get("fact_authors") or []
    if not isinstance(specified, list) or not all(isinstance(a, str) and a.strip() for a in specified):
        raise NativeClaimAuditError("CLAIM_AUDIT_AUTHOR_POLICY_INVALID")
    if not isinstance(comments, (list, tuple)) or len(comments) > 2000:
        raise NativeClaimAuditError("CLAIM_AUDIT_COMMENTS_UNBOUNDED")
    native = _native()
    authors = set(specified)
    counts = {
        "blocks_seen": 0,
        "native_structural_claims": 0,
        "untrusted_author_claims": 0,
        "invalid_claims": 0,
        "current_candidate_claims": 0,
        "stale_candidate_claims": 0,
        "complete_verified_unit_claims": 0,
    }
    for comment in comments:
        if not isinstance(comment, Mapping) or not isinstance(comment.get("body"), str):
            raise NativeClaimAuditError("CLAIM_AUDIT_COMMENT_INVALID")
        author = comment.get("user")
        if author is None:
            author = {}
        if not isinstance(author, Mapping):
            raise NativeClaimAuditError("CLAIM_AUDIT_AUTHOR_INVALID")
        login = str(author.get("login") or "")
        association = str(comment.get("author_association") or "")
        structurally_trusted = (
            login in authors if authors else association in native.TRUSTED_ASSOCIATIONS
        )
        try:
            claims = native.extract_facts_blocks(comment["body"])
        except Exception as exc:
            # Invalid YAML is an observation failure, not "no facts".
            # Error text can contain comment content: never disclose it.
            raise NativeClaimAuditError("CLAIM_AUDIT_NATIVE_BLOCK_PARSE_FAILED") from exc
        for claimed in claims:
            counts["blocks_seen"] += 1
            if not structurally_trusted:
                counts["untrusted_author_claims"] += 1
            issues = native.validate_facts(claimed)
            if issues:
                counts["invalid_claims"] += 1
                continue
            responsibility = claimed.get("responsibility")
            try:
                bound_leaf = native.same_ref(responsibility["issue"], leaf_ref)
            except (ValueError, KeyError, TypeError):
                bound_leaf = False
            if not bound_leaf:
                counts["invalid_claims"] += 1
                continue
            counts["native_structural_claims"] += 1
            material = claimed.get("material") or {}
            if material.get("candidate_sha") == candidate_sha:
                counts["current_candidate_claims"] += 1
            else:
                counts["stale_candidate_claims"] += 1
            for unit in claimed.get("units") or []:
                if unit.get("state") == "COMPLETE" and unit.get("result") == "VERIFIED":
                    counts["complete_verified_unit_claims"] += 1
    return {
        "status": "HOLD_UNATTESTED_COMMENT_CLAIMS" if counts["blocks_seen"] else "HOLD_NO_COMMENT_CLAIMS",
        **counts,
        "provider_evidence_eligibility": "UNKNOWN_NOT_ASSESSED",
        "accepted_evidence_count": None,
        "writer_authorized": False,
        "delp_invoked": False,
    }
