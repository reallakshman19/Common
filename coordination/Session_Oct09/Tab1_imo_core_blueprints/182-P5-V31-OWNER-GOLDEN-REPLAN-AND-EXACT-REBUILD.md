# 182-P5 — Sticky label v3.1.0 replan against the Owner-designated five-role golden

2026-10-12 | chat=6acc408a | tab=Tab1 | issue=Grade9v3.5 #182 | plan=P5 | Owner sticky v3.1.0 / label_sha 2ff9246 | main authority Common/main relay/AIM/IMO-CORE-BLUEPRINTS.yaml blob 5c8457bdef4a7019c29f90668fe3b51118a4a7ff | TEST only

## Owner's words (exact, unchanged)

> Problem: Core 1B is done with a golden fixture; other Cores are not yet created or optimized from blueprints based on QRT.
>
> Main aim: Create or optimize blueprints for each Core based on QRT; Core 1B is done, golden fixture created, others remain.
>
> Outcomes:
> O1 Each remaining Core (1, 1A, 2A, 2B) has a page built from its blueprint that matches its golden fixture.
> O2 Each page serves a named QRT cell and that cell has an accepted decision.
> O3 Where a golden shows a blueprint gap, the blueprint is optimized and the change is recorded.
>
> Owner constraints: Pages come from the existing blueprint registry and are aligned with the golden fixtures.; This work grants no source rights, QRT acceptance, merge or release.; Use the existing blueprints for Core 2, Core 1A and Core 1B and reuse them wherever possible; create a new one adapted to QRT only where one is missing; benchmark every page against the available golden fixtures (Owner, 12 Oct).; Parent aim: every page is generated from its registered blueprint through Shared/tools/render_core.py and benchmarked against its golden fixture. A standalone, hand-written or composer-made HTML page is never a deliverable and is never presented as one; if the renderer cannot run, report BLOCKED (Owner, 12 Oct).
>
> Task aim (O1): Build the next Core page from its blueprint against its golden: Core 2A done structurally, Core 1A next, then 1B.
>
> Done when: PENDING: the Owner sets which Cores, acceptance per QRT cell, real learner inputs and A4 print.
>
> Not now (Owner-approved, with the condition that brings it back): Authentic Core 2 from the 68 source questions: separate work in Tab 2, back when a Core page needs a real source question.
>
> Watch for (not forbidden; say how it serves an outcome if you do it): Print, CI, lease or route work: do it only when it blocks a Core page, and say which outcome it serves.; Task counts such as 3/3 or 5/5 are not progress toward the aim.

Master metadata note: current canonical file itself encodes `engineering_critical: "standard"`; the user message describes this as "no". The v3.1.0 and label_sha 2ff9246 match exactly, no master field was edited or normalized by this agent. This discrepancy has no effect on the limited TEST-only O1 technical regression below.

## Last three tasks: effect on real learner workflow and evidence carried forward

1. **182-T8, O2 decision packet** (https://github.com/reallakshman19/Grade9v3.5/issues/182#issuecomment-6118945308): five-page association register exists with named authored QRT-JUSTIFY-D2 candidates Core2A/Core2B, concept support Core1/1A/1B, unresolved H3 and explicit independent-review fields. **STILL VALID as review evidence**, not QRT accepted; canonical QRT **0/28** and no user-visible released learner change.
2. **182-T9, O3 golden/blueprint gap ledger** (https://github.com/reallakshman19/Grade9v3.5/issues/182#issuecomment-6118952533): no proven absent registry capability against the former G-MATH-LINEAR-CONSTRAINT candidate; separate authored SVG stage accessibility, early hint and potential Core2B closure projection identified and classified. **STILL VALID for issue history**, but absence of an O3 gap MUST BE RETESTED against the **newly Owner-designated exact five-role golden**, not promoted to blanket assurance.
3. **182-S3, O1 one-head TEST integrated preview** (https://github.com/reallakshman19/Grade9v3.5/issues/182#issuecomment-6119462405): #188 exact head f87d2f627e3f05476d39fb04d7f26e453661dc68, five registered roles and no source Core2 rendered via sole render_core.py; hosted run 38215683516 **SUCCESS 17/17**, six actual HTML files plus receipts, reference-depth gaps=0, learner answer gates in local Chromium PASS. **STILL VALID at those exact artifact hashes**, not production release/approval of every resulting page.
4. **Owner's newer golden designation** at 2026-10-12T07:30:37Z: `golden/units/G-IMO-G9-FIVE-CORE-20261012/GOLDEN.md` on #188 head `a8dbdad1dd316574514d8a74a33c59e177c9ab97`; it freezes five HTML files from the **above prior verified renderer CI artifact** `11732117118` and pins five SHA256 and git blob IDs in `snapshot-lock.json`; status `OWNER_DESIGNATED_EXACT_HTML_SNAPSHOT`. This **new authority is not a QRT, H3, A4 or release decision**, and is more direct for O1 than algebra-different G-MATH-LINEAR-CONSTRAINT comparison. The golden is a frozen **renderer-generated** output, not an independent handwritten/composer-made HTML deliverable.

## P5 ordered work map and stop line

| Priority | ID/outcome | Smallest real next step | Exact oracle / status |
| --- | --- | --- | --- |
| **NOW** | `182-P5-W01` / **O1** | **Golden lock/rebuild check**: use actual TEST five-role manifest and golden pin records with **Shared/tools/render_core.py**. Assert frozen SHA256/git object identities, exact byte-equality to the five emitted TEST HTML role pages from the original source manifest; check the pinned golden-manifest reference regeneration after replacing **only** its expected render-authority digest. Assert registered blueprint refs, all five correct roles, zero reference-depth gaps, protected attempt gates. | New isolated DRAFT PR #189 based on existing #188 owner-snapshot head `a8dbdad1dd316574514d8a74a33c59e177c9ab97`; only a test and targeted CI workflow, **no HTML authored/edited**. Focused hosted workflow `IMO 182 Owner-designated five-Core golden lock (TEST only)`. If test fails on genuine content/role mismatch, report precisely and stop; do not change a blueprint without proof of a missing affordance. |
| **AFTER POSITIVE PROOF** | `182-P5-W02` / **O1/O3 conditional** | Preserve Owner-complete Core1B, record five-role exact golden/renderer alignment and no-change if no missing blueprint capability; only then assess potential genuine O3 gap. | Reviewer sees source lock, actual renderer-based page SHA, and what remains unaccepted; no specimen HTML replaces renderer output. No code or golden snapshots change unless Owner directs a new version. |
| **OWNER** | `182-P5-W03` / **O2** | Return existing five-role QRT decision packet; get named independent academic/Owner per-page QRT verdict and **D-182-2-H3**. | 0/28 until explicit Owner-accepted source decision with ID; no model self-acceptance. |
| **OWNER / other module** | `182-P5-W04` / prerequisite to O1 publication | A4 print linked actual PDF, human real learner input, PR-wide CI/integration, source custody only where it blocks an authorized Core page. | A4 parked with shared-printer owner; no new source Core2 or merge/release. PR #186/#187/#188 all draft. |

**O3 trigger gate:** A frozen, Owner-designated role snapshot contains a learner-essential move not expressible by the existing `BP-CORE*` registry, with a failing exact role proof, reproduced source, and the smallest proposed before/after blueprint correction; otherwise **NO_CHANGE**. A test file or CI workflow being absent is an O1 verification infrastructure gap **not itself a blueprint gap**.

**Only new scoped changes in this iteration:** `tests/test_imo182_owner_golden_snapshot.py` and `.github/workflows/imo-182-owner-golden-lock.yml` on separate DRAFT PR #189. No standalone page, owner golden mutation, registry, renderer, QRT, source rights, print, public route, or merge. Technical CI outcome to be separately linked when completed; no projection based on past run.

## Evidence and outcome claims

- Owner golden: https://github.com/reallakshman19/Grade9v3.5/blob/a8dbdad1dd316574514d8a74a33c59e177c9ab97/golden/units/G-IMO-G9-FIVE-CORE-20261012/GOLDEN.md
- Owner HTML artifact original CI: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38215683516
- Verification draft PR: https://github.com/reallakshman19/Grade9v3.5/pull/189
- No change for live learners, no real learner measurement or academic QRT judgement. Outcome `O1` evidence infrastructure in progress; O2 academic acceptance `NOT_MET`; O3 conditional `NOT_TRIGGERED`.
