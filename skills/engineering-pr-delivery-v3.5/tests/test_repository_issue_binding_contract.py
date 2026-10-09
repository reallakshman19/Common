"""Source-level classification of provider-observed repository/issue identity.

The fixture captures historic GitHub readbacks; matching its fields at runtime
DOES NOT replace a fresh authenticated GET by an external controller. No caller
may mint writer/Stage2 authority from the result of this pure formatting check.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "relay/CONTINUITY/REVIEWER_ONLY/REPOSITORY_ISSUE_BINDING_PROVIDER_NEGATIVES_V1.json"


def format_qualifies_current_issue(row: dict, expected_repository: str) -> bool:
    if row.get("lookup_repository") != expected_repository:
        return False
    if row.get("api_status") != 200 or row.get("returned_kind") != "issue":
        return False
    if row.get("returned_pull_request_marker") is not False:
        return False
    if type(row.get("returned_repository_id")) is not int or row["returned_repository_id"] != 1412133785:
        return False
    if row.get("returned_repository_url") != "https://api.github.com/repos/" + expected_repository:
        return False
    issue_id = row.get("returned_issue_id")
    if type(issue_id) is not int or issue_id < 1:
        return False
    if not isinstance(row.get("returned_issue_node_id"), str) or not row["returned_issue_node_id"].startswith("I_"):
        return False
    number = row.get("lookup_number")
    if type(number) is not int or number < 1 or row.get("returned_issue_number") != number:
        return False
    url = row.get("returned_url")
    if not isinstance(url, str):
        return False
    parsed = urlparse(url)
    owner, name = expected_repository.split("/", 1)
    return (
        parsed.scheme == "https"
        and parsed.netloc == "github.com"
        and parsed.path == f"/{owner}/{name}/issues/{number}"
        and not parsed.query
        and not parsed.fragment
        and not parsed.params
        and not parsed.username
        and not parsed.password
    )


class ProviderIssueBindingFormatTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(self.document["schema"], "relay-provider-issue-readback-negatives-v1")
        self.repo = self.document["expected_repository"]
        self.rows = {row["id"]: row for row in self.document["observations"]}

    def test_real_readback_fixture_format_positive_and_negative(self):
        self.assertEqual(len(self.rows), 7)
        for key, row in self.rows.items():
            with self.subTest(key=key):
                self.assertEqual(
                    format_qualifies_current_issue(row, self.repo),
                    row["expected_provider_issue_kind_match"],
                )

    def test_recovery_audit_does_not_call_pr_2_an_issue(self):
        report = (ROOT / "relay/CONTINUITY/REVIEWER_ONLY/V32_BUDDY_RECOVERY_P0_GOVERNANCE_20261009.md").read_text(encoding="utf-8")
        self.assertNotIn("new issue #2](https://github.com/reallakshman19/Common/issues/2)", report)
        self.assertIn("new governance issue #4](https://github.com/reallakshman19/Common/issues/4)", report)
        self.assertIn("new PR #2](https://github.com/reallakshman19/Common/pull/2)", report)

    def test_pr_number_is_not_current_issue_binding(self):
        pr = self.rows["N01"]
        self.assertFalse(format_qualifies_current_issue(pr, self.repo))
        self.assertFalse(format_qualifies_current_issue({**pr, "returned_kind": "issue"}, self.repo))
        self.assertFalse(format_qualifies_current_issue({**pr, "returned_kind": "issue", "returned_pull_request_marker": False}, self.repo))
        self.assertFalse(format_qualifies_current_issue({**pr, "returned_issue_node_id": "I_forged", "returned_kind": "issue", "returned_pull_request_marker": False}, self.repo))

    def test_old_repo_issue_and_missing_new_issue_fail_closed(self):
        self.assertFalse(format_qualifies_current_issue(self.rows["N02"], self.repo))
        self.assertFalse(format_qualifies_current_issue(self.rows["N03"], self.repo))
        self.assertFalse(format_qualifies_current_issue(self.rows["N04"], self.repo))
        self.assertFalse(format_qualifies_current_issue(self.rows["N05"], self.repo))

    def test_stable_repo_issue_ids_and_response_kind_fail_closed(self):
        good = self.rows["P02"]
        for mutation in (
            {"returned_repository_id": 1207996454},
            {"returned_issue_id": None},
            {"returned_issue_id": True},
            {"returned_issue_node_id": "PR_fake"},
            {"returned_issue_number": 2},
            {"returned_repository_url": "https://api.github.com/repos/reallaksh19/Common"},
            {"returned_pull_request_marker": True},
            {"returned_pull_request_marker": None},
        ):
            with self.subTest(mutation=mutation):
                self.assertFalse(format_qualifies_current_issue({**good, **mutation}, self.repo))
        self.assertTrue(format_qualifies_current_issue(good, self.repo))
        self.assertEqual(self.document["expected_repository_id"], 1412133785)

    def test_provider_object_kind_is_not_owner_scope_admission(self):
        self.assertTrue(format_qualifies_current_issue(self.rows["P01"], self.repo))
        self.assertTrue(format_qualifies_current_issue(self.rows["P02"], self.repo))
        self.assertTrue(all(r["dispatch_authorization"] == "NOT_ASSESSED" for r in self.rows.values()))

    def test_forged_cross_repo_url_and_host_are_denied(self):
        good = self.rows["P02"]
        self.assertFalse(format_qualifies_current_issue({**good, "returned_url": "https://github.com/reallaksh19/Common/issues/6"}, self.repo))
        self.assertFalse(format_qualifies_current_issue({**good, "returned_url": "https://github.com.evil.invalid/reallakshman19/Common/issues/6"}, self.repo))
        self.assertFalse(format_qualifies_current_issue({**good, "returned_url": "https://github.com/reallakshman19/Common/pull/6"}, self.repo))

    def test_readback_qualifier_grants_no_runtime_authority(self):
        self.assertEqual(self.document["grade"], "SOURCE_OBSERVED_GITHUB_GET_SNAPSHOT_ONLY")
        self.assertIn("does not constitute runtime provider admission", self.document["warning"])
        self.assertTrue(all(r["dispatch_authorization"] == "NOT_ASSESSED" for r in self.rows.values()))


if __name__ == "__main__":
    unittest.main()
