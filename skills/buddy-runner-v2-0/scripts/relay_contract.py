"""Versioned structural contracts; semantic understanding is assessed by an engineer."""
from copy import deepcopy
import re

PARTS = {"purpose", "deliverable", "inputs", "boundaries", "success",
         "uncertainty", "continuation"}
EFFORTS = {"high", "xhigh", "max", "ultra"}
PHASES = {"1a", "1b", "2", "RECOVERY"}
STATES = {"REPORTED", "VERIFIED", "UNKNOWN", "NOT_RUN"}
DECISIONS = {"KEEP", "IMPROVE", "VERIFY_FIRST", "OWNER_DECISION_REQUIRED"}


def text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(field + " must be nonempty text")
    return value


def texts(value, field):
    if not isinstance(value, list) or not value:
        raise ValueError(field + " must be a nonempty list")
    for item in value:
        text(item, field)
    return value


def profile_status(profile):
    if not isinstance(profile, dict):
        return "UNVERIFIED"
    if not profile.get("model") or profile.get("effort") not in EFFORTS:
        return "UNQUALIFIED"
    if profile.get("assurance") not in {"HOST_OBSERVED", "UI_OBSERVED"} or not profile.get("basis"):
        return "UNVERIFIED"
    if (profile.get("model"), profile.get("effort")) != (
            profile.get("observed_model"), profile.get("observed_effort")):
        return "MISMATCH"
    return "CONFIGURATION_OBSERVED"


def validate_request(case):
    if not isinstance(case, dict):
        raise ValueError("request must be an object")
    result = deepcopy(case)
    if result.get("version") != "buddy-runner/v2":
        raise ValueError("explicit buddy-runner/v2 version required")
    for key in ("id", "actor", "incoming", "owner", "repository", "issue"):
        text(result.get(key), key)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", result["repository"]):
        raise ValueError("invalid repository")
    expected = "https://github.com/" + result["repository"] + "/issues/"
    if not result["issue"].startswith(expected) or not re.fullmatch(
            r"[1-9][0-9]*", result["issue"][len(expected):]):
        raise ValueError("issue must name the exact owning repository")
    if not re.fullmatch(r"[0-9a-f]{40}", result.get("assessed_commit", "")):
        raise ValueError("exact assessed commit required")
    if result.get("mode") == "ONBOARD":
        if result.get("continuation") != "AWAIT_OWNER_TASK":
            raise ValueError("ONBOARD requires AWAIT_OWNER_TASK")
        result["mode"] = "RECOVERY"
    if result.get("mode") not in {"ASSISTED", "RECOVERY"}:
        raise ValueError("unknown takeover mode")
    if result.get("continuation") not in {"CONTINUE_AUTHORIZED_TASK", "AWAIT_OWNER_TASK"}:
        raise ValueError("explicit continuation policy required")
    phase = result.get("phase")
    if phase not in PHASES:
        raise ValueError("unknown phase")
    if result["mode"] == "RECOVERY":
        if phase != "RECOVERY" or result["actor"] != result["incoming"]:
            raise ValueError("recovery belongs to the incoming engineer")
    else:
        outgoing = text(result.get("outgoing"), "outgoing")
        if outgoing == result["incoming"] or phase == "RECOVERY":
            raise ValueError("assisted roles must be distinct")
        expected_actor = result["incoming"] if phase == "1b" else outgoing
        if result["actor"] != expected_actor:
            raise ValueError("phase assigned to a different actor")
    assignment = result.get("assignment")
    if not isinstance(assignment, dict) or set(assignment) != PARTS:
        raise ValueError("assignment must contain exactly the seven parts")
    for key in PARTS:
        if key in {"inputs", "boundaries", "success"}:
            texts(assignment[key], key)
        else:
            text(assignment[key], key)
    if not isinstance(result.get("profile"), dict):
        raise ValueError("explicit runtime profile required")
    return result


def validate_reconstruction(case, record):
    if not isinstance(record, dict):
        raise ValueError("reconstruction must be an object")
    if record.get("takeover_id") != case["id"]:
        raise ValueError("reconstruction takeover identity mismatch")
    for field in ("actor", "phase", "assessed_commit"):
        if record.get(field) != case[field]:
            raise ValueError("reconstruction " + field + " mismatch")
    sections = record.get("sections", [])
    if (not isinstance(sections, list) or len(sections) != 12
            or any(not isinstance(item, dict) for item in sections)
            or [item.get("id") for item in sections] != list(range(1, 13))):
        raise ValueError("twelve sections required in order")
    for section in sections:
        text(section.get("text"), "section text")
        state = section.get("state")
        if state not in STATES:
            raise ValueError("unknown section evidence state")
        if state in {"UNKNOWN", "NOT_RUN"}:
            text(section.get("reason"), "missing evidence reason")
            if section.get("refs"):
                raise ValueError("unknown section cannot claim supporting evidence")
        else:
            texts(section.get("refs"), "section references")
    for field in ("route_challenge", "rationale", "next_action"):
        text(record.get(field), field)
    choices = record.get("choices")
    if not isinstance(choices, list) or not 1 <= len(choices) <= 3:
        raise ValueError("one to three credible ROI choices required")
    ids = set()
    for choice in choices:
        if not isinstance(choice, dict):
            raise ValueError("choice must be an object")
        cid = text(choice.get("id"), "choice id")
        if cid in ids or choice.get("decision") not in DECISIONS:
            raise ValueError("duplicate choice or unknown decision")
        ids.add(cid)
        for field in ("benefit", "route", "risk", "falsifier"):
            text(choice.get(field), field)
        texts(choice.get("evidence"), "choice evidence")
        if choice.get("effort") not in {"XS", "S", "M", "L"}:
            raise ValueError("effort must be XS/S/M/L")
    if record.get("chosen") not in ids:
        raise ValueError("selected choice is missing")
    finding_ids = set()
    findings = record.get("findings", [])
    if not isinstance(findings, list):
        raise ValueError("findings must be a list")
    for finding in findings:
        if not isinstance(finding, dict):
            raise ValueError("finding must be an object")
        fid = text(finding.get("id"), "finding id")
        if fid in finding_ids:
            raise ValueError("duplicate finding")
        finding_ids.add(fid)
        if finding.get("kind") not in {"DRIFT", "DEFECT", "IMPROVEMENT",
                                        "INPUT_GAP", "DECISION_CONFLICT"}:
            raise ValueError("unknown finding kind")
        for field in ("impact", "action"):
            text(finding.get(field), field)
        texts(finding.get("refs"), "finding references")
        if finding.get("introduced") is True:
            text(finding.get("before"), "introduced before evidence")
            text(finding.get("after"), "introduced after evidence")
    return record
