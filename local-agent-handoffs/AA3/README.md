# AA3 — local-agent handoff artifact index

**Owning project:** [reallakshman19/AA3](https://github.com/reallakshman19/AA3)  
**Common shared artifact namespace:** `local-agent-handoffs/AA3/`  
**Original task / engineering authority:** [AA3 issue #56](https://github.com/reallakshman19/AA3/issues/56)

This is an **index on Common/main**. It is not AA3 production code, an issue completion report, a test receipt or acceptance. AA3's protected original fixture, engineering solver, task criteria and native evidence stay under their actual source and authorizations.

## Transfer an AA3 #56 candidate

The local agent builds a non-sensitive ZIP using the [local handover protocol](../../skills/agent-work/local-handover/README.md) and reviews its contents before exposing them to the **public** Common repository.

- **Artifact repository / PR base:** `reallakshman19/Common` / `main`
- **One new ZIP path per attempt:** `local-agent-handoffs/AA3/issue-56/<candidate-id>.zip`
- **Branch example:** `handoff/AA3/issue-56/<candidate-id>`
- **PR:** dedicated `DRAFT` PR targeting `Common/main` with **exactly this one ZIP path changed**
- **GitHub conversation:** post an [OUTGOING or INCOMING_RESULT comment block](../../skills/agent-work/local-handover/forms/COMMENT_BLOCK.md) on [AA3 #56](https://github.com/reallakshman19/AA3/issues/56); include draft PR URL, head SHA, local file SHA-256/bytes, verified diff and NOT_RUN checks
- **Receiving agent:** independently inspect ZIP, exact clean base, authentic available inputs, baseline failures and real Run/Output/CSV before updating acceptance statuses

Do not include `BM4_L.ACCDB` or any original/protected content in the public ZIP merely to simplify transfer. If the Owner explicitly permits a specific public fixture, retain that authority link and still exclude unrelated restricted material. Use its **source repository locator + independently verified hash** when the recipient has access. Never infer that a path or displayed hash proves original bytes were actually examined.

The previous AA3 #56 work and reported defects remain tracked on [issue #56](https://github.com/reallakshman19/AA3/issues/56). The Owner's AC1–AC12 and project A13/A14 remain authoritative; no old handoff, mock test, or draft artifact PR supersedes them. This index is intentionally **not** a manually maintained list of completed artifacts; the authoritative transfer sequence is the issue comment permalinks.

**No AA3 candidate ZIP is committed in this folder on `main` by this index update.** Future ZIPs appear only on their dedicated draft-PR branches until the Owner separately decides disposition. No AA3 implementation PR, solver, fixtures or workflows change from creating this index.
