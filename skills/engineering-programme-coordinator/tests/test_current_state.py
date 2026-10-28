import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from current_state import canonical_document_digest, validate_current_state


MAIN = "a" * 40
CANDIDATE = "c" * 40
DIGEST = "d" * 64


def execution_state(candidate_sha=CANDIDATE):
    return {
        "schema_version": "EXECUTION_STATE_V1",
        "authority": "EXECUTION_STATE_PROJECTION",
        "identity": {
            "parent": "COMMON-PROD-CONTROL-V1",
            "responsibility": "PRD-527-P1-R3B",
            "attempt": 1,
        },
        "repository": {
            "target_ref": "main",
            "target_sha": MAIN,
            "branch": "prod/527-p1-r3b-current-state",
            "pr": 549,
            "candidate_sha": candidate_sha,
        },
        "protocol": {
            "local_ref": f"reallaksh19/Common@{MAIN}:skills/Local_PR_Deliverty_v1.1",
            "local_digest": DIGEST,
            "v35_ref": f"reallaksh19/Common@{MAIN}:skills/engineering-pr-delivery-v3.5",
            "v35_digest": DIGEST,
            "common_reviewer_ref": f"reallaksh19/Common@{MAIN}:skills/common-reviewer-protocol-v1.0",
            "common_reviewer_digest": DIGEST,
        },
        "capability": {
            "resolution_state": "VERIFIED",
            "resolver_ref": f"reallaksh19/Common@{MAIN}:skills/authority-resolver",
            "resolver_digest": DIGEST,
            "active_role": "CODER",
            "capability_basis": ["authority://resolved"],
            "allowed_actions": ["RUN_VERIFICATION"],
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
            "expectation_manifest_ref": "manifest://1",
            "evidence_ledger_ref": None,
            "evidence_state": "STALE",
            "evidence_candidate_sha": None,
            "unresolved_critical": [],
            "gate": {
                "disposition": "NOT_AVAILABLE",
                "candidate_sha": None,
                "result_ref": None,
                "result_digest": None,
            },
        },
        "contradictions": [],
        "next_action": {
            "type": "VERIFY_CANDIDATE",
            "reason_code": "VERIFICATION_REQUIRED",
            "basis_refs": [CANDIDATE, "manifest://1"],
        },
    }


def current_state():
    execution = execution_state()
    execution_ref = "artifact://execution-state/current"
    return {
        "schema_version": "CURRENT_STATE_V1",
        "authority": "CURRENT_STATE_PROJECTION",
        "parent": {
            "programme_or_parent_id": "COMMON-PROD-CONTROL-V1",
            "parent_ref": "issue://527",
            "parent_contract_version": "CURRENT_STATE_V1",
            "main_sha": MAIN,
        },
        "active": {
            "phase": "PHASE-1-CANONICAL-RUNTIME",
            "prd_id": "PRD-527-P1-R3B",
            "issue_ref": "issue://548",
            "role": "CODER",
            "attempt": 1,
        },
        "candidate": {
            "state": "ACTIVE",
            "pr": 549,
            "branch": "prod/527-p1-r3b-current-state",
            "base_sha": MAIN,
            "head_sha": CANDIDATE,
            "changed_files": ["schemas/current-state.schema.yaml"],
        },
        "frontiers": {
            "material": "CURRENT_STATE_RUNTIME",
            "semantic": "NEXT_BOUND_TO_EXECUTION_STATE",
            "evidence": "SELF_REVIEW_PENDING",
        },
        "dependencies": [{
            "producer": "PRD-527-P1-R3A",
            "required_state": "COMPLETE",
            "observed_state": "VERIFIED",
            "evidence_ref": "issue://527/task-result/6011212048",
            "exact_result_ref": "commit://effcc90b8dd506cf6de1a0843e130813cd0db35d",
        }],
        "open_critical_findings": [],
        "open_critical_unknowns": [],
        "stale_evidence": [],
        "production": {
            "mode": "OFF",
            "authority_ref": None,
        },
        "merge_authority": {
            "state": "NOT_GRANTED",
            "authority_ref": None,
        },
        "next_action": {
            "execution_state_ref": execution_ref,
            "execution_state_digest": canonical_document_digest(execution),
            "type": execution["next_action"]["type"],
            "reason_code": execution["next_action"]["reason_code"],
            "basis_refs": execution["next_action"]["basis_refs"],
        },
        "forbidden_next_actions": ["REQUEST_STAGE_ADVANCE"],
        "source_refs": ["issue://527", "issue://548", execution_ref],
    }


class CurrentStateTests(unittest.TestCase):
    def test_active_projection_with_exact_execution_binding_is_valid(self):
        self.assertEqual(
            validate_current_state(current_state(), execution_state()),
            [],
        )

    def test_candidate_none_forbids_coordinates(self):
        value = current_state()
        value["candidate"] = {
            "state": "NONE",
            "pr": None,
            "branch": None,
            "base_sha": None,
            "head_sha": None,
            "changed_files": [],
        }
        execution = execution_state(candidate_sha=None)
        value["next_action"]["execution_state_digest"] = canonical_document_digest(execution)
        value["next_action"]["type"] = execution["next_action"]["type"]
        value["next_action"]["reason_code"] = execution["next_action"]["reason_code"]
        value["next_action"]["basis_refs"] = execution["next_action"]["basis_refs"]
        self.assertEqual(validate_current_state(value, execution), [])

    def test_candidate_none_rejects_head(self):
        value = current_state()
        value["candidate"]["state"] = "NONE"
        errors = validate_current_state(value, execution_state())
        self.assertTrue(any("candidate NONE" in error for error in errors), errors)

    def test_active_candidate_requires_exact_coordinates(self):
        value = current_state()
        value["candidate"]["head_sha"] = None
        errors = validate_current_state(value, execution_state())
        self.assertTrue(any("ACTIVE requires head_sha" in error for error in errors), errors)

    def test_verified_dependency_requires_exact_evidence(self):
        value = current_state()
        value["dependencies"][0]["exact_result_ref"] = None
        errors = validate_current_state(value, execution_state())
        self.assertTrue(any("requires evidence_ref and exact_result_ref" in error for error in errors), errors)

    def test_refuted_dependency_requires_exact_evidence(self):
        value = current_state()
        value["dependencies"][0]["observed_state"] = "REFUTED"
        value["dependencies"][0]["evidence_ref"] = None
        errors = validate_current_state(value, execution_state())
        self.assertTrue(any("REFUTED requires" in error for error in errors), errors)

    def test_off_mode_forbids_authority_ref(self):
        value = current_state()
        value["production"]["authority_ref"] = "owner://stale-cutover"
        errors = validate_current_state(value, execution_state())
        self.assertTrue(any("OFF cannot carry" in error for error in errors), errors)

    def test_non_off_mode_requires_authority_ref(self):
        value = current_state()
        value["production"]["mode"] = "SHADOW_ONLY"
        errors = validate_current_state(value, execution_state())
        self.assertTrue(any("requires authority_ref" in error for error in errors), errors)

    def test_owner_merge_grant_requires_authority_ref(self):
        value = current_state()
        value["merge_authority"]["state"] = "OWNER_GRANTED"
        errors = validate_current_state(value, execution_state())
        self.assertTrue(any("OWNER_GRANTED" in error for error in errors), errors)

    def test_not_granted_merge_forbids_authority_ref(self):
        value = current_state()
        value["merge_authority"]["authority_ref"] = "owner://old-merge"
        errors = validate_current_state(value, execution_state())
        self.assertTrue(any("NOT_GRANTED" in error for error in errors), errors)

    def test_next_action_cannot_also_be_forbidden(self):
        value = current_state()
        value["forbidden_next_actions"].append(value["next_action"]["type"])
        errors = validate_current_state(value, execution_state())
        self.assertTrue(any("cannot also appear" in error for error in errors), errors)

    def test_required_source_refs_must_be_present(self):
        value = current_state()
        value["source_refs"].remove("issue://548")
        errors = validate_current_state(value, execution_state())
        self.assertTrue(any("source_refs must include" in error for error in errors), errors)

    def test_unbound_current_state_validation_is_rejected(self):
        value = current_state()
        errors = validate_current_state(value, None)
        self.assertTrue(any("requires bound EXECUTION_STATE_V1" in error for error in errors), errors)

    def test_execution_digest_mismatch_is_rejected(self):
        value = current_state()
        value["next_action"]["execution_state_digest"] = "0" * 64
        errors = validate_current_state(value, execution_state())
        self.assertTrue(any("digest does not match" in error for error in errors), errors)

    def test_execution_action_mismatch_is_rejected(self):
        value = current_state()
        value["next_action"]["reason_code"] = "GATE_REQUIRED"
        errors = validate_current_state(value, execution_state())
        self.assertTrue(any("exactly mirror" in error for error in errors), errors)

    def test_execution_candidate_mismatch_is_rejected(self):
        value = current_state()
        execution = execution_state(candidate_sha="e" * 40)
        value["next_action"]["execution_state_digest"] = canonical_document_digest(execution)
        errors = validate_current_state(value, execution)
        self.assertTrue(any("candidate head_sha" in error for error in errors), errors)

    def test_execution_branch_mismatch_is_rejected(self):
        value = current_state()
        execution = execution_state()
        execution["repository"]["branch"] = "prod/other"
        value["next_action"]["execution_state_digest"] = canonical_document_digest(execution)
        errors = validate_current_state(value, execution)
        self.assertTrue(any("candidate branch" in error for error in errors), errors)

    def test_execution_base_mismatch_is_rejected(self):
        value = current_state()
        execution = execution_state()
        execution["repository"]["target_sha"] = "e" * 40
        value["next_action"]["execution_state_digest"] = canonical_document_digest(execution)
        errors = validate_current_state(value, execution)
        self.assertTrue(
            any(
                "parent.main_sha" in error or "candidate base_sha" in error
                for error in errors
            ),
            errors,
        )

    def test_execution_pr_mismatch_is_rejected(self):
        value = current_state()
        execution = execution_state()
        execution["repository"]["pr"] = 999
        value["next_action"]["execution_state_digest"] = canonical_document_digest(execution)
        errors = validate_current_state(value, execution)
        self.assertTrue(any("candidate pr" in error for error in errors), errors)

    def test_execution_attempt_mismatch_is_rejected(self):
        value = current_state()
        execution = execution_state()
        execution["identity"]["attempt"] = 2
        value["next_action"]["execution_state_digest"] = canonical_document_digest(execution)
        errors = validate_current_state(value, execution)
        self.assertTrue(any("active.attempt" in error for error in errors), errors)

    def test_execution_role_mismatch_is_rejected(self):
        value = current_state()
        execution = execution_state()
        execution["capability"]["active_role"] = "REVIEWER"
        value["next_action"]["execution_state_digest"] = canonical_document_digest(execution)
        errors = validate_current_state(value, execution)
        self.assertTrue(any("active.role" in error for error in errors), errors)

    def test_execution_parent_identity_mismatch_is_rejected(self):
        value = current_state()
        execution = execution_state()
        execution["identity"]["parent"] = "OTHER-PARENT"
        value["next_action"]["execution_state_digest"] = canonical_document_digest(execution)
        errors = validate_current_state(value, execution)
        self.assertTrue(any("parent identity" in error for error in errors), errors)

    def test_execution_responsibility_mismatch_is_rejected(self):
        value = current_state()
        execution = execution_state()
        execution["identity"]["responsibility"] = "PRD-OTHER"
        value["next_action"]["execution_state_digest"] = canonical_document_digest(execution)
        errors = validate_current_state(value, execution)
        self.assertTrue(any("active.prd_id" in error for error in errors), errors)

    def test_extra_authority_field_is_rejected(self):
        value = current_state()
        value["merge_now"] = True
        errors = validate_current_state(value, execution_state())
        self.assertTrue(any("Additional properties are not allowed" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
