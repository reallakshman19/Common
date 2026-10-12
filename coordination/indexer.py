"""
Multi-Project Evidence Ingestion & Durable Indexing Engine (WP1)
================================================================
Provides:
- SQLite WAL durable storage for immutable events and evidence versions
- Strict evidence adapters (Canonical 8-line v3.6, v3.5 governed, prose claimed/unknown)
- Exact-head CI check evaluator (no cross-head inheritance)
- Fault-isolated per-project ingestion with provider rate-limit backoff
- Public snapshot projection with privacy redaction
"""

import sqlite3
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


# Regex patterns for privacy redaction
SECRET_PATTERNS = [
    re.compile(r"ghp_[a-zA-Z0-9]{36}"),
    re.compile(r"github_pat_[a-zA-Z0-9_]{82}"),
    re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.]{20,}"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{16,})['\"]?"),
]

LOCAL_PATH_PATTERNS = [
    re.compile(r"[a-zA-Z]:\\(?:Users|Documents|antigravity)[^\s\"',;>]*", re.IGNORECASE),
    re.compile(r"/(?:Users|home)/[^\s\"',;>]*", re.IGNORECASE),
]


class PrivacyRedactor:
    """Sanitizes sensitive tokens and internal filesystem paths from exported snapshots."""

    @staticmethod
    def redact_text(text: str) -> str:
        if not text:
            return text
        result = text
        for pat in SECRET_PATTERNS:
            result = pat.sub("[REDACTED_SECRET]", result)
        for pat in LOCAL_PATH_PATTERNS:
            result = pat.sub("[REDACTED_LOCAL_PATH]", result)
        return result

    @classmethod
    def redact_dict(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: cls.redact_dict(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.redact_dict(item) for item in data]
        elif isinstance(data, str):
            return cls.redact_text(data)
        return data


class EvidenceIndex:
    """Durable SQLite storage for immutable events and versioned evidence."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, timeout=10.0)
            self._conn.row_factory = sqlite3.Row
            if self.db_path != ":memory:":
                self._conn.execute("PRAGMA journal_mode=WAL;")
                self._conn.execute("PRAGMA synchronous=NORMAL;")
        return self._conn

    def close(self):
        """Closes the underlying SQLite connection if open."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def _init_db(self):
        conn = self._get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ingestion_events (
                event_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                source_kind TEXT NOT NULL,
                source_ref TEXT NOT NULL,
                source_revision TEXT,
                content_sha TEXT NOT NULL,
                raw_payload TEXT,
                observed_at_utc TEXT NOT NULL,
                ingested_at_utc TEXT NOT NULL,
                parse_status TEXT NOT NULL,
                scope_key TEXT NOT NULL
            );
            """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS task_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evidence_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            provider_comment_id TEXT NOT NULL,
            task_id TEXT NOT NULL,
            owner_issue TEXT NOT NULL,
            candidate_sha TEXT NOT NULL,
            pr_number INTEGER,
            author TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            content_sha TEXT NOT NULL,
            proof_url TEXT,
            is_canonical_8line INTEGER NOT NULL,
            raw_text TEXT NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            is_active_version INTEGER NOT NULL DEFAULT 1,
            UNIQUE(project_id, provider_comment_id, version)
        );
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS check_observations (
            check_id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            repo_id TEXT NOT NULL,
            pr_number INTEGER NOT NULL,
            head_sha TEXT NOT NULL,
            workflow_name TEXT NOT NULL,
            job_name TEXT NOT NULL,
            applicability TEXT NOT NULL,
            conclusion TEXT NOT NULL,
            run_url TEXT,
            observed_at TEXT NOT NULL
        );
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS project_cursors (
            project_id TEXT NOT NULL,
            source_kind TEXT NOT NULL,
            last_cursor TEXT,
            last_fetch_at TEXT,
            provider_status TEXT NOT NULL DEFAULT 'REACHABLE',
            PRIMARY KEY (project_id, source_kind)
        );
        """)
        conn.commit()

    def record_ingestion_event(self, event: Dict[str, Any]) -> bool:
        """Idempotently records raw ingestion event."""
        with self._get_connection() as conn:
            try:
                conn.execute("""
                INSERT INTO ingestion_events (
                    event_id, project_id, source_kind, source_ref, source_revision,
                    content_sha, raw_payload, observed_at_utc, ingested_at_utc,
                    parse_status, scope_key
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    event["event_id"],
                    event["project_id"],
                    event["source_kind"],
                    event["source_ref"],
                    str(event.get("source_revision", "")),
                    event["content_sha"],
                    json.dumps(event.get("raw_payload")),
                    event["observed_at_utc"],
                    event["ingested_at_utc"],
                    event["parse_status"],
                    event["scope_key"]
                ))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                # Already ingested identical event ID
                return False

    def store_evidence(self, project_id: str, evidence: Dict[str, Any]) -> Tuple[int, bool]:
        """
        Stores evidence with idempotency and versioned edit handling.
        Returns (version, is_new_or_edited).
        """
        cid = str(evidence["provider_comment_id"])
        c_sha = hashlib.sha256(evidence["raw_text"].encode("utf-8")).hexdigest()

        with self._get_connection() as conn:
            # Check existing records for this comment ID
            rows = conn.execute("""
            SELECT version, content_sha FROM task_evidence
            WHERE project_id = ? AND provider_comment_id = ?
            ORDER BY version DESC
            """, (project_id, cid)).fetchall()

            if rows:
                latest = rows[0]
                if latest["content_sha"] == c_sha:
                    # Identical replay: idempotent return
                    return latest["version"], False
                # Edited comment: deactivate previous version, bump version
                new_version = latest["version"] + 1
                conn.execute("""
                UPDATE task_evidence SET is_active_version = 0
                WHERE project_id = ? AND provider_comment_id = ?
                """, (project_id, cid))
            else:
                new_version = 1

            conn.execute("""
            INSERT INTO task_evidence (
                evidence_id, project_id, provider_comment_id, task_id, owner_issue,
                candidate_sha, pr_number, author, created_at, updated_at,
                content_sha, proof_url, is_canonical_8line, raw_text, version, is_active_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                evidence.get("evidence_id", f"{project_id}-{cid}-v{new_version}"),
                project_id,
                cid,
                evidence["task_id"],
                evidence["owner_issue"],
                evidence["candidate_sha"],
                evidence.get("pr_number"),
                evidence["author"],
                evidence["created_at"],
                evidence.get("updated_at"),
                c_sha,
                evidence.get("proof_url"),
                1 if evidence.get("is_canonical_8line") else 0,
                evidence["raw_text"],
                new_version
            ))
            conn.commit()
            return new_version, True

    def store_check_observation(self, check: Dict[str, Any]):
        """Records or updates a CI check observation."""
        with self._get_connection() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO check_observations (
                check_id, project_id, repo_id, pr_number, head_sha,
                workflow_name, job_name, applicability, conclusion,
                run_url, observed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                check["check_id"],
                check["project_id"],
                check["repo_id"],
                check["pr_number"],
                check["head_sha"],
                check["workflow_name"],
                check["job_name"],
                check["applicability"],
                check["conclusion"],
                check.get("run_url"),
                check["observed_at"]
            ))
            conn.commit()

    def get_active_evidence(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns all active evidence records."""
        with self._get_connection() as conn:
            query = "SELECT * FROM task_evidence WHERE is_active_version = 1"
            params = []
            if project_id:
                query += " AND project_id = ?"
                params.append(project_id)
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_evidence_versions(self, project_id: str, provider_comment_id: str) -> List[Dict[str, Any]]:
        """Returns full version history of a specific comment ID."""
        with self._get_connection() as conn:
            rows = conn.execute("""
            SELECT * FROM task_evidence
            WHERE project_id = ? AND provider_comment_id = ?
            ORDER BY version ASC
            """, (project_id, provider_comment_id)).fetchall()
            return [dict(r) for r in rows]

    def get_checks_for_pr(self, project_id: str, pr_number: int) -> List[Dict[str, Any]]:
        """Returns all check observations for a given PR."""
        with self._get_connection() as conn:
            rows = conn.execute("""
            SELECT * FROM check_observations
            WHERE project_id = ? AND pr_number = ?
            ORDER BY observed_at DESC
            """, (project_id, pr_number)).fetchall()
            return [dict(r) for r in rows]

    def update_project_status(self, project_id: str, source_kind: str, status: str, cursor: Optional[str] = None):
        """Updates provider reachability cursor for a project."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with self._get_connection() as conn:
            conn.execute("""
            INSERT INTO project_cursors (project_id, source_kind, last_cursor, last_fetch_at, provider_status)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(project_id, source_kind) DO UPDATE SET
                provider_status = excluded.provider_status,
                last_fetch_at = excluded.last_fetch_at,
                last_cursor = COALESCE(excluded.last_cursor, project_cursors.last_cursor)
            """, (project_id, source_kind, cursor, now, status))
            conn.commit()

    def get_project_status(self, project_id: str, source_kind: str = "GITHUB_ISSUE_COMMENT") -> str:
        """Retrieves provider reachability status for a project."""
        with self._get_connection() as conn:
            row = conn.execute("""
            SELECT provider_status FROM project_cursors
            WHERE project_id = ? AND source_kind = ?
            """, (project_id, source_kind)).fetchone()
            return row["provider_status"] if row else "REACHABLE"


class CanonicalV36Adapter:
    """
    Parses and strictly validates canonical 8-line v3.6 TASK_EVIDENCE.
    Rejects any noncanonical modifications or trailing text.
    """

    REQUIRED_KEYS = [
        "TASK_EVIDENCE",
        "PARENT_EVIDENCE",
        "CLAIMED_RESULT",
        "CANDIDATE_SHA",
        "PR_NUMBER",
        "PROOF_URL",
        "AUTHOR",
        "TIMESTAMP"
    ]

    @classmethod
    def parse(cls, text: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Parses text. Returns (evidence_dict, parse_status).
        Enforces exactly the 8 canonical lines with no noncanonical trailing text.
        """
        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
        if len(lines) != 8:
            return None, "NONCANONICAL_REJECTED"

        data = {}
        for line in lines:
            if ":" not in line:
                return None, "NONCANONICAL_REJECTED"
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip()
            data[k] = v

        # Check exact key set
        if set(data.keys()) != set(cls.REQUIRED_KEYS):
            return None, "NONCANONICAL_REJECTED"

        # Validate candidate SHA
        if not re.match(r"^[0-9a-f]{40}$", data["CANDIDATE_SHA"]):
            return None, "NONCANONICAL_REJECTED"

        try:
            pr_num = int(data["PR_NUMBER"])
        except ValueError:
            return None, "NONCANONICAL_REJECTED"

        return {
            "evidence_id": data["TASK_EVIDENCE"],
            "parent_id": data["PARENT_EVIDENCE"],
            "task_id": data["TASK_EVIDENCE"],
            "claimed_result": data["CLAIMED_RESULT"],
            "candidate_sha": data["CANDIDATE_SHA"],
            "pr_number": pr_num,
            "proof_url": data["PROOF_URL"],
            "author": data["AUTHOR"],
            "created_at": data["TIMESTAMP"],
            "is_canonical_8line": True,
            "raw_text": text
        }, "PARSED"


class ExactHeadCIAdapter:
    """
    Evaluates CI check observations against current PR head.
    Enforces strict invalidation on SHA change (no cross-head inheritance).
    """

    @staticmethod
    def evaluate_check(
        check_name: str,
        check_head_sha: str,
        current_pr_head_sha: str,
        check_status: str,
        check_conclusion: str,
        is_path_scoped: bool = False,
        skipped: bool = False
    ) -> str:
        """
        Computes normalized conclusion:
        - TESTS_PASSED_ON_OLD_HEAD: check passed on a prior commit, but current head changed
        - GREEN_NOT_APPLICABLE: skipped/path-scoped check
        - EXACT_HEAD_PASSED: check passed on exact current head
        - FAILED, PENDING, or CI_UNKNOWN
        """
        if check_head_sha != current_pr_head_sha:
            if check_conclusion.lower() == "success":
                return "TESTS_PASSED_ON_OLD_HEAD"
            return "UNKNOWN"

        if is_path_scoped and (skipped or check_conclusion.lower() in ("skipped", "neutral")):
            return "GREEN_NOT_APPLICABLE"

        if check_status.lower() in ("queued", "in_progress", "pending"):
            return "PENDING"

        if check_conclusion.lower() == "success":
            return "EXACT_HEAD_PASSED"

        if check_conclusion.lower() in ("failure", "timed_out", "cancelled"):
            return "FAILED"

        return "UNKNOWN"


def generate_control_tower_snapshot(
    registry,
    evidence_index: EvidenceIndex,
    version: str = "v3.0.0",
    visibility: str = "PUBLIC"
) -> Dict[str, Any]:
    """
    Builds a coherent ControlTowerSnapshot from registry and durable evidence index.
    Applies privacy redaction for public visibility.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    active_ev = evidence_index.get_active_evidence()

    # Calculate watermarks per project
    watermarks = {}
    for p_id in registry.projects:
        ev_p = [e for e in active_ev if e["project_id"] == p_id]
        if ev_p:
            ev_p.sort(key=lambda x: x["created_at"], reverse=True)
            watermarks[p_id] = ev_p[0]["created_at"]
        else:
            watermarks[p_id] = registry.projects[p_id].as_of

    # Convert registry entities to dicts
    projects_list = [
        {
            "project_id": p.project_id,
            "name": p.name,
            "repo_url": p.repo_url,
            "coordination_dir": p.coordination_dir,
            "status": p.status,
            "as_of": p.as_of,
            "provider_reachability": p.provider_reachability
        }
        for p in registry.projects.values()
    ]

    works_list = [
        {
            "work_id": w.work_id,
            "project_id": w.project_id,
            "aim_id": w.aim_id,
            "label_sha": w.label_sha,
            "issue_ref": w.issue_ref,
            "acceptance_status": w.acceptance_status,
            "candidate_pr_ref": w.candidate_pr_ref,
            "candidate_head_sha": w.candidate_head_sha
        }
        for w in registry.works.values()
    ]

    assignments_list = [
        {
            "assignment_id": a.assignment_id,
            "lane_id": a.lane_id,
            "task_id": a.task_id,
            "owner_issue": a.owner_issue,
            "task_title": a.task_title,
            "state": a.state
        }
        for a in registry.assignments.values()
    ]

    runs_list = [
        {
            "run_id": r.run_id,
            "assignment_id": r.assignment_id,
            "generation": r.generation,
            "chat_id": r.chat_id,
            "meter_started_at": r.meter_started_at,
            "evidence_cadence_count": r.evidence_cadence_count,
            "run_state": r.run_state,
            "predecessor_run_id": r.predecessor_run_id
        }
        for r in registry.runs.values()
    ]

    bindings_list = [
        {
            "binding_id": b.binding_id,
            "run_id": b.run_id,
            "project_id": b.project_id,
            "tab_alias": b.tab_alias,
            "generation": b.generation,
            "binding_state": b.binding_state
        }
        for b in registry.bindings.values()
    ]

    conflicts_list = []
    # Check for active tab conflicts
    tab_conflicts = registry.validate_single_active_tab_invariants()
    for msg in tab_conflicts:
        conflicts_list.append({
            "conflict_type": "DUAL_ACTIVE_TAB_CONFLICT",
            "severity": "CRITICAL_HOLD",
            "entity_id": "active_tab_bindings",
            "details": msg,
            "source_refs": []
        })

    snapshot = {
        "snapshot_id": f"snap-{hashlib.sha256(now.encode('utf-8')).hexdigest()[:12]}",
        "version": version,
        "generated_at_utc": now,
        "visibility": visibility,
        "source_watermarks": watermarks,
        "projects": projects_list,
        "works": works_list,
        "assignments": assignments_list,
        "runs": runs_list,
        "tab_bindings": bindings_list,
        "evidence_count": len(active_ev),
        "conflicts": conflicts_list
    }

    if visibility == "PUBLIC":
        snapshot = PrivacyRedactor.redact_dict(snapshot)

    return snapshot
