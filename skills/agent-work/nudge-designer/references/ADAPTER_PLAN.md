# Multi-role adapter implementation plan

## Contents

- [Reconciled intent](#reconciled-intent)
- [Orthogonal dimensions](#orthogonal-dimensions)
- [Work and acceptance](#work-and-acceptance)
- [Reuse and boundaries](#reuse-and-boundaries)
- [Verification checkpoint](#verification-checkpoint)
- [Prompt templates and Applying guidance](#prompt-templates-and-applying-guidance)
- [Adaptive support amendment](#adaptive-support-amendment)

## Reconciled intent

Owner amendment, 18 October 2026: support broad application and different thinking
agents, reconcile end-to-end use, and implement robust adapters where applicable.

Preserve the existing intent/nudge separation. Add practical exchanges among Owner,
Designer, worker, specialist, reviewer, coordinator and successor without assuming
a model vendor, compulsory agent count, fixed pass count or new approval chain.
These are roles; one participant can hold several. Role labels and configuration
claims do not establish competence, independence or authorization.

## Orthogonal dimensions

| Dimension | Contract |
|---|---|
| Domain | Existing composable understanding/reasoning/evidence profiles |
| Participant | Recorded capabilities, tools, configuration basis and supported roles |
| Assignment | Per-nudge needs, selected participant, guidance and reserved decisions |
| Audience | Role-specific view of the same source-linked work |
| Surface | Plain, GitHub Markdown, NextNudge manual copy, BuddyRunner checkpoint, selected delivery brief |
| Return | Native report preserved with explicit task binding, attempts, findings and limits |

## Work and acceptance

1. Extend the existing plan schema with an explicit `plan/v1.1` opt-in for
   participants and assignments. Keep `intent/v1` and every old `plan/v1` fixture
   valid. Do not silently accept v1.1 fields under v1. Keep two formal schemas.
2. Check per-task capability/tool claims without ranking model names. Distinguish
   recorded, reported, unknown and missing requirements. Restrict conclusions to
   that assignment; never lock unrelated work or certify qualification.
3. Render role-specific views and manually delivered surface packets from the
   same bound inputs. Owner sees purpose/change/next decisions; workers receive
   seven elements and suitable guidance; reviewers receive claims and falsifiers;
   coordinators/successors retain remaining work and source identity.
4. Add a native-return envelope API. Preserve native content verbatim; require
   exact issued intent/plan/nudge binding. Record attempts, evidence references,
   declared findings, unresolved work and next proposal without interpreting free
   prose as approval. Reject malformed/cross-task returns with useful errors.
5. Produce a reconciliation worksheet: discrepancies, stale/unpinned source
   observations, declared drift/improvement/new issues, scope references and
   independent eligible work. No automatic semantic classification, plan mutation,
   Owner acceptance or dispatch. Historical returns use their issued snapshots.
6. Exercise role/domain/surface composition, legacy compatibility, missing tools,
   self-review conflicts, stale sources, native-content preservation, source
   injection, input overwrite, and actual CLI round trips. Forward-test real local
   execution/review tasks using raw artifacts without worked-answer leakage.

## Reuse and boundaries

Existing native reporting remains authoritative for its own project. The small
envelope links that report to the assignment; it does not replace its format.
Only intent and plan have JSON schema documents. Profiles and return/adapter API
inputs use strict local checks; they are not additional project governance systems.

Surface adapters prepare material. GitHub does not post it; NextNudge output is
explicitly manual-copy, not a native import object; BuddyRunner output is supporting
material, not a completed stage; delivery requires an explicitly selected protocol.
No adapter silently imports a legacy thinking/handover default or changes a target
application, issue, protocol selector or sent instruction.

Retain immutable issued snapshots and exact native returns. A new revision needs
semantic reconciliation and a new binding. Missing facts affect dependent actions.
Add no per-nudge Owner approval ceremony; use existing authority and reserve real
scope, outcome, engineering or pedagogical choices appropriately.

## Verification checkpoint

Implemented checkpoint, 18 October 2026: explicit backward-compatible v1.1 team
support, seven audience views, five manual surfaces, task binding/fit/native intake
and a human-interpreted reconciliation worksheet. The 84 focused checks pass on
local Python 3.12; all original v1 cases remain supported. This includes actual CLI
round trips, cross-domain composition and archived history/current-revision checks.

Fresh worker/specialist executions and a separate reviewer produced actual local
artifacts. Review exposed a stale numeric handover and unsupported learner fact;
the Designer corrected meaning in a separate revision while retaining issued
history. See [the role-cycle assessment](../examples/adapter-cycle/ASSESSMENT.md)
and [verification](VERIFICATION.md). No lower-capability-model qualification,
production UI/FEA acceptance or actual learner outcome is established. Hosted CI
and exact remote readback are reported on the draft PR after publication.

## Prompt templates and Applying guidance

Add reusable prompts for all seven roles, a filled seven-element assignment aid,
native-result guidance and an explicit decision process for applying the flows.
Provide paired raw/golden references for UI, logic, teaching, FEA, cold onboarding,
mixed teams and reconciliation. Show superfluous assumptions and tempting invalid
continuations. Keep goldens out of fresh-agent task context and accept justified
alternatives preserving the same conditions. Preserve existing APIs, two schemas,
native authority and archived execution evidence; add no fixed passes or gates.

Validate usability on fresh raw tasks with emitted artifacts, then check links,
skill metadata and the existing compatibility suite. Record actual observations
and limitations separately from synthetic expected decisions.

Implemented checkpoint: nine prompt/aid resources, Applying guidance and seven
paired cases are present. Four fresh role applications plus a fresh Designer
retest produced inspected artifacts; parent reconciliation corrected a screenshot
mapping assumption and retained all originals. The 84 compatibility checks,
skill/syntax/metadata/link and arithmetic checks pass locally. See the
[prompt application assessment](../examples/guidance-forward/ASSESSMENT.md) and
[verification](VERIFICATION.md); exact-head publication/CI remains on the draft PR.

## Adaptive support amendment

Owner follow-up, 19 October 2026 (Asia/Dubai): generalize the NLM pilot lessons,
especially for limited/unestablished task fit, update, then merge after verification.
The separate pilot-specific PR #439 remains held. This direct request authorizes
the broader amendment; neither a pilot report nor that held change supplies
shared-policy authority. Start from current main rather than stacking on #439.

Keep runtime, schemas, adapters, profile contracts and native reporting unchanged.
Add [adaptive support](ADAPTIVE_SUPPORT.md), selective role/assignment instructions
and paired references for claim/evidence, interpretation and correction causes.
Compile self-contained worker briefs rather than requiring narrower recipients
to learn the process library. Use task-specific observations, risk-based checks
and cause-specific correction without fixed passes, weakness counts, format bans
or mandatory new gates. Preserve consequential judgments and actual project rules.

Acceptance requires substantive fresh raw-task applications with original inputs
and outputs preserved, parent source-derived checks of material claims, and honest
limits. Include a small brief-only application to inspect usability without loading
the library. Different tasks/sessions cannot establish a model or GUIDED-versus-OPEN
effect. No low-thinking runtime is selected or qualified merely by these exercises.
Run existing focused compatibility checks and skill/syntax/metadata/link checks;
verify the published tree and exact-head hosted checks before the authorized merge.
See the [adaptive assessment](../examples/adaptive-forward/ASSESSMENT.md) and the
new [verification checkpoint](VERIFICATION.md#adaptive-support-amendment).
