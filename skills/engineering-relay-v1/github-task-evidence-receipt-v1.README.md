# R10 — observing public TaskEvidence is not accepting it

## Native observation path
`observePublicTaskEvidence({repository,parent_issue,task_issue,comment_id},{readToken})` performs two bounded, no-cache, redirect-refusing GitHub REST `GET /repos/{repo}/issues/comments/{id}` reads. Each read verifies the repository-scoped exact URL, HTML issue link, task issue id, author identity, created/updated timestamps, nonblank UTF-8 comment body and bounded size. SHA256 is over the **literal UTF-8 comment body bytes**. Any edit/author/source change between reads causes typed `STALE`. Provider errors, redirects, foreign refs, oversized responses and malformed JSON fail closed. A malicious historical edit restored between the two GETs cannot be detected; this is a mutable, non-atomic provider observation, NOT an immutable Git blob.

The return is deeply frozen *content-free* metadata: parent/task issue ID, comment ID, exact URL, author ID/login, timestamps, SHA256/body-byte length, marker presence, observed transport, read count and receipt SHA. It **never exposes the raw body** nor reads private chats. Comment author and a claim such as `TASK_EVIDENCE END`, `OWNER APPROVED` or `AC8/8` are explicitly producer assertions. No receipt is a different-principal code review or accepted engineering outcome.

## Actual consumers
`rehearseNativeFullChain(...,{publicEvidenceRead:{scope,readToken},...})` can optionally bind the comment to a task in the provider's **explicit child issue scope**. It reads G2c source, public comment (double read), then R3 native provider/pr/current CI (PR double read) before building R1+R3+public-comment `observed-frontier-v1`. R4 validates the receipt's digest and propagates it into parent managed-block *draft* and source-linked successor handover. Final full-chain digest binds lineage, receipt, provider and R4 preview. No magic acceptance: denominator `NOT_ADJUDICATED`, counts `null`, `producer_assertions_not_authority:true`, `live_writer_enabled:false`.

Without `publicEvidenceRead`, existing callers continue working and explicitly report `PUBLIC_TASK_EVIDENCE_NOT_OBSERVED` (the pure provider-only renderer still gives `SOURCE_GRAPH_UNAVAILABLE_NO_AUTHORIZED_NEXT`).

## Reproduction and authority
Real public sample is [R9 task #852's TaskEvidence END comment](https://github.com/reallaksh19/Common/issues/852#issuecomment-6072336145). Native Node22/24 workflow `relay-reset-public-task-evidence` makes a **real two-GET** source read and checks no acceptance/Owner private provenance. Also trigger full-chain native current-PR+source and R8 cold-process non-regression on receipt module changes. Local fixture/tests may inject fake native responses for adversarial refusals; injected transport is labeled `INJECTED_UNVERIFIED`.

Do not upload private ChatGPT/Codex/Claude chats or grant retention consent from this document. Do not enable R5/B2b live writer. Independent code and AC8 reviews remain open, **AC0/8**.
