"""Regression tests for read-only GitHub response envelopes.

The fixture's issue numbers and PR identity derive from actual public
GitHub connected GET observations made on 2026-10-11 (Common #5/#325/#326).
Issue/PR bodies are intentionally substituted; this is a SANITIZED REPLAY,
NOT an authenticated live run or released Owner graph. A fresh live GET
was performed separately by the coordinating agent; these tests make
its provider SHAPE portable and fail closed on material identity drift.
"""
from __future__ import annotations

import ast
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from generic_source_preflight import SourceHold, _read_source
from rest_readonly_provider import BoundReadOnlyGitHubProvider, RestContractHold

REPO = "reallakshman19/Common"
ROOT_NUM, LEAF_NUM, PR_NUM = 5, 325, 326
PINNED_PR_HEAD = "82b45eb0a947ffde8931448989c6e6b002c042fb"
OBSERVED_MAIN_HEAD = "32f4e3b4b64c45c23d7ddc97e47928f5ff4f541e"
PR_BASE_AT_OBSERVATION = "27fd8afbe76b45546e4512b252e1ea15045567f0"


class ObservedEnvelopeFixture:
    def __init__(self):
        self.reads = []
        self.base_sha = OBSERVED_MAIN_HEAD
        self.issue = {
            ROOT_NUM: {"number": ROOT_NUM, "state": "open",
                       "title": "[V3.5][RECOVERY PARENT] Common repo cutover + R14/Runner reconciliation → one DELP → live lifecycle | AC0/8",
                       "body": "[sanitized Owner text]"},
            LEAF_NUM: {"number": LEAF_NUM, "state": "open",
                       "title": "[V3.2][#289 child] Generic graph-bound source integration → native DELP → governed GitHub + C6",
                       "body": "[sanitized issue text]"},
        }
        # Connector's flattened metadata from GET /repos/{repo}/pulls/326.
        self.pull = {
            "number": PR_NUM, "state": "open", "merged": False, "draft": True,
            "title": "[V3.2][#325 T01] Generic released-graph read-only provider + native DELP preflight",
            "body": "[sanitized PR text]",
            "head_sha": PINNED_PR_HEAD,
            "head_repo_full_name": REPO,
            "base": "main", "base_sha": PR_BASE_AT_OBSERVATION,
        }

    def read_issue(self, number):
        self.reads.append(("GET_ISSUE", number))
        return {"issue": copy.deepcopy(self.issue[number])}

    def read_pull(self, number):
        self.reads.append(("GET_PR", number))
        return {"pull_request": copy.deepcopy(self.pull)}

    def read_commit_sha(self, ref):
        self.reads.append(("GET_COMMIT", ref))
        return self.base_sha

    def provider(self, repository=REPO):
        return BoundReadOnlyGitHubProvider(
            repository=repository, base_ref="main",
            read_issue=self.read_issue, read_pull=self.read_pull,
            read_commit_sha=self.read_commit_sha,
        )


class RestReadOnlyContractTests(unittest.TestCase):
    def setUp(self):
        self.fixture = ObservedEnvelopeFixture()
        self.provider = self.fixture.provider()

    def read(self, **overrides):
        args = dict(
            provider=self.provider, repository=REPO,
            root_num=ROOT_NUM, leaf_num=LEAF_NUM,
            pr_number=PR_NUM, base_ref="main", expected_head=PINNED_PR_HEAD,
        )
        args.update(overrides)
        return _read_source(**args)

    def test_observed_public_get_envelope_normalizes_without_writer(self):
        result = self.read()
        self.assertEqual(result["base_sha"], OBSERVED_MAIN_HEAD)
        self.assertEqual(result["pull"]["head_sha"], PINNED_PR_HEAD)
        self.assertEqual(result["pull"]["number"], PR_NUM)
        self.assertEqual(result["issues"][LEAF_NUM]["number"], LEAF_NUM)
        self.assertEqual([kind for kind, _ in self.fixture.reads],
                         ["GET_COMMIT", "GET_ISSUE", "GET_ISSUE", "GET_PR"])
        self.assertNotIn("evidence_admitted", result)
        self.assertNotIn("production_authorized", result)

    def test_flattened_foreign_head_is_refused(self):
        self.fixture.pull["head_repo_full_name"] = "other/Common"
        with self.assertRaisesRegex(RestContractHold, "REST_HEAD_REPOSITORY_MISMATCH"):
            self.provider.get_pull(PR_NUM)

    def test_flattened_missing_head_repository_is_refused(self):
        del self.fixture.pull["head_repo_full_name"]
        with self.assertRaisesRegex(RestContractHold, "REST_HEAD_REPOSITORY_MISMATCH"):
            self.provider.get_pull(PR_NUM)

    def test_stale_selected_candidate_is_refused_by_t01(self):
        with self.assertRaisesRegex(SourceHold, "^CANDIDATE_HEAD_MISMATCH$"):
            self.read(expected_head="f" * 40)

    def test_base_ref_drift_is_refused(self):
        self.fixture.pull["base"] = "staging"
        with self.assertRaisesRegex(RestContractHold, "REST_BASE_REF_MISMATCH"):
            self.provider.get_pull(PR_NUM)

    def test_invalid_issue_number_is_refused(self):
        self.fixture.issue[LEAF_NUM]["number"] = 9999
        with self.assertRaisesRegex(RestContractHold, "REST_ISSUE_IDENTITY_MISMATCH"):
            self.provider.get_issue(LEAF_NUM)

    def test_invalid_base_sha_is_refused(self):
        self.fixture.pull["base_sha"] = "0"
        with self.assertRaisesRegex(RestContractHold, "REST_PR_BASE_SHA_INVALID"):
            self.provider.get_pull(PR_NUM)

    def test_unbound_endpoint_repository_cannot_be_normalized_as_expected_repo(self):
        self.provider = self.fixture.provider(repository="elsewhere/Common")
        with self.assertRaisesRegex(SourceHold, "^PROVIDER_HEAD_REPOSITORY_MISMATCH$"):
            self.read()

    def test_nested_github_rest_pr_shape_supported_with_strict_base_repo_check(self):
        source = copy.deepcopy(self.fixture.pull)
        source["head"] = {"sha": PINNED_PR_HEAD, "repo": {"full_name": REPO}}
        source["base"] = {"ref": "main", "sha": PR_BASE_AT_OBSERVATION,
                          "repo": {"full_name": REPO}}
        self.fixture.pull = source
        self.assertEqual(self.read()["pull"]["head_sha"], PINNED_PR_HEAD)
        self.fixture.pull["base"]["repo"]["full_name"] = "foreign/Common"
        with self.assertRaisesRegex(RestContractHold, "REST_BASE_REPOSITORY_MISMATCH"):
            self.provider.get_pull(PR_NUM)

    def test_read_contract_adapter_has_no_network_or_mutation_implementation(self):
        path = Path(__file__).resolve().parent / "rest_readonly_provider.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        banned_imports = {"subprocess", "requests", "urllib", "httpx", "socket", "aiohttp"}
        banned_calls = {"patch", "post", "put", "delete", "urlopen", "request", "system", "popen"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                self.assertFalse(any(alias.name.split(".")[0] in banned_imports
                                     for alias in node.names))
            if isinstance(node, ast.ImportFrom):
                self.assertNotIn((node.module or "").split(".")[0], banned_imports)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr.lower(), banned_calls)


if __name__ == "__main__":
    unittest.main()
