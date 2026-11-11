"""Native T02 read-only injected source readers: no transport or live admission.

All data are local synthetic GitHub-shaped fixtures. Exact native DELP is used
in the final integration test; it cannot attest the fake graph or fake issuer.
"""
from __future__ import annotations

import ast
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rest_readonly_provider import (
    BoundNativeReadOnlyGitHubProvider, BoundReadOnlyGitHubProvider,
    RestContractHold,
)
from generic_current_source import reconcile_current_source
from test_current_source_reconciliation import (
    FakeGraphSource, FakeNativeProvider, GRAPH_PATH, REVISION,
)
from test_generic_source_preflight import REPO, BASE, HEAD, PR_NUM, LEAF, fixture_graph


class NativeEnvelope(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.comments = [{"id": 11, "body": "Human source body",
                          "user": {"login": "source-author"},
                          "author_association": "MEMBER"}]
        self.compare_value = {"ahead_by": 2, "behind_by": 1}
        self.extra_ref = "candidate/source"
        self.provider = self.make()

    def make(self, **kwargs):
        settings = dict(
            repository=REPO, base_ref="main",
            read_issue=lambda no: {"number": no, "state": "open",
                                   "title": "Original issue", "body": "Original body"},
            read_pull=lambda no: {
                "number": no, "state": "open", "merged": False, "draft": True,
                "title": "Original PR", "body": "Original PR body",
                "head": {"sha": HEAD, "repo": {"full_name": REPO}},
                "base": {"ref": "main", "sha": BASE,
                         "repo": {"full_name": REPO}},
            },
            read_commit_sha=self.commit,
            read_comments=self.comment,
            read_compare=self.compare,
            allowed_candidate_refs=(self.extra_ref,),
        )
        settings.update(kwargs)
        return BoundNativeReadOnlyGitHubProvider(**settings)

    def commit(self, ref):
        self.calls.append(("COMMIT", ref))
        return BASE if ref == "main" else HEAD

    def comment(self, number):
        self.calls.append(("COMMENTS", number))
        return copy.deepcopy(self.comments)

    def compare(self, base, head):
        self.calls.append(("COMPARE", base, head))
        return copy.deepcopy(self.compare_value)

    def test_01_existing_base_adapter_remains_three_get_only(self):
        p = self.provider
        self.assertIsInstance(p, BoundReadOnlyGitHubProvider)
        self.assertEqual(p.get_issue(718)["number"], 718)
        self.assertTrue(p.get_pull(PR_NUM)["draft"])
        self.assertEqual(p.get_commit_sha("main"), BASE)
        self.assertEqual(p.list_comments(733)[0]["id"], 11)
        self.assertEqual(p.compare("main", self.extra_ref)["ahead_by"], 2)

    def test_02_unbound_extra_commit_ref_holds_before_transport(self):
        with self.assertRaisesRegex(RestContractHold, "^REST_NATIVE_COMMIT_REF_UNBOUND$"):
            self.provider.get_commit_sha("different/branch")
        self.assertEqual(self.calls, [])

    def test_03_selected_candidate_commit_reads_observed_sha(self):
        self.assertEqual(self.provider.get_commit_sha(self.extra_ref), HEAD)
        self.assertEqual(self.calls, [("COMMIT", self.extra_ref)])

    def test_04_invalid_candidate_ref_constructor_holds(self):
        for value in ("../main", "/root", "-bad", "other..branch"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(RestContractHold,
                                            "^REST_NATIVE_CANDIDATE_REF_INVALID$"):
                    self.make(allowed_candidate_refs=(value,))

    def test_05_missing_native_reader_is_not_silent_default(self):
        with self.assertRaisesRegex(RestContractHold, "^REST_NATIVE_GET_READER_REQUIRED$"):
            self.make(read_comments=None)
        with self.assertRaisesRegex(RestContractHold, "^REST_NATIVE_GET_READER_REQUIRED$"):
            self.make(read_compare=None)

    def test_06_comment_order_and_identity_must_be_original(self):
        for comments in (
            [{"id": 11, "body": "", "user": {"login": "a"},
              "author_association": "OWNER"}] * 2,
            [{"id": 0, "body": "", "user": {"login": "a"},
              "author_association": "OWNER"}],
            [{"id": 12, "body": "", "user": None,
              "author_association": "NONE"}],
            [{"id": "12", "body": "", "user": {"login": "a"},
              "author_association": "OWNER"}],
        ):
            with self.subTest(comments=comments):
                self.comments = comments
                with self.assertRaisesRegex(RestContractHold,
                                            "^REST_NATIVE_COMMENT_SOURCE_INVALID$"):
                    self.provider.list_comments(733)

    def test_07_comment_total_and_per_item_bounds_hard_hold(self):
        self.comments = [{"id": 1, "body": "x" * 1_000_001,
                          "user": {"login": "a"}, "author_association": "OWNER"}]
        with self.assertRaisesRegex(RestContractHold,
                                    "^REST_NATIVE_COMMENT_TEXT_UNBOUNDED$"):
            self.provider.list_comments(733)
        self.comments = [{"id": i + 1, "body": "",
                          "user": {"login": "a"}, "author_association": "OWNER"}
                         for i in range(1001)]
        with self.assertRaisesRegex(RestContractHold,
                                    "^REST_NATIVE_COMMENTS_INVALID_OR_UNBOUNDED$"):
            self.provider.list_comments(733)

    def test_08_comment_response_cannot_be_malformed_or_wrong_selection(self):
        self.comments = {"unbounded": "not a full page collection"}
        with self.assertRaisesRegex(RestContractHold,
                                    "^REST_NATIVE_COMMENTS_INVALID_OR_UNBOUNDED$"):
            self.provider.list_comments(733)
        with self.assertRaisesRegex(RestContractHold,
                                    "^REST_NATIVE_COMMENT_SELECTION_INVALID$"):
            self.provider.list_comments(0)

    def test_09_compare_wrong_refs_never_reach_caller_get(self):
        for base, head in (("other", self.extra_ref),
                           ("main", "../main"),
                           ("main", "unbound"),
                           ("main", "main")):
            with self.subTest(base=base, head=head):
                with self.assertRaisesRegex(RestContractHold,
                                            "^REST_NATIVE_COMPARE_REF_UNBOUND$"):
                    self.provider.compare(base, head)
        self.assertEqual(self.calls, [])

    def test_10_compare_invalid_observation_holds_without_fabrication(self):
        for bad in ({"ahead_by": -1, "behind_by": 1},
                    {"ahead_by": 1, "behind_by": False},
                    {"ahead_by": 1},
                    {"ahead_by": "1", "behind_by": 1}):
            with self.subTest(value=bad):
                self.compare_value = bad
                with self.assertRaisesRegex(RestContractHold,
                                            "^REST_NATIVE_COMPARE_RESPONSE_INVALID$"):
                    self.provider.compare("main", self.extra_ref)

    def test_11_native_adapter_is_a_network_and_writer_free_read_model(self):
        p = Path(__file__).resolve().parent / "rest_readonly_provider.py"
        tree = ast.parse(p.read_text(encoding="utf-8"))
        forbidden = {"socket", "subprocess", "requests", "urllib", "httpx"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.assertFalse(any(a.name.split(".")[0] in forbidden
                                     for a in node.names))
            elif isinstance(node, ast.ImportFrom):
                self.assertNotIn((node.module or "").split(".")[0], forbidden)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr.lower(),
                                 {"patch", "post", "put", "delete", "urlopen"})


class NativeT02Integration(unittest.TestCase):
    def test_12_existing_native_t02_consumes_injected_five_get_facade(self):
        graph = fixture_graph()
        raw = FakeNativeProvider()
        graph_provider = FakeGraphSource(graph)
        def pr_source(number):
            p = raw.get_pull(number)
            # These are explicitly synthetic fixtures, not inferred provider fields.
            p["draft"] = bool(p.get("draft", True))
            p["base"]["sha"] = BASE
            p.setdefault("title", "Other candidate")
            p.setdefault("body", "Original human PR context")
            return p
        source = BoundNativeReadOnlyGitHubProvider(
            repository=REPO, base_ref="main",
            read_issue=raw.get_issue,
            read_pull=pr_source,
            read_commit_sha=raw.get_commit_sha,
            read_comments=raw.list_comments,
            read_compare=raw.compare,
        )
        report = reconcile_current_source(
            repository=REPO, graph_path=GRAPH_PATH, graph_revision=REVISION,
            leaf_ref=LEAF, pr_number=PR_NUM, expected_head=HEAD,
            graph_provider=graph_provider, provider=source,
        )
        self.assertEqual(report["status"], "READ_ONLY_RECONCILED_UNATTESTED")
        self.assertEqual(report["native_progress"]["leaf"]["E"], 0)
        self.assertEqual(report["writes"], 0)
        self.assertFalse(report["source_authenticated"])
        self.assertFalse(report["production_authorized"])
        self.assertTrue(any(call[0] == "GET_COMMENTS" for call in raw.calls))


if __name__ == "__main__":
    unittest.main()
