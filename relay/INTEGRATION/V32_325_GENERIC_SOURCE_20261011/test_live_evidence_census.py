"""G2 source-grounded negative cases, never mock independent acceptance."""
from __future__ import annotations

import ast
import copy
import urllib.error
import unittest
from pathlib import Path

from live_evidence_census import (
    CURRENT_REPO, LiveCensusHold, PR_NUMBER, census
)
HEAD = "a" * 40


class FakeEvidenceGET:
    def __init__(self):
        self.calls = []
        self.pr_reads = 0
        self.check_reads = 0
        self.review_reads = 0
        self.heads = [HEAD]
        self.checks = [
            {"id": 100, "name": "generic-source-preflight (3.11)",
             "head_sha": HEAD, "status": "completed", "conclusion": "success",
             "app": {"slug": "github-actions"}, "html_url": "https://github.com/example"},
            {"id": 101, "name": "validate-v3-2-candidate",
             "head_sha": HEAD, "status": "completed", "conclusion": "skipped",
             "app": {"slug": "github-actions"}, "html_url": "https://github.com/example"},
        ]
        self.reviews = []

    def get(self, path):
        self.calls.append(("GET", path))
        if path == f"/repos/{CURRENT_REPO}":
            return {"full_name": CURRENT_REPO, "id": 1412133785,
                    "default_branch": "main"}
        if path == f"/repos/{CURRENT_REPO}/pulls/{PR_NUMBER}":
            self.pr_reads += 1
            head = self.heads[min(self.pr_reads - 1, len(self.heads) - 1)]
            return {"number": PR_NUMBER, "state": "open", "draft": True,
                    "merged": False,
                    "head": {"sha": head, "repo": {"full_name": CURRENT_REPO}},
                    "base": {"ref": "main", "repo": {"full_name": CURRENT_REPO}}}
        if f"/repos/{CURRENT_REPO}/commits/" in path and path.endswith("/check-runs?per_page=100"):
            self.check_reads += 1
            return {"total_count": len(self.checks),
                    "check_runs": copy.deepcopy(self.checks)}
        if path.endswith("/branches/main/protection"):
            raise urllib.error.HTTPError("https://api.github.com" + path, 403,
                                         "Resource not accessible", None, None)
        raise AssertionError("Unexpected API GET " + path)

    def get_json(self, path):
        self.calls.append(("GET_JSON", path))
        if path == f"/repos/{CURRENT_REPO}/pulls/{PR_NUMBER}/reviews?per_page=100":
            self.review_reads += 1
            return copy.deepcopy(self.reviews)
        raise AssertionError("Unexpected API collection GET " + path)


class ReadOnlyG2Tests(unittest.TestCase):
    def test_01_checks_are_observed_but_policy_and_reviews_not_admitted(self):
        out = census(FakeEvidenceGET())
        self.assertEqual(out["check_run_set"]["count"], 2)
        self.assertEqual(out["check_run_set"]["success"], 1)
        self.assertEqual(out["check_run_set"]["skipped"], 1)
        self.assertEqual(out["review_set"]["count"], 0)
        self.assertEqual(out["branch_protection_probe"], "UNAVAILABLE_HTTP_403")
        self.assertEqual(out["required_checks_policy"], "UNKNOWN_NOT_OBTAINED_FROM_PROTECTION")
        self.assertEqual(out["native_E_earned_by_this_census"], 0)
        self.assertFalse(out["production_authorized"])
        self.assertEqual(out["writes"], 0)

    def test_02_pr_head_moves_between_reads_is_rejected(self):
        p = FakeEvidenceGET()
        p.heads = [HEAD, "b" * 40]
        with self.assertRaisesRegex(LiveCensusHold, "EVIDENCE_PROVIDER_CHANGED_DURING_READ"):
            census(p)

    def test_03_cross_repository_fork_is_rejected(self):
        p = FakeEvidenceGET()
        orig = p.get
        def drift(path):
            data = orig(path)
            if path == f"/repos/{CURRENT_REPO}/pulls/{PR_NUMBER}":
                data["head"]["repo"]["full_name"] = "attacker/Common"
            return data
        p.get = drift
        with self.assertRaisesRegex(LiveCensusHold, "EVIDENCE_PR_REPOSITORY_MISMATCH"):
            census(p)

    def test_04_foreign_check_sha_is_rejected(self):
        p = FakeEvidenceGET()
        p.checks[0]["head_sha"] = "b" * 40
        with self.assertRaisesRegex(LiveCensusHold, "EVIDENCE_CHECK_IDENTITY_OR_HEAD_MISMATCH"):
            census(p)

    def test_05_incomplete_check_page_is_rejected(self):
        p = FakeEvidenceGET()
        orig = p.get
        def bad(path):
            data = orig(path)
            if "/check-runs?" in path:
                data["total_count"] = 101
            return data
        p.get = bad
        with self.assertRaisesRegex(LiveCensusHold, "EVIDENCE_CHECK_SET_INCOMPLETE_OR_PAGINATED"):
            census(p)

    def test_06_approvals_observed_not_qualified_as_independent(self):
        p = FakeEvidenceGET()
        p.reviews = [
            {"id": 52, "user": {"login": "reviewer-a"}, "state": "APPROVED",
             "commit_id": HEAD, "submitted_at": "2026-10-11T07:00:00Z"},
            {"id": 53, "user": {"login": "reviewer-b"}, "state": "APPROVED",
             "commit_id": HEAD, "submitted_at": "2026-10-11T07:01:00Z"},
        ]
        out = census(p)
        self.assertEqual(out["review_set"]["at_head_approvals_observed"], 2)
        self.assertEqual(out["reviewer_independence"], "NOT_QUALIFIED")
        self.assertEqual(out["evidence_policy_version"], "NOT_AUTHENTICATED")
        self.assertFalse(out["positive_evidence_admitted"])

    def test_07_check_set_moves_between_reads_is_rejected(self):
        p = FakeEvidenceGET()
        orig = p.get
        def changing(path):
            data = orig(path)
            if "/check-runs?" in path and p.check_reads == 2:
                data["check_runs"][0]["conclusion"] = "failure"
            return data
        p.get = changing
        with self.assertRaisesRegex(LiveCensusHold, "EVIDENCE_PROVIDER_CHANGED_DURING_READ"):
            census(p)

    def test_08_duplicate_check_ids_refused(self):
        p = FakeEvidenceGET()
        p.checks[1]["id"] = p.checks[0]["id"]
        with self.assertRaisesRegex(LiveCensusHold, "EVIDENCE_CHECK_IDENTITY_OR_HEAD_MISMATCH"):
            census(p)

    def test_09_wrong_repo_stable_id_refused(self):
        p = FakeEvidenceGET()
        original = p.get
        def wrong(path):
            data = original(path)
            if path == f"/repos/{CURRENT_REPO}":
                data["id"] = 1207996454
            return data
        p.get = wrong
        with self.assertRaisesRegex(LiveCensusHold, "EVIDENCE_REPOSITORY_IDENTITY_INVALID"):
            census(p)

    def test_10_transport_shares_strict_GET_only_with_G1(self):
        p = Path(__file__).with_name("live_evidence_census.py")
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr.lower(),
                                 {"patch", "post", "put", "delete", "system", "popen", "write"})
        self.assertIn("ReadOnlyGitHub", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
