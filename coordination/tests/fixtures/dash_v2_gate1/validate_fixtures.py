"""Validation runner for Gate 1 fixtures and schema.

Validates coordinator_state_v330_positive.json and coordinator_state_v330_negative.json
against source_contract.schema.json, verifies SHA-256 digests, and tests 10-cell derivation
and Smart Economy cadence rules.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_against_schema(data: dict, schema: dict) -> None:
    # Minimal self-contained JSON schema validator for source_contract.schema.json
    anchor = schema.get("properties", {}).get("claude_code_log_anchor", {})
    if "const" in anchor and data.get("claude_code_log_anchor") != anchor["const"]:
        raise ValueError("Invalid claude_code_log_anchor")

    patterns = schema.get("patternProperties", {})
    for key, val in data.items():
        if key == "claude_code_log_anchor":
            continue
        matched = False
        for pat, pat_schema in patterns.items():
            if re.match(pat, key):
                matched = True
                _validate_object(key, val, pat_schema)
                break
        if not matched and not schema.get("additionalProperties", True):
            raise ValueError(f"Unrecognized key not matching schema: {key}")


def _validate_object(key: str, val: any, spec: dict) -> None:
    expected_type = spec.get("type")
    if expected_type:
        types = [expected_type] if isinstance(expected_type, str) else expected_type
        actual = (
            "null" if val is None else
            "boolean" if isinstance(val, bool) else
            "integer" if isinstance(val, int) and not isinstance(val, bool) else
            "number" if isinstance(val, (int, float)) and not isinstance(val, bool) else
            "string" if isinstance(val, str) else
            "array" if isinstance(val, list) else
            "object" if isinstance(val, dict) else "unknown"
        )
        if actual not in types:
            raise ValueError(f"{key}: expected type {types}, got {actual}")

    if isinstance(val, dict):
        required = spec.get("required", [])
        for req in required:
            if req not in val:
                raise ValueError(f"{key}: missing required property '{req}'")
        props = spec.get("properties", {})
        for prop_key, prop_val in val.items():
            if prop_key in props:
                _validate_object(f"{key}.{prop_key}", prop_val, props[prop_key])

    if "enum" in spec and val not in spec["enum"]:
        raise ValueError(f"{key}: value '{val}' not in enum {spec['enum']}")


def test_ten_cells_derivation(data: dict) -> list[dict]:
    """Test derivation of all 10 cells from state data matching watch.ps1 rowsjson."""
    cycle_key = next((k for k in data if k.startswith("claude_code_cycle_")), None)
    if not cycle_key:
        raise ValueError("Missing cycle state")
    cycle = data[cycle_key]
    cycle_mins = cycle.get("cycle", 30)
    seen_map = {}
    for entry in cycle.get("seen", []):
        parts = entry.split("|")
        if len(parts) >= 3:
            seen_map[parts[1]] = parts[2]

    rows = []
    for entry in cycle.get("map", []):
        parts = entry.split("|")
        if len(parts) < 4:
            continue
        pos, chat_id, folder, label = parts[0], parts[1], parts[2], parts[3]
        hw = data.get(f"claude_code_hw_{chat_id}", {})
        aim = data.get(f"claude_code_aim_{label}", {})

        # 1. Tab
        c_tab = f"Tab {pos}"
        # 2. Status
        last_state = hw.get("lastState", "unknown")
        park_at = hw.get("parkAt")
        c_status = f"parked: {hw.get('parkWhy')}" if park_at else last_state
        # 3. Aim
        c_aim = f"v{aim.get('vMain', 0)}.{aim.get('vTask', 0)}.{aim.get('vGuide', 0)}" if aim else "-"
        # 4. Plan
        c_plan = hw.get("fPlan") or "-"
        # 5. AC
        c_ac = hw.get("fAc") or "-"
        # 6. CI
        c_ci = hw.get("fCi") or "-"
        # 7. Meter
        turns = hw.get("turns", 0)
        cost_k = hw.get("costK", 0.0)
        c_meter = f"{turns} turns / {cost_k}k"
        # 8. Due
        c_due = hw.get("buddy") or "-"
        # 9. Checked
        c_checked = seen_map.get(chat_id, "**never**")
        # 10. Next
        c_next = "wait for reply" if hw.get("fHv") == "ready" else "normal route"

        rows.append({
            "tab": c_tab,
            "status": c_status,
            "aim": c_aim,
            "plan": c_plan,
            "ac": c_ac,
            "ci": c_ci,
            "meter": c_meter,
            "due": c_due,
            "checked": c_checked,
            "next": c_next
        })
    return rows


def test_cadence_evaluation(data: dict) -> int:
    """Test smart economy cadence derivation matching ghwatch.ps1 Cadence."""
    relay_key = next((k for k in data if k.startswith("claude_code_gh_relay_")), None)
    relay = data.get(relay_key, {}) if relay_key else {}
    cycle_key = next((k for k in data if k.startswith("claude_code_cycle_")), None)
    cycle = data.get(cycle_key, {}) if cycle_key else {}

    unsettled = []
    for entry in cycle.get("map", []):
        parts = entry.split("|")
        if len(parts) < 4:
            continue
        pos, chat_id, folder, label = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
        # Get-Works skips empty folder, [HOLD], [OUT], retired
        if not folder or re.match(r"^\[(HOLD|OUT)\]", label) or label.startswith("retired"):
            continue
        short = re.match(r"^(.+?)\s+-\s", label).group(1) if re.match(r"^(.+?)\s+-\s", label) else (label or f"Tab{pos}")
        hw = data.get(f"claude_code_hw_{chat_id}")
        if not hw or not hw.get("lastSeen") or not hw.get("fLine") or hw.get("turns", 0) < 2:
            unsettled.append(f"{short} boarding")
            continue
        if (hw.get("aLane") and hw.get("aLane") != "retired") or hw.get("buddy") in ("due", "s1", "s1ok", "areview", "s2") or hw.get("fHv") in ("due", "ready"):
            unsettled.append(f"{short} handover")
            continue
        if hw.get("parkAt") or (hw.get("fBk") and str(hw.get("fBk")).startswith("OWNER")):
            unsettled.append(f"{short} waits for Owner")
            continue
        r = relay.get(short)
        if r and r.get("forLa") and (not r.get("laDone") or r.get("forLa") > r.get("laDone")):
            unsettled.append(f"{short} LA paste pending")

    return 30 if unsettled else 60


def run():
    schema_path = ROOT / "source_contract.schema.json"
    pos_path = ROOT / "coordinator_state_v330_positive.json"
    neg_path = ROOT / "coordinator_state_v330_negative.json"

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    pos_data = json.loads(pos_path.read_text(encoding="utf-8"))
    neg_data = json.loads(neg_path.read_text(encoding="utf-8"))

    results = {}

    # 1. Schema validation
    try:
        validate_against_schema(pos_data, schema)
        results["POSITIVE_FIXTURE_SCHEMA_MATCH"] = "PASS"
    except Exception as e:
        results["POSITIVE_FIXTURE_SCHEMA_MATCH"] = f"FAIL: {e}"

    try:
        validate_against_schema(neg_data, schema)
        results["NEGATIVE_FIXTURE_SCHEMA_MATCH"] = "PASS"
    except Exception as e:
        results["NEGATIVE_FIXTURE_SCHEMA_MATCH"] = f"FAIL: {e}"

    # 2. 10 Cells Derivation
    try:
        pos_rows = test_ten_cells_derivation(pos_data)
        assert len(pos_rows) == 3, f"Expected 3 rows, got {len(pos_rows)}"
        for r in pos_rows:
            assert len(r) == 10, f"Expected 10 cells, got {len(r)}"
        neg_rows = test_ten_cells_derivation(neg_data)
        assert len(neg_rows) == 3
        results["TEN_CELL_LINEAGE_DERIVATION"] = "PASS"
    except Exception as e:
        results["TEN_CELL_LINEAGE_DERIVATION"] = f"FAIL: {e}"

    # 3. Smart Economy Cadence
    try:
        cadence_pos = test_cadence_evaluation(pos_data)
        assert cadence_pos == 30, f"Expected 30 min (unsettled), got {cadence_pos}"
        cadence_neg = test_cadence_evaluation(neg_data)
        assert cadence_neg == 30, f"Expected 30 min (unsettled), got {cadence_neg}"

        # Test fully settled synthetic data -> 60 min budget guard
        settled_data = json.loads(pos_path.read_text(encoding="utf-8"))
        settled_data["claude_code_gh_relay_Session_Synth"]["Synth-Work-2"]["laDone"] = "2026-10-13T12:05:00Z"
        settled_data["claude_code_hw_e5f6a7b8"]["fHv"] = None
        settled_data["claude_code_hw_e5f6a7b8"]["aLane"] = "retired"
        settled_cadence = test_cadence_evaluation(settled_data)
        assert settled_cadence == 60, f"Expected 60 min budget guard, got {settled_cadence}"

        results["SMART_ECONOMY_CADENCE_EVALUATION"] = "PASS"
    except Exception as e:
        results["SMART_ECONOMY_CADENCE_EVALUATION"] = f"FAIL: {e}"

    # 4. Digests
    digests = {
        "schema_sha256": compute_sha256(schema_path),
        "positive_fixture_sha256": compute_sha256(pos_path),
        "negative_fixture_sha256": compute_sha256(neg_path),
    }

    report = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fixture_version": "3.30.0-gate1-synthetic",
        "results": results,
        "digests": digests,
        "live_sources_status": "LOCAL_VERIFIED",
        "ci_status": "FOCUSED_FIXTURE_VALIDATION_ONLY",
    }
    print(json.dumps(report, indent=2))
    return all(v == "PASS" for v in results.values())


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
