#!/usr/bin/env python3
"""Read-only semantic observation adapter for proposed monitor v1 snapshots."""
import argparse
import hashlib
import json
from pathlib import Path

INPUT_SCHEMA = "workflow-progress-monitor/v1"
OUTPUT_SCHEMA = "workflow-intelligence.event/v1"


def fingerprint(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                     allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def normalize(snapshot):
    if not isinstance(snapshot, dict) or snapshot.get("schema") != INPUT_SCHEMA:
        raise ValueError("Unsupported monitor schema")
    workflows = snapshot.get("workflows")
    if not isinstance(workflows, list):
        raise ValueError("workflows must be a list")
    result = {}
    for wf in workflows:
        if not isinstance(wf, dict):
            raise ValueError("Invalid workflow record")
        wid, repo, issue = wf.get("id"), wf.get("repository"), wf.get("issue")
        if not isinstance(wid, str) or not wid or not isinstance(repo, str) or "/" not in repo:
            raise ValueError("Invalid workflow identity")
        if type(issue) is not int or issue < 1:
            raise ValueError("Invalid owning issue")
        scope = (repo, wid, issue)
        if scope in result:
            raise ValueError("Duplicate workflow scope")
        stages = wf.get("stages")
        if not isinstance(stages, list):
            raise ValueError("Missing stages")
        canonical = []
        used = set()
        for stage in stages:
            if not isinstance(stage, dict) or not isinstance(stage.get("id"), str) or not stage["id"]:
                raise ValueError("Invalid stage")
            sid = stage["id"]
            if sid in used:
                raise ValueError("Duplicate stage")
            used.add(sid)
            state, verification = stage.get("state"), stage.get("verification")
            if (state, verification) not in {("UNKNOWN", "UNKNOWN"), ("SUBMITTED", "UNVERIFIED")}:
                raise ValueError("Unsupported state or prohibited verification upgrade")
            evidence = stage.get("evidence")
            if not isinstance(evidence, list):
                raise ValueError("Invalid evidence list")
            if state == "UNKNOWN" and evidence:
                raise ValueError("Unknown stage cannot contain matched evidence")
            if state == "SUBMITTED" and not evidence:
                raise ValueError("Submitted stage requires observed evidence")
            records = []
            seen = set()
            for item in evidence:
                if not isinstance(item, dict):
                    raise ValueError("Invalid evidence record")
                cid, digest = item.get("comment_id"), item.get("sha256")
                if type(cid) is not int or cid < 1 or not isinstance(digest, str) or len(digest) != 64:
                    raise ValueError("Invalid observation identity")
                if any(ch not in "0123456789abcdef" for ch in digest):
                    raise ValueError("Invalid SHA-256 digest")
                key = (cid, digest)
                if key in seen:
                    raise ValueError("Duplicate evidence identity")
                seen.add(key)
                records.append({"comment_id": cid, "sha256": digest})
            canonical.append({"stage": sid, "state": state, "verification": verification,
                              "evidence": sorted(records, key=lambda r: (r["comment_id"], r["sha256"]))})
        result[scope] = sorted(canonical, key=lambda s: s["stage"])
    return result


def changed_events(current, previous=None):
    curr = normalize(current)
    prev = normalize(previous) if previous is not None else None
    if prev is None:
        return []
    events = []
    for scope, stages in sorted(curr.items()):
        before = {s["stage"]: s for s in prev.get(scope, [])}
        for stage in stages:
            if before.get(stage["stage"]) == stage:
                continue
            repo, wid, issue = scope
            identity = {"repository": repo, "workflow_id": wid, "issue": issue, **stage}
            events.append({"schema": OUTPUT_SCHEMA, "event_id": "sha256:" + fingerprint(identity),
                           "source": {"repository": repo, "workflow_id": wid, "issue": issue},
                           "observation": stage, "authority": "UNVERIFIED_COMMENT_OBSERVATION",
                           "alert_eligible": False, "mcda_eligible": False})
    return events


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current", required=True, type=Path)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        current = json.loads(args.current.read_text(encoding="utf-8"))
        old = json.loads(args.previous.read_text(encoding="utf-8")) if args.previous else None
        events = changed_events(current, old)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({"schema": OUTPUT_SCHEMA, "events": events},
                                          indent=2) + "\n", encoding="utf-8")
        print(f"Observed {len(events)} change(s); no verification or alerts issued.")
    except (OSError, ValueError, TypeError) as error:
        parser.exit(2, f"OBSERVATION_FAILED: {error}\n")


if __name__ == "__main__":
    main()
