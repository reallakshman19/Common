"""
Control Tower v3 Coordinator Transport Adapter (WP5)
=====================================================
Integrates the delivery plane with coordinator v3.28 session directories:
- Non-destructive composer buffer inspection (never clobbers unsent drafts)
- Explicitly no file-based SEND: v3.28 has no verified command consumer
- No fabricated cryptographic receipt or sender-created acknowledgment
- Fail-closed composer inspection until browser/IDE transport is verified
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
    """Fail-closed v3.28 compatibility boundary; not an active SEND adapter."""

    def __init__(self, base_coordination_dir: Path | str):
        self.base_dir = Path(base_coordination_dir)

    def _resolve_session_dir(self, target: TargetIdentity) -> Path:
        # Session names are identifiers, never arbitrary relative or absolute paths.
        import re
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", target.session_id):
            raise ValueError("Unsafe coordinator session identifier")
        base = self.base_dir.resolve()
        candidate = base / target.session_id
        if candidate.is_symlink() or not candidate.resolve().is_relative_to(base):
            raise ValueError("Coordinator session escapes approved root")
        return candidate

    def check_composer_safe(self, target: TargetIdentity) -> ComposerSafetyResult:
        """A filesystem draft marker is NOT an authoritative browser composer check."""
        try:
            session_dir = self._resolve_session_dir(target)
            if not session_dir.is_dir():
                return ComposerSafetyResult(False, "SESSION_DIRECTORY_NOT_FOUND")
            for filename in ("unsent_draft.txt", "composer_buffer.txt",
                             f"{target.chat_id}_draft.txt"):
                file = session_dir / filename
                if file.is_symlink():
                    return ComposerSafetyResult(False, "UNTRUSTED_DRAFT_SYMLINK")
                if file.is_file() and file.stat().st_size:
                    return ComposerSafetyResult(False, "COMPOSER_DIRTY_UNSENT_DRAFT",
                                                file.stat().st_size)
        except (ValueError, OSError):
            return ComposerSafetyResult(False, "COMPOSER_VERIFICATION_FAILED")
        # No approved browser/IDE adapter exists that can verify an actual
        # composer reservation. Never infer "empty" from absent files.
        return ComposerSafetyResult(False, "COMPOSER_VERIFICATION_UNAVAILABLE")

    def dispatch_command(self, command: OwnerCommandRecord) -> DispatchResult:
        """Fail closed: writing a JSON file is not delivery to an agent.

        The v3.28 coordinator has no registered command-consumer or trusted
        readback protocol. An adapter with real composer-state inspection and
        independently generated acknowledgments must be separately delivered.
        """
        return DispatchResult(False, "UNSUPPORTED_TRANSPORT", None,
                              "No verified v3.28 command delivery consumer installed")

    def readback_delivery(self, target: TargetIdentity, correlation_id: str) -> ReadbackResult:
        # The former implementation trusted sender-created receipt files and
        # substring matches in events.jsonl, which are NOT delivery evidence.
        return ReadbackResult(False, False, None,
                              "No independently authenticated consumer receipt available")
