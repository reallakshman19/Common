import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from execution_kernel import derive_next_action, validate_execution_state


SHA = "a" * 40
CANDIDATE = "c" * 40
DIGEST = "b" * 64
RESOLVER_REF = f"reallaksh19/Common@{SHA}:skills/authority-resolver"


def gate(disposition="NOT_AVAILABLE", candidate_sha=None):
    if disposition == "NOT_AVAILABLE":
        return {
            "disposition": disposition,
            "candidate_sha": None,
            "result_ref": None,
            "result_digest": None,
        }
    return {
        "disposition": disposition,
        "candidate_sha": candidate_sha or CANDIDATE,
        "result_ref": "evidence-gate://result/1",
        "result_digest": DIGEST,
    }


def state():
    return {
        "schema_version": "EXECUTION_STATE_V1",
        "authority": "EXECUTION_STATE_PROJECTION",
        "identity": {
            "parent": "PARENT-527",
            "responsibility": "PRD-527-P1-R2",
            "attempt": 1,
        },
        "repository": {
            "target_ref": "main",
            "target_sha": SHA,
            "branch": "prod/527-p1-r2-execution-kernel",
            "pr": None,
            "candidate_sha": None,
        },
        "protocol": {
            "local_ref": f"reallaksh19/Common@{SHA}:skills/Local_PR_Deliverty_v1.1",
            "local_digest": DIGEST,
            "v35_ref": f"reallaksh19/Common@{SHA}:skills/engineering-pr-delivery-v3.5",
            "v35_digest": DIGEST,
            "common_reviewer_ref": f"reallaksh19/Common@{SHA}:skills/common-reviewer-protocol-v1.0",
            "common_reviewer_digest": DIGEST,
        },
        "capability": {
            "resolution_state": "VERIFIED",
            "resolver_ref": RESOLVER_REF,
            "resolver_digest": DIGEST,
            "active_role": "CODER",
            "capability_basis": ["authority://resolved"],
            "allowed_actions": ["WRITE_CANDIDATE", "RUN_VERIFICATION"],
            "forbidden_actions": ["REQUEST_STAGE_ADVANCE"],
        },
        "lifecycle": {
            "stage": "CODING",
            "last_completed_checkpoint": None,
        },
        "dependencies": {
            "satisfied": [],
            "blocked": [],
        },
        "verification": {
            "expectation_manifest_ref": "manifest://L0-L1-L2",
            "evidence_ledger_ref": None,
            "evidence_state": "MISSING",
            "evidence_candidate_sha": None,
            "unresolved_critical": [],
            "gate": gate(),
        },
        "contradictions": [],
        "next_action": {
            "type": "IMPLEMENT",
            "reason_code": "IMPLEMENTATION_REQUIRED",
            "basis_refs": [SHA],
        },
    }


def set_derived(value):
    value["next_action"] = derive_next_action(value)
    return value


def current_candidate(value):
    value["repository"]["candidate_sha"] = CANDIDATE
    value["verification"]["evidence_state"] = "CURRENT"
    value["verification"]["evidence_candidate_sha"] = CANDIDATE
    value["verification"]["evidence_ledger_ref"] = "ledger://current"
    return value


class ExecutionKernelTests(unittest.TestCase):
    def test_missing_candidate_derives_implement(self):
        value = state()
        self.assertEqual(derive_next_action(value)["type"], "IMPLEMENT")
        self.assertEqual(validate_execution_state(value), [])

    def test_contradiction_dominates_stopped_lifecycle(self):
        value = state()
        value["lifecycle"]["stage"] = "STOPPED"
        value["contradictions"] = ["provider state conflicts with Local state"]
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "RECONCILE")
        self.assertEqual(value["next_action"]["reason_code"], "STATE_CONTRADICTION")
        self.assertEqual(validate_execution_state(value), [])

    def test_stopped_lifecycle_derives_stopped_when_consistent(self):
        value = state()
        value["lifecycle"]["stage"] = "STOPPED"
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "STOPPED")
        self.assertEqual(validate_execution_state(value), [])

    def test_blocked_dependency_derives_wait(self):
        value = state()
        value["dependencies"]["blocked"] = [{
            "id": "DEP-1",
            "reason": "upstream result unavailable",
            "evidence_refs": ["provider://dep-1"],
        }]
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "WAIT_DEPENDENCY")
        self.assertEqual(validate_execution_state(value), [])

    def test_unverified_capability_fails_closed_before_material_action(self):
        value = state()
        value["capability"] = {
            "resolution_state": "UNVERIFIED",
            "resolver_ref": None,
            "resolver_digest": None,
            "active_role": "CODER",
            "capability_basis": ["caller://claimed-role"],
            "allowed_actions": [],
            "forbidden_actions": ["REQUEST_STAGE_ADVANCE"],
        }
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "RECONCILE")
        self.assertEqual(value["next_action"]["reason_code"], "CAPABILITY_UNVERIFIED")
        self.assertEqual(validate_execution_state(value), [])

    def test_unverified_capability_cannot_carry_allowed_actions(self):
        value = state()
        value["capability"]["resolution_state"] = "UNVERIFIED"
        value["capability"]["resolver_ref"] = None
        value["capability"]["resolver_digest"] = None
        errors = validate_execution_state(value)
        self.assertTrue(any("allowed_actions" in error for error in errors), errors)

    def test_verified_capability_requires_exact_resolver_identity(self):
        value = state()
        value["capability"]["resolver_ref"] = None
        set_derived(value)
        errors = validate_execution_state(value)
        self.assertTrue(any("resolver_ref" in error for error in errors), errors)

    def test_active_role_none_fails_closed(self):
        value = state()
        value["capability"]["active_role"] = "NONE"
        value["capability"]["allowed_actions"] = []
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "RECONCILE")
        self.assertEqual(value["next_action"]["reason_code"], "ACTIVE_ROLE_MISSING")
        self.assertEqual(validate_execution_state(value), [])

    def test_stale_evidence_derives_verify(self):
        value = state()
        value["repository"]["candidate_sha"] = CANDIDATE
        value["verification"]["evidence_state"] = "STALE"
        value["verification"]["evidence_candidate_sha"] = "d" * 40
        value["verification"]["evidence_ledger_ref"] = "ledger://old"
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "VERIFY_CANDIDATE")
        self.assertEqual(validate_execution_state(value), [])

    def test_current_evidence_must_bind_exact_candidate(self):
        value = state()
        value["repository"]["candidate_sha"] = CANDIDATE
        value["verification"]["evidence_state"] = "CURRENT"
        value["verification"]["evidence_candidate_sha"] = "d" * 40
        value["verification"]["evidence_ledger_ref"] = "ledger://1"
        set_derived(value)
        errors = validate_execution_state(value)
        self.assertTrue(any("exact candidate_sha" in error for error in errors), errors)

    def test_current_refuted_without_gate_requires_gate_first(self):
        value = current_candidate(state())
        value["capability"]["allowed_actions"] = ["RUN_VERIFICATION", "REPAIR_CANDIDATE"]
        value["capability"]["forbidden_actions"] = ["REQUEST_STAGE_ADVANCE"]
        value["verification"]["unresolved_critical"] = [{
            "id": "L0-CRIT-1",
            "state": "REFUTED",
            "evidence_refs": ["evidence://failure"],
        }]
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "VERIFY_CANDIDATE")
        self.assertEqual(value["next_action"]["reason_code"], "GATE_REQUIRED")
        self.assertEqual(validate_execution_state(value), [])

    def test_current_unknown_without_gate_requires_gate_first(self):
        value = current_candidate(state())
        value["verification"]["unresolved_critical"] = [{
            "id": "L2-CRIT-2",
            "state": "UNKNOWN",
            "evidence_refs": [],
        }]
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "VERIFY_CANDIDATE")
        self.assertEqual(value["next_action"]["reason_code"], "GATE_REQUIRED")
        self.assertEqual(validate_execution_state(value), [])

    def test_current_evidence_alone_cannot_advance_without_gate(self):
        value = current_candidate(state())
        value["capability"]["allowed_actions"] = ["RUN_VERIFICATION", "REQUEST_STAGE_ADVANCE"]
        value["capability"]["forbidden_actions"] = []
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "VERIFY_CANDIDATE")
        self.assertEqual(value["next_action"]["reason_code"], "GATE_REQUIRED")
        self.assertEqual(validate_execution_state(value), [])

    def test_gate_replay_derives_verification(self):
        value = current_candidate(state())
        value["verification"]["gate"] = gate("REPLAY")
        set_derived(value)
        self.assertEqual(value["next_action"]["reason_code"], "GATE_REPLAY")
        self.assertEqual(validate_execution_state(value), [])

    def test_gate_repair_derives_repair(self):
        value = current_candidate(state())
        value["capability"]["allowed_actions"] = ["REPAIR_CANDIDATE"]
        value["capability"]["forbidden_actions"] = ["REQUEST_STAGE_ADVANCE"]
        value["verification"]["gate"] = gate("REPAIR")
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "REPAIR_CANDIDATE")
        self.assertEqual(value["next_action"]["reason_code"], "GATE_REPAIR")
        self.assertEqual(validate_execution_state(value), [])

    def test_gate_escalate_derives_escalation(self):
        value = current_candidate(state())
        value["capability"]["allowed_actions"] = ["ESCALATE"]
        value["capability"]["forbidden_actions"] = ["REQUEST_STAGE_ADVANCE"]
        value["verification"]["gate"] = gate("ESCALATE")
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "ESCALATE")
        self.assertEqual(validate_execution_state(value), [])

    def test_gate_escalate_with_unknown_is_reachable(self):
        value = current_candidate(state())
        value["capability"]["allowed_actions"] = ["ESCALATE"]
        value["capability"]["forbidden_actions"] = ["REQUEST_STAGE_ADVANCE"]
        value["verification"]["unresolved_critical"] = [{
            "id": "L2-CRIT-2",
            "state": "UNKNOWN",
            "evidence_refs": [],
        }]
        value["verification"]["gate"] = gate("ESCALATE")
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "ESCALATE")
        self.assertEqual(value["next_action"]["reason_code"], "GATE_ESCALATE")
        self.assertEqual(validate_execution_state(value), [])

    def test_gate_repair_with_refuted_is_reachable(self):
        value = current_candidate(state())
        value["capability"]["allowed_actions"] = ["REPAIR_CANDIDATE"]
        value["capability"]["forbidden_actions"] = ["REQUEST_STAGE_ADVANCE"]
        value["verification"]["unresolved_critical"] = [{
            "id": "L0-CRIT-1",
            "state": "REFUTED",
            "evidence_refs": ["evidence://failure"],
        }]
        value["verification"]["gate"] = gate("REPAIR")
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "REPAIR_CANDIDATE")
        self.assertEqual(value["next_action"]["reason_code"], "GATE_REPAIR")
        self.assertEqual(validate_execution_state(value), [])

    def test_gate_replay_cannot_hide_refuted_critical(self):
        value = current_candidate(state())
        value["verification"]["unresolved_critical"] = [{
            "id": "L0-CRIT-1",
            "state": "REFUTED",
            "evidence_refs": ["evidence://failure"],
        }]
        value["verification"]["gate"] = gate("REPLAY")
        set_derived(value)
        errors = validate_execution_state(value)
        self.assertTrue(any("current gate must select REPAIR" in error for error in errors), errors)

    def test_gate_escalate_cannot_hide_refuted_critical(self):
        value = current_candidate(state())
        value["capability"]["allowed_actions"] = ["ESCALATE"]
        value["capability"]["forbidden_actions"] = ["REQUEST_STAGE_ADVANCE"]
        value["verification"]["unresolved_critical"] = [{
            "id": "L0-CRIT-1",
            "state": "REFUTED",
            "evidence_refs": ["evidence://failure"],
        }]
        value["verification"]["gate"] = gate("ESCALATE")
        set_derived(value)
        errors = validate_execution_state(value)
        self.assertTrue(any("current gate must select REPAIR" in error for error in errors), errors)

    def test_advance_eligible_with_unresolved_critical_is_rejected(self):
        value = current_candidate(state())
        value["capability"]["allowed_actions"] = ["REQUEST_STAGE_ADVANCE"]
        value["verification"]["unresolved_critical"] = [{
            "id": "L2-CRIT-2",
            "state": "UNKNOWN",
            "evidence_refs": [],
        }]
        value["verification"]["gate"] = gate("ADVANCE_ELIGIBLE")
        set_derived(value)
        errors = validate_execution_state(value)
        self.assertTrue(
            any(
                "ADVANCE_ELIGIBLE cannot coexist with unresolved critical obligations" in error
                for error in errors
            ),
            errors,
        )

    def test_advance_eligible_only_requests_local_stage_advance(self):
        value = current_candidate(state())
        value["capability"]["allowed_actions"] = ["REQUEST_STAGE_ADVANCE"]
        value["capability"]["forbidden_actions"] = []
        value["verification"]["gate"] = gate("ADVANCE_ELIGIBLE")
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "REQUEST_STAGE_ADVANCE")
        self.assertEqual(value["next_action"]["reason_code"], "ADVANCEMENT_ELIGIBLE")
        self.assertEqual(validate_execution_state(value), [])

    def test_advance_eligible_without_capability_fails_closed(self):
        value = current_candidate(state())
        value["capability"]["allowed_actions"] = []
        value["capability"]["forbidden_actions"] = ["REQUEST_STAGE_ADVANCE"]
        value["verification"]["gate"] = gate("ADVANCE_ELIGIBLE")
        set_derived(value)
        self.assertEqual(value["next_action"]["type"], "RECONCILE")
        self.assertEqual(value["next_action"]["reason_code"], "CAPABILITY_MISSING")
        self.assertEqual(validate_execution_state(value), [])

    def test_gate_candidate_mismatch_is_rejected(self):
        value = current_candidate(state())
        value["verification"]["gate"] = gate("ADVANCE_ELIGIBLE", candidate_sha="d" * 40)
        set_derived(value)
        errors = validate_execution_state(value)
        self.assertTrue(any("gate result must bind" in error for error in errors), errors)

    def test_allowed_and_forbidden_actions_cannot_overlap(self):
        value = state()
        value["capability"]["forbidden_actions"] = ["WRITE_CANDIDATE"]
        set_derived(value)
        errors = validate_execution_state(value)
        self.assertTrue(any("both allowed and forbidden" in error for error in errors), errors)

    def test_stored_next_action_cannot_disagree_with_kernel(self):
        value = state()
        value["next_action"] = {
            "type": "REQUEST_STAGE_ADVANCE",
            "reason_code": "ADVANCEMENT_ELIGIBLE",
            "basis_refs": ["fake://basis"],
        }
        errors = validate_execution_state(value)
        self.assertTrue(any("exactly equal" in error for error in errors), errors)


    def test_stored_basis_refs_cannot_replace_derived_provenance(self):
        value = state()
        value["next_action"] = {
            "type": "IMPLEMENT",
            "reason_code": "IMPLEMENTATION_REQUIRED",
            "basis_refs": ["caller://fabricated-basis"],
        }
        errors = validate_execution_state(value)
        self.assertTrue(any("exactly equal" in error for error in errors), errors)

    def test_schema_rejects_advance_stage_capability(self):
        value = state()
        value["capability"]["allowed_actions"] = ["ADVANCE_STAGE"]
        errors = validate_execution_state(value)
        self.assertTrue(any("ADVANCE_STAGE" in error for error in errors), errors)

    def test_schema_rejects_model_confidence_as_execution_authority(self):
        value = state()
        value["model_confidence"] = 0.99
        errors = validate_execution_state(value)
        self.assertTrue(any("Additional properties are not allowed" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
