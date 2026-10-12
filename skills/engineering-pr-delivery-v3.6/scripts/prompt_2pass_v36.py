#!/usr/bin/env python3
"""v3.6 WP6: independent two-pass execution prompt generator.

Pass 1 = plan the next evidence-grounded task. Pass 2 = perform/test/publish.
This is NOT a BuddyRunner 1a/1b/2 review loop or a combined mode switcher.
"""
from __future__ import annotations

import argparse

from decompose_v36 import GithubClient, PARENT_REF, load_plan
from lifecycle_v36 import ContractError, load_label, require_explicit_lab
from successor_v36 import build_packet, render_markdown


def generate_two_pass(packet: dict, task_id: str) -> str:
    """Preserve approved Owner words and real source links, never invent acceptance."""
    matches = [t for t in packet["tasks"] if t["task_id"] == task_id]
    if len(matches) != 1 or not matches[0]["issue"]:
        raise ContractError("two-pass target must have exactly one real child")
    task = matches[0]
    return (
        "V36_TWO_PASS_EXECUTION_GENERATOR_V1\n"
        "Purpose: convert GitHub-only Owner intent into ONE bounded task execution "
        "without requiring an outgoing agent conversation. Two separate passes.\n\n"
        + render_markdown(packet) +
        f"Selected task: {task['task_id']} ({task['outcome']}); child: {task['issue']}; "
        f"provider status: {task['status']}.\n"
        "PASS 1 — Evidence-grounded plan (no product edits): Read the approved "
        "Owner aim, parent plan, selected child AC and current exact GitHub PR head. "
        "Identify the earliest unproven outcome boundary and a minimal command/test "
        "with observable success/failure. State code ownership, input provenance "
        "and an explicit stop/rollback check. Do not count CURRENT_EVIDENCE as "
        "accepted completion. Output PLAN_UPDATE on the existing parent if authorized.\n"
        "PASS 2 — Authorized execution and real task proof: Re-read exact head "
        "and current child issue, implement only the selected plan in independent "
        "v3.6 code, run real tests and trigger the lab event automatically. "
        "Observe GitHub-run URL and actual issue/PR title GET readback. Publish "
        "canonical TASK_EVIDENCE beginning Outcome, For the user, Proof on the "
        "selected child issue; state PASS/FAIL, exact SHA and next. Stop on "
        "wrong repo, stale SHA, untrusted source or permission failure; preserve "
        "the full fail history. Do not merge or assert Owner acceptance.\n"
        "Oracle: the same child has exact-head proof, independent hosted run, "
        "title transition and zero-change replay; otherwise report PARTIAL, "
        "not DONE. Two passes only; no reviewer echo loop.\n"
    )


def main(argv=None):
    parser=argparse.ArgumentParser(description="standalone v3.6 TWO-pass executor generator")
    parser.add_argument("--label",required=True)
    parser.add_argument("--plan",required=True)
    parser.add_argument("--lab",help="selected label Writable lab: repo for lab parent")
    parser.add_argument("--task-id",required=True)
    parser.add_argument("--pr",type=int,action="append",required=True)
    args=parser.parse_args(argv)
    try:
        label=load_label(args.label)
        plan=load_plan(args.plan,label)
        require_explicit_lab(label,plan["parent"],args.lab)
        client=GithubClient(PARENT_REF.fullmatch(plan["parent"])[1])
        client.get_pr=lambda n:client.request("GET",f"/pulls/{n}")
        print(generate_two_pass(build_packet(label,plan,client,args.pr),args.task_id),end="")
    except ContractError as err:
        parser.error(str(err))
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
