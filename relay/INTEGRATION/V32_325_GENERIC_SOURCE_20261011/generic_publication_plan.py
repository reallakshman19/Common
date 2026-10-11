"""T03: *pure* three-surface publisher plan and post-write observation contract.

This is NOT an authorized transport, a PATCH adapter, evidence issuer, status
writer or release gate. The *only* issue title + LIVE_STATUS owner remains the
unchanged native DELP sync_projection. Managed issue bodies and PR metadata
are separately scoped; this module performs no provider calls or writes.
A GitHub multi-resource update cannot be made atomic by this read model.
"""
from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

import pr_responsibility_view_v32 as view

from generic_source_preflight import SourceHold, _require, delp

_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_SCHEMA = "relay-v32-325-disjoint-publisher-plan-v1"


def _valid_digest(value: Any) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _surface(ref: str, raw: Any, *, kind: str) -> tuple[str, str]:
    _require(isinstance(raw, Mapping), "PUBLISHER_PROVIDER_SURFACE_INVALID")
    _require(type(raw.get("number")) is int and
             raw["number"] == delp.ref_number(ref),
             "PUBLISHER_PROVIDER_SURFACE_IDENTITY")
    title = raw.get("title")
    body = raw.get("body")
    _require(isinstance(title, str) and bool(title.strip()) and
             isinstance(body, str), "PUBLISHER_PROVIDER_SURFACE_INVALID")
    if kind == "PR":
        _require(raw.get("state") in ("open", "closed") and
                 isinstance(raw.get("head"), Mapping) and
                 isinstance(raw["head"].get("sha"), str),
                 "PUBLISHER_PROVIDER_PR_INVALID")
    return title, body


def _preserved_human_title(observed: str, expected: str, human: Any) -> bool:
    """Only safe observed source bases are eligible for derived title planning."""
    if not isinstance(human, str) or not human.strip():
        return False
    if not isinstance(expected, str) or not expected.strip() or expected == human:
        return False
    if not expected.endswith(" — " + human):
        return False
    # Never guess a newly edited owner title is an outdated machine prefix.
    return (observed == human or observed == expected or
            (observed.startswith("🟡 [") and observed.endswith(" — " + human)))


def build_publication_plan(
    *, graph: Mapping[str, Any], source: Mapping[str, Any],
    projection: Mapping[str, Any], views: Mapping[str, Any],
    observed_surfaces: Mapping[str, Any],
) -> dict[str, Any]:
    """Describe writes that existing single-owner publishers MAY later attempt.

    No provider access and no explicit authorization are possible from here.
    This accepts a caller-provided native-derived read-view; the caller must
    separately authenticate its Owner origin, released graph and issuer.
    """
    _require(isinstance(source, Mapping) and
             source.get("status") == "READ_ONLY_RECONCILED_UNATTESTED" and
             source.get("writes") == 0 and
             all(source.get(flag) is False for flag in (
                 "source_authenticated", "evidence_admitted",
                 "production_authorized", "automatic_successor")),
             "SOURCE_AUTHORITY_NOT_READONLY")
    _require(isinstance(graph, Mapping) and isinstance(projection, Mapping) and
             isinstance(views, Mapping) and isinstance(observed_surfaces, Mapping),
             "PUBLISHER_INPUT_INVALID")
    try:
        indexed = delp.validate_graph(graph)
        identity = source["identity"]
        core = source["native_core"]
        custody = source["source_custody"]
        root, leaf, pr_ref = identity["root"], identity["leaf"], identity["pr"]
        native = delp.source_bound_responsibility_core(graph, projection, leaf)
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise SourceHold("PUBLISHER_NATIVE_BASIS_INVALID") from exc
    _require(all(isinstance(x, Mapping) for x in (identity, core, custody)) and
             core == native and root == indexed["root"] and
             leaf in indexed["nodes"] and
             indexed["nodes"][leaf]["kind"] == "LEAF" and
             pr_ref == indexed["nodes"][leaf].get("primary_pr") and
             core["repository"] == identity["repository"] and
             core["root"] == root and core["leaf"] == leaf and
             core["primary_pr"] == pr_ref and
             core["candidate_sha"] == source.get("candidate_sha") and
             custody["repository"] == identity["repository"],
             "PUBLISHER_SOURCE_CORE_MISMATCH")
    _require(_valid_digest(projection.get("input_digest")) and
             projection["input_digest"] == custody.get("native_input_digest") and
             projection["input_digest"] == views.get("delp_input_digest") and
             projection.get("plan_digest") == views.get("plan_digest") and
             projection["plan_digest"] == core["digests"]["plan"] and
             core["digests"]["graph"] == delp.canonical_digest(graph),
             "PUBLISHER_NATIVE_INPUT_MISMATCH")
    _require(_valid_digest(views.get("input_digest")) and
             views.get("root") == root and views.get("leaf") == leaf and
             isinstance(views.get("pr"), Mapping) and
             views["pr"].get("binding") == "BOUND",
             "PUBLISHER_VIEW_BASIS_UNBOUND")
    _require(views["pr"].get("head_sha") == core["candidate_sha"],
             "PUBLISHER_PR_HEAD_MISMATCH")
    _require(views.get("parent_semantic") == core["progress"]["root"] and
             views.get("leaf_semantic") == core["progress"]["leaf"],
             "PUBLISHER_NATIVE_PROGRESS_MISMATCH")
    _require(delp._source_view_title_contract(graph, target_leaf=leaf) == (root, leaf),
             "PUBLISHER_NATIVE_TITLE_SCOPE_UNRELEASED")
    refs = (root, leaf, pr_ref)
    _require(len(set(refs)) == 3 and set(observed_surfaces) == set(refs),
             "PUBLISHER_THREE_SURFACE_SCOPE_INVALID")
    _require(isinstance(views.get("issue_titles"), Mapping) and
             set(views["issue_titles"]) == {root, leaf} and
             isinstance(views.get("issue_read_views"), Mapping) and
             set(views["issue_read_views"]) == {root, leaf} and
             isinstance(views.get("human_titles"), Mapping) and
             set(views["human_titles"]) == {root, leaf, "PR"},
             "PUBLISHER_READ_VIEW_SCOPE_INVALID")

    plan = {}
    for ref in refs:
        is_pr = ref == pr_ref
        observed_title, observed_body = _surface(
            ref, observed_surfaces[ref], kind="PR" if is_pr else "ISSUE")
        expected_title = (views.get("draft_pr_title") if is_pr else
                          views["issue_titles"][ref])
        human = views["human_titles"]["PR" if is_pr else ref]
        _require(_preserved_human_title(observed_title, expected_title, human),
                 "OWNER_HUMAN_TITLE_CHANGED")
        if is_pr:
            _require(observed_surfaces[ref]["head"]["sha"] ==
                     source["candidate_sha"], "PUBLISHER_PR_HEAD_MISMATCH")
            expected_block = views.get("pr_managed_block")
        else:
            expected_block = views["issue_read_views"][ref]
        _require(isinstance(expected_block, str), "PUBLISHER_MANAGED_BLOCK_INVALID")
        try:
            status = view.inspect_managed_block(
                observed_body, expected_block, pr=is_pr)
            _require(status not in ("CORRUPT_MARKERS",),
                     "MANAGED_BODY_MARKERS_UNSAFE")
            proposed_body = view.reconcile_managed_block(
                observed_body, expected_block,
                observed_digest=view.digest(observed_body), pr=is_pr)
        except (ValueError, TypeError, KeyError) as exc:
            raise SourceHold("MANAGED_BODY_MARKERS_UNSAFE") from exc
        plan[ref] = {
            "kind": "PR" if is_pr else "ISSUE",
            "number": delp.ref_number(ref),
            "title_owner": ("GUARDED_PR_METADATA" if is_pr else "NATIVE_DELP_ONLY"),
            "body_owner": "GUARDED_PR_METADATA" if is_pr else "MANAGED_ISSUE_BODY_ONLY",
            "observed_title": observed_title,
            "expected_title": expected_title,
            "observed_body_digest": view.digest(observed_body),
            "expected_body_digest": view.digest(proposed_body),
            "expected_body": proposed_body,
            "body_write_required": proposed_body != observed_body,
            "write_required": (observed_title != expected_title or
                               proposed_body != observed_body),
            "managed_block_status": status,
            "input_digest": projection["input_digest"],
        }
    order = [leaf, root, pr_ref]
    return {
        "schema": _SCHEMA,
        "status": "PLAN_ONLY_UNATTESTED",
        "identity": dict(identity),
        "candidate_sha": core["candidate_sha"],
        "expected_native_input_digest": projection["input_digest"],
        "source_custody_digest": custody.get("raw_blob_sha256"),
        "view_input_digest": views["input_digest"],
        "core_basis_digest": core["basis_digest"],
        "order": order,
        "changes": [ref for ref in order if plan[ref]["write_required"]],
        "surfaces": plan,
        "writers": {
            "issue_title_and_live_status": "NATIVE_DELP_SYNC_PROJECTION_ONLY",
            "issue_body": "MANAGED_ISSUE_BODY_ONLY",
            "pr_title_and_body": "SEPARATE_GUARDED_PR_METADATA",
        },
        "required_before_any_write": [
            "AUTHENTIC_OWNER_GRAPH_AND_PROVIDER",
            "OWNER_APPROVED_NATIVE_PUBLISHER",
            "RECHECK_CANDIDATE_AND_FULL_SOURCE_INPUT",
            "RECHECK_ALL_THREE_ORIGINAL_SURFACES",
            "VERIFY_CAS_OR_REPORT_PARTIAL",
            "VERIFY_DELP_NATIVE_LIVE_STATUS_AND_ALL_SURFACE_READBACKS",
        ],
        "non_atomic_external_writes": True,
        "writes": 0,
        "source_authenticated": False,
        "evidence_admitted": False,
        "production_authorized": False,
        "automatic_successor": False,
        "authority_effects": [],
    }


def reconcile_publication_readback(
    plan: Mapping[str, Any], observed_after: Mapping[str, Any],
    native_live_status: Mapping[str, Any],
) -> dict[str, Any]:
    """Pure readback classification, NEVER proof of a GitHub REST transaction.

    Provider content can be caller controlled, and even a perfect content match
    grants no execution, merge or release authority.
    """
    _require(isinstance(plan, Mapping) and plan.get("schema") == _SCHEMA and
             isinstance(plan.get("surfaces"), Mapping) and
             isinstance(observed_after, Mapping) and
             isinstance(native_live_status, Mapping),
             "PUBLISHER_READBACK_INPUT_INVALID")
    refs = plan["order"]
    matched, pending = [], []
    for ref in refs:
        row = plan["surfaces"][ref]
        actual = observed_after.get(ref)
        try:
            title, body = _surface(ref, actual, kind=row["kind"])
            ok = (title == row["expected_title"] and
                  view.digest(body) == row["expected_body_digest"])
            if row["kind"] == "PR":
                ok = ok and actual["head"]["sha"] == plan["candidate_sha"]
        except (SourceHold, TypeError, ValueError, KeyError):
            ok = False
        (matched if ok else pending).append(ref)
    root, leaf = plan["identity"]["root"], plan["identity"]["leaf"]
    missing_status = []
    for ref in (root, leaf):
        status = native_live_status.get(ref)
        if (not isinstance(status, Mapping) or
                type(status.get("version")) is not int or
                status["version"] < 1 or
                status.get("input_digest") != plan["expected_native_input_digest"]):
            missing_status.append(ref)
    all_match = not pending and not missing_status
    return {
        "schema": "relay-v32-325-publication-readback-v1",
        "status": ("OBSERVED_MATCH_NOT_AUTHORIZATION" if all_match
                   else "INCOMPLETE_SYNC"),
        "matched_surfaces": matched,
        "unverified_surfaces": pending,
        "unverified_native_status": missing_status,
        "native_input_digest": plan["expected_native_input_digest"],
        "candidate_sha": plan["candidate_sha"],
        "verified": all_match,
        "partial_rest_or_cas_possible": True,
        "writes": 0,
        "production_authorized": False,
        "automatic_successor": False,
        "authority_effects": [],
    }
