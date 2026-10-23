# PROTOTYPE RETURN (short builder return)

Used while a step is a prototype. Full native TASK EVIDENCE and SELF-CHECK are
required from the hardening state on.

```text
PROTOTYPE RETURN · {{project}} · {{slice}} (WBS {{wbs}}) · {{builder id}} · {{date time zone}}
Status: RUNNABLE | PARTIAL | BLOCKED
User can now: {{one line in the user's words, as the builder sees it}}
Run: {{one command or URL}} · pack: {{file name}} · sha256 {{first 12}} · where: {{private folder or "download in chat"}}
Demo I performed: {{the demo steps and what each showed}}
Tests: {{command}} -> {{passed / total}}; keeps: {{each earlier benchmark: PASS / FAIL / NOT_RUN}}
Inputs used: {{name · sha256 first 12 · real or synthetic}}
Gaps and risks: {{what does not work yet; what the user should look at first}}
Owner steering followed: {{corrections the user gave in chat, one line each}}
Private data: none published | {{what stayed private and where}}
METER: {{context use, or UNKNOWN}}
```
