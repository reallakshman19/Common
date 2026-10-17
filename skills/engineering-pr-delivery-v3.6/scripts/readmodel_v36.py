#!/usr/bin/env python3
"""V36-ECO-02: read-only source/context read model over the native snapshot.

Adds, per task, the A14 SELF-CHECK companion (parsed strictly by selfcheck_v36) and
source provenance, and pools pending items for coordinator reconciliation.
It never writes, never changes native E semantics and never grants acceptance.
"""
from __future__ import annotations
import argparse
import json
import re
from datetime import datetime

from decompose_v36 import GithubClient, PARENT_REF, load_plan
from lifecycle_v36 import ContractError, load_label, require_explicit_lab, validate_evidence
import snapshot_v36 as ss
from selfcheck_v36 import MARKER, parse_self_check, provenance

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
        if check["nonconformant"]:
            reasons.append("self-check not template-conformant (%d)" % len(check["nonconformant"]))
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
