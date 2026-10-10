#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from handover_projection import render as render_handover
from intelligence_projection import build_improvement, build_task
from lease_admission import build_native_lease
from lease_liveness import (
    DEFAULT_RECOVERY_AFTER_SECONDS,
    active_lease_renewal,
    material_activity_basis,
    recovery_eligibility,
    renew_copy,
)
from material_basis import inspect as inspect_material_basis
from nomenclature import allocate_next_id, allocate_next_ids, issue_number_from_ep, parse_canonical_id, require_issue_rooted_id
from programme_reconciliation import assess_boundary, require_boundary_ready
from local_execution_projection import build as build_local_execution
from render_local_execution_request import render as render_local_execution_request
from relay_can import _protocol_state, evaluate as can_action
from snapshot_projection import build as build_snapshot
from transactionlib import BUDDY_MESSAGE_STAGES, TransactionError, execute, jsonl_bytes, recover_all, yaml_bytes
from v3lib import canonical_digest, load_events, load_yaml, require_identifier, validate_schema
from validate_foundation import validate_authority


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _custody_epoch(state: dict[str, Any]) -> int | None:
    value = (state.get("execution") or {}).get("custody_epoch")
    return int(value) if value is not None else None


def _require_expected_custody_epoch(state: dict[str, Any], expected: int | None) -> None:
    # Recorder-first V3.1 keeps custody epochs as provenance only. A stale or
    # omitted epoch is diagnostic context, never a mutation gate.
    return


def _add_automatic_liveness(
    root: Path,
    state: dict[str, Any],
    actor: str,
    replacements: dict[str, bytes],
    *,
    base_ref: str | None = None,
) -> None:
    renewal = active_lease_renewal(root, state, actor, base_ref=base_ref)
    if renewal is None:
        return
    path, lease = renewal
    if path not in replacements:
        replacements[path] = yaml_bytes(lease)


def _authority(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    # Recorder-first V3.1 reads the durable ledger even when cross-object
    # validation reports debt. Structural YAML/schema failures still surface at
    # the concrete read/write boundary.
    state = load_yaml(root / "relay/STATE.yaml")
    controls_path = str((state.get("controls") or {}).get("path") or "")
    controls = load_yaml(root / controls_path) if controls_path else {"controls": []}
    return state, controls


def _events(root: Path) -> list[dict[str, Any]]:
    events, errors = load_events(root / "relay/EVENTS.jsonl")
    if errors:
        raise TransactionError("invalid event history: " + "; ".join(errors[:8]))
    return events


def _event(event_id: str, event_type: str, actor: str, subject: str, basis: list[str], details: dict[str, Any]) -> dict[str, Any]:
    value = {
        "schema_version": "relay-v3.1-event",
        "event_id": event_id,
        "type": event_type,
        "timestamp": _now(),
        "actor": actor,
        "subject": subject,
        "basis": basis,
        "details": details,
    }
    errors = validate_schema("event", value, "EVENT")
    if errors:
        raise TransactionError("; ".join(errors))
    return value


def _assert_event_ids_available(events: list[dict[str, Any]], event_ids: list[str]) -> None:
    existing = {str(item.get("event_id")) for item in events}
    duplicates = sorted(set(event_ids) & existing)
    if duplicates:
        raise TransactionError(f"duplicate event id(s): {', '.join(duplicates)}")
    if len(event_ids) != len(set(event_ids)):
        raise TransactionError("transaction event ids must be unique")


def _issue_scoped_id(
    root: Path,
    *,
    kind: str,
    value: str | None,
    issue_number: int | None,
    label: str,
) -> str:
    if value is None:
        if issue_number is None:
            raise TransactionError(
                f"{kind}_ID_REQUIRED_WITHOUT_GOVERNING_ISSUE: canonical allocation requires a provider-backed governing issue"
            )
        return allocate_next_id(root, kind=kind, root=issue_number)

    text = str(value)
    try:
        require_identifier(text, f"{kind}-", label)
        if parse_canonical_id(text) is not None and issue_number is not None:
            require_issue_rooted_id(
                text,
                kind=kind,
                issue_number=issue_number,
                label=label,
            )
    except ValueError as exc:
        raise TransactionError(str(exc)) from exc
    return text


def _transition_event_ids(
    root: Path,
    *,
    event_id: str | None,
    issue_number: int | None,
    legacy_suffixes: list[str],
) -> list[str]:
    if not legacy_suffixes:
        raise TransactionError("event allocation requires at least one event")
    if event_id is None:
        if issue_number is None:
            raise TransactionError(
                "EVT_ID_REQUIRED_WITHOUT_GOVERNING_ISSUE: canonical event allocation requires a provider-backed governing issue"
            )
        return allocate_next_ids(
            root,
            kind="EVT",
            root=issue_number,
            count=len(legacy_suffixes),
        )

    base = _issue_scoped_id(
        root,
        kind="EVT",
        value=event_id,
        issue_number=issue_number,
        label="event id",
    )
    if parse_canonical_id(base) is not None and len(legacy_suffixes) > 1:
        raise TransactionError(
            "CANONICAL_EVENT_ID_REQUIRES_ALLOCATOR_FOR_MULTI_EVENT_TRANSITION: omit event_id"
        )
    if len(legacy_suffixes) == 1:
        return [base]
    return [base + suffix for suffix in legacy_suffixes]


def _snapshot_path(state: dict[str, Any]) -> str:
    value = str((state.get("generated") or {}).get("snapshot") or "")
    if not value:
        raise TransactionError("STATE.generated.snapshot must be explicit")
    return value


def _require_action(
    root: Path,
    action: str,
    *,
    path: str | None = None,
    base_ref: str | None = None,
    expected_custody_epoch: int | None = None,
) -> None:
    result = can_action(
        root,
        action,
        path=path,
        base_ref=base_ref,
        expected_custody_epoch=expected_custody_epoch,
    )
    if not result["allowed"]:
        raise TransactionError(f"{action} denied: {', '.join(result['reason_codes'])}")


def _current_checkpoint(root: Path, state: dict[str, Any]) -> dict[str, Any] | None:
    cp_id = (state.get("accepted") or {}).get("checkpoint")
    return load_yaml(root / "relay/CHECKPOINTS" / f"{cp_id}.yaml") if cp_id else None


def _current_ep(root: Path, state: dict[str, Any]) -> dict[str, Any] | None:
    ep_id = (state.get("execution") or {}).get("ep")
    return load_yaml(root / "relay/WORK" / f"{ep_id}.yaml") if ep_id else None


def _governing_issue_number(root: Path, state: dict[str, Any]) -> int | None:
    """Resolve issue lineage from current execution or accepted checkpoint truth."""
    ep = _current_ep(root, state)
    issue = issue_number_from_ep(ep)
    if issue is not None:
        return issue
    checkpoint = _current_checkpoint(root, state)
    checkpoint_ep = (checkpoint or {}).get("ep")
    if checkpoint_ep:
        ep_path = root / "relay/WORK" / f"{checkpoint_ep}.yaml"
        if ep_path.exists():
            return issue_number_from_ep(load_yaml(ep_path))
    return None


def _governing_issue_for_change(
    root: Path,
    state: dict[str, Any],
    change_id: str,
    delta: dict[str, Any] | None = None,
) -> int | None:
    parsed = parse_canonical_id(change_id)
    if parsed and parsed.get("kind") == "CHANGE" and parsed.get("scope_kind") == "ISSUE":
        return int(parsed["issue_number"])
    source_issue = ((delta or {}).get("application") or {}).get("source_issue")
    if source_issue is not None:
        return int(source_issue)
    return _governing_issue_number(root, state)

def _require_programme_boundary(
    parent: dict[str, Any] | None,
    observations: list[dict[str, Any]] | None,
    *,
    boundary: str,
    selected_frontier_ref: str | None = None,
) -> dict[str, Any]:
    # Programme reconciliation is recorded as context, never execution authority.
    try:
        return assess_boundary(
            parent,
            observations,
            boundary=boundary,
            selected_frontier_ref=selected_frontier_ref,
        )
    except ValueError:
        return assess_boundary(None, None, boundary=boundary)


def _require_final_reconciliation(
    root: Path,
    state: dict[str, Any],
    *,
    parent_issue_observation: dict[str, Any] | None = None,
) -> None:
    # Recorder-first V3.1 permits closure while reconciliation/delivery debt is
    # still visible in the ledger. Closing records a decision; it does not certify
    # that all programme debt disappeared.
    return


def _require_fresh_handover(
    root: Path,
    state: dict[str, Any],
    *,
    base_ref: str | None,
    require_published: bool = True,
) -> str:
    context_path = root / "relay/GENERATED/HANDOVER_CONTEXT.yaml"
    if not context_path.exists():
        raise TransactionError("graceful lease release requires a fresh HANDOVER_CONTEXT")

    context = load_yaml(context_path)
    errors = validate_schema("handover-context", context, "HANDOVER_CONTEXT")
    if errors:
        raise TransactionError("; ".join(errors))

    frozen = context.get("frozen_basis") or {}
    execution = state.get("execution") or {}
    if frozen.get("lease") != execution.get("lease") or frozen.get("ep") != execution.get("ep"):
        raise TransactionError("HANDOVER_STALE: handover EP/lease does not match current execution")
    if frozen.get("state_digest") != canonical_digest(state):
        raise TransactionError("HANDOVER_STALE: handover state digest does not match current authority")

    ep = _current_ep(root, state)
    if isinstance(ep, dict):
        if not base_ref:
            raise TransactionError("graceful lease release requires --base-ref to verify handover material freshness")
        inspected = inspect_material_basis(root, ep, base_ref)["material_basis"]
        for key, frozen_key in (
            ("head", "material_head"),
            ("relevant_paths_digest", "relevant_paths_digest"),
            ("dependency_digest", "dependency_digest"),
        ):
            if inspected.get(key) != frozen.get(frozen_key):
                raise TransactionError(f"HANDOVER_STALE: {frozen_key} no longer matches current material reality")

    learning = context.get("accumulated_learning") or {}
    task_meta = learning.get("task_snapshot") or {}
    improvement_meta = learning.get("improvement_view") or {}
    task_snapshot = task_meta.get("value")
    improvement_view = improvement_meta.get("value")
    if not isinstance(task_snapshot, dict) or not isinstance(improvement_view, dict):
        raise TransactionError("HANDOVER_STALE: frozen task/improvement read model is missing")
    if canonical_digest(task_snapshot) != task_meta.get("digest"):
        raise TransactionError("HANDOVER_STALE: embedded task snapshot digest changed")
    if canonical_digest(improvement_view) != improvement_meta.get("digest"):
        raise TransactionError("HANDOVER_STALE: embedded improvement view digest changed")

    roadmap_effect = improvement_view.get("roadmap_effect") or {}
    if roadmap_effect.get("concept_change") == "UNKNOWN":
        raise TransactionError("ROADMAP_RECONCILIATION_REQUIRED before graceful lease release")

    parent_issue = task_snapshot.get("parent_issue") or {}
    if parent_issue.get("number") and parent_issue.get("disposition") == "UNKNOWN":
        raise TransactionError("PARENT_ISSUE_RECONCILIATION_REQUIRED before graceful lease release")

    digest = canonical_digest(context)
    planned = any(
        item.get("type") == "HANDOVER_PLANNED"
        and digest in (item.get("basis") or [])
        for item in _events(root)
    )
    if not planned:
        raise TransactionError("handover continuation requires a committed HANDOVER_PLANNED event for the current context")

    if require_published:
        published = any(
            item.get("type") == "HANDOVER_PUBLISHED"
            and digest in (item.get("basis") or [])
            for item in _events(root)
        )
        if not published:
            raise TransactionError(
                "HANDOVER_NOT_PUBLISHED: planned context exists but no matching HANDOVER_PUBLISHED event is committed"
            )
    return digest


def admit_task(
    root: Path,
    *,
    tx_id: str | None,
    event_id: str | None,
    actor: str,
    admission_path: Path,
    base_ref: str,
    programme_issue_observations: list[dict[str, Any]] | None = None,
    selected_programme_ref: str | None = None,
    fail_after: int | None = None,
) -> dict[str, Any]:
    live_v3, protocol_state = _protocol_state(root)

    state, _ = _authority(root)
    execution = state.get("execution") or {}
    # Recorder-first admission may supersede an existing execution pointer. The
    # predecessor objects remain durable history; admission no longer waits for
    # an IDLE repository.

    admission = load_yaml(admission_path)
    errors = validate_schema("task-admission", admission, "TASK_ADMISSION")
    if errors:
        raise TransactionError("; ".join(errors))
    ep = copy.deepcopy(admission.get("ep") or {})
    governing_issue = issue_number_from_ep(ep)
    ep["id"] = _issue_scoped_id(
        root,
        kind="EP",
        value=ep.get("id"),
        issue_number=governing_issue,
        label="ep_id",
    )
    errors = validate_schema("ep", ep, "EP")
    if errors:
        raise TransactionError("; ".join(errors))

    tx_id = _issue_scoped_id(
        root,
        kind="TX",
        value=tx_id,
        issue_number=governing_issue,
        label="transaction id",
    )

    programme_assessment = _require_programme_boundary(
        ep.get("parent_issue"),
        programme_issue_observations,
        boundary="ADMIT_TASK",
        selected_frontier_ref=selected_programme_ref,
    )
    programme_reconciliation = programme_assessment["reconciliation"]

    roadmap_path = root / str((state.get("roadmap") or {}).get("path"))
    roadmap = load_yaml(roadmap_path)
    rplan = admission["roadmap"]
    wp = copy.deepcopy(rplan["work_package"])
    wp_id = str(wp.get("id"))
    if str(ep.get("work_package")) != wp_id:
        raise TransactionError("EP work_package must match admitted roadmap work package")
    if rplan["new_revision"] == roadmap.get("revision"):
        raise TransactionError("ADMIT_TASK requires a new roadmap revision")

    work_packages = copy.deepcopy(roadmap.get("work_packages") or [])
    existing_index = next((i for i, item in enumerate(work_packages) if str(item.get("id")) == wp_id), None)
    disposition = rplan["disposition"]
    if disposition == "ADDED_EXECUTION_WP":
        if existing_index is not None:
            raise TransactionError("ADDED_EXECUTION_WP requires a new work package id")
        work_packages.append(wp)
    elif existing_index is None:
        raise TransactionError(f"{disposition} requires an existing work package")
    elif disposition == "MAPPED_EXISTING_WP":
        existing = work_packages[existing_index]
        for key in ("id", "title", "weight", "depends_on"):
            if existing.get(key) != wp.get(key):
                raise TransactionError("MAPPED_EXISTING_WP cannot silently revise the work package contract")
        existing["state"] = "ACTIVE"
    else:
        work_packages[existing_index] = wp

    # SERIAL constrains execution custody (STATE/LEASE), not the number of
    # unfinished programme obligations. Other ACTIVE work packages may remain
    # real while this admission selects exactly one execution frontier.

    ep_path = root / "relay/WORK" / f"{ep['id']}.yaml"
    lease_spec = copy.deepcopy(admission["lease"])
    lease_id = _issue_scoped_id(
        root,
        kind="LEASE",
        value=lease_spec.get("id"),
        issue_number=governing_issue,
        label="lease_id",
    )
    lease_spec["id"] = lease_id
    lease_path = root / "relay/LEASES" / f"{lease_id}.yaml"
    if ep_path.exists() or lease_path.exists():
        raise TransactionError("ADMIT_TASK refuses to overwrite an existing EP or lease")

    predecessor_lease_id = execution.get("lease")
    predecessor_lease = None
    if predecessor_lease_id and str(predecessor_lease_id) != str(lease_id):
        predecessor_path = root / "relay/LEASES" / f"{predecessor_lease_id}.yaml"
        if predecessor_path.exists():
            candidate = load_yaml(predecessor_path)
            if isinstance(candidate, dict) and candidate.get("state") == "ACTIVE":
                predecessor_lease = candidate

    new_roadmap = copy.deepcopy(roadmap)
    new_roadmap["revision"] = rplan["new_revision"]
    new_roadmap["work_packages"] = work_packages

    route = f"SERIAL:{ep['id']}"
    provisional_state = copy.deepcopy(state)
    provisional_state["roadmap"]["revision"] = rplan["new_revision"]
    provisional_state["execution"] = {
        "lifecycle": "ACTIVE",
        "ep": ep["id"],
        "lease": lease_id,
        "route": route,
        "custody_epoch": 1,
    }
    provisional_state["delivery"] = copy.deepcopy(admission["delivery"])

    lease = build_native_lease(
        root,
        lease_id=lease_id,
        executor_id=lease_spec["executor_id"],
        method=lease_spec["method"],
        qualification=lease_spec.get("qualification"),
        owner_basis=lease_spec.get("owner_basis"),
        branch=lease_spec.get("branch"),
        state_override=provisional_state,
        ep_override=ep,
        current_lease_override=None,
        custody_epoch=1,
        recovery_after_seconds=int(
            lease_spec.get("recovery_after_seconds") or DEFAULT_RECOVERY_AFTER_SECONDS
        ),
        recovery_policy=str(lease_spec.get("recovery_policy") or "TAKEOVER_AFTER_EXPIRY"),
        base_ref=base_ref,
    )
    snapshot = build_snapshot(
        root,
        base_ref,
        state_override=provisional_state,
        roadmap_override=new_roadmap,
        ep_override=ep,
        lease_override=lease,
    )

    events = _events(root)
    event_suffixes = (
        ["-SUPERSEDED", "-OWNER", "-EP", "-LEASE"]
        if predecessor_lease is not None
        else ["-OWNER", "-EP", "-LEASE"]
    )
    ids = _transition_event_ids(
        root,
        event_id=event_id,
        issue_number=governing_issue,
        legacy_suffixes=event_suffixes,
    )
    _assert_event_ids_available(events, ids)
    offset = 0
    replacements = {
        str((state.get("roadmap") or {}).get("path")): yaml_bytes(new_roadmap),
        "relay/STATE.yaml": yaml_bytes(provisional_state),
        f"relay/WORK/{ep['id']}.yaml": yaml_bytes(ep),
        f"relay/LEASES/{lease_id}.yaml": yaml_bytes(lease),
        _snapshot_path(provisional_state): yaml_bytes(snapshot),
    }
    if predecessor_lease is not None:
        superseded = copy.deepcopy(predecessor_lease)
        superseded["state"] = "INVALIDATED"
        reasons = list((superseded.get("invalidation") or {}).get("reasons") or [])
        reasons.append(f"RECORDER_SUPERSEDED_BY_ADMISSION:{lease_id}")
        superseded["invalidation"] = {"reasons": list(dict.fromkeys(reasons))}
        replacements[f"relay/LEASES/{predecessor_lease_id}.yaml"] = yaml_bytes(superseded)
        events.append(_event(
            ids[0],
            "LEASE_REVOKED",
            actor,
            str(predecessor_lease_id),
            [tx_id, f"successor-lease:{lease_id}", "continuation:ADMISSION_SUPERSEDED"],
            {
                "successor_lease": lease_id,
                "successor_executor": lease_spec["executor_id"],
                "continuation": "ADMISSION_SUPERSEDED",
            },
        ))
        offset = 1

    events.extend([
        _event(
            ids[offset],
            "OWNER_TASK_ADMITTED",
            actor,
            wp_id,
            [
                tx_id,
                disposition,
                *rplan["basis"],
                canonical_digest(programme_reconciliation),
            ],
            {
                "roadmap_revision": rplan["new_revision"],
                "programme_parent_count": len(programme_reconciliation.get("parents") or []),
                "programme_frontier": list(programme_reconciliation.get("programme_frontier") or []),
                "selected_programme_frontier": programme_assessment.get("selected_programme_frontier"),
                "next_programme_frontier": programme_assessment.get("next_frontier"),
                "superseded_lease": predecessor_lease_id if predecessor_lease is not None else None,
            },
        ),
        _event(ids[offset + 1], "EP_CREATED", actor, ep["id"], [tx_id, wp_id, str((ep.get("basis") or {}).get("protocol_basis"))], {}),
        _event(ids[offset + 2], "LEASE_GRANTED", actor, lease_id, [tx_id, route, "continuation:NEW"], {
            "executor": lease_spec["executor_id"],
            "method": lease_spec["method"],
            "continuation": "NEW",
            "custody_epoch": 1,
            "superseded_lease": predecessor_lease_id if predecessor_lease is not None else None,
        }),
    ])
    replacements["relay/EVENTS.jsonl"] = jsonl_bytes(events)

    return execute(
        root,
        tx_id=tx_id,
        command="ADMIT_TASK",
        actor=actor,
        replacements=replacements,
        fail_after=fail_after,
    )


def activate_lease(
    root: Path,
    *,
    tx_id: str | None,
    event_id: str | None,
    lease_id: str | None,
    executor_id: str,
    actor: str,
    method: str,
    qualification: dict[str, Any] | None,
    owner_basis: dict[str, str] | None,
    branch: str | None,
    base_ref: str,
    recovery_takeover: bool = False,
    expected_custody_epoch: int | None = None,
    recovery_observed_at: str | None = None,
    recovery_after_seconds: int = DEFAULT_RECOVERY_AFTER_SECONDS,
    recovery_policy: str = "TAKEOVER_AFTER_EXPIRY",
    recovery_observation: dict[str, Any] | None = None,
    programme_issue_observations: list[dict[str, Any]] | None = None,
    selected_programme_ref: str | None = None,
    fail_after: int | None = None,
) -> dict[str, Any]:
    state, _ = _authority(root)
    _require_expected_custody_epoch(state, expected_custody_epoch)
    current_ep = _current_ep(root, state)
    governing_issue = issue_number_from_ep(current_ep)
    tx_id = _issue_scoped_id(
        root,
        kind="TX",
        value=tx_id,
        issue_number=governing_issue,
        label="transaction id",
    )
    lease_id = _issue_scoped_id(
        root,
        kind="LEASE",
        value=lease_id,
        issue_number=governing_issue,
        label="lease_id",
    )
    execution = state.get("execution") or {}
    old_lease_id = execution.get("lease")
    old_lease = load_yaml(root / "relay/LEASES" / f"{old_lease_id}.yaml") if old_lease_id else None
    if old_lease_id == lease_id:
        raise TransactionError("new lease id must differ from the current lease id")
    new_lease_path = root / "relay/LEASES" / f"{lease_id}.yaml"
    if new_lease_path.exists():
        raise TransactionError(f"new lease id already exists: {lease_id}")

    old_active = isinstance(old_lease, dict) and old_lease.get("state") == "ACTIVE"
    old_executor = str(((old_lease or {}).get("executor") or {}).get("id") or "")
    different_executor = bool(old_active and old_executor != executor_id)
    continuation = "NEW"
    handover_digest = None
    programme_reconciliation = assess_boundary(
        None,
        None,
        boundary="RECOVERY_TAKEOVER",
    )["reconciliation"]

    if different_executor:
        try:
            handover_digest = _require_fresh_handover(root, state, base_ref=base_ref)
        except TransactionError:
            # Recorder-first V3.1 automatically records a takeover when no fresh
            # handover exists. Lease age, material activity and provider terminal
            # evidence remain diagnostics in recovery_assessment, never blockers.
            recovery_assessment = recovery_eligibility(
                root,
                old_lease or {},
                ep=current_ep,
                base_ref=base_ref,
                observed_at=recovery_observed_at,
                terminal_observation=recovery_observation,
            )
            programme_assessment = _require_programme_boundary(
                (current_ep or {}).get("parent_issue"),
                programme_issue_observations,
                boundary="RECOVERY_TAKEOVER",
                selected_frontier_ref=selected_programme_ref,
            )
            programme_reconciliation = programme_assessment["reconciliation"]
            continuation = "RECOVERY"
        else:
            continuation = "HANDOFF"

    transfer_from = str(old_lease_id) if different_executor else None
    current_epoch = _custody_epoch(state)
    if current_epoch is None:
        current_epoch = int(((old_lease or {}).get("custody") or {}).get("epoch") or 0)
    new_epoch = current_epoch + 1
    new_lease = build_native_lease(
        root,
        lease_id=lease_id,
        executor_id=executor_id,
        method=method,
        qualification=qualification,
        owner_basis=owner_basis,
        branch=branch,
        replace_active_lease_id=transfer_from,
        custody_epoch=new_epoch,
        recovery_after_seconds=recovery_after_seconds,
        recovery_policy=recovery_policy,
        base_ref=base_ref,
    )

    replacements: dict[str, bytes] = {}
    transfer = bool(old_active and old_lease_id != lease_id)
    predecessor_event_type = None
    if transfer:
        predecessor = copy.deepcopy(old_lease)
        if different_executor and continuation == "RECOVERY":
            predecessor["state"] = "INVALIDATED"
            reasons = list((predecessor.get("invalidation") or {}).get("reasons") or [])
            reasons.append(f"RECOVERY_TAKEOVER_BY:{lease_id}")
            predecessor["invalidation"] = {"reasons": list(dict.fromkeys(reasons))}
            predecessor_event_type = "LEASE_REVOKED"
        else:
            predecessor["state"] = "RELEASED"
            predecessor_event_type = "LEASE_RELEASED"
        replacements[f"relay/LEASES/{old_lease_id}.yaml"] = yaml_bytes(predecessor)

    new_state = copy.deepcopy(state)
    new_state["execution"] = {
        "lifecycle": "ACTIVE",
        "ep": (new_lease.get("basis") or {}).get("ep_id"),
        "lease": lease_id,
        "route": new_lease.get("route"),
        "custody_epoch": new_epoch,
    }
    replacements[f"relay/LEASES/{lease_id}.yaml"] = yaml_bytes(new_lease)
    replacements["relay/STATE.yaml"] = yaml_bytes(new_state)
    snapshot = build_snapshot(root, base_ref, state_override=new_state, lease_override=new_lease)
    replacements[_snapshot_path(new_state)] = yaml_bytes(snapshot)

    events = _events(root)
    event_suffixes: list[str] = []
    if transfer:
        event_suffixes.append("-REL")
    if continuation == "HANDOFF":
        event_suffixes.append("-HANDOVER")
    elif continuation == "RECOVERY":
        event_suffixes.append("-RECOVERY")
    event_suffixes.append("")
    allocated = _transition_event_ids(
        root,
        event_id=event_id,
        issue_number=governing_issue,
        legacy_suffixes=event_suffixes,
    )
    event_index = 0
    predecessor_event_id = allocated[event_index] if transfer else None
    if transfer:
        event_index += 1
    transition_event_id = (
        allocated[event_index]
        if continuation in {"HANDOFF", "RECOVERY"}
        else None
    )
    if continuation in {"HANDOFF", "RECOVERY"}:
        event_index += 1
    granted_event_id = allocated[event_index]

    _assert_event_ids_available(
        events,
        [
            value
            for value in [predecessor_event_id, transition_event_id, granted_event_id]
            if value
        ],
    )
    if transfer:
        basis = [tx_id, f"successor-lease:{lease_id}", f"continuation:{continuation}"]
        if handover_digest:
            basis.append(handover_digest)
        events.append(_event(
            str(predecessor_event_id),
            str(predecessor_event_type),
            actor,
            str(old_lease_id),
            basis,
            {
                "successor_lease": lease_id,
                "successor_executor": executor_id,
                "continuation": continuation,
                "predecessor_handover": bool(handover_digest),
                "custody_epoch_before": current_epoch,
                "custody_epoch_after": new_epoch,
            },
        ))
    if continuation == "HANDOFF":
        events.append(_event(
            str(transition_event_id),
            "HANDOVER_ACCEPTED",
            actor,
            lease_id,
            [tx_id, str(old_lease_id), str(handover_digest), f"custody_epoch:{new_epoch}"],
            {
                "predecessor_lease": old_lease_id,
                "successor_lease": lease_id,
                "successor_executor": executor_id,
                "custody_epoch": new_epoch,
            },
        ))
    elif continuation == "RECOVERY":
        events.append(_event(
            str(transition_event_id),
            "RECOVERY_STARTED",
            actor,
            lease_id,
            [
                tx_id,
                str(old_lease_id),
                f"custody_epoch:{new_epoch}",
                canonical_digest(programme_reconciliation),
                *list(recovery_assessment.get("basis") or []),
            ],
            {
                "predecessor_lease": old_lease_id,
                "successor_lease": lease_id,
                "successor_executor": executor_id,
                "custody_epoch": new_epoch,
                "predecessor_handover": False,
                "programme_parent_count": len(programme_reconciliation.get("parents") or []),
                "programme_frontier": list(programme_reconciliation.get("programme_frontier") or []),
                "selected_programme_frontier": programme_assessment.get("selected_programme_frontier"),
                "next_programme_frontier": programme_assessment.get("next_frontier"),
                "recovery_reason": recovery_assessment.get("reason"),
                "terminal_observation_digest": recovery_assessment.get("terminal_observation_digest"),
            },
        ))
    events.append(_event(
        granted_event_id,
        "LEASE_GRANTED",
        actor,
        lease_id,
        [
            tx_id,
            str(new_lease.get("route")),
            f"continuation:{continuation}",
            *(
                [canonical_digest(programme_reconciliation)]
                if continuation == "RECOVERY"
                else []
            ),
        ],
        {
            "executor": executor_id,
            "method": method,
            "continuation": continuation,
            "predecessor_lease": old_lease_id if transfer else None,
            "predecessor_handover": bool(handover_digest),
            "custody_epoch": new_epoch,
        },
    ))
    replacements["relay/EVENTS.jsonl"] = jsonl_bytes(events)

    return execute(root, tx_id=tx_id, command="ACTIVATE_LEASE", actor=actor, replacements=replacements, fail_after=fail_after)


def renew_lease(
    root: Path,
    *,
    tx_id: str | None,
    event_id: str | None,
    actor: str,
    expected_custody_epoch: int,
    base_ref: str,
    renewed_at: str | None = None,
    fail_after: int | None = None,
) -> dict[str, Any]:
    state, _ = _authority(root)
    _require_expected_custody_epoch(state, expected_custody_epoch)
    ep = _current_ep(root, state)
    governing_issue = issue_number_from_ep(ep)
    tx_id = _issue_scoped_id(
        root,
        kind="TX",
        value=tx_id,
        issue_number=governing_issue,
        label="transaction id",
    )
    event_id = _transition_event_ids(
        root,
        event_id=event_id,
        issue_number=governing_issue,
        legacy_suffixes=[""],
    )[0]
    execution = state.get("execution") or {}
    lease_id = execution.get("lease")
    if not lease_id:
        raise TransactionError("no active lease to renew")
    lease = load_yaml(root / "relay/LEASES" / f"{lease_id}.yaml")
    if lease.get("state") != "ACTIVE":
        raise TransactionError("current lease is not ACTIVE")
    custody = lease.get("custody") or {}
    if int(custody.get("epoch") or -1) != int(expected_custody_epoch):
        raise TransactionError("lease custody epoch does not match STATE")
    if str(((lease.get("executor") or {}).get("id") or "")) != str(actor):
        raise TransactionError("only the current lease executor may renew custody liveness")
    try:
        normalized_basis = (
            material_activity_basis(root, ep, base_ref)
            if isinstance(ep, dict)
            else None
        )
        renewed = renew_copy(
            lease,
            renewed_at=renewed_at or _now(),
            activity_basis=normalized_basis,
        )
    except ValueError as exc:
        raise TransactionError(str(exc)) from exc
    snapshot = build_snapshot(root, base_ref, lease_override=renewed)
    events = _events(root)
    _assert_event_ids_available(events, [event_id])
    events.append(_event(
        event_id,
        "LEASE_RENEWED",
        actor,
        str(lease_id),
        [tx_id, f"custody_epoch:{expected_custody_epoch}"],
        {"renewed_at": renewed["custody"]["renewed_at"], "custody_epoch": expected_custody_epoch},
    ))
    return execute(
        root,
        tx_id=tx_id,
        command="RENEW_LEASE",
        actor=actor,
        replacements={
            f"relay/LEASES/{lease_id}.yaml": yaml_bytes(renewed),
            _snapshot_path(state): yaml_bytes(snapshot),
            "relay/EVENTS.jsonl": jsonl_bytes(events),
        },
        fail_after=fail_after,
    )

def release_lease(
    root: Path,
    *,
    tx_id: str | None,
    event_id: str | None,
    actor: str,
    reason: str = "HANDOFF",
    base_ref: str | None = None,
    expected_custody_epoch: int | None = None,
    fail_after: int | None = None,
) -> dict[str, Any]:
    if reason not in {"HANDOFF", "ADMINISTRATIVE"}:
        raise TransactionError("lease release reason must be HANDOFF or ADMINISTRATIVE")

    state, _ = _authority(root)
    _require_expected_custody_epoch(state, expected_custody_epoch)
    ep = _current_ep(root, state)
    governing_issue = issue_number_from_ep(ep)
    tx_id = _issue_scoped_id(
        root,
        kind="TX",
        value=tx_id,
        issue_number=governing_issue,
        label="transaction id",
    )
    event_id = _transition_event_ids(
        root,
        event_id=event_id,
        issue_number=governing_issue,
        legacy_suffixes=[""],
    )[0]
    execution = state.get("execution") or {}
    lease_id = execution.get("lease")
    if not lease_id:
        raise TransactionError("no active lease to release")
    lease_path = root / "relay/LEASES" / f"{lease_id}.yaml"
    lease = load_yaml(lease_path)
    if lease.get("state") != "ACTIVE":
        raise TransactionError("current lease is not ACTIVE")

    handover_digest = None
    if reason == "HANDOFF":
        try:
            handover_digest = _require_fresh_handover(root, state, base_ref=base_ref)
        except TransactionError:
            handover_digest = "RECORDER_ADVISORY:NO_FRESH_HANDOVER"

    released = copy.deepcopy(lease)
    released["state"] = "RELEASED"
    new_state = copy.deepcopy(state)
    new_execution = {"lifecycle": "IDLE", "ep": None, "lease": None, "route": None}
    if execution.get("custody_epoch") is not None:
        new_execution["custody_epoch"] = int(execution["custody_epoch"])
    new_state["execution"] = new_execution
    snapshot = build_snapshot(root, state_override=new_state)

    events = _events(root)
    _assert_event_ids_available(events, [event_id])
    basis = [tx_id, f"reason:{reason}"]
    if handover_digest:
        basis.append(handover_digest)
    events.append(_event(
        event_id,
        "LEASE_RELEASED",
        actor,
        str(lease_id),
        basis,
        {
            "reason": reason,
            "graceful": reason == "HANDOFF",
            "handover_context_digest": handover_digest,
        },
    ))

    return execute(
        root,
        tx_id=tx_id,
        command="RELEASE_LEASE",
        actor=actor,
        replacements={
            f"relay/LEASES/{lease_id}.yaml": yaml_bytes(released),
            "relay/STATE.yaml": yaml_bytes(new_state),
            _snapshot_path(new_state): yaml_bytes(snapshot),
            "relay/EVENTS.jsonl": jsonl_bytes(events),
        },
        fail_after=fail_after,
    )


def accept_checkpoint(
    root: Path,
    *,
    tx_id: str | None,
    event_id: str | None,
    actor: str,
    checkpoint_path: Path,
    base_ref: str,
    expected_custody_epoch: int | None = None,
    fail_after: int | None = None,
) -> dict[str, Any]:
    _require_action(root, "CHECKPOINT", base_ref=base_ref, expected_custody_epoch=expected_custody_epoch)
    state, _ = _authority(root)
    _require_expected_custody_epoch(state, expected_custody_epoch)

    checkpoint = copy.deepcopy(load_yaml(checkpoint_path))
    checkpoint_ep_id = str(checkpoint.get("ep") or "")
    ep_path = root / "relay/WORK" / f"{checkpoint_ep_id}.yaml"
    ep = load_yaml(ep_path) if checkpoint_ep_id and ep_path.exists() else _current_ep(root, state)
    governing_issue = issue_number_from_ep(ep) if isinstance(ep, dict) else _governing_issue_number(root, state)

    checkpoint["id"] = _issue_scoped_id(
        root,
        kind="CP",
        value=checkpoint.get("id"),
        issue_number=governing_issue,
        label="checkpoint id",
    )
    tx_id = _issue_scoped_id(
        root,
        kind="TX",
        value=tx_id,
        issue_number=governing_issue,
        label="transaction id",
    )
    event_id = _transition_event_ids(
        root,
        event_id=event_id,
        issue_number=governing_issue,
        legacy_suffixes=[""],
    )[0]

    errors = validate_schema("checkpoint", checkpoint, "CHECKPOINT")
    if errors:
        raise TransactionError("; ".join(errors))
    # Recorder-first V3.1 stores the checkpoint exactly as reported. PASS/FAIL,
    # quality, AC coverage and material drift remain evidence for readers; they
    # do not decide whether the record may be appended.

    cp_id = str(checkpoint.get("id"))
    target = f"relay/CHECKPOINTS/{cp_id}.yaml"
    if (root / target).exists():
        raise TransactionError(f"checkpoint id already exists and is immutable: {cp_id}")
    new_state = copy.deepcopy(state)
    new_state["accepted"]["checkpoint"] = cp_id
    snapshot = build_snapshot(root, base_ref, state_override=new_state, checkpoint_override=checkpoint)

    events = _events(root)
    _assert_event_ids_available(events, [event_id])
    events.append(_event(
        event_id,
        "CHECKPOINT_ACCEPTED",
        actor,
        cp_id,
        [tx_id, str(checkpoint.get("ep"))],
        {"material_head": (checkpoint.get("material_result") or {}).get("head")},
    ))

    replacements = {
        target: yaml_bytes(checkpoint),
        "relay/STATE.yaml": yaml_bytes(new_state),
        _snapshot_path(new_state): yaml_bytes(snapshot),
        "relay/EVENTS.jsonl": jsonl_bytes(events),
    }
    _add_automatic_liveness(root, state, actor, replacements, base_ref=base_ref)
    return execute(
        root,
        tx_id=tx_id,
        command="ACCEPT_CHECKPOINT",
        actor=actor,
        replacements=replacements,
        fail_after=fail_after,
    )


def resolve_control(
    root: Path,
    *,
    tx_id: str | None,
    event_id: str | None,
    actor: str,
    control_id: str,
    evidence: list[str],
    base_ref: str,
    expected_custody_epoch: int | None = None,
    fail_after: int | None = None,
) -> dict[str, Any]:
    state, controls = _authority(root)
    governing_issue = _governing_issue_number(root, state)
    tx_id = _issue_scoped_id(
        root,
        kind="TX",
        value=tx_id,
        issue_number=governing_issue,
        label="transaction id",
    )
    event_id = _transition_event_ids(
        root,
        event_id=event_id,
        issue_number=governing_issue,
        legacy_suffixes=[""],
    )[0]
    _require_expected_custody_epoch(state, expected_custody_epoch)
    matches = [item for item in controls.get("controls") or [] if item.get("id") == control_id]
    if len(matches) != 1:
        raise TransactionError(f"expected one control {control_id}; found {len(matches)}")
    item = matches[0]
    if item.get("state") != "OPEN":
        raise TransactionError(f"control {control_id} is not OPEN")
    evidence = [str(item).strip() for item in evidence if str(item).strip()]
    if not evidence:
        raise TransactionError("control resolution requires durable evidence")

    new_controls = copy.deepcopy(controls)
    for row in new_controls["controls"]:
        if row.get("id") == control_id:
            row["state"] = "RESOLVED"
            row["resolution"]["evidence"] = list(evidence)

    snapshot = build_snapshot(root, base_ref, controls_override=new_controls)
    events = _events(root)
    _assert_event_ids_available(events, [event_id])
    events.append(_event(event_id, "CONTROL_RESOLVED", actor, control_id, [tx_id, *evidence], {}))
    controls_path = str((state.get("controls") or {}).get("path"))

    replacements = {
        controls_path: yaml_bytes(new_controls),
        _snapshot_path(state): yaml_bytes(snapshot),
        "relay/EVENTS.jsonl": jsonl_bytes(events),
    }
    _add_automatic_liveness(root, state, actor, replacements, base_ref=base_ref)
    return execute(
        root,
        tx_id=tx_id,
        command="RESOLVE_CONTROL",
        actor=actor,
        replacements=replacements,
        fail_after=fail_after,
    )


def reconcile_roadmap(
    root: Path,
    *,
    tx_id: str | None,
    event_id: str | None,
    actor: str,
    reconciliation_path: Path,
    base_ref: str,
    expected_custody_epoch: int | None = None,
    change_delta_path: Path | None = None,
    fail_after: int | None = None,
) -> dict[str, Any]:
    state, _ = _authority(root)
    governing_issue = _governing_issue_number(root, state)
    tx_id = _issue_scoped_id(
        root,
        kind="TX",
        value=tx_id,
        issue_number=governing_issue,
        label="transaction id",
    )
    event_id = _transition_event_ids(
        root,
        event_id=event_id,
        issue_number=governing_issue,
        legacy_suffixes=[""],
    )[0]
    _require_expected_custody_epoch(state, expected_custody_epoch)
    roadmap_path = str((state.get("roadmap") or {}).get("path"))
    current = load_yaml(root / roadmap_path)

    change_delta = None
    change_target = None
    if change_delta_path is not None:
        change_delta = load_yaml(change_delta_path)
        errors = validate_schema("change-delta", change_delta, "CHANGE_DELTA")
        if errors:
            raise TransactionError("; ".join(errors))
        # Recorder-first V3.1 records verification/authorization state as
        # provenance. It does not use those fields as roadmap-mutation gates.
        authorization = change_delta.get("authorization") or {}
        application = change_delta.get("application") or {}
        if application.get("status") != "NOT_APPLIED":
            raise TransactionError("CHANGE_DELTA is already applied or deferred")
        if application.get("expected_roadmap_revision") != (state.get("roadmap") or {}).get("revision"):
            raise TransactionError("CHANGE_DELTA expected roadmap revision is stale")
        if application.get("expected_state_digest") != canonical_digest(state):
            raise TransactionError("CHANGE_DELTA expected state digest is stale")
        change_target = f"relay/CHANGES/{change_delta['id']}.yaml"

    reconciliation = load_yaml(reconciliation_path)
    errors = validate_schema("roadmap-reconciliation", reconciliation, "ROADMAP_RECONCILIATION")
    if errors:
        raise TransactionError("; ".join(errors))
    if reconciliation.get("expected_revision") != current.get("revision"):
        raise TransactionError("roadmap reconciliation expected_revision does not match current ROADMAP")

    after = reconciliation.get("roadmap_after") or {}
    errors = validate_schema("roadmap", after, "ROADMAP_AFTER")
    if errors:
        raise TransactionError("; ".join(errors))

    disposition = str(reconciliation.get("disposition") or "")
    if disposition in {"NO_CHANGE", "OWNER_DECISION_REQUIRED"}:
        if canonical_digest(after) != canonical_digest(current):
            raise TransactionError(f"{disposition} cannot mutate ROADMAP")
    elif after.get("revision") == current.get("revision"):
        raise TransactionError("a roadmap-changing reconciliation requires a new ROADMAP revision")

    ep = _current_ep(root, state)
    if isinstance(ep, dict):
        work_package = str(ep.get("work_package") or "")
        after_ids = {str(row.get("id")) for row in after.get("work_packages") or [] if isinstance(row, dict)}
        if work_package and work_package not in after_ids:
            raise TransactionError("roadmap reconciliation cannot orphan the current EP work package")

    new_state = copy.deepcopy(state)
    new_state["roadmap"]["revision"] = after.get("revision")
    snapshot = build_snapshot(
        root,
        base_ref,
        state_override=new_state,
        roadmap_override=after,
        ep_override=ep,
    )

    events = _events(root)
    _assert_event_ids_available(events, [event_id])
    event_basis = [tx_id, *list(reconciliation.get("basis") or [])]
    if change_delta is not None:
        event_basis.append(str(change_delta.get("id")))
    events.append(_event(
        event_id,
        "ROADMAP_RECONCILED",
        actor,
        str(after.get("revision")),
        event_basis,
        {
            "disposition": disposition,
            "from_revision": current.get("revision"),
            "to_revision": after.get("revision"),
            "ep": (state.get("execution") or {}).get("ep"),
            "checkpoint": (state.get("accepted") or {}).get("checkpoint"),
            "change_delta": (change_delta or {}).get("id"),
        },
    ))

    replacements = {
        roadmap_path: yaml_bytes(after),
        "relay/STATE.yaml": yaml_bytes(new_state),
        _snapshot_path(new_state): yaml_bytes(snapshot),
        "relay/EVENTS.jsonl": jsonl_bytes(events),
    }
    if change_delta is not None and change_target is not None:
        applied_delta = copy.deepcopy(change_delta)
        applied_delta["application"]["status"] = "APPLIED"
        applied_delta["application"]["roadmap_before"] = str(current.get("revision"))
        applied_delta["application"]["roadmap_after"] = str(after.get("revision"))
        applied_delta["application"]["event"] = event_id
        replacements[change_target] = yaml_bytes(applied_delta)

    _add_automatic_liveness(root, state, actor, replacements, base_ref=base_ref)
    return execute(
        root,
        tx_id=tx_id,
        command="RECONCILE_ROADMAP",
        actor=actor,
        replacements=replacements,
        fail_after=fail_after,
    )

# A Buddy message is a transaction-recorded Markdown observation, NOT execution
# admission, accepted TASK_EVIDENCE, independent-context attestation or a handover.

def publish_buddy_markdown(
    root: Path,
    *,
    issue_number: int,
    tx_id: str,
    stage: str,
    actor: str,
    markdown: bytes,
    fail_after: int | None = None,
) -> dict[str, Any]:
    """Immutable issue-scoped Markdown inside the EXISTING Relay transaction log.

    This intentionally does not read/write global relay/STATE, derive P/E/D, inspect
    Agent A's private context, grant a new lease or assert that stage visibility
    was externally isolated. Stage admission must be verified separately.
    """
    if isinstance(issue_number, bool) or not isinstance(issue_number, int) or issue_number < 1:
        raise TransactionError("BUDDY_ISSUE_REQUIRED: use a positive governed issue number")
    if stage not in BUDDY_MESSAGE_STAGES:
        raise TransactionError("BUDDY_STAGE_INVALID")
    if not isinstance(actor, str) or not actor.strip():
        raise TransactionError("BUDDY_ACTOR_REQUIRED")
    if not isinstance(tx_id, str) or re.fullmatch(
        rf"TX\.{issue_number}\.[1-9][0-9]*", tx_id
    ) is None:
        raise TransactionError("BUDDY_TX_ID_MUST_MATCH_ISSUE")
    if not isinstance(markdown, bytes) or len(markdown) < 4 or len(markdown) > 2_000_000:
        raise TransactionError("BUDDY_MARKDOWN_BYTES_INVALID")
    try:
        decoded = markdown.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TransactionError("BUDDY_MARKDOWN_UTF8_REQUIRED") from exc
    if not decoded.startswith("# ") or "\x00" in decoded:
        raise TransactionError("BUDDY_MARKDOWN_HEADING_REQUIRED")

    relative = (
        f"relay/CONTINUITY/episodes/ISSUE-{issue_number}/messages/"
        f"{tx_id}-{stage}.md"
    )
    target = root / relative
    if target.exists() or target.is_symlink():
        raise TransactionError("BUDDY_MESSAGE_IMMUTABLE: existing target cannot be replaced")
    # No implicit writer/lease transfer. The explicit transaction manifest provides
    # a content digest and author claim, subject to the external provider readback.
    result = execute(
        root,
        tx_id=tx_id,
        command="PUBLISH_BUDDY_MARKDOWN",
        actor=actor,
        replacements={relative: markdown},
        fail_after=fail_after,
    )
    if result["status"] != "COMMITTED" or target.read_bytes() != markdown:
        raise TransactionError("BUDDY_MESSAGE_READBACK_MISMATCH")
    result["message_path"] = relative
    result["message_sha256"] = "sha256:" + hashlib.sha256(markdown).hexdigest()
    result["admission"] = "NOT_ATTESTED_BY_MESSAGE_TRANSPORT"
    return result


def publish_handover(
    root: Path,
    *,
    tx_id: str | None,
    event_id: str | None,
    actor: str,
    base_ref: str,
    expected_custody_epoch: int | None = None,
    fail_after: int | None = None,
) -> dict[str, Any]:
    _require_action(root, "HANDOVER", expected_custody_epoch=expected_custody_epoch)
    state, _ = _authority(root)
    governing_issue = _governing_issue_number(root, state)
    tx_id = _issue_scoped_id(
        root,
        kind="TX",
        value=tx_id,
        issue_number=governing_issue,
        label="transaction id",
    )
    event_id = _transition_event_ids(
        root,
        event_id=event_id,
        issue_number=governing_issue,
        legacy_suffixes=[""],
    )[0]
    _require_expected_custody_epoch(state, expected_custody_epoch)

    # Recorder-first V3.1 prefers a planned/frozen handover when available, but
    # never blocks publication because the plan is missing or stale.
    try:
        context_digest = _require_fresh_handover(
            root,
            state,
            base_ref=base_ref,
            require_published=False,
        )
        context = load_yaml(root / "relay/GENERATED/HANDOVER_CONTEXT.yaml")
        learning = context.get("accumulated_learning") or {}
        task_meta = learning.get("task_snapshot") or {}
        improvement_meta = learning.get("improvement_view") or {}
        task_snapshot = task_meta.get("value")
        improvement_view = improvement_meta.get("value")
        if not isinstance(task_snapshot, dict) or not isinstance(improvement_view, dict):
            raise TransactionError("planned handover read models unavailable")
    except TransactionError as exc:
        context_digest = "RECORDER_ADVISORY:NO_FRESH_PLANNED_HANDOVER"
        task_snapshot = build_task(root, base_ref)
        improvement_view = build_improvement(root)

    snapshot = build_snapshot(root, base_ref)
    checkpoint = _current_checkpoint(root, state)
    handover = render_handover(snapshot, checkpoint, task_snapshot, improvement_view).encode("utf-8")
    events = _events(root)
    _assert_event_ids_available(events, [event_id])
    events.append(_event(
        event_id,
        "HANDOVER_PUBLISHED",
        actor,
        str((state.get("execution") or {}).get("ep") or (state.get("accepted") or {}).get("checkpoint") or "relay"),
        [tx_id, _snapshot_path(state), context_digest],
        {
            "artifact": "relay/GENERATED/HANDOVER.md",
            "context_digest": context_digest,
        },
    ))
    replacements = {
        _snapshot_path(state): yaml_bytes(snapshot),
        "relay/GENERATED/HANDOVER.md": handover,
        "relay/EVENTS.jsonl": jsonl_bytes(events),
    }
    _add_automatic_liveness(root, state, actor, replacements, base_ref=base_ref)
    return execute(
        root,
        tx_id=tx_id,
        command="PUBLISH_HANDOVER",
        actor=actor,
        replacements=replacements,
        fail_after=fail_after,
    )


def record_recovery_reconstructed(
    root: Path,
    *,
    tx_id: str | None,
    event_id: str | None,
    actor: str,
    evidence: list[str],
    expected_custody_epoch: int,
    fail_after: int | None = None,
) -> dict[str, Any]:
    state, _ = _authority(root)
    governing_issue = _governing_issue_number(root, state)
    tx_id = _issue_scoped_id(
        root,
        kind="TX",
        value=tx_id,
        issue_number=governing_issue,
        label="transaction id",
    )
    event_id = _transition_event_ids(
        root,
        event_id=event_id,
        issue_number=governing_issue,
        legacy_suffixes=[""],
    )[0]
    _require_expected_custody_epoch(state, expected_custody_epoch)
    execution = state.get("execution") or {}
    lease_id = execution.get("lease")
    events = _events(root)
    started = any(
        item.get("type") == "RECOVERY_STARTED"
        and str((item.get("details") or {}).get("successor_lease") or item.get("subject")) == str(lease_id)
        for item in events
    )
    evidence = [str(item).strip() for item in evidence if str(item).strip()]
    reconstruction_basis = [tx_id, *evidence]
    if expected_custody_epoch is not None:
        reconstruction_basis.append(f"custody_epoch:{expected_custody_epoch}")
    if not started:
        reconstruction_basis.append("RECORDER_ADVISORY:NO_RECOVERY_STARTED")
    if not evidence:
        reconstruction_basis.append("RECORDER_ADVISORY:NO_RECONSTRUCTION_EVIDENCE")
    _assert_event_ids_available(events, [event_id])
    events.append(_event(
        event_id,
        "RECOVERY_RECONSTRUCTED",
        actor,
        str(lease_id or execution.get("ep") or "relay"),
        reconstruction_basis,
        {
            "ep": execution.get("ep"),
            "custody_epoch": expected_custody_epoch,
            "evidence_count": len(evidence),
            "recovery_started_observed": started,
        },
    ))
    replacements = {"relay/EVENTS.jsonl": jsonl_bytes(events)}
    _add_automatic_liveness(root, state, actor, replacements)
    return execute(
        root,
        tx_id=tx_id,
        command="RECORD_RECOVERY_RECONSTRUCTED",
        actor=actor,
        replacements=replacements,
        fail_after=fail_after,
    )


def record_change_hypothesis(
    root: Path,
    *,
    tx_id: str | None,
    event_id: str | None,
    actor: str,
    change_id: str | None,
    statement: str,
    basis: list[str],
    process: str = "PROMPT_1",
    expected_custody_epoch: int | None = None,
    fail_after: int | None = None,
) -> dict[str, Any]:
    state, _ = _authority(root)
    _require_expected_custody_epoch(state, expected_custody_epoch)
    governing_issue = _governing_issue_number(root, state)
    change_id = _issue_scoped_id(
        root,
        kind="CHANGE",
        value=change_id,
        issue_number=governing_issue,
        label="change_id",
    )
    tx_id = _issue_scoped_id(
        root,
        kind="TX",
        value=tx_id,
        issue_number=governing_issue,
        label="transaction id",
    )
    event_id = _transition_event_ids(
        root,
        event_id=event_id,
        issue_number=governing_issue,
        legacy_suffixes=[""],
    )[0]
    statement = statement.strip()
    basis = [str(item).strip() for item in basis if str(item).strip()]
    if not statement or not basis:
        raise TransactionError("change hypothesis requires statement and durable basis")
    target = root / "relay/CHANGES" / f"{change_id}.yaml"
    if target.exists():
        raise TransactionError(f"change delta already exists: {change_id}")
    ep = _current_ep(root, state)
    parent = (ep or {}).get("parent_issue") or {}
    delta = {
        "schema_version": "relay-v3.1-change-delta",
        "id": change_id,
        "authority": "GOVERNED_CHANGE_DELTA",
        "hypothesis": {
            "statement": statement,
            "discovered_by": {"process": process, "actor": actor},
            "basis": basis,
        },
        "verification": {
            "status": "PENDING",
            "verified_by": None,
            "evidence": [],
            "falsifiers_checked": [],
        },
        "proposal": None,
        "authorization": {
            "required": "UNKNOWN",
            "status": "PENDING",
            "owner_basis": None,
        },
        "application": {
            "status": "NOT_APPLIED",
            "expected_roadmap_revision": str((state.get("roadmap") or {}).get("revision")),
            "expected_state_digest": canonical_digest(state),
            "roadmap_before": None,
            "roadmap_after": None,
            "source_issue": parent.get("number"),
            "target_issue": None,
            "event": None,
        },
    }
    errors = validate_schema("change-delta", delta, "CHANGE_DELTA")
    if errors:
        raise TransactionError("; ".join(errors))
    events = _events(root)
    _assert_event_ids_available(events, [event_id])
    events.append(_event(
        event_id,
        "CHANGE_HYPOTHESIS_RECORDED",
        actor,
        change_id,
        [tx_id, *basis],
        {"process": process, "ep": (ep or {}).get("id"), "work_package": (ep or {}).get("work_package")},
    ))
    replacements = {
        f"relay/CHANGES/{change_id}.yaml": yaml_bytes(delta),
        "relay/EVENTS.jsonl": jsonl_bytes(events),
    }
    _add_automatic_liveness(root, state, actor, replacements)
    return execute(
        root,
        tx_id=tx_id,
        command="RECORD_CHANGE_HYPOTHESIS",
        actor=actor,
        replacements=replacements,
        fail_after=fail_after,
    )


def verify_change_delta(
    root: Path,
    *,
    tx_id: str | None,
    event_id: str | None,
    actor: str,
    change_id: str,
    status: str,
    evidence: list[str],
    falsifiers_checked: list[str],
    expected_custody_epoch: int | None = None,
    fail_after: int | None = None,
) -> dict[str, Any]:
    state, _ = _authority(root)
    _require_expected_custody_epoch(state, expected_custody_epoch)
    path = root / "relay/CHANGES" / f"{change_id}.yaml"
    delta = load_yaml(path)
    errors = validate_schema("change-delta", delta, "CHANGE_DELTA")
    if errors:
        raise TransactionError("; ".join(errors))
    governing_issue = _governing_issue_for_change(root, state, change_id, delta)
    tx_id = _issue_scoped_id(
        root,
        kind="TX",
        value=tx_id,
        issue_number=governing_issue,
        label="transaction id",
    )
    event_id = _transition_event_ids(
        root,
        event_id=event_id,
        issue_number=governing_issue,
        legacy_suffixes=[""],
    )[0]
    status = status.upper()
    if status not in {"CONFIRMED", "REJECTED"}:
        raise TransactionError("change verification status must be CONFIRMED or REJECTED")
    evidence = [str(item).strip() for item in evidence if str(item).strip()]
    falsifiers_checked = [str(item).strip() for item in falsifiers_checked if str(item).strip()]
    updated = copy.deepcopy(delta)
    updated["verification"] = {
        "status": status,
        "verified_by": {"process": "PROMPT_2", "actor": actor},
        "evidence": evidence,
        "falsifiers_checked": falsifiers_checked,
    }
    errors = validate_schema("change-delta", updated, "CHANGE_DELTA")
    if errors:
        raise TransactionError("; ".join(errors))
    events = _events(root)
    _assert_event_ids_available(events, [event_id])
    events.append(_event(
        event_id,
        "CHANGE_VERIFIED" if status == "CONFIRMED" else "CHANGE_REJECTED",
        actor,
        change_id,
        [tx_id, *evidence, *falsifiers_checked],
        {"status": status},
    ))
    replacements = {
        f"relay/CHANGES/{change_id}.yaml": yaml_bytes(updated),
        "relay/EVENTS.jsonl": jsonl_bytes(events),
    }
    _add_automatic_liveness(root, state, actor, replacements)
    return execute(
        root,
        tx_id=tx_id,
        command="VERIFY_CHANGE_DELTA",
        actor=actor,
        replacements=replacements,
        fail_after=fail_after,
    )


def propose_change_delta(
    root: Path,
    *,
    tx_id: str | None,
    event_id: str | None,
    actor: str,
    change_id: str,
    proposal_path: Path,
    authorization_required: str,
    expected_custody_epoch: int | None = None,
    fail_after: int | None = None,
) -> dict[str, Any]:
    state, _ = _authority(root)
    _require_expected_custody_epoch(state, expected_custody_epoch)
    path = root / "relay/CHANGES" / f"{change_id}.yaml"
    delta = load_yaml(path)
    errors = validate_schema("change-delta", delta, "CHANGE_DELTA")
    if errors:
        raise TransactionError("; ".join(errors))
    governing_issue = _governing_issue_for_change(root, state, change_id, delta)
    tx_id = _issue_scoped_id(
        root,
        kind="TX",
        value=tx_id,
        issue_number=governing_issue,
        label="transaction id",
    )
    event_id = _transition_event_ids(
        root,
        event_id=event_id,
        issue_number=governing_issue,
        legacy_suffixes=[""],
    )[0]
    if delta.get("proposal") is not None:
        raise TransactionError("change delta already has a proposal")
    proposal = load_yaml(proposal_path)
    if not isinstance(proposal, dict):
        raise TransactionError("change proposal must be a mapping")
    authorization_required = authorization_required.upper()
    if authorization_required not in {"NONE", "OWNER"}:
        raise TransactionError("authorization_required must be NONE or OWNER")
    updated = copy.deepcopy(delta)
    updated["proposal"] = proposal
    updated["authorization"] = {
        "required": authorization_required,
        "status": "NOT_REQUIRED" if authorization_required == "NONE" else "PENDING",
        "owner_basis": None,
    }
    errors = validate_schema("change-delta", updated, "CHANGE_DELTA")
    if errors:
        raise TransactionError("; ".join(errors))
    events = _events(root)
    _assert_event_ids_available(events, [event_id])
    events.append(_event(
        event_id,
        "CHANGE_DELTA_PROPOSED",
        actor,
        change_id,
        [tx_id, str(proposal.get("disposition"))],
        {"disposition": proposal.get("disposition"), "authorization_required": authorization_required},
    ))
    replacements = {
        f"relay/CHANGES/{change_id}.yaml": yaml_bytes(updated),
        "relay/EVENTS.jsonl": jsonl_bytes(events),
    }
    _add_automatic_liveness(root, state, actor, replacements)
    return execute(
        root,
        tx_id=tx_id,
        command="PROPOSE_CHANGE_DELTA",
        actor=actor,
        replacements=replacements,
        fail_after=fail_after,
    )


def authorize_change_delta(
    root: Path,
    *,
    tx_id: str | None,
    event_id: str | None,
    actor: str,
    change_id: str,
    granted: bool,
    direct_utterance_digest: str,
    session_timestamp: str,
    fail_after: int | None = None,
) -> dict[str, Any]:
    state, _ = _authority(root)
    path = root / "relay/CHANGES" / f"{change_id}.yaml"
    delta = load_yaml(path)
    errors = validate_schema("change-delta", delta, "CHANGE_DELTA")
    if errors:
        raise TransactionError("; ".join(errors))
    governing_issue = _governing_issue_for_change(root, state, change_id, delta)
    tx_id = _issue_scoped_id(
        root,
        kind="TX",
        value=tx_id,
        issue_number=governing_issue,
        label="transaction id",
    )
    event_id = _transition_event_ids(
        root,
        event_id=event_id,
        issue_number=governing_issue,
        legacy_suffixes=[""],
    )[0]
    authorization = delta.get("authorization") or {}
    if not direct_utterance_digest.strip() or not session_timestamp.strip():
        raise TransactionError("Owner authorization requires direct utterance digest and session timestamp")
    updated = copy.deepcopy(delta)
    updated["authorization"] = {
        "required": "OWNER",
        "status": "GRANTED" if granted else "DENIED",
        "owner_basis": {
            "direct_utterance_digest": direct_utterance_digest,
            "session_timestamp": session_timestamp,
        },
    }
    errors = validate_schema("change-delta", updated, "CHANGE_DELTA")
    if errors:
        raise TransactionError("; ".join(errors))
    events = _events(root)
    _assert_event_ids_available(events, [event_id])
    events.append(_event(
        event_id,
        "CHANGE_AUTHORIZED",
        actor,
        change_id,
        [tx_id, direct_utterance_digest],
        {"status": updated["authorization"]["status"]},
    ))
    return execute(
        root,
        tx_id=tx_id,
        command="AUTHORIZE_CHANGE_DELTA",
        actor=actor,
        replacements={
            f"relay/CHANGES/{change_id}.yaml": yaml_bytes(updated),
            "relay/EVENTS.jsonl": jsonl_bytes(events),
        },
        fail_after=fail_after,
    )

def export_local_execution(
    root: Path,
    *,
    tx_id: str | None,
    event_id: str | None,
    actor: str,
    base_ref: str,
    mode: str = "VALIDATE_ONLY",
    commands: list[str] | None = None,
    return_sub_issue: str | None = None,
    expected_custody_epoch: int | None = None,
    fail_after: int | None = None,
) -> dict[str, Any]:
    _require_action(root, "LOCAL_EXECUTION_EXPORT", expected_custody_epoch=expected_custody_epoch)
    state, _ = _authority(root)
    governing_issue = _governing_issue_number(root, state)
    tx_id = _issue_scoped_id(
        root,
        kind="TX",
        value=tx_id,
        issue_number=governing_issue,
        label="transaction id",
    )
    event_id = _transition_event_ids(
        root,
        event_id=event_id,
        issue_number=governing_issue,
        legacy_suffixes=[""],
    )[0]
    _require_expected_custody_epoch(state, expected_custody_epoch)
    snapshot = build_snapshot(root, base_ref)
    ep = _current_ep(root, state)
    checkpoint = _current_checkpoint(root, state)
    if ep is None and isinstance(checkpoint, dict) and checkpoint.get("ep"):
        ep = load_yaml(root / "relay/WORK" / f"{checkpoint['ep']}.yaml")
    local_request_id = (
        allocate_next_id(root, kind="LOCAL", root=governing_issue)
        if governing_issue is not None
        else None
    )
    package = build_local_execution(
        root,
        snapshot,
        ep,
        checkpoint,
        mode=mode,
        commands=commands,
        return_sub_issue=return_sub_issue,
        request_id=local_request_id,
    )
    request_md = render_local_execution_request(package).encode("utf-8")
    events = _events(root)
    _assert_event_ids_available(events, [event_id])
    events.append(_event(
        event_id,
        "LOCAL_EXECUTION_EXPORTED",
        actor,
        str((state.get("execution") or {}).get("ep") or "relay"),
        [tx_id, _snapshot_path(state)],
        {
            "artifacts": [
                "relay/GENERATED/LOCAL_EXECUTION.yaml",
                "relay/GENERATED/LOCAL_EXECUTION.md",
            ],
            "request_id": (package.get("request") or {}).get("id"),
            "mode": mode,
            "return_sub_issue": (package.get("provider_return") or {}).get("target_sub_issue"),
        },
    ))
    replacements = {
        _snapshot_path(state): yaml_bytes(snapshot),
        "relay/GENERATED/LOCAL_EXECUTION.yaml": yaml_bytes(package),
        "relay/GENERATED/LOCAL_EXECUTION.md": request_md,
        "relay/EVENTS.jsonl": jsonl_bytes(events),
    }
    _add_automatic_liveness(root, state, actor, replacements, base_ref=base_ref)
    return execute(
        root,
        tx_id=tx_id,
        command="EXPORT_LOCAL_EXECUTION",
        actor=actor,
        replacements=replacements,
        fail_after=fail_after,
    )


def accept_local_execution_result(
    root: Path,
    *,
    tx_id: str | None,
    event_id: str | None,
    actor: str,
    result_path: Path,
    fail_after: int | None = None,
) -> dict[str, Any]:
    state, _ = _authority(root)
    governing_issue = _governing_issue_number(root, state)
    tx_id = _issue_scoped_id(
        root,
        kind="TX",
        value=tx_id,
        issue_number=governing_issue,
        label="transaction id",
    )
    event_id = _transition_event_ids(
        root,
        event_id=event_id,
        issue_number=governing_issue,
        legacy_suffixes=[""],
    )[0]
    package_path = root / "relay/GENERATED/LOCAL_EXECUTION.yaml"
    if not package_path.exists():
        raise TransactionError("local execution result requires an exported LOCAL_EXECUTION package")
    package = load_yaml(package_path)
    package_errors = validate_schema("local-execution", package, "LOCAL_EXECUTION")
    if package_errors:
        raise TransactionError("; ".join(package_errors))

    result = load_yaml(result_path)
    result_errors = validate_schema("local-execution-result", result, "LOCAL_EXECUTION_RESULT")
    if result_errors:
        raise TransactionError("; ".join(result_errors))

    request = package.get("request") or {}
    if result.get("request_id") != request.get("id"):
        raise TransactionError("local execution result request_id does not match the active exported request")

    required_head = str(((request.get("exact_basis") or {}).get("material_head")) or "")
    observed_head = str(result.get("observed_head") or "")
    status = str(result.get("status") or "")
    if status == "HEAD_MISMATCH":
        if observed_head == required_head:
            raise TransactionError("HEAD_MISMATCH result must report a different observed_head")
    elif observed_head != required_head:
        raise TransactionError("local execution result observed_head does not match the exported exact basis")

    result_digest = canonical_digest(result)
    digest_token = result_digest.split(":", 1)[-1]
    request_id = str(request.get("id"))
    evidence_rel = f"relay/EVIDENCE/local/{request_id}/{digest_token}.yaml"
    evidence_path = root / evidence_rel
    if evidence_path.exists():
        raise TransactionError(
            f"LOCAL_EXECUTION_EVIDENCE_ALREADY_EXISTS: immutable result receipt already exists at {evidence_rel}"
        )

    events = _events(root)
    _assert_event_ids_available(events, [event_id])
    events.append(_event(
        event_id,
        "LOCAL_EXECUTION_RETURNED",
        actor,
        request_id,
        [
            tx_id,
            request_id,
            str((package.get("generated_from") or {}).get("snapshot_digest")),
            evidence_rel,
            result_digest,
        ],
        {
            "status": status,
            "observed_head": observed_head,
            "required_head": required_head,
            "evidence_path": evidence_rel,
            "evidence_digest": result_digest,
        },
    ))

    return execute(
        root,
        tx_id=tx_id,
        command="IMPORT_LOCAL_EXECUTION_RESULT",
        actor=actor,
        replacements={
            evidence_rel: yaml_bytes(result),
            "relay/GENERATED/LOCAL_EXECUTION_RESULT.yaml": yaml_bytes(result),
            "relay/EVENTS.jsonl": jsonl_bytes(events),
        },
        fail_after=fail_after,
    )

def sync_delivery(
    root: Path,
    *,
    tx_id: str | None,
    event_id: str | None,
    actor: str,
    observation_path: Path,
    fail_after: int | None = None,
) -> dict[str, Any]:
    state, _ = _authority(root)
    governing_issue = _governing_issue_number(root, state)
    tx_id = _issue_scoped_id(
        root,
        kind="TX",
        value=tx_id,
        issue_number=governing_issue,
        label="transaction id",
    )
    event_id = _transition_event_ids(
        root,
        event_id=event_id,
        issue_number=governing_issue,
        legacy_suffixes=[""],
    )[0]
    delivery = state.get("delivery") or {}
    expected = delivery.get("primary_vehicle")
    if delivery.get("required") is not True or not isinstance(expected, dict):
        raise TransactionError("STATE has no required primary delivery vehicle")
    observation = load_yaml(observation_path)
    errors = validate_schema("delivery-status", observation, "DELIVERY_STATUS")
    if errors:
        raise TransactionError("; ".join(errors))
    if observation.get("vehicle") != expected:
        raise TransactionError("provider readback vehicle does not match STATE.delivery.primary_vehicle")
    events = _events(root)
    _assert_event_ids_available(events, [event_id])
    events.append(_event(
        event_id,
        "DELIVERY_SYNCED",
        actor,
        f"{expected.get('kind')}:{expected.get('number')}",
        [tx_id, str(observation.get("provider_ref"))],
        {"lifecycle": observation.get("lifecycle")},
    ))
    replacements = {
        "relay/GENERATED/DELIVERY_STATUS.yaml": yaml_bytes(observation),
        "relay/EVENTS.jsonl": jsonl_bytes(events),
    }
    _add_automatic_liveness(root, state, actor, replacements)
    return execute(
        root,
        tx_id=tx_id,
        command="SYNC_DELIVERY",
        actor=actor,
        replacements=replacements,
        fail_after=fail_after,
    )


def close_task(
    root: Path,
    *,
    tx_id: str | None,
    event_id: str | None,
    actor: str,
    parent_issue_observation: dict[str, Any] | None = None,
    expected_custody_epoch: int | None = None,
    fail_after: int | None = None,
) -> dict[str, Any]:
    _require_action(root, "CLOSE_TASK", expected_custody_epoch=expected_custody_epoch)
    state, _ = _authority(root)
    _require_expected_custody_epoch(state, expected_custody_epoch)
    governing_issue = _governing_issue_number(root, state)
    tx_id = _issue_scoped_id(
        root,
        kind="TX",
        value=tx_id,
        issue_number=governing_issue,
        label="transaction id",
    )
    _require_final_reconciliation(
        root,
        state,
        parent_issue_observation=parent_issue_observation,
    )

    delivery = state.get("delivery") or {}
    vehicle = delivery.get("primary_vehicle")
    # Delivery/provider state is recorded elsewhere and never blocks closing the
    # local execution record.

    execution = state.get("execution") or {}
    lease_id = execution.get("lease")
    lease = load_yaml(root / "relay/LEASES" / f"{lease_id}.yaml") if lease_id else None
    new_state = copy.deepcopy(state)
    terminal_execution = {"lifecycle": "TERMINAL", "ep": None, "lease": None, "route": None}
    if execution.get("custody_epoch") is not None:
        terminal_execution["custody_epoch"] = int(execution["custody_epoch"])
    new_state["execution"] = terminal_execution
    snapshot = build_snapshot(root, state_override=new_state)

    replacements: dict[str, bytes] = {
        "relay/STATE.yaml": yaml_bytes(new_state),
        _snapshot_path(new_state): yaml_bytes(snapshot),
    }
    if lease and lease.get("state") == "ACTIVE":
        released = copy.deepcopy(lease)
        released["state"] = "RELEASED"
        replacements[f"relay/LEASES/{lease_id}.yaml"] = yaml_bytes(released)

    events = _events(root)
    has_active_lease = bool(lease and lease.get("state") == "ACTIVE")
    transition_ids = _transition_event_ids(
        root,
        event_id=event_id,
        issue_number=governing_issue,
        legacy_suffixes=["-REL", ""] if has_active_lease else [""],
    )
    release_event_id = transition_ids[0] if has_active_lease else None
    close_event_id = transition_ids[1] if has_active_lease else transition_ids[0]
    _assert_event_ids_available(events, [x for x in [release_event_id, close_event_id] if x])
    if release_event_id:
        events.append(_event(str(release_event_id), "LEASE_RELEASED", actor, str(lease_id), [tx_id, "close-task"], {
            "reason": "CLOSE_TASK",
            "graceful": True,
        }))
    events.append(_event(
        close_event_id,
        "TASK_CLOSED",
        actor,
        str((state.get("accepted") or {}).get("checkpoint") or "relay"),
        [tx_id],
        {
            "delivery_required": bool(delivery.get("required")),
            "roadmap_reconciled": True,
            "parent_issue_reconciled": True,
        },
    ))
    replacements["relay/EVENTS.jsonl"] = jsonl_bytes(events)
    return execute(root, tx_id=tx_id, command="CLOSE_TASK", actor=actor, replacements=replacements, fail_after=fail_after)

def _add_start_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--tx-id",
        help="Explicit transaction ID. Omit to allocate TX.<issue>.<serial> from the governing EP issue.",
    )
    parser.add_argument(
        "--event-id",
        help="Explicit legacy event base ID. Omit to allocate canonical EVT.<issue>.<serial> IDs.",
    )
    parser.add_argument(
        "--lease-id",
        help="Explicit lease ID. Omit to allocate LEASE.<issue>.<serial> from the governing EP issue.",
    )
    parser.add_argument("--executor-id", required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--method", choices=["DETERMINISTIC", "QUALIFIED", "OWNER_OVERRIDE"], required=True)
    parser.add_argument("--qualification")
    parser.add_argument("--owner-utterance-digest")
    parser.add_argument("--owner-session-timestamp")
    parser.add_argument("--branch")
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--expected-custody-epoch", type=int)
    parser.add_argument("--recovery-observed-at")
    parser.add_argument(
        "--recovery-after-seconds",
        type=int,
        default=DEFAULT_RECOVERY_AFTER_SECONDS,
    )
    parser.add_argument("--recovery-policy", choices=["MANUAL_ONLY", "TAKEOVER_AFTER_EXPIRY"], default="TAKEOVER_AFTER_EXPIRY")
    parser.add_argument(
        "--recovery-takeover",
        action="store_true",
        help="Explicitly invalidate abandoned predecessor custody when no valid handover exists.",
    )
    parser.add_argument(
        "--recovery-observation",
        help="Provider/session termination observation YAML bound to the predecessor lease/epoch.",
    )
    parser.add_argument(
        "--programme-issue-observation",
        action="append",
        default=[],
        help="Provider observation for one reconciled programme parent; repeat in intended programme order.",
    )
    parser.add_argument(
        "--selected-programme-ref",
        help="Explicit Owner/ROADMAP selected programme parent ref (for example owner/repo#123).",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Engineering Relay V3.1 transactional command surface.")
    parser.add_argument("repo_root", nargs="?", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("recover")

    admit_task_parser = sub.add_parser("admit-task")
    admit_task_parser.add_argument(
        "--tx-id",
        help="Explicit transaction ID. Omit to allocate TX.<issue>.<serial> from the admitted EP parent issue.",
    )
    admit_task_parser.add_argument(
        "--event-id",
        help="Explicit legacy event base ID. Omit to allocate canonical EVT.<issue>.<serial> IDs.",
    )
    admit_task_parser.add_argument("--actor", required=True)
    admit_task_parser.add_argument("--admission", required=True)
    admit_task_parser.add_argument("--base-ref", required=True)
    admit_task_parser.add_argument(
        "--programme-issue-observation",
        action="append",
        default=[],
        help="Provider observation for one reconciled programme parent; repeat in intended programme order.",
    )
    admit_task_parser.add_argument(
        "--selected-programme-ref",
        help="Explicit Owner/ROADMAP selected programme parent ref.",
    )

    admit = sub.add_parser("admit")
    admit.add_argument("--lease-id", required=True)
    admit.add_argument("--executor-id", required=True)
    admit.add_argument("--method", choices=["DETERMINISTIC", "QUALIFIED", "OWNER_OVERRIDE"], required=True)
    admit.add_argument("--qualification")
    admit.add_argument("--owner-utterance-digest")
    admit.add_argument("--owner-session-timestamp")
    admit.add_argument("--branch")

    start = sub.add_parser("start")
    _add_start_args(start)
    activate = sub.add_parser("activate-lease")
    _add_start_args(activate)

    renew = sub.add_parser("renew-lease")
    renew.add_argument(
        "--tx-id",
        help="Explicit transaction ID. Omit to allocate TX.<issue>.<serial> from the current EP parent issue.",
    )
    renew.add_argument(
        "--event-id",
        help="Explicit event ID. Omit to allocate EVT.<issue>.<serial> from the current EP parent issue.",
    )
    renew.add_argument("--actor", required=True)
    renew.add_argument("--expected-custody-epoch", type=int, required=True)
    renew.add_argument("--base-ref", required=True)
    renew.add_argument("--renewed-at")

    release = sub.add_parser("release-lease")
    release.add_argument(
        "--tx-id",
        help="Explicit transaction ID. Omit to allocate TX.<issue>.<serial> from the current EP parent issue.",
    )
    release.add_argument(
        "--event-id",
        help="Explicit event ID. Omit to allocate EVT.<issue>.<serial> from the current EP parent issue.",
    )
    release.add_argument("--actor", required=True)
    release.add_argument("--reason", choices=["HANDOFF", "ADMINISTRATIVE"], default="HANDOFF")
    release.add_argument("--base-ref")
    release.add_argument("--expected-custody-epoch", type=int)

    checkpoint = sub.add_parser("checkpoint")
    checkpoint.add_argument(
        "--tx-id",
        help="Explicit transaction ID. Omit to allocate TX.<issue>.<serial> from the current EP parent issue.",
    )
    checkpoint.add_argument(
        "--event-id",
        help="Explicit event ID. Omit to allocate EVT.<issue>.<serial> from the current EP parent issue.",
    )
    checkpoint.add_argument("--actor", required=True)
    checkpoint.add_argument("--checkpoint", required=True)
    checkpoint.add_argument("--base-ref", required=True)
    checkpoint.add_argument("--expected-custody-epoch", type=int)
    accept_cp = sub.add_parser("accept-checkpoint")
    accept_cp.add_argument(
        "--tx-id",
        help="Explicit transaction ID. Omit to allocate TX.<issue>.<serial> from the current EP parent issue.",
    )
    accept_cp.add_argument(
        "--event-id",
        help="Explicit event ID. Omit to allocate EVT.<issue>.<serial> from the current EP parent issue.",
    )
    accept_cp.add_argument("--actor", required=True)
    accept_cp.add_argument("--checkpoint", required=True)
    accept_cp.add_argument("--base-ref", required=True)
    accept_cp.add_argument("--expected-custody-epoch", type=int)

    control = sub.add_parser("resolve-control")
    control.add_argument("--tx-id")
    control.add_argument("--event-id")
    control.add_argument("--actor", required=True)
    control.add_argument("--control-id", required=True)
    control.add_argument("--evidence", action="append", default=[])
    control.add_argument("--base-ref", required=True)
    control.add_argument("--expected-custody-epoch", type=int)

    roadmap = sub.add_parser("reconcile-roadmap")
    roadmap.add_argument("--tx-id")
    roadmap.add_argument("--event-id")
    roadmap.add_argument("--actor", required=True)
    roadmap.add_argument("--reconciliation", required=True)
    roadmap.add_argument("--base-ref", required=True)
    roadmap.add_argument("--expected-custody-epoch", type=int)
    roadmap.add_argument("--change-delta")

    buddy = sub.add_parser("buddy-message", help="Commit an immutable issue-scoped Relay Markdown message; no stage or writer admission")
    buddy.add_argument("--issue-number", type=int, required=True)
    buddy.add_argument("--tx-id", required=True, help="TX.<issue>.<serial>, never guessed from root Relay state")
    buddy.add_argument("--stage", choices=sorted(BUDDY_MESSAGE_STAGES), required=True)
    buddy.add_argument("--actor", required=True)
    buddy.add_argument("--markdown", required=True, help="Existing UTF-8 Markdown payload; author/source claims still require independent verification")

    handover = sub.add_parser("handover")
    handover.add_argument("--tx-id")
    handover.add_argument("--event-id")
    handover.add_argument("--actor", required=True)
    handover.add_argument("--base-ref", required=True)
    handover.add_argument("--expected-custody-epoch", type=int)

    local = sub.add_parser("local-execution")
    local.add_argument("--tx-id")
    local.add_argument("--event-id")
    local.add_argument("--actor", required=True)
    local.add_argument("--base-ref", required=True)
    local.add_argument("--mode", choices=["VALIDATE_ONLY", "BOUNDED_EXECUTION"], default="VALIDATE_ONLY")
    local.add_argument("--command", action="append", default=[], help="Exact local command to run; repeat for multiple commands.")
    local.add_argument(
        "--return-sub-issue",
        help="Governed provider sub-issue URL/ref the local agent must update with result/evidence before returning.",
    )
    local.add_argument("--expected-custody-epoch", type=int)

    local_result = sub.add_parser("local-execution-result")
    local_result.add_argument("--tx-id")
    local_result.add_argument("--event-id")
    local_result.add_argument("--actor", required=True)
    local_result.add_argument("--result", required=True)

    delivery = sub.add_parser("sync-delivery")
    delivery.add_argument("--tx-id")
    delivery.add_argument("--event-id")
    delivery.add_argument("--actor", required=True)
    delivery.add_argument("--observation", required=True)

    close = sub.add_parser("close")
    close.add_argument("--tx-id")
    close.add_argument("--event-id")
    close.add_argument("--actor", required=True)
    close.add_argument("--parent-issue-observation")
    close.add_argument("--expected-custody-epoch", type=int)

    recovery_done = sub.add_parser("recovery-reconstructed")
    recovery_done.add_argument("--tx-id")
    recovery_done.add_argument("--event-id")
    recovery_done.add_argument("--actor", required=True)
    recovery_done.add_argument("--expected-custody-epoch", type=int, required=True)
    recovery_done.add_argument("--evidence", action="append", default=[])

    change_record = sub.add_parser("record-change")
    change_record.add_argument("--tx-id")
    change_record.add_argument("--event-id")
    change_record.add_argument("--actor", required=True)
    change_record.add_argument("--change-id")
    change_record.add_argument("--statement", required=True)
    change_record.add_argument("--basis", action="append", default=[])
    change_record.add_argument("--process", choices=["PROMPT_1", "OWNER"], default="PROMPT_1")
    change_record.add_argument("--expected-custody-epoch", type=int)

    change_verify = sub.add_parser("verify-change")
    change_verify.add_argument("--tx-id")
    change_verify.add_argument("--event-id")
    change_verify.add_argument("--actor", required=True)
    change_verify.add_argument("--change-id", required=True)
    change_verify.add_argument("--status", choices=["CONFIRMED", "REJECTED"], required=True)
    change_verify.add_argument("--evidence", action="append", default=[])
    change_verify.add_argument("--falsifier", action="append", default=[])
    change_verify.add_argument("--expected-custody-epoch", type=int)

    change_propose = sub.add_parser("propose-change")
    change_propose.add_argument("--tx-id")
    change_propose.add_argument("--event-id")
    change_propose.add_argument("--actor", required=True)
    change_propose.add_argument("--change-id", required=True)
    change_propose.add_argument("--proposal", required=True)
    change_propose.add_argument("--authorization-required", choices=["NONE", "OWNER"], required=True)
    change_propose.add_argument("--expected-custody-epoch", type=int)

    change_authorize = sub.add_parser("authorize-change")
    change_authorize.add_argument("--tx-id")
    change_authorize.add_argument("--event-id")
    change_authorize.add_argument("--actor", required=True)
    change_authorize.add_argument("--change-id", required=True)
    change_authorize.add_argument("--decision", choices=["GRANT", "DENY"], required=True)
    change_authorize.add_argument("--owner-utterance-digest", required=True)
    change_authorize.add_argument("--owner-session-timestamp", required=True)

    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    if args.command == "recover":
        for result in recover_all(root):
            print(f"{result['id']}: {result['status']}")
        return

    if args.command == "admit-task":
        result = admit_task(
            root,
            tx_id=args.tx_id,
            event_id=args.event_id,
            actor=args.actor,
            admission_path=Path(args.admission),
            base_ref=args.base_ref,
            programme_issue_observations=[
                load_yaml(Path(path)) for path in args.programme_issue_observation
            ],
            selected_programme_ref=args.selected_programme_ref,
        )
        print(f"{result['id']}: {result['status']}")
        return

    if args.command == "admit":
        qualification = load_yaml(Path(args.qualification)) if args.qualification else None
        owner_basis = None
        if args.method == "OWNER_OVERRIDE":
            owner_basis = {
                "direct_utterance_digest": args.owner_utterance_digest,
                "session_timestamp": args.owner_session_timestamp,
            }
        lease = build_native_lease(
            root,
            lease_id=args.lease_id,
            executor_id=args.executor_id,
            method=args.method,
            qualification=qualification,
            owner_basis=owner_basis,
            branch=args.branch,
        )
        print(yaml_bytes(lease).decode("utf-8"), end="")
        return

    if args.command in {"start", "activate-lease"}:
        qualification = load_yaml(Path(args.qualification)) if args.qualification else None
        owner_basis = None
        if args.method == "OWNER_OVERRIDE":
            owner_basis = {
                "direct_utterance_digest": args.owner_utterance_digest,
                "session_timestamp": args.owner_session_timestamp,
            }
        result = activate_lease(
            root,
            tx_id=args.tx_id,
            event_id=args.event_id,
            lease_id=args.lease_id,
            executor_id=args.executor_id,
            actor=args.actor,
            method=args.method,
            qualification=qualification,
            owner_basis=owner_basis,
            branch=args.branch,
            base_ref=args.base_ref,
            recovery_takeover=args.recovery_takeover,
            expected_custody_epoch=args.expected_custody_epoch,
            recovery_observed_at=args.recovery_observed_at,
            recovery_after_seconds=args.recovery_after_seconds,
            recovery_policy=args.recovery_policy,
            recovery_observation=(
                load_yaml(Path(args.recovery_observation))
                if args.recovery_observation
                else None
            ),
            programme_issue_observations=[
                load_yaml(Path(path)) for path in args.programme_issue_observation
            ],
            selected_programme_ref=args.selected_programme_ref,
        )
    elif args.command == "renew-lease":
        result = renew_lease(
            root,
            tx_id=args.tx_id,
            event_id=args.event_id,
            actor=args.actor,
            expected_custody_epoch=args.expected_custody_epoch,
            base_ref=args.base_ref,
            renewed_at=args.renewed_at,
        )
    elif args.command == "release-lease":
        result = release_lease(
            root,
            tx_id=args.tx_id,
            event_id=args.event_id,
            actor=args.actor,
            reason=args.reason,
            base_ref=args.base_ref,
            expected_custody_epoch=args.expected_custody_epoch,
        )
    elif args.command in {"checkpoint", "accept-checkpoint"}:
        result = accept_checkpoint(
            root,
            tx_id=args.tx_id,
            event_id=args.event_id,
            actor=args.actor,
            checkpoint_path=Path(args.checkpoint),
            base_ref=args.base_ref,
            expected_custody_epoch=args.expected_custody_epoch,
        )
    elif args.command == "resolve-control":
        result = resolve_control(
            root,
            tx_id=args.tx_id,
            event_id=args.event_id,
            actor=args.actor,
            control_id=args.control_id,
            evidence=args.evidence,
            base_ref=args.base_ref,
            expected_custody_epoch=args.expected_custody_epoch,
        )
    elif args.command == "reconcile-roadmap":
        result = reconcile_roadmap(
            root,
            tx_id=args.tx_id,
            event_id=args.event_id,
            actor=args.actor,
            reconciliation_path=Path(args.reconciliation),
            base_ref=args.base_ref,
            expected_custody_epoch=args.expected_custody_epoch,
            change_delta_path=Path(args.change_delta) if args.change_delta else None,
        )
    elif args.command == "buddy-message":
        result = publish_buddy_markdown(
            root,
            issue_number=args.issue_number,
            tx_id=args.tx_id,
            stage=args.stage,
            actor=args.actor,
            markdown=Path(args.markdown).read_bytes(),
        )
    elif args.command == "handover":
        result = publish_handover(
            root,
            tx_id=args.tx_id,
            event_id=args.event_id,
            actor=args.actor,
            base_ref=args.base_ref,
            expected_custody_epoch=args.expected_custody_epoch,
        )
    elif args.command == "local-execution":
        result = export_local_execution(
            root,
            tx_id=args.tx_id,
            event_id=args.event_id,
            actor=args.actor,
            base_ref=args.base_ref,
            mode=args.mode,
            commands=args.command,
            return_sub_issue=args.return_sub_issue,
            expected_custody_epoch=args.expected_custody_epoch,
        )
    elif args.command == "local-execution-result":
        result = accept_local_execution_result(
            root,
            tx_id=args.tx_id,
            event_id=args.event_id,
            actor=args.actor,
            result_path=Path(args.result),
        )
    elif args.command == "recovery-reconstructed":
        result = record_recovery_reconstructed(
            root,
            tx_id=args.tx_id,
            event_id=args.event_id,
            actor=args.actor,
            evidence=args.evidence,
            expected_custody_epoch=args.expected_custody_epoch,
        )
    elif args.command == "record-change":
        result = record_change_hypothesis(
            root,
            tx_id=args.tx_id,
            event_id=args.event_id,
            actor=args.actor,
            change_id=args.change_id,
            statement=args.statement,
            basis=args.basis,
            process=args.process,
            expected_custody_epoch=args.expected_custody_epoch,
        )
    elif args.command == "verify-change":
        result = verify_change_delta(
            root,
            tx_id=args.tx_id,
            event_id=args.event_id,
            actor=args.actor,
            change_id=args.change_id,
            status=args.status,
            evidence=args.evidence,
            falsifiers_checked=args.falsifier,
            expected_custody_epoch=args.expected_custody_epoch,
        )
    elif args.command == "propose-change":
        result = propose_change_delta(
            root,
            tx_id=args.tx_id,
            event_id=args.event_id,
            actor=args.actor,
            change_id=args.change_id,
            proposal_path=Path(args.proposal),
            authorization_required=args.authorization_required,
            expected_custody_epoch=args.expected_custody_epoch,
        )
    elif args.command == "authorize-change":
        result = authorize_change_delta(
            root,
            tx_id=args.tx_id,
            event_id=args.event_id,
            actor=args.actor,
            change_id=args.change_id,
            granted=args.decision == "GRANT",
            direct_utterance_digest=args.owner_utterance_digest,
            session_timestamp=args.owner_session_timestamp,
        )
    elif args.command == "sync-delivery":
        result = sync_delivery(
            root,
            tx_id=args.tx_id,
            event_id=args.event_id,
            actor=args.actor,
            observation_path=Path(args.observation),
        )
    else:
        result = close_task(
            root,
            tx_id=args.tx_id,
            event_id=args.event_id,
            actor=args.actor,
            parent_issue_observation=(
                load_yaml(Path(args.parent_issue_observation))
                if args.parent_issue_observation
                else None
            ),
            expected_custody_epoch=args.expected_custody_epoch,
        )
    print(f"{result['id']}: {result['status']}")
    if args.command == "buddy-message":
        print(f"{result['message_path']}: {result['message_sha256']} (stage/writer admission NOT_ATTESTED)")
    if args.command == "local-execution":
        request_path = root / "relay/GENERATED/LOCAL_EXECUTION.md"
        if not request_path.exists():
            raise TransactionError("LOCAL_EXECUTION committed without recipient-ready Markdown artifact")
        print()
        print(request_path.read_text(encoding="utf-8"), end="")


if __name__ == "__main__":
    main()
