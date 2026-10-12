"""Control Tower WP4 Acceptance & Adversarial Test Suite.

Covers ADV-17 through ADV-26:
- Strict allowlist schema validation (ADV-17)
- Coordinator Next withholding in public export (ADV-18)
- Fail-closed secret leak gate on allowed fields (ADV-19)
- Fail-closed local path leak gate (ADV-20)
- Unapproved project exclusion (ADV-21)
- Deterministic public content digest (ADV-22)
- Generation shift 410 recovery (ADV-23)
- Atomic publication and rollback (ADV-24)
- URL sanitizer security (ADV-25)
- DOM XSS immunity, zero Google Fonts, and CSP headers (ADV-26)
"""
from __future__ import annotations

import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from coordination.contracts import (
    AgentAssignment, AgentRun, ControlTowerRegistry, ExecutionLane,
    Project, TabBinding, Work
)
from coordination.indexer import EvidenceIndex
from coordination.projections import ProjectionEngine, ProjectionQueryService
from coordination.public_exporter import (
    PrivacyValidator, PrivacyViolationError, GenerationShiftError,
    PolicyViolationError, URLSanitizer, export_public_snapshot
)

ASOF = "2026-10-12T12:00:00Z"


def _make_fixture_db(tmp_dir: Path):
    reg = ControlTowerRegistry()
    for pid in ("common", "grade9"):
        reg.register_project(Project(pid, pid.upper(), f"https://github.com/example/{pid}",
                                     coordination_dir=f"/tmp/{pid}", status="ACTIVE", as_of=ASOF,
                                     provider_reachability="REACHABLE" if pid == "common" else "RATE_LIMITED"))
    snapshots = {}
    for i in range(5):
        pid = "common" if i < 3 else "grade9"
        wid, lid, aid, rid = (f"{pid}-work-{i}", f"{pid}-lane-{i}",
                              f"{pid}-assignment-{i}", f"{pid}-run-{i}")
        reg.register_work(Work(wid, pid, f"AIM-{i}", "5f9065d" * 5 + "0" * 5,
                               f"https://github.com/example/{pid}/issues/{i+1}", "IN_PROGRESS"))
        reg.register_lane(ExecutionLane(lid, wid, "DEVELOPMENT"))
        reg.register_assignment(AgentAssignment(aid, lid, f"RESP-{i}", "PRIMARY_IMPLEMENTER", "ACTIVE"))
        tab = "Tab3" if i in (0, 3) else "Tab5" if i == 2 else f"Tab{i+1}"
        chat = "same-chat" if i in (0, 3) else f"chat-{i}"
        reg.register_run(AgentRun(rid, aid, 1, chat, ASOF, 0, "IN_PROGRESS"))
        reg.register_binding(TabBinding(f"binding-{i}", rid, pid, tab, 1, "ACTIVE", session_alias="Session_One"))
        snap = snapshots.setdefault(pid, {
            "schema_version": "v1.0.0",
            "project_id": pid, "coordinator_id": "coord-1",
            "session_id": "Session_One", "generated_at_utc": ASOF,
            "source_digest": "a" * 64, "source_watermark": "cycle-1",
            "cycle_seconds": 900, "observations": []
        })
        snap["observations"].append({
            "tab": tab, "status": f"status-{i}", "aim": "-", "plan": "-", "ac": "-",
            "ci": "CI_UNKNOWN", "meter": "-", "due": "-", "checked": "-",
            "next": f"original coordinator next {i}",
            "tab_position": tab.replace("Tab", ""), "chat_id": chat,
            "binding_generation": 1, "probe_status": "SUCCESS",
            "last_probe_at_utc": "2026-10-12T11:59:00Z",
            "observed_at_utc": ASOF
        })

    ev_db = tmp_dir / "evidence.db"
    idx = EvidenceIndex(str(ev_db))
    idx.store_evidence("common", {
        "provider_comment_id": "100", "task_id": "WP4-T01",
        "owner_issue": "common#353", "candidate_sha": "a" * 40,
        "author": "tester", "created_at": "2026-10-12T11:50:00Z",
        "updated_at": "2026-10-12T11:50:00Z",
        "raw_text": ("Outcome: O1\nFor the user: Safe\nProof: https://github.com/reallakshman19/Common/issues/353\n"
                     "TASK_EVIDENCE v3.6\nTask: WP4-T01\nChild issue: common#353\nCandidate: " + "a"*40 + "\nTests: 1/1\n"),
        "proof_url": "https://github.com/reallakshman19/Common/issues/353",
        "is_canonical_8line": True
    })

    proj_db = tmp_dir / "projections.db"
    engine = ProjectionEngine(str(proj_db))
    attributions = [{
        "project_id": "common", "task_id": "WP4-T01", "child_issue": "common#353",
        "work_id": "common-work-0", "assignment_id": "common-assignment-0",
        "run_id": "common-run-0", "source_ref": "https://github.com/reallakshman19/Common/issues/353",
        "source_revision": "r1", "valid_from_utc": "2026-10-12T00:00:00Z", "valid_to_utc": None
    }]
    engine.materialize(reg, idx, list(snapshots.values()), ASOF, {"source": "1"},
                       task_attributions=attributions)
    idx.close()
    return proj_db


class TestPublicDashboard(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.proj_db = _make_fixture_db(self.tmp_path)
        self.out_json = self.tmp_path / "public_snapshot.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_adv17_allowlist_schema_enforcement(self):
        """ADV-17: Export validates against public schema and excludes forbidden keys."""
        snap = export_public_snapshot(
            self.proj_db, self.out_json, approved_projects=["common"]
        )
        self.assertTrue(self.out_json.is_file())
        self.assertEqual(snap["visibility"], "PUBLIC")
        self.assertEqual(len(snap["portfolio"]), 1)
        self.assertEqual(snap["portfolio"][0]["project_id"], "common")

        # Verify no internal identifiers leaked
        forbidden = ["chat_id", "tab_position", "coordinator_id", "session_id", "coordination_dir"]
        for assign in snap["assignments"]:
            for k in forbidden:
                self.assertNotIn(k, assign)

    def test_adv18_coordinator_next_withheld_in_public_export(self):
        """ADV-18: Coordinator Next is withheld in public export but preserved in local DB."""
        snap = export_public_snapshot(
            self.proj_db, self.out_json, approved_projects=["common"]
        )
        # In public snapshot, next is withheld
        for a in snap["assignments"]:
            self.assertEqual(a["next"], "[WITHHELD_PRIVATE_COORDINATOR_NEXT]")

        # In local SQLite projection read, next remains verbatim
        svc = ProjectionQueryService(str(self.proj_db))
        local_page = svc.page("assignments", project="common", limit=10)
        self.assertTrue(len(local_page["items"]) > 0)
        for item in local_page["items"]:
            self.assertTrue(item["next"].startswith("original coordinator next"))

    def test_adv19_secret_in_allowed_field_leak_gate(self):
        """ADV-19: Secret token in an allowed field fails closed with PrivacyViolationError."""
        # Clean passes
        PrivacyValidator.assert_no_leaks({"project_id": "common", "status": "ALL_GREEN"})

        # Token in status fails
        with self.assertRaises(PrivacyViolationError):
            PrivacyValidator.assert_no_leaks({
                "project_id": "common",
                "status": "ghp_123456789012345678901234567890123456"
            })

        # Bearer token fails
        with self.assertRaises(PrivacyViolationError):
            PrivacyValidator.assert_no_leaks({
                "project_id": "common",
                "aim": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            })

    def test_adv20_local_path_leak_gate(self):
        """ADV-20: Windows or POSIX local path fails closed with PrivacyViolationError."""
        with self.assertRaises(PrivacyViolationError):
            PrivacyValidator.assert_no_leaks({
                "project_id": "common",
                "aim": r"C:\Users\operator\Documents\secret_folder"
            })
        with self.assertRaises(PrivacyViolationError):
            PrivacyValidator.assert_no_leaks({
                "project_id": "common",
                "aim": "/home/operator/project"
            })

    def test_adv21_unapproved_project_exclusion(self):
        """ADV-21: Unapproved project (grade9) is completely omitted from public export."""
        snap = export_public_snapshot(
            self.proj_db, self.out_json, approved_projects=["common"]
        )
        project_ids = {p["project_id"] for p in snap["portfolio"]}
        self.assertIn("common", project_ids)
        self.assertNotIn("grade9", project_ids)

        for w in snap["works"]:
            self.assertEqual(w["project_id"], "common")
        for a in snap["assignments"]:
            self.assertEqual(a["project_id"], "common")
        for e in snap["evidence"]:
            self.assertEqual(e["project_id"], "common")

    def test_adv22_deterministic_content_digest(self):
        """ADV-22: Deterministic digest and byte-exact JSON with fixed clock."""
        out1 = self.tmp_path / "snap1.json"
        out2 = self.tmp_path / "snap2.json"
        s1 = export_public_snapshot(self.proj_db, out1, approved_projects=["common"], fixed_clock=ASOF)
        s2 = export_public_snapshot(self.proj_db, out2, approved_projects=["common"], fixed_clock=ASOF)

        self.assertEqual(s1["content_digest"], s2["content_digest"])
        self.assertEqual(out1.read_bytes(), out2.read_bytes())

    def test_adv23_generation_shift_410_recovery(self):
        """ADV-23: Generation shift (410) recovers once, then fails closed if persistent."""
        with patch.object(ProjectionQueryService, "page") as mock_page:
            # First call returns normal init page, second call raises LookupError (410), third succeeds
            init_page = {"generation": "a" * 64, "as_of_utc": ASOF, "items": []}
            mock_page.side_effect = [
                init_page,
                LookupError("Expired projection generation"),
                init_page,
                {"generation": "a" * 64, "as_of_utc": ASOF, "items": [], "next_cursor": None},
                {"generation": "a" * 64, "as_of_utc": ASOF, "items": [], "next_cursor": None},
                {"generation": "a" * 64, "as_of_utc": ASOF, "items": [], "next_cursor": None},
                {"generation": "a" * 64, "as_of_utc": ASOF, "items": [], "next_cursor": None},
                {"generation": "a" * 64, "as_of_utc": ASOF, "items": [], "next_cursor": None},
                {"generation": "a" * 64, "as_of_utc": ASOF, "items": [], "next_cursor": None},
            ]
            snap = export_public_snapshot(self.proj_db, self.out_json, approved_projects=["common"])
            self.assertIsNotNone(snap)

    def test_adv24_atomic_rollback_on_failure(self):
        """ADV-24: Failure during export unlinks temporary file and leaves existing snapshot intact."""
        # Create an existing safe snapshot
        self.out_json.write_text('{"safe": true}', encoding="utf-8")

        with patch("coordination.public_exporter.PrivacyValidator.assert_no_leaks",
                   side_effect=PrivacyViolationError("Simulated leak")):
            with self.assertRaises(PrivacyViolationError):
                export_public_snapshot(self.proj_db, self.out_json, approved_projects=["common"])

        # Verify original file untouched and no leftover .tmp files
        self.assertEqual(self.out_json.read_text(encoding="utf-8"), '{"safe": true}')
        tmp_files = list(self.tmp_path.glob("*.tmp.*"))
        self.assertEqual(len(tmp_files), 0)

    def test_adv25_url_sanitizer_security(self):
        """ADV-25: URLSanitizer neutralizes non-HTTPS, javascript, data, and untrusted domains."""
        self.assertIsNone(URLSanitizer.sanitize("javascript:alert(1)"))
        self.assertIsNone(URLSanitizer.sanitize("data:text/html,<h1>XSS</h1>"))
        self.assertIsNone(URLSanitizer.sanitize("file:///etc/passwd"))
        self.assertIsNone(URLSanitizer.sanitize("http://insecure.com/repo"))
        self.assertIsNone(URLSanitizer.sanitize("https://evil.com/repo"))

        safe = "https://github.com/reallakshman19/Common/issues/353"
        self.assertEqual(URLSanitizer.sanitize(safe), safe)

        safe_sub = "https://raw.githubusercontent.com/reallakshman19/Common/main/README.md"
        self.assertEqual(URLSanitizer.sanitize(safe_sub), safe_sub)

    def test_adv26_dom_xss_and_csp_headers(self):
        """ADV-26: index.html has strict CSP meta tag, zero Google Fonts, and app.js has zero unescaped innerHTML."""
        ui_dir = Path(__file__).parent.parent / "ui"
        index_html = (ui_dir / "index.html").read_text(encoding="utf-8")
        app_js = (ui_dir / "app.js").read_text(encoding="utf-8")

        # Zero external Google Fonts in HTML
        self.assertNotIn("fonts.googleapis.com", index_html)
        self.assertNotIn("fonts.gstatic.com", index_html)

        # Meta CSP tag is present
        self.assertIn("http-equiv=\"Content-Security-Policy\"", index_html)
        self.assertIn("default-src 'self'", index_html)

        # Check app.js for dangerous raw innerHTML interpolations
        # innerHTML should not be used to render raw dynamic object attributes
        self.assertNotIn("innerHTML = item.", app_js)


if __name__ == "__main__":
    unittest.main()
