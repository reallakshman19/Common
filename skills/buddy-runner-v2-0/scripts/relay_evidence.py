"""Fail-closed API scaffold; never reads a provider."""
import hashlib
import json

def digest(value):
    body = value if isinstance(value, str) else json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()

def collect(case, reader):
    return [{"digest": "", "grade": "UNIMPLEMENTED", "permission_to_write": False}]

def verify_event(case, event, subject, reader):
    return False

