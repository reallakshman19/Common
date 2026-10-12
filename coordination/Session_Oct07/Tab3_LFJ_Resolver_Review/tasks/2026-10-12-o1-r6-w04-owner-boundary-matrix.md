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

## Hosted exact-head partial results — 38215243840, after initial W04 record
Directly re-fetched GitHub Actions job conclusions and decoded terminal job logs at PR #228 HEAD 6388f1ae3f26cb1f73a4bdcf32cd7826b6ee3ae9. These are **actual authored Chromium**, NOT a local simulation; emitted LFJ226_O1_W04_EDGE JSON is preserved in the raw job logs and artifacts.

- byte-in **PASS**: exactly 104857600 B, source SHA256 300d14e37af6cd33c67092a7c5dd56b4b2507e85937c3887f7622d3e9b11edf4, 26932 COMMITTED original values, 241 path audits, full node CSV 216 rows / 57945 B / 0d8bb4482ed4a9d0d116faeac5e68ce564f07b6bba2dd73dfc3676b72ec2eddc, evidence CSV 241 rows / 50399 B / 653485ff968bf478fa0001488432bb210a9ce6e85a901e9cc19f368f53a24809. Malformed replacement revokes old exports (O1_EXPORT_SOURCE_STALE); max observed frame gap ~16.8ms. Time source 43325ms, matching 1698ms. No independent semantic oracle.
- byte-out **FAILED, actual Owner policy violation PROVEN**: exactly 104857601 B, SHA256 8150f5a03f333bc33b3ead11b2db10a117e1a1aef16488abd95617ef343a617e, 26932 ORIGINALS COMMITTED where the required byte-limit typed refusal should have occurred. XML domain Worker then matched 241 paths, and the app produced **both original complete CSVs** (216 / 241 rows, hashes same as byte-in), 64 visible rows, max frame ~16.8ms. The behavior is a policy admission defect **not** a freeze: out-of-range trace/download rights wrongly granted. Correct narrow source Worker + UI byte-fence belongs to W05 after W04 closure. This job rightly exits code 1, no CI waiver.
- count-out **PASS**: generated 4686299 B with **2000001 original values** (generator uses known original Firstpass 23754 values then literal scalar zeros); SHA256 e44a26b36a7f78132b05fbdfbb685c7ba9cfcc1e43dc259a74a690b90b808ce4. Visible LFJ Worker FAILED: OCCURRENCE_LIMIT; no trace/export rights; no commit, no download, zero output controls, ~16.8ms max rAF, typed response after 69845ms. No explicit Owner timeout was set.
- count-in **PENDING at checkpoint**: hosted job still executing real Chromium; its status and exact 2000000 positive export results must be fetched before W04 is closed.

Exact job IDs: count-out 114698356570 SUCCESS, byte-out 114698356786 FAILURE, byte-in 114698356789 SUCCESS, count-in 114698356731 IN_PROGRESS. Source app test-only at 6388f1a; accepted exact-head focused CI on *prior* ef003ad must not be carried forward. No product fixes have been made.

## W04 CLOSED — all four exact-head Chromium jobs terminal (diagnostic)
At original W04 head `6388f1ae3f26cb1f73a4bdcf32cd7826b6ee3ae9`, real [CI run 38215243840](https://github.com/reallakshman19/3D_Converters/actions/runs/38215243840) is **RED 3 PASS / 1 FAIL**, and the red byte-out is the *real Owner-policy defect*, not a bypass of the test. W04 diagnostic is DONE, **NOT** O1 product accepted. [Issue #226 W04 final TASK EVIDENCE](https://github.com/reallakshman19/3D_Converters/issues/226#issuecomment-6119490728) posted and read back. Details of other three runs are in the preceding section.

- **count-in PASS:** exactly **2,000,000 original occurrences**, **4,686,297B**, SHA256 `61156f26e51748cb44c42100285ab8465a9b3b1ff92118df5b196668c6f6275d`. Native source **COMMITTED**, exact count and source SHA returned; original XML matched 241 attested paths; 64 visible rows; full original 216-row/57945B Node-wise CSV SHA `0d8bb4482ed4a9d0d116faeac5e68ce564f07b6bba2dd73dfc3676b72ec2eddc` and 241-row/50399B Evidence CSV SHA `653485ff968bf478fa0001488432bb210a9ce6e85a901e9cc19f368f53a24809`; invalid source replacement blocked old export `O1_EXPORT_SOURCE_STALE`; max measured rAF 16.8ms. Source index 65061ms and matched-domain build 70211ms. This is a generated capacity case, not an independently certified semantic golden.
- **byte-out FAIL:** exactly 104,857,601B, 26,932 originals wrongly committed and downloaded both CSVs, not a benign expected negative. W05 engineering-correct product fix required.
- **byte-in PASS:** exactly 104,857,600B, 26,932 originals + both CSVs.
- **count-out PASS:** exactly 2,000,001 originals within byte cap, typed OCCURRENCE_LIMIT, no commit/exports.

No app/source code was changed by W04; new W05 head CI evidence must be read separately, never carried from W04 SHA.
