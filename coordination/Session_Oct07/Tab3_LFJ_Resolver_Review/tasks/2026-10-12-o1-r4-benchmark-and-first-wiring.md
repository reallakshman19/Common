Outcome: O1
For the user: Nothing proven yet. The original app remains unchanged on main; a direct-main draft now exposes opt-in source-only native LFJ indexing in the real standalone JSON input, not final matching/CSV.
Proof: Diagnostic PR [#227](https://github.com/reallakshman19/3D_Converters/pull/227), first artifact [run 38191541433](https://github.com/reallakshman19/3D_Converters/actions/runs/38191541433/artifacts/11721599743) with all five UI cases failing **before** JSON ingestion; corrected Single-mode main browser run [38193362714](https://github.com/reallakshman19/3D_Converters/actions/runs/38193362714) in progress when this record was written; new partial product wiring draft [#228](https://github.com/reallakshman19/3D_Converters/pull/228) and exact-head Chromium proof [38193374330](https://github.com/reallakshman19/3D_Converters/actions/runs/38193374330) in progress at writing. Neither is represented as PASS O1.

# #226 T1 measured baseline / T3 source-Worker wiring — R4
Date 2026-10-12; chat 6acc2f08, Owner aim STICKY v1.1.0 label_sha 9c35909; critical. Baseline `reallakshman19/3D_Converters main@4f14beb37bc0b719453c52a116c1c5d7183d2fd0` unchanged. T2 prior source map DONE; T1 NOT YET END-TO-END QUALIFIED; T3 STARTED partial and draft.

## Actual 38191541433 result vs green CI check
The benchmark's Node runner exited success but each real Chromium app case stopped before uploading the JSON because a wrong UI-readiness assertion waited 90 s on an absent XML-loaded badge. A follow-on green workflow 38192934136 also contained **five** wrong-input/panel assertions, this time 10 s each, before JSON ingestion. These are NOT a large JSON performance curve, and no acceptable longest-freeze/operating size can be deduced.

| Intended input | Original bytes | Original/XML pairing | Actual 38191541433 stage | Stage wall ms | Observed peak JS heap bytes (sample) | Max observed aggregate Chromium RSS KiB (proxy) | Longest rAF gap ms | Correctness |
|---|---:|---|---|---:|---:|---:|---:|---|
| Firstpass real | 733806 | FirstpassXML 144471 B | wrong XML badge wait, JSON never opened | 90010 | 26258008 | 527268 | 150.0 | NOT_RUN JSON |
| NC real negative | 10232634 | topology.input.xml 1067628 B | wrong XML badge wait, JSON never opened | 90007 | 35627776 | 574668 | 183.3 | NOT_RUN JSON |
| Generated ~30 MiB | 30819769 | FirstpassXML reference only | wrong XML badge wait | 90007 | 22620860 | 532232 | 133.3 | CAPACITY_ONLY; NOT_RUN JSON |
| Generated ~60 MiB | 62373341 | FirstpassXML reference only | wrong XML badge wait | 90005 | 26280900 | 533764 | 133.3 | CAPACITY_ONLY; NOT_RUN JSON |
| Generated ~100 MiB | 104200169 | FirstpassXML reference only | wrong XML badge wait | 90009 | 26376828 | 533572 | 150.0 | CAPACITY_ONLY; NOT_RUN JSON |

These samples are from idle/UI navigation and a failed element-readiness wait. They are not true peak memory (CDP periodic sample, aggregate RSS is multiple Chromium processes) and not large-JSON upload, trace or export frame gaps. Do not use to approve 100 MiB or 200 ms. Firstpass generated repeats duplicate root identity; never a positive matching oracle. Real NC source metadata sha blob 9ac18595..., Firstpass Git blob f3400dc9..., previously recorded. Source SHA per browser runner recorded only for generated/original file inventory.

## Corrective benchmark runs
- First FAIL #38191487161: insufficient shallow ancestry, before browser.
- #38191541433 GREEN workflow but 5/5 case stages FAIL due incorrect Single-versus-Mode-A badge. Source JSON not uploaded.
- #38192824278 FAIL before browser: invalid regex in one test-only assertion; corrected.
- #38192934136 GREEN workflow but 5/5 cases FAIL (Mode-A control absent because app defaults to Single); source JSON not uploaded.
- #38193156645 FAIL before browser because git merge-base lost ancestor with shallow fetch.
- New exact-main test-only #227 head at checkpoint 3998af7 then 2f54d14→f60d577 uses full checkout and correct default Single `data-field="staged-json-file"` input, real XML source, actual Build+CSV, memory/rAF instrumentation. Run 38193362714 active. Do not claim its results before reading artifact.
- Restore source/main approach only, no benchmark fixture modified, tests are diagnostic not a product deliverable.

## T3 product start, scope and source gate
New draft PR #228 direct main, branch `lfj/226-t3-main-worker-intake-20261012`; no stack inheritance, no 32MiB cap. Only existing code edited: two-line opt-in call in actual shipped `xml-cii-adapted-workflow-shell-mode-a-easy-bulk-v6.js` (pre-edit exact content backed up in agents/backups). New `xml-cii-adapted-lfj-o1-intake.js` binds BOTH actual Single/Mode-A staged JSON inputs behind unchecked opt-in; existing behavior unchanged without explicit opt-in. It sends original File/Blob to main LFJ genuine `source-browser-worker.mjs` R10; asynchronously pages provisional OPEN/SEAL to main LFJ `indexed-record-store.mjs` R07 with one ACK after each durable staging; requires exact source hash/revision/identity, complete OPEN/SEAL census and successful committed head before showing source index. Supersession aborts and deletes transient db; malformed source or native Worker failure fails closed. Raw source facts DO NOT authorize final trace/CSV or engineering content; opt-in Build/CSV clicks blocked until full consumer bridge qualified. **User workflow improvement NOT_PROVEN until exact-head browser proof; matching/XML source value/CSV still outstanding.**
- New Playwright 50-line test loads actual rendered standalone UI, Firstpass original, NC original negative and invalid JSON, with SHA prefixes compared against independent Node oracle, frame gap; hosted CI started with #228. Browser result still pending at writing.
- Scope intentionally first vertical integration: no reconstruction of core tokenizer/index, no legacy algorithm patch, no 37-stack branch, no merge/close/rebase, no Owner 32MiB cap. Further T3 needed to bind committed source index into actual resolver matching/output and original two CSV parity with source-path ownership.

## Operating range / Owner approval
Propose validation matrix from actual original files rather than selecting a single Owner 30MiB: Firstpass 0.70MiB genuine positive + original XML, NC 9.76MiB genuine negative + original XML, generated capacity-only 30 / 60 / 100MiB. ***Do not propose an accepted largest file or freeze limit until actual JSON-through-UI measurements from 38193362714 are read***. Candidate policy after evidence: measured threshold must be at least representative 10MiB, optionally 100MiB if demonstrated; beyond Owner bound typed recoverable fail BEFORE any full main-thread file read, never silent sync fallback; cancellation and source SHA/occurrence integrity mandatory. 200ms prior threshold merely proposal, no acceptance.

## Future exact next steps
1. Fetch 38193362714 artifact, validate actual JSON stage reached for every intended case and extract per-file stage timings/max rAF/renderer observed peak/RSS, compare failure vs capacity, propose concrete Owner size+freeze/overrange; reject any fake-green CI. Record acceptance status clearly.
2. Fetch #228 exact-head browser result, fix any genuine O1 source index failure at same PR head, rerun; prove real File/Blob and original SHA, no sync parsing, no premature CSV.
3. Follow-on direct-main small wiring to committed selection/page to actual XML matching + two CSVs, real input and source-authority negative, Owner decision if additional source-bounded hashing or retention budgets required.

Workpack: T1 IN_PROGRESS, T2 DONE, T3 IN_PROGRESS partial. O1/O2/O3 0/3 independently met; no deployed source. PR #227 test-only draft / #228 product draft direct main.

## Final T1 measured evidence, Owner decision D-AIM-2, T3 first CI — 12 Oct 2026
Outcome: O1
For the user: Nothing released; real main's large-JSON trace hangs, and draft worker intake is not a complete trace/CSV.
Proof: [actual T1 run 38193362714 and artifact 11721934084](https://github.com/reallakshman19/3D_Converters/actions/runs/38193362714/artifacts/11721934084); [NC correction 38193975925](https://github.com/reallakshman19/3D_Converters/actions/runs/38193975925); [T3 Chromium 38193622267](https://github.com/reallakshman19/3D_Converters/actions/runs/38193622267).

### Chromium 136, single run per input, real main code @4f14beb
| JSON | Original bytes | JSON upload ms | Build attempt ms | max main rAF gap ms | sampled max renderer JS heap B | sampled max aggregate Chromium RSS KiB | actual trace |
|---|---:|---:|---:|---:|---:|---:|---|
| Firstpass original positive | 733806 | 286 | 31017 | 950.0 | 28297188 | 597976 | FAILED trace timeout |
| NC original negative | 10232634 | NOT_RUN | NOT_RUN | 200.0 *navigation only* | 20750224 *preupload* | 531620 *preupload* | BLOCKED before JSON upload |
| Firstpass-shaped generated ~30MiB | 30819769 | 5087 | 49323 | 19249.3 | 239589260 | 852916 | FAILED trace timeout |
| Firstpass-shaped generated ~60MiB | 62373341 | 9602 | 67503 | 37431.8 | 328369336 | 908576 | FAILED trace timeout |
| Firstpass-shaped generated ~100MiB | 104200169 | 14938 | 89892 | 59814.3 | 471596288 | 1128848 | FAILED trace timeout |

Derived from LFJ226_CASE records in job 114630672152. Stated maxima refer to sampling, *not actual physical memory peaks*. Generated JSON repeats original Firstpass structures/identities: syntax and capacity only, NEVER an engineering golden. NC original topology XML fails transition to JSON Trace. NC-only attempted correction run 38193975925 also returned status success while the case failed on missing staged-json-file input after XML load (10,231ms), so NO NC JSON ingestion performance proof. CI success is not product PASS.

### Owner approval requested: operating range NOT ACCEPTED YET
Propose target support **up to 100 MiB (104857600 bytes) original JSON**. Representative original positive Firstpass 733806B + paired FirstpassXML, distinct real negative NC 10232634B + its original topology XML (must resolve navigation/source-mode compatibility first), plus generated 30/60/100 MiB stress cases only. Proposed longest acceptable foreground freeze: **200ms maximum rAF gap**, measured throughout File->Worker index->matched trace->render->CSV/cancel; none of the presently measured true-trace cases passes, not even Firstpass. Beyond 100 MiB, fail fast with typed recoverable capacity refusal *before full UI FileReader/JSON.parse*, allow replace/cancel and no synchronous fallback. 100 MiB / 200ms are engineering **proposals** needing Owner confirmation and positive output proof; do not apply old PR #180's 32 MiB cap.

### T3 actual product wiring state
Main-based draft PR #228 @bb7a78d invokes existing main LFJ native R10 source worker + durable R07 indexed store from real default Single and Mode-A staged JSON file controls on explicit opt-in. Source-only complete positive Firstpass measured 733806B, 23754 source occurrences, exact independently checked SHA256 6b2c8b01ab0ba6ec8e9e7c42eb4a719668ffd2dc4dbe4790d27cf426a1f60288, 18.9s elapsed and 16.8ms max rAF gap after 1024-event page batching. Yet exact-head run 38193622267 **FAIL** on NC distinct source receipt waiting 180s; malformed negative was not reached. NC stall diagnosis UNKNOWN, requires source-page/IDB timing instrumentation before changing semantics. Raw source index is not XML matching and must not grant either CSV export or engineering rights. App main unchanged, historical stack unmodified.
T1 COMPLETE **as failure characterization**: four valid JSON-upload curves, NC source case explicitly UNMEASURED (acceptance gap); T2 read-only DONE; T3 WIP / blocked red NC; O1/O2/O3 all NOT_ACCEPTED, 0/3, user NO.
