#!/usr/bin/env python3
"""v3.6 WP5: standalone GitHub-only cold successor packet and BuddyRunner v1.6 prompts.

Pure renderers and read-only GitHub API operations. Does not import prior skills,
invoke agents, publish evidence, or grant implementation/review authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re

from decompose_v36 import GithubClient, PARENT_REF, load_plan
from lifecycle_v36 import ContractError, load_label, require_explicit_lab
from snapshot_v36 import snapshot
from successor_context_v36 import ContextError, attach as attach_continuity, load_input as load_continuity_input, render as render_continuity

HEX40 = re.compile(r"^[0-9a-f]{40}$")
PHASES = frozenset({"1a", "1b", "2", "Y"})


def build_packet(label: dict, plan: dict, client, pr_numbers: list[int]) -> dict:
    """All facts come from approved label, checked plan and current GitHub reads."""
    match = PARENT_REF.fullmatch(plan["parent"])
    if not match or client.repo != match[1]:
        raise ContractError("cold successor repository mismatch")
    if (plan["label"]["work"], plan["label"]["version"], plan["label"]["label_sha"]) != (
        label["work"], label["version"], label["label_sha"]
    ):
        raise ContractError("cold successor label/plan mismatch")
    report = snapshot(plan, client)
    parent = client.request("GET", f"/issues/{match[2]}")
    if parent.get("number") != int(match[2]):
        raise ContractError("missing real GitHub parent")
    comments = client.list_comments(int(match[2]))
    marker = f"<!-- v36-plan-index:{plan['plan_version']} parent:{plan['parent']} -->"
    indices = [x for x in comments if marker in (x.get("body") or "")]
    if len(indices) != 1:
        raise ContractError("missing or ambiguous real managed parent index")
    index = indices[0]
    if label["version"] not in (index.get("body") or "") or label["label_sha"] not in index["body"]:
        raise ContractError("parent index uses a stale Owner label")
    prs = []
    if len(set(pr_numbers)) != len(pr_numbers) or any(
        not isinstance(n, int) or n < 1 for n in pr_numbers
    ):
        raise ContractError("PR selection must be unique positive numbers")
    for number in pr_numbers:
        pr = client.get_pr(number)
        head = pr.get("head", {}).get("sha") if isinstance(pr, dict) else None
        if (not HEX40.fullmatch(head or "") or pr.get("number") != number or
            not isinstance(pr.get("title"), str)):
            raise ContractError(f"live PR #{number} unavailable or malformed")
        prs.append({"number": number, "url": f"https://github.com/{client.repo}/pull/{number}",
                    "head": head, "state": pr.get("state"), "draft": bool(pr.get("draft")),
                    "merged": bool(pr.get("merged")), "title": pr["title"]})
    task_rows = []
    spec_by_id = {t["task_id"]: t for t in plan["tasks"]}
    for t in report["tasks"]:
        spec = spec_by_id[t["task_id"]]
        task_rows.append({"task_id": t["task_id"], "outcome": t["outcome"],
                          "issue": t["issue"], "status": t["status"],
                          "evidence": t["evidence"], "proof_pr": t["pr"],
                          "acceptance": spec["acceptance"],
                          "for_user": spec["for_user"], "accepted": False})
    pending = [t["task_id"] for t in task_rows if t["status"] != "CURRENT_EVIDENCE"]
    return {
        "schema": "V36_COLD_SUCCESSOR_V1", "parent": plan["parent"],
        "parent_url": f"https://github.com/{client.repo}/issues/{match[2]}",
        "parent_title": parent["title"], "plan": plan["plan_version"],
        "label": {"work": label["work"], "version": label["version"],
                  "label_sha": label["label_sha"], **label["label"]},
        "index_url": index.get("html_url") or index.get("url"),
        "source_of_truth": "GitHub issue comments + exact PR heads; not previous chats",
        "snapshot": {"current_evidence": report["current_evidence"],
                     "stale_evidence": report["stale_evidence"],
                     "total": report["total"], "accepted_complete": 0},
        "tasks": task_rows, "prs": prs,
        "next": pending[0] if pending else "INDEPENDENT_ACCEPTANCE_REQUIRED",
        "unproven": ["Current evidence is not accepted task completion",
                     "O5 cold agent must independently continue from GitHub",
                     "No release or merge authority follows from this packet"]
    }


def render_markdown(packet: dict) -> str:
    """Portable packet: links and Owner sentences survive verbatim."""
    label = packet["label"]
    lines = ["<!-- v36-cold-successor-packet -->",
             "# V3.6 GitHub-only cold successor packet",
             f"Parent: {packet['parent_url']} — {packet['parent_title']}",
             f"Plan: {packet['plan']} | Index: {packet['index_url']}",
             f"Owner label: {label['work']}@{label['version']} ({label['label_sha']})",
             f"Problem: {label['problem']}",
             f"Main aim: {label['main_aim']}",
             f"Task aim: {label['task_aim']}",
             f"Done when: {label['done_when']}",
             "Owner constraints:"] + [f"- {s}" for s in label["owner_constraints"]]
    lines += ["Outcomes:"] + [f"- {k}: {v}" for k, v in label["outcomes"].items()]
    data = packet["snapshot"]
    lines += [f"Evidence: E{data['current_evidence']}/{data['total']}; stale={data['stale_evidence']}; accepted={data['accepted_complete']}",
              "Task | Outcome | Child | Source evidence | Status | Accepted",
              "--- | --- | --- | --- | --- | ---"]
    for row in packet["tasks"]:
        lines.append(f"{row['task_id']} | {row['outcome']} | {row['issue'] or 'UNKNOWN'} | "
                     f"{row['evidence'] or 'NONE'} | {row['status']} | NO")
        lines.append(f"  Acceptance for {row['task_id']}: {row['acceptance']}")
        lines.append(f"  For the user: {row['for_user']}")
    lines += ["Current PRs:"]
    for pr in packet["prs"]:
        lines.append(f"- {pr['url']} @ {pr['head']} | state={pr['state']} "
                     f"draft={pr['draft']} merged={pr['merged']} | {pr['title']}")
    lines += [f"Next: {packet['next']}", "Unknowns / stop conditions:"]
    lines.extend(f"- {u}" for u in packet["unproven"])
    lines += ["To continue without chats: refresh these GitHub issue/PR links, verify "
              "the current Owner label and exact PR head, then perform one authorized "
              "next step with its own task evidence. A title count is not approval."]
    return "\n".join(lines) + "\n"


def buddy_prompt(phase: str, *, handover_id: str, parent: str, assessed_sha: str,
                 evidence_url: str = "", body_digest: str = "") -> str:
    """V1.6 1a/1b/2 or optional one-shot Y; no agent execution or provider claims."""
    if phase not in PHASES or not handover_id.strip() or not PARENT_REF.fullmatch(parent):
        raise ContractError("invalid BuddyRunner phase, handover or parent")
    if not HEX40.fullmatch(assessed_sha):
        raise ContractError("BuddyRunner assessed commit requires exact 40-character SHA")
    if phase in ("2", "Y") and (not evidence_url.startswith("https://github.com/") or
                               not re.fullmatch(r"[0-9a-f]{64}", body_digest)):
        raise ContractError("reconciliation/intervention requires publication link and exact UTF-8 SHA256")
    common = (f"BuddyRunner v1.6 | handover={handover_id} | phase={phase}\n"
              f"GitHub parent: https://github.com/{parent.split('#')[0]}/issues/{parent.split('#')[1]}\n"
              f"Assessed exact head: {assessed_sha}\n"
              "Work only from the approved Owner label, current issue plan, child "
              "evidence and current GitHub source/CI. Never rely on prior chats. "
              "Preserve exact label words and distinguish current/stale evidence from acceptance.\n")
    if phase == "1a":
        return common + ("Outgoing G1: provide ONE successor-ready source-first investigation "
                         "prompt with explicit inputs/risks; do not implement. End 1a "
                         "| EXECUTION=HOLD | NEXT=G2 independently investigates and submits 1b.\n")
    if phase == "1b":
        return common + ("Incoming G2: independently inspect source and real provider state, "
                         "reconcile Owner outcome with alternatives; submit ONE proposal, no "
                         "product implementation or repeated questions. End 1b | SUBMITTED | "
                         "NEXT=G1 final reconciliation 2 | PRODUCT_IMPLEMENTATION=HOLD.\n")
    if phase == "2":
        return common + (f"Verified-by-executor 1b reference: {evidence_url}\n"
                         f"Claimed 1b exact-body sha256: {body_digest}\n"
                         "Outgoing G1: re-fetch and hash the exact body, reconcile with "
                         "Owner purpose and current source, deliver one bounded workpack "
                         "and twelve-section handover. Close predecessor involvement, "
                         "no further review loop. End 2 | HANDOVER=CLOSED | "
                         "NEXT=successor follows final direction under existing authorization "
                         "| PREDECESSOR=STOP.\n")
    return common + (f"Submitted Xb evidence: {evidence_url}\n"
                     f"Claimed exact-body sha256: {body_digest}\n"
                     "Designated buddy: independently verify exact evidence then give ONE "
                     "Y correction, CONTINUE or NO_CHANGE. Do not reopen 1a/1b/2 or claim "
                     "independent approval. No new review round.\n")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="v3.6 read-only GitHub successor and BuddyRunner")
    sub = p.add_subparsers(dest="mode", required=True)
    cold = sub.add_parser("cold", help="fetch GitHub-only evidence and render packet")
    cold.add_argument("--label", required=True)
    cold.add_argument("--plan", required=True)
    cold.add_argument("--lab", help="explicit lab repo from selected label when parent is lab")
    cold.add_argument("--pr", type=int, action="append", default=[])
    cold.add_argument("--continuity-chain", help="optional public reported-only C1 source index")
    cold.add_argument("--custody-manifest", help="optional pinned C2 source-pointer manifest")
    cold.add_argument("--stage2-freeze-verified", action="store_true", help="caller asserts independent stage2 disclosure authorization; this flag is not proof")
    buddy = sub.add_parser("buddy", help="render a read-only v1.6 stage prompt")
    buddy.add_argument("--phase", choices=sorted(PHASES), required=True)
    buddy.add_argument("--handover-id", required=True)
    buddy.add_argument("--parent", required=True)
    buddy.add_argument("--assessed-sha", required=True)
    buddy.add_argument("--evidence-url", default="")
    buddy.add_argument("--body-digest", default="")
    args = p.parse_args(argv)
    try:
        if args.mode == "cold":
            requested = bool(args.continuity_chain or args.custody_manifest)
            if requested and (not args.continuity_chain or not args.custody_manifest or
                              not args.stage2_freeze_verified):
                raise ContractError("C3 requires both source documents and independently verified stage2 freeze; caller flag is not verification")
            label = load_label(args.label)
            plan = load_plan(args.plan, label)
            require_explicit_lab(label, plan["parent"], args.lab)
            client = GithubClient(PARENT_REF.fullmatch(plan["parent"])[1])
            client.get_pr = lambda n: client.request("GET", f"/pulls/{n}")
            packet = build_packet(label, plan, client, args.pr)
            rendered = render_markdown(packet)
            if requested:
                try:
                    context = attach_continuity(packet, load_continuity_input(args.continuity_chain),
                                                load_continuity_input(args.custody_manifest))
                except (ContextError, OSError, ValueError) as exc:
                    raise ContractError("C3 CONTEXT_HOLD: " + str(exc)) from exc
                rendered += render_continuity(context)
            print(rendered, end="")
        else:
            print(buddy_prompt(args.phase, handover_id=args.handover_id,
                               parent=args.parent, assessed_sha=args.assessed_sha,
                               evidence_url=args.evidence_url,
                               body_digest=args.body_digest), end="")
    except ContractError as e:
        p.error(str(e))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
