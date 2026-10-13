# Start a QRT Blueprint Mapping Agent — exact prompt for a new agent

This is **not automatically installed or running** merely because a SKILL.md exists on GitHub. The Owner/user can load this skill into a compatible coding/ChatGPT agent, provide it with GitHub read/write access for an **explicitly authorized branch**, and invoke it with one question or bounded question set. Keep it separate from the person signing academic review and the Owner decision.

## Minimal standalone start

In a new agent/session with repository access, use the following task text; replace only the bracketed parameters:

```text
Act as the QRT Blueprint Mapping Agent.

First read the entire SKILL.md and mandatory companion files at:
https://github.com/reallakshman19/Common/tree/<PINNED_SKILL_COMMIT>/skills/qrt-blueprint-mapping-agent

Task repository: reallakshman19/Grade9v3.5
Authoritative issue/plan: <ISSUE URL, OWNER AIM/LABEL REF>
Question: <EXACT SOURCE RECORD PATH AND QUESTION ID>
Question/source ref: <FULL SOURCE SHA>
Existing manifest (if any): <EXACT PATH>
Existing golden/comparator (if any): <FIXTURE PATH AND LOCK SHA>
Execution mode: ANALYZE_ONLY initially. Produce DRAFT_TEST_BUILD only on my authorized isolated branch.
Permission: read the sources; do not modify main or any frozen golden, blueprint registry, live public route or source rights.
Output: first the complete question-first QRT cognitive and difficulty rationale with strongest counter-demand, exact protected W, and a role-specific active blueprint mapping.
Only if classification passes the falsifier and source rights allow it, build with Shared/tools/render_core.py and compare the native render against the pinned golden using same-question exactness or cross-question semantic technique as appropriate.
Collect genuine HTML/receipt, math, changed-case, H1-H3/S1-S3/P1-P3/M1-M3, pre/post attempt, site asset and CI evidence. Use the unsigned mapping-record template and structural validator.
Issue a review-ready, source-SHA-bound packet and request a distinct qualified academic reviewer and separate Owner decision. Your own work is SELF_REVIEW, never independently accepted.
Stop with a named blocker if any required authoritative source, right, actual native fixture or learner protected W is missing or contradicted.
```

## One ready-made safe pilot (analysis only)

Use the old authored TEST MODEL exemplar at:

- Issue [#201](https://github.com/reallakshman19/Grade9v3.5/issues/201)
- Draft [PR #205](https://github.com/reallakshman19/Grade9v3.5/pull/205)
- Exact source `TEST/imo-research/qrt-d2/model.v1.json`, question `Q-TEST-QRT-MODEL-D2-PRIMARY`, parent authored source SHA `eb3cf06646f00bf208084e794b41b4d8d83135b6`
- Existing five-role manifest `TEST/products/imo182-qrt-d2-model.manifest.json`
- Comparison fixture `golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshot-lock.json` and 7×4 QRT review, all unsigned

**Challenge**: the source instructs the learner to choose a variable for the **LARGE cup** count, but the claimed protected W says selecting the category is independent learner work. A good agent will spot the contradiction **before generating new pages**. It will propose either a narrower MODEL W (complement + weighted equation) with credible band evidence, or a candidate full five-role revision that removes the cue. It will **not** declare either academically accepted, publish an authentic Core2 source, or modify the QRT golden.

Pass/fail for this pilot should be assessed by the **quality of its evidence and its identified falsifier**, not by whether it generates five green HTML pages.

## General running model

- A **skill** is the reusable operating method, with deterministic templates and preflight tests.
- A **task run** is one agent invocation on actual source/issue/manifest at an exact ref, optionally writing to an isolated authorized draft PR.
- A **qualified Reviewer** is a distinct person (or separately authorized, appropriately qualified principal if the project's protocol allows it) making genuine mathematics/QRT judgments. Same-agent "new persona" is not independent.
- The **Owner** approves cell/golden, source rights, merge and publication separately.
- An **automation** is optional later; adding a skill file by itself schedules nothing.

To use this package in more subjects, retain the three-layer separation and substitute the project-specific demand/blueprint/golden authorities. Never carry Grade9's five-role or exact 28-cell contract to a subject with a different governing registry.
