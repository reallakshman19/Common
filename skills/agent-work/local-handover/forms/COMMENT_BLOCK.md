# GitHub issue handover comment block — fill actual facts

Use the **existing task issue**. Fill this human-readable Markdown, including both exact markers, and post it as **one top-level GitHub issue comment**. The markers are invisible in rendered GitHub; the fields stay readable. Do not wrap the entire comment in a code fence.

<!-- LOCAL-HANDOVER:BEGIN v1 -->
**Local-agent handover v1**

- Task-Issue: https://github.com/OWNER/REPO/issues/NUMBER
- Transfer-ID: TASK-NUMBER/attempt-001
- Kind: OUTGOING | INCOMING_RESULT | CORRECTION
- Source: original Owner request and applicable amendments/policy, direct URLs/revisions
- Candidate: exact base + commit SHA or file hash; UNKNOWN if not accessible
- Claims: EXECUTED_HERE / FACT_OBSERVED / REPORTED_BY_PREDECESSOR / UNKNOWN with clear limits
- Executed: exact commands/runtime/exits and actual log/result links; NOT_RUN when not performed
- Failed-Or-Not-Run: all known failed/skipped/blocked tests, pre-existing vs introduced vs unattributed
- Open-Criteria: every unmet original acceptance ID and specific missing evidence
- Next: actor, authority, smallest task, dependency and expected return location
- Artifact-Repository: NONE | reallakshman19/Common | other explicitly authorized repository
- Artifact-Visibility: NONE | PUBLIC_SAFE_CONFIRMED | BLOCKED_PRIVATE(reason)
- Artifact-PR: NONE | NOT_CREATED(reason) | https://github.com/reallakshman19/Common/pull/NUMBER
- Artifact-Path: NONE | local-agent-handoffs/<project-slug>/issue-<number>/<candidate-id>.zip (one changed PR path)
- Artifact-Head: NONE | 40-character commit SHA
- Artifact-SHA256: NONE | 64-character SHA-256 of actual file bytes
- Artifact-Bytes: NONE | actual positive integer
- Artifact-Diff: NONE | VERIFIED_ONE_FILE(path, draft=true, head=SHA) | NOT_RUN(reason)
- Supersedes: NONE | earlier issuecomment permalink
- Owner-Reserved: acceptance / merge / deploy / restricted publication, actual state
<!-- LOCAL-HANDOVER:END -->

Write a local UTF-8 `handoff-comment.md` and use `gh api -X POST repos/OWNER/REPO/issues/NUMBER/comments -F body=@handoff-comment.md`. Read the returned `html_url` and GET the posted body. The next agent only needs the original issue or this permalink, not a manually copied report.

For `INCOMING_RESULT`, read actual original source and candidate independently; set `Supersedes` to the received comment permalink, post a **new** comment and read it back. Keep the native project SELF-CHECK and LOG separate.

For ZIP, use the Owner-selected public [Common project-wise artifact folder](../../../../local-agent-handoffs/README.md) when safe and fill all artifact fields from the real [dedicated one-file draft PR](ARTIFACT_PR_CHECKLIST.md). If no artifact, all artifact fields are `NONE`. A claim that a PR is draft or has one file requires direct GitHub verification, not only the outgoing agent's text.

**Never post** secrets, confidential files, customer data or private chats on public GitHub. Comments and archive PRs don't grant technical approval, implementation permission or Owner acceptance.
