# TAB3-O1-W04 — Owner Option A exact-edge Chromium diagnostic (PARTIAL; awaiting CI)
Date 2026-10-12 | chat 6acc7d4e | aim 3DC-XML-CII v2.2.0 / 5f9065d | outcome O1
Owning issue: https://github.com/reallakshman19/3D_Converters/issues/226
Workpack R6: https://github.com/reallakshman19/3D_Converters/issues/226#issuecomment-6119316935
Closed predecessor response 2: https://github.com/reallakshman19/3D_Converters/issues/226#issuecomment-6119199006

## Exact task-only changes
Existing unmerged draft PR #228 branch lfj/226-t3-main-worker-intake-20261012, base/main 4f14beb37bc0b719453c52a116c1c5d7183d2fd0.
Original assessed draft ef003ad24282c48ede5c11515d25d3298b961237.
Test-only script added at 9262a976deeace8bb08671856ad6f5886cec3cb6:
- scripts/lfj-226-o1-policy-edge-browser.mjs
Added standalone CI workflow at current exact head 6388f1ae3f26cb1f73a4bdcf32cd7826b6ee3ae9:
- .github/workflows/lfj-226-o1-policy-boundaries.yml
Source intake, R03/R04/R05, Native Worker, domain Worker, storage, CSV exporters, and production UI **unchanged**.

## Cases (separate actual authored Chromium with native IndexedDB and two real workers)
1. byte-in: generated JSON exactly 104857600 bytes, one authentic Firstpass semantic fragment + <=32KiB scalar padding; expected low-count native commit, XML matching and complete Node/Evidence CSV.
2. byte-out: exactly 104857601 bytes, same low-count form; expected clear typed byte policy refusal and zero export, no work in W04 to add missing guard.
3. count-in: exactly 2000000 original value occurrences within byte cap; original Firstpass fragment plus literal zero scalars, expected committed OPEN/SEAL, matched XML/source path audit and both CSV downloads.
4. count-out: exactly 2000001 original values within byte cap; expected OCCURRENCE_LIMIT typed refusal, no committed trace/export.
Positive runs capture full CSV sizes, SHA256, rows, bounded visible UI table, source SHA/occurrence census; negative runs assert visible typed failure and no export rights. rAF monitored during each run (<=200ms used only as an engineering diagnostic, not approved Owner limit). byte-in/count-in test source replacement with malformed JSON and revoked export. Every input generated for **capacity only, not semantic golden**. Failing job retains artifact JSON with counts/bytes/result and precise reason; no test waiver or overcount redesign.

## Current state and accuracy
GitHub Actions run https://github.com/reallakshman19/3D_Converters/actions/runs/38215243840 at exact head 6388f1a: four matrix jobs queued/in_progress after workflow submission. First job's checkout and node --check passed; native Chrome/browser outcome, input hashes, semantics, frame gaps, positive/negative policy results and all per-case job conclusions **PENDING/NOT_RUN** at this checkpoint. Overall W04 **PARTIAL**, 0 of 4 cases completed at recorded readback. No app source correction/merge/deploy, no W05 commenced, no O1 Owner acceptance; original Firstpass/NC regression and C05 release limitations remain.

## Next within W04 only
Read final exact-head four-job CI and retained JSON artifacts, identify first failing boundary (byte>100MiB should refuse; exactly2m should complete), compare source SHA/trace/CSV and cancellation/refusal. Publish subsequent exact completion or narrowed blocker before starting W05; STOP rather than relax protected R05 or authentic-source assertions.
