# Coordination Cockpit — Multi-Project Scalable Architecture (V2)

Interactive multi-session, multi-tab coordination cockpit and high-performance web dashboard for tracking engineering handovers, decision registers, checkpoints, lineage, and QRT agent monitor boards across `reallakshman19/Common/coordination` and multiple external projects.

Target repository branch commit: [`9d176f8e74bd71c7aa041aababd90ed31455bd9c`](https://github.com/reallakshman19/Common/tree/9d176f8e74bd71c7aa041aababd90ed31455bd9c/coordination).

---

## ⚡ Scalability Architecture (V1 vs V2)

| Dimension | Monolithic V1 (Superseded) | Scalable V2 (Current) |
|---|---|---|
| **Multi-Project Support** | Hardcoded to single local directory | **Config-driven (`ui_config.json`)**; seamlessly registers multiple repositories and paths |
| **Payload Delivery** | Full ~1.1 MB JSON embedded inline inside HTML | **Clean separation**: UI shell is 2 KB; data fetched on-demand via paginated REST API |
| **Parsing Performance** | Full recursive `os.walk` + file parsing on every request | **Incremental mtime cache**: unchanged files are skipped; sub-100ms scans; 0.0s cache hits |
| **DOM Rendering** | Injects all 250+ decisions and 250+ checkpoints at once | **Virtual DOM scrolling (`buildVList`)**: recycles visible DOM nodes; scales to 100,000+ rows smoothly |
| **Code Structure** | 1,800-line Python string containing HTML/CSS/JS | **Modular architecture**: separate `ui/index.html`, `ui/style.css`, `ui/app.js`, and `coordination_ui.py` |
| **API Endpoints** | Single monolithic dump endpoint | **Granular REST API** (`/api/projects`, `/api/decisions`, `/api/checkpoints`, `/api/tab`, etc.) |

---

## 🚀 Quick Start

### 1. Live Dynamic Server (Recommended)

Starts the high-performance local server with automatic real-time caching and REST API:

```bash
# In the coordination directory:
python coordination_ui.py --serve

# Or specify a custom port without auto-opening a browser:
python coordination_ui.py --serve --port 8080 --no-browser
```

Open `http://localhost:8080` in any web browser.

### 2. Multi-Project Registration

You can track multiple independent projects/repositories from the same cockpit interface.

#### Via CLI:
```bash
python coordination_ui.py --add-project \
  --id "grade9" \
  --name "Grade 9 V3.5" \
  --dir "C:/path/to/Grade9v3.5/coordination" \
  --repo "https://github.com/reallakshman19/Grade9v3.5" \
  --desc "Curriculum validation & test harness"
```

#### Via `ui_config.json`:
Edit `ui_config.json` directly to add projects or customize cache TTL / page size limits:

```json
{
  "version": 1,
  "projects": [
    {
      "id": "common",
      "name": "reallakshman19/Common",
      "repo_url": "https://github.com/reallakshman19/Common",
      "commit": "9d176f8e74bd71c7aa041aababd90ed31455bd9c",
      "coordination_dir": ".",
      "description": "Shared engineering skills, governance, coordination docs"
    },
    {
      "id": "grade9",
      "name": "reallakshman19/Grade9v3.5",
      "repo_url": "https://github.com/reallakshman19/Grade9v3.5",
      "coordination_dir": "../Grade9v3.5/coordination",
      "description": "Grade 9 math & physics curriculum delivery"
    }
  ],
  "server": {
    "port": 8080,
    "cache_ttl_seconds": 15,
    "page_size_default": 50,
    "max_page_size": 500
  }
}
```

### 3. File Watcher Mode

Automatically monitors the coordination folders for changes and triggers incremental rebuilds:

```bash
python coordination_ui.py --watch
```

### 4. Build Static Snapshot

Compiles a standalone `coordination_data.json` snapshot:

```bash
python coordination_ui.py
```

---

## 📁 Directory & File Layout

```text
coordination/
├── ui_config.json          # Multi-project registry & server settings
├── coordination_ui.py      # Core server, incremental mtime cache & REST API
├── index.html              # Lightweight launcher/redirect to ui/
├── README.md               # Documentation & architecture guide
│
├── ui/                     # Modular frontend assets (no inline templates)
│   ├── index.html          # Lightweight SPA shell (2 KB)
│   ├── style.css           # Modern themeable design (dark/light, responsive)
│   └── app.js              # SPA logic: virtual scrolling, lazy fetch, filtering
│
├── Session_Oct07/          # Coordination Session Oct 07
│   ├── TABS.md
│   ├── Tab1_V32_Generic_Source_Lifecycle/
│   ├── Tab2_Lifecycle_Evidence_Reconciliation/
│   ├── Tab3_LFJ_Resolver_Review/
│   └── Tab4_Source_Authority_Recovery/
│
└── Session_Oct09/          # Coordination Session Oct 09
    ├── TABS.md
    ├── Tab1_imo_core_blueprints/  (contains 182-P6-28-CELL-AGENT-MONITOR.json)
    ├── Tab1_track-a-integration/
    ├── Tab2_imo_core2_core1a/
    ├── Tab2_track-b-source-custody/
    ├── Tab4_imo_qrt_d1/
    ├── Tab5_imo_qrt_d2/
    ├── Tab6_imo_qrt_d3/
    └── Tab7_imo_qrt_d4/
```

---

## 🌐 REST API Endpoints

All endpoints support project selection via `?project=<project_id>` (defaults to the first project in `ui_config.json`).

| Endpoint | Method | Query Parameters | Description |
|---|---|---|---|
| `/api/status` | GET | — | Server health check, registered projects, and timestamp |
| `/api/projects` | GET | — | List all registered project definitions |
| `/api/manifest` | GET | `project` | Project summary metrics and sessions/tabs catalog |
| `/api/decisions` | GET | `project`, `session`, `tab`, `status`, `q`, `page`, `limit` | Paginated decision register with full-text search & status filter |
| `/api/checkpoints` | GET | `project`, `session`, `tab`, `q`, `page`, `limit` | Paginated checkpoint entries & timeline |
| `/api/handovers` | GET | `project`, `session`, `tab`, `stage`, `q`, `page`, `limit` | Paginated agent handovers with stage classification |
| `/api/tab` | GET | `project`, `session`, `tab` | Tab metadata, receipt schemas, and file summaries |
| `/api/files` | GET | `project`, `q`, `page`, `limit` | File index catalog with size and type metadata |
| `/api/file` | GET | `project`, `path` | Raw content retrieval for safe paths within coordination directory |
| `/api/qrt` | GET | `project` | 28-cell QRT agent monitor matrix board schema and status |

---

## 🌟 Dashboard Views & Features

1. **Executive Overview & KPI Strip**: Instant metrics on tracked decisions, handovers, checkpoints, tabs, and sessions. Session switcher and tab cards with live status badges.
2. **Decisions Register (Virtual Scroll)**: High-performance recycled row rendering for hundreds or thousands of decisions. Filter by status (`OPEN`, `ANSWERED`, `APPROVAL EVIDENCE`, `HOLD`, `OWNER CORRECTION`, `VERIFIED`), session, tab, or search query. Click any row for details and GitHub links.
3. **Interactive 28-Cell QRT Agent Matrix**: 4x7 grid representing `182-P6-28-CELL-AGENT-MONITOR.json` (Bands D1–D4 across demands RETRIEVE, REPRESENT, EXPLAIN, MODEL, JUSTIFY, COMPARE, GENERALIZE). Color-coded states (`UNSTARTED`, `PILOT`, `REVIEWED`, `ACCEPTED`).
4. **Checkpoints Timeline**: Chronological milestone revisions, pass/fail test run receipts, and chat provenance links.
5. **Agent Handovers Hub**: Categorized handovers across stages (`STAGE 1`, `STAGE 2`, `REVIEW`, `GENERAL`) with file viewer modal.
6. **JSON Receipts Inspector**: Audit trails and JSON schemas (`Q003_*`, benchmarks, and verification runs).
7. **File Explorer**: Browse and inspect all coordination markdown, JSON, and log files on demand with live code styling.
8. **Theme Toggle**: Fast dark and light theme switching.

---

## 🛠️ CLI Reference

```text
usage: coordination_ui.py [-h] [--serve] [--port PORT] [--no-browser] [--watch]
                          [--add-project] [--id ID] [--name NAME] [--dir DIR]
                          [--repo REPO] [--desc DESC]

Coordination Cockpit — multi-project, scalable server

options:
  -h, --help      show this help message and exit
  --serve         Start live HTTP server (recommended)
  --port PORT     HTTP port (overrides ui_config.json)
  --no-browser    Don't open browser automatically
  --watch         Watch for file changes and auto-rebuild static snapshot
  --add-project   Add a new project to ui_config.json
  --id ID         Project ID (for --add-project)
  --name NAME     Project display name
  --dir DIR       Absolute or relative path to coordination directory
  --repo REPO     GitHub repo URL
  --desc DESC     Project description
```
