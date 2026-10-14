# Per-invocation monitoring toggle (not a permanent app UI setting)

When a user calls Software MCDA or Workflow Intelligence, offer **Monitoring OFF (default) / ON (one-time read-only)**. If explicitly ON/OFF already requested, honor it without questioning again. For an unspecified ordinary engineering MCDA request, proceed OFF and let the user opt into ON next time. A ChatGPT skill is an instruction package, not a native always-present switch; render two choices or ask briefly where interactive controls are unavailable.

| Mode | Behavior | Preconditions | Persistence |
| --- | --- | --- | --- |
| OFF (default) | MCDA can run from supplied decision input; zero live GitHub observation requests | None | This call only |
| ON | Fetch the configured selected issue's comments once; return SUBMITTED/UNVERIFIED or UNKNOWN observations with refs | Exact selected workflow ID and separately reviewed enabled mapping, trusted authors, real GitHub issue/repo | This call only |

The user's toggle **never** modifies workflows.json, does not set UWI_DIAGNOSTIC_HANDOFF_ENABLED, cannot add an extra cron, does not dispatch GitHub Actions, and does not send SMTP/Gmail/Work notifications. It is independent of the existing scheduled observer. The scheduled observer remains controlled separately by repository config/variables and its first-run bootstrap.

## CLI from repository root

OFF, with standalone MCDA:

    python3 skills/workflow-intelligence/scripts/invoke.py \
      --monitor off \
      --decision skills/software-mcda/assets/example-decision.json

ON for a separately reviewed project mapping:

    python3 skills/workflow-intelligence/scripts/invoke.py \
      --monitor on \
      --workflow-config /path/to/reviewed-workflows.json \
      --workflow-id actual-workflow-id \
      --decision /path/to/approved-decision.json

Omitting --monitor is OFF. Providing an unreadable workflow config in OFF mode must have **no** effect and must not even open that config file. ON fails closed if config is missing, selected workflow disabled, issue/repository a placeholder, author allowlist absent, or source response malformed. It performs a single bounded GitHub issue-comment read using the existing read-only monitor logic and its configured stage markers. It does not use comments as MCDA scores.

ON can be used without --decision to return only the monitored workflow snapshot. OFF without --decision returns a no-op scope/status report, not a claim that a live workflow was monitored.

## Interaction examples

User: "Use Software MCDA to compare rewrite vs refactor."
Skill: Evaluate the user-supplied decision with monitoring OFF by default, and offer the ON option for one-time evidence inspection if useful.

User: "Use the MCDA skill with workflow monitoring ON for workflow X."
Skill: Check that X has a reviewed, enabled source mapping. If it does, perform one read-only check, render evidence states separately from MCDA scores. If it does not, report "MONITORING UNAVAILABLE — CONFIGURATION REQUIRED" and continue an independent MCDA evaluation if possible.

User: "Turn on monitoring forever."
Skill: Do not reinterpret this per-call toggle as a persistent activation. Explain that scheduled monitoring requires separate approved repository configuration, workflow ownership, explicit enablement and applicable credential/trigger setup.

## Security and authority

Stage markers remain SUBMITTED/UNVERIFIED until the controlling protocol's distinct verification conditions are met. A successful GitHub read does not verify technical correctness, grant Owner authorization, or approve an MCDA rating. MCDA stays advisory. Output JSON response schema: schemas/invocation.v1.schema.json. Tests use injected fake provider records and ensure OFF performs no read even when an invalid config file is supplied.
