# Gate 1 Installed-Source Contract & Lineage Specification

## 1. Document Identity & Purpose

This document provides the authoritative, source-grounded contract for the Coordinator Protocol v3.30 state schema, 10-column table derivation, Smart Economy cadence rules, and error semantics. It satisfies Gate 1 requirements for Dash v2 on branch `feature/dash-v2-d2-1-d2-5-foundations` in `reallakshman19/Common`.

All specifications herein are directly derived from the installed PowerShell scripts and skill instructions on the LA environment. Public fixtures and examples are strictly synthetic/sanitized to guarantee zero privacy or credential leakage.

---

## 2. Source Provenance & Cryptographic Hashes

The contract is grounded in the five installed coordinator protocol files located locally at `C:\Users\reall\.claude\skills\coordinator-protocol\`:

| Relative Path | Component / Role | Version / Header | SHA-256 Digest |
| :--- | :--- | :--- | :--- |
| `SKILL.md` | Coordinator Policy Core | v3.30 | `e388241adbad15dd744446c4e5b56c5720d850ed29caa09fdafed3bafee31348` |
| `scripts/watch.ps1` | Observation, 10 Cells, Aim | v3.28+ (Aim v2) | `a18d1eb206a2b1444ef55b4da32d55f6b1aea9aa328c85ce8e528ee4713a1b6e` |
| `scripts/ghwatch.ps1` | GitHub Polling, Watermark, Waiter, Relay, Cadence | v3.30 (Smart Economy) | `246c8cc8b8b8af3ab1dd67a3a479966272dfb494f8c9645bf91c4fd91d06cf22` |
| `scripts/cyclestate.ps1` | Session Lifecycle, Tab Mapping, Liveness | v3.26+ | `46f44c71cc1d13875510f237b6ed5f8f44eabc32b885aba557adf221aa172bd9` |
| `scripts/state-io.ps1` | Atomic Mutex-Locked State I/O | v3.27+ | `9f4a2164c5a31c636ebf1bfe991e84f9e4fe2adeed91820682c16c94252d8646` |
| `scripts/aim-lib.ps1` | Shared Sticky Label & Card Library | v3.28 | `9623f038ba658cd254ee9bd0ad5498acd242c3e7d51ea0ca409083a41ae838ba` |

> [!IMPORTANT]
> **Lineage & Verification Distinction**: The above scripts are installed locally on the host environment and are **not** committed to `reallakshman19/Common` (which tracks older v3.28 fixtures in `coordination/tests/fixtures/v328_source/`). Therefore, live script verification remains strictly labeled **LOCAL**, while the versioned artifacts under `coordination/tests/fixtures/dash_v2_gate1/` provide immutable, synthetic fixtures for repository CI.

---

## 3. Coordinator State Key Families & Type Definitions

The coordinator state file (`coordinator-state.json`) is a JSON object containing key families prefixed with `claude_code_`. The atomic updater (`state-io.ps1`) enforces that all top-level keys match `(?m)^[ \t]*"(claude_code_[^"]+)":` and preserves the synchronization sentinel `"claude_code_log_anchor": 0,`.

### 3.1. Session Cycle State: `claude_code_cycle_<Session>`
Managed by `cyclestate.ps1`.
- **Key Pattern**: `^claude_code_cycle_[A-Za-z0-9_]+$`
- **Type**: `object`
- **Fields**:
  - `status` (`string`, required): Current coordinator cycle state. Enum: `"RUNNING"`, `"HOLD"`, `"WAIT"`.
  - `cycle` (`integer`, required): Polling cadence in minutes (typically `30`, `60`, or `15`).
  - `since` (`string`, required): Local time or ISO string indicating when the current status started (e.g., `"14:05"` or `"2026-10-13T10:00:00Z"`).
  - `lastFull` (`string` or `null`): Timestamp of last full status/report execution.
  - `mode` (`string` or `null`): Cycle mode (e.g., `"economy"`, `"speed"`, or `null`).
  - `scope` (`string` or `null`): Scope filter string (e.g., `"Dash v2"` or `null`).
  - `job` (`string` or `null`): Cron/heartbeat job identifier.
  - `until` (`string` or `null`): Resumption timestamp when `status == "WAIT"`.
  - `map` (`array` of `string`, required): Tab-to-chat mapping entries.
    - Format: `"<pos>|<chat_id>|<folder>|<label>"`
    - Examples: `"1|6accd172|IMO-CORE-BLUEPRINTS|IMO-CORE-BLUEPRINTS"`, `"2|6accecfd|Common|[HOLD] Dash v2"`, `"3|6acd1de0|Grade9|[OUT] Other"`
    - Flag semantics: `[HOLD]` halts coordinator messaging; `[OUT]` excludes the tab from coordinator scope entirely.
  - `seen` (`array` of `string`, required): Recent probe timestamps per tab.
    - Format: `"<pos>|<chat_id>|<timestamp>"`
  - `modes` (`array` of `string`, required): Per-tab execution modes.
    - Format: `"<pos>|<speed>|<coder>|<handover>"`

### 3.2. GitHub Monitoring Config: `claude_code_gh_cfg_<Session>`
Managed by `ghwatch.ps1 config`.
- **Key Pattern**: `^claude_code_gh_cfg_[A-Za-z0-9_]+$`
- **Type**: `string` (JSON-encoded string)
- **Syntax**: `"<pos>=<source_spec>[,<source_spec>...];..."`
  - `<source_spec>`: `i:<owner/repo>#<issue_number>` (polls issue comments) or `r:<owner/repo>` (polls repo events).
  - Example: `"1=i:reallakshman19/Common#360,r:reallakshman19/Common;2=i:reallakshman19/Common#353"`

### 3.3. GitHub Watermark: `claude_code_gh_seen_<Session>`
Managed by `ghwatch.ps1 news`.
- **Key Pattern**: `^claude_code_gh_seen_[A-Za-z0-9_]+$`
- **Type**: `string` (JSON-encoded ISO 8601 UTC string)
- **Semantics**: High-water mark timestamp (e.g. `"\"2026-10-13T10:32:00Z\""`). Only events newer than this timestamp are processed.
- **Error Semantics**: If GitHub polling encounters errors (rate-limit, HTTP 403/500, network failure), `ghwatch.ps1` records `GH_ERR` and **retains the old watermark** without advancing it.

### 3.4. Background Waiter State: `claude_code_gh_waiter_<Session>`
Managed by `ghwatch.ps1 wait` / `stop`.
- **Key Pattern**: `^claude_code_gh_waiter_[A-Za-z0-9_]+$`
- **Type**: `object` or `null`
- **Fields (when active)**:
  - `pid` (`integer`): Process ID of the active background watcher process.
  - `start` (`string`): Process start time in ISO format (`yyyy-MM-ddTHH:mm:ss`).
  - `since` (`string`): Time string (`HH:mm`) when wait began.
- **When inactive**: Set to `null` or absent.

### 3.5. Inter-Agent Relay Tracker: `claude_code_gh_relay_<Session>`
Managed by `ghwatch.ps1 news` / `Note-Relay`.
- **Key Pattern**: `^claude_code_gh_relay_[A-Za-z0-9_]+$`
- **Type**: `object` (mapping work name to relay timestamps)
- **Fields per work item**:
  - `forLa` (`string`): ISO 8601 UTC timestamp of latest detected `FOR LA` comment (or `""`).
  - `laDone` (`string`): ISO 8601 UTC timestamp of latest detected `LA DONE` comment (or `""`).
- **Cadence Effect**: If `forLa > laDone`, work has `"LA paste pending"`: considered unsettled, which prevents entering the 60-minute budget guard.

### 3.6. Sticky Aim Labels: `claude_code_aim_<work>`
Defined by `aim-lib.ps1` (Architecture v2).
- **Key Pattern**: `^claude_code_aim_[A-Za-z0-9_-]+$`
- **Type**: `object`
- **Fields**:
  - `work` (`string`, required): Canonical work identifier (e.g., `"Dash v2"`).
  - `repo` (`string`, required): Repository identifier (e.g., `"reallakshman19/Common"`).
  - `crit` (`string`, required): Criticality rating. Enum: `"critical"`, `"standard"`, `"unknown"`.
  - `status` (`string`, required): Lifecycle state. Enum: `"ACTIVE"`, `"DRAFT"`, `"RETIRED"`.
  - `vMain` (`integer`), `vTask` (`integer`), `vGuide` (`integer`): Semantic version tuple formatting `v{vMain}.{vTask}.{vGuide}`.
  - `sha` (`string`): SHA-256 of the authoritative `relay/AIM/<WORK>.yaml` in `Common`.
  - `label` (`object`): Structured aim definitions (`taskOutcome`, `problem`, `mainAim`, `doneWhen`, etc.).
  - `bind` (`array` of `string`): Bindings to sessions and positions, formatted `"<Session>:<pos>|<folder>"`.
  - `judge` (`object` or `null`): Latest human/coordinator judgement record:
    - `color` (`string`): Enum `"green"`, `"amber"`, `"red"`, `"yellow"`, `"none"`.
    - `sum` (`string`): Brief summary (truncated to 60 chars in 10-cell display).
    - `why` (`string`): Rationale (truncated to 50 chars in 10-cell display).
  - `adopt` (`object` or `null`): Adoption card pointer (`card_id`), or `null`.
  - `groundDue` (`string` or `null`): Enum `"new"`, `"ground"`, or `""`.

### 3.7. Change Proposal Cards: `claude_code_cp_<work>_<nn>`
- **Key Pattern**: `^claude_code_cp_[A-Za-z0-9_-]+_\d{2}$`
- **Type**: `object`
- **Fields**: `id`, `work`, `cls`, `state` (`"PROPOSED"`, `"ACCEPTED"`, `"REJECTED"`), `change`, `why`, `stops`, `unblocks`, `neededBy`, `raised`.

### 3.8. Judgement History: `claude_code_judge_<work>_<stamp>`
- **Key Pattern**: `^claude_code_judge_[A-Za-z0-9_-]+_\d{14}$`
- **Type**: `object`
- **Fields**: `work`, `at`, `hold`, `ver`, `crit`, `color`, `sum`, `blocks`, `doubt`, `unauth`.

### 3.9. Tab Heartbeat & Agent State: `claude_code_hw_<chat8>`
Monitored by `watch.ps1`.
- **Key Pattern**: `^claude_code_hw_[0-9a-f]{8}$`
- **Type**: `object`
- **Fields**:
  - `id` (`string`, required): 8-hex character conversation ID.
  - `actAt` (`string` or `null`): Last agent activity timestamp.
  - `lastState` (`string`): State indicator (`"working"`, `"idle"`, `"ERROR"`, `"LOADFAIL"`, `"NOBOX"`, `"UNUSUAL"`).
  - `lastSeen` (`string` or `null`): Timestamp when coordinator last inspected the tab.
  - `turns` (`integer`): Turn counter in the current conversation.
  - `nudgeTurn` (`integer`): Turn number when coordinator last nudged.
  - `costK` (`number`): Approximate token/cost consumption metric.
  - `fLine` (`integer` or `null`): Last footer line number observed.
  - `fAim` (`string` or `null`): Footer aim string reported by the agent.
  - `fHv` (`string` or `null`): Footer handover flag (`"due"`, `"ready"`, or `null`).
  - `fBk` (`string` or `null`): Footer blocker (`"OWNER"`, etc., or `null`).
  - `aLane` (`string` or `null`): Outgoing lane state (`"asked"`, `"moved"`, `"review"`, `"s2ready"`, `"retired"`).
  - `buddy` (`string` or `null`): Successor lane state (`"due"`, `"s1"`, `"s1ok"`, `"areview"`, `"s2"`, `"done"`, `"blocked"`).
  - `bV` (`string` or `null`): Buddy version indicator (`"16"` for v1.6, or legacy).
  - `parkAt` (`string` or `null`): Timestamp when tab was parked, or `null`.
  - `parkWhy` (`string` or `null`): Park reason string, or `null`.

---

## 4. Source-to-10-Cell Lineage & Derivation

In `watch.ps1` (`rows` and `rowsjson`), the coordinator renders a strictly structured 10-column table:
`| Tab | Status | Aim | Plan | AC | CI | Meter | Due | Checked | Next |`

| Column | Cell Header | Source Origin | Derivation Logic |
| :---: | :--- | :--- | :--- |
| 1 | **Tab** | `cycle.map` entry | Formatted as `Tab <pos>`. |
| 2 | **Status** | `hw.lastState`, `hw.actAt`, `hw.buddy`, `hw.aLane`, `hw.parkAt` | Formatted with status dot (`🟢`, `🟡`, `🔴`, `⚪`, `🔵`) + status string. If `idle >= 60 min`, displays `🔵 stable <min> min · <status>`. If `parkAt`, displays `⚪ parked: <why>`. Handover and Buddy states override default working state. |
| 3 | **Aim** | `aim-lib.ps1` (`aim` record + `cp` cards) | Formatted as `[🛡️] <Aim-Ver> · <AimDot> <sum> [· <why>] [· card <id>]`. If draft: `label draft · card <id>`. |
| 4 | **Plan** | `hw.fPlan`, `hw.bPub1`, `hw.yLast` | Displays agent's task claims and Buddy progress tokens (`Buddy 1b ✓`, `Y ✓ <step>`). |
| 5 | **AC** | `hw.fAc` | Acceptance criteria summary reported in agent footer. |
| 6 | **CI** | `hw.fCi` | CI status string reported in agent footer. |
| 7 | **Meter** | `hw.turns`, `hw.costK`, `hw.actAt` | Handover budget meter formatted as `<elapsed> min / <turns> turns / <costK>k`. |
| 8 | **Due** | `hw.buddy`, `hw.aLane`, `aim.judge` | Due checkpoint, next handover phase, or retry timer. |
| 9 | **Checked** | `cycle.seen` timestamp | Elapsed check time, or `**never**` if unprobed. |
| 10 | **Next** | `watch.ps1` decision tree | Prescriptive coordinator action: nudge text, handover pointer, or `normal route`. |

---

## 5. Handover State Lineage: v3.29/v3.30 vs Legacy

A critical distinction exists between modern coordinator handover mechanics and legacy buddy protocols:

1. **v3.29/v3.30 Handover**:
   - Triggered when agent footer reports `handover=ready` (`hw.fHv == "ready"`).
   - Generates action `BRIEF_READY` ("brief ready for new chat; outgoing agent holds until successor starts").
   - Followed by `HSTART` ("send start workpack to successor").
   - Outgoing lane transitions: `asked` → `moved` → `review` → `s2ready` → `retired`.
2. **Legacy v1.5 / v1.6 Buddy Protocol**:
   - Governed by `hw.bV == "16"` and `hw.buddy`.
   - States: `due` (1b next) → `s1` (1b: G2 investigates) → `s1ok` (G1 writes 2 next) → `areview` (G1 writes 2) → `done`.
   - LFEA / older fixtures preserve these states; they must not be conflated with modern v3.29 `BRIEF_READY`.

---

## 6. Smart Economy Cadence (v3.30) vs Handover Meter

1. **Smart Economy Cadence** (`ghwatch.ps1 Cadence`):
   - **Standard Economy Mode (30 min)**: Applied whenever any work is **UNSETTLED**:
     - *Boarding*: chat has no record, no footer seen yet, or `turns < 2`.
     - *Handover active*: `aLane` open (`!= "retired"`), or `buddy` in `('due', 's1', 's1ok', 'areview', 's2')`, or `fHv` in `('due', 'ready')`.
     - *Waiting on Owner*: `parkAt != null`, or `fBk` matches `'^OWNER'`, or relay has `forLa > laDone` (`LA paste pending`).
   - **Budget Guard Mode (60 min / 120 min)**: Applied only when **all works are settled** (no onboarding, no handover, no owner wait, and no pending LA pastes).
2. **Handover Budget Meter**:
   - The meter `60 min / 30 pages / 10 turns` is a **handover consumption ceiling** designed to prevent runaways during chat-to-chat transitions.
   - It is **never** a polling heartbeat cycle and must not be used as the scheduler interval.

---

## 7. Freshness, Error, Partial, and Outage Behavior

1. **Quiet GitHub vs Offline**:
   - A quiet GitHub repository produces `GH_QUIET since <watermark>`. It is **not** an error and does not change health status.
2. **Polling Failures (`GH_ERR`)**:
   - On 403, 404, rate limits, or network timeout, `ghwatch.ps1` records `GH_ERR (watermark kept)`.
   - The high-water mark `claude_code_gh_seen_<Session>` is strictly preserved.
   - The adapter must mark status as `UNKNOWN` or `DEGRADED`, retaining the last confirmed data with an explicit `stale` flag.
3. **Coordinator Liveness Threshold**:
   - In `cyclestate.ps1` and `watch.ps1`, an unprobed chat whose age exceeds `2 * cycle` is flagged `STALE` (`NOT_CHECKED ... more than 2 cycles`).
   - Less than `2 * cycle` is `ALIVE`.

---

## 8. Fixture Artifact Directory

The accompanying synthetic test fixtures provide immutable, sanitized representations of these states:
- [`coordinator_state_v330_positive.json`](./coordinator_state_v330_positive.json): Valid running sessions, settled & unsettled works, relay, waiter, and AIM records.
- [`coordinator_state_v330_negative.json`](./coordinator_state_v330_negative.json): Adversarial states, stale checks, waiter failure, partial relay, error states, and rate-limit degradation.
- [`source_contract.schema.json`](./source_contract.schema.json): Strict JSON schema for validating coordinator-state structures.
- [`validate_fixtures.py`](./validate_fixtures.py): Focused validation runner verifying digests, schema compliance, 10-cell derivation, and cadence logic.
