# Multi-role adapter implementation plan

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

Implementation and new checks pending at plan creation. Actual results will be
recorded in the adapter reference and PR receipt. Existing v1 planning pilots are
not lower-capability-worker qualification or production UI/FEA acceptance.
