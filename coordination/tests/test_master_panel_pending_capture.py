"""B2-a own focused regression profile; synthetic raw comment/provider inputs."""
import hashlib
import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "master_panel" / "pending_capture.py"
spec = importlib.util.spec_from_file_location("pending_capture", MODULE)
pc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc)


class Source:
    def __init__(self, body="message\r\nΔ \n", updated="2026-10-14T13:12:30Z",
                 comment="1", issue=383):
        self.fields = dict(project_id="common", repo_id="1412133785",
                           repo_full_name="reallakshman19/Common", kind="ISSUE_COMMENT",
                           entity_id=comment, comment_id=comment, issue_number=issue,
                           revision_id=updated, updated_at_utc=updated,
                           created_at_utc="2026-10-14T13:10:00Z",
                           body_sha256=hashlib.sha256(body.encode()).hexdigest(),
                           url="https://github.com/reallakshman19/Common/issues/383#issuecomment-1")
    def public_dict(self):
        return dict(self.fields)


class PendingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "private.sqlite3")
        self.store = pc.PendingCaptureJournal(self.db)
        self.body = "message\r\nΔ \n"
        self.source = Source(self.body)
        self.actor = {"id": "277598171", "login": "reallakshman19"}

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def capture(self, obs="obs-1", source=None, body=None, actor="default", at="2026-10-14T13:15:00Z"):
        return self.store.capture(obs, source or self.source,
                                  self.body if body is None else body,
                                  actor=self.actor if actor == "default" else actor,
                                  observed_at=at)

    def test_exact_raw_unicode_and_crlf_hash(self):
        result = self.capture()
        self.assertEqual(result["source_body_sha256"], hashlib.sha256(self.body.encode()).hexdigest())
        self.assertEqual(result["disposition"], "PENDING")
        raw = self.store.conn.execute("SELECT raw_body FROM pending_captures").fetchone()[0]
        self.assertEqual(raw, self.body)

    def test_same_observation_exact_replay(self):
        self.capture()
        same = self.capture()
        self.assertTrue(same["replay"])
        self.assertEqual(self.store.conn.execute("SELECT COUNT(*) FROM pending_captures").fetchone()[0], 1)

    def test_same_observation_changed_time_conflicts(self):
        self.capture()
        with self.assertRaises(pc.CaptureConflict):
            self.capture(at="2026-10-14T13:16:00Z")

    def test_second_observation_same_capture_is_replay(self):
        one = self.capture()
        two = self.capture("obs-2", at="2026-10-14T13:16:00Z")
        self.assertEqual(one["capture_id"], two["capture_id"])
        self.assertTrue(two["replay"])
        self.assertEqual(self.store.conn.execute("SELECT COUNT(*) FROM pending_observations").fetchone()[0], 2)

    def test_changed_body_equal_timestamp_conflicts(self):
        self.capture()
        b = "changed"
        with self.assertRaises(pc.CaptureConflict):
            self.capture("obs-2", Source(b), b)

    def test_a_b_a_with_distinct_revision_is_three_versions(self):
        self.capture()
        b = "B"
        self.capture("obs-2", Source(b,"2026-10-14T13:12:31Z"), b)
        self.capture("obs-3", Source(self.body,"2026-10-14T13:12:32Z"))
        rows = self.store.conn.execute("SELECT body_sha256 FROM pending_captures ORDER BY updated_at").fetchall()
        self.assertEqual([r[0] for r in rows], [hashlib.sha256(s.encode()).hexdigest() for s in (self.body,b,self.body)])

    def test_missing_body_and_mismatched_body_rejected(self):
        with self.assertRaises(ValueError):
            self.store.capture("bad", self.source, None)
        with self.assertRaises(ValueError):
            self.capture(body="modified")

    def test_invalid_actor_rejected(self):
        with self.assertRaises(ValueError):
            self.capture(actor={"id":"01","login":"wrong"})
        with self.assertRaises(ValueError):
            self.capture(actor={"id":"2","login":"real","token":"DO_NOT_RECORD"})

    def test_unknown_actor_stays_unknown(self):
        result = self.capture(actor=None)
        self.assertEqual(result["authentication"], "UNKNOWN")
        self.assertEqual(self.store.conn.execute("SELECT actor_json FROM pending_captures").fetchone()[0], None)

    def test_wrong_kind_and_issue_rejected(self):
        s=Source(self.body);s.fields["kind"]="ISSUE"
        with self.assertRaises(ValueError):
            self.capture(source=s)
        s=Source(self.body);s.fields["issue_number"]=0
        with self.assertRaises(ValueError):
            self.capture(source=s)

    def test_wrong_revision_and_clock_rejected(self):
        s=Source(self.body);s.fields["revision_id"]="unexpected"
        with self.assertRaises(ValueError):
            self.capture(source=s)
        with self.assertRaises(ValueError):
            self.capture(at="yesterday")

    def test_mark_is_not_promotion_and_replay(self):
        self.capture()
        a=self.store.mark_source_observed("obs-1","scan-1","NEW")
        self.assertEqual(a["source_commits_reported"],1)
        self.assertEqual(a["disposition"],"PENDING")
        b=self.store.mark_source_observed("obs-1","scan-1","NEW")
        self.assertTrue(b["replay"])
        self.assertEqual(b["source_commits_reported"],1)

    def test_repeat_same_scan_after_initial_commit_is_replay(self):
        self.capture()
        self.store.mark_source_observed("obs-1","scan-1","NEW")
        replay=self.store.mark_source_observed("obs-1","scan-1","REPLAY")
        self.assertEqual(replay["disposition"],"PENDING")
        self.assertTrue(replay["replay"])

    def test_mark_conflict_and_unknown_capture_rejected(self):
        self.capture()
        self.store.mark_source_observed("obs-1","scan-1","NEW")
        with self.assertRaises(pc.CaptureConflict):
            self.store.mark_source_observed("obs-1","scan-1","EDITED")
        with self.assertRaises(ValueError):
            self.store.mark_source_observed("missing","scan-1","NEW")

    def test_restart_pending_and_mark_survives(self):
        self.capture()
        self.store.close()
        self.store=pc.PendingCaptureJournal(self.db)
        self.assertEqual(self.store.status("obs-1")["source_commits_reported"],0)
        self.store.mark_source_observed("obs-1","scan-1","NEW")
        self.store.close()
        self.store=pc.PendingCaptureJournal(self.db)
        self.assertEqual(self.store.status("obs-1")["disposition"], "PENDING")
        self.assertEqual(self.store.status("obs-1")["source_commits_reported"],1)

    def test_immutable_history_and_private_projection(self):
        self.capture()
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.conn.execute("UPDATE pending_captures SET raw_body='changed'")
        safe = json.dumps(self.store.status("obs-1"))
        self.assertNotIn(self.body, safe)
        self.assertNotIn(self.actor["login"], safe)
        self.assertNotIn("raw_body", safe)
        self.assertEqual(self.store.status("obs-1")["dispatch_authority"], "NOT_GRANTED")

    def test_partial_failure_keeps_orphan_pending(self):
        self.capture()
        # No source ledger commit after capture; subsequent replay cannot promote.
        self.assertEqual(self.store.status("obs-1")["source_commits_reported"],0)
        self.assertEqual(self.store.status("obs-1")["independent_acceptance"],"UNKNOWN")

    def test_no_implicit_casp_review_or_accepted_state(self):
        self.capture()
        self.store.mark_source_observed("obs-1","scan-2","REPLAY")
        d = self.store.status("obs-1")
        self.assertEqual(d["registration"],"NOT_CONFIGURED")
        self.assertNotIn("SOURCE_CORRELATED", json.dumps(d))


if __name__ == "__main__":
    unittest.main()
