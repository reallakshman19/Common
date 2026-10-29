# Test page protocol — optional project-local demonstration

**Open:** Project Home → Test page, or `#/PROJECT_KEY/test` (Lessons: `#/learned/test`). This is an in-memory UI sandbox, not a mandatory agent onboarding step, assignment inbox, acceptance gate or a live Timeline.

## Demonstrate
1. Select a currently recorded WBS/card. The demonstration uses its existing project AIM, milestone and Smart Badge IDs; a missing/closed task is UNRESOLVED or UNSCOPED, never replaced by a fabricated production task.
2. Select `ACTION/OPEN` and optionally simulate `NEEDS_OWNER`. This sends no request to the Owner or IR.
3. Select `INFO/HANDED_OFF`. This illustrates a handoff transition, retaining the Action conceptually; IR engineering review is a *separate* task and is never marked PASS by the sample.
4. Select `INFO-Auto generated` to inspect actual, already-published Page-audit WBS evidence. When no matching audited entry exists, show no record, not a fabricated status.
5. `Copy demonstration packet` creates a text-only `DEMONSTRATION ONLY` explanation, deliberately *not* the `CYCLE_TIMELINE_CARD v2` event grammar. It is not a receipt, a report or a Page update.

## Isolation and checks
- Controls exist only in the current browser view: no GitHub comment, Page audit, Cycle revision, task dispatch, acceptance, assignment, credential or private-file operation.
- Use source-linked badge IDs AIM/ROADMAP/WBS/PLAN/FIXTURE/ORACLE_CONTINUITY only where supported; unknown or historical context stays labelled. Do not infer fixture delivery from a link.
- A screenshot verifies presentation, **not** original-byte access, engineering correctness, independent reviewer neutrality or Owner acceptance.
- For production, return native evidence once and let the authorized Oracle/Page writer reconcile under [Timeline mode](CYCLE_TIMELINE_PROTOCOL.md), [START_HERE](../../START_HERE.md) and [Page modes](MODES.md).

**No new agent check-in is needed to use or demonstrate this page.**
