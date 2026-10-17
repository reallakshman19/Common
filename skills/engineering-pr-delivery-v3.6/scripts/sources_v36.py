#!/usr/bin/env python3
"""V36-ECO-02b: source history, attribution and issue-hop helpers for readmodel_v36.

Read-only and deterministic. Every value is either read from a source or an explicit
unknown; nothing here authenticates a human or grants acceptance.
"""
from __future__ import annotations
import copy
import re

from selfcheck_v36 import MARKER, digest

MAX_ID = 2 ** 63 - 1                 # custom providers may send arbitrarily large ints
MAX_HOPS = 20
LINK_ANY = re.compile(r"Self-check: (?P<url>\S+)")
LINK_FORM = re.compile(r"https://github\.com/(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/issues/(?P<issue>[1-9][0-9]{0,14})"
                       r"#issuecomment-[1-9][0-9]{0,14}")
INPUT_STATE = re.compile(r"\b(?P<kind>input|golden|benchmark) (?P<state>COMPLETE|PARTIAL|MISSING|NOT_APPLICABLE|UNKNOWN)\b")
CALLER_HASH = re.compile(r"caller[_ -]?(?:sha256|hash)\s*[:=]\s*[0-9a-f]{16,}", re.I)
SUPERSEDED = re.compile(r"Superseded by:?\**\s*#(?P<to>[1-9][0-9]{0,14})\b\s*(?:[—–:-]\s*)?(?P<reason>.*)")


def bounded_id(value):
    """True for a positive int id a GitHub-like provider can actually issue."""
    return type(value) is int and 0 < value <= MAX_ID


def link_problem(evidence_body, repo, issue_number):
    """Specific reason when the For the user line carries a Self-check link of another form or target."""
    lines = (evidence_body or "").splitlines()
    hit = LINK_ANY.search(lines[1]) if len(lines) > 1 else None
    if not hit:
        return None
    form = LINK_FORM.fullmatch(hit["url"])
    if not form:
        return ("evidence Self-check link form not recognised (expected "
                "https://github.com/<owner>/<repo>/issues/<n>#issuecomment-<id>)")
    if form["repo"] != repo or int(form["issue"]) != issue_number:
        return "evidence Self-check link targets %s#%s, not this child issue" % (form["repo"], form["issue"])
    return None


def declared_inputs(check_body):
    """Input/golden/benchmark completeness as the author declared it on the Basis line; else UNKNOWN."""
    out = {"input": "UNKNOWN", "golden": "UNKNOWN", "benchmark": "UNKNOWN", "attribution": "REPORTED_BY_AUTHOR"}
    basis = next((l for l in (check_body or "").splitlines() if l.startswith("Basis: ")), "")
    for m in INPUT_STATE.finditer(basis):
        out[m["kind"]] = m["state"]
    return out


def owner_input_kind(comment, owner_login):
    body = comment.get("body") or ""
    if CALLER_HASH.search(body):
        return "CALLER_HASH"
    if any(line.lstrip().startswith(">") for line in body.splitlines()):
        return "QUOTED_TEXT"
    if comment["user"]["login"] == owner_login:
        return "GITHUB_ACCOUNT"
    return None


def owner_inputs(comments, owner_login, skip_ids):
    """Possible Owner input, always REPORTED: an account, hash or quote is not authenticated approval."""
    out = []
    for c in comments:
        if c["id"] in skip_ids or MARKER in (c.get("body") or ""):
            continue
        kind = owner_input_kind(c, owner_login)
        if kind:
            out.append({"comment_id": c["id"], "url": c["html_url"], "reported_by": c["user"]["login"],
                        "kind": kind, "body_sha256": digest(c.get("body")), "attribution": "REPORTED",
                        "authenticated_human_approval": False})
    return out


def hop_status(exc):
    """Map a provider failure: 410 is verified deletion, 404/403 only inaccessible, anything else unread."""
    code = getattr(exc, "code", None) or getattr(exc.__cause__, "code", None)
    if code == 410:
        return "VERIFIED_DELETED"
    return "NOT_FOUND_OR_INACCESSIBLE" if code in (403, 404) else "UNREAD"


def issue_hops(start, issues, fetch):
    """Every Superseded-by hop from the task issue, with reason, source and target status."""
    hops, seen, current = [], {start}, issues.get(start)
    while current is not None and len(hops) < MAX_HOPS:
        hit = next(filter(None, map(SUPERSEDED.search, (current.get("body") or "").splitlines())), None)
        if not hit:
            break
        to = int(hit["to"])
        hop = {"from": current["number"], "to": to, "reason": hit["reason"].strip() or "UNKNOWN",
               "source": current["html_url"]}
        if to in seen:
            hops.append({**hop, "status": "CYCLE"})
            break
        seen.add(to)
        status, current = ("FOUND", issues[to]) if to in issues else fetch(to)
        hops.append({**hop, "status": status})
    return hops


def merge_cursor(read, loaded_issues, now, prior):
    """Per-source cursor and append-only revision history; earlier reads are never rewritten.
    read: {key: entry} from this read; loaded_issues: issues whose comments loaded in full."""
    prior = copy.deepcopy(prior or {})
    cursor, history = {}, prior.get("source_history", {})
    edited = []
    for key, entry in read.items():
        cursor[key] = {**entry, "read_at": now, "status": "READ"}
        revs = history.setdefault(key, [])
        if not revs or revs[-1]["body_sha256"] != entry["body_sha256"]:
            if revs:
                edited.append(key)
            revs.append({"body_sha256": entry["body_sha256"], "updated_at": entry["updated_at"], "first_read_at": now})
    for key, entry in prior.get("source_cursor", {}).items():
        if key in cursor:
            continue
        reread = entry.get("issue") in loaded_issues
        cursor[key] = {**entry, "status": "MISSING_SINCE_PRIOR" if reread else "UNREAD_KEEPING_PRIOR"}
        if reread:
            cursor[key]["checked_at"] = now
    return cursor, history, sorted(edited)
