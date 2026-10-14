---
name: workflow-intelligence
description: Read-only companion for Software MCDA and Universal Workflow Progress, used to normalize workflow observations, persist semantic state, and run advisory-only decision scoring with explicit evidence references. Does not authorize workflow stage changes or notifications.
---

# Workflow Intelligence — read-only foundation

This optional coordinator is independent of the Software MCDA engine, the GitHub monitor, and ChatGPT Work. It is not an execution controller.

1. Obtain a real monitor snapshot from the approved provider, or use an explicitly labeled offline fixture. Draft monitor PR #364 produces workflow-progress-monitor/v1 comment observations; these can be SUBMITTED/UNVERIFIED or UNKNOWN only.
2. Run scripts/observe.py to compare current and previous monitor snapshots, or scripts/state.py for namespace-scoped, durable, semantic observations. Preserve its returned next state for the subsequent poll. Initial baseline is silent; corrupt prior state fails closed.
3. For a project-approved MCDA decision request, run scripts/decision_gate.py. It requires exact candidate and declared evidence bindings. It cannot authenticate GitHub itself, so results are ADVISORY_REVIEW_REQUIRED or NOT_EVALUATED, never a verified live architecture decision.
4. Use the independent Software MCDA skill to examine weights, rubric, hard constraints and sensitivity; never treat a monitoring event as a substitute for measurable score evidence.
5. Report sources, candidate SHA, unknowns, unchanged/changed semantics and review obligations. Do not advance a workflow, launch agents, write GitHub comments, merge PRs, send email, or activate a Work trigger.

## Core interfaces

- scripts/observe.py: stateless monitor-snapshot normalization and comparison.
- scripts/state.py: versioned durable state, idempotent diagnostic event identities, silent first poll.
- scripts/decision_gate.py: explicitly bound **advisory** MCDA computation; no automatic alert eligibility.
- schemas/: documentation of versioned boundaries; Python provides strict cross-field validation.
- config/decisions.example.disabled.json: intentionally disabled sample.
- references/integration-contract.md: CLI examples, trust limits, state restoration and future integration.
- tests/: offline falsifiers and regression cases.

## Safe mode and governance

The observer contains **no scheduler or SMTP integration**. A later integration must reuse the single monitor/cron proposed by draft PR #364, not create another timer or controller. Comment markers, even from configured trusted authors, never establish independent verification or Owner approval. Unverified observations are never allowed to become MCDA decision triggers. Preserve repository AGENTS.md, BuddyRunner stage roles, selected governing policy and explicit Owner merge rights.

Run tests: python3 -m unittest discover -s skills/workflow-intelligence/tests -v.


## Compare an advisory decision with its prior state

Run decision_gate.py with a typed decision request to create an assessment artifact. Pass that artifact to state.py with --assessment; the logical decision ID is isolated per repository/workflow/issue, and a changed recommendation becomes a diagnostic decision event. Every event remains NOT alert-eligible. The exact CLI sequence and event schemas are in references/integration-contract.md.


## Verify GitHub CI source facts (optional, read-only)

When a project explicitly supplies the expected GitHub check-run IDs, exact names, trusted GitHub App IDs and assessed commit SHA, use `scripts/github_check_facts.py` to query only GitHub's exact check-run REST resources. See `references/github-ci-evidence.md`. Successful provider results attest to the configured CI check facts, **not** MCDA scores, workflow acceptance, or Owner approval.

An enabled `scripts/decision_gate.py` request can take `--github-check-request <path>`; mismatched repository/SHA is refused before provider fetch, and missing/failed CI facts produce `NOT_EVALUATED`. Even fully matched checks leave the evaluation `ADVISORY_REVIEW_REQUIRED` and notifications disabled, pending independent approval and rubric-to-rating verification. Never claim the sample rating evidence is verified.


## Portable monitor snapshot handoff

The optional scripts/monitor_handoff.py consumes PR #364's proposed workflow-progress-monitor/v1 snapshot directly and emits **one** reusable diagnostic-only state artifact. The first run requires explicit --bootstrap; every later run requires --previous-artifact. Missing, corrupted or incompatible prior state fails closed, not a silent reset. It can optionally carry an advisory decision assessment in the same state. All output events are non-notifying and unqualified for MCDA scoring.

Read references/monitor-handoff.md for exact commands and the future bounded connection to PR #364's *existing single scheduler*. The handoff does not modify PR #364, send mail, or create a new cron workflow. Run all read-only skill tests before changing the monitor integration seam.


## Optional same-workflow diagnostic sidecar

The existing Universal Workflow Progress GitHub Actions workflow now supports an **opt-in diagnostic job** via repository variable UWI_DIAGNOSTIC_HANDOFF_ENABLED=true. It retains the only 15-minute scheduler; PR events remain tests-only. The job requires an explicit one-time manual baseline using workflow_dispatch input uwi_bootstrap=true, then restores a vetted prior successful artifact from the same workflow ID, repository, and branch. With the variable absent or false, the diagnostic job is skipped. This does not activate live workflow monitoring, MCDA rating authority, notifications, or ChatGPT Work. See references/scheduled-handoff-activation.md.
