# Gate 1 Installed-Source Contract & Lineage Specification (R4)

## 1. Document Identity & Purpose

This document provides the authoritative, source-grounded contract for the Coordinator Protocol v3.30 state schema, 10-column table derivation, Smart Economy cadence rules, manifest coverage, and error semantics. It repairs Gate 1 evidence defects on branch `feature/dash-v2-gate1-r4-evidence` in `reallakshman19/Common`, addressing controller directive comment `6150903209` (Request ID: `21567fdd-cbf9-47c4-b500-8e2891f22b9c`, Request digest: `f3837b42a2f8a5eac161d427b7830bbd307aa112d962d2fadb40469af501653f`).

All specifications herein are directly derived from the coordinator protocol PowerShell scripts and skill instructions. All fixture data and examples are strictly **SYNTHETIC** to guarantee zero private environment or credential disclosure. All source locations are referenced by **sanitized relative paths** rather than host-specific absolute paths.

---

## 2. Source Provenance & Cryptographic Hashes

The contract is grounded in the coordinator protocol files installed on the execution host:

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
> The above scripts are installed locally on the host environment and are **not** versioned in `reallakshman19/Common` (which tracks older v3.28 fixtures in `coordination/tests/fixtures/v328_source/`).
> Because `watch.ps1` evaluates time-dependent fields (meter, idle, checked, due) against live unmocked host clock `(Get-Date)` via `TotalMinutes`, and expects single-line compressed JSON formatting, running live source parity without frozen clock isolation cannot yield deterministic row matches. Per governance rules, mutating installed host scripts is strictly forbidden.
> Therefore, source parity is truthfully reported as **`LIVE_INSTALLED_SOURCE_PARITY: NOT_RUN`**, while source identity is independently recorded through local cryptographic hashing (**`LOCAL_INSTALLED_SOURCES_READ_AND_HASHED`**).

---

## 3. Coordinator State Key Families & Complete 106-Field HW Specification

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
| `cycle` | `integer` | Required (`>= 1`) | `SCRIPT_DERIVED` | Cadence interval in minutes (e.g. `30`, `60`, `15`). Under Draft 2020-12, integral floats (e.g. `1.0`) are valid integers, while non-integral floats (`1.5`) and booleans (`True`) are rejected. |
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
- **Component 5 (`chatSetAt`)**: Timestamp when chat binding was assigned (confirmed `chatSetAt`, not pane).

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
| `laDone` | `string` | Optional | `SCRIPT_DERIVED` | ISO 8601 UTC timestamp of latest detected `LA DONE` comment (or `""`). |

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
| `crit` | `string` | Required | `SCRIPT_DERIVED` | Enum: `"critical"`, `"standard"`, `"unknown"`, `""`. |
| `status` | `string` | Required | `SCRIPT_DERIVED` | Lifecycle state: `"ACTIVE"`, `"DRAFT"`, `"RETIRED"`, `"STUB"`. |
| `vMain` | `integer` | Required | `SCRIPT_DERIVED` | Major version number. |
| `vTask` | `integer` | Required | `SCRIPT_DERIVED` | Task version number. |
| `vGuide` | `integer` | Required | `SCRIPT_DERIVED` | Guidance version number. |
| `sha` | `string` | Optional | `SCRIPT_DERIVED` | SHA-256 of the authoritative `relay/AIM/<WORK>.yaml`. |
| `label` | `object` | Optional | `SCRIPT_DERIVED` | Structured definitions: `problem`, `main`, `mainAim`, `outcomes` (object), `constraints` (array), `taskOutcome`, `task`, `done`, `doneWhen`. |
| `watch` | `array` of `string` | Optional | `SCRIPT_DERIVED` | Watch items. |
| `notNow` | `array` of `string` | Optional | `SCRIPT_DERIVED` | Parked guidance items. |
| `notes` | `array` of `string` | Optional | `SCRIPT_DERIVED` | Work notes. |
| `bind` | `array` of `string` | Optional | `SCRIPT_DERIVED` | Session bindings: `"<Session>:<pos>\|<folder>"`. |
| `hist` | `array` | Optional | `SCRIPT_DERIVED` | History entries. |
| `cpN` | `integer` | Optional | `SCRIPT_DERIVED` | Change card sequence number. |
| `judge` | `object` or `null` | Optional / Nullable | `SCRIPT_DERIVED` | Last judgement: `{"at": "...", "hold": "...", "color": "green", "sum": "...", "why": "..."}`. |
| `adopt` | `object` or `null` | Optional / Nullable | `SCRIPT_DERIVED` | Adoption record: `{"card": "...", "at": "...", "why": "..."}`. |
| `pub` | `object` or `null` | Optional / Nullable | `SCRIPT_DERIVED` | Publication metadata. |
| `groundDue` | `string` or `null` | Optional / Nullable | `SCRIPT_DERIVED` | Enum: `"new"`, `"ground"`, `""`, or `null`. |

---

### 3.7. Change Proposal Cards: `claude_code_cp_<work>_<nn>`
- **Key Pattern**: `^claude_code_cp_[A-Za-z0-9_-]+_\d{2}$`
- **Type**: `object`
- **Fields**: `id` (`string`), `work` (`string`), `cls` (`string`), `state` (`"PROPOSED"`, `"ACCEPTED"`, `"REJECTED"`, `"APPLIED"`, `"CANCELLED"`), `change` (`string`), `why` (`string`), `raised` (`string`), `answers` (optional).

---

### 3.8. Judgement History: `claude_code_judge_<work>_<stamp>`
- **Key Pattern**: `^claude_code_judge_[A-Za-z0-9_-]+_\d{14}$`
- **Type**: `object`
- **Fields**: `work` (`string`), `at` (`string`), `hold` (`string`), `ver` (`string`), `color` / `col` (`string`), `sum` (`string`), `why` (`string`), `blocks` (`array`), `next` (`string`), `adopt` (`string`, `boolean`, or `null`).

---

### 3.9. Tab Heartbeat & Agent State: `claude_code_hw_<chat8>` (All 106 `New-Rec` Fields)
Monitored by `watch.ps1`. All 106 properties instantiated by `New-Rec` in `watch.ps1` are explicitly declared in the schema:
- **Key Pattern**: `^claude_code_hw_[0-9a-f]{8}$`
- **Type**: `object`
- **Required**: `["id", "lastState", "turns"]`
- **`additionalProperties: false`** (strict typing without blanket permissiveness)

#### Complete Property Breakdown:
1. **Identity & Core Indicators**:
   - `id`: `string` (`^[0-9a-f]{8}$`)
   - `lastState`: `string` (`"working"`, `"idle"`, `"ERROR"`, `"LOADFAIL"`, `"NOBOX"`, `"UNUSUAL"`)
   - `turns`: `integer`
   - `costK`: `number`
   - `costDay`: `string` or `null`
   - `actAt`: `string` or `null`
   - `lastSeen`: `string` or `null`
   - `firstAt`: `string` or `null`
   - `gen`: `integer`
   - `rcn`: `integer`
2. **Reconciliation & Progress Metrics**:
   - `reconMode`: `string` or `null`
   - `reconDate`: `string` or `null`
   - `pd`: `integer` (default -1)
   - `pt`: `integer` (default -1)
   - `aca`: `integer` (default -1, source of AC column)
   - `act`: `integer` (default -1, source of AC column)
   - `dPd`: `integer`
   - `dAc`: `integer`
   - `noProg`: `integer`
   - `evN`: `integer`
   - `evLast`: `integer`
   - `evSince`: `integer`
   - `ckAt`: `integer`
   - `sumMin`: `number` (handover minute accumulation)
   - `sumPages`: `number` (handover page accumulation)
3. **Footer Fields**:
   - `fLine`: `string` or `null`
   - `fPlan`: `string` or `null`
   - `fDone`: `string` or `null`
   - `fNext`: `string` or `null`
   - `fRel`: `string` or `null`
   - `fBk`: `string` or `null` (`"OWNER"`, `"PERSON"`, `"CI"`, `"MACHINE"`, or `null`)
   - `fBr`: `string` or `null`
   - `fHv`: `string` or `null` (`"ready"`, or `null`)
   - `fPr`: `string` or `null`
   - `fTests`: `string` or `null` (source of CI column)
   - `fMissing`: `string` or `null`
   - `fHead`: `string` or `null`
   - `fProof`: `string` or `null`
   - `fAim`: `string` or `null`
   - `fOut`: `string` or `null`
   - `fUser`: `string` or `null`
   - `stale`: `string` or `null`
   - `footAsk`: `string` or `null`
4. **Lane & Buddy Fields**:
   - `aLane`: `string` or `null` (`"asked"`, `"moved"`, `"review"`, `"s2ready"`, `"retired"`)
   - `buddy`: `string` or `null` (`"due"`, `"s1"`, `"s1ok"`, `"areview"`, `"s2"`, `"done"`, `"blocked"`)
   - `bV`: `string` or `null` (`"16"`)
   - `bRev`: `string` or `null`
   - `bPrompt`: `string` or `null`
   - `bSent`: `integer`
   - `bTry`: `integer`
   - `bNeed`: `integer`
   - `bPub1`: `string` or `null`
   - `bPub2`: `string` or `null`
   - `bAss`: `string` or `null`
   - `bWhy`: `string` or `null`
   - `bAt`: `string` or `null`
   - `bMed`: `number`
   - `bAfter`: `array`
   - `prevId`: `string` or `null`
   - `nextId`: `string` or `null`
5. **Coordinator Actions & Decisions**:
   - `lastKind`: `string` or `null` (`"SENT"`, `"FOOTER_ASK"`, `"BUDDY_START"`, `"NONE"`, etc.)
   - `sentWhat`: `string` or `null`
   - `parkAt`: `string` or `null`
   - `pingAt`: `string` or `null`
   - `parkWhy`: `string` or `null`
   - `hard`: `string` or `null`
   - `hint`: `string` or `null`
   - `redSent`: `string` or `null`
   - `redN`: `integer`
   - `soonSent`: `string` or `null`
   - `heavySent`: `string` or `null`
   - `driftTurn`: `integer`
   - `nudgeTurn`: `integer`
   - `planDoneAt`: `string` or `null`
   - `lastTp`: `integer`
   - `lastTp2`: `integer`
   - `fresh`: `boolean`
   - `ciSent`: `string` or `null`
   - `fixSent`: `string` or `null`
   - `rcAsk`: `string` or `null`
   - `lastBk`: `string` or `null`
   - `prState`: `string` or `null`
   - `lastTests`: `string` or `null`
   - `url`: `string` or `null`
   - `title`: `string` or `null`
   - `folder`: `string` or `null`
   - `lastLog`: `string` or `null`
   - `fHr`: `string` or `null`
   - `unknown`: `string` or `null`
   - `aPub`: `string` or `null`
   - `yLast`: `string` or `null`
   - `yDec`: `string` or `null`
   - `pStage`: `string` or `null`
   - `evChat`: `integer`
   - `userNoN`: `integer`
   - `aimSends`: `integer`
   - `aimIntro`: `string` or `null`
   - `repo`: `string` or `null`
   - `ciLimSent`: `string` or `null`
   - `seenK`: `array`
   - `doneHist`: `array` of `string`
   - `planSeen`: `array` of `string`
   - `judgeKeys`: `array` of `string`
   - `ciHeads`: `array` of `string`
   - `last3`: `array`
   - `soft`: `array` of `string`

> [!CAUTION]
> **Removal of Fabricated `fAc` and `fCi`**:
> Historical R3 fixtures claimed that `watch.ps1` consumed `fAc` and `fCi` directly from `claude_code_hw_*`. Inspection of `watch.ps1` lines 472 and 473 confirms this was fabricated.
> In installed source `watch.ps1`:
> - **AC column** is computed exclusively from `aca` and `act`:
>   `$ac = $(if ([int]$o.aca -ge 0) { '{0}/{1}' -f $o.aca, $(if ([int]$o.act -ge 0) { $o.act } else { '?' }) } else { '-' })`
> - **CI column** is computed from `fTests`, `fProof`, `fPr`/`fHead`, `ciHeads`, and `redN`:
>   `if ($o.fTests) { $ci += $o.fTests } elseif ($o.fProof) { $ci += (& $cutW $o.fProof 22) }`
> `fAc` and `fCi` have been completely removed from the schema and all representative fixtures.

---

## 4. Source-to-10-Cell Lineage & Expected Outputs

In `watch.ps1` (`rows` and `rowsjson`), the coordinator formats:
`| Tab | Status | Aim | Plan | AC | CI | Meter | Due | Checked | Next |`

| Cell Column | Field Name | State Origin | Exact Derivation Logic in `watch.ps1` |
| :---: | :--- | :--- | :--- |
| 1 | **Tab** | `cycle.map` component 1 | Formatted as `Tab <pos>`. |
| 2 | **Status** | `hw.lastState`, `hw.actAt`, `hw.buddy`, `hw.aLane`, `hw.parkAt` | Dot icon (`🟢`, `🟡`, `🔴`, `⚪`, `🔵`) + status string. If `idle >= 60 min`, `🔵 stable <min> min · <status>`. If `parkAt`, `⚪ parked: <why>`. Handover and Buddy states override default working state. |
| 3 | **Aim** | `aim` record + `cp` cards | Formatted as `[🛡️] <Aim-Ver> · <AimDot> <sum> [· <why>] [· card <id>]`. If draft: `label draft · card <id>`. |
| 4 | **Plan** | `hw.fPlan`, `hw.bPub1`, `hw.yLast` | Agent task claim string and Buddy progress tokens (`Buddy 1b ✓`, `Y ✓ <step>`). |
| 5 | **AC** | `hw.aca`, `hw.act` | Formatted as `"{aca}/{act}"` if `aca >= 0`, else `"-"`. |
| 6 | **CI** | `hw.fTests`, `hw.fProof` | Test results or proof summary (`fTests` if present, else `"-"`). |
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
    "ac": "-",
    "ci": "-",
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
    "ac": "-",
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

## 5. Manifest Membership, Existence, and Tamper Enforcement

The versioned artifact manifest [`expected_digests.json`](./expected_digests.json) strictly enforces:
1. **Mandatory Membership**:
   Every required evidence artifact (`source_contract.schema.json`, `coordinator_state_v330_positive.json`, `coordinator_state_v330_negative.json`, `SOURCE_CONTRACT.md`, `validate_fixtures.py`) MUST be declared in the manifest. Omitting any required file immediately causes test failure (exit code 1).
2. **On-Disk Existence**:
   Every file declared in the manifest MUST actually exist on disk. Declaring a nonexistent file (such as `missing-evidence.json`) causes immediate test failure (exit code 1).
3. **Fixed Pinned Hashes**:
   Every declared file's SHA-256 digest is strictly compared against its pinned value. Any tamper or digest corruption causes immediate test failure (exit code 1).
4. **Self-Updating Manifest Forbidden**:
   The test runner does NOT rewrite or self-update `expected_digests.json` at runtime.
