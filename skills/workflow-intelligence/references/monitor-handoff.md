# Reuse the PR #364 monitor through a UWI diagnostic handoff

## Observed upstream contract

Draft PR #364 (https://github.com/reallakshman19/Common/pull/364) proposes one scheduled, read-only monitor. Its check.py emits .state/latest.json with schema workflow-progress-monitor/v1. Issue-comment stage markers remain SUBMITTED/UNVERIFIED or UNKNOWN. The existing schedule is 7,22,37,52 * * * *.

This module **does not modify PR #364**, create a second timer, activate any disabled workflow configuration, or send SMTP messages. The handoff below is implemented and offline-tested but not yet wired into the scheduled YAML; PR #364 remains a separately owned draft.

## CLI: exact handoff after the monitor creates .state/latest.json

Intentional first baseline:

    python3 skills/workflow-intelligence/scripts/monitor_handoff.py \
      --monitor-current .state/latest.json \
      --bootstrap \
      --output-artifact .state/uwi-handoff.json

All subsequent checks with a restored and independently selected last successful handoff artifact:

    python3 skills/workflow-intelligence/scripts/monitor_handoff.py \
      --monitor-current .state/latest.json \
      --previous-artifact .state/previous-uwi-handoff.json \
      --output-artifact .state/uwi-handoff.json

The single atomically written output contains a semantic state, digest, source semantic digest, and diagnostic events. The initial baseline is silent. Unchanged semantic observations are silent even when the poll timestamp differs. Missing/corrupt prior state fails closed. The state is a derived cache, not a source of engineering authority or a new Relay ledger.

The output may be uploaded by GitHub Actions **after** a trusted prior successful-run restore design is reviewed. GitHub artifact restore itself must be proven not to cross monitored workflow identities or mistake a stale/failed run for a correct predecessor. Choosing the newest artifact by timestamp alone is not a custody or source guarantee. A stale old artifact can regenerate the same stable event ID; exactly-once alert delivery is not claimed.

An optional --assessment file from decision_gate.py can preserve an advisory decision in the same bundle. This cannot promote comment observations to verified evidence. All event records have alert_eligible=false and mcda_eligible=false.

## Proposed integration seam — intentionally not installed

In PR #364's existing observe job, append a bounded handoff invocation after the Observe GitHub read-only step, before uploading state. Reuse the existing scheduler and do not create another workflow timer. Keep the handoff in a **separate artifact name** such as uwi-diagnostic-handoff-state rather than overwriting universal-workflow-progress-state.

Before enabling a real GitHub schedule, review: live exact-head integration PRs, configured trusted source mappings, first baseline procedure, prior-artifact provider provenance, successful-run-only restore, fork PR secret isolation, end-to-end negative tests, and the disabled-by-default behavior.

Do not invoke the existing send_email.py with these diagnostics. The handoff is NOT an alert source and does NOT authorize ChatGPT Work events. Activation requires independently qualified rating evidence and Owner notification policy.

## Rollback

Omit the optional handoff step and artifact. Existing PR #364 progress collection, persistence and sender must be unchanged. Never rewrite historical evidence to conceal rollback.
