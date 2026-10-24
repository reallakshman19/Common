# Agent-work artifact handoffs (separate from V3.1 execution ledger)

This path is reserved for **Oracle↔agent artifact handoffs** selected by the Owner on 2026-10-24. Follow [the agent-work policy](../../skills/agent-work/ARTIFACT_RELAY.md) before creating any transfer.

Do not use this folder to edit, impersonate or bypass `relay/STATE.yaml`, `relay/EVENTS.jsonl`, `relay/TRANSACTIONS/` or other active V3.1 execution state. No handoff, receipt or agent assignment is created merely by the existence of this README.

For each authorized transaction use:

```text
relay/AGENT_WORK/<project-key>/<handoff-id>/
  receipt.md             # public-safe metadata, status and native receipt link
  payload/               # only if actual bytes are authorized for public Common
```

For protected/private artifacts the bytes **must remain in authorized private storage**; this public folder contains only a sanitized reference. Temporary `/mnt/data` and `sandbox:` links are not cross-chat custody or proof of transfer. Publishing a draft PR is preparation; recipients verify actual access and bytes independently. A relay receipt is not a technical PASS or Owner acceptance.
