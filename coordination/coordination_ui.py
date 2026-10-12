#!/usr/bin/env python3
"""
Coordination Cockpit — Multi-Project Scalable Server
=====================================================
Replaces the monolithic single-file approach with:
  - Paginated REST API (no full-dump endpoints)
  - Per-file mtime-based incremental scan cache
  - Multi-project support via ui_config.json
  - Static assets served from ui/ subfolder

Usage:
    python coordination_ui.py                # Rebuild static snapshot
    python coordination_ui.py --serve        # Start live server (recommended)
    python coordination_ui.py --serve --port 8080
    python coordination_ui.py --watch        # File-watcher rebuild mode
    python coordination_ui.py --add-project --id myproj --name "My Repo" --dir /path/to/coordination
"""

import os, sys, re, json, time, argparse, threading
import http.server, socketserver, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

# ─── Constants ───────────────────────────────────────────────────────────────

HERE = Path(__file__).parent.resolve()
CONFIG_FILE = HERE / "ui_config.json"
UI_DIR = HERE / "ui"
EXCLUDED_FILES = {"coordination_data.json", "index.html", "ui_config.json"}
IGNORED_DIRS = {"ui", "__pycache__", ".git"}

# ─── Config Loading ───────────────────────────────────────────────────────────

def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"projects": [], "server": {}, "ui": {}}


def save_config(cfg: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def resolve_project_dir(project: dict) -> Path:
    raw = project.get("coordination_dir", ".")
    p = Path(raw)
    return p if p.is_absolute() else (HERE / p).resolve()

# ─── Incremental Scan Cache ───────────────────────────────────────────────────

class ScanCache:
    """Per-file mtime cache. Only re-parses files that actually changed."""

    def __init__(self):
        self._lock = threading.Lock()
        # { abs_path_str -> {"mtime": float, "data": Any} }
        self._entries: dict[str, dict] = {}
        # Project-level manifest cache
        # { project_id -> {"manifest": ..., "built_at": float, "mtimes": dict} }
        self._manifests: dict[str, dict] = {}

    def get_or_parse(self, path: Path, parser_fn, *args):
        key = str(path)
        try:
            mtime = path.stat().st_mtime
        except OSError:
            return None
        with self._lock:
            entry = self._entries.get(key)
            if entry and entry["mtime"] == mtime:
                return entry["data"]
        # Parse outside lock to avoid blocking
        result = parser_fn(path, *args)
        with self._lock:
            self._entries[key] = {"mtime": mtime, "data": result}
        return result

    def invalidate_project(self, project_id: str):
        with self._lock:
            self._manifests.pop(project_id, None)


CACHE = ScanCache()

# ─── File Parsers ─────────────────────────────────────────────────────────────

def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _find_url(text: str) -> str:
    m = re.search(r"(https?://[^\s|\"'<>]+)", text)
    return m.group(1) if m else ""


def _detect_status(line: str) -> str:
    u = line.upper()
    for s in ("ANSWERED", "APPROVAL EVIDENCE", "OWNER CORRECTION", "FOLLOW-UP",
              "VERIFIED", "OPEN", "HOLD"):
        if s in u:
            return s
    return "UNKNOWN"


def parse_decisions(path: Path, session: str, tab: str) -> list[dict]:
    rows = []
    for line in _read(path).splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.upper().startswith("DECISIONS"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 2:
            continue
        date_m = re.match(r"^\d{4}-\d{2}-\d{2}", parts[0])
        chat_m = re.search(r"chat=([^\s|,]+)", line)
        id_m = re.search(r"\b(D-\d+-\d+|D[1-5]|BUDDY-[A-Z0-9\-]+)\b", line)
        # Pick longest non-URL part as description
        descs = [p for p in parts if len(p) > 12 and "http" not in p and "chat=" not in p]
        rows.append({
            "session": session, "tab": tab,
            "date": parts[0] if date_m else "",
            "chat": chat_m.group(1) if chat_m else "",
            "id": id_m.group(1) if id_m else "",
            "status": _detect_status(line),
            "description": descs[0][:300] if descs else parts[-1][:300],
            "link": _find_url(line),
        })
    return rows


def parse_checkpoints(path: Path, session: str, tab: str) -> list[dict]:
    items, cur = [], None
    for line in _read(path).splitlines():
        t = line.strip()
        if not t:
            continue
        is_new = (re.match(r"^\d{4}-\d{2}-\d{2}\s*[|/]", t)
                  or re.match(r"^##\s+\d{4}-\d{2}-\d{2}", t))
        if is_new:
            if cur:
                items.append(cur)
            date_m = re.search(r"(\d{4}-\d{2}-\d{2})", t)
            chat_m = re.search(r"chat=([^\s|,]+)", t)
            cur = {"session": session, "tab": tab,
                   "date": date_m.group(1) if date_m else "",
                   "chat": chat_m.group(1) if chat_m else "",
                   "title": t[:200], "body": ""}
        elif cur and len(cur["body"]) < 600:
            cur["body"] += t + "\n"
    if cur:
        items.append(cur)
    return items


def parse_lineage(path: Path, session: str, tab: str) -> list[dict]:
    rows = []
    for line in _read(path).splitlines():
        t = line.strip()
        if not t or t.startswith("#"):
            continue
        if re.match(r"^\d{4}-\d{2}-\d{2}", t):
            parts = [p.strip() for p in t.split("|")]
            chat_m = re.search(r"chat=([^\s|,]+)", t)
            rows.append({
                "session": session, "tab": tab,
                "date": parts[0],
                "chat": chat_m.group(1) if chat_m else "",
                "summary": parts[2][:250] if len(parts) > 2 else t[:250],
            })
    return rows


def parse_handovers(ho_dir: Path, session: str, tab: str) -> list[dict]:
    results = []
    if not ho_dir.is_dir():
        return results
    for f in ho_dir.iterdir():
        if not f.is_file():
            continue
        head = _read(f)[:1500]
        hid_m = re.search(r"\*\*Handover ID:\*\*\s*`?([^`\n]{3,80})`?", head, re.I)
        out_m = re.search(r"\*\*Outgoing:\*\*\s*([^;\n]{3,60})", head, re.I)
        stage = "GENERAL"
        fn = f.name.lower()
        if "stage1" in fn or fn.endswith("-1a.md"):
            stage = "STAGE 1"
        elif "stage2" in fn or fn.endswith("-2.md") or "baseline" in fn:
            stage = "STAGE 2"
        elif "review" in fn:
            stage = "REVIEW"
        results.append({
            "session": session, "tab": tab,
            "filename": f.name,
            "path": str(f.relative_to(f.parent.parent.parent.parent)).replace("\\", "/"),
            "size": f.stat().st_size,
            "updated": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d"),
            "handover_id": hid_m.group(1).strip() if hid_m else "",
            "outgoing": out_m.group(1).strip() if out_m else "",
            "stage": stage,
        })
    return sorted(results, key=lambda x: x["filename"])


def parse_evidence(path: Path, session: str, tab: str) -> list[dict]:
    content = _read(path)
    records = []
    blocks = re.split(r"(?:^|\n)(?=Outcome:\s*O\d+|LOG\s*\|)", content)
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        task_m = re.search(r"Task:\s*([^\n]+)", b)
        status_m = re.search(r"Status:\s*([^\n]+)", b)
        outcome_m = re.search(r"Outcome:\s*([^\n]+)", b)
        chat_m = re.search(r"chat=([^\s|,]+)", b)
        records.append({
            "session": session, "tab": tab,
            "task": (task_m.group(1).strip()[:80] if task_m else ""),
            "status": (status_m.group(1).strip()[:80] if status_m else ""),
            "outcome": (outcome_m.group(1).strip()[:40] if outcome_m else ""),
            "chat": (chat_m.group(1).strip() if chat_m else ""),
            "snippet": b[:300],
        })
    return records


def parse_tabs_index(tabs_file: Path) -> list[dict]:
    rows = []
    if not tabs_file.exists():
        return rows
    for line in _read(tabs_file).splitlines():
        t = line.strip()
        if not t or t.startswith("#") or "SESSION_" in t.upper():
            continue
        parts = [p.strip() for p in t.split("|")]
        if len(parts) < 3:
            continue
        meta = {}
        for p in parts:
            for k, v in re.findall(r"([a-zA-Z0-9_\-]+)=([^\s|]+)", p):
                meta[k] = v
        rows.append({
            "date": parts[0] if re.match(r"\d{4}", parts[0]) else "",
            "tab_num": parts[1],
            "name": parts[2],
            "path": parts[3] if len(parts) > 3 and "coordination/" in parts[3] else "",
            "meta": meta,
        })
    return rows

# ─── Project Scanner ──────────────────────────────────────────────────────────

def scan_tab(coord_dir: Path, session_name: str, tab_name: str) -> dict:
    """Scan one Tab directory. Uses per-file cache."""
    t_path = coord_dir / session_name / tab_name

    def cached(fname, parser, *extra):
        fp = t_path / fname
        if not fp.exists():
            return []
        return CACHE.get_or_parse(fp, parser, session_name, tab_name) or []

    decisions = cached("DECISIONS.md", parse_decisions)
    checkpoints = cached("CHECKPOINTS.md", parse_checkpoints)
    lineage = cached("LINEAGE.md", parse_lineage)
    evidence = cached("EVIDENCE.log", parse_evidence)
    handovers = CACHE.get_or_parse(
        t_path / "handovers" / "_dir_",  # sentinel key; we handle dir specially
        lambda *_: None  # we'll do it below
    )
    # Handovers: parse dir (no single-file caching for directories; use mtime of newest file)
    ho_dir = t_path / "handovers"
    ho_mtime = 0.0
    if ho_dir.is_dir():
        for f in ho_dir.iterdir():
            try:
                m = f.stat().st_mtime
                if m > ho_mtime:
                    ho_mtime = m
            except OSError:
                pass
    # Store under sentinel key
    sentinel = str(ho_dir / "__dir__")
    existing = CACHE._entries.get(sentinel, {})
    if existing.get("mtime") != ho_mtime:
        handovers_list = parse_handovers(ho_dir, session_name, tab_name)
        with CACHE._lock:
            CACHE._entries[sentinel] = {"mtime": ho_mtime, "data": handovers_list}
    else:
        handovers_list = existing.get("data", [])

    # JSON receipts & special reports (flat files in tab dir)
    json_receipts = []
    special_files = []
    known = {"DECISIONS.md", "CHECKPOINTS.md", "LINEAGE.md", "INPUTS.md",
              "ARTIFACTS.md", "STATUS.md", "EVIDENCE.log"}
    if t_path.exists():
        for f in t_path.iterdir():
            if not f.is_file():
                continue
            if f.name in known:
                continue
            if f.suffix == ".json":
                try:
                    data = json.loads(f.read_text(encoding="utf-8", errors="ignore"))
                    json_receipts.append({
                        "filename": f.name,
                        "path": str(f.relative_to(coord_dir)).replace("\\", "/"),
                        "schema": data.get("schema", data.get("$schema", "receipt")),
                        "size": f.stat().st_size,
                        "data": data,
                    })
                except Exception:
                    pass
            elif f.suffix == ".md":
                special_files.append({
                    "filename": f.name,
                    "path": str(f.relative_to(coord_dir)).replace("\\", "/"),
                    "size": f.stat().st_size,
                })

    return {
        "name": tab_name,
        "session": session_name,
        "decisions": decisions,
        "checkpoints": checkpoints,
        "lineage": lineage,
        "evidence": evidence,
        "handovers": handovers_list,
        "json_receipts": json_receipts,
        "special_files": special_files,
        "counts": {
            "decisions": len(decisions),
            "checkpoints": len(checkpoints),
            "lineage": len(lineage),
            "evidence": len(evidence),
            "handovers": len(handovers_list),
        },
    }


def scan_project(project: dict) -> dict:
    """Full scan of one project. Returns manifest + per-tab data."""
    coord_dir = resolve_project_dir(project)
    pid = project["id"]

    sessions_data = []
    all_decisions, all_checkpoints, all_handovers = [], [], []
    all_files = []

    # Gather all files for the index (metadata only)
    for root, dirs, files in os.walk(coord_dir):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for fname in files:
            fp = Path(root) / fname
            if fname in EXCLUDED_FILES:
                continue
            rel = str(fp.relative_to(coord_dir)).replace("\\", "/")
            all_files.append({
                "name": fname,
                "path": rel,
                "ext": fp.suffix.lower(),
                "size": fp.stat().st_size,
            })

    # Discover sessions
    session_dirs = sorted(
        d for d in coord_dir.iterdir()
        if d.is_dir() and d.name.startswith("Session_") and d.name not in IGNORED_DIRS
    )

    for s_dir in session_dirs:
        s_name = s_dir.name
        tabs_index = CACHE.get_or_parse(s_dir / "TABS.md", lambda p, *_: parse_tabs_index(p)) or []

        tab_dirs = sorted(d for d in s_dir.iterdir() if d.is_dir() and d.name not in IGNORED_DIRS)
        tab_summaries = []

        for t_dir in tab_dirs:
            t_name = t_dir.name
            reg = next((r for r in tabs_index
                        if r["tab_num"] in t_name or t_name.startswith(r["tab_num"])), None)

            tab_data = scan_tab(coord_dir, s_name, t_name)

            all_decisions.extend(tab_data["decisions"])
            all_checkpoints.extend(tab_data["checkpoints"])
            all_handovers.extend(tab_data["handovers"])

            tab_summaries.append({
                "name": t_name,
                "title": reg["name"] if reg else t_name.replace("_", " "),
                "chat": reg["meta"].get("chat", "") if reg else "",
                "issue": reg["meta"].get("issue", "") if reg else "",
                "status": (reg["meta"].get("status", reg["meta"].get("state", "ACTIVE"))
                           if reg else "ACTIVE"),
                "plan": reg["meta"].get("plan", "") if reg else "",
                "counts": tab_data["counts"],
            })

        sessions_data.append({
            "id": s_name,
            "title": s_name.replace("_", " "),
            "tabs": tab_summaries,
        })

    # Decision status breakdown
    status_counts: dict[str, int] = {}
    for d in all_decisions:
        st = d["status"]
        status_counts[st] = status_counts.get(st, 0) + 1

    return {
        "project": {k: v for k, v in project.items() if k != "coordination_dir"},
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
        "summary": {
            "total_sessions": len(sessions_data),
            "total_tabs": sum(len(s["tabs"]) for s in sessions_data),
            "total_decisions": len(all_decisions),
            "total_checkpoints": len(all_checkpoints),
            "total_handovers": len(all_handovers),
            "total_files": len(all_files),
            "decision_statuses": status_counts,
        },
        "sessions": sessions_data,
        # Full data — only used by static builder; server uses paginated endpoints
        "_all_decisions": all_decisions,
        "_all_checkpoints": all_checkpoints,
        "_all_handovers": all_handovers,
        "_files_index": all_files,
    }

# ─── Paginated helpers ────────────────────────────────────────────────────────

def paginate(items: list, page: int, limit: int) -> dict:
    total = len(items)
    start = (page - 1) * limit
    end = start + limit
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit if limit > 0 else 1,
        "items": items[start:end],
    }


def filter_items(items: list, q: str, keys: list[str]) -> list:
    if not q:
        return items
    q = q.lower()
    return [it for it in items
            if any(q in str(it.get(k, "")).lower() for k in keys)]

# ─── Per-project in-memory data store with TTL ───────────────────────────────

class DataStore:
    def __init__(self, ttl: float = 15.0):
        self._lock = threading.Lock()
        self._ttl = ttl
        self._data: dict[str, dict] = {}   # project_id -> full scan result
        self._fetched: dict[str, float] = {}  # project_id -> timestamp

    def get(self, project: dict, force: bool = False) -> dict:
        pid = project["id"]
        with self._lock:
            age = time.monotonic() - self._fetched.get(pid, 0.0)
            if not force and pid in self._data and age < self._ttl:
                return self._data[pid]
        # Scan outside lock
        result = scan_project(project)
        with self._lock:
            self._data[pid] = result
            self._fetched[pid] = time.monotonic()
        return result

    def find_tab_data(self, project: dict, session: str, tab: str) -> dict | None:
        coord_dir = resolve_project_dir(project)
        t_path = coord_dir / session / tab
        if not t_path.is_dir():
            return None
        return scan_tab(coord_dir, session, tab)


STORE = DataStore()

# ─── Path Containment Helper ──────────────────────────────────────────────────

def is_safe_contained_path(target: Path, root: Path) -> bool:
    """Ensure target path is strictly contained within root path and resolves safely."""
    try:
        resolved_target = target.resolve()
        resolved_root = root.resolve()
        return os.path.commonpath([str(resolved_target), str(resolved_root)]) == str(resolved_root)
    except (ValueError, OSError):
        return False

# ─── HTTP API Handler ─────────────────────────────────────────────────────────

class ApiHandler(http.server.BaseHTTPRequestHandler):
    config: dict = {}
    server_host: str = "127.0.0.1"

    def log_message(self, fmt, *args):
        pass  # suppress request logs for cleanliness

    def _send_common_headers(self, content_type: str, length: int):
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com;")
        # Same-origin policy: do NOT send wildcard Access-Control-Allow-Origin: *
        origin = self.headers.get("Origin")
        if origin:
            allowed_origins = self.config.get("server", {}).get("allowed_origins", [])
            if origin in allowed_origins:
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")

    def send_json(self, obj, status: int = 200):
        body = json.dumps(obj, separators=(",", ":")).encode()
        self.send_response(status)
        self._send_common_headers("application/json", len(body))
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, text: str, mime: str = "text/plain; charset=utf-8", status: int = 200):
        body = text.encode("utf-8", errors="replace")
        self.send_response(status)
        self._send_common_headers(mime, len(body))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path: Path, root: Path = UI_DIR):
        if not is_safe_contained_path(path, root):
            self.send_text("Forbidden", status=403)
            return
        if not path.is_file():
            self.send_text("Not found", status=404)
            return
        mime_map = {
            ".html": "text/html; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".json": "application/json",
        }
        mime = mime_map.get(path.suffix.lower(), "text/plain")
        body = path.read_bytes()
        self.send_response(200)
        self._send_common_headers(mime, len(body))
        self.end_headers()
        self.wfile.write(body)

    def _project(self, params: dict) -> dict | None:
        pid = params.get("project", [""])[0] or self.config["projects"][0]["id"]
        return next((p for p in self.config["projects"] if p["id"] == pid), None)

    def _qs(self) -> dict:
        parsed = urllib.parse.urlparse(self.path)
        return urllib.parse.parse_qs(parsed.query)

    def _int(self, params: dict, key: str, default: int) -> int:
        try:
            return max(1, int(params.get(key, [default])[0]))
        except (ValueError, TypeError):
            return default

    def _str(self, params: dict, key: str, default: str = "") -> str:
        return params.get(key, [default])[0]

    def do_GET(self):
        # Null-byte rejection
        if "\x00" in self.path:
            self.send_text("Invalid request path", status=400)
            return

        # DNS rebinding / Host header validation
        host_header = self.headers.get("Host", "").split(":")[0].strip()
        allowed_hosts = {"127.0.0.1", "localhost", "::1", getattr(self, "server_host", "127.0.0.1")}
        if host_header and host_header not in allowed_hosts and not self.config.get("server", {}).get("allow_any_host", False):
            self.send_text("Invalid Host header (DNS rebinding protection)", status=400)
            return

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        qs = urllib.parse.parse_qs(parsed.query)

        # ── Static files ─────────────────────────────────
        if path == "/" or path == "/index.html":
            self.send_file(UI_DIR / "index.html", root=UI_DIR)
            return
        if path.startswith("/ui/"):
            target_file = UI_DIR / path[4:]
            self.send_file(target_file, root=UI_DIR)
            return
        asset_candidate = UI_DIR / path.lstrip("/")
        if is_safe_contained_path(asset_candidate, UI_DIR) and asset_candidate.is_file():
            self.send_file(asset_candidate, root=UI_DIR)
            return

        # ── API Routes ────────────────────────────────────
        if not path.startswith("/api/"):
            self.send_text("Not found", status=404)
            return

        route = path[5:]  # strip /api/

        # GET /api/status
        if route == "status":
            projects = [{"id": p["id"], "name": p["name"]} for p in self.config["projects"]]
            self.send_json({"ok": True, "projects": projects,
                            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
            return

        # GET /api/manifest?project=ID
        if route == "manifest":
            proj = self._project(qs)
            if not proj:
                self.send_json({"error": "Unknown project"}, 404)
                return
            data = STORE.get(proj)
            self.send_json({
                "project": data["project"],
                "generated_at": data["generated_at"],
                "summary": data["summary"],
                "sessions": data["sessions"],
            })
            return

        # GET /api/projects
        if route == "projects":
            self.send_json([{"id": p["id"], "name": p["name"],
                             "description": p.get("description", "")}
                            for p in self.config["projects"]])
            return

        # GET /api/decisions?project=&session=&tab=&status=&q=&page=1&limit=50
        if route == "decisions":
            proj = self._project(qs)
            if not proj:
                self.send_json({"error": "Unknown project"}, 404)
                return
            data = STORE.get(proj)
            items = data["_all_decisions"]
            # Filter
            sess = self._str(qs, "session")
            tab = self._str(qs, "tab")
            status = self._str(qs, "status")
            q = self._str(qs, "q")
            if sess:
                items = [d for d in items if d["session"] == sess]
            if tab:
                items = [d for d in items if d["tab"] == tab]
            if status and status != "ALL":
                items = [d for d in items if d["status"] == status]
            if q:
                items = filter_items(items, q,
                                     ["description", "id", "chat", "status", "date"])
            limit = min(self._int(qs, "limit", 50),
                        self.config.get("server", {}).get("max_page_size", 500))
            self.send_json(paginate(items, self._int(qs, "page", 1), limit))
            return

        # GET /api/checkpoints?project=&session=&tab=&q=&page=1&limit=50
        if route == "checkpoints":
            proj = self._project(qs)
            if not proj:
                self.send_json({"error": "Unknown project"}, 404)
                return
            data = STORE.get(proj)
            items = data["_all_checkpoints"]
            sess = self._str(qs, "session")
            tab = self._str(qs, "tab")
            q = self._str(qs, "q")
            if sess:
                items = [d for d in items if d["session"] == sess]
            if tab:
                items = [d for d in items if d["tab"] == tab]
            if q:
                items = filter_items(items, q, ["title", "body", "chat", "date"])
            limit = min(self._int(qs, "limit", 50),
                        self.config.get("server", {}).get("max_page_size", 500))
            self.send_json(paginate(items, self._int(qs, "page", 1), limit))
            return

        # GET /api/handovers?project=&session=&tab=&stage=&q=&page=1&limit=50
        if route == "handovers":
            proj = self._project(qs)
            if not proj:
                self.send_json({"error": "Unknown project"}, 404)
                return
            data = STORE.get(proj)
            items = data["_all_handovers"]
            sess = self._str(qs, "session")
            tab = self._str(qs, "tab")
            stage = self._str(qs, "stage")
            q = self._str(qs, "q")
            if sess:
                items = [d for d in items if d["session"] == sess]
            if tab:
                items = [d for d in items if d["tab"] == tab]
            if stage and stage != "ALL":
                items = [d for d in items if d["stage"] == stage]
            if q:
                items = filter_items(items, q, ["filename", "handover_id", "outgoing", "stage"])
            limit = min(self._int(qs, "limit", 50),
                        self.config.get("server", {}).get("max_page_size", 500))
            self.send_json(paginate(items, self._int(qs, "page", 1), limit))
            return

        # GET /api/tab?project=&session=&tab=
        if route == "tab":
            proj = self._project(qs)
            if not proj:
                self.send_json({"error": "Unknown project"}, 404)
                return
            sess = self._str(qs, "session")
            tab = self._str(qs, "tab")
            if not sess or not tab:
                self.send_json({"error": "session and tab required"}, 400)
                return
            tab_data = STORE.find_tab_data(proj, sess, tab)
            if not tab_data:
                self.send_json({"error": "Tab not found"}, 404)
                return
            # Return without heavy full data — summary + receipts
            self.send_json({
                "name": tab_data["name"],
                "counts": tab_data["counts"],
                "json_receipts": tab_data["json_receipts"],
                "special_files": tab_data["special_files"],
            })
            return

        # GET /api/files?project=&q=
        if route == "files":
            proj = self._project(qs)
            if not proj:
                self.send_json({"error": "Unknown project"}, 404)
                return
            data = STORE.get(proj)
            items = data["_files_index"]
            q = self._str(qs, "q")
            if q:
                items = filter_items(items, q, ["name", "path"])
            limit = min(self._int(qs, "limit", 200),
                        self.config.get("server", {}).get("max_page_size", 500))
            self.send_json(paginate(items, self._int(qs, "page", 1), limit))
            return

        # GET /api/file?project=&path=<rel_path>
        if route == "file":
            proj = self._project(qs)
            if not proj:
                self.send_json({"error": "Unknown project"}, 404)
                return
            rel_path = self._str(qs, "path")
            coord_dir = resolve_project_dir(proj)
            target = coord_dir / rel_path
            # Security: strict canonical path containment check
            if not is_safe_contained_path(target, coord_dir):
                self.send_text("Forbidden", status=403)
                return
            if not target.is_file():
                self.send_text("Not found", status=404)
                return
            # Configurable read quota protection (HTTP 413 / TOO_LARGE)
            max_quota = self.config.get("server", {}).get("max_file_read_bytes", 5 * 1024 * 1024)
            file_size = target.stat().st_size
            if file_size > max_quota:
                self.send_json({
                    "error": f"File size ({file_size:,} bytes) exceeds read quota ({max_quota:,} bytes)",
                    "code": "TOO_LARGE",
                    "size": file_size,
                    "limit": max_quota
                }, status=413)
                return
            mime = ("application/json" if target.suffix == ".json"
                    else "text/plain; charset=utf-8")
            self.send_text(_read(target), mime=mime)
            return

        # GET /api/qrt?project=
        if route == "qrt":
            proj = self._project(qs)
            if not proj:
                self.send_json({"error": "Unknown project"}, 404)
                return
            coord_dir = resolve_project_dir(proj)
            monitor_file = coord_dir / "Session_Oct09" / "Tab1_imo_core_blueprints" / "182-P6-28-CELL-AGENT-MONITOR.json"
            if not monitor_file.exists():
                self.send_json({"cells": []})
                return
            try:
                self.send_json(json.loads(_read(monitor_file)))
            except Exception:
                self.send_json({"cells": []})
            return

        self.send_json({"error": "Not found"}, 404)

# ─── Server ───────────────────────────────────────────────────────────────────

def run_server(config: dict, port: int, host: str = "127.0.0.1", open_browser: bool = True, allow_remote_unauthenticated: bool = False):
    """Start the live HTTP server with loopback by default and security validation."""
    if host not in ("127.0.0.1", "localhost", "::1") and not allow_remote_unauthenticated:
        print(f"[SECURITY ERROR] Refusing to bind to non-loopback address ('{host}') without an authenticated TLS gateway.")
        print("To override for testing only, pass --allow-remote-unauthenticated.")
        sys.exit(1)
    if host not in ("127.0.0.1", "localhost", "::1") and allow_remote_unauthenticated:
        print("\n" + "!" * 65)
        print("  [SECURITY WARNING] Binding to non-loopback address without authentication!")
        print("  Coordination documents are exposed unauthenticated on the network.")
        print("!" * 65 + "\n")

    # Pre-warm cache
    print("[INIT] Pre-scanning projects...")
    for proj in config["projects"]:
        t0 = time.monotonic()
        data = STORE.get(proj)
        dt = round(time.monotonic() - t0, 2)
        print(f"  [{proj['id']}] {data['summary']['total_decisions']} decisions, "
              f"{data['summary']['total_files']} files — {dt}s")

    # Bind handler with config injected
    class BoundHandler(ApiHandler):
        pass
    BoundHandler.config = config
    BoundHandler.server_host = host

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((host, port), BoundHandler) as httpd:
        url = f"http://{host}:{port}"
        print(f"\n{'='*55}")
        print(f"  Coordination Cockpit running at:  {url}")
        print(f"  REST API:  {url}/api/manifest?project=common")
        print(f"  Press Ctrl+C to stop.")
        print(f"{'='*55}\n")
        if open_browser:
            import webbrowser
            try:
                webbrowser.open(url)
            except Exception:
                pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[STOP] Server stopped.")

# ─── Watcher ──────────────────────────────────────────────────────────────────

def run_watcher(config: dict, interval: float = 4.0):
    print(f"[WATCH] Polling for changes every {interval}s. Ctrl+C to stop.")
    last_mtimes: dict[str, float] = {}
    while True:
        try:
            changed = False
            for proj in config["projects"]:
                coord_dir = resolve_project_dir(proj)
                for root, dirs, files in os.walk(coord_dir):
                    dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
                    for f in files:
                        if f in EXCLUDED_FILES:
                            continue
                        fp = str(Path(root) / f)
                        try:
                            m = os.path.getmtime(fp)
                        except OSError:
                            continue
                        if last_mtimes.get(fp) != m:
                            last_mtimes[fp] = m
                            changed = True
            if changed:
                ts = datetime.now().strftime("%H:%M:%S")
                print(f"[{ts}] Changes detected. Rebuilding static snapshot...")
                build_static(config)
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[WATCH] Stopped.")
            break

# ─── Static Builder ───────────────────────────────────────────────────────────

def build_static(config: dict):
    """Build coordination_data.json (no embedded HTML; server reference only)."""
    all_projects = []
    for proj in config["projects"]:
        t0 = time.monotonic()
        data = STORE.get(proj, force=True)
        dt = round(time.monotonic() - t0, 2)
        # Strip huge internal fields for static export
        export = {
            "project": data["project"],
            "generated_at": data["generated_at"],
            "summary": data["summary"],
            "sessions": data["sessions"],
            "decisions": data["_all_decisions"],
            "checkpoints": data["_all_checkpoints"],
            "handovers": data["_all_handovers"],
            "files_index": data["_files_index"],
        }
        all_projects.append(export)
        print(f"  [{proj['id']}] scanned in {dt}s: "
              f"{data['summary']['total_decisions']} decisions, "
              f"{data['summary']['total_files']} files")

    out_file = HERE / "coordination_data.json"
    payload = {"version": 1, "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
               "projects": all_projects}
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, separators=(",", ":"))
    print(f"  [OK] coordination_data.json — {out_file.stat().st_size:,} bytes")

# ─── CLI ──────────────────────────────────────────────────────────────────────

def cmd_add_project(args):
    cfg = load_config()
    cfg.setdefault("projects", [])
    pid = args.id
    if any(p["id"] == pid for p in cfg["projects"]):
        print(f"[ERROR] Project '{pid}' already exists.")
        sys.exit(1)
    cfg["projects"].append({
        "id": pid,
        "name": args.name or pid,
        "repo_url": args.repo or "",
        "coordination_dir": str(args.dir),
        "description": args.desc or "",
    })
    save_config(cfg)
    print(f"[OK] Added project '{pid}'. Re-run with --serve to include it.")


def main():
    parser = argparse.ArgumentParser(
        description="Coordination Cockpit — multi-project, scalable server")
    parser.add_argument("--serve", action="store_true",
                        help="Start live HTTP server (recommended)")
    parser.add_argument("--port", type=int, default=None,
                        help="HTTP port (overrides ui_config.json)")
    parser.add_argument("--host", default="127.0.0.1",
                        help="HTTP host to bind (default: 127.0.0.1 loopback only)")
    parser.add_argument("--allow-remote-unauthenticated", action="store_true",
                        help="Explicitly permit non-loopback binding without authentication")
    parser.add_argument("--no-browser", action="store_true",
                        help="Don't open browser automatically")
    parser.add_argument("--watch", action="store_true",
                        help="Watch for file changes and auto-rebuild static snapshot")
    parser.add_argument("--add-project", action="store_true",
                        help="Add a new project to ui_config.json")
    parser.add_argument("--id", help="Project ID (for --add-project)")
    parser.add_argument("--name", help="Project display name")
    parser.add_argument("--dir", help="Absolute path to coordination directory")
    parser.add_argument("--repo", help="GitHub repo URL")
    parser.add_argument("--desc", help="Project description")

    args = parser.parse_args()

    if args.add_project:
        if not args.id or not args.dir:
            print("[ERROR] --add-project requires --id and --dir")
            sys.exit(1)
        cmd_add_project(args)
        return

    config = load_config()
    if not config.get("projects"):
        print("[ERROR] No projects found in ui_config.json. Add at least one project.")
        sys.exit(1)

    port = args.port or config.get("server", {}).get("port", 8080)
    host = args.host or config.get("server", {}).get("host", "127.0.0.1")

    if args.serve:
        run_server(config, port, host=host, open_browser=not args.no_browser,
                   allow_remote_unauthenticated=args.allow_remote_unauthenticated)
    elif args.watch:
        run_watcher(config)
    else:
        print("[BUILD] Scanning all projects...")
        build_static(config)
        print("\n[COMPLETE]")
        print(f"  Open: file:///{(HERE / 'ui' / 'index.html').as_posix()}")
        print(f"  Or run: python coordination_ui.py --serve")


if __name__ == "__main__":
    main()
