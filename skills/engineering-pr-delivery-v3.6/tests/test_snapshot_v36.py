"""WP3: test current/stale, invalid, missing and ambiguous evidence without writes."""
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import decompose_v36 as dc
import lifecycle_v36 as lc
import snapshot_v36 as ss

LABEL = lc.load_label(ROOT / "tests/fixtures/relay/AIM/V35-LIFECYCLE.yaml")
PLAN = dc.load_plan(ROOT / "plans/V36-341-PLAN-02.yaml", LABEL)
HEAD = "11b17586e7a14c4be90cca46cb4a2193804cd59e"
OLD = "46071cbc695226a3ba29f2c53f64a0103102302d"
ISSUE = {"number": 345, "title": "V36-341-WP1", "state": "open",
         "body": "**Parent:** #341 · **Task:** V36-341-WP1 · **Size:** S",
         "html_url": "https://github.com/reallakshman19/Common/issues/345"}


def evidence(sha=OLD, outcome="O1", child="reallakshman19/Common#345"):
    return lc.render_evidence(
        outcome=outcome, for_user="A usable lifecycle plan exists",
        proof="https://github.com/reallakshman19/Common/pull/344/commits/"+sha,
        task_id="V36-341-WP1", issue_ref=child,
        candidate="reallakshman19/Common@"+sha, tests_passed=16, tests_run=16)


class Provider:
    repo = "reallakshman19/Common"
    def __init__(self, comments=None, issues=None, head=HEAD):
        self.issues = [ISSUE] if issues is None else issues
        self.comments = comments if comments is not None else [{"body": evidence()}]
        self.head = head
    def list_issues(self): return self.issues
    def list_comments(self, n): return self.comments if n == 345 else []
    def get_pr(self, n):
        if n != 344: raise lc.ContractError("wrong PR")
        return {"head": {"sha": self.head}, "draft": True}


class SnapshotTests(unittest.TestCase):
    def test_real_wp1_stale(self):
        r = ss.snapshot(PLAN, Provider())
        self.assertEqual((r["total"], r["stale_evidence"], r["verified_complete"]), (7, 1, 0))
        self.assertEqual(r["tasks"][0]["status"], "STALE_EVIDENCE")

    def test_current_not_complete(self):
        r = ss.snapshot(PLAN, Provider(comments=[{"body": evidence(HEAD)}]))
        self.assertEqual(r["tasks"][0]["status"], "CURRENT_EVIDENCE")
        self.assertFalse(r["tasks"][0]["complete"])

    def test_cross_child_rejected(self):
        r = ss.snapshot(PLAN, Provider(comments=[{"body": evidence(child="reallakshman19/Common#999")}]))
        self.assertEqual(r["tasks"][0]["status"], "INVALID_EVIDENCE")

    def test_wrong_outcome_rejected(self):
        r = ss.snapshot(PLAN, Provider(comments=[{"body": evidence(outcome="O3")}]))
        self.assertEqual(r["tasks"][0]["status"], "INVALID_EVIDENCE")

    def test_fake_comment_not_completion(self):
        r = ss.snapshot(PLAN, Provider(comments=[{"body": "task ready"}]))
        self.assertEqual(r["tasks"][0]["status"], "NO_EVIDENCE")

    def test_no_children_not_zero_progress_claim(self):
        r = ss.snapshot(PLAN, Provider(issues=[]))
        self.assertTrue(all(t["status"] == "MISSING_CHILD" for t in r["tasks"]))

    def test_duplicate_child_ambiguous(self):
        r = ss.snapshot(PLAN, Provider(issues=[ISSUE, dict(ISSUE)]))
        self.assertEqual(r["tasks"][0]["status"], "AMBIGUOUS_CHILD")

    def test_wrong_repo_proof_rejected(self):
        wrong = evidence(HEAD).replace("github.com/reallakshman19/Common/pull/", "github.com/other/repo/pull/")
        r = ss.snapshot(PLAN, Provider(comments=[{"body": wrong}]))
        self.assertEqual(r["tasks"][0]["status"], "UNVERIFIED_PROOF")

    def test_provider_failure_unknown(self):
        provider = Provider(comments=[{"body": evidence(HEAD)}])
        def fail(n): raise lc.ContractError("offline")
        provider.get_pr = fail
        r = ss.snapshot(PLAN, provider)
        self.assertEqual(r["tasks"][0]["status"], "PROVIDER_UNAVAILABLE")

    def test_multiple_undated_ambiguous(self):
        r = ss.snapshot(PLAN, Provider(comments=[{"body": evidence(OLD)}, {"body": evidence(HEAD)}]))
        self.assertEqual(r["tasks"][0]["status"], "AMBIGUOUS_EVIDENCE")

    def test_dated_comment_newest(self):
        provider = Provider(comments=[
            {"body": evidence(OLD), "created_at": "2026-10-11T05:00:00Z", "id": 1},
            {"body": evidence(HEAD), "created_at": "2026-10-12T05:00:00Z", "id": 2}])
        self.assertEqual(ss.snapshot(PLAN, provider)["tasks"][0]["status"], "CURRENT_EVIDENCE")

    def test_closed_child_stale_remains_stale(self):
        r = ss.snapshot(PLAN, Provider(issues=[{**ISSUE, "state": "closed"}]))
        self.assertEqual(r["tasks"][0]["status"], "STALE_EVIDENCE")

if __name__ == "__main__":
    unittest.main()
