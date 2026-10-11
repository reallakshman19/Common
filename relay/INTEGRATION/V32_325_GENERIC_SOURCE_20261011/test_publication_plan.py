"""T03: only pure planning and readback, never a GitHub mutator."""
import copy
import unittest

import delp_projection_v32 as delp
import pr_responsibility_view_v32 as view

from test_current_source_reconciliation import (
    CurrentSourceTests, GRAPH_PATH, HEAD, LEAF, PR_NUM, REPO, ROOT_REF,
)
from generic_source_preflight import SourceHold
from generic_current_source import reconcile_current_source
from generic_publication_plan import build_publication_plan, reconcile_publication_readback

PR_REF = "Pipeline#740"


class PurePublisherPlanTests(CurrentSourceTests):
    # Inherited adversarial current-source regressions still execute on this
    # actual native V3.2 fixture, but T03-specific tests start at test_22.
    def setUp(self):
        super().setUp()
        self.source = self.call()
        ledger = delp.ledger_from_github(self.provider, self.graph)
        observations = delp.observe_github(self.provider, self.graph)
        self.projection = delp.project(self.graph, ledger, observations)
        self.observed = {
            ROOT_REF: copy.deepcopy(self.provider.issues[718]),
            LEAF: copy.deepcopy(self.provider.issues[733]),
            PR_REF: copy.deepcopy(self.provider.pull),
        }
        self.views = {
            "root": ROOT_REF, "leaf": LEAF,
            "plan_digest": self.projection["plan_digest"],
            "delp_input_digest": self.projection["input_digest"],
            "input_digest": "sha256:" + "c" * 64,
            "parent_semantic": {
                k: self.projection["nodes"][ROOT_REF]["progress"][k] for k in ("D", "E")
            },
            "leaf_semantic": {
                k: self.projection["nodes"][LEAF]["progress"][k] for k in ("P", "E")
            },
            "pr": {"head_sha": HEAD, "binding": "BOUND"},
            "human_titles": {
                ROOT_REF: "Root", LEAF: "Leaf", "PR": "Candidate"
            },
            "issue_titles": {
                ROOT_REF: "🟡 [718] NEXT #733/C4 — Root",
                LEAF: "🟡 [718›733] R-PROJECTION · C4 — Leaf",
            },
            "draft_pr_title": "🟡 [718›733] DRAFT · VIEW-PR · HEAD:bbbbbbb — Candidate",
            "issue_read_views": {
                ROOT_REF: view.ISSUE_START + "\nOWNER SOURCE: Root\n" + view.ISSUE_END,
                LEAF: view.ISSUE_START + "\nOWNER SOURCE: Leaf\n" + view.ISSUE_END,
            },
            "pr_managed_block": view.START + "\nPR OBSERVED HEAD: bbbbbbb\n" + view.END,
        }

    def build(self, **changes):
        opts = dict(graph=self.graph, source=self.source,
                    projection=self.projection, views=self.views,
                    observed_surfaces=self.observed)
        opts.update(changes)
        return build_publication_plan(**opts)

    def test_22_three_disjoint_surface_ownership_and_human_preservation(self):
        plan = self.build()
        self.assertEqual(plan["status"], "PLAN_ONLY_UNATTESTED")
        self.assertEqual(plan["order"], [LEAF, ROOT_REF, PR_REF])
        self.assertEqual(plan["writers"]["issue_title_and_live_status"],
                         "NATIVE_DELP_SYNC_PROJECTION_ONLY")
        self.assertEqual(plan["writers"]["issue_body"],
                         "MANAGED_ISSUE_BODY_ONLY")
        self.assertEqual(plan["writers"]["pr_title_and_body"],
                         "SEPARATE_GUARDED_PR_METADATA")
        self.assertEqual(plan["writes"], 0)
        self.assertFalse(plan["production_authorized"])
        for ref in (ROOT_REF, LEAF, PR_REF):
            row = plan["surfaces"][ref]
            self.assertTrue(row["body_write_required"])
            self.assertIn(self.observed[ref]["body"], row["expected_body"])
            self.assertEqual(row["observed_body_digest"], view.digest(self.observed[ref]["body"]))
            self.assertEqual(row["expected_body_digest"], view.digest(row["expected_body"]))
            self.assertTrue(row["write_required"])
        self.assertEqual(plan["expected_native_input_digest"], self.projection["input_digest"])

    def test_23_second_plan_is_idempotent_no_body_or_title_changes(self):
        plan = self.build()
        for ref in (ROOT_REF, LEAF, PR_REF):
            self.observed[ref]["title"] = plan["surfaces"][ref]["expected_title"]
            self.observed[ref]["body"] = plan["surfaces"][ref]["expected_body"]
        second = self.build()
        self.assertEqual(second["changes"], [])
        self.assertTrue(all(not second["surfaces"][r]["write_required"]
                            for r in (ROOT_REF, LEAF, PR_REF)))
        self.assertEqual(second["writes"], 0)

    def test_24_human_owner_title_changed_cannot_be_overwritten(self):
        self.observed[ROOT_REF]["title"] = "Edited directly by Owner"
        with self.assertRaisesRegex(SourceHold, "^OWNER_HUMAN_TITLE_CHANGED$"):
            self.build()

    def test_25_multiple_or_broken_managed_markers_hard_hold(self):
        self.observed[LEAF]["body"] += "\n" + view.ISSUE_START + "\n" + view.ISSUE_START
        with self.assertRaisesRegex(SourceHold, "^MANAGED_BODY_MARKERS_UNSAFE$"):
            self.build()

    def test_26_native_delp_input_mismatch_holds_before_planning(self):
        self.views["delp_input_digest"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(SourceHold, "^PUBLISHER_NATIVE_INPUT_MISMATCH$"):
            self.build()

    def test_27_wrong_pr_head_or_node_binding_fails(self):
        self.views["pr"]["head_sha"] = "d" * 40
        with self.assertRaisesRegex(SourceHold, "^PUBLISHER_PR_HEAD_MISMATCH$"):
            self.build()

    def test_28_recheck_full_body_and_title_detects_race(self):
        plan = self.build()
        after = copy.deepcopy(self.observed)
        after[LEAF]["body"] = "Owner just changed this"
        report = reconcile_publication_readback(plan, after, {})
        self.assertEqual(report["status"], "INCOMPLETE_SYNC")
        self.assertIn(LEAF, report["unverified_surfaces"])
        self.assertFalse(report["verified"])
        self.assertFalse(report["production_authorized"])

    def test_29_partial_write_is_reported_not_rolled_back(self):
        plan = self.build()
        after = copy.deepcopy(self.observed)
        after[LEAF]["title"] = plan["surfaces"][LEAF]["expected_title"]
        after[LEAF]["body"] = plan["surfaces"][LEAF]["expected_body"]
        report = reconcile_publication_readback(plan, after, {})
        self.assertEqual(report["status"], "INCOMPLETE_SYNC")
        self.assertEqual(report["matched_surfaces"], [LEAF])
        self.assertEqual(set(report["unverified_surfaces"]), {ROOT_REF, PR_REF})
        self.assertFalse(report["verified"])

    def test_30_matching_surfaces_without_native_status_is_incomplete(self):
        plan = self.build()
        after = copy.deepcopy(self.observed)
        for ref in (LEAF, ROOT_REF, PR_REF):
            after[ref]["title"] = plan["surfaces"][ref]["expected_title"]
            after[ref]["body"] = plan["surfaces"][ref]["expected_body"]
        report = reconcile_publication_readback(plan, after, {})
        self.assertEqual(report["status"], "INCOMPLETE_SYNC")
        self.assertEqual(report["unverified_native_status"], [ROOT_REF, LEAF])

    def test_31_verified_readback_is_observation_not_approval(self):
        plan = self.build()
        after = copy.deepcopy(self.observed)
        for ref in (LEAF, ROOT_REF, PR_REF):
            after[ref]["title"] = plan["surfaces"][ref]["expected_title"]
            after[ref]["body"] = plan["surfaces"][ref]["expected_body"]
        status = {
            r: {"version": 1, "input_digest": plan["expected_native_input_digest"]}
            for r in (ROOT_REF, LEAF)
        }
        report = reconcile_publication_readback(plan, after, status)
        self.assertEqual(report["status"], "OBSERVED_MATCH_NOT_AUTHORIZATION")
        self.assertTrue(report["verified"])
        self.assertFalse(report["production_authorized"])
        self.assertEqual(report["writes"], 0)

    def test_32_lookalike_stale_digest_or_wrong_pr_identity_not_verified(self):
        plan = self.build()
        after = copy.deepcopy(self.observed)
        for ref in (LEAF, ROOT_REF, PR_REF):
            after[ref]["title"] = plan["surfaces"][ref]["expected_title"]
            after[ref]["body"] = plan["surfaces"][ref]["expected_body"]
        after[PR_REF]["number"] = 741
        statuses = {
            r: {"version": 2, "input_digest": "sha256:" + "e" * 64}
            for r in (ROOT_REF, LEAF)
        }
        report = reconcile_publication_readback(plan, after, statuses)
        self.assertEqual(report["status"], "INCOMPLETE_SYNC")
        self.assertFalse(report["verified"])
        self.assertIn(PR_REF, report["unverified_surfaces"])

    def test_33_untrusted_source_authority_cannot_be_elevated(self):
        adulterated = dict(self.source, production_authorized=True)
        with self.assertRaisesRegex(SourceHold, "^SOURCE_AUTHORITY_NOT_READONLY$"):
            self.build(source=adulterated)

    def test_34_forged_view_progress_refused_against_native_projection(self):
        self.views["leaf_semantic"] = {"P": 100, "E": 100}
        with self.assertRaisesRegex(SourceHold, "^PUBLISHER_NATIVE_PROGRESS_MISMATCH$"):
            self.build()


if __name__ == "__main__":
    unittest.main()
