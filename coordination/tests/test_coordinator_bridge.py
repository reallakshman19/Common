"""
Adversarial Acceptance Suite for Coordinator Status-to-JSON Bridge (WP2)
========================================================================
Covers ADV-01 through ADV-08:
- ADV-01: Multi-Project Tab3 Disambiguation
- ADV-02: Carry Generation Invalidation & Handover Meter Reset
- ADV-03: 10-Cell Parity Across Abnormal States
- ADV-04: Full and Short Golden Byte Fidelity
- ADV-05: Timeout Liveness & Freshness against 2x Cycle
- ADV-06: Fault Isolation & Corrupt State Tolerance
- ADV-07: Internal API Defense (GET /api/v3/observations)
- ADV-08: Cross-Project Work Violation Detection
"""

import json
import os
import shutil
import socketserver
import subprocess
import tempfile
import threading
import unittest
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from coordination.contracts import (
    Project, Work, ExecutionLane, AgentAssignment, AgentRun,
    TabBinding, CoordinatorObservation, ControlTowerRegistry
)
from coordination.coordinator_bridge import (
    AtomicSnapshotWriter, AtomicSnapshotReader, LivenessEvaluator,
    CompositeBindingResolver, CoordinatorBridge, get_observations_for_api
)
from coordination.coordination_ui import ApiHandler


class TestCoordinatorBridgeWP2(unittest.TestCase):

    def setUp(self):
        self.coordinator_id = "claude-desktop-coordinator-01"
        self.now_utc = "2026-10-12T16:00:00Z"

    def test_adv01_multiproject_tab3_disambiguation(self):
        """ADV-01: Two projects each with Tab3 must resolve distinctly without collision."""
        reg = ControlTowerRegistry()

        p1 = Project("reallakshman19/Common", "Common", "https://github.com/reallakshman19/Common",
                     "coordination", "ACTIVE", self.now_utc, "REACHABLE")
        p2 = Project("reallakshman19/Grade9v3.5", "Grade9", "https://github.com/reallakshman19/Grade9v3.5",
                     "coordination", "ACTIVE", self.now_utc, "REACHABLE")
        reg.register_project(p1)
        reg.register_project(p2)

        w1 = Work("work-common-353", "reallakshman19/Common", "AIM-COMMON-V1", "1234567",
                  "https://github.com/reallakshman19/Common/issues/353", "IN_PROGRESS")
        w2 = Work("work-grade9-182", "reallakshman19/Grade9v3.5", "AIM-GRADE9-V1", "7654321",
                  "https://github.com/reallakshman19/Grade9v3.5/issues/182", "IN_PROGRESS")
        reg.register_work(w1)
        reg.register_work(w2)

        l1 = ExecutionLane("work-common-353/lane/dev", "work-common-353", "DEVELOPMENT")
        l2 = ExecutionLane("work-grade9-182/lane/dev", "work-grade9-182", "DEVELOPMENT")
        reg.register_lane(l1)
        reg.register_lane(l2)

        a1 = AgentAssignment("work-common-353/lane/dev/assign/g1", "work-common-353/lane/dev",
                             "RESP-01", "PRIMARY_IMPLEMENTER", "ACTIVE")
        a2 = AgentAssignment("work-grade9-182/lane/dev/assign/g2", "work-grade9-182/lane/dev",
                             "RESP-02", "PRIMARY_IMPLEMENTER", "ACTIVE")
        reg.register_assignment(a1)
        reg.register_assignment(a2)

        run1 = AgentRun("run-common-353-1", a1.assignment_id, 1, "chat-c1", self.now_utc, 3, "IN_PROGRESS")
        run2 = AgentRun("run-grade9-182-1", a2.assignment_id, 1, "chat-g1", self.now_utc, 2, "IN_PROGRESS")
        reg.register_run(run1)
        reg.register_run(run2)

        # Both coordinator observations report 'Tab3'
        obs_common = {
            "tab": "Tab3 · [chat-c1](url) · Common Task",
            "status": "🟢 working", "aim": "AIM-COMMON-V1", "plan": "WP2", "ac": "2/5",
            "ci": "green", "meter": "10/35 min", "due": "handover in 25 min",
            "checked": "2 min ago", "next": "export rowsjson",
            "tab_position": "3", "chat_id": "chat-c1", "binding_generation": 1,
            "probe_status": "SUCCESS", "last_probe_at_utc": self.now_utc
        }
        obs_grade9 = {
            "tab": "Tab3 · [chat-g1](url) · Grade9 Task",
            "status": "🟢 working", "aim": "AIM-GRADE9-V1", "plan": "QRT", "ac": "4/5",
            "ci": "green", "meter": "18/35 min", "due": "handover in 17 min",
            "checked": "1 min ago", "next": "verify proof",
            "tab_position": "3", "chat_id": "chat-g1", "binding_generation": 1,
            "probe_status": "SUCCESS", "last_probe_at_utc": self.now_utc
        }

        res_common = CompositeBindingResolver.resolve(
            obs_common, p1.project_id, self.coordinator_id, "Session_Common", reg
        )
        res_grade9 = CompositeBindingResolver.resolve(
            obs_grade9, p2.project_id, self.coordinator_id, "Session_Grade9", reg
        )

        # Verification: Correct and distinct assignment and work resolution
        self.assertEqual(res_common["assignment_id"], a1.assignment_id)
        self.assertEqual(res_common["work_id"], "work-common-353")
        self.assertEqual(res_grade9["assignment_id"], a2.assignment_id)
        self.assertEqual(res_grade9["work_id"], "work-grade9-182")
        self.assertNotIn("UNASSIGNED_OR_UNKNOWN_TAB", res_common["conflicts"])
        self.assertNotIn("UNASSIGNED_OR_UNKNOWN_TAB", res_grade9["conflicts"])

    def test_adv02_carry_generation_invalidation(self):
        """ADV-02: Predecessor carried to g+1 retains history; successor starts fresh run."""
        reg = ControlTowerRegistry()
        p = Project("reallakshman19/Common", "Common", "https://github.com/reallakshman19/Common",
                    "coordination", "ACTIVE", self.now_utc, "REACHABLE")
        reg.register_project(p)
        w = Work("work-common-353", p.project_id, "AIM-COMMON-V1", "1234567",
                 "https://github.com/reallakshman19/Common/issues/353", "IN_PROGRESS")
        reg.register_work(w)
        lane = ExecutionLane("work-common-353/lane/dev", w.work_id, "DEVELOPMENT")
        reg.register_lane(lane)
        assign = AgentAssignment("work-common-353/lane/dev/assign/g1", lane.lane_id,
                                 "RESP-01", "PRIMARY_IMPLEMENTER", "ACTIVE")
        reg.register_assignment(assign)

        # Run 1 (Generation 1, chat-001) completed/handed over
        run1 = AgentRun("run-001", assign.assignment_id, 1, "chat-001", "2026-10-12T14:00:00Z",
                        5, "SUCCEEDED")
        reg.register_run(run1)

        # Run 2 (Generation 2, chat-002) carried from run 1
        run2 = AgentRun("run-002", assign.assignment_id, 2, "chat-002", self.now_utc,
                        0, "IN_PROGRESS", predecessor_run_id=run1.run_id)
        reg.register_run(run2)

        # Both exist in history; generation 1 is not overwritten
        self.assertEqual(reg.runs["run-001"].generation, 1)
        self.assertEqual(reg.runs["run-001"].evidence_cadence_count, 5)
        self.assertEqual(reg.runs["run-002"].generation, 2)
        self.assertEqual(reg.runs["run-002"].evidence_cadence_count, 0)
        self.assertEqual(reg.runs["run-002"].predecessor_run_id, "run-001")

        # Resolving chat-002 resolves to run2 while preserving assignment
        obs_new = {
            "tab": "Tab1 g2 ⚡ · [chat-002](url)", "status": "🟢 working", "aim": "AIM-COMMON-V1",
            "plan": "WP2", "ac": "3/5", "ci": "green", "meter": "0/35 min",
            "due": "handover in 35 min", "checked": "0 min ago", "next": "implement bridge",
            "tab_position": "1", "chat_id": "chat-002", "binding_generation": 2,
            "probe_status": "SUCCESS", "last_probe_at_utc": self.now_utc
        }
        res = CompositeBindingResolver.resolve(obs_new, p.project_id, self.coordinator_id, "Session_Oct12", reg)
        self.assertEqual(res["assignment_id"], assign.assignment_id)
        self.assertEqual(res["work_id"], w.work_id)
        self.assertEqual(res["binding_generation"], 2)

    def test_adv03_ten_cell_parity_across_abnormal_states(self):
        """ADV-03: Ensure all 10 columns are present and intact across diverse coordinator states."""
        bridge = CoordinatorBridge(coordinator_id=self.coordinator_id)
        states_to_test = [
            # 1. Normal working
            {"tab": "Tab1", "status": "🟢 working", "aim": "AIM-1", "plan": "WP2", "ac": "1/2",
             "ci": "green", "meter": "15/35 min", "due": "handover in 20 min", "checked": "1 min ago", "next": "run test",
             "tab_position": "1", "chat_id": "c1", "binding_generation": 1, "probe_status": "SUCCESS", "last_probe_at_utc": self.now_utc},
            # 2. LOADFAIL recovery wait
            {"tab": "Tab2", "status": "🔴 problem: loadfail since 15:40", "aim": "-", "plan": "-", "ac": "-",
             "ci": "-", "meter": "0/35 min", "due": "retry 15:50", "checked": "2 min ago", "next": "normal route",
             "tab_position": "2", "chat_id": "c2", "binding_generation": 1, "probe_status": "LOADFAIL", "last_probe_at_utc": "2026-10-12T15:40:00Z"},
            # 3. NOBOX
            {"tab": "Tab3", "status": "🔴 problem: nobox since 15:30", "aim": "-", "plan": "-", "ac": "-",
             "ci": "-", "meter": "5/35 min", "due": "retry 15:40", "checked": "10 min ago", "next": "normal route",
             "tab_position": "3", "chat_id": "c3", "binding_generation": 1, "probe_status": "NOBOX", "last_probe_at_utc": "2026-10-12T15:30:00Z"},
            # 4. UNUSUAL activity wait
            {"tab": "Tab4", "status": "🔴 problem: unusual since 15:00", "aim": "-", "plan": "-", "ac": "-",
             "ci": "-", "meter": "12/35 min", "due": "retry 15:35", "checked": "35 min ago", "next": "normal route",
             "tab_position": "4", "chat_id": "c4", "binding_generation": 1, "probe_status": "UNUSUAL", "last_probe_at_utc": "2026-10-12T15:00:00Z"},
            # 5. [OUT] not in scope
            {"tab": "Tab5 · c5 · [OUT] external", "status": "⚪ not in my scope", "aim": "-", "plan": "-", "ac": "-",
             "ci": "-", "meter": "-", "due": "-", "checked": "-", "next": "nothing",
             "tab_position": "5", "chat_id": "c5", "binding_generation": 1, "probe_status": "NEVER_PROBED", "last_probe_at_utc": None},
            # 6. [HOLD] on hold by Owner
            {"tab": "Tab6 · c6 · [HOLD] paused", "status": "⚪ on hold (Owner)", "aim": "-", "plan": "-", "ac": "-",
             "ci": "-", "meter": "-", "due": "-", "checked": "-", "next": "nothing",
             "tab_position": "6", "chat_id": "c6", "binding_generation": 1, "probe_status": "NEVER_PROBED", "last_probe_at_utc": None},
            # 7. new chat: not measured yet
            {"tab": "Tab7 · c7", "status": "new chat: not measured yet", "aim": "-", "plan": "-", "ac": "-",
             "ci": "-", "meter": "-", "due": "-", "checked": "**never**", "next": "read it next cycle",
             "tab_position": "7", "chat_id": "c7", "binding_generation": 1, "probe_status": "NEVER_PROBED", "last_probe_at_utc": None},
            # 8. Stable (> 60 min)
            {"tab": "Tab8", "status": "🔵 stable 65 min · working", "aim": "AIM-8", "plan": "done D1", "ac": "5/5",
             "ci": "green", "meter": "22/35 min", "due": "handover in 13 min", "checked": "1 min ago", "next": "ask you: still mine to drive?",
             "tab_position": "8", "chat_id": "c8", "binding_generation": 1, "probe_status": "SUCCESS", "last_probe_at_utc": self.now_utc}
        ]

        raw_json = json.dumps(states_to_test)
        snapshot = bridge.build_snapshot(raw_json, as_of_utc=self.now_utc)
        self.assertEqual(len(snapshot["observations"]), 8)

        ten_columns = ["tab", "status", "aim", "plan", "ac", "ci", "meter", "due", "checked", "next"]
        for i, obs in enumerate(snapshot["observations"]):
            for col in ten_columns:
                self.assertIn(col, obs, f"Row {i} ({obs['status']}) missing column '{col}'")
                self.assertEqual(obs[col], states_to_test[i][col], f"Column '{col}' altered in row {i}")

    def test_adv04_full_and_short_golden_byte_fidelity(self):
        """ADV-04: watch.ps1 -Action rows and -Action report retain 100% byte fidelity to .bak."""
        installed_watch = Path(r"C:\Users\reall\.claude\skills\coordinator-protocol\scripts\watch.ps1")
        installed_bak = Path(r"C:\Users\reall\.claude\skills\coordinator-protocol\scripts\watch.ps1.bak")
        if not installed_watch.is_file() or not installed_bak.is_file():
            self.skipTest("Coordinator script files not found in Claude environment")

        with tempfile.TemporaryDirectory() as td:
            temp_bak_ps1 = Path(td) / "watch.bak.ps1"
            shutil.copyfile(installed_bak, temp_bak_ps1)

            # Test -Action rows
            cmd_bak_rows = ["powershell", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
                            "-File", str(temp_bak_ps1), "-Action", "rows", "-Tabs", "1=c35d978a"]
            cmd_cur_rows = ["powershell", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
                            "-File", str(installed_watch), "-Action", "rows", "-Tabs", "1=c35d978a"]
            out_bak_rows = subprocess.run(cmd_bak_rows, capture_output=True).stdout
            out_cur_rows = subprocess.run(cmd_cur_rows, capture_output=True).stdout
            self.assertEqual(out_bak_rows, out_cur_rows, "Binary mismatch in -Action rows output")

            # Test -Action report
            cmd_bak_rep = ["powershell", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
                           "-File", str(temp_bak_ps1), "-Action", "report", "-Tabs", "1=c35d978a"]
            cmd_cur_rep = ["powershell", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass",
                           "-File", str(installed_watch), "-Action", "report", "-Tabs", "1=c35d978a"]
            out_bak_rep = subprocess.run(cmd_bak_rep, capture_output=True).stdout
            out_cur_rep = subprocess.run(cmd_cur_rep, capture_output=True).stdout
            self.assertEqual(out_bak_rep, out_cur_rep, "Binary mismatch in -Action report output")

    def test_adv05_timeout_liveness_and_freshness_against_2x_cycle(self):
        """ADV-05: Liveness evaluated against 2x Cycle; TIMEOUT -> STALE; never STOPPED."""
        cycle = 15  # seconds; 2x cycle = 30s
        now = "2026-10-12T16:00:00Z"

        # 1. Fresh probe (10s ago) with SUCCESS -> ALIVE
        fresh_time = "2026-10-12T15:59:50Z"
        self.assertEqual(
            LivenessEvaluator.evaluate("SUCCESS", fresh_time, as_of_utc=now, cycle_seconds=cycle),
            "ALIVE"
        )

        # 2. Expired probe (45s ago, > 30s) -> STALE
        old_time = "2026-10-12T15:59:15Z"
        self.assertEqual(
            LivenessEvaluator.evaluate("SUCCESS", old_time, as_of_utc=now, cycle_seconds=cycle),
            "STALE"
        )

        # 3. Probe status TIMEOUT -> STALE (even if recent)
        self.assertEqual(
            LivenessEvaluator.evaluate("TIMEOUT", fresh_time, as_of_utc=now, cycle_seconds=cycle),
            "STALE"
        )

        # 4. Probe status LOADFAIL / ERROR / NOBOX / UNUSUAL -> STALE
        for abnormal in ("LOADFAIL", "ERROR", "NOBOX", "UNUSUAL"):
            self.assertEqual(
                LivenessEvaluator.evaluate(abnormal, fresh_time, as_of_utc=now, cycle_seconds=cycle),
                "STALE"
            )

        # 5. NEVER_PROBED -> UNKNOWN
        self.assertEqual(
            LivenessEvaluator.evaluate("NEVER_PROBED", None, as_of_utc=now, cycle_seconds=cycle),
            "UNKNOWN"
        )

        # Invariant: Evaluator NEVER outputs STOPPED
        for p in ("SUCCESS", "TIMEOUT", "LOADFAIL", "NOBOX", "UNUSUAL", "ERROR", "NEVER_PROBED"):
            result = LivenessEvaluator.evaluate(p, fresh_time, as_of_utc=now, cycle_seconds=cycle)
            self.assertNotEqual(result, "STOPPED")

    def test_adv06_fault_isolation_and_corrupt_state_tolerance(self):
        """ADV-06: Corrupted snapshot file or invalid JSON handled safely without crashing."""
        with tempfile.TemporaryDirectory() as td:
            # 1. Missing file -> returns None
            missing = Path(td) / "missing.json"
            self.assertIsNone(AtomicSnapshotReader.read_snapshot(missing))

            # 2. Corrupt JSON -> returns None
            corrupt = Path(td) / "corrupt.json"
            corrupt.write_text("{bad json: missing quotes", encoding="utf-8")
            self.assertIsNone(AtomicSnapshotReader.read_snapshot(corrupt))

            # 3. Invalid schema version -> returns None
            invalid_ver = Path(td) / "invalid_ver.json"
            invalid_ver.write_text(json.dumps({"schema_version": "v999.0", "observations": []}), encoding="utf-8")
            self.assertIsNone(AtomicSnapshotReader.read_snapshot(invalid_ver))

            # 4. get_observations_for_api fallback
            fallback = get_observations_for_api("reallakshman19/Common", session_id="NonExistent", snapshot_dir=td)
            self.assertEqual(fallback["schema_version"], "v1.0.0")
            self.assertEqual(fallback["observations"], [])
            self.assertEqual(fallback["source_watermark"], "NO_OBSERVATIONS_FOUND")

    def test_adv07_internal_api_defense(self):
        """ADV-07: GET /api/v3/observations loopback defense, Host check, and snapshot query."""
        with tempfile.TemporaryDirectory() as td:
            snap_path = Path(td) / "observations_reallakshman19_Common_Session_Test.json"
            sample_snap = {
                "schema_version": "v1.0.0",
                "coordinator_id": self.coordinator_id,
                "session_id": "Session_Test",
                "project_id": "reallakshman19/Common",
                "generated_at_utc": self.now_utc,
                "source_digest": "a" * 64,
                "source_watermark": "cycle-100",
                "cycle_seconds": 15,
                "observations": [
                    {
                        "tab": "Tab1 · c1", "status": "🟢 working", "aim": "AIM-1",
                        "plan": "-", "ac": "-", "ci": "-", "meter": "10/35 min",
                        "due": "-", "checked": "1 min ago", "next": "route",
                        "tab_position": "1", "chat_id": "c1", "binding_generation": 1,
                        "observed_at_utc": self.now_utc, "probe_status": "SUCCESS",
                        "liveness": "ALIVE", "coordinator_liveness": "ALIVE",
                        "conflicts": []
                    }
                ]
            }
            AtomicSnapshotWriter.write_snapshot(snap_path, sample_snap)

            class LocalHandler(ApiHandler):
                config = {
                    "projects": [{"id": "reallakshman19/Common", "name": "Common"}],
                    "server": {"snapshot_dir": td}
                }

            server = socketserver.TCPServer(("127.0.0.1", 0), LocalHandler)
            port = server.server_address[1]
            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()
            try:
                # 1. Valid request to /api/v3/observations
                url = f"http://127.0.0.1:{port}/api/v3/observations?project=reallakshman19/Common&session=Session_Test"
                req = urllib.request.Request(url, headers={"Host": f"127.0.0.1:{port}"})
                with urllib.request.urlopen(req) as resp:
                    self.assertEqual(resp.status, 200)
                    body = json.loads(resp.read().decode())
                    self.assertEqual(body["schema_version"], "v1.0.0")
                    self.assertEqual(len(body["observations"]), 1)
                    self.assertEqual(body["observations"][0]["status"], "🟢 working")

                # 2. DNS rebinding host header rejection
                bad_req = urllib.request.Request(url, headers={"Host": "attacker.com"})
                try:
                    urllib.request.urlopen(bad_req)
                    self.fail("Expected 400 for bad Host header")
                except urllib.error.HTTPError as e:
                    self.assertEqual(e.code, 400)

                # 3. Encoded null byte parameter rejection
                null_url = f"http://127.0.0.1:{port}/api/v3/observations?project=reallakshman19/Common&session=%00test"
                try:
                    urllib.request.urlopen(urllib.request.Request(null_url, headers={"Host": f"127.0.0.1:{port}"}))
                    self.fail("Expected 400 for null byte path")
                except urllib.error.HTTPError as e:
                    self.assertEqual(e.code, 400)
            finally:
                server.shutdown()
                server.server_close()

    def test_adv08_cross_project_work_violation_detection(self):
        """ADV-08: Two tabs in same session binding to same work flagged with MULTIPLE_ACTIVE_TABS_FOR_WORK."""
        reg = ControlTowerRegistry()
        p = Project("reallakshman19/Common", "Common", "https://github.com/reallakshman19/Common",
                    "coordination", "ACTIVE", self.now_utc, "REACHABLE")
        reg.register_project(p)
        w = Work("work-common-353", p.project_id, "AIM-COMMON-V1", "1234567",
                 "https://github.com/reallakshman19/Common/issues/353", "IN_PROGRESS")
        reg.register_work(w)
        lane = ExecutionLane("work-common-353/lane/dev", w.work_id, "DEVELOPMENT")
        reg.register_lane(lane)

        # Tab 1 mapped to work-common-353
        assign1 = AgentAssignment("work-common-353/lane/dev/assign/g1", lane.lane_id, "RESP-01", "PRIMARY_IMPLEMENTER", "ACTIVE")
        reg.register_assignment(assign1)
        run1 = AgentRun("run-001", assign1.assignment_id, 1, "chat-111", self.now_utc, 1, "IN_PROGRESS")
        reg.register_run(run1)

        # Tab 2 also mapped to same work-common-353
        assign2 = AgentAssignment("work-common-353/lane/dev/assign/g2", lane.lane_id, "RESP-02", "PRIMARY_IMPLEMENTER", "ACTIVE")
        reg.register_assignment(assign2)
        run2 = AgentRun("run-002", assign2.assignment_id, 1, "chat-222", self.now_utc, 1, "IN_PROGRESS")
        reg.register_run(run2)

        raw_rows = [
            {"tab": "Tab1 · c1", "status": "🟢 working", "aim": "AIM-1", "plan": "-", "ac": "-", "ci": "-",
             "meter": "5/35 min", "due": "-", "checked": "1 min ago", "next": "step1",
             "tab_position": "1", "chat_id": "chat-111", "binding_generation": 1, "probe_status": "SUCCESS", "last_probe_at_utc": self.now_utc},
            {"tab": "Tab2 · c2", "status": "🟢 working", "aim": "AIM-1", "plan": "-", "ac": "-", "ci": "-",
             "meter": "8/35 min", "due": "-", "checked": "1 min ago", "next": "step2",
             "tab_position": "2", "chat_id": "chat-222", "binding_generation": 1, "probe_status": "SUCCESS", "last_probe_at_utc": self.now_utc}
        ]

        bridge = CoordinatorBridge(coordinator_id=self.coordinator_id, project_id=p.project_id)
        snapshot = bridge.build_snapshot(json.dumps(raw_rows), registry_or_map=reg, as_of_utc=self.now_utc)

        obs1 = snapshot["observations"][0]
        obs2 = snapshot["observations"][1]

        # Tab 1 binds cleanly
        self.assertEqual(obs1["work_id"], "work-common-353")
        self.assertNotIn("MULTIPLE_ACTIVE_TABS_FOR_WORK:work-common-353", obs1["conflicts"])

        # Tab 2 detects conflict violation and flags it
        self.assertEqual(obs2["work_id"], "work-common-353")
        self.assertIn("MULTIPLE_ACTIVE_TABS_FOR_WORK:work-common-353", obs2["conflicts"])

        # Original coordinator status text is preserved verbatim
        self.assertEqual(obs1["status"], "🟢 working")
        self.assertEqual(obs2["status"], "🟢 working")


if __name__ == "__main__":
    unittest.main()
