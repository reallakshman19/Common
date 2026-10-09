"""WP1/U1 proposal only: versioned historical/current GitHub reference roles.

Reuses unchanged V1 source-role validator. Structural references can NEVER
authenticate GitHub GET, Owner's private original, reviews, CI or a writer lease.
Not admitted as runtime programme policy until WP0 review/Owner decision.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator

from identity_contract_v1 import IdentityContractError, validate_identity

SCHEMA = "relay-lifecycle-cross-repository-identity-v2"
SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "schemas/lifecycle-v35/cross-repository-identity-v2.schema.json"
)


class CrossRepositoryIdentityError(ValueError):
    """Invalid historical/current identity or attempted source escalation."""


def _canonical_url(ref: Mapping[str, Any]) -> str:
    return f"https://github.com/{ref['repository']}/issues/{ref['number']}"


def validate_crossrepo_identity_v2(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CrossRepositoryIdentityError("ENVELOPE_MAPPING_REQUIRED")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    faults = sorted(
        Draft202012Validator(schema).iter_errors(payload),
        key=lambda e: (tuple(str(x) for x in e.path), e.message),
    )
    if faults:
        first = faults[0]
        where = ".".join(str(part) for part in first.path) or "$"
        raise CrossRepositoryIdentityError(f"SCHEMA_INVALID:{where}:{first.message}")

    # Reference-only wrapper must not relax V1's strict, same-current-repo
    # graph/session/candidate role validation.
    try:
        current = validate_identity(payload["current_identity"])
    except IdentityContractError as exc:
        raise CrossRepositoryIdentityError(f"CURRENT_V1_IDENTITY_INVALID:{exc}") from exc

    historical = payload["historical_origin"]
    target = payload["current_target"]
    current_v1 = payload["current_identity"]
    if historical["source_grade"] != "HISTORICAL_SOURCE_REFERENCE":
        raise CrossRepositoryIdentityError("HISTORICAL_SOURCE_GRADE_MISMATCH")
    if target["source_grade"] != "CURRENT_EXECUTION_REFERENCE":
        raise CrossRepositoryIdentityError("TARGET_SOURCE_GRADE_MISMATCH")
    if (
        historical["repository_id"] == target["repository_id"]
        or historical["repository"] == target["repository"]
    ):
        raise CrossRepositoryIdentityError("SEPARATE_REPOSITORY_ID_REQUIRED")
    if historical["url"] != _canonical_url(historical):
        raise CrossRepositoryIdentityError("HISTORICAL_URL_NAMESPACE_MISMATCH")
    if target["url"] != _canonical_url(target):
        raise CrossRepositoryIdentityError("TARGET_URL_NAMESPACE_MISMATCH")
    if (
        current_v1["programme"]["repository"] != target["repository"]
        or current_v1["programme"]["root_issue"] != target["number"]
    ):
        raise CrossRepositoryIdentityError("CURRENT_PROGRAMME_ROOT_NOT_BOUND")

    # Do not inherit historical Owner claims into the new V1 programme.
    # This U1 grade is a *reference*, never actual authenticated Owner intent.
    if current_v1["owner_source_grade"] != "UNKNOWN":
        raise CrossRepositoryIdentityError("HISTORICAL_OWNER_GRADE_PROMOTED")

    origin_sha = payload["source_continuity"]["historical_commit_sha"]
    current_sha = payload["source_continuity"]["current_commit_sha"]
    relation = payload["source_continuity"]["relationship"]
    if relation == "CODE_EQUIVALENT" and origin_sha != current_sha:
        raise CrossRepositoryIdentityError("FALSE_CODE_EQUIVALENCE")
    if relation == "CODE_CHANGED" and origin_sha == current_sha:
        raise CrossRepositoryIdentityError("FALSE_CODE_CHANGE")
    # Equal commit hashes never mean equal source roles or imported GitHub
    # object identity, review state, author, graph approval, or writer rights.
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                           separators=(",", ":"), allow_nan=False)
    digest = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {
        "schema": SCHEMA,
        "cross_repository_identity_sha256": digest,
        "current_v1_identity_sha256": current["identity_sha256"],
        "reference_grade": "CALLER_REFERENCED_UNATTESTED",
        "provider_object_verification": "NOT_EXECUTED",
        "owner_authentication": "NOT_AUTHENTICATED",
        "historical_reviews_and_checks": "NOT_TRANSFERRED",
        "programme_progress": None,
        "accepted_evidence": "NOT_ADJUDICATED",
        "writer_lease": "NOT_GRANTED",
        "merge_authority": "NOT_GRANTED",
    }
