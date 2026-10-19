# Receive diagnostic

**COMPLETE — bounded synthetic diagnostic only.** The unchanged supplied function
violates source ownership twice: an A/12 completion publishes `A12` while labeling
it as source B. Revision 11 is rejected, and valid B/12 completes successfully in
all three orders. Wider Owner acceptance remains unresolved.

Read this run: `assignment.md`, `source.py`, Nudge Designer's `SKILL.md`,
`references/APPLYING_GUIDANCE.md`, and `assets/prompts/worker.md`. No worked
examples, tests, verification records, or other task outputs were read.

The prediction in `prediction.md` was written before execution. It predicted
the two cross-source publications, the stale-revision rejection, and successful
current publication. All six observed transitions match those predictions.

Each order starts fresh at
`{'selected_source': 'B', 'current_revision': 12, 'result': None}`.
Selection B and revision 12 remain unchanged throughout. In the table below,
`B:A12` means the actual result object `{'source': 'B', 'payload': 'A12'}`;
payload origin is determined from the issued synthetic completion, not from
the misleading stored source label. Expected results follow the invariant
across the full order.

| Order / step | Input source, revision, payload | Actual result before → after | Expected result after | Invariant after this step |
| --- | --- | --- | --- | --- |
| A12 → B12 / 1 | A, 12, A12 | None → B:A12 | None | **FAIL:** payload belongs to A |
| A12 → B12 / 2 | B, 12, B12 | B:A12 → B:B12 | B:B12 | PASS; earlier violation remains evidence |
| B12 → A12 / 1 | B, 12, B12 | None → B:B12 | B:B12 | PASS |
| B12 → A12 / 2 | A, 12, A12 | B:B12 → B:A12 | B:B12 | **FAIL:** valid result overwritten by A payload |
| B11 → B12 / 1 | B, 11, B11 | None → None | None | PASS; stale completion ignored |
| B11 → B12 / 2 | B, 12, B12 | None → B:B12 | B:B12 | PASS; valid completion accepted |

The code checks revision equality only and never uses `source_id`. It assigns
`selected_source` to the result's source field, so checking that field alone
would conceal the ownership failure. A matching final state in the first order
also conceals its intermediate failure. The revision-only control and valid
current completions distinguish this defect from a function that rejects
everything or ignores revisions.

Reproduce from this directory:

```bash
PYTHONDONTWRITEBYTECODE=1 python -B probe.py
```

The command exited 0. `probe.py` imports the original `source.py` using
`importlib`; it does not replace, edit, or mock `receive`. Its separate oracle
only records expected results. `output.json` contains all input fields, full
before/after states, expected states, payload provenance, and invariant results.
Bytecode was disabled. The source's SHA-256 before and after execution was
`766a81726984857c9e66c8ed07e9582e850ffeb651b65f81c80e30a4acd451f3`.

Artifacts: `prediction.md`, `probe.py`, `output.json`, and this report.
No tool restriction blocked the assigned work. Host model, reasoning
configuration, and formal qualification are **UNKNOWN**. This is local
synthetic evidence; production integration, real request handling, and wider
acceptance were not exercised. The independent CSV-unit question remains
unassigned and unresolved. No repair, product change, external publication, or
delegation was performed.

Next feasible proposal: issue a separate implementation assignment to require
both source identity and current revision before publication, preserving valid
B/12 behavior. Reuse these contrasts to evaluate that change, then separately
exercise the actual production path before claiming integrated acceptance.
