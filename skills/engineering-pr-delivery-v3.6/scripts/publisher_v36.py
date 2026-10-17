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

# ECO-04 attention grammar v1 is *display only*. It cannot grant work or acceptance.
# Parent display profile derives from the actual plan.parent repo: only the accepted
# v3.6 lab gets LAB; all other repos use non_lab. No schema or label changes.
ATTENTION_GRAMMAR = "v36.attention/v1"
LAB_REPO = "reallakshman19/relay-v36-e2e-lab"
MAX_TITLE = 256  # refuse, never destroy, a human's suffix to fit a prefix
URL_PR = re.compile(r"^https://github\.com/([^/]+/[^/]+)/pull/([1-9][0-9]*)$")
BRACKET = re.compile(r"\[([^\]\r\n]{1,64})\]")
OUTCOMES = re.compile(r"O[1-5](?:[/–-]O?[1-5])*")
ECOUNT = re.compile(r"E[0-9]+/[0-9]+")
OLD_COUNT = re.compile(r"[0-9]+/[0-9]+")
OWNED_WORDS = frozenset((
    "LAB", "DRAFT", "OPEN", "MERGED", "CLOSED", "EVIDENCED",
    "PLANNED", "PENDING", "UNATTRIBUTED", "STALE", "HOLD",
    "ORIGINALS_MISSING", "CHAIN_GAP", "OWNER_GATE", "UNKNOWN",
))


def is_owned_token(token):
    """Only tokens following our literal [V3.6] marker belong to us."""
    return token in OWNED_WORDS or bool(OUTCOMES.fullmatch(token) or
                                      ECOUNT.fullmatch(token) or OLD_COUNT.fullmatch(token))


def split_title(current: str, fallback: str) -> tuple[str, str]:
    """Return (foreign leading brackets, human suffix), without generic stripping.

    Foreign bracket tokens BEFORE the managed namespace retain their position;
    those AFTER it start human suffix. Adjacent repeated managed sequences collapse.
    No [V3.6] marker means all existing bracket text is human-owned.
    """
    if not isinstance(current, str):
        raise ContractError("missing GitHub title")
    pos, foreign = 0, []
    length = len(current)
    while pos < length:
        match = BRACKET.match(current, pos)
        if not match:
            break
        if match[1] == "V3.6":
            break
        foreign.append(match.group(0))
        pos = match.end()
        while pos < length and current[pos] == " ":
            pos += 1
    first = BRACKET.match(current, pos)
    if first and first[1] == "V3.6":
        pos = first.end()
        while pos < length:
            while pos < length and current[pos] == " ":
                pos += 1
            match = BRACKET.match(current, pos)
            if not match or not (match[1] == "V3.6" or is_owned_token(match[1])):
                break
            pos = match.end()
    return "".join(foreign), current[pos:].strip() or fallback


def title_tail(current: str, fallback: str) -> str:
    """Legacy helper: expose preserved human content, never discard foreign brackets."""
    prefix, tail = split_title(current, fallback)
    return (prefix + " " + tail).strip()


def compose_title(current: str, fallback: str, managed: str) -> str:
    """Refuse unsupported title length instead of silently cutting human words."""
    foreign, tail = split_title(current, fallback)
    title = foreign + managed + " " + tail
    if len(title) > MAX_TITLE:
        raise ContractError("projected title exceeds 256 characters; preserve human suffix and resolve manually")
    return title


def parent_display_profile(plan: dict) -> str:
    """Non-schema policy: only reallakshman19/relay-v36-e2e-lab renders LAB.

    The actual parent repository is authoritative; a label/plan option, guessed
    environment variable or current title cannot silently claim an approved lab.
    """
    parent = PARENT_REF.fullmatch(plan.get("parent", ""))
    if not parent:
        raise ContractError("invalid parent")
    return "lab" if parent[1] == LAB_REPO else "non_lab"


def validate_scoreboard(plan, report, scoreboard):
    """The optional ECO-03 board never upgrades native E or invents a PR link."""
    if scoreboard is None:
        return None
    if (not isinstance(scoreboard, dict) or scoreboard.get("schema") != "v36.scoreboard/v1"
            or scoreboard.get("parent") != plan["parent"]
            or scoreboard.get("plan") != plan["plan_version"]
            or scoreboard.get("label_sha") != plan["label"]["label_sha"]):
        raise ContractError("ECO-03 board source/scope mismatch")
    rows = scoreboard.get("rows")
    grouped = scoreboard.get("by_pr")
    if not isinstance(rows, list) or not isinstance(grouped, dict):
        raise ContractError("ECO-03 board missing rows or per-PR linkage")
    native = {r["task_id"]: r for r in report["tasks"]}
    if len(native) != len(report["tasks"]):
        raise ContractError("duplicate native task ID")
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or row.get("task_id") not in native:
            raise ContractError("ECO-03 board references an unrelated task")
        tid = row["task_id"]
        if tid in seen:
            raise ContractError("ECO-03 board duplicate task")
        seen.add(tid)
        if row.get("E") == "CURRENT_EVIDENCE" and (
                native[tid]["status"] != "CURRENT_EVIDENCE"
                or native[tid].get("pr") != row.get("pr")):
            raise ContractError("ECO-03 board attempts to promote native E or PR attribution")
    return {row["task_id"]: row for row in rows}


def pr_linkage(plan, report, pr_ref, scoreboard, board_rows):
    """PR-specific count: board-selected links when present, else native proof links.

    Board can have a zero-evidence PR-linked task, but its E cannot promote the
    native snapshot. Unknown/degraded provider data never becomes an evidenced task.
    """
    native = {r["task_id"]: r for r in report["tasks"]}
    board_group = (scoreboard.get("by_pr", {}).get(pr_ref)
                   if scoreboard is not None else None)
    if board_group is None:
        return [native[t["task_id"]] | {"E": native[t["task_id"]]["status"]}
                for t in plan["tasks"] if native[t["task_id"]].get("pr") == pr_ref]
    ids = board_group.get("task_ids")
    if not isinstance(ids, list) or len(ids) != len(set(ids)) or (
            board_group.get("tasks") != len(ids)):
        raise ContractError("inconsistent ECO-03 PR denominator")
    linked = []
    for tid in ids:
        row = board_rows.get(tid)
        if row is None or row.get("pr") != pr_ref:
            raise ContractError("ECO-03 PR references missing/foreign task")
        n = native[tid]
        effective = row["E"]
        if effective == "CURRENT_EVIDENCE" and (
                n["status"] != "CURRENT_EVIDENCE" or n.get("pr") != pr_ref):
            raise ContractError("ECO-03 PR evidence not native-qualified")
        linked.append(n | {"E": effective})
    if (board_group.get("E_current") != sum(t["E"] == "CURRENT_EVIDENCE" for t in linked)):
        raise ContractError("ECO-03 PR current count inconsistent")
    return linked


def title_attention(linked, board_rows=None):
    """Only actual task-local blockers get an attention token.

    Precedence: blocking pending HOLD > native/board STALE > explicit MISSING
    originals > admitted CHAIN_GAP > source UNKNOWN. Ordinary future Owner
    acceptance and not-yet-admitted #401 audit do not cause constant alarms.
    Full detail stays in ECO-03; the token and one source pointer are display only.
    """
    board_rows = board_rows or {}
    def observed(t):
        return board_rows.get(t["task_id"], {})
    for t in linked:
        for p in observed(t).get("pending", []) or []:
            if isinstance(p, dict) and p.get("prevents_done"):
                return {"signal": "HOLD", "source": "board:pending:" + str(p.get("what") or "UNKNOWN"),
                        "task_id": t["task_id"]}
    for t in linked:
        if t["E"] == "STALE_EVIDENCE":
            return {"signal": "STALE", "source": "native:STALE_EVIDENCE" if
                    t["status"] == "STALE_EVIDENCE" else "board:STALE_EVIDENCE",
                    "task_id": t["task_id"]}
    for t in linked:
        originals = observed(t).get("original_input") or {}
        if originals.get("input") == "MISSING":
            return {"signal": "ORIGINALS_MISSING", "source": "board:original_input:MISSING",
                    "task_id": t["task_id"]}
    for t in linked:
        audit = observed(t).get("A_detail") or {}
        if audit.get("status") == "EVALUATED" and audit.get("chain_gap") is True:
            return {"signal": "CHAIN_GAP", "source": "board:admitted_chain_gap", "task_id": t["task_id"]}
    unread = {"UNKNOWN", "UNKNOWN_PR", "PROVIDER_UNAVAILABLE", "HEAD_UNREAD", "SOURCE_MISMATCH"}
    for t in linked:
        if t["E"] in unread:
            return {"signal": "UNKNOWN", "source": "evidence:" + t["E"], "task_id": t["task_id"]}
    return {"signal": None, "source": None, "task_id": None}


def title_plan(plan: dict, issues: list[dict], pr: dict | None, report: dict,
               *, scoreboard: dict | None = None) -> list[dict]:
    """Pure title projection. No provider calls; board is optional read-only input.

    ECO-04 creates no second writer, never grants acceptance and preserves native
    PR state, plan outcome attribution, and current E counting boundaries.
    """
    if report["parent"] != plan["parent"] or report["label_sha"] != plan["label"]["label_sha"]:
        raise ContractError("snapshot/plan mismatch")
    parent = PARENT_REF.fullmatch(plan["parent"])
    if not parent:
        raise ContractError("invalid parent")
    profile = parent_display_profile(plan)
    board_rows = validate_scoreboard(plan, report, scoreboard)
    count = report["current_evidence"]
    total = report["total"]
    current_by_task = {x["task_id"]: x for x in report["tasks"]}
    updates = []
    parent_issue = next((x for x in issues if x.get("number") == int(parent[2])), None)
    if parent_issue is None:
        raise ContractError("parent issue absent")
    parent_marker = "[V3.6][LAB]" if profile == "lab" else "[V3.6]"
    new_parent = compose_title(parent_issue.get("title"), "Independent lifecycle acceptance",
                               f"{parent_marker}[E{count}/{total}]")
    updates.append({"kind": "issue", "number": int(parent[2]), "before": parent_issue["title"],
                    "after": new_parent, "display_profile": profile})
    for task in plan["tasks"]:
        matches = [x for x in issues if is_task_issue(x, task, plan["parent"])]
        if len(matches) != 1:
            raise ContractError("cannot title missing or ambiguous child")
        row = current_by_task[task["task_id"]]
        state = ("EVIDENCED" if row["status"] == "CURRENT_EVIDENCE"
                 else "STALE" if row["status"] == "STALE_EVIDENCE" else "PENDING")
        before = matches[0]["title"]
        new_title = compose_title(before, task["task_id"] + " — " + task["title"],
                                  f"[V3.6][{task['outcome']}][{state}]")
        updates.append({"kind": "issue", "number": matches[0]["number"],
                        "before": before, "after": new_title})
    if pr is not None:
        if not isinstance(pr.get("number"), int) or not isinstance(pr.get("head"), dict):
            raise ContractError("malformed PR")
        if pr.get("merged") is True:
            status = "MERGED"
        elif pr.get("state") == "closed":
            status = "CLOSED"
        elif pr.get("state") == "open":
            status = "DRAFT" if pr.get("draft") is True else "OPEN"
        else:
            raise ContractError("PR state unavailable or unsupported; refusing title projection")
        pr_ref = f"https://github.com/{parent[1]}/pull/{pr['number']}"
        linked = pr_linkage(plan, report, pr_ref, scoreboard, board_rows)
        linked_ids = {t["task_id"] for t in linked}
        outcomes = "/".join(sorted({t["outcome"] for t in plan["tasks"]
                                    if t["task_id"] in linked_ids})) or "UNATTRIBUTED"
        pr_count = sum(t["E"] == "CURRENT_EVIDENCE" for t in linked)
        pr_total = len(linked)
        attention = title_attention(linked, board_rows)
        token = f"[{attention['signal']}]" if attention["signal"] else ""
        managed = f"[V3.6][{outcomes}][{status}][E{pr_count}/{pr_total}]{token}"
        after = compose_title(pr.get("title"), "Lifecycle work", managed)
        updates.append({"kind": "pr", "number": pr["number"], "before": pr["title"],
                        "after": after, "head_sha": pr["head"].get("sha"),
                        "attention_grammar": ATTENTION_GRAMMAR, "attention": attention,
                        "pr_e_denominator": pr_total, "pr_e_current": pr_count})
    return updates


def calculate(plan: dict, client, pr_number: int | None = None,
              *, scoreboard: dict | None = None) -> dict:
    """All reads are fresh. No GET failure turns into a completed task."""
    repo = PARENT_REF.fullmatch(plan["parent"])[1]
    if client.repo != repo:
        raise ContractError("wrong repository")
    issues = client.list_issues()
    if not hasattr(client, "get_pr"):
        client.get_pr = lambda n: client.request("GET", f"/pulls/{n}")
    report = snapshot(plan, client)
    pr = client.get_pr(pr_number) if pr_number is not None else None
    updates = title_plan(plan, issues, pr, report, scoreboard=scoreboard)
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
    parser.add_argument("--scoreboard", help="optional ECO-03 board JSON; dry-run projection only")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm-scope", default="")
    args = parser.parse_args(argv)
    if args.scoreboard and args.apply:
        parser.error("ECO-04 board projection is dry-run only; ECO-05 write gate is not implemented")
    try:
        label = load_label(args.label)
        plan = load_plan(args.plan, label)
        require_explicit_lab(label, plan["parent"], args.lab)
        repo = PARENT_REF.fullmatch(plan["parent"])[1]
        token = os.environ.get("GITHUB_TOKEN")
        if args.apply and (args.confirm_scope != plan["parent"] or not token):
            raise ContractError("write requires token and exact --confirm-scope")
        client = GithubClient(repo, token)
        if args.scoreboard:
            try:
                with open(args.scoreboard, encoding="utf-8") as f:
                    board_input = json.load(f)
            except (OSError, json.JSONDecodeError) as exc:
                raise ContractError(f"unreadable ECO-03 scoreboard: {exc}") from exc
        else:
            board_input = None
        result = calculate(plan, client, args.pr, scoreboard=board_input)
        applied = apply_projection(result, client, confirm_scope=args.confirm_scope, allow_write=args.apply)
        print(json.dumps({"projection": result, "write": applied}, indent=2, sort_keys=True))
        return 0
    except ContractError as exc:
        parser.error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
