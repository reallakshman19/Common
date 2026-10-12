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
        self.assertTrue(all(path.startswith(("/issues/", "/pulls/", "/contents/", "/git/ref/",
                                             "")) for path in reader.calls))
        # This test is a negative physical characterization, not E>0 or release.

if __name__ == "__main__":
    unittest.main()
