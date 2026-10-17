#!/usr/bin/env python3
"""V36-ECO-02: read-only source/context read model over the native snapshot.

Adds, per task, the A14 SELF-CHECK companion (CODING_PRACTICES_ADDENDUM.md) and
source provenance, and pools pending items for coordinator reconciliation.
It never writes, never changes native E semantics and never grants acceptance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import unicodedata
from datetime import datetime

from decompose_v36 import GithubClient, PARENT_REF, load_plan
from lifecycle_v36 import ContractError, load_label, require_explicit_lab, validate_evidence
import snapshot_v36 as ss

MARKER = "TASK_EVIDENCE v3.6"
SELF_CHECK = re.compile(r"^SELF-CHECK v1 · (?P<task>\S+) · ", re.M)
CANDIDATE = re.compile(r"candidate (?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@(?P<sha>[0-9a-f]{40})")
DONE_WHEN = re.compile(r"^Done-when: .*?→ (?P<state>MET|NOT_MET|NOT_RUN|UNKNOWN)\b", re.M)
# Fail-closed pending detection (A14): normalise, skip known template keys, and require
# every other line mentioning "pend" to match the strict Pending grammar exactly once.
INVISIBLE = re.compile("[\u00ad\u200b-\u200f\u2060\ufeff]")
MARKUP = re.compile(r"<[^>]*>|[*_`~\\]")
KNOWN_KEYS = ("SELF-CHECK v1", "Basis:", "Done-when:", "Scope:", "A13:", "A13 review:", "Tests:",
              "Issue reconciliation:", "Proposed claim:", "Native report:")
PENDING = re.compile(r"^(?:\d+[.)]\s*)?(?:\[[ xX]\]\s*)?Pending\s*:\s*(?P<what>.+?)\s*·\s*owner\s+(?P<owner>.+?)"
                     r"\s*·\s*next\s+(?P<next>.+?)\s*·\s*unblocks\s+(?P<unblocks>.+?)"
                     r"\s*·\s*prevents task DONE\s+(?P<prevents>yes|no)(?![/\w])", re.I)
CLAIM = re.compile(r"^Proposed claim: (?P<claim>DONE|PARTIAL|BLOCKED|FAILED)\b", re.M)
LINK = re.compile(r"Self-check: https://github\.com/(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/issues/(?P<issue>[1-9][0-9]*)#issuecomment-(?P<id>[1-9][0-9]*)\s*$")


class CachingClient:
    """Wraps a provider so the native snapshot's reads are recorded and reused."""

    def __init__(self, client):
        self._client = client
        self.repo = client.repo
        self.comments, self.failures = {}, set()

    def list_issues(self):
        return self._client.list_issues()

    def list_comments(self, number):
        if number not in self.comments:
            try:
                self.comments[number] = self._client.list_comments(number)
            except ContractError:
                self.failures.add(number)
                raise
        return self.comments[number]

    def get_pr(self, number):
        try:
            return self._client.get_pr(number)
        except ContractError:
            self.failures.add("pr:%s" % number)
            raise


def digest(body):
    return hashlib.sha256((body or "").encode("utf-8")).hexdigest()


def provenance(comment):
    return {"comment_id": comment.get("id"), "url": comment.get("html_url"),
            "updated_at": comment.get("updated_at"), "body_sha256": digest(comment.get("body"))}


def parse_self_check(comment, task_id, owner_login):
    """Parse one SELF-CHECK v1 companion. Returns None when it is not one for this task."""
    body = comment.get("body") or ""
    head = SELF_CHECK.search(body)
    if not head or head["task"] != task_id:
        return None
    record = {**provenance(comment), "created_at": comment.get("created_at"), "status": "PARSED"}
    actor = comment.get("user")
    if MARKER in body:
        record["status"] = "REJECTED_CONTAINS_CANONICAL_MARKER"
    elif not isinstance(actor, dict) or actor.get("login") != owner_login:
        record["status"] = "REJECTED_FOREIGN_AUTHOR"
    states = [m["state"] for m in DONE_WHEN.finditer(body)]
    record["done_when"] = {s: states.count(s) for s in ("MET", "NOT_MET", "NOT_RUN", "UNKNOWN")}
    cand = CANDIDATE.search(body)
    record["candidate"] = f"{cand['repo']}@{cand['sha']}" if cand else "UNKNOWN"
    claim = CLAIM.search(body)
    record["claim"] = claim["claim"] if claim else "UNKNOWN"
    record["pending"], record["unparsed_pending"] = [], 0
    for raw in body.splitlines():
        line = MARKUP.sub("", INVISIBLE.sub("", unicodedata.normalize("NFKC", raw)))
        line = re.sub(r"^[^\w\[]*", "", line).strip()      # bullets, quotes, table bars, emoji
        if line.startswith(KNOWN_KEYS) or "pend" not in line.lower():
            continue
        if re.fullmatch(r"Pending\s*:\s*none\.?", line, re.I):
            continue                           # explicit empty list
        m = PENDING.match(line)
        if not m or "pend" in line[m.end():].lower():
            record["unparsed_pending"] += 1   # fail closed: unknown shape or several items on one line
            continue
        record["pending"].append({k: m[k].strip() for k in ("what", "owner", "next", "unblocks")}
                                 | {"prevents_done": m["prevents"].lower() == "yes"})
    return record


def linked_comment_id(evidence_body, repo, issue_number):
    """Comment id linked on the For the user line, only if it is on this repo and child issue."""
    lines = (evidence_body or "").splitlines()
    if len(lines) < 2 or not lines[1].startswith("For the user: "):
        return None
    hit = LINK.search(lines[1])
    if not hit or hit["repo"] != repo or int(hit["issue"]) != issue_number:
        return None
    return int(hit["id"])


def qualify(row, check, link_id):
    """Claim qualification only: native current evidence plus a consistent self-check.
    Never acceptance; reasons explain every gap."""
    reasons = []
    if row["status"] != "CURRENT_EVIDENCE":
        reasons.append("native evidence " + row["status"])
    if check is None:
        reasons.append("no SELF-CHECK v1 companion found")
    else:
        if check["status"] != "PARSED":
            reasons.append("self-check " + check["status"])
        if link_id is None:
            reasons.append("evidence does not link the self-check on its For the user line")
        elif link_id != check["comment_id"]:
            reasons.append("evidence links a different comment than the latest self-check")
        if check["claim"] != "DONE":
            reasons.append("self-check claim " + check["claim"])
        open_items = sum(check["done_when"][s] for s in ("NOT_MET", "NOT_RUN", "UNKNOWN"))
        if open_items or not check["done_when"]["MET"]:
            reasons.append("done-when not all MET")
        if any(p["prevents_done"] for p in check["pending"]):
            reasons.append("pending item prevents DONE")
        if check["unparsed_pending"]:
            reasons.append("unparsed Pending line(s) in self-check")
    return {"claim_qualified": not reasons, "reasons": reasons,
            "acceptance": "NOT_EVALUATED"}


def read_model(plan, client, now):
    """Native snapshot + self-check companions + provenance; one read per source."""
    if not isinstance(now, str) or datetime.fromisoformat(now.replace("Z", "+00:00")).tzinfo is None:
        raise ValueError("now must be an ISO timestamp with timezone")
    cached = CachingClient(client)
    snap = ss.snapshot(plan, cached)
    owner_login = client.repo.split("/", 1)[0]
    tasks, pending = [], []
    by_issue = {f"https://github.com/{client.repo}/issues/{n}": n for n in cached.comments}
    for row in snap["tasks"]:
        number = by_issue.get(row["issue"])
        comments = cached.comments.get(number, []) if number else []
        checks = [c for c in (parse_self_check(x, row["task_id"], owner_login) for x in comments) if c]
        checks.sort(key=lambda c: (c.get("created_at") or "", c.get("comment_id") or 0))
        check = checks[-1] if checks else None
        evidence_body = next((c.get("body") for c in comments
                              if (c.get("html_url") or c.get("url")) == row["evidence"]), None)
        link_id = linked_comment_id(evidence_body, client.repo, number)
        out = {**row, "self_check": check, "self_check_history": len(checks),
               "evidence_links_self_check": link_id,
               "sources_read": [provenance(c) for c in comments if MARKER in (c.get("body") or "")
                                or (check and c.get("id") == check["comment_id"])]}
        out.update(qualify(row, check, link_id))
        out["self_check_matches_candidate"] = None
        if check and evidence_body:
            try:
                native_candidate = validate_evidence(evidence_body)["candidate"]
            except (ContractError, ValueError, IndexError):
                native_candidate = None
            out["self_check_matches_candidate"] = check["candidate"] == native_candidate
            if not out["self_check_matches_candidate"]:
                out["claim_qualified"] = False
                out["reasons"].append("self-check candidate differs from native evidence candidate")
        for item in (check or {}).get("pending", []):
            pending.append({"task_id": row["task_id"], "source": check["url"], **item})
        tasks.append(out)
    return {"schema": "v36.readmodel/v1", "observed_at": now, "plan": snap["plan"],
            "parent": snap["parent"], "label_sha": snap["label_sha"],
            "read_complete": not cached.failures,
            "unread_sources": sorted(str(f) for f in cached.failures),
            "native": {k: snap[k] for k in ("total", "current_evidence", "stale_evidence", "verified_complete")},
            "claims_qualified": sum(t["claim_qualified"] for t in tasks),
            "acceptance": "NOT_EVALUATED", "pending": pending, "tasks": tasks}


def main():
    p = argparse.ArgumentParser(description="v3.6 read-only read model (snapshot + SELF-CHECK + provenance)")
    p.add_argument("--label", required=True)
    p.add_argument("--plan", required=True)
    p.add_argument("--lab", help="explicit Writable lab: repository for lab-target reads")
    p.add_argument("--now", required=True, help="observation time, ISO with timezone")
    args = p.parse_args()
    label = load_label(args.label)
    plan = load_plan(args.plan, label)
    require_explicit_lab(label, plan["parent"], args.lab)
    client = GithubClient(PARENT_REF.fullmatch(plan["parent"])[1])
    client.get_pr = lambda n: client.request("GET", f"/pulls/{n}")
    print(json.dumps(read_model(plan, client, args.now), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
