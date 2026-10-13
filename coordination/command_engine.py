"""
Control Tower v3 Command Engine & Concurrency Gate (WP5)
==========================================================
Coordinates:
- Scoped idempotency evaluation
- Two-stage Compare-and-Swap (CAS) gating:
    Stage 1: At admission (generation, AIM label SHA, single-flight, decision card)
    Stage 2: Immediately pre-send (re-verifies generation, active chat, AIM SHA, HOLD/OUT, one-active-tab)
- Non-destructive composer safety check (never overwrite unsent human drafts)
- Database-enforced single-flight locking (including DELIVERY_UNCERTAIN retention)
- Transport dispatch and honest readback reconciliation (zero blind double-send)
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from coordination.command_contracts import (
    CommandAction,
    CommandState,
    ComposerSafetyResult,
    DispatchResult,
    NoOpTransportAdapter,
    OwnerCommandRecord,
    ReadbackResult,
    SINGLE_FLIGHT_ACTIVE_STATES,
    TargetIdentity,
    TERMINAL_STATES,
    TransportAdapter,
    compute_payload_digest,
)
from coordination.command_db import CommandDatabase
from coordination.contracts import ControlTowerRegistry


class CommandEngineError(Exception):
    """Base error for command engine."""
    pass


class IdempotencyConflictError(CommandEngineError):
    """Raised when an idempotency key is reused with a different payload."""
    pass


class SingleFlightConflictError(CommandEngineError):
    """Raised when an assignment already has an active command."""
    pass


class CASConflictError(CommandEngineError):
    """Raised when target binding generation or AIM label SHA mismatches."""
    pass


class DecisionCardRequiredError(CommandEngineError):
    """Raised when an action requires decision-card provenance that is missing/invalid."""
    pass


class CommandEngine:
    """Core execution engine for Control Tower Owner Commands."""

    def __init__(
        self,
        db: CommandDatabase,
        registry: Optional[ControlTowerRegistry] = None,
        transport: Optional[TransportAdapter] = None,
    ):
        self.db = db
        self.registry = registry
        self.transport = transport or NoOpTransportAdapter()
        # In-memory observation lookup for live coordinator state checks
        self.live_observations: Dict[str, Dict[str, Any]] = {}

    def set_live_observation(self, assignment_id: str, obs_data: Dict[str, Any]):
        """Sets live coordinator observation for assignment (used in testing/live updates)."""
        self.live_observations[assignment_id] = obs_data

    def submit_command(
        self,
        cmd: OwnerCommandRecord,
        actor: str = "OWNER"
    ) -> Tuple[OwnerCommandRecord, bool]:
        """
        Submits a command through Stage 1 admission:
        1. Validates schema and contracts.
        2. Evaluates idempotency key against existing records.
        3. Enforces typed action allowlist and decision-card requirements.
        4. Evaluates Stage 1 CAS against registry and live state.
        5. Verifies database single-flight availability.
        6. Persists to SQLite WAL store in QUEUED state.
        Returns: (record, is_newly_queued)
        """
        cmd.validate()

        # 1. Idempotency Check
        existing = self.db.get_command_by_idempotency_key(cmd.idempotency_key)
        if existing:
            if existing.payload_digest == cmd.payload_digest:
                # Idempotent replay: return existing record
                return existing, False
            raise IdempotencyConflictError(
                f"Idempotency key '{cmd.idempotency_key}' reused with different payload digest "
                f"({cmd.payload_digest} != {existing.payload_digest})"
            )

        # 2. Decision Card Provenance Check
        if cmd.action == CommandAction.DECISION_RESOLVE.value:
            card_id = cmd.payload.get("decision_card_id") or cmd.decision_card_id
            outcome = cmd.payload.get("decision_outcome") or cmd.decision_outcome
            if not card_id or not outcome:
                raise DecisionCardRequiredError("DECISION_RESOLVE requires valid decision_card_id and outcome")

        # 3. Single-Flight Database Check
        active = self.db.get_active_command_for_assignment(cmd.target.assignment_id)
        if active:
            raise SingleFlightConflictError(
                f"Assignment '{cmd.target.assignment_id}' already has active command '{active.command_id}' "
                f"in state '{active.state}'"
            )

        # 4. Stage 1 CAS Verification
        self._verify_cas_stage1(cmd.target)

        # 5. Transition DRAFT -> ACCEPTED -> QUEUED and persist
        cmd.state = CommandState.QUEUED.value
        now_utc = datetime.now(timezone.utc).isoformat()
        cmd.created_at_utc = now_utc
        cmd.updated_at_utc = now_utc

        self.db.insert_command(cmd, actor)
        queued_cmd = self.db.get_command(cmd.command_id)
        return queued_cmd, True  # type: ignore

    def _verify_cas_stage1(self, target: TargetIdentity):
        """Verifies authority against registry and live observations at admission."""
        if self.registry:
            work = self.registry.works.get(target.work_id)
            if not work:
                raise CASConflictError(f"Target work '{target.work_id}' not found in registry")
            if work.label_sha != target.expected_label_sha:
                raise CASConflictError(
                    f"AIM label SHA mismatch: target expected '{target.expected_label_sha}', "
                    f"registry has '{work.label_sha}'"
                )

            assign = self.registry.assignments.get(target.assignment_id)
            if not assign:
                raise CASConflictError(f"Target assignment '{target.assignment_id}' not found in registry")

            run = self.registry.runs.get(target.run_id)
            if not run:
                raise CASConflictError(f"Target run '{target.run_id}' not found in registry")
            if run.generation != target.binding_generation:
                raise CASConflictError(
                    f"Binding generation mismatch: target expected {target.binding_generation}, "
                    f"registry run has {run.generation}"
                )
            if run.run_state in ("SUPERSEDED", "INTERRUPTED", "SUCCEEDED", "FAILED"):
                raise CASConflictError(f"Target run '{target.run_id}' is no longer active (state: {run.run_state})")

            assign_runs = [r for r in self.registry.runs.values() if r.assignment_id == target.assignment_id]
            assign_runs.sort(key=lambda x: x.generation, reverse=True)
            if assign_runs and assign_runs[0].generation != target.binding_generation:
                raise CASConflictError(
                    f"Binding generation mismatch: target expected {target.binding_generation}, "
                    f"assignment has advanced to generation {assign_runs[0].generation}"
                )

        # Check live observation if present
        obs = self.live_observations.get(target.assignment_id)
        if obs:
            if obs.get("binding_generation") and obs["binding_generation"] != target.binding_generation:
                raise CASConflictError(
                    f"Live coordinator generation advanced: expected {target.binding_generation}, "
                    f"found {obs['binding_generation']}"
                )
            status = obs.get("status", "")
            if "HOLD" in status or "OUT" in status:
                raise CASConflictError(f"Coordinator status in '{status}'; commands cannot bypass coordinator holds")

    def reserve_and_dispatch(
        self,
        command_id: str,
        worker_id: str = "worker-1"
    ) -> OwnerCommandRecord:
        """
        Executes reservation, pre-send CAS re-verification, composer check, and dispatch:
        1. Acquires reservation lease (QUEUED -> RESERVED).
        2. Re-verifies Stage 2 CAS immediately pre-send.
        3. Inspects target composer safety (must be clean/empty).
        4. Transitions to DISPATCHING.
        5. Invokes transport adapter.
        6. Transitions to DELIVERED_CONFIRMED or DELIVERY_UNCERTAIN.
        """
        cmd = self.db.get_command(command_id)
        if not cmd:
            raise KeyError(f"Command not found: {command_id}")

        if cmd.state != CommandState.QUEUED.value:
            return cmd

        # 1. Acquire Reservation Lease
        reserved = self.db.reserve_command(command_id, worker_id, lease_seconds=60)
        if not reserved:
            return self.db.get_command(command_id)  # type: ignore

        cmd = self.db.get_command(command_id)  # type: ignore

        # 2. Stage 2 CAS Re-verification
        cas_error = self._verify_cas_stage2(cmd.target)
        if cas_error:
            # Stage 2 failed: Deny command
            return self.db.transition_state(
                command_id,
                CommandState.DENIED.value,
                worker_id,
                reason=cas_error
            )

        # 3. Target Composer Safety Check
        safety = self.transport.check_composer_safe(cmd.target)
        if not safety.is_safe:
            return self.db.transition_state(
                command_id,
                CommandState.DENIED.value,
                worker_id,
                reason=safety.reason
            )

        # 4. Transition to DISPATCHING
        self.db.transition_state(
            command_id,
            CommandState.DISPATCHING.value,
            worker_id,
            reason="Pre-send verification passed; initiating transport dispatch"
        )
        cmd = self.db.get_command(command_id)  # type: ignore

        # 5. Transport Dispatch
        delivery_id = f"del-{uuid.uuid4().hex[:12]}"
        try:
            result = self.transport.dispatch_command(cmd)
            if result.success and result.status == "CONFIRMED":
                self.db.record_delivery_attempt(
                    delivery_id=delivery_id,
                    command_id=command_id,
                    attempt_number=1,
                    outcome="CONFIRMED",
                    receipt_digest=result.receipt_digest,
                    readback_status="CONFIRMED",
                    message=result.message,
                )
                return self.db.transition_state(
                    command_id,
                    CommandState.DELIVERED_CONFIRMED.value,
                    worker_id,
                    reason="Transport confirmed delivery",
                    receipt_digest=result.receipt_digest
                )
            else:
                # Timeout / Ambiguous outcome -> DELIVERY_UNCERTAIN
                self.db.record_delivery_attempt(
                    delivery_id=delivery_id,
                    command_id=command_id,
                    attempt_number=1,
                    outcome=result.status,
                    receipt_digest=None,
                    readback_status="UNCERTAIN",
                    message=result.message,
                )
                return self.db.transition_state(
                    command_id,
                    CommandState.DELIVERY_UNCERTAIN.value,
                    worker_id,
                    reason=f"Transport returned uncertain status: {result.status} ({result.message})"
                )
        except Exception as exc:
            # Process crash / unexpected exception -> DELIVERY_UNCERTAIN
            self.db.record_delivery_attempt(
                delivery_id=delivery_id,
                command_id=command_id,
                attempt_number=1,
                outcome="CRASH_EXCEPTION",
                receipt_digest=None,
                readback_status="UNCERTAIN",
                message=str(exc),
            )
            return self.db.transition_state(
                command_id,
                CommandState.DELIVERY_UNCERTAIN.value,
                worker_id,
                reason=f"Transport invocation error: {exc}"
            )

    def _verify_cas_stage2(self, target: TargetIdentity) -> Optional[str]:
        """Stage 2 check immediately before dispatch. Returns error message or None."""
        if self.registry:
            work = self.registry.works.get(target.work_id)
            if not work or work.label_sha != target.expected_label_sha:
                return "AIM_LABEL_CONFLICT: AIM plan label changed before dispatch"

            run = self.registry.runs.get(target.run_id)
            if not run or run.generation != target.binding_generation:
                return "GENERATION_CONFLICT: Agent run generation changed before dispatch"

            if run.run_state in ("SUPERSEDED", "INTERRUPTED", "SUCCEEDED", "FAILED"):
                return f"GENERATION_CONFLICT: Agent run state is {run.run_state}"

            assign_runs = [r for r in self.registry.runs.values() if r.assignment_id == target.assignment_id]
            assign_runs.sort(key=lambda x: x.generation, reverse=True)
            if assign_runs and assign_runs[0].generation != target.binding_generation:
                return f"GENERATION_CONFLICT: Assignment run generation advanced to {assign_runs[0].generation}"

            conflicts = self.registry.validate_single_active_tab_invariants()
            if conflicts:
                return f"ONE_ACTIVE_TAB_CONFLICT: {'; '.join(conflicts)}"

        obs = self.live_observations.get(target.assignment_id)
        if obs:
            if obs.get("binding_generation") and obs["binding_generation"] != target.binding_generation:
                return "GENERATION_CONFLICT: Live coordinator generation advanced before dispatch"
            if obs.get("chat_id") and obs["chat_id"] != target.chat_id:
                return "CHAT_ID_CONFLICT: Active chat switched before dispatch"
            status = obs.get("status", "")
            if "HOLD" in status or "OUT" in status:
                return f"COORDINATOR_HOLD: Work entered '{status}' before dispatch"

        return None

    def reconcile_uncertain_command(
        self,
        command_id: str,
        actor: str = "OWNER"
    ) -> OwnerCommandRecord:
        """
        Reconciles a DELIVERY_UNCERTAIN command using transport readback.
        - Positive proof -> DELIVERED_CONFIRMED.
        - Conclusive negative proof -> DENIED (releasing single-flight slot for clean retry).
        - Inconclusive -> Retains DELIVERY_UNCERTAIN.
        """
        cmd = self.db.get_command(command_id)
        if not cmd:
            raise KeyError(f"Command not found: {command_id}")

        if cmd.state != CommandState.DELIVERY_UNCERTAIN.value:
            return cmd

        readback = self.transport.readback_delivery(cmd.target, cmd.correlation_id)
        if readback.found and readback.conclusive:
            return self.db.transition_state(
                command_id,
                CommandState.DELIVERED_CONFIRMED.value,
                actor,
                reason="Positive delivery confirmed via transport readback",
                receipt_digest=readback.evidence_sha
            )
        elif not readback.found and readback.conclusive:
            return self.db.transition_state(
                command_id,
                CommandState.DENIED.value,
                actor,
                reason="Conclusively confirmed not delivered via transport readback"
            )
        else:
            # Remains uncertain
            return cmd

    def cancel_command(
        self,
        command_id: str,
        actor: str = "OWNER",
        reason: str = "Cancelled by Owner"
    ) -> OwnerCommandRecord:
        """Cancels a QUEUED or RESERVED command prior to dispatch."""
        cmd = self.db.get_command(command_id)
        if not cmd:
            raise KeyError(f"Command not found: {command_id}")

        if cmd.state not in (CommandState.QUEUED.value, CommandState.RESERVED.value):
            raise CommandEngineError(f"Cannot cancel command in state '{cmd.state}'")

        return self.db.transition_state(
            command_id,
            CommandState.CANCELLED.value,
            actor,
            reason=reason
        )
