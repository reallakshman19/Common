# AUTO MODE — Autonomous Phase Execution

`AUTO MODE` is an explicit owner execution authorization. It permits automatic progression through the approved plan without routine phase-by-phase confirmation.

It does not grant unlimited scope, engineering authority, destructive-operation authority, or merge authority.

## Activation

When the current owner instruction contains the exact keyword `AUTO MODE`, persist:

```text
EXECUTION_MODE = AUTO
AUTO_STATE = RUNNING
SCOPE_AUTHORITY = LOCKED_TO_APPROVED_MISSION
PHASE_PROGRESSION = AUTO
MERGE_AUTHORITY = OWNER_ONLY
```

If a status record exists, persist the same authorization there.

`AUTO MODE` does not imply `AUTO MERGE`. Automatic merge requires a separate explicit owner authorization.

## Required behavior

While no hard-stop condition exists, completion of a normal phase is not a reason to ask for confirmation.

The agent shall repeatedly:

1. re-check live repository/PR state, coordination claims, and current recovery state;
2. select the next approved phase;
3. record objective, expected files, rationale, prediction, invariants, and validation plan;
4. implement only that phase;
5. validate and classify evidence accurately;
6. update work report, findings, changed-file ledger, status/claims, and Appendix A if next unresolved work changed;
7. create a durable checkpoint;
8. evaluate hard-stop conditions;
9. continue automatically when none applies.

Invalid routine stops while AUTO is active include:

- `Phase complete; awaiting confirmation.`
- `Would you like me to continue?`
- `Let me know if you want the next stage.`
- `Should I run the remaining planned tests?`
- `I can continue if desired.`

## Hard-stop conditions

Stop automatic progression and record the exact blocker when:

- the next action materially expands or changes approved scope;
- the approved plan is materially invalidated and requires an owner-level product/engineering decision;
- a protected engineering authority, governing formulation, controlled source, runtime/writer/canvas, or other protected authority must change beyond existing authorization;
- safety-critical uncertainty cannot be bounded by approved evidence;
- takeover qualification fails, becomes stale, or write authority is revoked;
- an independent oracle materially contradicts the implementation and bounded diagnosis cannot resolve it within approved scope;
- an unresolved `BLOCKED_BY_ACTIVE_CLAIM` or equivalent authority collision exists;
- a destructive, credential, security, permission, or irreversible action requires new authorization;
- continuing would require guessing engineering intent or weakening a validation/acceptance gate;
- `SUPERSEDE` or `ABANDON` would discard material work and owner disposition is required;
- merge is the next action but merge authority has not been separately granted.

Set `AUTO_STATE` to `BLOCKED`, `OWNER_DECISION_REQUIRED`, or `TAKEOVER_REQUIRED` as appropriate. Preserve handover readiness and record evidence, safe options, and one executable next action.

## Bounded self-recovery

AUTO MODE may investigate, repair, rerun validation, and continue automatically when the problem remains inside approved scope and authority boundaries.

Do not thrash indefinitely. If repeated attempts do not narrow uncertainty, or the agent cannot state a concrete hypothesis, falsifier, next isolating experiment, and protected invariants, stop production mutation and set:

```text
PR_RECOVERY_STATE = TAKEOVER_REQUIRED
TAKEOVER_AUTHORITY = READ_ONLY
AUTO_STATE = TAKEOVER_REQUIRED
```

Refresh the work report and Appendix A so another qualified agent can take over immediately.

## Completion

When all approved phases and required validation/reconciliation are complete:

```text
AUTO_STATE = COMPLETE
```

If merge authority remains owner-only, stop in a merge-ready, handover-ready state and request only the merge decision—not routine implementation confirmation.
