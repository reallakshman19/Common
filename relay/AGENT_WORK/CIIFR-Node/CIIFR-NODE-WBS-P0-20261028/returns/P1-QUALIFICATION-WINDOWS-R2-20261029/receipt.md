# CIIFR-Node — Local Windows P1 Qualification Return (Revision 2)

**Date:** 29 October 2026 (+04:00). **Task:** `CIIFR-NODE-N02-FIXTURE-V14` / `LOCAL_WINDOWS_P1_QUALIFICATION.md`.  
**Executor:** local qualification agent `01429edb` (Windows 10/11 x64, Node v22.23.2).  
**Candidate:** draft PR #232 commit `d3fbd4041ef4434b4cf5b3c22459f06167be2729`; parent draft PR #226 `b2b695f66fc8dfc907f2b9a493b39bd4d4109570`; base at review `fd86b21aa9dcbfbbe4f8a1d26133b7e9779448be`.  
**Primary Issue:** [#229](https://github.com/reallakshman19/XML_Compare_Utilities/issues/229); **Linked Review:** [#228](https://github.com/reallakshman19/XML_Compare_Utilities/issues/228); **Parent WBS:** [#227](https://github.com/reallakshman19/XML_Compare_Utilities/issues/227).  
**Historical Continuity:** Historical R1 return `P1-QUALIFICATION-WINDOWS-20261029` at commit `e46c5687a3854d4319c4fa06e415a7e1a88ff362` and receiver assessment `P1-WINDOWS-RECEIVER-REVIEW-20261029` at commit `a8554897abcae1be5429e348138ed3f8846730b7` are fully retained. This Revision 2 (R2) package supplies the bounded local evidence correction requested by the Receiver.

---

## 1. Executive Summary & Gate Disposition

- **Disposition:** **LOCAL EVIDENCE RETURN COMPLETE — GATE_R0 HOLD**.
- **WBS 2.1 (Engineering P1.1 / Browser Qualification & Native Regressions):** Qualification evidence return complete and verified. All 6 browser cases strictly pass under enforced harness assertions on both Microsoft Edge and Google Chrome.
- **WBS 2.2 (Engineering P1.2 / Original-V14 Trial):** Remains **`ORIGINAL=NOT_RECEIVED / NOT_RUN`**. Awaiting authorized original V14 file locator and custody instructions from Owner.
- **GATE_R0 HOLD Maintained:** Strict read-only qualification. PR #232 and PR #226 remain unmerged draft PRs. No property-writing authority, no oracle tampering, no merge, no deployment, and no release promotion.

---

## 2. WH1 Resolution — Canonical Public Fixture Transport & Manifest Identity

In the R1 return, Windows Git `core.autocrlf true` converted public fixtures into 8,167-byte LF files upon commit. In this R2 return:
1. `core.autocrlf false` is configured locally for the Common repository, and `*.cii binary` is explicitly pinned in `.gitattributes`.
2. Exact canonical 8,276-byte CRLF fixtures are restored, and their Git blob identities are verified:
   - `SYNTH_V14_SOURCE.cii`: 8,276 bytes, CRLF, SHA-256 `c8de516c54767c7cf7d5239d404810be891ed3d56ec2111db3dc4c2b07dcdb0b`, Git blob `7d00c13f5c5906a9bb2dba53287f133c8db06358`.
   - `SYNTH_V14_TARGET0.cii`: 8,276 bytes, CRLF, SHA-256 `0bbc3b0a8b7b1e73d655d0a0ffc267e6a698dec5ff66763c468cdc835cc19661`, Git blob `dddf157895571802973b71904fbad0a679a7e271`.
3. `ARTIFACT_MANIFEST.json` is generated directly from physical file measurements and read back, recording exact byte lengths and SHA-256 hashes for all members.

---

## 3. WH2 Resolution — Harness Assertions Strengthened & Enforced

All weaknesses identified in the Receiver's `receipt.md` and `probe-runner-verdicts.mjs` have been resolved in `run_qualification_browser.mjs`:

1. **Served HTTP Module Integrity:**
   - Prior to browser test execution, the runner fetches all 13 served HTTP modules from `http://127.0.0.1:8765/` and asserts that their SHA-256 hashes and Git blob hashes match the disk candidate tree (`CIIFR-Node-P12-20261029-152402`) with 100% agreement.
2. **Case 2 Proposal Decision Values:**
   - Before visiting Property Transfer, individual proposal decision values in Normal are recorded (`[ { id: "rule-10:...", value: "APPROVED" }, { id: "rule-11:...", value: "REJECTED" } ]`).
   - After returning from Property Transfer, the runner strictly asserts that every proposal decision value matches the pre-visit state exactly (`assert.deepStrictEqual`), confirming zero state loss across tab navigation.
3. **Case 3 Precondition & Pending-CSV Controlled Delay:**
   - Pre-mutation applied state is strictly asserted (`exportDisabled === false`, `proposalsCount > 0`).
   - Immediate authority revocation on rule edit is verified (`exportDisabled === true`, `proposalsCount === 0`).
   - Normal applied state is re-established before delay testing.
   - Delay hook explicitly records and asserts active in-flight pending state (`delayActive === true`, `delayPending === true`, `hasResolver === true`).
   - Authority revocation while read is actively pending is strictly asserted (`exportDisabled === true`, `applyDisabled === true`, `validateDisabled === true`, `claimsCount === 0`).
   - Clear while pending is verified (delayed read does not overwrite state upon late promise resolution).
   - Fresh delayed read completes cleanly and restores export eligibility upon re-approval.
4. **Case 4 Process Ownership, Reverse Orientation & Attachments:**
   - Structured table row parsing asserts exact field values:
     - Forward 400→500: Ordinal `1`, FromTo `400 → 500`, `T1 stored raw` includes `200`, `P1 stored raw` includes `30`, `Fluid density stored raw` includes `1.01`, `Qualification` includes `HOLD`.
     - Forward 500→600: Ordinal `2`, FromTo `500 → 600`, `T1 stored raw` includes `180`, `P1 stored raw` includes `20`, `Fluid density stored raw` includes `1.01`, `Qualification` includes `HOLD`.
     - Reverse 500→400: strictly asserts `0 element(s)` found.
     - Node 500 attachments: strictly parses table rows for RESTRANT (owner 1, pointer 1, slot 1, type 1, cnode 0), DISPLMNT (owner 1, pointer 1, spec 1), FORCMNT (owner 1, pointer 1, spec 1), and RIGID (owner 1, pointer 1, weight raw 100).
   - Guard blocks reject contrary pressure or density values (`case4WrongPressureRejected: true`).
5. **Case 5 Challenge Enforcement:**
   - Enforcing assertions throw immediately if any of the 6 security/validation challenges fail: UI search negative endpoint (`PROPERTY_NODE_NOT_CANONICAL`), UI search zero endpoint (`PROPERTY_NODE_INVALID`), file intake negative endpoint (`PROPERTY_ELEMENT_ENDPOINT_NEGATIVE`), file intake zero endpoint (`PROPERTY_ELEMENT_ZERO_ENDPOINT_UNQUALIFIED`), pointer beyond CONTROL (`PROPERTY_POINTER_RANGE_BEND`), and dormant restraint residue reporting UNKNOWN evidence (`PROPERTY_RESTRAINT_DORMANT_RESIDUE`).
   - Confirms Property Transfer DOM exposes no Apply or Export controls (`noApplyOrExportInProperty: true`).
   - Verified against receiver-style contrary probe (`case5FailedChallengesRejected: true`).
6. **Case 6 Console & Page Error Enforcement:**
   - Strictly asserts `session.pageErrors.length === 0` and `consoleErrors.length === 0`.
   - Verified against receiver-style contrary probe (`case6LateExceptionRejected: true`, `case6ConsoleErrorRejected: true`).
   - Re-verifies synthetic fixtures on disk are byte-identical before and after run (`match === true`).
   - Strictly asserts zero external network requests (`externalRequestsCount === 0`).

---

## 4. Native Regressions Status (Unchanged Verification)

As verified by Receiver in `receipt.md`, native TAP logs match canonical hashes:
- `required-three.tap`: 17 tests, 17 pass, 0 fail (`17/17 PASS`).
- `repair.tap`: 13 tests, 13 pass, 0 fail (`13/13 PASS`).
- `geometry.tap`: 9 tests, 9 pass, 0 fail (`9/9 PASS`).
- `vnext-all-complete.tap`: 124 tests, 123 pass, 1 fail (`FAIL/RED`).
  - Inherited branch-scope failure at `tests/cii-fnr-vnext-branch-scope.test.mjs:81:1` (`AssertionError: 1 !== 0`) disclosed and preserved without modification or greenwashing.

---

## 5. Live Windows Browser Qualification Execution Summary

Both browsers executed against `http://127.0.0.1:8765/docs/cii-fnr-vnext.html` on Windows:

| Browser | Version | Cases 1–6 Result | Served Module Match | Page Exceptions | Console Errors | Network Leaks |
|---|---|---|---|---|---|---|
| **Microsoft Edge** | `156.0.4314.42` | **6 / 6 PASS** | 13 / 13 MATCH | 0 | 0 | 0 |
| **Google Chrome** | `156.0.8078.48` | **6 / 6 PASS** | 13 / 13 MATCH | 0 | 0 | 0 |

---

## 6. Artifact Custody & Integrity

All members staged under `relay/AGENT_WORK/CIIFR-Node/CIIFR-NODE-WBS-P0-20261028/returns/P1-QUALIFICATION-WINDOWS-R2-20261029/`:
- `ARTIFACT_MANIFEST.json`: Complete catalog of member sizes and SHA-256 hashes.
- `receipt.md`: This document.
- `payload/run_qualification_browser.mjs`: Strengthened qualification runner.
- `payload/browser_qualification_report.json`: Live test execution report for Edge and Chrome.
- `payload/fixtures/`: Canonical CRLF fixtures (`SYNTH_V14_SOURCE.cii`, `SYNTH_V14_TARGET0.cii`, `.gitattributes`).
- `payload/evidence/`: Native TAP logs (`required-three.tap`, `repair.tap`, `geometry.tap`, `vnext-all-complete.tap`), `environment.json`, `source-verification.json`, `served-source-verification.json`, `fixture-verification.json`.

Private screenshots (`*.png`), user data profiles, and local paths remain private on the Windows machine.
