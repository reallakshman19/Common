#!/usr/bin/env python3
"""v3.6 WP6: standalone three-pass cold successor falsification generator.

Pass 1 independently traces/attacks assumptions. Pass 2 implements the fix.
Pass 3 independently tests current GitHub acceptance; no predecessor loop.
"""
from __future__ import annotations

import argparse

from decompose_v36 import GithubClient, PARENT_REF, load_plan
from lifecycle_v36 import ContractError, load_label
from successor_v36 import build_packet, render_markdown


def generate_three_pass(packet: dict, task_id: str) -> str:
    """Require a falsifier and independent third pass, not two-pass with extra words."""
    matches=[t for t in packet["tasks"] if t["task_id"]==task_id]
    if len(matches)!=1 or not matches[0]["issue"]:
        raise ContractError("three-pass target must have exactly one real child")
    task=matches[0]
    return (
        "V36_THREE_PASS_INDEPENDENT_VALIDATION_GENERATOR_V1\n"
        "Purpose: cold-engineer independent failure analysis, bounded implementation, "
        "then independent real-provider acceptance. Three passes are mandatory.\n\n"
        + render_markdown(packet) +
        f"Selected child: {task['issue']}; task {task['task_id']} / {task['outcome']}; "
        f"observed status {task['status']}; proof {task['evidence'] or 'NONE'}.\n"
        "PASS 1 — Independent reconstruction and negative oracle: Ignore chat "
        "claims, fetch current Owner label and source at exact SHA; independently "
        "verify provider child and PR, and challenge predecessor assumptions. "
        "Design one negative/falsifying lab case with expected bad/stale/unknown "
        "state; publish no TASK_EVIDENCE just for a plan.\n"
        "PASS 2 — Bounded engineering work: After Pass 1 oracles, change only "
        "authorized v3.6 modules, preserve Owner wording and original input "
        "and historical GitHub evidence. Produce exact diff, tests and real "
        "action-run links. On fail, stop and fix before advancing.\n"
        "PASS 3 — Independent GitHub-only verification: A distinct evaluator "
        "not relying on earlier chats re-fetches Owner label, current source "
        "head, affected child issue and both related/unrelated PRs; runs positive "
        "and negative checks and tests automatic event→title readback plus "
        "zero-change replay. Confirm separate GitHub proof before describing "
        "any accepted progress, and never turn current evidence into completion "
        "without actual Owner acceptance. Publish exact-head TASK_EVIDENCE on "
        "the selected child if met; otherwise report NOT_PROVEN/FAILED with "
        "specific falsifier and next work.\n"
        "Oracle: three independent phase outputs, including a negative case "
        "and a genuinely independent third-pass readback by a new evaluator; "
        "any missing oracle means PARTIAL. No unified two/three mode and "
        "no repeated predecessor review.\n"
    )


def main(argv=None):
    parser=argparse.ArgumentParser(description="standalone v3.6 THREE-pass independent validator generator")
    parser.add_argument("--label",required=True)
    parser.add_argument("--plan",required=True)
    parser.add_argument("--task-id",required=True)
    parser.add_argument("--pr",type=int,action="append",required=True)
    args=parser.parse_args(argv)
    try:
        label=load_label(args.label)
        plan=load_plan(args.plan,label)
        client=GithubClient(PARENT_REF.fullmatch(plan["parent"])[1])
        client.get_pr=lambda n:client.request("GET",f"/pulls/{n}")
        print(generate_three_pass(build_packet(label,plan,client,args.pr),args.task_id),end="")
    except ContractError as err:
        parser.error(str(err))
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
