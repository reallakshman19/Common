"""Source-owned tests for V3.2 generic *read-only* graph/provider preflight.

Uses the shipped native released Proposal-V2 graph and genuine native DELP
functions; all GitHub provider calls below are deliberately synthetic.
"""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills/engineering-pr-delivery-v3.2/scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import delp_projection_v32 as delp
from generic_source_preflight import SourceHold, preflight

GRAPH_PATH = ROOT / ".github/v32-evidence-spine/718-proposal-v2.json"
REPO = "example/Pipeline"
LEAF = "Pipeline#733"
ROOT_REF = "Pipeline#718"
PR_NUM = 740
BASE = "a" * 40
HEAD = "b" * 40


def _replace_graph_names(value):
    if isinstance(value, str):
        return value.replace("reallaksh19/Common", REPO).replace("Common#", "Pipeline#")
    if isinstance(value, list):
        return [_replace_graph_names(item) for item in value]
    if isinstance(value, dict):
        return {key: _replace_graph_names(item) for key, item in value.items()}
    return value


def fixture_graph():
    return _replace_graph_names(json.loads(GRAPH_PATH.read_text(encoding="utf-8")))


class ReadOnlyFake:
    repository = REPO

    def __init__(self):
        self.calls = []
        self.heads = [HEAD]
        self.issues = {
            718: {"number": 718, "state": "open", "title": "Root", "body": "Owner context"},
            733: {"number": 733, "state": "open", "title": "Leaf", "body": "Source evidence"},
        }
        self.pull = {
            "number": PR_NUM, "state": "open", "merged": False, "draft": True,
            "head": {"sha": HEAD, "repo": {"full_name": REPO}},
            "base": {"ref": "main", "repo": {"full_name": REPO}},
            "title": "Candidate", "body": "Human PR description",
        }
        self.pull_reads = 0

    def get_issue(self, number):
        self.calls.append(("GET_ISSUE", number))
        return copy.deepcopy(self.issues[number])

    def get_pull(self, number):
        self.calls.append(("GET_PULL", number))
        self.pull_reads += 1
        result = copy.deepcopy(self.pull)
        result["head"]["sha"] = self.heads[min(self.pull_reads - 1, len(self.heads) - 1)]
        return result

    def get_commit_sha(self, ref):
        self.calls.append(("GET_COMMIT", ref))
        return BASE


class GenericSourceTest(unittest.TestCase):
    def setUp(self):
        self.graph = fixture_graph()
        self.provider = ReadOnlyFake()

    def run_preflight(self, **kwargs):
        args = {
            "graph": self.graph, "repository": REPO,
            "leaf_ref": LEAF, "pr_number": PR_NUM,
            "expected_head": HEAD, "provider": self.provider,
        }
        args.update(kwargs)
        return preflight(**args)

    def test_01_native_original_graph_is_valid_after_noncommon_rebinding(self):
        indexed = delp.validate_graph(self.graph)
        self.assertEqual(indexed["programme"]["repository"], REPO)
        self.assertIn(LEAF, indexed["nodes"])
        self.assertEqual(indexed["nodes"][LEAF]["primary_pr"], "Pipeline#740")

    def test_02_readonly_generic_repository_returns_native_delp_zero_progress(self):
        out = self.run_preflight()
        self.assertEqual(out["status"], "READ_ONLY_SOURCE_OBSERVED_UNATTESTED")
        self.assertEqual(out["identity"], {"repository": REPO, "root": ROOT_REF,
                                           "leaf": LEAF, "pr": "Pipeline#740"})
        self.assertEqual(out["candidate_sha"], HEAD)
        self.assertEqual(out["native_progress"]["leaf"]["E"], 0)
        self.assertEqual(out["writes"], 0)
        self.assertFalse(out["source_authenticated"])
        self.assertFalse(out["evidence_admitted"])
        self.assertFalse(out["production_authorized"])
        self.assertEqual(self.provider.pull_reads, 2)
        self.assertTrue(all(call[0].startswith("GET_") for call in self.provider.calls))

    def test_03_other_repository_selection_refused_before_provider_reads(self):
        with self.assertRaisesRegex(SourceHold, "^REPOSITORY_SELECTION_MISMATCH$"):
            self.run_preflight(repository="attacker/Pipeline")
        self.assertEqual(self.provider.calls, [])

    def test_04_unbound_leaf_and_wrong_pr_refused_before_provider_reads(self):
        for opts, code in [
            ({"leaf_ref": "Pipeline#99999"}, "LEAF_NOT_GRAPH_BOUND"),
            ({"pr_number": 800}, "PRIMARY_PR_NOT_GRAPH_BOUND"),
        ]:
            with self.subTest(opts=opts):
                with self.assertRaisesRegex(SourceHold, "^" + code + "$"):
                    self.run_preflight(**opts)
                self.assertEqual(self.provider.calls, [])

    def test_05_foreign_provider_head_repository_is_not_source(self):
        self.provider.pull["head"]["repo"]["full_name"] = "foreign/Pipeline"
        with self.assertRaisesRegex(SourceHold, "^PROVIDER_HEAD_REPOSITORY_MISMATCH$"):
            self.run_preflight()

    def test_06_head_movement_between_provider_reads_holds(self):
        self.provider.heads = [HEAD, "c" * 40]
        with self.assertRaisesRegex(SourceHold, "^PROVIDER_MOVED_DURING_READ$"):
            self.run_preflight()

    def test_07_selected_candidate_sha_must_match_actual_provider(self):
        with self.assertRaisesRegex(SourceHold, "^CANDIDATE_HEAD_MISMATCH$"):
            self.run_preflight(expected_head="d" * 40)

    def test_08_wrong_provider_base_ref_is_rejected(self):
        self.provider.pull["base"]["ref"] = "feature"
        with self.assertRaisesRegex(SourceHold, "^PROVIDER_BASE_REF_MISMATCH$"):
            self.run_preflight()

    def test_09_changed_issue_body_between_reads_holds(self):
        original = self.provider.get_issue
        count = [0]

        def changing(number):
            x = original(number)
            count[0] += 1
            if number == 733 and count[0] > 2:
                x["body"] = "changed during read"
            return x

        self.provider.get_issue = changing
        with self.assertRaisesRegex(SourceHold, "^PROVIDER_MOVED_DURING_READ$"):
            self.run_preflight()

    def test_10_wrong_graph_repository_refuses_even_matching_basename(self):
        self.graph["programme"]["repository"] = "foreign/Pipeline"
        with self.assertRaisesRegex(SourceHold, "^REPOSITORY_SELECTION_MISMATCH$"):
            self.run_preflight()

    def test_11_no_authority_even_if_pr_is_merged(self):
        self.provider.pull["merged"] = True
        self.provider.pull["state"] = "closed"
        out = self.run_preflight()
        self.assertEqual(out["pr_state"], "MERGED")
        self.assertFalse(out["production_authorized"])
        self.assertEqual(out["writes"], 0)


if __name__ == "__main__":
    unittest.main()
