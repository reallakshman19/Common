#!/usr/bin/env python3
"""V36-ECO-02: strict SELF-CHECK v1 companion parser (A14), whitelist and fail closed.

A companion is template-conformant only when every non-blank line matches one exact
line of the Companion template (TEAM_PROTOCOL A6.2 / CODING_PRACTICES_ADDENDUM A14),
uses a restricted character set, and its free text carries no open-item wording.
Nothing is guessed: every other line is listed as non-conformant, and a
non-conformant companion cannot qualify a claim. Conforming is cheap for an author:
write the template lines as they are.
"""
from __future__ import annotations
import hashlib
import re

MARKER = "TASK_EVIDENCE v3.6"
STATES = ("MET", "NOT_MET", "NOT_RUN", "UNKNOWN", "NOT_APPLICABLE")
OUTSIDE_CHARSET = re.compile(r"[^\t\x20-\x7e·→—–]")      # ASCII + the template's own symbols
HTML = re.compile(r"&(?:#\d+|#x[0-9a-f]+|[a-z][a-z0-9]*);|<[a-z/!?]", re.I)
HEADER = re.compile(r"SELF-CHECK v1 · (?P<task>[^\s·]+) · (?P<issue>[^\s·]+)")
DONE_WHEN = re.compile(r"Done-when: (?P<crit>[^→·]+?) → (?P<state>%s)(?P<rest>(?: [^→·]*)?)" % "|".join(STATES))
PENDING_NONE = re.compile(r"Pending: none", re.I)
PENDING = re.compile(r"Pending: (?P<what>[^·]+?) · owner (?P<owner>[^·]+?) · next (?P<next>[^·]+?)"
                     r" · unblocks (?P<unblocks>[^·]+?) · prevents task DONE (?P<prevents>yes|no)"
                     r"(?P<basis>(?:[^\w·][^·]*)?)")
CLAIM = re.compile(r"Proposed claim: (?P<claim>DONE|PARTIAL|BLOCKED|FAILED)(?: · (?P<reason>[^·]*))?")
NATIVE = re.compile(r"Native report: (?:https://github\.com/\S+|PENDING|NOT_POSTED)(?P<rest>(?: [^·]*)?)")
FREE = re.compile(r"(?P<key>Basis|Scope|A13|A13 review|Tests|Issue reconciliation): (?P<text>[^·]+)")
CANDIDATE = re.compile(r"\bcandidate (?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@(?P<sha>[0-9a-f]{40})\b")
BENIGN = re.compile(r"depend|append|spend|expend|failures/skips/NOT_RUN", re.I)  # ordinary words, template label
OPEN = re.compile(r"pend|block|outstanding|todo|tbd|await|waiting|unresolved|incomplete|unfinished|partial"
                  r"|not[ _-]?(?:met|run|done|yet)|prevents|Done-when|Proposed claim", re.I)
UNIQUE = ("Basis", "Proposed claim", "Native report")


def digest(body):
    return hashlib.sha256((body or "").encode("utf-8")).hexdigest()


def provenance(comment):
    return {"comment_id": comment.get("id"), "url": comment.get("html_url"),
            "updated_at": comment.get("updated_at"), "body_sha256": digest(comment.get("body"))}


def has_open_wording(text, extra=None):
    text = BENIGN.sub("", text or "")
    return bool(OPEN.search(text) or (extra and extra.search(text)))


def classify(line, record):
    """Apply one template line to the record. Returns a non-conformance reason or None."""
    if OUTSIDE_CHARSET.search(line):
        return "character outside the template charset"
    if HTML.search(line):
        return "HTML tag or entity"
    m = DONE_WHEN.fullmatch(line)
    if m:
        record["done_when"][m["state"]] += 1
        return "open-item wording in Done-when text" if has_open_wording(m["crit"] + m["rest"]) else None
    if PENDING_NONE.fullmatch(line):
        return None
    m = PENDING.fullmatch(line)
    if m:
        record["pending"].append({k: m[k].strip() for k in ("what", "owner", "next", "unblocks")}
                                 | {"prevents_done": m["prevents"] == "yes"})
        if m["prevents"] == "no" and has_open_wording(m["basis"], re.compile(r"\byes\b", re.I)):
            return "Pending says prevents task DONE no but its basis reads as open"
        return None
    m = CLAIM.fullmatch(line)
    if m:
        record["claims"].append(m["claim"])
        return "open-item wording in claim reason" if has_open_wording(m["reason"], re.compile("fail", re.I)) else None
    m = NATIVE.fullmatch(line) or FREE.fullmatch(line)
    if m:
        if line.startswith("Basis: ") and record["candidate"] == "UNKNOWN":
            cand = CANDIDATE.search(line)
            record["candidate"] = f"{cand['repo']}@{cand['sha']}" if cand else "UNKNOWN"
        text = m["rest"] if line.startswith("Native report: ") else m["text"]
        return "open-item wording in free text" if has_open_wording(text) else None
    return "not a template line"


def parse_self_check(comment, task_id, owner_login):
    """Parse one SELF-CHECK v1 companion. Returns None when it is not one for this task.
    The header must be the first non-blank line."""
    body = comment.get("body") or ""
    lines = [(n, raw.rstrip("\r").rstrip(" ")) for n, raw in enumerate(body.split("\n"), 1)]
    lines = [(n, line) for n, line in lines if line.strip()]
    head = HEADER.fullmatch(lines[0][1]) if lines else None
    if not head or head["task"] != task_id:
        return None
    record = {**provenance(comment), "created_at": comment.get("created_at"), "status": "PARSED",
              "done_when": dict.fromkeys(STATES, 0), "candidate": "UNKNOWN", "pending": [], "claims": [],
              "nonconformant": []}
    actor = comment.get("user")
    if MARKER in body:
        record["status"] = "REJECTED_CONTAINS_CANONICAL_MARKER"
    elif not isinstance(actor, dict) or actor.get("login") != owner_login:
        record["status"] = "REJECTED_FOREIGN_AUTHOR"
    for n, line in lines[1:]:
        why = classify(line, record)
        if why:
            record["nonconformant"].append({"line": n, "why": why})
    for key in UNIQUE:
        if sum(line.startswith(key + ": ") for _, line in lines) > 1:
            record["nonconformant"].append({"line": 0, "why": "more than one %s line" % key})
    claims = record.pop("claims")
    record["claim"] = claims[0] if len(claims) == 1 else "UNKNOWN"
    return record
