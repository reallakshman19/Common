"""Focused falsifier checks for the #417 candidate stage model; no physical tests."""
import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stage_model import analyze

BASE = json.loads(Path(__file__).resolve().parents[1].joinpath('stage_candidate.json').read_text())


class StageModelTests(unittest.TestCase):
    def test_candidate_rectangular_screen(self):
        result = analyze(BASE)
        self.assertTrue(result['all_screened_checks_pass'], result['checks'])
        self.assertGreater(result['metrics_mm']['worst_case_left_right_side_clearance'][0], 10)
        self.assertIn('NO_PHYSICAL_VALIDATION', result['authority'])

    def test_narrow_opening_rejected(self):
        case = copy.deepcopy(BASE)
        case['pillar']['clear_opening_width_nominal'] = 104
        self.assertFalse(analyze(case)['checks']['arm_down_passes_opening'])

    def test_puppet_hits_rearward_door_sweep(self):
        case = copy.deepcopy(BASE)
        case['narasimha']['hidden_plane_z'] = 111
        self.assertFalse(analyze(case)['checks']['hidden_puppet_behind_leaf_sweep'])

    def test_high_reveal_hits_lintel(self):
        case = copy.deepcopy(BASE)
        case['narasimha']['rise_during_reveal'] = 45
        self.assertFalse(analyze(case)['checks']['vertical_head_clearance_after_rise'])

    def test_twenty_degree_prahlada_bow_conflicts(self):
        case = copy.deepcopy(BASE)
        case['prahlada']['bow_degrees_toward_pillar'] = 20
        self.assertFalse(analyze(case)['checks']['prahlada_bow_vs_narasimha_blessing_nominal'])

    def test_arm_must_remain_down_in_aperture(self):
        case = copy.deepcopy(BASE)
        case['narasimha']['arm_pose_in_aperture'] = 'BLESS_90_DEGREES'
        self.assertFalse(analyze(case)['checks']['blessing_arm_outside_aperture_only'])

    def test_missing_understage_grip_space_rejected(self):
        case = copy.deepcopy(BASE)
        case['stage']['substage_clearance_required'] = 80
        self.assertFalse(analyze(case)['checks']['substage_handle_clearance'])


if __name__ == '__main__':
    unittest.main()
