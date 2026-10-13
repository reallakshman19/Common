"""
Control Tower v3 Durable Command Store & SQLite WAL Ledger (WP5)
==================================================================
Provides:
- SQLite WAL mode with durable transactional boundaries (BEGIN IMMEDIATE)
- Database-enforced single-flight invariant:
    Partial unique index on assignment_id covering
    ('QUEUED', 'RESERVED', 'DISPATCHING', 'DELIVERY_UNCERTAIN')
- Scoped idempotency key enforcement
- Append-only transition journal with SQLite trigger mutation protection
- Delivery attempts, independent downstream acknowledgments, and adoptions
"""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from coordination.command_contracts import (
    CommandAction,
    CommandState,
    CommandTransition,
    OwnerCommandRecord,
    SINGLE_FLIGHT_ACTIVE_STATES,
    TargetIdentity,
    compute_payload_digest,
)

DEFAULT_COMMAND_DB_PATH = Path(__file__).parent / "command_index.db"


class CommandDatabase:
    """Thread-safe SQLite WAL interface for Control Tower Owner Commands."""

    def __init__(self, db_path: str | Path = DEFAULT_COMMAND_DB_PATH):
        self.db_path = str(db_path)
        self._lock = threading.RLock()
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(
                self.db_path,
                timeout=10.0,
                check_same_thread=False,
                isolation_level=None,  # Explicit transaction management
            )
            self._conn.row_factory = sqlite3.Row
            if self.db_path != ":memory:":
                self._conn.execute("PRAGMA journal_mode=WAL;")
                self._conn.execute("PRAGMA synchronous=NORMAL;")
            self._conn.execute("PRAGMA busy_timeout=5000;")
            self._conn.execute("PRAGMA foreign_keys=ON;")
        return self._conn

    def _init_db(self):
        with self._lock:
            conn = self.get_connection()
            conn.execute("BEGIN IMMEDIATE;")
            try:
                # 1. owner_commands table
                conn.execute("""
                CREATE TABLE IF NOT EXISTS owner_commands (
                    command_id TEXT PRIMARY KEY,
                    idempotency_key TEXT UNIQUE NOT NULL,
                    correlation_id TEXT UNIQUE NOT NULL,
                    authenticated_actor TEXT NOT NULL,
                    action TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    work_id TEXT NOT NULL,
                    lane_id TEXT NOT NULL,
                    assignment_id TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    binding_id TEXT NOT NULL,
                    coordinator_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    chat_id TEXT NOT NULL,
                    binding_generation INTEGER NOT NULL,
                    expected_label_sha TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_digest TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at_utc TEXT NOT NULL,
                    updated_at_utc TEXT NOT NULL,
                    denial_reason TEXT,
                    decision_card_id TEXT,
                    decision_outcome TEXT,
                    reserved_by TEXT,
                    reserved_at_utc TEXT,
                    lease_expires_at_utc TEXT
                );
                """)

                # Partial unique index enforcing single-flight per assignment
                conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_single_flight_per_assignment
                ON owner_commands(assignment_id)
                WHERE state IN ('QUEUED', 'RESERVED', 'DISPATCHING', 'DELIVERY_UNCERTAIN');
                """)

                # 2. command_transition_journal table (Append-Only)
                conn.execute("""
                CREATE TABLE IF NOT EXISTS command_transition_journal (
                    journal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_id TEXT NOT NULL,
                    from_state TEXT NOT NULL,
                    to_state TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    reason TEXT,
                    receipt_digest TEXT,
                    transition_at_utc TEXT NOT NULL,
                    FOREIGN KEY(command_id) REFERENCES owner_commands(command_id)
                );
                """)

                # Triggers enforcing append-only immutability
                conn.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_no_update_journal
                BEFORE UPDATE ON command_transition_journal
                BEGIN
                    SELECT RAISE(ABORT, 'Mutation forbidden: command_transition_journal is append-only');
                END;
                """)

                conn.execute("""
                CREATE TRIGGER IF NOT EXISTS trg_no_delete_journal
                BEFORE DELETE ON command_transition_journal
                BEGIN
                    SELECT RAISE(ABORT, 'Deletion forbidden: command_transition_journal is append-only');
                END;
                """)

                # 3. command_deliveries table
                conn.execute("""
                CREATE TABLE IF NOT EXISTS command_deliveries (
                    delivery_id TEXT PRIMARY KEY,
                    command_id TEXT NOT NULL,
                    attempt_number INTEGER NOT NULL,
                    dispatched_at_utc TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    receipt_digest TEXT,
                    readback_status TEXT,
                    readback_at_utc TEXT,
                    message TEXT,
                    FOREIGN KEY(command_id) REFERENCES owner_commands(command_id)
                );
                """)

                # 4. command_acknowledgments table (Independent downstream observations)
                conn.execute("""
                CREATE TABLE IF NOT EXISTS command_acknowledgments (
                    ack_id TEXT PRIMARY KEY,
                    command_id TEXT NOT NULL,
                    correlation_id TEXT NOT NULL,
                    ack_evidence_sha TEXT NOT NULL,
                    ack_at_utc TEXT NOT NULL,
                    recorded_at_utc TEXT NOT NULL,
                    FOREIGN KEY(command_id) REFERENCES owner_commands(command_id)
                );
                """)

                # 5. command_adoptions table (Independent downstream observations)
                conn.execute("""
                CREATE TABLE IF NOT EXISTS command_adoptions (
                    adoption_id TEXT PRIMARY KEY,
                    command_id TEXT NOT NULL,
                    correlation_id TEXT NOT NULL,
                    adoption_evidence_sha TEXT NOT NULL,
                    adopted_at_utc TEXT NOT NULL,
                    recorded_at_utc TEXT NOT NULL,
                    FOREIGN KEY(command_id) REFERENCES owner_commands(command_id)
                );
                """)

                conn.execute("COMMIT;")
            except Exception:
                conn.execute("ROLLBACK;")
                raise

    def close(self):
        with self._lock:
            if self._conn is not None:
                self._conn.close()
                self._conn = None

    def insert_command(self, cmd: OwnerCommandRecord, actor: str) -> None:
        """Atomically inserts an accepted command into QUEUED state and logs journal entry."""
        cmd.validate()
        with self._lock:
            conn = self.get_connection()
            conn.execute("BEGIN IMMEDIATE;")
            try:
                conn.execute("""
                INSERT INTO owner_commands (
                    command_id, idempotency_key, correlation_id, authenticated_actor,
                    action, project_id, work_id, lane_id, assignment_id, run_id,
                    binding_id, coordinator_id, session_id, chat_id, binding_generation,
                    expected_label_sha, payload_json, payload_digest, state,
                    created_at_utc, updated_at_utc, denial_reason, decision_card_id,
                    decision_outcome, reserved_by, reserved_at_utc, lease_expires_at_utc
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                );
                """, (
                    cmd.command_id, cmd.idempotency_key, cmd.correlation_id, cmd.authenticated_actor,
                    cmd.action, cmd.target.project_id, cmd.target.work_id, cmd.target.lane_id,
                    cmd.target.assignment_id, cmd.target.run_id, cmd.target.binding_id,
                    cmd.target.coordinator_id, cmd.target.session_id, cmd.target.chat_id,
                    cmd.target.binding_generation, cmd.target.expected_label_sha,
                    json.dumps(cmd.payload, sort_keys=True), cmd.payload_digest, cmd.state,
                    cmd.created_at_utc, cmd.updated_at_utc, cmd.denial_reason, cmd.decision_card_id,
                    cmd.decision_outcome, cmd.reserved_by, cmd.reserved_at_utc, cmd.lease_expires_at_utc
                ))

                conn.execute("""
                INSERT INTO command_transition_journal (
                    command_id, from_state, to_state, actor, reason, receipt_digest, transition_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (
                    cmd.command_id, "DRAFT", cmd.state, actor, "Initial command admission", None, cmd.created_at_utc
                ))

                conn.execute("COMMIT;")
            except Exception:
                conn.execute("ROLLBACK;")
                raise

    def get_command(self, command_id: str) -> Optional[OwnerCommandRecord]:
        with self._lock:
            conn = self.get_connection()
            cur = conn.execute("SELECT * FROM owner_commands WHERE command_id = ?;", (command_id,))
            row = cur.fetchone()
            if not row:
                return None
            return self._row_to_command(row)

    def get_command_by_idempotency_key(self, idempotency_key: str) -> Optional[OwnerCommandRecord]:
        with self._lock:
            conn = self.get_connection()
            cur = conn.execute("SELECT * FROM owner_commands WHERE idempotency_key = ?;", (idempotency_key,))
            row = cur.fetchone()
            if not row:
                return None
            return self._row_to_command(row)

    def get_command_by_correlation_id(self, correlation_id: str) -> Optional[OwnerCommandRecord]:
        with self._lock:
            conn = self.get_connection()
            cur = conn.execute("SELECT * FROM owner_commands WHERE correlation_id = ?;", (correlation_id,))
            row = cur.fetchone()
            if not row:
                return None
            return self._row_to_command(row)

    def get_active_command_for_assignment(self, assignment_id: str) -> Optional[OwnerCommandRecord]:
        with self._lock:
            conn = self.get_connection()
            cur = conn.execute("""
            SELECT * FROM owner_commands
            WHERE assignment_id = ?
              AND state IN ('QUEUED', 'RESERVED', 'DISPATCHING', 'DELIVERY_UNCERTAIN')
            LIMIT 1;
            """, (assignment_id,))
            row = cur.fetchone()
            if not row:
                return None
            return self._row_to_command(row)

    def transition_state(
        self,
        command_id: str,
        new_state: str,
        actor: str,
        reason: Optional[str] = None,
        receipt_digest: Optional[str] = None
    ) -> OwnerCommandRecord:
        """Atomically transitions command state and appends to transition journal."""
        with self._lock:
            conn = self.get_connection()
            conn.execute("BEGIN IMMEDIATE;")
            try:
                cur = conn.execute("SELECT * FROM owner_commands WHERE command_id = ?;", (command_id,))
                row = cur.fetchone()
                if not row:
                    raise KeyError(f"Command not found: {command_id}")
                old_state = row["state"]
                now_utc = datetime.now(timezone.utc).isoformat()

                conn.execute("""
                UPDATE owner_commands
                SET state = ?, updated_at_utc = ?, denial_reason = COALESCE(?, denial_reason)
                WHERE command_id = ?;
                """, (new_state, now_utc, reason, command_id))

                conn.execute("""
                INSERT INTO command_transition_journal (
                    command_id, from_state, to_state, actor, reason, receipt_digest, transition_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (command_id, old_state, new_state, actor, reason, receipt_digest, now_utc))

                conn.execute("COMMIT;")
            except Exception:
                conn.execute("ROLLBACK;")
                raise

            return self.get_command(command_id)  # type: ignore

    def reserve_command(
        self,
        command_id: str,
        worker_id: str,
        lease_seconds: int = 60
    ) -> bool:
        """Atomically acquires lease on a QUEUED command."""
        now = datetime.now(timezone.utc)
        now_utc = now.isoformat()
        expires_utc = (now + timedelta(seconds=lease_seconds)).isoformat()

        with self._lock:
            conn = self.get_connection()
            conn.execute("BEGIN IMMEDIATE;")
            try:
                cur = conn.execute("""
                SELECT state FROM owner_commands WHERE command_id = ?;
                """, (command_id,))
                row = cur.fetchone()
                if not row or row["state"] != CommandState.QUEUED.value:
                    conn.execute("ROLLBACK;")
                    return False

                conn.execute("""
                UPDATE owner_commands
                SET state = ?, reserved_by = ?, reserved_at_utc = ?,
                    lease_expires_at_utc = ?, updated_at_utc = ?
                WHERE command_id = ? AND state = ?;
                """, (
                    CommandState.RESERVED.value, worker_id, now_utc, expires_utc, now_utc,
                    command_id, CommandState.QUEUED.value
                ))

                conn.execute("""
                INSERT INTO command_transition_journal (
                    command_id, from_state, to_state, actor, reason, receipt_digest, transition_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (
                    command_id, CommandState.QUEUED.value, CommandState.RESERVED.value,
                    worker_id, f"Reserved by worker {worker_id}", None, now_utc
                ))

                conn.execute("COMMIT;")
                return True
            except Exception:
                conn.execute("ROLLBACK;")
                raise

    def record_delivery_attempt(
        self,
        delivery_id: str,
        command_id: str,
        attempt_number: int,
        outcome: str,
        receipt_digest: Optional[str] = None,
        readback_status: Optional[str] = None,
        message: str = ""
    ) -> None:
        now_utc = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self.get_connection()
            conn.execute("BEGIN IMMEDIATE;")
            try:
                conn.execute("""
                INSERT INTO command_deliveries (
                    delivery_id, command_id, attempt_number, dispatched_at_utc,
                    outcome, receipt_digest, readback_status, readback_at_utc, message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    delivery_id, command_id, attempt_number, now_utc, outcome,
                    receipt_digest, readback_status, now_utc if readback_status else None, message
                ))
                conn.execute("COMMIT;")
            except Exception:
                conn.execute("ROLLBACK;")
                raise

    def record_acknowledgment(
        self,
        ack_id: str,
        command_id: str,
        correlation_id: str,
        ack_evidence_sha: str,
        ack_at_utc: str
    ) -> None:
        now_utc = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self.get_connection()
            conn.execute("BEGIN IMMEDIATE;")
            try:
                conn.execute("""
                INSERT OR IGNORE INTO command_acknowledgments (
                    ack_id, command_id, correlation_id, ack_evidence_sha, ack_at_utc, recorded_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?);
                """, (ack_id, command_id, correlation_id, ack_evidence_sha, ack_at_utc, now_utc))
                conn.execute("COMMIT;")
            except Exception:
                conn.execute("ROLLBACK;")
                raise

    def record_adoption(
        self,
        adoption_id: str,
        command_id: str,
        correlation_id: str,
        adoption_evidence_sha: str,
        adopted_at_utc: str
    ) -> None:
        now_utc = datetime.now(timezone.utc).isoformat()
        with self._lock:
            conn = self.get_connection()
            conn.execute("BEGIN IMMEDIATE;")
            try:
                conn.execute("""
                INSERT OR IGNORE INTO command_adoptions (
                    adoption_id, command_id, correlation_id, adoption_evidence_sha, adopted_at_utc, recorded_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?);
                """, (adoption_id, command_id, correlation_id, adoption_evidence_sha, adopted_at_utc, now_utc))
                conn.execute("COMMIT;")
            except Exception:
                conn.execute("ROLLBACK;")
                raise

    def get_journal(self, command_id: str) -> List[CommandTransition]:
        with self._lock:
            conn = self.get_connection()
            cur = conn.execute("""
            SELECT * FROM command_transition_journal
            WHERE command_id = ?
            ORDER BY journal_id ASC;
            """, (command_id,))
            rows = cur.fetchall()
            return [
                CommandTransition(
                    journal_id=r["journal_id"],
                    command_id=r["command_id"],
                    from_state=r["from_state"],
                    to_state=r["to_state"],
                    actor=r["actor"],
                    reason=r["reason"],
                    receipt_digest=r["receipt_digest"],
                    transition_at_utc=r["transition_at_utc"]
                )
                for r in rows
            ]

    def list_commands(
        self,
        project_id: Optional[str] = None,
        assignment_id: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[OwnerCommandRecord]:
        query = "SELECT * FROM owner_commands WHERE 1=1"
        params: List[Any] = []
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        if assignment_id:
            query += " AND assignment_id = ?"
            params.append(assignment_id)
        if state:
            query += " AND state = ?"
            params.append(state)
        query += " ORDER BY created_at_utc DESC LIMIT ? OFFSET ?;"
        params.extend([limit, offset])

        with self._lock:
            conn = self.get_connection()
            cur = conn.execute(query, params)
            return [self._row_to_command(r) for r in cur.fetchall()]

    def get_owner_inbox(self) -> Dict[str, Any]:
        """Gathers pending items, active queue, uncertain deliveries, and downstream receipts."""
        with self._lock:
            conn = self.get_connection()
            # Active commands
            cur = conn.execute("""
            SELECT * FROM owner_commands
            WHERE state IN ('QUEUED', 'RESERVED', 'DISPATCHING')
            ORDER BY created_at_utc DESC;
            """)
            active = [self._row_to_command(r).to_dict() for r in cur.fetchall()]

            # Uncertain deliveries requiring readback/investigation
            cur = conn.execute("""
            SELECT * FROM owner_commands
            WHERE state = 'DELIVERY_UNCERTAIN'
            ORDER BY created_at_utc DESC;
            """)
            uncertain = [self._row_to_command(r).to_dict() for r in cur.fetchall()]

            # Recent receipts (ACK / ADOPT)
            cur = conn.execute("""
            SELECT a.ack_id, a.command_id, a.correlation_id, a.ack_evidence_sha, a.ack_at_utc,
                   c.action, c.assignment_id, c.project_id
            FROM command_acknowledgments a
            JOIN owner_commands c ON a.command_id = c.command_id
            ORDER BY a.recorded_at_utc DESC LIMIT 20;
            """)
            acks = [dict(r) for r in cur.fetchall()]

            cur = conn.execute("""
            SELECT ad.adoption_id, ad.command_id, ad.correlation_id, ad.adoption_evidence_sha,
                   ad.adopted_at_utc, c.action, c.assignment_id, c.project_id
            FROM command_adoptions ad
            JOIN owner_commands c ON ad.command_id = c.command_id
            ORDER BY ad.recorded_at_utc DESC LIMIT 20;
            """)
            adoptions = [dict(r) for r in cur.fetchall()]

            return {
                "active_commands": active,
                "uncertain_deliveries": uncertain,
                "recent_acknowledgments": acks,
                "recent_adoptions": adoptions,
                "inbox_generated_at_utc": datetime.now(timezone.utc).isoformat(),
            }

    def _row_to_command(self, row: sqlite3.Row) -> OwnerCommandRecord:
        target = TargetIdentity(
            project_id=row["project_id"],
            work_id=row["work_id"],
            lane_id=row["lane_id"],
            assignment_id=row["assignment_id"],
            run_id=row["run_id"],
            binding_id=row["binding_id"],
            coordinator_id=row["coordinator_id"],
            session_id=row["session_id"],
            chat_id=row["chat_id"],
            binding_generation=row["binding_generation"],
            expected_label_sha=row["expected_label_sha"],
        )
        return OwnerCommandRecord(
            command_id=row["command_id"],
            idempotency_key=row["idempotency_key"],
            correlation_id=row["correlation_id"],
            authenticated_actor=row["authenticated_actor"],
            action=row["action"],
            target=target,
            payload=json.loads(row["payload_json"]),
            payload_digest=row["payload_digest"],
            state=row["state"],
            created_at_utc=row["created_at_utc"],
            updated_at_utc=row["updated_at_utc"],
            denial_reason=row["denial_reason"],
            decision_card_id=row["decision_card_id"],
            decision_outcome=row["decision_outcome"],
            reserved_by=row["reserved_by"],
            reserved_at_utc=row["reserved_at_utc"],
            lease_expires_at_utc=row["lease_expires_at_utc"],
        )
