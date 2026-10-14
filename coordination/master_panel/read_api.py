"""M1-U03 owner-panel loopback read API v1.0.0.

Read-only projection over local SQLite source ledger. No raw comments, tokens,
chat URLs, browser probes, command queue, provider fetching or SEND.
The caller may inject validated explicit bindings/reviewer records; the API
never infers those from source author or comment prose.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import http.server
import json
import re
import sqlite3
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional

from .github_source import ALLOWLIST
from .models import ROW_SCHEMA_VERSION, SourceIdentity, SourceKind, build_row


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_clock(stamp: Any) -> Optional[datetime]:
    if not isinstance(stamp, str):
        return None
    try:
        d = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        return d.astimezone(timezone.utc) if d.tzinfo else None
    except (ValueError, OverflowError):
        return None


def _fresh(stamp: Any, as_of: datetime, max_age: int = 3600) -> str:
    observed = _parse_clock(stamp)
    if observed is None:
        return "UNKNOWN"
    age = (as_of - observed).total_seconds()
    return "UNKNOWN" if age < 0 else "FRESH" if age <= max_age else "STALE"


class MasterReadService:
    """SQLite mode=ro; if generation changes, reject old pagination cursor."""

    def __init__(
        self, db_path: str, *,
        bindings: Optional[Mapping[str, list[dict[str, Any]]]] = None,
        reviews: Optional[Mapping[str, dict[str, Any]]] = None,
        current_heads: Optional[Mapping[str, str]] = None,
    ):
        self.db_path = str(db_path)
        self.bindings = dict(bindings or {})
        self.reviews = dict(reviews or {})
        self.current_heads = dict(current_heads or {})

    def _conn(self):
        path = Path(self.db_path).resolve()
        if not path.is_file():
            raise FileNotFoundError("Owner panel source ledger not available")
        conn = sqlite3.connect("file:" + urllib.parse.quote(str(path), safe="/:") +
                               "?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    def _source_state(self, conn, pid: str) -> dict[str, Any]:
        row = conn.execute(
            "SELECT * FROM scans WHERE project_id=?", (pid,)
        ).fetchone()
        return dict(row) if row else {
            "status": "UNKNOWN", "last_fetch_at": None,
            "completed_at": None, "failure_code": None,
            "failure_kind": None, "issue_page": None,
            "issue_index": None, "comment_page": None,
        }

    @staticmethod
    def _generation(conn, pid: str) -> str:
        versions = conn.execute("""
            SELECT COUNT(*) n, COALESCE(SUM(version),0) cumulative
            FROM versions WHERE project_id=?
        """, (pid,)).fetchone()
        scanned = conn.execute("""
            SELECT scan_id,status,issue_page,issue_index,comment_page,
                   last_fetch_at,failure_code,failure_kind
            FROM scans WHERE project_id=?
        """, (pid,)).fetchone()
        basis = {
            "project": pid, "version_count": versions["n"],
            "version_sum": versions["cumulative"],
            "source": dict(scanned) if scanned else None,
        }
        return hashlib.sha256(
            json.dumps(basis, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    @staticmethod
    def _cursor_encode(generation: str, pid: str, offset: int) -> str:
        body = json.dumps({
            "schema": ROW_SCHEMA_VERSION, "generation": generation,
            "project_id": pid, "offset": offset,
        }, sort_keys=True, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(body).decode().rstrip("=")

    @staticmethod
    def _cursor_decode(value: str, generation: str, pid: str) -> int:
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,512}", value):
            raise ValueError("Invalid cursor")
        try:
            raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
            obj = json.loads(raw)
        except (ValueError, UnicodeError) as exc:
            raise ValueError("Malformed cursor") from exc
        if (not isinstance(obj, dict) or set(obj) != {
            "schema", "generation", "project_id", "offset"
        }):
            raise ValueError("Malformed cursor")
        if obj["generation"] != generation:
            raise LookupError("Expired generation")
        if obj["schema"] != ROW_SCHEMA_VERSION or obj["project_id"] != pid:
            raise ValueError("Cursor scope mismatch")
        if type(obj["offset"]) is not int or obj["offset"] < 0:
            raise ValueError("Invalid cursor offset")
        return obj["offset"]

    def projects(self) -> dict[str, Any]:
        with self._conn() as conn:
            as_of = _now()
            projects = []
            for pid, reg in sorted(ALLOWLIST.items()):
                state = self._source_state(conn, pid)
                projects.append({
                    "project_id": pid, "repo_id": reg.repo_id,
                    "repo_full_name": reg.repo_full_name,
                    "source_state": state["status"],
                    "source_freshness": _fresh(state["last_fetch_at"], as_of),
                })
            return {"schema_version": ROW_SCHEMA_VERSION, "projects": projects}

    def sources(self) -> dict[str, Any]:
        with self._conn() as conn:
            as_of = _now()
            items = []
            for pid, reg in sorted(ALLOWLIST.items()):
                row = self._source_state(conn, pid)
                items.append({
                    "project_id": pid, "repo_id": reg.repo_id,
                    "repo_full_name": reg.repo_full_name,
                    "state": row["status"],
                    "freshness": _fresh(row["last_fetch_at"], as_of),
                    "last_fetch_at_utc": row["last_fetch_at"],
                    "completed_at_utc": row["completed_at"],
                    "error_code": row["failure_code"],
                    "error_kind": row["failure_kind"],
                    "cursor": {
                        "issue_page": row["issue_page"],
                        "issue_index": row["issue_index"],
                        "comment_page": row["comment_page"],
                    },
                })
            return {"schema_version": ROW_SCHEMA_VERSION, "sources": items}

    def rows(self, pid: str, limit: int = 50,
             cursor: Optional[str] = None) -> dict[str, Any]:
        if pid not in ALLOWLIST:
            raise ValueError("Unregistered project")
        if type(limit) is not int or not 1 <= limit <= 200:
            raise ValueError("Invalid page limit")
        with self._conn() as conn:
            state = self._source_state(conn, pid)
            generation = self._generation(conn, pid)
            offset = self._cursor_decode(cursor, generation, pid) if cursor else 0
            actual = conn.execute("""
                SELECT * FROM objects WHERE project_id=?
                ORDER BY repo_id,kind,entity_id LIMIT ? OFFSET ?
            """, (pid,limit+1,offset)).fetchall()
            as_of = _now()
            output = []
            for record in actual[:limit]:
                item = dict(record)
                source = SourceIdentity(
                    project_id=item["project_id"], repo_id=item["repo_id"],
                    repo_full_name=ALLOWLIST[pid].repo_full_name,
                    kind=SourceKind(item["kind"]), entity_id=item["entity_id"],
                    revision_id=item["revision_id"],
                    issue_number=item["issue_number"],
                    comment_id=item["comment_id"],
                    body_sha256=item["body_sha256"],
                    created_at_utc=item["created_at_utc"],
                    updated_at_utc=item["updated_at_utc"],
                    url=item["source_url"],
                )
                key = source.stable_key
                output.append(build_row(
                    source,
                    bindings=self.bindings.get(key, ()),
                    report=json.loads(item["report_json"]) if item.get("report_json") else None,
                    review=self.reviews.get(key),
                    current_pr_head_sha=self.current_heads.get(key),
                    source_state=state["status"],
                    observed_at_utc=state["last_fetch_at"],
                    freshness=_fresh(state["last_fetch_at"], as_of),
                    completed_scan=state["status"] == "REACHABLE" and
                                   state["completed_at"] is not None,
                    present=not bool(item["deleted"]),
                ))
            return {
                "schema_version": ROW_SCHEMA_VERSION,
                "project_id": pid, "generation": generation,
                "items": output, "has_more": len(actual) > limit,
                "next_cursor": self._cursor_encode(
                    generation, pid, offset+limit
                ) if len(actual) > limit else None,
            }


class MasterPanelHandler(http.server.BaseHTTPRequestHandler):
    service: MasterReadService

    def log_message(self, fmt, *args):
        # Never log query, source refs, credentials or internal paths.
        pass

    def do_GET(self):
        parsed = urllib.parse.urlsplit(self.path)
        host = self.headers.get("Host", "")
        if host not in ("127.0.0.1:" + str(self.server.server_port),
                        "localhost:" + str(self.server.server_port)):
            return self._reply(400, {"error": "Invalid Host"})
        origin = self.headers.get("Origin")
        if origin and origin not in (
            "http://127.0.0.1:" + str(self.server.server_port),
            "http://localhost:" + str(self.server.server_port)
        ):
            return self._reply(403, {"error": "Cross-origin request denied"})
        params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
        if any(len(vals) != 1 for vals in params.values()):
            return self._reply(400, {"error": "Ambiguous query"})
        try:
            if parsed.path == "/api/master/v1/projects" and not params:
                result = self.service.projects()
            elif parsed.path == "/api/master/v1/sources" and not params:
                result = self.service.sources()
            elif parsed.path == "/api/master/v1/rows":
                if set(params) - {"project_id", "limit", "cursor"}:
                    raise ValueError("Unknown query")
                pid = params.get("project_id", [""])[0]
                raw_limit = params.get("limit", ["50"])[0]
                if not re.fullmatch(r"[0-9]{1,3}", raw_limit):
                    raise ValueError("Invalid page limit")
                result = self.service.rows(
                    pid, int(raw_limit), params.get("cursor", [None])[0]
                )
            else:
                return self._reply(404, {"error": "Not Found"})
            return self._reply(200, result)
        except FileNotFoundError:
            return self._reply(503, {"error": "Source ledger unavailable"})
        except LookupError:
            return self._reply(409, {"error": "Expired cursor"})
        except (ValueError, sqlite3.DatabaseError):
            return self._reply(400, {"error": "Invalid request or ledger"})

    def _reply(self, code: int, data: dict[str, Any]):
        raw = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        # Deliberately no CORS authorization header: reject cross-origin reads.
        self.end_headers()
        self.wfile.write(raw)


def serve(db_path: str, port: int = 8777) -> None:
    if not 1 <= port <= 65535:
        raise ValueError("Invalid loopback port")
    service = MasterReadService(db_path)
    class Handler(MasterPanelHandler):
        pass
    Handler.service = service
    server = http.server.HTTPServer(("127.0.0.1", port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--port", type=int, default=8777)
    opts = ap.parse_args()
    serve(opts.db, opts.port)
