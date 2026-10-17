#!/usr/bin/env python3
"""V36-ECO-03: pure read-only scoreboard over ECO-02b; no provider writes.

E = native current evidence, never test success or acceptance.
A = NOT_EVALUATED until the #401 11-category audit is admitted.
V = NOT_EVALUATED without external source-attestation evidence.
Acceptance = NOT_EVALUATED without an authorised sourced Owner decision.

Only plan-selected tasks enter denominators. PR/child views are intersections
of that selection with verified same-repository links; repeated test suites
are never summed. Incomplete provider reads are not zeros.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone

SCHEMA = "v36.scoreboard/v1"
MANAGED_BEGIN = "<!-- v36-scoreboard:begin (managed; text outside is never changed) -->"
MANAGED_END = "<!-- v36-scoreboard:end -->"
NOT_EVALUATED = {
    "A": "NOT_EVALUATED: #401 chain accounting not admitted (#409 Q13)",
    "V": "NOT_EVALUATED: no external source attestation; native verified_complete=0 is a constant",
    "acceptance": "NOT_EVALUATED: no authorised acceptance-source reader; only the Owner accepts",
}
CATEGORIES = (
    "ROOT_OWNER_INTENT", "OWNER_AMENDMENTS", "ORIGINAL_INPUT",
    "COMPLETE_GOLDEN", "MEASURED_BENCHMARK", "SOURCE_IMPLEMENTATION_CRUX",
    "AGENT_CONTRIBUTIONS", "DECISION_AND_PARKED_IDEAS", "KNOWN_FAILURES",
    "SELECTED_NEXT_VERIFICATION", "TECHNICAL_HANDOVER",
)
UNKNOWN_OUTCOME = "UNKNOWN: original Owner outcome/amendments not in ECO-02b read model"
UNKNOWN_CRUX = "UNKNOWN: source implementation crux not in ECO-02b read model"
TITLE_NOTE = "A title or this board is a projection of cited sources, not engineering truth."
PARENT = re.compile(r"^(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#[1-9][0-9]*$")
ISSUE = re.compile(r"^https://github\.com/(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/issues/[1-9][0-9]*$")
PR = re.compile(r"^https://github\.com/(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/pull/[1-9][0-9]*$")


def parse_time(value):
    if not isinstance(value, str):
        return None
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, OverflowError):
        return None
    return stamp.astimezone(timezone.utc) if stamp.tzinfo else None


def source_age_minutes(task, observed):
    """Newest author-companion source age; missing or future timestamps remain UNKNOWN."""
    stamps = [parse_time(s.get("updated_at")) for s in (task.get("sources_read") or [])
              if isinstance(s, dict)]
    stamps = [s for s in stamps if s is not None]
    now = parse_time(observed)
    if not stamps or now is None or max(stamps) > now:
        return None
    return int((now - max(stamps)).total_seconds() // 60)


def proper_link(url, repo, regex):
    hit = regex.fullmatch(url) if isinstance(url, str) else None
    return bool(hit and hit["repo"] == repo)


def status_and_gaps(task, repo):
    """Fail closed for a contradictory model, without altering the native input."""
    native = task.get("status", "UNKNOWN")
    status = native
    gaps = list(task.get("reasons") or [])
    issue, pr = task.get("issue"), task.get("pr")
    child_valid = proper_link(issue, repo, ISSUE) if issue is not None else False
    pr_valid = proper_link(pr, repo, PR) if pr is not None else False
    if issue is not None and not child_valid:
        status = "SOURCE_MISMATCH"
        gaps.append("foreign child issue or malformed child URL; cannot attribute native evidence")
    if pr is not None and not pr_valid:
        status = "SOURCE_MISMATCH"
        gaps.append("foreign PR or malformed PR URL; cannot attribute PR evidence")
    if issue is None and native in ("CURRENT_EVIDENCE", "STALE_EVIDENCE"):
        status = "SOURCE_MISMATCH"
        gaps.append("missing child issue for evidence status")
    if pr is None and native in ("CURRENT_EVIDENCE", "STALE_EVIDENCE"):
        status = "SOURCE_MISMATCH"
        gaps.append("missing PR for evidence status")
    if status != "SOURCE_MISMATCH" and task.get("head_matches_candidate") is False:
        status = "STALE_EVIDENCE"
        gaps.append("observed PR head differs from candidate; current evidence is invalidated")
    if status == "CURRENT_EVIDENCE" and (not task.get("observed_head")
                                         or not task.get("candidate_sha")):
        status = "HEAD_UNREAD"
        gaps.append("current evidence cannot be displayed without an observed and candidate head")
    return status, gaps, child_valid, pr_valid


def next_step(task, pending):
    """Named actor/action under fixed precedence; source of the instruction is visible."""
    status = task["status"]
    if status in ("SOURCE_MISMATCH", "MISSING_CHILD", "AMBIGUOUS_CHILD"):
        return {"actor": "coordinator", "action": "resolve this task's owned child/repository binding",
                "source": status}
    if status in ("PROVIDER_UNAVAILABLE", "UNKNOWN", "UNKNOWN_PR", "HEAD_UNREAD"):
        return {"actor": "coordinator", "action": "re-read the unavailable source",
                "source": status}
    if status == "STALE_EVIDENCE":
        return {"actor": "implementer", "action": "publish current evidence bound to the observed PR head",
                "source": status}
    blocking = [p for p in pending if p.get("prevents_done")]
    if blocking:
        p = blocking[0]
        return {"actor": p.get("owner") or "UNKNOWN",
                "action": p.get("next") or "resolve pending action",
                "source": "pending: " + str(p.get("what") or "UNKNOWN")}
    if status != "CURRENT_EVIDENCE":
        return {"actor": "implementer", "action": "publish current evidence",
                "source": status}
    if not task.get("claim_qualified"):
        reasons = task.get("reasons") or ["self-check requires independent verification"]
        return {"actor": "implementer", "action": "fix: " + str(reasons[0]),
                "source": "self-check"}
    return {"actor": "coordinator",
            "action": "read companion, verify originals and scope independently; request Owner decision",
            "source": "claim structurally qualified; not accepted"}


def source_revisions(task):
    """Source identities from ECO-02b, not an endorsement of their content."""
    return [
        {k: s.get(k) for k in ("comment_id", "url", "updated_at", "body_sha256")
         if k in s}
        for s in (task.get("sources_read") or []) if isinstance(s, dict)
    ]


def task_row(task, observed, all_pending, repo):
    task_id = task.get("task_id", "UNKNOWN")
    status, gaps, child_ok, pr_ok = status_and_gaps(task, repo)
    check = task.get("self_check") or {}
    pending = [p for p in all_pending if isinstance(p, dict) and p.get("task_id") == task_id]
    view = {**task, "status": status, "reasons": gaps,
            "claim_qualified": bool(task.get("claim_qualified")) and status == "CURRENT_EVIDENCE"}
    inputs = task.get("inputs") if isinstance(task.get("inputs"), dict) else {}
    originals = {k: inputs.get(k, "UNKNOWN") for k in ("input", "golden", "benchmark")}
    originals["attribution"] = inputs.get("attribution", "UNKNOWN")
    if originals["input"] == "UNKNOWN":
        gaps.append("original input UNKNOWN; no source-authenticated input identification")
    if originals["golden"] == "UNKNOWN":
        gaps.append("complete/partial golden UNKNOWN")
    if originals["benchmark"] == "UNKNOWN":
        gaps.append("benchmark/oracle UNKNOWN")
    if not task.get("observed_head") and task.get("pr"):
        gaps.append("observed PR head UNKNOWN")
    return {
        "task_id": task_id, "outcome": task.get("outcome", "UNKNOWN"),
        "issue": task.get("issue"), "pr": task.get("pr"),
        "evidence": task.get("evidence"), "E": status, "native_E": task.get("status"),
        **NOT_EVALUATED,
        "A_detail": {"status": "NOT_EVALUATED", "source": "#401 not admitted"},
        "claim": check.get("claim", "NONE"), "claim_qualified": view["claim_qualified"],
        "qualification_basis": task.get("qualification_basis"),
        "done_when": check.get("done_when"), "gaps": gaps, "pending": pending,
        "candidate_matches": task.get("self_check_matches_candidate"),
        "candidate_sha": task.get("candidate_sha"),
        "observed_head": task.get("observed_head"),
        "head_matches_candidate": task.get("head_matches_candidate"),
        "source_age_minutes": source_age_minutes(task, observed),
        "source_revisions": source_revisions(task),
        "source_history_hops": task.get("issue_hops") or [],
        "owner_inputs": task.get("owner_inputs") or [],
        "user_outcome": UNKNOWN_OUTCOME, "implementation_crux": UNKNOWN_CRUX,
        "original_input": originals,
        "verification_scope": {
            "reported_done_when": check.get("done_when"),
            "structural_self_check": "QUALIFIED" if view["claim_qualified"] else "NOT_QUALIFIED",
            "run_verified": "NOT_EVALUATED", "tested_head": "UNKNOWN",
            "note": "SELF-CHECK is author-reported; native E is a source/head binding, not test validation",
        },
        "child_attributed": child_ok,
        "pr_attributed": child_ok and pr_ok,
        "child_denominator": None, "pr_denominator": None,
        "next": next_step(view, pending),
    }


def _group(rows, field):
    groups = {}
    for r in rows:
        valid = r["child_attributed"] if field == "issue" else r["pr_attributed"]
        if not valid or not r.get(field):
            continue
        link = r[field]
        g = groups.setdefault(link, {"tasks": 0, "E_current": 0, "E_stale": 0,
                                     "task_ids": [], "heads": [], "counting_unit": "linked plan task"})
        g["tasks"] += 1
        g["E_current"] += r["E"] == "CURRENT_EVIDENCE"
        g["E_stale"] += r["E"] == "STALE_EVIDENCE"
        g["task_ids"].append(r["task_id"])
        head = r.get("observed_head")
        if head and head not in g["heads"]:
            g["heads"].append(head)
    for r in rows:
        if field == "issue":
            r["child_denominator"] = groups[r[field]]["tasks"] if r.get(field) in groups else None
        else:
            r["pr_denominator"] = groups[r[field]]["tasks"] if r.get(field) in groups and r["pr_attributed"] else None
    return groups


def board(readmodel):
    """Pure projection; no source fetch, provider mutation, or derived approval."""
    if not isinstance(readmodel, dict) or readmodel.get("schema") != "v36.readmodel/v1":
        raise ValueError("expected a v36.readmodel/v1 document")
    tasks = readmodel.get("tasks", [])
    pending = readmodel.get("pending") or []
    if not isinstance(tasks, list) or not isinstance(pending, list) or any(not isinstance(t, dict) for t in tasks):
        raise ValueError("malformed readmodel tasks/pending; cannot produce a trustworthy board")
    observed = readmodel.get("observed_at")
    match = PARENT.fullmatch(readmodel.get("parent") or "")
    repo = match["repo"] if match else None
    rows = [task_row(t, observed, pending, repo) for t in tasks]
    ids = [r["task_id"] for r in rows]
    duplicate = len(set(ids)) != len(ids)
    incomplete = (readmodel.get("read_complete") is not True or not match or duplicate
                  or any(r["E"] in ("SOURCE_MISMATCH", "HEAD_UNREAD") for r in rows)
                  or (readmodel.get("native") or {}).get("total", len(rows)) != len(rows))
    by_child = _group(rows, "issue")
    by_pr = _group(rows, "pr")
    native = readmodel.get("native") or {}
    unread = list(readmodel.get("unread_sources") or [])
    if not match:
        unread.append("parent:missing_or_invalid")
    if duplicate:
        unread.append("task_ids:duplicate")
    count = len(rows) if rows or not incomplete else None
    return {
        "schema": SCHEMA, "observed_at": observed, "plan": readmodel.get("plan"),
        "parent": readmodel.get("parent"), "label_sha": readmodel.get("label_sha"),
        "read_complete": not incomplete,
        "unread_sources": unread,
        "source_cursor": readmodel.get("source_cursor") or {},
        "edited_sources": readmodel.get("edited_sources") or [],
        "last_complete_read_at": (readmodel.get("cursor") or {}).get("last_complete_read_at"),
        "totals": {
            "denominator": "selected tasks of this plan only",
            "tasks": count, "known_rows": len(rows),
            "E_current": sum(r["E"] == "CURRENT_EVIDENCE" for r in rows) if count is not None else None,
            "E_stale": sum(r["E"] == "STALE_EVIDENCE" for r in rows) if count is not None else None,
            "claims_qualified": sum(r["claim_qualified"] for r in rows) if count is not None else None,
            "native_total_matches": native.get("total") == len(rows) if native else None,
            "partial": incomplete, "zero_is_not_established": incomplete,
            "note": "No cross-PR test-suite addition or acceptance inference.",
        },
        "by_child": by_child, "by_pr": by_pr,
        "A_detail": {
            "status": "NOT_EVALUATED", "required_categories": list(CATEGORIES),
            "accounted": None, "reported": None, "unknown": None, "not_applicable": None,
            "attested": None, "reason": "#401 chain audit not admitted; no 11/11 or A100% claim",
            "external_attestation": "NOT_EVALUATED",
        },
        "V_detail": {
            "status": "NOT_EVALUATED", "external_attestation": "NOT_EVALUATED",
            "reported_only_tool_limit": "C1 reports 0/11 externally verified by this tool, not zero proof in existence",
            "native_zero_limit": "snapshot verified_complete=0 is a constant, not a query",
        },
        **NOT_EVALUATED, "rows": rows, "title_note": TITLE_NOTE,
        "managed_region": [MANAGED_BEGIN, MANAGED_END], "render_mode": "READ_ONLY_DRY_RUN",
    }


def cell(value):
    """Single Markdown cell; never allow untrusted text to escape a managed table."""
    return str(value if value is not None else "UNKNOWN").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", r"\|").replace("\r", " ").replace("\n", " ")


def merge_managed_region(original, projection):
    """Pure *proposal* for ECO-05; preserves every byte of human text outside one region.

    Never writes to a provider. Refuse ambiguous/duplicated or unbalanced markers.
    A projection may be a framed render_markdown() result or just region contents.
    """
    if not isinstance(original, str) or not isinstance(projection, str):
        raise ValueError("both source and projection must be text")
    if projection.startswith(MANAGED_BEGIN) and projection.endswith(MANAGED_END):
        if projection.count(MANAGED_BEGIN) != 1 or projection.count(MANAGED_END) != 1:
            raise ValueError("ambiguous replacement projection")
        payload = projection[len(MANAGED_BEGIN):-len(MANAGED_END)].strip("\n")
    else:
        if MANAGED_BEGIN in projection or MANAGED_END in projection:
            raise ValueError("unexpected marker inside replacement")
        payload = projection.strip("\n")
    region = MANAGED_BEGIN + "\n" + payload + "\n" + MANAGED_END
    begins, ends = original.count(MANAGED_BEGIN), original.count(MANAGED_END)
    if begins != ends or begins > 1:
        raise ValueError("unbalanced or repeated owned scoreboard region")
    if begins == 0:
        separator = "" if not original or original.endswith("\n") else "\n"
        return original + separator + region
    start = original.index(MANAGED_BEGIN)
    end = original.index(MANAGED_END, start) + len(MANAGED_END)
    return original[:start] + region + original[end:]


def render_markdown(b):
    """No provider calls or writes; render only the uniquely-owned managed region."""
    t = b["totals"]
    lines = [MANAGED_BEGIN, "### v3.6 smart scoreboard — " + cell(b.get("plan")), ""]
    if not b["read_complete"]:
        src = ", ".join(map(cell, b["unread_sources"])) or "incomplete provider/readmodel data"
        lines += ["**INCOMPLETE READ** - unread: " + src +
                  ". Known rows are partial, not a zero or a complete denominator.", ""]
    counts = (str(t["E_current"]) + "/" + str(t["tasks"])) if t["tasks"] is not None else "UNKNOWN/UNKNOWN"
    lines += [
        "Observed " + cell(b["observed_at"]) + " · Parent " + cell(b["parent"]) +
        " · label " + cell(b["label_sha"]) + " · selected-plan E current " + counts +
        " (stale " + cell(t["E_stale"]) + ").",
        "**A: NOT_EVALUATED** (#401 11-category audit unadmitted); "
        "**V: NOT_EVALUATED** (no external attestation; native zero is constant); "
        "**Owner acceptance: NOT_EVALUATED** (no authorised decision reader).",
        "A categories required: " + ", ".join(CATEGORIES) + ". Accounting is not attestation.",
        "",
        "| Task/outcome | Child | PR | Observed head | E | Claim | Gaps | Next actor/action | Age min |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in b["rows"]:
        nxt = str(r["next"]["actor"]) + ": " + str(r["next"]["action"])
        lines.append("| " + " | ".join(map(cell, (
            r["task_id"] + " / " + str(r["outcome"]), r["issue"] or "UNKNOWN",
            r["pr"] or "UNATTRIBUTED", r["observed_head"] or "UNKNOWN",
            r["E"], r["claim"], "; ".join(r["gaps"]) or "none", nxt,
            r["source_age_minutes"] if r["source_age_minutes"] is not None else "UNKNOWN"
        ))) + " |")
    lines += ["", "#### PR-specific evidence denominators (selected linked tasks only)", "",
              "| PR | Current/linked | Stale | Linked task IDs |",
              "|---|---|---|---|"]
    for pr, g in sorted(b["by_pr"].items()):
        lines.append("| " + " | ".join(map(cell, (
            pr, str(g["E_current"]) + "/" + str(g["tasks"]), g["E_stale"], ", ".join(g["task_ids"])
        ))) + " |")
    if not b["by_pr"]:
        lines.append("No securely linked PR denominator established.")
    lines += ["", "#### Child-specific evidence denominators", ""]
    for issue, g in sorted(b["by_child"].items()):
        lines.append("- " + cell(issue) + ": " + str(g["E_current"]) + "/" + str(g["tasks"]) +
                     " current; stale " + str(g["E_stale"]))
    if not b["by_child"]:
        lines.append("No securely linked child denominator established.")
    lines += ["", "#### Source/verification notes by task", ""]
    for r in b["rows"]:
        original = r["original_input"]
        verification = r["verification_scope"]
        lines += [
            "**" + cell(r["task_id"]) + "** — source-bound details",
            "- User outcome: " + cell(r["user_outcome"]) + " (native outcome " + cell(r["outcome"]) + ")",
            "- Implementation crux: " + cell(r["implementation_crux"]),
            "- Original input / golden / benchmark: " + cell(original["input"]) + " / " +
                cell(original["golden"]) + " / " + cell(original["benchmark"]) +
                " [" + cell(original["attribution"]) + "; not source-authenticated]",
            "- Verification scope: author-reported done-when " +
                cell(verification["reported_done_when"]) + "; run-verified " +
                cell(verification["run_verified"]) + "; tested head " + cell(verification["tested_head"]),
            "- Observed head " + cell(r["observed_head"]) + "; candidate head " +
                cell(r["candidate_sha"]) + "; source age min " + cell(r["source_age_minutes"]),
            "- Source revisions: " + ("; ".join(cell(s.get("url", "UNKNOWN")) + " @ " +
                cell(s.get("body_sha256", "UNKNOWN")) for s in r["source_revisions"])
                if r["source_revisions"] else "UNKNOWN"),
            "- Owner input attribution: " + cell(len(r["owner_inputs"])) +
                " reported links; no authenticated human approval inferred",
            "- Issue hops: " + cell(len(r["source_history_hops"])) +
                " reported (not authenticated deletion proof)",
            "- Known gaps: " + cell("; ".join(r["gaps"]) or "none"),
            "- Next actor/action: " + cell(r["next"]["actor"]) + " → " +
                cell(r["next"]["action"]) + " [basis " + cell(r["next"]["source"]) + "]",
            "",
        ]
    lines += ["_" + cell(TITLE_NOTE) + " Native evidence, author self-check, chain accounting, "
              "source verification and Owner decisions are different stages._", MANAGED_END]
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description="v3.6 read-only scoreboard/dry-run JSON or Markdown")
    p.add_argument("--readmodel", required=True, help="ECO-02b readmodel_v36.py output")
    p.add_argument("--markdown", action="store_true", help="print managed Markdown instead of JSON")
    args = p.parse_args()
    with open(args.readmodel, encoding="utf-8") as f:
        projected = board(json.load(f))
    print(render_markdown(projected) if args.markdown else json.dumps(projected, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
