#!/usr/bin/env python3
"""Read-only intake of real Stage-01 mock-up observations.

The output NEVER grants physical/product approval. It distinguishes missing
observations, recorded failures, and completeness for independent human review.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

REQUIRED_POSITIONS = ("approach", "door_plane", "emerged")
REQUIRED_COUNT = 5


def assess(record: dict) -> dict:
    missing: list[str] = []
    failed: list[str] = []
    evidence = record.get("evidence", {})
    if record.get("schema") != "puppet-stage01-physical-evidence/v1":
        missing.append("schema")
    commit = record.get("assessed_commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[a-f0-9]{40}", commit):
        missing.append("assessed_commit")
    operator_count = evidence.get("actual_operators")
    if not isinstance(operator_count, int) or isinstance(operator_count, bool) or operator_count < 1:
        missing.append("evidence.actual_operators")
    measured_print = evidence.get("printed_100mm_bar_measured_mm")
    if not isinstance(measured_print, (float, int)) or isinstance(measured_print, bool) or not math.isfinite(measured_print):
        missing.append("evidence.printed_100mm_bar_measured_mm")
    elif not (99 <= measured_print <= 101):
        failed.append("PRINT_SCALE_OUTSIDE_PROPOSED_99_101_MM")

    actual_cutout = evidence.get("actual_narasimha_with_control_rods")
    if actual_cutout is not True:
        missing.append("evidence.actual_narasimha_with_control_rods")

    positions = evidence.get("m1_clearance_by_position")
    if not isinstance(positions, dict):
        positions = {}
    for key in REQUIRED_POSITIONS:
        entry = positions.get(key, {})
        if not isinstance(entry, dict):
            entry = {}
        value = entry.get("minimum_clearance_mm")
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value < 0:
            missing.append(f"m1.{key}.minimum_clearance_mm")
        elif value < 10:
            failed.append(f"M1_CLEARANCE_BELOW_10MM_{key}")
        if entry.get("rods_included") is not True:
            missing.append(f"m1.{key}.rods_included")

    cycles = evidence.get("m2_trials", [])
    if not isinstance(cycles, list) or len(cycles) != REQUIRED_COUNT:
        missing.append("m2.five_distinct_trials")
        cycles = []
    ids = [v.get("trial") for v in cycles if isinstance(v, dict)]
    if ids and sorted(ids) != [1, 2, 3, 4, 5]:
        missing.append("m2.trial_ids_1_to_5")
    for item in cycles:
        if not isinstance(item, dict):
            missing.append("m2.trial_record")
            continue
        n = item.get("trial")
        for field in ("opened", "stayed_open", "reveal_clear", "no_jam"):
            value = item.get(field)
            if value is not True and value is not False:
                missing.append(f"m2.trial{n}.{field}")
            elif value is False:
                failed.append(f"M2_TRIAL_{n}_{field.upper()}_FAIL")

    m3 = evidence.get("m3_operator_handoff", {})
    if not isinstance(m3, dict):
        m3 = {}
    for key in ("no_unplanned_hands", "all_controls_reachable"):
        value = m3.get(key)
        if value is not True and value is not False:
            missing.append(f"m3.{key}")
        elif value is False:
            failed.append(f"M3_{key.upper()}_FAIL")
    for key in ("frame_stable", "no_sharp_edges_or_pinches"):
        value = evidence.get(key)
        if value is not True and value is not False:
            missing.append(f"safety.{key}")
        elif value is False:
            failed.append(f"SAFETY_{key.upper()}_FAIL")

    media = record.get("evidence_refs", [])
    if not isinstance(media, list) or not media or not all(
        isinstance(u, str) and u.startswith("https://") for u in media
    ):
        missing.append("evidence_refs_for_independent_review")

    if failed:
        status = "RECORDED_FAILURE_HOLD"
    elif missing:
        status = "INCOMPLETE_HOLD"
    else:
        status = "READY_FOR_INDEPENDENT_HUMAN_REVIEW_NOT_APPROVED"
    return {
        "schema": "puppet-stage01-evidence-intake-result/v1",
        "status": status,
        "missing": sorted(set(missing)),
        "observed_failures": sorted(set(failed)),
        "evidence_is_self_reported": True,
        "no_physical_or_manufacturing_approval": True,
        "notice": "No measurement or photograph was checked independently by this parser.",
    }


if __name__ == "__main__":
    file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("M1_M3_RECORD_BLANK.json")
    report = assess(json.loads(file.read_text(encoding="utf-8")))
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["status"] == "READY_FOR_INDEPENDENT_HUMAN_REVIEW_NOT_APPROVED" else 1)
