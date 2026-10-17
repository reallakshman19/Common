---
name: handover-master
description: Single source-first entrypoint for technical handovers, 2-pass and 3-pass prompts, v3.6 delivery generators, BuddyRunner 1a/1b/2, zero-exit onboarding, and read-only progress.
---
# Handover Master — ONE invocation for existing native workflows

**User entrypoint: this file only.** Read this SKILL.md, [DECISION_GUIDE.md](DECISION_GUIDE.md), and [sources.json](sources.json). Do not ask the Owner to discover folders or protocol versions. The original modules remain at their canonical paths; Master is a **routing facade**, not a copy of their code or a new approval controller.

**One reusable Owner invocation:**
> Use Handover Master for [repo/issue/human outcome]. Select the appropriate handover, two-pass, three-pass, BuddyRunner, zero-exit or progress mode from live Owner/project authority. Read current canonical source/schema, protect blind-stage isolation, show exact phase, sources and gaps, and only perform an authorized next step.

**Read-only local route preview:**
~~~sh
python "skills/Handover Master/route.py" --intent "2-pass baseline and reconciliation for v3.6"
python "skills/Handover Master/route.py" --mode buddy --workflow v3.6 --phase 1a
python "skills/Handover Master/route.py" --mode zero-exit --format json
~~~
This CLI prints source paths/instructions only; it NEVER fetches remote authority, executes a generator, posts comments, starts a stage, merges or schedules anything. `READ_SOURCE_NOW` means only "read the native skill."

## Mandatory decision sequence

1. **Identify desired deliverable:** independent current-system baseline, exploratory project reframing, actual Stage-2 technical handover, BuddyRunner phase, zero-exit source reconstruction or read-only status. Respect any expressly selected mode/version; reconcile later Owner amendments before relying on older claims.
2. **Resolve governing workflow:** selected v3.6 AIM label/plan means use v3.6's OWN `prompt_2pass_v36.py` or `prompt_3pass_v36.py`, not the standalone validators. Pinned v3.5 work stays v3.5 by default; never silently upgrade. Without a governing lifecycle use standalone prompt protocols when appropriate.
3. **Choose by outcome, not directory:**
   - **Two-pass:** task-blind independent system baseline, then actual task-aware STEP-BACK reconciliation/plan and Owner approval boundary.
   - **Three-pass:** imagination/problem kernel, current reality, and reconciliation/revalidation. Native **five prompts** `0.5 / 1 / 2 / 2.5 / 3`, not an invented extra stage.
   - **BuddyRunner:** `1a` G1 preparation/HOLD → `1b` G2 investigation → `2` G1 final reconciliation, or one `Xb → Y` intervention. v3.6 pins **v1.6**; v1.7 requires its own project/Owner version selection.
   - **Technical handover:** native coherent 12-section `HANDOVER_TECHNICAL_V2`, **Stage2 after independently authenticated Stage1 freeze and verified recipient isolation only**; native PLAN_HANDOVER/HANDOVER_CONTEXT remains source custody.
   - **Zero-exit:** successor has no predecessor LOG/exit; source-first ONB-RWI WP5 report, manifest and fail-closed verdict. Draft WP1a–WP4 are NOT present on main; do not import until merged/verified. RWI remains NOT_EVALUATED without independent proof/Owner approval.
   - **Status:** Universal Workflow Progress observer, not BuddyRunner execution.
4. **Read selected canonical source and current schema from main THIS RUN.** Prove actual source/blob SHA and native protocol revision. Emit any canonical generator handshake required by the native schema; do not synthesize it from memory.
5. **Gate isolation and authority:** original problem, Owner/roadmap amendments, exact current main and candidate PR heads, tests against exact code SHAs, independent fixture/oracle custody, privacy, phase completion receipts and explicit permissions. Missing facts ⇒ HOLD/UNKNOWN, not fabricated acceptance.
6. **Perform only the authorized module action.** The Master router has no apply flag. Any actual script, GitHub publication or workflow advancement uses the native module's own guarded commands, scope and fresh provider readback.
7. **Return a human report:** chosen method and reason; canonical skill/schema and fetched SHA; exact generated phase/result (or HOLD), original user outcome, reality and tests, explicit unknowns, and ONE next evidence-producing verification.

## Source/authority precedence and overlap

- Explicit Owner/project-pinned version beats intent keyword routing; native pins still apply.
- **v3.6 version amendments (Common #408 HM-01):** v3.6 natively pins BuddyRunner 1.6. A request for another version **without** `--amendment-ref` returns `HOLD_VERSION`. With a well-formed GitHub issue/PR/comment reference, the router returns `PROVISIONAL_ROUTE`: an **unverified, read-only candidate preview** (exit 2) showing the native pin and the candidate sources, never admission. The **controller** must verify the cited Owner decision, its scope (a lane begun on 1.6 finishes on 1.6), currency/HOLD, native compatibility, phase receipts, source freshness and work/custody authority before any action; anything unresolved is CONFLICT/UNKNOWN. A malformed reference returns `INVALID_AMENDMENT_REF`; an unused reference is reported as not applied.
- Conflicting versions or ambiguous method ⇒ request one discriminator, do not choose by habit.
- A report under blind-stage isolation ⇒ HOLD unless freeze and recipient isolation were verified externally; command-line assertions alone are not proof.
- If a BuddyRunner 2 response contains a 12-section report, **no fourth Buddy phase** is created. Likewise `three-pass` is NOT BuddyRunner's `1a→1b→2`.
- Zero-exit does not presume the outgoing agent's claims; fetch source independently. A source SHA or PASS is not semantic acceptance.
- A request to show progress is NOT authorization to start a handover phase.

## Canonical links / no breakage

All modules are indexed in one [MODULE_INDEX.md](MODULE_INDEX.md), machine registry `sources.json` and [README.md](README.md). Modules physically remain where existing source imports, CLI paths, tools, Actions and issue references expect them:

`relay/CONTINUITY/TEMPLATES/`; `skills/two-pass-prompt-generator/`; `skills/three-pass-prompt-generator/`; `skills/engineering-pr-delivery-v3.6/` (v3.5 history separately); `skills/buddy-runner-v1-6/`; `skills/buddy-runner-v1-7/`; `skills/relay-onboarding-rwi/`; `skills/universal-workflow-progress/`.

**Do not move or duplicate implementation folders** into Master unless a later migration explicitly updates ALL consumers, tests, links, scripts and Owners. Master provides one selectable path, not a competing protocol.

**CoordinatorLandingpage #21/#7** supersedes Dash V2 as a possible separately approved read-only consumer; this entry point does not write its site, registry, owner-input or Team Protocol.
