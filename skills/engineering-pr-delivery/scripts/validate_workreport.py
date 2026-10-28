#!/usr/bin/env python3
from pathlib import Path
import re, sys

REQUIRED_HEADINGS = [
    "CURRENT RECOVERY STATE",
    "Handover in 60 Seconds",
    "Repository Ground Truth",
    "Mission / Scope / Acceptance",
    "Current Implementation State",
    "Active Engineering Item Register",
    "Authority and Invariants",
    "Current Validation",
    "Changed-File Ledger",
    "Continuation State",
    "APPENDIX A",
]

REQUIRED_FIELDS = [
    "HANDOVER_READINESS:",
    "PR_RECOVERY_STATE:",
    "TAKEOVER_AUTHORITY:",
    "EXECUTION_MODE:",
    "PHASE_PROGRESSION:",
    "MERGE_AUTHORITY:",
    "REPORT_BASIS_HEAD:",
    "MAIN_HEAD_LAST_CHECKED:",
    "REPORT_SYNC:",
    "APPENDIX_A_STATUS:",
    "GROUNDING_EPOCH:",
    "EXACT_NEXT_ACTION:",
]

AUTO_FIELDS = [
    "AUTO_STATE:",
    "SCOPE_AUTHORITY:",
]

VALID_AUTO_STATES = {
    "RUNNING",
    "VALIDATING",
    "RECOVERING",
    "BLOCKED",
    "OWNER_DECISION_REQUIRED",
    "TAKEOVER_REQUIRED",
    "COMPLETE",
}


def field_value(text, name):
    match = re.search(rf"(?m)^\s*{re.escape(name)}\s*:\s*([^\n#]+)", text)
    return match.group(1).strip() if match else None


def main():
    if len(sys.argv) != 2:
        print("Usage: validate_workreport.py <workreport.md>", file=sys.stderr)
        return 2
    p = Path(sys.argv[1])
    text = p.read_text(encoding="utf-8")
    errors = []
    for h in REQUIRED_HEADINGS:
        if h.lower() not in text.lower():
            errors.append(f"missing heading/section: {h}")
    for f in REQUIRED_FIELDS:
        if f not in text:
            errors.append(f"missing recovery field: {f}")

    execution_mode = field_value(text, "EXECUTION_MODE")
    if execution_mode and execution_mode not in {"MANUAL", "AUTO"}:
        errors.append(f"invalid EXECUTION_MODE: {execution_mode}")

    if execution_mode == "AUTO":
        for f in AUTO_FIELDS:
            if f not in text:
                errors.append(f"AUTO mode missing field: {f}")
        auto_state = field_value(text, "AUTO_STATE")
        if auto_state and auto_state not in VALID_AUTO_STATES:
            errors.append(f"invalid AUTO_STATE: {auto_state}")
        if field_value(text, "PHASE_PROGRESSION") != "AUTO":
            errors.append("AUTO mode requires PHASE_PROGRESSION: AUTO")
        scope = field_value(text, "SCOPE_AUTHORITY")
        if scope and scope not in {"LOCKED_TO_APPROVED_MISSION", "OWNER_EXPANDED"}:
            errors.append(f"invalid SCOPE_AUTHORITY: {scope}")
        merge = field_value(text, "MERGE_AUTHORITY")
        if merge and merge not in {"OWNER_ONLY", "AUTO_AFTER_EXPLICIT_AUTHORIZATION"}:
            errors.append(f"invalid MERGE_AUTHORITY: {merge}")

    if "HANDOVER_READINESS: READY" in text:
        if "REPORT_SYNC: CURRENT" not in text:
            errors.append("READY requires REPORT_SYNC: CURRENT")
        if "APPENDIX_A_STATUS: STALE" in text:
            errors.append("READY cannot have stale Appendix A")
    if re.search(r"\bPR_PENDING_workreport\.md\b", text):
        errors.append("single shared PR_PENDING_workreport.md is forbidden; use unique WIP ID")
    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1
    print("PASS: work report structural recovery gate")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
