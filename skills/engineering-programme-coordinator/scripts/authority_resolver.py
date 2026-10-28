#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from coordlib import load_yaml, validate as schema_validate
import local_v11_integrated as local_adapter


ALL_ACTIONS = frozenset({
    "WRITE_CANDIDATE",
    "RUN_VERIFICATION",
    "REPAIR_CANDIDATE",
    "PUBLISH_EVIDENCE",
    "REQUEST_STAGE_ADVANCE",
    "ESCALATE",
})
ACTIVE_ACTIONS = {
    "CODER": frozenset({
        "WRITE_CANDIDATE",
        "RUN_VERIFICATION",
        "REPAIR_CANDIDATE",
        "PUBLISH_EVIDENCE",
        "REQUEST_STAGE_ADVANCE",
        "ESCALATE",
    }),
    "REVIEWER": frozenset({
        "RUN_VERIFICATION",
        "REPAIR_CANDIDATE",
        "PUBLISH_EVIDENCE",
        "REQUEST_STAGE_ADVANCE",
        "ESCALATE",
    }),
    "COORDINATOR": frozenset({
        "RUN_VERIFICATION",
        "REPAIR_CANDIDATE",
        "PUBLISH_EVIDENCE",
        "REQUEST_STAGE_ADVANCE",
        "ESCALATE",
    }),
}
NON_MATERIAL_ACTIONS = frozenset({"PUBLISH_EVIDENCE", "ESCALATE"})
ROLE_ORDER = ("CODER", "REVIEWER", "COORDINATOR")
WAITING_STATUSES = {
    "WAITING_CI",
    "WAITING_OWNER",
    "WAITING_EXTERNAL",
    "BLOCKED",
    "HELD",
    "PAUSED",
    "STALLED",
    "INCONCLUSIVE",
}
EXPECTED_BUNDLE_KEYS = {
    "tasks",
    "stages",
    "results",
    "observed",
    "support",
    "native_support",
}


class AuthorityResolutionError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuthorityResolutionError(message)


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def parse_instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(parsed.tzinfo is not None, "Observation time requires timezone")
    return parsed.astimezone(timezone.utc)


def _records(bundle: dict[str, Any], task_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    require(set(bundle) == EXPECTED_BUNDLE_KEYS, "Local native bundle has unexpected/missing top-level fields")
    parents = [task for task in bundle["tasks"] if task.get("kind") == "PARENT"]
    require(len(parents) == 1, "Authority resolution requires exactly one Parent TASK")
    responsibilities = [
        task for task in bundle["tasks"]
        if task.get("kind") == "RESPONSIBILITY" and task.get("task_id") == task_id
    ]
    require(len(responsibilities) == 1, "Authority resolution requires exactly one matching RESPONSIBILITY")
    return parents[0], responsibilities[0]


def _role(stage: str) -> str:
    require(stage in ROLE_ORDER, f"Responsibility has unsupported Local stage: {stage}")
    return stage


def _next_role(stage: str) -> str:
    role = _role(stage)
    index = ROLE_ORDER.index(role)
    return ROLE_ORDER[index + 1] if index + 1 < len(ROLE_ORDER) else "NONE"


def _owner_control_projection(control: dict[str, Any] | None) -> dict[str, str] | None:
    if control is None:
        return None
    return {
        "id": control["id"],
        "command": control["command"],
        "instruction_ref": control["instruction_ref"],
    }


def _capability_projection(
    *,
    role: str,
    lifecycle_state: str,
    owner_control: dict[str, Any] | None,
) -> tuple[list[str], list[str]]:
    if role == "NONE":
        allowed: set[str] = set()
    elif owner_control is not None:
        allowed = set(NON_MATERIAL_ACTIONS)
    elif lifecycle_state in {"ACTIVE", "REWORK"}:
        allowed = set(ACTIVE_ACTIONS[role])
    elif lifecycle_state in WAITING_STATUSES:
        allowed = set(NON_MATERIAL_ACTIONS)
    else:
        allowed = set()

    forbidden = set(ALL_ACTIONS) - allowed
    return sorted(allowed), sorted(forbidden)


def _principal_independence(
    *,
    bundle: dict[str, Any],
    stages: list[dict[str, Any]],
    latest: dict[str, Any],
) -> tuple[str, str | None]:
    role = _role(latest["stage"])
    if role == "CODER":
        return "NONE", None

    # Same-role REWORK attempts do not create a new Local role boundary. Find the
    # first attempt in the current contiguous role block, then resolve the actual
    # adjacent prior-role boundary against that first attempt.
    current_index = stages.index(latest)
    block_start = current_index
    while block_start > 0 and stages[block_start - 1]["stage"] == latest["stage"]:
        block_start -= 1
    first_current = stages[block_start]
    prior = stages[block_start - 1] if block_start > 0 else None

    if prior is None or prior["executor"] != latest["executor"]:
        return "DISTINCT", None

    transition = next(
        (
            row for row in bundle["native_support"]["role_transitions"]
            if row["task_id"] == latest["task_id"]
            and row["previous_record_id"] == prior["record_id"]
            and row["next_record_id"] == first_current["record_id"]
        ),
        None,
    )
    require(
        transition is not None,
        "Same-principal active review stage lacks validated ROLE_TRANSITION evidence",
    )
    require(
        transition["role_execution_grant_ref"],
        "Same-principal active review stage lacks ROLE_EXECUTION grant ref",
    )
    return "DEGRADED", transition["transition_id"]


def _source(
    *,
    bundle: dict[str, Any],
    task: dict[str, Any],
    observation: dict[str, Any],
    observed_at: str,
) -> dict[str, Any]:
    return {
        "bundle_digest": canonical_digest(bundle),
        "observed_at": observed_at,
        "local_protocol_ref": task["protocol_ref"],
        "local_protocol_digest": task["protocol_digest"],
        "acceptance_epoch_id": observation["acceptance_epoch_id"],
        "acceptance_profile_ref": observation["acceptance_profile_ref"],
        "acceptance_profile_digest": observation["acceptance_profile_digest"],
    }


def _base_result(
    *,
    bundle: dict[str, Any],
    task: dict[str, Any],
    observation: dict[str, Any],
    observed_at: str,
    local_validation: str,
    lifecycle_state: str,
    stage_record_id: str | None,
    stage_status: str | None,
    active_role: str,
    active_principal: str | None,
    principal_independence: str,
    next_eligible_role: str,
    role_transition_ref: str | None,
    owner_control: dict[str, Any] | None,
    capability_basis: list[str],
) -> dict[str, Any]:
    allowed, forbidden = _capability_projection(
        role=active_role,
        lifecycle_state=lifecycle_state,
        owner_control=owner_control,
    )
    return {
        "schema_version": "AUTHORITY_RESOLUTION_V1",
        "authority": "LOCAL_AUTHORITY_RESOLUTION",
        "task_id": task["task_id"],
        "source": _source(
            bundle=bundle,
            task=task,
            observation=observation,
            observed_at=observed_at,
        ),
        "release_state": observation["release_state"],
        "local_validation": local_validation,
        "lifecycle": {
            "state": lifecycle_state,
            "stage_record_id": stage_record_id,
            "stage_status": stage_status,
        },
        "active_role": active_role,
        "active_principal": active_principal,
        "principal_independence": principal_independence,
        "next_eligible_role": next_eligible_role,
        "role_transition_ref": role_transition_ref,
        "owner_control": _owner_control_projection(owner_control),
        "allowed_actions": allowed,
        "forbidden_actions": forbidden,
        "capability_basis": capability_basis,
        "authority_boundaries": {
            "performs_local_stage_transition": False,
            "grants_merge_authority": False,
            "grants_production_cutover": False,
            "accepts_caller_role_assertion": False,
            "accepts_caller_capability_assertion": False,
        },
    }


def _derive_ready(
    *,
    bundle: dict[str, Any],
    parent: dict[str, Any],
    task: dict[str, Any],
    observation: dict[str, Any],
    observed_at: str,
    validator: Any,
) -> dict[str, Any]:
    now = validator.legacy.instant(observed_at)
    delivery_results = [
        row for row in bundle["results"]
        if row.get("record") == "DELIVERY_RESULT"
        and row.get("task_id") == task["task_id"]
        and row.get("responsibility_complete") is True
    ]
    require(len(delivery_results) <= 1, "Duplicate complete DELIVERY_RESULT for responsibility")
    if delivery_results:
        result = delivery_results[0]
        return _base_result(
            bundle=bundle,
            task=task,
            observation=observation,
            observed_at=observed_at,
            local_validation="PASS",
            lifecycle_state="COMPLETE",
            stage_record_id=result["final_record"],
            stage_status="DELIVERY_RESULT_COMPLETE",
            active_role="NONE",
            active_principal=None,
            principal_independence="NOT_APPLICABLE",
            next_eligible_role="NONE",
            role_transition_ref=None,
            owner_control=None,
            capability_basis=[
                f"local://delivery-result/{result['record_id']}",
                result["parent_comment_ref"],
            ],
        )

    stages = [
        row for row in bundle["stages"]
        if row.get("task_id") == task["task_id"]
        and row.get("stage") in ROLE_ORDER
    ]
    stages.sort(key=lambda row: validator.legacy.instant(row["started_at"]))

    if not stages:
        return _base_result(
            bundle=bundle,
            task=task,
            observation=observation,
            observed_at=observed_at,
            local_validation="PASS",
            lifecycle_state="NOT_STARTED",
            stage_record_id=None,
            stage_status=None,
            active_role="NONE",
            active_principal=None,
            principal_independence="NOT_APPLICABLE",
            next_eligible_role="CODER",
            role_transition_ref=None,
            owner_control=None,
            capability_basis=[
                f"local://parent-registry/{task['task_id']}/READY",
                f"local://start-permission/pending/{task['task_id']}",
            ],
        )

    latest = stages[-1]
    role = _role(latest["stage"])
    control = validator.legacy.blocking_control(
        parent["owner_commands"],
        task,
        latest["stage"],
        now,
    )
    effective_status = validator.legacy.stage_status(
        latest,
        parent["timers"],
        parent["owner_commands"],
        task,
        now,
    )

    if control is not None and control["command"] == "STOP":
        lifecycle_state = "STOPPED"
        active_role = "NONE"
        active_principal = None
        independence = "NOT_APPLICABLE"
        transition_ref = None
        next_role = "NONE"
    elif effective_status in {"STAGE_COMPLETE", "STAGE_COMPLETE_WITH_WAIVER"}:
        lifecycle_state = "STAGE_COMPLETE"
        active_role = "NONE"
        active_principal = None
        independence = "NOT_APPLICABLE"
        transition_ref = None
        next_role = _next_role(role)
    elif effective_status == "STOPPED":
        lifecycle_state = "STOPPED"
        active_role = "NONE"
        active_principal = None
        independence = "NOT_APPLICABLE"
        transition_ref = None
        next_role = "NONE"
    else:
        lifecycle_state = {
            "RUNNING": "ACTIVE",
            "REWORK": "REWORK",
            "WAITING_CI": "WAITING_CI",
            "WAITING_OWNER": "WAITING_OWNER",
            "WAITING_EXTERNAL": "WAITING_EXTERNAL",
            "BLOCKED": "BLOCKED",
            "STALLED": "STALLED",
            "INCONCLUSIVE": "INCONCLUSIVE",
            "HELD": "HELD",
            "PAUSED": "PAUSED",
        }.get(effective_status, effective_status)
        if control is not None and control["command"] == "HOLD":
            lifecycle_state = "HELD"
        elif control is not None and control["command"] == "PAUSE":
            lifecycle_state = "PAUSED"
        active_role = role
        active_principal = latest["executor"]
        independence, transition_ref = _principal_independence(
            bundle=bundle,
            stages=stages,
            latest=latest,
        )
        next_role = "NONE"

    basis = [
        f"local://stage/{latest['record_id']}",
        latest["publications"]["start"]["comment_ref"],
        f"local://release/{task['task_id']}/{observation['release_state']}",
    ]
    if latest["publications"]["end"] is not None:
        basis.append(latest["publications"]["end"]["comment_ref"])
    if control is not None:
        basis.append(control["instruction_ref"])
    if transition_ref is not None:
        basis.append(f"local://role-transition/{transition_ref}")

    return _base_result(
        bundle=bundle,
        task=task,
        observation=observation,
        observed_at=observed_at,
        local_validation="PASS",
        lifecycle_state=lifecycle_state,
        stage_record_id=latest["record_id"],
        stage_status=effective_status,
        active_role=active_role,
        active_principal=active_principal,
        principal_independence=independence,
        next_eligible_role=next_role,
        role_transition_ref=transition_ref,
        owner_control=control,
        capability_basis=basis,
    )


def semantic_errors(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    allowed = set(value["allowed_actions"])
    forbidden = set(value["forbidden_actions"])

    if allowed & forbidden:
        errors.append("allowed_actions and forbidden_actions must not overlap")
    if allowed | forbidden != set(ALL_ACTIONS):
        errors.append("allowed_actions + forbidden_actions must exactly partition action universe")

    role = value["active_role"]
    principal = value["active_principal"]
    independence = value["principal_independence"]
    if role == "NONE":
        if principal is not None:
            errors.append("active_role NONE requires active_principal null")
        if independence != "NOT_APPLICABLE":
            errors.append("active_role NONE requires NOT_APPLICABLE independence")
    else:
        if not principal:
            errors.append("active role requires active_principal")
        if role == "CODER" and independence != "NONE":
            errors.append("CODER requires principal_independence NONE")
        if role in {"REVIEWER", "COORDINATOR"} and independence not in {"DISTINCT", "DEGRADED"}:
            errors.append("review roles require DISTINCT or DEGRADED independence")

    if independence == "DEGRADED" and not value["role_transition_ref"]:
        errors.append("DEGRADED independence requires role_transition_ref")
    if independence != "DEGRADED" and value["role_transition_ref"] is not None:
        errors.append("role_transition_ref is only valid for DEGRADED succession")

    if value["release_state"] != "READY":
        if value["local_validation"] != "NOT_REQUIRED_NO_CAPABILITY":
            errors.append("non-READY release must use NOT_REQUIRED_NO_CAPABILITY")
        if allowed:
            errors.append("non-READY release cannot emit allowed actions")
        if role != "NONE":
            errors.append("non-READY release cannot emit active role")

    if value["local_validation"] == "NOT_REQUIRED_NO_CAPABILITY" and allowed:
        errors.append("unvalidated resolution cannot emit capability")

    if value["lifecycle"]["state"] in {"COMPLETE", "STAGE_COMPLETE", "STOPPED", "NOT_STARTED"} and allowed:
        errors.append("terminal/boundary lifecycle state cannot emit allowed actions")

    return errors


def resolve_authority(
    bundle: dict[str, Any],
    task_id: str,
    observed_at: str,
) -> dict[str, Any]:
    require(isinstance(bundle, dict), "Local bundle must be an object")
    require(isinstance(task_id, str) and task_id.startswith("PRD-"), "Resolver requires PRD-* task_id")
    parse_instant(observed_at)

    parent, task = _records(bundle, task_id)
    try:
        observation = local_adapter.canonical_local_observation(parent, task)
    except Exception as exc:
        raise AuthorityResolutionError(f"Local canonical observation rejected bundle: {exc}") from exc

    release_state = observation["release_state"]
    if release_state != "READY":
        lifecycle = {
            "BLOCKED_DEPENDENCY": "BLOCKED",
            "HELD": "HELD",
            "STOPPED": "STOPPED",
        }[release_state]
        result = _base_result(
            bundle=bundle,
            task=task,
            observation=observation,
            observed_at=observed_at,
            local_validation="NOT_REQUIRED_NO_CAPABILITY",
            lifecycle_state=lifecycle,
            stage_record_id=None,
            stage_status=None,
            active_role="NONE",
            active_principal=None,
            principal_independence="NOT_APPLICABLE",
            next_eligible_role="NONE",
            role_transition_ref=None,
            owner_control=None,
            capability_basis=[f"local://parent-registry/{task_id}/{release_state}"],
        )
    else:
        validator = local_adapter._load_local_native_validator_module()
        validated = copy.deepcopy(bundle)
        try:
            summary = validator.validate_native_bundle(validated, observed_at)
        except Exception as exc:
            raise AuthorityResolutionError(
                f"READY responsibility failed Local native validation: {exc}"
            ) from exc
        require(summary.get("record_consistency") == "PASS", "Local native validation did not PASS")
        require(summary.get("native_projection") == "PASS", "Local native projection did not PASS")
        result = _derive_ready(
            bundle=validated,
            parent=next(task for task in validated["tasks"] if task["kind"] == "PARENT"),
            task=next(
                task for task in validated["tasks"]
                if task.get("kind") == "RESPONSIBILITY" and task.get("task_id") == task_id
            ),
            observation=observation,
            observed_at=observed_at,
            validator=validator,
        )

    errors = schema_validate("authority-resolution", result, "authority-resolution")
    errors.extend(
        f"authority-resolution: {error}"
        for error in semantic_errors(result)
    )
    require(not errors, "; ".join(errors))
    return result


def validate_authority_resolution(
    value: Any,
    bundle: Any,
    observed_at: str | None,
    label: str = "authority-resolution",
) -> list[str]:
    errors = schema_validate("authority-resolution", value, label)
    if errors:
        return errors
    if not isinstance(value, dict):
        return [f"{label}: authority resolution must be an object"]
    errors = [f"{label}: {error}" for error in semantic_errors(value)]

    if not isinstance(bundle, dict):
        errors.append(f"{label}: authority resolution requires raw Local native bundle")
        return errors
    if not isinstance(observed_at, str) or not observed_at:
        errors.append(f"{label}: authority resolution requires explicit observed_at")
        return errors
    if value["source"]["observed_at"] != observed_at:
        errors.append(f"{label}: observed_at differs from projected source time")
        return errors

    try:
        derived = resolve_authority(bundle, value["task_id"], observed_at)
    except Exception as exc:
        errors.append(f"{label}: bound Local replay failed: {exc}")
        return errors

    if value != derived:
        errors.append(
            f"{label}: stored authority resolution must exactly equal raw Local-bundle derivation"
        )
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Derive Local v1.1 role/lifecycle/capability authority from canonical native records."
    )
    parser.add_argument("bundle")
    parser.add_argument("task_id")
    parser.add_argument("--observed-at", required=True)
    args = parser.parse_args()

    result = resolve_authority(
        load_yaml(Path(args.bundle)),
        args.task_id,
        args.observed_at,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
