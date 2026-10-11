"""G2: Current, provider-observed evidence and review readiness (GET-only).

Observed CI checks are NOT the *required* branch-policy check set.
A passed check, skipped check, reviewer comment or self-issued fact is never
accepted task E or a release/adoption authorization. No mutation is possible.

    GITHUB_TOKEN=<read-only token> python live_evidence_census.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
from collections.abc import Mapping
from typing import Any

from live_source_census import (
    CURRENT_REPO, REPO_ID, ReadOnlyGitHub, LiveCensusHold, _require, SHA40,
    _safe_get,
)

PR_NUMBER = 326
MAX_CHECK_RUNS = 100
MAX_REVIEWS = 100
_ALLOWED_STATES = {"completed", "queued", "in_progress", "requested", "waiting", "pending"}


def _parse_pr(raw: Any) -> dict[str, Any]:
    _require(isinstance(raw, Mapping) and raw.get("number") == PR_NUMBER,
             "EVIDENCE_PR_IDENTITY_INVALID")
    head = raw.get("head")
    base = raw.get("base")
    _require(isinstance(head, Mapping) and isinstance(base, Mapping) and
             isinstance(head.get("repo"), Mapping) and
             isinstance(base.get("repo"), Mapping),
             "EVIDENCE_PR_SOURCE_INVALID")
    sha = head.get("sha")
    _require(isinstance(sha, str) and SHA40.fullmatch(sha) is not None,
             "EVIDENCE_PR_HEAD_INVALID")
    _require(head["repo"].get("full_name") == CURRENT_REPO and
             base["repo"].get("full_name") == CURRENT_REPO and
             base.get("ref") == "main", "EVIDENCE_PR_REPOSITORY_MISMATCH")
    _require(raw.get("state") in ("open", "closed") and
             type(raw.get("draft")) is bool and
             type(raw.get("merged")) is bool, "EVIDENCE_PR_STATE_INVALID")
    return {"number": PR_NUMBER, "head_sha": sha,
            "base_ref": "main", "state": raw["state"],
            "draft": raw["draft"], "merged": raw["merged"],
            "url": f"https://github.com/{CURRENT_REPO}/pull/{PR_NUMBER}"}


def _parse_checks(raw: Any, head_sha: str) -> list[dict[str, Any]]:
    _require(isinstance(raw, Mapping) and
             type(raw.get("total_count")) is int and
             0 <= raw["total_count"] <= MAX_CHECK_RUNS and
             isinstance(raw.get("check_runs"), list) and
             len(raw["check_runs"]) == raw["total_count"],
             "EVIDENCE_CHECK_SET_INCOMPLETE_OR_PAGINATED")
    rows = []
    ids = set()
    for ch in raw["check_runs"]:
        _require(isinstance(ch, Mapping) and
                 type(ch.get("id")) is int and ch["id"] > 0 and
                 ch["id"] not in ids and
                 ch.get("head_sha") == head_sha and
                 isinstance(ch.get("name"), str) and
                 bool(ch["name"].strip()) and
                 ch.get("status") in _ALLOWED_STATES,
                 "EVIDENCE_CHECK_IDENTITY_OR_HEAD_MISMATCH")
        ids.add(ch["id"])
        conclusion = ch.get("conclusion")
        if ch["status"] != "completed":
            _require(conclusion is None, "EVIDENCE_PENDING_CHECK_HAS_CONCLUSION")
        elif conclusion is not None:
            _require(conclusion in {
                "success", "failure", "neutral", "cancelled", "skipped",
                "timed_out", "action_required", "stale",
            }, "EVIDENCE_CHECK_CONCLUSION_INVALID")
        app = ch.get("app")
        rows.append({"id": ch["id"], "name": ch["name"],
                     "status": ch["status"], "conclusion": conclusion,
                     "app": app.get("slug") if isinstance(app, Mapping) else None,
                     "url": ch.get("html_url")})
    return sorted(rows, key=lambda x: (x["name"], x["id"]))


def _parse_reviews(raw: Any, head_sha: str) -> list[dict[str, Any]]:
    _require(isinstance(raw, list) and len(raw) <= MAX_REVIEWS,
             "EVIDENCE_REVIEWS_INVALID_OR_PAGINATED")
    result = []
    ids = set()
    for review in raw:
        _require(isinstance(review, Mapping) and
                 type(review.get("id")) is int and
                 review["id"] > 0 and review["id"] not in ids and
                 isinstance(review.get("user"), Mapping) and
                 isinstance(review["user"].get("login"), str) and
                 review.get("state") in {
                    "APPROVED", "CHANGES_REQUESTED", "COMMENTED",
                    "DISMISSED", "PENDING",
                }, "EVIDENCE_REVIEW_IDENTITY_INVALID")
        ids.add(review["id"])
        result.append({
            "id": review["id"], "login": review["user"]["login"],
            "state": review["state"],
            "commit_id": review.get("commit_id"),
            "at_exact_head": review.get("commit_id") == head_sha,
            "submitted_at": review.get("submitted_at"),
        })
    return sorted(result, key=lambda x: x["id"])


def _get_collection(reader: Any, path: str) -> Any:
    getter = getattr(reader, "get_json", None)
    _require(callable(getter), "EVIDENCE_GET_COLLECTION_REQUIRED")
    return getter(path)


def _protection(reader: Any) -> str:
    _, status = _safe_get(reader, f"/repos/{CURRENT_REPO}/branches/main/protection")
    return status


def census(reader: Any) -> dict[str, Any]:
    """Read the real check/review *facts*. Never self-determine required checks."""
    repo = reader.get(f"/repos/{CURRENT_REPO}")
    _require(isinstance(repo, Mapping) and repo.get("full_name") == CURRENT_REPO and
             repo.get("id") == REPO_ID and repo.get("default_branch") == "main",
             "EVIDENCE_REPOSITORY_IDENTITY_INVALID")
    pr1 = _parse_pr(reader.get(f"/repos/{CURRENT_REPO}/pulls/{PR_NUMBER}"))
    sha = pr1["head_sha"]
    check_path = (f"/repos/{CURRENT_REPO}/commits/{sha}/check-runs?per_page=100")
    review_path = f"/repos/{CURRENT_REPO}/pulls/{PR_NUMBER}/reviews?per_page=100"
    checks1 = _parse_checks(reader.get(check_path), sha)
    reviews1 = _parse_reviews(_get_collection(reader, review_path), sha)
    pr2 = _parse_pr(reader.get(f"/repos/{CURRENT_REPO}/pulls/{PR_NUMBER}"))
    checks2 = _parse_checks(reader.get(check_path), sha)
    reviews2 = _parse_reviews(_get_collection(reader, review_path), sha)
    _require(pr1 == pr2 and checks1 == checks2 and reviews1 == reviews2,
             "EVIDENCE_PROVIDER_CHANGED_DURING_READ")
    protection_status = _protection(reader)
    completed = sum(ch["status"] == "completed" for ch in checks2)
    successes = sum(ch["conclusion"] == "success" for ch in checks2)
    skipped = sum(ch["conclusion"] == "skipped" for ch in checks2)
    negative_checks = [ch["name"] for ch in checks2 if
                       ch["conclusion"] in ("failure", "cancelled", "timed_out", "stale",
                                            "action_required")]
    approvals_at_head = [x for x in reviews2 if
                         x["state"] == "APPROVED" and x["at_exact_head"]]
    # Counting approvals cannot establish the actual policy, qualification,
    # independence, prior invalidation, or Owner-approved evidence issuer.
    return {
        "schema": "common-v32-325-live-evidence-census-v1",
        "capture_kind": "REAL_GITHUB_GET_NOT_TRUST_ADMISSION",
        "repository": CURRENT_REPO, "repository_id": REPO_ID,
        "candidate_pr": pr2,
        "check_run_set": {"count": len(checks2), "completed": completed,
                          "success": successes, "skipped": skipped,
                          "negative_names": negative_checks, "runs": checks2},
        "review_set": {"count": len(reviews2),
                       "at_head_approvals_observed": len(approvals_at_head),
                       "reviews": reviews2},
        "branch_protection_probe": protection_status,
        "source_read_stable_twice": True,
        "required_checks_policy": "UNKNOWN_NOT_OBTAINED_FROM_PROTECTION",
        "evidence_policy_version": "NOT_AUTHENTICATED",
        "fact_issuer": "NOT_AUTHENTICATED",
        "reviewer_independence": "NOT_QUALIFIED",
        "positive_evidence_admitted": False,
        "native_E_earned_by_this_census": 0,
        "G2": "HOLD_POLICY_AND_REVIEWER_AUTHORITY",
        "production_authorized": False,
        "ready_for_production": False,
        "writes": 0,
    }


def main() -> int:
    try:
        report = census(ReadOnlyGitHub(os.environ.get("GITHUB_TOKEN", "")))
    except Exception as exc:
        print(json.dumps({
            "schema": "common-v32-325-live-evidence-census-v1",
            "status": "HOLD_PROVIDER_OR_CONSISTENCY",
            "reason_code": str(exc) if isinstance(exc, LiveCensusHold)
                           else "GET_OR_PROVIDER_UNAVAILABLE",
            "error_type": type(exc).__name__,
            "production_authorized": False, "ready_for_production": False,
            "writes": 0,
        }, sort_keys=True))
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
