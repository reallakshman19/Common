# Owner entry prompts

Use one variant. Replace the goal/link; omit inapplicable slots. The agent does
the modeling. These prompts select no protocol/model setting or new authority.

## General

```text
Use Nudge Designer for {{goal}}, starting from {{source links or supplied context}}. Preserve my original conditions and useful existing work.
Reconstruct what matters, choose the next useful assignment for the available agent, and proceed within existing authority; bring me only a real unresolved decision.
```

## Narrower worker

```text
Use Nudge Designer to help an agent with {{known tool/support limits}} achieve {{goal}} from {{sources}}.
Give it one coherent task, the concrete method and a meaningful contrast; retain consequential decisions and inspect its actual result before choosing the next work.
```

## Recovery, predecessor unavailable

```text
Use Nudge Designer with the project's selected recovery protocol for {{project/issue}}; the outgoing agent is unavailable. Start from {{durable sources/last report}}.
Reconstruct independently, reconcile drift and useful improvements, then take the next feasible action under existing authority and the protocol's actual continuation rules.
```

## Onboarding before a new task

```text
Use Nudge Designer with the project's selected onboarding protocol to reconstruct {{project/issue}} from {{sources}}; do not depend on the predecessor.
After reconstruction and the applicable review/approval, wait for my next task prompt. Keep remaining work visible without starting an unassigned product task.
```

## Fresh task-local workers

```text
Use Nudge Designer for {{goal/sources}} with fresh workers where useful task boundaries support it.
Give each worker necessary local context and a concrete method; keep global decisions with Oracle. For blind evaluation, state which references are withheld and disclose prior exposure and self-assessment.
```
