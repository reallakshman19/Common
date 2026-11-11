"""M1-U02 isolated fake-provider tests (no network, SEND or Oracle mutation).

Run: python -m unittest coordination.tests.test_master_panel_intake -v
All test bodies are synthetic. Hosted integration/auth/live source parity NOT_RUN.
"""
import tempfile
import unittest
from pathlib import Path

from coordination.master_panel.github_source import (
    ALLOWLIST, GitHubSourceScanner, ProviderError
)
from coordination.master_panel.storage import SourceStore


T1 = "2026-10-14T00:01:00Z"
T2 = "2026-10-14T00:02:00Z"
T3 = "2026-10-14T00:03:00Z"


class FakeGitHub:
    def __init__(self):
        self.issues = {}
        self.comments = {}
        self.fail_repo = None
        self.fail_code = 429
        for reg in ALLOWLIST.values():
            self.issues[reg.project_id] = [self.issue(reg.project_id)]
            self.comments[reg.project_id] = [self.comment(reg.project_id)]

    @staticmethod
    def issue(pid):
        reg = ALLOWLIST[pid]
        return {"id": 101, "number": 373, "body": "synthetic issue",
                "created_at": T1, "updated_at": T1,
                "html_url": f"https://github.com/{reg.repo_full_name}/issues/373"}

    @staticmethod
    def comment(pid, ident=1001):
        reg = ALLOWLIST[pid]
        return {"id": ident, "body": "synthetic A",
                "created_at": T1, "updated_at": T1,
                "html_url": (f"https://github.com/{reg.repo_full_name}/issues/373"
                             f"#issuecomment-{ident}")}

    def get_json(self, path, query=None):
        fields = path.split("/")
        pid = next((pid for pid, r in ALLOWLIST.items()
                    if fields[1:3] == r.repo_full_name.split("/")), None)
        if pid is None:
            raise AssertionError("Nonallowlisted provider access")
        if self.fail_repo == pid:
            raise ProviderError(self.fail_code, "synthetic failure")
        reg = ALLOWLIST[pid]
        if len(fields) == 3:
            return {"id": int(reg.repo_id), "full_name": reg.repo_full_name}
        page = query["page"]
        if fields[3:] == ["issues"]:
            values = self.issues[pid]
        elif len(fields) == 6 and fields[3] == "issues" and fields[5] == "comments":
            values = self.comments[pid]
        else:
            raise AssertionError(path)
        return values[(page-1)*100:page*100]


class TestMasterPanelGitHubIntake(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / "source.sqlite")
        self.db = SourceStore(self.path)
        self.fake = FakeGitHub()
        self.scanner = GitHubSourceScanner(self.db, self.fake)

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def scan(self, pid="common", max_requests=5):
        return self.scanner.run(pid, max_requests=max_requests)

    def versions(self, pid="common", comment_id="1001"):
        return self.db.revisions(
            pid, ALLOWLIST[pid].repo_id, "ISSUE_COMMENT", comment_id
        )

    def test_complete_and_replay_across_scans(self):
        first = self.scan()
        self.assertEqual(first["source_status"], "REACHABLE")
        self.assertEqual(first["new_versions"], 2)  # issue + comment
        again = self.scan()
        self.assertEqual(again["source_status"], "REACHABLE")
        self.assertEqual(again["new_versions"], 0)
        self.assertEqual(len(self.versions()), 1)

    def test_body_reversion_is_distinct_version_and_exact_replay(self):
        self.scan()
        comment = self.fake.comments["common"][0]
        comment.update(body="synthetic B", updated_at=T2)
        self.scan()
        comment.update(body="synthetic A", updated_at=T3)
        self.scan()
        versions = self.versions()
        self.assertEqual([v["action"] for v in versions],
                         ["NEW", "EDITED", "EDITED"])
        self.assertEqual(versions[0]["body_sha256"], versions[2]["body_sha256"])
        self.assertEqual(len({v["body_sha256"] for v in versions}), 2)
        self.scan()
        self.assertEqual(len(self.versions()), 3)

    def test_full_scan_tombstone_then_restore(self):
        self.scan()
        old = self.fake.comments["common"].pop()
        outcome = self.scan()
        self.assertEqual(outcome["tombstones"], 1)
        self.assertEqual(self.versions()[-1]["action"], "TOMBSTONE")
        self.fake.comments["common"].append(old)
        outcome = self.scan()
        self.assertEqual(outcome["new_versions"], 1)
        self.assertEqual(self.versions()[-1]["action"], "RESTORED")

    def test_partial_page_restart_never_tombstones_unseen(self):
        self.fake.comments["common"] = [
            self.fake.comment("common", i+1001) for i in range(101)
        ]
        partial = self.scan(max_requests=3)
        self.assertEqual(partial["source_status"], "PARTIAL")
        self.assertEqual(partial["cursor"]["comment_page"], 2)
        self.assertEqual(partial["tombstones"], 0)
        self.db.close()
        self.db = SourceStore(self.path)
        self.scanner = GitHubSourceScanner(self.db, self.fake)
        finished = self.scan(max_requests=3)
        self.assertEqual(finished["source_status"], "REACHABLE")
        self.assertEqual(finished["tombstones"], 0)
        self.assertEqual(len(self.db.objects("common", limit=200)), 102)

    def test_per_repo_failures_are_isolated(self):
        self.scan("common")
        self.fake.fail_repo = "common"
        for code, state, kind in [
            (401, "UNAVAILABLE", "AUTHENTICATION"),
            (403, "FORBIDDEN", "AUTHORIZATION"),
            (429, "RATE_LIMITED", "RATE_LIMIT"),
            (503, "UNAVAILABLE", "HTTP_ERROR"),
        ]:
            with self.subTest(code=code):
                self.fake.fail_code = code
                failure = self.scan("common")
                self.assertEqual(failure["source_status"], state)
                self.assertEqual(failure["error_kind"], kind)
                self.assertEqual(failure["tombstones"], 0)
                self.assertEqual(len(self.versions()), 1)
        aa3 = self.scan("aa3")
        self.assertEqual(aa3["source_status"], "REACHABLE")
        self.assertNotEqual(
            self.db.objects("aa3")[1]["repo_id"],
            self.db.objects("common")[1]["repo_id"]
        )

    def test_conflicting_same_timestamp_cannot_overwrite(self):
        self.scan()
        self.fake.comments["common"][0]["body"] = "contradictory edit"
        result = self.scan()
        self.assertEqual(result["source_status"], "UNAVAILABLE")
        self.assertEqual(result["error_kind"], "SOURCE_CONFLICT")
        self.assertEqual(len(self.versions()), 1)

    def test_allowlist_and_budget(self):
        with self.assertRaisesRegex(ValueError, "Unregistered"):
            self.scan("unauthorized")
        with self.assertRaisesRegex(ValueError, "bounded"):
            self.scan(max_requests=101)


if __name__ == "__main__":
    unittest.main()
