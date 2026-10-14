#!/usr/bin/env python3
"""Durable, read-only semantic-change state for proposed monitor v1.

No GitHub writes, SMTP or cron. Emits diagnostic change records that are
explicitly NOT eligible for alerts or MCDA scoring.
"""
import argparse
import json
import os
import tempfile
from pathlib import Path
from observe import fingerprint, normalize

STATE_SCHEMA = "workflow-intelligence.state/v1"
EVENT_SCHEMA = "workflow-intelligence.event/v1"


def scoped_key(repository, workflow, issue, stage):
    return json.dumps([repository, workflow, issue, stage],
                      separators=(",", ":"), ensure_ascii=False)


def canonical_entries(snapshot):
    canonical = normalize(snapshot)
    entries = {}
    for (repo, workflow, issue), stages in canonical.items():
        for stage in stages:
            key = scoped_key(repo, workflow, issue, stage["stage"])
            entries[key] = {"semantic_sha256": fingerprint(stage), "observation": stage}
    return dict(sorted(entries.items()))


def validated_prior(prior):
    if not isinstance(prior, dict) or prior.get("schema") != STATE_SCHEMA:
        raise ValueError("Missing/corrupt/unsupported prior state")
    entries = prior.get("entries")
    if not isinstance(entries, dict):
        raise ValueError("Prior state missing entries")
    for key, record in entries.items():
        if not isinstance(key, str) or not isinstance(record, dict):
            raise ValueError("Invalid previous-state entry")
        observation = record.get("observation")
        if not isinstance(observation, dict):
            raise ValueError("Invalid prior observation")
        if fingerprint(observation) != record.get("semantic_sha256"):
            raise ValueError("Prior-state semantic digest mismatch")
        try:
            identity = json.loads(key)
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid prior-state key") from exc
        if (not isinstance(identity, list) or len(identity) != 4 or
                any(not isinstance(v, str) or not v for v in (identity[0], identity[1], identity[3])) or
                type(identity[2]) is not int or identity[2] < 1 or
                observation.get("stage") != identity[3]):
            raise ValueError("Invalid prior-state identity")
        if (observation.get("state"), observation.get("verification")) not in {
            ("UNKNOWN", "UNKNOWN"), ("SUBMITTED", "UNVERIFIED")
        }:
            raise ValueError("Prior-state verification upgrade not allowed")
    return entries


def advance(current_snapshot, previous_state=None):
    """First poll is a silent baseline. Stale/corrupt supplied state fails closed."""
    current = canonical_entries(current_snapshot)
    previous = validated_prior(previous_state) if previous_state is not None else None
    new_state = {"schema": STATE_SCHEMA, "entries": current}
    if previous is None:
        return new_state, []
    events = []
    for key in sorted(set(previous) | set(current)):
        before, after = previous.get(key), current.get(key)
        if before == after:
            continue
        identity = json.loads(key)
        transition = {"namespace": identity,
                      "previous_digest": before["semantic_sha256"] if before else None,
                      "current_digest": after["semantic_sha256"] if after else None,
                      "kind": "OBSERVATION_REMOVED" if after is None else "OBSERVATION_CHANGED"}
        events.append({
            "schema": EVENT_SCHEMA, "event_id": "sha256:" + fingerprint(transition),
            **transition, "observation": after["observation"] if after else None,
            "authority": "UNVERIFIED_COMMENT_OBSERVATION",
            "alert_eligible": False, "mcda_eligible": False
        })
    return new_state, events


def atomic_json(path, payload):
    """Atomic per-file write. Separate state/event files are not transactional."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".uwi-", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--current", required=True, type=Path)
    p.add_argument("--previous-state", type=Path)
    p.add_argument("--state-output", required=True, type=Path)
    p.add_argument("--events-output", required=True, type=Path)
    args = p.parse_args()
    if args.state_output.resolve() == args.events_output.resolve():
        p.error("State/event paths must differ")
    try:
        now = json.loads(args.current.read_text(encoding="utf-8"))
        old = json.loads(args.previous_state.read_text(encoding="utf-8")) if args.previous_state else None
        nxt, events = advance(now, old)
        atomic_json(args.state_output, nxt)
        atomic_json(args.events_output, {"schema": EVENT_SCHEMA, "events": events})
        print(f"Read-only semantic changes: {len(events)}; alerts sent: 0")
    except (OSError, ValueError, TypeError) as exc:
        p.exit(2, f"STATE_FAILED: {exc}\n")


if __name__ == "__main__":
    main()
