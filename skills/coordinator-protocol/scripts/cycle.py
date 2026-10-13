"""Coordinator v3.28: ledger-bound planning, guarded sends, private transport state.

No browser, network, scheduler or subprocess access. JSON in; compact JSON out.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from urllib.parse import urlsplit
import uuid
from aim_store import Store as AimStore

POLICY = json.loads((Path(__file__).resolve().parents[1] / "policy.json").read_text(encoding="utf-8"))


def stamp(value=None):
    d = datetime.fromisoformat(value.replace("Z", "+00:00")) if value else datetime.now(timezone.utc)
    if d.tzinfo is None:
        raise ValueError("timestamps must include a timezone")
    return d.astimezone(timezone.utc)


def iso(d):
    return d.isoformat()


def digest(value):
    data = value if isinstance(value, str) else json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def content_hash(text):
    return digest(text.replace("\r\n", "\n").strip())


def conversation(url):
    u = urlsplit(url)
    if u.scheme != "https" or u.netloc != "chatgpt.com" or not re.fullmatch(r"/c/[a-zA-Z0-9-]+/?", u.path):
        raise ValueError("expected a full https://chatgpt.com/c/... conversation URL")
    return "https://chatgpt.com" + u.path.rstrip("/")


@contextmanager
def locked(path, timeout=10):
    """OS lock shared by every command, released even if a process exits."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(path) + ".lock", "a+b") as f:
        if f.seek(0, 2) == 0:
            f.write(b"\0")
            f.flush()
        deadline = time.monotonic() + timeout
        while True:
            try:
                f.seek(0)
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("coordinator state lock busy")
                time.sleep(0.02)
        try:
            yield
        finally:
            f.seek(0)
            if os.name == "nt":
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def atomic_save(path, state):
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(state, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        # Windows scanners can hold a transient sharing lock on the destination.
        # Keep the transaction lock while retrying the atomic replacement.
        for attempt in range(50):
            try:
                os.replace(temporary, path)
                break
            except PermissionError:
                if attempt == 49:
                    raise
                time.sleep(0.02)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def normalize_plan(plan):
    if not isinstance(plan, dict) or not plan.get("rev"):
        raise ValueError("plan requires rev and tasks")
    result = {"rev": str(plan["rev"]), "tasks": {}}
    for task in plan.get("tasks", []):
        tid = str(task["id"])
        if tid in result["tasks"]:
            raise ValueError("duplicate plan task ID")
        if task.get("status", "open") not in ("open", "done", "claimed", "blocked"):
            raise ValueError("invalid plan task state")
        status = task.get("status", "open")
        result["tasks"][tid] = {"outcome": str(task.get("outcome", "")), "status": "claimed" if status == "done" else status, "blocked": bool(task.get("blocked", False))}
    return result


def binding(config):
    if not isinstance(config, dict) or set(config) != {"path", "namespace", "workpack_id"}:
        raise ValueError("ledger requires path, namespace and workpack_id")
    if not isinstance(config["path"], str) or not Path(config["path"]).is_absolute():
        raise ValueError("ledger path must be absolute")
    if not isinstance(config["namespace"], str) or not re.fullmatch(r"work:[A-Za-z0-9][A-Za-z0-9._-]{0,63}", config["namespace"]):
        raise ValueError("ledger namespace must be work:<stable-id>")
    if not isinstance(config["workpack_id"], str) or not config["workpack_id"].strip():
        raise ValueError("ledger workpack_id is required")
    return copy.deepcopy(config)


def claim(r, tid, rev, source, message=""):
    receipt = {"task_id": tid, "rev": rev, "source": source, "message": message}
    if receipt not in r["claim_history"]:
        r["claim_history"].append(receipt)
    r["claims"][tid] = receipt


def refresh_aims(r):
    """Read only: JSON stores a disposable projection, never aim authority."""
    projection, problem = None, "approved aim ledger is not bound"
    if r.get("ledger"):
        store = None
        try:
            config = binding(r["ledger"])
            if not Path(config["path"]).is_file():
                raise ValueError("aim ledger does not exist; this reader will not create it")
            store = AimStore(config["path"], read_only=True)
            projection = store.projection(config["namespace"], config["workpack_id"], r["url"])
            if not isinstance(projection, dict) or type(projection.get("sequence")) is not int or projection["sequence"] < 0:
                raise ValueError("invalid aim ledger projection")
            for kind in ("main", "task"):
                aim = projection.get(kind)
                if not isinstance(aim, dict) or not all(isinstance(aim.get(k), str) and aim[k].strip() for k in ("id", "label")):
                    raise ValueError("approved main and task aims are required")
            for key in ("validated_ids", "registered_ids", "eligible_ids", "reviewed_message_ids", "pending_proposal_ids"):
                ids = projection.get(key)
                if not isinstance(ids, list) or any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
                    raise ValueError("invalid ledger ID projection: " + key)
            if not set(projection["validated_ids"]) <= set(projection["registered_ids"]) or not set(projection["eligible_ids"]) <= set(projection["registered_ids"]) - set(projection["validated_ids"]):
                raise ValueError("ledger eligibility or validation is inconsistent")
            for key in ("due", "reviewed_thresholds"):
                values = projection.get(key)
                if not isinstance(values, list) or any(type(v) is not int or v not in POLICY.get("aim_checkpoints", [5, 10, 15, 19]) for v in values):
                    raise ValueError("invalid aim review thresholds")
            problem = ""
        except (ValueError, OSError, KeyError, TypeError, sqlite3.Error) as error:
            projection, problem = None, str(error)
        finally:
            if store is not None:
                store.close()
    r["aim_projection"] = copy.deepcopy(projection)
    r["aim_error"] = problem
    r["closed"] = {tid: {"source": "aim-ledger", "workpack_id": r["ledger"]["workpack_id"]} for tid in projection["validated_ids"]} if projection else {}
    r["evidence"] = len(r["closed"])
    r["checkpoint"] = max([0] + projection["reviewed_thresholds"]) if projection else 0
    return projection


def aim_token(r):
    p = r.get("aim_projection")
    return {"binding": copy.deepcopy(r["ledger"]), "recipient": r["url"], "sequence": p["sequence"],
            "main_id": p["main"]["id"], "task_id": p["task"]["id"]} if p else None


def progress(r):
    p = r.get("aim_projection") or {}
    return {"done": len(p.get("validated_ids", [])), "validated": len(p.get("validated_ids", [])),
            "claimed": len(r["claims"]), "total": len(p.get("registered_ids", []))}


def review_due(r):
    projection = r.get("aim_projection") or {}
    reviewed = set(projection.get("reviewed_message_ids", []))
    known = list(dict.fromkeys(list(r["task_reports"]) + projection.get("unreviewed_message_ids", [])))
    return [mid for mid in known if mid not in reviewed]


def aim_summary(r):
    p = r.get("aim_projection") or {}
    return {"aims": {"main": p.get("main"), "task": p.get("task")},
            "aim_sequence": p.get("sequence"), "progress": progress(r),
            "alignment": p.get("alignment", "NEEDS_AIMS"),
            "latest_assessment": p.get("latest_assessment"),
            "pending_proposal_ids": p.get("pending_proposal_ids", []),
            "aim_error": r.get("aim_error", ""), "task_review_due": list(r["task_review_due"])}


def stream_record(config):
    r = {"url": conversation(config["url"]), "hold": False, "denied": False,
         "speed": "auto", "handover_hold": False, "repo": {}, "buddy": {},
         "plan": None, "plan_history": [], "closed": {}, "claims": {}, "claim_history": [],
         "ledger": None, "aim_projection": None, "aim_error": "approved aim ledger is not bound",
         "task_reports": {}, "task_review_due": [], "message_history": [], "messages": {}, "evidence": 0,
         "checkpoint": 0, "stall": 0, "ac": None, "last_status_id": "",
         "last_probe": "", "last_full": "", "fingerprint": "", "summary": {},
         "pending": None, "last_ticket": None, "waiting_assistant": None,
         "park_since": "", "last_ping": "", "special": {}, "last_action": ""}
    patch_stream(r, config)
    return r


def patch_stream(r, patch):
    allowed = {"url", "hold", "denied", "speed", "handover_hold", "repo", "buddy", "plan", "ledger"}
    if set(patch) - allowed:
        raise ValueError("unknown stream configuration field")
    if patch.get("speed", r["speed"]) not in ("auto", "speed", "economy"):
        raise ValueError("speed must be auto/speed/economy")
    if "buddy" in patch and r["buddy"] and r["buddy"].get("stage", "work") != "work" and patch["buddy"].get("commit") != r["buddy"]["commit"]:
        raise ValueError("cannot replace the pin of an active handover lane")
    if "url" in patch:
        new_url = conversation(patch["url"])
        if new_url != r["url"]:
            if r["pending"]:
                raise ValueError("resolve pending send before changing conversation")
            r["message_history"].append({"url": r["url"], "messages": copy.deepcopy(r["messages"]), "task_reports": copy.deepcopy(r["task_reports"]), "last_status_id": r["last_status_id"]})
            r.update(url=new_url, messages={}, last_status_id="", waiting_assistant=None,
                     last_full="", last_probe="", fingerprint="", summary={}, special={},
                     observed_pages=0, stall=0, ac=None, task_reports={}, task_review_due=[], aim_projection=None)
    for k in ("hold", "denied", "handover_hold", "speed", "repo", "buddy"):
        if k in patch:
            r[k] = copy.deepcopy(patch[k])
    buddy = r["buddy"]
    if buddy and not re.fullmatch(r"[0-9a-fA-F]{40}", buddy.get("commit", "")):
        raise ValueError("BuddyRunner needs a full pinned commit SHA")
    if "plan" in patch:
        plan = normalize_plan(patch["plan"])
        if r["plan"] and r["plan"] not in r["plan_history"]:
            r["plan_history"].append(copy.deepcopy(r["plan"]))
        for tid, task in plan["tasks"].items():
            if task["status"] == "claimed":
                claim(r, tid, plan["rev"], "plan-baseline")
            elif tid in r["claims"] and task["status"] == "open":
                task["status"] = "claimed"
        r["plan"] = plan
    if "ledger" in patch:
        r["ledger"] = binding(patch["ledger"]) if patch["ledger"] is not None else None
        r["aim_projection"] = None
    r["last_action"] = ""


def mode(r):
    return ("speed" if r["evidence"] < POLICY["speed_evidence"] else "economy") if r["speed"] == "auto" else r["speed"]


def ci_policy(r):
    repo = r["repo"]
    verified = repo.get("verified") is True and bool(repo.get("source"))
    if not verified or repo.get("private") not in (True, False):
        return {"mode": "unverified", "flag": "Visibility unverified"}
    if repo["private"] and POLICY["private_ci_limited"]:
        return {"mode": "limited", "flag": "CI limited (private)"}
    return {"mode": "normal", "flag": "Normal CI"}


def report_table(rows):
    def cell(value):
        return str(value).replace("|", "/").replace("\n", " ")
    lines = ["| Stream | Chat | Status | Main aim | Task aim | Claimed / validated | Alignment | Decisions / next | CI | Meter |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for row in rows:
        progress = row.get("progress", {})
        state = "held" if row["hold"] else row.get("state", "not checked")
        if row.get("live_error"):
            state += "; ERROR: " + row["live_error"]
        meter = row["meter"]
        aims = row.get("aims") or {}
        label = lambda kind: f"{aims[kind]['id']}: {aims[kind]['label']}" if aims.get(kind) else "NEEDS_AIMS"
        decisions = ", ".join(row.get("pending_proposal_ids", [])) or "none"
        values = [row["stream"], row["url"], state, label("main"), label("task"),
                  f"{progress.get('claimed', 0)} claimed / {progress.get('validated', 0)}/{progress.get('total', 0)} validated",
                  row.get("alignment", "UNKNOWN"), decisions + "; " + row.get("next", "review current evidence"), row["ci"]["flag"],
                  f"{meter['minutes']} min / {meter['pages']} pages / {meter['turns']} turns"]
        lines.append("| " + " | ".join(cell(value) for value in values) + " |")
    return "\n".join(lines)


def metric(r):
    messages = r["messages"].values()
    return {"turns": len(r["messages"]), "minutes": round(sum(m.get("minutes") or 0 for m in messages), 2),
            "pages": round(max([r.get("observed_pages", 0)] + [m.get("pages") or 0 for m in messages]), 2)}


def snapshot(p):
    return digest({k: p.get(k) for k in ("url", "state", "at_bottom", "user_ids", "latest_user", "latest_assistant", "draft", "status", "live_error")})


def identity(p):
    u = p.get("latest_user") or {}
    return bool(p.get("at_bottom") is True and u.get("id") and u.get("hash") and u["id"] in p.get("user_ids", []))


def elapsed(now, value):
    return (now - stamp(value)).total_seconds() / 60 if value else float("inf")


def action(s, label, r, p, kind, text="", detail="", task_ids=None):
    a = {"stream": label, "url": r["url"], "kind": kind}
    if detail:
        a["detail"] = detail
    if text:
        a.update(text=text, snapshot=snapshot(p), epoch=s["epoch"], policy=POLICY["version"])
        a["aim_token"] = aim_token(r)
        a["task_ids"] = list(task_ids or [])
        a["action_id"] = digest(a)
        r["last_action"] = a["action_id"]
    return a


def choose(s, label, r, p, now, status):
    def a(kind, text="", detail="", task_ids=None):
        return action(s, label, r, p, kind, text, detail, task_ids)
    state = p.get("state")
    if r["hold"] or s["status"] != "RUNNING":
        return None
    if r["denied"]:
        return a("DENIED", detail="explicit retry instruction needed")
    if r["pending"]:
        return a("DELIVERY_PENDING", detail=r["pending"]["ticket"])
    if state in ("LIMIT", "NOACCESS", "UNUSUAL"):
        return a(state, detail=p.get("live_error", ""))
    if p.get("live_error"):
        projection = r.get("aim_projection")
        if identity(p) and projection and projection["eligible_ids"] and state == "ERROR" and re.search(r"hmm\.{0,3}\s*something seems to have gone wrong", p["live_error"], re.I) and r["special"].get("RECOVER") != r["last_status_id"]:
            return a("RECOVER", text="proceed now", detail=p["live_error"], task_ids=projection["eligible_ids"])
        return a("ERROR", detail=p["live_error"])
    if state == "NOBOX":
        return a("ERROR", detail="composer unavailable")
    if state == "GENERATING":
        return None
    if not r.get("aim_projection"):
        return a("NEEDS_AIMS", detail=r.get("aim_error") or "approved main and task aims required")
    if not identity(p):
        return a("IDENTITY_REQUIRED", detail="stable user message IDs required before sending")
    if p.get("draft"):
        return a("SEND_DRAFT", text=p["draft"], detail="trusted runner must review the exact draft against the current aims before reservation")
    if r["waiting_assistant"] is not None:
        return None
    if not p.get("latest_assistant"):
        return None
    latest = p["latest_assistant"].get("id")
    if latest not in r["task_reports"]:
        return None
    if latest not in r["aim_projection"]["reviewed_message_ids"]:
        result = a("REVIEW_TASK_REPORT", detail="review relevance, proof and next permitted action for finished message " + latest)
        result["message_id"] = latest
        return result
    buddy = r["buddy"]
    if buddy and buddy.get("stage", "work") != "work":
        return a("HANDOVER_READY", detail="pinned lane active; follow handover reference")
    if status.get("handover", "").startswith(("ready", "s2ready")):
        return a("HANDOVER_READY", detail=status["handover"])
    if not r["plan"]:
        text = "" if r["special"].get("NEEDS_PLAN") else POLICY["messages"]["plan"]
        return a("NEEDS_PLAN", text=text, detail="current plan revision needed")
    m = metric(r)
    handover = any(m[k] >= v for k, v in POLICY["handover"].items()) or status.get("handover") == "due"
    if handover and not r["handover_hold"]:
        if not buddy:
            return a("NEEDS_PIN", detail="resolve BuddyRunner commit before handover")
        return a("HANDOVER", text=POLICY["messages"]["handover"].format(**buddy))
    bk = status.get("blocker") or {}
    if bk.get("kind") == "CI":
        repo = r["repo"]
        private = repo.get("private") is True and repo.get("verified") is True and bool(repo.get("source"))
        infrastructure = status.get("ci_kind") in ("runner", "billing", "queue", "infrastructure")
        if private and infrastructure:
            eligible = set(r["aim_projection"]["eligible_ids"])
            ids = [tid for tid in status.get("next", []) if tid in eligible and tid in r["plan"]["tasks"]]
            if not ids:
                return a("CI_BLOCKED", detail="no eligible registered task; resolve assignment, scope adoption or proof gates first")
            if r["special"].get("CI_FALLBACK") != r["last_status_id"]:
                return a("CI_FALLBACK", text=POLICY["messages"]["ci"], task_ids=list(dict.fromkeys(ids)))
            return None
        return a("CI_BLOCKED", detail="normal CI handling; no skip fallback")
    tasks = r["plan"]["tasks"]
    eligible = set(r["aim_projection"]["eligible_ids"])
    next_ids = list(dict.fromkeys(i for i in status.get("next", []) if i in tasks and i in eligible and tasks[i]["status"] in ("open", "claimed") and not tasks[i]["blocked"]))
    if bk.get("kind") in ("OWNER", "PERSON", "EXTERNAL") and not next_ids:
        if elapsed(now, r["last_ping"] or r["park_since"]) >= s["interval"]:
            return a("PING", text=POLICY["messages"]["ping"])
        return None
    if r["stall"] >= POLICY["stall_replies"] and r["special"].get("RECONCILE") != r["last_status_id"]:
        return a("RECONCILE", text=POLICY["messages"]["reconcile"])
    due = max([0] + r["aim_projection"]["due"])
    if due:
        if not buddy:
            return a("NEEDS_PIN", detail="resolve BuddyRunner commit for Y")
        return a("Y_CHECK", text=POLICY["messages"]["y"].format(**buddy), detail=str(due))
    if not next_ids:
        return a("PLAN_WAIT", detail="no open authorized next task; report blocker or plan revision")
    size = POLICY["batch_speed"] if mode(r) == "speed" else POLICY["batch_economy_good_y"] if r.get("y_decision") in ("CONTINUE", "NO_CHANGE", "CONTINUE/NO_CHANGE") else POLICY["batch_economy_other"]
    ids = next_ids[:size]
    approved = r["aim_projection"]["task"]
    outcome = f"registered outcomes and required proof under {approved['id']}: {approved['label']}"
    text = POLICY["messages"]["nudge"].format(ids=", ".join(ids), outcomes=outcome)
    if ci_policy(r)["mode"] == "limited":
        text += " Private-repo CI is limited: reuse evidence for this commit and local checks; request another remote run only for relevant code changes or an explicit Owner instruction."
    return a("NUDGE", text=text, task_ids=ids)


def observe(s, payload, now):
    probes = {}
    for p in payload.get("probes", []):
        url = conversation(p["url"])
        if url in probes:
            raise ValueError("duplicate conversation probe")
        probes[url] = p
    actions, changes, full = [], [], []
    for label, r in s["streams"].items():
        r["last_action"] = ""
        previous = aim_token(r)
        before_count = r["evidence"]
        refresh_aims(r)
        r["task_review_due"] = review_due(r)
        ledger_changed = previous != aim_token(r)
        if r["hold"]:
            r["summary"].update(aim_summary(r))
            continue
        p = probes.get(r["url"])
        if not p:
            summary = {"state": "NOT_OPEN", **aim_summary(r), "next": "wait for mapped conversation"}
            if r["summary"] != summary:
                changes.append({"stream": label, **summary})
            r["summary"] = summary
            continue
        r["last_probe"] = iso(now)
        fp = snapshot(p)
        changed = fp != r["fingerprint"]
        if changed or ledger_changed or mode(r) == "speed" or elapsed(now, r["last_full"]) >= POLICY["fallback_minutes"]:
            full.append(label)
            r["last_full"] = iso(now)
        r["fingerprint"] = fp
        completed = {m["id"]: m for m in p.get("completed_messages", []) if m.get("id")}
        for mid, m in completed.items():
            for k in ("minutes", "pages"):
                if m.get(k) is not None and (not isinstance(m[k], (int, float)) or m[k] < 0):
                    raise ValueError("invalid message metric")
            stored = r["messages"].setdefault(mid, {"minutes": None, "pages": None})
            r["task_reports"].setdefault(mid, {"observed_at": iso(now)})
            for key in ("minutes", "pages"):
                if m.get(key) is not None:
                    stored[key] = m[key]
        r["observed_pages"] = max(r.get("observed_pages", 0), p.get("pages") or 0)
        latest = (p.get("latest_assistant") or {}).get("id", "")
        finished = latest in completed
        status = (p.get("status") or {}) if finished else {}
        r["task_review_due"] = review_due(r)
        if r["waiting_assistant"] is not None and finished and latest != r["waiting_assistant"]:
            r["waiting_assistant"] = None
        if latest and finished and latest != r["last_status_id"]:
            r["last_status_id"] = latest
            delta = r["evidence"] - before_count
            for tid in dict.fromkeys(status.get("done", [])):
                if isinstance(tid, str) and tid:
                    matching = r["plan"] and status.get("plan_rev") == r["plan"]["rev"] and tid in r["plan"]["tasks"]
                    claim(r, tid, status.get("plan_rev"), "agent-report" if matching else "agent-report-off-plan", latest)
                    if matching:
                        r["plan"]["tasks"][tid]["status"] = "claimed"
            ac = status.get("ac")
            if isinstance(ac, (int, float)):
                r["ac"] = ac
            blocked = (status.get("blocker") or {}).get("kind") in ("OWNER", "PERSON", "EXTERNAL")
            if delta > 0:
                r["stall"] = 0
            elif not blocked:
                r["stall"] += 1
            if status.get("y_decision"):
                r["y_decision"] = status["y_decision"].replace(" ", "")
        bk = status.get("blocker") or {}
        if bk.get("kind") in ("OWNER", "PERSON", "EXTERNAL"):
            r["park_since"] = r["park_since"] or iso(now)
        else:
            r["park_since"] = r["last_ping"] = ""
        summary = {"state": p.get("state", "UNKNOWN"), "live_error": p.get("live_error", ""), "blocker": bk, **aim_summary(r),
                   "plan": r["plan"]["rev"] if r["plan"] else None,
                   "claimed_ac": r["ac"], "handover": status.get("handover", "no")}
        if p.get("state") == "UNUSUAL":
            s["unusual_day"] = (now + timedelta(hours=4)).date().isoformat()
        a = choose(s, label, r, p, now, status)
        summary["next"] = (a["kind"] + (" " + ", ".join(a.get("task_ids", [])) if a.get("task_ids") else "")) if a else "wait; no permitted send"
        if summary != r["summary"]:
            changes.append({"stream": label, **summary})
        r["summary"] = summary
        if a:
            actions.append(a)
    actions.sort(key=lambda a: (POLICY["priority"].index(a["kind"]) if a["kind"] in POLICY["priority"] else 999, a["stream"]))
    minutes = POLICY["report_speed_minutes"] if any(mode(r) == "speed" for r in s["streams"].values()) else POLICY["report_economy_minutes"]
    reviews = [{"stream": label, "url": r["url"], "message_id": mid,
                "workpack_id": (r.get("ledger") or {}).get("workpack_id")}
               for label, r in s["streams"].items() for mid in r["task_review_due"]]
    return {"actions": actions, "changes": changes, "full_check": full, "task_review_due": reviews,
            "report_due": elapsed(now, s.get("last_report", "")) >= minutes, "next_minutes": s["interval"]}


def reserve(s, payload, now):
    a, p = payload["action"], payload["probe"]
    r = s["streams"][a["stream"]]
    fresh = refresh_aims(r)
    reason = ""
    if s["status"] != "RUNNING" or r["hold"] or r["denied"]:
        reason = "scope held or denied"
    elif any(other["pending"] for other in s["streams"].values()):
        reason = "previous send unresolved"
    elif a.get("epoch") != s["epoch"] or a.get("policy") != POLICY["version"]:
        reason = "policy or configuration changed"
    elif not a.get("text") or a.get("action_id") != r["last_action"] or digest({k: v for k, v in a.items() if k != "action_id"}) != a["action_id"]:
        reason = "action not issued by latest planner"
    elif conversation(p["url"]) != r["url"] or a["snapshot"] != snapshot(p):
        reason = "conversation observation changed"
    elif not fresh or a.get("aim_token") != aim_token(r):
        reason = "aim ledger or approved scope changed; observe and review again"
    elif a["kind"] in ("NUDGE", "CI_FALLBACK", "RECOVER") and (not a.get("task_ids") or not set(a["task_ids"]) <= set(fresh["eligible_ids"])):
        reason = "task is no longer eligible under the approved aims"
    elif a["kind"] not in ("RECOVER", "SEND_DRAFT") and (p.get("latest_assistant") or {}).get("id") not in fresh["reviewed_message_ids"]:
        reason = "latest finished report has not been reviewed against the current aims"
    elif not identity(p) or not (p.get("state") == "IDLE" and not p.get("live_error") or a["kind"] == "RECOVER" and p.get("state") == "ERROR" and re.search(r"hmm\.{0,3}\s*something seems to have gone wrong", p.get("live_error", ""), re.I)):
        reason = "not an idle identified conversation"
    elif (p.get("draft", "") != a["text"]) if a["kind"] == "SEND_DRAFT" else bool(p.get("draft")):
        reason = "draft changed or composer occupied"
    if not reason and a["kind"] == "SEND_DRAFT":
        review = payload.get("draft_scope_review") or {}
        token = aim_token(r)
        if (review.get("within_scope") is not True or review.get("sequence") != token["sequence"] or
            review.get("main_id") != token["main_id"] or review.get("task_id") != token["task_id"] or
            review.get("draft_hash") != digest(p["draft"])):
            reason = "trusted runner must review this exact draft against the current ledger scope"
    gap = POLICY["unusual_gap_seconds"] if s.get("unusual_day") == (now + timedelta(hours=4)).date().isoformat() else POLICY["send_gap_seconds"]
    last = s.get("last_send")
    if not reason and last and last["stream"] != a["stream"] and (now - stamp(last["at"])).total_seconds() < gap:
        reason = "send spacing not reached"
    if reason:
        return {"result": "STOP", "reason": reason}
    ticket = uuid.uuid4().hex
    r["pending"] = {"ticket": ticket, "hash": content_hash(a["text"]), "before": list(p["user_ids"]), "assistant": (p.get("latest_assistant") or {}).get("id", ""), "kind": a["kind"], "detail": a.get("detail", ""), "reserved": iso(now),
                    "aim_token": a.get("aim_token"), "task_ids": a.get("task_ids", []),
                    "draft_scope_review": copy.deepcopy(payload.get("draft_scope_review")) if a["kind"] == "SEND_DRAFT" else None}
    return {"result": "RESERVED", "ticket": ticket}


def verify(s, payload, now):
    ticket, p = payload["ticket"], payload["probe"]
    for label, r in s["streams"].items():
        if r["last_ticket"] and r["last_ticket"]["ticket"] == ticket:
            return {"result": "DELIVERED", **r["last_ticket"]}
        q = r["pending"]
        if not q or q["ticket"] != ticket:
            continue
        user = p.get("latest_user") or {}
        if conversation(p["url"]) != r["url"] or not identity(p) or user["id"] in q["before"] or user.get("hash") != q["hash"]:
            return {"result": "UNCERTAIN", "ticket": ticket}
        r["last_ticket"] = {"ticket": ticket, "message": user["id"]}
        r["waiting_assistant"] = q["assistant"]
        r["special"][q["kind"]] = r["last_status_id"]
        if q["kind"] == "PING":
            r["last_ping"] = iso(now)
        # Sending Y is not a recorded reconciliation. Only the ledger sets checkpoint.
        if q["kind"] == "HANDOVER":
            r["buddy"]["stage"] = "1a_requested"
        r["pending"] = None
        r["last_action"] = ""
        s["last_send"] = {"stream": label, "at": iso(now)}
        return {"result": "DELIVERED", **r["last_ticket"]}
    raise ValueError("unknown delivery ticket")


def upgrade(s, now):
    if s.get("schema") != 1 or s.get("version") != "3.27":
        raise ValueError("upgrade accepts only coordinator schema 1 version 3.27")
    lease = s.get("lease")
    if lease and stamp(lease["until"]) > now:
        raise ValueError("active legacy lease must finish before upgrade")
    for r in s.get("streams", {}).values():
        old_closed = copy.deepcopy(r.get("closed", {}))
        old_progress = {k: copy.deepcopy(r.get(k)) for k in ("evidence", "checkpoint", "closed")}
        defaults = stream_record({"url": r["url"]})
        for key, value in defaults.items():
            r.setdefault(key, copy.deepcopy(value))
        r["legacy_progress"] = old_progress
        for tid, old in old_closed.items():
            claim(r, tid, old.get("rev"), "legacy-unvalidated-closure", old.get("message", ""))
        if r["plan"]:
            original = copy.deepcopy(r["plan"])
            if original not in r["plan_history"]:
                r["plan_history"].append(original)
            for tid, task in r["plan"]["tasks"].items():
                if task.get("status") == "done":
                    task["status"] = "claimed"
                    claim(r, tid, r["plan"]["rev"], "legacy-plan-baseline")
        r.update(closed={}, evidence=0, checkpoint=0, ledger=None, aim_projection=None,
                 aim_error="upgraded claims require an approved aim ledger binding", last_action="")
        r["summary"].update(aim_summary(r))
        r["summary"]["next"] = "NEEDS_AIMS; keep the upgraded session held"
    s.update(schema=POLICY["schema"], version=POLICY["version"], status="HOLD", epoch=s.get("epoch", 0) + 1)
    return {"result": "UPGRADED", "status": "HOLD", "schema": s["schema"],
            "pending_preserved": sum(bool(r.get("pending")) for r in s["streams"].values())}


def operate(s, command, payload):
    now = stamp(payload.get("now"))
    if command == "upgrade":
        return upgrade(s, now)
    if command == "init":
        if s:
            raise ValueError("state already exists; use control/update")
        if payload.get("interval") not in POLICY["intervals"]:
            raise ValueError("select interval 10, 15 or 30")
        streams = {k: stream_record(v) for k, v in payload.get("streams", {}).items()}
        if len({r["url"] for r in streams.values()}) != len(streams):
            raise ValueError("one conversation cannot map to two streams")
        s.update(schema=POLICY["schema"], version=POLICY["version"], epoch=0, revision=0,
                 session=payload.get("session", "coordinator"), status="HOLD", interval=payload["interval"], streams=streams,
                 heartbeat="", lease=None, last_send=None, last_report="")
        return {"result": "INITIALIZED", "status": "HOLD", "streams": len(streams)}
    if s.get("schema") != POLICY["schema"] or s.get("version") != POLICY["version"]:
        raise ValueError("incompatible state; do not overwrite legacy or Codex state")
    if command == "control":
        if payload.get("status", s["status"]) not in ("HOLD", "RUNNING"):
            raise ValueError("status must be HOLD/RUNNING")
        if payload.get("interval", s["interval"]) not in POLICY["intervals"]:
            raise ValueError("select interval 10, 15 or 30")
        for key in ("status", "interval", "heartbeat"):
            if key in payload:
                s[key] = payload[key]
        s["epoch"] += 1
        return {"result": "CONFIGURED", "status": s["status"], "interval": s["interval"]}
    if command == "lease":
        owner = payload["owner"]
        lease = s["lease"]
        if lease and lease["owner"] != owner and stamp(lease["until"]) > now:
            return {"result": "BUSY", "owner": lease["owner"]}
        seconds = payload.get("seconds", 180)
        if not isinstance(seconds, (int, float)) or not 0 <= seconds <= 600:
            raise ValueError("lease must be 0..600 seconds; renew during long cycles")
        s["lease"] = {"owner": owner, "until": iso(now + timedelta(seconds=seconds))} if seconds else None
        return {"result": "LEASED" if seconds else "RELEASED"}
    lease = s.get("lease")
    if command in ("observe", "reserve") and lease and stamp(lease["until"]) > now and payload.get("owner") != lease["owner"]:
        return {"result": "BUSY", "owner": lease["owner"]}
    if command == "update":
        label = payload["stream"]
        if label not in s["streams"]:
            s["streams"][label] = stream_record(payload["patch"])
        else:
            patch_stream(s["streams"][label], payload["patch"])
        if len({r["url"] for r in s["streams"].values()}) != len(s["streams"]):
            raise ValueError("duplicate stream conversation")
        s["epoch"] += 1
        return {"result": "UPDATED", "stream": label}
    if command == "observe":
        return observe(s, payload, now)
    if command == "reserve":
        return reserve(s, payload, now)
    if command == "verify":
        return verify(s, payload, now)
    if command == "resolve":
        if payload.get("disposition") not in ("not_sent", "abandon") or not payload.get("evidence"):
            raise ValueError("resolution requires not_sent/abandon and evidence or explicit instruction")
        for r in s["streams"].values():
            if r["pending"] and r["pending"]["ticket"] == payload["ticket"]:
                r["pending"] = None
                r["last_action"] = ""
                return {"result": "RESOLVED", "disposition": payload["disposition"]}
        raise ValueError("unknown pending ticket")
    if command == "report":
        s["last_report"] = iso(now)
        for r in s["streams"].values():
            refresh_aims(r)
            r["task_review_due"] = review_due(r)
            r["summary"].update(aim_summary(r))
            p = r.get("aim_projection")
            if r["hold"] or s["status"] != "RUNNING":
                next_step = "held; no sends"
            elif r["pending"]:
                next_step = "resolve uncertain delivery; no competing send"
            elif not p:
                next_step = "NEEDS_AIMS"
            elif r["task_review_due"]:
                next_step = "REVIEW_TASK_REPORT " + ", ".join(r["task_review_due"])
            elif p["due"]:
                next_step = "reconcile validated checkpoints " + ", ".join(map(str, p["due"]))
            elif p["eligible_ids"]:
                next_step = "reobserve before dispatch; eligible registered tasks: " + ", ".join(p["eligible_ids"])
            else:
                next_step = "wait; no eligible registered task under the current scope"
            r["summary"]["next"] = next_step
        rows = [{"stream": k, "url": r["url"], "mode": mode(r), "hold": r["hold"], **r["summary"], "ci": ci_policy(r), "meter": metric(r), "tasks_closed": len(r["closed"]), "pending": bool(r["pending"])} for k, r in s["streams"].items()]
        return {"status": s["status"], "interval": s["interval"], "streams": rows, "table": report_table(rows)}
    raise ValueError("unknown command")


def transaction(path, command, payload):
    path = Path(path).resolve()
    with locked(path):
        state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        result = operate(state, command, payload)
        state["revision"] = state.get("revision", 0) + 1
        atomic_save(path, state)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True)
    parser.add_argument("command", choices=("init", "upgrade", "control", "observe", "reserve", "verify", "resolve", "update", "report", "lease"))
    parser.add_argument("--input")
    args = parser.parse_args()
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8")) if args.input else {} if args.command == "report" else json.load(sys.stdin)
        print(json.dumps(transaction(args.state, args.command, payload), ensure_ascii=False, separators=(",", ":")))
    except (ValueError, KeyError, OSError, TypeError) as error:
        print(json.dumps({"result": "ERROR", "reason": str(error)}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
