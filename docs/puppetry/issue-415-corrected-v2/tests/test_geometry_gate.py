"""Synthetic/falsifying checks only; no physical puppet fabricated."""
import copy
import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from geometry_gate import inspect, load


class CandidateDimensionChecks(unittest.TestCase):
    def setUp(self):
        self.cfg = load()

    def test_current_proposal_has_consistent_candidate_geometry(self):
        out = inspect(self.cfg)
        self.assertTrue(out["passed"], out["errors"])
        self.assertEqual(out["authority"], "RECTANGULAR_SOURCE_HYPOTHESIS_ONLY__NOT_PDF_OR_PHYSICAL_ACCEPTANCE")

    def test_inherited_16_degree_bow_fails_minimum(self):
        m = inspect(self.cfg)["metrics_mm"]
        self.assertLess(m["bow_gap_inherited_16deg"], 10)

    def test_relocated_bow_20_degrees_has_margin(self):
        m = inspect(self.cfg)["metrics_mm"]
        self.assertGreater(m["bow_gap_relocated_20deg"], 20)

    def test_move_prahlada_back_to_old_center_fails(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["stage"]["prahlada_center_x_proposal"] = cfg["stage"]["prahlada_center_x_inherited"]
        out = inspect(cfg)
        self.assertFalse(out["passed"])
        self.assertTrue(any("bow" in e.lower() for e in out["errors"]))

    def test_opening_drops_to_inherited_height_fails_margin(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["stage"]["portal_open_top_proposal"] = cfg["stage"]["portal_top"]
        out = inspect(cfg)
        self.assertFalse(out["passed"])
        self.assertTrue(any("headroom" in e.lower() for e in out["errors"]))

    def test_shift_narasimha_off_center_fails(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["stage"]["n_center_x"] += 20
        # one-sided envelope screen must reject this, not report false success
        out = inspect(cfg)
        self.assertFalse(out["passed"])

    def test_oversized_hole_fails(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["characters"]["narasimha"]["holes"][0]["diameter"] = 20
        out = inspect(cfg)
        self.assertFalse(out["passed"])

    def test_arm_extended_inside_pillar_fails(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["characters"]["narasimha"]["arm_angle_deg_from_down"]["hidden"] = 90
        self.assertFalse(inspect(cfg)["passed"])

    def test_prahlada_hinge_regression_fails(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["characters"]["prahlada"]["internal_hinge_dof"] = 1
        self.assertFalse(inspect(cfg)["passed"])

    def test_insufficient_below_stage_grip_room_fails(self):
        cfg = copy.deepcopy(self.cfg)
        cfg["stage"]["unobstructed_below_stage"] = 80
        self.assertFalse(inspect(cfg)["passed"])


if __name__ == "__main__":
    unittest.main()
