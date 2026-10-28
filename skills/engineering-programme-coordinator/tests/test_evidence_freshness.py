import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evidence_freshness import (
    canonical_digest,
    derive_evidence_freshness,
    semantic_errors,
    validate_evidence_freshness,
)


SHA = "a" * 40
OLD_SHA = "b" * 40
D1 = "1" * 64
D2 = "2" * 64
D3 = "3" * 64
D4 = "4" * 64
ENV = "5" * 64


def current():
    return {
        "candidate_sha": SHA,
        "acceptance_epoch_id": "AE-1",
        "project_protocol_digest": D1,
        "acceptance_profile_digest": D2,
        "protected_surface_digest": D3,
        "environment_digest": ENV,
        "dependency_heads": {"PRD-UPSTREAM": "c" * 40},
    }


def binding(
    evidence_id="EV-1",
    method_id="VM-1",
    provenance="VERIFIED",
):
    source = {
        "evidence_id": evidence_id,
        "candidate_sha": SHA,
        "verification_method_id": method_id,
        "project_protocol_digest": D1,
        "environment_digest": ENV,
        "result": "PASS",
        "procedure": "synthetic immutable evidence",
    }
    return {
        "evidence_id": evidence_id,
        "evidence_ref": f"evidence://{evidence_id}",
        "evidence_digest": canonical_digest(source),
        "source_evidence": source,
        "verification_method_id": method_id,
        "provenance_state": provenance,
        "candidate_sha": SHA,
        "acceptance_epoch_id": "AE-1",
        "project_protocol_digest": D1,
        "acceptance_profile_digest": D2,
        "protected_surface_digest": D3,
        "environment_digest": ENV,
        "dependency_heads": {"PRD-UPSTREAM": "c" * 40},
    }


def bind_source_field(row, key, value):
    row[key] = value
    row["source_evidence"][key] = value
    row["evidence_digest"] = canonical_digest(row["source_evidence"])


def derive(
    evidence=None,
    *,
    required=None,
    materials=None,
    policies=None,
    current_value=None,
):
    required = required or ["VM-1"]
    return derive_evidence_freshness(
        evidence_bindings=evidence if evidence is not None else [binding()],
        current=current_value or current(),
        ledger_ref="ledger://P1-R5",
        required_method_ids=required,
        method_material_inputs=materials or {
            method: ["CANDIDATE", "ACCEPTANCE_EPOCH", "PROJECT_PROTOCOL",
                     "ACCEPTANCE_PROFILE", "PROTECTED_SURFACE", "ENVIRONMENT",
                     "DEPENDENCIES"]
            for method in required
        },
        method_rerun_policy=policies or {
            method: "DECLARED_MATERIAL_INPUTS"
            for method in required
        },
    )


class EvidenceFreshnessTests(unittest.TestCase):
    def test_exact_required_evidence_is_current(self):
        result = derive()
        self.assertEqual(result["overall"]["evidence_state"], "CURRENT")
        self.assertEqual(result["overall"]["evidence_candidate_sha"], SHA)
        self.assertEqual(result["method_results"][0]["state"], "CURRENT")
        self.assertEqual(result["replay_plan"]["mode"], "NO_REPLAY")
        self.assertEqual(result["replay_plan"]["rerun_method_ids"], [])

    def test_candidate_movement_marks_evidence_stale_and_replays(self):
        evidence = binding()
        bind_source_field(evidence, "candidate_sha", OLD_SHA)
        result = derive([evidence])
        self.assertEqual(result["overall"]["evidence_state"], "STALE")
        self.assertIn("CANDIDATE_CHANGED", result["evidence_results"][0]["reasons"])
        self.assertEqual(
            result["replay_plan"]["rerun_method_ids"],
            ["VM-1"],
        )

    def test_binding_cannot_lie_about_source_evidence_candidate(self):
        evidence = binding()
        evidence["candidate_sha"] = OLD_SHA
        with self.assertRaisesRegex(Exception, "candidate_sha differs from source_evidence"):
            derive([evidence])

    def test_binding_cannot_lie_about_source_evidence_method(self):
        evidence = binding()
        evidence["verification_method_id"] = "VM-OTHER"
        with self.assertRaisesRegex(Exception, "verification_method_id differs from source_evidence"):
            derive([evidence])

    def test_evidence_digest_must_bind_source_evidence_content(self):
        evidence = binding()
        evidence["source_evidence"]["procedure"] = "mutated after digest"
        with self.assertRaisesRegex(Exception, "evidence_digest does not match"):
            derive([evidence])

    def test_acceptance_epoch_drift_is_stale(self):
        evidence = binding()
        evidence["acceptance_epoch_id"] = "AE-OLD"
        result = derive([evidence])
        self.assertIn("ACCEPTANCE_BASIS_CHANGED", result["evidence_results"][0]["reasons"])

    def test_project_protocol_drift_is_stale(self):
        evidence = binding()
        bind_source_field(evidence, "project_protocol_digest", "9" * 64)
        result = derive([evidence])
        self.assertIn("PROJECT_PROTOCOL_CHANGED", result["evidence_results"][0]["reasons"])

    def test_acceptance_profile_drift_is_stale(self):
        evidence = binding()
        evidence["acceptance_profile_digest"] = "8" * 64
        result = derive([evidence])
        self.assertIn("ACCEPTANCE_PROFILE_CHANGED", result["evidence_results"][0]["reasons"])

    def test_protected_surface_drift_is_stale(self):
        evidence = binding()
        evidence["protected_surface_digest"] = "7" * 64
        result = derive([evidence])
        self.assertIn("PROTECTED_SURFACE_CHANGED", result["evidence_results"][0]["reasons"])

    def test_material_environment_drift_is_stale(self):
        evidence = binding()
        bind_source_field(evidence, "environment_digest", "6" * 64)
        result = derive([evidence])
        self.assertIn("ENVIRONMENT_CHANGED", result["evidence_results"][0]["reasons"])

    def test_environment_not_declared_material_is_not_invented(self):
        evidence = binding()
        bind_source_field(evidence, "environment_digest", "6" * 64)
        now = current()
        now["environment_digest"] = None
        result = derive([evidence], current_value=now)
        self.assertEqual(result["overall"]["evidence_state"], "CURRENT")
        self.assertNotIn("ENVIRONMENT_CHANGED", result["evidence_results"][0]["reasons"])

    def test_dependency_map_order_is_irrelevant(self):
        evidence = binding()
        evidence["dependency_heads"] = {
            "B": "d" * 40,
            "A": "e" * 40,
        }
        now = current()
        now["dependency_heads"] = {
            "A": "e" * 40,
            "B": "d" * 40,
        }
        result = derive([evidence], current_value=now)
        self.assertEqual(result["overall"]["evidence_state"], "CURRENT")

    def test_dependency_head_change_is_stale(self):
        evidence = binding()
        evidence["dependency_heads"] = {"PRD-UPSTREAM": "d" * 40}
        result = derive(
            [evidence],
            materials={"VM-1": ["DEPENDENCY:PRD-UPSTREAM"]},
        )
        self.assertEqual(result["overall"]["evidence_state"], "STALE")
        self.assertIn("DEPENDENCY_HEAD_CHANGED", result["evidence_results"][0]["reasons"])
        self.assertIn(
            "DEPENDENCY:PRD-UPSTREAM",
            result["replay_plan"]["changed_inputs"],
        )

    def test_duplicate_evidence_ids_fail_closed(self):
        with self.assertRaisesRegex(Exception, "duplicate evidence_id"):
            derive([binding(), binding()])

    def test_missing_required_method_is_missing(self):
        result = derive(
            [binding(method_id="VM-1")],
            required=["VM-1", "VM-2"],
        )
        states = {row["method_id"]: row["state"] for row in result["method_results"]}
        self.assertEqual(states["VM-2"], "MISSING")
        self.assertEqual(result["overall"]["evidence_state"], "MISSING")
        self.assertIsNone(result["overall"]["evidence_ledger_ref"])
        self.assertIn("VM-2", result["replay_plan"]["rerun_method_ids"])

    def test_unknown_provenance_is_unknown(self):
        result = derive([binding(provenance="UNKNOWN")])
        self.assertEqual(result["overall"]["evidence_state"], "UNKNOWN")
        self.assertEqual(result["evidence_results"][0]["reasons"], ["PROVENANCE_UNKNOWN"])
        self.assertEqual(result["replay_plan"]["mode"], "GAP_REPLAY")

    def test_stale_reason_dominates_unknown_provenance(self):
        evidence = binding(provenance="UNKNOWN")
        bind_source_field(evidence, "candidate_sha", OLD_SHA)
        result = derive([evidence])
        self.assertEqual(result["overall"]["evidence_state"], "STALE")
        self.assertEqual(result["evidence_results"][0]["state"], "STALE")
        self.assertNotIn("PROVENANCE_UNKNOWN", result["evidence_results"][0]["reasons"])

    def test_one_current_evidence_can_satisfy_method_despite_stale_history(self):
        old = binding("EV-OLD")
        bind_source_field(old, "candidate_sha", OLD_SHA)
        fresh = binding("EV-NEW")
        result = derive([old, fresh])
        self.assertEqual(result["method_results"][0]["state"], "CURRENT")
        self.assertEqual(result["overall"]["evidence_state"], "CURRENT")

    def test_unknown_rerun_policy_for_stale_method_forces_full_set(self):
        evidence = binding()
        bind_source_field(evidence, "candidate_sha", OLD_SHA)
        result = derive(
            [evidence],
            required=["VM-1", "VM-2"],
            materials={
                "VM-1": ["CANDIDATE"],
                "VM-2": ["CANDIDATE"],
            },
            policies={"VM-2": "DECLARED_MATERIAL_INPUTS"},
        )
        self.assertEqual(result["replay_plan"]["mode"], "CONSERVATIVE_FULL_REQUIRED_SET")
        self.assertEqual(result["replay_plan"]["rerun_method_ids"], ["VM-1", "VM-2"])

    def test_full_required_set_policy_forces_full_replay(self):
        evidence = binding()
        bind_source_field(evidence, "candidate_sha", OLD_SHA)
        result = derive(
            [evidence],
            required=["VM-1", "VM-2"],
            policies={
                "VM-1": "FULL_REQUIRED_SET",
                "VM-2": "DECLARED_MATERIAL_INPUTS",
            },
        )
        self.assertEqual(result["replay_plan"]["mode"], "FULL_REQUIRED_SET")
        self.assertEqual(result["replay_plan"]["rerun_method_ids"], ["VM-1", "VM-2"])

    def test_selective_replay_requires_declared_material_input_match(self):
        evidence = binding()
        bind_source_field(evidence, "candidate_sha", OLD_SHA)
        result = derive(
            [evidence],
            required=["VM-1", "VM-2"],
            materials={
                "VM-1": ["CANDIDATE"],
                "VM-2": ["PROJECT_PROTOCOL"],
            },
        )
        self.assertEqual(result["replay_plan"]["mode"], "SELECTIVE_PLUS_GAPS")
        self.assertEqual(result["replay_plan"]["rerun_method_ids"], ["VM-1", "VM-2"])

    def test_unexplained_stale_method_forces_conservative_full_replay(self):
        evidence = binding()
        bind_source_field(evidence, "candidate_sha", OLD_SHA)
        result = derive(
            [evidence],
            materials={"VM-1": ["PROJECT_PROTOCOL"]},
        )
        self.assertEqual(result["replay_plan"]["mode"], "CONSERVATIVE_FULL_REQUIRED_SET")
        self.assertEqual(result["replay_plan"]["rerun_method_ids"], ["VM-1"])

    def test_source_evidence_is_not_mutated(self):
        evidence = [binding()]
        before = json.dumps(evidence, sort_keys=True)
        derive(evidence)
        self.assertEqual(json.dumps(evidence, sort_keys=True), before)

    def test_ledger_digest_is_order_independent_by_evidence_identity(self):
        one = binding("EV-1")
        two = binding("EV-2")
        first = derive([one, two])
        second = derive([two, one])
        self.assertEqual(
            first["source_ledger"]["ledger_digest"],
            second["source_ledger"]["ledger_digest"],
        )

    def test_non_current_projection_cannot_claim_exact_evidence_candidate(self):
        evidence = binding()
        bind_source_field(evidence, "candidate_sha", OLD_SHA)
        result = derive([evidence])
        result["overall"]["evidence_candidate_sha"] = SHA
        errors = semantic_errors(result)
        self.assertTrue(any("non-CURRENT" in error for error in errors), errors)

    def test_unbound_projection_validation_is_rejected(self):
        request = {
            "evidence_bindings": [binding()],
            "current": current(),
            "ledger_ref": "ledger://P1-R5",
            "required_method_ids": ["VM-1"],
            "method_material_inputs": {"VM-1": ["CANDIDATE"]},
            "method_rerun_policy": {"VM-1": "DECLARED_MATERIAL_INPUTS"},
        }
        result = derive_evidence_freshness(**copy.deepcopy(request))
        errors = validate_evidence_freshness(result, None)
        self.assertTrue(any("requires source request" in error for error in errors), errors)

    def test_forged_current_projection_fails_bound_replay(self):
        request = {
            "evidence_bindings": [binding()],
            "current": current(),
            "ledger_ref": "ledger://P1-R5",
            "required_method_ids": ["VM-1"],
            "method_material_inputs": {"VM-1": ["CANDIDATE"]},
            "method_rerun_policy": {"VM-1": "DECLARED_MATERIAL_INPUTS"},
        }
        result = derive_evidence_freshness(**copy.deepcopy(request))
        forged = copy.deepcopy(result)
        forged["source_ledger"]["ledger_digest"] = "f" * 64
        errors = validate_evidence_freshness(forged, request)
        self.assertTrue(
            any("must exactly equal source-request derivation" in error for error in errors),
            errors,
        )

    def test_projection_carries_no_pass_or_lifecycle_authority(self):
        result = derive()
        bounds = result["authority_boundaries"]
        self.assertFalse(bounds["mutates_source_evidence"])
        self.assertFalse(bounds["emits_engineering_pass"])
        self.assertFalse(bounds["performs_lifecycle_advance"])
        self.assertFalse(bounds["grants_merge_authority"])
        self.assertFalse(bounds["grants_production_cutover"])


if __name__ == "__main__":
    unittest.main()
