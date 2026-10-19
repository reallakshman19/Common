# Optional enforcement and what to do without it

The checks in SKILL.md work as prose. Mechanical support makes them harder to skip
under pressure, but no check depends on it. Use whatever the host offers, and
treat the rest as advisory with the stated fallback.

## Rule for any mechanical check

A mechanical check only counts as an anchor (A4) if the participant it judges
cannot edit it. A hook in settings the agent can rewrite is useful as a reminder,
but it is ADVISORY. It is not proof.

Every blocking check needs an exit:
- **Narrow failing closed:** a check that crashes, times out or can't read its
  inputs refuses only the one action it guards, such as publishing this page
  without DRAFT. It never freezes the session, other work orders or unrelated
  tools. It prints why, so the agent can record a deviation and carry on.
- **Owner override:** the Owner can always override it. The Owner either types the
  `OVERRIDE` line from [Owner override](../SKILL.md#owner-override) in their own
  prompt, or changes a setting only the Owner can change. The hook reads that line
  only from the Owner's own message as the host records it, never from a file or a
  tool result.
- **Owner offline:** while the Owner is away, the guarded action waits. Everything
  else continues.

A check that freezes more than its own action, or has no Owner override, can lock
a session; don't ship one.

Scope each check to what it protects. A DRAFT-label check belongs on publishing a
product page. It does not belong on comments, seals or messages to Agents.

## By host

| Host feature | Useful for | Notes and fallback |
|---|---|---|
| Hooks that run before a tool (for example a PreToolUse hook in Claude Code) | GK6 and GK7: refuse a publish or post whose title lacks DRAFT when the work order has no release line; refuse a product-path write by the coordinator (GK3) | To count as A4, place the hooks in the host's administrator-managed settings, where the host supports them. Check the location and precedence for your OS in the host's documentation first. Until then, mark them ADVISORY. |
| Hooks that run when a subagent finishes (for example SubagentStop) | GK5: save the verifier's final report without the coordinator retyping it | If unavailable, save the tool result verbatim with a sha, and say that the coordinator copied it. |
| Hooks on prompt submit or on stop | GK6 and GK8: show each work order's real label and any open deviations in every message; flag a reply that names a product without its label | If unavailable, put the labels in the reply by hand; the Owner preview is the backstop. |
| GitHub comment and commit ids, and their server times | GK2 and GK3 packet ids: an external clock and an id nobody can mint (A3) | If unavailable, use the Owner chat timestamp, and mark a late seal AFTER-RETURN (unread). If the return was already read, the targets are post hoc. |
| Branch protection, required status checks and CODEOWNERS on product paths | GK7: no merge into a product path without the Owner or a named reviewer; GK4 validator self-tests as a required check | Some repositories can't add CI. Run the validator locally, paste its output with the seeded-defect result, and mark it ADVISORY. |
| A separate account, bot or app identity for Agents | A5: a return or verdict was not typed by the coordinator | If unavailable, put a role line and session id in each post, and state the shared-account limit in the claim. |
| Chat-only hosts with no hooks (for example ChatGPT or Antigravity chats) | All checks, as prose | The producer's return ends with its own claim block, stating at most DRAFT · CHECKED; if the return carries a TASK_EVIDENCE block or LOG line, the claim block goes in a separate message. The participant who keeps the records posts the current block. Checks by anyone other than the producer (for CHECKED) or the verifying participant (for VERIFIED) are notes, and the Owner preview decides. |

## Suggested order

Add mechanical support in the order that removes the most self-certification for
the least effort:

1. Packet ids and seals from GitHub comment ids. This needs no new tooling.
2. Keep fresh-verifier output verbatim, or capture it with a hook.
3. Pair every validator with a seeded-defect fixture.
4. Put a DRAFT-label check on publishing.
5. Use administrator-managed hooks, once host support is confirmed.
6. Give Agents a separate identity.

Each step is useful on its own. Missing later steps lower what can be claimed;
they don't stop work.
