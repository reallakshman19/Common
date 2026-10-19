"""Recorded task fit and exact issued bindings; never model qualification."""
from nd_io import acyclic, digest, indexed, references, require

ROLES = ("owner", "designer", "worker", "specialist", "reviewer", "coordinator", "successor")


def nudge_by_id(plan, ident):
    nudges = indexed(plan["nudges"], "nudge")
    references([ident], nudges, "nudge")
    return nudges[ident]


def validate_team(plan, sources, nudges):
    people = indexed(plan.get("participants", []), "participant")
    for participant in people.values():
        for group in ("capabilities", "tools"):
            for claim in indexed(participant[group], "participant " + group).values():
                references(claim["evidence_refs"], sources, "capability evidence")
                if claim["basis"] == "OBSERVED":
                    require(bool(claim["evidence_refs"]), "observed capability/tool claim needs evidence")
    for nudge in nudges.values():
        assignment = nudge.get("assignment")
        if assignment is None:
            continue
        actor = assignment["participant_id"]
        if actor is not None:
            references([actor], people, "assigned participant")
            require(assignment["role"] in people[actor]["roles"], "participant does not support assigned role")
        if assignment["support"] == "GUIDED":
            require(isinstance(assignment["method"], str) and bool(assignment["method"].strip()),
                    "guided assignment needs a concrete method")
        for field in ("capabilities", "tools"):
            indexed(assignment[field], "required " + field)
        references(assignment["review_of"], nudges, "reviewed nudge")
        require(nudge["id"] not in assignment["review_of"], "a nudge cannot review itself")
    edges = {key: row["depends_on"] + row.get("assignment", {}).get("review_of", [])
             for key, row in nudges.items()}
    for values in edges.values():
        references(values, nudges, "review/execution dependency")
    acyclic(edges, "review/execution dependency")


def capability_fit(plan, nudge_id, participant_id=None):
    nudge = nudge_by_id(plan, nudge_id)
    assignment = nudge.get("assignment")
    people = indexed(plan.get("participants", []), "participant")
    selected = participant_id or (assignment or {}).get("participant_id")
    rows = []
    role_mismatch = False
    if selected is not None:
        references([selected], people, "candidate participant")
    if assignment and selected:
        participant = people[selected]
        role_mismatch = assignment["role"] not in participant["roles"]
        for group in ("capabilities", "tools"):
            claims = indexed(participant[group], group)
            for need in assignment[group]:
                claim = claims.get(need["id"])
                rows.append({"group": group, "id": need["id"], "importance": need["importance"],
                             "status": claim["status"] if claim else "UNKNOWN",
                             "basis": claim["basis"] if claim else "UNKNOWN"})
    essential = [row for row in rows if row["importance"] == "ESSENTIAL"]
    if role_mismatch or any(row["status"] == "UNAVAILABLE" for row in essential):
        status = "MISSING_REQUIREMENTS"
    elif not assignment or not selected or not essential or any(row["status"] != "AVAILABLE" for row in essential):
        status = "NOT_ESTABLISHED"
    elif all(row["basis"] == "OBSERVED" for row in essential):
        status = "RECORDED_FIT"
    elif any(row["basis"] == "UNKNOWN" for row in essential):
        status = "NOT_ESTABLISHED"
    else:
        status = "REPORTED_FIT"
    return {"status": status, "affected_nudge": nudge_id, "participant_id": selected,
            "role_mismatch": role_mismatch, "requirements": rows,
            "qualification_verified": False, "execution_authorized": False,
            "scope": "THIS_ASSIGNMENT_ONLY", "workflow_locked": False}


def task_binding(intent, plan, nudge_id):
    nudge = nudge_by_id(plan, nudge_id)
    return {"intent_id": intent["id"], "intent_revision": intent["revision"],
            "intent_sha256": digest(intent), "plan_id": plan["id"], "plan_revision": plan["revision"],
            "plan_sha256": digest(plan), "nudge_id": nudge_id, "nudge_sha256": digest(nudge),
            "participant_id": nudge.get("assignment", {}).get("participant_id")}


def worker_context(intent, plan, nudge):
    """Per-task participant overrides supplied legacy defaults without rewriting them."""
    assignment = nudge.get("assignment", {})
    people = indexed(plan.get("participants", []), "participant")
    participant = people.get(assignment.get("participant_id"))
    context = dict(intent["worker"])
    if participant:
        for key in ("model", "reasoning_effort", "configuration_basis"):
            context[key] = participant[key]
        context["tools"] = [row["id"] + ": " + row["status"] + "/" + row["basis"] for row in participant["tools"]]
    context["reserved_decisions"] = list(dict.fromkeys(
        intent["worker"]["reserved_decisions"] + assignment.get("reserved_decisions", [])))
    return context
