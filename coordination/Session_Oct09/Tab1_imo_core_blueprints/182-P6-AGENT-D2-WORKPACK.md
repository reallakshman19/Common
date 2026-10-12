# Worker handoff: AGENT-D2 — exactly seven D2 QRT cells (Grade9 issue #182)

**READ THIS FILE FIRST.** Written 2026-10-12 from issue #182 and actual pinned files; no inherited chat assumptions. Owner master `Common/main:relay/AIM/IMO-CORE-BLUEPRINTS.yaml` **v3.1.0 / label_sha 2ff9246**. Outcome **O1** actual renderer five-role page vs Owner candidate golden, **O2** one named cell + independent decision, **O3** proposed blueprint change only when golden proves missing capability.

**Status: INSTRUCTIONS READY, WORKER NOT YET VERIFIED AS RUNNING.** No task credit for merely creating this handoff. The lead owns fixes for missing controls, collisions and CI diagnostics; you must fix your own documented, scoped authoring defects immediately without bouncing implementation questions to the Owner.

## Mandatory naive-first preflight — check fresh repo, do not trust a remembered head

1. Read original issue [#182](https://github.com/reallakshman19/Grade9v3.5/issues/182), its latest comments, the v3.1.0 master **not v1.1.0 in the issue's historical introduction**, and the last pinned source commit. Read canonical `Shared/quality/question-demand-matrix.v1.json` and `TEST/imo-research/verification/qrt-proposed-coverage.v1.json`; baseline QRT accepted **0/28** unless Owner signed changed.
2. Read registered `Shared/web/interactive-page-blueprints.v1.json` and actual `Shared/tools/render_core.py`, not hand-edited public HTML. Pin the SHA. Registered five roles: Core1 `BP-CORE1-ORIENTATION@1.1.0`, Core1A `BP-CORE1A-CONSTRUCTION@1.8.0`, Core1B `BP-CORE1B-RECONSTRUCTION@1.1.0`, Core2A `BP-CORE2A-SUPPORTED-APPLICATION@1.1.0`, Core2B `BP-CORE2B-TRANSFER@1.1.0`. Mature optional Core2 `BP-CORE2-SOURCE-QUESTION@1.11.0` is **not permitted authentic source work** in this lane; borrow its support policy only.
3. Check recent PR [#190](https://github.com/reallakshman19/Grade9v3.5/pull/190) exact head (was `67c34dababb0da0ef7d5f4a532bfcf3119754961`), approved **H3 AFTER_ATTEMPT** source/renderer patch, and [CI 38231707376](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38231707376). Base new TEST work on a **verified exact snapshot** with that correction, or explicitly import the correction as isolated test dependency; document stacked ancestry instead of pretending it is merged main. H1/H2 remain requestable; H3 must require nonblank committed attempt. Old frozen HTML golden `G-IMO-G9-FIVE-CORE-20261012` predates this H3 fix, so an exact hash comparison against changed Core2A will properly FAIL; preserve the frozen bytes and ask lead to route new successor golden acceptance, not weaken the gate.
4. Read the [four-agent plan](182-P6-FOUR-AGENT-28-QRT-CELL-EXECUTION-AND-MONITORING.md), [repository reuse audit](182-P6-RECENT-PR-REUSE-AND-MATURE-BLUEPRINT-AUDIT.md) and canonical [monitor](182-P6-28-CELL-AGENT-MONITOR.json). These are *not* a substitute for actual record/CI re-read.
5. Check source/question **rights** before any admission. Organizer sample Q004/Q006/etc and 68 authentic Core2 Qs are research-only/not admitted, Tab2 #183 separately governs them; create **wholly original `AUTHORED` TEST** items if no source-rights-cleared source exists. Do not use official text, official logos, PDFs, KEY, exam year as claimed provenance.

## Owned seven cells and actual reusable starting evidence

| `QRT-RETRIEVE-D2` | Author non-trivial connected retrieval/application; if only single criterion move, reclassify D1. | UNSTARTED, no academic/Owner acceptance |
| `QRT-EXPLAIN-D2` | PR #140 authored TEST review fixture TEST/imo-research/golden/imo-327-explain-d2.v1.json; it is NOT a full package/product. | UNSTARTED, no academic/Owner acceptance |
| `QRT-APPLY-D2` | Author known-procedure check and connected execution in changed context. | UNSTARTED, no academic/Owner acceptance |
| `QRT-MODEL-D2` | Official Q008 research proposal only. Author a distinguishable D2 selection/connection. | UNSTARTED, no academic/Owner acceptance |
| `QRT-REPRESENT-D2` | Official Q002 research proposal only. Author distinct 2-step invariant mapping. | UNSTARTED, no academic/Owner acceptance |
| `QRT-SYNTHESIZE-D2` | Author short two-idea dependency with one learner-owned connection. | UNSTARTED, no academic/Owner acceptance |
| `QRT-JUSTIFY-D2` | Existing actual authored TEST Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF in five-role #190; new after-attempt H3 exact CI passed. Need distinct successor golden, independent band/QRT review. | UNSTARTED, no academic/Owner acceptance |

**Start pilot: `QRT-JUSTIFY-D2`**. `D2` band learner-owned W policy: Leave a short connection/choice PLUS execution to learner; H1/H2 can orient but protected W must remain. Owner rule: authored Core2A H3 AFTER_ATTEMPT ONLY.

## A single cell's implementation instructions (repeat seven times, no cloned filler)

**Step A — identify, verify, protect W.** One unique primary cognitive demand **D2** + one justified D band, exactly one main `QRT-{DEMAND}-D2` cell; record `X` problem, `Y` prelearned bridge, `Z` proposed route and `W` protected decisive act, wrong idea, diagnostic, replacement rule, independent check and adjacent-band comparison. If the user can't fairly do the D2 W under that question, write `REVISIONS_REQUIRED` and repair the question or propose reclassification; **never insert a cosmetic tag**.

**Step B — author linked TEST package without overriding approved Core1B.** Use band-owned unique paths/record IDs under `TEST/imo-research/qrt-d2/`; create a genuine microtopic and separate task-specific Core2A and changed Core2B questions, warranted answer routes, safe first-stage SVG, staged Core1A construction with reduced-support exit, and cell-specific Core1B wrong route + falsifying boundary + independent test. No copy/paste of the universal triple proof across demands; any reused mature component must be adapted to this question's actual W. Source schema must validate `Shared/library/package.schema.json`. Keep original Owner-complete Core1B package untouched.

**Step C — use existing blueprints, not written HTML.** Create one unique manifest `TEST/products/imo182-qrt-d2-{demand}.manifest.json`, `output_roles=[CORE1,CORE1A,CORE1B,CORE2A,CORE2B]`, `selection.core2=[]`, one owned microtopic and exact authored Core2A/Core2B IDs. Run **sole renderer**:
```sh
python Shared/tools/render_core.py build \
  --manifest TEST/products/imo182-qrt-d2-<demand>.manifest.json \
  --out build/imo182-qrt/d2/<demand> --draft --reference
```
If the renderer cannot run, **BLOCKED_RENDER**, not an invented page. A failure in your record/manifest/schema/fig should be fixed by you; shared renderer bug gets precise 10-line reproduction sent to lead, who fixes it centrally.

**Step D — same-head, actual-browser and subject QA.** Demand five generated role HTML files and index with SHA256 receipt; no `REFERENCE` depth gaps; preserve baseline Owner frozen-golden exact-lock separately, and **benchmark novel cell against corresponding five role goldens by technique/slot** (Core1 orientation, Core1A stages+independent exit, Core1B misconception reconstruction/boundary, Core2A hint protected W+attempt, Core2B invariant and truly new decision). Exact bytes of new question naturally differ; don't fake a match by cloning old pages. Verify actual stem correctness, exhaustive cases/conditions, independent check, no answer in SVG `<desc>`/alt/aria/quickcheck, refusal of blank attempt, H3 AFTER_ATTEMPT, solution post attempt, Core1B extra boundary gate, repaired exit after changed givens, Core2B different task. Use Chromium/Playwright actual generated HTML and tests; not just regex.

**Step E — review artifact first, Owner questions last.** Package five actual sole-renderer HTML links + five golden comparisons + exact SHA/CI run & artifact, named cell and protected W, 12 H1–H3/S1–S3/P1–P3/M1–M3 review evidence (meaning, not rung counts), mathematics independent verifier, source custody/rights evidence, qualified reviewer verdict blank, Owner acceptance blank; reviewer can export notes but not self-accept. This cell's **five outputs count only after receipt and role QA**; acceptance count remains **0/28 until signed independent review+Owner decision**.

## Scope, CI and mistakes I expect you to catch yourself

- Never revert or bypass H3_after_attempt on PR #190. Older frozen golden must fail changed Core2A byte equality; do not overwrite or weaken it. Do not claim owner accepted D2.
- **Never fix a failing golden by editing frozen HTML or git snapshot; never author a second renderer or standalone composer HTML.** Golden gap O3 requires specific missing registered affordance, before/after learner evidence and lead approval.
- Owner decision `D-182-2-H3` **timing approved after attempt**, independent academic proof/difficulty acceptance **still open**; do not ask the Owner to restate the timing.
- Original source Core2 rights absent; source refs from #140/#155/#166 are on **unmerged drafts**, academic scope unaccepted, and require exact blob/read + independent adoption. No copyrighted source promotion.
- Keep dedicated DRAFT PR and scope files owned by D2; no `Shared/tools/render_core.py`, `Shared/web/interactive-page-blueprints.v1.json`, `relay/STATE.yaml`, shared printer, canonical accepted QRT file or other agent's manifest changes. Escalate only **specific reproducible shared-tool defect** to lead, not a generic "blocked" question.
- Every PR/head must yield: status `SCHEMA_PASS/RENDERED_TEST/GOLDEN_TECHNIQUE_PASS/REVIEW_READY/BLOCKED_...` with exact source SHA, actual learner HTML SHA per role, CI run URL, source custody and next single action. Don't use 7/7 issue checkboxes as progress.

## Lead-integrated handoff: no chat ping-pong

Post scoped issue #182 **TASK EVIDENCE** beginning:
```text
Outcome: O1
For the user: Actual learner-visible TEST change, or "none (blocked)".
Proof: <exact-head CI + actual renderer HTML artifact>
Task: AGENT-D2/QRT-<DEMAND>-D2
Status: DONE/PARTIAL/BLOCKED
Code: <draft PR + exact head>
Tests: <command and actual result>
Golden: <old owner baseline digest, semantic diff, new exact role SHA>
QRT: proposal only, reviewer pending, accepted=0/28
Blocker: NONE or SPECIFIC reason + self-attempted fix + lead-owned action
Next: <single next cell or source rights hold>
```
Don't await a routine answer from Owner. If content/maths/figure/CI fails, fix and rerun yourself; the **lead personally patches missed instructions** and records corrected evidence. No worker self-assigns approval, owner signature or merge/release.

**Agent completion criterion:** seven distinct cells each with legitimate right-sized authored question, one coherent actual five-role renderer journey, CI/artifact SHA/golden semantic QA and review packet; otherwise individual unresolved cells marked and not counted. No claim that this file starts work, and no back-and-forth to Owner for routine implementation.
