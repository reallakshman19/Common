#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

from coordlib import load_yaml, validate as schema_validate
from authority_resolver import resolve_authority
from current_state import canonical_document_digest, validate_current_state
from evidence_freshness import canonical_digest as evidence_digest
from evidence_freshness import derive_evidence_freshness
from execution_kernel import derive_next_action, validate_execution_state
import local_v11_integrated
from production_readiness import validate_readiness
from provider_mutation import derive_provider_action, validate_provider_mutation


ROOT = Path(__file__).resolve().parents[2]
V35_RUNTIME = ROOT / "engineering-pr-delivery-v3.5" / "scripts" / "embedded_coder_v35.py"
COMMON_REVIEWER_MANIFEST = ROOT / "common-reviewer-protocol-v1.0" / "protocol-manifest.yaml"
COORDINATOR_ROOT = Path(__file__).resolve().parents[1]

REQUEST_KEYS = {
    "local_bundle",
    "task_id",
    "observed_at",
    "v35_context",
    "v35_result",
    "provider_transaction",
}
SAFE_PROVIDER_ACTIONS = {
    "LOOKUP",
    "READBACK_EXISTING",
    "READBACK_AFTER_MUTATION",
    "COMPLETE",
    "RECONCILE_DUPLICATES",
    "RECONCILE_MISSING_TARGET",
    "RECONCILE_MISMATCH",
}


class Phase1ReplayError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Phase1ReplayError(message)


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_v35() -> Any:
    spec = importlib.util.spec_from_file_location(
        "phase1_runtime_replay_v35_contract",
        V35_RUNTIME,
    )
    if spec is None or spec.loader is None:
        raise Phase1ReplayError("Unable to load V3.5 embedded Coder runtime")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V35 = _load_v35()


def _task_records(
    bundle: dict[str, Any],
    task_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    parents = [row for row in bundle.get("tasks", []) if row.get("kind") == "PARENT"]
    require(len(parents) == 1, "Replay requires exactly one Local Parent TASK")
    tasks = [
        row for row in bundle.get("tasks", [])
        if row.get("kind") == "RESPONSIBILITY" and row.get("task_id") == task_id
    ]
    require(len(tasks) == 1, "Replay requires exactly one matching Local RESPONSIBILITY")
    return parents[0], tasks[0]


def _profile(bundle: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    matches = [
        row for row in bundle.get("native_support", {}).get("acceptance_profiles", [])
        if row.get("profile_id") == task.get("acceptance_profile_ref")
    ]
    require(len(matches) == 1, "Replay requires exactly one matching Acceptance Profile")
    require(
        matches[0].get("digest") == task.get("acceptance_profile_digest"),
        "Acceptance Profile digest differs from responsibility",
    )
    return matches[0]


def _epoch(bundle: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    matches = [
        row for row in bundle.get("native_support", {}).get("acceptance_epochs", [])
        if row.get("epoch_id") == task.get("acceptance_epoch_id")
    ]
    require(len(matches) == 1, "Replay requires exactly one matching Acceptance Epoch")
    return matches[0]


def _lease_heads(lease: dict[str, Any]) -> dict[str, str]:
    rows = lease.get("dependency_heads") or []
    require(isinstance(rows, list), "Local REVIEW_LEASE dependency_heads must be array")
    heads: dict[str, str] = {}
    for row in rows:
        require(
            isinstance(row, dict)
            and isinstance(row.get("task_id"), str)
            and isinstance(row.get("sha"), str),
            "Invalid Local REVIEW_LEASE dependency head",
        )
        require(row["task_id"] not in heads, "Duplicate dependency head in Local REVIEW_LEASE")
        heads[row["task_id"]] = row["sha"]
    return dict(sorted(heads.items()))


def _observed_dependency_heads(
    bundle: dict[str, Any],
    task_id: str,
    fallback: dict[str, str],
) -> dict[str, str]:
    observed = bundle.get("observed", {}).get("dependency_heads", {})
    value = observed.get(task_id)
    if value is None:
        return copy.deepcopy(fallback)
    if isinstance(value, dict):
        return dict(sorted(value.items()))
    if isinstance(value, list):
        heads: dict[str, str] = {}
        for row in value:
            require(
                isinstance(row, dict)
                and isinstance(row.get("task_id"), str)
                and isinstance(row.get("sha"), str),
                "Invalid observed dependency head",
            )
            require(row["task_id"] not in heads, "Duplicate observed dependency head")
            heads[row["task_id"]] = row["sha"]
        return dict(sorted(heads.items()))
    raise Phase1ReplayError("Observed dependency heads must be object or array")


def _historical_lease(
    bundle: dict[str, Any],
    task_id: str,
) -> dict[str, Any]:
    leases = [
        row for row in bundle.get("support", {}).get("review_leases", [])
        if row.get("task_id") == task_id
    ]
    require(leases, "Replay requires at least one historical Local REVIEW_LEASE")
    leases.sort(key=lambda row: (row.get("sealed_at") or "", row.get("lease_id") or ""))
    return leases[-1]


def _current_candidate(bundle: dict[str, Any], task: dict[str, Any], lease: dict[str, Any]) -> str:
    pr = task.get("pr")
    if pr is not None:
        head = (bundle.get("observed", {}).get("pr_heads") or {}).get(str(pr))
        if head:
            return head
    return lease["candidate_sha"]


def _project_protocol(bundle: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    matches = [
        row for row in bundle.get("support", {}).get("project_protocols", [])
        if row.get("digest") == profile.get("project_protocol_digest")
    ]
    require(len(matches) == 1, "Replay requires exact Project Protocol by profile digest")
    return matches[0]


def _freshness_request_from_local(
    bundle: dict[str, Any],
    task: dict[str, Any],
) -> dict[str, Any]:
    profile = _profile(bundle, task)
    epoch = _epoch(bundle, task)
    protocol = _project_protocol(bundle, profile)
    lease = _historical_lease(bundle, task["task_id"])
    candidate_sha = _current_candidate(bundle, task, lease)

    evidence_by_id = {
        row["evidence_id"]: row
        for row in bundle.get("support", {}).get("evidence_records", [])
    }
    lease_evidence = [
        row for row in evidence_by_id.values()
        if row.get("review_lease_ref") == lease["lease_id"]
        and row.get("evidence_phase") in {"FINAL_ACCEPTANCE", "EXTERNAL_GATE"}
    ]
    require(lease_evidence, "Selected Local REVIEW_LEASE has no final evidence")

    leases = {
        row["lease_id"]: row
        for row in bundle.get("support", {}).get("review_leases", [])
    }
    bindings: list[dict[str, Any]] = []
    for source in lease_evidence:
        source_lease = leases.get(source.get("review_lease_ref"))
        require(source_lease is not None, "Evidence references missing Local REVIEW_LEASE")
        bindings.append({
            "evidence_id": source["evidence_id"],
            "evidence_ref": f"local://evidence/{source['evidence_id']}",
            "evidence_digest": evidence_digest(source),
            "source_evidence": copy.deepcopy(source),
            "verification_method_id": source["verification_method_id"],
            "provenance_state": "VERIFIED",
            "candidate_sha": source["candidate_sha"],
            "acceptance_epoch_id": source_lease["acceptance_epoch_id"],
            "project_protocol_digest": source["project_protocol_digest"],
            "acceptance_profile_digest": source_lease["acceptance_profile_digest"],
            "protected_surface_digest": source_lease["acceptance_surface_digest"],
            "environment_digest": source["environment_digest"],
            "dependency_heads": _lease_heads(source_lease),
        })

    certifier_role = lease["certifier_role"]
    profile_role = "COORDINATOR" if certifier_role == "PARENT_CHECK" else certifier_role
    role_bindings = profile.get("role_bindings", {}).get(profile_role, [])
    required_methods = sorted({
        row["verification_method_id"]
        for row in role_bindings
    })
    require(
        required_methods,
        f"Acceptance Profile has no required methods for lease certifier role {certifier_role}",
    )
    protocol_methods = {
        row["id"]: row
        for row in protocol.get("verification_methods", [])
    }
    material_inputs: dict[str, list[str]] = {}
    rerun_policy: dict[str, str] = {}
    for method_id in required_methods:
        method = protocol_methods.get(method_id)
        require(method is not None, f"Local evidence uses unknown verification method {method_id}")
        material_inputs[method_id] = list(method["material_inputs"])
        rerun_policy[method_id] = method["rerun_policy"]

    current_dependencies = _observed_dependency_heads(
        bundle,
        task["task_id"],
        _lease_heads(lease),
    )

    task_stages = [
        row for row in bundle.get("stages", [])
        if row.get("task_id") == task["task_id"]
    ]
    task_stages.sort(key=lambda row: row.get("started_at") or "")
    active_stage = task_stages[-1] if task_stages else None

    current_surface_digest = lease["acceptance_surface_digest"]
    current_environment_digest = lease["environment_digest"]
    if active_stage is not None:
        surface = active_stage.get("acceptance_surface")
        if isinstance(surface, dict) and surface.get("digest"):
            current_surface_digest = surface["digest"]
        environment_ref = active_stage.get("environment_ref")
        if environment_ref:
            environments = {
                row["environment_id"]: row
                for row in bundle.get("support", {}).get("environments", [])
            }
            environment = environments.get(environment_ref)
            require(environment is not None, "Active Local stage references missing environment")
            current_environment_digest = environment["digest"]

    return {
        "evidence_bindings": bindings,
        "current": {
            "candidate_sha": candidate_sha,
            "acceptance_epoch_id": task["acceptance_epoch_id"],
            "project_protocol_digest": profile["project_protocol_digest"],
            "acceptance_profile_digest": profile["digest"],
            "protected_surface_digest": current_surface_digest,
            "environment_digest": current_environment_digest,
            "dependency_heads": current_dependencies,
        },
        "ledger_ref": f"local://review-lease/{lease['lease_id']}",
        "required_method_ids": required_methods,
        "method_material_inputs": material_inputs,
        "method_rerun_policy": rerun_policy,
        "_basis": {
            "lease_id": lease["lease_id"],
            "base_sha": lease["base_sha"],
            "target_ref": lease["target_ref"],
            "acceptance_epoch_digest": epoch["digest"],
        },
    }


def _lifecycle_stage(authority: dict[str, Any]) -> str:
    state = authority["lifecycle"]["state"]
    role = authority["active_role"]
    if state == "STOPPED":
        return "STOPPED"
    if state in {"REWORK"}:
        return "REPAIR"
    if role == "CODER":
        return "CODING"
    if role in {"REVIEWER", "COORDINATOR"}:
        return "REVIEW"
    if state in {"COMPLETE", "STAGE_COMPLETE"}:
        return "READY"
    return "PLANNING"


def _common_reviewer_ref(local_ref: str) -> str:
    prefix = local_ref.split(":skills/", 1)[0]
    return prefix + ":skills/common-reviewer-protocol-v1.0"


def _resolver_ref(local_ref: str) -> str:
    prefix = local_ref.split(":skills/", 1)[0]
    return prefix + ":skills/engineering-programme-coordinator/scripts/authority_resolver.py"


def _execution_state(
    *,
    parent: dict[str, Any],
    task: dict[str, Any],
    v35_context: dict[str, Any],
    authority: dict[str, Any],
    freshness: dict[str, Any],
    freshness_basis: dict[str, Any],
) -> dict[str, Any]:
    candidate_sha = freshness["candidate_sha"]
    branch = f"provider://pr/{task.get('pr')}/head"
    resolver_path = COORDINATOR_ROOT / "scripts" / "authority_resolver.py"
    reviewer_digest = file_digest(COMMON_REVIEWER_MANIFEST)

    state = {
        "schema_version": "EXECUTION_STATE_V1",
        "authority": "EXECUTION_STATE_PROJECTION",
        "identity": {
            "parent": parent["task_id"],
            "responsibility": task["task_id"],
            "attempt": 1,
        },
        "repository": {
            "target_ref": freshness_basis["target_ref"],
            "target_sha": freshness_basis["base_sha"],
            "branch": branch,
            "pr": task.get("pr"),
            "candidate_sha": candidate_sha,
        },
        "protocol": {
            "local_ref": v35_context["local_protocol_ref"],
            "local_digest": v35_context["local_protocol_digest"],
            "v35_ref": v35_context["relay_protocol_ref"],
            "v35_digest": v35_context["relay_protocol_digest"],
            "common_reviewer_ref": _common_reviewer_ref(v35_context["local_protocol_ref"]),
            "common_reviewer_digest": reviewer_digest,
        },
        "capability": {
            "resolution_state": "VERIFIED",
            "resolver_ref": _resolver_ref(v35_context["local_protocol_ref"]),
            "resolver_digest": file_digest(resolver_path),
            "active_role": authority["active_role"],
            "capability_basis": list(authority["capability_basis"]),
            "allowed_actions": list(authority["allowed_actions"]),
            "forbidden_actions": list(authority["forbidden_actions"]),
        },
        "lifecycle": {
            "stage": _lifecycle_stage(authority),
            "last_completed_checkpoint": authority["lifecycle"]["stage_record_id"],
        },
        "dependencies": {
            "satisfied": sorted(freshness["current_basis"]["dependency_heads"]),
            "blocked": [],
        },
        "verification": {
            "expectation_manifest_ref": task["acceptance_profile_ref"],
            "evidence_ledger_ref": freshness["overall"]["evidence_ledger_ref"],
            "evidence_state": freshness["overall"]["evidence_state"],
            "evidence_candidate_sha": freshness["overall"]["evidence_candidate_sha"],
            "unresolved_critical": [],
            "gate": {
                "disposition": "NOT_AVAILABLE",
                "candidate_sha": None,
                "result_ref": None,
                "result_digest": None,
            },
        },
        "contradictions": [],
        "next_action": {},
    }
    state["next_action"] = derive_next_action(state)
    errors = validate_execution_state(state, "phase1-execution-state")
    require(not errors, "; ".join(errors))
    return state


def _current_state(
    *,
    parent: dict[str, Any],
    task: dict[str, Any],
    authority: dict[str, Any],
    freshness: dict[str, Any],
    execution: dict[str, Any],
    execution_ref: str,
    observed_main_sha: str,
) -> dict[str, Any]:
    issue_ref = f"provider://issue/{task['issue']}"
    parent_ref = parent["spec_ref"]
    dependencies = [
        {
            "producer": dependency,
            "required_state": "EXACT_HEAD",
            "observed_state": "VERIFIED",
            "evidence_ref": f"local://dependency/{dependency}",
            "exact_result_ref": f"commit://{sha}",
        }
        for dependency, sha in sorted(freshness["current_basis"]["dependency_heads"].items())
    ]
    next_action = execution["next_action"]
    state = {
        "schema_version": "CURRENT_STATE_V1",
        "authority": "CURRENT_STATE_PROJECTION",
        "parent": {
            "programme_or_parent_id": parent["task_id"],
            "parent_ref": parent_ref,
            "parent_contract_version": "LOCAL_V1_1_NATIVE",
            "main_sha": observed_main_sha,
        },
        "active": {
            "phase": "PHASE-1-CANONICAL-RUNTIME",
            "prd_id": task["task_id"],
            "issue_ref": issue_ref,
            "role": authority["active_role"],
            "attempt": execution["identity"]["attempt"],
        },
        "candidate": {
            "state": "ACTIVE",
            "pr": task.get("pr"),
            "branch": execution["repository"]["branch"],
            "base_sha": execution["repository"]["target_sha"],
            "head_sha": execution["repository"]["candidate_sha"],
            "changed_files": [],
        },
        "frontiers": {
            "material": "PHASE1_RUNTIME_REPLAY",
            "semantic": next_action["reason_code"],
            "evidence": freshness["overall"]["evidence_state"],
        },
        "dependencies": dependencies,
        "open_critical_findings": [],
        "open_critical_unknowns": [],
        "stale_evidence": (
            [row["evidence_id"] for row in freshness["evidence_results"] if row["state"] == "STALE"]
        ),
        "production": {"mode": "OFF", "authority_ref": None},
        "merge_authority": {"state": "NOT_GRANTED", "authority_ref": None},
        "next_action": {
            "execution_state_ref": execution_ref,
            "execution_state_digest": canonical_document_digest(execution),
            "type": next_action["type"],
            "reason_code": next_action["reason_code"],
            "basis_refs": list(next_action["basis_refs"]),
        },
        "forbidden_next_actions": [],
        "source_refs": [parent_ref, issue_ref, execution_ref],
    }
    errors = validate_current_state(state, execution, "phase1-current-state")
    require(not errors, "; ".join(errors))
    return state


def _readiness(
    *,
    task: dict[str, Any],
    v35_context: dict[str, Any],
    replay_ref: str,
    execution_ref: str,
) -> dict[str, Any]:
    verified = lambda ref: {"state": "VERIFIED", "evidence_refs": [ref], "note": None}
    not_implemented = lambda note: {"state": "NOT_IMPLEMENTED", "evidence_refs": [], "note": note}
    conditional = lambda ref, note: {
        "state": "CONDITIONALLY_QUALIFIED",
        "evidence_refs": [ref],
        "note": note,
    }
    value = {
        "schema_version": "PRODUCTION_READINESS_V1",
        "authority": "PRODUCTION_READINESS_PROJECTION",
        "target": {
            "local_runtime": "Local_PR_Deliverty_v1.1",
            "coder_runtime": "engineering-pr-delivery-v3.5",
            "coordinator": "engineering-programme-coordinator",
            "common_reviewer": "common-reviewer-protocol-v1.0",
        },
        "exact_basis": {
            "target_ref": "main",
            "target_sha": task.get("base_sha") or "0" * 40,
            "local_protocol_ref": v35_context["local_protocol_ref"],
            "local_protocol_digest": v35_context["local_protocol_digest"],
            "v35_protocol_ref": v35_context["relay_protocol_ref"],
            "v35_protocol_digest": v35_context["relay_protocol_digest"],
            "common_reviewer_ref": _common_reviewer_ref(v35_context["local_protocol_ref"]),
            "common_reviewer_digest": file_digest(COMMON_REVIEWER_MANIFEST),
        },
        "components": {
            "canonical_local_projection": verified(replay_ref + "#local"),
            "active_authority_resolution": verified(replay_ref + "#authority"),
            "activation_state_derivation": verified(execution_ref),
            "role_succession_semantics": conditional(
                replay_ref + "#local-native-validation",
                "Local native validation covers role succession; this replay does not manufacture a transition.",
            ),
            "acceptance_denominator_closure": not_implemented("Programme denominator runtime is outside Phase-1 integration."),
            "reviewer_definition": verified(replay_ref + "#common-reviewer"),
            "real_artifact_horizontal_integration": conditional(
                replay_ref,
                "Actual runtimes are replayed over canonical synthetic Local records; retained real #527 Local native artifact is not yet available.",
            ),
            "exact_candidate_verification": verified(execution_ref),
            "provider_idempotency": verified(replay_ref + "#provider"),
            "execution_kernel": verified(execution_ref),
            "proof_obligation_runtime": not_implemented("Phase 2 responsibility."),
            "evidence_gate": not_implemented("Phase 3 responsibility."),
            "shadow_rollout": not_implemented("Phase 4 responsibility."),
            "rollback": not_implemented("Phase 4 responsibility."),
        },
        "production_mode": "OFF",
        "cutover_authorization": {
            "authorized": False,
            "authorized_mode": None,
            "authority_ref": None,
            "authorized_at": None,
        },
        "cutover_blockers": [
            {
                "id": "P1I-REAL-ARTIFACT-MISSING",
                "severity": "HARD",
                "state": "OPEN",
                "reason": "Retained real Local/V3.5/Coordinator record replay is still required; current qualification uses canonical synthetic Local records.",
                "evidence_refs": [replay_ref],
            },
            {
                "id": "P1I-LATER-PHASES",
                "severity": "HARD",
                "state": "OPEN",
                "reason": "Proof-obligation, evidence-gate, shadow and rollback phases remain unqualified.",
                "evidence_refs": [replay_ref],
            }
        ],
        "non_blocking_residuals": [],
        "deferred_research": [],
    }
    # target_sha is the Local observed main SHA, supplied by caller after construction.
    return value


def semantic_errors(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value["v35"]["local_responsibility_complete"] is not False:
        errors.append("V3.5 cannot declare Local responsibility complete")
    if value["provider_transaction"]["next_action"] not in SAFE_PROVIDER_ACTIONS:
        errors.append("integration replay cannot expose a provider mutation-capable next action")
    assertions = value["assertions"]
    if assertions["production_mode"] != "OFF":
        errors.append("Phase-1 replay must remain production mode OFF")
    if assertions.get("artifact_class") != "CANONICAL_SYNTHETIC":
        errors.append("P1-I-A replay must truthfully identify canonical synthetic artifact class")
    horizontal = value["production_readiness"]["components"]["real_artifact_horizontal_integration"]
    if horizontal["state"] == "VERIFIED":
        errors.append("canonical synthetic replay cannot mark real-artifact integration VERIFIED")
    if value["execution_state"]["verification"]["gate"]["disposition"] == "ADVANCE_ELIGIBLE":
        errors.append("Phase-1 replay cannot manufacture evidence-gate advancement")
    boundaries = value["authority_boundaries"]
    if any(boundaries.values()):
        errors.append("Phase-1 replay authority boundaries must all remain false")
    return errors


def run_phase1_replay(request: dict[str, Any]) -> dict[str, Any]:
    require(isinstance(request, dict), "Replay request must be object")
    require(set(request) == REQUEST_KEYS, "Replay request has unexpected/missing fields")
    local_bundle = request["local_bundle"]
    v35_context = request["v35_context"]
    v35_result = request["v35_result"]
    provider_transaction = request["provider_transaction"]
    task_id = request["task_id"]
    observed_at = request["observed_at"]

    before = {
        "local_bundle": canonical_digest(local_bundle),
        "v35_context": canonical_digest(v35_context),
        "v35_result": canonical_digest(v35_result),
        "provider_transaction": canonical_digest(provider_transaction),
    }

    parent, task = _task_records(local_bundle, task_id)
    validator = local_v11_integrated._load_local_native_validator_module()
    validated = copy.deepcopy(local_bundle)
    try:
        validation = validator.validate_native_bundle(validated, observed_at)
    except Exception as exc:
        raise Phase1ReplayError(f"Local native validation failed: {exc}") from exc
    require(validation.get("record_consistency") == "PASS", "Local record consistency did not PASS")
    require(validation.get("native_projection") == "PASS", "Local native projection did not PASS")

    validated_context = V35.validate_context(copy.deepcopy(v35_context))
    validated_result = V35.validate_task_result(validated_context, copy.deepcopy(v35_result))
    require(
        validated_result["local_responsibility_complete"] is False,
        "V3.5 illegally claims Local completion",
    )

    local_observation = local_v11_integrated.observe_responsibility(
        parent,
        task,
        validated_result,
        local_bundle=local_bundle,
        local_validation_now=observed_at,
    )
    authority = resolve_authority(copy.deepcopy(local_bundle), task_id, observed_at)

    freshness_request = _freshness_request_from_local(local_bundle, task)
    freshness_basis = freshness_request.pop("_basis")
    freshness = derive_evidence_freshness(**freshness_request)

    execution_ref = "artifact://phase1-runtime-replay/execution-state"
    execution = _execution_state(
        parent=parent,
        task=task,
        v35_context=validated_context,
        authority=authority,
        freshness=freshness,
        freshness_basis=freshness_basis,
    )

    observed_main_sha = local_bundle.get("observed", {}).get("main_sha")
    require(isinstance(observed_main_sha, str) and len(observed_main_sha) == 40, "Local observed main SHA missing")
    current = _current_state(
        parent=parent,
        task=task,
        authority=authority,
        freshness=freshness,
        execution=execution,
        execution_ref=execution_ref,
        observed_main_sha=observed_main_sha,
    )

    provider_errors = validate_provider_mutation(
        copy.deepcopy(provider_transaction),
        "phase1-provider-transaction",
    )
    require(not provider_errors, "; ".join(provider_errors))
    provider_action = derive_provider_action(provider_transaction)
    require(
        provider_action["type"] in SAFE_PROVIDER_ACTIONS,
        "P1-I cannot perform or authorize a provider mutation",
    )

    replay_ref = "artifact://phase1-runtime-replay/result"
    readiness = _readiness(
        task=task,
        v35_context=validated_context,
        replay_ref=replay_ref,
        execution_ref=execution_ref,
    )
    readiness["exact_basis"]["target_sha"] = observed_main_sha
    readiness_errors = validate_readiness(readiness, "phase1-production-readiness")
    require(not readiness_errors, "; ".join(readiness_errors))

    after = {
        "local_bundle": canonical_digest(local_bundle),
        "v35_context": canonical_digest(v35_context),
        "v35_result": canonical_digest(v35_result),
        "provider_transaction": canonical_digest(provider_transaction),
    }
    require(before == after, "Phase-1 replay mutated source artifacts")

    result = {
        "schema_version": "PHASE1_RUNTIME_REPLAY_V1",
        "authority": "INTEGRATION_PROJECTION_ONLY",
        "task_id": task_id,
        "source_digests": before,
        "local_observation": local_observation,
        "v35": {
            "engineering_responsibility": validated_result["engineering_responsibility"],
            "engineering_responsibility_complete": validated_result["engineering_responsibility_complete"],
            "local_responsibility_complete": validated_result["local_responsibility_complete"],
        },
        "authority_resolution": authority,
        "freshness": freshness,
        "execution_state": execution,
        "current_state": current,
        "provider_transaction": {
            "next_action": provider_action["type"],
            "mutation_performed_by_replay": False,
        },
        "production_readiness": readiness,
        "assertions": {
            "evidence_state": freshness["overall"]["evidence_state"],
            "evidence_candidate_sha": freshness["overall"]["evidence_candidate_sha"],
            "execution_next_action": execution["next_action"]["type"],
            "execution_reason_code": execution["next_action"]["reason_code"],
            "production_mode": readiness["production_mode"],
            "artifact_class": "CANONICAL_SYNTHETIC",
            "local_native_validation": "PASS",
            "local_source_unchanged": before["local_bundle"] == after["local_bundle"],
            "v35_source_unchanged": (
                before["v35_context"] == after["v35_context"]
                and before["v35_result"] == after["v35_result"]
            ),
            "provider_source_unchanged": before["provider_transaction"] == after["provider_transaction"],
        },
        "authority_boundaries": {
            "performs_local_stage_transition": False,
            "performs_provider_mutation": False,
            "emits_engineering_pass": False,
            "emits_evidence_gate_advance": False,
            "grants_merge_authority": False,
            "grants_production_cutover": False,
        },
    }

    schema_errors = schema_validate("phase1-runtime-replay", result, "phase1-runtime-replay")
    schema_errors.extend(
        f"phase1-runtime-replay: {error}"
        for error in semantic_errors(result)
    )
    require(not schema_errors, "; ".join(schema_errors))
    return result


def validate_phase1_replay(
    value: Any,
    request: Any,
    label: str = "phase1-runtime-replay",
) -> list[str]:
    errors = schema_validate("phase1-runtime-replay", value, label)
    if errors:
        return errors
    if not isinstance(value, dict):
        return [f"{label}: replay result must be object"]
    errors = [f"{label}: {error}" for error in semantic_errors(value)]
    if not isinstance(request, dict):
        errors.append(f"{label}: replay validation requires source request")
        return errors
    try:
        derived = run_phase1_replay(copy.deepcopy(request))
    except Exception as exc:
        errors.append(f"{label}: source replay failed: {exc}")
        return errors
    if value != derived:
        errors.append(f"{label}: stored replay must exactly equal source replay")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Phase-1 Local/V3.5/Coordinator horizontal replay.")
    parser.add_argument("request")
    args = parser.parse_args()

    request = load_yaml(Path(args.request))
    result = run_phase1_replay(request)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
