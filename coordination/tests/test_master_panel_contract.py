"""M1-U01 model and discriminating synthetic fixtures (no network needed).

Run: python -m unittest coordination.tests.test_master_panel_contract -v
These tests do not qualify the U02 durable pagination/restart or U03 API.
"""
import json
import unittest
from pathlib import Path

from coordination.master_panel.models import (
    ROW_SCHEMA_VERSION, SourceIdentity, SourceKind, build_row, version_trace
)

FIXTURE = Path(__file__).parent / "fixtures" / "master_panel"


def source_from_fixture(data):
    return SourceIdentity(**{**data, "kind": SourceKind(data["kind"])})


class TestMasterPanelRowContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.positive = json.loads((FIXTURE / "positive.json").read_text(encoding="utf-8"))
        cls.negative = json.loads((FIXTURE / "negative.json").read_text(encoding="utf-8"))

    def test_known_sources_are_distinct_across_repositories(self):
        p = self.positive
        self.assertEqual(p["schema_version"], ROW_SCHEMA_VERSION)
        left = source_from_fixture(p["source"])
        right = source_from_fixture(p["second_repo"])
        self.assertEqual(left.stable_key, p["expected"]["identity_key"])
        self.assertEqual(right.stable_key, p["expected"]["second_identity_key"])
        self.assertNotEqual(left.stable_key, right.stable_key)

    def test_report_is_never_independent_review(self):
        p = self.positive
        row = build_row(
            source_from_fixture(p["source"]), bindings=p["bindings"],
            report=p["report"], coordinator=p["coordinator"],
            source_state=p["source_state"], freshness=p["freshness"],
            completed_scan=p["completed_scan"], present=p["present"],
        )
        self.assertEqual(row["schema_version"], ROW_SCHEMA_VERSION)
        self.assertEqual(row["binding"]["state"], p["expected"]["binding_state"])
        self.assertEqual(row["report"]["provenance"], "PROVIDER_REPORT")
        self.assertEqual(row["evidence"]["reported_verdict"], "PASS")
        self.assertEqual(row["evidence"]["review_verdict"], "UNKNOWN")
        self.assertIsNone(row["evidence"]["review_ref"])
        self.assertEqual(row["coordinator_observation"]["liveness"], "UNKNOWN")
        self.assertEqual(row["absence"], "PRESENT")
        serialized = json.dumps(row)
        self.assertNotIn("synthetic A", serialized)
        self.assertNotIn("raw_body", serialized)
        self.assertNotIn("owner_token", serialized)

    def test_edit_revert_and_exact_replay_fixture(self):
        p = self.positive
        trace = version_trace([tuple(x) for x in p["observations"]])
        self.assertEqual(len(trace), p["expected"]["versions"])
        self.assertEqual(len({x["body_sha256"] for x in trace}),
                         p["expected"]["unique_digests"])
        self.assertNotEqual(trace[0]["version"], trace[-1]["version"])
        self.assertEqual(trace[0]["body_sha256"], trace[-1]["body_sha256"])
        self.assertEqual(trace[-1]["version"], 3)

    def test_negative_absence_conflict_old_head_and_review_provenance(self):
        source = source_from_fixture(self.positive["source"])
        for case in self.negative["cases"]:
            with self.subTest(case=case["name"]):
                kwargs = {
                    k: case[k] for k in (
                        "bindings", "report", "review", "source_state",
                        "completed_scan", "present", "current_pr_head_sha"
                    ) if k in case
                }
                if "expected_error" in case:
                    with self.assertRaisesRegex(ValueError, case["expected_error"]):
                        build_row(source, **kwargs)
                    continue
                row = build_row(source, **kwargs)
                if "expected_absence" in case:
                    self.assertEqual(row["absence"], case["expected_absence"])
                if "expected_binding" in case:
                    self.assertEqual(row["binding"]["state"], case["expected_binding"])
                    self.assertIsNone(row["binding"]["assignment_id"])
                if "expected_relation" in case:
                    self.assertEqual(row["evidence"]["candidate_relation"],
                                     case["expected_relation"])
                    self.assertEqual(row["evidence"]["review_verdict"], "PASS")

    def test_conflicting_same_revision_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Conflicting body"):
            version_trace([("2026-10-14T00:00:00Z", "A"),
                           ("2026-10-14T00:00:00Z", "B")])

    def test_unseen_out_of_order_revision_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Out-of-order"):
            version_trace([("2026-10-14T01:00:00Z", "B"),
                           ("2026-10-14T00:00:00Z", "A")])

    def test_private_raw_identifiers_rejected(self):
        s = self.positive["source"]
        for changed in ({"repo_id":"abc"}, {"body_sha256":"bad"},
                        {"url":"https://chatgpt.com/c/private"},
                        {"entity_id":"different-comment-id"}):
            with self.subTest(changed=changed):
                with self.assertRaises(ValueError):
                    source_from_fixture({**s, **changed})
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            build_row(source_from_fixture(s), report={
                "task_id":"Bearer ghp_secret_should_not_be_public"
            })

    def test_mismatched_cross_project_binding_is_hard_conflict(self):
        source = source_from_fixture(self.positive["source"])
        with self.assertRaisesRegex(ValueError, "Cross-project"):
            build_row(source, bindings=[{"project_id":"aa3",
                                         "assignment_id":"wrong"}])


if __name__ == "__main__":
    unittest.main()
