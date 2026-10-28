# [Relay Handover] Programme Operational Ledger

This child issue is the durable **current operational index** for one programme.

It is continuously useful during multi-agent execution, not only when a human/agent hands over.

It is an index to durable evidence, not the engineering truth itself.

```text
ISSUE_ROLE: RELAY_HANDOVER
PARENT_PROGRAMME: github:<owner>/<repo>#<parent>
PROGRAMME_BASIS_REVISION: PB-....
RELAY_PROTOCOL: V3.1_ONLY
```

## Non-authority rule

Missing, stale or incorrect Handover content may reduce observability/reconstruction quality.

It does **not** invalidate production work, revoke ownership, block coding, block PRs or authorize execution.

A ledger statement such as "B produced X" is not proof by itself. Link the commit/PR/test/artifact that proves X.

## Programme basis

- Parent:
- Current effective programme basis:
- Last observed main:
- Last reconciled at:

## Reconstruction references

- **Original Intent:** <github issue/ref or NONE>
- **Latest programme reconciliation:** <comment/event ref or NONE>
- **Roadmap refs:** <RM-* / ROADMAP_RECONCILED refs>

These are pointers only. Do not copy the Original Intent body or conversation transcript into Handover.

## Workstreams

### <A> — <child issue>

**Owned outcome:** ...

**Implementation plan:** PRESENT / MISSING / STALE / UNKNOWN — <ref/revision>

**Plan responsibility basis:** <child issue/provider ref + body/contract digest when available>

**Agent / local coordinator ref:** ...

**Provider issue state:** OPEN / CLOSED / UNKNOWN

**Branch:** ...

**PR:** ...

**Base:** ...

**Exact head:** ...

**Task Snapshot:** <ref>

**Latest responsibility reconciliation:** <ref or NONE>

**Primary conversation refs:** <refs only>

**Agent continuity:** <AGENT_STATUS_V1 ref / custody epoch / NEW|HANDOFF|RECOVERY / ACTIVE|HANDOFF_READY|COMPLETE|SUPERSEDED|BLOCKED>

**Unresolved Further task IDs:** <FT-* refs only>

**Predecessor status ref:** <ref or NONE>

**Local Agent / OFFLOAD refs:** <refs only>

**RLL execution/state refs:** <refs only>

**Responsibility state:** COMPLETE / PARTIAL / OPEN / NOT_RUN / UNKNOWN

**Child acceptance:** SATISFIED / PARTIAL / OPEN / UNKNOWN — <coverage or UNKNOWN>

**Programme contribution:** SATISFIED / PARTIAL / OPEN / UNKNOWN — <coverage or UNKNOWN>

**Verification:** PASS / PARTIAL / FAIL / NOT_RUN / PENDING / UNKNOWN — <failure origins>

**Delivery:** NONE / DRAFT / OPEN / REVIEW_READY / CHANGES_REQUESTED / CONFLICTED / MERGED / CLOSED / UNKNOWN

**What remains:**

- ...

**Expected next observable:** ...

**Latest task publications:**

- IMPLEMENTATION_PLAN / PLAN_UPDATE / TASK_EVIDENCE / TASK_RESULT refs only

**Latest durable evidence:**

- ...

**Next programme consequence:** ...

Repeat for every active/nonterminal workstream, and retain recently completed workstreams while their result still has an unresolved consumer/programme consequence. Provider issue state and responsibility state are independent; an OPEN issue may already have a completed responsibility.

## Dependency ledger

| Producer | Required production output | Consumer | State | Evidence | Independent work |
| --- | --- | --- | --- | --- | --- |
| B | ... | C | MISSING / UNCERTAIN / DISCOVERED / SATISFIED / SUPERSEDED | ... | ... |

Do not represent dependencies as permission locks.

## Nonterminal PRs

Carry every nonterminal PR until it is merged, closed or superseded.

| PR | Workstream | Lifecycle | Head | Base | Mergeability / review | Note |
| --- | --- | --- | --- | --- | --- | --- |
| #... | ... | DRAFT / OPEN / CHANGES_REQUESTED / CONFLICTED / REVIEWABLE / UNKNOWN | ... | ... | ... | ... |

## Pending items

- ...

## Known issues

- ...

## Negative knowledge / do-not-reopen

For each important rejected path or disproved assumption:

### NK-...

**Statement:** ...

**Evidence:**

- ...

**Reopen only if:** ...

This prevents replacement agents from re-running already-settled dead ends.

## Recent producer → consumer handoffs

### <producer> → <consumer>

**Output:** ...

**Evidence:**

- ...

**Proved:**

- ...

**Not proved:**

- ...

**Known limitations:**

- ...

**Consumer must not infer:**

- ...

## Local engineering coordination

Promote only programme-significant local results:

- durable result;
- discovered production dependency;
- semantic change;
- local evidence requiring shared promotion;
- session loss with material programme consequence.

Do not copy routine worker chatter or command logs here. Keep the full mutable AGENT_STATUS_V1 comment on the owned work issue, Local Agent conversation/evidence on its governed OFFLOAD/provider issue, and RLL operational chatter/state on the existing RLL surfaces; Handover only indexes the refs/FT IDs needed for reconstruction.

## Owner decisions needed

Prefer:

```text
NONE
```

When needed, state the exact decision, why it belongs to the Owner, affected workstreams, evidence and reversible consequences.

## Next coordinator action

What is the smallest useful coordination move now?

Examples:

- route B's durable output to C;
- send a CONTEXT_UPDATE to local coordinator;
- observe an expected PR result later;
- reconcile a semantic change;
- ask Owner one genuine question;
- do nothing.

## Next useful observation

**Reason:** ...

**Expected evidence:**

- ...

A timer/event may be used to wake this observation, but the timer is never authority.
