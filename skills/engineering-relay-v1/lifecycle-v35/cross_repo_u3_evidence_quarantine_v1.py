"""R14 WP1/U3 cutover: typed old/new U3 contracts, never evidence migration.

The original evidence envelope and a separately authored current-repo
envelope are each evaluated by the actual U3->U2->U1 validators. This
read-only reconciliation is a PRE-ADMISSION negative guard, not another
DELP projector or a provider/Owner/reviewer/writer decision.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator
from evidence_review_contract_v1 import (
    EvidenceReviewError, validate_evidence_review,
)

SCHEMA_NAME = "relay-v35-cross-repo-u3-evidence-quarantine-v1"
SCHEMA_FILE = Path(__file__).resolve().parents[1] / (
    "schemas/lifecycle-v35/cross-repo-u3-evidence-quarantine-v1.schema.json"
)


class CrossRepoEvidenceError(ValueError):
    """Contradictory source-role binding or forbidden historical promotion."""


def reconcile_u3_cutover(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CrossRepoEvidenceError("MIGRATION_OBJECT_REQUIRED")
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    faults = sorted(
        Draft202012Validator(schema).iter_errors(payload),
        key=lambda e: (tuple(map(str, e.path)), e.message),
    )
    if faults:
        first = faults[0]
        where = ".".join(str(x) for x in first.path) or "$"
        raise CrossRepoEvidenceError("SCHEMA_INVALID:" + where + ":" + first.message)

    migration = payload["migration"]
    origin, target = migration["historical"], migration["current"]
    if origin["repository"] == target["repository"] or (
        origin["repository_id"] == target["repository_id"]
    ):
        raise CrossRepoEvidenceError("REPOSITORY_IDENTITY_NOT_DISTINCT")
    for label, bound in (("HISTORICAL", origin), ("CURRENT", target)):
        if bound["root_issue"] == bound["leaf_issue"]:
            raise CrossRepoEvidenceError(label + "_LEAF_IS_ROOT")

    historical = payload["historical_evidence"]
    current = payload["current_evidence"]
    # Validate the real R14 U3 including U2 history, U1 roles and actual
    # full-checkout V3.2 DELP facts *structure*. U3 never approves its input.
    try:
        old_receipt = validate_evidence_review(historical)
    except (EvidenceReviewError, KeyError, TypeError) as exc:
        raise CrossRepoEvidenceError("HISTORICAL_U3_INVALID:" + str(exc)) from exc
    try:
        new_receipt = validate_evidence_review(current)
    except (EvidenceReviewError, KeyError, TypeError) as exc:
        raise CrossRepoEvidenceError("CURRENT_U3_INVALID:" + str(exc)) from exc

    for label, envelope, bound in (
        ("HISTORICAL", historical, origin), ("CURRENT", current, target),
    ):
        identity = envelope["owner_session"]["identity"]
        programme = identity["programme"]
        candidate = identity["candidate_source"]
        facts = envelope["checkpoint_facts"]
        if (
            programme["repository"] != bound["repository"]
            or programme["root_issue"] != bound["root_issue"]
            or envelope["responsibility"]["issue_number"] != bound["leaf_issue"]
            or candidate["pr_number"] != bound["pr_number"]
            or facts["responsibility"]["issue"] != (
                bound["repository"] + "#" + str(bound["leaf_issue"])
            )
            or facts["material"]["pr"] != (
                bound["repository"] + "#" + str(bound["pr_number"])
            )
        ):
            raise CrossRepoEvidenceError(label + "_SOURCE_ROLE_BINDING_MISMATCH")

    # The new repo must obtain its OWN Owner/session claims: old GitHub Owner
    # mirrors are not a new-repo original Owner instruction or access grant.
    identity = current["owner_session"]["identity"]
    if identity["owner_source_grade"] != "UNKNOWN":
        raise CrossRepoEvidenceError("HISTORICAL_OWNER_MIRROR_PROMOTED")
    if any(
        event["source_grade"] != "UNKNOWN"
        or event["source_url"] is not None
        or event["content_sha256"] is not None
        for event in current["owner_session"]["owner_events"]
    ):
        raise CrossRepoEvidenceError("HISTORICAL_OWNER_SOURCE_COPIED")
    if current["producer"]["session_id"] == historical["producer"]["session_id"]:
        raise CrossRepoEvidenceError("HISTORICAL_EXECUTOR_SESSION_REUSED")

    # Deliberately conservative INITIAL cutover gate. Independent current-repo
    # evidence may be added only in a later, native-reviewed admission path;
    # old COMPLETE/VERIFIED/CI PASS/claimed reviewer cannot transfer here.
    if current["reviewer_claim"]["state"] != "NOT_SUBMITTED":
        raise CrossRepoEvidenceError("HISTORICAL_REVIEW_PROMOTED")
    for unit in current["checkpoint_facts"]["units"]:
        if (
            unit["state"] == "COMPLETE"
            or unit["result"] not in ("NOT_RUN", "PENDING")
            or unit["evidence_refs"]
        ):
            raise CrossRepoEvidenceError("HISTORICAL_UNIT_EVIDENCE_PROMOTED:" + unit["id"])
    for test in current["test_observations"]:
        if (
            test["result"] not in ("NOT_RUN", "UNKNOWN")
            or test["tested_head_sha"] is not None
            or test["run_url"] is not None
        ):
            raise CrossRepoEvidenceError("HISTORICAL_CI_PROMOTED:" + test["id"])

    for label, receipt in (("HISTORICAL", old_receipt), ("CURRENT", new_receipt)):
        if (
            receipt["reviewer_admission"] != "NOT_QUALIFIED"
            or receipt["owner_authenticity"] != "NOT_AUTHENTICATED"
            or receipt["lease"] != "NOT_PROVEN"
            or receipt["publisher"] != "OFF"
            or receipt["programme_progress"] is not None
        ):
            raise CrossRepoEvidenceError(label + "_U3_FORGED_AUTHORITY")

    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False,
                   separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    return {
        "schema": "relay-v35-cross-repo-u3-evidence-quarantine-result-v1",
        "binding_sha256": "sha256:" + digest,
        "historical_u3_claim_sha256": old_receipt["evidence_claim_sha256"],
        "current_u3_claim_sha256": new_receipt["evidence_claim_sha256"],
        "historical_evidence": "QUARANTINED_NOT_TRANSFERRED",
        "current_evidence": "NEW_REPOSITORY_REVERIFICATION_REQUIRED",
        "source_grade": "CALLER_REFERENCED_UNATTESTED",
        "provider_acquisition": "NOT_EXECUTED",
        "original_owner": "NOT_AUTHENTICATED",
        "independent_reviewer": "NOT_QUALIFIED",
        "delp_evidence_admission": "NOT_ADMITTED",
        "canonical_delp_projection": "NOT_CALCULATED",
        "programme_progress": None,
        "writer_authorization": "NOT_GRANTED",
        "successor_lease": "NOT_PROVEN",
    }
