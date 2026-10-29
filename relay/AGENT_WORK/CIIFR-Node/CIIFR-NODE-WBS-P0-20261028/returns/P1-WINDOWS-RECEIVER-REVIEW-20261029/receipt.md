# CIIFR-Node — Windows return receiver assessment

**Date:** 29 October 2026 (+04:00). **Disposition: PARTIAL / EVIDENCE REPAIR REQUIRED.**

**Receiver:** current Owner-directed CIIFR contributor, chat ID UNKNOWN. The receiver authored PR232 repairs; this is evidence reconciliation, not independent product approval. Executor identity `01429edb` is supplied by the Owner's return. Separate account/host and blind independence are not independently established here.

**Candidate:** product PR232 `d3fbd4041ef4434b4cf5b3c22459f06167be2729`; parent PR226 `b2b695f66fc8dfc907f2b9a493b39bd4d4109570`. Both remain draft/unmerged. **Received artifact:** Common `e46c5687a3854d4319c4fa06e415a7e1a88ff362`, `returns/P1-QUALIFICATION-WINDOWS-20261029/` under this task. Primary native task [#229](https://github.com/reallakshman19/XML_Compare_Utilities/issues/229), linked review [#228](https://github.com/reallakshman19/XML_Compare_Utilities/issues/228), WBS [#227](https://github.com/reallakshman19/XML_Compare_Utilities/issues/227).

## Verified observations

The receiver retrieved all 12 manifest members and the manifest itself. Ten members match their declared byte length and SHA-256; the two copied CII fixtures do not. All actual member Git blob identities were verified, with the TAP-specific transport treatment below. The receipt, browser runner, structured report and JSON metadata match their declared identities. The14 source-verification entries all agree with the actual pinned candidate tree; these are executor-reported local measurements, not a receiver observation of that Windows disk.

All four native TAP logs match their declared exact bytes, hashes and Git blobs. The file connector decodes their UTF-16LE-with-BOM representation into UTF-8 even when base64 is requested. Re-encoding the received text as UTF-16LE exactly reproduces each independent expected Git SHA-1 and SHA-256. This is a verified transport reversal, not an artifact defect or a new test run. Results: required 17/17, repair 13/13, Geometry 9/9; full suite 123 PASS/1 FAIL, with the inherited branch-scope assertion retained. Whole-suite status remains FAIL.

The structured browser report contains two Windows runs, Edge 156.0.4314.42 and Chrome 156.0.8078.48. It records positive query and mutated-file outcomes, state/export observations, zero page exceptions and zero external page requests. These are now durable inspectable executor observations. The receiver did not run Edge/Chrome or inspect private screenshots. Native/backend evidence is not substituted for browser execution.

## WH1 — Two public fixture copies changed during relay

| Member | Declared/tested | Actual committed member | Actual SHA-256 |
|---|---|---|---|
| SOURCE.cii | 8276 bytes, CRLF, SHA `c8de516c54767c7cf7d5239d404810be891ed3d56ec2111db3dc4c2b07dcdb0b` | 8167 bytes,109 LF,0 CRLF | `d07bb0857093878f2c1374e19ddec67be6bad156e62c0bcdce4f4f2509e6a86d` |
| TARGET0.cii | 8276 bytes, CRLF, SHA `0bbc3b0a8b7b1e73d655d0a0ffc267e6a698dec5ff66763c468cdc835cc19661` | 8167 bytes,109 LF,0 CRLF | `d56eb9d87a27cf3ab9e4059bd0c87a583f0727975f3fb965761cbe9c07ae10ad` |

The returned Git blobs are `2366d12d67833debfe6497718fbc6fa9cfba53d4` and `32814b5650c9d3f8cc6e8c3b7d2cc3f19440ce61`, rather than the canonical original blobs `7d00c13f5c5906a9bb2dba53287f133c8db06358` and `dddf157895571802973b71904fbad0a679a7e271`. Replacing each LF with CRLF in a scratch comparison reproduces both canonical hashes. This identifies an exact newline-only delta; Git line-ending conversion is a plausible cause, not a proven observation of the producer's upload path. The receiver did not alter the committed files.

The runner checks the canonical CRLF hashes before starting; the committed copies therefore cannot serve as its expected fixtures unchanged. This does not disprove that the local browser run used correct private scratch copies. It does disprove the claim that all relayed members match the manifest.

The manifest itself is 2227 bytes, SHA-256 `e9f1227a8473a0be41012852be0dab5e8a49cfb87f1054e19d8db65be3b20bc6`, Git blob `2d9b8943abdbbc656d7faa80da32beb1a02d826c`. The public return instead declares 2122 bytes and SHA `66d0efea2df17c6e00b8577317789467645ef20ea8573229b4e7cecf4cb3d1ee`; that external manifest identity must be corrected too. Do not change the expected fixture hashes to bless converted files. Reuse the exact canonical public blobs or publish a byte-preserving correction, then measure the committed members.

## WH2 — Browser assertions do not enforce all qualification claims

The receiver inspected the actual runner SHA `8934bb53c0e8a4ca09abe598d8f8140cc088e554ece438ea060e10b989cad5db`. `probe-runner-verdicts.mjs` extracts its unchanged guard/verdict blocks and supplies contrary observations; this is a local Node probe of the harness only, not a simulated browser PASS or a product defect reproduction.

- Case 5 lines 858–873 assigns `status: 'PASS'` even when all six query/intake challenge booleans are false. The published JSON happens to contain true values; those observations remain evidence, but the exit/result policy must reject a failed challenge.
- Case 6 lines 884–920 does not reject late page exceptions or count/assert console errors. The probe produces PASS with `pageErrorsCount:1`. The published JSON records zero page exceptions, but contains no console-error count to substantiate that separate zero-error claim.
- Case 4 lines 673–679 prints pressure checks but only guards broad text occurrences of 200 and 180 plus the reverse-match text. Wrong pressure values pass this guard. Density and exact element/field/attachment owner/pointer/slot associations are not asserted. Presence of numbers/family labels across combined SOURCE/TARGET results is weaker than the planned field/ownership comparison.
- Case 2 lines 336–343 checks proposal row count, export eligibility and output hash for Normal; it does not compare decision values. Nodal checks output hash/export eligibility. Retain these measured claims, but qualify the receipt's broader '100% state preserved' claim or add explicit before/after decision assertions.
- Case 3 checks disabled controls and cleared claims, which is useful. It does not assert that the pre-delay applied state was established or that the delay hook was actually pending before the revocation checks. Assert those preconditions so an already-disabled state cannot satisfy the contrary case. The previous independent native direct-export probes remain separate valid evidence; no new browser direct-export proof is inferred.

The runner also does not hash served HTTP module responses against the pinned checkout. Bind the served files to that candidate when completing the planned exact-source browser claim. No new browser/engineering acceptance is inferred from a source-verification JSON file alone.

## Minimal continuation and gate disposition

**Next actor/action:** existing local qualification agent `01429edb` corrects the public fixture transport/manifest identity and completes the missing assertions or narrows unsupported claims. Retain this immutable historical return; publish a new corrected revision through the same Common task route. Repeat only affected browser checks with exact observed values, served source identity, actual delay/pre-state and explicit failed-check handling. Existing unchanged native suites need not be rerun merely to repair packaging/reporting.

Return the actual committed sizes/SHA-256 and readback observations on #229. One linked review return is sufficient; do not generate parallel WBS/assignments or edit product source. This assessment creates no agent dispatch or shared-branch product custody.

WBS 2.1 is **PARTIAL**, with native evidence verified and useful Windows browser observations preserved; the full claimed qualification is not yet accepted. Public canonical fixture receipt remains valid historically, but these two new copies fail exact-byte transfer. WBS 2.2 remains **ORIGINAL NOT_RECEIVED / NOT_RUN**. Owner-provided authorized private original inspection can proceed independently when custody is actually available; this packaging finding does not block unaffected read-only work. Private originals/paths/screenshots remain private. PR232/226 and GATE_R0 stay HOLD; no P2, property writer, merge, deployment or release promotion.
