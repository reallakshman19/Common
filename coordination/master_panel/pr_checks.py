"""Bounded public PR/check observations; no worker, dispatch or acceptance.

Collection-scoped tables preserve provider state independently of CASP reports
and the issue/comment scan clock. No absence is inferred from offset pages.
"""
from __future__ import annotations
import hashlib
import json
import re
import sqlite3
import uuid
import base64
from datetime import datetime, timezone
from urllib.parse import urlsplit
from typing import Any

from .github_source import ALLOWLIST, ProviderError, PageBudgetExhausted
from .storage import SourceConflict, SourceStore, utc_now

_SHA = re.compile(r"[a-f0-9]{40}")
_STATUS = {"queued", "in_progress", "completed", "waiting", "requested", "pending"}
_CONCLUSION = {"success", "failure", "neutral", "cancelled", "skipped",
               "timed_out", "action_required", "stale", "startup_failure"}


def _clock(value):
    if value is None:
        return None
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value):
        raise SourceConflict("Invalid provider clock")
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        raise SourceConflict("Invalid provider clock") from None
    return value


def _number(value):
    if type(value) is not int or value < 1:
        raise SourceConflict("Invalid provider numeric identity")
    return value


def _sha(value):
    if not isinstance(value, str) or not _SHA.fullmatch(value):
        raise SourceConflict("Invalid provider head")
    return value


def _revision(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _url(value, reg):
    if not isinstance(value, str):
        raise SourceConflict("Missing provider link")
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or parsed.netloc != "github.com"
            or not parsed.path.startswith("/" + reg.repo_full_name + "/")
            or parsed.query or parsed.fragment
            or any(part in (".", "..") for part in parsed.path.split("/"))):
        raise SourceConflict("Noncanonical provider link")
    return value


class PullCheckIntake:
    PAGE_SIZE = 100

    def __init__(self, store: SourceStore, reader):
        self.store, self.reader = store, reader
        store.conn.executescript("""
            CREATE TABLE IF NOT EXISTS pr_check_objects(
                project_id TEXT, repo_id TEXT, kind TEXT, entity_id TEXT,
                revision_id TEXT NOT NULL, payload_json TEXT NOT NULL,
                latest_version INTEGER NOT NULL, observed_at TEXT NOT NULL,
                PRIMARY KEY(project_id,repo_id,kind,entity_id)
            );
            CREATE TABLE IF NOT EXISTS pr_check_versions(
                project_id TEXT,repo_id TEXT,kind TEXT,entity_id TEXT,
                version INTEGER,revision_id TEXT,payload_json TEXT,observed_at TEXT,
                PRIMARY KEY(project_id,repo_id,kind,entity_id,version)
            );
            CREATE TABLE IF NOT EXISTS pr_check_links(
                project_id TEXT,repo_id TEXT,pr_number INTEGER,
                kind TEXT,entity_id TEXT,last_seen_scan TEXT,
                PRIMARY KEY(project_id,repo_id,pr_number,kind,entity_id)
            );
            CREATE TABLE IF NOT EXISTS pr_check_scans(
                project_id TEXT,repo_id TEXT,pr_number INTEGER,
                head_sha TEXT,scan_id TEXT,page INTEGER,total_count INTEGER,
                status TEXT,last_fetch_at TEXT,completed_at TEXT,
                error_code INTEGER,error_kind TEXT,
                PRIMARY KEY(project_id,repo_id,pr_number)
            );
        """)

    def _observe(self, reg, number, kind, payload, scan_id):
        key = (reg.project_id, reg.repo_id, kind, str(payload["id"]))
        revision = _revision(payload)
        body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        now = utc_now()
        with self.store.conn:
            old = self.store.conn.execute(
                "SELECT * FROM pr_check_objects WHERE project_id=? AND repo_id=? AND kind=? AND entity_id=?", key
            ).fetchone()
            if kind == "CHECK_RUN" and old and json.loads(old["payload_json"])["head_sha"] != payload["head_sha"]:
                raise SourceConflict("Existing check identity changed head")
            if kind == "PR" and self.store.conn.execute("""
                SELECT 1 FROM pr_check_links WHERE project_id=? AND repo_id=?
                  AND pr_number=? AND kind='PR' AND entity_id<>?
            """, (reg.project_id,reg.repo_id,number,str(payload["id"]))).fetchone():
                raise SourceConflict("Existing PR number changed identity")
            replay = old is not None and old["revision_id"] == revision
            version = int(old["latest_version"]) if replay else int(old["latest_version"])+1 if old else 1
            if not replay:
                self.store.conn.execute(
                    "INSERT INTO pr_check_versions VALUES(?,?,?,?,?,?,?,?)",
                    (*key, version, revision, body, now))
            self.store.conn.execute("""
                INSERT INTO pr_check_objects VALUES(?,?,?,?,?,?,?,?)
                ON CONFLICT(project_id,repo_id,kind,entity_id) DO UPDATE SET
                  revision_id=excluded.revision_id,payload_json=excluded.payload_json,
                  latest_version=excluded.latest_version,observed_at=excluded.observed_at
            """, (*key, revision, body, version, now))
            self.store.conn.execute("""
                INSERT INTO pr_check_links VALUES(?,?,?,?,?,?)
                ON CONFLICT(project_id,repo_id,pr_number,kind,entity_id) DO UPDATE SET
                  last_seen_scan=excluded.last_seen_scan
            """, (reg.project_id, reg.repo_id, number, kind, str(payload["id"]), scan_id))
        return "REPLAY" if replay else "OBSERVED"

    @staticmethod
    def _pull(item, reg, number):
        if not isinstance(item, dict) or type(item.get("number")) is not int or item["number"] != number:
            raise SourceConflict("Invalid PR detail")
        base, head = item.get("base"), item.get("head")
        if not isinstance(base, dict) or not isinstance(head, dict):
            raise SourceConflict("Missing PR refs")
        repo = base.get("repo")
        if not isinstance(repo, dict) or str(repo.get("id")) != reg.repo_id or repo.get("full_name") != reg.repo_full_name:
            raise SourceConflict("PR repository mismatch")
        if item.get("state") not in ("open", "closed") or type(item.get("draft")) is not bool:
            raise SourceConflict("Invalid PR state")
        created, updated = _clock(item.get("created_at")), _clock(item.get("updated_at"))
        if not created or not updated:
            raise SourceConflict("Missing PR clocks")
        return {"id": _number(item.get("id")), "number": number,
                "state": item["state"], "draft": item["draft"],
                "head_sha": _sha(head.get("sha")), "base_sha": _sha(base.get("sha")),
                "created_at": created, "updated_at": updated,
                "merged_at": _clock(item.get("merged_at")),
                "source_url": _url(item.get("html_url"), reg)}

    @staticmethod
    def _check(item, reg, head):
        if not isinstance(item, dict) or item.get("status") not in _STATUS:
            raise SourceConflict("Invalid check object/status")
        sha = _sha(item.get("head_sha"))
        if sha != head:
            raise SourceConflict("Check head mismatch")
        conclusion = item.get("conclusion")
        if conclusion is not None and conclusion not in _CONCLUSION:
            raise SourceConflict("Invalid check conclusion")
        if item["status"] != "completed" and conclusion is not None:
            raise SourceConflict("Unfinished check has conclusion")
        name = item.get("name")
        if not isinstance(name, str) or not name or len(name) > 160 or re.search(r"[\x00-\x1f]", name):
            raise SourceConflict("Invalid check name")
        suite = item.get("check_suite")
        if not isinstance(suite, dict):
            raise SourceConflict("Missing check suite")
        ident = _number(item.get("id"))
        return {"id": ident, "head_sha": sha, "name": name,
                "status": item["status"], "conclusion": conclusion,
                "suite_id": _number(suite.get("id")),
                "started_at": _clock(item.get("started_at")),
                "completed_at": _clock(item.get("completed_at")),
                "source_url": _url(item.get("html_url"), reg)}

    def run(self, project_id: str, pr_number: int, max_requests: int = 20):
        if project_id not in ALLOWLIST or type(pr_number) is not int or pr_number < 1:
            raise ValueError("Unregistered project/invalid PR")
        if type(max_requests) is not int or not 3 <= max_requests <= 100:
            raise ValueError("Invalid bounded request budget")
        reg = ALLOWLIST[project_id]
        key = (reg.project_id, reg.repo_id, pr_number)
        prior = self.store.conn.execute(
            "SELECT * FROM pr_check_scans WHERE project_id=? AND repo_id=? AND pr_number=?", key).fetchone()
        calls = 0
        page, total, head, scan_id = 1, None, None, uuid.uuid4().hex
        def read(path, query=None):
            nonlocal calls
            if calls >= max_requests:
                raise PageBudgetExhausted()
            calls += 1
            return self.reader.get_json(path, query)
        def finish(state, error_kind=None, error_code=None, complete=False):
            now = utc_now()
            with self.store.conn:
                self.store.conn.execute("""
                    INSERT INTO pr_check_scans VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(project_id,repo_id,pr_number) DO UPDATE SET
                      head_sha=excluded.head_sha,scan_id=excluded.scan_id,page=excluded.page,
                      total_count=excluded.total_count,status=excluded.status,
                      last_fetch_at=excluded.last_fetch_at,completed_at=excluded.completed_at,
                      error_code=excluded.error_code,error_kind=excluded.error_kind
                """, (*key, head, scan_id, page, total, state, now,
                      now if complete else None, error_code, error_kind))
            return {"project_id": project_id, "pr_number": pr_number,
                    "head_sha": head, "state": state, "complete": complete,
                    "requests": calls, "cursor_page": page,
                    "error_kind": error_kind, "error_code": error_code,
                    "absence_verified": False, "tombstones": 0}
        try:
            meta = read(f"repos/{reg.repo_full_name}")
            if not isinstance(meta, dict) or str(meta.get("id")) != reg.repo_id or meta.get("full_name") != reg.repo_full_name or meta.get("private") is not False:
                raise SourceConflict("Repository public identity mismatch")
            pull = self._pull(read(f"repos/{reg.repo_full_name}/pulls/{pr_number}"), reg, pr_number)
            head = pull["head_sha"]
            if prior and prior["head_sha"] == head and prior["status"] != "REACHABLE" and prior["error_kind"] not in ("PAGE_DRIFT", "HEAD_MOVED", "SOURCE_CONFLICT"):
                scan_id, page, total = prior["scan_id"], prior["page"], prior["total_count"]
            finish("PARTIAL")
            self._observe(reg, pr_number, "PR", pull, scan_id)
            while True:
                response = read(f"repos/{reg.repo_full_name}/commits/{head}/check-runs",
                                {"per_page": self.PAGE_SIZE, "page": page, "filter": "all"})
                if not isinstance(response, dict) or type(response.get("total_count")) is not int or response["total_count"] < 0 or not isinstance(response.get("check_runs"), list):
                    raise SourceConflict("Invalid check collection")
                if total is not None and total != response["total_count"]:
                    return finish("PARTIAL", "PAGE_DRIFT")
                total = response["total_count"]
                values = response["check_runs"]
                if len(values) > self.PAGE_SIZE:
                    raise SourceConflict("Oversized check page")
                parsed = [self._check(item, reg, head) for item in values]
                ids = [item["id"] for item in parsed]
                if len(set(ids)) != len(ids):
                    raise SourceConflict("Duplicate check identity")
                for payload in parsed:
                    self._observe(reg, pr_number, "CHECK_RUN", payload, scan_id)
                if len(values) < self.PAGE_SIZE:
                    if (page - 1) * self.PAGE_SIZE + len(values) != total:
                        return finish("PARTIAL", "PAGE_DRIFT")
                    latest = self._pull(read(f"repos/{reg.repo_full_name}/pulls/{pr_number}"), reg, pr_number)
                    self._observe(reg, pr_number, "PR", latest, scan_id)
                    if latest["head_sha"] != head:
                        return finish("PARTIAL", "HEAD_MOVED")
                    count = self.store.conn.execute("""
                        SELECT COUNT(*) FROM pr_check_links WHERE project_id=? AND repo_id=?
                          AND pr_number=? AND kind='CHECK_RUN' AND last_seen_scan=?
                    """, (*key, scan_id)).fetchone()[0]
                    if count != total:
                        return finish("PARTIAL", "PAGE_DRIFT")
                    return finish("REACHABLE", complete=True)
                page += 1
                finish("PARTIAL")
        except PageBudgetExhausted:
            return finish("PARTIAL", "READ_BUDGET")
        except ProviderError as error:
            return finish("RATE_LIMITED" if error.code == 429 else "FORBIDDEN" if error.code in (401, 403) else "UNAVAILABLE",
                          "RATE_LIMIT" if error.code == 429 else "AUTHENTICATION" if error.code == 401 else "AUTHORIZATION" if error.code == 403 else "HTTP_ERROR", error.code)
        except (SourceConflict, KeyError, TypeError, ValueError):
            return finish("UNAVAILABLE", "SOURCE_CONFLICT")


def collection_rows(conn: sqlite3.Connection, project_id: str, number: int, limit: int = 100, cursor=None):
    if project_id not in ALLOWLIST or type(number) is not int or number < 1 or type(limit) is not int or not 1 <= limit <= 200:
        raise ValueError("Invalid bounded source query")
    reg = ALLOWLIST[project_id]
    if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='pr_check_scans'").fetchone():
        if cursor is not None:
            raise LookupError("Provider collection unavailable")
        return {"schema_version":"1.0.0", "source_family":"PR_CHECK_COLLECTION",
                "scope": {"project_id": project_id, "repo_id":reg.repo_id, "pr_number": number, "head_sha":None},
                "state":"UNKNOWN", "observed_at":None, "completed_at":None,
                "freshness":"UNKNOWN", "total_count":None, "has_more":False,
                "next_cursor":None, "items": [], "absence_verified": False, "independent_acceptance": "UNKNOWN"}
    scan = conn.execute("SELECT * FROM pr_check_scans WHERE project_id=? AND repo_id=? AND pr_number=?",
                        (project_id, reg.repo_id, number)).fetchone()
    state = dict(scan) if scan else {}
    versions = conn.execute("""
        SELECT COUNT(*) n, COALESCE(SUM(v.version),0) total FROM pr_check_versions v
        JOIN pr_check_links l USING(project_id,repo_id,kind,entity_id)
        WHERE l.project_id=? AND l.repo_id=? AND l.pr_number=?
    """, (project_id,reg.repo_id,number)).fetchone()
    generation = _revision({"scope":[project_id,reg.repo_id,number], "scan":state, "versions":dict(versions)})
    offset = 0
    if cursor is not None:
        if not isinstance(cursor, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,512}",cursor):
            raise ValueError("Invalid provider cursor")
        try:
            decoded = json.loads(base64.urlsafe_b64decode(cursor+'='*(-len(cursor)%4)))
        except (ValueError, UnicodeError):
            raise ValueError("Invalid provider cursor") from None
        if not isinstance(decoded,dict) or decoded.get("scope") != [project_id,reg.repo_id,number] or decoded.get("generation") != generation:
            raise LookupError("Expired provider cursor")
        offset = decoded.get("offset")
        if type(offset) is not int or not 0 <= offset <= 1_000_000:
            raise ValueError("Invalid provider offset")
    records = conn.execute("""
        SELECT o.*,l.last_seen_scan FROM pr_check_objects o JOIN pr_check_links l
          USING(project_id,repo_id,kind,entity_id)
        WHERE l.project_id=? AND l.repo_id=? AND l.pr_number=?
        ORDER BY o.kind,o.entity_id LIMIT ? OFFSET ?
    """, (project_id, reg.repo_id, number, limit+1,offset)).fetchall()
    items = []
    freshness = "UNKNOWN"
    if state.get("status") == "REACHABLE" and state.get("completed_at"):
        age = (datetime.now(timezone.utc)-datetime.fromisoformat(state["completed_at"].replace("Z","+00:00"))).total_seconds()
        freshness = "UNKNOWN" if age < 0 else "FRESH" if age <= 3600 else "STALE"
    for record in records[:limit]:
        payload = json.loads(record["payload_json"])
        current = state.get("status") == "REACHABLE" and record["last_seen_scan"] == state.get("scan_id")
        items.append({"source": {"project_id": project_id, "repo_id": reg.repo_id,
                                  "kind": record["kind"], "entity_id": record["entity_id"],
                                  "revision_id": record["revision_id"],
                                  "hash_profile": "safe-provider-fields-v1"},
                      "provider": payload, "provenance": "GITHUB_PR_CHECK_PROVIDER",
                      "observed_at": record["observed_at"],
                      "source_freshness": freshness if current else "UNKNOWN",
                      "presence": "OBSERVED_IN_SCAN" if current else "UNQUALIFIED_LAST_GOOD",
                      "provider_head_relation": "MATCHES_OBSERVED_PR_HEAD" if current and payload.get("head_sha") == state.get("head_sha") else "UNKNOWN",
                      "independent_acceptance": "UNKNOWN"})
    next_cursor = base64.urlsafe_b64encode(json.dumps({"scope":[project_id,reg.repo_id,number],"generation":generation,"offset":offset+limit},sort_keys=True,separators=(",",":")).encode()).decode().rstrip("=") if len(records) > limit else None
    return {"schema_version":"1.0.0", "source_family":"PR_CHECK_COLLECTION", "scope": {"project_id": project_id, "repo_id": reg.repo_id,
                       "pr_number": number, "head_sha": state.get("head_sha")},
            "state": state.get("status", "UNKNOWN"), "observed_at": state.get("last_fetch_at"),
            "completed_at": state.get("completed_at"), "error_kind": state.get("error_kind"),
            "freshness":freshness,"next_cursor":next_cursor,"generation":generation,
            "total_count":state.get("total_count"),
            "items": items, "has_more": len(records) > limit, "absence_verified": False,
            "independent_acceptance": "UNKNOWN"}

