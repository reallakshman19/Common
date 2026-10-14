---
name: workflow-intelligence
description: Read-only companion for the standalone Software MCDA and Universal Workflow Progress skills. Use to normalize versioned workflow observations, detect semantic changes and prepare an optional future decision analysis without upgrading stage evidence.
---

# Workflow Intelligence — observer adapter (v1.2 foundation)

This is a **foundation only**. It does not deploy a scheduler, an alert sender, an active decision policy, a new Relay ledger or a ChatGPT Work trigger.

The adapter consumes the workflow-progress-monitor/v1 snapshot format proposed in draft PR #364. Stage comment observations remain SUBMITTED/UNVERIFIED or UNKNOWN. An issue-comment match does not prove execution, review, Owner approval or MCDA input quality.

Run from repository root:

    python3 skills/workflow-intelligence/scripts/observe.py --current snapshot.json --output changed-events.json

To compare to a previous persisted snapshot, add:

    --previous previous-snapshot.json

Use this as a boundary contract for a later verified-evidence adapter. Do not convert its event records directly to scoring inputs; MCDA requires separately approved project criteria, score provenance and mandatory-constraint evidence.

- No integration changes to existing monitor/CI while PR #364 remains draft.
- Missing previous state is a silent baseline.
- Changes are based on stable semantic evidence identity, not poll timestamps.
- Fail closed for malformed inputs, duplicate workflow IDs, unsupported states or attempts to upgrade v1 observation verification.
- Neither this skill nor MCDA grants progress, release, writer or Owner authority.

Offline tests: python3 -m unittest discover -s skills/workflow-intelligence/tests -v
