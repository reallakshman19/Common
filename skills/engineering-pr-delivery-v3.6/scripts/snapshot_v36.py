#!/usr/bin/env python3
"""WP3: GitHub-only read snapshot, never infer task completion."""
from __future__ import annotations
import argparse
import json
import re
from urllib.parse import urlparse

from decompose_v36 import GithubClient, PARENT_REF, is_task_issue, load_plan
from lifecycle_v36 import ContractError, load_label, validate_evidence

SHA = re.compile(r"^([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([0-9a-f]{40})$")
PR = re.compile(r"^/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/pull/([1-9][0-9]*)(?:/commits/[0-9a-f]{40})?/?$")


def proof_pr(body, repo):
    lines = body.splitlines()
    if len(lines) < 3 or not lines[2].startswith("Proof: "):
        return None
    url = urlparse(lines[2][7:])
    hit = PR.fullmatch(url.path)
    if url.scheme != "https" or url.netloc != "github.com" or not hit:
        return None
    if hit[1]+"/"+hit[2] != repo or url.query or url.fragment:
        return None
    return int(hit[3])


def snapshot(plan, client):
    match = PARENT_REF.fullmatch(plan["parent"])
    if not match or match[1] != client.repo:
        raise ContractError("snapshot repository mismatch")
    issues = client.list_issues()
    tasks, prs = [], {}
    for task in plan["tasks"]:
        row = {"task_id": task["task_id"], "outcome": task["outcome"],
               "size": task["size"], "issue": None, "evidence": None,
               "pr": None, "status": "UNKNOWN", "complete": False}
        matches = [issue for issue in issues if is_task_issue(issue, task, plan["parent"])]
        if len(matches) != 1:
            row["status"] = "MISSING_CHILD" if not matches else "AMBIGUOUS_CHILD"
            tasks.append(row)
            continue
        issue = matches[0]
        number = issue.get("number")
        if not isinstance(number, int) or not isinstance(issue.get("html_url"), str):
            tasks.append(row)
            continue
        row["issue"] = issue["html_url"]
        try:
            comments = client.list_comments(number)
        except ContractError:
            row["status"] = "PROVIDER_UNAVAILABLE"
            tasks.append(row)
            continue
        eligible, invalid = [], 0
        for comment in comments:
            body = comment.get("body") or ""
            if "TASK_EVIDENCE v3.6" not in body:
                continue
            try:
                evidence = validate_evidence(body)
            except (ContractError, ValueError, IndexError):
                invalid += 1
                continue
            if (evidence["task_id"], evidence["outcome"], evidence["issue_ref"]) != (
                task["task_id"], task["outcome"], f"{client.repo}#{number}"
            ):
                invalid += 1
                continue
            eligible.append((comment, evidence))
        if not eligible:
            row["status"] = "INVALID_EVIDENCE" if invalid else "NO_EVIDENCE"
            tasks.append(row)
            continue
        if len(eligible) > 1:
            if not all(isinstance(e[0].get("created_at"), str) for e in eligible):
                row["status"] = "AMBIGUOUS_EVIDENCE"
                tasks.append(row)
                continue
            eligible.sort(key=lambda e: (e[0]["created_at"], e[0].get("id", 0)))
        comment, evidence = eligible[-1]
        row["evidence"] = comment.get("html_url") or comment.get("url")
        candidate = SHA.fullmatch(evidence["candidate"])
        pr_no = proof_pr(comment["body"], client.repo)
        if not candidate or candidate[1] != client.repo or pr_no is None:
            row["status"] = "UNVERIFIED_PROOF"
            tasks.append(row)
            continue
        try:
            if pr_no not in prs:
                prs[pr_no] = client.get_pr(pr_no)
            live = prs[pr_no]
        except ContractError:
            row["status"] = "PROVIDER_UNAVAILABLE"
            tasks.append(row)
            continue
        if not isinstance(live, dict) or not isinstance(live.get("head"), dict):
            row["status"] = "UNKNOWN_PR"
            tasks.append(row)
            continue
        row["pr"] = f"https://github.com/{client.repo}/pull/{pr_no}"
        row["status"] = ("CURRENT_EVIDENCE" if candidate[2] == live["head"].get("sha")
                         else "STALE_EVIDENCE")
        tasks.append(row)
    return {"plan": plan["plan_version"], "parent": plan["parent"],
            "label_sha": plan["label"]["label_sha"], "total": len(tasks),
            "current_evidence": sum(t["status"] == "CURRENT_EVIDENCE" for t in tasks),
            "stale_evidence": sum(t["status"] == "STALE_EVIDENCE" for t in tasks),
            "verified_complete": 0, "tasks": tasks}


def main():
    p = argparse.ArgumentParser(description="v3.6 read-only GitHub evidence snapshot")
    p.add_argument("--label", required=True)
    p.add_argument("--plan", required=True)
    args = p.parse_args()
    label = load_label(args.label)
    plan = load_plan(args.plan, label)
    client = GithubClient(PARENT_REF.fullmatch(plan["parent"])[1])
    client.get_pr = lambda n: client.request("GET", f"/pulls/{n}")
    print(json.dumps(snapshot(plan, client), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
