# UWI v1.2 integration contract (early-stage, read-only)

The new skills are independently runnable and do not replace existing lifecycle policy. Draft PR #364 is the proposed monitor producer; it is NOT merged as of this foundation. No action here deploys or enables it.

## Durable semantic observations

The monitor's snapshot uses schema workflow-progress-monitor/v1 and reports SUBMITTED/UNVERIFIED when trusted-comment markers are seen. The state adapter is local, offline and read-only:

    python3 skills/workflow-intelligence/scripts/state.py \
      --current monitor-snapshot.json \
      --state-output next-state.json \
      --events-output diagnostic-events.json

Once a valid prior state is available, include:

    --previous-state previous-state.json

Omitting prior state creates a silent first-run baseline. Explicitly supplying a nonexistent, malformed, or incompatible prior state is an error; do NOT silently rebaseline. Save next-state.json durably only after a successful run. The state file is a content-addressed semantic cache, NOT a provenance authority or a global Relay/assignment ledger.

Keys are JSON tuples: repository, workflow ID, issue number and stage ID. Polling timestamps are excluded from event identity; evidence changes create deterministic event IDs. Old restored state can re-emit the same ID; consumer deduplication is necessary. Delivery is NOT exactly-once. Each event is diagnostic with alert_eligible=false and mcda_eligible=false.

## Review-gated MCDA

The standalone Software MCDA engine remains usable without this adapter. An optional typed decision request for a named repository/workflow/issue/decision/candidate supports self-declared approval and evidence references:

    python3 skills/workflow-intelligence/scripts/decision_gate.py \
      --request decision-request.json \
      --output assessment.json

- If disabled, malformed or lacking exact source and configuration digest bindings, result is NOT_EVALUATED.
- If every required option/criterion has a declared OBSERVED source URL and matching exact SHA, the engine may compute weighted scores, but result is still ADVISORY_REVIEW_REQUIRED.
- A JSON string claiming an approval or source is not proof that the Owner approved it or that test evidence is genuine. A trusted GitHub/CI verifier is NOT connected. As such every response includes notification_eligible=false; it cannot automatically change an implementation decision, grant progress or send an alert.
- Missing/stale score data must never be silently inferred from observed GitHub issue comments or prior ratings.
- The example skill's ASSUMED refactor/rewrite scores are explanatory only.

## Operational integration not enabled

- No second 15-minute cron or monitor fork.
- No SMTP sender invocation, notification task or credentials.
- No GitHub writes in the core engine or adapters.
- Persisted state via workflow artifacts can be attempted after the source contract in PR #364 is reviewed, but artifact retention/restoration is not transactional and must be tested before alert delivery.
- Downstream installation, Owner merge/release authority and roadmap approvals are separate concerns.

## Validation / limitations

Tests cover replay silence, semantic transition identity, malformed/restored state, namespace isolation, malformed evidence and conservative notification gating. Run:

    python3 -m unittest discover -s skills/workflow-intelligence/tests -v

Output fields represent local assertions only. Only exact-head GitHub CI can establish passing candidate validation; local source inspection does not.
