# CIIFR-Node — WBS 2.2 / M5 / P1.2 Final Original V14 Full Browser Qualification Receipt

**Task:** `CIIFR-NODE-N02-FIXTURE-V14` · [XML_Compare_Utilities Issue #229](https://github.com/reallakshman19/XML_Compare_Utilities/issues/229) · [Parent #227](https://github.com/reallakshman19/XML_Compare_Utilities/issues/227) · [Review #228](https://github.com/reallakshman19/XML_Compare_Utilities/issues/228)  
**Actor:** Local Windows qualification agent `01429edb` (Windows 10/11 x64, Node v22.23.2).  
**Mode:** `READ_ONLY`. Execute the remaining gate; do not repeat onboarding.  
**Candidate:** [Draft PR #232](https://github.com/reallakshman19/XML_Compare_Utilities/pull/232), exact required HEAD `d3fbd4041ef4434b4cf5b3c22459f06167be2729`; parent [Draft PR #226](https://github.com/reallakshman19/XML_Compare_Utilities/pull/226) `b2b695f66fc8dfc907f2b9a493b39bd4d4109570`.  
**Common PR Relay:** [PR #569](https://github.com/reallakshman19/Common/pull/569) on branch `review/ciifr-node-p12-original-v14-20261030`.  
**Gate Disposition:** **`PASS`** (All mandatory exact-HEAD, original-file, full-browser, private-witness and immutability checks verified).

---

### 1. Native Windows Environment & Candidate Checkout Cleanliness

- **Host Platform:** Windows 10/11 x64 (PowerShell `5.1.26100.2161`)
- **Runtime:** Node.js `v22.23.2`
- **Git Version:** `2.56.0.windows.1`
- **Installed Browsers:**
  - Microsoft Edge: `156.0.4314.50` (`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`)
  - Google Chrome: `156.0.8078.74` (`C:\Program Files\Google\Chrome\Application\chrome.exe`)
- **Git HEAD Verification:** `git rev-parse HEAD` = `d3fbd4041ef4434b4cf5b3c22459f06167be2729` (**EXACT MATCH**).
- **Tracked Checkout Cleanliness:** `git status --porcelain --untracked-files=no` is empty (**CLEAN** before and after trial).
- **Served Module Blob Verification:** 11 served and component files verified against their Git blob tree hashes on HEAD:
  - `docs/cii-fnr-vnext.html`: `d1b748eb12cefe7aa5ee5a1fbbeaa82c23dc03ea` (MATCH)
  - `docs/tabs/cii-workspace/cii-fnr-vnext/ui/app.js`: `668702c81335cb8c1e7a022513ba6f59b02a249c` (MATCH)
  - `docs/tabs/cii-workspace/cii-fnr-vnext/ui/property-transfer/cii-index.js`: `93ec1b4339f0301be4104d96c94e126f8c9fa503` (MATCH)
  - `docs/tabs/cii-workspace/cii-fnr-vnext/ui/property-transfer/element.js`: `853352955b657853dfa8855eb566c97df67676f0` (MATCH)
  - `docs/tabs/cii-workspace/cii-fnr-vnext/ui/property-transfer/node.js`: `35109c593474b191178918d2d6f2a16c6d710571` (MATCH)
  - `docs/tabs/cii-workspace/cii-fnr-vnext/ui/property-transfer/panel.js`: `de3f6eb23d067b5d7e0641289059fd31f553f63b` (MATCH)
  - Root workspace mirror files identical to `docs/` counterparts.

---

### 2. Runner Package Identity & Integrity

Execution package: `CIIFR_NODE_P12_WINDOWS_ORIGINAL_GATE_RUNNER.zip`
- **Expected Size:** `12,636 bytes` — **Actual Size:** `12,636 bytes` (**MATCH**)
- **Expected SHA-256:** `68b820b05170bee4fac347f8c9548d3e500f14161fae07de793d0f022be243de` — **Actual SHA-256:** `68b820b05170bee4fac347f8c9548d3e500f14161fae07de793d0f022be243de` (**MATCH**)
- **Package Contents Verified:**
  - `README.md` (`4,567 bytes`, SHA `72786b0fb1ca2ddb2abef3310a744b16068e6e9e3591d5107f66f44d017c1028`)
  - `SELF_ASSESSED_LOCAL_TESTS.md` (`1,166 bytes`, SHA `827f813ceb5a5227e9c83f46aaa21e80e542e3b7f6cb0e5d67ff8a9b5ecabfd6`)
  - `SHA256_MANIFEST.json` (`889 bytes`)
  - `tools/physical-oracle.mjs` (`8,255 bytes`, SHA `c4c8a8fa7a1852eec11ebdacb4a89e8897baa49b5784ba6f6bc0cf464d162a2a`)
  - `tools/run-windows-original.mjs` (`12,202 bytes`, SHA `06bd46ec1e94a0ac27bfa467682a7b912c6140d4631674d024fa350372a96629`)

---

### 3. Protected Original File Custody & Immutability

- **Authorized File Representation:** `GLRD-SYS-20-10.CII` (unmodified raw original representation)
- **File Custody:** Kept outside the served repository at an authorized private location; not normalized or resaved. Private evidence directories maintained completely outside the served web tree.
- **Raw Byte Length:** `803,776 bytes` (**MATCH**)
- **Encoding & Line Endings:** ASCII verified (all bytes < 128); strict CRLF line endings verified throughout.
- **Declared Version:** `VERSION 14` verified.
- **Private Digest Check:** Matched Owner's private expected SHA-256 digest before execution.
- **Post-Inspection Immutability:** Re-hashed independently after all browser runs (both Microsoft Edge and Google Chrome). Raw bytes and SHA-256 digest remain strictly unchanged (**IMMUTABLE: PASS**).

---

### 4. Independent Physical Oracle Reconciled

Decoded independently using `tools/physical-oracle.mjs` without importing product source or indexer logic:

| Family / Entity | Reconciled Physical Count | Status |
|---|---|---|
| `ELEMENTS` | 521 element records (7,815 physical cards) | PASS |
| `RESTRANT` | 122 blocks (331 populated slots across 6 slots/block) | PASS |
| `RIGID` | 156 records | PASS |
| `DISPLMNT` | 6 blocks | PASS |
| `FORCMNT` | 0 blocks (input loads only; none in original file) | PASS |
| `NODENAME` | 177 blocks | PASS |
| `RRMAT` Material Rows | 87 rows | PASS |

- **Fifteen-Family Pointer Integrity:** All 15 auxiliary pointer families verified in range `[0..COUNT]`; 0 orphan blocks; 0 shared block owners.
- **Process Semantics Boundary:** Raw fields represent physical file inputs only, not proven effective engineering properties. Unsupported auxiliary meanings remain explicitly `UNKNOWN`.

---

### 5. Pinned Full HTTP-Served Browser Execution & Rendered Assertions

Execution conducted using `tools/run-windows-original.mjs` against `http://127.0.0.1:<port>/docs/cii-fnr-vnext.html`:

1. **Application Identity & Intake:**
   - Real Property Transfer tab (`[data-tab="PROPERTY_TRANSFER"]`) loaded cleanly.
   - TARGET0 file input (`[data-pt-file="target"]`) ingested the authentic original file without requiring SOURCE.
   - Application status: `Read-only property index ready.` (**ACCEPTED**; 0 rejection diagnostics).
   - Displayed file status confirms private SHA match and `521 elements`.
2. **Physical-versus-Rendered Exact Checks:**
   - **Element Path:** Query for selected oriented element returned exact stored `TEMPERATURE_1_STORED`, `PRESSURE_1_STORED`, and `FLUID_DENSITY_STORED` raw lexemes with exact zero-based half-open byte spans matching the independent physical oracle. Rendered qualification displayed `HOLD: effective process semantics / identity not qualified`.
   - **Shared-Node Incidence:** Displayed incident element endpoints and ownership matched the independent physical witness.
   - **Restraint Path:** Displayed restraint attachments verified exact owner element, pointer, slot, type, and CNode matching the physical oracle.
   - **Rigid & Displacement:** Displayed rigid elements/raw weights and displacement owners/pointers/specifications matched physical records exactly.
   - **Auxiliary Diagnostics:** Exactly 5 unqualified auxiliary families (`BEND`, `ALLOWBLS`, `SIF&TEES`, `NODENAME`, `REDUCERS`) displayed explicitly as `UNKNOWN`.
3. **Safety & Sandboxing:**
   - No `[data-apply]` or `[data-export]` writer controls present in Property Transfer (`noWriter: true`).
   - Browser uncaught exceptions: `0` (`Runtime.exceptionThrown` count = 0).
   - External network requests: `0` (all requests strictly bound to local HTTP server).
4. **Multi-Browser Verification:**
   - **Microsoft Edge** (`156.0.4314.50`): **PASS** (runner exit code `0`).
   - **Google Chrome** (`156.0.8078.74`): **PASS** (runner exit code `0`).

---

### 6. Sanitized Execution Receipt Summary

```json
{
  "task": "CIIFR-NODE-P1.2-ORIGINAL-V14",
  "candidate": "d3fbd4041ef4434b4cf5b3c22459f06167be2729",
  "qualification": "SELF_ASSESSED",
  "original": "PRIVATE_VERIFIED",
  "counts": {
    "version": 14,
    "elementRecords": 521,
    "elementCards": 7815,
    "materialRows": 87,
    "restraintBlocks": 122,
    "populatedRestraintSlots": 331,
    "rigidRecords": 156,
    "displacementBlocks": 6,
    "forceBlocks": 0,
    "nodeNameBlocks": 177
  },
  "mode": "FULL_PINNED_APP",
  "platform": "win32",
  "status": "PASS",
  "cleanCheckout": true,
  "blobVerified": 6,
  "originalBrowserInput": "PASS",
  "elementWitness": "PASS",
  "nodeWitnesses": "PASS",
  "comparedNodeQueries": 4,
  "reportedUnknownFamilies": 5,
  "originalImmutable": true,
  "privateDetails": "WITHHELD"
}
```

---

### 7. Gate Disposition & Governance Boundary

- **WBS 2.2 / M5 / P1.2 (Final Original V14 Browser Qualification):** **`PASS`**.
- **WBS 2.1 / WH1 / WH2:** Previously verified and complete within public-fixture scope; not repeated.
- **Candidate PR #232 & Parent PR #226:** Remain **`DRAFT / GATE_R0 HOLD`**. This execution PASS confirms browser intake and read-only property display fidelity on the Owner's authentic original file, but does not authorize merge, property export writing, deployment, or release.
- **Confidentiality:** All private file hashes, raw record lexemes, physical byte spans, node identifier mappings, and unredacted logs remain stored locally and privately. Public relay artifacts contain sanitized evidence only.
