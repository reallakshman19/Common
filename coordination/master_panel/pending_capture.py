"""Private B2-a exact-source capture journal; never an admission or review oracle.

The source ledger commits in a different transaction. An orphaned raw receipt or
source-commit note remains PENDING until a later independently qualified join.
Neither a CASP kind/status nor supplied actor promotes a report to trusted work.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone


class CaptureConflict(ValueError):
    """Immutable provider/observation identity disagrees with prior evidence."""


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _wire(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _id(value: object, name: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", value):
        raise ValueError("invalid " + name)
    return value


def _utc(value: object) -> str:
    if (not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", value
    )):
        raise ValueError("whole-second UTC required")
    datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class PendingCaptureJournal:
    """Separate, append-only SQLite receipts; no implicit cross-store atomicity."""

    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path, timeout=10)
        self.conn.row_factory = sqlite3.Row
        if db_path != ":memory:":
            self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS pending_captures(
                capture_id TEXT PRIMARY KEY, identity_sha256 TEXT UNIQUE NOT NULL,
                project_id TEXT NOT NULL, repo_id TEXT NOT NULL,
                comment_id TEXT NOT NULL, issue_number INTEGER NOT NULL,
                revision_id TEXT NOT NULL, updated_at TEXT NOT NULL,
                body_sha256 TEXT NOT NULL, raw_body TEXT NOT NULL,
                actor_json TEXT, source_json TEXT NOT NULL,
                first_observed_at TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS idx_pending_revision ON pending_captures(
                project_id,repo_id,comment_id,updated_at);
            CREATE TABLE IF NOT EXISTS pending_observations(
                observation_id TEXT PRIMARY KEY, input_sha256 TEXT NOT NULL,
                capture_id TEXT NOT NULL, observed_at TEXT NOT NULL,
                FOREIGN KEY(capture_id) REFERENCES pending_captures(capture_id));
            CREATE TABLE IF NOT EXISTS pending_source_commits(
                capture_id TEXT NOT NULL, scan_id TEXT NOT NULL,
                outcome TEXT NOT NULL, noted_at TEXT NOT NULL,
                PRIMARY KEY(capture_id,scan_id),
                FOREIGN KEY(capture_id) REFERENCES pending_captures(capture_id));
        """)
        for table in ("pending_captures", "pending_observations", "pending_source_commits"):
            for operation in ("UPDATE", "DELETE"):
                self.conn.execute(
                    f"CREATE TRIGGER IF NOT EXISTS {table}_immutable_{operation.lower()} "
                    f"BEFORE {operation} ON {table} BEGIN "
                    "SELECT RAISE(ABORT,'capture history immutable'); END"
                )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def capture(self, observation_id: str, source: object, raw_body: str,
                *, actor: dict | None = None, observed_at: str | None = None) -> dict:
        """Retain exact decoded provider comment text *before* minimum parsing.

        Existing SourceIdentity supplies public_dict(); this journal intentionally
        accepts only an ISSUE_COMMENT with a matching exact raw-body digest.
        Provider actor is an observation, not conversation authentication.
        """
        _id(observation_id, "observation ID")
        if not isinstance(raw_body, str) or len(raw_body.encode("utf-8")) > 65536:
            raise ValueError("bounded exact UTF-8 body required")
        if not hasattr(source, "public_dict"):
            raise ValueError("SourceIdentity required")
        fields = source.public_dict()
        if fields.get("kind") != "ISSUE_COMMENT":
            raise ValueError("comment source required")
        for key in ("project_id", "repo_id", "entity_id", "comment_id", "revision_id"):
            _id(fields.get(key), key)
        if not fields["repo_id"].isascii() or not fields["repo_id"].isdecimal():
            raise ValueError("numeric repository identity required")
        if fields["entity_id"] != fields["comment_id"]:
            raise ValueError("comment ID mismatch")
        n = fields.get("issue_number")
        if type(n) is not int or n < 1:
            raise ValueError("issue number required")
        if _utc(fields.get("updated_at_utc")) != fields["revision_id"]:
            raise ValueError("revision clock mismatch")
        _utc(fields.get("created_at_utc"))
        if _sha(raw_body) != fields.get("body_sha256"):
            raise ValueError("raw-body fingerprint mismatch")
        if actor is not None:
            if (not isinstance(actor, dict) or set(actor) != {"id", "login"}
                or not isinstance(actor["id"], str)
                or not re.fullmatch(r"[1-9][0-9]{0,19}", actor["id"])
                or not isinstance(actor["login"], str)
                or not re.fullmatch(r"[A-Za-z0-9-]{1,64}", actor["login"])):
                raise ValueError("invalid provider actor observation")
        observed_at = _utc(observed_at if observed_at is not None else _now())
        fingerprint = _sha(_wire({"source": fields, "actor": actor, "body_sha256": _sha(raw_body)}))
        observation_fingerprint = _sha(_wire({"capture": fingerprint, "observed_at": observed_at}))
        scope = (fields["project_id"], fields["repo_id"], fields["comment_id"])
        with self.conn:
            self.conn.execute("BEGIN IMMEDIATE")
            prior_observation = self.conn.execute(
                "SELECT * FROM pending_observations WHERE observation_id=?", (observation_id,)
            ).fetchone()
            if prior_observation:
                if prior_observation["input_sha256"] != observation_fingerprint:
                    raise CaptureConflict("observation identity conflict")
                return self._status(prior_observation["capture_id"], replay=True)
            contradictory = self.conn.execute("""
                SELECT 1 FROM pending_captures
                WHERE project_id=? AND repo_id=? AND comment_id=?
                AND updated_at=? AND body_sha256<>? LIMIT 1
            """, (*scope, fields["updated_at_utc"], fields["body_sha256"])).fetchone()
            if contradictory:
                raise CaptureConflict("same provider revision has different body")
            prior_capture = self.conn.execute(
                "SELECT capture_id FROM pending_captures WHERE identity_sha256=?", (fingerprint,)
            ).fetchone()
            capture_id = prior_capture["capture_id"] if prior_capture else observation_id
            if not prior_capture:
                self.conn.execute("""INSERT INTO pending_captures VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (capture_id, fingerprint, *scope, n, fields["revision_id"],
                     fields["updated_at_utc"], fields["body_sha256"], raw_body,
                     _wire(actor) if actor is not None else None, _wire(fields), observed_at))
            self.conn.execute(
                "INSERT INTO pending_observations VALUES (?,?,?,?)",
                (observation_id, observation_fingerprint, capture_id, observed_at))
            return self._status(capture_id, replay=bool(prior_capture))

    def mark_source_observed(self, capture_id: str, scan_id: str, outcome: str,
                             *, noted_at: str | None = None) -> dict:
        """Append source-ledger commit *report*, not a proven atomic join."""
        _id(capture_id, "capture ID")
        _id(scan_id, "scan ID")
        if outcome not in {"NEW", "EDITED", "RESTORED", "REPLAY"}:
            raise ValueError("invalid source observation result")
        noted_at = _utc(noted_at if noted_at is not None else _now())
        with self.conn:
            self.conn.execute("BEGIN IMMEDIATE")
            if not self.conn.execute("SELECT 1 FROM pending_captures WHERE capture_id=?",
                                     (capture_id,)).fetchone():
                raise ValueError("unknown pending capture")
            old = self.conn.execute("SELECT * FROM pending_source_commits WHERE capture_id=? AND scan_id=?",
                                    (capture_id, scan_id)).fetchone()
            if old:
                if old["outcome"] != outcome and outcome != "REPLAY":
                    raise CaptureConflict("source-commit receipt conflict")
                return self._status(capture_id, replay=True)
            self.conn.execute("INSERT INTO pending_source_commits VALUES (?,?,?,?)",
                              (capture_id, scan_id, outcome, noted_at))
            return self._status(capture_id)

    def _status(self, capture_id: str, *, replay: bool = False) -> dict:
        row = self.conn.execute("SELECT * FROM pending_captures WHERE capture_id=?",
                                (capture_id,)).fetchone()
        if row is None:
            raise ValueError("unknown pending capture")
        commits = self.conn.execute("SELECT count(*) FROM pending_source_commits WHERE capture_id=?",
                                    (capture_id,)).fetchone()[0]
        # Never expose body, actor, descriptor, free text, private proof or routes.
        return {"capture_id": capture_id, "source_body_sha256": row["body_sha256"],
                "source_identity_sha256": row["identity_sha256"],
                "source_commits_reported": commits, "replay": replay,
                "disposition": "PENDING", "registration": "NOT_CONFIGURED",
                "authentication": "UNKNOWN", "independent_acceptance": "UNKNOWN",
                "dispatch_authority": "NOT_GRANTED"}

    def status(self, capture_id: str) -> dict:
        return self._status(_id(capture_id, "capture ID"))
