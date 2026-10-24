# Changeover and succession — inherit the established Oracle contract

**Normative source at the Owner-selected reference commit**
`f2fe525264b486c397d1f2b3dbcb013d9c83ae0a`:
[Oracle Continuity](../../oracle-continuity/PROTOCOL.md) §§2, 6–9;
[Task Decomposer Oracle use](../../task-decomposer/references/ORACLE_USE.md);
[Nudge Designer Oracle OnBoard](../../nudge-designer/references/ORACLE_ONBOARD.md);
[Prototype-first](../../prototype-first/SKILL.md) §After a prototype is finalized;
[Contribution Handoff](../../CONTRIBUTION_HANDOFF.md);
[Local-agent handover](../../local-handover/AGENT_PROTOCOL.md).

This is a decision guide for a GitHub Cycle operator, not a second
continuity schema, permission service, or new compulsory agent position.

## 1. Distinguish recommendation, preparation, and activation

| Event | Meaning | What it must NOT imply |
|---|---|---|
| **RECOMMEND_CHANGEOVER** | Current evidence suggests a replacement may improve delivery | Agent retired, task handed over, executor unauthorized |
| **PREPARED_SUCCESSOR** | Candidate session/checkpoint/onboarding ready; capability check may be pending | Current assignment displaced or successor may write |
| **CUTOVER_ACTIVATED** | Authorized canonical publication superseded the old binding, selected successor and adopted work | Physical write access revoked unless the adapter did so |
| **ORACLE_CONTROL_TRANSFERRED** | New Oracle control epoch published with ongoing assignments explicitly adopted | New aim, changed task scope, review reset or release authority |
| **LATE_RETURN** | Old actor delivered after cutover | Latest/current artifact or accepted evidence |
| **ADOPTED_RETURN** | Oracle records an authorized, exact-version decision to use a late return | Predecessor reacquired write/control authority |

A `Cycle now` prompt triggers *reading and checking* these states;
it cannot itself effect a secure handover. A short URL ID, copied
response or role label is never authenticated actor identity.

## 2. When to suggest an agent change

Suggest **continuing** with the current agent when progress and evidence
are useful, access exists, scope is settled and changeover cost outweighs
benefit. A long task alone is not proof that a fresh chat is better.

Suggest **bounded replacement or assistance** when a material blocker
recurs after correct input and method, a decisive capability is absent,
current context no longer carries essential project meaning, or the
Owner expressly prefers another participant. First inspect
sender/measurement/access errors rather than blaming worker ability.
Keep a coherent task intact where splitting would lose its
model/architecture decisions or multiply handoff costs.

At finalized prototype boundaries, the Owner/coordinator may promote
a participant to Oracle only if it **demonstrated understanding beyond
its own artifact** (traced contradictions, preserved source model,
made useful grounded decisions). Once Oracle-only, the participant
writes slices/briefs and reviews returns, rather than silently
continuing as an unreviewed producer. Preserve the frozen baseline and
the next two connected delivery cards.

**Special Owner-selected ChatGPT-agent activity duty:**
if and only if selected for this agent/project and the actual surface
is in scope, retain its episode across subtasks, record observable
GitHub-access turns and recorded active-turn minutes, and suggest
BuddyRunner after **>5 distinct GitHub-access turns OR >35 recorded
active-turn minutes**. Do not count tool calls as turns, sum agents'
episodes, reset per subtask, or invent hidden timing. ChatGPT Work and
other specified exempt surfaces remain outside this activity rule;
UNKNOWN applicability is not an exemption. Recommend only once per
episode; this is a suggestion, **not** automatic retirement, forced
handover, a universal stop or a measure of model competence.
Reference: `task-decomposer/references/ORACLE_USE.md` §Owner-selected
ChatGPT-agent activity duty and `nudge-designer/references/ORACLE_EXECUTION.md`.

## 3. Worker replacement: prepare and cut over safely

1. **Checkpoint:** retain original Owner aim/amendments, stable task ID,
   source and exact frozen baseline, current candidate bytes/hashes,
   decisions and alternatives, evidence lineage, remaining defects,
   state/assignment revision, actual in-flight operations and the
   next precise action. Use the existing selected task/custody record.
2. **Reconcile old worker:** inspect actual GitHub issue/PR/Drive
   side effects and unconfirmed actions. Try to stop or isolate the
   predecessor using the real channel. Mark uncertainty UNKNOWN,
   not “stopped” merely because a new chat opened.
3. **Prepare successor:** issue an [Oracle OnBoard Prompt](../../nudge-designer/references/ORACLE_ONBOARD.md)
   when meaningful prior understanding exists. Preserve the same
   task ID, assign a **new assignment/session generation** with
   `replaces_assignment_id` in the continuity-native record, probe
   actual access/capability and agree on isolated branch/output.
   A prepared successor may read but **must not** share the
   predecessor's uncontrolled write scope.
4. **Publish one cutover:** under actual Owner/project authority and
   compare-and-swap publication, retire/cancel/supersede predecessor
   assignment, activate the successor binding and record the
   effective control revision. The old assignment remains historical.
5. **Resume:** successor rechecks originals and current file bytes,
   performs the next bounded action, and returns observed evidence.
   Carry forward only still-applicable verdicts on exact candidate
   and claim; previous observations are not erased.
6. **Late result:** record separately. Select the late artifact only
   by explicit `adopt_return` decision bound to its exact bytes/revision;
   never silently reelect the old worker.

If old/new workers still have overlapping writes, isolation is
required on the **actual** write surface (branch locks, permissions,
separate output files, or adapter-mediated scope). A declared
`CURRENT.json` “retired” status cannot revoke write access.
GitHub PR merging or branch write controls are real side effects;
do not pretend prose is an enforced lease.

## 4. Oracle succession: control epoch, not task reset

- Select successor from observed project understanding and suitable
  granted role authority, not the number of messages or a fresh
  model/session label.
- Carry baseline, aim, source/decision model, protected invariants,
  old/ongoing assignments, unresolved return claims and **the next two
  connected deliveries**. A useful *onboarding prompt* preserves
  context but never overrides originals.
- Prepare the old/new Oracle sessions and old-epoch→new-epoch
  control handover. Publish one authorized cutover: old control
  binding retired, new binding activated, **ongoing worker assignments
  explicitly adopted**. Existing execution continues where safe.
- An Oracle successor does **not** get new approval, merge, release
  or engineering scope merely by promotion. Source criteria and
  already independent reviews remain as before; affected self-authored
  expectations still require candid exposure assessment.
- Actual command publisher rejects stale old-epoch control commands.
  If no authenticated publisher exists, declare the cutover
  **administratively proposed / enforcement UNKNOWN** and use
  real branch/resource isolation. Do not claim guaranteed exclusivity.

## 5. What Oracle displays to the Owner

Keep it short and actionable; this is **not** a required multi-page form:

```text
CHANGEOVER: RECOMMENDED | PREPARING | ACTIVATED | HELD
FROM: <role, short chat ID, assignment/generation or epoch>
TO: <role, short chat ID, NEW assignment/generation or epoch>
WHY: <observed context/capability/cost evidence>
KEEPS: <task ID, frozen baseline, surviving checks, pending assignments>
ACTUAL WRITE ACCESS: <isolated/revoked/UNKNOWN>
NEXT: <one actor and observable step>
```

No unsolicited changeover ceremony when a normal current agent can
finish the next useful task. The Owner may prefer one capable builder
and a separately required reviewer; the protocol has no mandatory
number of agents.

## 6. Contradictory tests

A fresh chat named Oracle with no control epoch → **not promoted**.
An old worker still writing to the same branch → **no safe cutover claim**.
Successor proposed but no published revision → **prepared, not active**.
Old review PASS with changed target bytes → **historical scope only**.
Late predecessor return → **quarantined until adopted**.
BuddyRunner threshold crossed → **suggestion, not cancellation**.
Oracle contributed code → **SELF-ASSESSED** for affected claims.
A GitHub comment acknowledging handoff → **receipt, not source proof
or exclusivity**.
