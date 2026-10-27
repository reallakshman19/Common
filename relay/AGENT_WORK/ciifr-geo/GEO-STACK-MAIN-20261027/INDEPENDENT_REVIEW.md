# CIIFR_GEO prerequisite stack — independent integration review

**Current verdict: SCOPED_INTEGRATION_PASS at `5a098b8805dcf998e9dd42af91a8e48d7edfcfb1`, tree `47fca239283da31f1c53d48ac4a560451b39a463`, relative to main `c823f0c0edbeb315c07fa2911390dc781968146f`.** The main-artifact sample delivery defect found during this review is repaired and independently challenged. No remaining material product finding within the inspected and exercised scope. This is not GPU, Windows, physical correspondence, large-model performance or Owner acceptance.

## Assignment and independence

The Owner explicitly authorized fixing and merging the prerequisite chain PR183 → PR181 → main. This reviewer was separately assigned READ_ONLY assessment, with no product editing, public posting, approval or merge authority. The reviewer did not contribute product code. This is an exposed, separate non-author review: inherited conversation, earlier product review, author explanations and shared authoritative requirements are disclosed. It is not blind or independently authenticated account/principal review. The Oracle performs reconciliation and the authorized merges.

Re-read current repository AGENTS, Common START_HERE, Independent Reviewer and independence guidance. The relevant expectations are: preserve current main and unrelated work; keep this a read-only XML correspondence prototype; qualify shared-viewer changes for existing consumers; keep runtime sample dependencies available under the existing deployment policy; bind claims to exact source and actual execution. No new release or merge permission is inferred from a review verdict.

## Independently refreshed stack and scope

At initial refresh:

| Subject | Exact revision / observation |
| --- | --- |
| Current main / cumulative merge base | `c823f0c0edbeb315c07fa2911390dc781968146f` |
| PR181 | Head `683a1ac37b5e4457b3e67753cec1c951ec1a2dc9`, base main, open/draft, mergeable clean; 21 add-only paths |
| PR183 before repair | Head `7ad4caaa706584fc6fa92667e4cfe5f3230295eb`, base PR181, open/draft, mergeable clean |
| PR185 merge wrapper | 7ad4 parents are `3a1bec9524c8a14e4b0a90a23d628f0b5d47aaf6` and reviewed `1da8c88c38ed6202896dfe5ecce2cac51e91ecba` |
| Reuse boundary | 7ad4 tree `08df2c44e667f579381b90fdf59a61cd1fce542e` is exactly the earlier reviewed 1da8 tree; the merge wrapper changes no file bytes |
| Initial cumulative scope | 60 paths: 56 additions and four existing shared-viewer modifications; no deletions, workflow, converter, Writer or other-tab application edit |

The four existing modified paths are `workbench3d/contracts/contracts.js`, `workbench3d/viewer/workbench-navigation-controls.js`, `workbench3d/viewer/workbench-navigation-state.js` and `workbench3d/viewer/workbench-viewer.js`. They extend X-up navigation, selected-pivot direct orbit, opt-in SOURCE/TARGET colours, navigation state access/restoration, and current-layout annotation projection. Their published Git blobs match the earlier reviewed source. Existing Y/Z paths and default status styles remain subject to the bounded regressions below; source equality alone is not runtime qualification.

Independently retrieved changed-file inventories for all 55 then-open XCU PRs. Every inventory was complete, with no 100-file pagination boundary. Excluding PR181/183, there was no exact-path overlap, no other `workbench3d/` path and no other `prototypes/ciifr-map/` path. PR184 remains seven added `tools/ciifr-geo-pick-review/`/report paths; PR182 remains six added topology-tool/test/report paths. Their work is preserved and is not merged through this assignment. This exhaustive path observation does not prove semantic independence or grant authority over those PRs. Receipt: `ir-stack-integration/OPEN_PR_OVERLAP_RECEIPT.json`.

Final API refresh before returning this review confirms PR183 head 5a098, base 683a, 51 changed paths, open/draft and mergeable clean; PR181 remains head 683a against main c823. PR183's title/body now explain the final A/B/C/shared-viewer scope and packaging repair. PR181's current 21-file description is historical until the PR183 merge advances its head; the Oracle must rewrite that final main-facing description before merging PR181.

GitHub check-runs were zero at both inspected PR183 heads; initial combined status was pending with zero statuses, and native GitHub reviews were absent. These are not hosted CI PASS claims. Recheck actual heads, checks and mergeability immediately before each authorized merge.

## Finding discovered: runtime samples excluded from Pages

**F1 — Medium, addressed in final source.** The unchanged main deployment workflow stages the repository using unanchored `rsync --exclude='tests/'`. The previous app sample button fetched `./tests/fixtures/S1-F05.xml` and `S1-R4.xml`. Thus the prototype entry was packaged while both runtime dependencies were removed. Local checkout HTTP and the custom immutable preview could pass while the main Pages sample button would fail.

The reviewer independently read the exact main workflow and app source, then executed the actual rsync exclusion policy on the same nested paths with the actual public XML bytes. The staged entry existed and both sample paths were absent. A separate reviewer original-hash HTTP invariant then requested the actual app URLs from that staged layout: both returned HTTP404 and the invariant failed with exit1. This was a product-delivery failure, not a test that could not run. The existing root Pages graph regression also passed while the defect was present, demonstrating its coverage gap.

The repair changes only the app's sample request prefix to `./samples/`, adds three runtime sample paths reusing the exact existing XML/manifest Git blobs, and adds the actual-workflow-rsync/staged-HTTP regression plus documentation/receipts. Development fixtures are retained for tests and parallel CLI consumers. There is no workflow, server, matching, scoring, graph, export, Worker, shared-viewer or other-tab runtime change in this repair.

Original runtime sample identities independently measured from actual bytes:

| File | Bytes | SHA256 | Git blob |
| --- | ---: | --- | --- |
| S1-F05.xml | 882735 | `1154c980d08344b1f803cda3bd9884b169753148b150641a745c9bfcb15de995` | `914303e2437fffaa5682757ee32b3ae3d8f37df8` |
| S1-R4.xml | 1426775 | `a332dd7b2551faae51de3c016941762c3b795cdf19073b373817354e309526e6` | `2da10efac2d2f040000edd988d4a1e0baae5dbe1` |
| manifest.json | 726 | `973cac32441f388efb5a49f9b80f56d1409fcbaf697785ba8002299dfefd0e6b` | `559ed00b9de48b362f0d7b207df2e3fc3abfc81a` |

**F2 — Low, publication wording.** PR183 initially claimed eight local-only paths and no shared-viewer edits despite its updated 47-path delta. Its final title/body correct this. This is not an unresolved code defect. PR181 still needs the ordinary final-description refresh after its head advances; Owner authorization is already supplied.

## Final immutable receipt

Independently fetched exact commit and immutable compares for `5a098b8805dcf998e9dd42af91a8e48d7edfcfb1`, tree `47fca239283da31f1c53d48ac4a560451b39a463`, parent 7ad4. The repair is exactly eight paths:

- Modified app.js, README.md, agents/PR183_workreport.md and agents/PR185_multibase_manifest.json.
- Added tests/pages_delivery_smoke.py and the three samples/ paths.

Received full UTF-8 contents of the five changed text files through GitHub. Computed byte count, SHA256 and Git blob from received bytes; all match the published manifest and tested local source. Published sample tree-entry Git blobs equal the actually read original fixture bodies above, and the staged HTTP bodies retain those independent original hashes. This receipt does not misdescribe that identity proof as a separate XML redownload from GitHub.

Critical received app identity is 13,817 bytes, SHA256 `66e1dff863a64d6a0926f4b1ee01223fdb794892586c4898032bf693b8f7536a`, Git blob `77a905aba3b20bd09d2f83722cba46fa35238919`. Received manifest identity is 8,857 bytes, SHA256 `6e527ac63adcb209ddb02c5cf386a1cc86d488478b3348fa25125b87996b58cc`, Git blob `e9c1918c8141fdd289e1f76a18e70ec527aad505`.

The final cumulative comparison against unchanged main c823 contains **64 paths: 60 additions and the same four existing shared modifications**. Independently calculated all 64 local changed-file Git blobs and matched every one against the published immutable comparison. No other runtime change was introduced. The isolated test workspace is `/workspace/scratch/ca71d2f89cf7/geo-stack-integration-20261027`: native Git HEAD is still 3a1bec with a verified final-source overlay, not a native checkout of 5a098. A local operational backup journal is the only tracked native difference outside the reviewed runtime paths and is absent from the published compare. Receipts disclose this instead of claiming a false checkout identity.

Receipts: `ir-stack-integration/RECEIVED_5A098.json`, `STACK_SCOPE_5A098.json`, and the earlier `RECEIVED_STACK_SCOPE_7AD4.json`. They preserve published source, actual received text identities, sample identity basis and current scope. The old integration packaging FAIL remains recorded above; it is not silently replaced by a later PASS.

## Independently executed focused integration evidence

Input basis and expectation were defined before execution: unchanged current-main consumer tests; exact shared source; actual pinned Three; the existing Pages exclusion policy; real public S1 XML; original independently measured XML hashes. No tolerances or production answers were altered to make a check pass.

| Check | Actual outcome / scope |
| --- | --- |
| Shared navigation/contracts/settings/static/markers/transfer-overlay | Six entrypoints PASS, exit0. Includes the 82-module static-hosting scan and invoked real bend/package/ancestry subchecks. |
| Existing consumer and root deployment graph | Four entrypoints PASS, exit0: sequential move manipulator, move snap acquisition, rotation ring controller, and root Pages graph. |
| Test-source custody | All ten selected test files byte-identical to current main c823; all four shared product blobs independently match the published final stack. |
| Separate Rodrigues oracle | 18 cases PASS, exit0: X/Y/Z, selected pivot or existing model center, positive/negative/90-degree direct orbit at plant coordinates; maximum error 4.547473508864641e-13. Real pinned Three, no GPU. |
| Baseline Y/Z control | Same oracle passes six no-pivot cases on actual c823 controls; maximum error 2.2737367544323206e-13. |
| Wrong-X falsifier | Reviewer-only copy lacking the X coordinate transform fails the unchanged requested-camera-position invariant, exit1. No product file edited. |
| Old artifact runtime sample invariant | Actual request URLs HTTP404, invariant FAIL exit1, expected negative. |
| Repaired bounded artifact runtime sample invariant | Same unchanged independent original-hash check requests the new app's actual URLs: both HTTP200, expected original byte count/SHA256, PASS exit0. Reconfirmed using the received published app. |
| Full-root actual workflow stage | Independently executed new pages_delivery_smoke.py, which reads actual deployment exclusions, stages the full root with rsync and boots the staged server: both original XML hashes and staged HTTP200 PASS exit0. |

Commands and captured results are retained in `ir-stack-integration/SHARED_CONSUMERS.log`, `SEQUENTIAL_AND_PAGES_GRAPH.log`, `NAVIGATION_RODRIGUES_PASS.log`, `NAVIGATION_BASELINE_YZ_PASS.log`, `NAVIGATION_NEGATIVE_FAIL.log`, `PAGES_OLD_FAIL.log`, `PAGES_REPAIRED_PASS.log` and `PAGES_FULL_STAGE_PASS.log`. Reviewer probes are `navigation-rodrigues.mjs` and `pages-sample-invariant.py`. Actual rsync command receipts remain under `pages-fixture-probe/receipt.json` and `pages-repaired-probe/receipt.json`; large copied inputs need not be relayed again because their immutable original source/blob identities are recorded.

The Oracle separately reports final native58/58, five unchanged Method C suites, HTTP39-module graph, pinned Three/Worker/license/denylist and syntax checks PASS. Those are contributor execution claims, not this reviewer's newly rerun results. Earlier independently received core/projection/selection review at the identical 1da8/7ad4 tree remains reusable within its original limits: the sole subsequent runtime delta is the sample URL prefix, now directly challenged through staged HTTP. Unchanged numerical and export code was not broadly retested merely to increase counts.

## Surviving-error challenge and limits

A green root Pages graph test could miss omitted runtime fixtures; it demonstrably did. Actual staged HTTP plus original fixed hashes now discriminates that wrong delivery state. A static scan or contract test could miss an axis transform or wrong rotation center; the separate Rodrigues calculation and missing-X negative address that numerical navigation subset. These do not prove GPU orbit, rendered colours, all pixel picking, all asynchronous renderer paths or every existing consumer interaction.

The full-stage test uses the existing workflow's exclusion policy and actual rsync/server behavior. It does not execute GitHub's remote deployment action or prove the future main-hosted endpoint; the Oracle should inspect the real post-merge deployment and sample URL responses. The Windows launcher path was inspected, not executed on Windows. Real WebGL, native fullscreen success, independent-model physical qualification, full edit-event/pin audit, target-host large-graphics performance and Owner acceptance remain unverified or incomplete. The samples are the same S1 model in two XML profiles, not independent-model correctness evidence.

## Return and authorized next action

**SCOPED_INTEGRATION_PASS** for exact source5a098/tree47fca against current main c823. F1 is addressed; there is no surviving material integration defect in the exercised scope. Preserve this independent verdict separately from contributor test reports and engineering/Owner acceptance.

The Oracle can persist this receipt, refresh exact live heads, merge the already authorized PR183 → PR181 chain, rewrite PR181 around its resulting final scope, and verify that each merge preserves tree47fca and that main's actual deployment serves both original sample files. A changed product tree requires affected reassessment. This reviewer did not edit product source, post, APPROVE, merge, deploy or accept the product.
