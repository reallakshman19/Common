"""WP2 tests: no network, safe dry-run, child and parent index deduplication."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import lifecycle_v36 as lc
import decompose_v36 as dc

LABEL = lc.load_label(ROOT / "tests" / "fixtures" / "relay" / "AIM" / "V35-LIFECYCLE.yaml")
PLAN = dc.load_plan(ROOT / "plans" / "V36-341-PLAN-02.yaml", LABEL)


class FakeClient:
    repo = "reallakshman19/Common"

    def __init__(self, *, manual_wp1=False):
        self.issues = []
        self.comments = []
        self.calls = []
        if manual_wp1:
            self.issues.append({
                "number": 345,
                "html_url": "https://github.com/reallakshman19/Common/issues/345",
                "title": "[V3.6][O1/O2][DRAFT] V36-341-WP1 — independent label and evidence foundation",
                "body": "**Parent:** #341 · **Task:** V36-341-WP1 · **Size:** S",
            })

    def list_issues(self):
        return list(self.issues)

    def list_comments(self, n):
        self.calls.append(("list_comments", n))
        return list(self.comments)

    def create_issue(self, title, body):
        self.calls.append(("create_issue", title))
        number = 400 + len(self.issues)
        issue = {"number": number, "title": title, "body": body,
                 "html_url": f"https://github.com/reallakshman19/Common/issues/{number}"}
        self.issues.append(issue)
        return issue

    def create_comment(self, n, body):
        self.calls.append(("create_comment", n))
        item = {"id": 999, "body": body}
        self.comments.append(item)
        return item

    def update_comment(self, comment_id, body):
        self.calls.append(("update_comment", comment_id))
        self.comments[0]["body"] = body
        return self.comments[0]


class PlanTests(unittest.TestCase):
    def test_approved_label_binding(self):
        self.assertEqual(PLAN["label"]["label_sha"], LABEL["label_sha"])
        self.assertEqual(len(PLAN["tasks"]), 7)

    def test_reject_stale_sha(self):
        plan = {**PLAN, "label": {**PLAN["label"], "label_sha": "abc1234"}}
        with self.assertRaises(lc.ContractError):
            dc.validate_plan(plan, LABEL)

    def test_reject_other_parent(self):
        with self.assertRaises(lc.ContractError):
            dc.validate_plan({**PLAN, "parent": "someother/repo#341"}, LABEL)

    def test_reject_duplicate_task_ids(self):
        with self.assertRaises(lc.ContractError):
            dc.validate_plan({**PLAN, "tasks": PLAN["tasks"] + [PLAN["tasks"][0]]}, LABEL)

    def test_reject_missing_acceptance(self):
        changed = {key: value for key, value in PLAN["tasks"][0].items() if key != "acceptance"}
        with self.assertRaises(lc.ContractError):
            dc.validate_plan({**PLAN, "tasks": [changed]}, LABEL)

    def test_reject_invalid_size(self):
        task = {**PLAN["tasks"][0], "size": "XXL"}
        with self.assertRaises(lc.ContractError):
            dc.validate_plan({**PLAN, "tasks": [task]}, LABEL)

    def test_reject_unknown_outcome(self):
        task = {**PLAN["tasks"][0], "outcome": "O6"}
        with self.assertRaises(lc.ContractError):
            dc.validate_plan({**PLAN, "tasks": [task]}, LABEL)


class LiveShapeTests(unittest.TestCase):
    def test_dry_run_never_creates_issues_or_parent_index(self):
        client = FakeClient(manual_wp1=True)
        result = dc.execute(PLAN, client, apply=False)
        self.assertEqual(len(result["would_create"]), 6)
        self.assertEqual(len(client.calls), 0)
        self.assertEqual(result["index"], "pending")

    def test_applies_six_and_adopts_real_wp1_then_replay_noops(self):
        client = FakeClient(manual_wp1=True)
        result = dc.execute(PLAN, client, apply=True)
        self.assertEqual(result["already_present"], 1)
        self.assertEqual(len(result["created"]), 6)
        self.assertIn("issues/345", result["children"]["V36-341-WP1"])
        self.assertEqual(len(client.comments), 1)
        again = dc.execute(PLAN, client, apply=True)
        self.assertEqual(again["created"], [])
        self.assertEqual(again["index"], "unchanged")
        self.assertEqual(len([c for c in client.calls if c[0] == "create_issue"]), 6)
        self.assertEqual(len([c for c in client.calls if c[0] == "create_comment"]), 1)

    def test_fresh_parent_gets_seven_children(self):
        client = FakeClient()
        self.assertEqual(len(dc.execute(PLAN, client, apply=True)["created"]), 7)

    def test_duplicate_provider_issue_refuses_write(self):
        client = FakeClient(manual_wp1=True)
        client.issues.append(dict(client.issues[0]))
        with self.assertRaises(lc.ContractError):
            dc.execute(PLAN, client, apply=True)
        self.assertEqual(client.calls, [])

    def test_foreign_repo_refuses_write(self):
        client = FakeClient()
        client.repo = "other/repo"
        with self.assertRaises(lc.ContractError):
            dc.execute(PLAN, client, apply=True)

    def test_existing_index_is_updated_not_duplicated(self):
        client = FakeClient(manual_wp1=True)
        dc.execute(PLAN, client, apply=True)
        client.comments[0]["body"] = dc.index_marker(PLAN) + "\nstale\n"
        again = dc.execute(PLAN, client, apply=True)
        self.assertEqual(again["index"], "updated")
        self.assertEqual(len(client.comments), 1)

    def test_duplicate_parent_index_fails_closed(self):
        client = FakeClient(manual_wp1=True)
        body = dc.index_marker(PLAN) + "\n"
        client.comments = [{"id": 1, "body": body}, {"id": 2, "body": body}]
        with self.assertRaises(lc.ContractError):
            dc.execute(PLAN, client, apply=True)


if __name__ == "__main__":
    unittest.main()
