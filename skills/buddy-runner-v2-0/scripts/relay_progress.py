"""Describe supplied continuation claims; never grant authority or verify execution."""
from copy import deepcopy


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def references(value):
    return isinstance(value, list) and bool(value) and all(map(nonempty, value))


def progress_report(progress=None, *, owner_wait=False, coding_eligible=False):
    result = {"status": "OWNER_WAIT" if owner_wait else "NOT_STARTED",
              "grade": "SUPPLIED_UNVERIFIED", "missing": []}
    if progress is None:
        return result
    if not isinstance(progress, dict):
        raise ValueError("progress must be an object")
    status = progress.get("status", "NOT_STARTED")
    if status not in {"NOT_STARTED", "PLANNED", "EXECUTED", "BLOCKED"}:
        raise ValueError("unknown progress status")
    if status == "NOT_STARTED":
        return result
    activity = progress.get("activity")
    if activity not in {"RECONSTRUCTION", "INVESTIGATION", "CODING"}:
        raise ValueError("progress activity must identify the actual stage")
    result["activity"] = activity
    if activity == "RECONSTRUCTION":
        result["note"] = "Reconstruction/publication is not execution of the selected continuation"
        return result
    if activity == "CODING" and status == "EXECUTED" and not coding_eligible:
        return dict(result, status="CODING_CLAIM_CONFLICT")
    if activity == "CODING" and owner_wait:
        return result
    result["action"] = progress.get("action")
    if status == "PLANNED":
        return dict(result, status="PLANNED" if nonempty(progress.get("action"))
                    else "EXECUTION_UNSUPPORTED")
    required = {"action": nonempty, "evidence": references}
    if status == "EXECUTED":
        required["result"] = nonempty
    else:
        required.update(attempted=lambda v: type(v) is bool,
                        observed_restriction=nonempty, affected_scope=references,
                        next_feasible_action=nonempty)
        if progress.get("attempted") is False:
            required["not_attempted_reason"] = nonempty
    missing = [key for key, valid in required.items() if not valid(progress.get(key))]
    result.update(missing=missing, evidence=deepcopy(progress.get("evidence", [])))
    if missing:
        return dict(result, status="BLOCKER_UNSUPPORTED" if status == "BLOCKED"
                    else "EXECUTION_UNSUPPORTED")
    if status == "EXECUTED":
        return dict(result, status="EXECUTION_REPORTED", result=progress["result"])
    return dict(result, status="BLOCKED_REPORTED", attempted=progress["attempted"],
                observed_restriction=progress["observed_restriction"],
                affected_scope=deepcopy(progress["affected_scope"]),
                next_feasible_action=progress["next_feasible_action"],
                not_attempted_reason=progress.get("not_attempted_reason"))


def carry_forward(known_items, dispositions):
    if (not isinstance(known_items, list) or not all(map(nonempty, known_items))
            or len(known_items) != len(set(known_items))):
        raise ValueError("known_items must contain distinct declared item identifiers")
    if not isinstance(dispositions, dict):
        raise ValueError("dispositions must be an object")
    for key, item in dispositions.items():
        if not nonempty(key) or not isinstance(item, dict):
            raise ValueError("disposition must identify an item")
        if (item.get("decision") not in {"RETAIN", "RESOLVED", "SUPERSEDED", "PARK"}
                or not nonempty(item.get("reason")) or not references(item.get("refs"))):
            raise ValueError("disposition requires a decision, source references and reason")
    return {"declared_count": len(known_items),
            "unaddressed": [key for key in known_items if key not in dispositions],
            "grade": "DECLARED_ITEMS_ONLY_NOT_SEMANTIC_REVIEW"}
