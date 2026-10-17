#!/usr/bin/env python3
"""Fail-closed candidate dimension/motion screen, not print or physical approval."""
from __future__ import annotations
import copy
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE / "FABRICATION_CANDIDATE.json"


def load(path: Path = CANDIDATE) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def inspect(config: dict) -> dict:
    stage = config["stage"]
    characters = config["characters"]
    errors = []
    if config.get("schema") != "puppet-415-fabrication-candidate/v1":
        errors.append("incorrect dimensional data schema")
    holes_seen = set()
    for name, model in characters.items():
        w, h = model["body"]["width"], model["body"]["height"]
        arm = model.get("arms")
        for hole in model["holes"]:
            key = (name, hole["part"], hole["id"])
            if key in holes_seen:
                errors.append(f"duplicate hole ID {key}")
            holes_seen.add(key)
            radius = hole["diameter"] / 2
            if hole["diameter"] <= 0:
                errors.append(f"nonpositive hole diameter {key}")
                continue
            if hole["part"] == "body":
                if name == "narasimha":   # top centre coordinate datum
                    x_ok = abs(hole["x"]) + radius <= w/2
                else:                     # top-left datum
                    x_ok = radius <= hole["x"] <= w-radius
                y_ok = radius <= hole["y"] <= h-radius
            elif hole["part"].startswith("arm"):
                x_ok = radius <= hole["x"] <= arm["width"]-radius
                y_ok = radius <= hole["y"] <= arm["height"]-radius
            else:
                errors.append(f"unsupported hole part {key}")
                continue
            if not (x_ok and y_ok):
                errors.append(f"hole outside bounding material {key}")
    king = characters["king"]
    p = characters["prahlada"]
    n = characters["narasimha"]
    if king["internal_hinge_dof"] != 2 or king["active_joint_dof"] != 1:
        errors.append("king candidate DOF differs from inherited two-hinge design")
    if p["internal_hinge_dof"] != 0:
        errors.append("Prahlada must remain a fixed prayer silhouette")
    if n["internal_hinge_dof"] != 1:
        errors.append("Narasimha blessing joint missing")
    if n["arm_angle_deg_from_down"]["hidden"] != 0:
        errors.append("Narasimha arm must be DOWN inside portal")
    if n["arm_angle_deg_from_down"]["roar"] != 0:
        errors.append("Narasimha roar must use voice/body movement, no in-portal arm extension")
    if n["arm_angle_deg_from_down"]["bless_after_clear"] != 90:
        errors.append("blessing arm travel must be bounded at 90 degrees after exit")

    # Nominal 2.5D screen derived from PR #418; never substitute for full outline.
    opening_l = stage["pillar_center_x"] - stage["portal_width"]/2
    n_l = stage["n_center_x"] - stage["n_down_width"]/2
    side_gap = n_l - opening_l - stage["door_edge_intrusion_each"] - stage["tolerance_horizontal"]
    puppet_top = stage["n_initial_bottom"] + stage["n_rise"] + n["body"]["height"]
    headroom_existing = stage["portal_top"] - puppet_top - stage["tolerance_vertical"]
    headroom_proposed = stage["portal_open_top_proposal"] - puppet_top - stage["tolerance_vertical"]
    if not (stage["portal_open_top_proposal"] < stage["pillar_height"]):
        errors.append("proposed portal must leave a pillar lintel")
    if side_gap < stage["min_clearance"]:
        errors.append("Narasimha DOWN arm side passage fails")
    if headroom_proposed < stage["min_clearance"] + 5:
        errors.append("Narasimha proposed headroom needs 5mm additional reserve")
    if stage["unobstructed_below_stage"] < (n["control_sticks"]["main_length"] -
            n["control_sticks"]["main_overlap"] - stage["n_initial_bottom"]):
        errors.append("Narasimha control handle catches substage")

    n_right = stage["n_center_x"] + stage["n_blessing_reach_right"]
    grip_to_head = p["body"]["height"] + p["stick"]["length"] - p["stick"]["overlap"]
    def bow_gap(center: float, deg: float) -> float:
        return (center - p["body"]["width"]/2 -
                grip_to_head*math.sin(math.radians(deg)) -
                n_right - 2*stage["tolerance_horizontal"])

    bow = p["bow"]
    inherited_15 = bow_gap(stage["prahlada_center_x_inherited"], 15)
    inherited_16 = bow_gap(stage["prahlada_center_x_inherited"], 16)
    proposed_15 = bow_gap(stage["prahlada_center_x_proposal"], bow["target_deg"])
    proposed_20 = bow_gap(stage["prahlada_center_x_proposal"], bow["max_trial_deg"])
    if proposed_20 < stage["min_clearance"] + 5:
        errors.append("Prahlada proposed worst-case 20-degree bow lacks added clearance reserve")
    if proposed_15 < stage["design_margin_for_bow"]:
        errors.append("Prahlada nominal bow below proposed 20mm design margin")
    if stage["prahlada_center_x_proposal"] + p["body"]["width"]/2 > stage["width"] - 20:
        errors.append("Prahlada relocated puppet too close to stage edge")
    if n["body"]["width"] > stage["portal_width"]:
        errors.append("body wider than portal")
    if stage["n_down_width"] >= stage["portal_width"]:
        errors.append("parked Narasimha cannot pass portal")
    if stage["king_center_x"] + stage["king_shoulder_right_offset"] + stage["king_arm_reach"] < opening_l:
        errors.append("King striking arm cannot reach pillar opening edge")
    return {
      "schema":"puppet-415-geometry-screen/v1",
      "passed":not errors,
      "errors":errors,
      "authority":"RECTANGULAR_SOURCE_HYPOTHESIS_ONLY__NOT_PDF_OR_PHYSICAL_ACCEPTANCE",
      "metrics_mm":{
        "arm_down_side_gap_conservative":round(side_gap,2),
        "headroom_existing_pr418":round(headroom_existing,2),
        "headroom_proposed_portal":round(headroom_proposed,2),
        "bow_gap_inherited_15deg":round(inherited_15,2),
        "bow_gap_inherited_16deg":round(inherited_16,2),
        "bow_gap_relocated_15deg":round(proposed_15,2),
        "bow_gap_relocated_20deg":round(proposed_20,2)
      },
      "unresolved":[
        "Narasimha silhouette, arm coupler, pin head, door hinge and rod sweeps not measured",
        "Proposed +10mm portal headroom/237mm leaf and relocated Prahlada position need PR418 adoption",
        "v2 corrected PDF binaries unavailable for line geometry and 100% print validation",
        "physical five-cycle reveal, minimum gap and three-minute rehearsal NOT_RUN"
      ]
    }


if __name__ == "__main__":
    result = inspect(load())
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["passed"] else 1)
