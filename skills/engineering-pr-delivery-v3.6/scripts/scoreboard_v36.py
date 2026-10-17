#!/usr/bin/env python3
"""V36-ECO-03: read-only smart scoreboard over the ECO-02 read model (dry-run render only).

Dimensions stay independent and are never inferred from each other:
  E  native evidence status (snapshot_v36), per task and as current/total of the plan's tasks;
  A  chain accounting: NOT_EVALUATED until the #401 chain is admitted (#409 Q13);
  V  verification: NOT_EVALUATED; the native verified_complete is a constant 0, not data;
  acceptance: always NOT_EVALUATED; only the Owner accepts.
A claim shown as qualified is the A14 structural check of the author's self-check, not truth.
Nothing here writes to GitHub. MANAGED_BEGIN/END name the one region a future, separately
authorised writer (ECO-05) may own; text outside it is never touched.
"""
from __future__ import annotations
import argparse
import json
from datetime import datetime

SCHEMA = "v36.scoreboard/v1"
MANAGED_BEGIN = "<!-- v36-scoreboard:begin (managed; text outside is never changed) -->"
MANAGED_END = "<!-- v36-scoreboard:end -->"
NOT_EVALUATED = {
    "A": "NOT_EVALUATED: #401 chain accounting not admitted (#409 Q13)",
    "V": "NOT_EVALUATED: native verified_complete is a constant 0, not verification data",
    "acceptance": "NOT_EVALUATED: only the Owner accepts",
}
FROM_ECO02B = "UNKNOWN: not in the read model yet (ECO-02b)"
TITLE_NOTE = "A title or this board is a projection of the sources above, not engineering truth."


def parse_time(value):
    try:
        stamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return stamp if stamp.tzinfo else None


def source_age_minutes(task, observed):
    """Minutes since the newest source used for this task changed; None when unknown."""
    stamps = [parse_time(s.get("updated_at")) for s in task.get("sources_read") or []]
    stamps = [s for s in stamps if s]
    now = parse_time(observed)
    if not stamps or not now:
        return None
    return int((now - max(stamps)).total_seconds() // 60)


def next_step(task, pending):
    """Exact next actor/action, in a fixed precedence, with its source."""
    if task["status"] in ("PROVIDER_UNAVAILABLE", "UNKNOWN", "UNKNOWN_PR"):
        return {"actor": "coordinator", "action": "re-read the unavailable source", "source": task["status"]}
    if task["status"] in ("MISSING_CHILD", "AMBIGUOUS_CHILD"):
        return {"actor": "coordinator", "action": "resolve the task's one child issue", "source": task["status"]}
    blocking = [p for p in pending if p["prevents_done"]]
    if blocking:
        p = blocking[0]
        return {"actor": p["owner"], "action": p["next"], "source": "pending: " + p["what"]}
    if task["status"] != "CURRENT_EVIDENCE":
        return {"actor": "implementer", "action": "publish current evidence", "source": task["status"]}
    if not task["claim_qualified"]:
        return {"actor": "implementer", "action": "fix: " + task["reasons"][0], "source": "self-check"}
    return {"actor": "coordinator", "action": "read the companion; independent check; Owner decides acceptance",
            "source": "claim structurally qualified"}


def task_row(task, observed, all_pending):
    check = task.get("self_check") or {}
    pending = [p for p in all_pending if p["task_id"] == task["task_id"]]
    return {
        "task_id": task["task_id"], "issue": task.get("issue"), "pr": task.get("pr"),
        "evidence": task.get("evidence"), "E": task["status"], **NOT_EVALUATED,
        "claim": check.get("claim", "NONE"), "claim_qualified": task["claim_qualified"],
        "qualification_basis": task.get("qualification_basis"), "gaps": task.get("reasons", []),
        "done_when": check.get("done_when"), "pending": pending,
        "candidate_matches": task.get("self_check_matches_candidate"),
        "source_age_minutes": source_age_minutes(task, observed),
        "user_outcome": FROM_ECO02B, "implementation_crux": FROM_ECO02B, "original_input": FROM_ECO02B,
        "next": next_step(task, pending),
    }


def board(readmodel):
    """Pure projection of one read model. Totals use only the plan's own tasks."""
    if readmodel.get("schema") != "v36.readmodel/v1":
        raise ValueError("expected a v36.readmodel/v1 document")
    observed = readmodel.get("observed_at")
    rows = [task_row(t, observed, readmodel.get("pending", [])) for t in readmodel.get("tasks", [])]
    complete = bool(readmodel.get("read_complete"))
    native = readmodel.get("native") or {}
    return {
        "schema": SCHEMA, "observed_at": observed, "plan": readmodel.get("plan"),
        "parent": readmodel.get("parent"), "read_complete": complete,
        "unread_sources": readmodel.get("unread_sources", []),
        "totals": {"denominator": "tasks in this plan", "tasks": len(rows),
                   "E_current": sum(r["E"] == "CURRENT_EVIDENCE" for r in rows),
                   "E_stale": sum(r["E"] == "STALE_EVIDENCE" for r in rows),
                   "claims_qualified": sum(r["claim_qualified"] for r in rows),
                   "native_total_matches": native.get("total") == len(rows) if native else None,
                   "partial": not complete},
        **NOT_EVALUATED, "rows": rows, "title_note": TITLE_NOTE,
        "managed_region": [MANAGED_BEGIN, MANAGED_END],
    }


def cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def render_markdown(b):
    """Dry-run Markdown inside the managed region markers."""
    t = b["totals"]
    head = ("**INCOMPLETE READ** - unread: %s. Totals below are partial.\n\n" % ", ".join(b["unread_sources"])
            if not b["read_complete"] else "")
    lines = [MANAGED_BEGIN, "### v3.6 scoreboard - %s" % cell(b["plan"]), "", head +
             "Observed %s. E current %d/%d (stale %d) over %s. Claims structurally qualified: %d. "
             "A, V and acceptance: NOT_EVALUATED." % (b["observed_at"], t["E_current"], t["tasks"],
                                                       t["E_stale"], t["denominator"], t["claims_qualified"]),
             "", "| Task | E | Claim | Qualified | Gaps | Next | Age (min) |", "|---|---|---|---|---|---|---|"]
    for r in b["rows"]:
        nxt = "%s: %s" % (r["next"]["actor"], r["next"]["action"])
        age = "UNKNOWN" if r["source_age_minutes"] is None else r["source_age_minutes"]
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            cell(r["task_id"]), r["E"], r["claim"], "yes" if r["claim_qualified"] else "no",
            cell("; ".join(r["gaps"]) or "none"), cell(nxt), age))
    lines += ["", "_%s A: %s V: %s_" % (TITLE_NOTE, b["A"], b["V"]), MANAGED_END]
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description="v3.6 read-only scoreboard (dry-run) from a read-model JSON file")
    p.add_argument("--readmodel", required=True, help="output of readmodel_v36.py")
    p.add_argument("--markdown", action="store_true", help="print the dry-run Markdown instead of JSON")
    args = p.parse_args()
    with open(args.readmodel, encoding="utf-8") as f:
        b = board(json.load(f))
    print(render_markdown(b) if args.markdown else json.dumps(b, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
