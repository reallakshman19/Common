# Q003 G4 r7 — Secure browser QA oracle for real native Core1A

**Issue #183 / 183-T4-G2-W1 and 183-T3-G2-W1** · 13 Oct 2026 Dubai · chat `6acd1e6b` · aim v3.1.0 · **operator instructions only; NO QA result is claimed here.**

## Exact private artifact and permitted operations

- Run against **the same native renderer-generated** `TEST/imo-research/core2-q003/.private/core1a/rendered/core1a.html` from **Grade9v3.5 `agent/183-q003-private-core2-test-6acc303b@f030a0aca51038575778de3489f75d1d629a6b74`**, independently comparing the on-screen version to the Owner-local `G-MATH-LINEAR-CONSTRAINT/rendered/core1a.html`.
- Verify the original remains SHA-pinned, the Core1A page matches **76,401 bytes / SHA-256 `d1fe23c43d1eeae67c69600beef1b5054c361854c3e5cd6742545859592998c0`**. If not, **STOP as SHA_MISMATCH** and do not transfer the result to this receipt.
- Use a real browser, fresh tab and a fresh site state (separate profile or cleared localStorage/sessionStorage for the TEST origin). Do not change the original/answer, author HTML, create a new page, mutate any repository, or upload private screenshots/DOM/full HTML.
- The two generated Core1A construction units each have a separate staged visual; the source question Q003 itself is **not** repeated as teaching input. All stage/transfer examples are expressly **AUTHORED**, not the original exam item. Some worked examples are purposefully present before exit attempt: Core1A is construction-first, not Core2's attempt-first primary screen.

## Minimum operator checks and pass or fail or not-run reporting

| ID | Real learner test | Grounded expected behaviour / record |
|---|---|---|
| A0 | Confirm exact generated page SHA, renderer identity, and fresh browser state. | Record `hash_match`, `renderer=render_core/2`, `fresh_state`, actual browser name/version and viewport. If SHA differs, stop. |
| A1 | At desktop (~1366×854), open the generated Core1A lesson without interacting. | Concept header, two construction-unit headers, two real action/why-valid/output steps **per unit**, key move, authored example, quick checks, formula reference tiles, trap repair and independent exit are accessible and intelligible; do not require unsupported `LEARNING_TRANSITIONS`. Record two real unit IDs and count. |
| A2 | Open each unit's **Formula reference** tile. | Both show the same authored relationship `k = y − x²`, explain input/output direction, constant `k`, and scope/validity conditions. No broken MathML or source Q003 verbatim stem/options. This is a math/render review, not independent subject approval. |
| A3 | In first unit use staged chips, then Next/Previous; repeat in second. | Both units have **at least two relevant selectable stages**, visible distinct content, accurate current-stage label/caption, no blank image or broken controls. Test actual arrow/buttons—not just static HTML counts. Record stages per unit, first-to-last and back, and whether all expected controls respond. |
| A4 | Keyboard-only from beginning: Tab/Shift+Tab, Enter/Space through section navigation, formula tile, stage chips, Next/Previous, misconception tile, and exit. | Visible focus, no focus trap, stage button action by Enter/Space; context remains readable. The diagram may be a separately scrollable labelled region, but the **page** should not need sideways scroll. Record first broken focus/control if any, without copying text. |
| A5 | At **375×812**, reload the page and exercise both visual stages, the equation disclosure and exit controls; optionally at ~768×1024 tablet. | No horizontal scroll of **document body** and no clipping of question, stage chips, equations, exit or commit. An intentionally scrollable diagram region is different from page overflow. Measure minimum actionable tap target; contract minimum **48 CSS px**, 8px gap where applicable. Report sizes/first offender, not unsubstantiated PASS. |
| A6 | Fresh browser state: inspect Core1A **exit-recall** before commitment and try `I have attempted this` with free-response empty and paper checkbox unchecked. | Blank commit is **refused** and the exit **Model answer** cannot be opened as visible or accessibility-tree content. A `<template>` may exist in document source by registered renderer design; it must stay inert/not accessible/visibly disclosed before commitment. Do not claim all answer bytes absent from HTML source. Record actual warning/focus outcome. |
| A7 | Type a meaningful **own response** into the exit text area (or independently solve on paper with the provided checkbox), then click commit. | Commitment enables **Model answer**. Open the answer; confirm it compares a newly authored changed-offset case rather than Q003 original/source options, gives a coherent why-valid and independent residual check. Record whether uncommitted answer stayed inaccessible and after-commit answer opens. This is **self-attempt**, not auto-grading. |
| A8 | Repeat A6–A7 **keyboard-only** (Tab to response, type, Tab to commit, Enter/Space; then Tab to disclosure, Enter/Space) with fresh state. | No hidden mouse dependency; visible focus follows usable order and protected exit only opens after valid commitment. |
| A9 | Inspect both trap/diagnose/repair disclosures and the two quick-check prompts. | Each clinic describes a real confusable wrong route and a bounded remedy; quick checks are not identical to the independent exit. Allow collapsed secondary disclosures. Count unit1/unit2 prompts; do not force golden's exact prose/panel count. |
| A10 | Side by side **actual Core1A vs candidate math golden** on Owner machine, at matched desktop and at 375px where practical. | Compare legibility, identity area versus registered **190px maximum target** at reference tablet, content flow, consistent stage labels, readable math, no portrait clipping, figure scaling, role sequencing and card usability. **Do not** use the rejected 2026-10-12 standalone prototype as acceptance reference. Record deviations; Owner alone determines visual/pedagogic acceptance. |
| A11 | **Core2 complement**, only if convenient in same session: at frozen `98ae06741f4d90865fcd313d609aeabba46826e2` browser original, check preattempt protected content absent from visible/accessibility tree, blank radio refusal, after-attempt disclosure and no accidental early answer on reload. | Prior Coordinator mouse/keyboard/375px evidence is already recorded; **do not rerun solely to restate it**. Focus on **new** accessibility/refresh/source-custody observation. Core2 original was 62,277 bytes SHA `827a8a99128601721c3c13dfd99806b5a563624526edfd8ba137ab8d4b64b6a0`; do not compare its bytes to Core1A. |

**A4 print**: keep `NOT_RUN` unless the actual native same-page A4 PDF is produced and the Owner inspects/decides it. **Screen reader**: `NOT_RUN` unless actually tested (keyboard and DOM/AX checks are not a screen-reader run). Pixel-diff comparison: `NOT_RUN` unless actually performed. An unattended automated suite or static HTML source inspection is NOT a browser observation.

## Safe return template (fill values, not question content)

```text
CORE1A_BROWSER_LOCAL | operator=Coordinator | tested_commit=f030a0aca51038575778de3489f75d1d629a6b74 | page_sha256=d1fe23c43d1eeae67c69600beef1b5054c361854c3e5cd6742545859592998c0 | browser=<name version> | fresh_state=<yes/no>
A0=<PASS/FAIL/NOT_RUN> | A1=<...> | A2=<...> | A3=<...> | A4=<...> | A5=<...> | A6=<...> | A7=<...> | A8=<...> | A9=<...> | A10=<...> | A11=<...>
staged_unit1_count=<n> | staged_unit2_count=<n> | narrow_viewport=375x812 | body_horizontal_scroll=<yes/no> | smallest_touch_target_css_px=<n/unknown>
exit_blank_refused=<yes/no> | exit_answer_before_valid_commit_inert=<yes/no> | exit_valid_commit_reveals=<yes/no> | keyboard_commit_reveals=<yes/no>
A4=NOT_RUN | screen_reader=NOT_RUN | pixel_diff=NOT_RUN | Owner_visual_verdict=PENDING | QRT_owner_decision=PENDING | rights=NOT_GRANTED
defect_first=<none or ID/role/behavior with no private question/answer/HTML>
```

Do not publicly send source Q003 stem, option strings, key, crux, author answer body, SVG inline DOM, screenshots with source, any generated HTML, or private JSON. PASS/FAIL/NOT_RUN must describe *actual operator observation*. A zero-gap structural receipt is not itself a browser, academic, accessibility, A4, rights, or Owner acceptance.

## Evidence identity

- Coordinator-reported zero-gap original Core1A plus candidate golden: [source-safe receipt](Q003_G4_R7_COORDINATOR_CORE1A_ZERO_GAP_RECEIPT_2026-10-13.json)
- Renderer and registered BP-CORE1A-CONSTRUCTION@1.8.0 in `Grade9v3.5@f030a0a`; the standalone TEST manifest deliberately lacks a portal root, so **LEARNING_TRANSITIONS is OPTIONAL and expected absent**.
- Owner packet: [183-T5 source-safe decision packet](Q003_G4_R7_OWNER_T5_REVIEW_PACKET_2026-10-13.md).
