#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

from coordlib import load_yaml, validate as schema_validate


LOCAL_ACCEPTANCE_BASIS = (
    Path(__file__).resolve().parents[2]
    / "Local_PR_Deliverty_v1.1"
    / "scripts"
    / "acceptance_basis.py"
)
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
BINDING_KEYS = {
    "evidence_id",
    "evidence_ref",
    "evidence_digest",
    "source_evidence",
    "verification_method_id",
    "provenance_state",
    "candidate_sha",
    "acceptance_epoch_id",
    "project_protocol_digest",
    "acceptance_profile_digest",
    "protected_surface_digest",
    "environment_digest",
    "dependency_heads",
}
CURRENT_KEYS = {
    "candidate_sha",
    "acceptance_epoch_id",
    "project_protocol_digest",
    "acceptance_profile_digest",
    "protected_surface_digest",
    "environment_digest",
    "dependency_heads",
}
REASON_TO_INPUT = {
    "CANDIDATE_CHANGED": "CANDIDATE",
    "ACCEPTANCE_BASIS_CHANGED": "ACCEPTANCE_EPOCH",
    "PROJECT_PROTOCOL_CHANGED": "PROJECT_PROTOCOL",
    "ACCEPTANCE_PROFILE_CHANGED": "ACCEPTANCE_PROFILE",
    "PROTECTED_SURFACE_CHANGED": "PROTECTED_SURFACE",
    "ENVIRONMENT_CHANGED": "ENVIRONMENT",
}


class EvidenceFreshnessError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceFreshnessError(message)


def _load_local_acceptance_basis() -> Any:
    spec = importlib.util.spec_from_file_location(
        "local_v11_acceptance_basis_freshness_contract",
        LOCAL_ACCEPTANCE_BASIS,
    )
    if spec is None or spec.loader is None:
        raise EvidenceFreshnessError("Unable to load Local v1.1 acceptance-basis module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LOCAL = _load_local_acceptance_basis()


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate_sha(value: Any, label: str) -> None:
    require(isinstance(value, str) and bool(SHA_RE.fullmatch(value)), f"{label} must be 40-hex SHA")


def _validate_digest(value: Any, label: str) -> None:
    require(isinstance(value, str) and bool(DIGEST_RE.fullmatch(value)), f"{label} must be 64-hex digest")


def _validate_heads(value: Any, label: str) -> dict[str, str]:
    require(isinstance(value, dict), f"{label} must be object")
    result: dict[str, str] = {}
    for key, head in value.items():
        require(isinstance(key, str) and bool(key), f"{label} dependency id must be non-empty")
        _validate_sha(head, f"{label}.{key}")
        result[key] = head
    return result


def _validate_current(current: Any) -> dict[str, Any]:
    require(isinstance(current, dict), "current basis must be object")
    require(set(current) == CURRENT_KEYS, "current basis has unexpected/missing fields")
    _validate_sha(current["candidate_sha"], "current.candidate_sha")
    require(
        isinstance(current["acceptance_epoch_id"], str)
        and bool(current["acceptance_epoch_id"]),
        "current.acceptance_epoch_id is required",
    )
    for key in (
        "project_protocol_digest",
        "acceptance_profile_digest",
        "protected_surface_digest",
    ):
        _validate_digest(current[key], f"current.{key}")
    environment = current["environment_digest"]
    if environment is not None:
        _validate_digest(environment, "current.environment_digest")
    heads = _validate_heads(current["dependency_heads"], "current.dependency_heads")
    return {
        **copy.deepcopy(current),
        "dependency_heads": dict(sorted(heads.items())),
    }


def _validate_binding(binding: Any) -> dict[str, Any]:
    require(isinstance(binding, dict), "evidence binding must be object")
    require(set(binding) == BINDING_KEYS, "evidence binding has unexpected/missing fields")
    for key in ("evidence_id", "evidence_ref", "verification_method_id", "acceptance_epoch_id"):
        require(isinstance(binding[key], str) and bool(binding[key]), f"{key} is required")
    _validate_digest(binding["evidence_digest"], "evidence_digest")
    source = binding["source_evidence"]
    require(isinstance(source, dict), "source_evidence must be object")
    for key in (
        "evidence_id",
        "candidate_sha",
        "verification_method_id",
        "project_protocol_digest",
        "environment_digest",
    ):
        require(key in source, f"source_evidence missing {key}")
    require(
        canonical_digest(source) == binding["evidence_digest"],
        "evidence_digest does not match immutable source_evidence",
    )
    require(
        source["evidence_id"] == binding["evidence_id"],
        "freshness binding evidence_id differs from source_evidence",
    )
    require(
        source["candidate_sha"] == binding["candidate_sha"],
        "freshness binding candidate_sha differs from source_evidence",
    )
    require(
        source["verification_method_id"] == binding["verification_method_id"],
        "freshness binding verification_method_id differs from source_evidence",
    )
    require(
        source["project_protocol_digest"] == binding["project_protocol_digest"],
        "freshness binding project_protocol_digest differs from source_evidence",
    )
    require(
        source["environment_digest"] == binding["environment_digest"],
        "freshness binding environment_digest differs from source_evidence",
    )

    _validate_sha(binding["candidate_sha"], "candidate_sha")
    for key in (
        "project_protocol_digest",
        "acceptance_profile_digest",
        "protected_surface_digest",
    ):
        _validate_digest(binding[key], key)
    environment = binding["environment_digest"]
    if environment is not None:
        _validate_digest(environment, "environment_digest")
    require(
        binding["provenance_state"] in {"VERIFIED", "UNKNOWN"},
        "provenance_state must be VERIFIED or UNKNOWN",
    )
    heads = _validate_heads(binding["dependency_heads"], "dependency_heads")
    normalized = copy.deepcopy(binding)
    normalized["dependency_heads"] = dict(sorted(heads.items()))
    return normalized


def _ledger_digest(bindings: list[dict[str, Any]]) -> str:
    return canonical_digest(sorted(bindings, key=lambda row: row["evidence_id"]))


def _dependency_changed_inputs(
    evidence_heads: dict[str, str],
    current_heads: dict[str, str],
) -> set[str]:
    changed: set[str] = set()
    for dependency in sorted(set(evidence_heads) | set(current_heads)):
        if evidence_heads.get(dependency) != current_heads.get(dependency):
            changed.add("DEPENDENCIES")
            changed.add(f"DEPENDENCY:{dependency}")
    return changed


def _evidence_result(
    binding: dict[str, Any],
    current: dict[str, Any],
) -> tuple[dict[str, Any], set[str]]:
    validity = LOCAL.evidence_validity_projection(
        binding,
        candidate_sha=current["candidate_sha"],
        acceptance_epoch_id=current["acceptance_epoch_id"],
        project_protocol_digest=current["project_protocol_digest"],
        acceptance_profile_digest=current["acceptance_profile_digest"],
        protected_surface_digest=current["protected_surface_digest"],
        environment_digest=current["environment_digest"],
        dependency_heads=current["dependency_heads"],
    )
    reasons = list(validity["reasons"])
    changed_inputs: set[str] = {
        REASON_TO_INPUT[reason]
        for reason in reasons
        if reason in REASON_TO_INPUT
    }
    if "DEPENDENCY_HEAD_CHANGED" in reasons:
        changed_inputs |= _dependency_changed_inputs(
            binding["dependency_heads"],
            current["dependency_heads"],
        )

    if reasons:
        state = "STALE"
    elif binding["provenance_state"] == "UNKNOWN":
        state = "UNKNOWN"
        reasons = ["PROVENANCE_UNKNOWN"]
    else:
        state = "CURRENT"

    return (
        {
            "evidence_id": binding["evidence_id"],
            "evidence_ref": binding["evidence_ref"],
            "evidence_digest": binding["evidence_digest"],
            "verification_method_id": binding["verification_method_id"],
            "state": state,
            "reasons": sorted(set(reasons)),
        },
        changed_inputs,
    )


def _method_results(
    required_method_ids: list[str],
    evidence_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_method: dict[str, list[dict[str, Any]]] = {}
    for result in evidence_results:
        by_method.setdefault(result["verification_method_id"], []).append(result)

    rows: list[dict[str, Any]] = []
    for method_id in required_method_ids:
        matches = by_method.get(method_id, [])
        states = {row["state"] for row in matches}
        if not matches:
            state = "MISSING"
        elif "CURRENT" in states:
            state = "CURRENT"
        elif "STALE" in states:
            state = "STALE"
        else:
            state = "UNKNOWN"
        rows.append({
            "method_id": method_id,
            "state": state,
            "evidence_ids": sorted(row["evidence_id"] for row in matches),
        })
    return rows


def _overall_state(method_results: list[dict[str, Any]]) -> str:
    states = {row["state"] for row in method_results}
    if "MISSING" in states:
        return "MISSING"
    if "STALE" in states:
        return "STALE"
    if "UNKNOWN" in states:
        return "UNKNOWN"
    return "CURRENT"


def _validate_method_maps(
    required: set[str],
    method_material_inputs: Any,
    method_rerun_policy: Any,
) -> tuple[dict[str, set[str]], dict[str, str]]:
    require(isinstance(method_material_inputs, dict), "method_material_inputs must be object")
    require(isinstance(method_rerun_policy, dict), "method_rerun_policy must be object")
    require(
        set(method_material_inputs) <= required,
        "method_material_inputs contains non-required method",
    )
    require(
        set(method_rerun_policy) <= required,
        "method_rerun_policy contains non-required method",
    )

    materials: dict[str, set[str]] = {}
    for method_id, inputs in method_material_inputs.items():
        require(isinstance(inputs, list), f"{method_id} material inputs must be array")
        require(all(isinstance(item, str) and item for item in inputs), f"{method_id} has invalid material input")
        materials[method_id] = set(inputs)

    policies: dict[str, str] = {}
    for method_id, policy in method_rerun_policy.items():
        require(
            policy in {"DECLARED_MATERIAL_INPUTS", "FULL_REQUIRED_SET"},
            f"{method_id} has invalid rerun policy",
        )
        policies[method_id] = policy
    return materials, policies


def _replay_plan(
    *,
    required_method_ids: list[str],
    method_results: list[dict[str, Any]],
    evidence_results: list[dict[str, Any]],
    changed_by_evidence: dict[str, set[str]],
    method_material_inputs: dict[str, set[str]],
    method_rerun_policy: dict[str, str],
) -> dict[str, Any]:
    required = set(required_method_ids)
    state_by_method = {row["method_id"]: row["state"] for row in method_results}
    if all(state == "CURRENT" for state in state_by_method.values()):
        return {
            "mode": "NO_REPLAY",
            "changed_inputs": [],
            "rerun_method_ids": [],
        }

    gap_methods = {
        method_id
        for method_id, state in state_by_method.items()
        if state in {"MISSING", "UNKNOWN"}
    }
    stale_methods = {
        method_id
        for method_id, state in state_by_method.items()
        if state == "STALE"
    }

    # A missing/unknown method with unspecified or full-set policy cannot be safely
    # narrowed. This is deliberately fail-conservative.
    for method_id in gap_methods:
        policy = method_rerun_policy.get(method_id)
        if policy != "DECLARED_MATERIAL_INPUTS":
            return {
                "mode": "CONSERVATIVE_FULL_REQUIRED_SET"
                if policy is None
                else "FULL_REQUIRED_SET",
                "changed_inputs": [],
                "rerun_method_ids": sorted(required),
            }

    changed_inputs: set[str] = set()
    stale_evidence_ids: set[str] = set()
    for row in evidence_results:
        if row["verification_method_id"] in stale_methods and row["state"] == "STALE":
            stale_evidence_ids.add(row["evidence_id"])
            changed_inputs |= changed_by_evidence.get(row["evidence_id"], set())

    if stale_methods:
        # Every stale method must have a declared input map that explains at least one
        # observed changed input; otherwise selective replay is not justified.
        for method_id in stale_methods:
            policy = method_rerun_policy.get(method_id)
            if policy is None:
                return {
                    "mode": "CONSERVATIVE_FULL_REQUIRED_SET",
                    "changed_inputs": sorted(changed_inputs),
                    "rerun_method_ids": sorted(required),
                }
            if policy == "FULL_REQUIRED_SET":
                return {
                    "mode": "FULL_REQUIRED_SET",
                    "changed_inputs": sorted(changed_inputs),
                    "rerun_method_ids": sorted(required),
                }
            inputs = method_material_inputs.get(method_id)
            if inputs is None or not (inputs & changed_inputs):
                return {
                    "mode": "CONSERVATIVE_FULL_REQUIRED_SET",
                    "changed_inputs": sorted(changed_inputs),
                    "rerun_method_ids": sorted(required),
                }

        local_plan = LOCAL.replay_plan(
            required_method_ids=required,
            method_material_inputs=method_material_inputs,
            method_rerun_policy=method_rerun_policy,
            changed_inputs=changed_inputs,
        )
        if local_plan["mode"] in {"FULL_REQUIRED_SET", "CONSERVATIVE_FULL_REQUIRED_SET"}:
            return {
                "mode": local_plan["mode"],
                "changed_inputs": sorted(changed_inputs),
                "rerun_method_ids": sorted(required),
            }
        rerun = set(local_plan["rerun_method_ids"]) | stale_methods | gap_methods
        return {
            "mode": "SELECTIVE_PLUS_GAPS" if gap_methods else "SELECTIVE_DECLARED_INPUTS",
            "changed_inputs": sorted(changed_inputs),
            "rerun_method_ids": sorted(rerun),
        }

    return {
        "mode": "GAP_REPLAY",
        "changed_inputs": [],
        "rerun_method_ids": sorted(gap_methods),
    }


def semantic_errors(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = set(value["required_method_ids"])
    methods = {row["method_id"]: row for row in value["method_results"]}
    if set(methods) != required:
        errors.append("method_results must exactly cover required_method_ids")

    evidence_ids = [row["evidence_id"] for row in value["evidence_results"]]
    if len(evidence_ids) != len(set(evidence_ids)):
        errors.append("evidence_results contains duplicate evidence_id")

    overall = value["overall"]
    state = overall["evidence_state"]
    candidate = value["candidate_sha"]
    if state == "CURRENT":
        if overall["evidence_candidate_sha"] != candidate:
            errors.append("CURRENT evidence must bind exact candidate_sha")
        if overall["evidence_ledger_ref"] != value["source_ledger"]["ledger_ref"]:
            errors.append("CURRENT evidence must bind source ledger ref")
    else:
        if overall["evidence_candidate_sha"] is not None:
            errors.append("non-CURRENT evidence cannot claim exact evidence_candidate_sha")
        if state == "MISSING" and overall["evidence_ledger_ref"] is not None:
            errors.append("MISSING evidence cannot populate execution ledger ref")

    rerun = set(value["replay_plan"]["rerun_method_ids"])
    if not rerun <= required:
        errors.append("replay plan contains non-required method")
    if state == "CURRENT" and rerun:
        errors.append("CURRENT evidence cannot require replay")
    if state != "CURRENT" and not rerun:
        errors.append("non-CURRENT evidence requires non-empty replay plan")

    return errors


def derive_evidence_freshness(
    *,
    evidence_bindings: list[dict[str, Any]],
    current: dict[str, Any],
    ledger_ref: str,
    required_method_ids: list[str],
    method_material_inputs: dict[str, list[str]],
    method_rerun_policy: dict[str, str],
) -> dict[str, Any]:
    require(isinstance(evidence_bindings, list), "evidence_bindings must be array")
    require(isinstance(ledger_ref, str) and bool(ledger_ref), "ledger_ref is required")
    require(
        isinstance(required_method_ids, list)
        and required_method_ids
        and len(required_method_ids) == len(set(required_method_ids))
        and all(isinstance(item, str) and item for item in required_method_ids),
        "required_method_ids must be non-empty unique strings",
    )

    before = canonical_digest(evidence_bindings)
    normalized = [_validate_binding(row) for row in evidence_bindings]
    ids = [row["evidence_id"] for row in normalized]
    require(len(ids) == len(set(ids)), "duplicate evidence_id")
    current_value = _validate_current(current)
    materials, policies = _validate_method_maps(
        set(required_method_ids),
        method_material_inputs,
        method_rerun_policy,
    )

    evidence_results: list[dict[str, Any]] = []
    changed_by_evidence: dict[str, set[str]] = {}
    for binding in normalized:
        result, changed_inputs = _evidence_result(binding, current_value)
        evidence_results.append(result)
        changed_by_evidence[binding["evidence_id"]] = changed_inputs
    evidence_results.sort(key=lambda row: row["evidence_id"])

    methods = _method_results(sorted(required_method_ids), evidence_results)
    overall_state = _overall_state(methods)
    replay = _replay_plan(
        required_method_ids=sorted(required_method_ids),
        method_results=methods,
        evidence_results=evidence_results,
        changed_by_evidence=changed_by_evidence,
        method_material_inputs=materials,
        method_rerun_policy=policies,
    )
    after = canonical_digest(evidence_bindings)
    require(before == after, "freshness derivation mutated source evidence")

    result = {
        "schema_version": "EVIDENCE_FRESHNESS_V1",
        "authority": "EVIDENCE_FRESHNESS_PROJECTION",
        "candidate_sha": current_value["candidate_sha"],
        "source_ledger": {
            "ledger_ref": ledger_ref,
            "ledger_digest": _ledger_digest(normalized),
            "evidence_count": len(normalized),
        },
        "current_basis": {
            key: copy.deepcopy(current_value[key])
            for key in (
                "acceptance_epoch_id",
                "project_protocol_digest",
                "acceptance_profile_digest",
                "protected_surface_digest",
                "environment_digest",
                "dependency_heads",
            )
        },
        "required_method_ids": sorted(required_method_ids),
        "evidence_results": evidence_results,
        "method_results": methods,
        "overall": {
            "evidence_state": overall_state,
            "evidence_candidate_sha": (
                current_value["candidate_sha"]
                if overall_state == "CURRENT"
                else None
            ),
            "evidence_ledger_ref": (
                ledger_ref
                if overall_state in {"CURRENT", "STALE", "UNKNOWN"}
                else None
            ),
        },
        "replay_plan": replay,
        "authority_boundaries": {
            "mutates_source_evidence": False,
            "emits_engineering_pass": False,
            "performs_lifecycle_advance": False,
            "grants_merge_authority": False,
            "grants_production_cutover": False,
        },
    }

    errors = schema_validate("evidence-freshness", result, "evidence-freshness")
    errors.extend(
        f"evidence-freshness: {error}"
        for error in semantic_errors(result)
    )
    require(not errors, "; ".join(errors))
    return result


def validate_evidence_freshness(
    value: Any,
    request: Any,
    label: str = "evidence-freshness",
) -> list[str]:
    errors = schema_validate("evidence-freshness", value, label)
    if errors:
        return errors
    if not isinstance(value, dict):
        return [f"{label}: evidence freshness projection must be an object"]
    errors = [f"{label}: {error}" for error in semantic_errors(value)]

    if not isinstance(request, dict):
        errors.append(f"{label}: evidence freshness validation requires source request")
        return errors

    expected = {
        "evidence_bindings",
        "current",
        "ledger_ref",
        "required_method_ids",
        "method_material_inputs",
        "method_rerun_policy",
    }
    if set(request) != expected:
        errors.append(f"{label}: source request has unexpected/missing fields")
        return errors

    try:
        derived = derive_evidence_freshness(**copy.deepcopy(request))
    except Exception as exc:
        errors.append(f"{label}: source request replay failed: {exc}")
        return errors

    if value != derived:
        errors.append(
            f"{label}: stored freshness projection must exactly equal source-request derivation"
        )
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Derive exact-candidate evidence freshness without mutating historical evidence."
    )
    parser.add_argument("request")
    args = parser.parse_args()

    request = load_yaml(Path(args.request))
    require(isinstance(request, dict), "freshness request must be object")
    expected = {
        "evidence_bindings",
        "current",
        "ledger_ref",
        "required_method_ids",
        "method_material_inputs",
        "method_rerun_policy",
    }
    require(set(request) == expected, "freshness request has unexpected/missing fields")
    result = derive_evidence_freshness(**request)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
