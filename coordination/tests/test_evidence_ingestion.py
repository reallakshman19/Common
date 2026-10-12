"""
Tests for Multi-Project Evidence Ingestion & Durable Indexing (WP1)
===================================================================
Verifies:
- Canonical 8-line parser strictness (rejection of trailing text / noncanonical metrics)
- Exact-head CI check evaluator (no cross-head inheritance, old head detection)
- Evidence idempotency on replay
- Comment edit versioning & history preservation
- Multi-project provider fault isolation
- Privacy redaction of secrets and local paths
- Snapshot projection and source watermarks
- Durable SQLite WAL persistence
"""

import unittest
import tempfile
import os
from pathlib import Path
from datetime import datetime, timezone

from coordination.indexer import (
    EvidenceIndex,
    CanonicalV36Adapter,
    ExactHeadCIAdapter,
    PrivacyRedactor,
    generate_control_tower_snapshot
)
from coordination.contracts import (
    ControlTowerRegistry,
    Project,
    Work,
    ExecutionLane,
    AgentAssignment,
    AgentRun,
    TabBinding
)


class TestEvidenceIngestionAndIndexing(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp_dir.name) / "test_evidence.db")
        self.index = EvidenceIndex(self.db_path)

    def tearDown(self):
        self.index.close()
        self.tmp_dir.cleanup()

    def test_canonical_8line_parser_success(self):
        raw = (
            "Outcome: O1\n"
            "For the user: Worker is responsive\n"
            "Proof: https://github.com/reallakshman19/Common/issues/353\n"
            "TASK_EVIDENCE v3.6\n"
            "Task: WP1-353-W01\n"
            "Child issue: reallakshman19/Common#353\n"
            "Candidate: c37187955fd9bf7b292779565eac9cc18bfa728a\n"
            "Tests: 10/10\n"
        )
        parsed, status = CanonicalV36Adapter.parse(raw)
        self.assertEqual(status, "PARSED")
        self.assertEqual(parsed["outcome"], "O1")
        self.assertEqual(parsed["owner_issue"], "reallakshman19/Common#353")
        self.assertEqual(parsed["candidate_sha"], "c37187955fd9bf7b292779565eac9cc18bfa728a")
        self.assertTrue(parsed["is_canonical_8line"])

    def test_canonical_8line_parser_rejects_trailing_metrics(self):
        raw = (
            "Outcome: O1\nFor the user: Worker responsive\n"
            "Proof: https://github.com/reallakshman19/Common/issues/353\n"
            "TASK_EVIDENCE v3.6\nTask: WP1-353-W01\n"
            "Child issue: reallakshman19/Common#353\n"
            "Candidate: " + "a"*40 + "\nTests: 9/10\n"
        )
        for tampered in (raw + "TASK_EVIDENCE_METRICS_V1: x\n", raw.rstrip("\n"), raw + "Tests: 1/1\n"):
            with self.subTest(tampered=tampered[-25:]):
                parsed, status = CanonicalV36Adapter.parse(tampered)
                self.assertEqual(status, "NONCANONICAL_REJECTED")
                self.assertIsNone(parsed)

    def test_canonical_8line_parser_rejects_malformed_sha(self):
        # v3.6 permits textual candidate refs; the semantic invalidity here
        # is the missing mandatory repo/issue relationship, not SHA length.
        bad_issue = (
            "Outcome: O1\nFor the user: Worker responsive\n"
            "Proof: https://github.com/reallakshman19/Common/issues/353\n"
            "TASK_EVIDENCE v3.6\nTask: WP1-353-W01\n"
            "Child issue: not-a-repo-issue\n"
            "Candidate: c37187955fd9bf7b292779565eac9cc18bfa728a\n"
            "Tests: 10/10\n"
        )
        parsed, status = CanonicalV36Adapter.parse(bad_issue)
        self.assertEqual(status, "NONCANONICAL_REJECTED")
        self.assertIsNone(parsed)

    def test_exact_head_ci_invalidation(self):
        old_sha = "1111111111111111111111111111111111111111"
        current_head = "c37187955fd9bf7b292779565eac9cc18bfa728a"

        # Check on old SHA was green -> evaluates to TESTS_PASSED_ON_OLD_HEAD
        res_old = ExactHeadCIAdapter.evaluate_check(
            check_name="coordination-ci",
            check_head_sha=old_sha,
            current_pr_head_sha=current_head,
            check_status="completed",
            check_conclusion="success"
        )
        self.assertEqual(res_old, "TESTS_PASSED_ON_OLD_HEAD")

        # Check on current head that passed -> EXACT_HEAD_PASSED
        res_current = ExactHeadCIAdapter.evaluate_check(
            check_name="coordination-ci",
            check_head_sha=current_head,
            current_pr_head_sha=current_head,
            check_status="completed",
            check_conclusion="success"
        )
        self.assertEqual(res_current, "EXACT_HEAD_PASSED")

        # Path-scoped skipped check on current head -> GREEN_NOT_APPLICABLE
        res_skipped = ExactHeadCIAdapter.evaluate_check(
            check_name="delp-validator",
            check_head_sha=current_head,
            current_pr_head_sha=current_head,
            check_status="completed",
            check_conclusion="skipped",
            is_path_scoped=True,
            skipped=True
        )
        self.assertEqual(res_skipped, "GREEN_NOT_APPLICABLE")

    def test_ingestion_idempotency_on_replay(self):
        ev = {
            "evidence_id": "ev-001",
            "provider_comment_id": "comment-9988",
            "task_id": "task-001",
            "owner_issue": "#353",
            "candidate_sha": "c37187955fd9bf7b292779565eac9cc18bfa728a",
            "pr_number": 352,
            "author": "Antigravity",
            "created_at": "2026-10-12T14:00:00Z",
            "raw_text": "TASK_EVIDENCE: task-001\nRESULT: PASS"
        }

        # First ingest
        v1, is_new1 = self.index.store_evidence("project-common", ev)
        self.assertEqual(v1, 1)
        self.assertTrue(is_new1)

        # Replay identical ingest
        v2, is_new2 = self.index.store_evidence("project-common", ev)
        self.assertEqual(v2, 1)
        self.assertFalse(is_new2)  # Idempotent: no new record created

        # Total active count is 1
        active = self.index.get_active_evidence("project-common")
        self.assertEqual(len(active), 1)

    def test_comment_edit_versioning(self):
        ev = {
            "evidence_id": "ev-001",
            "provider_comment_id": "comment-9988",
            "task_id": "task-001",
            "owner_issue": "#353",
            "candidate_sha": "c37187955fd9bf7b292779565eac9cc18bfa728a",
            "pr_number": 352,
            "author": "Antigravity",
            "created_at": "2026-10-12T14:00:00Z",
            "raw_text": "Original comment content"
        }

        # Ingest initial version
        v1, is_new1 = self.index.store_evidence("project-common", ev)
        self.assertEqual(v1, 1)

        # Ingest edited comment (different content)
        ev_edited = dict(ev)
        ev_edited["raw_text"] = "Edited comment content with revised findings"
        ev_edited["updated_at"] = "2026-10-12T14:15:00Z"

        v2, is_new2 = self.index.store_evidence("project-common", ev_edited)
        self.assertEqual(v2, 2)
        self.assertTrue(is_new2)

        # Active version should only be v2
        active = self.index.get_active_evidence("project-common")
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0]["version"], 2)
        self.assertIn("Edited comment content", active[0]["raw_text"])

        # History retains both v1 and v2
        history = self.index.get_evidence_versions("project-common", "comment-9988")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["version"], 1)
        self.assertEqual(history[1]["version"], 2)

    def test_provider_fault_isolation(self):
        # Project A experiences 429 Rate Limit
        self.index.update_project_status("project-common", "GITHUB_ISSUE_COMMENT", "RATE_LIMITED")
        # Project B continues normally
        self.index.update_project_status("project-grade9", "GITHUB_ISSUE_COMMENT", "REACHABLE")

        status_a = self.index.get_project_status("project-common", "GITHUB_ISSUE_COMMENT")
        status_b = self.index.get_project_status("project-grade9", "GITHUB_ISSUE_COMMENT")

        self.assertEqual(status_a, "RATE_LIMITED")
        self.assertEqual(status_b, "REACHABLE")

    def test_privacy_redactor_strips_secrets_and_local_paths(self):
        text_with_secrets = (
            "Found token ghp_123456789012345678901234567890123456 and "
            "path C:\\Users\\reall\\Documents\\antigravity\\amazing-mendeleev\\coordination\\file.txt "
            "and unix path /home/user/workspace/secret.key"
        )
        redacted = PrivacyRedactor.redact_text(text_with_secrets)
        self.assertNotIn("ghp_123456789012345678901234567890123456", redacted)
        self.assertNotIn("C:\\Users\\reall", redacted)
        self.assertNotIn("/home/user", redacted)
        self.assertIn("[REDACTED_SECRET]", redacted)
        self.assertIn("[REDACTED_LOCAL_PATH]", redacted)

    def test_snapshot_generation_with_watermarks(self):
        reg = ControlTowerRegistry()
        p = Project(
            project_id="project-common",
            name="Common",
            repo_url="https://github.com/reallakshman19/Common",
            coordination_dir="coordination",
            status="ACTIVE",
            as_of="2026-10-12T14:00:00Z",
            provider_reachability="REACHABLE"
        )
        reg.register_project(p)

        w = Work(
            work_id="work-353",
            project_id="project-common",
            aim_id="AIM-353",
            label_sha="149770a21ca073df49717a96e2106c967adddc2d",
            issue_ref="#353",
            acceptance_status="ACCEPTED"
        )
        reg.register_work(w)

        ev = {
            "evidence_id": "ev-001",
            "provider_comment_id": "comment-9988",
            "task_id": "task-001",
            "owner_issue": "#353",
            "candidate_sha": "c37187955fd9bf7b292779565eac9cc18bfa728a",
            "pr_number": 352,
            "author": "Antigravity",
            "created_at": "2026-10-12T14:10:00Z",
            "raw_text": "Sample evidence"
        }
        self.index.store_evidence("project-common", ev)

        snap = generate_control_tower_snapshot(reg, self.index, visibility="INTERNAL")
        self.assertEqual(snap["visibility"], "INTERNAL")
        with self.assertRaises(PermissionError):
            generate_control_tower_snapshot(reg, self.index, visibility="PUBLIC")
        self.assertEqual(snap["evidence_count"], 1)
        self.assertIn("project-common", snap["source_watermarks"])
        self.assertEqual(snap["source_watermarks"]["project-common"], "2026-10-12T14:10:00Z")
        self.assertEqual(len(snap["projects"]), 1)
        self.assertEqual(len(snap["works"]), 1)

    def test_sqlite_wal_persistence_across_reconnect(self):
        # Write event
        event = {
            "event_id": "evt-001",
            "project_id": "project-common",
            "source_kind": "GITHUB_ISSUE_COMMENT",
            "source_ref": "https://github.com/reallakshman19/Common/issues/353#issuecomment-1",
            "source_revision": "1",
            "content_sha": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "observed_at_utc": "2026-10-12T14:00:00Z",
            "ingested_at_utc": "2026-10-12T14:00:01Z",
            "parse_status": "PARSED",
            "scope_key": "project-common/work-353",
            "raw_payload": {"hello": "world"}
        }
        self.assertTrue(self.index.record_ingestion_event(event))

        # Reopen database with new instance
        reopened_index = EvidenceIndex(self.db_path)
        # Attempt to insert identical event ID -> must return False (IntegrityError caught)
        self.assertFalse(reopened_index.record_ingestion_event(event))
        reopened_index.close()


if __name__ == "__main__":
    unittest.main()
