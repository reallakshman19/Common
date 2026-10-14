#!/usr/bin/env python3
"""Provider-backed GitHub check-run facts, NEVER MCDA rating or Owner approval.

Read-only, bounded GitHub REST GETs; exact assessed commit + trusted App ID,
check-run ID and check name must all match. Unknown/failed/skipped checks are
NOT_VERIFIED. Results cannot cause workflow progression or notifications.
Python 3.10+, standard library only.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

from observe import fingerprint

REQUEST_SCHEMA = "workflow-intelligence.github-check-request/v1"
RESULT_SCHEMA = "workflow-intelligence.github-check-result/v1"
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA = re.compile(r"^[0-9a-f]{40}$")
MAX_CHECKS = 25


def validate(request):
    if not isinstance(request, dict) or request.get("schema") != REQUEST_SCHEMA:
        raise ValueError("Unsupported GitHub check request schema")
    if type(request.get("enabled")) is not bool:
        raise ValueError("enabled must be explicitly boolean")
    scope = request.get("scope")
    if not isinstance(scope, dict) or not isinstance(scope.get("repository"), str):
        raise ValueError("Missing repository scope")
    repository, sha = scope["repository"], scope.get("assessed_sha")
    if not REPO.fullmatch(repository) or not isinstance(sha, str) or not SHA.fullmatch(sha):
        raise ValueError("Invalid repository or exact assessed SHA")
    requested = request.get("checks", [])
    if not isinstance(requested, list) or len(requested) > MAX_CHECKS:
        raise ValueError("Check list invalid or exceeds safe bound")
    if request["enabled"] and not requested:
        raise ValueError("Enabled verification requires at least one check")
    aliases = set()
    run_ids = set()
    for item in requested:
        if not isinstance(item, dict) or set(item) != {
                "alias", "check_run_id", "expected_name", "trusted_app_id"}:
            raise ValueError("Check requires exact alias/ID/name/trusted App ID fields")
        alias, name = item["alias"], item["expected_name"]
        if not isinstance(alias, str) or not alias or alias in aliases or len(alias) > 100:
            raise ValueError("Duplicate/invalid check alias")
        if not isinstance(name, str) or not name.strip() or len(name) > 200:
            raise ValueError("Invalid check name")
        run_id, app_id = item["check_run_id"], item["trusted_app_id"]
        if type(run_id) is not int or run_id < 1 or run_id in run_ids:
            raise ValueError("Invalid/duplicate check-run ID")
        if type(app_id) is not int or app_id < 1:
            raise ValueError("Invalid trusted GitHub App ID")
        aliases.add(alias)
        run_ids.add(run_id)
    return repository, sha, requested


def github_get(repository, check_run_id, token=None):
    # Host fixed; input components syntactically restricted. No generic URL fetch.
    url = f"https://api.github.com/repos/{repository}/check-runs/{check_run_id}"
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28",
               "User-Agent": "workflow-intelligence-check-reader/v1"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise ValueError("Unexpected GitHub API redirect")

    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(urllib.request.Request(url, headers=headers), timeout=20) as response:
        if response.url != url:
            raise ValueError("Unexpected GitHub API response location")
        return json.load(response)


def check_record(data, expected, repository, sha):
    """Validate source fields independently of potentially untrusted display URLs."""
    source = (f"https://api.github.com/repos/{repository}/check-runs/"
              f"{expected['check_run_id']}")
    base = {"alias": expected["alias"], "check_run_id": expected["check_run_id"],
            "source_api_url": source, "verified": False}
    if not isinstance(data, dict):
        return {**base, "status": "NOT_VERIFIED", "reason": "MALFORMED_PROVIDER_RESPONSE"}
    app = data.get("app")
    if (type(data.get("id")) is not int or data["id"] != expected["check_run_id"] or
            not isinstance(data.get("head_sha"), str) or data["head_sha"] != sha or
            data.get("name") != expected["expected_name"] or
            not isinstance(app, dict) or type(app.get("id")) is not int or
            app["id"] != expected["trusted_app_id"]):
        return {**base, "status": "NOT_VERIFIED", "reason": "SOURCE_IDENTITY_MISMATCH"}
    if data.get("status") != "completed" or data.get("conclusion") != "success":
        return {**base, "status": "NOT_VERIFIED", "reason": "NOT_SUCCESSFUL_COMPLETED_CHECK"}
    return {**base, "status": "VERIFIED_CI_CHECK_SUCCESS", "reason": None,
            "verified": True, "check_name": expected["expected_name"],
            "app_id": expected["trusted_app_id"], "assessed_sha": sha}


def verify(request, reader=None):
    repo, sha, checks = validate(request)
    summary = {"schema": RESULT_SCHEMA, "scope": {"repository": repo, "assessed_sha": sha},
               "authority": "EXACT_COMMIT_GITHUB_CI_CHECK_ONLY",
               "eligible_for_mcda_rating": False, "notification_eligible": False}
    if not request["enabled"]:
        return {**summary, "status": "DISABLED", "checks": [], "verification_digest": None}
    if reader is None:
        token = os.getenv("WF_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")
        reader = lambda repository, cid: github_get(repository, cid, token)
    observed = []
    for check in checks:
        try:
            result = reader(repo, check["check_run_id"])
            observed.append(check_record(result, check, repo, sha))
        except (OSError, ValueError, TypeError, urllib.error.HTTPError) as exc:
            # No response body, token, URL query, or credentials in audit output.
            observed.append({"alias": check["alias"], "check_run_id": check["check_run_id"],
                             "source_api_url": f"https://api.github.com/repos/{repo}/check-runs/{check['check_run_id']}",
                             "verified": False, "status": "NOT_VERIFIED",
                             "reason": "PROVIDER_UNAVAILABLE_OR_INVALID"})
    verified = all(x["verified"] for x in observed)
    return {**summary, "status": "CHECKS_VERIFIED" if verified else "NOT_VERIFIED",
            "checks": observed,
            "verification_digest": "sha256:" + fingerprint(
                {"scope": summary["scope"], "checks": observed})}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        source = json.loads(args.request.read_text(encoding="utf-8"))
        result = verify(source)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n",
                               encoding="utf-8")
        print(f"CI source fact status: {result['status']}; MCDA rating verification: NO")
    except (ValueError, OSError, TypeError) as exc:
        parser.exit(2, f"CHECK_VERIFICATION_FAILED: {exc}\n")


if __name__ == "__main__":
    main()
