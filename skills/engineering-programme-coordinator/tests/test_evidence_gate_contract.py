import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from coordlib import validate
from evidence_gate import validate_source


CANDIDATE = "c" * 40
DIGEST = "d" * 64


def binding(name):
    return {
        "ref": f"artifact://{name}",
        "digest": DIGEST,
        "candidate_sha": CANDIDATE,
    }


def source():
    return {
        "schema_version": "DETERMINISTIC_EVIDENCE_GATE_SOURCE_V1",
        "authority": "DETERMINISTIC_EVIDENCE_GATE_INPUT",
        "identity": {
            "programme_or_parent_id": "COMMON-PROD-CONTROL-V1",
            "parent_ref": "https://github.com/reallaksh19/Common/issues/527",
            "task_id": "PRD-527-P3-SOLO-6",
            "child_ref": "SELF:PRD-527-P3-SOLO-6",
            "contract_version": "P3-SOLO-6-v1",
        },
        "candidate": {
            "repository": "reallaksh19/Common",
            "ref": "prod/527-p3-solo-6-deterministic-evidence-gate",
            "sha": CANDIDATE,
        },
        "inputs": {
            "verdict_projection": binding("verdict"),
            "self_check_context": binding("self-check"),
            "common_review_floor": binding("common-floor"),
            "expectation_challenge": binding("expectation-challenge"),
            "project_falsification": binding("project-falsification"),
            "principal_truth": binding("principal-truth"),
        },
        "local_resolution": [{
            "subject_ref": "obligation://L2-UNKNOWN-1",
            "candidate_sha": CANDIDATE,
            "state": "LOCAL_WORK_REMAINING",
            "evidence_refs": [],
            "boundary_ref": None,
        }],
        "decision_policy": {
            "stale_or_invalid": "REPLAY",
            "proven_repairable_defect": "REPAIR",
            "unknown_local_work_remaining": "REPLAY",
            "unknown_local_resolution_exhausted": "ESCALATE",
            "closed_current_denominator": "ADVANCE_ELIGIBLE",
        },
        "authority_boundaries": {
            "emits_engineering_pass": False,
            "emits_project_acceptance_pass": False,
            "emits_independent_review_verdict": False,
            "performs_lifecycle_advance": False,
            "grants_merge_authority": False,
            "grants_production_cutover": False,
        },
    }


def result(disposition="REPLAY"):
    return {
        "schema_version": "DETERMINISTIC_EVIDENCE_GATE_RESULT_V1",
        "authority": "EVIDENCE_GATE_DISPOSITION_ONLY",
        "candidate_sha": CANDIDATE,
        "source": {
            "source_digest": DIGEST,
            "verdict_projection_digest": DIGEST,
            "self_check_basis_digest": DIGEST,
            "common_review_floor_digest": DIGEST,
            "expectation_challenge_digest": DIGEST,
            "project_falsification_digest": DIGEST,
            "principal_truth_digest": DIGEST,
            "local_resolution_digest": DIGEST,
        },
        "disposition": disposition,
        "reason_codes": ["REQUIRED_EVIDENCE_INCOMPLETE"],
        "blocking_refs": [],
        "unresolved_refs": ["obligation://L2-UNKNOWN-1"],
        "authority_boundaries": {
            "emits_engineering_pass": False,
            "emits_project_acceptance_pass": False,
            "emits_independent_review_verdict": False,
            "performs_lifecycle_advance": False,
            "grants_merge_authority": False,
            "grants_production_cutover": False,
        },
        "result_digest": DIGEST,
    }


class EvidenceGateContractTests(unittest.TestCase):
    def test_source_accepts_fixed_policy_and_local_work_record(self):
        self.assertEqual(validate("deterministic-evidence-gate-source", source()), [])

    def test_source_rejects_policy_weakening_unknown_to_escalate(self):
        value = source()
        value["decision_policy"]["unknown_local_work_remaining"] = "ESCALATE"
        errors = validate("deterministic-evidence-gate-source", value)
        self.assertTrue(any("REPLAY" in error for error in errors), errors)

    def test_exhausted_local_resolution_requires_evidence_and_boundary(self):
        value = source()
        value["local_resolution"][0]["state"] = "LOCAL_RESOLUTION_EXHAUSTED"
        errors = validate("deterministic-evidence-gate-source", value)
        self.assertTrue(any("non-empty" in error or "[] should be non-empty" in error for error in errors), errors)
        self.assertTrue(any("not of type 'string'" in error or "string" in error for error in errors), errors)

    def test_source_rejects_caller_cannot_resolve_shortcut(self):
        value = source()
        value["local_resolution"][0]["cannot_resolve_locally"] = True
        errors = validate("deterministic-evidence-gate-source", value)
        self.assertTrue(any("Additional properties are not allowed" in error for error in errors), errors)

    def test_source_rejects_duplicate_local_resolution_subject_refs(self):
        value = source()
        value["local_resolution"].append(dict(value["local_resolution"][0]))
        errors = validate_source(value)
        self.assertTrue(
            any("subject_ref values must be unique" in error for error in errors),
            errors,
        )

    def test_source_rejects_arbitrary_exhaustion_boundary_label(self):
        value = source()
        value["local_resolution"][0]["state"] = "LOCAL_RESOLUTION_EXHAUSTED"
        value["local_resolution"][0]["evidence_refs"] = ["provider://attempts/1"]
        value["local_resolution"][0]["boundary_ref"] = "caller-says-exhausted"
        errors = validate("deterministic-evidence-gate-source", value)
        self.assertTrue(
            any("does not match" in error or "pattern" in error for error in errors),
            errors,
        )

    def test_result_accepts_only_canonical_gate_dispositions(self):
        for disposition in ["REPLAY", "REPAIR", "ESCALATE", "ADVANCE_ELIGIBLE"]:
            value = result(disposition)
            if disposition == "ADVANCE_ELIGIBLE":
                value["reason_codes"] = ["CLOSED_CURRENT_DENOMINATOR"]
                value["unresolved_refs"] = []
            self.assertEqual(
                validate("deterministic-evidence-gate-result", value),
                [],
                disposition,
            )

    def test_result_rejects_pass_and_legacy_replay_evidence_tokens(self):
        for disposition in ["PASS", "REPLAY_EVIDENCE"]:
            value = result()
            value["disposition"] = disposition
            errors = validate("deterministic-evidence-gate-result", value)
            self.assertTrue(any("is not one of" in error for error in errors), (disposition, errors))

    def test_result_rejects_engineering_pass_authority(self):
        value = result()
        value["authority_boundaries"]["emits_engineering_pass"] = True
        errors = validate("deterministic-evidence-gate-result", value)
        self.assertTrue(any("False was expected" in error for error in errors), errors)

    def test_result_rejects_lifecycle_merge_and_cutover_authority(self):
        for field in [
            "performs_lifecycle_advance",
            "grants_merge_authority",
            "grants_production_cutover",
        ]:
            value = result()
            value["authority_boundaries"][field] = True
            errors = validate("deterministic-evidence-gate-result", value)
            self.assertTrue(any("False was expected" in error for error in errors), (field, errors))


if __name__ == "__main__":
    unittest.main()
