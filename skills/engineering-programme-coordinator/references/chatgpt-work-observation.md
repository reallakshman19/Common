# ChatGPT Work temporal observation

Timers/events are coordinator wakeups, not engineering authority.

## Core rule

```text
EXPECTATION
= programme meaning

TIMER / EVENT
= one mechanism that wakes re-observation
```

Persist the expectation. Do not build a large timer state machine into Relay or the coordinator repository model.

## Wakeup preflight

Every timer/event wake first asks:

1. Is the watched expectation still relevant?
2. Has the expected result already appeared and been consumed?
3. Was the work superseded?
4. Did the product/issue meaning change?
5. Is there any useful coordinator consequence now?

If the expectation is obsolete, the wakeup is a no-op.

## RETURN_CHECK

Use after dispatching substantial work when a future re-observation would be useful.

Prompt shape:

```text
Re-observe <workstream>.

Expected next observable:
<commit / PR / test / handoff / negative finding / dependency discovery>

Read durable production reality first.

Classify the observation:
DONE
PROGRESSING
NO_MEANINGFUL_PROGRESS
NEW_PRODUCTION_DEPENDENCY
SESSION_OR_CHANNEL_STALLED
UNKNOWN

Do not treat elapsed time as lateness or invalidity.
If the result already exists, route its consequence.
If nothing meaningful changed, do not manufacture intervention.
```

## DEPENDENCY_CHECK

```text
Re-check whether <required production output> now exists.

Consumer:
<workstream>

Satisfaction evidence:
...

If satisfied:
report exact evidence and consumer consequence.

If still missing with no material change:
remain concise/silent according to reporting mode.

Ignore coordinator/Relay status as permission.
```

## LOCAL_RESULT_CHECK

Use for short browser/runtime/local probes.

Recommended pattern:

```text
initial bounded wait
→ one bounded extension if visibly still executing
→ settle as evidence / failed / unknown
```

Do not poll indefinitely.

## PROGRESS_SANITY_CHECK

Ask about meaningful progress, not messages.

Meaningful progress includes:

- useful implementation;
- falsified hypothesis;
- verified negative result;
- dependency discovery;
- runtime/test evidence;
- reduced uncertainty;
- consumer handoff.

```text
NO MESSAGE
≠ NO REPOSITORY ACTIVITY
≠ NO MEANINGFUL PROGRESS
```

## PROGRAMME_RECONCILIATION

Use a recurring observation when several workstreams are active.

Prompt shape:

```text
Re-observe the active programme.

For each workstream:
EXPECTED
OBSERVED
CONSEQUENCE

Then inspect:
- new/satisfied dependencies;
- conflicting assumptions;
- ownership overlap;
- local evidence requiring promotion;
- helper opportunities;
- semantic-boundary changes;
- genuine Owner decisions.

If nothing meaningful changed, do nothing except the configured Owner reporting mode.
```

## OWNER_UPDATE_CHECK

Two valid modes:

### SEMANTIC_DELTA

Notify only when a meaningful coordination consequence exists.

### CADENCED

Emit a concise report on the requested cadence, including when unchanged.

Example unchanged report:

```text
A/B/C/D remain coherent with their current plans.
No new dependencies or helper needs detected.
Nothing needs you.
Next useful observation: <reason>.
```

Reporting cadence is an Owner preference, never an execution rule.

## Semantic-boundary escalation

Routine wakeups use:

```text
EXPECTED
OBSERVED
WHAT CHANGED
CONSEQUENCES
DOES THE PRIOR DIRECTION STILL HOLD?
SMALLEST COORDINATOR ACTION
```

Run a fresh full three-pass sequence only when the product/issue meaning, ownership, shared architecture or core problem definition changed materially.
