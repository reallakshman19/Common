#!/usr/bin/env python3
"""Candidate-only 2D/2.5D stage clearance screen for Common #417.

Computed rectangular envelopes are conservative approximations and cannot
certify cardboard fit, linkages, stage safety or a three-minute rehearsal.
"""
import json
import math
import sys
from pathlib import Path

DEFAULT = Path(__file__).with_name('stage_candidate.json')


def analyze(cfg: dict) -> dict:
    st, p, n, k, pr, tol = (cfg[x] for x in (
        'stage', 'pillar', 'narasimha', 'king', 'prahlada', 'tolerances'))
    opening_l = p['center_x'] - p['clear_opening_width_nominal'] / 2
    opening_r = p['center_x'] + p['clear_opening_width_nominal'] / 2
    outer_l = p['center_x'] - p['outer_width'] / 2
    outer_r = p['center_x'] + p['outer_width'] / 2
    shut_l = n['center_x'] - n['arm_down_width'] / 2
    shut_r = n['center_x'] + n['arm_down_width'] / 2
    clear_l = shut_l - (opening_l + p['edge_intrusion_each'])
    clear_r = (opening_r - p['edge_intrusion_each']) - shut_r
    min_side_clearance = min(clear_l, clear_r) - tol['horizontal_placement_each']
    leaf_swing_back_max_z = (p['door_plane_z'] +
        p['left_and_right_leaf_width'] * math.sin(math.radians(p['opening_angle_degrees'])))
    rear_gap = n['hidden_plane_z'] - leaf_swing_back_max_z - tol['depth_placement_each']
    front_gap = p['door_plane_z'] - n['front_plane_z'] - tol['depth_placement_each']
    top_at_reveal = n['body_bottom_initial_y'] + n['rise_during_reveal'] + n['body_height']
    upper_gap = p['opening_top_y'] - top_at_reveal - tol['vertical_placement_each']
    lower_gap = n['body_bottom_initial_y'] - p['opening_bottom_y'] - tol['vertical_placement_each']
    below_floor_handle = max(0, n['main_stick'] - n['body_overlap'] - n['body_bottom_initial_y'])
    king_pivot_x = k['center_x'] + k['shoulder_offset_from_center_x']
    king_reach_gap = opening_l - (king_pivot_x + k['active_arm_reach_from_pivot'])
    nr_blessing_right = n['center_x'] + n['active_arm_span_to_audience_right_from_centre']
    pr_visible_handle = pr['main_stick'] - pr['body_overlap']
    pr_head_to_grip = pr_visible_handle + pr['body_height']
    pr_nearest_head_x = (pr['center_x'] - pr['body_width']/2 -
        pr_head_to_grip*math.sin(math.radians(pr['bow_degrees_toward_pillar'])))
    pr_bow_gap = pr_nearest_head_x - nr_blessing_right - 2*tol['horizontal_placement_each']
    threshold = tol['required_worst_case_gap']
    checks = {
      'arm_down_passes_opening': min_side_clearance >= threshold,
      'hidden_puppet_behind_leaf_sweep': rear_gap >= threshold,
      'revealed_puppet_in_front_of_leaf_sweep': front_gap >= threshold,
      'vertical_head_clearance_after_rise': upper_gap >= threshold,
      'vertical_feet_clearance_initial': lower_gap >= threshold,
      'substage_handle_clearance': st['substage_clearance_required'] >= below_floor_handle,
      'prahlada_bow_vs_narasimha_blessing_nominal': pr_bow_gap >= threshold,
      'king_active_arm_reaches_pillar_opening_edge': king_reach_gap <= 0,
      'pillar_fits_stage': outer_l >= 0 and outer_r <= st['width'] and p['overall_height'] <= st['visible_height']
    }
    expanded_envelope_w = (n['active_arm_span_to_audience_right_from_centre'] +
        n['opposite_body_span_from_centre'])
    checks['blessing_arm_outside_aperture_only'] = (
        expanded_envelope_w > p['clear_opening_width_nominal'] and
        n['arm_pose_in_aperture'] == 'DOWN_ONLY' and
        n['arm_pose_after_front_clearance'] == 'BLESS_90_DEGREES')
    return {
      'schema': 'puppet-stage-screen/v1',
      'authority': 'CANDIDATE_GEOMETRY_ONLY_NO_PHYSICAL_VALIDATION',
      'all_screened_checks_pass': all(checks.values()),
      'checks': checks,
      'metrics_mm': {
        'pillar_outer_x_range': [outer_l, outer_r],
        'nominal_opening_x_range': [opening_l, opening_r],
        'narasimha_arm_down_x_range': [shut_l, shut_r],
        'worst_case_left_right_side_clearance': [clear_l-tol['horizontal_placement_each'], clear_r-tol['horizontal_placement_each']],
        'swing_back_max_z': leaf_swing_back_max_z,
        'worst_case_rear_gap_z': rear_gap,
        'worst_case_front_gap_z': front_gap,
        'worst_case_headroom_after_20mm_rise': upper_gap,
        'worst_case_foot_clearance': lower_gap,
        'exposed_handle_required_below_stage_y': below_floor_handle,
        'narasimha_raised_arm_horizontal_span': expanded_envelope_w,
        'king_reach_minus_opening_gap': -king_reach_gap,
        'worst_case_prahlada_bow_to_blessing_right_gap': pr_bow_gap,
        'prahlada_head_horizontal_shift_bow': pr_head_to_grip*math.sin(math.radians(pr['bow_degrees_toward_pillar']))
      },
      'limitations': cfg['physical_unknowns']
    }


def main() -> int:
    cfg = json.loads(Path(sys.argv[1] if len(sys.argv)>1 else DEFAULT).read_text(encoding='utf-8'))
    result = analyze(cfg)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['all_screened_checks_pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
