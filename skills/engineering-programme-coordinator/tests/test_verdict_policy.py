#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from coordlib import load_yaml
from verdict_policy import (
    BOUNDARIES,
    canonical_digest,
    derive_projection,
    object_digest,
    validate_projection,
    validate_projection_shape,
    validate_source,
)

SOURCE_PATH = ROOT / "references" / "p2-s6-verdict-policy-source.yaml"


class VerdictPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = load_yaml(SOURCE_PATH)
        cls.projection = derive_projection(cls.source, REPO_ROOT)

    def test_source_digest_is_frozen(self) -> None:
        self.assertEqual(
            "c7ba9a019a518b3c0cd87539de953a7b128074ae8edac874e3affa5a1082d935",
            canonical_digest(self.source),
        )

    def test_real_projection_is_four_verified_nine_unknown(self) -> None:
        self.assertEqual(13, self.projection["accounting"]["obligation_count"])
        self.assertEqual(
            {
                "VERIFIED": 4,
                "REFUTED": 0,
                "UNKNOWN": 9,
                "NOT_APPLICABLE": 0,
                "WAIVER": 0,
            },
            self.projection["accounting"]["state_counts"],
        )

    def test_real_critical_projection_keeps_seven_unknown_visible(self) -> None:
        critical = self.projection["criticality"]
        self.assertEqual(9, critical["obligation_count"])
        self.assertEqual(2, critical["state_counts"]["VERIFIED"])
        self.assertEqual(7, critical["state_counts"]["UNKNOWN"])
        self.assertEqual(7, len(critical["unresolved_unknown_ids"]))
        self.assertEqual([], critical["unresolved_refuted_ids"])

    def test_provider_provenance_is_preserved(self) -> None:
        record = next(
            row for row in self.projection["records"]
            if row["obligation_id"] == "L2-IMPACT-5D3B0FDADE7B"
        )
        item = record["requirements"][0]["evidence_items"][0]
        self.assertEqual("DETERMINISTIC_TOOL", item["verifier_kind"])
        self.assertEqual(
            "engineering-programme-coordinator-integrated",
            item["verifier_identity"],
        )
        self.assertEqual(
            ["github-actions://reallaksh19/Common/runs/37408270193/jobs/112090640333#step-7"],
            item["refs"],
        )
        self.assertEqual("SATISFIES", item["evaluation_outcome"])

    def test_unknown_never_counts_as_verified(self) -> None:
        counts = self.projection["accounting"]["state_counts"]
        self.assertEqual(4, counts["VERIFIED"])
        self.assertEqual(9, counts["UNKNOWN"])
        verified = {
            row["obligation_id"]
            for row in self.projection["records"]
            if row["state"] == "VERIFIED"
        }
        unknown = {
            row["obligation_id"]
            for row in self.projection["records"]
            if row["state"] == "UNKNOWN"
        }
        self.assertFalse(verified & unknown)

    def test_refuted_requirement_dominates_obligation(self) -> None:
        source = copy.deepcopy(self.source)
        source["evidence_evaluations"][2]["outcome"] = "CONTRADICTS"
        result = derive_projection(source, REPO_ROOT, enforce_expected=False)
        record = next(
            row for row in result["records"]
            if row["obligation_id"] == "L2-IMPACT-5D3B0FDADE7B"
        )
        self.assertEqual("REFUTED", record["state"])
        self.assertIn(
            "L2-IMPACT-5D3B0FDADE7B",
            result["criticality"]["unresolved_refuted_ids"],
        )

    def test_inconclusive_evidence_is_unknown_not_verified(self) -> None:
        source = copy.deepcopy(self.source)
        source["evidence_evaluations"][2]["outcome"] = "INCONCLUSIVE"
        result = derive_projection(source, REPO_ROOT, enforce_expected=False)
        record = next(
            row for row in result["records"]
            if row["obligation_id"] == "L2-IMPACT-5D3B0FDADE7B"
        )
        self.assertEqual("UNKNOWN", record["state"])

    def test_missing_evaluation_is_unknown(self) -> None:
        source = copy.deepcopy(self.source)
        source["evidence_evaluations"] = source["evidence_evaluations"][1:]
        result = derive_projection(source, REPO_ROOT, enforce_expected=False)
        record = next(
            row for row in result["records"]
            if row["obligation_id"] == "L2-IMPACT-17D147C9F024"
        )
        self.assertEqual("UNKNOWN", record["state"])

    def test_not_applicable_requires_explicit_valid_disposition(self) -> None:
        source = copy.deepcopy(self.source)
        source["dispositions"] = [{
            "obligation_id": "L0-CLOSED-PRECOMMITTED-EXPECTATIONS",
            "state": "NOT_APPLICABLE",
            "basis_ref": "contract://P2-S6/test-na",
            "authority_kind": "CHILD_CONTRACT",
            "authority_ref": "issue://568",
            "reason": "Adversarial semantics fixture only",
        }]
        result = derive_projection(source, REPO_ROOT, enforce_expected=False)
        record = next(
            row for row in result["records"]
            if row["obligation_id"] == "L0-CLOSED-PRECOMMITTED-EXPECTATIONS"
        )
        self.assertEqual("NOT_APPLICABLE", record["state"])
        self.assertNotEqual("VERIFIED", record["state"])

    def test_not_applicable_without_basis_is_rejected(self) -> None:
        source = copy.deepcopy(self.source)
        source["dispositions"] = [{
            "obligation_id": "L0-CLOSED-PRECOMMITTED-EXPECTATIONS",
            "state": "NOT_APPLICABLE",
            "basis_ref": "",
            "authority_kind": "CHILD_CONTRACT",
            "authority_ref": "issue://568",
            "reason": "invalid",
        }]
        self.assertTrue(validate_source(source))

    def test_waiver_requires_owner_authority(self) -> None:
        source = copy.deepcopy(self.source)
        source["dispositions"] = [{
            "obligation_id": "L0-CLOSED-PRECOMMITTED-EXPECTATIONS",
            "state": "WAIVER",
            "basis_ref": "owner://decision",
            "authority_kind": "CHILD_CONTRACT",
            "authority_ref": "issue://568",
            "reason": "invalid authority",
        }]
        errors = validate_source(source)
        self.assertTrue(any("OWNER_DECISION" in error for error in errors), errors)

    def test_owner_waiver_is_visible_and_not_verified(self) -> None:
        source = copy.deepcopy(self.source)
        source["dispositions"] = [{
            "obligation_id": "L0-CLOSED-PRECOMMITTED-EXPECTATIONS",
            "state": "WAIVER",
            "basis_ref": "owner://decision/1",
            "authority_kind": "OWNER_DECISION",
            "authority_ref": "owner://527",
            "reason": "Adversarial semantics fixture only",
        }]
        result = derive_projection(source, REPO_ROOT, enforce_expected=False)
        record = next(
            row for row in result["records"]
            if row["obligation_id"] == "L0-CLOSED-PRECOMMITTED-EXPECTATIONS"
        )
        self.assertEqual("WAIVER", record["state"])
        self.assertIn(
            "L0-CLOSED-PRECOMMITTED-EXPECTATIONS",
            result["criticality"]["waiver_ids"],
        )

    def test_disposition_cannot_hide_evaluated_evidence(self) -> None:
        source = copy.deepcopy(self.source)
        source["dispositions"] = [{
            "obligation_id": "L2-IMPACT-5D3B0FDADE7B",
            "state": "NOT_APPLICABLE",
            "basis_ref": "contract://invalid",
            "authority_kind": "CHILD_CONTRACT",
            "authority_ref": "issue://568",
            "reason": "invalid conflict",
        }]
        with self.assertRaisesRegex(ValueError, "cannot coexist"):
            derive_projection(source, REPO_ROOT, enforce_expected=False)

    def test_absent_evidence_evaluation_is_rejected(self) -> None:
        source = copy.deepcopy(self.source)
        source["evidence_evaluations"][0]["evidence_id"] = "EVID-NOT-PRESENT"
        with self.assertRaisesRegex(ValueError, "absent evidence"):
            derive_projection(source, REPO_ROOT, enforce_expected=False)

    def test_requirement_mismatch_is_rejected(self) -> None:
        source = copy.deepcopy(self.source)
        source["evidence_evaluations"][0]["requirement_id"] = "REQ-WRONG"
        with self.assertRaisesRegex(ValueError, "requirement_id"):
            derive_projection(source, REPO_ROOT, enforce_expected=False)

    def test_candidate_mismatch_is_rejected(self) -> None:
        source = copy.deepcopy(self.source)
        source["evidence_evaluations"][0]["candidate_sha"] = "a" * 40
        self.assertTrue(
            any("candidate_sha" in error for error in validate_source(source))
        )

    def test_basis_ref_must_be_retained_provenance(self) -> None:
        source = copy.deepcopy(self.source)
        source["evidence_evaluations"][0]["basis_ref"] = "github-actions://wrong"
        with self.assertRaisesRegex(ValueError, "retained evidence provenance"):
            derive_projection(source, REPO_ROOT, enforce_expected=False)

    def test_duplicate_evaluation_is_rejected(self) -> None:
        source = copy.deepcopy(self.source)
        source["evidence_evaluations"].append(
            copy.deepcopy(source["evidence_evaluations"][0])
        )
        self.assertTrue(any("unique evidence_id" in e for e in validate_source(source)))

    def test_duplicate_disposition_is_rejected(self) -> None:
        source = copy.deepcopy(self.source)
        disposition = {
            "obligation_id": "L0-CLOSED-PRECOMMITTED-EXPECTATIONS",
            "state": "NOT_APPLICABLE",
            "basis_ref": "contract://basis",
            "authority_kind": "CHILD_CONTRACT",
            "authority_ref": "issue://568",
            "reason": "fixture",
        }
        source["dispositions"] = [disposition, copy.deepcopy(disposition)]
        self.assertTrue(any("unique obligation_id" in e for e in validate_source(source)))

    def test_unbound_projection_validation_fails_closed(self) -> None:
        errors = validate_projection(self.projection)
        self.assertTrue(
            any("source-bound verdict replay is required" in e for e in errors),
            errors,
        )

    def test_bound_projection_validation_passes(self) -> None:
        self.assertEqual(
            [],
            validate_projection(self.projection, self.source, REPO_ROOT),
        )

    def test_recomputed_tamper_digest_does_not_bypass_replay(self) -> None:
        projection = copy.deepcopy(self.projection)
        projection["accounting"]["state_counts"]["VERIFIED"] = 5
        projection["projection_digest"] = object_digest(
            projection,
            "projection_digest",
        )
        self.assertTrue(
            validate_projection(projection, self.source, REPO_ROOT)
        )

    def test_projection_rejects_gate_and_pass_authority_fields(self) -> None:
        for field, value in [
            ("pass", True),
            ("aggregate_pass", True),
            ("gate", "ADVANCE_ELIGIBLE"),
            ("next_action", "ADVANCE"),
            ("merge_authority", True),
            ("production_mode", "CRITICAL_GATE"),
        ]:
            projection = copy.deepcopy(self.projection)
            projection[field] = value
            projection["projection_digest"] = object_digest(
                projection,
                "projection_digest",
            )
            self.assertTrue(validate_projection_shape(projection), field)

    def test_authority_boundaries_are_semantic_only(self) -> None:
        self.assertEqual(BOUNDARIES, self.projection["authority_boundaries"])
        self.assertTrue(BOUNDARIES["assigns_evidence_verdict"])
        self.assertTrue(BOUNDARIES["applies_criticality_policy"])
        self.assertFalse(BOUNDARIES["emits_aggregate_pass"])
        self.assertFalse(BOUNDARIES["emits_evidence_gate_decision"])
        self.assertFalse(BOUNDARIES["performs_lifecycle_advance"])
        self.assertFalse(BOUNDARIES["grants_merge_authority"])
        self.assertFalse(BOUNDARIES["grants_production_cutover"])


if __name__ == "__main__":
    unittest.main()
