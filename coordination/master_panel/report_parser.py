"""Typed, non-executable GitHub CASP source claim extraction.

The provenance of this *reported claim* is a GitHub source revision, NOT a
registration, coordinator observation, permission grant, accepted evidence,
agent liveness or independent review. No free text or private URL leaves here.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Optional

from .models import SourceIdentity, SourceKind

_FENCE = re.compile(r"```casp[ \t]*\r?\n(.*?)\r?\n```", re.I | re.S)
_PUBLIC_ID = re.compile(r"^[a-zA-Z0-9_.:-]{1,128}$")
_SHA = re.compile(r"^[a-fA-F0-9]{40}$")
_KINDS = {"REQUEST", "ACK", "RESULT", "REVIEW"}
_STATUS = {"REQUESTED", "RECEIVED", "REPORTED"}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate envelope field")
        result[key] = value
    return result


def _utc(value: Any) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        return True
    except ValueError:
        return False


def _id(value: Any) -> Optional[str]:
    if not isinstance(value, str) or not _PUBLIC_ID.fullmatch(value):
        return None
    return value


def extract_report(body: Any, source: SourceIdentity) -> Optional[dict[str, Any]]:
    """Return claim metadata only when envelope scope matches GitHub identity.

    The issue author's comment can *claim* another role; that is never treated
    as independent identity binding. A malformed/ambiguous envelope is not
    promoted to a work/agent assignment.
    """
    if source.kind != SourceKind.ISSUE_COMMENT:
        return None
    if not isinstance(body, str) or len(body.encode("utf-8")) > 65536:
        return None
    matches = _FENCE.findall(body)
    if len(matches) != 1:
        return None
    try:
        envelope = json.loads(matches[0], object_pairs_hook=_unique_object)
    except (TypeError, ValueError):
        return None
    if not isinstance(envelope, dict):
        return None
    target = envelope.get("target")
    mailbox = envelope.get("mailbox")
    repository = envelope.get("repository")
    if not all(isinstance(x, dict) for x in (target, mailbox, repository)):
        return None
    box_repo = mailbox.get("repository")
    if not isinstance(box_repo, dict):
        return None
    if repository.get("name") != source.repo_full_name:
        return None
    if str(repository.get("id")) != source.repo_id:
        return None
    if box_repo.get("name") != source.repo_full_name:
        return None
    if str(box_repo.get("id")) != source.repo_id:
        return None
    if mailbox.get("issue_number") != source.issue_number:
        return None
    kind, status = envelope.get("kind"), envelope.get("status")
    if (envelope.get("protocol_version") != "1.0.0"
            or kind not in _KINDS or status not in _STATUS):
        return None
    if status != {"REQUEST": "REQUESTED", "ACK": "RECEIVED", "RESULT": "REPORTED", "REVIEW": "REPORTED"}[kind]:
        return None
    # Old identity-only source fixtures remain readable as explicitly
    # unqualified claims. Once transport metadata appears, reject incomplete
    # or invalid transport rather than laundering it into a typed claim.
    transport = ("created_at", "request_digest", "reply_to", "expected_revision")
    has_transport = any(key in envelope for key in transport) or "binding_generation" in target
    if has_transport:
        if (not _utc(envelope.get("created_at"))
                or (kind != "REQUEST" and (
                    not isinstance(envelope.get("request_digest"), str)
                    or not re.fullmatch(r"[a-f0-9]{64}", envelope["request_digest"])))
                or (kind == "REQUEST" and envelope.get("request_digest") is not None)
                or type(envelope.get("expected_revision")) is not int
                or envelope["expected_revision"] < 1
                or type(target.get("binding_generation")) is not int
                or target["binding_generation"] < 1
                or (kind != "REQUEST" and not _id(envelope.get("reply_to")))
                or (kind == "REQUEST" and envelope.get("reply_to") is not None)
                or (envelope.get("expires_at") is not None and not _utc(envelope["expires_at"]))):
            return None
    for key in ("project_id", "work_id", "assignment_id",
                "run_id", "lane_id"):
        if not _id(target.get(key)):
            return None
    if target["project_id"] != source.project_id:
        return None
    basis = envelope.get("basis")
    candidate = basis.get("candidate") if isinstance(basis, dict) else None
    if not (isinstance(candidate, str) and _SHA.fullmatch(candidate)):
        candidate = None
    request_id = _id(envelope.get("request_id"))
    message_id = envelope.get("message_id")
    sender_id = _id(envelope.get("sender_id"))
    if not request_id or not sender_id or not isinstance(message_id, str):
        return None
    if len(message_id) > 128 or not re.fullmatch(r"[a-zA-Z0-9-]+", message_id):
        return None

    return {
        "kind": kind, "reported_status": status,
        "request_id": request_id, "message_id": message_id,
        "sender_id": sender_id, "project_id": target["project_id"],
        "work_id": target["work_id"], "assignment_id": target["assignment_id"],
        "run_id": target["run_id"], "lane_id": target["lane_id"],
        "candidate_sha": candidate,
        "transport_status": "MINIMUM_FIELDS_VALID" if has_transport else "UNQUALIFIED_LEGACY",
    }
