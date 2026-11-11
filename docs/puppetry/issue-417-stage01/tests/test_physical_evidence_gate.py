"""Synthetic record controls. Never substitute test fixtures for real physical evidence."""
import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from physical_evidence_gate import assess

BLANK = json.loads((HERE/"M1_M3_RECORD_BLANK.json").read_text(encoding="utf-8"))


def fabricated_fixture_for_code_test_only():
    r = copy.deepcopy(BLANK)
    r["assessed_commit"] = "a" * 40
    r["evidence_refs"] = ["https://example.com/synthetic-test-only"]
    e = r["evidence"]
    e["actual_operators"] = 4
    e["printed_100mm_bar_measured_mm"] = 100
    e["actual_narasimha_with_control_rods"] = True
    for pos in e["m1_clearance_by_position"].values():
        pos["minimum_clearance_mm"] = 12
        pos["rods_included"] = True
    for tr in e["m2_trials"]:
        tr.update(opened=True, stayed_open=True, reveal_clear=True, no_jam=True)
    e["m3_operator_handoff"].update(no_unplanned_hands=True, all_controls_reachable=True)
    e["frame_stable"] = True
    e["no_sharp_edges_or_pinches"] = True
    return r


class EvidenceGateTests(unittest.TestCase):
    def test_blank_template_never_claims_pass(self):
        result = assess(BLANK)
        self.assertEqual(result["status"], "INCOMPLETE_HOLD")
        self.assertTrue(result["missing"])
        self.assertTrue(result["no_physical_or_manufacturing_approval"])

    def test_synthetic_complete_is_only_review_ready(self):
        result = assess(fabricated_fixture_for_code_test_only())
        self.assertEqual(result["status"], "READY_FOR_INDEPENDENT_HUMAN_REVIEW_NOT_APPROVED")
        self.assertTrue(result["evidence_is_self_reported"])

    def test_unsafe_clearance_is_fail(self):
        r = fabricated_fixture_for_code_test_only()
        r["evidence"]["m1_clearance_by_position"]["door_plane"]["minimum_clearance_mm"] = 8
        self.assertEqual(assess(r)["status"], "RECORDED_FAILURE_HOLD")

    def test_any_jam_is_fail(self):
        r = fabricated_fixture_for_code_test_only()
        r["evidence"]["m2_trials"][3]["no_jam"] = False
        self.assertIn("M2_TRIAL_4_NO_JAM_FAIL", assess(r)["observed_failures"])

    def test_handoffs_cannot_use_hidden_helper(self):
        r = fabricated_fixture_for_code_test_only()
        r["evidence"]["m3_operator_handoff"]["no_unplanned_hands"] = False
        self.assertEqual(assess(r)["status"], "RECORDED_FAILURE_HOLD")

    def test_absent_real_evidence_ref_holds(self):
        r = fabricated_fixture_for_code_test_only()
        r["evidence_refs"] = []
        self.assertEqual(assess(r)["status"], "INCOMPLETE_HOLD")

    def test_incorrect_scale_holds(self):
        r = fabricated_fixture_for_code_test_only()
        r["evidence"]["printed_100mm_bar_measured_mm"] = 96
        self.assertIn("PRINT_SCALE_OUTSIDE_PROPOSED_99_101_MM", assess(r)["observed_failures"])

    def test_missing_rods_marked_incomplete(self):
        r = fabricated_fixture_for_code_test_only()
        r["evidence"]["m1_clearance_by_position"]["approach"]["rods_included"] = False
        self.assertEqual(assess(r)["status"], "INCOMPLETE_HOLD")


if __name__ == "__main__":
    unittest.main()
