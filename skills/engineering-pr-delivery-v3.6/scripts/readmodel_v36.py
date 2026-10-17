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
from datetime import datetime, timezone

from decompose_v36 import GithubClient, PARENT_REF, load_plan
from lifecycle_v36 import ContractError, load_label, require_explicit_lab, validate_evidence
import snapshot_v36 as ss
from selfcheck_v36 import MARKER, digest, parse_self_check, provenance
import sources_v36 as src

SHA40 = re.compile(r"[0-9a-f]{40}")
LINK = re.compile(r"Self-check: https://github\.com/(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/issues/(?P<issue>[1-9][0-9]{0,14})#issuecomment-(?P<id>[1-9][0-9]{0,14})\s*$")


def utc_stamp(value):
    """Fixed-width UTC form of an ISO timestamp with timezone, so string order is time order."""
    if not isinstance(value, str):
        raise ValueError("timestamp is not a string")
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("timestamp has no timezone")
    u = stamp.astimezone(timezone.utc)       # OverflowError at the range edges -> unread source
    return "%04d-%02d-%02dT%02d:%02d:%02d.%06dZ" % (u.year, u.month, u.day, u.hour, u.minute, u.second,
                                                     u.microsecond)


def clean_comment(c):
    """Validated copy of one provider comment; ValueError when malformed."""
    if (not isinstance(c, dict) or not src.bounded_id(c.get("id")) or not isinstance(c.get("body"), (str, type(None)))
            or not isinstance(c.get("html_url"), str) or not isinstance(c.get("updated_at"), (str, type(None)))
            or not isinstance(c.get("user"), dict) or not isinstance(c["user"].get("login"), str)):
        raise ValueError("malformed comment")
    return {**c, "created_at": utc_stamp(c.get("created_at"))}


def clean_issue(i):
    if (not isinstance(i, dict) or not src.bounded_id(i.get("number")) or not isinstance(i.get("html_url"), str)
            or not all(isinstance(i.get(k), (str, type(None))) for k in ("title", "body", "state"))):
        raise ValueError("malformed issue")
    return i


class CachingClient:
    """Wraps a provider so the native snapshot's reads are recorded and reused."""

    def __init__(self, client):
        self._client = client
        self.repo = client.repo
        self.comments, self.failures, self.prs, self.issues = {}, set(), {}, {}

    def _read(self, source, call, *args):
        """Any provider error is recorded as an unread source and re-raised as ContractError."""
        try:
            return call(*args)
        except Exception as exc:
            self.failures.add(source)
            if isinstance(exc, ContractError):
                raise
            raise ContractError("provider error reading %s: %s" % (source, type(exc).__name__)) from exc

    def _checked(self, source, call, check, *args):
        """Read, then validate; malformed provider data is an unread source too."""
        data = self._read(source, call, *args)
        try:
            return check(data)
        except Exception as exc:                # any malformed shape, incl. OverflowError
            self.failures.add(source)
            raise ContractError("malformed provider data for %s: %s" % (source, exc)) from exc

    def list_issues(self):
        issues = self._checked("issues", self._client.list_issues, lambda d: [clean_issue(i) for i in list_of(d)])
        self.issues = {i["number"]: i for i in issues}
        return issues

    def fetch_issue(self, number):
        """(status, issue) for a hop target outside the listing; never raises."""
        get = getattr(self._client, "get_issue", None)
        if get is None:
            self.failures.add("issue:%d" % number)
            return "UNREAD", None
        try:
            issue = clean_issue(get(number))
        except Exception as exc:
            status = src.hop_status(exc)
            if status == "UNREAD":
                self.failures.add("issue:%d" % number)
            return status, None
        if issue["number"] != number:          # provider answered for another issue
            self.failures.add("issue:%d" % number)
            return "MISMATCHED", None
        return "FOUND", issue

    def list_comments(self, number):
        if number not in self.comments:
            self.comments[number] = self._checked(number, self._client.list_comments,
                                                  lambda d: [clean_comment(c) for c in list_of(d)], number)
        return self.comments[number]

    def get_pr(self, number):
        pr = self._checked("pr:%s" % number, self._client.get_pr, clean_pr, number)
        self.prs[number] = pr["head"]["sha"]
        return pr


def list_of(data):
    if not isinstance(data, list):
        raise ValueError("expected a list")
    return data


def clean_pr(data):
    head = data.get("head") if isinstance(data, dict) else None
    if not isinstance(head, dict) or not isinstance(head.get("sha"), str) or not SHA40.fullmatch(head["sha"]):
        raise ValueError("expected a pull request with a head sha")
    return data


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
        open_items = sum(check["done_when"][s] for s in ("NOT_MET", "NOT_RUN", "UNKNOWN", "NOT_APPLICABLE"))
        if open_items or not check["done_when"]["MET"]:
            reasons.append("done-when not all MET")
        if any(p["prevents_done"] for p in check["pending"]):
            reasons.append("pending item prevents DONE")
        if check["nonconformant"]:
            reasons.append("self-check not template-conformant (%d)" % len(check["nonconformant"]))
    return {"claim_qualified": not reasons, "reasons": reasons,
            "qualification_basis": "STRUCTURAL: author's declared fields only; prose not interpreted",
            "acceptance": "NOT_EVALUATED"}


def is_own_evidence(comment, row, repo, number):
    """Canonical evidence by the owner for this task and issue (the native admission rule)."""
    actor = comment.get("user")
    if not isinstance(actor, dict) or actor.get("login") != repo.split("/", 1)[0]:
        return False
    try:
        ev = validate_evidence(comment.get("body"))
    except (ContractError, ValueError, IndexError, TypeError, AttributeError):
        return False
    return (ev["task_id"], ev["outcome"], ev["issue_ref"]) == (row["task_id"], row["outcome"], f"{repo}#{number}")


def task_view(row, comments, repo, number):
    """One task: latest self-check, unparseable look-alikes, link, qualification."""
    owner_login, issue_ref = repo.split("/", 1)[0], f"{repo}#{number}"
    parsed = [(x, parse_self_check(x, row["task_id"], owner_login, issue_ref)) for x in comments]
    checks = sorted((c for _, c in parsed if c), key=lambda c: (c["created_at"], c["comment_id"]))
    check = checks[-1] if checks else None
    after = (check["created_at"], check["comment_id"]) if check else None
    newer = [x["id"] for x, c in parsed if after and c is not check and (x["created_at"], x["id"]) >= after
             and not is_own_evidence(x, row, repo, number)]
    evidence_body = next((c.get("body") for c in comments
                          if (c.get("html_url") or c.get("url")) == row["evidence"]), None)
    link_id = linked_comment_id(evidence_body, repo, number)
    native_candidate = native_candidate_of(evidence_body)
    out = {**row, "self_check": check, "self_check_history": len(checks),
           "comments_after_self_check": newer, "evidence_links_self_check": link_id,
           "sources_read": [provenance(c) for c in comments if MARKER in str(c.get("body") or "")
                            or (check and c.get("id") == check["comment_id"]) or c.get("id") in newer]}
    out.update(qualify(row, check, link_id))
    problem = src.link_problem(evidence_body, repo, number)
    if problem:
        out["reasons"].append(problem)
    out["candidate_sha"] = native_candidate.split("@", 1)[1] if native_candidate else None
    if newer:                                   # fail closed: only canonical evidence may follow
        out["claim_qualified"] = False
        out["reasons"].append("comment(s) after the self-check other than canonical evidence: %s" % newer)
    out["self_check_matches_candidate"] = None
    if check and evidence_body:
        out["self_check_matches_candidate"] = check["candidate"] == native_candidate
        if not out["self_check_matches_candidate"]:
            out["claim_qualified"] = False
            out["reasons"].append("self-check candidate differs from native evidence candidate")
    return out


def native_candidate_of(evidence_body):
    if not evidence_body:
        return None
    try:
        return validate_evidence(evidence_body)["candidate"]
    except (ContractError, ValueError, IndexError):
        return None


def fail(out, reason):
    out["claim_qualified"] = False
    out["reasons"].append(reason)


def context_view(out, comments, repo, number, cached, edited):
    """ECO-02b fields: observed head, edits since the prior read, inputs, Owner input, issue hops."""
    pr_no = int(out["pr"].rsplit("/", 1)[1]) if out["pr"] else None
    head, cand = cached.prs.get(pr_no), out["candidate_sha"]
    out["observed_head"] = head
    out["head_matches_candidate"] = None if head is None or cand is None else head == cand
    if out["head_matches_candidate"] is False:
        fail(out, "observed PR head %s differs from candidate %s" % (head, cand))
    if out["issue"] and number is None:
        fail(out, "child issue url form not recognised: %s (expected https://github.com/%s/issues/<n>)"
             % (out["issue"], repo))
    for key in ("comment:%s" % s["comment_id"] for s in out["sources_read"]):
        if key in edited:
            fail(out, "source edited since prior read: " + key)
    check = out["self_check"]
    body = next((c.get("body") for c in comments if check and c["id"] == check["comment_id"]), None)
    out["inputs"] = src.declared_inputs(body)
    skip = {check["comment_id"]} if check else set()
    out["owner_inputs"] = src.owner_inputs(comments, repo.split("/", 1)[0], skip)
    out["issue_hops"] = src.issue_hops(number, cached.issues, cached.fetch_issue) if number else []
    return out


def source_cursor(cached, now, prior):
    read = {"comment:%d" % c["id"]: {"issue": n, "url": c["html_url"], "updated_at": c.get("updated_at"),
                                     "body_sha256": digest(c.get("body"))}
            for n, cs in cached.comments.items() for c in cs}
    cursor, history, edited = src.merge_cursor(read, set(cached.comments), now, prior)
    return {"source_cursor": cursor, "source_history": history, "edited_sources": edited,
            "cursor": complete_cursor(cached, now, prior)}


def complete_cursor(cached, now, prior):
    """Advances only when nothing failed; call again after any later reads (hop fetches)."""
    last = now if not cached.failures else ((prior or {}).get("cursor") or {}).get("last_complete_read_at")
    return {"last_complete_read_at": last}


def read_model(plan, client, now, prior=None):
    """Native snapshot + self-check companions + provenance; one read per source.
    prior: an earlier read_model result; its history is carried forward, never rewritten."""
    if not isinstance(now, str) or datetime.fromisoformat(now.replace("Z", "+00:00")).tzinfo is None:
        raise ValueError("now must be an ISO timestamp with timezone")
    cached = CachingClient(client)
    base = {"schema": "v36.readmodel/v1", "observed_at": now, "acceptance": "NOT_EVALUATED"}
    try:
        snap = ss.snapshot(plan, cached)
    except Exception as exc:                     # unreadable issue list, or any native parse failure
        if not isinstance(exc, ContractError):
            cached.failures.add("snapshot")
        return {**base, **source_cursor(cached, now, prior), "read_complete": False, "unread_sources": sorted(str(f) for f in cached.failures),
                "error": str(exc), "claims_qualified": 0, "pending": [], "tasks": []}
    tasks, pending, cur = [], [], source_cursor(cached, now, prior)
    by_issue = {f"https://github.com/{client.repo}/issues/{n}": n for n in cached.comments}
    for row in snap["tasks"]:
        number = by_issue.get(row["issue"])
        comments = cached.comments.get(number, []) if number else []
        out = context_view(task_view(row, comments, client.repo, number), comments, client.repo, number,
                           cached, cur["edited_sources"])
        for item in (out["self_check"] or {}).get("pending", []):
            pending.append({"task_id": row["task_id"], "source": out["self_check"]["url"], **item})
        tasks.append(out)
    cur["cursor"] = complete_cursor(cached, now, prior)          # hop fetches may have failed since
    return {**base, **cur, "plan": snap["plan"], "parent": snap["parent"], "label_sha": snap["label_sha"],
            "read_complete": not cached.failures,
            "unread_sources": sorted(str(f) for f in cached.failures),
            "native": {k: snap[k] for k in ("total", "current_evidence", "stale_evidence", "verified_complete")},
            "claims_qualified": sum(t["claim_qualified"] for t in tasks),
            "pending": pending, "tasks": tasks}


def main():
    p = argparse.ArgumentParser(description="v3.6 read-only read model (snapshot + SELF-CHECK + provenance)")
    p.add_argument("--label", required=True)
    p.add_argument("--plan", required=True)
    p.add_argument("--lab", help="explicit Writable lab: repository for lab-target reads")
    p.add_argument("--now", required=True, help="observation time, ISO with timezone")
    p.add_argument("--prior", help="earlier read-model JSON whose source history is carried forward")
    args = p.parse_args()
    label = load_label(args.label)
    plan = load_plan(args.plan, label)
    require_explicit_lab(label, plan["parent"], args.lab)
    client = GithubClient(PARENT_REF.fullmatch(plan["parent"])[1])
    client.get_pr = lambda n: client.request("GET", f"/pulls/{n}")
    client.get_issue = lambda n: client.request("GET", f"/issues/{n}")
    prior = json.load(open(args.prior, encoding="utf-8")) if args.prior else None
    print(json.dumps(read_model(plan, client, args.now, prior), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
