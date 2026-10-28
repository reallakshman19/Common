# Opt-in UWI diagnostic sidecar for existing Universal Workflow Progress

The existing read-only monitor workflow at .github/workflows/universal-workflow-progress.yml retains the single schedule (7,22,37,52 * * * *). This integration adds a new job, uwi-handoff, with a dependency on the original observe job. It does not create a second timer or replace the monitor.

## Default: disabled

The additional job is skipped until repository variable UWI_DIAGNOSTIC_HANDOFF_ENABLED is explicitly set to the literal value true. The sample workflow configuration also remains disabled. There is no MCDA live rating evidence or new notification sender. The sidecar can neither send an email nor create a ChatGPT Work notification.

The original observe job continues to execute and preserve its previous behavior; a failing UWI sidecar cannot directly block its own prior observation or sender. A sidecar failure is visible in the overall workflow status.

## First baseline: explicit manual dispatch only

Once Owner-authorized, set UWI_DIAGNOSTIC_HANDOFF_ENABLED=true. Manually dispatch the EXISTING workflow on main with input uwi_bootstrap=true. This is a deliberate one-time baseline; it generates no diagnostic events.

For subsequent scheduled checks, the sidecar reads the upstream universal-workflow-progress-state artifact from that same run, then searches for a recent prior uwi-diagnostic-handoff-state. It selects an artifact only if the candidate's workflow run was COMPLETED/SUCCESS, from the same GitHub workflow ID, repository, main branch and scheduled/manual event, and was created before the current run. The selector is bounded to 5 pages and an artifact no older than 72 hours. The run ID is used with gh run download and a fixed artifact name. Corrupt/missing/expired previous state fails closed and never silently re-baselines.

This is a diagnostic cache, not an authority ledger. Stage observations are still SUBMITTED/UNVERIFIED, and all emitted UWI event records have alert_eligible=false and mcda_eligible=false. SMTP, Work triggers, and Owner approvals are unaffected. Token scopes remain contents:read and actions:read. GitHub schedule timing and artifact retention are best-effort; this is not a transactional or exactly-once notification system.

## Rollback

Unset UWI_DIAGNOSTIC_HANDOFF_ENABLED or set it to false. Only the extra job is skipped; the monitor still operates. Never delete or rewrite old evidence to conceal history. After a long outage, a new deliberate manual bootstrap must be authorized.

## Validation boundary

Unit tests inject GitHub API metadata, verify exact workflow/run/branch/commit selection, and reject failed, skipped, stale, wrong-repo, wrong-branch, future, malformed and expired artifacts. CI validates Python syntax and the disabled sample. A live manual bootstrap followed by a real scheduled restoration is NOT_RUN and is intentionally not authorized by code merge alone.
