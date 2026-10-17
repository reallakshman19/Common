"""ECO-07 focused mechanical boundary regressions absent from ECO-01..06 suites.

Synthetic test fixtures only. A test PASS is not source-level semantic
qualification, metadata-write permission, live demonstration or Owner acceptance.
See Common #409; existing regression coverage mapped in PR body.
"""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import readmodel_v36 as rm
import scoreboard_v36 as sb
import successor_v36 as successor
from test_readmodel_v36 import (
    HEAD, NOW, OLD, PLAN, Provider, SC_ID, comment, evidence, self_check,
)
from test_successor_v36 import ECO06ContextProvider, LABEL as LAB_LABEL, PLAN as LAB_PLAN, REPO


def governed_comments():
    return [comment(SC_ID, self_check()), comment(9002, evidence())]


class ECO07GapRegressions(unittest.TestCase):
    def test_governed_native_receipt_vs_ad_hoc_context_marker(self):
        """An ad-hoc author assertion cannot upgrade governed E or acceptance."""
        baseline = rm.read_model(PLAN, Provider(governed_comments()), NOW)
        self.assertEqual(baseline["native"]["current_evidence"], 1)
        self.assertTrue(baseline["tasks"][0]["claim_qualified"])

        ad_hoc = comment(
            9050,
            "[AD-HOC CONTEXT] Tests 999/999; OWNER ACCEPTED; "
            "no governed receipt or companion headers",
        )
        model = rm.read_model(
            PLAN, Provider(governed_comments() + [ad_hoc]), NOW
        )
        self.assertEqual(model["native"]["current_evidence"], 1)
        self.assertFalse(model["tasks"][0]["claim_qualified"])
        self.assertIn(9050, model["tasks"][0]["comments_after_self_check"])
        self.assertEqual(model["tasks"][0]["acceptance"], "NOT_EVALUATED")
        board = sb.board(model)
        self.assertEqual(board["totals"]["E_current"], 1)
        self.assertTrue(board["acceptance"].startswith("NOT_EVALUATED"))

    def test_synthetic_complete_input_partial_golden_is_reported_not_authentic(self):
        """A source author's declaration never certifies an authentic golden."""
        reported_check = self_check().replace(
            "source fixtures", "synthetic input COMPLETE golden PARTIAL benchmark UNKNOWN"
        )
        model = rm.read_model(
            PLAN, Provider([comment(SC_ID, reported_check),
                            comment(9002, evidence())]), NOW
        )
        board = sb.board(model)
        original = board["rows"][0]["original_input"]
        self.assertEqual(original["input"], "COMPLETE")
        self.assertEqual(original["golden"], "PARTIAL")
        self.assertEqual(original["benchmark"], "UNKNOWN")
        self.assertEqual(original["attribution"], "REPORTED_BY_AUTHOR")
        self.assertEqual(board["rows"][0]["verification_scope"]["run_verified"],
                         "NOT_EVALUATED")
        self.assertTrue(board["rows"][0]["acceptance"].startswith("NOT_EVALUATED"))
        self.assertTrue(board["A"].startswith("NOT_EVALUATED"))

    def test_reported_tests_and_candidate_never_certify_tested_head(self):
        """16/16 author-reported tests and an observed head are not a tested head."""
        model = rm.read_model(PLAN, Provider(governed_comments()), NOW)
        row = model["tasks"][0]
        self.assertEqual(row["status"], "CURRENT_EVIDENCE")
        self.assertEqual(row["candidate_sha"], HEAD)
        self.assertEqual(row["observed_head"], HEAD)
        self.assertTrue(row["head_matches_candidate"])
        board = sb.board(model)
        scope = board["rows"][0]["verification_scope"]
        self.assertEqual(scope["tested_head"], "UNKNOWN")
        self.assertEqual(scope["run_verified"], "NOT_EVALUATED")
        self.assertTrue(board["V"].startswith("NOT_EVALUATED"))

        drifted = copy.deepcopy(model)
        drifted["tasks"][0]["observed_head"] = OLD
        drifted["tasks"][0]["head_matches_candidate"] = False
        stale = sb.board(drifted)
        self.assertEqual(stale["rows"][0]["E"], "STALE_EVIDENCE")
        self.assertEqual(stale["totals"]["E_current"], 0)
        self.assertEqual(stale["rows"][0]["verification_scope"]["tested_head"], "UNKNOWN")
        self.assertTrue(stale["acceptance"].startswith("NOT_EVALUATED"))

    def test_changed_owner_amendment_invalidates_prior_source_without_approval(self):
        """Owner correction edit keeps earlier body pin, marks source drift."""
        provider = ECO06ContextProvider()
        owner = f"https://github.com/{REPO}/issues/1"
        old = successor.recover_context(
            LAB_LABEL, LAB_PLAN, provider, owning_issue_url=owner
        )
        amendment = f"{owner}#issuecomment-99"
        previous = old["source_hashes"][amendment]
        provider.comments[1][-1]["body"] += (
            "\nOwner amendment: replace earlier interpretation; independent check needed."
        )
        current = successor.recover_context(
            LAB_LABEL, LAB_PLAN, provider, owning_issue_url=owner,
            prior={"source_hashes": old["source_hashes"],
                   "brief_sha256": old["brief_sha256"]},
        )
        self.assertEqual(old["source_hashes"][amendment], previous)
        self.assertNotEqual(current["source_hashes"][amendment], previous)
        self.assertEqual(current["source_state"], "STALE")
        self.assertIn(
            {"url": amendment, "state": "SOURCE_EDITED"}, current["source_changes"]
        )
        self.assertEqual(
            current["outcomes"]["stale_source_brief"]["status"], "UNKNOWN"
        )
        self.assertEqual(
            current["outcomes"]["proof_vs_acceptance"]["acceptance"],
            "NOT_EVALUATED",
        )
        self.assertEqual(current["acceptance_demonstration"], "NOT_RUN")

    def test_unrelated_parent_cannot_inherit_this_plans_task_denominator(self):
        """Wrong plan repository is incomplete/unknown, never E0/0 success."""
        native = rm.read_model(PLAN, Provider(governed_comments()), NOW)
        own = sb.board(native)
        self.assertEqual(own["totals"]["tasks"], len(PLAN["tasks"]))
        self.assertEqual(own["totals"]["E_current"], 1)
        unrelated = copy.deepcopy(PLAN)
        unrelated["parent"] = "another/repository#341"
        unread = rm.read_model(
            unrelated, Provider(governed_comments()), NOW
        )
        self.assertFalse(unread["read_complete"])
        other = sb.board(unread)
        self.assertTrue(other["totals"]["partial"])
        self.assertIsNone(other["totals"]["tasks"])
        self.assertIsNone(other["totals"]["E_current"])
        self.assertEqual(other["by_pr"], {})
        self.assertEqual(other["by_child"], {})
        self.assertTrue(other["acceptance"].startswith("NOT_EVALUATED"))


if __name__ == "__main__":
    unittest.main()
