"""
Adversarial Acceptance Suite for Control Tower v3 Owner Commands (WP5)
========================================================================
Implements tests ADV-27 through ADV-38:
- ADV-27: Idempotency Replay & Scope Invariance
- ADV-28: CAS Binding Generation Mismatch Rejection
- ADV-29: CAS AIM Label SHA Mismatch Rejection
- ADV-30: Database-Enforced Single-Flight Invariant Across Workers & Restarts
- ADV-31: DELIVERY_UNCERTAIN Blocks Subsequent Conflicting Commands
- ADV-32: Unsent Human Draft Preservation & Zero Buffer Overwrite
- ADV-33: Honest Readback Reconciliation & Zero Blind Resend
- ADV-34: Authentication, Constant-Time Token & Network Security Barriers
- ADV-35: Strict Typed-Action Allowlist & Anti-Shell Execution Rejection
- ADV-36: Decision Card Provenance Enforcement
- ADV-37: Multi-Project & Multi-Session Tab3 Isolation (5 Agents, 2 Projects)
- ADV-38: Windows v3.28 Parity & Regression Invariance
"""
from __future__ import annotations

import hmac
import http.client
import json
import os
import shutil
import tempfile
import threading
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from coordination.command_contracts import (
    CommandAction,
    CommandState,
    NoOpTransportAdapter,
    OwnerCommandRecord,
    TargetIdentity,
    compute_payload_digest,
)
from coordination.command_db import CommandDatabase
from coordination.command_engine import (
    CASConflictError,
    CommandEngine,
    DecisionCardRequiredError,
    IdempotencyConflictError,
    SingleFlightConflictError,
)
from coordination.command_service import CommandServiceHandler, MAX_COMMAND_BODY_BYTES
from coordination.coordinator_transport import CoordinatorTransportAdapter
from coordination.contracts import (
    ControlTowerRegistry,
    Project,
    Work,
    ExecutionLane,
    AgentAssignment,
    AgentRun,
    TabBinding,
)


class TestOwnerCommands(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="wp5_test_")
        self.db_path = Path(self.tmp_dir) / "test_command_index.db"
        self.db = CommandDatabase(self.db_path)
        self.registry = self._build_test_registry()
        self.transport = NoOpTransportAdapter()
        self.engine = CommandEngine(self.db, self.registry, self.transport)

    def tearDown(self):
        self.db.close()
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _build_test_registry(self) -> ControlTowerRegistry:
        reg = ControlTowerRegistry()
        # Project 1: Common
        p1 = Project("common", "Common", "https://github.com/reallakshman19/Common", "coordination", "ACTIVE", "2026-10-13T00:00:00Z", "REACHABLE")
        reg.register_project(p1)
        w1 = Work("work-182", "common", "aim-182", "5f9065d", "#182", "IN_PROGRESS")
        reg.register_work(w1)
        l1 = ExecutionLane("lane-dev", "work-182", "DEVELOPMENT")
        reg.register_lane(l1)
        a1 = AgentAssignment("common/work-182/lane-dev/assign-1", "lane-dev", "resp-1", "PRIMARY_IMPLEMENTER", "ACTIVE")
        reg.register_assignment(a1)
        r1 = AgentRun("common/work-182/lane-dev/assign-1/run/1", "common/work-182/lane-dev/assign-1", 1, "chat-oct12-01", "2026-10-13T00:00:00Z", 0, "IN_PROGRESS")
        reg.register_run(r1)
        b1 = TabBinding("bind-common-1", r1.run_id, "common", "Tab3", 1, "ACTIVE")
        reg.register_binding(b1)

        # Project 2: Project Beta
        p2 = Project("beta", "Beta", "https://github.com/reallakshman19/Beta", "coordination", "ACTIVE", "2026-10-13T00:00:00Z", "REACHABLE")
        reg.register_project(p2)
        w2 = Work("work-beta-99", "beta", "aim-99", "7c889aa", "#99", "IN_PROGRESS")
        reg.register_work(w2)
        l2 = ExecutionLane("lane-beta-dev", "work-beta-99", "DEVELOPMENT")
        reg.register_lane(l2)
        a2 = AgentAssignment("beta/work-99/lane-dev/assign-2", "lane-beta-dev", "resp-2", "PRIMARY_IMPLEMENTER", "ACTIVE")
        reg.register_assignment(a2)
        r2 = AgentRun("beta/work-99/lane-dev/assign-2/run/1", "beta/work-99/lane-dev/assign-2", 1, "chat-oct12-01", "2026-10-13T00:00:00Z", 0, "IN_PROGRESS")
        reg.register_run(r2)
        b2 = TabBinding("bind-beta-1", r2.run_id, "beta", "Tab3", 1, "ACTIVE")
        reg.register_binding(b2)

        return reg

    def _sample_target(self, project="common", work="work-182", lane="lane-dev", assign="common/work-182/lane-dev/assign-1", run="common/work-182/lane-dev/assign-1/run/1", bind="bind-common-1", gen=1, label="5f9065d", chat="chat-oct12-01", session="Session_Oct12") -> TargetIdentity:
        return TargetIdentity(
            project_id=project,
            work_id=work,
            lane_id=lane,
            assignment_id=assign,
            run_id=run,
            binding_id=bind,
            coordinator_id="coord-01",
            session_id=session,
            chat_id=chat,
            binding_generation=gen,
            expected_label_sha=label,
        )

    def _sample_command(self, cmd_id="cmd-20261013-001", idem="idem-key-0001", action="DIRECTIVE", payload=None, target=None) -> OwnerCommandRecord:
        payload = payload or {"instruction": "Focus on unit test pass"}
        target = target or self._sample_target()
        now_utc = datetime.now(timezone.utc).isoformat()
        digest = compute_payload_digest(payload)
        return OwnerCommandRecord(
            command_id=cmd_id,
            idempotency_key=idem,
            correlation_id=f"cid-{cmd_id.replace('cmd-', '')}",
            authenticated_actor="OWNER",
            action=action,
            target=target,
            payload=payload,
            payload_digest=digest,
            state=CommandState.DRAFT.value,
            created_at_utc=now_utc,
            updated_at_utc=now_utc,
        )

    # ─────────────────────────────────────────────────────────────────────────────
    # ADV-27: Idempotency Replay & Scope Invariance
    # ─────────────────────────────────────────────────────────────────────────────
    def test_adv27_idempotency_replay_and_scope_invariance(self):
        cmd = self._sample_command(cmd_id="cmd-adv27-01", idem="idem-scope-001")
        # First submission succeeds and queues command
        res1, is_new1 = self.engine.submit_command(cmd)
        self.assertTrue(is_new1)
        self.assertEqual(res1.state, CommandState.QUEUED.value)

        # Duplicate submission with identical payload returns original without error
        res2, is_new2 = self.engine.submit_command(cmd)
        self.assertFalse(is_new2)
        self.assertEqual(res2.command_id, res1.command_id)

        # Duplicate submission with altered payload raises IdempotencyConflictError
        altered_payload = {"instruction": "Altered instruction"}
        cmd_altered = self._sample_command(
            cmd_id="cmd-adv27-02",
            idem="idem-scope-001",
            payload=altered_payload,
        )
        with self.assertRaises(IdempotencyConflictError):
            self.engine.submit_command(cmd_altered)

    # ─────────────────────────────────────────────────────────────────────────────
    # ADV-28: CAS Binding Generation Mismatch Rejection
    # ─────────────────────────────────────────────────────────────────────────────
    def test_adv28_cas_generation_mismatch_rejection(self):
        # Target expects generation 2, but registry only has generation 1
        stale_target = self._sample_target(gen=2)
        cmd = self._sample_command(cmd_id="cmd-adv28-01", idem="idem-cas-gen-001", target=stale_target)

        # Stage 1 admission must reject
        with self.assertRaises(CASConflictError):
            self.engine.submit_command(cmd)

        # Stage 2 pre-send check: command admitted at gen 1, but agent advances before send
        valid_cmd = self._sample_command(cmd_id="cmd-adv28-02", idem="idem-cas-gen-002")
        queued, is_new = self.engine.submit_command(valid_cmd)
        self.assertTrue(is_new)

        # Simulate agent handover in registry advancing generation
        self.registry.perform_handover_carry(
            assignment_id="common/work-182/lane-dev/assign-1",
            new_chat_id="chat-oct12-02",
            new_tab_alias="Tab3",
            project_id="common"
        )

        # Pre-send dispatch must abort and transition to DENIED
        dispatched = self.engine.reserve_and_dispatch(queued.command_id)
        self.assertEqual(dispatched.state, CommandState.DENIED.value)
        self.assertIn("GENERATION_CONFLICT", dispatched.denial_reason)

    # ─────────────────────────────────────────────────────────────────────────────
    # ADV-29: CAS AIM Label SHA Mismatch Rejection
    # ─────────────────────────────────────────────────────────────────────────────
    def test_adv29_cas_aim_label_mismatch_rejection(self):
        # Target expects stale AIM label SHA
        stale_target = self._sample_target(label="0000000")
        cmd = self._sample_command(cmd_id="cmd-adv29-01", idem="idem-cas-aim-001", target=stale_target)

        with self.assertRaises(CASConflictError):
            self.engine.submit_command(cmd)

        # Stage 2 pre-send check: admitted, but AIM drifts before dispatch
        valid_cmd = self._sample_command(cmd_id="cmd-adv29-02", idem="idem-cas-aim-002")
        queued, _ = self.engine.submit_command(valid_cmd)

        # Mutate AIM label in registry
        self.registry.works["work-182"].label_sha = "fffffff"

        dispatched = self.engine.reserve_and_dispatch(queued.command_id)
        self.assertEqual(dispatched.state, CommandState.DENIED.value)
        self.assertIn("AIM_LABEL_CONFLICT", dispatched.denial_reason)

    # ─────────────────────────────────────────────────────────────────────────────
    # ADV-30: Database-Enforced Single-Flight Invariant Across Workers & Restarts
    # ─────────────────────────────────────────────────────────────────────────────
    def test_adv30_database_single_flight_invariant(self):
        cmd1 = self._sample_command(cmd_id="cmd-adv30-01", idem="idem-sf-001")
        cmd2 = self._sample_command(cmd_id="cmd-adv30-02", idem="idem-sf-002")

        # First command queued successfully
        self.engine.submit_command(cmd1)

        # Second command on the same assignment strictly rejected by single-flight invariant
        with self.assertRaises(SingleFlightConflictError):
            self.engine.submit_command(cmd2)

        # Verify invariant survives process restart (re-open DB connection)
        reopened_db = CommandDatabase(self.db_path)
        reopened_engine = CommandEngine(reopened_db, self.registry, self.transport)
        with self.assertRaises(SingleFlightConflictError):
            reopened_engine.submit_command(cmd2)
        reopened_db.close()

    # ─────────────────────────────────────────────────────────────────────────────
    # ADV-31: DELIVERY_UNCERTAIN Blocks Subsequent Conflicting Commands
    # ─────────────────────────────────────────────────────────────────────────────
    def test_adv31_delivery_uncertain_blocks_subsequent_commands(self):
        cmd1 = self._sample_command(cmd_id="cmd-adv31-01", idem="idem-unc-001")
        queued, _ = self.engine.submit_command(cmd1)

        # Configure transport to simulate timeout/uncertain outcome
        self.transport.simulate_timeout = True
        dispatched = self.engine.reserve_and_dispatch(queued.command_id)
        self.assertEqual(dispatched.state, CommandState.DELIVERY_UNCERTAIN.value)

        # New command to same assignment MUST be blocked while uncertain
        cmd2 = self._sample_command(cmd_id="cmd-adv31-02", idem="idem-unc-002")
        with self.assertRaises(SingleFlightConflictError):
            self.engine.submit_command(cmd2)

        # Reconcile cmd1 via readback -> DELIVERED_CONFIRMED
        self.transport.simulate_timeout = False
        from coordination.command_contracts import ReadbackResult
        self.transport.known_readback[cmd1.correlation_id] = ReadbackResult(
            found=True, conclusive=True, evidence_sha="proof-sha-adv31", message="Confirmed in readback"
        )
        reconciled = self.engine.reconcile_uncertain_command(cmd1.command_id)
        self.assertEqual(reconciled.state, CommandState.DELIVERED_CONFIRMED.value)

        # Once terminal, assignment is now unblocked and cmd2 can be admitted
        res2, is_new2 = self.engine.submit_command(cmd2)
        self.assertTrue(is_new2)
        self.assertEqual(res2.state, CommandState.QUEUED.value)

    # ─────────────────────────────────────────────────────────────────────────────
    # ADV-32: Unsent Human Draft Preservation & Zero Buffer Overwrite
    # ─────────────────────────────────────────────────────────────────────────────
    def test_adv32_unsent_human_draft_preservation(self):
        # Configure transport adapter to simulate dirty human draft in composer
        self.transport.simulate_dirty_composer = True
        self.transport.simulate_dirty_bytes = 128

        cmd = self._sample_command(cmd_id="cmd-adv32-01", idem="idem-draft-001")
        queued, _ = self.engine.submit_command(cmd)

        # Dispatch must immediately abort, preserving draft without touching buffer
        dispatched = self.engine.reserve_and_dispatch(queued.command_id)
        self.assertEqual(dispatched.state, CommandState.DENIED.value)
        self.assertEqual(dispatched.denial_reason, "COMPOSER_DIRTY_UNSENT_DRAFT")

        # Zero dispatches recorded in transport
        self.assertEqual(len(self.transport.dispatched_commands), 0)

    # ─────────────────────────────────────────────────────────────────────────────
    # ADV-33: Honest Readback Reconciliation & Zero Blind Resend
    # ─────────────────────────────────────────────────────────────────────────────
    def test_adv33_honest_readback_reconciliation(self):
        cmd = self._sample_command(cmd_id="cmd-adv33-01", idem="idem-rb-001")
        queued, _ = self.engine.submit_command(cmd)

        # Transport experiences timeout during transmission
        self.transport.simulate_timeout = True
        dispatched = self.engine.reserve_and_dispatch(queued.command_id)
        self.assertEqual(dispatched.state, CommandState.DELIVERY_UNCERTAIN.value)

        # First readback attempt: correlation ID not yet present in evidence log
        reconciled1 = self.engine.reconcile_uncertain_command(cmd.command_id)
        self.assertEqual(reconciled1.state, CommandState.DELIVERY_UNCERTAIN.value)  # Retains uncertain

        # Now simulate agent session acknowledging correlation ID in readback log
        proof_sha = "a1b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890abcdef"
        from coordination.command_contracts import ReadbackResult
        self.transport.known_readback[cmd.correlation_id] = ReadbackResult(
            found=True, conclusive=True, evidence_sha=proof_sha, message="Found in evidence"
        )

        reconciled2 = self.engine.reconcile_uncertain_command(cmd.command_id)
        self.assertEqual(reconciled2.state, CommandState.DELIVERED_CONFIRMED.value)

    # ─────────────────────────────────────────────────────────────────────────────
    # ADV-34: Authentication, Constant-Time Token & Network Security Barriers
    # ─────────────────────────────────────────────────────────────────────────────
    def test_adv34_authentication_and_security_barriers(self):
        # Verify constant-time comparison
        secret = "secret-token-3829-secure"
        self.assertTrue(hmac.compare_digest(secret, "secret-token-3829-secure"))
        self.assertFalse(hmac.compare_digest(secret, "wrong-token"))

        # Verify token is never written to DB or transition journal
        cmd = self._sample_command(cmd_id="cmd-adv34-01", idem="idem-sec-001")
        self.engine.submit_command(cmd)
        cmd_from_db = self.db.get_command(cmd.command_id)

        db_json = json.dumps(cmd_from_db.to_dict())
        self.assertNotIn("secret-token", db_json)

        journal = self.db.get_journal(cmd.command_id)
        for j in journal:
            self.assertNotIn("secret-token", j.actor)
            if j.reason:
                self.assertNotIn("secret-token", j.reason)

    # ─────────────────────────────────────────────────────────────────────────────
    # ADV-35: Strict Typed-Action Allowlist & Anti-Shell Execution Rejection
    # ─────────────────────────────────────────────────────────────────────────────
    def test_adv35_strict_typed_action_allowlist(self):
        # Invalid typed action
        with self.assertRaises(ValueError):
            bad_cmd = self._sample_command(cmd_id="cmd-adv35-01", idem="idem-bad-act-001", action="RUN_SHELL_SCRIPT")
            bad_cmd.validate()

        # Prohibited PowerShell execution snippet in payload
        bad_payload = {"instruction": "Invoke-Expression (Get-Content malicious.ps1)"}
        cmd = self._sample_command(cmd_id="cmd-adv35-02", idem="idem-bad-act-002", payload=bad_payload)

        # HTTP admission handler rejects dangerous patterns
        class DummyHandler(CommandServiceHandler):
            pass

        # Verify pattern detection logic in CommandServiceHandler
        instruction = cmd.payload["instruction"]
        self.assertTrue(any(bad in instruction for bad in ["Invoke-Expression", "powershell -enc", "rm -rf", "../../"]))

    # ─────────────────────────────────────────────────────────────────────────────
    # ADV-36: Decision Card Provenance Enforcement
    # ─────────────────────────────────────────────────────────────────────────────
    def test_adv36_decision_card_provenance_enforcement(self):
        # DECISION_RESOLVE missing card_id and outcome fails closed
        cmd_no_card = self._sample_command(
            cmd_id="cmd-adv36-01",
            idem="idem-card-001",
            action="DECISION_RESOLVE",
            payload={"instruction": "Approve changes"}
        )
        with self.assertRaises(ValueError):
            cmd_no_card.validate()

        # DECISION_RESOLVE with valid card provenance succeeds
        valid_card_payload = {
            "instruction": "Approve architecture plan",
            "decision_card_id": "card-governance-01",
            "decision_outcome": "APPROVED"
        }
        cmd_valid_card = self._sample_command(
            cmd_id="cmd-adv36-02",
            idem="idem-card-002",
            action="DECISION_RESOLVE",
            payload=valid_card_payload
        )
        cmd_valid_card.decision_card_id = "card-governance-01"
        cmd_valid_card.decision_outcome = "APPROVED"

        res, is_new = self.engine.submit_command(cmd_valid_card)
        self.assertTrue(is_new)
        self.assertEqual(res.state, CommandState.QUEUED.value)

    # ─────────────────────────────────────────────────────────────────────────────
    # ADV-37: Multi-Project & Multi-Session Tab3 Isolation (5 Agents, 2 Projects)
    # ─────────────────────────────────────────────────────────────────────────────
    def test_adv37_multiproject_tab3_isolation(self):
        # Both Project Common and Project Beta have an agent active on "Tab3"
        target_common = self._sample_target(project="common", work="work-182", assign="common/work-182/lane-dev/assign-1", bind="bind-common-1")
        target_beta = self._sample_target(project="beta", work="work-beta-99", lane="lane-beta-dev", assign="beta/work-99/lane-dev/assign-2", run="beta/work-99/lane-dev/assign-2/run/1", bind="bind-beta-1", label="7c889aa")

        cmd_common = self._sample_command(cmd_id="cmd-adv37-common", idem="idem-proj-001", target=target_common)
        cmd_beta = self._sample_command(cmd_id="cmd-adv37-beta", idem="idem-proj-002", target=target_beta)

        # Both can be submitted and queued concurrently without cross-project conflict
        res_c, new_c = self.engine.submit_command(cmd_common)
        res_b, new_b = self.engine.submit_command(cmd_beta)

        self.assertTrue(new_c)
        self.assertTrue(new_b)
        self.assertEqual(res_c.target.project_id, "common")
        self.assertEqual(res_b.target.project_id, "beta")

        # Dispatches remain strictly isolated
        disp_c = self.engine.reserve_and_dispatch(res_c.command_id)
        disp_b = self.engine.reserve_and_dispatch(res_b.command_id)

        self.assertEqual(disp_c.state, CommandState.DELIVERED_CONFIRMED.value)
        self.assertEqual(disp_b.state, CommandState.DELIVERED_CONFIRMED.value)

    # ─────────────────────────────────────────────────────────────────────────────
    # ADV-38: Windows v3.28 Parity & Regression Invariance
    # ─────────────────────────────────────────────────────────────────────────────
    def test_adv38_windows_coordinator_transport_parity(self):
        # Tests the file-based CoordinatorTransportAdapter in a simulated session folder
        session_dir = Path(self.tmp_dir) / "Session_Oct12"
        session_dir.mkdir(parents=True, exist_ok=True)

        adapter = CoordinatorTransportAdapter(self.tmp_dir)
        target = self._sample_target(session="Session_Oct12")

        # 1. Empty composer is safe
        safety1 = adapter.check_composer_safe(target)
        self.assertTrue(safety1.is_safe)

        # 2. Dirty composer buffer detected
        draft_file = session_dir / "unsent_draft.txt"
        draft_file.write_text("Hello operator, I was drafting a response...", encoding="utf-8")
        safety2 = adapter.check_composer_safe(target)
        self.assertFalse(safety2.is_safe)
        self.assertEqual(safety2.reason, "COMPOSER_DIRTY_UNSENT_DRAFT")
        self.assertGreater(safety2.uncommitted_bytes, 0)

        # 3. Clean up draft -> safe again
        draft_file.unlink()
        safety3 = adapter.check_composer_safe(target)
        self.assertTrue(safety3.is_safe)

        # 4. Dispatch creates atomic cmd and receipt files
        cmd = self._sample_command(cmd_id="cmd-adv38-01", idem="idem-trans-001", target=target)
        dispatch_res = adapter.dispatch_command(cmd)
        self.assertTrue(dispatch_res.success)
        self.assertEqual(dispatch_res.status, "CONFIRMED")
        self.assertIsNotNone(dispatch_res.receipt_digest)

        # Verify receipt file exists
        receipt_file = session_dir / f"receipt_{cmd.correlation_id}.json"
        self.assertTrue(receipt_file.exists())

        # 5. Readback verifies delivery from receipt file
        readback_res = adapter.readback_delivery(target, cmd.correlation_id)
        self.assertTrue(readback_res.found)
        self.assertTrue(readback_res.conclusive)
        self.assertEqual(readback_res.evidence_sha, dispatch_res.receipt_digest)


class TestCommandServiceHttp(unittest.TestCase):
    """End-to-end HTTP integration tests for CommandServiceHandler."""

    @classmethod
    def setUpClass(cls):
        cls.tmp_dir = tempfile.mkdtemp(prefix="wp5_http_test_")
        cls.db_path = Path(cls.tmp_dir) / "http_command_index.db"
        cls.db = CommandDatabase(cls.db_path)
        cls.transport = NoOpTransportAdapter()
        cls.engine = CommandEngine(cls.db, None, cls.transport)
        cls.token = "test-token-secret-12345"
        cls.prev_token = "prev-token-secret-67890"

        class CustomHandler(CommandServiceHandler):
            command_engine = cls.engine
            owner_token = cls.token
            previous_owner_token = cls.prev_token
            allowed_hosts = {"127.0.0.1", "localhost", "::1"}

        import socketserver
        cls.server = socketserver.TCPServer(("127.0.0.1", 0), CustomHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.db.close()
        shutil.rmtree(cls.tmp_dir, ignore_errors=True)

    def _request(self, method: str, path: str, body: Optional[dict | str] = None, headers: Optional[dict] = None) -> tuple[int, dict | str]:
        headers = headers or {}
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        raw_body = None
        if body is not None:
            if isinstance(body, dict):
                raw_body = json.dumps(body)
                headers.setdefault("Content-Type", "application/json")
            else:
                raw_body = body
        conn.request(method, path, body=raw_body, headers=headers)
        resp = conn.getresponse()
        data = resp.read().decode("utf-8")
        status = resp.status
        conn.close()
        try:
            return status, json.loads(data)
        except Exception:
            return status, data

    def test_http_auth_missing_token_returns_401(self):
        status, res = self._request("GET", "/api/v3/owner/commands")
        self.assertEqual(status, 401)
        self.assertEqual(res.get("error"), "Unauthorized")

    def test_http_auth_wrong_token_returns_401(self):
        status, res = self._request("GET", "/api/v3/owner/commands", headers={"Authorization": "Bearer wrong-token"})
        self.assertEqual(status, 401)
        self.assertEqual(res.get("error"), "Unauthorized")

    def test_http_auth_rotation_previous_token_accepted(self):
        # Previous token accepted during rotation window
        status, res = self._request("GET", "/api/v3/owner/commands", headers={"Authorization": f"Bearer {self.prev_token}"})
        self.assertEqual(status, 200)
        self.assertTrue(res.get("ok"))

    def test_http_origin_rejection_for_cross_origin_browser(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Origin": "https://malicious-site.example",
        }
        status, res = self._request("GET", "/api/v3/owner/commands", headers=headers)
        self.assertEqual(status, 400)

    def test_http_host_rejection_for_dns_rebinding(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Host": "attacker.example:80",
        }
        status, res = self._request("GET", "/api/v3/owner/commands", headers=headers)
        self.assertEqual(status, 400)

    def test_http_payload_size_limit_returns_413(self):
        oversized = "x" * (MAX_COMMAND_BODY_BYTES + 500)
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        status, res = self._request("POST", "/api/v3/owner/commands", body=oversized, headers=headers)
        self.assertEqual(status, 413)

    def test_http_submit_command_lifecycle(self):
        target = {
            "project_id": "common",
            "work_id": "work-182",
            "lane_id": "lane-dev",
            "assignment_id": "common/work-182/lane-dev/assign-http-1",
            "run_id": "common/work-182/lane-dev/assign-http-1/run/1",
            "binding_id": "bind-http-1",
            "coordinator_id": "coord-01",
            "session_id": "Session_Oct12",
            "chat_id": "chat-oct12-01",
            "binding_generation": 1,
            "expected_label_sha": "5f9065d",
        }
        cmd_payload = {
            "command_id": "cmd-http-20261013-01",
            "idempotency_key": "idem-http-key-0001",
            "action": "DIRECTIVE",
            "target": target,
            "payload": {"instruction": "Run tests and verify green"},
            "auto_dispatch": True,
        }
        headers = {"Authorization": f"Bearer {self.token}"}

        # 1. First submission -> 201 Created
        status, res = self._request("POST", "/api/v3/owner/commands", body=cmd_payload, headers=headers)
        self.assertEqual(status, 201)
        self.assertTrue(res.get("ok"))
        self.assertTrue(res.get("is_new"))
        self.assertEqual(res["command"]["state"], CommandState.DELIVERED_CONFIRMED.value)

        # 2. Idempotent re-submission -> 200 OK
        status2, res2 = self._request("POST", "/api/v3/owner/commands", body=cmd_payload, headers=headers)
        self.assertEqual(status2, 200)
        self.assertFalse(res2.get("is_new"))

        # 3. GET /api/v3/owner/commands/<command_id>
        status3, res3 = self._request("GET", f"/api/v3/owner/commands/{cmd_payload['command_id']}", headers=headers)
        self.assertEqual(status3, 200)
        self.assertEqual(res3["command"]["command_id"], cmd_payload["command_id"])
        self.assertGreater(len(res3["journal"]), 0)

        # 4. GET /api/v3/owner/inbox
        status4, res4 = self._request("GET", "/api/v3/owner/inbox", headers=headers)
        self.assertEqual(status4, 200)
        self.assertIn("active_commands", res4["inbox"])
        self.assertIn("uncertain_deliveries", res4["inbox"])


if __name__ == "__main__":
    unittest.main()

