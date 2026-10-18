"""Suggest revision impact from declared references; never edit or certify plans."""
from nd_contract import intent_index, nudge_context, validate_intent, validate_plan
from nd_io import require


def changed_rows(before, after):
    return {key for key in set(before) | set(after) if before.get(key) != after.get(key)}


def impact_report(previous_intent, previous_plan, current_intent, profiles):
    validate_plan(previous_intent, previous_plan, profiles)
    validate_intent(current_intent)
    require(previous_intent["id"] == current_intent["id"], "impact comparison needs the same intent ID")
    old_sources, old_items, old_outcomes = intent_index(previous_intent)
    sources, items, outcomes = intent_index(current_intent)
    changed_sources = changed_rows(old_sources, sources)
    changed_items = changed_rows(old_items, items)
    for key, item in old_items.items():
        if changed_sources & set(item["source_refs"]):
            changed_items.add(key)
    changed_outcomes = changed_rows(old_outcomes, outcomes)
    for key, outcome in old_outcomes.items():
        if set(outcome["item_refs"]) & changed_items:
            changed_outcomes.add(key)
    global_change = any(previous_intent[key] != current_intent[key]
                        for key in ("owner_request", "purpose", "scope", "worker", "protocols"))
    changed_constraints = [row for group in (old_items, items) for key, row in group.items()
                           if key in changed_items and row["kind"] == "CONSTRAINT"
                           and row["state"] != "SUPERSEDED"]
    old_knowledge, knowledge = previous_intent["knowledge"], current_intent["knowledge"]
    changed_knowledge = ([row for row in old_knowledge if row not in knowledge] +
                         [row for row in knowledge if row not in old_knowledge])
    knowledge_outcomes = set()
    global_knowledge = False
    for row in changed_knowledge:
        if not row["outcome_refs"]:
            global_knowledge = True
        knowledge_outcomes.update(row["outcome_refs"])
    affected = set()
    for nudge in previous_plan["nudges"]:
        relevant, context_items, declared_sources, _ = nudge_context(previous_intent, nudge)
        constraint_changed = any(not row["outcome_refs"] or set(row["outcome_refs"]) & relevant
                                 for row in changed_constraints)
        if (global_change or global_knowledge or constraint_changed or
                context_items & changed_items or declared_sources & changed_sources or
                relevant & (changed_outcomes | knowledge_outcomes)):
            affected.add(nudge["id"])
    # Dependencies and decomposition ancestry inform reconciliation, not locks.
    while True:
        more = {row["id"] for row in previous_plan["nudges"]
                if set(row["depends_on"]) & affected or row["parent_id"] in affected}
        if more <= affected:
            break
        affected.update(more)
    ids = {row["id"] for row in previous_plan["nudges"]}
    return {"status": "RECONCILIATION_SUGGESTED" if affected else "NO_DECLARED_IMPACT",
            "basis": "DECLARED_DEPENDENCIES_ONLY", "changed_sources": sorted(changed_sources),
            "changed_items": sorted(changed_items), "changed_outcomes": sorted(changed_outcomes),
            "global_context_changed": global_change, "affected_nudges": sorted(affected),
            "unaffected_by_declared_refs": sorted(ids - affected), "plans_modified": False,
            "execution_authorized": False, "semantic_completeness_verified": False,
            "next_action": "Review affected conclusions. Preserve sent instructions and history; use corrections where needed."
                           if affected else "Retain the plan unless semantic review finds an undeclared dependency."}
