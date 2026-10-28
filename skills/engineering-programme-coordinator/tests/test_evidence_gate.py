import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import evidence_gate
from evidence_gate import canonical_digest, compile_gate, validate_result


CANDIDATE = "c" * 40
DIGEST = "d" * 64


def verdict():
    return {
        "projection_digest": "1" * 64,
        "candidate": {"sha": CANDIDATE},
        "criticality": {
            "unresolved_refuted_ids": [],
            "unresolved_unknown_ids": [],
        },
    }


def context():
    return {
        "candidate_sha": CANDIDATE,
        "principal": {
            "principal_independence": "NONE",
        },
    }


def governing_basis():
    return {
        "basis": "self-check",
    }


def criterion(result="PASS"):
    return {
        "applicability": "REQUIRED",
        "result": result,
        "evidence_refs": ["evidence://criterion"],
    }


def profile():
    return {
        "review_profile": {
            "role": "SELF_REVIEW",
            "final_candidate": CANDIDATE,
            "common_criteria": {
                f"CR-{index:02d}": criterion()
                for index in range(1, 11)
            },
            "findings": [],
            "unresolved_required_findings": 0,
            "result": "COMPLETE",
        },
    }


def freeze():
    return {
        "freeze_digest": "2" * 64,
        "identity": {"candidate_sha": CANDIDATE},
    }


def falsification(status="NOT_FALSIFIED"):
    observation_result = {
        "NOT_FALSIFIED": "PASS",
        "FALSIFIED": "FAIL",
        "NOT_RUN": "NOT_RUN",
        "INCONCLUSIVE": "INCONCLUSIVE",
    }[status]
    return {
        "result_digest": "3" * 64,
        "identity": {
            "responsibility_id": "PRD-527-P3-SOLO-4",
            "candidate_sha": CANDIDATE,
        },
        "falsification_status": status,
        "observations": [{
            "method_id": "PM-1",
            "result": observation_result,
        }],
    }


def principal_truth():
    return {
        "truth_digest": "4" * 64,
        "candidate_sha": CANDIDATE,
        "review_mode": "SELF_REVIEW",
        "principals": {
            "author": "principal://solo",
            "reviewer": "principal://solo",
            "relationship": "SAME_PRINCIPAL",
            "principal_independence": "NONE",
        },
    }


def binding(ref, digest):
    return {
        "ref": ref,
        "digest": digest,
        "candidate_sha": CANDIDATE,
    }


def source(v=None, ctx=None, basis=None, prof=None, frz=None, fals=None, truth=None):
    v = v or verdict()
    ctx = ctx or context()
    basis = basis or governing_basis()
    prof = prof or profile()
    frz = frz or freeze()
    fals = fals or falsification()
    truth = truth or principal_truth()
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
            "verdict_projection": binding("artifact://verdict", v["projection_digest"]),
            "self_check_context": binding(
                "artifact://self-check",
                canonical_digest({"context": ctx, "governing_basis": basis}),
            ),
            "common_review_floor": binding(
                "artifact://common-floor",
                canonical_digest(prof),
            ),
            "expectation_challenge": binding(
                "artifact://expectation-challenge",
                frz["freeze_digest"],
            ),
            "project_falsification": binding(
                "artifact://project-falsification",
                fals["result_digest"],
            ),
            "principal_truth": binding(
                "artifact://principal-truth",
                truth["truth_digest"],
            ),
        },
        "local_resolution": [],
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


def compile_case(
    *,
    src=None,
    v=None,
    ctx=None,
    basis=None,
    prof=None,
    frz=None,
    fals=None,
    truth=None,
):
    v = v or verdict()
    ctx = ctx or context()
    basis = basis or governing_basis()
    prof = prof or profile()
    frz = frz or freeze()
    fals = fals or falsification()
    truth = truth or principal_truth()
    src = src or source(v, ctx, basis, prof, frz, fals, truth)

    with patch.multiple(
        evidence_gate,
        validate_projection=lambda *args, **kwargs: [],
        review_basis_errors=lambda *args, **kwargs: [],
        validate_freeze=lambda *args, **kwargs: [],
        validate_falsification=lambda *args, **kwargs: [],
        validate_truth=lambda *args, **kwargs: [],
    ):
        return compile_gate(
            src,
            v,
            {},
            ctx,
            basis,
            prof,
            frz,
            {},
            {},
            {},
            {},
            [],
            fals,
            truth,
            Path("."),
        )


class DeterministicEvidenceGateTests(unittest.TestCase):
    def test_eg01_clean_closed_candidate_is_advance_eligible(self):
        result = compile_case()
        self.assertEqual("ADVANCE_ELIGIBLE", result["disposition"])
        self.assertEqual(["CLOSED_CURRENT_DENOMINATOR"], result["reason_codes"])
        self.assertEqual([], result["blocking_refs"])
        self.assertEqual([], result["unresolved_refs"])
        self.assertFalse(any(result["authority_boundaries"].values()))

    def test_eg02_binding_digest_mismatch_replays(self):
        src = source()
        src["inputs"]["verdict_projection"]["digest"] = "f" * 64
        result = compile_case(src=src)
        self.assertEqual("REPLAY", result["disposition"])
        self.assertIn("SOURCE_REPLAY_INVALID", result["reason_codes"])

    def test_eg03_fresh_source_replay_failure_replays(self):
        v = verdict()
        src = source(v=v)
        with patch.multiple(
            evidence_gate,
            validate_projection=lambda *args, **kwargs: ["stored projection differs from replay"],
            review_basis_errors=lambda *args, **kwargs: [],
            validate_freeze=lambda *args, **kwargs: [],
            validate_falsification=lambda *args, **kwargs: [],
            validate_truth=lambda *args, **kwargs: [],
        ):
            result = compile_gate(
                src, v, {}, context(), governing_basis(), profile(), freeze(),
                {}, {}, {}, {}, [], falsification(), principal_truth(), Path(".")
            )
        self.assertEqual("REPLAY", result["disposition"])
        self.assertIn("source-replay://verdict_projection", result["blocking_refs"])

    def test_eg04_critical_refuted_requires_repair(self):
        v = verdict()
        v["criticality"]["unresolved_refuted_ids"] = ["L0-CRIT-1"]
        result = compile_case(v=v, src=source(v=v))
        self.assertEqual("REPAIR", result["disposition"])
        self.assertIn("CRITICAL_REFUTED", result["reason_codes"])
        self.assertEqual(["obligation://L0-CRIT-1"], result["blocking_refs"])

    def test_eg05_required_common_criterion_fail_requires_repair(self):
        prof = profile()
        prof["review_profile"]["common_criteria"]["CR-03"]["result"] = "FAIL"
        result = compile_case(prof=prof, src=source(prof=prof))
        self.assertEqual("REPAIR", result["disposition"])
        self.assertIn("COMMON_CRITERION_FAIL", result["reason_codes"])
        self.assertIn("criterion://CR-03", result["blocking_refs"])

    def test_eg06_project_falsified_requires_repair(self):
        fals = falsification("FALSIFIED")
        result = compile_case(fals=fals, src=source(fals=fals))
        self.assertEqual("REPAIR", result["disposition"])
        self.assertIn("PROJECT_OUTCOME_FALSIFIED", result["reason_codes"])
        self.assertIn("project-method://PM-1", result["blocking_refs"])

    def test_eg07_unknown_without_exhaustion_replays(self):
        v = verdict()
        v["criticality"]["unresolved_unknown_ids"] = ["L2-CRIT-2"]
        result = compile_case(v=v, src=source(v=v))
        self.assertEqual("REPLAY", result["disposition"])
        self.assertIn("CRITICAL_UNKNOWN_LOCAL_WORK_REMAINING", result["reason_codes"])
        self.assertEqual(["obligation://L2-CRIT-2"], result["unresolved_refs"])

    def test_eg08_unknown_with_proven_exhaustion_escalates(self):
        v = verdict()
        v["criticality"]["unresolved_unknown_ids"] = ["L2-CRIT-2"]
        src = source(v=v)
        src["local_resolution"] = [{
            "subject_ref": "obligation://L2-CRIT-2",
            "candidate_sha": CANDIDATE,
            "state": "LOCAL_RESOLUTION_EXHAUSTED",
            "evidence_refs": ["provider://attempts/1"],
            "boundary_ref": "owner://decision-required",
        }]
        result = compile_case(v=v, src=src)
        self.assertEqual("ESCALATE", result["disposition"])
        self.assertIn("LOCAL_RESOLUTION_EXHAUSTED", result["reason_codes"])
        self.assertIn("AUTHORITY_OR_EXTERNAL_BOUNDARY", result["reason_codes"])

    def test_conflicting_duplicate_resolution_records_replay_not_escalate(self):
        v = verdict()
        v["criticality"]["unresolved_unknown_ids"] = ["L2-CRIT-2"]
        src = source(v=v)
        src["local_resolution"] = [
            {
                "subject_ref": "obligation://L2-CRIT-2",
                "candidate_sha": CANDIDATE,
                "state": "LOCAL_WORK_REMAINING",
                "evidence_refs": [],
                "boundary_ref": None,
            },
            {
                "subject_ref": "obligation://L2-CRIT-2",
                "candidate_sha": CANDIDATE,
                "state": "LOCAL_RESOLUTION_EXHAUSTED",
                "evidence_refs": ["provider://attempts/1"],
                "boundary_ref": "owner://decision-required",
            },
        ]
        result = compile_case(v=v, src=src)
        self.assertEqual("REPLAY", result["disposition"])
        self.assertIn("SOURCE_REPLAY_INVALID", result["reason_codes"])

    def test_fake_boundary_label_replays_not_escalates(self):
        v = verdict()
        v["criticality"]["unresolved_unknown_ids"] = ["L2-CRIT-2"]
        src = source(v=v)
        src["local_resolution"] = [{
            "subject_ref": "obligation://L2-CRIT-2",
            "candidate_sha": CANDIDATE,
            "state": "LOCAL_RESOLUTION_EXHAUSTED",
            "evidence_refs": ["provider://attempts/1"],
            "boundary_ref": "caller-says-exhausted",
        }]
        result = compile_case(v=v, src=src)
        self.assertEqual("REPLAY", result["disposition"])
        self.assertIn("SOURCE_REPLAY_INVALID", result["reason_codes"])

    def test_cannot_resolve_boolean_shortcut_replays_not_escalates(self):
        v = verdict()
        v["criticality"]["unresolved_unknown_ids"] = ["L2-CRIT-2"]
        src = source(v=v)
        src["local_resolution"] = [{
            "subject_ref": "obligation://L2-CRIT-2",
            "candidate_sha": CANDIDATE,
            "state": "LOCAL_RESOLUTION_EXHAUSTED",
            "evidence_refs": ["provider://attempts/1"],
            "boundary_ref": "owner://decision-required",
            "cannot_resolve_locally": True,
        }]
        result = compile_case(v=v, src=src)
        self.assertEqual("REPLAY", result["disposition"])
        self.assertIn("SOURCE_REPLAY_INVALID", result["reason_codes"])

    def test_eg09_required_not_run_replays(self):
        prof = profile()
        prof["review_profile"]["common_criteria"]["CR-04"]["result"] = "NOT_RUN"
        prof["review_profile"]["result"] = "INCONCLUSIVE"
        result = compile_case(prof=prof, src=source(prof=prof))
        self.assertEqual("REPLAY", result["disposition"])
        self.assertIn("REQUIRED_EVIDENCE_INCOMPLETE", result["reason_codes"])
        self.assertIn("criterion://CR-04", result["unresolved_refs"])

    def test_open_blocking_finding_requires_repair(self):
        prof = profile()
        prof["review_profile"]["findings"] = [{
            "id": "F-1",
            "class": "BLOCKING_DEFECT",
            "summary": "candidate violates invariant",
            "disposition": "OPEN",
        }]
        prof["review_profile"]["unresolved_required_findings"] = 1
        prof["review_profile"]["result"] = "REWORK"
        result = compile_case(prof=prof, src=source(prof=prof))
        self.assertEqual("REPAIR", result["disposition"])
        self.assertIn("REQUIRED_FINDING_OPEN", result["reason_codes"])
        self.assertIn("finding://F-1", result["blocking_refs"])

    def test_non_complete_profile_cannot_fall_through_to_advance(self):
        prof = profile()
        prof["review_profile"]["result"] = "INCONCLUSIVE"
        result = compile_case(prof=prof, src=source(prof=prof))
        self.assertEqual("REPLAY", result["disposition"])
        self.assertIn("review://result/INCONCLUSIVE", result["unresolved_refs"])

    def test_candidate_binding_mismatch_replays(self):
        src = source()
        src["inputs"]["principal_truth"]["candidate_sha"] = "e" * 40
        result = compile_case(src=src)
        self.assertEqual("REPLAY", result["disposition"])
        self.assertIn("CANDIDATE_MISMATCH", result["reason_codes"])

    def test_validate_result_requires_fresh_source_replay(self):
        value = compile_case()
        errors = validate_result(value)
        self.assertTrue(any("source-bound fresh gate replay is required" in row for row in errors), errors)


if __name__ == "__main__":
    unittest.main()
