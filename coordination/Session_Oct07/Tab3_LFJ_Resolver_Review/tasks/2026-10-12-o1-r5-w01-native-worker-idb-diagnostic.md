# TAB3-O1-W01 — exact-head authentic Worker dispatch → ACK → IndexedDB diagnostic

- Issue: [3D_Converters#226](https://github.com/reallakshman19/3D_Converters/issues/226)
- AIM v2.1.0, label_sha d3ecd06, Outcome O1; chat=6acc44e0
- Plan: [R5 successor workpack](https://github.com/reallakshman19/3D_Converters/issues/226#issuecomment-6116914701), from G1 response2 [6116816559](https://github.com/reallakshman19/3D_Converters/issues/226#issuecomment-6116816559)
- Product unchanged (only browser diagnostic modified on existing DRAFT #228): [exact SHA 1edf1f913492c53418a096d40d75d66ebf8582d7](https://github.com/reallakshman19/3D_Converters/commit/1edf1f913492c53418a096d40d75d66ebf8582d7); base main unchanged 4f14beb37bc0b719453c52a116c1c5d7183d2fd0
- Exact-head [Chromium 136 hosted run 38197781925](https://github.com/reallakshman19/3D_Converters/actions/runs/38197781925), **FAIL** due NC source-only case timeout after 150000ms. [Original machine JSON artifact 11724091984](https://github.com/reallakshman19/3D_Converters/actions/runs/38197781925/artifacts/11724091984), including complete timed Worker message/IDB transaction event list; fetched and inspected with independent zip/json parsing.

## Test design and source provenance

Existing shipped standalone mounted from `tests/browser/lfj-226-o1-intake.html`; selector `[data-field=staged-json-file]` used with native File via Chromium, existing #228 opt-in LFJ Worker ON. Instrument `Worker.postMessage`, `message`, PAGE_ACK, `IDBDatabase.transaction`, IDB puts, deleteDatabase, file event/status and requestAnimationFrame; data recorded to machine artifact even on failing assertion. This observes the real source Worker + real IndexedDB, **not** a simulated store. Test-only change, no production endpoint patch.

| Case | Authentic original bytes | Independently computed test File SHA256 | Wall ms | max rAF gap ms | Accepted source-only? |
|---|---:|---|---:|---:|---|
| Firstpass positive source | 733806 | `6b2c8b01ab0ba6ec8e9e7c42eb4a719668ffd2dc4dbe4790d27cf426a1f60288` | 30641 | 33.4 | YES, 23754 occurrences; full SHA matched worker; no matched XML/CSV |
| NC negative source | 10232634 | `89f9c2ab7a9f1df15c1b9e1e0e30a8ca6c97ef994dcd56aec86c3a90f7d71646` | 150084 | 16.8 | NO; still provisional, timed out before SCAN_DONE/commit |

**Actual stage counters:** Firstpass 47 PROVISIONAL_PAGE, 47 PAGE_ACK, 47 IDB record transactions, 23,754 occurrence source-only commit. Record transaction wall durations median **619ms**, max **1172ms**, summed **28,609ms**; 47,509 observed IndexedDB `put` calls including head updates. NC 152 provisional pages, **151** ACK at timeout, 151 completed record transactions, **no** SCAN_DONE/commit/FAILED; record transaction median **973ms**, max **1533ms**, summed **142,169ms**, with >203k observed IDB `put` calls **cumulative across both inputs**, 402 IDB transactions cumulative. Latest provisional page sequence 151, latest committed-to-store ACK sequence 150, no source-index head visible; no matching/export rights. These transaction duration sums are observed overlapping stage timings; do not represent total exclusive CPU or all future rows. Real source Worker was dispatched for NC: **not an input-control or 'Worker never started' failure**. NC SHA computed independently in Node and matches Worker provisional source SHA. No user-visible main-thread freeze (rAF remained ~16.8ms) **during NC scan**, but source progress throughput unacceptable until budget/required range is agreed.

**Distinguish previous navigation negative:** historical [NC-only run 38193975925](https://github.com/reallakshman19/3D_Converters/actions/runs/38193975925) used original topology XML then targeted unavailable staged-json-file; it **did not upload NC JSON**. This new direct File proof removes that navigation confound, not claiming the NC XML matches a positive Firstpass trace. The previous 180s [#228 run 38193622267](https://github.com/reallakshman19/3D_Converters/actions/runs/38193622267) gave only Playwright timeout; stage evidence now locates prolonged per-page IndexedDB record writes/ACK, rather than no Worker dispatch or mere stale UI status. Do not promote this to a unique root-cause claim for all large JSON; the exact number of remaining NC occurrences, further scan/CPU costs, and finished end-to-end XML trace are still unknown. Cancellation at job replacement evidenced by IDB_DELETE_REQUEST/SUCCESS between scans, but concurrent in-flight cancellation and stale output gate require W02 negative tests.

## Judgment, limits and next

**W01 diagnostic goal met**: one exact-head, real-browser dual-original probe isolates first presently demonstrated capacity bottleneck; the hosted test remains deliberately **RED** because NC has no complete source head. **User delivered result: none** (no deploy, no XML match/CSV). O1/O2/O3 acceptance remains 0/3. Don't patch old synchronous UI algorithm. W02 must preserve the existing LFJ core and correct throughput at **versioned committed-store/adapter ownership** if justified, then qualify OPEN+SEAL pair lookup/committed query and real original XML selected matching. Test one narrow record-store staging alternative and compare original SHA/occurrence completeness; any index-store optimization cannot infer export/engineeringReady rights. D-AIM-2 numeric range 100MiB/200ms still PROPOSED, not Owner-approved. #203 inherited C05 unrelated to this focused diagnosis, but broader release still gated separately. Reuse Preview/Weight for future O2/O3; no coding here.

```text
Task: TAB3-O1-W01
Goal (issue AC): Establish first authentic NC vs Firstpass Worker/control/page ACK/store boundary
Status: DONE
Met: yes - diagnosis only, NC admission and O1 full output still red
Done: Instrumented PR #228 real browser test; original Node SHA checked, source-only positive, NC stall located at IDB writer throughput
Code (repo branch @ commit | PR): 3D_Converters lfj/226-t3-main-worker-intake-20261012 @ 1edf1f913492c53418a096d40d75d66ebf8582d7 | #228 draft
Tests (command -> pass/fail/skip): CI node --check scripted test+intake -> PASS; node scripts/lfj-226-o1-worker-intake-browser.mjs -> FAIL NC >150000ms with 151 acknowledged pages
CI (run -> result): 38197781925 -> RED, diagnostic logs and artifact uploaded
Evidence (link): https://github.com/reallakshman19/3D_Converters/actions/runs/38197781925/artifacts/11724091984
AC (before -> after): undifferentiated NC timeout -> DISPATCH and 151 PAGE_ACK proven, 142169ms summed record writes, no SCAN_DONE/commit
Claim: HOSTED_CI
Blocker: NONE for W02; OWNER:D-AIM-2 for final range acceptance
Next: TAB3-O1-W02
```
