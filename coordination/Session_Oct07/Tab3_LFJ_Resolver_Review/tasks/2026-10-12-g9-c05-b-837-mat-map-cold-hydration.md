# G9-C05-B — C05.3 #837 Mat Map cold-hydration contract reconciled
Date: 2026-10-12; chat 6acd281a; Owner CP-3DC-XML-CII-08 exclusive #203 C05 writer. Governing AIM 3DC-XML-CII v2.2.0 label_sha 5f9065d, engineering-critical O1 release prerequisite. V3.5 Simplified=OFF, one bounded task per reply. No merge/deploy.

## Outcome
O1 release prerequisite #203 — one inherited C05.3 historical assertion reconciled to current three-master durable restart semantics. Mat Map cold-hydration gate #837 is now hosted green on integrated draft PR #228, without production source changes. G9-C05-A #836 also stays green on the same new head.

## For the user
Integrated draft PR #228 advanced from `f20cb3c379e61ed3272307baee08d16e112eb79b` to `5a74e554be8a9fe087f1bbabea558a3b47120ebe` with ONLY one test file `tests/xml-cii-issue-837-mat-map-cold-hydration.test.mjs` (+43/-19). Its previously red hosted #837 old 2/4 node failures became 4/4 PASS and actual Chromium first-load -> reload -> fresh-worker IndexedDB Mat Map 383/383 rows PASS at [new hosted run #38294471194](https://github.com/reallakshman19/3D_Converters/actions/runs/38294471194). Not a completed release: other C05 gates remain red and full CI on this head was still processing at evidence time.

## Proof / source contract verification
- Owner G9 exclusive #203 writer transfer recorded and provider-verified on issue bodies [#203](https://github.com/reallakshman19/3D_Converters/issues/203) and [#226](https://github.com/reallakshman19/3D_Converters/issues/226), card CP-3DC-XML-CII-08; #205/#225 superseded as writers but their test evidence can be used.
- Pre-edit HEAD checked exactly `f20cb3c379e61ed3272307baee08d16e112eb79b`; latest previous head's 44 workflows were 30 success/14 inherited other-C05 failures, zero pending; #836 was green. The #837 original file Git blob `e4e25360e6ef98c3a6ec9b7eb2b31ee3f3f54546` and old #837 job #38293184399 failing historical revision undefined and missing global rejection were rechecked.
- Created immutable rollback anchor `backup/203-c05-g9-c05-b-pre-fix-20261012-6acd281a` @ `f20cb3c379e61ed3272307baee08d16e112eb79b`, backup file blob same as old.
- Independently fetched live runtime `tabs/xml-cii-2019-standalone/workers/master-dataset-startup-hydration.js` blob `a1444411eaab99ec30c486491d2a33e5451ef083` (unchanged since task A): compares datasetRevision before row reads, raises `REVISION_MISMATCH` at `metadata-validate`, captures per-master typed failure identity while allowing independent unaffected masters.
- Adopted **only exact test content** from isolated #205@5ec7f1e/#225@8d3f798 tested candidate, blob `891537b79fdf161b6e5f19244f0da870ca6fdb27`. GitHub update-file CAS required old file blob `e4e253...`. Commit `5a74e554be8a9fe087f1bbabea558a3b47120ebe`, commit compare one file only, additions 43, deletions 19. No app source code, docs mirror, original masters, fixtures, Weight, Preview, O1 Worker, workflows or protected golden changed.
- Positives retained: Mat Map compact custody, original datasetRevision preservation and preview, docs deployment mirror parity. Subsequent three-master custody requires Piping Class revision 4 and Weight revision 5, source dataset IDs, Weight fingerprint and appliedMappingRevision; no full staging arrays or spurious failure identities.
- Negatives strengthened: mismatched cold Mat Map metadata revision (stored 3 vs observed 4) must result in typed `REVISION_MISMATCH` `metadata-validate`, zero calls to getRowsRange/getRows, no stale datasetRefs.materialMap, no appliedMappingRevision.materialMap; strict error-message expected/observed. Does not weaken source authority.
- New-head hosted [#837 #38294471194](https://github.com/reallakshman19/3D_Converters/actions/runs/38294471194) job `114962127924` SUCCESS, actual Node 4 tests PASS / 0 failures, Chromium script `scripts/run-xml-cii-issue-837-mat-map-cold-reload-e2e.mjs` PASS, receipt [artifact #11767655908](https://github.com/reallakshman19/3D_Converters/actions/runs/38294471194/artifacts/11767655908). Browser JSON: source `PCF_MAT_MAP.TXT`, original `rowCount=383`, `materializedRows=383`, `persistence=indexeddb`, `datasetRevision=1`, `appliedRevision=1`, 7/7 asserted flags true: activeSessionReadable, parsedRepresentationStable, compactCustody, coldReloadRestoredIdentity, coldReloadRestoredDatasetRevision, coldReloadRestoredMappingRevision, freshWorkerMaterializedPersistedRows.
- New-head hosted #836 [#38294470946](https://github.com/reallakshman19/3D_Converters/actions/runs/38294470946) SUCCESS, #118 V4.1 docs parity #38294470846 SUCCESS, #60 #776 #38294470899 SUCCESS at last checked. Other O1 and #98 jobs in flight; their earlier-head success is historical and not invented for this SHA.

## TASK_EVIDENCE
Outcome: O1 / C05 #203.
For the user: Mat Map #837 repaired; other red C05 still block release.
Proof: PR #228@5a74e55, hosted #837 run #38294471194 job 114962127924 PASS Node 4/4 + browser 383 rows, artifact #11767655908.
Task: G9-C05-B; Goal: C05.3 stale-revision and three-master revision custody reconciliation; Status: IMPLEMENTED_AND_TARGETED_CI_GREEN.
Met: targeted #837 1/1. Done: G9-C05-B (no other C05 task). Code: one test file +43/-19, no runtime.
Tests: 4/4 focused Node + 1/1 native Chromium success. CI: #837 SUCCESS; overall full 44-workflow matrix still red/in-progress at snapshot.
Evidence: source/old+new blob refs, backup, exact commit compare, workflow/artifact above; AC: #836 + #837 2 of baseline 15 C05 red workflows repaired, not release complete.
Claim: stale Mat Map cold-revision quarantined before any row reads/authority; positive original 383-row persisted/worker cold reload retained. No claim public site, Owner #141 golden or all C05 green.
Blocker: CI (remaining inherited C05), final Owner merge/deploy authorization. Next: G9-C05-C — #856 Valve Weight restart custody stale milestone, only after fresh-head check; keep #835/#855/#871/#884 Owner contract adjudication distinct.
