#!/usr/bin/env python3
"""V3.6 WP4. Deterministic GitHub issue and PR titles from observed evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re

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
PR_STATES = frozenset(("DRAFT", "OPEN", "MERGED", "CLOSED"))
CHILD_STATES = frozenset(("PLANNED", "PENDING", "EVIDENCED", "STALE"))
ATTENTION_WORDS = frozenset((
    "HOLD", "STALE", "ORIGINALS_MISSING", "CHAIN_GAP", "OWNER_GATE", "UNKNOWN",
))
# A human [HOLD] immediately after a legacy [E1/1] could be indistinguishable
# from an old, unmarked projected attention signal. Prefer preserving human
# content. All *new* generated attention signals carry this exact grammar
# marker, so re-projection may safely remove only that tool-owned pair.
ATTENTION_MARKER = "[v36.attention/v1]"


def managed_block_end(current: str, start: int) -> int:
    """End of one *structurally recognised* native prefix, not any owned-looking word.

    Native supported shapes (with legacy lab form retained):
      [V3.6][LAB?][E#/#]                        parent
      [V3.6][LAB?][O1–O5][#/#]                  legacy parent
      [V3.6][O#][PLANNED|PENDING|EVIDENCED|STALE] child
      [V3.6][LAB?][outcomes][PR-state][E#/#?]  PR
      [V3.6][outcomes][PR-state][E#/#][attention][v36.attention/v1]
    A bare [V3.6] is ours, but an adjacent free-standing [UNKNOWN] or
    [HOLD] is *never* ours. An unmarked trailing attention word also stays
    human-owned, even if it resembles one of our historical projections.
    """
    first = BRACKET.match(current, start)
    if not first or first[1] != "V3.6":
        return start
    marker_end = first.end()
    cursor = marker_end

    def token(at):
        m = BRACKET.match(current, at)
        return (m[1], m.end()) if m else (None, at)

    value, nxt = token(cursor)
    if value == "LAB":
        cursor = nxt
        value, nxt = token(cursor)

    if value is not None and ECOUNT.fullmatch(value):
        return nxt  # parent

    if value is None or not (OUTCOMES.fullmatch(value) or value == "UNATTRIBUTED"):
        return marker_end

    cursor = nxt
    state, after_state = token(cursor)
    if state is not None and OLD_COUNT.fullmatch(state):
        return after_state  # legacy parent
    if state in CHILD_STATES:
        return after_state
    if state not in PR_STATES:
        return marker_end  # do not consume partial or human tokens

    cursor = after_state
    value, nxt = token(cursor)
    if value is not None and ECOUNT.fullmatch(value):
        cursor = nxt
        attention, attention_end = token(cursor)
        if (attention in ATTENTION_WORDS
                and current.startswith(ATTENTION_MARKER, attention_end)):
            cursor = attention_end + len(ATTENTION_MARKER)
        return cursor
    return cursor  # old PR grammar without an E counter


def split_title(current: str, fallback: str) -> tuple[str, str]:
    """Return (foreign preamble, human suffix), stripping only structured own prefixes.

    When there is no leading [V3.6] namespace, the *entire original title* is
    human-owned, including all leading bracket text. This avoids guessing
    which foreign brackets are metadata vs actual title words. If an owned
    prefix follows foreign leading brackets, preserve that preamble separately.
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
    if not first or first[1] != "V3.6":
        return "", current.strip() or fallback
    pos = managed_block_end(current, pos)

    # Older projections sometimes repeated their entire owned header. Strip
    # another header only when it actually parses as a full managed sequence.
    while pos < length:
        candidate = pos
        while candidate < length and current[candidate] == " ":
            candidate += 1
        marker = BRACKET.match(current, candidate)
        if not marker or marker[1] != "V3.6":
            break
        following = managed_block_end(current, candidate)
        if following <= marker.end():
            break
        pos = following
    return "".join(foreign), current[pos:].strip() or fallback


def title_tail(current: str, fallback: str) -> str:
    """Compatibility helper; intentionally retains foreign brackets plus human tail."""
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
                    "after": new_parent, "display_profile": profile,
                    "body_before": parent_issue.get("body"),
                    "labels_before": parent_issue.get("labels")})
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
                        "before": before, "after": new_title,
                        "body_before": matches[0].get("body"),
                        "labels_before": matches[0].get("labels"),
                        "task_id": task["task_id"]})
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
        token = f"[{attention['signal']}]{ATTENTION_MARKER}" if attention["signal"] else ""
        managed = f"[V3.6][{outcomes}][{status}][E{pr_count}/{pr_total}]{token}"
        after = compose_title(pr.get("title"), "Lifecycle work", managed)
        updates.append({"kind": "pr", "number": pr["number"], "before": pr["title"],
                        "after": after, "head_sha": pr["head"].get("sha"),
                        "body_before": pr.get("body"), "labels_before": pr.get("labels"),
                        "attention_grammar": ATTENTION_GRAMMAR, "attention": attention,
                        "pr_e_denominator": pr_total, "pr_e_current": pr_count})
    return updates



def source_digest(plan: dict, report: dict) -> str:
    """Digest native source observations, not an endorsement or accepted outcome."""
    value = {"parent": plan["parent"], "label_sha": plan["label"]["label_sha"],
             "plan_version": plan["plan_version"], "native_snapshot": report}
    data = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def scoreboard_body_change(parent_issue: dict, region: str, *, parent_number: int) -> dict:
    """Pure parent-only ECO-03 region update. No destructive body replacement."""
    from scoreboard_v36 import merge_managed_region
    if (type(parent_number) is not int or parent_number < 1 or
            parent_issue.get("number") != parent_number or
            not isinstance(parent_issue.get("body"), str) or
            not isinstance(parent_issue.get("title"), str)):
        raise ContractError("scoreboard target lacks parent identity/body/title")
    before = parent_issue["body"]
    try:
        after = merge_managed_region(before, region)
    except ValueError as exc:
        raise ContractError("ambiguous scoreboard region: " + str(exc)) from exc
    return {"surface": "scoreboard", "kind": "issue", "number": parent_number,
            "before": parent_issue["title"], "after": parent_issue["title"],
            "body_before": before, "after_body": after,
            "labels_before": parent_issue.get("labels")}


def _item_surface(item):
    return item.get("surface", "title")


def _endpoint(item):
    if not isinstance(item, dict):
        raise ContractError("malformed projection item")
    kind, number = item.get("kind"), item.get("number")
    if kind not in ("issue", "pr") or type(number) is not int or number <= 0:
        raise ContractError("unscoped projected target")
    return (kind, number), (f"/issues/{number}" if kind == "issue" else f"/pulls/{number}")


def _surface_receipt(item):
    return {"surface": _item_surface(item), "kind": item["kind"], "number": item["number"]}


def _outcome(status, changes, verified, reason, attempted=None):
    return {"status": status, "dry_run": False, "complete": status == "VERIFIED",
            "applied": len(verified), "applied_surfaces": verified,
            "pending_surfaces": [_surface_receipt(x) for x in changes[len(verified):]],
            "attempted_surfaces": attempted or [],
            "uncertain_surfaces": (attempted or [])[len(verified):],
            "readback_ok": status == "VERIFIED",
            "next_reconciliation": reason}


def _observed_state(item, observed):
    """Fresh expected title/body/PR-head/labels comparison; not atomic CAS."""
    surface = _item_surface(item)
    if not isinstance(observed, dict):
        return "provider returned malformed target"
    if not isinstance(item.get("before"), str) or not isinstance(item.get("body_before"), str):
        return "expected title/body unavailable"
    if item.get("labels_before") != observed.get("labels"):
        return "human labels changed; inspect AIM governance"
    if item["kind"] == "pr" and (
            not isinstance(item.get("head_sha"), str) or
            observed.get("head", {}).get("sha") != item["head_sha"]):
        return "PR head changed"
    if observed.get("body") != item["body_before"] and not (
            surface == "scoreboard" and observed.get("body") == item.get("after_body")):
        return "provider body changed; protect Owner edits"
    if surface == "title":
        if observed.get("title") not in (item["before"], item["after"]):
            return "provider title changed; protect human title"
        return "already" if observed["title"] == item["after"] else "ready"
    if surface == "scoreboard":
        if item["kind"] != "issue" or not isinstance(item.get("after_body"), str):
            return "invalid scoreboard body target"
        if observed.get("title") != item["before"]:
            return "provider title changed"
        return "already" if observed.get("body") == item["after_body"] else "ready"
    return "unauthorised/unsupported surface"



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
            "source_pin": source_digest(plan, report),
            "current_evidence": report["current_evidence"], "total": report["total"],
            "accepted_complete": report["verified_complete"],
            "changes": [u for u in updates if u["before"] != u["after"]],
            "all": updates}


def apply_projection(calculated: dict, client, *, confirm_scope: str,
                     allow_write: bool = False, authorized_surfaces=frozenset(),
                     authorized_targets=frozenset(), lab_scope: str | None = None,
                     source_probe=None) -> dict:
    """Sole native writer: fake-provider ECO-05; never an atomic CAS.

    The production CLI refuses live --apply without future exact consent.
    For synthetic execution, require exact target/surface permissions, source
    pinning, and GET preflight/readback. Neither human labels nor the AIM master
    are ever patched. Namespace modification is deliberately unsupported.
    Token permission minimisation requires controller-side verification; this
    local method cannot infer actual GitHub token scope.
    """
    changes = calculated.get("changes")
    if not isinstance(changes, list):
        raise ContractError("projection changes must be a list")
    if not allow_write:
        return {"status": "NOT_RUN", "dry_run": True, "complete": False,
                "proposed": len(changes), "applied": 0, "applied_surfaces": [],
                "pending_surfaces": [_surface_receipt(x) for x in changes],
                "readback_ok": False,
                "next_reconciliation": "live demonstration NOT_RUN; no exact-scope write consent"}
    parent = PARENT_REF.fullmatch(calculated.get("parent") or "")
    if not parent or confirm_scope != calculated["parent"] or client.repo != parent[1]:
        raise ContractError("scope confirmation or repository mismatch")
    if parent[1] == LAB_REPO and lab_scope != LAB_REPO:
        raise ContractError("explicit writable lab required, no implicit lab")
    pin = calculated.get("source_pin")
    if (not isinstance(calculated.get("label_sha"), str) or
            not isinstance(pin, str) or not re.fullmatch(r"[0-9a-f]{64}", pin)):
        raise ContractError("trusted label and source pin required")
    if (not isinstance(authorized_surfaces, (set, frozenset)) or
            not authorized_surfaces or not authorized_surfaces <= {"title", "scoreboard"}):
        raise ContractError("separate surface consent required; namespace/labels disabled")
    if not isinstance(authorized_targets, (set, frozenset)):
        raise ContractError("exact target allowlist required")
    if not callable(source_probe):
        raise ContractError("trusted source re-read required")
    target_keys = []
    for item in changes:
        ident, _ = _endpoint(item)
        surface = _item_surface(item)
        if surface not in authorized_surfaces or ident not in authorized_targets:
            raise ContractError("unauthorised surface or target")
        if surface == "scoreboard" and ident != ("issue", int(parent[2])):
            raise ContractError("scoreboard target must be exact parent")
        if surface == "title" and ident[0] == "issue" and ident[1] != int(parent[2]):
            marker = "<!-- v36-task:{} parent:{} -->".format(item.get("task_id"), calculated["parent"])
            if marker not in (item.get("body_before") or ""):
                raise ContractError("child lacks owned issue marker; do not guess")
        if surface == "title" and ident[0] == "pr" and not item.get("head_sha"):
            raise ContractError("PR head pin required")
        target_keys.append((ident, surface))
    if len(target_keys) != len(set(target_keys)):
        raise ContractError("duplicate writer responsibility")
    if len({entry[0] for entry in target_keys}) != len(target_keys):
        raise ContractError("multiple surfaces per target need fresh separate projections")

    verified, attempted, prepared = [], [], []
    def pin_is_current():
        try:
            return source_probe() == pin
        except Exception:
            return False

    if not pin_is_current():
        return _outcome("BLOCKED", changes, verified, "reconcile source: stale/unavailable pin")
    # Preflight every target. Mixed already/ready after an interrupted run
    # cannot be treated as a safe automatic replay.
    try:
        for item in changes:
            _, endpoint = _endpoint(item)
            state = _observed_state(item, client.request("GET", endpoint))
            if state not in ("ready", "already"):
                return _outcome("BLOCKED", changes, verified,
                                "reconcile precondition: " + state)
            prepared.append(state)
    except Exception as exc:
        return _outcome("BLOCKED", changes, verified,
                        "reconcile provider GET failure: " + str(exc))
    if "ready" in prepared and "already" in prepared:
        return _outcome("BLOCKED", changes, verified,
                        "reconcile prior partial application; do not blindly replay")
    if changes and all(x == "already" for x in prepared):
        return {"status": "VERIFIED", "dry_run": False, "complete": True,
                "proposed": len(changes), "applied": 0, "applied_surfaces": [],
                "pending_surfaces": [], "attempted_surfaces": [], "readback_ok": True,
                "next_reconciliation": "none; GET-verified zero-change replay"}

    for item in changes:
        receipt = _surface_receipt(item)
        _, endpoint = _endpoint(item)
        if not pin_is_current():
            return _outcome("PARTIAL" if verified else "BLOCKED", changes,
                            verified, "reconcile source drift before next patch", attempted)
        try:
            if _observed_state(item, client.request("GET", endpoint)) != "ready":
                return _outcome("PARTIAL" if verified else "BLOCKED", changes,
                                verified, "reconcile concurrent title/body/head edit", attempted)
            payload = {"title": item["after"]} if _item_surface(item) == "title" else {
                "body": item["after_body"]}
            attempted.append(receipt)
            client.request("PATCH", endpoint, payload)
            state = _observed_state(item, client.request("GET", endpoint))
            if state != "already":
                return _outcome("UNCERTAIN", changes, verified,
                                "reconcile readback mismatch after PATCH", attempted)
            verified.append(receipt)
        except Exception as exc:
            # A thrown PATCH/GET may have committed despite the exception.
            uncertain = bool(attempted and attempted[-1] == receipt)
            return _outcome("PARTIAL" if verified else "UNCERTAIN" if uncertain else "BLOCKED",
                            changes, verified,
                            "reconcile provider failure / uncertain write: " + str(exc),
                            attempted)
    return {"status": "VERIFIED", "dry_run": False, "complete": True,
            "proposed": len(changes), "applied": len(verified),
            "applied_surfaces": verified, "pending_surfaces": [],
            "attempted_surfaces": attempted, "readback_ok": True,
            "next_reconciliation": "none; fresh source replay should project zero changes"}


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
    # Code and fake-provider tests authorised; exact-scope live writes NOT authorised.
    if args.apply:
        parser.error("ECO-05 live demonstration: NOT_RUN (no exact-scope write consent)")
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
