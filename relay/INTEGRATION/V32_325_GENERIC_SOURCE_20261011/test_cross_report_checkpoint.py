"""B2-N03 regression: existing real-GET G1/G2 output join, not real Owner proof."""
from __future__ import annotations

import ast
import copy
import json
import tempfile
import unittest
from pathlib import Path

from cross_report_checkpoint import (
    SCHEMA, DIAGNOSTIC_BASE, LiveCensusHold, _load, _no_duplicate_keys,
    reconcile_reports,
)
from live_source_census import CURRENT_REPO, census as source_census
from live_evidence_census import census as evidence_census
from test_live_source_census import FakeReader
from test_live_evidence_census import FakeEvidenceGET

SELECTED_HEAD = "b" * 40
DIAGNOSTIC_HEAD = "d" * 40
CHECKOUT_HEAD = "e" * 40
MAIN_HEAD = "1" * 40


class FinalReader(FakeReader):
    """One bounded final GET window after the two distinct source reports."""

    def __init__(self):
        super().__init__()
        self.moved_pr = False
        self.move_pr_second = False
        self.moved_main = False
        self.move_main_second = False
        self.changed_graph = False
        self.diagnostic_head = DIAGNOSTIC_HEAD
        self.bad_diagnostic_base = False
        self.bad_repo_id = False
        self._pr_reads_final = 0
        self._main_reads_final = 0

    def get(self, path):
        if path == f"/repos/{CURRENT_REPO}/pulls/336":
            return {
                "number": 336, "state": "open", "draft": True,
                "head": {"sha": self.diagnostic_head,
                         "repo": {"full_name": CURRENT_REPO}},
                "base": {"ref": "main" if self.bad_diagnostic_base else DIAGNOSTIC_BASE,
                         "repo": {"full_name": CURRENT_REPO}},
            }
        if path == f"/repos/{CURRENT_REPO}/pulls/326":
            self._pr_reads_final += 1
            item = super().get(path)
            if self.moved_pr or (self.move_pr_second and self._pr_reads_final > 1):
                item["head"]["sha"] = "c" * 40
            return item
        if path == f"/repos/{CURRENT_REPO}/branches/main":
            self._main_reads_final += 1
            item = super().get(path)
            if self.moved_main or (self.move_main_second and self._main_reads_final > 1):
                item["commit"]["sha"] = "2" * 40
            return item
        if "/contents/" in path and self.changed_graph:
            self.graph["programme"]["root"] = "forged-root"
        item = super().get(path)
        if path == f"/repos/{CURRENT_REPO}" and self.bad_repo_id:
            item["id"] = 1207996454
        return item


def reports():
    """Generate reports using the *existing* G1/G2 parsers and safe fake GETs."""
    g1 = source_census(FakeReader())
    provider = FakeEvidenceGET()
    provider.heads = [SELECTED_HEAD]
    for check in provider.checks:
        check["head_sha"] = SELECTED_HEAD
    g2 = evidence_census(provider)
    return g1, g2


def run_pair(g1=None, g2=None, reader=None, *, code=CHECKOUT_HEAD,
             diagnostic_head=DIAGNOSTIC_HEAD):
    if g1 is None or g2 is None:
        a, b = reports()
        g1 = a if g1 is None else g1
        g2 = b if g2 is None else g2
    return reconcile_reports(g1, g2, reader if reader is not None else FinalReader(),
                             diagnostic_code_sha=code,
                             expected_diagnostic_pr_head=diagnostic_head)


class CrossReportCheckpointTests(unittest.TestCase):
    def test_01_coherent_unqualified_with_skipped_check_and_no_reviews(self):
        out = run_pair()
        self.assertEqual(out["schema"], SCHEMA)
        self.assertEqual(out["result"], "OBSERVATIONS_COHERENT_UNQUALIFIED")
        self.assertEqual(out["selected_pr"], 326)
        self.assertEqual(out["selected_pr_head"], SELECTED_HEAD)
        self.assertEqual(out["main_source_sha"], MAIN_HEAD)
        self.assertEqual(out["diagnostic_pr"], 336)
        self.assertEqual(out["diagnostic_pr_source_head_sha"], DIAGNOSTIC_HEAD)
        self.assertEqual(out["diagnostic_code_sha"], CHECKOUT_HEAD)
        self.assertNotEqual(out["diagnostic_code_sha"], out["selected_pr_head"])
        self.assertEqual(out["observed_check_count"], 2)
        self.assertEqual(out["observed_review_count"], 0)
        self.assertEqual(out["required_checks_policy"],
                         "UNKNOWN_NOT_OBTAINED_FROM_PROTECTION")
        self.assertEqual(out["reviewer_independence"], "NOT_QUALIFIED")
        self.assertFalse(out["owner_source_authenticated"])
        self.assertFalse(out["positive_evidence_admitted"])
        self.assertFalse(out["production_authorized"])
        self.assertEqual(out["native_E_earned"], 0)
        self.assertEqual(out["writes"], 0)

    def test_02_g2_head_differs_from_g1_after_two_green_censuses(self):
        g1, g2 = reports()
        g2["candidate_pr"]["head_sha"] = "a" * 40
        with self.assertRaisesRegex(LiveCensusHold, "CHECKPOINT_G1_G2_HEAD_MISMATCH"):
            run_pair(g1, g2)

    def test_03_wrong_numeric_repository_id_is_not_fuzzy_match(self):
        g1, g2 = reports()
        g2["repository_id"] = 1207996454
        with self.assertRaisesRegex(LiveCensusHold, "CHECKPOINT_REPOSITORY_ID_MISMATCH"):
            run_pair(g1, g2)

    def test_04_selected_pr_number_mismatch_refused(self):
        g1, g2 = reports()
        g2["candidate_pr"]["number"] = 313
        with self.assertRaisesRegex(LiveCensusHold,
                                    "CHECKPOINT_SELECTED_PR_IDENTITY_MISMATCH"):
            run_pair(g1, g2)

    def test_05_head_moves_after_g2_and_g1_but_before_final_get(self):
        provider = FinalReader()
        provider.moved_pr = True
        with self.assertRaisesRegex(
                LiveCensusHold, "CHECKPOINT_SELECTED_PR_MOVED_AFTER_G1_G2"):
            run_pair(reader=provider)

    def test_06_head_moves_during_final_get_window(self):
        provider = FinalReader()
        provider.move_pr_second = True
        with self.assertRaisesRegex(
                LiveCensusHold, "CHECKPOINT_SOURCE_MOVED_DURING_FINAL_READ"):
            run_pair(reader=provider)

    def test_07_main_moves_after_g1_and_before_final_get(self):
        provider = FinalReader()
        provider.moved_main = True
        with self.assertRaisesRegex(LiveCensusHold,
                                    "CHECKPOINT_MAIN_MOVED_AFTER_G1_G2"):
            run_pair(reader=provider)

    def test_08_main_moves_during_final_get_window(self):
        provider = FinalReader()
        provider.move_main_second = True
        with self.assertRaisesRegex(
                LiveCensusHold, "CHECKPOINT_SOURCE_MOVED_DURING_FINAL_READ"):
            run_pair(reader=provider)

    def test_09_main_graph_blob_changes_with_same_main_ref(self):
        provider = FinalReader()
        provider.changed_graph = True
        with self.assertRaisesRegex(LiveCensusHold,
                                    "CHECKPOINT_MAIN_GRAPH_DIGEST_CHANGED"):
            run_pair(reader=provider)

    def test_10_diagnostic_branch_moves_within_check(self):
        provider = FinalReader()
        provider.diagnostic_head = "f" * 40
        with self.assertRaisesRegex(LiveCensusHold,
                                    "CHECKPOINT_DIAGNOSTIC_PR_MOVED"):
            run_pair(reader=provider)

    def test_11_diagnostic_pr_base_must_remain_selected_feature_branch(self):
        provider = FinalReader()
        provider.bad_diagnostic_base = True
        with self.assertRaisesRegex(
                LiveCensusHold, "CHECKPOINT_DIAGNOSTIC_PR_IDENTITY_INVALID"):
            run_pair(reader=provider)

    def test_12_repository_provider_id_rechecked_at_end(self):
        provider = FinalReader()
        provider.bad_repo_id = True
        with self.assertRaisesRegex(
                LiveCensusHold, "REPOSITORY_STABLE_IDENTITY_MISMATCH"):
            run_pair(reader=provider)

    def test_13_report_claiming_owner_or_evidence_authority_fails(self):
        g1, g2 = reports()
        g1["owner_source_authenticated"] = True
        with self.assertRaisesRegex(
                LiveCensusHold, "CHECKPOINT_REPORT_ILLEGITIMATE_AUTHORITY"):
            run_pair(g1, g2)
        g1, g2 = reports()
        g2["native_E_earned_by_this_census"] = 1
        with self.assertRaisesRegex(
                LiveCensusHold, "CHECKPOINT_REPORT_ILLEGITIMATE_AUTHORITY"):
            run_pair(g1, g2)

    def test_14_missing_or_truncated_check_and_review_sets_fail(self):
        g1, g2 = reports()
        g2["check_run_set"]["runs"] = []
        with self.assertRaisesRegex(
                LiveCensusHold, "CHECKPOINT_EVIDENCE_REPORT_PARTIAL"):
            run_pair(g1, g2)
        g1, g2 = reports()
        g2["review_set"]["count"] = 1
        with self.assertRaisesRegex(
                LiveCensusHold, "CHECKPOINT_EVIDENCE_REPORT_PARTIAL"):
            run_pair(g1, g2)

    def test_15_wrong_schema_or_missing_graph_custody_refused(self):
        g1, g2 = reports()
        g1["schema"] = "old-schema"
        with self.assertRaisesRegex(LiveCensusHold,
                                    "CHECKPOINT_REPORT_SCHEMA_MISMATCH"):
            run_pair(g1, g2)
        g1, g2 = reports()
        g1["known_graph"]["source_commit"] = "0" * 40
        with self.assertRaisesRegex(LiveCensusHold,
                                    "CHECKPOINT_GRAPH_RECEIPT_INVALID"):
            run_pair(g1, g2)

    def test_16_bad_code_sha_and_duplicate_json_keys_fail(self):
        with self.assertRaisesRegex(
                LiveCensusHold, "CHECKPOINT_DIAGNOSTIC_CODE_SHA_INVALID"):
            run_pair(code="not a git sha")
        with self.assertRaisesRegex(
                LiveCensusHold, "CHECKPOINT_JSON_DUPLICATE_KEY"):
            _no_duplicate_keys([("a", 1), ("a", 2)])

    def test_17_bounded_loader_fails_on_duplicate_or_empty_json(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "report.json"
            path.write_text('{"schema":"a","schema":"b"}', encoding="utf-8")
            with self.assertRaisesRegex(
                    LiveCensusHold, "CHECKPOINT_JSON_DUPLICATE_KEY"):
                _load(str(path))
            path.write_bytes(b"")
            with self.assertRaisesRegex(
                    LiveCensusHold, "CHECKPOINT_JSON_LENGTH_INVALID"):
                _load(str(path))

    def test_18_new_consumer_is_read_only_not_second_transport(self):
        path = Path(__file__).with_name("cross_report_checkpoint.py")
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src)
        forbidden_imports = {"requests", "urllib", "httpx", "socket", "subprocess"}
        forbidden_methods = {"patch", "post", "put", "delete", "urlopen", "system",
                             "popen", "write_text", "write_bytes"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.assertTrue(all(x.name.split(".")[0] not in forbidden_imports
                                    for x in node.names))
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn((node.module or "").split(".")[0],
                                 forbidden_imports)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr.lower(), forbidden_methods)
        self.assertIn("ReadOnlyGitHub", src)
        workflow = (Path(__file__).parents[3] / ".github" / "workflows" /
                    "v32-325-generic-source-preflight.yml").read_text(encoding="utf-8")
        self.assertIn("B2-N02 G1/G2 same selected-PR-head", workflow)
        self.assertIn("--g1", workflow)
        self.assertIn("--g2", workflow)
        self.assertIn("--diagnostic-code-sha", workflow)
        self.assertIn("--expected-diagnostic-pr-head", workflow)
        self.assertIn("github.event.pull_request.number == 336", workflow)


if __name__ == "__main__":
    unittest.main()
