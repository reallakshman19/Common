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
