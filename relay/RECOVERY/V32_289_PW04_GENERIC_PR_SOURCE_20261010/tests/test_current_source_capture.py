"""Full source capture and capture→native→managed PR→C6 end-to-end tests.

GitHub provider is a deterministic GET-only fixture; this test never accesses
the Owner's private repo or authenticates a human.
"""
from __future__ import annotations

from base64 import b64encode
from copy import deepcopy
from hashlib import sha1
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pr_source_binding import PreviewPins
from v32_capture_current_source import capture, CaptureHold, git_blob
from v32_integrated_shadow import integrated_shadow, SnapshotGET

REPO = "owner/source-lab"
HEAD = "a" * 40
BASE = "b" * 40
GRAPH = {
    "schema": "relay-v3.2-delp-execution-graph",
    "programme": {"repository": REPO, "root": REPO + "#1", "base_ref": "main"},
    "nodes": [
        {"ref": REPO+"#1", "kind": "ROOT"},
        {"ref": REPO+"#2", "kind": "LEAF", "parent": REPO+"#1",
         "weight": 1, "primary_pr": REPO+"#10",
         "units": [{"id": "U01", "weight": 100}]},
    ],
}


def graph_raw(graph=GRAPH):
    return json.dumps(graph, sort_keys=True).encode()


class FakeGET:
    def __init__(self, graph=GRAPH):
        self.graph = graph_raw(graph)
        self.log = []
        self.repo_id = 42
        self.source = REPO
        self.base = BASE
        self.final_base = BASE
        self.head = HEAD
        self.pr_base_ref = "main"
        self.wrong_head_repo_id = None
        self.issue_title_changes = False
        self.issue_calls = 0
        self.comment_calls = 0
        self.comments = []
        self.pr_reads = 0
        self.pr_change = False

    def __call__(self, endpoint):
        self.log.append(endpoint)
        assert endpoint.startswith("repos/") and "/"+REPO.split("/")[-1] in endpoint
        if endpoint == f"repos/{REPO}":
            return {"id": self.repo_id, "full_name": self.source, "default_branch": "main"}
        if endpoint == f"repos/{REPO}/commits/main":
            count = sum(e.endswith("/commits/main") for e in self.log)
            return {"sha": self.final_base if count > 1 else self.base}
        if "/contents/governance/released-graph.json?" in endpoint:
            return {"type": "file", "encoding": "base64",
                    "content": b64encode(self.graph).decode(), "sha": git_blob(self.graph)}
        if endpoint.endswith("/issues/1") or endpoint.endswith("/issues/2"):
            no = int(endpoint[-1])
            self.issue_calls += 1
            title = f"Original human issue {no}"
            if self.issue_title_changes and self.issue_calls > 2:
                title += " moved"
            return {"number": no, "title": title, "body": "Human issue description"}
        if endpoint.endswith("/pulls/10"):
            self.pr_reads += 1
            sha = "f"*40 if self.pr_change and self.pr_reads > 1 else self.head
            return {
                "number": 10, "state": "closed", "merged": True,
                "merged_at": "2026-10-09T11:00:00Z",
                "title": "Human PR title", "body": "Human PR details.",
                "head": {"sha": sha, "ref": "lab/issue2",
                         "repo": {"id": self.wrong_head_repo_id or self.repo_id,
                                  "full_name": REPO}},
                "base": {"sha": BASE, "ref": self.pr_base_ref,
                         "repo": {"id": self.repo_id, "full_name": REPO}},
            }
        if "/issues/2/comments?" in endpoint:
            self.comment_calls += 1
            return deepcopy(self.comments)
        raise AssertionError(endpoint)


class CurrentCaptureTests(unittest.TestCase):
    def setUp(self):
        self.g = FakeGET()
        self.raw = self.g.graph

    def do(self):
        return capture(self.raw, REPO, git_blob(self.raw), self.g)

    def test_01_two_pass_complete_capture(self):
        result = self.do()
        self.assertEqual(result["repository_id"], 42)
        self.assertEqual(result["graph_git_blob"], git_blob(self.raw))
        self.assertEqual(result["pulls"]["10"]["head"]["sha"], HEAD)
        self.assertEqual(set(result["issues"]), {"1", "2"})
        self.assertEqual(result["source_kind"], "GITHUB_GET_ONLY_UNATTESTED")
        self.assertEqual(result["owner_release"], "NOT_VERIFIED")
        self.assertEqual(self.g.pr_reads, 2)
        self.assertEqual(self.g.issue_calls, 4)
        self.assertEqual(self.g.comment_calls, 2)
        self.assertTrue(all(p.startswith("repos/") for p in self.g.log))
        self.assertFalse(hasattr(SnapshotGET(result), "patch_title"))

    def test_02_capture_graph_is_independent_pin(self):
        self.assertEqual(git_blob(self.raw), git_blob(self.g.graph))
        with self.assertRaisesRegex(CaptureHold, "PINNED_RELEASED_GRAPH_INVALID"):
            capture(self.raw, REPO, "f"*40, self.g)
        self.assertEqual(self.g.log, [])

    def test_03_provider_graph_replaced_refuses(self):
        self.g.graph = self.g.graph + b" "
        with self.assertRaisesRegex(CaptureHold, "RELEASED_PROVIDER_GRAPH_PIN_MISMATCH"):
            self.do()

    def test_04_issue_move_refuses(self):
        self.g.issue_title_changes = True
        with self.assertRaisesRegex(CaptureHold, "ISSUE_CHANGED_DURING_READ"):
            self.do()

    def test_05_pr_head_move_refuses(self):
        self.g.pr_change = True
        with self.assertRaisesRegex(CaptureHold, "PR_CHANGED_DURING_READ"):
            self.do()

    def test_06_repo_name_move_refuses(self):
        self.g.source = "foreign/source-lab"
        with self.assertRaisesRegex(CaptureHold, "PROVIDER_REPOSITORY_MISMATCH"):
            self.do()

    def test_07_foreign_numeric_pr_head_refuses(self):
        self.g.wrong_head_repo_id = 43
        with self.assertRaisesRegex(CaptureHold, "PR_REPOSITORY_IDENTITY_MISMATCH"):
            self.do()

    def test_08_base_moves_refuses(self):
        self.g.final_base = "f"*40
        with self.assertRaisesRegex(CaptureHold, "DEFAULT_BRANCH_MOVED_DURING_READ"):
            self.do()

    def test_09_incomplete_comment_refuses(self):
        self.g.comments = [{"id": 19, "body": "source incomplete", "user": {"login": "user"}}]
        with self.assertRaisesRegex(CaptureHold, "COMMENT_SOURCE_INVALID"):
            self.do()

    def test_10_same_comment_id_refuses(self):
        c = {"id": 19, "body": "foo", "author_association": "CONTRIBUTOR",
             "user": {"login": "user"}}
        self.g.comments = [c, deepcopy(c)]
        with self.assertRaisesRegex(CaptureHold, "COMMENT_DUPLICATE_ID"):
            self.do()

    def test_11_full_repo_graph_leaf_matches_real_original_ref_grammar(self):
        r = self.do()
        self.assertEqual(r["pulls"]["10"]["number"], 10)
        self.assertEqual(r["main_sha"], BASE)

    @unittest.skipUnless((Path(__file__).resolve().parents[4] / "skills" /
                          "engineering-pr-delivery-v3.2" / "scripts" /
                          "delp_projection_v32.py").is_file(), "needs real native checkout")
    def test_12_end_to_end_capture_native_issue_pr_c6_idempotence(self):
        source = self.do()
        pins = PreviewPins(REPO, 42, git_blob(self.raw), REPO+"#2", HEAD)
        result = integrated_shadow(self.raw, pins, source)
        # Genuine original lab graphs use owner/repo#PR; the unchanged native
        # responsibility-core reader currently refuses this valid binding.
        # Native DELP + C6 still run; hold the unqualified cross-view core.
        self.assertIsNone(result["native_core"])
        self.assertEqual(result["native_core_hold"], "RESPONSIBILITY_CORE_MATERIAL_BOUNDARY")
        self.assertTrue(result["native_input_digest"].startswith("sha256:"))
        self.assertEqual(result["c6_frontier"]["observed"]["candidate_sha"], HEAD)
        self.assertIn("Human PR details.", result["pr_body_preview"])
        self.assertEqual(len(result["in_memory_issue_second_pass"]), 2)
        self.assertTrue(all(x["status"] == "UNCHANGED"
                            for x in result["in_memory_issue_second_pass"].values()))
        self.assertFalse(result["production_activation"])
        self.assertFalse(result["issue_or_pr_github_writes"])


if __name__ == "__main__":
    unittest.main()
