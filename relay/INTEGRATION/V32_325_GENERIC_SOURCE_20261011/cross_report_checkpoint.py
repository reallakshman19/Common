"""B2-N02: bounded G1/G2 current material identity checkpoint, never trust admission.

Composes *existing* source and evidence GET reports; does not calculate DELP,
authenticate original Owner bytes, approve checks/reviews or perform writes.
Two GitHub GET windows are not a globally atomic repository snapshot.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from live_source_census import (
    CURRENT_REPO, REPO_ID, CANDIDATE_PR, SHA40, ReadOnlyGitHub,
    LiveCensusHold, _require, _repo, _pr, _branch, _graph,
)

SCHEMA = "common-v32-325-cross-report-checkpoint-v1"
DIAGNOSTIC_PR = 336
DIAGNOSTIC_BASE = "feature/v32-325-graph-bound-readonly-integration"
MAX_REPORT_BYTES = 1_000_000


def _sha(value: Any, code: str) -> str:
    _require(isinstance(value, str) and SHA40.fullmatch(value) is not None, code)
    return value


def _mapping(value: Any, code: str) -> Mapping[str, Any]:
    _require(isinstance(value, Mapping), code)
    return value


def _bounded_observed_reports(g1: Any, g2: Any) -> tuple[str, str]:
    """Validate *report contract* and selected material, not its authority."""
    s = _mapping(g1, "CHECKPOINT_G1_NOT_OBJECT")
    e = _mapping(g2, "CHECKPOINT_G2_NOT_OBJECT")
    _require(s.get("schema") == "common-v32-325-live-source-census-v1" and
             e.get("schema") == "common-v32-325-live-evidence-census-v1",
             "CHECKPOINT_REPORT_SCHEMA_MISMATCH")
    _require(s.get("capture_kind") == "REAL_GITHUB_GET_NOT_OWNER_ADMISSION" and
             e.get("capture_kind") == "REAL_GITHUB_GET_NOT_TRUST_ADMISSION" and
             s.get("provider_observations_stable_twice") is True and
             e.get("source_read_stable_twice") is True and
             s.get("checks_pass") is True,
             "CHECKPOINT_REPORT_NOT_STABLE")
    repo = _mapping(s.get("current_repository"), "CHECKPOINT_G1_REPO_MISSING")
    _require(repo.get("repository") == CURRENT_REPO and
             type(repo.get("stable_id")) is int and
             repo["stable_id"] == REPO_ID and
             e.get("repository") == CURRENT_REPO and
             type(e.get("repository_id")) is int and
             e["repository_id"] == REPO_ID,
             "CHECKPOINT_REPOSITORY_ID_MISMATCH")
    sp = _mapping(s.get("candidate_pr"), "CHECKPOINT_G1_PR_MISSING")
    ep = _mapping(e.get("candidate_pr"), "CHECKPOINT_G2_PR_MISSING")
    _require(type(sp.get("pr")) is int and sp["pr"] == CANDIDATE_PR and
             type(ep.get("number")) is int and ep["number"] == CANDIDATE_PR and
             sp.get("base_ref") == "main" and ep.get("base_ref") == "main" and
             sp.get("state") == ep.get("state") and
             sp.get("draft") == ep.get("draft"),
             "CHECKPOINT_SELECTED_PR_IDENTITY_MISMATCH")
    sh = _sha(sp.get("head_sha"), "CHECKPOINT_G1_HEAD_INVALID")
    eh = _sha(ep.get("head_sha"), "CHECKPOINT_G2_HEAD_INVALID")
    _require(sh == eh, "CHECKPOINT_G1_G2_HEAD_MISMATCH")
    main = _sha(s.get("current_main_head"), "CHECKPOINT_MAIN_SHA_INVALID")
    graph = _mapping(s.get("known_graph"), "CHECKPOINT_GRAPH_RECEIPT_MISSING")
    _require(graph.get("source_commit") == main and
             isinstance(graph.get("raw_sha256"), str) and
             graph["raw_sha256"].startswith("sha256:") and
             len(graph["raw_sha256"]) == 71 and
             isinstance(graph.get("git_blob_sha"), str) and
             SHA40.fullmatch(graph["git_blob_sha"]) is not None,
             "CHECKPOINT_GRAPH_RECEIPT_INVALID")
    checks = _mapping(e.get("check_run_set"), "CHECKPOINT_CHECK_SET_MISSING")
    reviews = _mapping(e.get("review_set"), "CHECKPOINT_REVIEW_SET_MISSING")
    runs = checks.get("runs")
    rows = reviews.get("reviews")
    _require(isinstance(runs, list) and type(checks.get("count")) is int and
             0 <= checks["count"] <= 100 and checks["count"] == len(runs) and
             isinstance(rows, list) and type(reviews.get("count")) is int and
             0 <= reviews["count"] <= 100 and reviews["count"] == len(rows),
             "CHECKPOINT_EVIDENCE_REPORT_PARTIAL")
    _require(s.get("owner_source_authenticated") is False and
             s.get("evidence_admitted") is False and
             s.get("production_authorized") is False and
             e.get("positive_evidence_admitted") is False and
             e.get("production_authorized") is False and
             e.get("native_E_earned_by_this_census") == 0 and
             s.get("writes") == 0 and e.get("writes") == 0 and
             e.get("required_checks_policy") ==
             "UNKNOWN_NOT_OBTAINED_FROM_PROTECTION" and
             e.get("reviewer_independence") == "NOT_QUALIFIED",
             "CHECKPOINT_REPORT_ILLEGITIMATE_AUTHORITY")
    return sh, main


def reconcile_reports(
    g1: Mapping[str, Any], g2: Mapping[str, Any], reader: Any, *,
    diagnostic_code_sha: str, expected_diagnostic_pr_head: str,
) -> dict[str, Any]:
    """Bound one PR head + main/graph revision after both prior GET reports.

    diagnostic_code_sha is the actual checkout commit (often a PR merge commit),
    NOT the selected PR #326 HEAD or necessarily the #336 branch tip.
    expected_diagnostic_pr_head is GitHub's event PR #336 head, rechecked via GET.
    """
    checkout = _sha(diagnostic_code_sha, "CHECKPOINT_DIAGNOSTIC_CODE_SHA_INVALID")
    source_head = _sha(expected_diagnostic_pr_head,
                       "CHECKPOINT_DIAGNOSTIC_PR_HEAD_INVALID")
    selected_head, observed_main = _bounded_observed_reports(g1, g2)
    # Use G1's existing bounded GitHub reader + source parsers. No new transport.
    _repo(reader, CURRENT_REPO, REPO_ID)
    pr_first = _pr(reader)
    main_first = _branch(reader, CURRENT_REPO, "main")
    _require(pr_first["head_sha"] == selected_head,
             "CHECKPOINT_SELECTED_PR_MOVED_AFTER_G1_G2")
    _require(main_first == observed_main,
             "CHECKPOINT_MAIN_MOVED_AFTER_G1_G2")
    current_graph = _graph(reader, main_first)
    main_last = _branch(reader, CURRENT_REPO, "main")
    pr_last = _pr(reader)
    _require(main_first == main_last == observed_main and
             pr_first == pr_last and pr_last["head_sha"] == selected_head,
             "CHECKPOINT_SOURCE_MOVED_DURING_FINAL_READ")
    original_graph = _mapping(g1["known_graph"], "CHECKPOINT_GRAPH_RECEIPT_MISSING")
    _require(current_graph == original_graph, "CHECKPOINT_MAIN_GRAPH_DIGEST_CHANGED")
    diag = _mapping(
        reader.get(f"/repos/{CURRENT_REPO}/pulls/{DIAGNOSTIC_PR}"),
        "CHECKPOINT_DIAGNOSTIC_PR_MISSING",
    )
    head = _mapping(diag.get("head"), "CHECKPOINT_DIAGNOSTIC_SOURCE_MISSING")
    base = _mapping(diag.get("base"), "CHECKPOINT_DIAGNOSTIC_BASE_MISSING")
    head_repo = _mapping(head.get("repo"), "CHECKPOINT_DIAGNOSTIC_REPO_MISSING")
    base_repo = _mapping(base.get("repo"), "CHECKPOINT_DIAGNOSTIC_REPO_MISSING")
    _require(type(diag.get("number")) is int and
             diag["number"] == DIAGNOSTIC_PR and
             diag.get("state") == "open" and diag.get("draft") is True and
             head_repo.get("full_name") == CURRENT_REPO and
             base_repo.get("full_name") == CURRENT_REPO and
             base.get("ref") == DIAGNOSTIC_BASE,
             "CHECKPOINT_DIAGNOSTIC_PR_IDENTITY_INVALID")
    _require(_sha(head.get("sha"), "CHECKPOINT_DIAGNOSTIC_HEAD_INVALID") ==
             source_head, "CHECKPOINT_DIAGNOSTIC_PR_MOVED")
    return {
        "schema": SCHEMA,
        "result": "OBSERVATIONS_COHERENT_UNQUALIFIED",
        "scope": "BOUNDED_SELECTED_PR_HEAD_AND_MAIN_GRAPH_NOT_GLOBAL_TRANSACTION",
        "repository": CURRENT_REPO, "repository_id": REPO_ID,
        "selected_pr": CANDIDATE_PR, "selected_pr_head": selected_head,
        "main_source_sha": main_last,
        "graph_path": current_graph["path"],
        "graph_git_blob_sha": current_graph["git_blob_sha"],
        "graph_raw_sha256": current_graph["raw_sha256"],
        "diagnostic_pr": DIAGNOSTIC_PR,
        "diagnostic_pr_source_head_sha": source_head,
        "diagnostic_code_sha": checkout,
        "observed_check_count": g2["check_run_set"]["count"],
        "observed_review_count": g2["review_set"]["count"],
        "required_checks_policy": "UNKNOWN_NOT_OBTAINED_FROM_PROTECTION",
        "reviewer_independence": "NOT_QUALIFIED",
        "owner_source_authenticated": False, "positive_evidence_admitted": False,
        "native_E_earned": 0, "production_authorized": False,
        "ready_for_production": False, "writes": 0,
    }


def _no_duplicate_keys(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        _require(key not in result, "CHECKPOINT_JSON_DUPLICATE_KEY")
        result[key] = value
    return result


def _load(path: str) -> Mapping[str, Any]:
    raw = Path(path).read_bytes()
    _require(0 < len(raw) <= MAX_REPORT_BYTES, "CHECKPOINT_JSON_LENGTH_INVALID")
    result = json.loads(raw.decode("utf-8"), object_pairs_hook=_no_duplicate_keys)
    return _mapping(result, "CHECKPOINT_JSON_NOT_OBJECT")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only G1/G2 exact-head checkpoint")
    parser.add_argument("--g1", required=True, help="Existing source-census JSON path")
    parser.add_argument("--g2", required=True, help="Existing evidence-census JSON path")
    parser.add_argument("--diagnostic-code-sha", required=True,
                        help="actual checkout SHA; may be PR synthetic merge commit")
    parser.add_argument("--expected-diagnostic-pr-head", required=True,
                        help="immutable event #336 PR branch head to compare to provider")
    args = parser.parse_args(argv)
    try:
        report = reconcile_reports(
            _load(args.g1), _load(args.g2), ReadOnlyGitHub(os.environ.get("GITHUB_TOKEN", "")),
            diagnostic_code_sha=args.diagnostic_code_sha,
            expected_diagnostic_pr_head=args.expected_diagnostic_pr_head,
        )
    except Exception as exc:
        print(json.dumps({"schema": SCHEMA,
                          "result": "HOLD_CROSS_REPORT_SOURCE_CHECKPOINT",
                          "reason_code": str(exc) if isinstance(exc, LiveCensusHold)
                          else "GET_OR_REPORT_UNAVAILABLE",
                          "production_authorized": False, "writes": 0},
                         sort_keys=True))
        return 1
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
