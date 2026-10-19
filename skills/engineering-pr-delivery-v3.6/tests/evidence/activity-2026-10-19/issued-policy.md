# ChatGPT-agent activity and BuddyRunner suggestion

This policy is mandatory **only for an explicitly identified ChatGPT agent using
standalone mode**. `chatgpt-work`, other hosts and UNKNOWN hosts are exempt. A model
name, browser tab or Oracle title does not identify the environment. Record the
actual supplied/observed surface; never relabel Work to satisfy the policy.
Coordinator mode and its runtime remain unchanged.

## Responsibility and trigger

The **executing ChatGPT agent** records its own activity and evaluates the counters
at each turn end, useful progress checkpoint and before proposing DONE. No separate worker, Oracle, daemon,
CI or background timer is required. A clock does not run after the agent yields.
A selected host adapter can capture events when available; it is not installed by
this skill. The local recorder supports agent-reported observations now.

An available Oracle/lead preserves the episode binding in assignments, checks the
returned activity summary, and keeps a due recommendation visible. It does not
infer a worker's unseen tool calls or active time. An Oracle that is itself an
in-scope ChatGPT agent records its own episode separately. Without Oracle, the
executing agent carries both responsibilities. Do not sum separate agents' turns
or durations into one agent's threshold.

Suggest the project's selected BuddyRunner when either observed lower bound is:

- **GitHub-access turns > 5** (the sixth distinct turn), **OR**
- **active-turn elapsed time > 35 minutes** (strictly more than 2,100 seconds).

Exactly five turns or exactly 35 minutes does not cross the threshold. A turn is
one host/user turn containing at least one GitHub access, not one tool call,
JavaScript cell, model generation or API page. Record retries/failures as accesses;
twelve calls in one turn count as one access turn. A batch is not twelve turns.
Use actual host turn IDs when available. Otherwise identify observed user turns
with stable local IDs and label SELF_RECORDED; if turns cannot be distinguished,
record a gap rather than inventing a count. Hidden connector pagination is unknown.

Active time is the union of observed start/end turn intervals for this agent,
including model/tool processing during those intervals. Close before yielding to
the user; resume on the next actual execution interval. Exclude idle/user-wait
gaps. Do not call wall time since assignment, CPU time or private reasoning time
active-turn duration. Unclosed intervals are shown as gaps and are not extrapolated
across a long idle period. Actual final-response composition after the last
measurement can remain unmeasured; label the recorded duration a lower bound.

Counters persist for the **agent/project episode**, across tasks/nudges. Do not
reset on a new task, checker run or brief. Start another episode only for an actual
recorded takeover/new agent context under the project's selected handover method.
Preserve the old log and link the new episode to its source. The local helper
refuses a second session event in one log; it cannot authenticate a genuine takeover.

## Record observations

Use a per-agent JSONL file with one writer. Commands below run from the skill
folder; replace the sample values with the actual episode and current user turn:

```bash
python scripts/standalone_activity_cli_v36.py start --log activity.jsonl --surface chatgpt-agent --session-id EPISODE_ID
python scripts/standalone_activity_cli_v36.py turn-start --log activity.jsonl --turn-id TURN_ID
python scripts/standalone_activity_cli_v36.py github --log activity.jsonl --turn-id TURN_ID --tool github_fetch --outcome success
python scripts/standalone_activity_cli_v36.py turn-end --log activity.jsonl --turn-id TURN_ID
python scripts/standalone_activity_cli_v36.py summary --log activity.jsonl
```

Record each actually observed GitHub call, with failure/unknown outcome as relevant.
For a long turn, close and restart its interval at a useful progress checkpoint,
using the same turn ID; this lets a crossed time threshold be observed during work.
The recorder does not intercept tools by itself. A host with a real event stream
can supply its timestamped events using the same record shape; HOST_OBSERVED must
name the actual trace source. A manually written label does not authenticate it.
Do not collect credentials, full tool arguments, private chat bodies or tokens.

If measurement started late or host IDs/timing are unavailable, logging the
restriction is mandatory; do not fabricate earlier history:

```bash
python scripts/standalone_activity_cli_v36.py gap --log activity.jsonl --reason "Earlier history or precise host timing unavailable; current observations only"
```

An incomplete record does not show that thresholds were not reached. It reports
UNKNOWN, observed lower bounds and the gap. A lower bound already exceeding a
threshold still requires a suggestion. This condition does not invent a product
defect, invalidate useful work or prohibit an honest task completion report.

## Suggest once; retain authority

When `buddy_suggestion_due` is true, include a concise recommendation in the actual
Owner-facing response, for example:

> This agent episode has six observed GitHub-access turns. I suggest BuddyRunner
> at the next useful boundary to preserve the current intent, evidence and next task.

Then retain the actual response/publication reference:

```bash
python scripts/standalone_activity_cli_v36.py buddy-suggested --log activity.jsonl --reference "Actual response or permitted publication locator"
```

A declared reference is a receipt, not proof that another participant saw it. The
helper remembers only a suggestion recorded **after** a threshold crossing. It
suggests once per episode, retains the counters and never auto-executes BuddyRunner,
forces a handover, stops useful work or creates a permission request. Follow an
existing Owner handover direction when present. Do not choose a protocol version
from an old example or restart predecessor loops.

## Bind to the pre-DONE record

For an in-scope ChatGPT agent, supply these additional options to
`standalone_done_v36.py`:

```text
--agent-surface chatgpt-agent --activity-log /PROJECT/activity.jsonl --activity-session-id EPISODE_ID
```

Include `activity episode EPISODE_ID; activity sha256 FULL_64_HEX` in the native
`Issue reconciliation:` line, and retain the accessible log/summary with the
other evidence. Compute the digest after closing the measured interval and
recording any required suggestion. Appending an event requires refreshing that
binding. No extra line is added to the canonical eight-line task receipt.

The checker requires the activity log/episode and native binding for this surface;
it reports a due but unrecorded suggestion as a declaration gap. Work/other/UNKNOWN
surfaces need no log, and the checker does not read one for them. Unknown observation
coverage is reportable; an attempt/gap record is preferable to invented precision.

## Limits

The policy requires recording and a timely recommendation, not a minimum amount
of work or a quality score. Fewer accesses can reflect effective batching. More
minutes/calls do not establish deeper reasoning. Judge the task by its actual
source, result, negative cases and remaining obligations.

This is an agent-invoked recorder and declaration check. It cannot intercept a
ChatGPT final response, authenticate the declared runtime, reconstruct hidden past
activity, enforce append-only storage against a file editor or prove that every
call was logged. A host-managed tool/turn adapter can strengthen observation when
available; do not claim it exists here. Missing host access must stay visible.
