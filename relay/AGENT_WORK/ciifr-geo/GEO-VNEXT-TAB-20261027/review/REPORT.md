# CIIFR_GEO VNext integration review — source 1f4fb608

## Verdict and action

**No blocking integration defect found in the inspected source and executed native/controlled-DOM/HTTP scope.** The candidate supplies the requested additive CIIFR_GEO tab through the existing CII Find & Replace → VNext Standalone host, reuses the existing A/B/C workbench, and preserves the separate engine and writer paths. The implemented route, lazy load, retained iframe and preserved outer entry are supported by executed checks. This is a completed bounded non-author agent review, **not rendered-browser approval, engineering acceptance, release readiness, or Owner merge authorization**.

The actual nested rendered user journey, browser-native fullscreen, WebGL rendering/picking, Windows and heavy-model performance remain **NOT_RUN**. A browser launch prerequisite failed before a usable page; source inspection and controlled DOM do not close that gap. Principal/account independence is **UNKNOWN**; the reviewer is a distinct non-author agent, not an authenticated distinct human/account.

**One useful next action:** the contributor/Owner should run the exact final candidate in a supported browser through CII Find & Replace → VNext → CIIFR_GEO, load the bundled S1 pair, create A/B review state, switch among host tabs and return, verify state retention, then enter/exit fullscreen and the 3D viewer. Return a trace/screenshots and console/network observations tied to the final source. This closes the material integration uncertainty before an acceptance or merge decision.

## Review basis and identity

- Assignment: Common commit `2afd9e2db50f03a3794954f8c47952a3f1778d95`, `relay/AGENT_WORK/ciifr-geo/GEO-VNEXT-TAB-20261027/REVIEW_ASSIGNMENT.md` and `SOURCE_MANIFEST.json`, actually fetched with the GitHub connector. Owner purpose: “wire it to CII Find & Replace > ↔ CII Find & Replace VNext · Standalone as a new tab (independent modules).”
- Repository: `reallakshman19/XML_Compare_Utilities`, draft PR191, observed open and mergeable. Candidate `1f4fb608ccdbeb53adae230ac45877d94a16c113`, tree `839287d121abf4bff2bce1c7952d7f1e86225261`; base and observed compare merge base `e3d52e8a5e2855f0e684e9cb1358f4bca5f2b211`. Compare is one commit ahead and exactly the twelve manifest paths. No workflows, prototype core or shared viewer changes in this candidate.
- Local source is native Git HEAD `3a1bec9524c8a14e4b0a90a23d628f0b5d47aaf6` plus the published-main/candidate file overlay. It is **not** a native Git checkout of 1f4. Relevant file bytes were checked directly instead of inferring identity from HEAD.
- Read applicable live repository `AGENTS.md`, mirrored docs policy, master index, actual host/app/workbench and changed tests, pinned independent-review instructions, and Common review floor. The stale repository-policy owner alias `reallaksh19/Common` produced 404; the actual public assignment is under `reallakshman19/Common` and succeeded.
- Pinned method: Common `d7365707dca0039f9a529f7309b635ff160c9dd0`, `skills/agent-work/independent-review/SKILL.md` Git blob `b80f8297d2c067fbab0a43528a7c9eba61928398`, with APPLYING_GUIDANCE and INDEPENDENCE. Common review floor was fetched at main, then independently pinned/read back at assignment commit2afd; same blob `9ea7ff68c9e5d61331ec08e690f231c921c842f5` for `skills/common-reviewer-protocol-v1.0/SKILL.md`.
- Authority: read-only product review. No product edits, workflow edits, test expectation changes, external comments/messages, commits, or merges performed by this reviewer. Evidence and isolated defect seeds live outside the product tree. Appendix A implementation takeover is NOT_APPLICABLE: no implementation authority is requested or exercised.

## Findings

**A1 — ADVISORY, inherited user-facing wording.** `prototypes/ciifr-map/index.html:10` says “VNext integration pending.” That statement is stale when the same document is reached through the new VNext tab. The text predates this PR and does not prevent use or change engineering authority. A narrow wording correction would improve the integrated experience; do not interpret this finding as permission for core/prototype scope expansion. The contributor was informed and may supply a separate exact-source text-only follow-up. This report preserves the finding on 1f4 regardless of that follow-up.

**E1 — EXTERNAL_DEPENDENCY, acceptance uncertainty.** Native Chromium launch exits SIGTRAP before a usable page on this host. Actual iframe browsing-context persistence, native fullscreen policy through both ancestor frames, visible dimensions/scrolling, local Three.js import-map behavior and GPU resize/picking cannot be established by HTTP and controlled DOM. This is missing execution evidence, not a reproduced product defect. Required end-to-end acceptance remains open.

**F1 — ACCEPTANCE_SURFACE_DEFECT, preexisting failed branch expectation.** `tests/cii-fnr-vnext-branch-scope.test.mjs:81–85` treats B1 as a mismatch while its own synthetic target has a B1 element with pointer3 into the third named record `ALIAS-OLD`. The rule therefore produces one claim rather than zero. Both candidate and isolated base-app projection reproduce the same 18 PASS / 1 FAIL at the identical assertion. The GitHub base/head compare confirms the planner, parser, writer and test fixture are unchanged. This PR does not regress that behavior. The failed test remains FAIL; its assertion was not changed or waived by this review.

## Product integration reasoning

The existing outer `cii-workspace-find-replace-ui.js` selects source/docs-relative VNext URLs and sets the iframe src once on explicit switch. The candidate only adds fullscreen delegation to that outer iframe. Its CII editing session and close/destroy semantics remain the existing behavior; closing the entire host removes the iframe and is not a persistence promise.

VNext `app.js` adds CIIFR_GEO to its known tab set, hides the CII workspace/config appropriately, and delegates display to a nineteen-line module. Its `workTabs` engine state remains NORMAL/LINE_NODE/GEOMETRY. Existing tab-change invalidation clears CII plans/approvals/export before and after a switch. The new tab's fallback to NORMAL state follows the existing CONFIG path; the geometry workbench never enters CII planning, approval, validation or writer state.

`geo-tab.js` resolves the root-level `prototypes/ciifr-map/index.html` from both source/docs modules. It sets iframe src only when absent, preserves the actual element on hide/show, and sets the separate-window link to the same module-relative route. Both iframe levels contain fullscreen delegation. The document boundary separates application state; these same-origin frames are **not a security sandbox**. There is no new `contentWindow`, `postMessage`, storage bridge or host-data transfer in the delta. The workbench's existing native file intake, A/B/C matching, XML geometry authority and viewer are unchanged.

The unchanged deployment workflow rsyncs the repository root, so the root prototype is available alongside the docs VNext page. A docs-only deployment would be incompatible, but that is not this repository's observed workflow. Reviewer HTTP probing used a project prefix and included both module workers plus the local import-map Three.js vendor, which the author's simple static-import graph does not fully cover. Retaining a hidden workbench also retains its computation/resources; heavy-model resource behavior remains unmeasured, with no invented claim of pause or disposal.

## Executed evidence

All commands ran from the product root unless otherwise stated. Logs retain full actual output. PASS scope and oracle are explicit:

| Check | Result | Observation and oracle | Evidence |
|---|---|---|---|
| Fetch all twelve candidate files via GitHub, compare remote bytes to actual local bytes, byte counts, SHA-256 and computed Git blob IDs | PASS 12/12 | Connector retrieval + local hashing; authoritative immutable source identity, not semantic approval | `file-verification-{0,1,2}.json`, `remote-source/`, `SOURCE_MANIFEST.json` |
| Fetch complete candidate Git tree (9286 entries, not truncated); compare 116 relevant host/VNext/prototype/viewer/deployment files locally | PASS 116/116 | Independent source custody; all bytes match actual candidate tree | `dependency-verification-{0,100}.json`, `live/candidate-tree-summary.json` |
| `node --test tests/cii-fnr-vnext-geo-tab.test.mjs tests/cii-workspace-vnext-modal-entry.test.mjs` | PASS 8/8 | Re-executed author/existing controlled-DOM and source tests; implementation-coupled oracle, inspected assertions | `author-focused.log` |
| `node reviewer-probe.mjs` from review directory | PASS | Reviewer-authored controlled-DOM/module harness; expectations derived from Owner purpose and retained independent-workbench semantics | `reviewer-probe.mjs`, `reviewer-probe.log` |
| Same reviewer harness against isolated bad docs-route and unconditional-reload module seeds | PASS: both rejected | Wrong route yields docs/prototypes; reload seed yields20 navigations vs1. No candidate or expected-answer modification | `reviewer-probe.log` |
| `python reviewer-pages.py` from review directory | PASS 60 served assets | Actual unchanged workflow exclusions + rsync staging, prefixed HTTP, all A/B/C markup, both workers, local Three import map, original sample hashes, negative wrong-route404 | `reviewer-pages.py`, `reviewer-pages.log`, `reviewer-pages.json` |
| Every one of the60 served assets compared to immutable candidate Git-tree blobs | PASS 60/60 | Authoritative source-byte comparison, including transitive modules beyond the116-file selection | `staged-candidate-verification.json` |
| `node --test tests/cii-fnr-vnext-branch-scope.test.mjs` | FAIL 18/19 | Existing fixture/assertion; actual1 expected0 | `candidate-branch.log` |
| `python run-baseline.py` from review directory | Same FAIL 18/19 | Isolated copy with exact fetched base app in both mirrors and unchanged production planner/parser/writer/test. It is a base-app projection, not a complete native base checkout; the failing direct-planner case does not depend on app/HTML | `run-baseline.py`, `baseline-branch.log`, `base-source/app.js` |
| `CIIFR_TEST_RUNTIME=/workspace/scratch/ca71d2f89cf7/map-test-runtime node --experimental-vm-modules --test prototypes/ciifr-map/tests/*.test.mjs` | PASS 58/58 | Re-executed existing native/VM/XML tests with real test-only xmldom parser; inspected source, not browser/GPU evidence | `existing-workbench-configured.log` |
| `node tests/deploy-workflow-pages-artifact.test.js` | PASS | Existing deployment graph check | `existing-pages.log` |
| Native Playwright Chrome launch using supplied concrete executable and writable TMPDIR | NOT_RUN for usable page | Launch attempted; process exits SIGTRAP before any page. Initial default launch also exposed missing default headless binary and /tmp preparation; those are environment/pre-step failures | `browser-attempt*.log` |
| Remote check-runs for exact1f4 | No checks | GitHub returns total_count0; not CI PASS | `live/checks.json` |

The first workbench command omitted its documented test runtime and VM flag, producing 33 passing cases plus seven file-level preparation failures. That attempt is preserved in `existing-workbench.log`; parser-dependent checks were NOT_RUN there. Reading the README supplied the correct prerequisite, and the configured run above passes58/58. No preparation failure is classified as product PASS or defect.

The reviewer probe exercises unknown-tab rejection, nested button-content clicks, all existing tab types/config, exclusive panels, repeated same-tab clicks, twenty hide/show cycles, one iframe navigation, unchanged outer lazy-entry code and root/project-prefix routing. It uses the existing lightweight DOM helper, so its claims stop at handlers/attributes/element identity. It cannot observe a real browsing context or pixels.

Original public sample SHA-256s observed through staged HTTP:

- `S1-F05.xml`: `1154c980d08344b1f803cda3bd9884b169753148b150641a745c9bfcb15de995`
- `S1-R4.xml`: `a332dd7b2551faae51de3c016941762c3b795cdf19073b373817354e309526e6`

## Common review floor coverage

| Criterion | Applicability/result |
|---|---|
| CR-01 Basis/scope | REQUIRED; exact source/base/tree/12-path inventory verified; all changed human-written regions inspected |
| CR-02 Design/system fit | REQUIRED; PASS in inspected scope, additive document host reuses existing workbench |
| CR-03 Functional/negative behavior | REQUIRED; handler/routing/state checks PASS; actual rendered user journey NOT_RUN |
| CR-04 Maintainability | REQUIRED; PASS; small named display module, limited mirrored host edits, scoped styles |
| CR-05 Verification quality | REQUIRED; assertions inspected, two seeded wrong results rejected; known FAIL preserved, environment gaps explicit |
| CR-06 Interfaces/data | REQUIRED; route/deployment/mirror compatibility PASS; no changed serialization, units, writer or persistence authority |
| CR-07 Security/privacy | REQUIRED proportionate review; no new engine data transfer/dependency/input processing; same-origin trust limitation disclosed |
| CR-08 Reliability/resources | REQUIRED; lazy-once and state-handler behavior PASS; real frame lifecycle/heavy-model/GPU behavior NOT_RUN |
| CR-09 Documentation | REQUIRED; recovery/PR explain purpose/limits; advisory stale workbench banner A1 |
| CR-10 Regression/release fit | REQUIRED; native/HTTP evidence supports host delta, baseline failure is preexisting; browser acceptance and Owner decision remain open |

## Independence and surviving wrong result

Reviewer agent `/root/vnext_geo_independent_review` did not author or repair this candidate. Contributor is root/Oracle. Account/principal separation was not authenticated and remains UNKNOWN. The assignment and author PR/report/tests were read before final method selection; the known branch failure and browser limitation were explicitly supplied beforehand. They are reproduced corroboration, not blind discovery. Source manifests are legitimate custody inputs; matching them does not create an independent semantic oracle.

Expectations come from the Owner's requested host path and independent-module outcome, existing host invalidation behavior, deployment workflow and production entry points. The reviewer wrote its own harness/staging walk, inspected author assertions, extended graph coverage to workers/import-map vendor, and tested isolated wrong implementations. Route/retention probes overlap author-selected risks; this is disclosed shared context. Existing tests, XML fixtures, parser and underlying production engineering assumptions remain shared lineage. No numerical/original-CII/Writer correctness certification is issued.

A plausible surviving wrong result is a real browser showing an unusably small/scroll-trapped nested viewport, losing a GPU context on hide/show, or denying native fullscreen despite correct static attributes. Controlled DOM and served bytes would still pass. This is why end-to-end rendered/GPU acceptance remains open.

## Reproduction and continuation

Run `python verify-received.py` to recheck frozen fetched-source integrity and captured custody receipts. `node reviewer-probe.mjs`, `python reviewer-pages.py`, and `python run-baseline.py` reproduce the principal probes while the original product source remains at the reviewed bytes. The local staged artifact and exact fetched source are preserved. If product/base changes, retain this report against1f4 and recheck affected conclusions; do not silently retarget its verdict.

A contributor follow-up changing only the stale banner and recovery-report filename should receive a separate source-bound addendum; it does not retroactively change this original review or close browser execution. No additional product action is assigned by the reviewer.
