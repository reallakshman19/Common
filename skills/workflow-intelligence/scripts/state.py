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


def decision_key(scope):
    """Logical decision key; assessed SHA is part of its changing contents."""
    required = ("repository", "workflow_id", "issue", "decision_id")
    if not isinstance(scope, dict) or any(key not in scope for key in required):
        raise ValueError("Missing decision scope")
    values = [scope[key] for key in required]
    if (any(not isinstance(v, str) or not v for v in (values[0], values[1], values[3]))
            or type(values[2]) is not int or values[2] < 1):
        raise ValueError("Invalid decision scope")
    return json.dumps(values, separators=(",", ":"), ensure_ascii=False)


def canonical_assessment(record):
    """Accept only known non-notifying decision-gate output, never caller authority claims."""
    if not isinstance(record, dict) or record.get("schema") != "workflow-intelligence.assessment/v1":
        raise ValueError("Invalid assessment schema")
    if record.get("notification_eligible") is not False:
        raise ValueError("Cannot persist an assessment as alert-eligible")
    if record.get("authority") != "SELF_DECLARED_INPUTS_NOT_INDEPENDENTLY_VERIFIED":
        raise ValueError("Unsupported assessment authority")
    status = record.get("status")
    if status not in {"NOT_EVALUATED", "ADVISORY_REVIEW_REQUIRED"}:
        raise ValueError("Unsupported decision assessment status")
    scope = record.get("scope")
    key = decision_key(scope)
    sha = scope.get("assessed_sha")
    if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("Invalid decision candidate SHA")
    result = {"scope": {k: scope[k] for k in ("repository", "workflow_id", "issue",
                                              "decision_id", "assessed_sha")},
              "status": status, "reason": record.get("reason")}
    if not isinstance(result["reason"], str):
        raise ValueError("Decision assessment reason missing")
    if status == "ADVISORY_REVIEW_REQUIRED":
        mcda = record.get("mcda")
        digest = record.get("configuration_digest")
        if not isinstance(mcda, dict) or mcda.get("schema") != "software-mcda.result/v1":
            raise ValueError("Advisory result missing MCDA calculation")
        if not isinstance(digest, str) or not digest.startswith("sha256:"):
            raise ValueError("Advisory result missing configuration digest")
        original = mcda.get("original")
        if not isinstance(original, dict) or not isinstance(original.get("ranking"), list):
            raise ValueError("Advisory result missing ranked options")
        result["configuration_digest"] = digest
        result["winner"] = original.get("winner")
        result["ranking"] = original["ranking"]
    return key, result


def _valid_prior_decisions(previous_state):
    raw = previous_state.get("decisions", {})
    if not isinstance(raw, dict):
        raise ValueError("Invalid prior decision-state mapping")
    for key, record in raw.items():
        if not isinstance(record, dict) or not isinstance(record.get("summary"), dict):
            raise ValueError("Malformed prior decision")
        summary = record["summary"]
        if fingerprint(summary) != record.get("semantic_sha256"):
            raise ValueError("Prior decision-state digest mismatch")
        if key != decision_key(summary.get("scope")):
            raise ValueError("Prior decision namespace mismatch")
        if (summary.get("status") not in {"NOT_EVALUATED", "ADVISORY_REVIEW_REQUIRED"}
                or summary.get("scope", {}).get("assessed_sha") is None):
            raise ValueError("Unsupported prior decision state")
    return raw


def advance(current_snapshot, previous_state=None, assessment_record=None):
    """Return next durable state and strictly non-notifying diagnostic events."""
    current = canonical_entries(current_snapshot)
    previous = validated_prior(previous_state) if previous_state is not None else None
    before_decisions = _valid_prior_decisions(previous_state) if previous_state is not None else {}
    after_decisions = dict(before_decisions)
    next_state = {"schema": STATE_SCHEMA, "entries": current, "decisions": after_decisions}
    events = []
    if previous is not None:
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
    if assessment_record is not None:
        key, summary = canonical_assessment(assessment_record)
        digest = fingerprint(summary)
        before = before_decisions.get(key)
        after_decisions[key] = {"semantic_sha256": digest, "summary": summary}
        if previous_state is not None and (before is None or before["semantic_sha256"] != digest):
            previous_winner = (before["summary"].get("winner") if before else None)
            current_winner = summary.get("winner")
            kind = ("ADVISORY_RECOMMENDATION_CHANGED" if before and
                    previous_winner != current_winner else "DECISION_INPUT_CHANGED")
            event = {"namespace": json.loads(key), "kind": kind,
                     "previous_digest": before["semantic_sha256"] if before else None,
                     "current_digest": digest,
                     "previous_recommendation": previous_winner,
                     "current_recommendation": current_winner}
            events.append({"schema": "workflow-intelligence.decision-event/v1",
                           "event_id": "sha256:" + fingerprint(event),
                           **event, "authority": "SELF_DECLARED_INPUTS_NOT_INDEPENDENTLY_VERIFIED",
                           "alert_eligible": False, "mcda_eligible": False})
    return next_state, events


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
    p.add_argument("--assessment", type=Path)
    p.add_argument("--state-output", required=True, type=Path)
    p.add_argument("--events-output", required=True, type=Path)
    args = p.parse_args()
    if args.state_output.resolve() == args.events_output.resolve():
        p.error("State/event paths must differ")
    try:
        now = json.loads(args.current.read_text(encoding="utf-8"))
        old = json.loads(args.previous_state.read_text(encoding="utf-8")) if args.previous_state else None
        assessed = json.loads(args.assessment.read_text(encoding="utf-8")) if args.assessment else None
        nxt, events = advance(now, old, assessed)
        atomic_json(args.state_output, nxt)
        atomic_json(args.events_output, {"schema": "workflow-intelligence.events/v1", "events": events})
        print(f"Read-only semantic changes: {len(events)}; alerts sent: 0")
    except (OSError, ValueError, TypeError) as exc:
        p.exit(2, f"STATE_FAILED: {exc}\n")


if __name__ == "__main__":
    main()
