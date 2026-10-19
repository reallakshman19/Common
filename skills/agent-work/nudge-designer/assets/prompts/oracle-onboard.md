# Oracle OnBoard Prompt template

Owner can use two lines:

> Prepare an Oracle OnBoard Prompt for [next task], using [original sources/current context].
> Preserve the whole outcome and give the receiver a usable direction, room to correct it from evidence, and an evidence-based next action.

Use the [guide](../../references/ORACLE_ONBOARD.md). Fill the load-bearing fields;
link detail, remove unused alternatives, and preserve the native assignment/tracker
identity and return format. No schema, extra role or operating mode is required.

```text
Oracle OnBoard Prompt — {{native task/assignment identity}}
You are continuing from the supplied context. Check the essential originals and
current candidate needed for this task, then execute within the existing authority.
Treat the explanation below as revisable. No questionnaire, scored admission or
separate reconstruction report is requested. A completed BuddyRunner/two-pass/
three-pass is reused directly; do not repeat it or add a reconstruction stage.

Purpose
Owner outcome and relevant amendments: {{original words + direct references}}
Why this task matters: {{connection to outcome; what remains after this task}}

One bounded task
Deliverable: {{one checkable result}}
Working explanation: {{FACT/CLAIM/HYPOTHESIS + evidence + plausible alternative}}
Method: {{concrete GUIDED operations, or OPEN investigation with decision contrast}}

Authoritative inputs
{{original sources; exact candidate/base or artifact; locators/access route;
revisions/digests where consequential; relevant completed-flow outputs or none}}
Earlier reported results and their scope: {{historical basis; not execution now}}

Boundaries
Allowed actions/writes: {{existing scope and actual authorization}}
Preserve/reserve: {{invariants, coupled decisions, acceptance/release authority}}

Success criteria
{{observable result; meaningful contrary case; statuses/roll-up and UNKNOWN}}

Uncertainty handling
Known access/tools: {{observed availability or UNKNOWN; report actual errors}}
If evidence contradicts the explanation, cite the witness and revise the affected
diagnosis/method within scope. Do not execute a repair based on a falsified premise.
Resolve discoverable facts; return consequential missing intent/authority. Scope a
restriction to its dependent work and continue unaffected authorized actions.

Evidence and continuation
Return via {{native format/channel/binding; exact ACK only if used by that system}}.
Include actual action/result and witnesses or NOT_RUN; what changed in understanding;
task status; remaining parent outcome; next justified action and its authority.
For a blocked action include attempt, restriction, affected scope and feasible route.
After this result: {{conditional next action within standing authority, or proposed
action for the appropriate actor; no implied expansion of scope}}
COMPLETE refers to this task. Product validation, independent review where actually
required, Owner acceptance and release remain separate.
```
