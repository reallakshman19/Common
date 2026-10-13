"""
Control Tower v3 Authenticated Owner Command HTTP Service (WP5)
================================================================
Provides:
- Dedicated loopback HTTP API (/api/v3/owner/...)
- Constant-time Bearer token authentication (hmac.compare_digest)
- Token rotation support (primary and previous token)
- Zero token logging
- Request size limit (64 KB)
- Host and Origin / CSRF protections (rejects external cross-origin browser requests)
- Strict typed-action JSON schema validation
- Routes for command submission, status query, cancellation, readback reconciliation, and Owner Inbox
"""
from __future__ import annotations

import hmac
import http.server
import json
import os
import re
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from coordination.command_contracts import (
    CommandAction,
    CommandState,
    NoOpTransportAdapter,
    OwnerCommandRecord,
    TargetIdentity,
    compute_payload_digest,
)
from coordination.command_db import CommandDatabase, DEFAULT_COMMAND_DB_PATH
from coordination.command_engine import (
    CASConflictError,
    CommandEngine,
    CommandEngineError,
    DecisionCardRequiredError,
    IdempotencyConflictError,
    SingleFlightConflictError,
)

MAX_COMMAND_BODY_BYTES = 64 * 1024  # 64 KB request size cap
DEFAULT_SERVER_HOSTS = {"127.0.0.1", "localhost", "::1"}


class CommandServiceHandler(http.server.BaseHTTPRequestHandler):
    """HTTP Request Handler for Control Tower Authenticated Command Plane."""

    command_engine: CommandEngine
    owner_token: str
    previous_owner_token: Optional[str] = None
    allowed_hosts: set[str] = DEFAULT_SERVER_HOSTS

    def log_message(self, fmt, *args):
        # Suppress logging of sensitive tokens or internal routing details
        pass

    def _send_common_headers(self, content_type: str, length: int):
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'none'; style-src 'none'; object-src 'none';"
        )

    def send_json(self, obj: Any, status: int = 200):
        body = json.dumps(obj, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self._send_common_headers("application/json", len(body))
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, text: str, status: int = 200):
        body = text.encode("utf-8", errors="replace")
        self.send_response(status)
        self._send_common_headers("text/plain; charset=utf-8", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _verify_auth(self) -> bool:
        """Verifies Bearer token with constant-time equality. Never logs token."""
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return False
        token = auth_header[7:].strip()
        if not token:
            return False

        # Constant-time comparison
        valid = hmac.compare_digest(token, self.owner_token)
        if not valid and self.previous_owner_token:
            valid = hmac.compare_digest(token, self.previous_owner_token)
        return valid

    def _verify_network_and_origin(self) -> Tuple[bool, str]:
        """Validates Host and Origin headers to prevent DNS rebinding and cross-origin attacks."""
        host_header = self.headers.get("Host", "").split(":")[0].strip()
        if host_header not in self.allowed_hosts:
            return False, "Invalid Host header (DNS rebinding protection)"

        origin = self.headers.get("Origin")
        if origin:
            parsed = urllib.parse.urlparse(origin)
            if parsed.hostname not in self.allowed_hosts:
                return False, f"Cross-origin requests forbidden: {origin}"

        return True, ""

    def do_GET(self):
        # 1. Null-byte rejection
        if "\x00" in self.path:
            self.send_text("Invalid request path", status=400)
            return

        # 2. Host & Origin validation
        ok, msg = self._verify_network_and_origin()
        if not ok:
            self.send_text(msg, status=400)
            return

        # 3. Authentication barrier
        if not self._verify_auth():
            self.send_json({"error": "Unauthorized", "detail": "Valid Bearer token required"}, status=401)
            return

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        qs = urllib.parse.parse_qs(parsed.query)

        # GET /api/v3/owner/inbox
        if path == "/api/v3/owner/inbox":
            inbox_data = self.command_engine.db.get_owner_inbox()
            self.send_json({"ok": True, "inbox": inbox_data}, status=200)
            return

        # GET /api/v3/owner/commands
        if path == "/api/v3/owner/commands":
            proj = qs.get("project_id", [None])[0]
            assign = qs.get("assignment_id", [None])[0]
            state = qs.get("state", [None])[0]
            limit = min(100, max(1, int(qs.get("limit", [50])[0])))
            offset = max(0, int(qs.get("offset", [0])[0]))

            cmds = self.command_engine.db.list_commands(
                project_id=proj, assignment_id=assign, state=state, limit=limit, offset=offset
            )
            self.send_json({
                "ok": True,
                "count": len(cmds),
                "commands": [c.to_dict() for c in cmds]
            }, status=200)
            return

        # GET /api/v3/owner/commands/<command_id>
        m = re.match(r"^/api/v3/owner/commands/(cmd-[a-zA-Z0-9_-]{8,64})$", path)
        if m:
            cmd_id = m.group(1)
            cmd = self.command_engine.db.get_command(cmd_id)
            if not cmd:
                self.send_json({"error": "Not Found", "detail": f"Command {cmd_id} not found"}, status=404)
                return
            journal = self.command_engine.db.get_journal(cmd_id)
            self.send_json({
                "ok": True,
                "command": cmd.to_dict(),
                "journal": [
                    {
                        "journal_id": j.journal_id,
                        "from_state": j.from_state,
                        "to_state": j.to_state,
                        "actor": j.actor,
                        "reason": j.reason,
                        "receipt_digest": j.receipt_digest,
                        "transition_at_utc": j.transition_at_utc,
                    }
                    for j in journal
                ]
            }, status=200)
            return

        self.send_json({"error": "Not Found"}, status=404)

    def do_POST(self):
        # 1. Null-byte rejection
        if "\x00" in self.path:
            self.send_text("Invalid request path", status=400)
            return

        # 2. Host & Origin validation
        ok, msg = self._verify_network_and_origin()
        if not ok:
            self.send_text(msg, status=400)
            return

        # 3. Authentication barrier
        if not self._verify_auth():
            self.send_json({"error": "Unauthorized", "detail": "Valid Bearer token required"}, status=401)
            return

        # 4. Request size cap (64 KB)
        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (ValueError, TypeError):
            content_length = 0

        if content_length > MAX_COMMAND_BODY_BYTES:
            self.send_json(
                {"error": "Payload Too Large", "detail": f"Max request size is {MAX_COMMAND_BODY_BYTES} bytes"},
                status=413
            )
            return

        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            payload_data = json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json({"error": "Bad Request", "detail": "Invalid JSON body"}, status=400)
            return

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        # POST /api/v3/owner/commands
        if path == "/api/v3/owner/commands":
            self._handle_submit_command(payload_data)
            return

        # POST /api/v3/owner/commands/<command_id>/cancel
        m_cancel = re.match(r"^/api/v3/owner/commands/(cmd-[a-zA-Z0-9_-]{8,64})/cancel$", path)
        if m_cancel:
            cmd_id = m_cancel.group(1)
            try:
                cancelled = self.command_engine.cancel_command(cmd_id, actor="OWNER")
                self.send_json({"ok": True, "command": cancelled.to_dict()}, status=200)
            except KeyError:
                self.send_json({"error": "Not Found", "detail": f"Command {cmd_id} not found"}, status=404)
            except CommandEngineError as exc:
                self.send_json({"error": "Conflict", "detail": str(exc)}, status=409)
            return

        # POST /api/v3/owner/commands/<command_id>/reconcile
        m_recon = re.match(r"^/api/v3/owner/commands/(cmd-[a-zA-Z0-9_-]{8,64})/reconcile$", path)
        if m_recon:
            cmd_id = m_recon.group(1)
            try:
                reconciled = self.command_engine.reconcile_uncertain_command(cmd_id, actor="OWNER")
                self.send_json({"ok": True, "command": reconciled.to_dict()}, status=200)
            except KeyError:
                self.send_json({"error": "Not Found", "detail": f"Command {cmd_id} not found"}, status=404)
            return

        self.send_json({"error": "Not Found"}, status=404)

    def _handle_submit_command(self, data: Dict[str, Any]):
        # Validate required fields
        required = ["command_id", "idempotency_key", "action", "target", "payload"]
        for field in required:
            if field not in data:
                self.send_json({"error": "Bad Request", "detail": f"Missing required field: {field}"}, status=400)
                return

        # Strict Typed Action Allowlist check
        valid_actions = [a.value for a in CommandAction]
        if data["action"] not in valid_actions:
            self.send_json(
                {"error": "Bad Request", "detail": f"Invalid action: {data['action']}. Must be one of {valid_actions}"},
                status=400
            )
            return

        # Security check on instruction content: No arbitrary scripts or path traversal
        instruction = data["payload"].get("instruction", "")
        if any(bad in instruction for bad in ["Invoke-Expression", "powershell -enc", "rm -rf", "../../"]):
            self.send_json(
                {"error": "Bad Request", "detail": "Arbitrary command execution patterns are strictly forbidden"},
                status=400
            )
            return

        try:
            target = TargetIdentity.from_dict(data["target"])
            target.validate()

            correlation_id = data.get("correlation_id") or f"cid-{data['command_id'].replace('cmd-', '')}"
            payload_digest = compute_payload_digest(data["payload"])
            now_utc = datetime.now(timezone.utc).isoformat()

            cmd = OwnerCommandRecord(
                command_id=data["command_id"],
                idempotency_key=data["idempotency_key"],
                correlation_id=correlation_id,
                authenticated_actor="OWNER",
                action=data["action"],
                target=target,
                payload=data["payload"],
                payload_digest=payload_digest,
                state=CommandState.DRAFT.value,
                created_at_utc=now_utc,
                updated_at_utc=now_utc,
                decision_card_id=data["payload"].get("decision_card_id"),
                decision_outcome=data["payload"].get("decision_outcome"),
            )

            # Submit through engine
            queued_cmd, is_new = self.command_engine.submit_command(cmd, actor="OWNER")

            # Attempt immediate dispatch if auto-dispatch requested
            auto_dispatch = data.get("auto_dispatch", True)
            if auto_dispatch and is_new and queued_cmd.state == CommandState.QUEUED.value:
                final_cmd = self.command_engine.reserve_and_dispatch(queued_cmd.command_id)
            else:
                final_cmd = queued_cmd

            status_code = 201 if is_new else 200
            self.send_json({"ok": True, "is_new": is_new, "command": final_cmd.to_dict()}, status=status_code)

        except (ValueError, KeyError) as exc:
            self.send_json({"error": "Bad Request", "detail": str(exc)}, status=400)
        except DecisionCardRequiredError as exc:
            self.send_json({"error": "Unprocessable Entity", "detail": str(exc)}, status=422)
        except (IdempotencyConflictError, SingleFlightConflictError, CASConflictError) as exc:
            self.send_json({"error": "Conflict", "detail": str(exc)}, status=409)
        except Exception as exc:
            self.send_json({"error": "Internal Error", "detail": str(exc)}, status=500)
