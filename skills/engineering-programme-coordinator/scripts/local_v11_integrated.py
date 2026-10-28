#!/usr/bin/env python3
"""Observation-only adapter for Local PR Delivery v1.1 + Relay V3.5.

The programme coordinator consumes canonical Parent + RESPONSIBILITY records through
Local's existing responsibility_observation() path, then combines that Local-owned
observation with optional validated Local delivery truth and V3.5 Coder evidence. It
does not create Local state, engineering acceptance truth, lifecycle authority, or
merge authority.
"""
from __future__ import annotations

import copy
import importlib.util
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

MODE = "LOCAL_V1_1_INTEGRATED"
AUTHORITY = "OBSERVATION_ONLY"
LEGACY_V31 = "READABLE_COMPATIBILITY_ONLY"
CANONICAL_RELEASE_STATES = frozenset({
    "READY",
    "BLOCKED_DEPENDENCY",
    "HELD",
    "STOPPED",
})
RESPONSIBILITY_OBSERVATION_FIELDS = frozenset({
    "task_id",
    "release_state",
    "acceptance_epoch_id",
    "acceptance_profile_ref",
    "acceptance_profile_digest",
    "nested_engineering_responsibility",
    "coder_engineering_complete",
    "local_responsibility_complete",
})
RESPONSIBILITY_INPUT_FIELDS = frozenset({
    "responsibility_task",
    "v35_result",
    "local_bundle",
    "local_validation_now",
})
NON_AUTHORITIES = {
    "ENGINEERING_PASS",
    "LOCAL_ROLE_TRANSITION",
    "PRODUCT_WRITE",
    "ACCEPTANCE_POLICY_WRITE",
    "RISK_RELAXATION",
    "MERGE",
}
PRD_RE = re.compile(r"^PRD-[A-Za-z0-9._-]+$")
DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
LOCAL_REF_RE = re.compile(
    r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}:skills/Local_PR_Deliverty_v1[.]1$"
)
V35_REF_RE = re.compile(
    r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}:skills/engineering-pr-delivery-v3[.]5$"
)
LOCAL_SCRIPTS = Path(__file__).resolve().parents[2] / "Local_PR_Deliverty_v1.1" / "scripts"
LOCAL_IMPORT_COLLISIONS = (
    "validate",
    "pipeline",
    "acceptance_basis",
    "responsibility",
    "role_transition",
)
_MISSING_MODULE = object()


class IntegratedModeError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise IntegratedModeError(message)


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise IntegratedModeError(f"Unable to load Local v1.1 module: {path.name}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise IntegratedModeError(f"Unable to load Local v1.1 module {path.name}: {exc}") from exc
    return module


def _load_local_responsibility_module() -> Any:
    return _load_module(
        "local_v11_responsibility_contract",
        LOCAL_SCRIPTS / "responsibility.py",
    )


@lru_cache(maxsize=1)
def _load_local_native_validator_module() -> Any:
    """Load Local native validation without leaking colliding top-level modules.

    Local v1.1 uses script-directory imports such as ``import validate`` while the
    programme coordinator owns modules with some of the same top-level names.  The
    Local directory therefore has to lead ``sys.path`` during this one import, but the
    caller's import environment must be restored exactly afterwards.  Restoring the
    colliding ``sys.modules`` entries also prevents the Local validator from shadowing
    coordinator modules (and prevents a preloaded coordinator module from being bound
    as Local's dependency).
    """
    scripts = str(LOCAL_SCRIPTS)
    original_path = list(sys.path)
    previous_modules = {
        name: sys.modules.get(name, _MISSING_MODULE)
        for name in LOCAL_IMPORT_COLLISIONS
    }
    try:
        sys.path[:] = [scripts, *[entry for entry in original_path if entry != scripts]]
        for name in LOCAL_IMPORT_COLLISIONS:
            sys.modules.pop(name, None)
        return _load_module(
            "local_v11_native_validator_contract",
            LOCAL_SCRIPTS / "validate_native.py",
        )
    finally:
        sys.path[:] = original_path
        for name, previous in previous_modules.items():
            sys.modules.pop(name, None)
            if previous is not _MISSING_MODULE:
                sys.modules[name] = previous


LOCAL_RESPONSIBILITY = _load_local_responsibility_module()


def expected_nested_identity(task_id: str) -> str:
    require(bool(PRD_RE.fullmatch(task_id)), "Integrated responsibility must use PRD-* identity")
    return "ENG-" + task_id + "-CODER"


def canonical_local_observation(
    parent_task: dict[str, Any],
    responsibility_task: dict[str, Any],
) -> dict[str, Any]:
    """Derive coordinator input through Local's canonical observation implementation."""
    try:
        return LOCAL_RESPONSIBILITY.responsibility_observation(parent_task, responsibility_task)
    except (LOCAL_RESPONSIBILITY.ResponsibilityError, KeyError, TypeError) as exc:
        raise IntegratedModeError(f"Local canonical observation rejected input: {exc}") from exc


def validated_local_completion(
    parent_task: dict[str, Any],
    responsibility_task: dict[str, Any],
    local_bundle: dict[str, Any] | None,
    local_validation_now: str | None,
) -> bool:
    """Return Local completion only from a bundle accepted by Local native validation."""
    if local_bundle is None:
        require(local_validation_now is None, "Local validation time requires a Local validation bundle")
        return False

    require(
        isinstance(local_validation_now, str) and bool(local_validation_now),
        "Local validation bundle requires an explicit validation time",
    )
    validator = _load_local_native_validator_module()
    validated_bundle = copy.deepcopy(local_bundle)
    try:
        validator.validate_native_bundle(validated_bundle, local_validation_now)
    except Exception as exc:
        raise IntegratedModeError(f"Local native validation rejected bundle: {exc}") from exc

    parents = [task for task in validated_bundle.get("tasks", []) if task.get("kind") == "PARENT"]
    require(len(parents) == 1, "Validated Local bundle must contain exactly one Parent TASK")
    require(parents[0] == parent_task, "Validated Local bundle Parent differs from observed Parent")

    task_id = responsibility_task.get("task_id")
    responsibilities = [
        task
        for task in validated_bundle.get("tasks", [])
        if task.get("kind") == "RESPONSIBILITY" and task.get("task_id") == task_id
    ]
    require(
        len(responsibilities) == 1,
        "Validated Local bundle does not contain exactly one observed RESPONSIBILITY",
    )
    require(
        responsibilities[0] == responsibility_task,
        "Validated Local bundle RESPONSIBILITY differs from observed RESPONSIBILITY",
    )

    delivery_results = [
        result
        for result in validated_bundle.get("results", [])
        if result.get("record") == "DELIVERY_RESULT" and result.get("task_id") == task_id
    ]
    require(len(delivery_results) <= 1, "Validated Local bundle has duplicate DELIVERY_RESULT for responsibility")
    if not delivery_results:
        return False
    return bool(delivery_results[0]["responsibility_complete"])


def observe_responsibility(
    parent_task: dict[str, Any],
    responsibility_task: dict[str, Any],
    v35_result: dict[str, Any] | None = None,
    *,
    local_bundle: dict[str, Any] | None = None,
    local_validation_now: str | None = None,
) -> dict[str, Any]:
    """Observe canonical Local records plus independently scoped completion evidence.

    Parent + RESPONSIBILITY provenance is recomputed through Local's canonical
    responsibility_observation() implementation. Local completion can become true only
    when the existing Local native validation path accepts the supplied full bundle and
    the matching schema-valid DELIVERY_RESULT says responsibility_complete=true.

    V3.5 remains an independent Coder-only evidence source. Its completion bit can only
    affect coder_engineering_complete and can never manufacture Local completion.
    """
    local_observation = canonical_local_observation(parent_task, responsibility_task)
    task_id = local_observation.get("task_id")
    require(isinstance(task_id, str) and PRD_RE.fullmatch(task_id), "Integrated responsibility must use PRD-* identity")
    require(
        local_observation.get("release_state") in CANONICAL_RELEASE_STATES,
        "Canonical Local observation has invalid release state",
    )
    require(local_observation.get("acceptance_epoch_id"), "Canonical Local observation lacks acceptance_epoch_id")
    require(local_observation.get("acceptance_profile_ref"), "Canonical Local observation lacks acceptance profile")
    require(
        bool(DIGEST_RE.fullmatch(local_observation.get("acceptance_profile_digest", ""))),
        "Canonical Local observation has invalid acceptance profile digest",
    )
    require(
        local_observation.get("local_responsibility_complete") is False,
        "Local base observation must not manufacture completion before validated DELIVERY_RESULT binding",
    )

    local_complete = validated_local_completion(
        parent_task,
        responsibility_task,
        local_bundle,
        local_validation_now,
    )

    nested = expected_nested_identity(task_id)
    coder_complete = False
    if v35_result is not None:
        require(v35_result.get("result_scope") == "CODER_ENGINEERING_EXECUTION", "Coordinator can consume only Coder-scoped V3.5 result")
        require(isinstance(v35_result.get("engineering_responsibility_complete"), bool), "V3.5 Coder completion must be boolean")
        require(v35_result.get("engineering_responsibility") == nested, "V3.5 nested responsibility does not match Local responsibility")
        require(v35_result.get("local_responsibility_task_id") == task_id, "V3.5 result points at another Local responsibility")
        require(v35_result.get("local_responsibility_complete") is False, "V3.5 result illegally claims Local responsibility completion")
        require(v35_result.get("acceptance_epoch_ref") == local_observation["acceptance_epoch_id"], "V3.5 result acceptance epoch is stale")
        require(v35_result.get("acceptance_profile_ref") == local_observation["acceptance_profile_ref"], "V3.5 result acceptance profile is stale")
        require(v35_result.get("acceptance_profile_digest") == local_observation["acceptance_profile_digest"], "V3.5 result acceptance profile digest is stale")
        coder_complete = v35_result["engineering_responsibility_complete"]

    return {
        "task_id": task_id,
        "release_state": local_observation["release_state"],
        "acceptance_epoch_id": local_observation["acceptance_epoch_id"],
        "acceptance_profile_ref": local_observation["acceptance_profile_ref"],
        "acceptance_profile_digest": local_observation["acceptance_profile_digest"],
        "nested_engineering_responsibility": nested,
        "coder_engineering_complete": coder_complete,
        "local_responsibility_complete": local_complete,
    }


def build_integrated_context(
    *,
    parent_task: dict[str, Any],
    local_protocol_ref: str,
    local_protocol_digest: str,
    engineering_evidence_provider_ref: str,
    engineering_evidence_provider_digest: str,
    responsibility_inputs: list[dict[str, Any]] | None = None,
    responsibility_observations: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build integrated context only from canonical Local records/evidence.

    Raw observation dictionaries are deliberately rejected.  The public construction
    boundary derives every row through observe_responsibility(), so callers cannot
    manufacture Local completion or provenance by supplying a schema-shaped projection.
    """
    require(isinstance(parent_task, dict), "Integrated mode requires canonical Parent TASK")
    require(parent_task.get("kind") == "PARENT", "Integrated mode requires canonical Parent TASK")
    parent_task_id = parent_task.get("task_id")
    require(isinstance(parent_task_id, str) and parent_task_id, "Missing Local parent TASK identity")
    require(bool(LOCAL_REF_RE.fullmatch(local_protocol_ref)), "Integrated mode requires exact Local v1.1 protocol ref")
    require(bool(DIGEST_RE.fullmatch(local_protocol_digest)), "Invalid Local protocol digest")
    require(bool(V35_REF_RE.fullmatch(engineering_evidence_provider_ref)), "Integrated mode requires exact V3.5 evidence-provider ref")
    require(bool(DIGEST_RE.fullmatch(engineering_evidence_provider_digest)), "Invalid V3.5 provider digest")
    require(
        responsibility_observations is None,
        "Raw responsibility observations are not accepted; provide canonical responsibility_inputs",
    )
    require(isinstance(responsibility_inputs, list), "Responsibility inputs must be an array")

    observations: list[dict[str, Any]] = []
    for item in responsibility_inputs:
        require(isinstance(item, dict), "Responsibility input must be an object")
        require(
            set(item) <= RESPONSIBILITY_INPUT_FIELDS and "responsibility_task" in item,
            "Responsibility input has invalid fields",
        )
        observations.append(
            observe_responsibility(
                parent_task,
                item["responsibility_task"],
                item.get("v35_result"),
                local_bundle=item.get("local_bundle"),
                local_validation_now=item.get("local_validation_now"),
            )
        )

    ids = [row.get("task_id") for row in observations]
    require(len(ids) == len(set(ids)), "Duplicate responsibility observation")
    for row in observations:
        require(
            set(row) == RESPONSIBILITY_OBSERVATION_FIELDS,
            "Canonical responsibility observation shape differs from runtime/schema contract",
        )
        require(row.get("nested_engineering_responsibility") == expected_nested_identity(row.get("task_id", "")), "Nested engineering identity mismatch")
        require(row.get("release_state") in CANONICAL_RELEASE_STATES, "Invalid Local release state")
        require(row.get("acceptance_epoch_id"), "Missing canonical Local acceptance_epoch_id")
        require(row.get("acceptance_profile_ref"), "Missing canonical Local acceptance profile")
        require(
            bool(DIGEST_RE.fullmatch(row.get("acceptance_profile_digest", ""))),
            "Invalid canonical Local acceptance profile digest",
        )
        require(isinstance(row.get("coder_engineering_complete"), bool), "Missing Coder engineering completion observation")
        require(isinstance(row.get("local_responsibility_complete"), bool), "Missing validated Local completion observation")

    return {
        "mode": MODE,
        "authority": AUTHORITY,
        "parent_task_id": parent_task_id,
        "local_protocol_ref": local_protocol_ref,
        "local_protocol_digest": local_protocol_digest,
        "engineering_evidence_provider_ref": engineering_evidence_provider_ref,
        "engineering_evidence_provider_digest": engineering_evidence_provider_digest,
        "responsibilities": copy.deepcopy(observations),
        "non_authorities": sorted(NON_AUTHORITIES),
        "legacy_v31_interpretation": LEGACY_V31,
    }

def assert_observation_only_action(action: str) -> None:
    require(action not in NON_AUTHORITIES, "Programme coordinator integrated mode cannot exercise authority: " + action)


def derive_programme_status(context: dict[str, Any]) -> dict[str, Any]:
    """Return a coordination status projection without inventing engineering PASS."""
    require(context.get("mode") == MODE and context.get("authority") == AUTHORITY, "Not a valid integrated coordinator context")
    require(set(context.get("non_authorities", [])) == NON_AUTHORITIES, "Integrated context weakened its non-authority boundary")
    rows = context.get("responsibilities", [])
    return {
        "mode": MODE,
        "observed_responsibilities": len(rows),
        "coder_engineering_complete": sum(bool(row["coder_engineering_complete"]) for row in rows),
        "local_responsibilities_complete": sum(bool(row["local_responsibility_complete"]) for row in rows),
        "blocked_or_held": [row["task_id"] for row in rows if row["release_state"] in {"BLOCKED_DEPENDENCY", "HELD"}],
        "stopped": [row["task_id"] for row in rows if row["release_state"] == "STOPPED"],
        "engineering_acceptance_verdict": "NOT_AUTHORIZED",
        "merge_authority": "NOT_AUTHORIZED",
    }