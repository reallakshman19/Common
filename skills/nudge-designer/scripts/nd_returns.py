"""Strict native-return intake. Evidence and classifications remain supplied claims."""
import hashlib

from nd_contract import intent_index, nudge_context, validate_plan
from nd_io import digest, indexed, references, require, safe_locator
from nd_team import nudge_by_id, task_binding

FIELDS = {"binding", "actor_id", "claimed_status", "native_report", "attempts", "findings",
          "source_observations", "contributors", "unresolved", "next_proposal"}
KINDS = {"OBSERVATION", "DRIFT", "IMPROVEMENT", "NEW_ISSUE", "ASSUMPTION_CONFLICT"}


def object_fields(value, fields, label):
    require(isinstance(value, dict) and set(value) == set(fields), "invalid " + label + " fields")


def text_value(value, label, nullable=False):
    require((nullable and value is None) or isinstance(value, str) and bool(value.strip()), "invalid " + label)


def rows(value, label):
    require(isinstance(value, list), "invalid " + label + " list")
    return value


def strings(value, label):
    rows(value, label)
    for item in value:
        text_value(item, label)
    require(len(value) == len(set(value)), "duplicate " + label)


def receive(intent, plan, report, profiles):
    validate_plan(intent, plan, profiles)
    object_fields(report, FIELDS, "return")
    require(isinstance(report["binding"], dict), "invalid return binding")
    ident = report["binding"].get("nudge_id")
    require(isinstance(ident, str), "invalid nudge binding")
    require(digest(report["binding"]) == digest(task_binding(intent, plan, ident)),
            "return binding differs; use the exact issued intent/plan snapshots for historical evidence")
    nudge = nudge_by_id(plan, ident)
    sources, items, outcomes = intent_index(intent)
    people = indexed(plan.get("participants", []), "participant")
    actor = report["actor_id"]
    text_value(actor, "actor", nullable=True)
    if actor is not None:
        references([actor], people, "return actor")
    assigned = report["binding"]["participant_id"]
    require(assigned is None or actor == assigned, "return actor differs from issued assignment")
    require(report["claimed_status"] in ("COMPLETE", "PARTIAL", "BLOCKED", "NOT_RUN"), "invalid claimed status")
    native = report["native_report"]
    object_fields(native, {"format", "locator", "revision", "content"}, "native report")
    text_value(native["format"], "native format")
    text_value(native["content"], "native content", nullable=True)
    for key in ("locator", "revision"):
        text_value(native[key], "native " + key, nullable=True)
    safe_locator(native["locator"])
    require(native["content"] is not None or native["locator"] is not None,
            "reference-only native report needs a locator")
    attempts = rows(report["attempts"], "attempt")
    require(bool(attempts), "return needs an actual attempt or an explicit NOT_RUN/BLOCKED attempt")
    for attempt in attempts:
        object_fields(attempt, {"id", "action", "state", "observed", "evidence"}, "attempt")
        for key in ("id", "action", "observed"):
            text_value(attempt[key], "attempt " + key)
        require(attempt["state"] in ("EXECUTED", "NOT_RUN", "BLOCKED"), "invalid attempt state")
        strings(attempt["evidence"], "attempt evidence")
        for locator in attempt["evidence"]:
            safe_locator(locator)
    attempt_ids = indexed(attempts, "attempt")
    if report["claimed_status"] == "COMPLETE":
        require(any(row["state"] == "EXECUTED" for row in attempts), "COMPLETE needs a claimed executed action")
    findings = rows(report["findings"], "finding")
    result_findings = []
    referenced = set()
    for finding in findings:
        object_fields(finding, {"kind", "text", "item_refs", "attempt_refs"}, "finding")
        text_value(finding["kind"], "finding kind")
        require(finding["kind"] in KINDS, "invalid declared finding kind")
        text_value(finding["text"], "finding text")
        strings(finding["item_refs"], "finding item")
        strings(finding["attempt_refs"], "finding attempt")
        references(finding["item_refs"], items, "finding item")
        references(finding["attempt_refs"], attempt_ids, "finding attempt")
        if finding["kind"] == "DRIFT":
            require(any(items[key]["kind"] in ("REQUIREMENT", "CONSTRAINT") for key in finding["item_refs"]),
                    "declared drift must name an original requirement or constraint")
        referenced.update(finding["item_refs"])
        result_findings.append({"declared_kind": finding["kind"], "text": finding["text"],
                                "item_refs": list(finding["item_refs"]), "attempt_refs": list(finding["attempt_refs"])})
    observations = rows(report["source_observations"], "source observation")
    observed_ids, discrepancies, unpinned = set(), [], []
    for observation in observations:
        object_fields(observation, {"source_id", "revision"}, "source observation")
        text_value(observation["source_id"], "observed source")
        references([observation["source_id"]], sources, "observed source")
        key = observation["source_id"]
        require(key not in observed_ids, "duplicate observed source")
        observed_ids.add(key)
        text_value(observation["revision"], "observed revision", nullable=True)
        if sources[key]["revision"] is None or observation["revision"] is None:
            unpinned.append(key)
        elif sources[key]["revision"] != observation["revision"]:
            discrepancies.append(key)
    strings(report["contributors"], "contributor")
    references(report["contributors"], people, "contributor")
    strings(report["unresolved"], "unresolved")
    text_value(report["next_proposal"], "next proposal")
    try:
        native_bytes = native["content"].encode("utf-8") if native["content"] is not None else None
    except UnicodeEncodeError:
        require(False, "native content must be UTF-8 encodable")
    relevant, context_items, source_ids, _ = nudge_context(intent, nudge, plan)
    dependent = {ident}
    while True:
        more = {row["id"] for row in plan["nudges"]
                if set(row["depends_on"] + row.get("assignment", {}).get("review_of", [])) & dependent
                or row["parent_id"] in dependent}
        if more <= dependent:
            break
        dependent.update(more)
    independent = [row["id"] for row in plan["nudges"] if row["id"] not in dependent]
    return {"status": "RETURN_RECORDED", "binding": dict(report["binding"]), "actor_id": actor,
            "claimed_status": report["claimed_status"], "native_report": dict(native),
            "native_content_sha256": hashlib.sha256(native_bytes).hexdigest() if native_bytes is not None else None,
            "native_representation": "TEXT_SNAPSHOT" if native_bytes is not None else "REFERENCE_ONLY",
            "attempts": [dict(row, evidence=list(row["evidence"])) for row in attempts], "findings": result_findings,
            "outside_nudge_refs": sorted(referenced - context_items),
            "freshness": "DISCREPANCY_RECORDED" if discrepancies else "DECLARED_OBSERVATIONS_ONLY" if observations else "NOT_ASSESSED",
            "source_discrepancies": discrepancies, "unpinned_observations": unpinned,
            "sources_not_observed": sorted(source_ids - observed_ids),
            "unresolved": list(report["unresolved"]), "next_proposal": report["next_proposal"],
            "independent_candidates": independent, "independence": "NOT_ESTABLISHED",
            "reconcile_questions": ["Which observations support or contradict the current explanation?",
                                    "Is each declared drift, improvement or new issue correctly scoped?",
                                    "What independent work remains useful under existing authority?",
                                    "What integrated outcome evidence is still missing?"],
            "accepted_outcomes": [], "execution_verified": False, "authority_verified": False,
            "evidence_authenticated": False,
            "semantic_classification_verified": False, "scope_expanded": False, "workflow_locked": False,
            "plan_modified": False, "next_action": "Designer reviews evidence and affected conclusions; preserve issued history."}
