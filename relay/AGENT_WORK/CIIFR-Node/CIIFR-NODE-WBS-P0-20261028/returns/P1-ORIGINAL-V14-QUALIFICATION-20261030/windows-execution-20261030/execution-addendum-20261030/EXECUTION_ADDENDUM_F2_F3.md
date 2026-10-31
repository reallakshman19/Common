# CIIFR-Node P1.2 Windows Execution Addendum (F2 / F3)

**Task:** `CIIFR-NODE-N02-FIXTURE-V14` · [XML_Compare_Utilities Issue #229](https://github.com/reallakshman19/XML_Compare_Utilities/issues/229) · [Parent #227](https://github.com/reallakshman19/XML_Compare_Utilities/issues/227) · [Review #228](https://github.com/reallakshman19/XML_Compare_Utilities/issues/228)  
**Actor:** Local Windows qualification agent `01429edb` (native Windows 10/11 x64, Node v22.23.2).  
**Mode:** `READ_ONLY`. Continuation on candidate [Draft PR #232](https://github.com/reallakshman19/XML_Compare_Utilities/pull/232) commit `d3fbd4041ef4434b4cf5b3c22459f06167be2729`.  
**Reference Request:** [`LOCAL_AGENT_ADDENDUM_REQUEST.md`](https://github.com/reallakshman19/Common/blob/44b7c54b28319aeaa5285106aef5a05ff2581a79/relay/AGENT_WORK/CIIFR-Node/CIIFR-NODE-WBS-P0-20261028/returns/P1-ORIGINAL-V14-QUALIFICATION-20261030/windows-execution-20261030/reporting-reconciliation-20261030/LOCAL_AGENT_ADDENDUM_REQUEST.md) · Erratum [`REPORTING_ERRATUM_F1.md`](https://github.com/reallakshman19/Common/blob/44b7c54b28319aeaa5285106aef5a05ff2581a79/relay/AGENT_WORK/CIIFR-Node/CIIFR-NODE-WBS-P0-20261028/returns/P1-ORIGINAL-V14-QUALIFICATION-20261030/windows-execution-20261030/reporting-reconciliation-20261030/REPORTING_ERRATUM_F1.md)  
**Base Execution Commit:** [`52067c1b36d54f50c6945c3538dcc83967232fbe`](https://github.com/reallakshman19/Common/commit/52067c1b36d54f50c6945c3538dcc83967232fbe)  
**Relay PR:** [reallakshman19/Common Draft PR #569](https://github.com/reallakshman19/Common/pull/569) on branch `review/ciifr-node-p12-original-v14-20261030`.

---

### 1. F1 Narrative Acknowledgment

The two stale git blob quotes in historical `windows-receipt.md` for `docs/cii-fnr-vnext.html` and `docs/tabs/cii-workspace/cii-fnr-vnext/ui/app.js` are formally acknowledged and corrected by `REPORTING_ERRATUM_F1.md`. The separately committed `payload/evidence/source-verification.json` and actual product candidate checkout at HEAD `d3fbd4041ef4434b4cf5b3c22459f06167be2729` correctly record exact blobs `3c0f8dae2ccc68f518f1ad582f1ba831a13a24ac` and `74891ccd948782b54b8f7781168e996c65d2af9e` across all 11 records.

---

### 2. F2: Execution-Bound Browser Distinctions

Two distinct browser executions were performed sequentially on the authorized native Windows workstation. Grounded in the preserved command transcripts, timestamps, process logs, and host CDP probes:

#### Run 1 — Microsoft Edge (Default Discovery)
- **Executable Basename:** `msedge.exe`
- **Browser Selection Mechanism:** Automatic discovery order in `tools/run-windows-original.mjs` (`browserExecutable()`). Without `--browser`, the runner checked `PROGRAMFILES(X86)`, `PROGRAMFILES`, and `LOCALAPPDATA`, selecting the first match: `Microsoft/Edge/Application/msedge.exe`.
- **Command Invocation:**
  ```powershell
  node .\CIIFR_P12_ORIGINAL_WINDOWS_GATE\tools\run-windows-original.mjs `
    --repo $repo `
    --original $original `
    --private-dir $privateDirEdge `
    --public-dir $publicDirEdge `
    --expected-sha $privateSha
  ```
- **Execution Timestamp:** `2026-10-30T14:45:50+04:00` to `2026-10-30T14:45:56+04:00` (elapsed ~6 seconds).
- **Process Exit Code:** `0`
- **Candidate HEAD:** `d3fbd4041ef4434b4cf5b3c22459f06167be2729` (clean tracked status verified).
- **Runner Identity:** SHA-256 `06bd46ec1e94a0ac27bfa467682a7b912c6140d4631674d024fa350372a96629` (`tools/run-windows-original.mjs`).
- **CDP Protocol & Browser Version Evidence:**
  - *Historical run note:* The unchanged runner `tools/run-windows-original.mjs` calls `Page.enable`, `Runtime.enable`, and `Network.enable`, but does not invoke `Browser.getVersion` over CDP.
  - *Host CDP probe against the identical `msedge.exe` binary:*
    - `product`: `Edg/156.0.4314.50`
    - `revision`: `@af2ba23ae0ecf7084d900446fc59d5119dd5fd5e`
    - `userAgent`: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/156.0.0.0 Safari/537.36 Edg/156.0.0.0`
    - `protocolVersion`: `1.3`
    - `jsVersion`: `15.6.12.7`
- **Assertion Outcome:** 6/6 served blob matches, intake accepted, element witness PASS (exact stored T1, P1, fluid density raw lexemes and zero-based half-open byte spans), node witnesses PASS (4 node queries matching incident, restraint, rigid, displacement rows), 5 UNKNOWN families, no writer, 0 exceptions, 0 external requests (**PASS**).

#### Run 2 — Google Chrome (Explicit CLI Selection)
- **Executable Basename:** `chrome.exe`
- **Browser Selection Mechanism:** Explicit CLI flag `--browser <full_path_to_chrome.exe>` passed to `tools/run-windows-original.mjs`, explicitly overriding Edge auto-discovery.
- **Command Invocation:**
  ```powershell
  node .\CIIFR_P12_ORIGINAL_WINDOWS_GATE\tools\run-windows-original.mjs `
    --repo $repo `
    --original $original `
    --private-dir $privateDirChrome `
    --public-dir $publicDirChrome `
    --expected-sha $privateSha `
    --browser $chrome
  ```
- **Execution Timestamp:** `2026-10-30T14:46:20+04:00` to `2026-10-30T14:46:24+04:00` (elapsed ~4 seconds).
- **Process Exit Code:** `0`
- **Candidate HEAD:** `d3fbd4041ef4434b4cf5b3c22459f06167be2729` (clean tracked status verified).
- **Runner Identity:** SHA-256 `06bd46ec1e94a0ac27bfa467682a7b912c6140d4631674d024fa350372a96629` (`tools/run-windows-original.mjs`).
- **CDP Protocol & Browser Version Evidence:**
  - *Historical run note:* As with Run 1, `Browser.getVersion` was not queried by the original runner.
  - *Host CDP probe against the identical `chrome.exe` binary:*
    - `product`: `Chrome/156.0.8078.74`
    - `revision`: `@d331de35ca8ab1358c7a17e4bd41627d55eaef51`
    - `userAgent`: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/156.0.0.0 Safari/537.36`
    - `protocolVersion`: `1.3`
    - `jsVersion`: `15.6.75.25`
- **Assertion Outcome:** 6/6 served blob matches, intake accepted, element witness PASS, node witnesses PASS (4 node queries), 5 UNKNOWN families, no writer, 0 exceptions, 0 external requests (**PASS**).

---

### 3. F3: Private Expected SHA Authentication & Custody Isolation

- **Truthful Booleans:**
  - `privateExpectedSHAProvided`: **`true`** (both Run 1 and Run 2)
  - `privateExpectedSHAMatched`: **`true`** (both Run 1 and Run 2)
- **Evidence Basis in Runner:**
  - In `tools/physical-oracle.mjs` line 63:
    ```javascript
    if (expectedSHA) REQUIRE(hash.toLowerCase() === expectedSHA.toLowerCase(), 'INTAKE_DIGEST_MISMATCH');
    ```
  - Both runs were executed with `--expected-sha $privateSha` where `$privateSha` was verified matching `^[0-9a-fA-F]{64}$`.
  - Neither run threw `PHYSICAL_ORACLE_INTAKE_DIGEST_MISMATCH`; both proceeded cleanly to full browser execution and exited with code `0`.
- **Pre-Execution Expected Match vs Post-Execution Immutability:**
  - *Expected Match:* Intake SHA-256 matched Owner's expected digest before trial (`INTAKE_DIGEST_MISMATCH` passed).
  - *Post-Inspection Immutability:* Re-hashed after the browser session; raw file bytes and SHA-256 digest remained strictly identical to pre-trial state (`ORIGINAL_CHANGED` check in line 139 passed).
  - *Confidentiality:* The actual 64-hex SHA-256 digest remains withheld from public GitHub.
- **Custody & Path Separation:**
  - **Original Input Location:** Preserved in private local downloads path outside the served repository (`originalInsideServedRepo: false`).
  - **Private Evidence Directories:** Both `ciifr-p12-original-private` and `ciifr-p12-original-chrome-private` resided in separate evidence directories outside the served repository (`privateDirInsideServedRepo: false`).
  - **Loopback Web Root:** Pinned candidate repository served strictly over `127.0.0.1` without exposure of the protected original or private evidence directories.

---

### 4. Summary Matrix

| Metric | Run 1 (Microsoft Edge) | Run 2 (Google Chrome) |
|---|---|---|
| **Executable Basename** | `msedge.exe` | `chrome.exe` |
| **Selection Mode** | Auto-discovery default | Explicit `--browser` argument |
| **CDP Product (Probed)** | `Edg/156.0.4314.50` | `Chrome/156.0.8078.74` |
| **Run Window (UTC+4)** | `2026-10-30 14:45:50 – 14:45:56` | `2026-10-30 14:46:20 – 14:46:24` |
| **Exit Code** | `0` | `0` |
| **Product HEAD** | `d3fbd4041ef4434b4cf5b3c22459f06167be2729` | `d3fbd4041ef4434b4cf5b3c22459f06167be2729` |
| **Tracked Cleanliness** | Clean (`--porcelain` empty) | Clean (`--porcelain` empty) |
| **`privateExpectedSHAProvided`** | `true` | `true` |
| **`privateExpectedSHAMatched`** | `true` | `true` |
| **Original Immutable** | `true` | `true` |
| **Separated from Served Repo** | `true` | `true` |
| **Assertion Outcome** | `PASS` | `PASS` |

---

### 5. Gate Status & Governance

- **WBS 2.2 / M5 / P1.2 Browser Qualification:** **`PASS`** (evidence authenticated).
- **Candidate PR #232, Parent PR #226, GATE_R0:** Remain **`DRAFT / HOLD`**.
- No product source, fixture, property writer, merge, deployment, or release authorized.
