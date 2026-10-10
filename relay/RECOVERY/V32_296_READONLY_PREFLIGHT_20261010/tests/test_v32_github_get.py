"""GET-only transport contract tested without credentials or external network."""
from __future__ import annotations

from base64 import b64encode
from json import dumps
from pathlib import Path
from subprocess import CompletedProcess
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from v32_github_get import GitHubGetOnly, GitHubReadError

REPO = "lab/v32-proto"
HEAD = "1" * 40


class Runner:
    def __init__(self, responses):
        self.responses = list(responses)
        self.commands = []

    def __call__(self, argv, **kwargs):
        self.commands.append((argv, kwargs))
        return CompletedProcess(argv, 0, dumps(self.responses.pop(0)))


class ReadOnlyGetTests(unittest.TestCase):
    def test_01_repo_get_always_get(self):
        stub = Runner([{"full_name": REPO, "id": 123}]); g = GitHubGetOnly(stub)
        self.assertEqual(g.get_repository(REPO)["id"], 123)
        self.assertEqual(stub.commands[0][0], ["gh", "api", "--method", "GET", "repos/" + REPO])

    def test_02_full_graph_read_is_pinned_to_sha(self):
        raw = b'{"programme":{"repository":"lab/v32-proto"}}'
        stub = Runner([{"type":"file", "encoding":"base64", "content": b64encode(raw).decode()}])
        self.assertEqual(GitHubGetOnly(stub).get_file_bytes(REPO, "governance/released-graph.json", HEAD), raw)
        self.assertIn("?ref=" + HEAD, stub.commands[0][0][-1])

    def test_03_reject_unpinned_graph_fetch(self):
        stub = Runner([])
        with self.assertRaisesRegex(GitHubReadError, "UNPINNED_GRAPH_COMMIT"):
            GitHubGetOnly(stub).get_file_bytes(REPO, "graph.json", "main")
        self.assertEqual(stub.commands, [])

    def test_04_invalid_repo_selector_no_transport(self):
        stub = Runner([])
        with self.assertRaisesRegex(GitHubReadError, "INVALID_REPOSITORY_SELECTOR"):
            GitHubGetOnly(stub).get_repository("bad/repo/extra")
        self.assertEqual(stub.commands, [])

    def test_05_list_comments_one_page(self):
        stub = Runner([[{"id": 1, "body": "record"}]])
        out = GitHubGetOnly(stub).get_issue_comments(REPO, 4)
        self.assertEqual(out[0]["id"], 1)
        self.assertIn("?per_page=100&page=1", stub.commands[0][0][-1])

    def test_06_list_comments_pagination(self):
        stub = Runner([[{"id": i, "body":"x"} for i in range(100)], [{"id": 100, "body":"z"}]])
        self.assertEqual(len(GitHubGetOnly(stub).get_issue_comments(REPO, 4)), 101)
        self.assertEqual(len(stub.commands), 2)

    def test_07_selected_check_projection_not_required_policy(self):
        stub = Runner([{"total_count":1,"check_runs":[{"name":"build", "head_sha":HEAD,"status":"completed","conclusion":"success"}]}])
        rows = GitHubGetOnly(stub).get_check_runs(REPO, HEAD)
        self.assertEqual(rows, [{"name":"build","head_sha":HEAD,"status":"completed","conclusion":"success"}])
        self.assertNotIn("required", rows[0])

    def test_08_transport_error_fails_closed_without_secret_stderr(self):
        class ErrorRunner:
            def __call__(self, argv, **kwargs):
                return CompletedProcess(argv, 1, "", "secret token must never echo")
        with self.assertRaisesRegex(GitHubReadError, "GITHUB_GET_FAILED") as ctx:
            GitHubGetOnly(ErrorRunner()).get_repository(REPO)
        self.assertNotIn("secret", str(ctx.exception))

    def test_09_reject_wrong_graph_encoding(self):
        stub = Runner([{"type": "file", "encoding": "utf-8", "content": "foo"}])
        with self.assertRaisesRegex(GitHubReadError, "GRAPH_RESPONSE_NOT_CONTENT_FILE"):
            GitHubGetOnly(stub).get_file_bytes(REPO, "graph.json", HEAD)

    def test_10_no_write_verbs_anywhere_in_client(self):
        stub = Runner([{"full_name": REPO}, {"sha": HEAD}, {"number": 10}])
        g = GitHubGetOnly(stub)
        g.get_repository(REPO); g.get_commit(REPO, "main"); g.get_pull(REPO, 10)
        self.assertTrue(all(x[0][2:4] == ["--method", "GET"] for x in stub.commands))

if __name__ == "__main__":
    unittest.main()
