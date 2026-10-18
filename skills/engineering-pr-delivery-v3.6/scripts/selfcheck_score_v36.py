"""SELF-CHECK v2 exact criterion inventory, and read-only v1 compatibility."""
from __future__ import annotations
import re

from selfcheck_v36 import parse_self_check as parse_native_v1
from criteria_v36 import SOURCE_PATTERN

HEADER = re.compile(r"SELF-CHECK v2 · (?P<task>[A-Za-z0-9_.-]+) · (?P<issue>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9]\d*)")
BASIS = re.compile(
    r"Basis: CRITERIA v1 · source (?P<source>" + SOURCE_PATTERN +
    r") · candidate (?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@(?P<sha>[0-9a-f]{40})"
)
CLAUSE = re.compile(r"Criterion: (?P<id>(?:AC|K|J)[1-9]\d*) → (?P<state>MET|NOT_MET|NOT_RUN|UNKNOWN|NOT_APPLICABLE) · proof: (?P<proof>[^\n·]+)")
SCORE = re.compile(r"Score: (?P<num>\d+)/(?P<den>\d+) · claim: (?P<claim>DONE|PARTIAL|BLOCKED)")
CLAIM = re.compile(r"Proposed claim: (?P<claim>DONE|PARTIAL|BLOCKED) · reason: (?P<reason>[^\n·]+)")
V1 = re.compile(r"SELF-CHECK v1 · (?P<task>[A-Za-z0-9_.-]+)(?: \([^\n·]*\))? · (?P<issue>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9]\d*)")


def parse_self_check_v2(body, criteria):
    if not isinstance(body, str) or len(body) > 100000:
        raise ValueError("v2 self-check must be bounded text")
    lines = [x.rstrip(" \t\r") for x in body.split("\n") if x.strip()]
    if len(lines) < 6 or any("TASK_EVIDENCE v3.6" in x for x in lines):
        raise ValueError("missing v2 clauses or forbidden canonical marker")
    header, basis = HEADER.fullmatch(lines[0]), BASIS.fullmatch(lines[1])
    if not header or not basis:
        raise ValueError("invalid v2 header or frozen basis")
    if basis["source"].strip() != criteria["source"]:
        raise ValueError("v2 source differs from frozen CRITERIA authority")
    checks, claimed_score, claim = {}, None, None
    for line in lines[2:]:
        m = CLAUSE.fullmatch(line)
        if m:
            if m["id"] in checks or m["id"] not in criteria["criteria"]:
                raise ValueError("extra or repeated criterion")
            checks[m["id"]] = {"state": m["state"], "proof": m["proof"].strip()}
            continue
        m = SCORE.fullmatch(line)
        if m and claimed_score is None:
            claimed_score, claim = (int(m["num"]), int(m["den"])), m["claim"]
            continue
        m = CLAIM.fullmatch(line)
        if m and "reason" not in locals():
            reason = m["reason"]
            proposed = m["claim"]
            continue
        raise ValueError("unrecognized, ambiguous or duplicate v2 line")
    if set(checks) != set(criteria["criteria"]):
        raise ValueError("missing or extra frozen criteria")
    if claimed_score is None or "proposed" not in locals() or proposed != claim:
        raise ValueError("missing score or inconsistent claims")
    return {"version": 2, "task_id": header["task"], "issue": header["issue"],
            "candidate": f'{basis["repo"]}@{basis["sha"]}', "criteria": checks,
            "claimed_score": claimed_score, "claim": claim, "reason": reason,
            "source": basis["source"]}


def parse_compatible(body, *, task_id, issue_ref, owner_login):
    """Retain native SELF-CHECK v1, including the real #409 annotated header.

    A legacy v1 parsed record is not automatically upgraded to scored v2, nor
    does a successful parse imply qualified task evidence or acceptance.
    """
    if not isinstance(body, str) or not body:
        raise ValueError("missing companion")
    first = body.splitlines()[0].strip()
    match = V1.fullmatch(first)
    if match:
        if match["task"] != task_id or match["issue"] != issue_ref:
            raise ValueError("v1 companion identity mismatch")
        normalized = body.replace(first, f"SELF-CHECK v1 · {task_id} · {issue_ref}", 1)
        result = parse_native_v1(
            {"id": 1, "html_url": "", "body": normalized,
             "user": {"login": owner_login}}, task_id, owner_login, issue_ref)
        if result is None or result["status"] != "PARSED":
            raise ValueError("legacy v1 companion cannot be parsed")
        return {"version": 1, "issue": issue_ref, "claim": result["claim"],
                "legacy": result, "owner_accepted": False}
    raise ValueError("not a supported legacy v1 companion")
