# Universal Workflow Progress — 15-minute Bridge (prototype v1.1)

## Contents

- `SKILL.md` — original ChatGPT read-only progress-view skill
- `.github/workflows/universal-workflow-progress.yml` — 15-minute GitHub Actions timer
- `skills/universal-workflow-progress/config/workflows.json` — explicit source/stage/evidence mapping (disabled sample)
- `skills/universal-workflow-progress/scripts/check.py` — reads GitHub issue comments, compares with last run; never claims VERIFIED
- `skills/universal-workflow-progress/scripts/send_email.py` — sends an email only on a meaningful observation change
- `skills/universal-workflow-progress/tests/test_check.py` — offline acceptance tests
- `WORK_TRIGGER.md` — Work/Gmail event-trigger instructions

## How to deploy

1. This draft PR places the monitor under `skills/universal-workflow-progress/` and its GitHub Actions timer at `.github/workflows/universal-workflow-progress.yml`; review it before merging. Nothing is installed or deployed by downloading this package.
2. Customize the workflow list: set the exact owning issue, evidence markers and nonempty trusted-author allowlists. Set `enabled: true` only after checking the real contract and matching evidence records. The supplied stage IDs/markers are **illustrative and intentionally disabled**, not actual BuddyRunner proof rules.
3. Configure GitHub Actions secrets: optional `WF_GITHUB_TOKEN` (GitHub App token or fine-grained PAT with read access when monitoring other/private repositories; the built-in token normally covers only the host repository), plus `WF_SMTP_HOST`, `WF_SMTP_PORT` (465 or 587), `WF_SMTP_USER`, `WF_SMTP_PASSWORD`, `WF_ALERT_TO`, `WF_ALERT_FROM` (optional; defaults to SMTP username). For Gmail SMTP, use separately issued eligible SMTP credentials; ChatGPT Gmail connection cannot be reused in GitHub Actions. Never commit credentials. An external mail provider is also supported.
4. Enable Actions and run `workflow_dispatch` once. First run establishes a baseline and should not email. Subsequent runs compare with the prior successful snapshot artifact and email only changes. Inspect the workflow run logs and artifacts. GitHub schedule is best-effort, not a guaranteed exact 15-minute SLA.
5. Use `WORK_TRIGGER.md` to configure a new-mail event-triggered Work task and enable ChatGPT notifications.

## Oracle + MCDA presentation (v1.1)

See the [Oracle / MCDA / progress bridge](references/oracle-mcda-bridge.md):
one compact contract-derived strip, independent lanes and a named blocker/next
observable, followed (only when requested) by separate advisory MCDA.
Neither the bridge nor the pure router installs a ChatGPT feature, launches
an Oracle or activates the existing disabled scheduled monitor.

```sh
python skills/universal-workflow-progress/scripts/route_invocation.py --consumer oracle --intent combined --workflow selected-id --monitor OFF
python skills/universal-workflow-progress/scripts/route_invocation.py --consumer oracle --intent mcda
```

## Invoking in a ChatGPT conversation

**Progress request:** "show/check status" invokes read-only observation; select Monitoring ON only for a verified, one-time live source read, otherwise disclose `NOT LIVE`. **Start request:** "start/kick off" must be routed to the named *governing* execution skill, not the monitor. For BuddyRunner v1.7, that means preparing a real Stage 1a packet and returning its `PROMPT_PREPARED` receipt; this is not G2 dispatch. The [skill's invocation-routing contract](SKILL.md#intent-sensitive-invocation-routing-before-rendering-progress) is accompanied by a pure diagnostic:

```sh
python skills/universal-workflow-progress/scripts/route_invocation.py --intent start --workflow buddy-runner-v1-7
python skills/universal-workflow-progress/scripts/route_invocation.py --intent progress --workflow buddy-runner-v1-7 --monitor ON
```

The diagnostic returns a **routing recommendation, never a source read or agent execution**. A ChatGPT skill mention does not itself install an agent runner; authorized tool/runtime execution must be performed separately. This addition does not change the existing scheduled GitHub observer, email or Work trigger.

## Current behavior and important limits

This is an **observation bridge**. The supplied monitor is disabled; pull request checks test the script but do not run the notifier. It does not magically understand every engineering workflow. The shared ChatGPT skill can interpret a workflow contract during a chat, but unattended automated checks require an explicit adapter/mapping to authoritative evidence. The sample uses comment token observations only: matching text produces **SUBMITTED / UNVERIFIED**, never VERIFIED. It cannot establish whether the author truly performed the task, agent independence, Owner approval, current head or engineering acceptance.

The alert receiver (ChatGPT Work) must independently verify source and protocol before reporting strong conclusions. This package does not start/stop workflows, write comments/branches, claim delivery or alter an already-sent chat message. Because the monitor only watches configured stage markers, it does not yet implement generic contract parsing, dependency analysis, or native DELP projection. For robust production use, add protocol-specific resolvers and contract tests.

Run offline tests: `python -m unittest discover -s skills/universal-workflow-progress/tests -v`.

## Operational caveats

- Workflow state is stored in run artifacts, not committed to GitHub. If artifact retention expires or a first run has no prior state, the monitor initializes silently.
- This prototype monitors issue comments only. PR checks, handover digests, independent execution, and canonical stage discovery require protocol-native resolvers.
- Exact 15-minute scheduling is not guaranteed: GitHub scheduled runs can be delayed or skipped.
- If the email succeeds but artifact upload fails, a later retry may repeat an alert. Delivery is **at least once**, not exactly once.
