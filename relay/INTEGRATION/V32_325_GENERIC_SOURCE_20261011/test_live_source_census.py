"""Tests for real GET-only census shape and fail-closed source/currentness.

CI separately executes the actual GitHub GET census; this fake reader tests
only the boundaries, not Owner authenticity or the external provider.
"""
from __future__ import annotations
import ast
import base64
import copy
import json
import urllib.error
import unittest
from pathlib import Path
from live_source_census import (
    CURRENT_REPO, OLD_REPO, GRAPH_PATH, LiveCensusHold,
    census, _git_blob_sha, ReadOnlyGitHub,
)

HEAD = "1" * 40


class FakeReader:
    def __init__(self):
        self.calls = []
        self.graph = {"programme": {"repository": OLD_REPO, "root": "Common#718"}}
        self.move_after_first_read = False
        self.edit_issue_after_first_read = False
        self.head_reads = 0
        self.issue_reads = {5: 0}

    def get(self, path):
        self.calls.append(path)
        if path == f"/repos/{CURRENT_REPO}":
            return {"full_name": CURRENT_REPO, "id": 1412133785, "default_branch": "main"}
        if path == f"/repos/{OLD_REPO}":
            return {"full_name": OLD_REPO, "id": 1207996454, "default_branch": "main"}
        if path == f"/repos/{CURRENT_REPO}/branches/main":
            self.head_reads += 1
            return {"commit": {"sha": "2" * 40 if
                                self.move_after_first_read and self.head_reads > 1
                                else HEAD}}
        for number in (5, 289, 325):
            if path == f"/repos/{CURRENT_REPO}/issues/{number}":
                if number == 5:
                    self.issue_reads[5] += 1
                return {"number": number, "state": "open",
                        "html_url": f"https://github.com/{CURRENT_REPO}/issues/{number}",
                        "body": "edited" if number == 5 and self.edit_issue_after_first_read
                                and self.issue_reads[5] > 1 else "Public issue mirror"}
        if path == f"/repos/{OLD_REPO}/issues/787":
            return {"number": 787, "state": "open",
                    "html_url": f"https://github.com/{OLD_REPO}/issues/787",
                    "body": "Historical public Owner quote (mirror, not original chat)"}
        if path == f"/repos/{CURRENT_REPO}/pulls/326":
            return {"number": 326, "state": "open", "draft": True,
                    "html_url": f"https://github.com/{CURRENT_REPO}/pull/326",
                    "head": {"sha": "b" * 40, "repo": {"full_name": CURRENT_REPO}},
                    "base": {"ref": "main", "repo": {"full_name": CURRENT_REPO}}}
        if path.startswith(f"/repos/{CURRENT_REPO}/contents/{GRAPH_PATH}?ref="):
            data = json.dumps(self.graph, sort_keys=True).encode()
            return {"path": GRAPH_PATH, "encoding": "base64",
                    "sha": _git_blob_sha(data),
                    "content": base64.b64encode(data).decode()}
        if path.endswith("/branches/main/protection") or path == "/repos/reallaksh19/relay-v32-e2e-lab":
            raise urllib.error.HTTPError("https://api.github.com" + path, 403,
                                         "Resource not accessible", None, None)
        raise AssertionError("Unexpected API path: " + path)


class LiveCensusContractTests(unittest.TestCase):
    def test_real_source_census_reports_observations_not_authority(self):
        result = census(FakeReader())
        self.assertTrue(result["checks_pass"])
        self.assertEqual(result["current_repository"]["stable_id"], 1412133785)
        self.assertEqual(result["historical_repository"]["stable_id"], 1207996454)
        self.assertTrue(result["known_graph_is_historical"])
        self.assertEqual(result["original_lab_access_probe"], "UNAVAILABLE_HTTP_403")
        self.assertEqual(result["branch_protection_probe"], "UNAVAILABLE_HTTP_403")
        self.assertFalse(result["owner_source_authenticated"])
        self.assertFalse(result["production_authorized"])
        self.assertEqual(result["writes"], 0)
        self.assertTrue(all(str(x).startswith("HOLD_") for x in result["gates"].values()))

    def test_moving_branch_fails_closed(self):
        provider = FakeReader()
        provider.move_after_first_read = True
        with self.assertRaisesRegex(LiveCensusHold, "LIVE_OBSERVATIONS_MOVED_DURING_READ"):
            census(provider)

    def test_issue_content_change_during_reads_fails_closed(self):
        provider = FakeReader()
        provider.edit_issue_after_first_read = True
        with self.assertRaisesRegex(LiveCensusHold, "LIVE_OBSERVATIONS_MOVED_DURING_READ"):
            census(provider)

    def test_historical_graph_not_rebranded_by_name(self):
        provider = FakeReader()
        provider.graph["programme"]["repository"] = CURRENT_REPO
        result = census(provider)
        self.assertFalse(result["known_graph_is_historical"])
        # Still not Owner adopted; program cannot grant authority even if a
        # json field has been trivially replaced.
        self.assertFalse(result["owner_source_authenticated"])
        self.assertFalse(result["known_graph"]["owner_adopted_current_repo"])

    def test_wrong_public_repo_identity_fails(self):
        provider = FakeReader()
        original = provider.get
        def wrong(path):
            val = original(path)
            if path == f"/repos/{CURRENT_REPO}":
                val["id"] = 1207996454
            return val
        provider.get = wrong
        with self.assertRaisesRegex(LiveCensusHold, "REPOSITORY_STABLE_IDENTITY_MISMATCH"):
            census(provider)

    def test_graph_blob_digest_mismatch_fails(self):
        provider = FakeReader()
        original = provider.get
        def altered(path):
            val = original(path)
            if "/contents/" in path:
                val["sha"] = "0" * 40
            return val
        provider.get = altered
        with self.assertRaisesRegex(LiveCensusHold, "GRAPH_BLOB_INTEGRITY_MISMATCH"):
            census(provider)

    def test_script_network_transport_is_get_only(self):
        src = Path(__file__).with_name("live_source_census.py")
        tree = ast.parse(src.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr.lower(), {"patch", "post", "put", "delete",
                                                             "system", "popen", "write"})
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Request":
                self.assertFalse(True, "Unexpected unqualified Request transport")
        self.assertIn("method=\"GET\"", src.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
