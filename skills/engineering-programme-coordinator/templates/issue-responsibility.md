# Engineering issue responsibility contract

Use this structure for substantial multi-agent engineering issues. Keep it focused on durable responsibility. Do not turn it into a live status dashboard.

## Reconstruction source refs

```text
Original Intent: <ref / inherited / NONE>
Current programme/Roadmap basis: <ref>
EP: <ref when assigned>
Latest responsibility reconciliation: <ref / NONE>
Local Agent / OFFLOAD refs: <refs / NONE>
RLL refs: <refs / NONE>
Task Snapshot / Handover: <refs / NONE>
```

These are reconstruction pointers, not extra authority stores. Keep the actual Original Intent, Local Agent evidence and RLL state on their existing provider surfaces.

## Outcome

What production capability/result should exist when this responsibility is fulfilled?

## Why now / witness

What concrete problem, user/system need, failure, contradiction or opportunity makes this work worth doing now?

Prefer one or more discriminating witnesses over generic motivation.

## Owned responsibility

This issue owns:

- ...

## Ownership boundary

This issue does **not** own:

- ...

Name neighboring owners where known.

## Canonical inputs

| Ref | Meaning | Source authority |
| --- | --- | --- |
| ... | ... | ... |

Only list production truth this issue may actually rely on.

## Consumer contract

| Consumer | Required output |
| --- | --- |
| ... | ... |

Describe the production output, not merely the consumer issue number.

## Dependencies

### DEP-1 — <required production output>

**Producer:** <issue/agent/source if known>

**Why required:** ...

**Satisfaction evidence:**

- ...

**Work that may continue independently before satisfaction:**

- ...

A dependency is missing production truth, not permission to work.

## Success oracle

Observable evidence that proves the issue worked:

- ...

## Falsifiers

Evidence that would prove the planned work unnecessary, wrong or differently framed:

- ...

## Preserve / invariants

Existing behavior/contracts that must remain true:

- ...

## Decision surface

### Engineer decides

- implementation details inside this responsibility;
- ...

### Coordinator decides

- routing cross-agent consequences;
- sequencing/parallelism based on current evidence;
- ...

### Owner decides

Only genuine product/intent decisions:

- ...

## Implementation Plan

Agent-authored and revisable.

Cover:

- approach;
- meaningful implementation slices;
- expected components/files;
- interfaces affected;
- tests/validation;
- dependencies assumed;
- local/browser/runtime validation expected;
- preserve/invariants;
- known uncertainties;
- expected handoff/result.

Updating this plan to match new evidence is normal. Plan drift is not a fault; **unreconciled** material drift is something the coordinator should notice.

## Handoff requirements

A downstream consumer must be able to reconstruct:

- exact durable output;
- exact material/evidence ref;
- what is proved;
- what is not proved;
- known limitations;
- consumer-facing contract;
- anything the consumer must not infer.

## Semantic escalation

Escalate only when evidence materially changes:

- product meaning;
- shared architecture/interface ownership;
- this issue's responsibility;
- another workstream's durable assumptions;
- a decision that genuinely belongs to the Owner.

Do not escalate ordinary implementation churn, test retries, commit count, worker silence or coordinator/reporting metadata.
