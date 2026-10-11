"""T02: current-default-branch graph custody + unchanged native DELP ledger, read-only."""
import copy
import json
import unittest

from test_generic_source_preflight import (
    BASE, HEAD, LEAF, PR_NUM, REPO, ReadOnlyFake, fixture_graph,
)
from generic_source_preflight import SourceHold
from generic_current_source import reconcile_current_source

GRAPH_PATH = ".github/v32-evidence-spine/718-proposal-v2.json"
REVISION = "9" * 40


class FakeGraphSource:
    repository = REPO

    def __init__(self, graph):
        self.blob = json.dumps(graph, sort_keys=True, separators=(",", ":")).encode()
        self.current_blob = self.blob
        self.revision_blob = self.blob
        self.default_branch = "main"
        self.calls = []
        self.current_reads = 0

    def get_repository(self):
        self.calls.append(("GET_REPO",))
        return {"full_name": REPO, "default_branch": self.default_branch}

    def get_file_bytes(self, path, ref):
        self.calls.append(("GET_GRAPH", path, ref))
        if ref == REVISION:
            return self.revision_blob
        if ref == "main":
            self.current_reads += 1
            return self.current_blob
        raise KeyError(ref)


class FakeNativeProvider(ReadOnlyFake):
    def __init__(self):
        super().__init__()
        self.comments = {}
        self.base = BASE
        self.additional_prs = {
            722: "1" * 40, 728: "2" * 40, 800: "3" * 40,
        }

    def get_commit_sha(self, ref):
        self.calls.append(("GET_COMMIT", ref))
        return self.base

    def get_pull(self, number):
        if number == PR_NUM:
            return super().get_pull(number)
        self.calls.append(("GET_PULL", number))
        sha = self.additional_prs[number]
        return {
            "number": number, "state": "open", "merged": False,
            "head": {"sha": sha, "repo": {"full_name": REPO}},
            "base": {"ref": "main", "repo": {"full_name": REPO}},
            "title": "Other candidate", "body": "Other owner",
        }

    def list_comments(self, number):
        self.calls.append(("GET_COMMENTS", number))
        return copy.deepcopy(self.comments.get(number, []))

    def compare(self, base, head):
        self.calls.append(("GET_COMPARE", base, head))
        return {"ahead_by": 0, "behind_by": 0}


class CurrentSourceTests(unittest.TestCase):
    def setUp(self):
        self.graph = fixture_graph()
        self.graph_source = FakeGraphSource(self.graph)
        self.provider = FakeNativeProvider()

    def call(self, **overrides):
        data = dict(repository=REPO, graph_path=GRAPH_PATH,
                    graph_revision=REVISION, leaf_ref=LEAF,
                    pr_number=PR_NUM, expected_head=HEAD,
                    graph_provider=self.graph_source, provider=self.provider)
        data.update(overrides)
        return reconcile_current_source(**data)

    def test_12_double_read_current_graph_reuses_native_ledger_and_core(self):
        result = self.call()
        self.assertEqual(result["status"], "READ_ONLY_RECONCILED_UNATTESTED")
        self.assertEqual(result["native_progress"]["leaf"]["E"], 0)
        self.assertEqual(result["native_ledger"]["accepted"], 0)
        self.assertEqual(result["native_ledger"]["rejected"], 0)
        self.assertEqual(result["native_core"]["leaf"], LEAF)
        self.assertEqual(result["source_custody"]["graph_revision"], REVISION)
        self.assertEqual(result["source_custody"]["current_default_branch"], "main")
        self.assertGreaterEqual(self.graph_source.current_reads, 2)
        self.assertEqual(result["writes"], 0)
        self.assertFalse(result["production_authorized"])
        self.assertFalse(result["source_authenticated"])
        self.assertFalse(result["evidence_admitted"])
        self.assertTrue(all(x[0].startswith("GET_") for x in self.provider.calls))

    def test_13_graph_not_on_default_branch_holds_before_provider(self):
        self.graph_source.current_blob = b'{"schema":"unreleased"}'
        with self.assertRaisesRegex(SourceHold, "^SOURCE_GRAPH_NOT_CURRENT_RELEASED$"):
            self.call()
        self.assertEqual(self.provider.calls, [])

    def test_14_immutable_graph_must_match_released_graph(self):
        self.graph_source.revision_blob = b'{"schema":"stale"}'
        with self.assertRaisesRegex(SourceHold, "^SOURCE_GRAPH_REVISION_MISMATCH$"):
            self.call()
        self.assertEqual(self.provider.calls, [])

    def test_15_default_branch_graph_moves_after_first_custody_read(self):
        original = self.graph_source.get_file_bytes
        count = [0]
        def moved(path, ref):
            data = original(path, ref)
            if ref == "main":
                count[0] += 1
                if count[0] > 1:
                    return b'{"schema":"changed"}'
            return data
        self.graph_source.get_file_bytes = moved
        with self.assertRaisesRegex(SourceHold, "^SOURCE_GRAPH_MOVED_DURING_READ$"):
            self.call()

    def test_16_repository_metadata_mismatch_holds(self):
        self.graph_source.get_repository = lambda: {
            "full_name": "foreign/Pipeline", "default_branch": "main"
        }
        with self.assertRaisesRegex(SourceHold, "^GRAPH_REPOSITORY_MISMATCH$"):
            self.call()
        self.assertEqual(self.provider.calls, [])

    def test_17_wrong_graph_revision_is_held_before_reads(self):
        with self.assertRaisesRegex(SourceHold, "^SOURCE_GRAPH_REVISION_INVALID$"):
            self.call(graph_revision="latest")
        self.assertEqual(self.graph_source.calls, [])

    def test_18_untrusted_comment_is_rejected_by_native_delp(self):
        self.provider.comments[733] = [{
            "id": 51, "user": {"login": "stranger"},
            "author_association": "NONE",
            "body": "```yaml\nCHECKPOINT_FACTS_V1:\n"
                    "  responsibility: {issue: Pipeline#733, id: R-PROJECTION}\n"
                    f"  material: {{pr: Pipeline#740, candidate_sha: {HEAD}}}\n"
                    "  units:\n"
                    "    - {id: VIEW-PR, state: COMPLETE, result: VERIFIED, evidence_refs: [Pipeline#733#issuecomment-51]}\n"
                    "```",
        }]
        outcome = self.call()
        self.assertEqual(outcome["native_ledger"]["accepted"], 0)
        self.assertEqual(outcome["native_ledger"]["rejected"], 1)
        self.assertEqual(outcome["native_progress"]["leaf"]["E"], 0)

    def test_19_native_fact_ledger_change_across_reads_holds(self):
        original = self.provider.list_comments
        counter = [0]
        def changed(number):
            counter[0] += 1
            rows = original(number)
            if counter[0] > 4 and number == 733:
                rows.append({"id": 1, "body": "new material"})
            return rows
        self.provider.list_comments = changed
        with self.assertRaisesRegex(SourceHold, "^NATIVE_LEDGER_OR_OBSERVATION_MOVED$"):
            self.call()

    def test_20_native_full_owner_repo_pr_ref_is_not_rewritten_to_short_ref(self):
        self.graph["nodes"] = [
            {**item, "primary_pr": "example/Pipeline#740"}
            if item.get("ref") == LEAF else item
            for item in self.graph["nodes"]
        ]
        self.graph_source = FakeGraphSource(self.graph)
        with self.assertRaisesRegex(
            SourceHold, "^NATIVE_RESPONSIBILITY_CORE_MATERIAL_BOUNDARY$"
        ):
            self.call()

    def test_21_source_and_native_remain_readonly_even_with_merged_pr(self):
        self.provider.pull["merged"] = True
        self.provider.pull["state"] = "closed"
        result = self.call()
        self.assertEqual(result["pr_state"], "MERGED")
        self.assertFalse(result["automatic_successor"])
        self.assertFalse(result["production_authorized"])
        self.assertEqual(result["writes"], 0)


if __name__ == "__main__":
    unittest.main()
