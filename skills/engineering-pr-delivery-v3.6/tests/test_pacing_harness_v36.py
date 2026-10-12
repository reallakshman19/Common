"""Tests for v3.6 bounded decomposition pacing harness."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import lifecycle_v36 as lc
import decompose_v36 as dc
import pacing_harness_v36 as ph

LABEL = lc.load_label(ROOT / "tests" / "fixtures" / "relay" / "AIM" / "V35-LIFECYCLE.yaml")
PLAN = dc.load_plan(ROOT / "plans" / "V36-341-PLAN-02.yaml", LABEL)


class FakeClient:
    repo = "reallakshman19/Common"

    def __init__(self):
        self.issues = []
        self.comments = []
        self.calls = []

    def list_issues(self):
        return list(self.issues)

    def list_comments(self, n):
        self.calls.append(("list_comments", n))
        return list(self.comments)

    def create_issue(self, title, body):
        self.calls.append(("create_issue", title))
        number = 500 + len(self.issues)
        issue = {
            "number": number,
            "title": title,
            "body": body,
            "html_url": f"https://github.com/reallakshman19/Common/issues/{number}"
        }
        self.issues.append(issue)
        return issue

    def create_comment(self, n, body):
        self.calls.append(("create_comment", n))
        item = {"id": 1000 + len(self.comments), "body": body}
        self.comments.append(item)
        return item

    def update_comment(self, comment_id, body):
        self.calls.append(("update_comment", comment_id))
        for c in self.comments:
            if c["id"] == comment_id:
                c["body"] = body
                return c
        return {"id": comment_id, "body": body}


class PacingHarnessTests(unittest.TestCase):
    def test_dry_run_never_creates_issues(self):
        client = FakeClient()
        res = ph.run_bounded_decomposition(PLAN, client, apply=False)
        self.assertTrue(res["dry_run"])
        self.assertEqual(res["items_created"], 0)
        self.assertEqual(res["batches_executed"], 0)
        self.assertEqual(len(client.calls), 0)
        self.assertEqual(res["total_missing"], len(PLAN["tasks"]))

    def test_bounded_apply_batches_and_creates_all(self):
        client = FakeClient()
        # Set 0 item and batch delays for fast deterministic test execution
        res = ph.run_bounded_decomposition(
            PLAN, client, apply=True, batch_size=2,
            item_delay_seconds=0.0, batch_delay_seconds=0.0
        )
        self.assertFalse(res["dry_run"])
        self.assertEqual(res["items_created"], len(PLAN["tasks"]))
        # PLAN has 4 tasks; with batch_size=2, exactly 2 batches
        expected_batches = (len(PLAN["tasks"]) + 1) // 2
        self.assertEqual(res["batches_executed"], expected_batches)
        self.assertEqual(len(res["latencies_seconds"]), len(PLAN["tasks"]))
        self.assertEqual(len(client.issues), len(PLAN["tasks"]))
        self.assertGreater(len(client.comments), 0)

    def test_idempotent_subsequent_run(self):
        client = FakeClient()
        # First run creates everything
        ph.run_bounded_decomposition(
            PLAN, client, apply=True, batch_size=10,
            item_delay_seconds=0.0, batch_delay_seconds=0.0
        )
        initial_issues = len(client.issues)

        # Second run should find 0 missing and create 0 issues
        res2 = ph.run_bounded_decomposition(
            PLAN, client, apply=True, batch_size=10,
            item_delay_seconds=0.0, batch_delay_seconds=0.0
        )
        self.assertEqual(res2["total_missing"], 0)
        self.assertEqual(res2["items_created"], 0)
        self.assertEqual(len(client.issues), initial_issues)

    def test_parent_repository_mismatch_fails(self):
        client = FakeClient()
        client.repo = "different/repository"
        with self.assertRaises(lc.ContractError):
            ph.run_bounded_decomposition(PLAN, client, apply=False)


if __name__ == "__main__":
    unittest.main()
