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

HEX40 = re.compile(r"^[0-9a-f]{40}$")
PHASES = frozenset({"1a", "1b", "2", "Y"})



# ECO-06 extends the EXISTING cold successor read path, without another agent
# stage or separate publisher. Treat fetched text as *reported sources*, not
# authoritative conclusions. No title, scoreboard, producer claim or CI count
# authenticates original intent, a causal model, approval, or release.
RECOVERY_SCHEMA = "v36.successor.recovery/v1"
OUTCOMES = (
    "original_intent_amendments",
    "originals_golden_benchmark",
    "causal_code_path",
    "decision_rationale",
    "issue_lineage",
    "permitted_provenance",
    "proof_vs_acceptance",
    "handover_next_verification",
    "stale_source_brief",
    "safety_boundaries",
)
MAX_LINKED_ISSUES = 20
MAX_ORIGINAL_FILES = 12
ISSUE_URL = re.compile(
    r"https://github\.com/(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/issues/(?P<n>[1-9][0-9]*)"
)
BLOB_URL = re.compile(
    r"https://github\.com/(?P<repo>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/blob/"
    r"(?P<sha>[0-9a-f]{40})/(?P<path>[A-Za-z0-9_./%+\-]+)"
)
ORIGINAL_LINE = re.compile(
    r"(?im)^\s*(?P<kind>Original input|Golden|Benchmark|Causal source)\s*:\s*(?P<url>https://\S+)"
)
CONTEXT_WORDS = {
    "original_intent_amendments": ("original owner intent:", "owner amendment:"),
    "decision_rationale": ("decision:", "adopted:", "rejected:", "parked:"),
    "handover_next_verification": ("handover:", "next verification:"),
}


def _hash_text(body):
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _outcome(status, reason, refs=(), **extra):
    """Every reported outcome cites a read source; all others explain gaps."""
    refs = list(dict.fromkeys(refs))
    if status == "REPORTED" and not refs:
        status, reason = "UNKNOWN", "no directly read source reference"
    return {"status": status, "source_refs": refs, "reason": reason, **extra}


def _owner_url(plan, client, url):
    parent = PARENT_REF.fullmatch(plan.get("parent", ""))
    if not parent or client.repo != parent[1]:
        raise ContractError("successor owner repository mismatch")
    expected = f"https://github.com/{parent[1]}/issues/{parent[2]}"
    if url != expected:
        raise ContractError("one authorised owning-issue URL required; other issue/repo/ref rejected")
    return expected, int(parent[2])


def recover_context(label: dict, plan: dict, client, *, owning_issue_url: str,
                    native_snapshot: dict | None = None, prior: dict | None = None) -> dict:
    """Read-only, bounded, source-first context collection for existing successor.

    Sources come from one exact owning issue, plan-selected children and their
    linked same-repository issue/original URLs. A quoted/linked source is only
    reported provenance, never a scientific verdict. The optional prior pins
    compare source revisions; without them freshness cannot be certified.
    Blind independent participation is NOT_RUN, not inferred from this open read.
    """
    owner_url, owner_no = _owner_url(plan, client, owning_issue_url)
    if (plan.get("label", {}).get("label_sha") != label.get("label_sha") or
            plan["label"].get("version") != label.get("version") or
            plan["label"].get("work") != label.get("work")):
        raise ContractError("successor Owner label/plan mismatch")
    if prior is not None and not isinstance(prior, dict):
        raise ContractError("prior pin set must be a dict")
    unavailable, sources, observed, statements, linked_history = [], [], {}, [], []
    original_urls = {}
    issue_links = set()
    repo = client.repo
    owner_login = repo.split("/", 1)[0]

    def add_source(kind, url, body, *, author=None, updated=None):
        if not isinstance(body, str):
            unavailable.append(kind + ":body_missing:" + url)
            return
        if url in observed:
            return
        record = {"kind": kind, "url": url, "body_sha256": _hash_text(body),
                  "updated_at": updated if isinstance(updated, str) else "UNKNOWN",
                  "attribution": "REPORTED", "author": author or "UNKNOWN"}
        sources.append(record)
        observed[url] = record["body_sha256"]
        lower = body.lower()
        statements.append((url, lower))
        for found in ISSUE_URL.finditer(body):
            if found["repo"] == repo:
                n = int(found["n"])
                if n != owner_no:
                    issue_links.add(n)
        for hit in ORIGINAL_LINE.finditer(body):
            kind_name, raw = hit["kind"].lower(), hit["url"].rstrip(".,;)")
            m = BLOB_URL.fullmatch(raw)
            if not m or m["repo"] != repo:
                unavailable.append("unqualified_original_link:" + raw)
                continue
            original_urls.setdefault(kind_name, []).append((raw, url, m["sha"]))

    def read_issue(issue, kind):
        if not isinstance(issue, dict):
            unavailable.append(kind + ":malformed_issue")
            return
        number = issue.get("number")
        if type(number) is not int or number < 1:
            unavailable.append(kind + ":malformed_issue_number")
            return
        expected = f"https://github.com/{repo}/issues/{number}"
        if issue.get("html_url", expected) != expected:
            unavailable.append(kind + ":foreign_issue_identity:" + expected)
            return
        add_source(kind, expected, issue.get("body"),
                   updated=issue.get("updated_at"))

    # Read the Owner issue from its exact authorised URL, independent of the
    # human title's current wording. Fail visibly if the provider is unavailable.
    try:
        owner = client.request("GET", f"/issues/{owner_no}")
        if not isinstance(owner, dict) or owner.get("number") != owner_no:
            raise ValueError("owning issue identity changed")
        read_issue(owner, "owning_issue")
    except Exception as exc:
        unavailable.append("owning_issue:provider_unavailable:" + type(exc).__name__)

    def comments_of(number):
        try:
            comments = client.list_comments(number)
            if not isinstance(comments, list):
                raise ValueError("comments not a list")
        except Exception as exc:
            unavailable.append(f"comments:{number}:provider_unavailable:{type(exc).__name__}")
            return
        for c in comments:
            if not isinstance(c, dict) or not isinstance(c.get("body"), str):
                unavailable.append(f"comments:{number}:malformed_record")
                continue
            url = c.get("html_url") or c.get("url")
            prefix = f"https://github.com/{repo}/issues/{number}#issuecomment-"
            if not isinstance(url, str) or not url.startswith(prefix) or not url[len(prefix):].isdigit():
                unavailable.append(f"comments:{number}:foreign_or_missing_reference")
                continue
            author = c.get("user") if isinstance(c.get("user"), dict) else {}
            add_source("issue_comment", url, c["body"],
                       author=author.get("login"), updated=c.get("updated_at"))

    comments_of(owner_no)
    try:
        child_issues = client.list_issues()
        if not isinstance(child_issues, list):
            raise ValueError("issue list not an array")
    except Exception as exc:
        unavailable.append("issues:provider_unavailable:" + type(exc).__name__)
        child_issues = []
    from decompose_v36 import is_task_issue
    owned = {owner_no}
    for task in plan["tasks"]:
        matches = [i for i in child_issues if isinstance(i, dict)
                   and is_task_issue(i, task, plan["parent"])]
        if len(matches) != 1:
            unavailable.append("plan_child:" + task["task_id"] + ":missing_or_ambiguous")
            continue
        issue = matches[0]
        number = issue.get("number")
        if type(number) is not int:
            unavailable.append("plan_child:" + task["task_id"] + ":number_unavailable")
            continue
        owned.add(number)
        read_issue(issue, "plan_child")
        comments_of(number)
        linked_history.append({"issue": f"https://github.com/{repo}/issues/{number}",
                               "kind": "plan_child", "status": "READ"})

    # Bounded issue lineage following *explicit source links*, not inferred from
    # numeric PRs or unrelated GitHub issues. Never cross into another repo.
    for number in sorted(issue_links - owned)[:MAX_LINKED_ISSUES]:
        url = f"https://github.com/{repo}/issues/{number}"
        try:
            getter = getattr(client, "get_issue", None)
            issue = getter(number) if callable(getter) else client.request("GET", f"/issues/{number}")
            if not isinstance(issue, dict) or issue.get("number") != number:
                raise ValueError("linked issue identity mismatch")
            previous_count = len(sources)
            read_issue(issue, "linked_issue")
            status = "READ" if len(sources) > previous_count else "UNKNOWN"
            linked_history.append({"issue": url, "kind": "linked_issue", "status": status})
            if status == "READ":
                comments_of(number)
        except Exception as exc:
            unavailable.append("linked_issue:" + url + ":not_found_or_inaccessible:" + type(exc).__name__)
            linked_history.append({"issue": url, "kind": "linked_issue",
                                   "status": "NOT_FOUND_OR_INACCESSIBLE"})

    checked_originals = []
    original_failures = []
    refs_by_type = {}
    for kind in ("original input", "golden", "benchmark", "causal source"):
        for url, citing_url, sha in original_urls.get(kind, [])[:MAX_ORIGINAL_FILES]:
            item = {"kind": kind, "url": url, "cited_by": citing_url,
                    "pinned_commit": sha, "status": "REPORTED_LINK"}
            fetcher = getattr(client, "fetch_source", None)
            if not callable(fetcher):
                item["status"] = "NOT_RUN"
                item["reason"] = "provider lacks exact-source content reader capability"
            else:
                try:
                    fetched = fetcher(url)
                    if (not isinstance(fetched, dict) or fetched.get("url") != url or
                            fetched.get("sha") != sha or
                            not isinstance(fetched.get("content"), str)):
                        raise ValueError("source content/commit mismatch")
                    add_source("pinned_source", url, fetched["content"], updated=None)
                    item["status"] = "READ_PINNED_SOURCE"
                    refs_by_type.setdefault(kind, []).append(url)
                except Exception as exc:
                    item["status"] = "UNKNOWN"
                    item["reason"] = "private/unavailable or mismatched pinned source: " + type(exc).__name__
            if item["status"] != "READ_PINNED_SOURCE":
                original_failures.append(item["reason"])
            checked_originals.append(item)

    brief_input = {
        "plan": plan.get("plan_version"),
        "parent": plan["parent"],
        "label": {"work": label["work"], "version": label["version"],
                  "label_sha": label["label_sha"], "content": label.get("label")},
        "tasks": plan.get("tasks"),
    }
    brief_sha = _hash_text(json.dumps(brief_input, sort_keys=True, ensure_ascii=False))
    changes = []
    if prior is not None:
        for url, old_sha in (prior.get("source_hashes") or {}).items():
            if not isinstance(old_sha, str) or not re.fullmatch("[0-9a-f]{64}", old_sha):
                raise ContractError("malformed earlier source pin")
            if url not in observed:
                changes.append({"url": url, "state": "UNREAD_OR_MISSING"})
            elif observed[url] != old_sha:
                changes.append({"url": url, "state": "SOURCE_EDITED"})
        if prior.get("brief_sha256") is not None and prior["brief_sha256"] != brief_sha:
            changes.append({"url": "approved_label_and_plan", "state": "BRIEF_CHANGED"})
    source_state = "STALE" if changes else "NO_PRIOR_PINS" if prior is None else "NO_DETECTED_CHANGE"
    def matched_words(words):
        return [url for url, low in statements if any(w in low for w in words)]

    intent_refs = matched_words(CONTEXT_WORDS["original_intent_amendments"])
    decision_refs = matched_words(CONTEXT_WORDS["decision_rationale"])
    next_refs = matched_words(("next verification:",))
    handover_refs = matched_words(("handover:",))
    proof_refs = ([t.get("evidence") for t in native_snapshot.get("tasks", [])
                   if isinstance(t, dict) and t.get("evidence")]
                  if isinstance(native_snapshot, dict) else [])
    valid_proof_refs = [u for u in proof_refs if isinstance(u, str) and
                        u.startswith(f"https://github.com/{repo}/issues/")]
    original_ref_list = [u for kind in ("original input", "golden", "benchmark")
                         for u in refs_by_type.get(kind, [])]
    needed_originals = all(refs_by_type.get(k) for k in ("original input", "golden", "benchmark"))
    original_status = "REPORTED" if needed_originals else "UNKNOWN" if checked_originals else "MISSING"
    original_reason = ("pinned files read; source authenticity, golden completeness and benchmark correctness NOT_EVALUATED"
                       if needed_originals else
                       "private/inaccessible or unverified originals: " + "; ".join(original_failures)
                       if checked_originals else "no pinned original input, full golden or benchmark sources cited")
    source_refs = [x["url"] for x in sources]
    read_complete = not unavailable and not original_failures
    outcomes = {
        "original_intent_amendments": _outcome(
            "REPORTED" if intent_refs else "UNKNOWN",
            "Owner intent/amendment appears in read issue text; source identity and interpretation not independently approved"
            if intent_refs else "original Owner intent/amendment not found in readable owning issue context",
            intent_refs),
        "originals_golden_benchmark": _outcome(
            original_status, original_reason,
            original_ref_list if needed_originals else [
                x["cited_by"] for x in checked_originals],
            originals=checked_originals, complete_golden="NOT_EVALUATED"),
        "causal_code_path": _outcome(
            "NOT_RUN", "independent source-level causal analysis not authorised or executed; links do not prove cause",
            refs_by_type.get("causal source", []), causal_verified=False),
        "decision_rationale": _outcome(
            "REPORTED" if decision_refs else "UNKNOWN",
            "adopted/rejected/parked words are cited, but alternative reasoning is not independently audited"
            if decision_refs else "no cited decision/parked-rationale sources",
            decision_refs),
        "issue_lineage": _outcome(
            "UNKNOWN" if unavailable else "REPORTED",
            "bounded linked issues read; complete historical lineage not authenticated"
            if not unavailable else "one or more linked issues or comments unavailable; full lineage UNKNOWN",
            [x["issue"] for x in linked_history if x["status"] == "READ"],
            completeness="UNKNOWN"),
        "permitted_provenance": _outcome(
            "REPORTED" if sources else "UNKNOWN",
            "provider-observed body hashes identify fetched records, not human or citation authenticity"
            if sources else "provider sources unavailable; cannot reconstruct provenance",
            source_refs, authenticated_approval=False),
        "proof_vs_acceptance": _outcome(
            "REPORTED" if valid_proof_refs else "NOT_RUN",
            "native snapshot E is an evidence indicator only; no Owner acceptance reader or independent review run"
            if valid_proof_refs else "native evidence source unavailable; no proof or approval may be inferred",
            valid_proof_refs, acceptance="NOT_EVALUATED",
            native_statuses=[{"task_id": t["task_id"], "E": t["status"]}
                             for t in native_snapshot["tasks"]]
            if isinstance(native_snapshot, dict) else []),
        "handover_next_verification": _outcome(
            "REPORTED" if next_refs and handover_refs else "UNKNOWN",
            "handover and next verification cited, but source-grounded independent continuation NOT_RUN"
            if next_refs and handover_refs else
            "complete handover and next verification cannot both be established from readable sources",
            next_refs + handover_refs),
        "stale_source_brief": _outcome(
            "UNKNOWN" if changes or prior is None else "REPORTED",
            "source or approved brief changed; re-read/reconcile before next action"
            if changes else "no prior source/brief pin supplied; freshness UNKNOWN"
            if prior is None else "no differences against supplied pins; provider completeness still requires review",
            [x["url"] for x in changes if x["url"].startswith("https://") and x["url"] in observed],
            changes=changes),
        "safety_boundaries": _outcome(
            "REPORTED" if source_refs else "NOT_RUN",
            "read-only owner-issue scope; no private chat access, no authorisation, merge, release or acceptance granted",
            [owner_url] if owner_url in observed else [],
            live_participation="NOT_RUN"),
    }
    return {
        "schema": RECOVERY_SCHEMA,
        "owning_issue_url": owner_url,
        "scope": "one plan-bound owning issue; only explicit same-repository links and selected plan children",
        "investigation": {
            "mode": "OPEN_SOURCE_INSPECTION",
            "blind_review": "NOT_RUN",
            "reason": "reading linked issues and source comments is not a blinded independent investigation",
        },
        "acceptance_demonstration": "NOT_RUN",
        "acceptance_reason": "no live participation authority; code/synthetic evaluation only",
        "prior_chats": {"status": "NOT_RUN", "reason": "earlier chat unavailable/not used; GitHub-only recovery"},
        "read_complete": read_complete,
        "unavailable_sources": sorted(set(unavailable)),
        "sources": sources,
        "source_hashes": observed,
        "source_changes": changes,
        "source_state": source_state,
        "brief_sha256": brief_sha,
        "linked_history": linked_history,
        "outcomes": outcomes,
        "limitations": [
            "Reported textual assertions are not engineering truth or independent causal proof",
            "No blind/G2 participation, no Owner acceptance, no launch or fixtures invented",
            "Untrusted source text never becomes shell/code, writes, or trusted instructions",
        ],
    }


def build_packet(label: dict, plan: dict, client, pr_numbers: list[int],
                 *, owning_issue_url: str | None = None, prior: dict | None = None) -> dict:
    """All facts come from approved label, checked plan and current GitHub reads."""
    match = PARENT_REF.fullmatch(plan["parent"])
    if not match or client.repo != match[1]:
        raise ContractError("cold successor repository mismatch")
    # Authorise the one owning URL *before* any snapshot or GitHub reads.
    _owner_url(plan, client, owning_issue_url or
               f"https://github.com/{match[1]}/issues/{match[2]}")
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
    owner_url = f"https://github.com/{client.repo}/issues/{match[2]}"
    recovery = recover_context(label, plan, client,
                               owning_issue_url=owning_issue_url or owner_url,
                               native_snapshot=report, prior=prior)
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
        "recovery": recovery,
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
    recovery = packet.get("recovery")
    if recovery:
        lines.extend([
            "## ECO-06 source-first recovery (code/synthetic only)",
            "Owning issue: " + recovery["owning_issue_url"],
            "Investigation: " + recovery["investigation"]["mode"]
            + "; blind review=" + recovery["investigation"]["blind_review"],
            "Acceptance demonstration: " + recovery["acceptance_demonstration"]
            + " (no live participation authority)",
            "Source freshness: " + recovery["source_state"],
        ])
        for name, item in recovery["outcomes"].items():
            lines.append("- " + name + ": " + item["status"] + "; " + item["reason"])
            for url in item["source_refs"]:
                lines.append("  Source read/reference: " + url)
        if recovery["unavailable_sources"]:
            lines.append("Unavailable sources: " + ", ".join(recovery["unavailable_sources"]))
        lines.extend(recovery["limitations"])
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
    cold.add_argument("--owning-issue-url",
                      help="must equal the one validated plan.parent GitHub issue URL")
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
            label = load_label(args.label)
            plan = load_plan(args.plan, label)
            require_explicit_lab(label, plan["parent"], args.lab)
            client = GithubClient(PARENT_REF.fullmatch(plan["parent"])[1])
            client.get_pr = lambda n: client.request("GET", f"/pulls/{n}")
            print(render_markdown(build_packet(
                label, plan, client, args.pr,
                owning_issue_url=args.owning_issue_url)), end="")
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
