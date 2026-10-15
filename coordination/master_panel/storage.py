"""M1-U02 SQLite state for public GitHub source observations.

This is a source ledger, NOT an engineering acceptance/evidence oracle.
Exact observations and observed-absence tombstones are append-only; partial
scans never assert deletion. Database files belong on private local storage.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .models import SourceIdentity


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class SourceConflict(ValueError):
    pass


class SourceStore:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path, timeout=10)
        self.conn.row_factory = sqlite3.Row
        if db_path != ":memory:":
            self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS objects(
                project_id TEXT NOT NULL, repo_id TEXT NOT NULL,
                kind TEXT NOT NULL, entity_id TEXT NOT NULL,
                issue_number INTEGER, comment_id TEXT,
                source_url TEXT, created_at_utc TEXT,
                updated_at_utc TEXT, body_sha256 TEXT,
                revision_id TEXT NOT NULL, latest_version INTEGER NOT NULL,
                last_seen_scan TEXT NOT NULL, last_seen_at TEXT NOT NULL,
                deleted INTEGER NOT NULL DEFAULT 0, missing_observed_at TEXT,
                report_json TEXT,
                PRIMARY KEY(project_id,repo_id,kind,entity_id)
            );
            CREATE TABLE IF NOT EXISTS versions(
                project_id TEXT NOT NULL, repo_id TEXT NOT NULL,
                kind TEXT NOT NULL, entity_id TEXT NOT NULL,
                version INTEGER NOT NULL, revision_id TEXT NOT NULL,
                updated_at_utc TEXT, body_sha256 TEXT,
                action TEXT NOT NULL, observed_at TEXT NOT NULL,
                PRIMARY KEY(project_id,repo_id,kind,entity_id,version)
            );
            CREATE TABLE IF NOT EXISTS scans(
                project_id TEXT PRIMARY KEY, repo_id TEXT NOT NULL,
                scan_id TEXT NOT NULL, issue_page INTEGER NOT NULL,
                issue_index INTEGER NOT NULL, comment_page INTEGER NOT NULL,
                status TEXT NOT NULL, last_fetch_at TEXT,
                completed_at TEXT, failure_code INTEGER, failure_kind TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_objects_scan
              ON objects(project_id,repo_id,last_seen_scan);
        """)
        columns = {col[1] for col in self.conn.execute("PRAGMA table_info(objects)")}
        if "report_json" not in columns:
            self.conn.execute("ALTER TABLE objects ADD COLUMN report_json TEXT")
            self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def scan(self, project_id: str) -> Optional[dict[str, Any]]:
        row = self.conn.execute(
            "SELECT * FROM scans WHERE project_id=?", (project_id,)
        ).fetchone()
        return dict(row) if row else None

    def save_scan(self, *, project_id: str, repo_id: str, scan_id: str,
                  issue_page: int, issue_index: int, comment_page: int,
                  status: str, failure_code: Optional[int] = None,
                  failure_kind: Optional[str] = None,
                  completed: bool = False) -> None:
        if min(issue_page, comment_page) < 1 or issue_index < 0:
            raise ValueError("Invalid scan cursor")
        with self.conn:
            self.conn.execute("""
                INSERT INTO scans(project_id,repo_id,scan_id,issue_page,
                  issue_index,comment_page,status,last_fetch_at,completed_at,
                  failure_code,failure_kind)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(project_id) DO UPDATE SET
                  repo_id=excluded.repo_id,scan_id=excluded.scan_id,
                  issue_page=excluded.issue_page,issue_index=excluded.issue_index,
                  comment_page=excluded.comment_page,status=excluded.status,
                  last_fetch_at=excluded.last_fetch_at,
                  completed_at=excluded.completed_at,
                  failure_code=excluded.failure_code,failure_kind=excluded.failure_kind
            """, (project_id, repo_id, scan_id, issue_page, issue_index,
                  comment_page, status, utc_now(),
                  utc_now() if completed else None, failure_code, failure_kind))

    def observe(self, source: SourceIdentity, scan_id: str,
                report: Optional[dict[str, Any]] = None) -> str:
        """Observe one provider revision, including body reversion A-B-A.

        Never make a new version from an exact retry. A different payload
        at the same provider updated_at is an identity conflict.
        """
        key = (source.project_id, source.repo_id, source.kind.value, source.entity_id)
        allowed = {
            "kind","reported_status","request_id","message_id","sender_id",
            "project_id","work_id","assignment_id","run_id","lane_id","candidate_sha","transport_status",
        }
        if report is not None and (
            not isinstance(report, dict) or
            set(report) - allowed or
            any(value is not None and (
                not isinstance(value, str) or len(value) > 128
            ) for value in report.values())
        ):
            raise ValueError("Unsafe provider claim metadata")
        claim = json.dumps(report, sort_keys=True) if report else None
        now = utc_now()
        with self.conn:
            old = self.conn.execute("""
                SELECT * FROM objects WHERE project_id=? AND repo_id=?
                    AND kind=? AND entity_id=?
            """, key).fetchone()
            if old is None:
                version, action = 1, "NEW"
                self.conn.execute("""
                    INSERT INTO objects(project_id,repo_id,kind,entity_id,
                      issue_number,comment_id,source_url,created_at_utc,
                      updated_at_utc,body_sha256,revision_id,latest_version,
                      last_seen_scan,last_seen_at,deleted)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,0)
                """, (*key, source.issue_number, source.comment_id, source.url,
                      source.created_at_utc, source.updated_at_utc,
                      source.body_sha256, source.revision_id, version, scan_id, now))
            else:
                previous = old["updated_at_utc"]
                if (not old["deleted"] and previous == source.updated_at_utc
                    and old["body_sha256"] == source.body_sha256):
                    self.conn.execute("""
                        UPDATE objects SET last_seen_scan=?,last_seen_at=?
                        WHERE project_id=? AND repo_id=? AND kind=? AND entity_id=?
                    """, (scan_id, now, *key))
                    return "REPLAY"
                if not old["deleted"] and previous == source.updated_at_utc:
                    raise SourceConflict("Contradictory source body at identical updated_at")
                if (not old["deleted"] and previous and source.updated_at_utc
                    and source.updated_at_utc < previous):
                    raise SourceConflict("Unseen stale source revision")
                version = int(old["latest_version"]) + 1
                action = "RESTORED" if old["deleted"] else "EDITED"
                self.conn.execute("""
                    UPDATE objects SET issue_number=?,comment_id=?,source_url=?,
                      created_at_utc=?,updated_at_utc=?,body_sha256=?,
                      revision_id=?,latest_version=?,last_seen_scan=?,
                      last_seen_at=?,deleted=0,missing_observed_at=NULL
                    WHERE project_id=? AND repo_id=? AND kind=? AND entity_id=?
                """, (source.issue_number, source.comment_id, source.url,
                      source.created_at_utc, source.updated_at_utc, source.body_sha256,
                      source.revision_id, version, scan_id, now, *key))
            self.conn.execute("""
                INSERT INTO versions(project_id,repo_id,kind,entity_id,
                  version,revision_id,updated_at_utc,body_sha256,
                  action,observed_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (*key, version, source.revision_id,
                  source.updated_at_utc, source.body_sha256, action, now))
            self.conn.execute("""
                UPDATE objects SET report_json=? WHERE project_id=? AND
                repo_id=? AND kind=? AND entity_id=?
            """, (claim, *key))
        return action

    def complete_scan(self, project_id: str, repo_id: str, scan_id: str) -> int:
        """Tombstone only after caller has reached the end of all provider pages.

        missing_observed_at is the *observation*, not a claimed GitHub
        deletion timestamp. Reappearance is a separate RESTORED version.
        """
        now = utc_now()
        with self.conn:
            missing = self.conn.execute("""
                SELECT * FROM objects WHERE project_id=? AND repo_id=?
                  AND last_seen_scan<>? AND deleted=0
            """, (project_id, repo_id, scan_id)).fetchall()
            for old in missing:
                key = (project_id,repo_id,old["kind"],old["entity_id"])
                ver = int(old["latest_version"]) + 1
                self.conn.execute("""
                    INSERT INTO versions(project_id,repo_id,kind,entity_id,
                      version,revision_id,updated_at_utc,body_sha256,
                      action,observed_at) VALUES(?,?,?,?,?,? ,NULL,NULL,?,?)
                """, (*key, ver, "OBSERVED_ABSENT", "TOMBSTONE", now))
                self.conn.execute("""
                    UPDATE objects SET deleted=1,missing_observed_at=?,
                      latest_version=? WHERE project_id=? AND repo_id=?
                      AND kind=? AND entity_id=?
                """, (now, ver, *key))
        return len(missing)

    def revisions(self, project_id: str, repo_id: str, kind: str,
                  entity_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute("""
            SELECT version,revision_id,updated_at_utc,body_sha256,
                   action,observed_at FROM versions
            WHERE project_id=? AND repo_id=? AND kind=? AND entity_id=?
            ORDER BY version
        """, (project_id,repo_id,kind,entity_id)).fetchall()
        return [dict(r) for r in rows]

    def objects(self, project_id: str, limit: int = 100,
                offset: int = 0) -> list[dict[str, Any]]:
        if not 1 <= limit <= 200 or offset < 0:
            raise ValueError("Invalid bounded page")
        rows = self.conn.execute("""
            SELECT * FROM objects WHERE project_id=?
            ORDER BY repo_id,kind,entity_id LIMIT ? OFFSET ?
        """, (project_id,limit,offset)).fetchall()
        return [dict(r) for r in rows]
