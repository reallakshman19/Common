"""B2-a scanner-to-private-journal integration; fake provider and SQLite only.

This is deliberately NOT a controller registration, CASP correlation, live
provider, authentication, agent command or acceptance test.
"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from coordination.master_panel.github_source import GitHubSourceScanner
from coordination.master_panel.pending_capture import PendingCaptureJournal
from coordination.master_panel.storage import SourceConflict, SourceStore
from coordination.tests.test_master_panel_intake import FakeGitHub, T1, T2, T3


class PendingScannerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.source = SourceStore(str(root / "sources.sqlite"))
        self.journal = PendingCaptureJournal(str(root / "private-captures.sqlite"))
        self.reader = FakeGitHub()
        self.scanner = GitHubSourceScanner(self.source, self.reader, self.journal)

    def tearDown(self):
        self.journal.close()
        self.source.close()
        self.tmp.cleanup()

    def scan(self, pid="common"):
        return self.scanner.run(pid, max_requests=5)

    def counts(self):
        a = self.journal.conn.execute("SELECT COUNT(*) FROM pending_captures").fetchone()[0]
        b = self.journal.conn.execute("SELECT COUNT(*) FROM pending_observations").fetchone()[0]
        c = self.journal.conn.execute("SELECT COUNT(*) FROM pending_source_commits").fetchone()[0]
        return a, b, c

    def test_provider_body_actor_before_legacy_parser_and_no_promotion(self):
        comment = self.reader.comments["common"][0]
        comment["body"] = "raw\r\nΔ  \n"
        comment["user"] = {"id": 12345, "login": "synthetic-agent"}
        outcome = self.scan()
        self.assertEqual(outcome["source_status"], "REACHABLE")
        self.assertEqual(self.counts(), (1, 1, 1))
        rec = self.journal.conn.execute(
            "SELECT capture_id,raw_body,actor_json FROM pending_captures"
        ).fetchone()
        self.assertEqual(rec["raw_body"], "raw\r\nΔ  \n")
        self.assertEqual(json.loads(rec["actor_json"]),
                         {"id": "12345", "login": "synthetic-agent"})
        status = self.journal.status(rec["capture_id"])
        self.assertEqual(status["disposition"], "PENDING")
        self.assertEqual(status["authentication"], "UNKNOWN")
        self.assertEqual(status["registration"], "NOT_CONFIGURED")
        self.assertNotIn("synthetic-agent", json.dumps(status))
        self.assertNotIn("raw\r\nΔ", json.dumps(status))
        # SourceStore exposes legacy claim only, never raw/private actor.
        self.assertNotIn("synthetic-agent", json.dumps(self.source.objects("common")))
        again = self.scan()
        self.assertEqual(again["source_status"], "REACHABLE")
        self.assertEqual(self.counts(), (1, 2, 2))

    def test_a_b_a_creates_three_committed_source_and_private_versions(self):
        self.scan()
        comment = self.reader.comments["common"][0]
        comment.update(body="B", updated_at=T2)
        self.scan()
        comment.update(body="synthetic A", updated_at=T3)
        self.scan()
        self.assertEqual(self.counts(), (3, 3, 3))
        versions = self.source.revisions("common", "1412133785",
                                         "ISSUE_COMMENT", "1001")
        self.assertEqual([v["action"] for v in versions],
                         ["NEW", "EDITED", "EDITED"])

    def test_invalid_provider_actor_fails_before_source_commit(self):
        self.reader.comments["common"][0]["user"] = {
            "id": 7, "login": "synthetic", "private_token": "SECRET"
        }
        result = self.scan()
        self.assertEqual(result["source_status"], "UNAVAILABLE")
        self.assertEqual(result["error_kind"], "SOURCE_CONFLICT")
        self.assertEqual(self.counts(), (0, 0, 0))
        self.assertEqual(self.source.revisions("common", "1412133785",
                                               "ISSUE_COMMENT", "1001"), [])

    def test_crash_before_source_commit_replays_orphan_without_promotion(self):
        real = self.source.observe
        def fail_comment(source, scan_id, report=None):
            if source.kind.value == "ISSUE_COMMENT":
                raise SourceConflict("injected pre-source failure")
            return real(source, scan_id, report)
        with patch.object(self.source, "observe", side_effect=fail_comment):
            failed = self.scan()
        self.assertEqual(failed["error_kind"], "SOURCE_CONFLICT")
        self.assertEqual(self.counts(), (1, 1, 0))
        self.assertEqual(self.scan()["source_status"], "REACHABLE")
        self.assertEqual(self.counts(), (1, 2, 1))

    def test_crash_after_source_commit_reconciles_report_only(self):
        with patch.object(self.journal, "mark_source_observed",
                          side_effect=ValueError("injected post-source failure")):
            failed = self.scan()
        self.assertEqual(failed["error_kind"], "SOURCE_CONFLICT")
        self.assertEqual(self.counts(), (1, 1, 0))
        versions = self.source.revisions("common", "1412133785",
                                         "ISSUE_COMMENT", "1001")
        self.assertEqual(len(versions), 1)
        resumed = self.scan()
        self.assertEqual(resumed["source_status"], "REACHABLE")
        self.assertEqual(len(self.source.revisions(
            "common", "1412133785", "ISSUE_COMMENT", "1001")), 1)
        self.assertEqual(self.counts(), (1, 2, 1))
        capture_id = self.journal.conn.execute(
            "SELECT capture_id FROM pending_captures"
        ).fetchone()[0]
        self.assertEqual(self.journal.status(capture_id)["disposition"], "PENDING")

    def test_partial_source_isolation_across_projects(self):
        self.assertEqual(self.scan("common")["source_status"], "REACHABLE")
        self.reader.fail_repo = "aa3"
        aa3 = self.scan("aa3")
        self.assertNotEqual(aa3["source_status"], "REACHABLE")
        self.assertEqual(self.counts(), (1, 1, 1))
        self.assertEqual(self.scan("common")["source_status"], "REACHABLE")
        self.assertEqual(self.counts(), (1, 2, 2))


if __name__ == "__main__":
    unittest.main()
