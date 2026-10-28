# Output Example Index

Use these **finished examples before inventing a new output shape**.

They are reference examples, not production authority. Always replace example IDs/SHAs/evidence with live truth.

## V3.1 Task Snapshot / reporting

| Scenario | Example |
| --- | --- |
| Review-ready PR, child/programme still open | `engineering-pr-delivery-v3.1/examples/task-snapshot/review-ready-parent-open.json` |
| Merged child, parent programme still open | `engineering-pr-delivery-v3.1/examples/task-snapshot/merged-child-parent-open.json` |
| Required certification NOT_RUN because infrastructure unavailable | `engineering-pr-delivery-v3.1/examples/task-snapshot/not-run-infrastructure.json` |
| Normal active task | `engineering-pr-delivery-v3.1/examples/task-snapshot/active-task.json` |
| Fully complete task/programme contribution | `engineering-pr-delivery-v3.1/examples/task-snapshot/complete-task.json` |
| Interpretation guide | `engineering-pr-delivery-v3.1/examples/task-snapshot/README.md` |

Render with:

```bash
python skills/engineering-pr-delivery-v3.1/scripts/render_task_snapshot.py <snapshot>
```

## Agent task publications

| Output | Example |
| --- | --- |
| `IMPLEMENTATION_PLAN` | `engineering-pr-delivery-v3.1/examples/publications/implementation-plan.md` |
| `PLAN_UPDATE` | `engineering-pr-delivery-v3.1/examples/publications/plan-update.md` |
| `TASK_EVIDENCE` | `engineering-pr-delivery-v3.1/examples/publications/task-evidence.md` |
| `TASK_RESULT` | `engineering-pr-delivery-v3.1/examples/publications/task-result.md` |

## PR / delivery reporting

- `engineering-pr-delivery-v3.1/examples/delivery/pr-review-ready.md`

This example demonstrates that review-ready material is not the same as merged delivery or programme completion.

## GitHub issue authoring

| Output | Example |
| --- | --- |
| Programme root with `EXIT-*` denominator | `engineering-github-issue-authoring/examples/programme-root.md` |
| Parallel-focused child with `AC-*` denominator | `engineering-github-issue-authoring/examples/parallel-focused.md` |

## Programme coordination

| Output | Example |
| --- | --- |
| Multi-agent `[Relay Handover]` ledger | `engineering-programme-coordinator/examples/relay-handover-multi-agent.md` |
| Owner semantic-delta report | `engineering-programme-coordinator/examples/owner-semantic-delta.md` |

## Work ↔ local engineering coordinator

| Output | Example |
| --- | --- |
| Work → local `EXECUTE_WORKSTREAM` | `engineering-programme-coordinator/examples/local/execute-workstream.md` |
| Local → Work `DURABLE_RESULT` | `engineering-programme-coordinator/examples/local/durable-result.md` |
| Local → Work `DEPENDENCY_DISCOVERED` | `engineering-programme-coordinator/examples/local/dependency-discovered.md` |

## Two-pass publication

- `two-pass-prompt-generator/examples/clean-two-pass-packet.md`

Publish exactly the two agent-facing prompts. Pass 1 ends at independent system understanding. Pass 2 shows quantified Improvement Proposal(s) and a draft implementation plan, pauses for Owner approval, then continues after approval without creating a third pass. Keep generator/compiler diagnostics out of the engineering issue unless a diagnostic itself is the subject of investigation.

## Reporting quality invariants

Examples encode these invariants:

```text
record != report
evidence != progress
implementation != verification
verification != delivery
delivery != child acceptance
child acceptance != programme completion
NOT_RUN != FAIL
sibling/pre-existing failure != current-task failure
OPEN issue != necessarily unfinished engineering
merged PR != necessarily complete programme
```

When no acceptance denominator exists, report `UNKNOWN / UNMAPPED`; never invent a completion percentage.
