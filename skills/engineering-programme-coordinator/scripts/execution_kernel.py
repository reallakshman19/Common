#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from coordlib import load_yaml, validate as schema_validate


def _decision(action: str, reason_code: str, *basis_refs: str) -> dict[str, Any]:
    refs = [ref for ref in basis_refs if ref]
    if not refs:
        refs = [f"derived://{reason_code.lower()}"]
    return {
        "type": action,
        "reason_code": reason_code,
        "basis_refs": refs,
    }


def _capability_or_reconcile(
    allowed: set[str],
    capability_action: str,
    decision_type: str,
    reason_code: str,
    *basis_refs: str,
) -> dict[str, Any]:
    if capability_action in allowed:
        return _decision(decision_type, reason_code, *basis_refs)
    return _decision(
        "RECONCILE",
        "CAPABILITY_MISSING",
        f"capability://{capability_action}",
    )


def derive_next_action(state: dict[str, Any]) -> dict[str, Any]:
    lifecycle = state["lifecycle"]
    capability = state["capability"]
    repository = state["repository"]
    dependencies = state["dependencies"]
    verification = state["verification"]
    contradictions = state["contradictions"]

    # Contradictions dominate every other projection. A STOPPED claim that
    # contradicts other canonical state still needs reconciliation.
    if contradictions:
        return _decision(
            "RECONCILE",
            "STATE_CONTRADICTION",
            *(f"contradiction://{index + 1}" for index, _ in enumerate(contradictions)),
        )

    if lifecycle["stage"] == "STOPPED":
        return _decision(
            "STOPPED",
            "LIFECYCLE_STOPPED",
            lifecycle.get("last_completed_checkpoint") or "state://lifecycle",
        )

    blocked = dependencies["blocked"]
    if blocked:
        return _decision(
            "WAIT_DEPENDENCY",
            "BLOCKED_DEPENDENCY",
            *(f"dependency://{row['id']}" for row in blocked),
        )

    if capability["resolution_state"] != "VERIFIED":
        return _decision(
            "RECONCILE",
            "CAPABILITY_UNVERIFIED",
            capability.get("resolver_ref") or "state://capability-resolution",
        )

    active_role = capability["active_role"]
    allowed = set(capability["allowed_actions"])
    if active_role == "NONE":
        return _decision(
            "RECONCILE",
            "ACTIVE_ROLE_MISSING",
            *(capability.get("capability_basis") or ["state://capability"]),
        )

    candidate_sha = repository["candidate_sha"]
    if candidate_sha is None:
        return _capability_or_reconcile(
            allowed,
            "WRITE_CANDIDATE",
            "IMPLEMENT",
            "IMPLEMENTATION_REQUIRED",
            repository["target_sha"],
        )

    evidence_state = verification["evidence_state"]
    evidence_candidate_sha = verification["evidence_candidate_sha"]
    if evidence_state != "CURRENT" or evidence_candidate_sha != candidate_sha:
        return _capability_or_reconcile(
            allowed,
            "RUN_VERIFICATION",
            "VERIFY_CANDIDATE",
            "VERIFICATION_REQUIRED",
            candidate_sha,
            verification.get("expectation_manifest_ref") or "state://expectation-manifest",
        )

    # Once evidence is CURRENT and bound to the exact candidate, the deterministic
    # evidence gate is the single disposition selector. Visible unresolved critical
    # rows remain semantic consistency inputs, but they must not pre-empt a current
    # gate decision (for example, a source-valid ESCALATE after local exhaustion).
    gate = verification["gate"]
    disposition = gate["disposition"]
    gate_ref = gate.get("result_ref") or "state://evidence-gate"

    if disposition == "NOT_AVAILABLE":
        return _capability_or_reconcile(
            allowed,
            "RUN_VERIFICATION",
            "VERIFY_CANDIDATE",
            "GATE_REQUIRED",
            gate_ref,
        )
    if disposition == "REPLAY":
        return _capability_or_reconcile(
            allowed,
            "RUN_VERIFICATION",
            "VERIFY_CANDIDATE",
            "GATE_REPLAY",
            gate_ref,
        )
    if disposition == "REPAIR":
        return _capability_or_reconcile(
            allowed,
            "REPAIR_CANDIDATE",
            "REPAIR_CANDIDATE",
            "GATE_REPAIR",
            gate_ref,
        )
    if disposition == "ESCALATE":
        return _capability_or_reconcile(
            allowed,
            "ESCALATE",
            "ESCALATE",
            "GATE_ESCALATE",
            gate_ref,
        )

    # ADVANCE_ELIGIBLE is still only an evidence-gate disposition. The coordinator
    # can request a Local transition but never performs or authorizes that transition.
    return _capability_or_reconcile(
        allowed,
        "REQUEST_STAGE_ADVANCE",
        "REQUEST_STAGE_ADVANCE",
        "ADVANCEMENT_ELIGIBLE",
        gate_ref,
    )


def semantic_errors(state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    capability = state["capability"]
    repository = state["repository"]
    verification = state["verification"]

    allowed = set(capability["allowed_actions"])
    forbidden = set(capability["forbidden_actions"])
    overlap = sorted(allowed & forbidden)
    if overlap:
        errors.append(
            "capability actions cannot be both allowed and forbidden: "
            + ", ".join(overlap)
        )

    resolution_state = capability["resolution_state"]
    resolver_ref = capability["resolver_ref"]
    resolver_digest = capability["resolver_digest"]
    if resolution_state == "VERIFIED":
        if not resolver_ref or not resolver_digest:
            errors.append(
                "VERIFIED capability resolution requires exact resolver_ref and resolver_digest"
            )
    else:
        if allowed:
            errors.append("UNVERIFIED capability resolution requires allowed_actions to be empty")
        if resolver_ref is not None or resolver_digest is not None:
            errors.append(
                "UNVERIFIED capability resolution cannot claim resolver_ref or resolver_digest"
            )

    if capability["active_role"] == "NONE" and allowed:
        errors.append("active_role NONE requires allowed_actions to be empty")

    candidate_sha = repository["candidate_sha"]
    evidence_state = verification["evidence_state"]
    evidence_sha = verification["evidence_candidate_sha"]
    ledger_ref = verification["evidence_ledger_ref"]
    unresolved = verification["unresolved_critical"]
    gate = verification["gate"]
    gate_disposition = gate["disposition"]
    gate_sha = gate["candidate_sha"]
    gate_ref = gate["result_ref"]
    gate_digest = gate["result_digest"]

    if candidate_sha is None:
        if evidence_state != "MISSING":
            errors.append("missing candidate requires evidence_state MISSING")
        if evidence_sha is not None:
            errors.append("missing candidate cannot have evidence_candidate_sha")
        if ledger_ref is not None:
            errors.append("missing candidate cannot have evidence_ledger_ref")
        if unresolved:
            errors.append("missing candidate cannot have unresolved critical obligations")
        if gate_disposition != "NOT_AVAILABLE":
            errors.append("missing candidate requires gate disposition NOT_AVAILABLE")
        if gate_sha is not None or gate_ref is not None or gate_digest is not None:
            errors.append("missing candidate cannot carry evidence-gate result identity")

    if evidence_state == "CURRENT":
        if candidate_sha is None:
            errors.append("CURRENT evidence requires candidate_sha")
        if evidence_sha != candidate_sha:
            errors.append("CURRENT evidence must bind the exact candidate_sha")
        if not ledger_ref:
            errors.append("CURRENT evidence requires evidence_ledger_ref")

    if evidence_state == "MISSING":
        if evidence_sha is not None:
            errors.append("MISSING evidence cannot have evidence_candidate_sha")
        if ledger_ref is not None:
            errors.append("MISSING evidence cannot have evidence_ledger_ref")

    if gate_disposition == "NOT_AVAILABLE":
        if gate_sha is not None or gate_ref is not None or gate_digest is not None:
            errors.append("NOT_AVAILABLE gate cannot carry candidate/ref/digest")
    else:
        if candidate_sha is None:
            errors.append("evidence-gate result requires candidate_sha")
        if gate_sha != candidate_sha:
            errors.append("evidence-gate result must bind the exact candidate_sha")
        if not gate_ref or not gate_digest:
            errors.append("evidence-gate result requires result_ref and result_digest")

    refuted = [row for row in unresolved if row["state"] == "REFUTED"]
    unknown = [row for row in unresolved if row["state"] == "UNKNOWN"]

    if gate_disposition == "ADVANCE_ELIGIBLE":
        if evidence_state != "CURRENT" or evidence_sha != candidate_sha:
            errors.append("ADVANCE_ELIGIBLE requires CURRENT exact-candidate evidence")
        if unresolved:
            errors.append("ADVANCE_ELIGIBLE cannot coexist with unresolved critical obligations")

    if gate_disposition in {"REPLAY", "ESCALATE"} and refuted:
        errors.append(
            f"{gate_disposition} cannot coexist with critical REFUTED obligations; "
            "current gate must select REPAIR"
        )

    if gate_disposition == "ESCALATE" and evidence_state != "CURRENT":
        errors.append("ESCALATE requires CURRENT exact-candidate evidence")

    if gate_disposition == "REPAIR" and evidence_state != "CURRENT":
        errors.append("REPAIR requires CURRENT exact-candidate evidence")

    # UNKNOWN is compatible with either REPLAY (local work remains) or ESCALATE
    # (local exhaustion is proven by the source-bound gate compiler). The compact
    # execution projection intentionally does not duplicate that exhaustion record.
    _ = unknown

    derived = derive_next_action(state)
    stored = state["next_action"]
    if stored != derived:
        errors.append(
            "stored next_action must exactly equal kernel-derived next_action "
            f"(stored={stored!r}, derived={derived!r})"
        )

    return errors


def validate_execution_state(value: Any, label: str = "execution-state") -> list[str]:
    errors = schema_validate("execution-state", value, label)
    if errors:
        return errors
    if not isinstance(value, dict):
        return [f"{label}: execution state must be an object"]
    return [f"{label}: {error}" for error in semantic_errors(value)]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Validate EXECUTION_STATE_V1 and deterministic next-safe-action projection. "
            "The result never performs Local lifecycle transition."
        )
    )
    parser.add_argument("path")
    args = parser.parse_args()

    path = Path(args.path)
    value = load_yaml(path)
    errors = validate_execution_state(value, path.name)
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print(f"OK: execution-state projection: {path}")


if __name__ == "__main__":
    main()
