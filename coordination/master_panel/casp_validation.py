"""Pinned CASP candidate validation input for source-only panel observations.

Adapted without wire-semantic changes from d9180904af5c6a54c4ea42213af68422087e7da7/tools/casp.py.
Schema bytes match that pin. No authority, authentication, adoption or acceptance.
No network, commands, publication, worker or file-writing interface.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION = "1.0.0"
PROTOCOL_REF = "reallakshman19/Common@d9180904af5c6a54c4ea42213af68422087e7da7:coordination/session-protocol"
SCHEMA_SHA256 = {'common.schema.json': '10b20d6ccc4f973cd77593ee875ab1f99e9422e9ae0aab9a54f3b67f4c2667bc', 'message.schema.json': '1c39848c86c6e17ccc93e6ffe691e2e69efdfca60f3ce8e12973985f38d7e65c', 'session.schema.json': '47f66c525f2068bef1aca184518f32a61252c67810f799274d8c0c38f1853448', 'source-observation.schema.json': 'e7d1212ff24bfc3d7b76ad72ece8e614e55ca88a7886df7d01dabbb39c0d518e'}


class ContractError(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise ContractError(reason)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def reject_number(value):
    raise ContractError("floats and non-finite numbers are outside CASP v1")


def loads(text):
    value = json.loads(text, object_pairs_hook=unique_object,
                       parse_float=reject_number, parse_constant=reject_number)
    canonical(value)  # rejects unpaired surrogates and non-wire values
    return value


def load(path):
    return loads(Path(path).read_text(encoding="utf-8"))


def canonical(value):
    def inspect(item):
        if isinstance(item, dict):
            for key, child in item.items():
                require(isinstance(key, str), "object keys must be strings")
                inspect(key)
                inspect(child)
        elif isinstance(item, list):
            for child in item:
                inspect(child)
        elif isinstance(item, str):
            require(not any(0xD800 <= ord(c) <= 0xDFFF for c in item), "lone surrogate")
        else:
            require(item is None or type(item) in (int, bool), "unsupported JSON value")
            if type(item) is int:
                require(abs(item) <= 9007199254740991, "integer exceeds interoperable range")
    inspect(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def timestamp(value):
    require(bool(re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", value)), "UTC time required")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def schema_check(value, filename):
    """Validate only this package's documented JSON Schema subset, not arbitrary schemas."""
    cache = {}
    def read(name):
        require(re.fullmatch(r"[a-z-]+\.schema\.json", name) is not None, "unsafe schema reference")
        if name not in cache:
            require(name in SCHEMA_SHA256, "unregistered schema")
            raw = (ROOT / "casp_schemas" / name).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == SCHEMA_SHA256[name], "pinned schema digest mismatch")
            cache[name] = loads(raw.decode("utf-8"))
        return cache[name]
    def visit(item, schema, name, path):
        if "$ref" in schema:
            file, _, pointer = schema["$ref"].partition("#")
            name = file or name
            node = read(name)
            for part in pointer.strip("/").split("/") if pointer else []:
                node = node[part]
            return visit(item, node, name, path)
        types = schema.get("type")
        actual = ("null" if item is None else "boolean" if type(item) is bool else
                  "integer" if type(item) is int else "string" if isinstance(item, str) else
                  "array" if isinstance(item, list) else "object" if isinstance(item, dict) else "invalid")
        if types:
            require(actual in ([types] if isinstance(types, str) else types), path + ": type")
        if "const" in schema:
            require(item == schema["const"], path + ": const")
        if "enum" in schema:
            require(item in schema["enum"], path + ": enum")
        if isinstance(item, dict):
            require(set(schema.get("required", [])) <= item.keys(), path + ": missing fields")
            props = schema.get("properties", {})
            if schema.get("additionalProperties") is False:
                require(item.keys() <= props.keys(), path + ": unknown fields")
            for key in item.keys() & props.keys():
                visit(item[key], props[key], name, path + "." + key)
        elif isinstance(item, list):
            require(len(item) >= schema.get("minItems", 0), path + ": too few items")
            require(len(item) <= schema.get("maxItems", 100000), path + ": too many items")
            if schema.get("uniqueItems"):
                require(len({canonical(x) for x in item}) == len(item), path + ": duplicate items")
            for child in item:
                visit(child, schema.get("items", {}), name, path + "[]")
        elif isinstance(item, str):
            require(schema.get("minLength", 0) <= len(item) <= schema.get("maxLength", 100000), path + ": length")
            if "pattern" in schema:
                require(re.search(schema["pattern"], item) is not None, path + ": pattern")
            if schema.get("format") == "date-time":
                timestamp(item)
        elif type(item) is int:
            require(schema.get("minimum", -9007199254740991) <= item <= schema.get("maximum", 9007199254740991), path + ": range")
    canonical(value)
    visit(value, read(filename), filename, "$")


def validate_session(session):
    schema_check(session, "session.schema.json")
    keys = []
    for binding in session["bindings"]:
        target = binding["target"]
        require(target["session_id"] == session["session_id"], "session identity mismatch")
        keys.append(target["binding_id"])
        require(binding["mode"] == "IMPLEMENTATION" or not binding["write_paths"], "read-only write paths")
        require(bool(binding["authority_refs"]), "binding requires existing authority reference")
    require(len(keys) == len(set(keys)), "duplicate binding ID")


STATUSES = {"REQUEST": {"REQUESTED"}, "ACK": {"RECEIVED", "BLOCKED", "REJECTED"},
            "PLAN": {"PROPOSED"}, "RESULT": {"REPORTED", "BLOCKED", "FAILED"},
            "REVIEW": {"ACCEPTED", "REJECTED"}, "INVALIDATION": {"INVALIDATED"}}


def validate_message(message, session=None):
    schema_check(message, "message.schema.json")
    require(len(canonical(message)) <= 32768, "envelope exceeds 32 KiB")
    kind = message["kind"]
    require(message["status"] in STATUSES[kind], "kind/status mismatch")
    if kind == "REQUEST":
        require(message["reply_to"] is None and message["request_digest"] is None, "request cannot be a reply")
        require(bool(message["authority_refs"]), "request requires authority reference")
    else:
        require(message["reply_to"] is not None and message["request_digest"] is not None, "reply requires correlation")
    decision = message["payload"]["decision"]
    if kind == "REQUEST" and message["action"] == "DECISION_RESOLVE":
        require(decision is not None, "decision action requires card and outcome")
    else:
        require(decision is None, "decision payload not applicable")
    if message["expires_at"]:
        require(timestamp(message["expires_at"]) > timestamp(message["created_at"]), "expiry precedes creation")
    if session is not None:
        validate_session(session)
        matches = [b for b in session["bindings"] if b["target"] == message["target"]]
        require(len(matches) == 1, "target not exactly registered")
        binding = matches[0]
        require(message["repository"] == binding["repository"], "project repository mismatch")
        require(message["mailbox"] == binding["mailbox"], "mailbox mismatch")
        if kind == "REQUEST":
            require(session["lifecycle"] == "ACTIVE" or message["action"] == "PAUSE_WORK", "session is held/retired")
            require(session["lifecycle"] != "RETIRED", "retired session")
            require(message["expected_revision"] == session["revision"], "stale revision")
            require(message["action"] in binding["allowed_actions"], "action not registered")
        if kind in {"ACK", "PLAN", "RESULT"}:
            require(message["sender_id"] == session["agent_id"], "response sender differs from registered agent")
    return digest(message)


def correlate(request, response):
    validate_message(request)
    validate_message(response)
    require(request["kind"] == "REQUEST" and response["kind"] != "REQUEST", "expected request and response")
    for key in ("request_id", "target", "repository", "mailbox", "expected_revision", "action"):
        require(request[key] == response[key], "response mismatch: " + key)
    require(response["reply_to"] == request["message_id"], "wrong reply_to")
    require(response["request_digest"] == digest(request), "wrong request digest")


def check_history(messages):
    """Audit a supplied snapshot; this is not a durable deduplication/admission store."""
    ids, requests = {}, {}
    for message in messages:
        value = validate_message(message)
        old = ids.setdefault(message["message_id"], value)
        require(old == value, "conflicting message ID")
        if message["kind"] == "REQUEST":
            t = message["target"]
            key = (t["project_id"], t["assignment_id"], message["request_id"])
            require(requests.setdefault(key, value) == value, "conflicting request key")
    return len(ids)


def request_allowed_now(message, now=None):
    """Local expiry check only; real source/authority/hold rechecks remain external."""
    validate_message(message)
    require(message["kind"] == "REQUEST", "expiry check requires request")
    moment = now or datetime.now(timezone.utc)
    require(timestamp(message["created_at"]) <= moment, "request from future")
    if message["expires_at"]:
        require(timestamp(message["expires_at"]) > moment, "request expired")


def extract(text):
    require(len(text.encode("utf-8")) <= 65536, "comment exceeds input limit")
    blocks = re.findall(r"(?m)^```casp\r?\n([\s\S]*?)^```[ \t]*\r?$", text)
    require(len(blocks) == 1, "expected exactly one casp envelope")
    message = loads(blocks[0])
    validate_message(message)
    return message



def inspect_comment(body, source, *, session=None, request=None):
    """Whitelist structural facts; a supplied context is not an admitted registry.

    Exact raw UTF-8 hashing precedes envelope parsing. No normalization, prompt,
    evidence text, private route or declared authority escapes this projection.
    Durable authenticated admission belongs to the separate F07 recorder.
    """
    from .models import SourceKind
    require(source.kind == SourceKind.ISSUE_COMMENT, "comment source required")
    require(isinstance(body, str), "source text required")
    require(hashlib.sha256(body.encode("utf-8")).hexdigest() == source.body_sha256,
            "observed raw-body fingerprint mismatch")
    envelope = extract(body)
    require(envelope["repository"] == {"id": source.repo_id, "name": source.repo_full_name},
            "observed repository mismatch")
    require(envelope["mailbox"]["repository"] == envelope["repository"]
            and envelope["mailbox"]["issue_number"] == source.issue_number
            and envelope["mailbox"]["visibility"] == "PUBLIC", "observed mailbox mismatch")
    require(envelope["target"]["project_id"] == source.project_id, "observed project mismatch")
    validate_message(envelope, session)
    correlation = "NOT_CONFIGURED"
    if request is not None:
        require(session is not None, "request context requires supplied descriptor")
        validate_message(request, session)
        correlate(request, envelope)
        correlation = "MATCHES_SUPPLIED_REQUEST"
    target = envelope["target"]
    return {
        "protocol_ref": PROTOCOL_REF, "schema": "VALID",
        "source_body_sha256": source.body_sha256,
        "canonical_envelope_sha256": digest(envelope),
        "registration": "MATCHES_SUPPLIED_DESCRIPTOR" if session else "NOT_CONFIGURED",
        "request_correlation": correlation,
        "kind": envelope["kind"], "reported_status": envelope["status"],
        "message_id": envelope["message_id"], "request_id": envelope["request_id"],
        "sender_id": envelope["sender_id"], "project_id": target["project_id"],
        "work_id": target["work_id"], "lane_id": target["lane_id"],
        "assignment_id": target["assignment_id"], "run_id": target["run_id"],
        "binding_generation": target["binding_generation"],
        "descriptor_revision": envelope["expected_revision"],
        "candidate_sha": envelope["basis"]["candidate"],
        "authentication": "UNKNOWN", "current_applicability": "UNKNOWN",
        "independent_acceptance": "UNKNOWN", "liveness": "UNKNOWN",
    }
