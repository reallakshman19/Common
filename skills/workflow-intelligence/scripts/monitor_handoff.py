#!/usr/bin/env python3
"""Single-artifact, diagnostic-only handoff for draft Progress Monitor PR #364.

Consumes the monitor's workflow-progress-monitor/v1 latest.json directly.
One self-contained atomic artifact carries next state and current diagnostic
events. It neither schedules checks nor delivers alerts. Explicit bootstrap
prevents accidentally treating missing retention/artifacts as a new baseline.
"""
import argparse
import json
from pathlib import Path

from observe import fingerprint
from state import advance, atomic_json, canonical_entries

SCHEMA = "workflow-intelligence.handoff/v1"
MONITOR_SCHEMA = "workflow-progress-monitor/v1"


def read_prior(bundle):
    if not isinstance(bundle, dict) or set(bundle) != {
            "schema", "mode", "source_schema", "source_digest",
            "state", "state_digest", "previous_state_digest", "events"}:
        raise ValueError("Prior artifact fields missing or incompatible")
    if (bundle["schema"] != SCHEMA or bundle["mode"] != "DIAGNOSTIC_ONLY"
            or bundle["source_schema"] != MONITOR_SCHEMA):
        raise ValueError("Prior artifact schema or mode unsupported")
    if (not isinstance(bundle["state"], dict) or
            bundle["state_digest"] != "sha256:" + fingerprint(bundle["state"])):
        raise ValueError("Prior artifact state digest mismatch")
    if not isinstance(bundle["events"], list):
        raise ValueError("Prior artifact events invalid")
    for event in bundle["events"]:
        if (not isinstance(event, dict) or event.get("alert_eligible") is not False
                or event.get("mcda_eligible") is not False or
                not isinstance(event.get("event_id"), str)):
            raise ValueError("Prior artifact contains unsupported/actionable event")
    return bundle["state"]


def reconcile(monitor_snapshot, *, previous_bundle=None, bootstrap=False,
              assessment=None):
    if type(bootstrap) is not bool or (previous_bundle is None) == (not bootstrap):
        raise ValueError("Choose exactly one of intentional bootstrap or prior artifact")
    if not isinstance(monitor_snapshot, dict) or monitor_snapshot.get("schema") != MONITOR_SCHEMA:
        raise ValueError("Unsupported monitor snapshot")
    source_digest = "sha256:" + fingerprint(canonical_entries(monitor_snapshot))
    prior_state = read_prior(previous_bundle) if previous_bundle is not None else None
    new_state, events = advance(monitor_snapshot, prior_state, assessment)
    if any(event.get("alert_eligible") is not False or
           event.get("mcda_eligible") is not False for event in events):
        raise ValueError("Actionable event not allowed in diagnostic handoff")
    return {"schema": SCHEMA, "mode": "DIAGNOSTIC_ONLY",
            "source_schema": MONITOR_SCHEMA, "source_digest": source_digest,
            "state": new_state, "state_digest": "sha256:" + fingerprint(new_state),
            "previous_state_digest": previous_bundle["state_digest"]
            if previous_bundle is not None else None,
            "events": events}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--monitor-current", required=True, type=Path)
    prior = parser.add_mutually_exclusive_group(required=True)
    prior.add_argument("--bootstrap", action="store_true",
                       help="Explicit one-time silent baseline; never use for ordinary retries")
    prior.add_argument("--previous-artifact", type=Path)
    parser.add_argument("--assessment", type=Path,
                        help="Optional unverified advisory assessment, never permission")
    parser.add_argument("--output-artifact", required=True, type=Path)
    args = parser.parse_args()
    try:
        source = json.loads(args.monitor_current.read_text(encoding="utf-8"))
        old = (json.loads(args.previous_artifact.read_text(encoding="utf-8"))
               if args.previous_artifact is not None else None)
        assessment = (json.loads(args.assessment.read_text(encoding="utf-8"))
                      if args.assessment is not None else None)
        output = reconcile(source, previous_bundle=old, bootstrap=args.bootstrap,
                           assessment=assessment)
        atomic_json(args.output_artifact, output)
        print("UWI read-only handoff: " + str(len(output["events"])) +
              " diagnostic event(s); 0 alerts; 0 GitHub writes")
    except (ValueError, TypeError, OSError) as exc:
        parser.exit(2, "HANDOFF_FAILED: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
