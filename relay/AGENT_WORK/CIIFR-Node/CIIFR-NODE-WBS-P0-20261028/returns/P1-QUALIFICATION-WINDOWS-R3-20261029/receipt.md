# CIIFR-Node — Local Windows P1 Qualification Return (Revision 3: Exact Fields & Physical Oracle)

**Date:** 29 October 2026 (+04:00). **Task:** `CIIFR-NODE-N02-FIXTURE-V14` / `LOCAL_WINDOWS_P1_QUALIFICATION.md`.  
**Executor:** local qualification agent `01429edb` (Windows 10/11 x64, Node v22.23.2).  
**Candidate:** draft PR #232 commit `d3fbd4041ef4434b4cf5b3c22459f06167be2729`; parent draft PR #226 `b2b695f66fc8dfc907f2b9a493b39bd4d4109570`; base at review `fd86b21aa9dcbfbbe4f8a1d26133b7e9779448be`.  
**Primary Issue:** [#229](https://github.com/reallakshman19/XML_Compare_Utilities/issues/229); **Linked Review:** [#228](https://github.com/reallakshman19/XML_Compare_Utilities/issues/228); **Parent WBS:** [#227](https://github.com/reallakshman19/XML_Compare_Utilities/issues/227).  
**Historical Continuity:** Historical returns and assessments remain immutable:
- R1 return: `P1-QUALIFICATION-WINDOWS-20261029` (`e46c5687a3854d4319c4fa06e415a7e1a88ff362`)
- Receiver review of R1: `P1-WINDOWS-RECEIVER-REVIEW-20261029` (`a8554897abcae1be5429e348138ed3f8846730b7`)
- R2 return: `P1-QUALIFICATION-WINDOWS-R2-20261029` (`dffe98513ddb938426e2a0068ee97a411280bf8e`)
- Prepared R3 package: `P1-WINDOWS-EXACT-CHECKS-R3-20261029` (`70978e35ca8a0a67678157b4c719bacb4801dce0`)

---

## 1. Executive Summary & Gate Disposition

- **Disposition:** **LOCAL R3 WINDOWS EXECUTION RETURN COMPLETE — GATE_R0 HOLD**.
- **WBS 2.1 (Engineering P1.1 / Browser Qualification & Native Regressions):** Complete with physical-oracle exact cell comparisons. All 6 cases pass under enforced harness assertions on Microsoft Edge and Google Chrome against product candidate `d3fbd4041ef4434b4cf5b3c22459f06167be2729`.
- **WBS 2.2 (Engineering P1.2 / Original-V14 Trial):** Remains **`ORIGINAL=NOT_RECEIVED / NOT_RUN`**. Awaiting authorized original V14 file locator and custody instructions from Owner.
- **GATE_R0 HOLD Maintained:** Strict read-only qualification. PR #232 and PR #226 remain unmerged draft PRs. No property-writing authority, no oracle tampering, no merge, no deployment, and no release promotion.

---

## 2. WH2 R3 Resolution — Physical Oracle & Complete Cell Comparisons

In R2, element and attachment columns used substring matching, which could permit false positives like pressure `130` for `30` or `Pointer 10` for `Pointer 1`. The R3 package resolves this with complete cell comparisons to independently decoded physical raw tokens and byte spans (`physical-oracle.json`):

1. **Exact Element Cell & Span Comparisons:**
   - Evaluates rendered table cells against `physical-oracle.json`:
     - Forward 400→500: Ordinal `1`, `400 → 500`, `T1 stored raw` = `TEMPERATURE_1_STORED: 200 [bytes 466–479]`, `P1 stored raw` = `PRESSURE_1_STORED: 30 [bytes 591–604]`, `Fluid density stored raw` = `FLUID_DENSITY_STORED: 1.01 [bytes 768–781]`, `Qualification` = `HOLD: effective process semantics / identity not qualified`.
     - Forward 500→600: Ordinal `2`, `500 → 600`, `T1 stored raw` = `TEMPERATURE_1_STORED: 180 [bytes 1696–1709]`, `P1 stored raw` = `PRESSURE_1_STORED: 20 [bytes 1821–1834]`, `Fluid density stored raw` = `FLUID_DENSITY_STORED: 1.01 [bytes 1998–2011]`, `Qualification` = `HOLD: effective process semantics / identity not qualified`.
     - Reverse 500→400: asserts exactly `0 element(s)` found.
   - Guard test suite (`qualification-guards.test.mjs`): **23/23 PASS**; `receiver-probes-r2-r3.mjs` confirms pressure `130` and pointer `10` are strictly rejected by R3 guards.
2. **Exact Node 500 Attachment Row Matching:**
   - Evaluates every attachment row against expected ownership, pointer, slot, and specification:
     - RESTRANT: `["RESTRANT", "1", "Pointer 1 · Slot 1", "Type 1 · CNode 0 · semantics partial"]`
     - DISPLMNT: `["DISPLMNT", "1", "Pointer 1 · Specification 1", "Vectors/cases not yet qualified"]`
     - FORCMNT: `["FORCMNT", "1", "Pointer 1 · Specification 1", "Input loads only; not computed reactions"]`
     - RIGID: `["RIGID", "1", "Pointer 1", "Weight raw 100 · element-owned, semantics partial"]`
3. **Reported Field Numbers & Raw Witnesses:**
   - Extracted directly from validated rendered DOM cells into `browser_qualification_report.json` with exact lexemes and byte spans.

---

## 3. Live Windows Browser Qualification Execution Summary

Both browsers executed against `http://127.0.0.1:8765/docs/cii-fnr-vnext.html` on Windows 10/11 x64:

| Browser | Version | Cases 1–6 Result | Served Module Match | Page Exceptions | Console Errors | Network Leaks |
|---|---|---|---|---|---|---|
| **Microsoft Edge** | `156.0.4314.42` | **6 / 6 PASS** | 13 / 13 MATCH | 0 | 0 | 0 |
| **Google Chrome** | `156.0.8078.48` | **6 / 6 PASS** | 13 / 13 MATCH | 0 | 0 | 0 |

- **Case 1 (Normal Demo):** TARGET1 validated in memory, applied to new copy preview, target1Hash `4bf7f868eda840cb45af6febfc2174a7ddfc2c21fb921be3cf411d3122bd7591`.
- **Case 2 (Property Isolation):** Normal proposal decisions (`s[0]=APPROVED`, `s[1]=REJECTED`) and Nodal hash/export state preserved across Property Transfer visits.
- **Case 3 (Pending-CSV Delay):** Pre-mutation applied state verified, immediate revocation on rule edit verified, active in-flight pending delay verified (`delayActive=true`, `delayPending=true`, `hasResolver=true`), revocation while pending verified, clear-while-pending verified, fresh delayed load completed and restored export eligibility.
- **Case 4 (Physical Oracle & Process Ownership):** Exact physical cell, span, and attachment row assertions verified.
- **Case 5 (Challenges):** UI search negative/zero, file intake negative/zero, pointer out-of-bounds, and dormant restraint residue UNKNOWN evidence verified. Zero Apply/Export buttons in Property Transfer.
- **Case 6 (Error-Free & Immutability):** 0 uncaught exceptions, 0 console errors, 0 network leaks, synthetic fixture byte immutability verified.

---

## 4. Native Regressions Status

- Required three (`required-three.tap`): `17/17 PASS`
- Repair additions (`repair.tap`): `13/13 PASS`
- Geometry authority (`geometry.tap`): `9/9 PASS`
- Guard tests (`guard-tests.tap`): `23/23 PASS`
- Complete VNext suite (`vnext-all-complete.tap`): **`123 PASS / 1 FAIL`** (inherited whole-suite branch-scope assertion failure at `tests/cii-fnr-vnext-branch-scope.test.mjs:81:1` disclosed and preserved; whole-suite status remains `FAIL/RED`).

---

## 5. Artifact Custody & Integrity

All members staged under `relay/AGENT_WORK/CIIFR-Node/CIIFR-NODE-WBS-P0-20261028/returns/P1-QUALIFICATION-WINDOWS-R3-20261029/`:
- `ARTIFACT_MANIFEST.json`: Catalog of all member sizes and SHA-256 hashes.
- `receipt.md`: This document.
- `payload/browser_qualification_report.json`: Live test execution report for Edge and Chrome.
- `payload/run_qualification_browser.mjs`: R3 qualification runner.
- `payload/qualification-guards.mjs`: Exact qualification guards module.
- `payload/qualification-guards.test.mjs`: Native test suite for exact guards (23 tests).
- `payload/physical-oracle.json`: Decoded physical oracle.
- `payload/receiver-probes-r2-r3.mjs`: Probe script demonstrating false positive rejection.
- `payload/panel-integration.mjs`: Native panel DOM integration script.
- `payload/fixtures/`: Canonical CRLF fixtures (`SYNTH_V14_SOURCE.cii`, `SYNTH_V14_TARGET0.cii`, `.gitattributes`).
- `payload/evidence/`: TAP logs, `environment.json`, `source-verification.json`, `served-source-verification.json`, `fixture-verification.json`.

Private screenshots (`*.png`), user data profiles, and local paths remain private on the Windows machine.
