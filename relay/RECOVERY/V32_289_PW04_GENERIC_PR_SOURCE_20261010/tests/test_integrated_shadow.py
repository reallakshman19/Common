"""Full V3.2 lifecycle verification using the UNCHANGED native projector.

Synthetic provider material only; never accepts or publishes a production fact.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha1
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pr_source_binding import BindingError, PreviewPins
from v32_integrated_shadow import CycleHold, SnapshotGET, integrated_shadow, _native_modules

REPO = "author/example-lab"
HEAD = "a" * 40
BASE = "b" * 40
GRAPH = {
    "schema": "relay-v3.2-delp-execution-graph",
    "programme": {
        "repository": REPO, "root": "example-lab#1", "base_ref": "main"
    },
    "nodes": [
        {"ref": "example-lab#1", "kind": "ROOT"},
        {"ref": "example-lab#2", "kind": "LEAF", "parent": "example-lab#1",
         "weight": 1, "primary_pr": "example-lab#10",
         "units": [{"id": "U01", "weight": 100}]},
    ],
}


def raw(graph):
    return json.dumps(graph, sort_keys=True).encode()


def oid(data):
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def make():
    graph = deepcopy(GRAPH)
    binary = raw(graph)
    node_repo = {"full_name": REPO, "id": 42}
    pull = {
        "number": 10, "title": "Original human PR title",
        "body": "Original human PR body.\n\nHuman acceptance is not granted.",
        "head": {"sha": HEAD, "repo": deepcopy(node_repo)},
        "base": {"sha": BASE, "ref": "main", "repo": deepcopy(node_repo)},
        "state": "closed", "merged": True,
        "merged_at": "2026-10-09T11:00:00Z",
    }
    source = {
        "source_kind": "GITHUB_GET_ONLY_UNATTESTED",
        "repository": REPO, "repository_id": 42,
        "graph_git_blob": oid(binary),
        "base_ref": "main", "main_sha": BASE, "final_main_sha": BASE,
        "issues": {"1": {"title": "Original root human title"},
                   "2": {"title": "Original leaf human title"}},
        "pulls": {"10": pull},
        "comments": {"2": []},
    }
    pin = PreviewPins(REPO, 42, oid(binary), "example-lab#2", HEAD)
    return binary, pin, source


@unittest.skipUnless((Path(__file__).resolve().parents[4] / "skills" /
                      "engineering-pr-delivery-v3.2" / "scripts" /
                      "delp_projection_v32.py").is_file(), "requires real Common native V3.2 checkout")
class IntegratedFullLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.binary, self.pin, self.source = make()

    def cycle(self):
        return integrated_shadow(self.binary, self.pin, self.source)

    def test_01_one_complete_native_delp_to_issue_pr_c6_cycle(self):
        r = self.cycle()
        self.assertEqual(r["status"], "INTEGRATED_SHADOW_ONLY_NOT_RELEASE_READY")
        self.assertTrue(r["native_input_digest"].startswith("sha256:"))
        self.assertEqual(r["binding"]["primary_pr_number"], 10)
        self.assertEqual(r["native_core"]["digests"]["input"], r["native_input_digest"])
        self.assertEqual(r["c6_frontier"]["observed"]["candidate_sha"], HEAD)
        self.assertEqual(len(r["native_expected_issue_titles"]), 2)
        self.assertIn("Original human PR body.", r["pr_body_preview"])
        self.assertIn("relay-v32:pr-read-view:start", r["pr_body_preview"])
        self.assertTrue(r["pr_body_changed_in_preview"])
        self.assertEqual(len(r["in_memory_issue_first_pass"]), 2)
        self.assertTrue(all(x["status"] == "WRITTEN" for x in r["in_memory_issue_first_pass"].values()))
        self.assertTrue(all(x["status"] == "UNCHANGED" for x in r["in_memory_issue_second_pass"].values()))
        self.assertFalse(r["issue_or_pr_github_writes"])
        self.assertFalse(r["production_activation"])
        self.assertFalse(r["owner_source_authenticated"])
        self.assertFalse(r["eligible_evidence_admitted_by_this_cycle"])
        self.assertEqual(r["real_cold_successor"], "NOT_EXECUTED")

    def test_02_real_native_material_without_facts_not_credited(self):
        r = self.cycle()
        self.assertEqual(r["native_rejected_facts"], [])
        self.assertEqual(r["native_core"]["progress"]["leaf"]["E"], 0)
        self.assertIn(r["native_core"]["leaf_state"], ("UNMATERIALIZED", "EVIDENCE_GAP"))

    def test_03_pr_head_move_refuses(self):
        self.source["pulls"]["10"]["head"]["sha"] = "c" * 40
        with self.assertRaisesRegex(BindingError, "PROVIDER_PR_HEAD_MOVED"):
            self.cycle()

    def test_04_wrong_pr_base_ref_refuses(self):
        self.source["pulls"]["10"]["base"]["ref"] = "other"
        with self.assertRaisesRegex(BindingError, "PROVIDER_PR_WRONG_BASE"):
            self.cycle()

    def test_05_forged_graph_pin_refuses(self):
        self.source["graph_git_blob"] = "f" * 40
        with self.assertRaisesRegex(CycleHold, "SOURCE_GRAPH_BLOB_MISMATCH"):
            self.cycle()

    def test_06_fake_repo_identity_refuses(self):
        self.source["repository_id"] = 999
        with self.assertRaisesRegex(CycleHold, "SOURCE_NUMERIC_REPOSITORY_MISMATCH"):
            self.cycle()

    def test_07_default_branch_move_refuses(self):
        self.source["final_main_sha"] = "f" * 40
        with self.assertRaisesRegex(CycleHold, "SOURCE_DEFAULT_BRANCH_MOVED"):
            self.cycle()

    def test_08_missing_private_issue_refuses(self):
        del self.source["issues"]["2"]
        with self.assertRaisesRegex(CycleHold, "SOURCE_ISSUE_MISSING"):
            self.cycle()

    def test_09_missing_private_comment_feed_refuses(self):
        del self.source["comments"]["2"]
        with self.assertRaisesRegex(CycleHold, "SOURCE_COMMENTS_MISSING"):
            self.cycle()

    def test_10_duplicate_managed_pr_markers_refuse(self):
        self.source["pulls"]["10"]["body"] = (
            "<!-- relay-v32:pr-read-view:start -->" * 2 + "Human text")
        with self.assertRaisesRegex(Exception, "DUPLICATE_MANAGED_MARKER"):
            self.cycle()

    def test_11_snapshot_has_no_mutating_transport_methods(self):
        t = SnapshotGET(self.source)
        for name in ("post_comment", "patch_comment", "patch_title",
                     "patch_issue_body", "patch_pull_title_body", "write", "apply"):
            self.assertFalse(hasattr(t, name), name)

    def test_12_original_graph_has_not_been_reduced_by_shadow(self):
        before = deepcopy(self.source)
        a = self.cycle()
        b = self.cycle()
        self.assertEqual(self.source, before)
        self.assertEqual(a["native_input_digest"], b["native_input_digest"])
        self.assertEqual(a["c6_frontier"]["frontier_digest"], b["c6_frontier"]["frontier_digest"])
        self.assertEqual(a["pr_body_preview"], b["pr_body_preview"])

    def test_13_bad_source_capture_kind_rejected(self):
        self.source["source_kind"] = "SIGNED_AND_APPROVED"
        with self.assertRaisesRegex(CycleHold, "SOURCE_CAPTURE_KIND_UNTRUSTED"):
            self.cycle()

    def test_14_malformed_original_pr_body_rejected(self):
        self.source["pulls"]["10"]["body"] = None
        with self.assertRaisesRegex(CycleHold, "PR_HUMAN_BODY_NOT_OBSERVED"):
            self.cycle()

    def test_15_unchanged_native_frontier_depends_on_live_head(self):
        r = self.cycle()
        native, _ = _native_modules()
        graph = json.loads(self.binary)
        self.assertEqual(r["c6_frontier"]["schema"], native.frontier(
            graph, native.ledger_from_github(SnapshotGET(self.source), graph),
            native.observe_github(SnapshotGET(self.source), graph), self.pin.leaf_ref)["schema"])


if __name__ == "__main__":
    unittest.main()
