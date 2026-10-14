#!/usr/bin/env python3
"""Pure intent router for workflow requests; never observes, dispatches or writes."""
from __future__ import annotations

import argparse
import json


def route(intent: str, workflow: str, monitor: str = "OFF") -> dict:
    """Return a routing decision, never an execution receipt."""
    if intent not in ("progress", "start", "unclear"):
        raise ValueError("intent must be progress/start/unclear")
    if monitor not in ("OFF", "ON"):
        raise ValueError("monitor must be OFF or ON")
    if not isinstance(workflow, str):
        raise ValueError("workflow must be text")
    name = workflow.strip()
    result = {
        "schema": "workflow-invocation-route/v1",
        "intent": intent,
        "workflow": name or "UNKNOWN",
        "source_checked": False,
        "agent_invoked": False,
        "workflow_executed": False,
        "approval_granted": False,
        "repository_mutated": False,
    }
    if intent == "unclear":
        return {**result, "route": "CLARIFY_INTENT", "next_action": "ASK_SHOW_PROGRESS_OR_START"}
    if not name:
        return {**result, "route": "REQUIRE_TARGET", "next_action": "ASK_WORKFLOW_AND_ISSUE"}
    if intent == "progress":
        return {
            **result, "route": "UNIVERSAL_WORKFLOW_PROGRESS",
            "monitor": monitor,
            "state": "READ_ONLY_OBSERVATION_REQUESTED" if monitor == "ON" else "NOT_LIVE",
            "next_action": "VERIFY_MAPPING_THEN_READ_ONCE" if monitor == "ON"
            else "DISPLAY_SUPPLIED_OR_CACHED_EVIDENCE_ONLY",
        }
    if name == "buddy-runner-v1-7":
        return {
            **result, "route": "GOVERNING_BUDDY_RUNNER_V17",
            "state": "PREPARATION_REQUIRED",
            "next_action": "VALIDATE_REAL_CASE_THEN_RENDER_1A_WITH_STATUS_JSON",
            "command": ("python skills/buddy-runner-v1-7/scripts/buddy_runner_v17.py "
                        "--input case.json --output handover-1a.md --status-json"),
        }
    return {
        **result, "route": "GOVERNING_EXECUTOR_REQUIRED",
        "state": "NOT_STARTED",
        "next_action": "RESOLVE_WORKFLOW_CONTRACT_AND_AUTHORIZED_EXECUTOR",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intent", choices=("progress", "start", "unclear"), required=True)
    parser.add_argument("--workflow", default="")
    parser.add_argument("--monitor", choices=("OFF", "ON"), default="OFF")
    args = parser.parse_args(argv)
    print(json.dumps(route(args.intent, args.workflow, args.monitor), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
