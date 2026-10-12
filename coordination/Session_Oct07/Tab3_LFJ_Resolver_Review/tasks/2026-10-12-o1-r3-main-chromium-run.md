# Tab3 / #226 R3 — Owner answers and exact-main O1 benchmark
Owner instructions 12 Oct; chat=6acc2f08, aim=v1.1.0 label_sha 9c35909, engineering-critical. This is a live checkpoint, not a passed benchmark or acceptance.

Outcome: O1
For the user: Nothing yet; no product code changed, no public/deployed app change.
Proof: [Diagnostic draft PR #227](https://github.com/reallakshman19/3D_Converters/pull/227) source base main 4f14beb37bc0b719453c52a116c1c5d7183d2fd0, test-only exact-head 85909672cccb0ff2d3c91d13b3481e8c0f8ef46d and hosted [Chromium run #38191541433](https://github.com/reallakshman19/3D_Converters/actions/runs/38191541433); **running, not a verified result at this checkpoint**.

## Owner decisions applied
- D-AIM-2 clarified task architecture: core is ALREADY BUILT on main (`lfj/tokenizer`, `lfj/index`, `lfj/ports/source-worker-port.mjs`, `lfj/runtime`, `lfj/storage`); T3 means **wire this existing core into the real standalone large-JSON UI path and test**, not build a new engine. Owner STILL decides accepted max size, representative positive cases, freeze tolerance, beyond-range action, based on T1 Chromium measurements proposed by this agent.
- D-T1-RUNNER APPROVED one focused Chromium test. PR #227 implements diagnostic-only harness; base pinned to main as of 12 Oct and branch compared three new files ONLY (`tests/browser/lfj-226-main-baseline.html`, `scripts/lfj-226-main-chromium-baseline.mjs`, `.github/workflows/lfj-226-main-chromium-baseline.yml`). No app file or fixture altered.
- D-AIM-3 salvage: **approved selectively, only if required** for wiring on fresh shallow PRs directly against main; #182 bounded SHA and #183 retention budget patterns may be reused as needed, NOT #180 fixed 32MiB limit. Do not merge/rebase/close historical stack; no more than two stacked PRs; maintain exact-head Chromium proof for each new PR. The repo and Owner approval NOT interpreted as permission to compromise original source identity/trace semantics.

## Test measurement design and caveats
- Actual production module mounted through `renderXmlCii2019StandaloneTab` in Chromium; real File input/Build button/CSV actions, not a fake JSON.parse-only surrogate. Tests **Firstpass JSON 733806 B and paired XML 144471 B**, **NC negative JSON 10232634 B and paired XML 1067628 B**, plus **generated 30/60/100 MiB valid Firstpass-shaped duplicate-root JSON** for CAPACITY/FREEZE only. Original-byte SHA included, no synthetic root engineering assertion.
- Measure stage wall times: authored navigation, original XML File upload, JSON File upload, Build + rendered trace; if possible download real Node and Evidence CSV and original SHA. Start in-page rAF heartbeat before stage, end after rendering; record observed max frame gap and frame count. Sample renderer JS heap through CDP and aggregate Chromium RSS proxy (not exact peak or unique memory, report limitation). Persist complete per-case JSON and errors even when the app fails/timeout/crashes, attach Actions artifact.
- First attempt #38191487161 failed **before Chromium** because shallow Git checkout prevented merge-base ancestry; fixed checkout fetch-depth in exact-head 85909672 without product changes. Current workflow #38191541433 must be inspected; failures NOT invented away.

## T3 shortest revised wiring (after T1)
1. Trace shipped UI path source File→readTextFile→stagedJsonText→synchronous `runStandaloneResolverJsonTrace` and identify needed consumer surface. Make a **new independently testable integration boundary** binding original Blob and job/revision/scope to main LFJ source-Worker port + committed source index/query/storage. Reuse production main core, never reimplement tokenization or hash algorithm.
2. Off-thread scan → bounded ACK/progress → committed trustworthy index → selected exact original occurrence trace/CSV; preserve independent original byte hash and source-path provenance, prevent provisional pages from granting export/Preview permissions; fail closed on stale selection/abort. Do not quietly use main-thread legacy JSON fallback.
3. Each product PR small, direct-main, original Firstpass + NC negative + generated size Chromium proof; no change to O2 Preview or O3 review here. #182 incremental SHA and #183 retention counters only if T1/engineering source review proves necessity, no fixed 32MiB from #180.

## Watch/not-now
- Specific authentic 30MiB hunt is not an O1 architectural prerequisite; real Firstpass positive and NC negative plus generated size profile used now, mark synthetic identity limits.
- C05 #203 unrelated failing families are not prerequisite to capturing O1 baseline; must not waive required release CI or transfer PR-head CI.
- Source authority matters precisely to trace correctness (original bytes/path/occurrence/selection); unrelated governance gates not introduced.
- Report is not product benefit; T1 actual measured artifact then T3 product wiring is shortest aim path.

Status: T1 IN_PROGRESS; T2 prior read-only DONE; T3 NOT_STARTED; O1/O2/O3 user acceptance 0/3; no merge, rebase, close or release. Next check exact job logs/artifact and propose Owner operating range grounded in measured results.
