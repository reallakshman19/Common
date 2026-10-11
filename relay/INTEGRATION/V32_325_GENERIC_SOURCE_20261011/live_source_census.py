"""Live, GET-only GitHub source-custody census for Common #325.

Unlike benchmark_walkthrough.py, this fetches actual GitHub metadata using a
least-privilege read-only token. It deliberately CANNOT authenticate an
original private Owner chat, adopt an Owner graph, admit evidence or grant a
publisher/Agent B. The report contains digests, paths and statuses, never raw
issue/PR body text or secrets.

    GITHUB_TOKEN=<read-only token> python live_source_census.py

Its output's "checks_pass" only means observations are internally consistent.
"owner_source_authenticated" is ALWAYS false until separately granted by a
real external Owner policy; there is no local override or CLI grant.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable

CURRENT_REPO = "reallakshman19/Common"
OLD_REPO = "reallaksh19/Common"
REPO_ID = 1412133785
OLD_REPO_ID = 1207996454
GRAPH_PATH = ".github/v32-evidence-spine/718-proposal-v2.json"
ISSUES = (5, 289, 325)
CANDIDATE_PR = 326
MAX_JSON_BYTES = 1_000_000
SHA40 = re.compile(r"^[a-f0-9]{40}$")


class LiveCensusHold(ValueError):
    """A source integrity or currentness violation, never an Owner verdict."""


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise LiveCensusHold(code)


def _digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


class ReadOnlyGitHub:
    """Fixed-host, strictly GET-only, bounded UTF-8 JSON public API reader."""

    def __init__(self, token: str = ""):
        self._token = token

    def get(self, path: str) -> dict[str, Any]:
        _require(path.startswith("/repos/") and
                 ".." not in path and "://" not in path,
                 "API_PATH_NOT_BOUND")
        headers = {"Accept": "application/vnd.github+json",
                   "User-Agent": "Common-V32-325-ReadOnlySourceCensus",
                   "X-GitHub-Api-Version": "2022-11-28"}
        if self._token:
            headers["Authorization"] = "Bearer " + self._token
        request = urllib.request.Request(
            "https://api.github.com" + path, headers=headers, method="GET")
        with urllib.request.urlopen(request, timeout=12) as response:
            raw = response.read(MAX_JSON_BYTES + 1)
        _require(len(raw) <= MAX_JSON_BYTES, "API_RESPONSE_TOO_LARGE")
        obj = json.loads(raw.decode("utf-8"))
        _require(isinstance(obj, dict), "API_RESPONSE_NOT_OBJECT")
        return obj


def _safe_get(reader: Any, path: str) -> tuple[dict[str, Any] | None, str]:
    try:
        item = reader.get(path)
        return item, "OBSERVED"
    except urllib.error.HTTPError as exc:
        # 403/404 means unavailable to this actor; absence must not be inferred.
        if exc.code in (401, 403, 404):
            return None, "UNAVAILABLE_HTTP_" + str(exc.code)
        return None, "UNAVAILABLE_HTTP_" + str(exc.code)
    except Exception as exc:
        return None, "GET_FAILED_" + type(exc).__name__


def _issue(reader: Any, repo: str, number: int) -> dict[str, Any]:
    obj = reader.get(f"/repos/{repo}/issues/{number}")
    _require(type(obj.get("number")) is int and obj["number"] == number,
             "ISSUE_IDENTITY_INVALID")
    body = obj.get("body")
    _require(body is None or isinstance(body, str), "ISSUE_BODY_INVALID")
    _require(obj.get("state") in ("open", "closed") and
             isinstance(obj.get("html_url"), str), "ISSUE_METADATA_INVALID")
    return {"number": number, "url": obj["html_url"], "state": obj["state"],
            "body_sha256": _digest((body or "").encode("utf-8"))}


def _repo(reader: Any, name: str, expected_id: int) -> dict[str, Any]:
    raw = reader.get(f"/repos/{name}")
    _require(raw.get("full_name") == name and raw.get("id") == expected_id,
             "REPOSITORY_STABLE_IDENTITY_MISMATCH")
    branch = raw.get("default_branch")
    _require(isinstance(branch, str) and branch == "main", "DEFAULT_BRANCH_MISMATCH")
    return {"repository": name, "stable_id": expected_id,
            "default_branch": branch}


def _branch(reader: Any, repo: str, branch: str) -> str:
    raw = reader.get(f"/repos/{repo}/branches/{branch}")
    sha = ((raw.get("commit") or {}).get("sha")
           if isinstance(raw.get("commit"), dict) else None)
    _require(isinstance(sha, str) and SHA40.fullmatch(sha) is not None,
             "BRANCH_SOURCE_SHA_INVALID")
    return sha


def _pr(reader: Any) -> dict[str, Any]:
    raw = reader.get(f"/repos/{CURRENT_REPO}/pulls/{CANDIDATE_PR}")
    head = raw.get("head")
    base = raw.get("base")
    _require(type(raw.get("number")) is int and raw["number"] == CANDIDATE_PR and
             isinstance(head, dict) and isinstance(base, dict),
             "CANDIDATE_PR_IDENTITY_INVALID")
    head_repo = head.get("repo")
    base_repo = base.get("repo")
    _require(isinstance(head_repo, dict) and
             head_repo.get("full_name") == CURRENT_REPO and
             isinstance(base_repo, dict) and
             base_repo.get("full_name") == CURRENT_REPO,
             "CANDIDATE_PR_CROSS_REPOSITORY")
    sha = head.get("sha")
    _require(isinstance(sha, str) and SHA40.fullmatch(sha) is not None,
             "CANDIDATE_PR_SHA_INVALID")
    _require(base.get("ref") == "main", "CANDIDATE_BASE_REF_MISMATCH")
    return {"pr": CANDIDATE_PR, "head_sha": sha, "base_ref": "main",
            "draft": raw.get("draft"), "state": raw.get("state"),
            "url": raw.get("html_url")}


def _graph(reader: Any, revision: str) -> dict[str, Any]:
    _require(SHA40.fullmatch(revision) is not None, "GRAPH_REVISION_NOT_IMMUTABLE")
    quoted = urllib.parse.quote(GRAPH_PATH, safe="/")
    raw = reader.get(f"/repos/{CURRENT_REPO}/contents/{quoted}?ref={revision}")
    _require(raw.get("path") == GRAPH_PATH and raw.get("encoding") == "base64"
             and isinstance(raw.get("content"), str), "GRAPH_SOURCE_CONTENT_INVALID")
    body = base64.b64decode(raw["content"], validate=False)
    _require(0 < len(body) <= MAX_JSON_BYTES and
             raw.get("sha") == _git_blob_sha(body),
             "GRAPH_BLOB_INTEGRITY_MISMATCH")
    graph = json.loads(body.decode("utf-8"))
    programme = graph.get("programme")
    _require(isinstance(programme, dict), "GRAPH_PROGRAMME_INVALID")
    repo = programme.get("repository")
    _require(repo in (OLD_REPO, CURRENT_REPO), "GRAPH_REPOSITORY_UNKNOWN")
    return {"path": GRAPH_PATH, "git_blob_sha": raw["sha"],
            "raw_sha256": _digest(body), "source_commit": revision,
            "graph_programme_repository": repo, "graph_root": programme.get("root"),
            "owner_adopted_current_repo": False}


def census(reader: Any) -> dict[str, Any]:
    """Always return an UNATTESTED source grade. No locally granted authority."""
    new_repo = _repo(reader, CURRENT_REPO, REPO_ID)
    old_repo = _repo(reader, OLD_REPO, OLD_REPO_ID)
    main_a = _branch(reader, CURRENT_REPO, "main")
    roots_a = [_issue(reader, CURRENT_REPO, i) for i in ISSUES]
    historical_a = _issue(reader, OLD_REPO, 787)
    pr_a = _pr(reader)
    graph = _graph(reader, main_a)
    # Double-read actual provider head and issue bodies; one good snapshot does
    # not establish that the source stayed stable during graph inspection.
    main_b = _branch(reader, CURRENT_REPO, "main")
    roots_b = [_issue(reader, CURRENT_REPO, i) for i in ISSUES]
    historical_b = _issue(reader, OLD_REPO, 787)
    pr_b = _pr(reader)
    _require(main_a == main_b and roots_a == roots_b and
             historical_a == historical_b and pr_a == pr_b,
             "LIVE_OBSERVATIONS_MOVED_DURING_READ")
    # Optional GET probes MUST NOT imply no rules, lab absence or authority.
    protection, protection_state = _safe_get(
        reader, f"/repos/{CURRENT_REPO}/branches/main/protection")
    lab, lab_state = _safe_get(reader, "/repos/reallaksh19/relay-v32-e2e-lab")
    _ = protection, lab
    old_repo_graph = graph["graph_programme_repository"] == OLD_REPO
    return {
        "schema": "common-v32-325-live-source-census-v1",
        "capture_kind": "REAL_GITHUB_GET_NOT_OWNER_ADMISSION",
        "provider_observations_stable_twice": True,
        "current_repository": new_repo, "historical_repository": old_repo,
        "current_main_head": main_b, "current_issue_refs": roots_b,
        "historical_owner_issue": historical_b, "candidate_pr": pr_b,
        "known_graph": graph,
        "known_graph_is_historical": old_repo_graph,
        "current_owner_graph_authentication": "NOT_ATTESTED",
        "authentic_private_owner_original": "NOT_ATTESTED",
        "branch_protection_probe": protection_state,
        "original_lab_access_probe": lab_state,
        "effective_required_checks": "UNKNOWN",
        "qualified_independent_reviews": "NOT_EVALUATED",
        "gates": {
            "G1": "HOLD_OWNER_RELEASE_NOT_AUTHENTICATED",
            "G2": "HOLD_ISSUER_REVIEW_POLICY_NOT_AUTHENTICATED",
            "G3": "HOLD_PROTECTED_NATIVE_GRANT_NOT_ATTESTED",
            "G4": "HOLD_NO_LIVE_PUBLISHER_AUTHORIZATION",
            "G5": "HOLD_NO_EXTERNAL_B_CUSTODY",
        },
        "checks_pass": True, "owner_source_authenticated": False,
        "evidence_admitted": False, "production_authorized": False,
        "ready_for_production": False, "writes": 0,
    }


def main() -> int:
    token = os.environ.get("GITHUB_TOKEN", "")
    try:
        result = census(ReadOnlyGitHub(token))
    except Exception as exc:
        # Never leak API bodies, token, original issue prose or source to logs.
        print(json.dumps({"schema": "common-v32-325-live-source-census-v1",
                          "result": "HOLD_LIVE_SOURCE_CENSUS",
                          "error_type": type(exc).__name__,
                          "reason_code": str(exc) if isinstance(exc, LiveCensusHold)
                          else "GET_OR_PROVIDER_UNAVAILABLE",
                          "owner_source_authenticated": False,
                          "ready_for_production": False, "writes": 0},
                         sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
