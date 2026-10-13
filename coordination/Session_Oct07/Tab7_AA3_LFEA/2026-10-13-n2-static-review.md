# Tab7 LFEA — independent source-only N2 prereview, 2026-10-13

Chat: `new`. Plan `Tab7-r1`. Owner aim MA-AA3-1 r1 and task aim TA-AA3-E2E-1 r1 unchanged. Owning issue: [AA3 #51](https://github.com/reallakshman19/AA3/issues/51), parent #50. Historical product #49 acceptance `1/7`; #50 programme accepted slices `0/21`; U/E/R gates open.

## Start status / live recheck
- Re-fetched AA3 issue #51: **22 comments** at recheck, last known LA output [LA DONE plan #6138266622](https://github.com/reallakshman19/AA3/issues/51#issuecomment-6138266622); latest reviewer dispatch [FOR LA #6138836435](https://github.com/reallakshman19/AA3/issues/51#issuecomment-6138836435). **No subsequent LA DONE execution receipt on #51**. Do not interpret plan as evidence of running N0/N1.
- Fresh [draft PR #48](https://github.com/reallakshman19/AA3/pull/48) head `f26689a22598bc2c374c335a821d87d83493a02d`, base/main `a8650bbe825d3fd217bab4974bcb0f0817c26158`; [draft PR #54](https://github.com/reallakshman19/AA3/pull/54) head `82afd52f1eea1ff7b342db8e7ab6b1d5ddfa79f7`. No pre-existing PR changed.
- N0/N1 LA measurement outstanding; N2 code audit independently useful but **does not admit a repair** until measured exact CSS hit-point and state invariants.

## Exact-head static source review (read-only)
Files directly fetched from `AA3@f26689a`; Git blobs:
- `src/workspace/lfea-diagnostics/lfea-accdb-repair-workspace.js@3c812b1b60613df1ba39f6d9d7c754234a5523da`.
- `src/workspace/lfea-diagnostics/lfea-error-check.css@9176470ce42b2e6dae52456fd1d2019e1c924794`.
- `src/workspace/lfea-model-review/lfea-geometry-review-svg.js@1bc8aadc6a33a64413acdbbec4bb9d27ef6ea43c`.
- `src/workspace/lfea-model-review/lfea-model-review.css@6f03bb3723ea11dcabf04c05e858e7dca6a6fc0e`.
- `src/workspace/lfea-svg-viewport.js@0e6395b25e42ee376f7ac62a5fbe7fb1dcd463af`.
- Original real-model spec `e2e/lfea-pipeline-accdb-real-model.spec.js@1a5bf9abdb16613861de0fe0ed37ec240bfc5ead`; lines 606–661, unforced E1 click at line657, real inspector/field assertions at lines658–660.

### Critical N2 risks and required evidence
1. **ViewBox mutation without rerender.** `lfea-geometry-review-svg.js:256–300`: wheel and pointerpan update `viewBox` on existing SVG; only persisted state callback, no repair-workspace rerender. A post-render-only E1 displaced hit-rail computation may be stale after wheel/drag, focus narrowing, normal button zoom, and 200% zoom. Evidence must assess collisions/visibility in actual CSS pixels at multiple allowed viewBoxes, not only initial fit; if no bounded safe placement, proposal fails closed.
2. **Later paint layers and support obstacles.** `lfea-geometry-review-svg.js:126–169` appends source segments first, `:171–226` appends node markers/restraint glyphs afterward; CSS `lfea-model-review.css:55` gives restraint invisible hit circle `pointer-events:all`. The rail may be covered by later-painted node or support targets even if it avoids the original E2 rounded cap. Browser evidence needs `elementsFromPoint` at actual proposed rail/E2/node centers and ordering.
3. **Listener, DOM identity and keyboard restoration.** Original interactive SVG line has `click` / Enter/Space callbacks closed over exact source segment at `lfea-geometry-review-svg.js:132–158`. Workspace `:513–535` captures keyboard focus prior to DOM rebuild, `:221–229` locates genuine `line[role=button][tabindex=0]` by `dataset.segmentId`, and `:247–256` rerenders then restores focus. An added cloned surrogate can silently lose listeners; extra matching `data-segment-id`/role/tabindex can corrupt `.first()` original test, source reverse selector and natural Tab order. Exactly one bound interactive E1 selector must remain; physical geometry stroke/leader are noninteractive, nonselector, aria-hidden.
4. **Selected stroke expansion and true physical geometry.** Workspace CSS `:493–497` sets selected `[data-segment-id]` stroke width 5 and filter shadow; global source line `lfea-model-review.css:47` has rounded width 2; initial E1/E2 clearance does not prove selected-rail/E2 clearance, and selected styling can mislead a user about physical source. Evaluate selected/unselected states, focus styles, safe E2 pointer activation, identity/geometry before/after fit/pan/zoom and disclosure of display-only displacement. Source fields and original test values/timeouts stay unchanged.

Reviewer supplemental instruction posted verbatim as [FOR LA #6140040387](https://github.com/reallakshman19/AA3/issues/51#issuecomment-6140040387). It requests LA to integrate these risks into upcoming N0/N1 `LA DONE:` evidence. No browser executed, no trace/screenshot independently opened, no changed preparatory cases/CI/product/tests touched.

## TASK EVIDENCE — TAB7-N2-SOURCE-PREREVIEW
Task: TAB7-N2-SOURCE-PREREVIEW
Goal (issue AC): #51 T02/E2; N2-T1..T3 inspect bounded two-file remedy, E1/E2 identities and rollback/safety contract
Status: PARTIAL
Met: partial
Done: Compared exact-head source and original oracle; enumerated four concrete viewBox, hit-paint, binding/focus and selection risks; posted FOR LA supplemental evidence requirements
Code: AA3 feat/issue-47-accdb-repair-workspace @ f26689a | PR #48 untouched; Common main @ [this log's commit]
Tests: GitHub source blob/readback and original test source inspection -> PASS (static); real Chromium E1 CSS hit-stack -> NOT_RUN pending LA; actual N2 browser matrix -> NOT_RUN
CI: existing shortcut #38271936864 -> FAILURE (21 pass/1 fail/4 not run); PR #54 EMP.1 failures #38339123833/#38339123857 unchanged
Evidence: https://github.com/reallakshman19/AA3/issues/51#issuecomment-6140040387
AC: P-01 unsupported design proposal -> detailed source-level risk/proof contract, still NOT APPROVED; product 1/7 unchanged
Claim: INDEPENDENT (static only)
Blocker: PERSON - LA actual N0/N1 browser evidence; OWNER - separate writer reassignment and scope/branch authority before implementation
Next: TAB7-N0-REMAINDER -> TAB7-N1-HITSTACK -> TAB7-N2-MEASURED-REVIEW

## Hard prohibitions
No new changes to PR #48/#54, source/fixture/oracle/tolerance/workflows/physics, CI rerun, forced click, long timeout rerun, scheduler restart, changed-prep Run, merge/rebase/close or deployed release. Work remains READ_ONLY and N2 admission remains conditional.
