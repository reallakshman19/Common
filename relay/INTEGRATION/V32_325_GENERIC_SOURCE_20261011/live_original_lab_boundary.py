"""Physical read-only original public lab probe against unchanged native DELP.

Runs only when explicitly selected in the candidate source-preflight workflow.
No fact issuance, source rewriting, GitHub mutations, reviewer grant or E claim.
This is an EXPECTED native source-boundary failure test until frozen native
AMEND-V32-289-PRREF-017 is independently reviewed/merged/base-resident.
"""
from __future__ import annotations

import base64
import json
import os
import unittest
from urllib.parse import quote
from urllib.request import Request, urlopen

from generic_current_source import SourceHold, reconcile_current_source

REPOSITORY = "reallaksh19/relay-v32-e2e-lab"
REPO_ID = 1411550807
GRAPH_PATH = "governance/released-graph.json"
GRAPH_BLOB = "fde7e1fbd0c71efb64a678206f0bc9f32e36f6c8"
GRAPH_HEAD = "f0dfc590bd3fa53c50c1b645f17faf3f88e2f155"
LEAF = f"{REPOSITORY}#4"
PR_NUMBER = 8
PR_HEAD = "8ced7c13d5e9f9ba6870899ae8c62ec5501011b4"


class PublicGetOnly:
    """GET-only, explicitly repository-scoped, rate-limited public GitHub reader."""

    repository = REPOSITORY

    def __init__(self) -> None:
        self.calls: list[str] = []

    def _get(self, suffix: str):
        # The caller supplies only fixed REST paths. Never accept a redirect to
        # a different repository or invoke write-capable transport methods.
        url = "https://api.github.com/repos/" + REPOSITORY + suffix
        headers = {"Accept": "application/vnd.github+json",
                   "User-Agent": "tab1-v32-original-live-readonly-probe",
                   "X-GitHub-Api-Version": "2022-11-28"}
        token = os.getenv("GH_READONLY_TOKEN", "")
        if token:
            headers["Authorization"] = "Bearer " + token
        request = Request(url, headers=headers, method="GET")
        with urlopen(request, timeout=20) as response:
            self.calls.append(suffix)
            return json.loads(response.read().decode("utf-8"))

    def get_repository(self):
        result = self._get("")
        if (result.get("id") != REPO_ID or
                result.get("full_name") != REPOSITORY or
                result.get("default_branch") != "main" or
                result.get("private") is not False):
            raise AssertionError("ORIGINAL_REPOSITORY_IDENTITY_MOVED")
        return result

    def get_file_bytes(self, path: str, ref: str) -> bytes:
        if path != GRAPH_PATH or ref not in ("main", GRAPH_HEAD):
            raise AssertionError("ORIGINAL_GRAPH_SELECTION_UNBOUND")
        data = self._get("/contents/" + GRAPH_PATH + "?ref=" + quote(ref))
        if data.get("sha") != GRAPH_BLOB or data.get("encoding") != "base64":
            raise AssertionError("ORIGINAL_GRAPH_BLOB_MOVED_OR_UNREADABLE")
        return base64.b64decode(data["content"], validate=False)

    def get_commit_sha(self, ref: str) -> str:
        if ref != "main":
            raise AssertionError("BASE_REF_UNBOUND")
        data = self._get("/git/ref/heads/main")
        sha = (data.get("object") or {}).get("sha")
        if sha != GRAPH_HEAD:
            raise AssertionError("ORIGINAL_HEAD_MOVED")
        return sha

    def get_issue(self, number: int):
        if number not in (1, 4):
            raise AssertionError("ISSUE_NOT_SELECTED")
        return self._get("/issues/" + str(number))

    def get_pull(self, number: int):
        if number not in (8, 13, 15):
            raise AssertionError("PR_NOT_IN_RELEASED_GRAPH")
        return self._get("/pulls/" + str(number))

    def list_comments(self, number: int):
        if number not in (4, 5, 6):
            raise AssertionError("LEAF_NOT_IN_RELEASED_GRAPH")
        rows = self._get("/issues/" + str(number) + "/comments?per_page=100&page=1")
        second = self._get("/issues/" + str(number) + "/comments?per_page=100&page=2")
        if second:
            raise AssertionError("COMMENT_PAGE_OVERFLOW_UNBOUNDED")
        if len(rows) > 100:
            raise AssertionError("COMMENT_PAGE_UNBOUNDED")
        return rows

    def compare(self, base: str, head: str):
        # Original released graph uses PRs, not branch-only leaf candidates.
        raise AssertionError("UNEXPECTED_COMPARE_FOR_PR_BOUND_GRAPH")


@unittest.skipUnless(os.getenv("V32_PUBLIC_LAB_LIVE") == "1",
                     "live original public lab probe is explicitly opt-in")
class OriginalPublicLabNativeSourceBoundary(unittest.TestCase):

    def test_real_released_graph_reaches_expected_native_material_hold(self):
        reader = PublicGetOnly()
        try:
            reconcile_current_source(
                repository=REPOSITORY, graph_path=GRAPH_PATH,
                graph_revision=GRAPH_HEAD, leaf_ref=LEAF,
                pr_number=PR_NUMBER, expected_head=PR_HEAD,
                graph_provider=reader, provider=reader,
            )
        except SourceHold as exc:
            self.assertEqual(str(exc), "NATIVE_RESPONSIBILITY_CORE_MATERIAL_BOUNDARY",
                             "A different source/custody failure must not be called the native PR-ref bug")
        else:
            self.fail("Original full owner/repo#PR unexpectedly passed frozen native core")
        self.assertGreaterEqual(len(reader.calls), 20,
                                "This must run the actual double-read native source path")
        self.assertTrue(all(path == "" or path.startswith((
                            "/issues/", "/pulls/", "/contents/", "/git/ref/"))
                            for path in reader.calls),
                        "Only repository metadata and fixed GitHub REST GETs are permitted")
        # This test is a negative physical characterization, not E>0 or release.

if __name__ == "__main__":
    unittest.main()


# G8 Batch 01. These are real original-provider GET-only tests, not
# CHECKPOINT_FACTS, writer qualification, or an independent successor.
from generic_source_preflight import delp


class WholeGraphPublicGetOnly(PublicGetOnly):
    """Extend only issue GET selection for all six graph-bound titles."""

    def get_issue(self, number: int):
        if number not in (1, 2, 3, 4, 5, 6):
            raise AssertionError("ISSUE_NOT_IN_RELEASED_GRAPH")
        return self._get("/issues/" + str(number))


@unittest.skipUnless(os.getenv("V32_PUBLIC_LAB_LIVE") == "1",
                     "G8 read-only original lab probes require explicit opt-in")
class G8Batch01ActualLabReadOnly(unittest.TestCase):
    """Actual V3.2 source + provider on fixed lab graph/head; zero writes."""

    def _source(self, reader):
        reader.get_repository()
        before = reader.get_commit_sha("main")
        self.assertEqual(before, GRAPH_HEAD, "LAB_MAIN_MOVED")
        pinned = reader.get_file_bytes(GRAPH_PATH, GRAPH_HEAD)
        current = reader.get_file_bytes(GRAPH_PATH, "main")
        self.assertEqual(pinned, current, "RELEASED_GRAPH_MOVED")
        graph = json.loads(pinned.decode("utf-8"))
        self.assertEqual(graph["programme"]["repository"], REPOSITORY)
        self.assertEqual(reader.get_commit_sha("main"), before,
                         "LAB_MAIN_MOVED_AFTER_SOURCE_READ")
        return graph

    def _native(self, reader, graph):
        ledger = delp.ledger_from_github(reader, graph)
        observed = delp.observe_github(reader, graph)
        projection = delp.project(graph, ledger, observed)
        return ledger, observed, projection

    def test_g8_w01_actual_evidence_to_issue_dryrun(self):
        reader = WholeGraphPublicGetOnly()
        graph = self._source(reader)
        ledger, observed, projection = self._native(reader, graph)
        self.assertEqual(ledger, [],
                         "CHECKPOINT_FACT_APPEARED_REQUALIFY_ISSUER_HEAD")
        self.assertEqual(projection["rejected_facts"], [])
        root, leaf = graph["programme"]["root"], LEAF
        self.assertEqual(projection["nodes"][root]["progress"]["E"], 0)
        self.assertEqual(projection["nodes"][leaf]["progress"]["E"], 0)
        dry = delp.plan_github(reader, graph)
        actual = {ref: reader.get_issue(delp.ref_number(ref))["title"]
                  for ref in (root, leaf)}
        expected = {ref: dry["expected_titles"][ref] for ref in (root, leaf)}
        markers = [delp.read_status_marker(row["body"])
                   for row in reader.list_comments(4)]
        markers = [row for row in markers if row is not None]
        self.assertEqual(len(markers), 1, "NATIVE_LIVE_STATUS_MARKER_MISSING")
        self.assertEqual(expected, actual,
                         "ISSUE_TITLE_DRIFT_REQUIRES_EVENT_DIAGNOSIS")
        self.assertEqual(reader.get_commit_sha("main"), GRAPH_HEAD,
                         "LAB_MAIN_MOVED_DURING_PROBE")
        print("G8_W01_ACTUAL_READONLY=" + json.dumps({
            "graph_blob": GRAPH_BLOB, "source_main": GRAPH_HEAD,
            "ledger_records": len(ledger),
            "rejected": len(projection["rejected_facts"]),
            "native_input_digest": projection["input_digest"],
            "root_E": projection["nodes"][root]["progress"]["E"],
            "leaf_E": projection["nodes"][leaf]["progress"]["E"],
            "root_title_equal": expected[root] == actual[root],
            "leaf_title_equal": expected[leaf] == actual[leaf],
            "total_title_drift": dry["would_write_titles"],
            "status_digest": markers[0]["input_digest"],
            "native_status_digest_equal": (
                markers[0]["input_digest"] == projection["input_digest"]),
            "writes": 0,
        }, sort_keys=True))

    def test_g8_w02_merged_pr_actual_native_view_boundary(self):
        reader = WholeGraphPublicGetOnly()
        graph = self._source(reader)
        ledger, observed, projection = self._native(reader, graph)
        actual = reader.get_pull(PR_NUMBER)
        self.assertTrue(actual["merged"], "EXPECTED_REAL_MERGED_PR")
        self.assertEqual(actual["head"]["sha"], PR_HEAD,
                         "LAB_PR_HEAD_MOVED")
        self.assertIn("[DRAFT]", actual["title"],
                      "HUMAN_PR_TITLE_ALREADY_UPDATED_REBASE_ORACLE")
        self.assertEqual(ledger, [], "NEW_FACT_REQUALIFY")
        try:
            delp.source_bound_responsibility_core(graph, projection, LEAF)
        except delp.DelpError as exc:
            self.assertIn("RESPONSIBILITY_CORE_MATERIAL_BOUNDARY", str(exc),
                          "DIFFERENT_NATIVE_CORE_FAILURE")
            failure = "RESPONSIBILITY_CORE_MATERIAL_BOUNDARY"
        else:
            self.fail("NATIVE_FULL_PR_REFERENCE_BOUNDARY_NO_LONGER_PRESENT")
        self.assertEqual(reader.get_commit_sha("main"), GRAPH_HEAD,
                         "LAB_MAIN_MOVED_DURING_PR_PROBE")
        print("G8_W02_ACTUAL_READONLY=" + json.dumps({
            "pr": REPOSITORY + "#8", "merged": actual["merged"],
            "head": actual["head"]["sha"], "live_title": actual["title"],
            "core": failure, "derived_pr_title": "BLOCKED_BY_NATIVE_CORE",
            "publisher": "NONE_VERIFIED_IN_LAB_WORKFLOW", "writes": 0
        }, sort_keys=True))

    def test_g8_w03_github_only_current_frontier_oracle(self):
        reader = WholeGraphPublicGetOnly()
        graph = self._source(reader)
        indexed = delp.validate_graph(graph)
        leaf = indexed["nodes"][LEAF]
        self.assertEqual(leaf["parent"], REPOSITORY + "#2")
        self.assertEqual(leaf["primary_pr"], REPOSITORY + "#8")
        self.assertEqual(leaf["depends_on"], [])
        ledger, observed, projection = self._native(reader, graph)
        self.assertEqual(ledger, [], "NEW_FACT_REQUIRES_AUTHORITY_CHECK")
        entry = delp.admit(projection, LEAF, "continue")
        frontier = delp.frontier(graph, ledger, observed, LEAF)
        actual = reader.get_issue(4)
        native_status = [delp.read_status_marker(row["body"])
                         for row in reader.list_comments(4)]
        native_status = [row for row in native_status if row]
        self.assertEqual(len(native_status), 1)
        self.assertEqual(entry["lineage"],
                         [REPOSITORY + "#1", REPOSITORY + "#2", LEAF])
        self.assertEqual(frontier["observed"]["candidate_sha"], PR_HEAD)
        self.assertEqual(frontier["inputs"]["facts"]["accepted"], 0)
        self.assertEqual(reader.get_commit_sha("main"), GRAPH_HEAD,
                         "LAB_MAIN_MOVED_DURING_ENTRY_ORACLE")
        print("G8_W03_GITHUB_ONLY_ENTRY=" + json.dumps({
            "root": graph["programme"]["root"], "selected_leaf": LEAF,
            "issue_title": actual["title"], "pr": leaf["primary_pr"],
            "pr_head": PR_HEAD, "fact_count": 0,
            "live_status_digest": native_status[0]["input_digest"],
            "frontier_digest": frontier["frontier_digest"],
            "action": entry["action"], "next": entry["next"],
            "authority": "ISSUER_UNSELECTED; NO_WRITER_GRANT",
            "actual_independent_successor": "NOT_RUN",
            "writes": 0,
        }, sort_keys=True))
