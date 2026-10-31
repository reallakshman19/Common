# CIIFR-Node — PR #238 Native Qualification Execution Receipt

**Task:** `CIIFR-NODE-PR238-NATIVE-REVIEW` · [XML_Compare_Utilities PR #238](https://github.com/reallakshman19/XML_Compare_Utilities/pull/238) · [Issue #231](https://github.com/reallakshman19/XML_Compare_Utilities/issues/231)  
**Parent / Context Issues:** [Parent #227](https://github.com/reallakshman19/XML_Compare_Utilities/issues/227) · [Review #228](https://github.com/reallakshman19/XML_Compare_Utilities/issues/228) · [Qualification #229](https://github.com/reallakshman19/XML_Compare_Utilities/issues/229)  
**Common PR Relay:** [PR #569](https://github.com/reallakshman19/Common/pull/569) on branch `review/ciifr-node-p12-original-v14-20261030`  
**Date:** 2026-10-31  
**Actor / Operator:** Local Windows qualification agent `01429edb`  
**Host Platform:** Windows 10/11 x64 (`Microsoft Windows NT 10.0.26200.0`, PowerShell `5.1.26100.2161`)  
**Runtime:** Node.js `v22.23.2`  
**Git Version:** `git version 2.56.0.windows.1`  
**Gate Disposition:** **`PASS_PINNED_NATIVE_TESTS`** (Native test qualification only; merge and engineering decisions remain on HOLD)

---

### 1. Identity, Authorship & Prior Exposure Declaration

In accordance with qualification protocol requirements:
- **Operator Identity:** Local Windows qualification agent `01429edb`.
- **Authorship of PR #238:** Agent `01429edb` did **not** author PR #238 (PR authored by `reallakshman19`).
- **Prior Exposure:** Source-exposed (previously inspected product source modules and test fixtures during WBS 2.1 / P1 / P1.2 qualification trials).
- **Operating Account:** Operating under authenticated GitHub account `reallakshman19`.
- **Review Boundary:** This is an automated native qualification run verifying package integrity, clean execution, test outputs, and complete path inventories. It does **not** claim blind or distinct-human review.

---

### 2. Runner Package Verification

The runner package `CIIFR_PR238_NATIVE_QUALIFICATION_R1.zip` was received and verified prior to extraction:
- **Archive Size:** `14,694 bytes` (**EXACT MATCH**)
- **Archive SHA-256:** `8b46b3af0450c02196d1a870be1e834ee7c92dbe4ccf285d865c6e77a82245bf` (**EXACT MATCH**)
- **Manifest Integrity:** All 13 manifest-listed files verified; JavaScript syntax passes `node --check`.

---

### 3. Native Execution Parameters & Cleanliness

Execution was invoked from the extracted package directory:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run-windows.ps1
```

- **Pinned Base Commit:** `417bf6a954c5a6de72237537e94b05b285191350`
- **Pinned Candidate Commit:** `fa6e948eb0f71ba93fe8bab01625e3146d1df3a0`
- **Clones:** The runner instantiated two fresh detached local clones (`base` and `head`).
- **Worktree Cleanliness:** Both `base` and `head` checkouts were verified completely clean before and after test execution (`gitStatusBefore: ""`, `gitStatusAfter: ""`).
- **Source Code Integrity:** Product source code, test assertions, `PINNED.json`, and runner logic were preserved strictly unmodified.

---

### 4. Native Test Results

All four test scopes ran natively and produced the expected TAP logs, counts, and exit codes:

| Test Scope | Executed Command | Exit Code | Tests | Pass | Fail | TAP Evidence |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **base-target** | `node --test --test-reporter=tap tests/cii-fnr-vnext-branch-scope.test.mjs` | **1** | 19 | 18 | 1 | `receipts/base-target.tap` |
| **head-target** | `node --test --test-reporter=tap tests/cii-fnr-vnext-branch-scope.test.mjs` | **0** | 20 | 20 | 0 | `receipts/head-target.tap` |
| **base-full** | `node --test --test-reporter=tap --test-concurrency=1 <21 test files>` | **1** | 95 | 94 | 1 | `receipts/base-full.tap` |
| **head-full** | `node --test --test-reporter=tap --test-concurrency=1 <21 test files>` | **0** | 96 | 96 | 0 | `receipts/head-full.tap` |

Package verifier execution:
- **Command:** `node verify-results.mjs <receipts-dir>`
- **Exit Code:** `0`
- **Verdict:** `PASS_PINNED_NATIVE_TESTS`
- **Verifier Output:** `receipts/verification.json` and `receipts/verifier.stdout`

---

### 5. Identification of the Inherited Baseline Failure

The baseline test failure observed in both `base-target` and `base-full` was independently inspected and confirmed to be the exact intended inherited test-oracle defect:

- **Target Failure (`base-target.tap` line 79):**  
  `not ok 6 - branch identifier mismatch gives zero replacements, no prefix matching`
- **Full Suite Failure (`base-full.tap` line 267):**  
  `not ok 22 - branch identifier mismatch gives zero replacements, no prefix matching`
- **Mechanism:** The legacy test asserted that querying branch identifiers including `B1` produced zero replacements across all three query cases. However, the synthetic test fixture explicitly contains element `9000->9001` with pointer `3` and authentic `B1` branch identifier. Production correctly resolves this valid branch claim.
- **Candidate Correction:** PR #238 (`fa6e948e`) retains the negative zero-replacement assertions for nonexistent branch identifiers and adds a positive assertion verifying that querying `B1` replaces only its owned FROM name (`ALIAS-OLD` -> `B1`).
- **Head Results:** In `head-target.tap` and `head-full.tap`, the corrected assertion passes cleanly (`ok 6` / `ok 22`), with 0 test failures across the entire suite.

---

### 6. Complete 35-Distinct-Path Inventory Audit

Addressing the receiver probe note regarding verifier coverage (`verify-results.mjs` checks raw hash row count threshold `>= 29`):
An exhaustive path inventory was performed comparing all tracked checkout paths against the 35 expected paths in `PACKAGE_READBACK.json`:

1. **Test Paths (21 distinct files under `tests/`):**
   - `tests/cii-fnr-vnext-a1-f01-compact.test.mjs`
   - `tests/cii-fnr-vnext-a1-fortran-exponent-adversaries.test.mjs`
   - `tests/cii-fnr-vnext-a1-line-node-admission.test.mjs`
   - `tests/cii-fnr-vnext-a1-normal-node-closure.test.mjs`
   - `tests/cii-fnr-vnext-a1-policy-a-compact.test.mjs`
   - `tests/cii-fnr-vnext-a1-scientific-numbers.test.mjs`
   - `tests/cii-fnr-vnext-a1.test.mjs`
   - `tests/cii-fnr-vnext-branch-scope.test.mjs`
   - `tests/cii-fnr-vnext-config-policy.test.mjs`
   - `tests/cii-fnr-vnext-csv-resolver.test.mjs`
   - `tests/cii-fnr-vnext-demo.test.mjs`
   - `tests/cii-fnr-vnext-f02-lifecycle.test.mjs`
   - `tests/cii-fnr-vnext-geo-tab.test.mjs`
   - `tests/cii-fnr-vnext-nodal-numelt-guard.test.mjs`
   - `tests/cii-fnr-vnext-nodal-sections.test.mjs`
   - `tests/cii-fnr-vnext-nodal-transfer.test.mjs`
   - `tests/cii-fnr-vnext-nodal-ui.test.mjs`
   - `tests/cii-fnr-vnext-nodal-zero-guard.test.mjs`
   - `tests/cii-fnr-vnext-node-only-csv.test.mjs`
   - `tests/cii-fnr-vnext-p2-repair.test.mjs`
   - `tests/cii-fnr-vnext-r2-regressions.test.mjs`
2. **Critical Source Modules (7 distinct files under `tabs/cii-workspace/cii-fnr-vnext/`):**
   - `tabs/cii-workspace/cii-fnr-vnext/ui/physical.js`
   - `tabs/cii-workspace/cii-fnr-vnext/normal/plan.js`
   - `tabs/cii-workspace/cii-fnr-vnext/normal/branch-scope.js`
   - `tabs/cii-workspace/cii-fnr-vnext/ui/normal-node-closure.js`
   - `tabs/cii-workspace/cii-fnr-vnext/ui/writer.js`
   - `tabs/cii-workspace/cii-fnr-vnext/ui/source-provenance.js`
   - `tabs/cii-workspace/cii-fnr-vnext/ui/app.js`
3. **Served Mirror Modules (7 distinct files under `docs/tabs/cii-workspace/cii-fnr-vnext/`):**
   - Exact mirror of the 7 critical source modules above.

**Inventory Audit Results:**
- **Base Total Distinct Paths:** Exactly 35 (0 missing, 0 extra, 0 duplicates).
- **Head Total Distinct Paths:** Exactly 35 (0 missing, 0 extra, 0 duplicates).
- **Git Blob Comparison:**
  - Exactly **34 of 35** paths have identical Git blobs between Base and Head.
  - Exactly **1 path** differs: `tests/cii-fnr-vnext-branch-scope.test.mjs`:
    - Base Blob: `c69511a8c5234f46d9d678b88e5de53955b26c79`
    - Head Blob: `4d2fa260fbd48487e1ae39871e663e7df782cc49`
  - Zero changes occurred in production source code or served mirrors.

---

### 7. Evidence Custody & Sanitization

- **Raw Receipts:** The unredacted receipts generated during execution are retained privately on the local Windows qualification workstation at:  
  `sharp-mendel\pr238-native-exec\CIIFR_PR238_NATIVE_QUALIFICATION_R1\PR238_NATIVE_20261031T110105Z_10476\receipts`
- **Sanitization:** In `receipts/execution-meta.json`, the local Windows machine hostname (`LAPTOP-MM7V32EQ`) has been redacted to `REDACTED_LOCAL_WINDOWS_HOST` with explicit derivative metadata. The file structure and test command execution records are otherwise preserved intact.
- **Relay Publication:** The complete sanitized public receipt payload and manifests are committed to Common relay branch `review/ciifr-node-p12-original-v14-20261030` under:  
  `relay/AGENT_WORK/CIIFR-Node/CIIFR-NODE-WBS-P0-20261028/returns/PR238-WINDOWS-NATIVE-QUALIFICATION-20261031/`
- **Manifest:** All 20 receipt files, `RECEIPT.md`, and `ARTIFACT_MANIFEST.json` are cataloged with byte counts, SHA-256 digests, and Git blob IDs.

---

### 8. Governance & Hold Status

- Native test qualification verifies package mechanics and test assertions only.
- It does **not** constitute independent engineering acceptance, CAESAR II compatibility sign-off, or merge authorization.
- **GATE_R0, PR #238, PR #232, and PR #226 remain on HOLD** pending Owner and receiver review decisions.
