# Local-agent handoffs — project-wise artifact home

This folder is the **shared handoff artifact namespace** in `reallakshman19/Common`, selected by the Owner for local agents and ChatGPT to use across projects. It is **not** the codebase of any project and grants no permission to edit, accept, merge or deploy a project's code.

**Reusable protocol:** [Common agent-work local-handover](../skills/agent-work/local-handover/README.md), especially [GitHub comment relay](../skills/agent-work/local-handover/COMMENT_RELAY.md) and [one-file draft PR checklist](../skills/agent-work/local-handover/forms/ARTIFACT_PR_CHECKLIST.md).

## Project folders

- [AA3](AA3/README.md) — includes the original task issue [AA3 #56](https://github.com/reallakshman19/AA3/issues/56).
- For a new project, add `local-agent-handoffs/<project-slug>/README.md` using [PROJECT_TEMPLATE.md](PROJECT_TEMPLATE.md) after verifying the owning repository and existing folder name. Prefer the repo's unambiguous short name; use `owner--repo` if names collide. Don't overwrite another project's identity.

A project README on `Common/main` is a **pointer/index**, not a statement of successful implementation. The authoritative original acceptance criteria, decisions, native evidence and Owner authority remain in the **owning project's issue**.

## Binary handoff: one draft PR, one file

1. The outgoing agent checks that **every byte is safe for a PUBLIC repository**. `Common` is public: an **OPEN/DRAFT PR is also public**. Never upload secrets, private chats, customer data, restricted inputs or a protected fixture, even inside a ZIP. If unsafe, do not publish: mark `NOT_CREATED(PRIVACY)` and request a permitted private route.
2. The agent builds one transfer archive locally containing `README.md`, patch or deliverable, manifest, executed test logs, and evidence (as applicable). The *archive* is the **one file** that will appear in the PR diff. Record local size, SHA-256 and ZIP entry integrity.
3. Create a fresh **artifact-only branch from `Common/main`**. Stage/commit exactly one path:
   `local-agent-handoffs/<project-slug>/issue-<number>/<candidate-id>.zip`
   A non-issue task may use `task-<stable-id>` instead of `issue-<number>`. `candidate-id` must distinguish transfers and be stable; do not reuse a path to silently replace earlier bytes.
4. Open a **dedicated DRAFT PR targeting `Common/main`** with a title such as `handoff(AA3 #56): <candidate-id> artifact only`. Do not put source implementation, sidecar manifest, or project-index changes in this PR. No ready-for-review transition, auto-merge or merge.
5. From the GitHub server (not a local claim), verify `isDraft=true`, `state=OPEN`, the expected base/head, and **exactly one changed path** equal to the archive path. Retrieve and re-hash the remote bytes where tooling permits, otherwise record that remote-byte verification is `NOT_RUN`.
6. Post and read back a [delimited handover comment](../skills/agent-work/local-handover/forms/COMMENT_BLOCK.md) on the **original owning-project task issue**, linking the Common draft PR, head commit, artifact path, local SHA-256/bytes, remote verification limit, full original unfinished criteria and next action.
7. The receiving local agent opens the owning issue link, reads the applicable comment and draft PR, checks the actual ZIP, and posts its separate result on the same issue. The Owner no longer needs to paste the handover prose.

**Do not commit ZIPs directly to `Common/main` by default.** This folder and project indexes may be committed to main; the binary transfer goes to an isolated draft PR. The Owner alone decides artifact PR disposition and any eventual merge or retention. An open draft PR link is retrievable while GitHub retains the ref; it is **not a guaranteed permanent archival URL** if the branch/PR is deleted or inaccessible.

## Already available Google Drive file

An agent may continue authorized work from an actual **Owner-linked Google Drive file**, after downloading and independently hashing its bytes. Drive access and transfer integrity are not product acceptance; do not create a fake GitHub artifact PR or delay tests merely to duplicate an already verified transfer. For a *separately selected* GitHub artifact PR, use the one-file OPEN/DRAFT route above only with content safe for public Common. [Local-agent operating instructions](../skills/agent-work/local-handover/AGENT_PROTOCOL.md) distinguish these routes. Preserve Drive sharing boundaries and do not widen permissions by default.

## Transfer vs acceptance

ZIP CRC, manifest hashes, GitHub delivery and a one-file PR do **not** prove engineering correctness. Independently inspect the candidate against the original project source and run the real consumer/negative tests. Keep predecessor reports distinct from actual executed evidence.

If GitHub access, Git binary limits, public safety or retrieval fails, give the **actual blocker** and proceed with unaffected authorized work. No automated background upload, hidden dispatch, role quota, qualification exam or merge permission is introduced.
