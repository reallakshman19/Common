# GitHub comment-block relay · optional local-agent handover

**Goal:** The Owner gives the next local agent a task **issue URL**, not a pasted conversation. Authorized agents read and post handover blocks directly in GitHub issue comments, while checking real source and artifacts separately. A comment is a relay, not technical proof, Owner acceptance, dispatch, or release.

## Comment → agent → comment

1. Use the **existing task issue** of the owning repository. If the project legitimately uses a PR conversation instead, use its top-level conversation comments. Never invent a new task or delete prior returns to tidy history.
2. The outgoing agent fills [the handover block](forms/COMMENT_BLOCK.md), posts it as a new issue comment, and **GETs its returned ID to read back the actual body**. The source of truth is the posted comment permalink, not the local draft.
3. The Owner supplies **only the task issue URL or latest comment permalink** to a new local agent. With permitted GitHub CLI/connector access, the agent reads that comment and independently reopens the original Owner request, candidate, source, fixtures and prior evidence. Without access, state `BLOCKED_GITHUB_ACCESS` and ask for a permitted route; don't pretend comments synchronize automatically.
4. The new agent returns another comment on the same issue, `Kind: INCOMING_RESULT`, with exact tested candidate, actual commands/exits/output, original criteria still open, before/introduced failures and next action. It reads back its own comment. It must not repeat the predecessor's PASS as its own.
5. Corrections or later candidates use a **new** comment with `Supersedes` pointing at the prior permalink and a new `Transfer-ID`. Don't rewrite historical verdicts. Select the latest **applicable** comment using task ID, candidate identity and supersession; chronological latest may be unrelated.
6. Keep original native task comments, SELF-CHECK, terminal LOG and Owner-only decisions in the locations required by the selected project. This relay doesn't replace them or add a mandatory role/review stage.

**Fetch by direct ID:** `gh api repos/OWNER/REPO/issues/comments/COMMENT_ID --jq .body`. A top-level comment URL looks like `https://github.com/OWNER/REPO/issues/ISSUE#issuecomment-COMMENT_ID`; for PR *conversation* comments the issue-comment endpoint also applies (not for inline diff comments).

**Post without copy/paste:** Fill a UTF-8 `handoff-comment.md` and execute `gh api -X POST repos/OWNER/REPO/issues/ISSUE/comments -F body=@handoff-comment.md`, then fetch and compare the posted body. Use a connected app/UI when CLI isn't available. Do not claim a posting or exact readback that didn't happen. Only include appropriate public information; never export private chats, customer data, passwords or restricted fixtures.

The block's `<!-- LOCAL-HANDOVER:BEGIN v1 -->` / `<!-- LOCAL-HANDOVER:END -->` marker pair is searchable in raw Markdown. Text between the invisible delimiters stays **visible** in rendered GitHub. Do not wrap the entire comment in a Markdown code fence.

## ZIP / single file → one *dedicated DRAFT PR*

For a ZIP or other handover file, the local agent must use an **artifact-only draft PR** containing **exactly one changed file path**, when repository permission, storage policy and content confidentiality allow it. This PR is separate from the implementation PR. The Owner has selected the **public** Common [project-wise artifact namespace](../../../local-agent-handoffs/README.md) as the default shared transfer repository; only files that are independently checked as safe for public exposure may be placed there.

1. Default to the Owner-selected `reallakshman19/Common` artifact repository, `main` base, and `local-agent-handoffs/<project-slug>/` namespace. Check that the project folder exists (e.g. [AA3](../../../local-agent-handoffs/AA3/README.md)) and confirm its identity. **Common is public and draft PRs are public**: inspect contents for secrets, private chat, protected fixtures, personal/customer information, rights and binary-size limits; confirm permission to create a branch and PR. If another repository/private route is required, obtain actual authority. If unsuitable, mark `Artifact-PR: NOT_CREATED(reason)`; ask for a permitted location and continue other work. No public leak to satisfy the protocol.
2. Hash the **actual local file** (SHA-256, bytes), inspect ZIP entries/CRC and package needed manifests/logs **inside** the one ZIP. For truthful original source claims, hash originals against independent authority, not just the producer's manifest.
3. Create a **fresh branch from Common/main** (ideally a separate worktree); add **only** `local-agent-handoffs/<project-slug>/issue-<number>/<candidate-id>.zip` (or `task-<stable-id>` for non-issue work). Add a project README to Common/main as a separate documentation commit if absent; **do not** add it to the one-ZIP PR. Before committing, `git diff --cached --name-only` must show exactly one path. Do not include README, manifest or evidence sidecars as separate PR paths.
4. Push; open via `gh pr create --draft` (or authorized equivalent). Independently verify `gh pr view NUMBER --json isDraft,headRefOid,baseRefOid,url` and **server** `gh pr diff NUMBER --name-only` shows **one path, identical to the ZIP path**. One-file claims in the producer's own report are not sufficient.
5. Verify the binary is retrievable and re-hash the fetched bytes if possible. If remote-byte retrieval is unavailable, record `NOT_RUN` for that check, not PASS. Cite exact artifact PR **head commit**, relative path, byte length and real SHA-256 in the issue handover block. New bytes/head require a new comment/digest; retain old evidence.
6. Leave the artifact PR **OPEN/DRAFT**. A draft PR URL is not guaranteed permanent if its branch/ref is deleted. Never promise perpetual file access. The Owner controls retention and any eventual merge. Don't merge/deploy or modify an implementation PR. Draft PR existence confirms a transfer surface, not a product pass or acceptance. The Owner controls release, merge and cleanup.

Follow [the one-file PR checklist](forms/ARTIFACT_PR_CHECKLIST.md). A ZIP that contains a software patch still needs **forward** `git apply --check` against the exact clean base before adoption. Artifact-only one-file diff does not conceal internal software changes from normal review.

## Fail-closed status

- Missing GitHub access, privacy permission, unsupported binary size or no safe repo: `NOT_RUN/BLOCKED` with the specific reason; do not invent a link.
- Artifact PR includes extra files or is not draft: `NOT_READY`, correct then inspect server again.
- Mismatched file hash, moving PR head or comment not read back: `STALE/UNVERIFIED`, reverify and issue a new indexed comment.
- Product test fails while archive transfer passes: preserve **FAIL** for product and **PASS** only for transfer.
- Same work continues with one agent: use the channel when useful; the protocol itself never requires handover.

This optional transport is compatible with [Common agent-work START_HERE](../START_HERE.md) and the source-bound self-check practices. It creates no bot, scheduler, role quota, credential, auto-merge or owner-approval shortcut.
