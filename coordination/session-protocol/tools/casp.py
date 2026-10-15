"""CASP 1.0.0 offline contract helper. No network, authentication or dispatch."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.0.0"


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
            cache[name] = load(ROOT / "schemas" / name)
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


def render(message):
    validate_message(message)
    prefix = "FOR LA:" if message["kind"] == "REQUEST" else "LA DONE:"
    return prefix + "\n\n```casp\n" + json.dumps(message, indent=2, ensure_ascii=False) + "\n```\n"


def extract(text):
    require(len(text.encode("utf-8")) <= 65536, "comment exceeds input limit")
    blocks = re.findall(r"(?m)^```casp\r?\n([\s\S]*?)^```[ \t]*\r?$", text)
    require(len(blocks) == 1, "expected exactly one casp envelope")
    message = loads(blocks[0])
    validate_message(message)
    return message


def build_message(args):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    require(args.text_file is not None and args.sender_id is not None, "--text-file and --sender-id required")
    text = Path(args.text_file).read_text(encoding="utf-8")
    if args.command == "make-request":
        session = load(args.path)
        validate_session(session)
        bindings = [b for b in session["bindings"] if b["target"]["binding_id"] == args.binding]
        require(len(bindings) == 1, "--binding must select exactly one registered binding")
        b = bindings[0]
        message = {"protocol_version": VERSION, "message_id": str(uuid.uuid4()), "request_id": str(uuid.uuid4()),
                   "kind": "REQUEST", "sender_id": args.sender_id, "reply_to": None, "request_digest": None,
                   "created_at": now, "expires_at": None, "expected_revision": session["revision"],
                   "target": b["target"], "repository": b["repository"], "mailbox": b["mailbox"],
                   "action": "DIRECTIVE", "status": "REQUESTED", "authority_refs": args.authority_ref or [],
                   "basis": {"candidate": None, "sources": [], "fixtures": [], "profiles": []},
                   "payload": {"text": text, "refs": [], "decision": None}, "evidence": []}
        validate_message(message, session)
    else:
        request = load(args.path)
        validate_message(request)
        require(request["kind"] == "REQUEST", "make-reply input must be REQUEST")
        message = dict(request, message_id=str(uuid.uuid4()), kind=args.kind,
                       sender_id=args.sender_id, reply_to=request["message_id"], request_digest=digest(request),
                       created_at=now, expires_at=None, status=args.status,
                       payload={"text": text, "refs": [], "decision": None}, evidence=[])
        correlate(request, message)
    return message


def demo():
    fixture = load(ROOT / "examples" / "exchange.json")
    sessions = {s["session_id"]: s for s in fixture["sessions"]}
    for session in sessions.values():
        validate_session(session)
    for request, response in fixture["exchanges"]:
        validate_message(request, sessions[request["target"]["session_id"]])
        validate_message(response, sessions[response["target"]["session_id"]])
        correlate(request, response)
    print(json.dumps({"profile": "FICTIONAL_OFFLINE", "sessions": len(sessions),
                      "projects": 2, "exchanges": len(fixture["exchanges"]), "contract": "PASS",
                      "authentication": "NOT_RUN", "live_delivery": "NOT_RUN"}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["demo", "validate-session", "validate-message", "check-request", "validate-source", "digest", "render", "extract", "correlate", "history", "make-request", "make-reply"])
    parser.add_argument("path", nargs="?")
    parser.add_argument("--session")
    parser.add_argument("--request")
    parser.add_argument("--binding")
    parser.add_argument("--text-file")
    parser.add_argument("--sender-id")
    parser.add_argument("--authority-ref", action="append")
    parser.add_argument("--kind", default="RESULT", choices=["ACK", "PLAN", "RESULT", "REVIEW", "INVALIDATION"])
    parser.add_argument("--status", default="REPORTED")
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        if args.command == "demo":
            demo()
            return 0
        require(args.path is not None, "path required")
        if args.command in {"make-request", "make-reply"}:
            require(args.output is not None, "--output required; existing files are never overwritten")
            value = build_message(args)
            with Path(args.output).open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
            print("CREATED_OFFLINE; source authentication/publication NOT_ATTEMPTED")
            return 0
        value = extract(Path(args.path).read_text(encoding="utf-8")) if args.command == "extract" else load(args.path)
        if args.command == "validate-session":
            validate_session(value)
        elif args.command in {"validate-message", "check-request"}:
            require(args.command != "check-request" or args.session is not None, "check-request requires --session")
            validate_message(value, load(args.session) if args.session else None)
            if args.command == "check-request":
                request_allowed_now(value)
        elif args.command == "validate-source":
            schema_check(value, "source-observation.schema.json")
        elif args.command == "correlate":
            require(args.request is not None, "--request required")
            correlate(load(args.request), value)
        elif args.command == "history":
            check_history(value)
        elif args.command in {"render", "extract"}:
            print(render(value) if args.command == "render" else json.dumps(value, indent=2, ensure_ascii=False))
            return 0
        print(digest(value) if args.command == "digest" else "OFFLINE_CONTRACT_VALID; authentication/delivery/acceptance NOT_VERIFIED")
        return 0
    except (ContractError, ValueError, KeyError, OSError) as error:
        print("INVALID: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
