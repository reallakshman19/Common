"""Offline structural contract checks. Source meaning and authority stay unverified."""
from pathlib import Path

from jsonschema import Draft202012Validator

from nd_io import acyclic, digest, indexed, load_json, references, require, safe_locator
from nd_profiles import guidance, profile_digest
from nd_team import validate_team

ROOT = Path(__file__).resolve().parents[1]


def schema_check(data, name):
    schema = load_json(ROOT / "schemas" / (name + ".schema.json"))
    errors = sorted(Draft202012Validator(schema).iter_errors(data),
                    key=lambda error: "/".join(map(str, error.absolute_path)))
    if errors:
        first = errors[0]
        location = "/".join(map(str, first.absolute_path)) or "$"
        require(False, name + " schema " + location + ": " + first.message)


def intent_digest(intent):
    return digest(intent)


def intent_index(intent):
    return (indexed(intent["sources"], "source"), indexed(intent["items"], "item"),
            indexed(intent["outcomes"], "outcome"))


def validate_intent(intent):
    schema_check(intent, "intent")
    sources, items, outcomes = intent_index(intent)
    all_ids = [row["id"] for group in (sources, items, outcomes) for row in group.values()]
    require(len(all_ids) == len(set(all_ids)), "duplicate IDs across intent namespaces")
    for source in sources.values():
        safe_locator(source["locator"])
        if source["kind"] == "UNKNOWN":
            require(source["assessment"] == "UNKNOWN", "unknown source cannot imply inspection")
    for item in items.values():
        references(item["source_refs"], sources, "item source")
        references(item["outcome_refs"], outcomes, "item outcome")
        if item["kind"] != "UNKNOWN":
            require(bool(item["source_refs"]), "substantive item needs a source reference")
        if item["kind"] == "UNKNOWN":
            require(item["state"] in ("UNRESOLVED", "SUPERSEDED"), "unknown item needs unresolved state")
        if item["kind"] == "PROPOSAL":
            require(item["state"] in ("PROPOSED", "SUPERSEDED"), "proposal is not an established fact")
    for outcome in outcomes.values():
        references(outcome["item_refs"], items, "outcome item")
        if outcome["parent_id"] is not None:
            references([outcome["parent_id"]], outcomes, "parent outcome")
    acyclic({key: [value["parent_id"]] if value["parent_id"] else []
             for key, value in outcomes.items()}, "outcome hierarchy")
    for row in intent["knowledge"]:
        references(row["outcome_refs"], outcomes, "knowledge outcome")
        references(row["source_refs"], sources, "knowledge source")
    references(intent["scope"]["basis_refs"], sources, "scope source")


def outcome_ancestors(outcomes, ids):
    result = set(ids)
    for ident in ids:
        parent = outcomes[ident]["parent_id"]
        while parent is not None:
            result.add(parent)
            parent = outcomes[parent]["parent_id"]
    return result


def nudge_context(intent, nudge, plan=None):
    """Shared rendered context, so revision checks follow the actual worker input."""
    sources, items, outcomes = intent_index(intent)
    relevant = outcome_ancestors(outcomes, nudge["outcome_refs"])
    context_items = set(nudge["item_refs"]) | set(nudge["boundaries"]["preserve_refs"])
    for ident in relevant:
        context_items.update(outcomes[ident]["item_refs"])
    source_ids = set(nudge["source_refs"]) | set(intent["scope"]["basis_refs"])
    for ident in context_items:
        source_ids.update(items[ident]["source_refs"])
    knowledge = [row for row in intent["knowledge"]
                 if not row["outcome_refs"] or set(row["outcome_refs"]) & relevant]
    for row in knowledge:
        source_ids.update(row["source_refs"])
    actor = nudge.get("assignment", {}).get("participant_id")
    for participant in (plan or {}).get("participants", []):
        if participant["id"] == actor:
            for claim in participant["capabilities"] + participant["tools"]:
                source_ids.update(claim["evidence_refs"])
    return relevant, context_items, source_ids, knowledge


def validate_plan(intent, plan, profiles):
    validate_intent(intent)
    schema_check(plan, "plan")
    require((plan["intent_id"], plan["intent_revision"]) == (intent["id"], intent["revision"]),
            "plan intent identity/revision mismatch")
    require(plan["intent_sha256"] == intent_digest(intent), "plan intent content binding is stale")
    require(plan["profiles_sha256"] == profile_digest(profiles, plan["profile_ids"]),
            "plan profile content binding is stale")
    sources, items, outcomes = intent_index(intent)
    nudges = indexed(plan["nudges"], "nudge")
    validate_team(plan, sources, nudges)
    require(not set(nudges).intersection(set(sources) | set(items) | set(outcomes)), "duplicate nudge/intent ID")
    dependency_edges, parent_edges = {}, {}
    for nudge in nudges.values():
        ident = nudge["id"]
        references(nudge["outcome_refs"], outcomes, "nudge outcome")
        references(nudge["item_refs"], items, "nudge item")
        references(nudge["source_refs"], sources, "nudge source")
        references(nudge["depends_on"], nudges, "nudge dependency")
        references(nudge["profile_ids"], set(plan["profile_ids"]), "nudge profile")
        require(set(nudge["reasoning_moves"]) <= set(guidance(profiles, nudge["profile_ids"], "reasoning_moves")),
                "reasoning operation missing from selected profile")
        require(set(nudge["evidence_methods"]) <= set(guidance(profiles, nudge["profile_ids"], "evidence_methods")),
                "evidence method missing from selected profile")
        dependency_edges[ident] = nudge["depends_on"]
        parent = nudge["parent_id"]
        references([parent] if parent else [], nudges, "parent nudge")
        parent_edges[ident] = [parent] if parent else []
        relevant = outcome_ancestors(outcomes, nudge["outcome_refs"])
        constraints = {key for key, item in items.items() if item["kind"] == "CONSTRAINT"
                       and item["state"] != "SUPERSEDED"
                       and (not item["outcome_refs"] or set(item["outcome_refs"]) & relevant)}
        preserved = nudge["boundaries"]["preserve_refs"]
        references(preserved, items, "preserved item")
        require(constraints <= set(preserved), "applicable constraint omitted by " + ident + ": " +
                ", ".join(sorted(constraints - set(preserved))))
        for branch in nudge["branches"]:
            references(branch["next_ids"], nudges, "branch nudge")
            require(ident not in branch["next_ids"], "branch cannot silently repeat the same nudge")
    acyclic(dependency_edges, "nudge dependency")
    acyclic(parent_edges, "nudge hierarchy")
    coverage = plan["coverage"]
    targets = [row["target_id"] for row in coverage]
    require(len(targets) == len(set(targets)), "duplicate coverage target")
    required = set(outcomes) | {key for key, item in items.items()
                               if item["kind"] in ("REQUIREMENT", "CONSTRAINT", "UNKNOWN")}
    require(required <= set(targets), "coverage omits declared requirements, constraints, unknowns or outcomes")
    for row in coverage:
        references([row["target_id"]], set(items) | set(outcomes), "coverage target")
        references(row["nudge_ids"], nudges, "coverage nudge")
        references(row["evidence_refs"], sources, "coverage evidence")
        for ident in row["nudge_ids"]:
            relevant, context_items, _, _ = nudge_context(intent, nudges[ident], plan)
            require(row["target_id"] in relevant | context_items,
                    "coverage nudge " + ident + " does not reference target " + row["target_id"])
        if row["disposition"] == "PLANNED":
            require(bool(row["nudge_ids"]), "planned coverage requires a nudge")
        if row["disposition"] == "EVIDENCE_REPORTED":
            require(bool(row["evidence_refs"]), "reported evidence coverage needs a source")
    return {"status": "STRUCTURALLY_VALID", "semantic_quality": "NOT_MACHINE_VERIFIED",
            "coverage_basis": "DECLARED_ITEMS_ONLY", "sources_authenticated": False,
            "authority_verified": False, "execution_performed": False,
            "intent_sha256": intent_digest(intent), "nudges": len(nudges),
            "declared_coverage_targets": len(targets)}
