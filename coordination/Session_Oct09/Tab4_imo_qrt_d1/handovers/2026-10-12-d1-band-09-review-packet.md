# D1-BAND-09 — academic review request, signed verdict pending
2026-10-12 | chat=6accecfd | Tab4 | plan=r2 | issue=Grade9v3.5#182 | aim=v3.1.0 label_sha=2ff9246 | outcome=O2 (prerequisite) | user=no

**Disposition: PARTIAL / INDEPENDENT_REVIEW_PENDING.** A distinct, demonstrably qualified academic reviewer has **not** signed a source-SHA-specific verdict. This is the D1 successor's review packet and falsifiable preliminary judgment, **not** an independent academic approval, not an adopted QRT classification, not Owner acceptance. Proposed reviewer disposition: **REVISIONS_REQUIRED** if the protected W is independent model selection, because the preattempt learner-facing text overtly identifies its model family and explicitly rejects the candidate wrong operation. An independently qualified reviewer must evaluate this against D1's allowances for scaffolding, may disagree, and must sign.

## Exact read-only inputs

- Current [draft PR #192](https://github.com/reallakshman19/Grade9v3.5/pull/192) `0949e4866b06aefd8b866fc3d2565f434e19bb93`, stacked on draft #190 `67c34dababb0da0ef7d5f4a532bfcf3119754961`, both open/unmerged when checked.
- MODEL authored source `TEST/imo-research/qrt-d1/model.v1.json` blob `5347aa49c7a96759128c994aa7a4e828c2f590e0`, question ID `Q-TEST-IMO182-D1-MOD-CORE2A-EQUAL-GROUPS-APPLICATION`; exact source: https://github.com/reallakshman19/Grade9v3.5/blob/0949e4866b06aefd8b866fc3d2565f434e19bb93/TEST/imo-research/qrt-d1/model.v1.json
- Official matrix `Shared/quality/question-demand-matrix.v1.json` blob `3779a53ae7d20efbb4644bc3f9243909e93dc145`: MODEL decisive act = choose/formulate governing model, W = final model/strategy choice/formulation. D1 rule = leave *one meaningful identification, relation, translation or execution decision*; narrowing the route is allowed but performing W is not. D2 rule = leave *connection/choice plus its execution*. That distinction must be judged from learner-facing prompts, not metadata.
- Exact hosted original `MODEL-D1` rendered HTML [run 38258022860, artifact 11751335796](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38258022860); original immutable golden [run 38215683516, artifact 11732117118](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38215683516); [D1-OBS-08 observation](https://github.com/reallakshman19/Common/blob/d19587257ff918f896040f9f2f5003c535734a12/coordination/Session_Oct09/Tab4_imo_qrt_d1/handovers/2026-10-12-d1-obs-08.md).
- Adjacent *independently authored research comparator* D2 MODEL PR #191@`24efd758570e41d1e4930ad6235789b10669d7a7`, source blob `eabc0626c978989a7a40dcc1d2dd22adf611b359`, question `Q-TEST-QRT-MODEL-D2-PRIMARY`: nine drinks of two prices, 48 total credits; learner chooses variable and connects `9-x` with weighted revenue `4(9-x)+7x=48`, solves, checks whole numbers. Not an approved QRT comparator; D2 academic acceptance likewise is pending. https://github.com/reallakshman19/Grade9v3.5/blob/24efd758570e41d1e4930ad6235789b10669d7a7/TEST/imo-research/qrt-d2/model.v1.json

## Independent desk assessment — preliminary, not a qualified reviewer signature

Mathematics: six equal trays with four seedlings each implies six groups of four, `6×4=24` seedlings; `6+4=10` is not the six groups total. CORE1A separate `3×5=15`; CORE1B falsifies `4+2=6` against `4×2=8`, then independent `2×1=2`; CORE2B inverse `24÷4=6` trays. No mathematical counterexample was identified to these claims. Source answer verification status `CHECKED_BY_AUTHOR`, *not signed independent reviewer proof*.

The authored `CORE2A` stem says “Build a mathematical MODEL”, already describes six “identical” trays with four in “EACH”, and **specifically tells learner to explain why adding `6+4` is not the model**. The `CORE2A` rendered page initial title/meta directly names the **equal-groups model**; initial figure caption text says **build the groups-of model yourself**. H1 prompts identifying containers versus contents; H2 expressly states “A valid group model has a separate group for every tray” and “repeating the same group.” H3 remains after a nonblank attempt, so the result 24 is gated; nevertheless the *method choice* is cued before it. The criterion at risk is **W=choose a model**, not the numerical result gate. This is **evidence for academic review**, not a demonstrated QRT rejection. Alternative: the primary meaningful W left may instead be mapping the group count to the equation, consistent with `APPLY-D1` / `REPRESENT-D1`, not necessarily `MODEL-D1`; academic reviewer must decide.

D1-vs-D2 countercase: D2 requires constructing and coordinating two separate conditions (total item count, total cost) and solving for a missing variable, so is more connected than the one-equation D1. This does NOT mean D1's explicit methodology can be waved through simply because the D2 item is harder. Nor does a cue automatically reclassify D1 as D2. The reviewer must judge whether, after allowed D1 support, **one meaningful model-choice/identification act remains unperformed by the page**, and whether the Core2B inverse transfer restores independent W on a *different* page versus repairing the primary Core2A cell.

### Cell table, as of this exact source

| Named QRT cell | Technical status | Independent academic W/band | Owner accepted |
| --- | --- | --- | --- |
| QRT-REPRESENT-D1 / D1-REP-01 | 5 registered sole-renderer HTML roles, prior hosted worker PASS | pending | NO |
| QRT-RETRIEVE-D1 / D1-RET-02 | 5 registered sole-renderer HTML roles, prior hosted worker PASS | pending | NO |
| QRT-EXPLAIN-D1 / D1-EXP-03 | 5 registered sole-renderer HTML roles, prior hosted worker PASS | pending | NO |
| QRT-APPLY-D1 / D1-APP-04 | 5 registered sole-renderer HTML roles, prior hosted worker PASS | pending | NO |
| QRT-MODEL-D1 / D1-MOD-05 / D1-BAND-09 | 5 registered sole-renderer HTML roles and new independent local golden/AX check PASS | **review pending; preattempt MODEL cue risk** | NO |
| QRT-SYNTHESIZE-D1 / D1-SYN-06 | not authored at assessed commit | pending | NO |
| QRT-JUSTIFY-D1 / D1-JUS-07 | not authored at assessed commit | pending | NO |

**Coverage: authoritative 0/28 accepted.** The 5/7 count denotes hosted *technical* packages, not learning outcomes or Owner-accepted QRT cells.

## Required qualified independent reviewer response (signed decision requested)

Please have a *named, independently qualified mathematics/QRT academic reviewer distinct from the D1 author* inspect the exact source SHA above and authentic hosted learner-visible Core2A preattempt/AX+H1/H2/H3 states, worked Core1A, repaired Core1B and changed Core2B, as well as D2 comparator. Reply on issue #182 (or a linked signed record) with:

1. **Reviewer**: real identity, qualified role/affiliation and explicit independence from the D1 author.
2. **Pinned material**: Git commit `0949e4866b06aefd8b866fc3d2565f434e19bb93`; blob `5347aa49c7a96759128c994aa7a4e828c2f590e0`; QRT `QRT-MODEL-D1`; candidate run `38258022860`.
3. **Verdict**: PASS / REVISIONS_REQUIRED / RECLASSIFY, with named *actual* learner-owned W, D1-versus-D2 rationale, mathematical correctness, hint exposure/timing and primary question versus changed transfer separation; identify which exact words/figures require an authored-only revision if necessary.
4. **Signature**: reviewer identity and dated source-specific signed/attributable decision URL. Do **not** write `accepted_coverage_numerator`, because QRT acceptance is a **separate Owner decision**.

Unless that signed reviewer verdict is provided, **D1-BAND-09 remains PARTIAL with PERSON blocker**, even though the review packet is ready. Existing TEST-only development of SYN/JUS can proceed independently. If revisions are required, D1 author edits only own TEST, re-renders through `Shared/tools/render_core.py`, obtains fresh SHA/Chromium/frozen-golden evidence and re-requests review. Do not alter Shared or frozen golden absent an evidenced O3 blueprint gap.

## CI red classification (separate from academic task)

**`SHARED_CI / technical lead`, not D1-BAND-09-created.** Independently fetched full workflow logs for PR#190 base run `38231707421` (job `114752508415`) and PR#192 exact-head run `38258022475` (job `114841031352`). Both first fail the same named step **“Topic independence guard — scan engine and tooling”** with precisely **`2385 violation(s) in 272 scanned file(s)`**. Both also report `test_browser_entry_matches_python_intake` failing. Thus shared failing baseline is demonstrated. PR#192's canonical assurance `38258022444` also RED; no waiver, rerun or repair. Other failures or TEST/generated-index contributions have not been ruled out. LEAD-CI-01, under technical-lead authority, is conditional on actually blocking O1; D1 academic review does not take over shared CI.

**User impact:** nothing has changed on the real/public learner route; only review evidence and request are made available. No actual signed reviewer or Owner decision is present in inspected issue/PR records at this checkpoint.
