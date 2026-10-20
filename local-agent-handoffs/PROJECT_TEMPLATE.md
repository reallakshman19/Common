# Template — create a project-wise local-agent handoff index

Copy this text to `local-agent-handoffs/<PROJECT-SLUG>/README.md` **after checking for an existing directory**. Use the project's real repository name; if the short name collides, use `owner--repo`. This index lives on Common/main; ZIPs live on isolated one-file DRAFT PR branches.

## Project identity

- Owning project: `OWNER/REPO` — https://github.com/OWNER/REPO
- Project slug: `<PROJECT-SLUG>`
- Existing task issue/PR: https://github.com/OWNER/REPO/issues/NUMBER
- Authentic governing instructions and criteria: <source URL and revision, not a pasted predecessor summary>
- Confidentiality: `Common` is PUBLIC. Only safe-to-publish bytes may enter Common draft PRs.

## One-file draft artifact PR path

- Repository: `reallakshman19/Common`
- Base: `main` at actual observed commit SHA
- Branch: `handoff/<PROJECT-SLUG>/issue-<NUMBER>/<candidate-id>`
- Path: `local-agent-handoffs/<PROJECT-SLUG>/issue-<NUMBER>/<candidate-id>.zip`
- Required server verification: PR `OPEN/DRAFT`, exact base/head, exactly **one diff file path**, local SHA-256/bytes, remote-byte rehash or `NOT_RUN`
- Required communication: post/read back [comment block](../skills/agent-work/local-handover/forms/COMMENT_BLOCK.md) on the **original project issue**, not a duplicate Common issue

## Limits

- Archive transfer != product verification or Owner acceptance.
- A local-agent completion claim remains reported until inspected on the exact candidate.
- Original Owner/native project authority overrides convenience. Don't upload protected/private fixtures, secrets or chats publicly.
- The Owner decides artifact PR merge/retention. No auto-merge/cleanup or implementation deployment.
- When a location/tool/permission is unavailable, report the exact `NOT_RUN/BLOCKED` instead of manufacturing a PR or link.

Full [Common project-wise protocol](README.md) and [agent-work handover](../skills/agent-work/local-handover/README.md).
