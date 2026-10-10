# STAGE1_SOURCE_PACKET_V2 — Core1B original-source investigation

**Record:** `STAGE1_SOURCE_PACKET_V2` · **Mode:** PLANNED_RUNNER_STAGE1 / TASK_AWARE · **Status:** SANITIZED_CANDIDATE_NOT_RELEASED · **Parent:** [Common #890](https://github.com/reallaksh19/Common/issues/890) · **Original case:** Grade9v3.5 Core1B / QRT three-learner-case golden investigation.

**Original-only research packet.** Its contents are curated historical Owner WHAT/WHY, the three learner-facing task inputs, and immutable source/fixture references. It does not disclose the previous preparer's analysis, suggested research questions, alternative designs or implementation plan. This is a historical investigation, not current acceptance.

## A. Original Owner WHAT and WHY (graded)

**Recorded Owner utterances**, reproduced from the historical case packet, whose source is the preceding conversation; this file does **not** itself independently authenticate that past chat:
- “now shoe me real 3 cases, were I can try as student”
- “buttons are not working”
- “could have been a better message which kid will feel motivated.”
- “Where is the answer1”
- “save 3 samples, covering diff 4x7 matrix, we will have these as golden fixtures, then we save in your PR”

**Task-aware intent:** Help a Grade 9 learner attempt and repair reasoning on **three distinct cases** within an existing 4-band × 7-demand QRT domain, then make the cases reliable golden regression examples. The student-facing behavior, actual explanations, accessibility of controls, representation/authority and valid QRT classification all require independent investigation. The historical source, not the packet writer's proposed fix, decides what the application originally does.

**Claim boundaries:** The three cases do not establish acceptance for all 28 possible matrix cells, a real learner trial, an official textbook/exam license, teacher authorization or a released browser journey. Historic sources and learner examples must be distinguished from real accepted curricula and human-observed learning. The **actual Agent A task-start SHA is UNKNOWN**; do not confuse the research cutoff with it.

## B. Learner-facing problem inputs (not solutions or expected goldens)

**Case A / consecutive factors:** A learner checks `t=3,4,5` and observes `(t−2)(t−1)t` divisible by 6; they claim checking these points proves the statement for every integer `t≥3`. Help the learner explore whether this reasoning justifies a universal statement. A changed situation involves two consecutive factors. **Do not supply a predetermined diagnosis or expected answer**.

**Case B / algebraic identity:** A learner writes `(x+2)²=x²+4` after noting agreement at `x=0`. The learner must investigate whether the asserted equality is general and consider input values where it may be true.

**Case C / movement and averages:** A student travels `60 m east` then `60 m west` in `40 s`, finishes at the start, and concludes average speed is zero. A changed journey is `60 m east` followed by `30 m west` in `30 s`. Investigate what the original UI/workflow actually lets students express or correct.

All three are task inputs, not approved independent classifications, teacher-reviewed answers or an Agent A solution design.

## C. Historical source cut-off (mandatory; no moving refs)

**Original repository:** `reallaksh19/Grade9v3.5`  
**Permitted historical cutoff:** `778eb35a70517a46108ad0a5dc01dfc89f61c0e3`  
**Unchanged source-only snapshot tree in Common:** `927192e073c78ef464aa737738b239d4c9f3874c` at [`Common@d60c366`](https://github.com/reallaksh19/Common/tree/d60c36605e988dcc160647421973f170fd87e0eb/relay/CORE1B_GOLDENS_RUNNER_20261009/SOURCE_SNAPSHOT/Grade9v3.5). **Source fixture/read allowance is exactly the nine files below** and must be enforced by an external controller, not guessed from this table.

| Source path relative to historical Grade9 repo | Verified original Git blob |
| --- | --- |
| `Shared/quality/question-demand-matrix.v1.json` | `3779a53ae7d20efbb4644bc3f9243909e93dc145` |
| `Shared/vocabularies/cognitive-demand.v1.json` | `b19b39586632cabb637a61fd05fdaaef105305ef` |
| `Shared/tools/question_review_matrix.py` | `42a51307d8d0f4b5254c610f7fefd62e27a09cd5` |
| `Shared/tools/render_core.py` | `9302174e1491138a459a80e9d3f176b83b19e6d7` |
| `TEST/imo-research/pilots/core1a-render-qualified-divisibility.v1.json` | `e8b1dcae1014f9a9a2cce7c2489b21b36c049f81` |
| `TEST/products/core1b-authored-reconstruction-journey.manifest.json` | `35b57884c605e324542201d99c62ff42174a2699` |
| `tests/test_core1b_reconstruction_maturity.py` | `b340269974323da72e4bd3d58ae19449728bb852` |
| `tools/site-audit/core1b-reconstruction-audit.mjs` | `08db5ee227a5ce0f16f8431e1276684ed7a9474d` |
| `.github/workflows/core1b-reconstruction-maturity.yml` | `3fbd48692b1f302d7d709ee0f1245f6f4cef4973` |

**Historical evidence/acceptance boundary:** Source blobs are real original bytes, not proof that the application currently works. The TEST example is authored TEST material. The corresponding authentic positive XML/interactive student transcript for all three cases may not exist. No browser, model, learner or actual current CI pass is claimed. If a direct dependency or authentic fixture is not present, record `NEEDS_OPERATOR_SOURCE_DECISION`, not an unauthorized repo search.

## D. Independent B method — ordered questions, not prescribed answers

**Part A, historical system baseline FIRST.** Without assuming a fix, discover the historical authority for a QRT cell and how a learner-facing attempt/explanation appears. Trace at least one actual original producer → transformation → downstream consumer → **observable student interaction/output** from pinned source. Cite the exact allowed paths/functions and, where actual permitted artifacts support it, one positive witness and one meaningful boundary change. State what is observed, what is merely asserted by a test or mock, and what requires a real browser/learner to verify. **Stop the factual section without selecting an architecture, drafting a PR or proposing an implementation plan.**

**Part B, original-problem reasoning AFTER Part A.** Compare *your own* observed historical behavior with the Owner's desire for three meaningful student journeys. Independently identify where the existing behavior may fall short, what would falsify that judgment, and what alternate approach **or no-change decision** may be warranted. Use source/consumer evidence, authentication grades and actual negative cases; never fabricate learner evidence, prescribe changes without proof or copy a current Agent A plan. Record unanswered, source-derived questions and a **provisional** investigation sketch. Do not publish a source-current implementation plan until the later separately authorized Stage 2.

**Output shape:** [`STAGE1_RECONSTRUCTION_V1`](../../TEMPLATES/STAGE1_RECONSTRUCTION.md) with Part A first, Part B second. An independently isolated **new Runner B** must author the artifact; Agent A may not write it. Only a controller can attest source-read isolation and freeze the submitted Markdown bytes.

## E. Strict visibility and STOP

- **STAGE1_ONLY; READ_ONLY.** No current Grade9 main/PR, current Agent A issue/comments, plan or diffs, Agent A answer key, current product UI, recent tests, Stage 2, operator rubric or unrestricted Common/GitHub connector access.
- The snapshot is *hosted inside the broader Common repository* and is therefore **not a technical sandbox**. Full GitHub connector access would violate source isolation. An external controller must enforce both source-path/commit limits and fresh-session context.
- If a forbidden read surface is accessible or current A material reached B, output `STAGE1_ISOLATION_NOT_ENFORCED` or `STAGE1_CONTAMINATED` instead of submitting a supposedly independent result.
- **Status:** `INPUT_CANDIDATE_PREPARED`, not Runner launched, independently reconstructed, frozen, Stage 2 qualified, approved or granted source writing.
