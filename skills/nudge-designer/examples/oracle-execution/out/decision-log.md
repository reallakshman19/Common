# Current decision basis

1. **Native passes were insufficient.** [Owner conditions](../raw/owner.md) include
   same-project supersession, project return and late cancellation callbacks.
   [Original native checks](../raw/test_existing.py) pass four cases, but
   [Oracle baseline traces](baseline-probe.stdout.txt) show ten contrary schedules:
   old callbacks return true and mutate rows/error/busy. Inspecting
   [original source](../raw/session.py) shows callback guards use scope only.
   Direction: require operation-lifetime identity, not just project equality.
2. **Keep one coupled repair.** `begin`, both terminal callbacks and `cancel`
   share callback ownership. [Task map T-SESSION](task-map.json) retains them in
   one bounded deliverable. Oracle keeps the state model, acceptance and scope;
   the fresh worker receives the established GUIDED method and meaningful
   positive/negative checks in the [actual issued brief](issued-worker.md).
3. **Verification is source-derived local behavior.** Oracle authored
   [explicit witnesses](../work/oracle_probe.py) and
   [bounded schedule enumeration](../work/oracle_sequence_check.py) before
   reading the worker return. They compare issued-handle ownership and every
   public snapshot, sharing the stated Owner/source assumptions. Their success
   can support this repair, not unseen transfer, real concurrency or UI behavior.

Issued records remain unchanged; this file records the actual execution continuation. Parent clarified that task-local commissioned returns are allowed to
inspect; that scope-only clarification is recorded in [coordination](coordination.json).


4. **Return supports the issued diagnosis; retain the repair.** Read the complete
   [worker source and tests](../work/session.py), [native return](worker-return.md),
   its native check logs, hash comparison and diff. Actual source changes are
   limited to sequence guards in both callbacks and cancellation invalidation.
   No source/model conflict or corrective reissue was needed. The worker's
   SELF-ASSESSED result did not itself accept the whole outcome.
5. **Integrated local outcome accepted from actual checks.** Oracle reran the
   native/focused tests and its prewritten witnesses on the returned candidate;
   [actual command receipts](final-checks.json) show all exit zero. The
   [ten-case trace](final-probe.stdout.json) passes 10/10 and
   [enumeration](final-enumeration.stdout.json) passes 7,024/7,024 schedules,
   versus 4,480/7,024 on [the original source](baseline-enumeration.stdout.json).
   The [final byte comparison](final-integrity.json) confirms raw content, file
   set and manifest unchanged. Preserve issued map/intent/plan r1: these are
   execution/evidence changes, not new task meaning needing an invented revision.
   Current state is [current.md](current.md); no additional local repair remains.
