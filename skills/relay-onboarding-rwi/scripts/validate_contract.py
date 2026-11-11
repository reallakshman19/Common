#!/usr/bin/env python3
"""Pure ONB-RWI WP1a contracts. No network, filesystem writes or authority escalation."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA = re.compile(r"^[0-9a-f]{40}$")
WORK = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$")
TARGET_KEYS = frozenset({"schema", "repository", "issue", "work_id", "mode",
                         "source_heads", "candidate_heads", "source_health", "owner_decision", "observed_at"})
EVIDENCE_KEYS = frozenset({"schema", "source_repository", "source_url", "assessed_sha",
                           "kind", "observation", "privacy"})
KINDS = frozenset({"SOURCE", "ISSUE", "PR", "CI", "TASK_EVIDENCE", "TEST",
                   "FIXTURE", "BENCHMARK", "OWNER_DECISION", "HANDOVER", "LOG"})
OBSERVATIONS = frozenset({"REPORTED", "PROVIDER_OBSERVED", "UNKNOWN"})
PRIVACY = frozenset({"PUBLIC", "PRIVATE", "RESTRICTED"})
HEALTH = frozenset({"COMPLETE", "PARTIAL", "UNAVAILABLE", "UNKNOWN"})
OWNER = frozenset({"PRESENT", "UNKNOWN", "CONFLICT"})


class ContractError(ValueError):
    """Malformed or insufficiently scoped claim."""


def require_keys(obj: object, keys: frozenset[str], label: str) -> dict:
    if not isinstance(obj, dict) or set(obj) != keys:
        raise ContractError(f"{label}: expected exactly {','.join(sorted(keys))}")
    return obj


def github_repo(url: object) -> str:
    if not isinstance(url, str):
        raise ContractError("GitHub URL must be text")
    v = urlsplit(url)
    if (v.scheme != "https" or v.netloc != "github.com" or v.username or v.password
            or v.query or v.fragment):
        raise ContractError("GitHub URL must be unambiguous HTTPS github.com without credentials/query/fragment")
    segments = v.path.strip("/").split("/")
    if len(segments) < 3 or not REPO.fullmatch("/".join(segments[:2])):
        raise ContractError("GitHub URL must identify a repo and resource")
    return "/".join(segments[:2])


def validate_target(value: object) -> dict:
    o = require_keys(value, TARGET_KEYS, "target")
    if o["schema"] != "onboarding.target/v1":
        raise ContractError("unsupported target schema")
    if not isinstance(o["repository"], str) or not REPO.fullmatch(o["repository"]):
        raise ContractError("invalid target repository")
    if type(o["issue"]) is not int or o["issue"] < 1:
        raise ContractError("invalid issue number")
    if not isinstance(o["work_id"], str) or not WORK.fullmatch(o["work_id"]):
        raise ContractError("invalid work identity")
    if o["mode"] != "READ_ONLY":
        raise ContractError("target cannot request execution")
    heads = o["source_heads"]
    if (not isinstance(heads, dict) or not heads or o["repository"] not in heads
            or any(not isinstance(r, str) or not REPO.fullmatch(r)
                   or not isinstance(h, str) or not SHA.fullmatch(h)
                   for r, h in heads.items())):
        raise ContractError("missing/invalid exact source head or target repo")
    candidates = o["candidate_heads"]
    if not isinstance(candidates, dict):
        raise ContractError("candidate_heads must be explicitly mapped")
    for url, head in candidates.items():
        if (not isinstance(url, str) or github_repo(url) not in heads
                or not isinstance(head, str) or not SHA.fullmatch(head)):
            raise ContractError("invalid or foreign candidate PR head")
        from urllib.parse import urlsplit as _split
        segments = _split(url).path.strip("/").split("/")
        if len(segments) != 4 or segments[2] != "pull" or not segments[3].isdigit() or int(segments[3]) < 1:
            raise ContractError("candidate_head must be a numbered GitHub PR URL")
    if o["source_health"] not in HEALTH:
        raise ContractError("unknown source health")
    decision = require_keys(o["owner_decision"], frozenset({"status", "ref"}), "owner decision")
    if decision["status"] not in OWNER:
        raise ContractError("invalid Owner decision status")
    if decision["status"] == "PRESENT":
        if github_repo(decision["ref"]) not in heads:
            raise ContractError("Owner source is outside declared repository scope")
    elif decision["ref"] is not None:
        raise ContractError("unknown/conflicting Owner decision cannot assert a reference")
    when = o["observed_at"]
    if not isinstance(when, str):
        raise ContractError("missing observed_at timestamp")
    try:
        parsed = dt.datetime.fromisoformat(when.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError("invalid observed_at timestamp") from exc
    if parsed.utcoffset() is None:
        raise ContractError("observed_at must have timezone")
    return o


def validate_evidence(value: object, target: dict) -> dict:
    e = require_keys(value, EVIDENCE_KEYS, "evidence")
    if e["schema"] != "onboarding.evidence/v1":
        raise ContractError("unsupported evidence schema")
    if (not isinstance(e["source_repository"], str)
            or e["source_repository"] not in target["source_heads"]):
        raise ContractError("WRONG_SCOPE: evidence repository not explicitly allowed")
    if github_repo(e["source_url"]) != e["source_repository"]:
        raise ContractError("WRONG_SCOPE: link repository mismatch")
    if not isinstance(e["assessed_sha"], str) or not SHA.fullmatch(e["assessed_sha"]):
        raise ContractError("invalid assessed SHA")
    if e["kind"] not in KINDS or e["observation"] not in OBSERVATIONS or e["privacy"] not in PRIVACY:
        raise ContractError("invalid evidence kind/observation/privacy")
    if e["kind"] == "PR" and e["source_url"] not in target["candidate_heads"]:
        raise ContractError("WRONG_SCOPE: PR evidence must bind an explicitly selected candidate")
    return e


def verdict(status: str, reasons: list[str], next_action: str, target: dict | None,
            n: int) -> dict:
    return {"schema": "onboarding.local-assessment/v1", "status": status,
            "reason_codes": sorted(set(reasons)), "next_action": next_action,
            "execution_authorized": False, "source_basis": target["source_heads"] if target else {},
            "evidence_count": n, "refreshed_live": False,
            "candidate_heads": target["candidate_heads"] if target else {}}


def assess(target: object, evidence: object) -> dict:
    """No local input, including PROVIDER_OBSERVED, can certify live facts/permission."""
    try:
        t = validate_target(target)
    except (ContractError, TypeError, ValueError) as exc:
        return verdict("BLOCKED", ["TARGET_INVALID"], "Correct target and independently verify authority: " + str(exc), None, 0)
    if not isinstance(evidence, list):
        return verdict("BLOCKED", ["EVIDENCE_INVALID"], "Supply evidence JSON array", t, 0)
    seen: set[tuple[str, str, str, str]] = set()
    for idx, raw in enumerate(evidence):
        try:
            e = validate_evidence(raw, t)
        except (ContractError, TypeError, ValueError) as exc:
            reason = "WRONG_SCOPE" if "WRONG_SCOPE" in str(exc) else "EVIDENCE_INVALID"
            return verdict("BLOCKED", [reason], f"Repair source pointer at index {idx}: {exc}", t, len(evidence))
        identity = (e["source_repository"], e["source_url"], e["assessed_sha"], e["kind"])
        if identity in seen:
            return verdict("BLOCKED", ["DUPLICATE_EVIDENCE"], "Deduplicate exact source pointer", t, len(evidence))
        seen.add(identity)
        if e["kind"] == "PR":
            accepted = {t["candidate_heads"][e["source_url"]]}
        else:
            accepted = {t["source_heads"][e["source_repository"]]}
            accepted.update(sha for url, sha in t["candidate_heads"].items()
                            if github_repo(url) == e["source_repository"])
        if e["assessed_sha"] not in accepted:
            return verdict("STALE", ["CANDIDATE_HEAD_STALE"], "Re-fetch exact provider heads; invalidate candidate claims", t, len(evidence))
    if t["source_health"] != "COMPLETE":
        return verdict("BLOCKED", ["SOURCE_INCOMPLETE"], "Re-fetch the incomplete/unknown source census", t, len(evidence))
    if t["owner_decision"]["status"] == "CONFLICT":
        return verdict("BLOCKED", ["OWNER_DECISION_CONFLICT"], "Escalate to actual Owner decision authority", t, len(evidence))
    if t["owner_decision"]["status"] == "UNKNOWN":
        return verdict("CONDITIONAL", ["OWNER_DECISION_UNKNOWN"], "Locate authoritative Owner decision; investigate read-only", t, len(evidence))
    if not evidence:
        return verdict("CONDITIONAL", ["EVIDENCE_MISSING"], "Fetch independent source evidence", t, 0)
    reasons = ["PROVIDER_RECHECK_REQUIRED"]
    if any(e["privacy"] != "PUBLIC" for e in evidence):
        reasons.append("PRIVATE_EVIDENCE_REDACTION_REQUIRED")
    return verdict("CONDITIONAL", reasons,
                   "Perform independent current GitHub/provider readback; no execution admission", t, len(evidence))


def main() -> int:
    p = argparse.ArgumentParser(description="Local read-only ONB-RWI contract validator")
    p.add_argument("--target", required=True)
    p.add_argument("--evidence", required=True)
    args = p.parse_args()
    try:
        target = json.loads(Path(args.target).read_text(encoding="utf-8"))
        evidence = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps(verdict("BLOCKED", ["INPUT_UNAVAILABLE"],
                                "Provide readable strict JSON input: " + str(exc), None, 0), indent=2))
        return 2
    out = assess(target, evidence)
    print(json.dumps(out, sort_keys=True, indent=2))
    return 0 if out["status"] == "CONDITIONAL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
