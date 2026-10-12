#!/usr/bin/env python3
"""V3.6 WP4. Deterministic GitHub issue and PR titles from observed evidence."""
from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import dataclass

from decompose_v36 import GithubClient, PARENT_REF, is_task_issue, load_plan
from lifecycle_v36 import ContractError, load_label, require_explicit_lab
from snapshot_v36 import snapshot

MANAGED = re.compile(r"^(?:\[[^\]\r\n]{1,64}\]){1,7}\s*")
URL_PR = re.compile(r"^https://github\.com/([^/]+/[^/]+)/pull/([1-9][0-9]*)$")


def title_tail(current: str, fallback: str) -> str:
    """Strip only a leading well-formed bracket namespace; retain readable suffix."""
    if not isinstance(current, str):
        raise ContractError("missing GitHub title")
    tail = MANAGED.sub("", current).strip()
    return tail or fallback


def title_plan(plan: dict, issues: list[dict], pr: dict | None, report: dict) -> list[dict]:
    """Pure projection: current evidenced != task complete or accepted."""
    if report["parent"] != plan["parent"] or report["label_sha"] != plan["label"]["label_sha"]:
        raise ContractError("snapshot/plan mismatch")
    parent = PARENT_REF.fullmatch(plan["parent"])
    if not parent:
        raise ContractError("invalid parent")
    count = report["current_evidence"]
    total = report["total"]
    current_by_task = {x["task_id"]: x for x in report["tasks"]}
    updates = []
    parent_issue = next((x for x in issues if x.get("number") == int(parent[2])), None)
    if parent_issue is None:
        raise ContractError("parent issue absent")
    suffix = title_tail(parent_issue.get("title"), "Independent lifecycle acceptance")
    updates.append({"kind": "issue", "number": int(parent[2]), "before": parent_issue["title"],
                    "after": f"[V3.6][LAB][E{count}/{total}] {suffix}"})
    for task in plan["tasks"]:
        matches = [x for x in issues if is_task_issue(x, task, plan["parent"])]
        if len(matches) != 1:
            raise ContractError("cannot title missing or ambiguous child")
        row = current_by_task[task["task_id"]]
        state = ("EVIDENCED" if row["status"] == "CURRENT_EVIDENCE"
                 else "STALE" if row["status"] == "STALE_EVIDENCE" else "PENDING")
        title = f"[V3.6][{task['outcome']}][{state}] {task['task_id']} — {task['title']}"
        updates.append({"kind": "issue", "number": matches[0]["number"],
                        "before": matches[0]["title"], "after": title})
    if pr is not None:
        if not isinstance(pr.get("number"), int) or not isinstance(pr.get("head"), dict):
            raise ContractError("malformed PR")
        status = "MERGED" if pr.get("merged") else "DRAFT" if pr.get("draft") else (
            "OPEN" if pr.get("state") == "open" else "CLOSED")
        # The parent count covers ALL children. A PR title, instead, may describe
        # only tasks whose provider-verified proof actually refers to THIS PR.
        # STALE evidence still identifies its PR, but never counts as current.
        pr_ref = f"https://github.com/{parent[1]}/pull/{pr['number']}"
        linked = [current_by_task[t["task_id"]] for t in plan["tasks"]
                  if current_by_task[t["task_id"]].get("pr") == pr_ref]
        linked_ids = {t["task_id"] for t in linked}
        outcomes = "/".join(sorted({t["outcome"] for t in plan["tasks"]
                                    if t["task_id"] in linked_ids})) or "UNATTRIBUTED"
        pr_count = sum(t["status"] == "CURRENT_EVIDENCE" for t in linked)
        pr_total = len(linked)
        tail = title_tail(pr.get("title"), "Lifecycle work")
        updates.append({"kind": "pr", "number": pr["number"], "before": pr["title"],
                        "after": f"[V3.6][{outcomes}][{status}][E{pr_count}/{pr_total}] {tail}",
                        "head_sha": pr["head"].get("sha")})
    return updates


def calculate(plan: dict, client, pr_number: int | None = None) -> dict:
    """All reads are fresh. No GET failure turns into a completed task."""
    repo = PARENT_REF.fullmatch(plan["parent"])[1]
    if client.repo != repo:
        raise ContractError("wrong repository")
    issues = client.list_issues()
    if not hasattr(client, "get_pr"):
        client.get_pr = lambda n: client.request("GET", f"/pulls/{n}")
    report = snapshot(plan, client)
    pr = client.get_pr(pr_number) if pr_number is not None else None
    updates = title_plan(plan, issues, pr, report)
    return {"parent": plan["parent"], "label_sha": plan["label"]["label_sha"],
            "current_evidence": report["current_evidence"], "total": report["total"],
            "accepted_complete": report["verified_complete"],
            "changes": [u for u in updates if u["before"] != u["after"]],
            "all": updates}


def apply_projection(calculated: dict, client, *, confirm_scope: str, allow_write: bool = False) -> dict:
    """Write only to an explicitly selected parent repository. Verify exact readback."""
    if not allow_write:
        return {"dry_run": True, "proposed": len(calculated["changes"]), "applied": 0}
    if confirm_scope != calculated["parent"] or client.repo != PARENT_REF.fullmatch(confirm_scope)[1]:
        raise ContractError("scope confirmation mismatch")
    changed = 0
    for item in calculated["changes"]:
        kind, number = item["kind"], item["number"]
        endpoint = f"/issues/{number}" if kind == "issue" else f"/pulls/{number}"
        observed = client.request("GET", endpoint)
        if observed.get("title") != item["before"]:
            raise ContractError(f"provider title drift for {kind} #{number}")
        if kind == "pr" and observed.get("head", {}).get("sha") != item["head_sha"]:
            raise ContractError("PR head changed before title write")
        client.request("PATCH", endpoint, {"title": item["after"]})
        verified = client.request("GET", endpoint)
        if verified.get("title") != item["after"]:
            raise ContractError(f"title readback mismatch for {kind} #{number}")
        changed += 1
    return {"dry_run": False, "applied": changed, "readback_ok": True}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="v3.6 title publisher; dry-run default")
    parser.add_argument("--label", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--lab", help="explicit Writable lab: repository when plan targets lab")
    parser.add_argument("--pr", type=int)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm-scope", default="")
    args = parser.parse_args(argv)
    try:
        label = load_label(args.label)
        plan = load_plan(args.plan, label)
        require_explicit_lab(label, plan["parent"], args.lab)
        repo = PARENT_REF.fullmatch(plan["parent"])[1]
        token = os.environ.get("GITHUB_TOKEN")
        if args.apply and (args.confirm_scope != plan["parent"] or not token):
            raise ContractError("write requires token and exact --confirm-scope")
        client = GithubClient(repo, token)
        result = calculate(plan, client, args.pr)
        applied = apply_projection(result, client, confirm_scope=args.confirm_scope, allow_write=args.apply)
        print(json.dumps({"projection": result, "write": applied}, indent=2, sort_keys=True))
        return 0
    except ContractError as exc:
        parser.error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
