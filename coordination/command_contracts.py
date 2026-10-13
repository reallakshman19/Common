"""
Control Tower v3 Owner Command Contracts & Transport Interfaces (WP5)
=======================================================================
Implements the typed command plane contracts:
- 11-part TargetIdentity composite tuple
- Typed actions: DIRECTIVE, DECISION_RESOLVE, RECON_MODE, PAUSE_WORK, RESUME_WORK
- Command states: DRAFT, ACCEPTED, QUEUED, RESERVED, DISPATCHING,
                  DELIVERED_CONFIRMED, DELIVERY_UNCERTAIN, DENIED, CANCELLED
- Downstream independent observations: ACKNOWLEDGED, ADOPTED
- Pluggable TransportAdapter interface and NoOpTransportAdapter (dry-run)
- Immutable Transition Journal entry dataclass
"""
from __future__ import annotations

import hashlib
import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class CommandAction(str, Enum):
    DIRECTIVE = "DIRECTIVE"
    DECISION_RESOLVE = "DECISION_RESOLVE"
    RECON_MODE = "RECON_MODE"
    PAUSE_WORK = "PAUSE_WORK"
    RESUME_WORK = "RESUME_WORK"


class CommandState(str, Enum):
    DRAFT = "DRAFT"
    ACCEPTED = "ACCEPTED"
    QUEUED = "QUEUED"
    RESERVED = "RESERVED"
    DISPATCHING = "DISPATCHING"
    DELIVERED_CONFIRMED = "DELIVERED_CONFIRMED"
    DELIVERY_UNCERTAIN = "DELIVERY_UNCERTAIN"
    DENIED = "DENIED"
    CANCELLED = "CANCELLED"


# Active states that hold the single-flight reservation slot per assignment
SINGLE_FLIGHT_ACTIVE_STATES = {
    CommandState.QUEUED.value,
    CommandState.RESERVED.value,
    CommandState.DISPATCHING.value,
    CommandState.DELIVERY_UNCERTAIN.value,
}

TERMINAL_STATES = {
    CommandState.DELIVERED_CONFIRMED.value,
    CommandState.DENIED.value,
    CommandState.CANCELLED.value,
}


@dataclass(frozen=True)
class TargetIdentity:
    """Authoritative 11-part composite identity tuple."""
    project_id: str
    work_id: str
    lane_id: str
    assignment_id: str
    run_id: str
    binding_id: str
    coordinator_id: str
    session_id: str
    chat_id: str
    binding_generation: int
    expected_label_sha: str

    def validate(self):
        if not self.project_id or not self.project_id.strip():
            raise ValueError("project_id cannot be empty")
        if not self.work_id or not self.work_id.strip():
            raise ValueError("work_id cannot be empty")
        if not self.lane_id or not self.lane_id.strip():
            raise ValueError("lane_id cannot be empty")
        if not self.assignment_id or not self.assignment_id.strip():
            raise ValueError("assignment_id cannot be empty")
        if not self.run_id or not self.run_id.strip():
            raise ValueError("run_id cannot be empty")
        if not self.binding_id or not self.binding_id.strip():
            raise ValueError("binding_id cannot be empty")
        if not self.coordinator_id or not self.coordinator_id.strip():
            raise ValueError("coordinator_id cannot be empty")
        if not self.session_id or not self.session_id.strip():
            raise ValueError("session_id cannot be empty")
        if not self.chat_id or not self.chat_id.strip():
            raise ValueError("chat_id cannot be empty")
        if self.binding_generation < 1:
            raise ValueError("binding_generation must be >= 1")
        if not re.fullmatch(r"(?:[0-9a-fA-F]{7}|[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", self.expected_label_sha):
            raise ValueError(f"Invalid expected_label_sha format: {self.expected_label_sha}")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TargetIdentity:
        return cls(
            project_id=str(data["project_id"]),
            work_id=str(data["work_id"]),
            lane_id=str(data["lane_id"]),
            assignment_id=str(data["assignment_id"]),
            run_id=str(data["run_id"]),
            binding_id=str(data["binding_id"]),
            coordinator_id=str(data["coordinator_id"]),
            session_id=str(data["session_id"]),
            chat_id=str(data["chat_id"]),
            binding_generation=int(data["binding_generation"]),
            expected_label_sha=str(data["expected_label_sha"]),
        )


def canonical_json(obj: Any) -> str:
    """Deterministic, sorted JSON serialization."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_payload_digest(payload: Dict[str, Any]) -> str:
    """Computes SHA-256 digest over canonical JSON representation."""
    raw = canonical_json(payload).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def compute_idempotency_scope_key(
    authenticated_actor: str,
    assignment_id: str,
    action: str,
    payload_digest: str
) -> str:
    """
    Computes scoped idempotency hash:
    (authenticated_actor, assignment_id, action, payload_digest)
    """
    seed = f"{authenticated_actor}|{assignment_id}|{action}|{payload_digest}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


@dataclass
class OwnerCommandRecord:
    command_id: str
    idempotency_key: str
    correlation_id: str
    authenticated_actor: str
    action: str
    target: TargetIdentity
    payload: Dict[str, Any]
    payload_digest: str
    state: str
    created_at_utc: str
    updated_at_utc: str
    denial_reason: Optional[str] = None
    decision_card_id: Optional[str] = None
    decision_outcome: Optional[str] = None
    reserved_by: Optional[str] = None
    reserved_at_utc: Optional[str] = None
    lease_expires_at_utc: Optional[str] = None

    def validate(self):
        if not re.fullmatch(r"cmd-[a-zA-Z0-9_-]{8,64}", self.command_id):
            raise ValueError(f"Invalid command_id format: {self.command_id}")
        if not re.fullmatch(r"cid-[a-zA-Z0-9_-]{8,64}", self.correlation_id):
            raise ValueError(f"Invalid correlation_id format: {self.correlation_id}")
        if not (8 <= len(self.idempotency_key) <= 128):
            raise ValueError(f"idempotency_key length must be between 8 and 128: {self.idempotency_key}")
        if self.authenticated_actor not in ("OWNER", "OWNER_DELEGATE"):
            raise ValueError(f"Invalid authenticated_actor: {self.authenticated_actor}")
        if self.action not in [a.value for a in CommandAction]:
            raise ValueError(f"Invalid action: {self.action}")
        if self.state not in [s.value for s in CommandState]:
            raise ValueError(f"Invalid state: {self.state}")
        self.target.validate()
        if not isinstance(self.payload, dict):
            raise ValueError("Command payload must be an object")
        allowed = {"instruction", "decision_card_id", "decision_outcome",
                   "recon_probe_type", "parameters"}
        if any(key not in allowed for key in self.payload):
            raise ValueError("Unsupported command payload field")
        instruction = self.payload.get("instruction")
        if not isinstance(instruction, str) or not 1 <= len(instruction) <= 4096:
            raise ValueError("Instruction must be 1..4096 characters")
        if self.payload.get("parameters"):
            raise ValueError("Executable command parameters are unsupported")
        if self.action == CommandAction.DECISION_RESOLVE.value:
            if "decision_card_id" not in self.payload or "decision_outcome" not in self.payload:
                raise ValueError("Decision card fields must be part of the audited payload")

        expected_digest = compute_payload_digest(self.payload)
        if self.payload_digest != expected_digest:
            raise ValueError(f"Payload digest mismatch: {self.payload_digest} != {expected_digest}")

        if self.action == CommandAction.DECISION_RESOLVE.value:
            card_id = self.payload.get("decision_card_id") or self.decision_card_id
            outcome = self.payload.get("decision_outcome") or self.decision_outcome
            if not card_id or not outcome:
                raise ValueError("DECISION_RESOLVE requires decision_card_id and decision_outcome")
            if not re.fullmatch(r"card-[a-zA-Z0-9_-]{4,64}", card_id):
                raise ValueError(f"Invalid decision_card_id format: {card_id}")
            if outcome not in ("APPROVED", "REJECTED", "MODIFIED", "DEFERRED"):
                raise ValueError(f"Invalid decision_outcome: {outcome}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command_id": self.command_id,
            "idempotency_key": self.idempotency_key,
            "correlation_id": self.correlation_id,
            "authenticated_actor": self.authenticated_actor,
            "action": self.action,
            "target": self.target.to_dict(),
            "payload": self.payload,
            "payload_digest": self.payload_digest,
            "state": self.state,
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
            "denial_reason": self.denial_reason,
            "decision_card_id": self.decision_card_id,
            "decision_outcome": self.decision_outcome,
            "reserved_by": self.reserved_by,
            "reserved_at_utc": self.reserved_at_utc,
            "lease_expires_at_utc": self.lease_expires_at_utc,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OwnerCommandRecord:
        target = TargetIdentity.from_dict(data["target"]) if isinstance(data["target"], dict) else data["target"]
        return cls(
            command_id=data["command_id"],
            idempotency_key=data["idempotency_key"],
            correlation_id=data["correlation_id"],
            authenticated_actor=data["authenticated_actor"],
            action=data["action"],
            target=target,
            payload=data["payload"],
            payload_digest=data["payload_digest"],
            state=data["state"],
            created_at_utc=data["created_at_utc"],
            updated_at_utc=data["updated_at_utc"],
            denial_reason=data.get("denial_reason"),
            decision_card_id=data.get("decision_card_id"),
            decision_outcome=data.get("decision_outcome"),
            reserved_by=data.get("reserved_by"),
            reserved_at_utc=data.get("reserved_at_utc"),
            lease_expires_at_utc=data.get("lease_expires_at_utc"),
        )


@dataclass
class CommandTransition:
    """Immutable record of an append-only state transition."""
    command_id: str
    from_state: str
    to_state: str
    actor: str
    transition_at_utc: str
    reason: Optional[str] = None
    receipt_digest: Optional[str] = None
    journal_id: Optional[int] = None


@dataclass
class ComposerSafetyResult:
    is_safe: bool
    reason: str
    uncommitted_bytes: int = 0


@dataclass
class DispatchResult:
    success: bool
    status: str  # CONFIRMED, UNCERTAIN, FAILED, TIMEOUT
    receipt_digest: Optional[str] = None
    message: str = ""


@dataclass
class ReadbackResult:
    found: bool
    conclusive: bool
    evidence_sha: Optional[str] = None
    message: str = ""


class TransportAdapter(ABC):
    """Abstract interface for delivery transports."""

    @abstractmethod
    def check_composer_safe(self, target: TargetIdentity) -> ComposerSafetyResult:
        """Inspects target composer. Must report safe ONLY if composer is empty/clean."""
        pass

    @abstractmethod
    def dispatch_command(self, command: OwnerCommandRecord) -> DispatchResult:
        """Transmits command to target agent. Returns confirmation receipt or uncertain status."""
        pass

    @abstractmethod
    def readback_delivery(self, target: TargetIdentity, correlation_id: str) -> ReadbackResult:
        """Searches session history/evidence logs for the command's correlation ID."""
        pass


class NoOpTransportAdapter(TransportAdapter):
    """
    Deterministic dry-run transport adapter for Phase 1-3 testing.
    Records dispatches without mutating live browser sessions.
    Configurable to simulate timeouts, composer dirty states, and readback proofs.
    """

    def __init__(self):
        self.dispatched_commands: List[OwnerCommandRecord] = []
        self.simulate_dirty_composer: bool = False
        self.simulate_dirty_bytes: int = 42
        self.simulate_timeout: bool = False
        self.simulate_crash: bool = False
        self.known_readback: Dict[str, ReadbackResult] = {}

    def check_composer_safe(self, target: TargetIdentity) -> ComposerSafetyResult:
        if self.simulate_dirty_composer:
            return ComposerSafetyResult(
                is_safe=False,
                reason="COMPOSER_DIRTY_UNSENT_DRAFT",
                uncommitted_bytes=self.simulate_dirty_bytes,
            )
        return ComposerSafetyResult(is_safe=True, reason="COMPOSER_EMPTY", uncommitted_bytes=0)

    def dispatch_command(self, command: OwnerCommandRecord) -> DispatchResult:
        if self.simulate_crash:
            raise RuntimeError("Simulated process crash during transport dispatch")
        if self.simulate_timeout:
            return DispatchResult(
                success=False,
                status="TIMEOUT",
                receipt_digest=None,
                message="Transport timed out waiting for delivery receipt",
            )
        self.dispatched_commands.append(command)
        receipt_seed = f"{command.command_id}:{command.correlation_id}:{datetime.now(timezone.utc).isoformat()}"
        digest = hashlib.sha256(receipt_seed.encode("utf-8")).hexdigest()
        return DispatchResult(
            success=True,
            status="CONFIRMED",
            receipt_digest=digest,
            message="No-op delivery recorded successfully",
        )

    def readback_delivery(self, target: TargetIdentity, correlation_id: str) -> ReadbackResult:
        if correlation_id in self.known_readback:
            return self.known_readback[correlation_id]
        # By default, check if we dispatched it
        for cmd in self.dispatched_commands:
            if cmd.correlation_id == correlation_id:
                proof = hashlib.sha256(f"readback:{correlation_id}".encode("utf-8")).hexdigest()
                return ReadbackResult(found=True, conclusive=True, evidence_sha=proof, message="Found in dry-run log")
        return ReadbackResult(found=False, conclusive=False, message="Correlation ID not found in dry-run history")
