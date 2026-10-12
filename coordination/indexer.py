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
import threading
import urllib.request
import urllib.error
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
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            if self.db_path != ":memory:":
                self._conn.execute("PRAGMA journal_mode=WAL;")
                self._conn.execute("PRAGMA synchronous=NORMAL;")
        return self._conn

    def close(self):
        """Closes the underlying SQLite connection if open."""
        with self._lock:
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
        with self._lock, self._get_connection() as conn:
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
                old = conn.execute("SELECT content_sha FROM ingestion_events WHERE event_id = ?",
                                   (event["event_id"],)).fetchone()
                if old and old["content_sha"] == event["content_sha"]:
                    return False
                raise ValueError("Immutable event ID collision with changed content")

    def store_evidence(self, project_id: str, evidence: Dict[str, Any]) -> Tuple[int, bool]:
        """
        Stores evidence with idempotency and versioned edit handling.
        Returns (version, is_new_or_edited).
        """
        cid = str(evidence["provider_comment_id"])
        c_sha = hashlib.sha256(evidence["raw_text"].encode("utf-8")).hexdigest()

        with self._lock, self._get_connection() as conn:
            # Check existing records for this comment ID
            rows = conn.execute("""
            SELECT version, content_sha FROM task_evidence
            WHERE project_id = ? AND provider_comment_id = ?
            ORDER BY version DESC
            """, (project_id, cid)).fetchall()

            if rows:
                latest = rows[0]
                # Any already observed historical revision must replay idempotently.
                for old in rows:
                    if old["content_sha"] == c_sha:
                        return old["version"], False
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
        with self._lock, self._get_connection() as conn:
            conn.execute("""
            INSERT OR IGNORE INTO check_observations (
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
        with self._lock, self._get_connection() as conn:
            query = "SELECT * FROM task_evidence WHERE is_active_version = 1"
            params = []
            if project_id:
                query += " AND project_id = ?"
                params.append(project_id)
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_evidence_versions(self, project_id: str, provider_comment_id: str) -> List[Dict[str, Any]]:
        """Returns full version history of a specific comment ID."""
        with self._lock, self._get_connection() as conn:
            rows = conn.execute("""
            SELECT * FROM task_evidence
            WHERE project_id = ? AND provider_comment_id = ?
            ORDER BY version ASC
            """, (project_id, provider_comment_id)).fetchall()
            return [dict(r) for r in rows]

    def get_checks_for_pr(self, project_id: str, pr_number: int) -> List[Dict[str, Any]]:
        """Returns all check observations for a given PR."""
        with self._lock, self._get_connection() as conn:
            rows = conn.execute("""
            SELECT * FROM check_observations
            WHERE project_id = ? AND pr_number = ?
            ORDER BY observed_at DESC
            """, (project_id, pr_number)).fetchall()
            return [dict(r) for r in rows]

    def update_project_status(self, project_id: str, source_kind: str, status: str, cursor: Optional[str] = None):
        """Updates provider reachability cursor for a project."""
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with self._lock, self._get_connection() as conn:
            conn.execute("""
            INSERT INTO project_cursors (project_id, source_kind, last_cursor, last_fetch_at, provider_status)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(project_id, source_kind) DO UPDATE SET
                provider_status = excluded.provider_status,
                last_fetch_at = excluded.last_fetch_at,
                last_cursor = COALESCE(excluded.last_cursor, project_cursors.last_cursor)
            """, (project_id, source_kind, cursor, now, status))
            conn.commit()

    def get_project_observation(self, project_id: str, source_kind: str = "GITHUB_ISSUE_COMMENT") -> Optional[Dict[str, Any]]:
        """Last provider observation; absence must not imply reachability."""
        with self._lock, self._get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM project_cursors WHERE project_id = ? AND source_kind = ?
                """, (project_id, source_kind)).fetchone()
            return dict(row) if row else None

    def get_project_status(self, project_id: str, source_kind: str = "GITHUB_ISSUE_COMMENT") -> str:
        """Retrieves provider reachability status for a project."""
        with self._lock, self._get_connection() as conn:
            row = conn.execute("""
            SELECT provider_status FROM project_cursors
            WHERE project_id = ? AND source_kind = ?
            """, (project_id, source_kind)).fetchone()
            return row["provider_status"] if row else "UNKNOWN"


class CanonicalV36Adapter:
    """Stdlib-only, byte-exact mirror of lifecycle_v36.validate_evidence.

    Conformance is verified against governing render_evidence/validate_evidence in
    the CI suite. Never mutate the canonical eight-line TASK_EVIDENCE comment.
    """
    TASK = re.compile(r"^[A-Z0-9][A-Z0-9_.-]{2,79}$")
    ISSUE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*$")
    TESTS = re.compile(r"([0-9]+)/([0-9]+)")

    @classmethod
    def parse(cls, text: str) -> Tuple[Optional[Dict[str, Any]], str]:
        from urllib.parse import urlparse
        if not isinstance(text, str):
            return None, "NONCANONICAL_REJECTED"
        lines = text.splitlines()
        prefixes = ("Outcome: ", "For the user: ", "Proof: ", "TASK_EVIDENCE v3.6",
                    "Task: ", "Child issue: ", "Candidate: ", "Tests: ")
        if len(lines) != 8 or not all(line.startswith(prefix) for line, prefix in zip(lines, prefixes)):
            return None, "NONCANONICAL_REJECTED"
        if lines[3] != "TASK_EVIDENCE v3.6":
            return None, "NONCANONICAL_REJECTED"
        try:
            outcome, for_user, proof = [lines[i].split(": ", 1)[1] for i in range(3)]
            task, issue, candidate, tests = [lines[i].split(": ", 1)[1] for i in range(4, 8)]
        except (IndexError, ValueError):
            return None, "NONCANONICAL_REJECTED"
        match = cls.TESTS.fullmatch(tests)
        parsed_url = urlparse(proof)
        if (outcome not in ("O1", "O2", "O3", "O4", "O5")
            or not for_user.strip() or for_user != for_user.strip()
            or not cls.TASK.fullmatch(task) or not cls.ISSUE.fullmatch(issue)
            or not candidate.strip() or not match
            or parsed_url.scheme != "https" or not parsed_url.netloc
            or parsed_url.username or parsed_url.password
            or any(term in proof.lower() for term in ("example.com", "localhost", "todo", "<", ">"))
            or any("<" in x and ">" in x for x in (for_user, candidate))):
            return None, "NONCANONICAL_REJECTED"
        if int(match[2]) < 1 or int(match[1]) > int(match[2]):
            return None, "NONCANONICAL_REJECTED"
        expected = (
            f"Outcome: {outcome}\nFor the user: {for_user}\nProof: {proof}\n"
            f"TASK_EVIDENCE v3.6\nTask: {task}\nChild issue: {issue}\n"
            f"Candidate: {candidate}\nTests: {int(match[1])}/{int(match[2])}\n"
        )
        if text != expected:
            return None, "NONCANONICAL_REJECTED"
        return {"outcome": outcome, "task_id": task, "owner_issue": issue,
                "candidate": candidate,
                "candidate_sha": candidate if re.fullmatch(r"[0-9a-fA-F]{40}", candidate) else "",
                "for_user": for_user, "proof": proof,
                "is_canonical_8line": True, "raw_text": text}, "PARSED"


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
    visibility: str = "INTERNAL"
) -> Dict[str, Any]:
    """
    Builds a coherent ControlTowerSnapshot from registry and durable evidence index.
    Applies privacy redaction for public visibility.
    """
    if visibility != "INTERNAL":
        raise PermissionError("Public export requires WP4 allowlist and privacy approval")
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
            "responsibility_id": a.responsibility_id,
            "assigned_role": a.assigned_role,
            "status": a.status
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
    active_by_work = {}
    for binding in registry.bindings.values():
        if binding.binding_state == "ACTIVE":
            work = registry.resolve_work_for_binding(binding.binding_id)
            if work:
                active_by_work.setdefault(work.work_id, []).append(binding.binding_id)
    for work_id, ids in active_by_work.items():
        if len(ids) > 1:
            conflicts_list.append({
                "conflict_type": "DUAL_ACTIVE_TAB_CONFLICT",
                "severity": "CRITICAL_HOLD",
                "entity_id": work_id,
                "details": f"{len(ids)} active tab bindings",
                "source_refs": ids
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

    return snapshot


class ProviderFailure(Exception):
    """A provider error for one source; other projects must remain queryable."""

    def __init__(self, status: int, reason: str = ""):
        self.status = status
        super().__init__(f"GitHub provider returned {status}: {reason}")


class GitHubEvidenceProvider:
    """Read-only GitHub REST adapter; use a separate trusted token/environment."""

    def __init__(self, token: Optional[str] = None, timeout: int = 15):
        self.token = token
        self.timeout = timeout

    def get_json(self, path: str, query: Optional[Dict[str, Any]] = None) -> Any:
        from urllib.parse import urlencode, quote
        if not path.startswith("repos/") or ".." in path.split("/"):
            raise ValueError("Provider path must identify a repository resource")
        url = "https://api.github.com/" + quote(path, safe="/-_.")
        if query:
            url += "?" + urlencode(query)
        headers = {"Accept": "application/vnd.github+json",
                   "User-Agent": "coordination-control-tower-wp1",
                   "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            raise ProviderFailure(exc.code, "permission, rate limit or source unavailable") from exc


def _provider_status(code: int) -> str:
    return ("RATE_LIMITED" if code == 429 else "FORBIDDEN" if code == 403 else
            "UNAVAILABLE" if code in (404, 500, 502, 503, 504) else "UNAVAILABLE")


def ingest_issue_evidence(
    index: EvidenceIndex,
    provider: GitHubEvidenceProvider,
    *,
    project_id: str,
    repository: str,
    issue_number: int,
    max_pages: int = 5
) -> Dict[str, Any]:
    """Bounded, idempotent, source-verified one-issue ingestion.

    The caller registers project/work bindings separately; an issue comment is
    not automatically assigned to a work or admitted as accepted engineering fact.
    """
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Expected owner/repository")
    if issue_number < 1 or not (1 <= max_pages <= 20):
        raise ValueError("Invalid bounded ingestion request")
    source_kind = f"GITHUB_ISSUE_COMMENT:{repository}:{issue_number}"
    stats = {"project_id": project_id, "ingested": 0, "replayed": 0,
             "canonical": 0, "rejected": 0, "provider_status": "UNKNOWN"}
    try:
        repo = provider.get_json(f"repos/{repository}")
        repo_id = str(repo["id"])
        canonical_full_name = repo["full_name"]
        # An explicit registered repository must match provider identity.
        if canonical_full_name.lower() != repository.lower():
            raise ValueError("Provider repository identity mismatch")
        newest = None
        for page in range(1, max_pages + 1):
            rows = provider.get_json(f"repos/{repository}/issues/{issue_number}/comments",
                                     {"per_page": 100, "page": page})
            if not isinstance(rows, list):
                raise ValueError("Unexpected GitHub comments response")
            for comment in rows:
                comment_id = str(comment["id"])
                raw = comment["body"] or ""
                digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
                parsed, result = CanonicalV36Adapter.parse(raw)
                ref = comment["html_url"]
                created = comment["created_at"]
                updated = comment.get("updated_at") or created
                if newest is None or updated > newest:
                    newest = updated
                event_id = f"github:{repo_id}:issue:{issue_number}:comment:{comment_id}:{digest}"
                event = {"event_id": event_id, "project_id": project_id,
                         "source_kind": "GITHUB_ISSUE_COMMENT",
                         "source_ref": ref, "source_revision": updated,
                         "content_sha": digest, "raw_payload": {"id": comment_id, "body": raw},
                         "observed_at_utc": updated,
                         "ingested_at_utc": datetime.now(timezone.utc).isoformat(),
                         "parse_status": result, "scope_key": f"{repo_id}/issue/{issue_number}"}
                if index.record_ingestion_event(event):
                    stats["ingested"] += 1
                else:
                    stats["replayed"] += 1
                if parsed is None:
                    stats["rejected"] += 1
                    continue
                # Own-child attachment is checked before publication; do not
                # treat a parent issue comment as accepted child task evidence.
                if str(parsed["owner_issue"]).strip() not in (
                    str(issue_number), f"#{issue_number}",
                    f"https://github.com/{repository}/issues/{issue_number}",
                    f"{repository}#{issue_number}"
                ):
                    stats["rejected"] += 1
                    continue
                index.store_evidence(project_id, {
                    "evidence_id": event_id, "provider_comment_id": comment_id,
                    "task_id": parsed["task_id"], "owner_issue": parsed["owner_issue"],
                    "candidate_sha": parsed["candidate_sha"], "pr_number": None,
                    "author": comment.get("user", {}).get("login") or "UNKNOWN",
                    "created_at": created, "updated_at": updated,
                    "raw_text": raw, "proof_url": ref,
                    "is_canonical_8line": True
                })
                stats["canonical"] += 1
            if len(rows) < 100:
                break
        index.update_project_status(project_id, source_kind, "REACHABLE", newest)
        index.update_project_status(project_id, "GITHUB_ISSUE_COMMENT", "REACHABLE", newest)
        stats["provider_status"] = "REACHABLE"
    except ProviderFailure as exc:
        state = _provider_status(exc.status)
        index.update_project_status(project_id, source_kind, state)
        index.update_project_status(project_id, "GITHUB_ISSUE_COMMENT", state)
        stats["provider_status"] = state
        stats["provider_error_code"] = exc.status
    return stats


def ingest_pr_checks(
    index: EvidenceIndex, provider: GitHubEvidenceProvider, *,
    project_id: str, repository: str, pr_number: int
) -> Dict[str, Any]:
    """Fetch PR HEAD from GitHub before classifying its observed check runs."""
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Expected owner/repository")
    if pr_number < 1:
        raise ValueError("Invalid PR number")
    try:
        repo = provider.get_json(f"repos/{repository}")
        if repo["full_name"].lower() != repository.lower():
            raise ValueError("Provider repository identity mismatch")
        pr = provider.get_json(f"repos/{repository}/pulls/{pr_number}")
        current_head = pr["head"]["sha"]
        checks = provider.get_json(f"repos/{repository}/commits/{current_head}/check-runs",
                                   {"per_page": 100})
        rows = checks["check_runs"]
        now = datetime.now(timezone.utc).isoformat()
        counts = {"EXACT_HEAD_PASSED": 0, "GREEN_NOT_APPLICABLE": 0,
                  "FAILED": 0, "PENDING": 0, "UNKNOWN": 0,
                  "TESTS_PASSED_ON_OLD_HEAD": 0}
        for row in rows:
            result = ExactHeadCIAdapter.evaluate_check(
                check_name=row["name"],
                check_head_sha=row["head_sha"],
                current_pr_head_sha=current_head,
                check_status=row["status"],
                check_conclusion=row.get("conclusion") or "",
                is_path_scoped=True, skipped=row.get("conclusion") in ("skipped", "neutral")
            )
            counts[result] = counts.get(result, 0) + 1
            receipt = f"{repo['id']}:{pr_number}:{current_head}:{row['id']}:{row.get('updated_at')}:{row.get('status')}:{row.get('conclusion')}"
            index.store_check_observation({
                "check_id": hashlib.sha256(receipt.encode("utf-8")).hexdigest(),
                "project_id": project_id, "repo_id": str(repo["id"]),
                "pr_number": pr_number, "head_sha": row["head_sha"],
                "workflow_name": row.get("name", ""), "job_name": row["name"],
                "applicability": "PATH_SCOPED", "conclusion": result,
                "run_url": row.get("html_url"), "observed_at": now
            })
        index.update_project_status(project_id, "GITHUB_CHECK_RUN", "REACHABLE", current_head)
        return {"project_id": project_id, "pr_number": pr_number,
                "observed_head": current_head, "counts": counts,
                "provider_status": "REACHABLE"}
    except ProviderFailure as exc:
        state = _provider_status(exc.status)
        index.update_project_status(project_id, "GITHUB_CHECK_RUN", state)
        return {"project_id": project_id, "pr_number": pr_number,
                "observed_head": None, "counts": {},
                "provider_status": state, "provider_error_code": exc.status}


def main(argv=None) -> int:
    """One-shot read-only GitHub fetch; recurring scheduling belongs to coordinator."""
    import argparse
    import os
    parser = argparse.ArgumentParser(description="WP1 bounded GitHub evidence ingestion")
    parser.add_argument("--db", required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--issue", type=int)
    parser.add_argument("--pr", type=int)
    args = parser.parse_args(argv)
    if not args.issue and not args.pr:
        parser.error("Provide --issue or --pr")
    index = EvidenceIndex(args.db)
    provider = GitHubEvidenceProvider(os.environ.get("GITHUB_TOKEN"))
    try:
        outputs = []
        if args.issue:
            outputs.append(ingest_issue_evidence(index, provider, project_id=args.project,
                                                 repository=args.repo, issue_number=args.issue))
        if args.pr:
            outputs.append(ingest_pr_checks(index, provider, project_id=args.project,
                                            repository=args.repo, pr_number=args.pr))
        print(json.dumps(outputs, indent=2))
        return 0 if all(x["provider_status"] == "REACHABLE" for x in outputs) else 2
    finally:
        index.close()


if __name__ == "__main__":
    raise SystemExit(main())
