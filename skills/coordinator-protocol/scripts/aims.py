"""Coordinator-owned aim/evidence commands and portable reports; no external actions."""
import argparse
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import sqlite3
import sys
from aim_store import Store, InvariantError


def required(data, key):
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a nonempty string")
    return value


def latest(records):
    return records[-1] if records else {}


def text_cell(value):
    return str(value if value is not None else "Unspecified").replace("|", "/").replace("\n", " ")


def compact_item(item):
    record = item["record"]
    keys = ("id", "task_id", "aim_id", "main_aim_id", "workpack_id", "message_id", "verdict", "result", "outcome", "proposal_id", "claim", "reason", "summary", "suggestion", "authority_ref", "recipient", "artifact", "proof_source")
    return {"kind": item["kind"], **{key: record[key] for key in keys if key in record}}


def record_task_report(store, ns, data):
    for key in ("id", "recipient", "workpack_id", "message_id", "summary", "alignment", "source_ref", "next_action"):
        required(data, key)
    if not isinstance(data.get("gaps"), list):
        raise ValueError("gaps must be explicit, including an empty list when none remain")
    assessments = data.get("assessments", [])
    if not isinstance(assessments, list):
        raise ValueError("assessments must be a list")
    # Each insert is idempotent. A failed/crashed submission never marks a report
    # reviewed until all assessments and its inspectable report are durable.
    for assessment in assessments:
        store.assess_task(assessment, namespace=ns)
    record = {k: v for k, v in data.items() if k != "assessments"}
    record.update(report_type="task", assessment_ids=[a["id"] for a in assessments])
    existing = next((r for r in store.list("report", ns) if r["id"] == record["id"]), None)
    if existing:
        record["aim_refs"] = existing["aim_refs"]
    else:
        record["aim_refs"] = {key: (value or {}).get("id") for key, value in store.current_aims(ns).items()}
    store.append("report", record, namespace=ns)
    store.append("control", {"id": "review:" + data["id"], "control_type": "TASK_REPORT_REVIEW",
        "recipient": data["recipient"], "workpack_id": data["workpack_id"], "message_id": data["message_id"],
        "assessment_ids": record["assessment_ids"], "report_id": data["id"], "reason": data["summary"],
        "source_ref": data["source_ref"], "alignment": data["alignment"]}, namespace=ns)
    return record


def record_handover_report(store, ns, data):
    handover = data.get("handover", {})
    for key in ("id", "from", "to", "workpack_id", "main_aim_id", "task_aim_id", "response_2_id", "authority_ref", "source_ref", "summary"):
        required(handover, key)
    if handover.get("owner_authorized") is not True:
        raise ValueError("handover needs the existing Owner-authorized recipient mapping")
    for key in ("unfinished_task_ids", "drift_ids", "roi_ids"):
        if not isinstance(handover.get(key), list):
            raise ValueError(f"handover {key} must be explicit")
    for kind, key in (("drift", "drift_ids"), ("roi", "roi_ids")):
        known = {r["id"] for r in store.list(kind, ns)}
        if not set(handover[key]) <= known:
            raise ValueError(f"handover cites unknown {kind}")
    suggestion = handover.get("main_aim_suggestion", "")
    if suggestion and len(suggestion.split()) >= 50:
        raise ValueError("Main Aim suggestion must be fewer than 50 words")
    store.append("handover", handover, namespace=ns)
    report = {"id": "handover-report:" + handover["id"], "report_type": "handover", "handover_id": handover["id"],
        "recipient": handover["to"], "workpack_id": handover["workpack_id"], "summary": handover["summary"],
        "source_ref": handover["source_ref"], "aim_refs": {"main": handover.get("main_aim_id"), "task": handover.get("task_aim_id")}}
    store.append("report", report, namespace=ns)
    return report


def report_data(store, ns, workpack, recipient):
    projection = store.projection(ns, workpack, recipient)
    records = store.snapshot(ns)
    tasks = [t for t in records["task"] if t["workpack_id"] == workpack]
    task_ids = {t["id"] for t in tasks}
    assessments = {a["task_id"]: a for a in records["assessment"] if a["task_id"] in task_ids}
    reports = [r for r in records["report"] if r.get("workpack_id") == workpack]
    handovers = [h for h in records["handover"] if h.get("workpack_id") == workpack]
    return {"namespace": ns, "workpack": workpack, "recipient": recipient, "projection": projection,
        "tasks": tasks, "assessments": assessments, "task_report": latest([r for r in reports if r.get("report_type") == "task"]),
        "handover": latest(handovers), "reports": reports, "records": records}


def unfinished_criteria(data):
    aims = {a["id"]: a for a in data["records"]["aim"]}
    selected = set(data["handover"].get("unfinished_task_ids", []))
    rows = []
    for task in data["tasks"]:
        if task["id"] not in selected:
            continue
        criteria = {c["id"]: c["text"] for c in aims.get(task["aim_id"], {}).get("criteria", [])}
        rows.append([task["id"], task["aim_id"], "; ".join(f"{c}: {criteria.get(c, 'Recall criterion before proceeding')}" for c in task["criterion_ids"])])
    return rows


def handover_summaries(data):
    h, records = data["handover"], data["records"]
    drift = [r for r in records["drift"] if r["id"] in h.get("drift_ids", [])]
    roi = [r for r in records["roi"] if r["id"] in h.get("roi_ids", [])]
    drift_lines = [f"{r['id']}: {r.get('comparison', r.get('summary', 'Comparison not supplied'))}; judgement: {r.get('verdict', 'Not assessed')}; correction: {r.get('correction', 'Not supplied')}" for r in drift]
    roi_lines = [f"{r['id']} — {r.get('agent', 'Unattributed agent')} claims: {r.get('claim', r.get('benefit_claim', 'Not supplied'))}; effort: {r.get('effort', 'Unknown')}; confidence: {r.get('confidence', 'Unverified')}; displaces: {r.get('displaced_work', 'Unknown')}" for r in roi]
    return drift_lines, roi_lines


def markdown(data):
    p = data["projection"]
    def aimline(key):
        a = p.get(key) or {}
        return f"**{key.title()} Aim · {a.get('id', 'not registered')}:** {a.get('label', 'Ground this stream before product follow-ups.')}"
    lines = [aimline("main"), "", aimline("task"), "",
        "| Stream | Alignment | Validated planned outcomes | Checkpoint due | Pending decisions |",
        "| --- | --- | --- | --- | --- |",
        "| " + " | ".join(text_cell(x) for x in [data["namespace"], p["alignment"], f"{len(p['validated_ids'])}/{len(p['registered_ids'])}", ", ".join(map(str, p["due"])) or "None", ", ".join(p["pending_proposal_ids"]) or "None"]) + " |"]
    r = data["task_report"]
    if r:
        refs = r.get("aim_refs", {})
        lines += ["", f"**Task report {r['id']} · {refs.get('main', 'unset')} / {refs.get('task', 'unset')}:** {r['summary']}",
                  f"Evidence gaps: {'; '.join(map(str, r.get('gaps', []))) or 'None recorded'}", f"Next permitted action: {r['next_action']}"]
    h = data["handover"]
    if h:
        drift, roi = handover_summaries(data)
        lines += ["", f"**Handover {h['id']}:** {h.get('summary', 'Review incoming plan against the current aim.')}",
                  f"Retained: {len(p['validated_ids'])}/{len(p['registered_ids'])} validated; reviewed checkpoints: {', '.join(map(str, p['reviewed_thresholds'])) or 'None'}.",
                  f"Outgoing drift: {' | '.join(drift) or 'None recorded; absence does not mean checked.'}",
                  f"ROI claims (attributed below; incoming claim may be missing): {' | '.join(roi) or 'Not supplied'}",
                  "", "Unfinished requirements:", ""]
        lines += [f"- {tid} · starting {aid} — {criteria}" for tid, aid, criteria in unfinished_criteria(data)] or ["- None recorded."]
        lines += ["", "Next authorized step: " + h.get("next_allowed_work", "Verify successor delivery, acknowledgement and plan adoption before product work.")]
        if h.get("main_aim_suggestion"):
            lines += ["Main Aim suggestion: " + h["main_aim_suggestion"]]
    return "\n".join(lines) + "\n"


def html_report(data):
    p, records = data["projection"], data["records"]
    e = lambda x: html.escape(str(x if x is not None else "Unspecified"))
    def details(rows):
        return "".join(f"<details><summary>{e(r.get('id', 'record'))}</summary><pre>{e(json.dumps(r, ensure_ascii=False, indent=2))}</pre></details>" for r in rows) or "<p>No records yet.</p>"
    def table(headers, rows):
        return "<div class='tablewrap'><table><thead><tr>" + "".join(f"<th>{e(v)}</th>" for v in headers) + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{e(v)}</td>" for v in row) + "</tr>" for row in rows) + "</tbody></table></div>"
    aims = "".join(f"<div><small>{e(k.title())} AIM · {e((p.get(k) or {}).get('id', 'unset'))}</small><p>{e((p.get(k) or {}).get('label', 'Not registered'))}</p></div>" for k in ("main", "task"))
    task = data["task_report"]
    task_body = (f"<h2>{e(task.get('summary', 'No task report yet'))}</h2><p>Starting/report revisions: {e(task.get('aim_refs', {}))}</p><p>Gaps: {e('; '.join(map(str, task.get('gaps', []))) or 'None recorded')}</p><p><strong>Next:</strong> {e(task.get('next_action', 'Review the next actual report.'))}</p>" + table(["Task / starting aim", "Review", "Evidence IDs"], [[t["id"] + " / " + t["aim_id"], data["assessments"].get(t["id"], {}).get("verdict", "UNVERIFIED"), ", ".join(data["assessments"].get(t["id"], {}).get("evidence_ids", []))] for t in data["tasks"]]))
    status = table(["Stream", "Aim / proof", "Next eligible tasks", "Decisions"], [[data["namespace"], f"{p['alignment']} · {len(p['validated_ids'])}/{len(p['registered_ids'])} validated", ", ".join(p["eligible_ids"]) or "None", ", ".join(p["pending_proposal_ids"]) or "None"]]) + "<p>Transport state, holds, CI flags and mapped chat links appear in cycle.py report. This view does not imply a running chat.</p>"
    h = data["handover"]
    selected_drift = [r for r in records["drift"] if r["id"] in h.get("drift_ids", [])]
    selected_roi = [r for r in records["roi"] if r["id"] in h.get("roi_ids", [])]
    drift_lines, roi_lines = handover_summaries(data)
    handover = f"<p>{e(h.get('summary', 'No handover recorded.'))}</p><p>Retained: {len(p['validated_ids'])}/{len(p['registered_ids'])} validated; reviewed checkpoints: {e(', '.join(map(str, p['reviewed_thresholds'])) or 'None')}.</p><p>Optional Main Aim suggestion: {e(h.get('main_aim_suggestion', 'None'))}</p><div class='columns'><div><h3>Outgoing drift</h3><p>{e(' | '.join(drift_lines) or 'Not assessed')}</p>{details(selected_drift)}</div><div><h3>Attributed ROI claims</h3><p>{e(' | '.join(roi_lines) or 'Incoming claim not supplied')}</p>{details(selected_roi)}</div></div><h3>Unfinished requirements</h3>{table(['Task', 'Starting aim', 'Required proof'], unfinished_criteria(data))}<h3>Adoption evidence</h3>{details(records['adoption'])}<p>Next: {e(h.get('next_allowed_work', 'Verify successor delivery, acknowledgement and plan adoption before product work.'))}</p>"
    changes = "<p>Evidence → proposal → impact review → Owner decision → revision → agent adoption → verified benefit</p><p>A pending proposal leaves current aims in force. Adoption alone does not prove benefit.</p><h3>Proposals</h3>" + details(records["proposal"]) + "<h3>Decisions</h3>" + details(records["decision"])
    recall = "<label for='recall'>Find an ID or phrase</label><input id='recall' type='search' placeholder='Search stored records'><div id='matches'>" + "".join("<div class='recall-record'>" + f"<small>{e(kind)}</small>" + details([r]) + "</div>" for kind, rows in records.items() if kind != "report" for r in rows) + "</div>"
    views = [("task", "After a task", task_body), ("status", "Tab status", status), ("handover", "Agent handover", handover), ("changes", "Change management", changes), ("memory", "Store & recall", recall)]
    nav = "".join(f"<button data-view='{key}' aria-pressed='{str(i == 0).lower()}'>{title}</button>" for i, (key, title, _) in enumerate(views))
    sections = "".join(f"<section id='{key}' {'hidden' if i else ''}><h1>{title}</h1>{body}</section>" for i, (key, title, body) in enumerate(views))
    css = """body{font:15px/1.5 system-ui;margin:0;background:#f2f5f4;color:#163537}main{max-width:1180px;margin:auto;padding:24px}header{display:flex;justify-content:space-between;gap:15px;flex-wrap:wrap}h1{font-size:23px}h2{font-size:19px}.aims{background:#163537;color:white;border-radius:12px;padding:20px;display:grid;grid-template-columns:1fr 1fr;gap:24px;margin:20px 0}.aims p{font-size:18px;margin:7px 0}.aims small{letter-spacing:1px}nav{display:flex;gap:8px;flex-wrap:wrap}button{font:inherit;border:1px solid #ccd9d7;background:white;border-radius:8px;padding:10px;cursor:pointer}button[aria-pressed=true]{background:#163537;color:white}section{margin-top:20px;background:white;border:1px solid #d4dfdd;border-radius:12px;padding:20px}.tablewrap{overflow:auto}table{border-collapse:collapse;width:100%}th,td{text-align:left;vertical-align:top;border-bottom:1px solid #d4dfdd;padding:12px}th{font-size:12px}td{overflow-wrap:anywhere}.columns{display:grid;grid-template-columns:1fr 1fr;gap:20px}details{padding:8px 0;border-bottom:1px solid #ddd}summary{cursor:pointer;color:#076b63}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}input{font:inherit;padding:10px;margin:10px 0;display:block;width:100%;box-sizing:border-box}footer{font-size:12px;margin:20px 0;color:#50686a}button:focus-visible,input:focus-visible,summary:focus-visible{outline:3px solid #138a7a;outline-offset:2px}@media(max-width:700px){main{padding:15px}.aims,.columns{grid-template-columns:1fr}.aims p{font-size:16px}th,td{min-width:130px}nav button{flex:1}}"""
    js = """document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('section').forEach(s=>s.hidden=s.id!==b.dataset.view);document.querySelectorAll('[data-view]').forEach(n=>n.setAttribute('aria-pressed',String(n===b)))}));document.getElementById('recall').addEventListener('input',e=>{let q=e.target.value.toLowerCase();document.querySelectorAll('.recall-record').forEach(r=>r.hidden=!r.textContent.toLowerCase().includes(q))});"""
    return f"<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Aim and evidence report</title><style>{css}</style><main><header><strong>Aim & evidence</strong><span>{e(data['namespace'])} · {e(data['workpack'])} · READ-ONLY REPORT</span></header><div class='aims'>{aims}</div><nav aria-label='Report views'>{nav}</nav>{sections}<footer>Generated {e(datetime.now(timezone.utc).isoformat(timespec='seconds'))}. Historical receipts retain their original artifact and aim revisions. This report sends nothing and grants no approval.</footer></main><script>{js}</script></html>"


def render(store, ns, workpack, recipient, output_dir=None):
    data = report_data(store, ns, workpack, recipient)
    result = {"projection": data["projection"], "markdown": markdown(data)}
    if output_dir:
        folder = Path(output_dir); folder.mkdir(parents=True, exist_ok=True)
        (folder / "status.md").write_text(result["markdown"], encoding="utf-8")
        (folder / "status.html").write_text(html_report(data), encoding="utf-8")
        result["files"] = {"markdown": str((folder / "status.md").resolve()), "visual": str((folder / "status.html").resolve())}
    return result


def execute(store, ns, command, data, workpack=None, recipient=None, output_dir=None):
    record = None
    if command == "record":
        if data["kind"] in ("decision", "report", "handover"):
            raise ValueError("use decide, task-report or handover-report for protected records")
        record = store.append(data["kind"], data["record"], namespace=ns)
    elif command == "decide":
        record = store.decide(namespace=ns, **data)
    elif command == "task-report":
        record = record_task_report(store, ns, data)
        workpack, recipient = data["workpack_id"], data["recipient"]
    elif command == "handover-report":
        record = record_handover_report(store, ns, data)
        workpack, recipient = record["workpack_id"], record["recipient"]
    elif command == "recall":
        result = store.recall(query=data.get("query"), ids=data.get("ids"), kinds=data.get("kinds"), namespace=ns, max_items=data.get("limit", 12))
        if not data.get("full"):
            result["items"] = [compact_item(r) for r in result["items"]]
        return result
    elif command != "report":
        raise ValueError("unknown command")
    if workpack and recipient:
        result = render(store, ns, workpack, recipient, output_dir)
        if record: result["recorded_id"] = record["id"]
        return result
    if command == "report":
        raise ValueError("report requires --workpack and --recipient")
    return {"recorded_id": record["id"], "kind": command}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", required=True); p.add_argument("--scope", required=True)
    p.add_argument("--workpack"); p.add_argument("--recipient"); p.add_argument("--output-dir")
    p.add_argument("command", choices=["record", "task-report", "handover-report", "decide", "recall", "report"])
    p.add_argument("--input")
    args = p.parse_args()
    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8-sig")) if args.input else {} if args.command == "report" else json.load(sys.stdin)
        with Store(args.db, read_only=args.command in ("report", "recall")) as store:
            result = execute(store, args.scope, args.command, data, args.workpack, args.recipient, args.output_dir)
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    except (ValueError, KeyError, TypeError, OSError, sqlite3.Error, InvariantError) as error:
        print(json.dumps({"result": "ERROR", "reason": str(error)})); raise SystemExit(1)


if __name__ == "__main__": main()
