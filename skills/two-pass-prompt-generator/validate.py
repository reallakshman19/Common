#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

EXPECTED_PROTOCOL_REVISION = "TPG-2P-2026-09-28-R3"
PASS1 = "## PASS 1 — INDEPENDENT SYSTEM BASELINE"
PASS2 = "## PASS 2 — IMPROVE, RECONCILE, PLAN"


def validate(text: str) -> list[str]:
    errors: list[str] = []
    if not text.startswith("# SCHEMA EXECUTION HANDSHAKE"):
        errors.append("artifact must begin with schema execution handshake")
    if EXPECTED_PROTOCOL_REVISION not in text:
        errors.append("protocol revision missing/mismatched")
    if "GENERATOR MODE:\nTWO_PASS_ONLY" not in text:
        errors.append("generator mode must be TWO_PASS_ONLY")
    if text.count(PASS1) != 1 or text.count(PASS2) != 1:
        errors.append("artifact must contain exactly one Pass 1 and one Pass 2")
        return errors
    for legacy in (
        "## PROMPT 0.5",
        "## PROMPT 1",
        "## PROMPT 2",
        "## PROMPT 2.5",
        "## PROMPT 3",
        "THREE_PASS_ONLY",
    ):
        if legacy in text:
            errors.append(f"legacy three-pass surface is invalid: {legacy}")
    p1 = text.split(PASS1, 1)[1].split(PASS2, 1)[0]
    for pattern in (
        r"https://github\.com/[^\s)]+/(?:issues|pull)/\d+",
        r"(?i)\bPR\s*#\d+",
        r"(?i)\bIssue\s*#\d+",
        r"(?i)ORIGINAL INTENT",
        r"(?i)CONVERSATION_RECORD",
        r"(?i)AGENT_STATUS_V1",
        r"(?i)\bFURTHER TASK\b",
        r"(?i)\bOFFLOAD\b",
        r"(?i)RLL_(?:EXECUTION|WORKER_STATE)",
        r"(?i)IMPROVEMENT PROPOSAL",
        r"(?i)IMPLEMENTATION_PLAN",
        r"(?i)APPROVAL REQUIRED",
    ):
        if re.search(pattern, p1):
            errors.append(f"Pass 1 leaks task/action material: {pattern}")
    p2 = text.split(PASS2, 1)[1]
    for token in (
        "STEP-BACK RECONCILIATION",
        "Original Intent",
        "Roadmap",
        "AGENT_STATUS_V1",
        "Further task",
        "LOCAL_AGENT_FINDING",
        "RLL_TRANSPORT_ONLY",
        "IMPROVEMENT PROPOSAL",
        "QUANTITATIVE",
        "FALSIFIER",
        "SCOPE RELATION",
        "DRAFT IMPLEMENTATION_PLAN",
        "APPROVAL REQUIRED",
        "EP",
        "Task Snapshot",
        "Handover",
    ):
        if token.lower() not in p2.lower():
            errors.append(f"Pass 2 missing required concept: {token}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate two-pass prompt-generator output.")
    parser.add_argument("artifact")
    args = parser.parse_args()
    errors = validate(Path(args.artifact).read_text(encoding="utf-8"))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("PASS")


if __name__ == "__main__":
    main()
