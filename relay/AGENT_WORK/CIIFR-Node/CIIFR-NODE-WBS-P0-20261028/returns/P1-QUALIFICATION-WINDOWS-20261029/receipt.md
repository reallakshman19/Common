# CIIFR-Node — Local Windows P1 Qualification Return (WBS 2.1)

**Task:** CIIFR-NODE-N02-FIXTURE-V14 ([Issue #229](https://github.com/reallakshman19/XML_Compare_Utilities/issues/229)); cross-linked to [#228](https://github.com/reallakshman19/XML_Compare_Utilities/issues/228) and parent [#227](https://github.com/reallakshman19/XML_Compare_Utilities/issues/227).  
**Governing WBS:** CIIFR-Node R1 (`progress-page/data/ciifr-node/index.json`): **2.1 / M4 / P1.1** (Windows browser regression & native checks); **1.1 / M2 / P0.1** (public fixture custody); **2.2 / M5 / P1.2** (original-V14 trial: `ORIGINAL=NOT_RECEIVED / NOT_RUN`).  
**Candidate:** [Draft PR #232](https://github.com/reallakshman19/XML_Compare_Utilities/pull/232), commit `d3fbd4041ef4434b4cf5b3c22459f06167be2729`; branch `codex/ciifr-node-p1-r1-repair-20261029`.  
**Parent / Base:** Parent PR #226 `b2b695f66fc8dfc907f2b9a493b39bd4d4109570`; base at code review `fd86b21aa9dcbfbbe4f8a1d26133b7e9779448be`.  
**Executor & Independence:** Local Windows Qualification Agent (Chat ID `01429edb`); non-author review executed locally on Windows 10/11 x64. Strict READ_ONLY qualification; no product code, test harness, or oracle edits.

---

## 1. Native Regressions Status Correction

Per protocol, native regression suites are distinguished between focused test suites and the complete historical VNext suite:

| Suite | Command | Result | Exit Code | Evaluation |
|---|---|:---:|:---:|---|
| Focused Property Transfer & UI | `node --test tests/cii-fnr-vnext-property-transfer-r0.test.mjs tests/cii-fnr-vnext-property-transfer-ui-regression.test.mjs tests/cii-fnr-vnext-nodal-ui.test.mjs` | **17 PASS / 0 FAIL** | 0 | **PASS** |
| Property Transfer Repair (PR232) | `node --test tests/cii-fnr-vnext-property-transfer-repair.test.mjs` | **13 PASS / 0 FAIL** | 0 | **PASS** |
| Bounded Geometry Authority | `node --test tests/cii-workspace-geometry-authority.test.js tests/cii-workspace-method-c-original-geometry.test.js` | **9 PASS / 0 FAIL** | 0 | **PASS** |
| **Complete VNext Suite (24 test files)** | `node --test --test-concurrency=1 @vnextTests` | **123 PASS / 1 FAIL** | 1 | **FAIL / RED (Preserved Inherited Failure)** |

### Inherited Assertion Disclosure
The complete VNext test suite contains one retained failure:
- **Location:** `tests/cii-fnr-vnext-branch-scope.test.mjs:81:1`
- **Subtest:** `branch identifier mismatch gives zero replacements, no prefix matching`
- **Assertion:** `AssertionError [ERR_ASSERTION]: Expected values to be strictly equal: 1 !== 0`
- **Diagnosis:** As independently documented in prior non-author R2 review, branch B1 actually owns node 9000's ALIAS-OLD, giving a physical match of 1 instead of the test harness's expected 0.
- **Protocol Action:** This existing failure is preserved unchanged without modification or assertion softening. Whole-suite status remains **123 PASS / 1 FAIL (FAIL/RED)**.

Raw TAP evidence logs are preserved in `payload/evidence/`: `required-three.tap`, `repair.tap`, `vnext-all-complete.tap`, and `geometry.tap`.

---

## 2. Case 5 Endpoint Checks: Node-Query Validation vs Mutated CII File Intake

Per Owner instruction, UI search/query box text validation is explicitly distinguished from mutated CII file intake parsing:

### 2A. UI Search / Query Box Input Validation
Tests the UI input elements (`sourceFrom`, `sourceTo`, `targetFrom`, `targetTo`, `sourceNode`, `targetNode`) parsed by `normalizedNode(s)`:
- **Negative node input (`-400`):** Blocked by query validator -> UI displays `Inspection blocked: PROPERTY_NODE_NOT_CANONICAL`.
- **Zero node input (`0`):** Blocked by query validator -> UI displays `Inspection blocked: PROPERTY_NODE_INVALID` (positive logical node numbers only).

### 2B. Mutated CII File Intake Parsing
Tests the neutral file parser and indexer `indexCiiV14(bytes)` when loading candidate CII files into the Property Transfer file intake (`[data-pt-file="target"]`):
- **Mutated CII with negative element endpoint (`-840`):** Indexer rejects on intake -> UI displays `Input rejected: PROPERTY_ELEMENT_ENDPOINT_NEGATIVE`.
- **Mutated CII with zero element endpoint (`0`):** Indexer holds on intake -> UI displays `Input rejected: PROPERTY_ELEMENT_ZERO_ENDPOINT_UNQUALIFIED`.
- **Mutated CII with pointer beyond CONTROL count (`BEND pointer = 999`, count = 0):** Indexer rejects on intake -> UI displays `Input rejected: PROPERTY_POINTER_RANGE_BEND`.
- **Mutated CII with dormant nonzero restraint payload (slot 2 card 2 has nonzero payload `999.0` with zero node):** File indexes successfully without data corruption; UI surfaces visible UNKNOWN diagnostic:
  - `TARGET · UNKNOWN input evidence`
  - `UNKNOWN · PROPERTY_RESTRAINT_DORMANT_RESIDUE · RESTRANT`
  - `Zero node/type/CNode with other payload; dormant-slot legality NOT_QUALIFIED. Bytes preserved.`
  - `Element 1 · Pointer 1 · Slot 2 · bytes 3236–3562`

### 2C. Write / Export Authority Isolation
- Verified that `[data-property-transfer-area]` exposes **no** Apply button and **no** Export button anywhere in the DOM.

---

## 3. Real Served Browser Qualification (Edge 156 & Chrome 156)

Executed against local HTTP server `http://127.0.0.1:8765/docs/cii-fnr-vnext.html` using the automated runner `run_qualification_browser.mjs` via Chrome DevTools Protocol (CDP) over WebSocket with clean user-data directories.

### Environment
- **Microsoft Edge:** `156.0.4314.42` (`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`)
- **Google Chrome:** `156.0.8078.48` (`C:\Program Files\Google\Chrome\Application\chrome.exe`)

### Observable Browser Cases Summary

| Case | Description | Microsoft Edge 156 | Google Chrome 156 |
|---|---|:---:|:---:|
| **Case 1** | Committed Normal Demo: load synthetic CII & CSV, generate proposals, approve/reject, validate in memory, apply to new copy, export enabled (Target1 SHA: `4bf7f868eda840cb45af6febfc2174a7ddfc2c21fb921be3cf411d3122bd7591`) | **PASS** | **PASS** |
| **Case 2** | Property Navigation Isolation: load public fixtures, inspect element/node, return to Normal -> Normal proposals, decisions, and export eligibility **100% preserved**. Repeat for Nodal -> Nodal applied hash `1736624d...` **100% preserved** | **PASS** | **PASS** |
| **Case 3** | Invalidation & Pending-CSV Controlled Delay: rule edit revokes authority immediately. Artificial controlled delay on `File.prototype.text`: export/apply/validate disabled and 0 claims while pending; clear while pending does not reinstall rules; fresh completed read restores eligibility | **PASS** | **PASS** |
| **Case 4** | Process Ownership & Separation: SOURCE 400->500 (`T1=200`, `P1=30`) and 500->600 (`T1=180`, `P1=20`) share node 500 but retain distinct process fields. Reverse 500->400 matches 0 elements. Node 500 attachments (RESTRANT, DISPLMNT, FORCMNT, RIGID) verified | **PASS** | **PASS** |
| **Case 5** | Negative/zero query inputs vs mutated CII file endpoints: query inputs throw `PROPERTY_NODE_NOT_CANONICAL` and `PROPERTY_NODE_INVALID`. Mutated files throw `PROPERTY_ELEMENT_ENDPOINT_NEGATIVE`, `PROPERTY_ELEMENT_ZERO_ENDPOINT_UNQUALIFIED`, `PROPERTY_POINTER_RANGE_BEND`. Dormant residue flagged as visible UNKNOWN. No Apply/Export buttons in Property DOM | **PASS** | **PASS** |
| **Case 6** | Tab Navigation & Integrity: cycled all 7 tabs (`NORMAL`, `NODAL`, `PROPERTY_TRANSFER`, `LINE_NODE`, `GEOMETRY`, `CIIFR_GEO`, `CONFIG`). 0 uncaught exceptions, 0 console errors. 0 external network requests. Public fixture hashes unchanged | **PASS** | **PASS** |

Structured JSON results: `payload/browser_qualification_report.json`.

---

## 4. Public Fixture Custody & Bitwise Immutability (WBS 1.1)

Public fixtures downloaded from Common `56dbc3a0af137c433ffb5fec48316fa2022d075c`:
- `SYNTH_V14_SOURCE.cii`: 8,276 bytes, SHA-256 `c8de516c54767c7cf7d5239d404810be891ed3d56ec2111db3dc4c2b07dcdb0b`
- `SYNTH_V14_TARGET0.cii`: 8,276 bytes, SHA-256 `0bbc3b0a8b7b1e73d655d0a0ffc267e6a698dec5ff66763c468cdc835cc19661`

Measured SHA-256 before and after execution: **Bitwise identical**. Neither local memory execution nor browser interaction mutated fixture bytes on disk.

---

## 5. Protected Original V14 Custody Gate (WBS 2.2 / M5 / P1.2)

- **Status:** **`ORIGINAL=NOT_RECEIVED / NOT_RUN`**.
- Per plan instructions:
  > *"Obtain the exact original file/path from the Owner or its authorized custodian. Never search unrelated conversations, Library files or guessed private links. Missing original access leaves ORIGINAL=NOT_RECEIVED/NOT_RUN while public/browser work continues."*
- No unprovided files, guessed paths, or private repositories were accessed.
- Protected original trial remains pending Owner dispatch of the authorized file locator.

---

## 6. Gate Status

- **WBS 2.1 (Windows Browser & Native Regression):** **EVIDENCE PUBLISHED** (Edge/Chrome PASS, native regressions documented with preserved inherited failure).
- **WBS 1.1 (Public Fixtures):** **PASS / IMMUTABLE**.
- **WBS 2.2 (Original V14 Trial):** **NOT_RUN / AWAITING AUTHORIZED CUSTODY**.
- **Candidate PR #232:** **DRAFT / GATE_R0 HOLD**. No merge, integration, or property writing permitted.
