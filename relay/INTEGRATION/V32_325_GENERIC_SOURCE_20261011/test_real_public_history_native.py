"""Optional physical GET-only historical-public replay into unchanged native DELP.

Uses real, unaltered public reallaksh19/Common REST source when the CI job opts
in. Never uses the owner's inaccessible private lab or publishes/mutates anything.
No synthetic fallback: API errors, graph drift and missing facts fail closed.
"""
from __future__ import annotations

from base64 import b64decode, b64encode
from hashlib import sha1
import json
import os
from pathlib import Path
import sys
import unittest
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from rest_readonly_provider import BoundNativeReadOnlyGitHubProvider
from generic_current_source import reconcile_current_source

REPO = "reallaksh19/Common"
REPO_ID = 1207996454
MAIN = "d60c36605e988dcc160647421973f170fd87e0eb"
GRAPH_PATH = ".github/v32-evidence-spine/718-proposal-v2.json"
GRAPH_BLOB = "d35019b416cb3b573280e166027d3f65ba61f59c"
LEAF = "Common#733"
PR = 740
HEAD = "d511fc0210ee823272f41c43621bc90bc290e739"


class HistoricalSourceHold(RuntimeError):
    """A safe error without public/private bodies, credentials or response text."""


def hold(condition, code):
    if not condition:
        raise HistoricalSourceHold(code)


def git_blob(data):
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


class PublicHistoricalGET:
    """Test-local real REST transport. Does not become a production adapter."""

    repository = REPO

    def __init__(self):
        self.calls = []
        self.page_counts = []
        self.graph_reads = 0
        self.headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "tab1-g6-r6-public-readonly-candidate",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        token = os.environ.get("GITHUB_TOKEN", "")
        hold(bool(token), "PUBLIC_READONLY_TOKEN_UNAVAILABLE")
        self.headers["Authorization"] = "Bearer " + token

    def get(self, path):
        # Absolute endpoints and redirects are forbidden: GitHub REST only.
        hold(isinstance(path, str) and path.startswith("repos/" + REPO + "/")
             or path == "repos/" + REPO, "PUBLIC_ENDPOINT_UNBOUND")
        req = Request("https://api.github.com/" + path, headers=self.headers,
                      method="GET")
        try:
            with urlopen(req, timeout=25) as response:
                hold(response.status == 200, "PUBLIC_GET_UNAVAILABLE")
                raw = response.read(5_000_001)
                hold(len(raw) <= 5_000_000, "PUBLIC_GET_RESPONSE_UNBOUNDED")
        except (HTTPError, URLError, OSError, TimeoutError) as exc:
            # Do not interpolate exception text: may contain provider URL.
            raise HistoricalSourceHold("PUBLIC_GET_UNAVAILABLE") from None
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeError, ValueError, TypeError):
            raise HistoricalSourceHold("PUBLIC_GET_JSON_INVALID") from None
        self.calls.append(path)
        return value

    def get_repository(self):
        row = self.get("repos/" + REPO)
        hold(row.get("full_name") == REPO and type(row.get("id")) is int
             and row["id"] == REPO_ID and row.get("default_branch") == "main",
             "PUBLIC_REPOSITORY_IDENTITY_MISMATCH")
        return row

    def get_file_bytes(self, path, ref):
        hold(path == GRAPH_PATH and ref in ("main", MAIN),
             "PUBLIC_GRAPH_PATH_OR_REVISION_UNBOUND")
        query = quote(ref, safe="")
        row = self.get("repos/" + REPO + "/contents/" + path + "?ref=" + query)
        hold(row.get("type") == "file" and row.get("encoding") == "base64"
             and row.get("sha") == GRAPH_BLOB
             and isinstance(row.get("content"), str),
             "PUBLIC_GRAPH_BLOB_MISMATCH")
        try:
            encoded = "".join(row["content"].split())
            raw = b64decode(encoded, validate=True)
            hold(b64encode(raw).decode() == encoded, "PUBLIC_GRAPH_B64_INVALID")
        except (ValueError, TypeError):
            raise HistoricalSourceHold("PUBLIC_GRAPH_B64_INVALID") from None
        hold(git_blob(raw) == GRAPH_BLOB, "PUBLIC_GRAPH_RAW_BLOB_MISMATCH")
        self.graph_reads += 1
        return raw

    def get_commit_sha(self, ref):
        hold(ref == "main", "PUBLIC_COMMIT_REF_UNBOUND")
        row = self.get("repos/" + REPO + "/commits/main")
        hold(isinstance(row, dict) and row.get("sha") == MAIN,
             "PUBLIC_CURRENT_MAIN_MOVED")
        return row["sha"]

    def get_issue(self, number):
        return self.get("repos/" + REPO + "/issues/" + str(number))

    def get_pull(self, number):
        return self.get("repos/" + REPO + "/pulls/" + str(number))

    def list_comments(self, number):
        # Actual REST GitHub pagination; never truncate a full page to pretend
        # complete original-source material. Each native pass invokes GETs.
        rows = []
        for page in range(1, 12):
            path = ("repos/" + REPO + "/issues/" + str(number)
                    + "/comments?per_page=100&page=" + str(page))
            batch = self.get(path)
            hold(isinstance(batch, list) and len(batch) <= 100,
                 "PUBLIC_COMMENT_PAGE_INVALID")
            rows.extend(batch)
            hold(len(rows) <= 1000, "PUBLIC_COMMENTS_TOO_MANY")
            if len(batch) < 100:
                self.page_counts.append((number, len(rows)))
                return rows
        raise HistoricalSourceHold("PUBLIC_COMMENT_PAGINATION_INCOMPLETE")

    def compare(self, base, head):
        hold(base == "main" and head.startswith("refs/"),
             "PUBLIC_COMPARE_UNBOUND")
        return self.get("repos/" + REPO + "/compare/"
                        + quote(base, safe="") + "..." + quote(head, safe=""))


@unittest.skipUnless(os.environ.get("V32_PUBLIC_HISTORY_GET") == "1",
                     "public historical GET intentionally opt-in, not synthetic")
class ActualPublicHistory(unittest.TestCase):
    def test_01_native_full_readonly_current_public_history(self):
        rest = PublicHistoricalGET()
        provider = BoundNativeReadOnlyGitHubProvider(
            repository=REPO, base_ref="main",
            read_issue=rest.get_issue,
            read_pull=rest.get_pull,
            read_commit_sha=rest.get_commit_sha,
            read_comments=rest.list_comments,
            read_compare=rest.compare,
        )
        actual = reconcile_current_source(
            repository=REPO, graph_path=GRAPH_PATH, graph_revision=MAIN,
            leaf_ref=LEAF, pr_number=PR, expected_head=HEAD,
            graph_provider=rest, provider=provider,
        )
        self.assertEqual(actual["status"], "READ_ONLY_RECONCILED_UNATTESTED")
        self.assertEqual(actual["identity"]["repository"], REPO)
        self.assertEqual(actual["candidate_sha"], HEAD)
        self.assertEqual(actual["native_ledger"]["total"], 0)
        self.assertEqual(actual["native_ledger"]["accepted"], 0)
        self.assertEqual(actual["native_ledger"]["rejected"], 0)
        self.assertEqual(actual["native_progress"]["leaf"]["E"], 0)
        self.assertFalse(actual["source_authenticated"])
        self.assertFalse(actual["production_authorized"])
        self.assertFalse(actual["evidence_admitted"])
        self.assertFalse(actual["automatic_successor"])
        self.assertEqual(actual["writes"], 0)
        self.assertGreaterEqual(rest.graph_reads, 4)
        # Four declared leaves each observed twice by real GET.
        for number, expected in ((720, 7), (724, 8), (733, 20), (793, 15)):
            self.assertEqual(rest.page_counts.count((number, expected)), 2)
        print("PUBLIC_HISTORY_NATIVE_ACTUAL_GET_PASS: graph=old-public"
              " comments=50 fact_blocks=0 native_E=0 writer=0"
              " original_owner_authorized=false")


if __name__ == "__main__":
    unittest.main()
