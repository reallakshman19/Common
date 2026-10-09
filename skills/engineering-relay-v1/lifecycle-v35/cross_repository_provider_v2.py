"""WP1/U1 provider boundary candidate: native old/new source GET, no authority.

Injected-reader receipt is never native. The fixed urllib wrapper may describe
bounded GitHub source observations only. No Owner, review, TaskEvidence, DELP
projection, custody or writer privileges originate from this module.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import ssl
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import (
    HTTPRedirectHandler, HTTPSHandler, Request, build_opener,
)

from cross_repository_identity_v2 import (
    CrossRepositoryIdentityError, validate_crossrepo_identity_v2,
)

SHA = re.compile(r"^[0-9a-f]{40}$")
ROUTE = re.compile(
    r"^(?:|issues/[1-9][0-9]*|pulls/[1-9][0-9]*|"
    r"commits/[0-9a-f]{40}|git/ref/heads/[A-Za-z0-9._/-]+|"
    r"contents/[A-Za-z0-9._/-]+[?]ref=[0-9a-f]{40})$"
)
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def _deny(code: str) -> None:
    raise ValueError(code)


def _observed(envelope: Mapping[str, Any], read: Callable[[str, str], Mapping[str, Any]]) -> dict[str, Any]:
    old = envelope["historical_origin"]
    new = envelope["current_target"]
    current = envelope["current_identity"]
    roles = current["graph_source"], current["session_source"], current["candidate_source"]
    for r in (old, new):
        reply = read(r["repository"], "")
        if not isinstance(reply, dict) or reply.get("id") != r["repository_id"] or reply.get("full_name") != r["repository"]:
            _deny("REPO_ID_OR_NAME_MISMATCH")
        issue = read(r["repository"], f"issues/{r['number']}")
        if (
            not isinstance(issue, dict) or issue.get("number") != r["number"]
            or issue.get("html_url") != r["url"]
            or issue.get("state") not in ("open", "closed")
            or "pull_request" in issue
        ):
            _deny("ISSUE_PROVIDER_BINDING_MISMATCH")

    s = envelope["source_continuity"]
    for role, ref in ((old, s["historical_commit_sha"]), (new, s["current_commit_sha"])):
        actual = read(role["repository"], f"commits/{ref}")
        if not isinstance(actual, dict) or actual.get("sha") != ref:
            _deny("SOURCE_COMMIT_NOT_VERIFIED")

    for role in roles[:2]:
        if role["state"] == "UNKNOWN":
            continue
        commit = role.get("revision_sha") if role["role"] == "PLAN_GRAPH_REVISION" else role.get("commit_sha")
        data = read(new["repository"], f"commits/{commit}")
        if not isinstance(data, dict) or data.get("sha") != commit:
            _deny("SOURCE_ROLE_COMMIT_NOT_VERIFIED")
        if role["role"] == "PLAN_GRAPH_REVISION":
            doc = read(new["repository"], f"contents/{role['path']}?ref={commit}")
            if not isinstance(doc, dict) or doc.get("type") != "file" or doc.get("encoding") != "base64":
                _deny("GRAPH_FILE_UNVERIFIED")
            try:
                raw = base64.b64decode("".join(doc["content"].split()), validate=True)
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError("GRAPH_FILE_INVALID_ENCODING") from exc
            if len(raw) > 2_000_000 or hashlib.sha256(raw).hexdigest() != role["content_sha256"][7:]:
                _deny("GRAPH_CONTENT_DIGEST_MISMATCH")

    candidate = roles[2]
    observed_head = None
    if candidate["state"] == "REFERENCED":
        def pr_and_branch():
            pr = read(new["repository"], f"pulls/{candidate['pr_number']}")
            if not isinstance(pr, dict) or pr.get("number") != candidate["pr_number"]:
                _deny("CANDIDATE_PR_ID_MISMATCH")
            hd, bs = pr.get("head"), pr.get("base")
            if (
                not isinstance(hd, dict) or not isinstance(bs, dict)
                or hd.get("sha") != candidate["head_sha"]
                or bs.get("sha") != candidate["base_sha"]
                or hd.get("repo", {}).get("full_name") != new["repository"]
                or bs.get("repo", {}).get("full_name") != new["repository"]
            ):
                _deny("CANDIDATE_PR_HEAD_OR_REPO_MISMATCH")
            ref = hd.get("ref")
            if not isinstance(ref, str) or not ref or ".." in ref or not re.fullmatch(r"[A-Za-z0-9._/-]+", ref):
                _deny("UNSAFE_CANDIDATE_BRANCH")
            native = read(new["repository"], f"git/ref/heads/{ref}")
            if not isinstance(native, dict) or native.get("ref") != "refs/heads/" + ref or native.get("object", {}).get("sha") != hd["sha"]:
                _deny("PR_BRANCH_REF_MISMATCH")
            return hd["sha"], ref
        observed_head = pr_and_branch()
        # Second independent material read; a move cannot be silently adopted.
        if pr_and_branch() != observed_head:
            _deny("CONCURRENT_CANDIDATE_MOVE")
    return {
        "schema": "relay-cross-repo-provider-source-observation-v2",
        "source_grade": "CALLER_INJECTED_UNATTESTED",
        "crossrepo_reference_digest": validate_crossrepo_identity_v2(envelope)["cross_repository_identity_sha256"],
        "historical_repository_id": old["repository_id"],
        "current_repository_id": new["repository_id"],
        "current_candidate_head_sha": None if observed_head is None else observed_head[0],
        "candidate_currentness": "UNKNOWN" if observed_head is None else "MATCH_AT_OBSERVATION",
        "owner_authenticated": False,
        "reviewer_qualified": False,
        "evidence_accepted": False,
        "writer_authorized": False,
        "programme_progress": None,
    }


def observe_crossrepo_provider_v2(envelope: Mapping[str, Any], read: Callable[[str, str], Mapping[str, Any]]) -> dict[str, Any]:
    """Read-only, structural/test-injected provider observation; never native-grade."""
    validate_crossrepo_identity_v2(envelope)
    return _observed(envelope, read)


class _RejectRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _deny("NATIVE_REDIRECT_FORBIDDEN")


def _native_get(repo: str, path: str, *, token: str = "") -> dict[str, Any]:
    # The transport itself, not just the caller, must restrict GitHub
    # namespaces. Avoid accidental cross-repository source promotion.
    if (
        repo not in {"reallaksh19/Common", "reallakshman19/Common"}
        or not REPO.fullmatch(repo)
        or not ROUTE.fullmatch(path)
        or ".." in path
    ):
        _deny("PROVIDER_PATH_NOT_ALLOWED")
    url = "https://api.github.com/repos/" + repo + ("/" + path if path else "")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "common-v35-crossrepo-reference-readonly-v2",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    opener = build_opener(_RejectRedirect(), HTTPSHandler(context=ssl.create_default_context()))
    req = Request(url, headers=headers, method="GET")
    try:
        with opener.open(req, timeout=15) as response:
            if response.status != 200 or response.geturl() != url:
                _deny("NATIVE_PROVIDER_RESPONSE_INVALID")
            data = response.read(2_000_001)
    except (HTTPError, URLError, TimeoutError) as exc:
        raise ValueError("NATIVE_PROVIDER_UNAVAILABLE") from exc
    if len(data) > 2_000_000:
        _deny("NATIVE_PROVIDER_BODY_TOO_LARGE")
    try:
        obj = json.loads(data)
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError("NATIVE_PROVIDER_JSON_INVALID") from exc
    if not isinstance(obj, dict):
        _deny("NATIVE_PROVIDER_OBJECT_REQUIRED")
    return obj


def observe_live_crossrepo_provider_v2(envelope: Mapping[str, Any], *, token: str = "") -> dict[str, Any]:
    """Native public GitHub GET only; still never Owner/reviewer/evidence/writer."""
    # Validate and fix the only two allowed GitHub repository slugs first.
    validate_crossrepo_identity_v2(envelope)
    old = envelope["historical_origin"]["repository"]
    new = envelope["current_target"]["repository"]
    # This specific cutover has a DIRECTION. A set-equality check silently
    # lets the old repo impersonate the current execution namespace.
    if (old, new) != ("reallaksh19/Common", "reallakshman19/Common"):
        _deny("UNAPPROVED_REPOSITORY_PAIR")
    observed = _observed(envelope, lambda r, p: _native_get(r, p, token=token))
    return {**observed, "source_grade": "NATIVE_GITHUB_GET_AT_OBSERVATION"}
