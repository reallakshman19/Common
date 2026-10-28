# ChatGPT Work ↔ Local Engineering Coordinator

Use this bridge when ChatGPT Work owns programme coordination but local execution requires capabilities that Work does not directly provide.

The local engineering coordinator is **not** a second programme coordinator.

**Relay protocol rule:** if Relay material is consulted, use **V3.1 only**. V3 and V2.5 are historical/compatibility material and must not be used for live execution, coordination, recovery, gating, status or Owner-command semantics.

## Work → local: EXECUTE_WORKSTREAM

```text
EXECUTE_WORKSTREAM

WORKSTREAM
<stable alias / issue ref>

OUTCOME
<what must become true>

PRODUCTION BOUNDARY
OWNS:
- ...

EXCLUDES:
- ...

CURRENT DURABLE INPUTS
- <issue/commit/PR/artifact + freshness/digest where useful>

DEPENDENCIES
- REQUIRED OUTPUT:
  ...
  WHY:
  ...
  SATISFACTION EVIDENCE:
  ...
  INDEPENDENT WORK:
  ...

FALSIFIER
- ...

SUCCESS ORACLE
- ...

EXPECTED NEXT OBSERVABLE
<what concrete production/evidence event should appear next>

CONSUMERS
- ...

SEMANTIC ESCALATION
Return only discoveries that materially change product meaning,
shared architecture, ownership, another workstream's durable assumptions,
or genuinely require Owner judgement.

OWNER DECISIONS ALREADY MADE
- ...
```

The local coordinator chooses engineering decomposition, workers, worktrees, tests and local probes.

For each substantial worker responsibility, the local coordinator should ensure the owning engineering agent has a durable child-issue `IMPLEMENTATION_PLAN` when practical. The worker authors the plan; the local coordinator does not replace engineering judgement with a coordinator-written plan.

Plan publication/revision is reconstruction context, never local execution permission.

## Work → local: CONTEXT_UPDATE

Use when one programme fact changed while local work continues.

```text
CONTEXT_UPDATE

CHANGED FACT
...

EVIDENCE
...

AFFECTED WORKSTREAMS
...

CONSEQUENCE
...

UNCHANGED ASSUMPTIONS
Everything else in the current Work Order remains unchanged.
```

## Work → local: OWNER_DECISION

```text
OWNER_DECISION

DECISION
...

WHY IT MATTERS
...

AFFECTED WORKSTREAMS
...

EFFECTIVE CONSTRAINT / CHOICE
...
```

## Work → local: SUPERSEDED

Use only when durable evidence makes existing local work obsolete.

```text
SUPERSEDED

WORKSTREAM
...

EVIDENCE
...

WHAT IS NOW OBSOLETE
...

WHAT USEFUL WORK/EVIDENCE TO PRESERVE
...

NEW DIRECTION
...
```

## Local → Work: DURABLE_RESULT

```text
DURABLE_RESULT

WORKSTREAM
...

OUTCOME
ACHIEVED | PARTIAL | FALSIFIED | UNKNOWN

SUMMARY
...

DURABLE EVIDENCE
- ...

CONSUMER CONSEQUENCES
- ...

INDEPENDENT REMAINING WORK
- ...

OWNER DECISION REQUIRED
NO | <exact question>
```

## Local → Work: DEPENDENCY_DISCOVERED

```text
DEPENDENCY_DISCOVERED

WORKSTREAM
...

MISSING PRODUCTION TRUTH
...

WHY REQUIRED
...

CURRENT EVIDENCE
...

LIKELY OWNER
...

SATISFACTION EVIDENCE
...

WORK THAT CONTINUES INDEPENDENTLY
- ...

PROGRAMME CONSEQUENCE
...
```

Do not say merely "blocked by X".

## Local → Work: SEMANTIC_CHANGE

```text
SEMANTIC_CHANGE

WORKSTREAM
...

DISCOVERY
...

EVIDENCE
...

WHY THIS CHANGES THE PROGRAMME/SHARED CONTRACT
...

AFFECTED WORKSTREAMS
...

LOCAL WORK THAT CAN CONTINUE
...

OWNER DECISION
NONE | <exact decision>
```

## Local → Work: LOCAL_EXECUTION_EVENT

Use only when an operational event affects programme coordination.

Good example:

```text
Worker session died.
Useful material is durable at <ref>.
Replacement worker is continuing.
No programme consequence.
```

Do not promote routine chatter:

- worker started;
- worker thinking;
- browser opened;
- test still running;
- worker idle;
- retrying command.

## Evidence promotion

Local evidence can remain `LOCAL_ONLY` while it matters only to local engineering.

Promote to `SHARED_DURABLE` when it:

- changes another workstream;
- changes a durable interface/contract;
- changes an Owner decision;
- is required for zero-context consumer reconstruction.

Promotion means persisting the useful conclusion/evidence locator in a shared durable surface such as an issue, PR, test artifact or repository file. It does not mean copying all local logs into GitHub.
