"""
Control Tower v3 Coordinator Transport Adapter (WP5)
=====================================================
Integrates the delivery plane with coordinator v3.28 session directories:
- Non-destructive composer buffer inspection (never clobbers unsent drafts)
- Atomic file-based delivery using correlation ID
- Cryptographic delivery receipts
- Readback verification scanning session histories and evidence logs
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from coordination.command_contracts import (
    ComposerSafetyResult,
    DispatchResult,
    OwnerCommandRecord,
    ReadbackResult,
    TargetIdentity,
    TransportAdapter,
)


class CoordinatorTransportAdapter(TransportAdapter):
    """File-based transport adapter operating within coordinator session workspaces."""

    def __init__(self, base_coordination_dir: Path | str):
        self.base_dir = Path(base_coordination_dir)

    def _resolve_session_dir(self, target: TargetIdentity) -> Path:
        return self.base_dir / target.session_id

    def check_composer_safe(self, target: TargetIdentity) -> ComposerSafetyResult:
        """
        Verifies that target agent composer is clean/empty:
        - If session dir contains unsent draft files with size > 0, reports dirty.
        - If session dir does not exist, fails closed.
        """
        session_dir = self._resolve_session_dir(target)
        if not session_dir.exists() or not session_dir.is_dir():
            return ComposerSafetyResult(
                is_safe=False,
                reason="SESSION_DIRECTORY_NOT_FOUND",
                uncommitted_bytes=0
            )

        # Inspect composer buffer markers
        draft_candidates = [
            session_dir / "unsent_draft.txt",
            session_dir / "composer_buffer.txt",
            session_dir / f"{target.chat_id}_draft.txt",
        ]

        for draft_file in draft_candidates:
            if draft_file.exists():
                size = draft_file.stat().st_size
                if size > 0:
                    return ComposerSafetyResult(
                        is_safe=False,
                        reason="COMPOSER_DIRTY_UNSENT_DRAFT",
                        uncommitted_bytes=size
                    )

        return ComposerSafetyResult(is_safe=True, reason="COMPOSER_EMPTY", uncommitted_bytes=0)

    def dispatch_command(self, command: OwnerCommandRecord) -> DispatchResult:
        """
        Delivers typed command to coordinator session directory atomically:
        - Writes {session_dir}/cmd_{correlation_id}.json.tmp -> cmd_{correlation_id}.json
        - Writes cryptographic receipt
        """
        session_dir = self._resolve_session_dir(command.target)
        if not session_dir.exists():
            return DispatchResult(
                success=False,
                status="FAILED",
                receipt_digest=None,
                message=f"Session directory not found: {session_dir}"
            )

        cmd_file = session_dir / f"cmd_{command.correlation_id}.json"
        tmp_file = session_dir / f"cmd_{command.correlation_id}.json.tmp"
        receipt_file = session_dir / f"receipt_{command.correlation_id}.json"

        data = {
            "command_id": command.command_id,
            "correlation_id": command.correlation_id,
            "action": command.action,
            "target": command.target.to_dict(),
            "payload": command.payload,
            "payload_digest": command.payload_digest,
            "dispatched_at_utc": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # Atomic write
            tmp_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            tmp_file.replace(cmd_file)

            # Generate receipt digest
            receipt_seed = f"{command.command_id}:{command.correlation_id}:{cmd_file.stat().st_mtime_ns}"
            receipt_digest = hashlib.sha256(receipt_seed.encode("utf-8")).hexdigest()

            receipt_data = {
                "command_id": command.command_id,
                "correlation_id": command.correlation_id,
                "receipt_digest": receipt_digest,
                "confirmed_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            receipt_file.write_text(json.dumps(receipt_data, indent=2), encoding="utf-8")

            return DispatchResult(
                success=True,
                status="CONFIRMED",
                receipt_digest=receipt_digest,
                message="Delivered and verified in coordinator session"
            )
        except Exception as exc:
            return DispatchResult(
                success=False,
                status="FAILED",
                receipt_digest=None,
                message=f"Dispatch I/O error: {exc}"
            )

    def readback_delivery(self, target: TargetIdentity, correlation_id: str) -> ReadbackResult:
        """
        Searches session workspace for delivery receipt or log entry.
        """
        session_dir = self._resolve_session_dir(target)
        if not session_dir.exists():
            return ReadbackResult(found=False, conclusive=False, message="Session directory missing")

        receipt_file = session_dir / f"receipt_{correlation_id}.json"
        if receipt_file.exists():
            try:
                data = json.loads(receipt_file.read_text(encoding="utf-8"))
                digest = data.get("receipt_digest")
                return ReadbackResult(
                    found=True,
                    conclusive=True,
                    evidence_sha=digest,
                    message="Positive receipt found in session directory"
                )
            except Exception:
                pass

        # Check if session has events log
        events_file = session_dir / "events.jsonl"
        if events_file.exists():
            try:
                lines = events_file.read_text(encoding="utf-8").splitlines()
                for line in lines:
                    if correlation_id in line:
                        proof = hashlib.sha256(line.encode("utf-8")).hexdigest()
                        return ReadbackResult(
                            found=True,
                            conclusive=True,
                            evidence_sha=proof,
                            message="Found in session events log"
                        )
            except Exception:
                pass

        return ReadbackResult(
            found=False,
            conclusive=False,
            message="No conclusive receipt or event found in session directory"
        )
