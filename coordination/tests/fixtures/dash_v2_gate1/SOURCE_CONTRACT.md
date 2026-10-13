# Gate 1 Installed-Source Contract & Lineage Specification (R3)

## 1. Document Identity & Purpose

This document provides the authoritative, source-grounded contract for the Coordinator Protocol v3.30 state schema, 10-column table derivation, Smart Economy cadence rules, and error semantics. It repairs Gate 1 evidence defects on branch `feature/dash-v2-gate1-r3-evidence` in `reallakshman19/Common`, addressing reviewer findings in comment `6146969723` and controller directive `6148140363`.

All specifications herein are directly derived from the coordinator protocol PowerShell scripts and skill instructions. All fixture data and examples are strictly **SYNTHETIC** to guarantee zero private environment or credential disclosure. All source locations are referenced by **sanitized relative paths** rather than host-specific absolute paths.

---

## 2. Source Provenance & Cryptographic Hashes

The contract is grounded in the five coordinator protocol files:

| Relative Source Reference | Component / Role | Version / Header | SHA-256 Digest | Taxonomy |
| :--- | :--- | :--- | :--- | :--- |
| `<coordinator-skill-root>/SKILL.md` | Coordinator Policy Core | v3.30 | `e388241adbad15dd744446c4e5b56c5720d850ed29caa09fdafed3bafee31348` | `SCRIPT_DERIVED` |
| `<coordinator-skill-root>/scripts/watch.ps1` | Observation, 10 Cells, Aim | v3.28+ (Aim v2) | `a18d1eb206a2b1444ef55b4da32d55f6b1aea9aa328c85ce8e528ee4713a1b6e` | `SCRIPT_DERIVED` |
| `<coordinator-skill-root>/scripts/ghwatch.ps1` | GitHub Polling, Watermark, Waiter, Relay, Cadence | v3.30 (Smart Economy) | `246c8cc8b8b8af3ab1dd67a3a479966272dfb494f8c9645bf91c4fd91d06cf22` | `SCRIPT_DERIVED` |
| `<coordinator-skill-root>/scripts/cyclestate.ps1` | Session Lifecycle, Tab Mapping, Liveness | v3.26+ | `46f44c71cc1d13875510f237b6ed5f8f44eabc32b885aba557adf221aa172bd9` | `SCRIPT_DERIVED` |
| `<coordinator-skill-root>/scripts/state-io.ps1` | Atomic Mutex-Locked State I/O | v3.27+ | `9f4a2164c5a31c636ebf1bfe991e84f9e4fe2adeed91820682c16c94252d8646` | `SCRIPT_DERIVED` |
| `<coordinator-skill-root>/scripts/aim-lib.ps1` | Shared Sticky Label & Card Library | v3.28 | `9623f038ba658cd254ee9bd0ad5498acd242c3e7d51ea0ca409083a41ae838ba` | `SCRIPT_DERIVED` |

> [!IMPORTANT]
> **Lineage & Verification Distinction**:
> The above scripts are installed locally on the host environment and are **not** versioned in `reallakshman19/Common` (which tracks older v3.28 fixtures in `coordination/tests/fixtures/v328_source/`). Therefore, live script verification remains strictly labeled **LOCAL_NOT_VERIFIED** in repository test runs, while the versioned artifacts under `coordination/tests/fixtures/dash_v2_gate1/` provide immutable, synthetic fixtures for repository validation.

---

## 3. Coordinator State Key Families & Field Taxonomy

The coordinator state file (`coordinator-state.json`) is a JSON object containing key families prefixed with `claude_code_`. The atomic updater (`state-io.ps1`) enforces that all top-level keys match `(?m)^[ \t]*"(claude_code_[^"]+)":` and preserves the synchronization sentinel `"claude_code_log_anchor": 0,`.

### Taxonomy Legend:
- **`OBSERVED`**: Inspected in local host state files.
- **`SCRIPT_DERIVED`**: Directly parsed, validated, or modified in the PowerShell scripts.
- **`SYNTHETIC`**: Value chosen for isolated test fixtures without private data.
- **`UNKNOWN`**: Field whose runtime variants or downstream meanings cannot be fully observed without private live session execution.

---

### 3.1. Session Cycle State: `claude_code_cycle_<Session>`
Managed by `cyclestate.ps1`.
- **Key Pattern**: `^claude_code_cycle_[A-Za-z0-9_]+$`
- **Type**: `object`

| Field | Type | Required / Nullable | Taxonomy | Description & Allowed Values |
| :--- | :--- | :--- | :--- | :--- |
| `status` | `string` | Required | `SCRIPT_DERIVED` | Enum: `"RUNNING"`, `"HOLD"`, `"WAIT"`. |
| `cycle` | `integer` | Required (`>= 1`) | `SCRIPT_DERIVED` | Cadence interval in minutes (e.g. `30`, `60`, `15`). Reject `cycle == 0`. |
| `since` | `string` | Required | `SCRIPT_DERIVED` | Timestamp when current status started (e.g., `"2026-10-13T10:00:00Z"`). |
| `lastFull` | `string` or `null` | Optional / Nullable | `OBSERVED` | Timestamp of last full status/report execution. |
| `mode` | `string` or `null` | Optional / Nullable | `OBSERVED` | Cycle mode (e.g., `"economy"`, `"speed"`, or `null`). |
| `scope` | `string` or `null` | Optional / Nullable | `OBSERVED` | Scope filter string, or `null`. |
| `job` | `string` or `null` | Optional / Nullable | `OBSERVED` | Cron/heartbeat job identifier. |
| `until` | `string` or `null` | Optional / Nullable | `OBSERVED` | Resumption timestamp when `status == "WAIT"`. |
| `map` | `array` of `string` | Required | `SCRIPT_DERIVED` | **Five-component** tab-to-chat mapping strings: `pos\|chat\|folder\|name\|chatSetAt`. |
| `seen` | `array` of `string` | Required | `SCRIPT_DERIVED` | Probed timestamps per tab: `pos\|chat\|timestamp`. |
| `modes` | `array` of `string` | Optional | `SCRIPT_DERIVED` | Per-tab execution modes: `pos\|speed\|coder\|handover`. |

#### Five-Component `map` Syntax (`cyclestate.ps1` Line 82):
`$line = '{0}|{1}|{2}|{3}|{4}' -f $Pos, $Chat, $Folder, $Name, $chatSetAt`
- **Component 1 (`pos`)**: Tab position number (`1`, `2`, ...).
- **Component 2 (`chat`)**: 8-hex chat ID (`a1b2c3d4`).
- **Component 3 (`folder`)**: Relative coordination folder path (e.g. `Session/Tab1_Work`).
- **Component 4 (`name`)**: Work name / label, optionally prefixed with `[HOLD]` (halts messages) or `[OUT]` (excludes from scope).
- **Component 5 (`chatSetAt`)**: Timestamp when chat binding was assigned.

---

### 3.2. GitHub Monitoring Config: `claude_code_gh_cfg_<Session>`
Managed by `ghwatch.ps1 config`.
- **Key Pattern**: `^claude_code_gh_cfg_[A-Za-z0-9_]+$`
- **Type**: `string` (JSON-encoded string)
- **Syntax**: `"<pos>=<source_spec>[,<source_spec>...];..."`
  - `<source_spec>`: `i:<owner/repo>#<issue_number>` (polls issue comments) or `r:<owner/repo>` (polls repo events).
  - Example: `"1=i:reallakshman19/Common#360,r:reallakshman19/Common;2=i:reallakshman19/Common#353"`

---

### 3.3. GitHub Watermark: `claude_code_gh_seen_<Session>`
Managed by `ghwatch.ps1 news`.
- **Key Pattern**: `^claude_code_gh_seen_[A-Za-z0-9_]+$`
- **Type**: `string` (JSON-encoded ISO 8601 UTC string)
- **Semantics**: High-water mark timestamp (e.g. `"\"2026-10-13T12:00:00Z\""`). Only events newer than this timestamp are processed.
- **Error Semantics**: On polling error (rate limits, 403, 404, network timeout), `ghwatch.ps1` records `GH_ERR` and **retains the old watermark** without advancing it.

---

### 3.4. Background Waiter State: `claude_code_gh_waiter_<Session>`
Managed by `ghwatch.ps1 wait` / `stop`.
- **Key Pattern**: `^claude_code_gh_waiter_[A-Za-z0-9_]+$`
- **Type**: `object` or `null`

| Field | Type | Required / Nullable | Taxonomy | Description |
| :--- | :--- | :--- | :--- | :--- |
| `pid` | `integer` | Required when active | `SCRIPT_DERIVED` | Process ID of the active watcher process. |
| `start` | `string` | Required when active | `SCRIPT_DERIVED` | Process start time (`yyyy-MM-ddTHH:mm:ss`). |
| `since` | `string` | Required when active | `SCRIPT_DERIVED` | Time string (`HH:mm`) when wait began. |

When stopped or inactive, value is `null`.

---

### 3.5. Inter-Agent Relay Tracker: `claude_code_gh_relay_<Session>`
Managed by `ghwatch.ps1 news` / `Note-Relay`.
- **Key Pattern**: `^claude_code_gh_relay_[A-Za-z0-9_]+$`
- **Type**: `object` (mapping work name to relay record object)

| Field | Type | Required / Nullable | Taxonomy | Description |
| :--- | :--- | :--- | :--- | :--- |
| `forLa` | `string` | Required | `SCRIPT_DERIVED` | ISO 8601 UTC timestamp of latest detected `FOR LA` comment (or `""`). |
| `laDone` | `string` | Required | `SCRIPT_DERIVED` | ISO 8601 UTC timestamp of latest detected `LA DONE` comment (or `""`). |

- **Cadence Effect**: If `forLa > laDone`, work has `"LA paste pending"`: considered unsettled, preventing entry into the 60-minute budget guard.

---

### 3.6. Sticky Aim Labels: `claude_code_aim_<work>`
Defined by `aim-lib.ps1` (Architecture v2).
- **Key Pattern**: `^claude_code_aim_[A-Za-z0-9_-]+$`
- **Type**: `object`

| Field | Type | Required / Nullable | Taxonomy | Description |
| :--- | :--- | :--- | :--- | :--- |
| `work` | `string` | Required | `SCRIPT_DERIVED` | Canonical work identifier. |
| `repo` | `string` | Required | `SCRIPT_DERIVED` | Repository identifier (e.g. `reallakshman19/Common`). |
| `crit` | `string` | Required | `SCRIPT_DERIVED` | Criticality rating: `"critical"`, `"standard"`, `"unknown"`. |
| `status` | `string` | Required | `SCRIPT_DERIVED` | Lifecycle state: `"ACTIVE"`, `"DRAFT"`, `"RETIRED"`. |
| `vMain` | `integer` | Required | `SCRIPT_DERIVED` | Major version number. |
| `vTask` | `integer` | Required | `SCRIPT_DERIVED` | Task version number. |
| `vGuide` | `integer` | Required | `SCRIPT_DERIVED` | Guidance version number. |
| `sha` | `string` | Optional | `SCRIPT_DERIVED` | SHA-256 of the authoritative `relay/AIM/<WORK>.yaml`. |
| `label` | `object` | Optional | `SCRIPT_DERIVED` | Structured definitions (`taskOutcome`, `problem`, `mainAim`, `doneWhen`). |
| `bind` | `array` of `string` | Optional | `SCRIPT_DERIVED` | Session bindings: `"<Session>:<pos>\|<folder>"`. |
| `judge` | `object` or `null` | Optional / Nullable | `SCRIPT_DERIVED` | Judgement: `{"color": "green", "sum": "...", "why": "..."}`. |
| `adopt` | `object` or `null` | Optional / Nullable | `SCRIPT_DERIVED` | Adoption card pointer (`card_id`), or `null`. |
| `groundDue` | `string` or `null` | Optional / Nullable | `SCRIPT_DERIVED` | Enum: `"new"`, `"ground"`, or `""`. |

---

### 3.7. Change Proposal Cards: `claude_code_cp_<work>_<nn>`
- **Key Pattern**: `^claude_code_cp_[A-Za-z0-9_-]+_\d{2}$`
- **Type**: `object`
- **Fields**: `id` (`string`), `work` (`string`), `cls` (`string`), `state` (`"PROPOSED"`, `"ACCEPTED"`, `"REJECTED"`), `change` (`string`), `why` (`string`), `raised` (`string`).

---

### 3.8. Judgement History: `claude_code_judge_<work>_<stamp>`
- **Key Pattern**: `^claude_code_judge_[A-Za-z0-9_-]+_\d{14}$`
- **Type**: `object`
- **Fields**: `work` (`string`), `at` (`string`), `color` (`"green"`, `"amber"`, `"red"`, `"yellow"`, `"none"`), `sum` (`string`), `why` (`string`, optional).

---

### 3.9. Tab Heartbeat & Agent State: `claude_code_hw_<chat8>`
Monitored by `watch.ps1`.
- **Key Pattern**: `^claude_code_hw_[0-9a-f]{8}$`
- **Type**: `object`

| Field | Type | Required / Nullable | Taxonomy | Description & Allowed Values |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `string` | Required | `SCRIPT_DERIVED` | 8-hex character conversation ID (`^[0-9a-f]{8}$`). |
| `lastState` | `string` | Required | `SCRIPT_DERIVED` | Indicator: `"working"`, `"idle"`, `"ERROR"`, `"LOADFAIL"`, `"NOBOX"`, `"UNUSUAL"`. |
| `turns` | `integer` | Required | `SCRIPT_DERIVED` | Turn counter in current conversation. |
| `costK` | `number` | Optional | `SCRIPT_DERIVED` | Approximate token/cost consumption metric. |
| `actAt` | `string` or `null` | Optional / Nullable | `OBSERVED` | Last agent activity timestamp. |
| `lastSeen` | `string` or `null` | Optional / Nullable | `OBSERVED` | Timestamp when coordinator last inspected tab. |
| `fLine` | `string` or `null` | Optional / Nullable | `SCRIPT_DERIVED` | **String representation** of last footer line (`[string]$ftO.line` or `""`). |
| `fPlan` | `string` or `null` | Optional / Nullable | `OBSERVED` | Agent task claim string from footer. |
| `fAc` | `string` or `null` | Optional / Nullable | `OBSERVED` | Acceptance criteria claim from footer. |
| `fCi` | `string` or `null` | Optional / Nullable | `OBSERVED` | CI status string from footer. |
| `fAim` | `string` or `null` | Optional / Nullable | `OBSERVED` | Footer aim string reported by agent. |
| `fHv` | `string` or `null` | Optional / Nullable | `SCRIPT_DERIVED` | Footer handover flag: `"due"`, `"ready"`, or `null`. |
| `fBk` | `string` or `null` | Optional / Nullable | `SCRIPT_DERIVED` | Footer blocker: `"OWNER"`, or `null`. |
| `aLane` | `string` or `null` | Optional / Nullable | `SCRIPT_DERIVED` | Outgoing lane state: `"asked"`, `"moved"`, `"review"`, `"s2ready"`, `"retired"`. |
| `buddy` | `string` or `null` | Optional / Nullable | `SCRIPT_DERIVED` | Successor lane state: `"due"`, `"s1"`, `"s1ok"`, `"areview"`, `"s2"`, `"done"`, `"blocked"`. |
| `bV` | `string` or `null` | Optional / Nullable | `SCRIPT_DERIVED` | Buddy version: `"16"` for v1.6, or legacy. |
| `parkAt` | `string` or `null` | Optional / Nullable | `OBSERVED` | Timestamp when tab was parked, or `null`. |
| `parkWhy` | `string` or `null` | Optional / Nullable | `OBSERVED` | Park reason string, or `null`. |

---

## 4. Source-to-10-Cell Lineage & Literal Parity Expectations

In `watch.ps1` (`rows` and `rowsjson`), the coordinator formats:
`| Tab | Status | Aim | Plan | AC | CI | Meter | Due | Checked | Next |`

| Cell Column | Field Name | State Origin | Exact Derivation Logic in `watch.ps1` |
| :---: | :--- | :--- | :--- |
| 1 | **Tab** | `cycle.map` component 1 | Formatted as `Tab <pos>`. |
| 2 | **Status** | `hw.lastState`, `hw.actAt`, `hw.buddy`, `hw.aLane`, `hw.parkAt` | Dot icon (`🟢`, `🟡`, `🔴`, `⚪`, `🔵`) + status string. If `idle >= 60 min`, `🔵 stable <min> min · <status>`. If `parkAt`, `⚪ parked: <why>`. Handover and Buddy states override default working state. |
| 3 | **Aim** | `aim` record + `cp` cards | Formatted as `[🛡️] <Aim-Ver> · <AimDot> <sum> [· <why>] [· card <id>]`. If draft: `label draft · card <id>`. |
| 4 | **Plan** | `hw.fPlan`, `hw.bPub1`, `hw.yLast` | Agent task claim string and Buddy progress tokens (`Buddy 1b ✓`, `Y ✓ <step>`). |
| 5 | **AC** | `hw.fAc` | Acceptance criteria summary reported in agent footer. |
| 6 | **CI** | `hw.fCi` | CI status string reported in agent footer. |
| 7 | **Meter** | `hw.turns`, `hw.costK` | Handover budget meter formatted as `<turns> turns / <costK>k`. |
| 8 | **Due** | `hw.buddy`, `hw.aLane`, `aim.judge` | Due checkpoint, next handover phase, or retry timer. |
| 9 | **Checked** | `cycle.seen` timestamp | Probed timestamp, or `**never**` if unprobed. |
| 10 | **Next** | `watch.ps1` decision tree | Prescriptive coordinator action: nudge text, handover pointer, or `normal route`. |

### Literal Expected Rows for `coordinator_state_v330_positive.json`:

```json
[
  {
    "tab": "Tab 1",
    "status": "🟢 working",
    "aim": "[🛡️] v1.0.0 · 🟢 On track with source verification · All field types match installed PowerShell implementation · card 01",
    "plan": "Verify fixtures against schema",
    "ac": "100% schema match",
    "ci": "local tests PASS",
    "meter": "8 turns / 4.5k",
    "due": "-",
    "checked": "2026-10-13T12:05:00Z",
    "next": "normal route"
  },
  {
    "tab": "Tab 2",
    "status": "🟡 Buddy: 1a ready (G1 holds)",
    "aim": "-",
    "plan": "Handover to successor session",
    "ac": "Evidence published",
    "ci": "PASS",
    "meter": "14 turns / 7.2k",
    "due": "-",
    "checked": "2026-10-13T12:05:00Z",
    "next": "new chat: 1b pointer"
  },
  {
    "tab": "Tab 3",
    "status": "⚪ not in my scope",
    "aim": "-",
    "plan": "-",
    "ac": "-",
    "ci": "-",
    "meter": "0 turns / 0.0k",
    "due": "-",
    "checked": "**never**",
    "next": "nothing"
  }
]
```

---

## 5. Handover State Lineage: v3.29/v3.30 vs Legacy

1. **v3.29/v3.30 Handover**:
   - Triggered when agent footer reports `handover=ready` (`hw.fHv == "ready"`).
   - Generates action `BRIEF_READY` ("brief ready for new chat; outgoing agent holds until successor starts").
   - Followed by `HSTART` ("send start workpack to successor").
   - Outgoing lane transitions: `asked` → `moved` → `review` → `s2ready` → `retired`.
2. **Legacy v1.5 / v1.6 Buddy Protocol**:
   - Governed by `hw.bV == "16"` and `hw.buddy`.
   - States: `due` (1b next) → `s1` (1b: G2 investigates) → `s1ok` (G1 writes 2 next) → `areview` (G1 writes 2) → `done`.
   - Legacy buddy protocols must not be conflated with modern v3.29 `BRIEF_READY`.

---

## 6. Smart Economy Cadence (v3.30) vs Handover Meter

1. **Smart Economy Cadence** (`ghwatch.ps1 Cadence`):
   - **Standard Economy Mode (30 min)**: Applied whenever any work is **UNSETTLED**:
     - *Boarding*: chat has no record, no footer seen yet, or `turns < 2`.
     - *Handover active*: `aLane` open (`!= "retired"`), or `buddy` in `('due', 's1', 's1ok', 'areview', 's2')`, or `fHv` in `('due', 'ready')`.
     - *Waiting on Owner*: `parkAt != null`, or `fBk` matches `'^OWNER'`, or relay has `forLa > laDone` (`LA paste pending`).
   - **Budget Guard Mode (60 min / 120 min)**: Applied only when **all works are settled** (no onboarding, no handover, no owner wait, and no pending LA pastes).
2. **Handover Budget Meter**:
   - The meter `60 min / 30 pages / 10 turns` is a **handover consumption ceiling** designed to prevent runaways during chat transitions.
   - It is **never** a recurring polling heartbeat cycle.

---

## 7. Freshness, Error, Partial, and Outage Behavior

1. **Quiet GitHub vs Offline**:
   - A quiet GitHub repository produces `GH_QUIET since <watermark>`. It is **not** an error and does not change health status.
2. **Polling Failures (`GH_ERR`)**:
   - On 403, 404, rate limits, or network timeout, `ghwatch.ps1` records `GH_ERR (watermark kept)`.
   - The high-water mark `claude_code_gh_seen_<Session>` is strictly preserved.
   - The adapter marks status as `UNKNOWN` or `DEGRADED`, retaining last confirmed data with an explicit `stale` flag.
3. **Coordinator Liveness Threshold**:
   - In `cyclestate.ps1` and `watch.ps1`, an unprobed chat whose age exceeds `2 * cycle` is flagged `STALE` (`NOT_CHECKED ... more than 2 cycles`).
   - Less than `2 * cycle` is `ALIVE`.

---

## 8. Expected Artifact Manifest & Verification

The versioned artifact manifest [`expected_digests.json`](./expected_digests.json) pins the exact SHA-256 digests of all evidence files. The runner [`validate_fixtures.py`](./validate_fixtures.py) enforces:
- Strict schema validation matching Draft 2020-12 constraints.
- Rejection of the four negative mutation profiles (`cycle0`, `numeric_map_entry`, `malformed_hw_id`, `numeric_relay_entry`).
- Literal equality against expected 10-cell fixture rows.
- Comparison against the pinned manifest digests and tamper-detection assertion.
