#!/usr/bin/env python3
"""V3.6 Bounded Decomposition Pacing Harness.

Executes progressive decomposition in rate-controlled batches to prevent triggering
GitHub secondary content-creation limits (<= 15 issue creates per minute).
Reports timing, latency, and rate-limit observations while exercising genuine v3.6 logic.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from decompose_v36 import (
    GithubClient, PARENT_REF, child_body, child_title,
    index_marker, is_task_issue, load_plan, render_index
)
from lifecycle_v36 import ContractError, load_label, require_explicit_lab


def update_index(plan: dict, client: GithubClient, parent_no: int, child_links: dict[str, str]) -> str:
    """Durably synchronize the managed index comment on the parent issue."""
    existing_index = [c for c in client.list_comments(parent_no)
                      if index_marker(plan) in (c.get("body") or "")]
    if len(existing_index) > 1:
        raise ContractError("duplicate managed parent indexes; manual reconciliation required")
    proposed_index = render_index(plan, child_links)
    if not existing_index:
        client.create_comment(parent_no, proposed_index)
        return "created"
    elif existing_index[0].get("body") != proposed_index:
        client.update_comment(existing_index[0]["id"], proposed_index)
        return "updated"
    return "unchanged"


def run_bounded_decomposition(plan: dict, client: GithubClient, *,
                              apply: bool = False,
                              batch_size: int = 15,
                              item_delay_seconds: float = 4.0,
                              batch_delay_seconds: float = 60.0) -> dict:
    """Execute decomposition in bounded batches with controlled pacing."""
    match = PARENT_REF.fullmatch(plan["parent"])
    if not match or match[1] != client.repo:
        raise ContractError("parent repository mismatch")
    parent_no = int(match[2])

    issues = client.list_issues()
    child_links: dict[str, str] = {}
    missing = []
    for task in plan["tasks"]:
        matches = [x for x in issues if is_task_issue(x, task, plan["parent"])]
        if len(matches) > 1:
            raise ContractError(f"ambiguous duplicate child issues for {task['task_id']}")
        if matches:
            child_links[task["task_id"]] = matches[0].get("html_url")
        else:
            missing.append(task)

    telemetry = {
        "parent": plan["parent"],
        "plan": plan["plan_version"],
        "total_tasks": len(plan["tasks"]),
        "already_existing": len(child_links),
        "total_missing": len(missing),
        "batches_executed": 0,
        "items_created": 0,
        "latencies_seconds": [],
        "dry_run": not apply,
        "index_actions": []
    }

    if not missing or not apply:
        if apply:
            action = update_index(plan, client, parent_no, child_links)
            telemetry["index_actions"].append(action)
        return telemetry

    total_missing_count = len(missing)
    num_batches = (total_missing_count + batch_size - 1) // batch_size

    for b_idx in range(num_batches):
        batch = missing[b_idx * batch_size: (b_idx + 1) * batch_size]
        print(f"Executing batch {b_idx + 1}/{num_batches} ({len(batch)} tasks)...", flush=True)

        for task in batch:
            title = child_title(task)
            body = child_body(task, plan)
            t0 = time.time()
            issue = client.create_issue(title, body)
            duration = time.time() - t0
            telemetry["latencies_seconds"].append(duration)
            telemetry["items_created"] += 1
            child_links[task["task_id"]] = issue.get("html_url")
            print(f"  Created {task['task_id']} in {duration:.2f}s: {issue.get('html_url')}", flush=True)

            if item_delay_seconds > 0 and task != batch[-1]:
                time.sleep(item_delay_seconds)

        telemetry["batches_executed"] += 1

        # Intermediate index update after each batch to preserve index durability
        action = update_index(plan, client, parent_no, child_links)
        telemetry["index_actions"].append(action)

        if b_idx < num_batches - 1 and batch_delay_seconds > 0:
            print(f"Batch {b_idx + 1} complete. Pacing pause for {batch_delay_seconds}s...", flush=True)
            time.sleep(batch_delay_seconds)

    return telemetry


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="v3.6 bounded rate-controlled decomposition")
    p.add_argument("--label", required=True)
    p.add_argument("--plan", required=True)
    p.add_argument("--lab", help="explicit Writable lab: repository")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--confirm-scope", default="", help="exact owner/repo#parent required for --apply")
    p.add_argument("--batch-size", type=int, default=15)
    p.add_argument("--item-delay", type=float, default=4.0)
    p.add_argument("--batch-delay", type=float, default=60.0)
    args = p.parse_args(argv)

    try:
        label = load_label(args.label)
        plan = load_plan(args.plan, label)
        require_explicit_lab(label, plan["parent"], args.lab)

        token = os.environ.get("GITHUB_TOKEN")
        if args.apply and (args.confirm_scope != plan["parent"] or not token):
            raise ContractError("write refused: --confirm-scope exact parent and GITHUB_TOKEN are required")

        client = GithubClient(PARENT_REF.fullmatch(plan["parent"])[1], token=token)
        res = run_bounded_decomposition(
            plan, client,
            apply=args.apply,
            batch_size=args.batch_size,
            item_delay_seconds=args.item_delay,
            batch_delay_seconds=args.batch_delay
        )
        print(json.dumps(res, indent=2))
    except ContractError as exc:
        print(f"v3.6 pacing harness error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
