#!/usr/bin/env python3
"""Preflight topology of the proposed pillar/rod assembly.

This checks configuration consistency ONLY; it does not measure any built
cardboard or operator's hand clearance. Conservative assumptions remain explicit.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def screen(mockup: dict, study: dict) -> dict:
    st = mockup["stage"]
    pill = mockup["pillar"]
    path = st["puppet_stick_corridor"]
    spec = study["pillar"]
    n = study["narasimha"]
    safe_gap = study["tolerances"]["depth_placement_each"]
    x_left = spec["center_x"] - spec["clear_opening_width_nominal"] / 2
    x_right = spec["center_x"] + spec["clear_opening_width_nominal"] / 2
    support = pill["proposed_side_returns_world_x"]
    checks = {
        "backdrop_rearward_of_hidden_puppet": st["rear_backdrop_z"] >= n["hidden_plane_z"] + safe_gap,
        "door_front_of_hidden_puppet": pill["door_plane_z"] < n["hidden_plane_z"],
        "door_rearward_of_emerged_puppet": pill["door_plane_z"] > n["front_plane_z"],
        "pillar_not_flush_to_backdrop": not pill["flush_mount_against_rear_backdrop_allowed"]
            and pill["door_plane_z"] < st["rear_backdrop_z"],
        "stick_corridor_covers_portal_width": path["x_min"] <= x_left and path["x_max"] >= x_right,
        "stick_corridor_covers_110mm_travel": path["z_min"] <= n["front_plane_z"]
            and path["z_max"] >= n["hidden_plane_z"],
        "stick_corridor_vertical_clearance": path["below_baseline_min"] >= 140
            and st["unobstructed_below_baseline_required"] >= 140,
        "no_solid_floor_across_stick_route": st["solid_floor_in_corridor_allowed"] is False,
        "side_returns_stay_out_of_portal": support[0][1] < x_left
            and support[1][0] > x_right,
        "supports_run_from_pillar_to_backdrop": pill["proposed_side_return_z"] == [
            pill["door_plane_z"], st["rear_backdrop_z"]],
        "mockup_opening_matches_study": (
            pill["opening_right"]-pill["opening_left"] == spec["clear_opening_width_nominal"])
    }
    return {
        "schema":"puppet-portal-preflight/v1",
        "status":"PROPOSED_ASSEMBLY_CONSISTENCY_ONLY_NOT_PHYSICAL_PASS",
        "checks":checks,
        "all_pass":all(checks.values()),
        "observations_required":[
            "Actual rear-wall and frame spacing measured",
            "No stage floor/support catches rod as it translates 110 mm",
            "Actual control rod and coupler in physical gap screen",
            "Side returns support frame safely and mask oblique view",
            "Physical door sweep and operator hands tested"
        ]
    }


if __name__ == "__main__":
    a=json.loads((HERE/"mockup_candidate_v1.json").read_text(encoding="utf-8"))
    b=json.loads((HERE/"stage_candidate.json").read_text(encoding="utf-8"))
    out=screen(a,b)
    print(json.dumps(out,indent=2))
    raise SystemExit(0 if out["all_pass"] else 1)
