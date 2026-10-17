"""Negative and positive candidate topology checks; physical fit is NOT_RUN."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from portal_gate import screen

MOCK = json.loads((ROOT/"mockup_candidate_v1.json").read_text())
STUDY = json.loads((ROOT/"stage_candidate.json").read_text())


class PortalTopologyTests(unittest.TestCase):
    def test_candidate_standoff_and_route(self):
        result=screen(MOCK,STUDY)
        self.assertTrue(result["all_pass"], result["checks"])
        self.assertIn("NOT_PHYSICAL_PASS", result["status"])

    def test_solid_floor_blocks_controls(self):
        c=copy.deepcopy(MOCK)
        c["stage"]["solid_floor_in_corridor_allowed"]=True
        self.assertFalse(screen(c,STUDY)["checks"]["no_solid_floor_across_stick_route"])

    def test_flush_backdrop_mount_disallowed(self):
        c=copy.deepcopy(MOCK)
        c["pillar"]["door_plane_z"]=150
        self.assertFalse(screen(c,STUDY)["checks"]["pillar_not_flush_to_backdrop"])
        self.assertFalse(screen(c,STUDY)["checks"]["door_front_of_hidden_puppet"])

    def test_rear_wall_blocks_hidden_position(self):
        c=copy.deepcopy(MOCK)
        c["stage"]["rear_backdrop_z"]=127
        self.assertFalse(screen(c,STUDY)["checks"]["backdrop_rearward_of_hidden_puppet"])

    def test_understage_clearance_short(self):
        c=copy.deepcopy(MOCK)
        c["stage"]["puppet_stick_corridor"]["below_baseline_min"]=80
        self.assertFalse(screen(c,STUDY)["checks"]["stick_corridor_vertical_clearance"])

    def test_floor_slot_too_short(self):
        c=copy.deepcopy(MOCK)
        c["stage"]["puppet_stick_corridor"]["z_min"]=35
        self.assertFalse(screen(c,STUDY)["checks"]["stick_corridor_covers_110mm_travel"])

    def test_side_return_blocks_opening(self):
        c=copy.deepcopy(MOCK)
        c["pillar"]["proposed_side_returns_world_x"][0]=[295,310]
        self.assertFalse(screen(c,STUDY)["checks"]["side_returns_stay_out_of_portal"])

    def test_thin_floor_slot_rejected(self):
        c=copy.deepcopy(MOCK)
        c["stage"]["puppet_stick_corridor"]["x_max"]=430
        self.assertFalse(screen(c,STUDY)["checks"]["stick_corridor_covers_portal_width"])


if __name__=="__main__":
    unittest.main()
