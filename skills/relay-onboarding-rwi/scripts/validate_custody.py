#!/usr/bin/env python3
"""WP1b: read-only normalized source custody and decision receipts; no provider trust upgrade."""
from __future__ import annotations

import hashlib
import json
import re
from urllib.parse import urlsplit

SCHEMA = "onboarding.custody-bundle/v1"
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")
CUSTODY_KEYS = {"schema", "id", "repository", "source_url", "source_revision",
                "path", "role", "claimed_sha256", "verification", "authority", "visibility"}
EXPERIMENT_KEYS = {"schema", "id", "repository", "candidate_sha", "input_ids",
                   "command", "expected", "observed", "status", "oracle_class", "proof_url"}
DECISION_KEYS = {"schema", "id", "repository", "statement", "actor_role",
                 "disposition", "source_url", "supersedes", "visibility"}
CUSTODY_ROLES = {"ORIGINAL_INPUT", "POSITIVE_ORACLE", "NEGATIVE_FIXTURE", "BENCHMARK", "GENERATED_OUTPUT"}
VERIFICATION = {"CLAIMED_ONLY", "UNAVAILABLE"}  # caller input only; no asserted observation
AUTHORITY = {"OWNER_SOURCE", "ISSUE_DECLARATION", "CANDIDATE", "SYNTHETIC"}
VISIBILITY = {"PUBLIC", "PRIVATE", "RESTRICTED"}
STATUS = {"PASS", "FAIL", "NOT_RUN", "NOT_APPLICABLE"}
ORACLES = {"OWNER_SOURCE", "INDEPENDENT_GOLDEN", "SYNTHETIC", "IMPLEMENTATION_COUPLED"}
DECISION_STATUS = {"REPORTED_APPROVED", "PROPOSED", "REJECTED", "UNKNOWN"}


class InvalidReceipt(ValueError):
    pass


def strict_keys(item, keys, context):
    if not isinstance(item, dict) or set(item) != keys:
        raise InvalidReceipt(context + ": missing/extra keys")
    return item


def identity(s, label):
    if not isinstance(s, str) or not s.strip() or len(s) > 120:
        raise InvalidReceipt(label + ": invalid identity")
    return s


def repo_name(s):
    if not isinstance(s, str) or not REPO.fullmatch(s):
        raise InvalidReceipt("invalid source repository")
    return s


def source_url(url, repository):
    if not isinstance(url, str):
        raise InvalidReceipt("missing source URL")
    try:
        parsed = urlsplit(url)
    except ValueError as exc:
        raise InvalidReceipt("malformed source URL") from exc
    parts = parsed.path.strip("/").split("/")
    if (parsed.scheme != "https" or parsed.netloc != "github.com"
            or parsed.query or (parsed.fragment and not re.fullmatch(r"issuecomment-[0-9]+", parsed.fragment))
            or len(parts) < 3 or "/".join(parts[:2]) != repository
            or any(p in ("", ".", "..") for p in parts)):
        raise InvalidReceipt("source URL repository/host/scope mismatch")
    return url


def valid_path(s):
    if (not isinstance(s, str) or not s or s.startswith("/")
            or "\\" in s or "\x00" in s or any(x in ("", ".", "..") for x in s.split("/"))):
        raise InvalidReceipt("invalid or traversal artifact path")
    return s


def validate_custody(item):
    d = strict_keys(item, CUSTODY_KEYS, "custody")
    if d["schema"] != "onboarding.custody/v1":
        raise InvalidReceipt("invalid custody schema")
    identity(d["id"], "custody")
    repo_name(d["repository"])
    source_url(d["source_url"], d["repository"])
    if not isinstance(d["source_revision"], str) or not SHA40.fullmatch(d["source_revision"]):
        raise InvalidReceipt("invalid source revision")
    valid_path(d["path"])
    if d["role"] not in CUSTODY_ROLES or d["verification"] not in VERIFICATION or d["authority"] not in AUTHORITY or d["visibility"] not in VISIBILITY:
        raise InvalidReceipt("unrecognized custody classification")
    claimed = d["claimed_sha256"]
    if claimed is not None and (not isinstance(claimed, str) or not SHA64.fullmatch(claimed)):
        raise InvalidReceipt("invalid claimed hash")
    # Neither a 'verified' status nor a 'mismatch' observation may be supplied
    # as self-authored custody evidence. Only an independent source attestor
    # can subsequently promote a provenance-bearing Git byte result.
    return d


def verify_bytes(custody, data):
    """Optional external byte supply; digest identity ONLY, not Owner/oracle acceptance."""
    if not isinstance(data, bytes):
        raise InvalidReceipt("original bytes required")
    d = validate_custody(custody)
    digest = hashlib.sha256(data).hexdigest()
    comparison = ("UNCLAIMED_BYTES" if d["claimed_sha256"] is None else
                  "SUPPLIED_BYTES_MATCH" if d["claimed_sha256"] == digest else
                  "SUPPLIED_BYTES_MISMATCH")
    return {"schema": "onboarding.supplied-byte-comparison/v1",
            "id": d["id"], "observed_sha256": digest,
            "claimed_sha256": d["claimed_sha256"],
            "comparison": comparison,
            "source_git_blob_verified": False,
            "provider_authenticated": False,
            "semantic_owner_acceptance": False,
            "execution_authorized": False}


def validate_experiment(item, custody_ids):
    d = strict_keys(item, EXPERIMENT_KEYS, "experiment")
    if d["schema"] != "onboarding.experiment/v1":
        raise InvalidReceipt("invalid experiment schema")
    identity(d["id"], "experiment")
    repo_name(d["repository"])
    if not isinstance(d["candidate_sha"], str) or not SHA40.fullmatch(d["candidate_sha"]):
        raise InvalidReceipt("invalid experiment revision")
    if not isinstance(d["input_ids"], list) or any(not isinstance(i, str) or i not in custody_ids for i in d["input_ids"]) or len(set(d["input_ids"])) != len(d["input_ids"]):
        raise InvalidReceipt("experiment references absent or repeated custody")
    identity(d["command"], "command")
    identity(d["expected"], "expected")
    if d["status"] not in STATUS or d["oracle_class"] not in ORACLES:
        raise InvalidReceipt("invalid experiment status/oracle")
    if d["status"] == "NOT_RUN" and (d["observed"] is not None or d["proof_url"] is not None):
        raise InvalidReceipt("NOT_RUN must not claim output or proof")
    if d["status"] in {"PASS", "FAIL"} and (not isinstance(d["observed"], str) or not d["observed"] or not isinstance(d["proof_url"], str)):
        raise InvalidReceipt("executed result requires observed output and concrete proof link")
    if d["proof_url"] is not None:
        source_url(d["proof_url"], d["repository"])
    return d


def validate_decision(item):
    d = strict_keys(item, DECISION_KEYS, "decision")
    if d["schema"] != "onboarding.decision/v1":
        raise InvalidReceipt("invalid decision schema")
    identity(d["id"], "decision")
    repo_name(d["repository"])
    if not isinstance(d["statement"], str) or not d["statement"].strip():
        raise InvalidReceipt("empty decision")
    if d["actor_role"] not in {"OWNER", "ENGINEER", "UNKNOWN"} or d["disposition"] not in DECISION_STATUS or d["visibility"] not in VISIBILITY:
        raise InvalidReceipt("invalid decision classification")
    if d["disposition"] == "REPORTED_APPROVED" and d["actor_role"] != "OWNER":
        raise InvalidReceipt("only reported Owner role can claim approval")
    if d["disposition"] == "UNKNOWN" and d["source_url"] is not None:
        raise InvalidReceipt("unknown decision cannot invent a source")
    if d["source_url"] is not None:
        source_url(d["source_url"], d["repository"])
    if not isinstance(d["supersedes"], list) or any(not isinstance(x, str) or not x for x in d["supersedes"]) or len(d["supersedes"]) != len(set(d["supersedes"])):
        raise InvalidReceipt("invalid supersession identities")
    return d


def digest(obj):
    """Deterministic digest of normalized JSON; byte identity is not factual proof."""
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def validate_bundle(payload):
    d = strict_keys(payload, {"schema", "custody", "experiments", "decisions"}, "bundle")
    if d["schema"] != SCHEMA or any(not isinstance(d[x], list) for x in ("custody", "experiments", "decisions")):
        raise InvalidReceipt("invalid custody bundle")
    artifacts = [validate_custody(x) for x in d["custody"]]
    keys = {(a["repository"], a["id"]) for a in artifacts}
    if len(keys) != len(artifacts):
        raise InvalidReceipt("duplicate custody identities")
    # Prevent cross-repo fixture reuse by composite, rather than global, identity.
    experiments = []
    for e in d["experiments"]:
        ids = {a["id"] for a in artifacts if a["repository"] == e.get("repository")}
        experiments.append(validate_experiment(e, ids))
    decisions = [validate_decision(x) for x in d["decisions"]]
    if len({(x["repository"], x["id"]) for x in decisions}) != len(decisions):
        raise InvalidReceipt("duplicate decision identity")
    # Supersession is a historical pointer, never a rewrite or authority upgrade.
    for x in decisions:
        if x["id"] in x["supersedes"]:
            raise InvalidReceipt("decision cannot supersede itself")
    return {"schema": "onboarding.custody-verdict/v1",
            "status": "LOCAL_VALIDATION_ONLY",
            "digest": "sha256:" + digest(d),
            "custody_count": len(artifacts),
            "experiment_count": len(experiments),
            "decision_count": len(decisions),
            "execution_authorized": False,
            "owner_approval_verified": False}
