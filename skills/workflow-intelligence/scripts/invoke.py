#!/usr/bin/env python3
"""One-invocation monitoring toggle: OFF by default; ON does one read-only scan.

No scheduler, changes to GitHub, SMTP, persistent config, or notifications.
Software MCDA always works independently of the monitoring setting.
"""
import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "workflow-intelligence.invocation/v1"
ROOT = Path(__file__).resolve().parents[2]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError("Required skill module unavailable: " + name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_invocation(monitor="off", *, workflow_config=None, workflow_id=None,
                   decision=None, read_comments=None, stamp=None):
    """Pure orchestration except explicit ON reads; provider dependency injectable.

    OFF intentionally does not open workflow_config or call read_comments.
    Enabling scheduled monitoring is a completely different, repository-level
    operation and cannot be triggered by this toggle.
    """
    if monitor not in ("off", "on"):
        raise ValueError("Monitoring must be on or off")
    if workflow_id is not None and (not isinstance(workflow_id, str) or not workflow_id):
        raise ValueError("Invalid workflow ID")
    output = {"schema": SCHEMA, "monitoring": {"mode": monitor, "scope": "this_invocation_only",
                                                "scheduled_monitoring_changed": False},
              "mcda": None}
    if monitor == "on":
        if workflow_config is None or not workflow_id:
            raise ValueError("ON requires an explicit approved workflow config and workflow ID")
        # Only import and inspect the monitor on the explicit ON path.
        module = load_module("universal_workflow_progress_check",
                             ROOT / "universal-workflow-progress" / "scripts" / "check.py")
        if not isinstance(workflow_config, dict):
            raise ValueError("Workflow config must be a parsed JSON object")
        module.validate(workflow_config)
        selected = [wf for wf in workflow_config["workflows"] if wf["id"] == workflow_id]
        if len(selected) != 1:
            raise ValueError("Selected workflow is not present in configuration")
        wf = selected[0]
        if not wf["enabled"]:
            raise ValueError("Selected workflow is disabled; do not bypass its enablement policy")
        if wf["repository"] == "owner/repo":
            raise ValueError("Placeholder sample repository cannot be monitored")
        # These fields are configured requirements, not proof that the Owner has
        # approved a stage or rating. Monitor output is always unverified.
        for stage in wf["stages"]:
            if not stage["trusted_authors"]:
                raise ValueError("Live stage requires a trusted-author allowlist")
        token = os.getenv("WF_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN", "")
        provider = read_comments or module.read_comments
        observed_at = stamp or datetime.now(timezone.utc).isoformat(timespec="seconds")
        records = provider(wf["repository"], wf["issue"], token)
        if not isinstance(records, list):
            raise ValueError("GitHub comments source returned an invalid response")
        observation = module.snapshot(wf, records, observed_at)
        output["monitoring"].update({
            "status": "OBSERVED_UNVERIFIED",
            "source": "user-selected GitHub issue comments",
            "observed_at": observed_at,
            "authority": "COMMENT_OBSERVATION_ONLY_NOT_VERIFIED",
            "snapshot": {"schema": module.SCHEMA, "observed_at": observed_at,
                         "workflows": [observation]}
        })
    else:
        output["monitoring"].update({"status": "SKIPPED", "source": None,
                                      "reason": "Explicitly off (default): no GitHub requests"})
    if decision is not None:
        engine = load_module("software_mcda_invocation",
                             ROOT / "software-mcda" / "scripts" / "mcda.py")
        calculated = engine.report(decision)
        # An independently verified evidence-to-score path is not implemented.
        # All calculations are advisory and have zero authority to act.
        output["mcda"] = {"authority": "ADVISORY_ONLY", "notification_eligible": False,
                          "result": calculated}
    return output


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--monitor", choices=("off", "on"), default="off",
                   help="One-invocation switch. Defaults off; on reads one configured GitHub issue.")
    p.add_argument("--workflow-config", type=Path)
    p.add_argument("--workflow-id")
    p.add_argument("--decision", type=Path, help="Optional standalone MCDA input")
    p.add_argument("--output", type=Path, help="Optional local JSON output; stdout otherwise")
    args = p.parse_args()
    try:
        # Crucial: OFF must not even read the workflow config.
        config = (json.loads(args.workflow_config.read_text(encoding="utf-8"))
                  if args.monitor == "on" and args.workflow_config else None)
        decision = (json.loads(args.decision.read_text(encoding="utf-8"))
                    if args.decision else None)
        result = run_invocation(args.monitor, workflow_config=config,
                                workflow_id=args.workflow_id, decision=decision)
        encoded = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(encoded, encoding="utf-8")
        else:
            sys.stdout.write(encoded)
    except (OSError, TypeError, ValueError, KeyError) as exc:
        p.exit(2, "INVOCATION_FAILED: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
