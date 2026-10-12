# #226 O1 / T1 — main-first large-JSON baseline (PARTIAL)
Date: 2026-10-12, Asia/Muscat | chat=new (replaces 6acbbb58) | plan R1 | engineering-critical.
Issue: https://github.com/reallakshman19/3D_Converters/issues/226
Application baseline: reallakshman19/3D_Converters main 4f14beb37bc0b719453c52a116c1c5d7183d2fd0. Common/main original at start: 9392f497fe6acd1c61213a840bc455acf58153ab.

Outcome: O1
For the user: Nothing yet; no deployed or draft product changes.
Proof: Re-fetched #226 complete body/no comments; source tree, original Firstpass blob, main event path, and below surrogate parse-only observations. **No application browser, memory or freeze evidence claimed.**

## Real source inventory at exact main
| Case | JSON | Git blob | Size bytes | Paired XML bytes | Role |
|---|---|---|---:|---:|---|
| Firstpass | Benchmarks/1885Sjson/Sjson.json | f3400dc9cbffa079d89ad850f0acc7a3709a21d9 | 733806 | 144471 | real positive input, 13 JSON roots |
| NC | Benchmarks/1885_NC/1885_NC.json | 9ac18595acdf8938f01579b5c211f0deebc5dc0a | 10232634 | 1067628 | real negative, cannot stand in for positive |

Note: Firstpass content fetched and JSON.parse succeeded; NC metadata/blob verified but GitHub connector returned zero contents for its 10 MB file. Cannot claim runtime execution of NC. Authenticated Owner positive ~30 MiB not staged.

## Actual main standalone source path (source inspection only)
- tabs/xml-cii-2019-standalone/ui-adapted/xml-cii-adapted-events.js lines 93–98: input "staged-json-file" → readTextFile(file) → updateWorkflowState({stagedJsonFile,stagedJsonText:text}) → render.
- Same file lines 210–218: authored resolver click → await stagedJsonTextFromState → **synchronous runStandaloneResolverJsonTrace** and result/render on calling main JS thread.
- tabs/xml-cii-2019-standalone/xml-cii-workflow-ui-adapter.js lines 7–12 uses FileReader; lines 108–122 materialize source/staged full text into workflow job.
- lfj/ports/source-browser-worker.mjs and source-worker-port.mjs exist and require WorkerGlobalScope, page ACK and max 1 MiB wire, but evidence DOES NOT establish that authored standalone resolver uses them. Do not substitute dedicated Worker qualification for user workflow.

## Surrogate timing (NOT the product/app)
Measured fresh V8 isolate JSON.parse x3 on fetched original Firstpass 13-root JSON and valid generated arrays repeating source roots. Repetitions preserve JSON parse shape but duplicate engineering source identities; generated files have **no engineering acceptance authority**. Byte sizing UTF-8 via JS scalar scan. Timing granularity Date.now milliseconds. Environment not the user's browser; no event-loop frame or browser heap access.
| Replication | Bytes | Root entries | 3 observed parse times ms (sorted) | Median ms |
|---:|---:|---:|---|---:|
| 1 | 733805 | 13 | 2,2,7 | 2 |
| 14 | 10273257 | 182 | 29,33,34 | 33 |
| 42 | 30819769 | 546 | 88,93,122 | 93 |
| 84 | 61639537 | 1092 | 151,190,222 | 190 |
Lengths differ by 1 from checked-in file because array outer whitespace was trimmed; original byte count remains 733806. These values are parse-only observations, not timing of read/upload, matching, trace render, export, worker transfer, resident/peak memory or longest UI freeze.

## T1 pending acceptance protocol, no unsupported pass
1. Real authored standalone application on exact main, native Chromium; Firstpass File upload + paired XML, NC + paired XML (negative), generated valid JSON sizes approx 10/30/60/100+ MiB. Keep generated source-shape provenance distinguishable from positive Owner inputs; never claim duplicated roots are valid match authority.
2. Measure each stage separately (file selected→read, JSON index, trace match, evidence render, CSV), memory peak/process RSS and JS heap where available, wall time and max requestAnimationFrame gap with heartbeat started BEFORE operation and ended AFTER the last render/settled state. Capture error, timeout, cancellation and over-range behavior; verify selected source digest and row/original occurrence oracle.
3. Cold and warm browser runs, x3 each size with machine/browser/commit/version, include failures and archive machine-readable rows and traces. Genuine original positive and NC negative oracles must not be mixed.
4. T1 passes only with captured actual Chromium/input evidence, complete size/time/memory/freeze curve and Owner-approved operating envelope. Current T1 status PARTIAL/NOT_PROVEN. No T2 or T3 started.

## Owner decisions / stops
- D-AIM-1: sticky label CP-3DC-XML-CII-01 approval pending, do not write assumed approved YAML.
- D-AIM-2: propose Firstpass 0.73 MB + NC 10.23 MB + generated 30/60/100 MiB, 200 ms longest main-thread frame gap as provisional target (NOT an agreed threshold); ask for largest accepted bytes, freeze limit, what should happen outside range and real positive original files.
- D-AIM-3: no cherry-pick/salvage before Owner approval; #180–#183 read-only analysis in T2.
- D-T1-RUNNER: exact-main hosted/browser runner needed for genuine authored workflow; no direct repo download from this runtime (git host cannot resolve); creating/modifying Actions workflow requires explicit permission under AGENTS.md. Do not call V8 surrogate a browser test.

## Workpack R1
T1 S: actual Chromium main baseline (in progress, blocker machine/runner+Owner range).
T2 S: source-only salvage map #180–#183 with per-commit evidence (not started; D-AIM-3 blocks product reuse).
T3 M: standalone worker from lfj/ports direct main small PR (not started; D-AIM-1/D-AIM-2/D-AIM-3 and T1 acceptance).
O2 / O3 later, each standalone module/worker.
No product PR changed/merged/closed/rebased. No CI test executed for T1. Global outcomes 0/3 met, no user-facing change.
