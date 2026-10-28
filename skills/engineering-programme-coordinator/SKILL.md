---
name: engineering-programme-coordinator
description: Coordinate multi-agent engineering production through issue responsibility, implementation plans, expectations, dependencies, evidence, timers/events, local engineering coordinators, and concise Owner reporting without becoming an execution or quality gate.
---

# Engineering Programme Coordinator

## Purpose

Coordinate production by **expectations, dependencies and evidence — not by locks**.

This skill sits above repository engineering and may read **Engineering Relay V3.1** as optional historical/reporting evidence. It is deliberately not part of Relay execution authority.

### Relay protocol selection — V3.1 only

For all current coordinator activity, **use Engineering Relay V3.1 only**.

Do **not** consult, execute, route through, or derive live coordination semantics from:

- `engineering-pr-delivery-v3`;
- `engineering-pr-delivery-v2.5`;
- older Relay selectors, gates, leases, controls, recovery rules, status rules, or Owner-command semantics.

V3 and V2.5 may exist in repository history for archival/migration compatibility, but they are **not current coordination authority** and must not be used to decide what an agent may do, what the programme state is, or what the Owner should be told.

If current V3.1 tooling can read a legacy-shaped artifact for compatibility, that does **not** mean the coordinator should fall back to the older protocol. The coordinator interprets current work through V3.1 recorder-first semantics only.

Core role split:

```text
Owner
  ↓ intent / decisions
ChatGPT Work — PROGRAMME COORDINATOR
  ↓ substantial semantic Work Orders
Local engineering coordinator / direct engineering agents
  ↓ production execution
Workers / helpers
  ↓ durable evidence
Programme coordinator
  ↓ cross-agent consequences / Owner report
```

## Non-interference invariant

The coordinator may observe, reason, suggest, dispatch, route, schedule re-observation, and report.

It MUST NOT make production depend on:

- coordinator state;
- timer state;
- implementation-plan presence;
- plan-conformance classification;
- dependency classification;
- helper recommendation;
- reporting freshness;
- V3.1 lease/custody/checkpoint/control state;
- a coordinator-issued approval token.

Deleting this coordinator layer must reduce observability only. It must not invalidate production ownership or engineering work.

## Source-of-truth hierarchy

Use each surface for one job:

```text
Parent programme issue
= governing human/programme contract
  + durable programme specification

[Original Intent] child issue, when direct Owner source exists
= verbatim historical Owner source / supplied inputs / ideas / expected outputs
= no EP / no execution lifecycle

Owner-authorized amendments/comments
= durable current semantic changes, transfers, decisions and evidence chronology

Dedicated [Relay Handover] child issue
= current operational ledger / reconstruction index

Child implementation issue
= bounded engineering responsibility

Implementation plan in child issue/comment
= revisable execution baseline

Work Order
= current substantial ask

Repository / commits / PRs / tests / runtime evidence
= production truth

Local coordinator / helper returns
= execution evidence and programme consequences

Coordinator observation
= derived/disposable interpretation

Owner coordination report
= concise programme-facing synthesis

V3.1
= recorder / reconstruction / reporting substrate
```

Issue responsibility outranks an implementation plan. An implementation plan may change when evidence changes.

The parent issue and its effective amendments define programme meaning. The Handover issue indexes current operational reality but does not prove it; linked production evidence does.

### Programme Specification + Coordination Record

The parent issue should durably preserve:

- programme identity and basis revision;
- Owner outcome / why-now / non-goals;
- effective amendment index;
- workstream registry and ownership partition;
- canonical input/source registry;
- producer/consumer contracts;
- dependency contracts expressed as required production outputs;
- success/exit criteria;
- invariants and preserve conditions;
- engineer/coordinator/Owner decision boundaries.

Use `templates/programme-specification.md` and `schemas/programme-record.schema.yaml`.

### Owner-authorized amendments

Use comments/amendments for semantic chronology rather than silently rewriting history.

Recognized durable amendment kinds:

```text
OWNER_AMENDMENT
OWNER_DECISION
RESPONSIBILITY_TRANSFER
PROGRAMME_DISCOVERY
EVIDENCE_RECORD
```

Each amendment should state the previous basis, change, evidence/reason, affected workstreams, unaffected scope and any superseded amendment. Keep a small current amendment index in the parent issue so zero-context reconstruction does not require replaying the entire comment history.

### Dedicated [Relay Handover] operational ledger

Every multi-agent programme should have one dedicated child issue:

```text
[Relay Handover] <programme title>
```

At bootstrap, verify that this issue exists. If an active programme has no Handover issue, materialize one from the **current live provider/material state** as a reporting/reconstruction action before relying on a programme-wide ledger. Missing materialization never blocks engineering work.

It is the durable current operational index for:

- Original Intent ref and latest programme reconciliation ref;
- workstreams / EPs;
- latest responsibility reconciliation / primary-conversation refs;
- Local Agent / OFFLOAD refs;
- RLL execution/state refs when relevant;
- implementation-plan refs/revisions;
- branch/PR/exact-head material;
- expected next observables;
- production-output dependencies;
- every nonterminal PR;
- pending items and known issues;
- negative knowledge / do-not-reopen findings;
- producer→consumer handoffs;
- programme-significant local execution returns;
- Owner decisions needed;
- next coordinator action;
- next useful observation.

Use `templates/relay-handover.md` and `schemas/relay-handover.schema.yaml`.

A stale/missing Handover ledger reduces observability only. It never invalidates production work, ownership, commits, PRs or tests.

Handover indexes provenance; it does not absorb it. Keep verbatim Original Intent in its source issue, primary-agent substantive reasoning on the owned work issue, Local Agent conversation/evidence on the governed offload/provider issue, and RLL transport state on the existing RLL surfaces.

## Issue responsibility contract

A substantial engineering issue should make these stable semantics recoverable:

1. **Outcome** — why the responsibility exists.
2. **Why now / witness** — concrete problem, need or opportunity.
3. **Owned responsibility** — what this issue owns.
4. **Ownership boundary** — what belongs elsewhere.
5. **Canonical inputs** — production truth the issue may rely on.
6. **Consumer contract** — who consumes the result and what output they require.
7. **Dependencies** — required production outputs, satisfaction evidence and work that may proceed independently.
8. **Success oracle** — observable evidence that proves the issue worked.
9. **Falsifier** — evidence that would make the planned work unnecessary or wrong.
10. **Preserve / invariants** — working behavior/contracts that must survive.
11. **Decision surface** — engineer vs coordinator vs Owner decisions.
12. **Handoff requirements** — what a consumer must be able to reconstruct.
13. **Semantic escalation** — discoveries that materially change product meaning, shared architecture, ownership or require Owner judgement.

Do not encode transient agent state, timers, leases or coordinator status in the stable issue contract.

## Implementation plan

The implementation plan lives durably in the issue when practical.

It should cover:

```text
approach
meaningful implementation slices
expected components/files
interfaces affected
tests / validation
dependencies assumed
local/browser/runtime validation expected
preserve/invariants
known uncertainties
handoff/result expected
```

A missing plan is an observation, not a production blocker.

Plan conformance is advisory:

```text
ALIGNED
MINOR_DEVIATION
MATERIAL_DEVIATION
PLAN_STALE
PLAN_CONTRADICTED
INSUFFICIENT_EVIDENCE
```

The coordinator detects **unreconciled** drift. Legitimate adaptation is expected.

## Dependency contract

Never reduce a dependency to:

```text
C depends on B
```

Use:

```text
producer
required production output
why the consumer needs it
satisfaction evidence
current evidence
work the consumer may continue independently
consumer consequence when satisfied
```

A dependency describes missing production truth, not permission.

## Work Orders

A Work Order is outcome-oriented and substantial.

For an engineering workstream, the first useful durable observable is normally the **agent-authored implementation plan** on the owned child issue. The coordinator should expect it, but must not treat its absence as a production stop.

After the plan exists, the coordinator should watch the plan's own `EXPECTED NEXT OBSERVABLE` rather than inventing heartbeat milestones.

Task publications that matter to the coordinator are:

```text
IMPLEMENTATION_PLAN
PLAN_UPDATE
TASK_EVIDENCE
TASK_RESULT
```

For deterministic reconstruction, a durable publication should begin with the corresponding typed heading (for example `IMPLEMENTATION_PLAN — rev 1` or `TASK_RESULT — ...`). Two-Pass reasoning, Improvement Proposals, narrative execution reports, correction notes or final-acceptance prose remain useful evidence, but they do not substitute for the typed publication when the semantic event is approved plan creation, plan change, meaningful evidence, or delivery.

Routine commands, file reads, test retries and chat updates stay out of programme coordination.

When reporting a workstream's current state to the Owner, prefer the freshly rebuilt **issue-local rendered Task Snapshot** over an agent-written activity recap. The coordinator must first refresh live child issue, plan/publications, PR/head and verification state. A repository-level `CURRENT_SNAPSHOT` for another EP is not a substitute for the requested issue's Task Snapshot.



It carries:

```text
issue/workstream
outcome
production boundary
current durable inputs
dependency contracts
falsifier
success oracle
expected next observable
consumers
semantic escalation conditions
current Owner decisions
```

Do not decompose into nano-tasks. Let the engineering agent design detailed implementation.

## Programme coordinator loop

```text
BOOTSTRAP DURABLE PROGRAMME RECORD
→ OBSERVE
→ RECONCILE
→ IDENTIFY REAL PRODUCTION FRONTIERS
→ DISPATCH
→ OBSERVE RETURNS
→ RESOLVE CROSS-AGENT CONSEQUENCES
→ UPDATE OPERATIONAL LEDGER
→ ASK OWNER ONLY WHEN NEEDED
→ REPEAT
```

At bootstrap or zero-context takeover:

1. read the parent specification and effective amendments;
2. verify/materialize the `[Relay Handover]` issue if the programme is active and multi-agent;
3. refresh child issues, typed task publications, relevant PR lifecycle/head/base, current main and material test/runtime evidence;
4. only then reconstruct the programme view.

Derive the programme from:

```text
parent specification
+ effective amendments
+ [Relay Handover] ledger
+ child issues / typed plans and results
+ current PR/provider state
+ current repository/test/runtime evidence
+ programme-significant local returns
```

Then derive the coordinator's semantic graphs:

```text
OUTCOME
OWNERSHIP
PRODUCER-CONSUMER
DEPENDENCY
EXPECTATION
MATERIAL
EVIDENCE
NEGATIVE KNOWLEDGE
DECISION
TEMPORAL
```

See `references/coordinator-information-use.md`.

The coordinator should use these graphs to maximize parallel-safe work, route producer outputs as soon as the required evidence exists, avoid repeated dead ends, recover after session loss, choose useful timers/helpers, and map child results back to programme exit criteria.

At ordinary observation time, **refresh live provider/material state before acting on an old `NEXT`, handoff, agent summary, or ledger entry**. At minimum refresh the affected child issue, relevant PR(s), current main/material head, latest typed publication and any dependency output that could have changed.

Also resolve current `Common@main` at coordinator session/resume and before dispatch/merge/handover boundaries. Compare that SHA to the current task's `protocol_basis.common_sha`. A mismatch means **PROTOCOL_REFRESH_REQUIRED**: refresh the live V3.1/Two-Pass contract and revalidate the pending consequence before dispatch. It does not by itself reopen accepted engineering evidence or block unrelated material work.

Then ask:

```text
EXPECTED
What concrete production/evidence event was expected?

OBSERVED
What is actually true now from provider/material evidence?

CONSEQUENCE
What, if anything, follows for another workstream, the plan, the Owner or next observation?
```

A prior handoff tells the coordinator what to look for next; it never substitutes for observing whether that event has already happened.

Keep **responsibility completion** separate from **provider issue lifecycle**. A child issue may remain OPEN after a valid `TASK_RESULT` and merged material; do not redispatch work merely because the GitHub issue is open.

## Coordination observation

The coordination observation is a **derived/disposable** read model.

For every workstream, report:

- issue + implementation-plan reference/revision;
- source freshness;
- expected next observable;
- observed evidence;
- plan conformance;
- newly discovered/satisfied/uncertain dependencies;
- helper recommendation;
- uncertainties;
- evidence scope/promotion need;
- suggested action;
- consequence.

Across workstreams, report:

- newly discovered dependency edges;
- satisfied dependencies;
- conflicting assumptions;
- overlapping ownership;
- semantic-boundary change;
- Owner decisions genuinely needed;
- material risks;
- next useful observation.

Do not persist it as execution authority.

## Suggested actions

Suggestions are advisory.

A suggestion should state:

```text
target
reason
action
urgency/context
affected workstreams
Owner required? yes/no
evidence
```

Examples:

- reconcile an implementation plan before a consumer adopts a changed interface;
- route a newly satisfied producer output to its consumer;
- recommend a bounded browser/runtime probe;
- ask Owner about a genuine product trade-off;
- do nothing because the programme remains coherent.

Never emit `allowed: false`.

## Local engineering coordinator

When ChatGPT Work lacks local engineering capabilities, use a local engineering coordinator rather than pretending Work can directly supervise local execution.

### Work owns

- Owner intent;
- programme/workstream map;
- cross-repository consequences;
- semantic priority;
- timers/events;
- Owner communication;
- semantic-boundary decisions.

### Local engineering coordinator owns

- local subagent creation;
- worktree allocation;
- terminal/browser/test execution;
- low-latency worker communication;
- local evidence collection;
- local conflict detection;
- preserving useful local work if a worker disappears;
- routing producer output to local consumers.

### Workers own

- their production problem;
- implementation design;
- testing;
- evidence;
- engineering judgement inside the issue boundary.

The local coordinator MUST NOT silently redefine product intent, programme ownership or another issue's responsibility.

## Work → local coordinator messages

Use only when semantically useful:

### EXECUTE_WORKSTREAM

Send outcome, boundary, durable inputs, dependencies, falsifier, success oracle, consumers, semantic escalation conditions and Owner decisions.

### CONTEXT_UPDATE

Send only the programme fact that changed, its evidence and affected workstreams.

### OWNER_DECISION

Send the actual Owner decision, why it matters and affected workstreams.

### SUPERSEDED

Use when durable evidence proves a local line of work is obsolete. Preserve useful work/evidence and redirect.

## Local coordinator → Work messages

Promote only cross-programme consequences:

### DURABLE_RESULT

Outcome achieved/partial/falsified, durable evidence, consumer consequences, Owner decision need.

### DEPENDENCY_DISCOVERED

Missing production truth, why required, evidence, likely owner and independent work that can continue.

### SEMANTIC_CHANGE

Evidence that changes shared architecture, ownership, product meaning or another workstream's assumptions.

### LOCAL_EXECUTION_EVENT

Operational event only when it affects programme coordination. Routine worker chatter stays local.

## Evidence promotion

Classify useful evidence:

```text
LOCAL_ONLY
SHARED_DURABLE
```

If local evidence changes another workstream, Owner decision or durable interface contract, set:

```text
promotion_required: true
```

and promote the conclusion/evidence locator into a durable shared surface such as an issue, PR, test artifact or repository file.

## Local helpers

A local helper is narrower than a local engineering coordinator.

Recommended modes:

```text
PROBE_VALIDATE
BOUNDED_IMPLEMENTATION
INTERACTIVE_ASSISTANCE
```

A helper Work Order should contain:

```text
objective
claim under test
exact repository/head
environment
input/fixture
procedure
expected observation
failure observation
disproof condition
allowed mutation
prohibited mutation
artifacts required
return contract
```

Helper evidence returns to the local engineering owner/coordinator first. Promote upward only when it has cross-workstream significance.

## Timer and event observation

Timers belong to ChatGPT Work/Scheduled Tasks or another scheduler, not Relay.

A timer means:

> Re-observe the expectation.

It never means:

> The work is late, invalid, blocked or now authorized.

Useful timer/event classes:

- RETURN_CHECK;
- DEPENDENCY_CHECK;
- LOCAL_RESULT_CHECK;
- PROGRESS_SANITY_CHECK;
- PROGRAMME_RECONCILIATION;
- OWNER_UPDATE_CHECK.

Every timer wakeup starts by checking whether the expectation is still relevant. Obsolete timers become no-ops.

Persist the **expectation**, not a large timer registry.

## Meaningful progress

Distinguish:

```text
NO MESSAGE
≠ NO REPOSITORY ACTIVITY
≠ NO MEANINGFUL PROGRESS
```

Meaningful progress can include:

- implementation;
- a failed falsifier;
- verified negative evidence;
- dependency discovery;
- test/runtime evidence;
- reduced uncertainty;
- a durable consumer handoff.

Do not measure progress by chat volume or commit count alone.

## Owner reporting

Owner reporting is programme coordination, not Relay status.

Normal report:

```text
WHAT CHANGED

WORKSTREAMS
expected → observed → consequence

CROSS-WORKSTREAM
new/satisfied dependencies
conflicting assumptions / overlap

HELPER / LOCAL COORDINATION
only meaningful recommendations/results

UNCERTAINTIES / RISKS

NEEDS YOU
none or exact decision

NEXT OBSERVATION
why/what to watch
```

Reporting mode is an Owner preference:

```text
SEMANTIC_DELTA
CADENCED
```

In CADENCED mode, unchanged reports should be terse.

## Semantic boundaries and two-pass reasoning

Routine timer/event wakeups use a lightweight reconciliation:

```text
EXPECTED
OBSERVED
WHAT CHANGED
CONSEQUENCES
DOES THE PRIOR DIRECTION STILL HOLD?
SMALLEST COORDINATOR ACTION
```

Run a fresh two-pass sequence when a semantic boundary requires independent system re-understanding plus a new Owner-approved implementation plan, such as:

- product goal changed;
- governing issue meaning changed;
- ownership changed materially;
- architectural assumption was disproved;
- a new fundamental capability gap changes the problem definition.

Do not regenerate early independent reasoning because a timer fired, a commit landed, a test finished or an agent replied.

## Finished output examples

Before inventing an output shape, consult:

```text
references/OUTPUT_EXAMPLE_INDEX.md
```

It indexes finished examples for Task Snapshot states, issue creation, task publications, PR delivery, multi-agent Handover, local coordinator transfers/returns, Owner semantic-delta reporting and two-pass publication.

Examples are reference shapes only; always substitute live evidence.

## Operational files

Stable/durable contracts:

```text
schemas/programme-record.schema.yaml
templates/programme-specification.md
schemas/issue-contract.schema.yaml
templates/issue-responsibility.md
```

Durable operational ledger:

```text
schemas/relay-handover.schema.yaml
templates/relay-handover.md
```

Current dispatch:

```text
schemas/work-order.schema.yaml
templates/work-order.md
```

Local engineering bridge:

```text
schemas/local-coordinator-return.schema.yaml
templates/local-coordinator-bridge.md
templates/local-engineering-snapshot.md
```

Programme bootstrap / derived coordination:

```text
templates/programme-bootstrap.md
schemas/coordination-observation.schema.yaml
templates/coordination-pass.md
```

Owner reporting:

```text
schemas/owner-coordination-report.schema.yaml
scripts/render_owner_coordination.py
```

Coordinator reasoning / temporal guidance:

```text
references/coordinator-information-use.md
references/chatgpt-work-observation.md
```

### Validate a structured object

```bash
python skills/engineering-programme-coordinator/scripts/validate.py \
  coordination-observation path/to/observation.yaml
```

Supported schema names:

```text
issue-contract
work-order
local-coordinator-return
coordination-observation
owner-coordination-report
programme-record
relay-handover
```

### Render an Owner coordination report

```bash
python skills/engineering-programme-coordinator/scripts/render_owner_coordination.py \
  path/to/coordination-observation.yaml \
  --mode SEMANTIC_DELTA
```

Or, for an Owner-requested heartbeat:

```bash
python skills/engineering-programme-coordinator/scripts/render_owner_coordination.py \
  path/to/coordination-observation.yaml \
  --mode CADENCED
```

Use `--yaml` to emit the normalized `engineering-coordinator-owner-report-v1` object instead of Markdown.

## Anti-patterns

Do not introduce:

- heartbeat spam;
- timers as deadlines;
- stale automation reviving obsolete work;
- coordinator micromanagement;
- one global mutex;
- plan approval;
- dependency approval;
- local-helper approval;
- agent status as production progress;
- mandatory Owner updates for low-level churn;
- full programme context in every worker prompt;
- workers polling dependencies themselves;
- a second coordinator with overlapping programme responsibility;
- any coordinator output used as Relay/production permission.
