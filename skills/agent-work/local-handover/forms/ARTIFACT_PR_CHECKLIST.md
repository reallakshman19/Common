# ZIP / single artifact: dedicated one-file DRAFT PR

**Default transfer destination, selected by the Owner:** public `reallakshman19/Common`, under [project-wise local-agent-handoffs](../../../../local-agent-handoffs/README.md). Only apply this route when the exact file is safe for a **public** repository and the agent has authority to open draft PRs. No permission or privacy grant follows from this document.

## Prepare
- [ ] Identify the original owning-project task issue, project slug/index, `reallakshman19/Common` as default artifact repo and **actual Common/main base SHA**. Confirm **public** visibility, secrets, protected fixtures, customer information, binary-size policy and rights to publish; a draft PR is public.
- [ ] Read the **actual local ZIP/file bytes**; record SHA-256 and byte size, and archive integrity/entry list for ZIP. Manifest correctness alone is not engineering authenticity.
- [ ] Include any README, patch, manifest, logs and test artifacts **inside the one ZIP**. Do not add them as sibling PR files.
- [ ] Start a fresh branch from the intended PR base (prefer a separate worktree, retaining any existing changes). Do not reuse the feature/product implementation branch.

## Publish without extra diff paths
- [ ] Put only `local-agent-handoffs/<project-slug>/issue-<number>/<candidate-id>.zip` (or `task-<stable-id>` for non-issue work) on the artifact branch. A project README, if newly needed, is a separate main documentation commit, not another path in this PR.
- [ ] Run `git diff --cached --name-only`; expect **exactly one file path**, the ZIP. Review actual staged diff.
- [ ] Commit/push; `gh pr create --draft` or equivalent. No merge, no deploy and no ready-for-review transition.
- [ ] Query server `gh pr view NUMBER --repo OWNER/REPO --json isDraft,headRefOid,baseRefOid,url` to confirm **draft=true**, correct head and base.
- [ ] Query server `gh pr diff NUMBER --repo OWNER/REPO --name-only`; expect exactly the one approved artifact path (not merely one local commit). Inspect if binary file can actually be fetched.
- [ ] Rehash downloaded remote bytes where available; otherwise mark remote-byte verification NOT_RUN and retain local SHA with qualification.

## Return to task issue
- [ ] Post a new [delimited handover comment](COMMENT_BLOCK.md) to the **existing issue**, with artifact PR URL, one path, exact head SHA, local SHA-256 and bytes, independent PR diff/draft check and remote retrieval status.
- [ ] Read back posted comment by comment ID. Give successor the **issue/comment link**, not copied prose.
- [ ] Leave artifact PR **OPEN/DRAFT** until the Owner decides disposition. A PR URL is not guaranteed permanent if refs are removed; do not promise archival permanence. If contents change, issue a **new commit and handover comment**; don't silently relabel old evidence.
- [ ] Keep unmet task criteria, product failures and NOT_RUN tests visible. Archive transmission PASS never equals product DONE.

If repository access, privacy, size or approved artifact location is absent, **do not create a public PR**. Return `Artifact-PR: NOT_CREATED(reason)` and ask for the smallest safe authorization/unblock. Continue independent authorized work.
