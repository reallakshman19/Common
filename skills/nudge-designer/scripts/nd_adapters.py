"""Orthogonal audience/surface adapters. Packets are manual, never native dispatch."""
import hashlib

from nd_contract import intent_index, nudge_context, validate_plan
from nd_io import quoted, references, require
from nd_render import data, render_nudge
from nd_returns import receive
from nd_team import ROLES, capability_fit, nudge_by_id, task_binding

SURFACES = ("plain", "github", "nextnudge-manual", "buddy-checkpoint", "delivery")


def role_content(intent, plan, nudge, audience, worksheet):
    if audience in ("worker", "specialist"):
        # Filled by caller, so the standard seven-element renderer stays canonical.
        return None
    sources, items, outcomes = intent_index(intent)
    relevant, context_items, source_ids, _ = nudge_context(intent, nudge, plan)
    lines = ["# " + audience.title() + " view", "", "Owner outcome: " + data(intent["purpose"]),
             "Direction: " + data(plan["strategy"]), "This work: " + data(nudge["purpose"]),
             "", ("Issued task: " if worksheet else "Next proposed work: ") + data(nudge["deliverable"])]
    if audience == "owner":
        lines += ["Changed understanding: " + data(plan["handover"]["changed_understanding"])]
    if audience in ("designer", "reviewer"):
        lines += ["", "## Evidence and challenge", "", "Observable: " + data(nudge["success"]["observable"]),
                  "Contradicting/contrast case: " + data(nudge["success"]["negative_case"])]
        lines += ["- " + key + " [" + items[key]["kind"] + "]: " + data(items[key]["text"])
                  for key in sorted(context_items)]
        lines += ["Review the original conditions, model assumptions and actual returned artifact.",
                  "A role label, recorded fit or supplied PASS does not establish independence or acceptance."]
    if audience in ("coordinator", "successor"):
        lines += ["", "## Work and continuation", ""]
        lines += ["- " + row["id"] + ": " + data(row["purpose"]) + "; dependencies: " + quoted(row["depends_on"])
                  for row in plan["nudges"]]
        lines += ["Remaining: " + quoted(plan["handover"]["remaining"]),
                  "Changed understanding: " + data(plan["handover"]["changed_understanding"]),
                  "Thinking protocol: " + quoted(intent["protocols"]["thinking"]),
                  "Delivery protocol: " + quoted(intent["protocols"]["delivery"]),
                  "Use issued snapshots and actual returns; reassess source freshness before dependent actions."]
    lines += ["", "## Preserved conditions and unresolved work", ""]
    for key in sorted(context_items):
        item = items[key]
        if item["kind"] in ("CONSTRAINT", "UNKNOWN"):
            lines.append("- " + key + ": " + data(item["condition"] or item["text"]))
    lines += ["- " + data(value) for value in nudge["uncertainty"]["missing"]]
    lines += ["Independent useful work: " + quoted(nudge["uncertainty"]["independent_work"]),
              "Return/decision condition: " + data(nudge["uncertainty"]["return_with"]),
              "Next eligible action: " + data(nudge["report"]["next_action"])]
    if worksheet:
        lines += ["", "## Actual return received", "", "Status claimed: " + worksheet["claimed_status"],
                  "Native report: " + quoted(worksheet["native_report"]["locator"]),
                  "Native content digest: " + quoted(worksheet["native_content_sha256"]),
                  "Source freshness: " + worksheet["freshness"]]
        lines += ["- " + row["declared_kind"] + ": " + data(row["text"]) for row in worksheet["findings"]]
        lines += ["Proposal to reconcile: " + data(worksheet["next_proposal"]),
                  "Intake preserves claims; execution, semantic conclusions and acceptance remain unverified."]
        if audience in ("designer", "reviewer"):
            if worksheet["native_report"]["content"] is None:
                lines += ["Native artifact is reference-only; use an authorized reader before assessing its content."]
            else:
                lines += ["Native report (quoted data): " + data(worksheet["native_report"]["content"])]
            lines += ["- Attempt " + row["id"] + " [" + row["state"] + "]: " + data(row["action"]) +
                      "; observed: " + data(row["observed"]) for row in worksheet["attempts"]]
    lines += ["", "## Source references", ""]
    lines += ["- " + key + ": " + quoted(sources[key]["locator"]) + " revision " + quoted(sources[key]["revision"])
              for key in sorted(source_ids)]
    return "\n".join(lines)


def adapt(intent, plan, nudge_id, profiles, audience="worker", surface="plain", recipient_id=None, report=None):
    validate_plan(intent, plan, profiles)
    require(audience in ROLES, "unknown audience")
    require(surface in SURFACES, "unknown surface adapter")
    nudge = nudge_by_id(plan, nudge_id)
    people = {row["id"]: row for row in plan.get("participants", [])}
    if recipient_id is not None:
        references([recipient_id], people, "recipient")
    worksheet = receive(intent, plan, report, profiles) if report is not None else None
    if worksheet:
        require(worksheet["binding"]["nudge_id"] == nudge_id, "returned report belongs to another nudge")
    if surface == "delivery":
        require(intent["protocols"]["delivery"] is not None, "delivery protocol must be explicitly selected")
    content = role_content(intent, plan, nudge, audience, worksheet)
    if content is None:
        content = render_nudge(intent, plan, nudge_id, profiles)
        if worksheet:
            content += "\n\nReturn available (requires reconciliation): " + worksheet["claimed_status"]
            content += "\nNative report: " + quoted(worksheet["native_report"]["locator"])
            content += "\nProposal: " + data(worksheet["next_proposal"])
    prefixes = {
        "plain": "",
        "github": "<!-- Nudge Designer: proposed Markdown; publication requires existing task authority. -->\n\n",
        "nextnudge-manual": "NextNudge manual-copy draft; not a native import or sent instruction.\nType: " + nudge["type"] + "\n\n",
        "buddy-checkpoint": "BuddyRunner supporting checkpoint; no mode, stage or continuation approval is asserted.\n\n",
        "delivery": "Prepared for explicitly selected delivery protocol: " + quoted(intent["protocols"]["delivery"]) +
                    "\nRead that protocol before coding; no legacy thinking/handover selection is imported.\n\n"}
    contributors = set(report["contributors"]) if report else set()
    if report and report["actor_id"]:
        contributors.add(report["actor_id"])
    conflict = "SAME_RECORDED_PARTICIPANT" if audience == "reviewer" and recipient_id in contributors else "NOT_ESTABLISHED"
    binding = task_binding(intent, plan, nudge_id)
    content += "\n\nIssued work: " + plan["id"] + " revision " + str(plan["revision"]) + "; nudge " + nudge_id
    content += "\nPlan digest: " + binding["plan_sha256"] + "; intent digest: " + binding["intent_sha256"]
    content = prefixes[surface] + content
    return {"adapter": surface, "audience": audience, "recipient_id": recipient_id,
            "recipient_role_supported": audience.upper() in people[recipient_id]["roles"] if recipient_id else None,
            "binding": binding, "content": content,
            "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "capability_fit": capability_fit(plan, nudge_id), "review_conflict": conflict,
            "independence_verified": False, "authority_verified": False, "execution_dispatched": False,
            "native_import_object": False, "workflow_locked": False,
            "delivery": "MANUAL_UNDER_EXISTING_AUTHORITY", "source_authentication": "NOT_PERFORMED"}
