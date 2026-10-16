#!/usr/bin/env python3
"""Independent v3.6 C2 read-only custody: pinned Git blobs and issue actor readback.

Standard library only. NO imports from v3.5/v3.2/v3.1, DELP, BuddyRunner,
Handover Master, C1 draft modules, or a workflow coordinator. No writes.
Byte custody and provider-observed account identity NEVER grant Owner acceptance.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

SCHEMA = "v36.source-custody/v1"
MAX_BLOB_BYTES = 16 * 1024 * 1024  # bounded first pilot, NOT product file-size limit
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
LOGIN = re.compile(r"^[A-Za-z0-9-]{1,39}$")
IDENT = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
ROLES = frozenset(("ORIGINAL_POSITIVE", "ORIGINAL_NEGATIVE",
                   "COMPLETE_GOLDEN", "PARTIAL_GOLDEN",
                   "BENCHMARK_INPUT", "DEMONSTRATION_ONLY"))


class InvalidManifest(ValueError):
    pass


class ProviderFailure(RuntimeError):
    def __init__(self, status):
        super().__init__(status)
        self.status = status


def need(ok, message):
    if not ok:
        raise InvalidManifest(message)


def git_blob_sha1(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") +
                        b"\0" + data).hexdigest()


def valid_path(value):
    need(isinstance(value, str) and 0 < len(value) <= 500,
         "INVALID_ARTIFACT_PATH")
    need(not value.startswith("/") and "\\" not in value and
         all(part not in ("", ".", "..") for part in value.split("/")) and
         all(ord(char) >= 32 and ord(char) != 127 for char in value),
         "UNSAFE_ARTIFACT_PATH")
    return urllib.parse.quote(value, safe="/")


class GitHubReadOnly:
    """Restricted REST GET transport. Test doubles implement get(path)."""

    def __init__(self, token=None, limit=24 * 1024 * 1024):
        self.token = token
        self.limit = limit

    def get(self, path):
        # path is made only from validated repo/SHA/path/number fields
        if not path.startswith("/repos/") or "?" not in path and "/contents/" in path:
            raise ProviderFailure("UNSAFE_PROVIDER_PATH")
        request = urllib.request.Request(
            "https://api.github.com" + path,
            headers={"Accept": "application/vnd.github+json",
                     "User-Agent": "v36-source-custody-readonly",
                     **({"Authorization": "Bearer " + self.token} if self.token else {})},
            method="GET")
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                raw = response.read(self.limit + 1)
                if len(raw) > self.limit:
                    raise ProviderFailure("PROVIDER_RESPONSE_TOO_LARGE")
            obj = json.loads(raw)
            if not isinstance(obj, dict):
                raise ProviderFailure("PROVIDER_SCHEMA_INVALID")
            return obj
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise ProviderFailure("NOT_FOUND_UNVERIFIED") from exc
            if exc.code in (401, 403, 429):
                raise ProviderFailure("PROVIDER_ACCESS_OR_RATE_LIMIT") from exc
            raise ProviderFailure("PROVIDER_HTTP_ERROR") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise ProviderFailure("PROVIDER_UNAVAILABLE_OR_INVALID") from exc


def validate_manifest(data):
    need(isinstance(data, dict) and set(data) ==
         {"schema", "repository", "revision", "artifacts", "issue_records"},
         "MANIFEST_SCHEMA_INVALID")
    need(data["schema"] == SCHEMA, "WRONG_SCHEMA")
    repo, revision = data["repository"], data["revision"]
    need(isinstance(repo, str) and REPO.fullmatch(repo), "REPOSITORY_INVALID")
    need(isinstance(revision, str) and HEX40.fullmatch(revision),
         "REVISION_MUST_BE_PINNED_SHA40")
    arts, records = data["artifacts"], data["issue_records"]
    need(isinstance(arts, list) and isinstance(records, list) and
         (arts or records), "EVIDENCE_SOURCES_MISSING")
    ids = set()
    for item in arts:
        need(isinstance(item, dict) and set(item) ==
             {"id", "role", "path", "expected_blob_sha1",
              "expected_sha256", "expected_size_bytes", "oracle_complete"},
             "ARTIFACT_SCHEMA_INVALID")
        _id = item["id"]
        need(isinstance(_id, str) and IDENT.fullmatch(_id) and _id not in ids,
             "INVALID_OR_DUPLICATE_RECORD_ID")
        ids.add(_id)
        need(item["role"] in ROLES, "ARTIFACT_ROLE_INVALID")
        valid_path(item["path"])
        need(isinstance(item["expected_blob_sha1"], str) and
             HEX40.fullmatch(item["expected_blob_sha1"]),
             "EXPECTED_GIT_BLOB_REQUIRED")
        need(isinstance(item["expected_sha256"], str) and
             HEX64.fullmatch(item["expected_sha256"]),
             "EXPECTED_BYTE_SHA256_REQUIRED")
        size = item["expected_size_bytes"]
        need(type(size) is int and size >= 0, "EXPECTED_SIZE_INVALID")
        need(item["oracle_complete"] in (True, False, None),
             "ORACLE_COMPLETENESS_INVALID")
        if item["role"] == "COMPLETE_GOLDEN":
            need(item["oracle_complete"] is True,
                 "FULL_GOLDEN_REQUIRES_COMPLETE_ORACLE_CLAIM")
        if item["role"] == "PARTIAL_GOLDEN":
            need(item["oracle_complete"] is False,
                 "PARTIAL_GOLDEN_REQUIRES_PARTIAL_ORACLE")
    for item in records:
        need(isinstance(item, dict) and set(item) ==
             {"id", "kind", "issue_number", "comment_id",
              "claimed_actor", "expected_body_sha256", "expected_updated_at"},
             "ISSUE_RECORD_SCHEMA_INVALID")
        _id = item["id"]
        need(isinstance(_id, str) and IDENT.fullmatch(_id) and _id not in ids,
             "INVALID_OR_DUPLICATE_RECORD_ID")
        ids.add(_id)
        need(item["kind"] in ("ISSUE", "ISSUE_COMMENT"), "RECORD_KIND_INVALID")
        need(type(item["issue_number"]) is int and item["issue_number"] > 0,
             "ISSUE_NUMBER_INVALID")
        if item["kind"] == "ISSUE_COMMENT":
            need(type(item["comment_id"]) is int and item["comment_id"] > 0,
                 "COMMENT_ID_REQUIRED")
        else:
            need(item["comment_id"] is None, "ISSUE_MUST_NOT_HAVE_COMMENT_ID")
        actor = item["claimed_actor"]
        need(actor is None or isinstance(actor, str) and LOGIN.fullmatch(actor),
             "CLAIMED_ACTOR_INVALID")
        digest = item["expected_body_sha256"]
        need(digest is None or isinstance(digest, str) and HEX64.fullmatch(digest),
             "BODY_DIGEST_INVALID")
        date = item["expected_updated_at"]
        need(date is None or isinstance(date, str) and
             re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", date),
             "UPDATE_TIMESTAMP_INVALID")
    return data


def attest_blob(client, repo, revision, item):
    out = {"id": item["id"], "role": item["role"],
           "path": item["path"], "revision": revision,
           "oracle_complete_claim": item["oracle_complete"],
           "byte_identity_verified": False,
           "semantic_acceptance": "NOT_ESTABLISHED",
           "owner_acceptance": "NOT_GRANTED"}
    try:
        if item["expected_size_bytes"] > MAX_BLOB_BYTES:
            out["status"] = "SIZE_OUT_OF_C2_PILOT_RANGE_UNVERIFIED"
            return out
        meta = client.get("/repos/" + repo + "/contents/" +
                          valid_path(item["path"]) + "?ref=" + revision)
        if meta.get("type") != "file" or meta.get("sha") != item["expected_blob_sha1"]:
            out["status"] = "CONTRADICTED_PINNED_PATH_OR_BLOB"
            return out
        if meta.get("size") != item["expected_size_bytes"]:
            out["status"] = "CONTRADICTED_DECLARED_SIZE"
            return out
        obj = client.get("/repos/" + repo + "/git/blobs/" +
                         item["expected_blob_sha1"])
        if obj.get("encoding") != "base64" or not isinstance(obj.get("content"), str):
            out["status"] = "BLOB_BYTES_UNAVAILABLE"
            return out
        # Do not decode unbounded base64 even if the provider reports a smaller size.
        raw64 = obj["content"].encode("ascii")
        if len(raw64) > (MAX_BLOB_BYTES * 4 // 3 + 16 * 1024):
            out["status"] = "SIZE_OUT_OF_C2_PILOT_RANGE_UNVERIFIED"
            return out
        raw = base64.b64decode(raw64, validate=False)
        if len(raw) > MAX_BLOB_BYTES:
            out["status"] = "SIZE_OUT_OF_C2_PILOT_RANGE_UNVERIFIED"
            return out
        actual_sha1 = git_blob_sha1(raw)
        actual_sha256 = hashlib.sha256(raw).hexdigest()
        out["observed_size_bytes"] = len(raw)
        out["observed_sha256"] = actual_sha256
        if (actual_sha1 != item["expected_blob_sha1"] or
            obj.get("sha") != actual_sha1 or
            actual_sha256 != item["expected_sha256"] or
            len(raw) != item["expected_size_bytes"]):
            out["status"] = "CONTRADICTED_ACTUAL_BYTES"
            return out
        out["status"] = "BYTE_VERIFIED_ON_PINNED_GIT_REVISION"
        out["byte_identity_verified"] = True
        # Complete oracle is still a claimant assertion, not semantic proof.
        return out
    except (ProviderFailure, UnicodeEncodeError, ValueError, binascii.Error) as exc:
        out["status"] = (exc.status if isinstance(exc, ProviderFailure)
                         else "PROVIDER_BLOB_MALFORMED")
        return out


def attest_issue(client, repo, item):
    out = {"id": item["id"], "kind": item["kind"],
           "issue_number": item["issue_number"],
           "provider_actor_observed": False,
           "owner_authority": "NOT_AUTHENTICATED",
           "owner_acceptance": "NOT_GRANTED"}
    try:
        if item["kind"] == "ISSUE":
            obj = client.get("/repos/" + repo + "/issues/" +
                             str(item["issue_number"]))
            if obj.get("number") != item["issue_number"]:
                out["status"] = "CONTRADICTED_ISSUE_REFERENCE"
                return out
        else:
            obj = client.get("/repos/" + repo + "/issues/comments/" +
                             str(item["comment_id"]))
            expected_issue_url = ("https://api.github.com/repos/" + repo +
                                  "/issues/" + str(item["issue_number"]))
            if obj.get("issue_url") != expected_issue_url:
                out["status"] = "CONTRADICTED_COMMENT_PARENT"
                return out
        actor = obj.get("user")
        if not isinstance(actor, dict) or not isinstance(actor.get("login"), str):
            out["status"] = "PROVIDER_ACTOR_NOT_AVAILABLE"
            return out
        out["provider_actor_observed"] = True
        out["observed_login"] = actor["login"]
        out["claimed_actor_matches"] = (item["claimed_actor"] is not None and
                                        actor["login"].casefold() ==
                                        item["claimed_actor"].casefold())
        out["provider_updated_at"] = obj.get("updated_at")
        body = obj.get("body")
        if not isinstance(body, str):
            out["status"] = "PROVIDER_BODY_NOT_AVAILABLE"
            return out
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
        out["observed_body_sha256"] = digest
        if (item["expected_updated_at"] is not None and
            item["expected_updated_at"] != obj.get("updated_at")):
            out["status"] = "STALE_ISSUE_EDIT"
        elif (item["expected_body_sha256"] is not None and
              item["expected_body_sha256"] != digest):
            out["status"] = "CONTRADICTED_ISSUE_BODY"
        elif item["claimed_actor"] is not None and not out["claimed_actor_matches"]:
            out["status"] = "CONTRADICTED_CLAIMED_ACTOR"
        else:
            out["status"] = "PROVIDER_RECORD_OBSERVED_NOT_OWNER_AUTHENTICATED"
        return out
    except ProviderFailure as exc:
        out["status"] = exc.status
        return out


def audit(manifest, client):
    data = validate_manifest(manifest)
    repo, revision = data["repository"], data["revision"]
    blobs = [attest_blob(client, repo, revision, a) for a in data["artifacts"]]
    issues = [attest_issue(client, repo, r) for r in data["issue_records"]]
    return {
        "schema": "v36.source-custody-audit/v1",
        "repository": repo, "revision": revision,
        "artifacts": blobs, "issue_records": issues,
        "byte_verified": sum(x["byte_identity_verified"] for x in blobs),
        "artifact_count": len(blobs),
        "provider_actors_observed": sum(x["provider_actor_observed"] for x in issues),
        "source_provenance_only": True,
        "semantic_verified": 0, "owner_decisions_authenticated": 0,
        "may_publish": False, "may_count_for_o2": False,
        "may_change_titles_or_labels": False,
        "may_merge_or_release": False,
        "v3_5_v3_2_runtime_dependency": False
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", required=True, type=Path)
    args = p.parse_args(argv)
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = audit(data, GitHubReadOnly(os.environ.get("GITHUB_TOKEN")))
    except (InvalidManifest, OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "C2_MANIFEST_BLOCKED",
                          "reason": str(exc), "may_publish": False}))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
