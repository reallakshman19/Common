"""Read-only structural and relational validation. This is not a transaction server."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

HERE = Path(__file__).resolve().parent
COLLECTIONS = ("sessions", "tasks", "assignments", "artifacts", "evidence", "assessments", "decisions", "handovers", "history")
IMMUTABLE = ("artifacts", "evidence", "assessments", "decisions", "history")
CURRENT = {"queued", "active", "blocked"}
FORMATS = FormatChecker()


@FORMATS.checks("date-time", raises=(ValueError, TypeError))
def strict_timestamp(value):
    """Require an explicit offset; this profile excludes leap-second timestamps."""
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})", value):
        return False
    return moment(value).utcoffset() is not None


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path):
    def bad_constant(value):
        raise ValueError(f"non-finite JSON number: {value}")
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=_pairs, parse_constant=bad_constant)


def structural(document, schema_name="oracle-state.schema.json"):
    schema = load(HERE / schema_name)
    validator = Draft202012Validator(schema, format_checker=FORMATS)
    return [f"SCHEMA {'.'.join(map(str, e.absolute_path)) or '$'}: {e.message}"
            for e in sorted(validator.iter_errors(document), key=lambda e: str(list(e.absolute_path)))]


def moment(value):
    return datetime.fromisoformat(value.upper().replace("Z", "+00:00"))


def validate(state, previous=None, artifact_root=None):
    errors = structural(state)
    if errors:
        return errors
    maps = {name: {item["id"]: item for item in state[name]} for name in COLLECTIONS}
    def fail(code, message):
        errors.append(f"{code}: {message}")
    def lookup(collection, ident, where):
        found = maps[collection].get(ident)
        if found is None:
            fail("REFERENCE", f"{where}: unknown {collection} id {ident}")
        return found
    all_ids = set()
    for name in COLLECTIONS:
        for item in state[name]:
            if item["id"] in all_ids:
                fail("DUPLICATE_ID", item["id"])
            all_ids.add(item["id"])

    def graph_cycle(nodes, edges, code):
        visiting, visited = set(), set()
        def visit(node):
            if node in visiting:
                fail(code, f"cycle through {node}")
                return
            if node in visited:
                return
            visiting.add(node)
            for nxt in edges(nodes[node]):
                if nxt in nodes:
                    visit(nxt)
            visiting.remove(node)
            visited.add(node)
        for node in nodes:
            visit(node)

    oracle = lookup("sessions", state["control"]["oracle_session_id"], "control")
    if oracle and ("oracle" not in oracle["roles"] or oracle["lifecycle"] != "active"):
        fail("ORACLE_BINDING", "current Oracle must be an active Oracle session")
    active_oracles = [s["id"] for s in state["sessions"] if "oracle" in s["roles"] and s["lifecycle"] == "active"]
    if active_oracles != [state["control"]["oracle_session_id"]]:
        fail("ORACLE_BINDING", "exactly one Oracle session may be active in this project")
    session_keys = set()
    for s in state["sessions"]:
        key = s["agent_id"], s["generation"]
        if key in session_keys:
            fail("SESSION_GENERATION", f"duplicate instance {key}")
        session_keys.add(key)
        for p in s["probes"]:
            if p["basis"] == "observed" and p["result"] != "unknown" and not p["witness"]:
                fail("PROBE_WITNESS", s["id"])

    for task in state["tasks"]:
        criterion_ids = [c["id"] for c in task["criteria"]]
        if len(set(criterion_ids)) != len(criterion_ids):
            fail("CRITERION_ID", task["id"])
        lookup("sessions", task["checkpoint"]["by"], task["id"])
        for dep in task["dependencies"]:
            item = lookup("tasks", dep, task["id"])
            if item and task["state"] in {"in_progress", "submitted", "complete"} and item["state"] != "complete":
                fail("DEPENDENCY_UNMET", f"{task['id']} depends on incomplete {dep}")
        for decision_id in task["decision_ids"]:
            lookup("decisions", decision_id, task["id"])
    graph_cycle(maps["tasks"], lambda t: t["dependencies"], "DEPENDENCY_CYCLE")

    owners, current_assignments, generations = {}, {}, {}
    for a in state["assignments"]:
        task = lookup("tasks", a["task_id"], a["id"])
        session = lookup("sessions", a["session_id"], a["id"])
        issuer = lookup("sessions", a["issued_by"], a["id"])
        if issuer and not set(issuer["roles"]) & {"owner", "oracle", "coordinator"}:
            fail("ISSUER_ROLE", a["id"])
        if a["issued_epoch"] > state["control"]["epoch"]:
            fail("ASSIGNMENT_EPOCH", a["id"])
        if task and (a["task_revision"] > task["revision"] or
                     (a["task_revision"] != task["revision"] and a["status"] in CURRENT)):
            fail("STALE_ASSIGNMENT", a["id"])
        key = (a["task_id"], a["role"])
        generations.setdefault(key, []).append(a["generation"])
        provisional = a["status"] == "queued" and a["replaces_assignment_id"] is not None
        if a["status"] in CURRENT and not provisional:
            if key in current_assignments:
                fail("ASSIGNMENT_CONFLICT", f"{key}: {a['id']} and {current_assignments[key]}")
            current_assignments[key] = a["id"]
        if session and a["status"] == "active":
            if session["lifecycle"] != "active" or a["role"] not in session["roles"]:
                fail("SESSION_ROLE", a["id"])
            if not {"read_inputs", "return_artifact"} <= set(a["required_capabilities"]):
                fail("CAPABILITY_REQUIREMENTS", a["id"])
            for cap in a["required_capabilities"]:
                probes = [p for p in session["probes"] if p["capability"] == cap]
                latest = max(enumerate(probes), key=lambda row: (moment(row[1]["at"]), row[0]))[1] if probes else None
                if not latest or latest["result"] != "yes" or latest["basis"] != "observed" or not latest["witness"]:
                    fail("CAPABILITY_UNCONFIRMED", f"{a['id']}: {cap}")
        if a["status"] in {"active", "returned"} and a["delivery"] != "confirmed":
            fail("DELIVERY_UNCONFIRMED", a["id"])
        if task and task["state"] in {"complete", "cancelled", "deferred"} and a["status"] in CURRENT:
            fail("TASK_ASSIGNMENT_STATE", a["id"])
        if a["status"] in {"active", "blocked"} and a["delivery"] == "confirmed":
            for resource in a["write_resources"]:
                if resource in owners:
                    fail("WRITER_CONFLICT", f"{resource}: {a['id']} and {owners[resource]}")
                owners[resource] = a["id"]
        old_id = a["replaces_assignment_id"]
        if a["generation"] == 1 and old_id is not None:
            fail("ASSIGNMENT_GENERATION", a["id"])
        if a["generation"] > 1:
            old = lookup("assignments", old_id, a["id"])
            if old and ((old["task_id"], old["role"], old["generation"] + 1) != (a["task_id"], a["role"], a["generation"]) or (not provisional and old["status"] not in {"superseded", "cancelled"})):
                fail("ASSIGNMENT_GENERATION", a["id"])
            if old and old["session_id"] != a["session_id"]:
                h = lookup("handovers", a["handover_id"], a["id"])
                if not h or (not provisional and h["status"] != "activated") or h["new_assignment_id"] != a["id"]:
                    fail("HANDOVER_REQUIRED", a["id"])
        elif a["handover_id"] is not None:
            fail("ASSIGNMENT_GENERATION", a["id"])
    for key, values in generations.items():
        if sorted(values) != list(range(1, len(values) + 1)):
            fail("ASSIGNMENT_GENERATION", str(key))

    for artifact in state["artifacts"]:
        task = lookup("tasks", artifact["task_id"], artifact["id"])
        if task and artifact["task_revision"] > task["revision"]:
            fail("ARTIFACT_REVISION", artifact["id"])
        for sid in artifact["produced_by"]:
            lookup("sessions", sid, artifact["id"])
        for parent in artifact["derived_from"]:
            lookup("artifacts", parent, artifact["id"])
        if artifact["assignment_id"]:
            a = lookup("assignments", artifact["assignment_id"], artifact["id"])
            if a and ((a["task_id"], a["task_revision"]) != (artifact["task_id"], artifact["task_revision"]) or a["session_id"] not in artifact["produced_by"]):
                fail("ARTIFACT_BINDING", artifact["id"])
    graph_cycle(maps["artifacts"], lambda a: a["derived_from"], "ARTIFACT_CYCLE")
    def authors(artifact_id, seen=None):
        seen = set() if seen is None else seen
        if artifact_id in seen or artifact_id not in maps["artifacts"]:
            return set()
        seen.add(artifact_id)
        a = maps["artifacts"][artifact_id]
        result = set(a["produced_by"])
        for parent in a["derived_from"]:
            result |= authors(parent, seen)
        return result

    def binding(record, artifact, code):
        if artifact and (record["task_id"], record["task_revision"]) != (artifact["task_id"], artifact["task_revision"]):
            fail(code, record["id"])

    superseded_evidence = set()
    for e in state["evidence"]:
        task = lookup("tasks", e["task_id"], e["id"])
        artifact = lookup("artifacts", e["artifact_id"], e["id"])
        actor = lookup("sessions", e["actor"], e["id"])
        binding(e, artifact, "EVIDENCE_BINDING")
        if task and e["task_revision"] > task["revision"]:
            fail("EVIDENCE_REVISION", e["id"])
        if task and e["task_revision"] == task["revision"] and not set(e["criterion_ids"]) <= {c["id"] for c in task["criteria"]}:
            fail("CRITERION_REFERENCE", e["id"])
        if e["basis"] == "observed" and (e["observed_at"] is None or (e["result"] == "PASS" and not e["witness"])):
            fail("OBSERVATION_WITNESS", e["id"])
        if e["observed_at"] and (moment(e["observed_at"]) > moment(e["recorded_at"]) or (artifact and moment(e["observed_at"]) < moment(artifact["created_at"]))):
            fail("EVIDENCE_TIME", e["id"])
        if moment(e["recorded_at"]) > moment(state["updated_at"]):
            fail("EVIDENCE_TIME", e["id"])
        if e["kind"] == "user_use" and actor and not set(actor["roles"]) & {"owner", "user"}:
            fail("USE_ACTOR", e["id"])
        if e["supersedes"]:
            old = lookup("evidence", e["supersedes"], e["id"])
            if old and any(old[k] != e[k] for k in ("task_id", "task_revision", "artifact_id", "kind", "criterion_ids")):
                fail("EVIDENCE_SUPERSESSION", e["id"])
            if e["supersedes"] in superseded_evidence:
                fail("EVIDENCE_FORK", e["id"])
            if old and moment(old["recorded_at"]) > moment(e["recorded_at"]):
                fail("EVIDENCE_TIME", e["id"])
            superseded_evidence.add(e["supersedes"])
    graph_cycle(maps["evidence"], lambda e: [e["supersedes"]] if e["supersedes"] else [], "EVIDENCE_CYCLE")

    superseded_assessments = {a["supersedes"] for a in state["assessments"] if a["supersedes"]}
    supersession_targets = set()
    heads = {}
    for a in state["assessments"]:
        task = lookup("tasks", a["task_id"], a["id"])
        artifact = lookup("artifacts", a["artifact_id"], a["id"])
        reviewer = lookup("sessions", a["by"], a["id"])
        binding(a, artifact, "ASSESSMENT_BINDING")
        if task and a["task_revision"] > task["revision"]:
            fail("ASSESSMENT_REVISION", a["id"])
        criterion = next((c for c in task["criteria"] if c["id"] == a["criterion_id"]), None) if task and a["task_revision"] == task["revision"] else None
        if task and a["task_revision"] == task["revision"] and not criterion:
            fail("CRITERION_REFERENCE", a["id"])
        key = (a["task_id"], a["task_revision"], a["criterion_id"], a["artifact_id"])
        if a["supersedes"]:
            old = lookup("assessments", a["supersedes"], a["id"])
            if old and (old["task_id"], old["criterion_id"]) != (a["task_id"], a["criterion_id"]):
                fail("ASSESSMENT_SUPERSESSION", a["id"])
            if a["supersedes"] in supersession_targets:
                fail("ASSESSMENT_FORK", a["id"])
            supersession_targets.add(a["supersedes"])
        positive, negative = [], []
        for eid in a["evidence_ids"]:
            e = lookup("evidence", eid, a["id"])
            if not e:
                continue
            if (e["task_id"], e["task_revision"], e["artifact_id"]) != (a["task_id"], a["task_revision"], a["artifact_id"]) or a["criterion_id"] not in e["criterion_ids"]:
                fail("ASSESSMENT_EVIDENCE", a["id"])
                continue
            if moment(e["recorded_at"]) > moment(a["at"]):
                fail("ASSESSMENT_TIME", a["id"])
            if e["basis"] == "observed" and e["witness"]:
                if e["result"] == "PASS":
                    positive.append(e)
                if e["result"] == "FAIL":
                    negative.append(e)
        if a["verdict"] == "supported" and (not positive or negative):
            fail("UNSUPPORTED_VERDICT", a["id"])
        if a["verdict"] == "refuted" and not negative:
            fail("UNSUPPORTED_VERDICT", a["id"])
        current_claim = task and a["task_revision"] == task["revision"] and a["artifact_id"] == task["candidate_artifact_id"] and a["id"] not in superseded_assessments
        if current_claim and a["verdict"] == "supported":
            if any(e["id"] in superseded_evidence for e in positive):
                fail("STALE_EVIDENCE", a["id"])
            contrary = [e for e in state["evidence"] if e["id"] not in superseded_evidence and e["basis"] == "observed" and e["result"] == "FAIL" and a["criterion_id"] in e["criterion_ids"] and (e["task_id"], e["task_revision"], e["artifact_id"]) == (a["task_id"], a["task_revision"], a["artifact_id"])]
            if contrary:
                fail("UNRECONCILED_FAILURE", a["id"])
        if a["verdict"] == "supported" and criterion and criterion["requires_separate_review"]:
            lineage = authors(a["artifact_id"])
            if a["by"] in lineage or not any(e["actor"] not in lineage and e["kind"] != "user_use" for e in positive):
                fail("AUTHOR_REVIEW", a["id"])
            if reviewer and not set(reviewer["roles"]) & {"reviewer", "oracle"}:
                fail("REVIEW_ROLE", a["id"])
        heads.setdefault(key, []).append(a)
    graph_cycle(maps["assessments"], lambda a: [a["supersedes"]] if a["supersedes"] else [], "ASSESSMENT_CYCLE")
    for key, rows in heads.items():
        if sum(a["id"] not in superseded_assessments for a in rows) > 1:
            fail("ASSESSMENT_FORK", str(key))

    superseded_decisions = set()
    for d in state["decisions"]:
        task = lookup("tasks", d["task_id"], d["id"])
        lookup("sessions", d["by"], d["id"])
        if d["status"] == "adopted" and d["kind"] in {"scope", "adopt_return"}:
            roles = maps["sessions"].get(d["by"], {}).get("roles", [])
            if "owner" not in roles and not d["authority"]:
                fail("DECISION_AUTHORITY", d["id"])
        if task and d["task_revision"] > task["revision"]:
            fail("DECISION_REVISION", d["id"])
        if d["artifact_id"]:
            artifact = lookup("artifacts", d["artifact_id"], d["id"])
            binding(d, artifact, "DECISION_BINDING")
        if d["supersedes"]:
            old = lookup("decisions", d["supersedes"], d["id"])
            if old and (old["task_id"], old["kind"]) != (d["task_id"], d["kind"]):
                fail("DECISION_SUPERSESSION", d["id"])
            if d["supersedes"] in superseded_decisions:
                fail("DECISION_FORK", d["id"])
            superseded_decisions.add(d["supersedes"])
    graph_cycle(maps["decisions"], lambda d: [d["supersedes"]] if d["supersedes"] else [], "DECISION_CYCLE")

    for task in state["tasks"]:
        candidate = None
        if task["candidate_artifact_id"]:
            candidate = lookup("artifacts", task["candidate_artifact_id"], task["id"])
            if candidate and (candidate["task_id"], candidate["task_revision"]) != (task["id"], task["revision"]):
                fail("CANDIDATE_BINDING", task["id"])
            origin = maps["assignments"].get(candidate["assignment_id"]) if candidate else None
            if origin and origin["status"] in {"superseded", "cancelled"}:
                adopted = any(d["kind"] == "adopt_return" and d["status"] == "adopted" and d["id"] not in superseded_decisions
                              and (d["task_id"], d["task_revision"], d["artifact_id"]) == (task["id"], task["revision"], candidate["id"])
                              for d in state["decisions"])
                if not adopted:
                    fail("LATE_RETURN", task["id"])
        if task["state"] in {"submitted", "complete"} and not candidate:
            fail("CANDIDATE_REQUIRED", task["id"])
        if task["state"] != "complete":
            continue
        for c in task["criteria"]:
            key = (task["id"], task["revision"], c["id"], task["candidate_artifact_id"])
            valid = [a for a in heads.get(key, []) if a["id"] not in superseded_assessments and a["verdict"] == "supported"]
            if len(valid) != 1:
                fail("INCOMPLETE_CRITERIA", f"{task['id']}: {c['id']}")
        if task["completion_policy"]["require_user_use"]:
            used = any(e["kind"] == "user_use" and e["basis"] == "observed" and e["result"] == "PASS" and e["witness"]
                       and (e["task_id"], e["task_revision"], e["artifact_id"]) == (task["id"], task["revision"], task["candidate_artifact_id"])
                       and e["id"] not in superseded_evidence for e in state["evidence"])
            if not used:
                fail("USER_USE_REQUIRED", task["id"])
        if task["completion_policy"]["require_acceptance"]:
            d = lookup("decisions", task["acceptance_decision_id"], task["id"])
            if not d or d["kind"] != "acceptance" or d["status"] != "adopted" or d["id"] in superseded_decisions or (d["task_id"], d["task_revision"], d["artifact_id"]) != (task["id"], task["revision"], task["candidate_artifact_id"]):
                fail("ACCEPTANCE_REQUIRED", task["id"])
            elif "owner" not in maps["sessions"].get(d["by"], {}).get("roles", []) and not d["authority"]:
                fail("ACCEPTANCE_AUTHORITY", task["id"])

    oracle_handovers = []
    for h in state["handovers"]:
        origin = lookup("sessions", h["from_session"], h["id"])
        target = lookup("sessions", h["to_session"], h["id"])
        lookup("sessions", h["checkpoint"]["by"], h["id"])
        if h["from_session"] == h["to_session"]:
            fail("HANDOVER_BINDING", h["id"])
        if h["cutover_at"] and moment(h["cutover_at"]) < moment(h["prepared_at"]):
            fail("HANDOVER_TIME", h["id"])
        if h["status"] == "activated" and h["cutover_at"] is None:
            fail("HANDOVER_TIME", h["id"])
        if h["kind"] == "worker":
            old = lookup("assignments", h["old_assignment_id"], h["id"])
            new = lookup("assignments", h["new_assignment_id"], h["id"])
            if h["from_epoch"] is not None or h["to_epoch"] is not None or h["adopted_assignment_ids"]:
                fail("HANDOVER_BINDING", h["id"])
            if old and new:
                if (old["task_id"], old["session_id"]) != (h["task_id"], h["from_session"]) or (new["task_id"], new["session_id"]) != (h["task_id"], h["to_session"]) or old["role"] != new["role"] or new["replaces_assignment_id"] != old["id"] or new["handover_id"] != h["id"]:
                    fail("HANDOVER_BINDING", h["id"])
                if h["status"] == "activated" and old["status"] not in {"superseded", "cancelled"}:
                    fail("HANDOVER_OLD_ACTIVE", h["id"])
                if h["status"] != "activated" and new["status"] != "queued":
                    fail("HANDOVER_NOT_ACTIVE", h["id"])
        else:
            if any(h[k] is not None for k in ("task_id", "old_assignment_id", "new_assignment_id")) or h["from_epoch"] is None or h["to_epoch"] != h["from_epoch"] + 1:
                fail("HANDOVER_BINDING", h["id"])
            if any(s and "oracle" not in s["roles"] for s in (origin, target)):
                fail("ORACLE_BINDING", h["id"])
            for aid in h["adopted_assignment_ids"]:
                lookup("assignments", aid, h["id"])
            if h["status"] == "activated":
                oracle_handovers.append(h)
    oracle_handovers.sort(key=lambda h: h["from_epoch"] or 0)
    for index, h in enumerate(oracle_handovers):
        if h["from_epoch"] != index + 1 or (index and oracle_handovers[index - 1]["to_session"] != h["from_session"]):
            fail("ORACLE_EPOCH_CHAIN", h["id"])
    if state["control"]["epoch"] != len(oracle_handovers) + 1 or (oracle_handovers and oracle_handovers[-1]["to_session"] != state["control"]["oracle_session_id"]):
        fail("ORACLE_EPOCH_CHAIN", "control does not match the activated handover chain")

    for i, ev in enumerate(state["history"]):
        if ev["seq"] != i + 1 or ev["previous_id"] != (state["history"][i - 1]["id"] if i else None):
            fail("HISTORY_CHAIN", ev["id"])
        lookup("sessions", ev["actor"], ev["id"])
        if moment(ev["at"]) > moment(state["updated_at"]) or (i and moment(ev["at"]) < moment(state["history"][i - 1]["at"])):
            fail("HISTORY_TIME", ev["id"])
    if state["revision"] != len(state["history"]):
        fail("STATE_REVISION", "one publication event is required per state revision")
    command_ids = [e["command_id"] for e in state["history"]]
    if len(command_ids) != len(set(command_ids)):
        fail("COMMAND_REPLAY", "command_id repeated in publication history")

    if artifact_root is not None:
        root = Path(artifact_root).resolve()
        for a in state["artifacts"]:
            try:
                path = (root / a["locator"]).resolve()
                if not path.is_relative_to(root):
                    fail("ARTIFACT_PATH", a["id"])
                elif not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != a["sha256"]:
                    fail("ARTIFACT_HASH", a["id"])
            except (OSError, ValueError):
                fail("ARTIFACT_PATH", a["id"])

    if previous is not None:
        old_errors = validate(previous)
        if old_errors:
            fail("PREVIOUS_INVALID", "; ".join(old_errors[:3]))
        else:
            errors.extend(compare(previous, state))
    return errors


def compare(old, new):
    errors = []
    def fail(code, text):
        errors.append(f"{code}: {text}")
    if old["project"]["id"] != new["project"]["id"]:
        fail("PROJECT_CHANGED", "project identity is stable")
    if new["revision"] != old["revision"] + 1:
        fail("REVISION_CONFLICT", "expected previous revision + 1")
    if moment(new["updated_at"]) < moment(old["updated_at"]):
        fail("TIME_ROLLBACK", "publication time moved backwards")
    for collection in IMMUTABLE:
        if new[collection][:len(old[collection])] != old[collection]:
            fail("HISTORY_REWRITE", collection)
    for collection in ("sessions", "tasks", "assignments", "handovers"):
        fresh = {x["id"]: x for x in new[collection]}
        if not {x["id"] for x in old[collection]} <= set(fresh):
            fail("RECORD_DELETED", collection)
    if errors:
        return errors
    old_assignments = {x["id"]: x for x in old["assignments"]}
    new_assignments = {x["id"]: x for x in new["assignments"]}
    for ident, a in old_assignments.items():
        b = new_assignments[ident]
        if {k: v for k, v in a.items() if k not in {"status", "delivery"}} != {k: v for k, v in b.items() if k not in {"status", "delivery"}}:
            fail("ASSIGNMENT_REWRITE", ident)
        if a["status"] in {"superseded", "cancelled"} and b["status"] != a["status"]:
            fail("ASSIGNMENT_REVIVED", ident)
    new_sessions = {x["id"]: x for x in new["sessions"]}
    for a in old["sessions"]:
        b = new_sessions[a["id"]]
        if any(a[k] != b[k] for k in ("agent_id", "generation", "surface")) or b["probes"][:len(a["probes"])] != a["probes"]:
            fail("SESSION_REWRITE", a["id"])
        if a["lifecycle"] == "retired" and b["lifecycle"] != "retired":
            fail("SESSION_REVIVED", a["id"])
    new_tasks = {x["id"]: x for x in new["tasks"]}
    mutable = {"revision", "state", "candidate_artifact_id", "acceptance_decision_id", "checkpoint", "decision_ids"}
    for a in old["tasks"]:
        b = new_tasks[a["id"]]
        changed = {k: v for k, v in a.items() if k not in mutable} != {k: v for k, v in b.items() if k not in mutable}
        if b["revision"] not in {a["revision"], a["revision"] + 1} or (changed and b["revision"] != a["revision"] + 1):
            fail("TASK_REVISION", a["id"])
        if b["revision"] != a["revision"]:
            if not any(d["kind"] == "scope" and d["status"] == "adopted" and d["task_id"] == b["id"] and d["task_revision"] == b["revision"] and d["id"] in b["decision_ids"] for d in new["decisions"]):
                fail("TASK_CHANGE_DECISION", a["id"])
    if old["project"] != new["project"] and new["project"]["aim_revision"] != old["project"]["aim_revision"] + 1:
        fail("AIM_REVISION", "changed project meaning requires a new aim revision and source")
    old_handovers = {h["id"]: h for h in old["handovers"]}
    for h in new["handovers"]:
        prior = old_handovers.get(h["id"])
        if prior:
            if {k: v for k, v in prior.items() if k not in {"status", "cutover_at"}} != {k: v for k, v in h.items() if k not in {"status", "cutover_at"}} or (prior["status"] == "activated" and prior != h):
                fail("HANDOVER_REWRITE", h["id"])
    if old["control"] != new["control"]:
        h = next((h for h in new["handovers"] if h["kind"] == "oracle" and h["status"] == "activated" and h["from_epoch"] == old["control"]["epoch"] and h["to_epoch"] == new["control"]["epoch"] and h["from_session"] == old["control"]["oracle_session_id"] and h["to_session"] == new["control"]["oracle_session_id"]), None)
        if not h:
            fail("ORACLE_CUTOVER", "control change needs a matching activated handover")
        else:
            continuing = {a["id"] for a in old["assignments"] if a["status"] in CURRENT and new_assignments.get(a["id"], {}).get("status") in CURRENT}
            if not continuing <= set(h["adopted_assignment_ids"]):
                fail("ORACLE_ADOPTION", "continuing assignments must be explicitly adopted")
    return errors


def validate_command(command, previous, state, raw_state):
    errors = structural(command, "oracle-command.schema.json")
    if errors:
        return errors
    def fail(code, message):
        errors.append(f"{code}: {message}")
    if command["project_id"] != previous["project"]["id"] or command["expected_revision"] != previous["revision"]:
        fail("COMMAND_PRECONDITION", "project/revision mismatch")
    if command["expected_oracle_epoch"] != previous["control"]["epoch"]:
        fail("COMMAND_EPOCH", "Oracle epoch mismatch")
    if hashlib.sha256(raw_state).hexdigest() != command["next_state_sha256"]:
        fail("COMMAND_DIGEST", "next-state bytes differ")
    if command["command_id"] in {e["command_id"] for e in previous["history"]}:
        fail("COMMAND_REPLAY", "already published; reconcile the existing receipt")
    actor = next((s for s in previous["sessions"] if s["id"] == command["actor"]), None)
    if not actor or actor["lifecycle"] != "active" or not (set(actor["roles"]) & {"owner", "coordinator"} or command["actor"] == previous["control"]["oracle_session_id"]):
        fail("COMMAND_ACTOR", "actor is not an enrolled active publisher")
    last = state["history"][-1]
    if (last["command_id"], last["actor"]) != (command["command_id"], command["actor"]):
        fail("COMMAND_BINDING", "publication event differs from command")
    activated_before = {h["id"] for h in previous["handovers"] if h["status"] == "activated"}
    activated_now = {h["id"] for h in state["handovers"] if h["status"] == "activated"}
    if (activated_now != activated_before) != (command["operation"] == "activate_handover"):
        fail("COMMAND_OPERATION", "operation does not describe the cutover")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path)
    parser.add_argument("--previous", type=Path)
    parser.add_argument("--command", type=Path)
    parser.add_argument("--artifact-root", type=Path, help="Opt-in: verify every artifact as a local path below this root")
    args = parser.parse_args()
    if args.command and not args.previous:
        parser.error("--command requires --previous")
    try:
        state = load(args.state)
        previous = load(args.previous) if args.previous else None
        errors = validate(state, previous, args.artifact_root)
        if args.command and not errors:
            errors += validate_command(load(args.command), previous, state, args.state.read_bytes())
    except (OSError, ValueError, RecursionError) as exc:
        print(f"INPUT: {exc}", file=sys.stderr)
        return 2
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("VALID: structural and declared-record invariants only; execution, identity and authority require external verification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
