#!/usr/bin/env python3
"""V36-ECO-02: strict SELF-CHECK v1 companion parser (A14), whitelist and fail closed.

A companion is template-conformant only when every non-blank line matches one exact
line of the Companion template (TEAM_PROTOCOL A6.2 / CODING_PRACTICES_ADDENDUM A14)
in a restricted character set. Nothing is guessed: every other line is listed as
non-conformant, and a non-conformant companion cannot qualify a claim.

Scope (A14 "qualified"): only the author's structured declarations are machine-read:
Done-when states, Pending prevents flags, one claim, the candidate. Prose inside the
fields is NOT interpreted; the coordinator still reads the companion (A14).
"""
from __future__ import annotations
import hashlib
import re

MARKER = "TASK_EVIDENCE v3.6"
STATES = ("MET", "NOT_MET", "NOT_RUN", "UNKNOWN", "NOT_APPLICABLE")   # only MET qualifies
OUTSIDE_CHARSET = re.compile(r"[^\t\x20-\x7e·→—–]")      # ASCII + the template's own symbols
HTML = re.compile(r"&(?:#\d+|#x[0-9a-f]+|[a-z][a-z0-9]*);|<[a-z/!?]", re.I)
HEADER = re.compile(r"SELF-CHECK v1 · (?P<task>[^\s·]+) · (?P<issue>[^\s·]+)")
DONE_WHEN = re.compile(r"Done-when: [^→·]+ → (?P<state>%s)(?=[ ,.;:(][^→·\w]*\w)[ ,.;:(][^→·]*" % "|".join(STATES))
PENDING_NONE = re.compile(r"Pending: none", re.I)
PENDING = re.compile(r"Pending: (?P<what>[^·]+?) · owner (?P<owner>[^·]+?) · next (?P<next>[^·]+?)"
                     r" · unblocks (?P<unblocks>[^·]+?) · prevents task DONE (?P<prevents>yes|no)"
                     r"(?:[ ,;:.(—–-][^·]*)?", re.I)
CLAIM = re.compile(r"Proposed claim: (?P<claim>DONE|PARTIAL|BLOCKED|FAILED)(?: · (?P<reason>[^·]*))?")
NATIVE = re.compile(r"Native report: (?:https://github\.com/[A-Za-z0-9_.#/-]+|PENDING|NOT_POSTED)(?: [^·]*)?")
FREE = re.compile(r"(?P<key>Basis|Scope|A13|A13 review|Tests|Issue reconciliation): (?P<text>[^·]+)")
CANDIDATE = re.compile(r"\bcandidate (?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@(?P<sha>[0-9a-f]{40})(?![\w@])")
UNIQUE = ("Basis", "Scope", "A13", "A13 review", "Proposed claim", "Native report")
EMBEDDED_KEY = re.compile(r"(?:Done-when|Pending|Proposed claim|Native report|SELF-CHECK)\s*:", re.I)


def digest(body):
    return hashlib.sha256((body if isinstance(body, str) else "").encode("utf-8")).hexdigest()


def provenance(comment):
    return {"comment_id": comment.get("id"), "url": comment.get("html_url"),
            "updated_at": comment.get("updated_at"), "body_sha256": digest(comment.get("body"))}


def classify(line, record):
    """Apply one template line to the record. Returns a non-conformance reason or None."""
    if OUTSIDE_CHARSET.search(line):
        return "character outside the template charset"
    if HTML.search(line):
        return "HTML tag or entity"
    if EMBEDDED_KEY.search(line, 1):
        return "template key embedded inside another line"
    m = DONE_WHEN.fullmatch(line)
    if m:
        record["done_when"][m["state"]] += 1
        return None
    if PENDING_NONE.fullmatch(line):
        return None
    m = PENDING.fullmatch(line)
    if m:
        record["pending"].append({k: m[k].strip() for k in ("what", "owner", "next", "unblocks")}
                                 | {"prevents_done": m["prevents"].lower() == "yes"})
        return None
    m = CLAIM.fullmatch(line)
    if m:
        record["claims"].append(m["claim"])
        return None
    if NATIVE.fullmatch(line) or FREE.fullmatch(line):
        if line.startswith("Basis: "):
            if len(re.findall(r"\bcandidate\b", line, re.I)) != 1:
                return "Basis must name exactly one candidate"
            cand = CANDIDATE.search(line)
            record["candidate"] = f"{cand['repo']}@{cand['sha']}" if cand else "UNKNOWN"
        return None
    return "not a template line"


def parse_self_check(comment, task_id, owner_login, issue_ref=None):
    """Parse one SELF-CHECK v1 companion. Returns None when it is not one for this task.
    The header must be the first non-blank line."""
    body = comment.get("body")
    if not isinstance(body, str):
        return None
    lines = [(n, raw.rstrip("\r").rstrip(" \t")) for n, raw in enumerate(body.split("\n"), 1)]
    lines = [(n, line) for n, line in lines if line.strip(" \t")]
    head = HEADER.fullmatch(lines[0][1]) if lines else None
    if not head or head["task"] != task_id:
        return None
    record = {**provenance(comment), "created_at": comment.get("created_at"), "status": "PARSED",
              "done_when": dict.fromkeys(STATES, 0), "candidate": "UNKNOWN", "pending": [], "claims": [],
              "nonconformant": []}
    actor = comment.get("user")
    if MARKER in body:
        record["status"] = "REJECTED_CONTAINS_CANONICAL_MARKER"
    elif not isinstance(actor, dict) or str(actor.get("login")).casefold() != owner_login.casefold():
        record["status"] = "REJECTED_FOREIGN_AUTHOR"
    if issue_ref and head["issue"] != issue_ref:
        record["nonconformant"].append({"line": lines[0][0], "why": "header issue is not this issue"})
    for n, line in lines[1:]:
        why = classify(line, record)
        if why:
            record["nonconformant"].append({"line": n, "why": why})
    for key in UNIQUE:
        if sum(line.startswith(key + ": ") for _, line in lines) > 1:
            record["nonconformant"].append({"line": 0, "why": "more than one %s line" % key})
    if not any(line.startswith("Pending: ") for _, line in lines):
        record["nonconformant"].append({"line": 0, "why": "no Pending line (use Pending: none)"})
    claims = record.pop("claims")
    record["claim"] = claims[0] if len(claims) == 1 else "UNKNOWN"
    return record
