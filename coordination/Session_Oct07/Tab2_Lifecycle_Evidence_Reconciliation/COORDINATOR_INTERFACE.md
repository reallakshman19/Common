# CI01 — V3.5 coordinator observation interface (Tab2)

**Scope:** Chat `6acb041f`, Common#294 PLAN-15, coordination-only XS task. This is a **human-facing status and tab-log convention**, not a Relay/DELP state engine, Local v1.1 writer lease, accepted programme fact, or policy amendment. Canonical source owners remain #20/#30; parent #5 governs AC-1..8. Do not change `skills/engineering-pr-delivery-v3.5` or any production code to adopt this convention.

## Single compact status line

At a coordinator checkpoint, emit exactly one current-observation line in this form:

```text
STATUS | Tab2 | chat=<chat-id> | issue=#294 | plan=<revision> | task=<task-id> | state=<PLANNED|IN_PROGRESS|COMPLETE_DOC_ONLY|VERIFIED_SMALL_TASK|HOLD|UNKNOWN> | source=<exact-ref-or-UNKNOWN> | proof=<scope> | AC=<accepted-count/8-or-UNKNOWN> | release=<HOLD|UNKNOWN|AUTHORIZED_FROM_OWNER_SOURCE>
```

**Current observation for CI01 (not live accepted P/E):**

```text
STATUS | Tab2 | chat=6acb041f | issue=#294 | plan=PLAN-15 | task=CI01 | state=COMPLETE_DOC_ONLY | source=PR324@8abe45dd195e613938ee004efa325cf4c9a99562 | proof=COORDINATION_READBACK_ONLY | AC=0/8 | release=HOLD
```

The status line describes **scope, task progress, observation and provenance only**. It MUST NOT contain hand-computed DELP `P/E`, a fabricated percentage, adopted graph, positive `CHECKPOINT_FACTS_V1`, or assumed reviewer/writer authority. An observed SHA is historical the moment a branch moves; re-fetch before consequential next work. Status `COMPLETE_DOC_ONLY` proves neither T37 fixture correction nor product acceptance. Unknown authorization remains UNKNOWN/HOLD.

## Tab log and end-of-reply contract

End **every user-facing reply in this Tab2 chat** with one `LOG` line (and keep any preceding `STATUS` line readable), using:

```text
LOG | Tab2 | chat=6acb041f | event=<compact-event> | issue=#294 | task=<task-id> | source=<exact-ref-or-UNKNOWN> | proof=<scope> | AC=0/8 | release=HOLD
```

- Keep **append-only** chronology in the pre-existing `LINEAGE.md`, `CHECKPOINTS.md`, `EVIDENCE.log`; do not rewrite RECON historical reports, other tabs, or old GitHub comments.
- `LINEAGE.md`: chat ID, current PLAN_UPDATE permalink, responsibility boundary, relevant commit/provenance and references. `CHECKPOINTS.md`: requested task, state, exact source observation, completed/not-completed distinction, next legitimate unit. `EVIDENCE.log`: each read/write result with path, GitHub URL/commit or provider reference, proof grade, and non-authority limits.
- Use one coordinator commit per bounded file write as needed: `coord-log: Tab2 ... [skip ci]`. Fetch the latest file blob before update and use optimistic blob-SHA guard. Never quietly overwrite another tab or concurrent changes. Read back each changed file and link the exact source ref before declaring success.
- Parent #5 receives **M/L future improvements** as a backlog, not an XS/S gate; #294 owns XS/S implementation plan and task checkpoints. Source tests/functional fixes belong to issue #20 and a properly scoped candidate PR, not this coordination log.
- On any provider/CI/authorization mismatch write `UNKNOWN` or `HOLD`; passing negative oracle, skipped job or template is never positive acceptance.
- Source-grounded starting evidence: [Tab2 RECON4](RECON/2026-10-11/4-report.md) blob `12de45e823e099d308d53107d54441fa97559130`; [PLAN-15](https://github.com/reallakshman19/Common/issues/294#issuecomment-6105200239); [M/L backlog](https://github.com/reallakshman19/Common/issues/5#issuecomment-6105202248). PR324 original 283-test suite is 262/21, green T36 only reproduced RED; programme AC0/8, release HOLD.

## CI01 acceptance

CI01 is complete **as documentation/coordination only** when the interface file, chat ID in `LINEAGE.md`, a task checkpoint and a log record are all present at GitHub main and independently re-fetched. No coding of T37/T38/CI02, no source-test claim, no native positive witness, no release. Readback success then supports `VERIFIED_SMALL_TASK` for CI01's own observation convention only.
