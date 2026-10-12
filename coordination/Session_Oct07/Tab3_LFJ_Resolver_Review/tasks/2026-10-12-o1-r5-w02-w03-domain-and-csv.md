# O1 R5 — W02 native source/domain integration and W03 original CSV presentation

**Status as of 2026-10-12:** W02 PARTIAL; W03 PARTIAL. Not owner-approved O1 acceptance. Chat `6acc44e0`. Engineering-critical AIM v2.1.0 label_sha `d3ecd06`. [Owning issue #226](https://github.com/reallakshman19/3D_Converters/issues/226) / [R5 plan](https://github.com/reallakshman19/3D_Converters/issues/226#issuecomment-6116914701) / [G1 BuddyRunner final response 2](https://github.com/reallakshman19/3D_Converters/issues/226#issuecomment-6116816559).

## Authority and code identity
- Application original unmodified main `4f14beb37bc0b719453c52a116c1c5d7183d2fd0`.
- Product DRAFT PR [#228](https://github.com/reallakshman19/3D_Converters/pull/228) direct-main branch `lfj/226-t3-main-worker-intake-20261012` exact tested HEAD `6ea536b80e7f5ecdb21b581ac09c6563bfd9e335`; not merged/deployed. Source Worker existing LFJ tokenizer and R10 intake reused, not rewritten; no patch to old main-thread resolver.
- [Exact HEAD hosted Chromium #38199900461](https://github.com/reallakshman19/3D_Converters/actions/runs/38199900461), focused workflow **GREEN**, [artifact #11724794402](https://github.com/reallakshman19/3D_Converters/actions/runs/38199900461/artifacts/11724794402), ZIP exact digest sha256 `fd11fcabed1a22c381ab8d881a41ec5006d47ba5e1b039df79836e586bca727b`. Independently downloaded the ZIP and checked both actual CSV SHA256s against the browser manifest.

## W02 — source/domain bridge (PARTIAL)
1. Added `lfj/storage/browser/indexed-page-record-store.mjs`: **one real IndexedDB put/transaction per bounded 1024-event page**, durable committed-head CAS, strict source identity, source-only rights, abort/rollback, bounded `readOrdered`, `lookupCommittedPair` OPEN+SEAL, selected-result range API. Existing `lfj/` tokenizer and Worker unchanged. `xml-cii-adapted-lfj-o1-intake.js` opt-in now uses this page store and preserves original Blob + summary. No 32MiB limit; no fallback to legacy unbounded foreground parsing.
2. Authentic Firstpass `Benchmarks/1885Sjson/Sjson.json`: 733,806 B, sha256 `6b2c8b01ab0ba6ec8e9e7c42eb4a719668ffd2dc4dbe4790d27cf426a1f60288`, committed **23,754 original occurrences** at **1.65s source-only** vs previously **30.64s**, max rAF **16.8ms** (previous 33.4ms). Authentic NC `Benchmarks/1885_NC/1885_NC.json`: 10,232,634 B, sha256 `89f9c2ab7a9f1df15c1b9e1e0e30a8ca6c97ef994dcd56aec86c3a90f7d71646`, committed **328,156 original occurrences** after **22.8s** instead of 150s timeout, max rAF **16.8ms**. NC is **source-only negative / original XML source-kind mismatched**, NOT a proven positive XML match. Malformed input fails closed `EXPECTED_VALUE`.
3. Added independent `tabs/xml-cii-2019-standalone/workers/lfj-o1-resolver-domain-worker.mjs`, which calls the **existing** `runStandaloneResolverJsonTrace` + original CSV builders inside a native Worker; browser main thread never runs that old synchronous Build while opted-in. Added `ui-adapted/xml-cii-adapted-lfj-o1-domain-ui.js` to read exact committed root OPEN+SEAL and every selected `$.children[...]` JSON source path via original index, with source SHA/revision/job/XML content/config/scope fencing before any result/export, cancel on original replacement. No bare source-only receipt grants engineeringReady/output release.
4. Browser original Firstpass XML `Benchmarks/1885Sjson/FirstpassXML` 144,471 B sha256 `feee5a5a6399207337e63bc56c8afb001fe37ab30c6a7a9283333ec60f6eea38` + original JSON: **241 actual matched evidence source paths** found in native committed R05 OPEN index; **216 XML node rows**, **241 Evidence Tree rows**; source-path count/basis attested. Authored standalone Single UI, not synthetic detached model. An independently certified engineering semantic golden and negative wrong-XML branch/occurrence corpus remain NOT_PROVEN, so W02 AC still **PARTIAL**, not closed. Original SourceSession contract's `lookupCommittedPair` is satisfied in new page store but no claim that the complete generic `openSourceSession` is production-integrated.

## W03 — UI page/CSV and acceptance (PARTIAL)
1. Original authored Build/CSV buttons when O1 opt-in ON delegate to independent Worker, no synchronous legacy fallback. Paged native row viewer **64 rows maximum**, scoped status, cancel/replace invalidates, original two CSV builders reused from `xml-cii-trace-export.js` and transported as <=64KiB ACKed chunks. Source-only/engineering approval separate; no Preview/Weight changes.
2. Actual archived original outputs, not merely export button clicks; **downloaded real ZIP and verified exact CSV bytes and hash**:
   - `ValidationRecords/lfj-226-o1-node-original.csv` — 216 data rows, 57,945 bytes, UTF8 BOM, SHA256 `0d8bb4482ed4a9d0d116faeac5e68ce564f07b6bba2dd73dfc3676b72ec2eddc`
   - `ValidationRecords/lfj-226-o1-evidence-original.csv` — 241 rows, 50,399 bytes, UTF8 BOM, SHA256 `653485ff968bf478fa0001488432bb210a9ce6e85a901e9cc19f368f53a24809`
   - Browser source replacement negative `O1_EXPORT_SOURCE_STALE`, no prior-source CSV released; malformed input `EXPECTED_VALUE`.
3. **Critical failure despite focused CI green**: latest authentic Firstpass complete Build **134,803 ms**, maximum observed requestAnimationFrame gap **2,933.2 ms**. Prior exact-head [38199716807](https://github.com/reallakshman19/3D_Converters/actions/runs/38199716807) Build **69,085 ms**, max RAF **1,550ms**. Thus proposed **<=200ms longest frame gap fails even at 733,806B**, and consistency is poor. Pages/docs mirror NOT_RUN, 30/60/100MiB generated capacity/end-to-end NOT_RUN, beyond-range typed refusal not verified; cold/warm repeat, actual peak JS heap and independent semantic oracle not qualified. Hence overall O1 acceptance **0/3**, W03 **PARTIAL** even though all focused asserts PASS. No approved final operating range: D-AIM-2 remains Owner pending; 100 MiB/200 ms is **proposed, not approved**.
4. The 2.9s apparent main-frame gap may be caused by repeated 1-by-1 committed OPEN source reads in `auditSourcePaths` while the Worker domain/result is awaited, or rendering, source event loop scheduling; **not attributed conclusively**. W02 source-only scan max rAF 16.8ms shows bottleneck after index handoff. Need per-phase frame/wall tracing then an O(1) page-batched provenance check from real committed R05 (not all 23,754 one-by-one IDB get per event), with negative tamper/stale tests. Domain JSON parse and original matching still inside native Worker; avoid copying main-thread legacy parser.
5. O2/O3 remain separate workers per owner, existing Preview & Weight unchanged, no deep PR stack merges; C05 #203 broad release gates distinct from focused O1 checks, not used as pretext to block diagnosis.

## Honest task outcomes
- **TAB3-O1-W02** — PARTIAL: original source scan and Worker-domain matched path/trace proven via real authored UI, but independent original-value semantics oracle and full selection/source stale negatives not completely proven; source-path audit throughput may violate responsiveness. Not closed.
- **TAB3-O1-W03** — PARTIAL: complete 216/241 row original CSV files downloadable, 64-row page UI and replacement negative proven, but >200ms proposed rAF and large range unsupported, Owner range pending; not closed.
- **User actual benefit:** yes in the DRAFT browser app: Firstpass original XML+JSON produces usable source-linked trace and two files; no released/main/Pages user benefit. Source-index NC responsive; genuine NC XML join still distinct negative.
- **Next engineering:** collect phase-by-phase RAF/DOM/IDB and retain independent semantic golden, efficient page-batched path attestation plus 30/60/100MiB capacity/negative and fail-closed beyond-range, full docs/Pages parity; get D-AIM-2 Owner approved thresholds after evidence. Keep PR #228 draft until met.

```text
Task: TAB3-O1-W02
Goal (issue AC): Real committed OPEN+SEAL source/selected XML domain Worker matching
Status: PARTIAL
Met: partial
Done: Page-store 30.6->1.65s original Firstpass / NC 150s timeout->22.8s success, 241 committed paths attested; authored XML positive domain output
Code (repo branch @ commit | PR): reallakshman19/3D_Converters lfj/226-t3-main-worker-intake-20261012 @ 6ea536b80e7f5ecdb21b581ac09c6563bfd9e335 | #228 DRAFT
Tests (command -> pass/fail/skip): node scripts/lfj-226-o1-worker-intake-browser.mjs -> PASS; node scripts/lfj-226-o1-resolver-domain-browser.mjs -> PASS; independent semantic golden -> NOT_RUN
CI (run -> result): 38199900461 -> focused GREEN at exact head; comprehensive PR checks independent
Evidence (link): https://github.com/reallakshman19/3D_Converters/actions/runs/38199900461/artifacts/11724794402
AC (before -> after): NC IDB staged timeout and source-only Firstpass -> both committed, true selected XML trace source-path attested, independent engineering semantic correctness still pending
Claim: HOSTED_CI
Blocker: NONE for next implementation; OWNER:D-AIM-2 for final operating-range acceptance
Next: W02 independent semantic oracle/efficient source-path audit, W03 full-range performance
```

```text
Task: TAB3-O1-W03
Goal (issue AC): responsive paged trace and both source-attested complete original CSVs across agreed range
Status: PARTIAL
Met: partial
Done: Firstpass real original XML+JSON 216 node/241 evidence rows, 64 page, complete original CSV bytes+SHA, stale export negative; frame target FAILED 2933.2ms
Code (repo branch @ commit | PR): reallakshman19/3D_Converters lfj/226-t3-main-worker-intake-20261012 @ 6ea536b80e7f5ecdb21b581ac09c6563bfd9e335 | #228 DRAFT
Tests (command -> pass/fail/skip): node scripts/lfj-226-o1-resolver-domain-browser.mjs -> PASS (functional), proposed frame <=200ms -> FAIL; generated 30/60/100MiB and Pages -> NOT_RUN
CI (run -> result): 38199900461 -> GREEN focused functional checks, performance unqualified
Evidence (link): https://github.com/reallakshman19/3D_Converters/actions/runs/38199900461/artifacts/11724794402
AC (before -> after): no original domain CSV -> 216/241 real original downloadable rows but 134.8s wall/2933.2ms frame gap; user responsiveness remains NOT_MET
Claim: HOSTED_CI
Blocker: OWNER:D-AIM-2 final range policy, ENGINEERING:frame/staging/semantics validation
Next: performance profile source paths/IDB/DOM, independent oracle, generated capacity and Owner approval
```
