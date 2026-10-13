"""Strict validation runner for Gate 1 fixtures, schema, and manifest (R4).

Enforces:
1. Strict Draft 2020-12 schema validation engine (type, minimum, items, pattern,
   patternProperties, additionalProperties) with exact Draft 2020-12 numeric/integer semantics:
   - Integers: whole numbers where num == int(num) (e.g. 1 and 1.0 are valid integers)
   - Numbers: int and float (excluding boolean)
   - Strict rejection of booleans and non-integral floats for integer type
2. Positive discriminating integer test:
   - cycle1.0 (integral float 1.0 is valid integer and >= minimum 1) -> PASS
3. Six adversarial negative mutation profile rejections:
   - cycle0 (minimum constraint violation) -> REJECTED
   - boolean_cycle (boolean True rejected for integer type) -> REJECTED
   - nonintegral_cycle (non-integral float 1.5 rejected for integer type) -> REJECTED
   - numeric_map_entry (items type constraint violation) -> REJECTED
   - malformed_hw_id (key pattern / additionalProperties constraint violation) -> REJECTED
   - numeric_relay_entry (nested additionalProperties type constraint violation) -> REJECTED
4. Exact literal 10-cell string equality against source-grounded expected outputs:
   - ac derived from legitimate aca / act integer fields (default -1 -> "-")
   - ci derived from legitimate fTests / fProof fields (default empty -> "-")
   - Removal of fabricated fAc / fCi claims
5. Smart Economy cadence derivation (30m unsettled vs 60m budget guard).
6. Artifact manifest membership, existence, and tamper enforcement:
   - Manifest MUST declare all required evidence artifacts (fails if schema omitted)
   - All declared artifacts MUST exist on disk (fails if missing-evidence.json declared)
   - Pinned fixed digests verified against disk content
   - Adversarial tamper and corrupt digest detection
7. Truthful live installed source status:
   - Read and hash installed coordinator scripts locally
   - Report LIVE_INSTALLED_SOURCE_PARITY as NOT_RUN with explicit dependency rationale
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent

REQUIRED_ARTIFACTS = {
    "source_contract.schema.json",
    "coordinator_state_v330_positive.json",
    "coordinator_state_v330_negative.json",
    "SOURCE_CONTRACT.md",
    "validate_fixtures.py",
}


def compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ValidationError(ValueError):
    pass


def is_draft202012_integer(val: any) -> bool:
    """Draft 2020-12 integer check: whole number, excluding booleans."""
    if isinstance(val, bool):
        return False
    if isinstance(val, int):
        return True
    if isinstance(val, float) and val.is_integer():
        return True
    return False


def is_draft202012_number(val: any) -> bool:
    """Draft 2020-12 number check: int or float, excluding booleans."""
    if isinstance(val, bool):
        return False
    return isinstance(val, (int, float))


def validate_schema(instance: any, schema: dict, path: str = "$") -> None:
    """Strict Draft 2020-12 recursive schema validator."""
    if not isinstance(schema, dict):
        return

    # 1. Type validation
    if "type" in schema:
        expected = schema["type"]
        types = [expected] if isinstance(expected, str) else expected

        valid_type = False
        for t in types:
            if t == "null" and instance is None:
                valid_type = True
                break
            elif t == "boolean" and isinstance(instance, bool):
                valid_type = True
                break
            elif t == "integer" and is_draft202012_integer(instance):
                valid_type = True
                break
            elif t == "number" and is_draft202012_number(instance):
                valid_type = True
                break
            elif t == "string" and isinstance(instance, str) and not isinstance(instance, bool):
                valid_type = True
                break
            elif t == "array" and isinstance(instance, list):
                valid_type = True
                break
            elif t == "object" and isinstance(instance, dict):
                valid_type = True
                break

        if not valid_type:
            raise ValidationError(
                f"{path}: expected type {types}, got {type(instance).__name__} (value={instance!r})"
            )

    # 2. Const validation
    if "const" in schema:
        if instance != schema["const"] or type(instance) != type(schema["const"]):
            raise ValidationError(f"{path}: expected const {schema['const']!r}, got {instance!r}")

    # 3. Enum validation
    if "enum" in schema:
        if instance not in schema["enum"]:
            raise ValidationError(f"{path}: value {instance!r} not in enum {schema['enum']}")

    # 4. Numeric minimum / maximum
    if is_draft202012_number(instance):
        if "minimum" in schema and instance < schema["minimum"]:
            raise ValidationError(f"{path}: value {instance} is less than minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            raise ValidationError(f"{path}: value {instance} is greater than maximum {schema['maximum']}")

    # 5. String pattern
    if isinstance(instance, str) and not isinstance(instance, bool):
        if "pattern" in schema:
            if not re.search(schema["pattern"], instance):
                raise ValidationError(f"{path}: string {instance!r} does not match pattern {schema['pattern']}")

    # 6. Array items
    if isinstance(instance, list):
        if "items" in schema:
            item_schema = schema["items"]
            for idx, item in enumerate(instance):
                validate_schema(item, item_schema, f"{path}[{idx}]")

    # 7. Object properties, patternProperties, required, additionalProperties
    if isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                raise ValidationError(f"{path}: missing required property {req!r}")

        properties = schema.get("properties", {})
        pattern_props = schema.get("patternProperties", {})
        additional_props = schema.get("additionalProperties", True)

        for prop_key, prop_val in instance.items():
            matched = False
            prop_path = f"{path}.{prop_key}"

            if prop_key in properties:
                matched = True
                validate_schema(prop_val, properties[prop_key], prop_path)

            for pat, pat_schema in pattern_props.items():
                if re.search(pat, prop_key):
                    matched = True
                    validate_schema(prop_val, pat_schema, prop_path)

            if not matched:
                if additional_props is False:
                    raise ValidationError(f"{path}: property {prop_key!r} not allowed by additionalProperties: false")
                elif isinstance(additional_props, dict):
                    validate_schema(prop_val, additional_props, prop_path)


def test_adversarial_mutations(base_data: dict, schema: dict) -> dict[str, str]:
    """Test and require rejection of six adversarial mutation profiles, plus one positive discriminating test."""
    results = {}

    # Positive Discriminating Test: cycle1.0 (valid JSON integer float under Draft 2020-12)
    pos_cycle_float = copy.deepcopy(base_data)
    pos_cycle_float["claude_code_cycle_Session_Synth"]["cycle"] = 1.0
    try:
        validate_schema(pos_cycle_float, schema)
        results["cycle1_0_discriminating_valid"] = "PASS"
    except ValidationError as e:
        results["cycle1_0_discriminating_valid"] = f"FAIL: rejected valid cycle=1.0: {e}"

    # Mutation 1: cycle0 (cycle = 0, minimum constraint violation)
    mut1 = copy.deepcopy(base_data)
    mut1["claude_code_cycle_Session_Synth"]["cycle"] = 0
    try:
        validate_schema(mut1, schema)
        results["cycle0"] = "FAIL: accepted cycle=0"
    except ValidationError:
        results["cycle0"] = "PASS"

    # Mutation 2: boolean_cycle (cycle = True, boolean rejected for integer type)
    mut2 = copy.deepcopy(base_data)
    mut2["claude_code_cycle_Session_Synth"]["cycle"] = True
    try:
        validate_schema(mut2, schema)
        results["boolean_cycle"] = "FAIL: accepted boolean cycle=True"
    except ValidationError:
        results["boolean_cycle"] = "PASS"

    # Mutation 3: nonintegral_cycle (cycle = 1.5, non-integral float rejected for integer type)
    mut3 = copy.deepcopy(base_data)
    mut3["claude_code_cycle_Session_Synth"]["cycle"] = 1.5
    try:
        validate_schema(mut3, schema)
        results["nonintegral_cycle"] = "FAIL: accepted non-integral cycle=1.5"
    except ValidationError:
        results["nonintegral_cycle"] = "PASS"

    # Mutation 4: numeric_map_entry (map contains integer instead of string)
    mut4 = copy.deepcopy(base_data)
    mut4["claude_code_cycle_Session_Synth"]["map"] = [123]
    try:
        validate_schema(mut4, schema)
        results["numeric_map_entry"] = "FAIL: accepted numeric map entry"
    except ValidationError:
        results["numeric_map_entry"] = "PASS"

    # Mutation 5: malformed_hw_id (key does not match 8-hex pattern)
    mut5 = copy.deepcopy(base_data)
    mut5["claude_code_hw_ZZZZZZZZ"] = copy.deepcopy(mut5["claude_code_hw_a1b2c3d4"])
    mut5["claude_code_hw_ZZZZZZZZ"]["id"] = "ZZZZZZZZ"
    try:
        validate_schema(mut5, schema)
        results["malformed_hw_id"] = "FAIL: accepted malformed hw key"
    except ValidationError:
        results["malformed_hw_id"] = "PASS"

    # Mutation 6: numeric_relay_entry (work relay record is integer instead of object)
    mut6 = copy.deepcopy(base_data)
    mut6["claude_code_gh_relay_Session_Synth"]["Synth-Work-1"] = 123
    try:
        validate_schema(mut6, schema)
        results["numeric_relay_entry"] = "FAIL: accepted numeric relay entry"
    except ValidationError:
        results["numeric_relay_entry"] = "PASS"

    return results


def derive_ten_cells(data: dict) -> list[dict]:
    """Derive literal 10 cells from coordinator state matching watch.ps1 rowsjson."""
    cycle_key = next((k for k in data if k.startswith("claude_code_cycle_")), None)
    if not cycle_key:
        raise ValueError("Missing cycle state")
    cycle = data[cycle_key]

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
        pos, chat_id, folder, name = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
        hw = data.get(f"claude_code_hw_{chat_id}", {})
        aim = data.get(f"claude_code_aim_{name}", {})

        # 1. Tab
        c_tab = f"Tab {pos}"

        # 2. Status
        if name.startswith("[OUT]"):
            c_status = "⚪ not in my scope"
        elif hw.get("parkAt"):
            c_status = f"⚪ parked: {hw.get('parkWhy')}"
        elif hw.get("aLane") == "asked" and hw.get("fHv") == "ready":
            c_status = "🟡 Buddy: 1a ready (G1 holds)"
        elif hw.get("lastState") == "working":
            c_status = "🟢 working"
        else:
            c_status = hw.get("lastState", "-")

        # 3. Aim
        if aim and aim.get("status") == "ACTIVE":
            v_str = f"v{aim.get('vMain', 0)}.{aim.get('vTask', 0)}.{aim.get('vGuide', 0)}"
            judge = aim.get("judge") or {}
            color_dot = "🟢" if judge.get("color") == "green" else "🟡"
            sum_txt = judge.get("sum", "")
            why_txt = f" · {judge.get('why')}" if judge.get("why") else ""
            c_aim = f"[🛡️] {v_str} · {color_dot} {sum_txt}{why_txt} · card 01"
        else:
            c_aim = "-"

        # 4. Plan
        c_plan = hw.get("fPlan") or "-"

        # 5. AC (Derived strictly from aca and act per watch.ps1)
        aca = hw.get("aca", -1)
        act = hw.get("act", -1)
        if isinstance(aca, (int, float)) and aca >= 0:
            c_ac = f"{int(aca)}/{int(act) if isinstance(act, (int, float)) and act >= 0 else '?'}"
        else:
            c_ac = "-"

        # 6. CI (Derived strictly from fTests / fProof per watch.ps1)
        if hw.get("fTests"):
            c_ci = hw.get("fTests")
        elif hw.get("fProof"):
            c_ci = hw.get("fProof")[:22]
        else:
            c_ci = "-"

        # 7. Meter
        turns = hw.get("turns", 0)
        cost_k = hw.get("costK", 0.0)
        c_meter = f"{turns} turns / {cost_k}k"

        # 8. Due
        c_due = hw.get("buddy") or "-"

        # 9. Checked
        c_checked = seen_map.get(chat_id, "**never**")

        # 10. Next
        if name.startswith("[OUT]"):
            c_next = "nothing"
        elif hw.get("aLane") == "asked" and hw.get("fHv") == "ready":
            c_next = "new chat: 1b pointer"
        else:
            c_next = "normal route"

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
            "next": c_next,
        })
    return rows


EXPECTED_POSITIVE_ROWS = [
    {
        "tab": "Tab 1",
        "status": "🟢 working",
        "aim": "[🛡️] v1.0.0 · 🟢 On track with source verification · All field types match installed PowerShell implementation · card 01",
        "plan": "Verify fixtures against schema",
        "ac": "-",
        "ci": "-",
        "meter": "8 turns / 4.5k",
        "due": "-",
        "checked": "2026-10-13T12:05:00Z",
        "next": "normal route",
    },
    {
        "tab": "Tab 2",
        "status": "🟡 Buddy: 1a ready (G1 holds)",
        "aim": "-",
        "plan": "Handover to successor session",
        "ac": "-",
        "ci": "PASS",
        "meter": "14 turns / 7.2k",
        "due": "-",
        "checked": "2026-10-13T12:05:00Z",
        "next": "new chat: 1b pointer",
    },
    {
        "tab": "Tab 3",
        "status": "⚪ not in my scope",
        "aim": "-",
        "plan": "-",
        "ac": "-",
        "ci": "-",
        "meter": "0 turns / 0.0k",
        "due": "-",
        "checked": "**never**",
        "next": "nothing",
    },
]


def test_cadence_evaluation(data: dict) -> int:
    """Evaluate Smart Economy cadence matching ghwatch.ps1 Cadence."""
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


def verify_manifest(manifest: dict, base_dir: Path) -> dict[str, str]:
    """Verify artifact manifest membership, disk existence, and digests.
    
    Enforces:
    1. All REQUIRED_ARTIFACTS must be declared in manifest
    2. All declared artifacts must exist on disk
    3. Digests must match exactly
    """
    artifacts = manifest.get("artifacts", {})
    
    # 1. Coverage: check all required artifacts are present in manifest
    missing_required = REQUIRED_ARTIFACTS - set(artifacts.keys())
    if missing_required:
        raise ValidationError(f"Manifest missing required artifact declarations: {sorted(missing_required)}")

    # 2. Existence and digest matching
    actual_hashes = {}
    for fname, expected_hash in artifacts.items():
        fpath = base_dir / fname
        if not fpath.exists():
            raise ValidationError(f"Declared manifest artifact not found on disk: {fname}")
        actual_hash = compute_sha256(fpath)
        if actual_hash != expected_hash:
            raise ValidationError(f"Digest mismatch on {fname}: expected {expected_hash}, got {actual_hash}")
        actual_hashes[fname] = actual_hash

    return actual_hashes


def test_manifest_enforcement(manifest: dict, base_dir: Path) -> dict[str, str]:
    """Test adversarial manifest failure modes: omission, nonexistent artifact, and corruption."""
    tests = {}

    # Test 1: Removing required artifact (e.g. source_contract.schema.json) MUST FAIL
    tampered_manifest_1 = copy.deepcopy(manifest)
    tampered_manifest_1["artifacts"].pop("source_contract.schema.json", None)
    try:
        verify_manifest(tampered_manifest_1, base_dir)
        tests["missing_required_in_manifest"] = "FAIL: accepted manifest lacking source_contract.schema.json"
    except ValidationError:
        tests["missing_required_in_manifest"] = "PASS"

    # Test 2: Declaring nonexistent artifact (missing-evidence.json) MUST FAIL
    tampered_manifest_2 = copy.deepcopy(manifest)
    tampered_manifest_2["artifacts"]["missing-evidence.json"] = "0" * 64
    try:
        verify_manifest(tampered_manifest_2, base_dir)
        tests["declared_nonexistent_artifact"] = "FAIL: accepted missing-evidence.json"
    except ValidationError:
        tests["declared_nonexistent_artifact"] = "PASS"

    # Test 3: Corrupted digest MUST FAIL
    tampered_manifest_3 = copy.deepcopy(manifest)
    tampered_manifest_3["artifacts"]["SOURCE_CONTRACT.md"] = "f" * 64
    try:
        verify_manifest(tampered_manifest_3, base_dir)
        tests["corrupted_digest"] = "FAIL: accepted corrupt digest"
    except ValidationError:
        tests["corrupted_digest"] = "PASS"

    return tests


def read_installed_coordinator_sources() -> dict[str, str]:
    """Read and hash installed coordinator scripts if present on local host."""
    scripts_dir = Path(r"C:\Users\reall\.claude\skills\coordinator-protocol\scripts")
    expected_scripts = ["watch.ps1", "cyclestate.ps1", "state-io.ps1", "aim-lib.ps1", "ghwatch.ps1"]
    out = {}
    for s in expected_scripts:
        p = scripts_dir / s
        if p.exists():
            out[s] = hashlib.sha256(p.read_bytes()).hexdigest()
        else:
            out[s] = "NOT_FOUND_ON_HOST"
    return out


def run():
    schema_path = ROOT / "source_contract.schema.json"
    pos_path = ROOT / "coordinator_state_v330_positive.json"
    neg_path = ROOT / "coordinator_state_v330_negative.json"
    contract_path = ROOT / "SOURCE_CONTRACT.md"
    manifest_path = ROOT / "expected_digests.json"

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    pos_data = json.loads(pos_path.read_text(encoding="utf-8"))
    neg_data = json.loads(neg_path.read_text(encoding="utf-8"))

    results = {}

    # 1. Positive and Negative Schema Validation
    try:
        validate_schema(pos_data, schema)
        results["POSITIVE_FIXTURE_SCHEMA_MATCH"] = "PASS"
    except Exception as e:
        results["POSITIVE_FIXTURE_SCHEMA_MATCH"] = f"FAIL: {e}"

    try:
        validate_schema(neg_data, schema)
        results["NEGATIVE_FIXTURE_SCHEMA_MATCH"] = "PASS"
    except Exception as e:
        results["NEGATIVE_FIXTURE_SCHEMA_MATCH"] = f"FAIL: {e}"

    # 2. Discriminating Integer Test and Adversarial Mutations
    mut_results = test_adversarial_mutations(pos_data, schema)
    if all(v == "PASS" for v in mut_results.values()):
        results["ADVERSARIAL_MUTATION_REJECTIONS"] = "PASS"
    else:
        results["ADVERSARIAL_MUTATION_REJECTIONS"] = f"FAIL: {mut_results}"

    # 3. Exact Literal 10-Cell Equality (Ground-truth derivation)
    try:
        derived_rows = derive_ten_cells(pos_data)
        assert derived_rows == EXPECTED_POSITIVE_ROWS, (
            f"Row mismatch: derived={derived_rows} != expected={EXPECTED_POSITIVE_ROWS}"
        )
        results["TEN_CELL_LITERAL_VALUE_PARITY"] = "PASS"
    except Exception as e:
        results["TEN_CELL_LITERAL_VALUE_PARITY"] = f"FAIL: {e}"

    # 4. Smart Economy Cadence Derivation
    try:
        cadence_pos = test_cadence_evaluation(pos_data)
        assert cadence_pos == 30, f"Expected 30m unsettled, got {cadence_pos}"

        settled_data = copy.deepcopy(pos_data)
        settled_data["claude_code_gh_relay_Session_Synth"]["Synth-Work-2"]["laDone"] = "2026-10-13T12:05:00Z"
        settled_data["claude_code_hw_e5f6a7b8"]["fHv"] = None
        settled_data["claude_code_hw_e5f6a7b8"]["aLane"] = "retired"
        cadence_settled = test_cadence_evaluation(settled_data)
        assert cadence_settled == 60, f"Expected 60m budget guard, got {cadence_settled}"

        results["SMART_ECONOMY_CADENCE_EVALUATION"] = "PASS"
    except Exception as e:
        results["SMART_ECONOMY_CADENCE_EVALUATION"] = f"FAIL: {e}"

    # 5. Manifest Membership, Coverage, and Adversarial Tamper Rejection
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        actual_hashes = verify_manifest(manifest, ROOT)
        results["ARTIFACT_MANIFEST_VERIFICATION"] = "PASS"

        manifest_tests = test_manifest_enforcement(manifest, ROOT)
        if all(v == "PASS" for v in manifest_tests.values()):
            results["TAMPER_DETECTION_VERIFICATION"] = "PASS"
        else:
            results["TAMPER_DETECTION_VERIFICATION"] = f"FAIL: {manifest_tests}"
    except Exception as e:
        results["ARTIFACT_MANIFEST_VERIFICATION"] = f"FAIL: {e}"
        results["TAMPER_DETECTION_VERIFICATION"] = f"FAIL: {e}"
        actual_hashes = {}
        manifest_tests = {}

    # 6. Local Source Identity and Truthful Live Parity Status
    installed_sources = read_installed_coordinator_sources()
    results["LIVE_INSTALLED_SOURCE_PARITY"] = "NOT_RUN"

    report = {
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fixture_version": "3.30.0-gate1-r4-evidence",
        "results": results,
        "mutation_details": mut_results,
        "manifest_enforcement_details": manifest_tests,
        "actual_hashes": actual_hashes,
        "installed_coordinator_sources": installed_sources,
        "source_identity_status": "LOCAL_INSTALLED_SOURCES_READ_AND_HASHED",
        "live_source_parity_not_run_reason": (
            "Installed script watch.ps1 evaluates time-dependent fields (meter, idle, checked, due) "
            "against live unmocked host clock [datetime]::Now via TotalMinutes, and expects compressed "
            "single-line JSON formatting. Per governance rules, live host script mutation or host clock "
            "manipulation is prohibited. Live source parity is truthfully marked NOT_RUN."
        ),
        "ci_status": "FOCUSED_GATE1_EVIDENCE_VALIDATION_ONLY",
    }
    print(json.dumps(report, indent=2))
    passed = all(v == "PASS" for k, v in results.items() if k != "LIVE_INSTALLED_SOURCE_PARITY")
    return passed


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
