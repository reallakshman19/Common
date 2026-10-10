# BuddyRunner v1.5 — Stage 2: Course correction, ROI reconciliation and technical handover

**Your role:** engineering buddy, not a rubber stamp. This stage must *challenge* the Stage 1 proposal and the predecessor's decisions with the current issue, parent roadmap and **current actual source**. Your result is a corrected engineering direction AND a self-contained technical handover, not just a plan or a PR summary.

**Mode: OPEN_SOURCE_PURPOSE_RECONSTRUCTION.** This is *not* a blind Runner B promotion. Existing V3.5 blind Stage 1/Stage 2 isolation, Local v1.1 writer transfer, independent review, DELP and Owner merge/release controls remain separate. This prompt creates no authorizations.

## A. Verify the prerequisite and keep history honest

Fetch the Stage 1 GitHub issue-comment body **on the owning current issue**. Compute SHA-256 over the **UTF-8 bytes of the provider-returned body text**, including its exact line breaks (not HTML/Markdown rendering, JSON wrapper, URL or metadata); compare against the supplied `sha256:<64 lowercase hex>` claim. Verify the issue-comment URL/author/provenance with the provider. A renderer-validated URL and an agent-supplied digest are never enough. If the publication is absent, inaccessible, on the wrong issue, or byte-mismatched, mark **STAGE1_NOT_VERIFIED** and stop at a bounded diagnostic. Do not fabricate an independent purpose. If Stage 1 is merely `NOT_PUBLISHED`, a provider-backed Stage 2 request cannot be generated; obtain permitted publication/readback first.

Treat a digest or an evidence_grade field as a *claim* until verified. Do not rewrite Stage 1 to make it look correct. Read the actual Owner current issue, parent, roadmap and amendments. Refresh the live PR/branch/source commit and compare it with the Stage 1 pinned commit; never silently change that baseline or borrow green CI from a different head.

If a historical blind/isolated Buddy trial is intended, stop and use the existing governed Runner B packet/freeze/disclosure contracts; this open-source generator cannot attest isolation.

## B. Reconcile the four distinct viewpoints

For every meaningful user outcome, compare:
1. Owner's actual purpose and source provenance.
2. Agent's *frozen* Stage 1 proposed purpose and module choices.
3. Existing predecessor/competing PR design claims.
4. Independently observed current source/functions, downstream consumers and evidence.

Use this decision table:

| User-visible outcome and invariant | Owner's purpose | Stage 1 agent choice | Current source and competing implementation | Decision | Smallest correction / source basis |
|---|---|---|---|---|---|

Decision values: KEEP_STAGE1, KEEP_EXISTING, COMBINE_BOUNDEDLY, REVISE_BOTH, VERIFY_FIRST, PARK, OUT_OF_SCOPE, OWNER_DECISION_REQUIRED, UNKNOWN.

Explicitly explain the agent's *own mistakes*, not just the predecessor's. When two architectures overlap, give each responsibility ONE proposed owner, identify the seam, and state which useful modules to retain. Do not merge incompatible size limits, permissions, source identities or CSV rights by accident.

Before proposing source edits, reconcile the **complete lifecycle**, not simply filenames: original-file selection, immutable file identity and hashing, storage/indexing, projection, XML/other domain matching, cancellation, recovery, result revision, user consent and export authorization. Specify one owner per responsibility. Treat purported defects as hypotheses until supported by code or targeted evidence. In particular:

- **Atomic source selection:** establish when original JSON/File, XML, configuration, source revision and selected mode become one valid Build identity; define the fail-closed behavior during partial or rapidly changing selections.
- **Scope contract:** establish whether evidence covers the *complete* original hierarchy, an explicitly authorized subtree, or a visible filtered/paginated view. Never let a partial rendered table or silent truncation masquerade as the complete authoritative result.
- **Full-output consistency:** reconcile projected facts, complete generated trace/evidence, rendered counts and both downloaded outputs against the SAME source/configuration revision; note which independent golden oracles would prove that.
- **Deployment reality:** investigate which source tree and generated artifact serve the actual deployed runtime early (repository root, `docs/`, generated artifact or another entrypoint), including transitive Worker/import closure. Implement mirror/deployment changes only AFTER coherent product module ownership is selected. Do not assume the existence of a `docs/` directory proves it is the deployed artifact.

For the LFJ example (when the request actually names competing 3D_Converters PRs #184/#185), assess the source-backed H10 handoff and the bounded indexed Build/hash/cancel/IndexedDB lifecycle separately. Consider reusing compatible proven capabilities without assuming which PR wins, rewriting established engineering matching/CSV semantics, or silently choosing between incompatible file-size, consent and revision policies. Keep independent semantic qualification, genuine Owner large-file evidence and downstream CII release outside the Stage 2 proposal.

## C. Choose high-ROI course correction

Rank no more than three source-grounded candidates by **user impact, recurrence prevented, complexity, semantic risk, dependency and rollback**. Compare a minimal local patch with a better bounded correction. Select **NOW**, **PARK** or **REJECT**; justify each. A NO_CHANGE outcome is legitimate.

Do not elevate cosmetic cleanup, extra test counts, complicated frameworks or performance claims unsupported by source over a missing real product path. Preserve established domain semantics, originals and independently protected golden expectations.

Provide a short **RECONCILED_PURPOSE** in plain language, a module-owner decision map covering Build, file identity, hashing, storage/projection, cancellation/recovery, result revision, rendering, CSV exports and the actual deployment artifact and one immediate *proposed* engineering outcome. Identify what needs a separate Owner/dependency decision. **This stage is analysis and handover, not coding or merge.**

## D. Produce a self-contained technical handover

A new engineer must be able to read this document *without any predecessor chat*. Include all sections below, each grounded or marked UNKNOWN/NOT_RUN:

1. **Original problem and Owner WHY** — context, user experience, roadmap and non-goals in plain words.
2. **Repository migration and identity** — old vs current repository, actual issue/PR object boundaries, main, inherited and current commits, tested commits.
3. **What exists** — real modules/functions, exact code ownership, native Workers, storage and frontend.
4. **How data flows** — original inputs → stored source → transformations → matching → user outputs and authority handoffs.
5. **What changed and why** — precise source files, function-level behavior, surviving variants and rationale.
6. **Input provenance and acceptance oracles** — original source files, size/hash where verified, synthetic-vs-authentic-vs-derived distinction and protected golden origin.
7. **Actual execution evidence** — exact command/CI URL + checked-out SHA, tested cases/results, browser/user-visible evidence and missing checks. Never promote prior-head CI to a new head.
8. **Known failures and unresolved defects** — failure signatures, cause established vs hypothesis, release effects.
9. **Reconciled high-ROI decisions** — chosen changes, rejected redesigns, parked alternatives, dependencies.
10. **Authority, security and preservation** — source integrity, research vs product rights, reviewer/Local/Owner distinction, deployed mirror and custody.
11. **What remains** — separate product, source, deployment, semantic, and release responsibilities; no invented percentages.
12. **Exact next engineer start** — repository, raw commit, branch/issue/PR, first modules to inspect, immediate bounded source-change proposal, verification that later implementation would need, rollback and stop conditions.

Include copyable Markdown. An optional document/PDF view is a presentation aid, not substitute for the original Markdown/source evidence.

## E. Publish the course correction and handover

Prepare one copy-ready comment for the existing current issue:

**PLAN_UPDATE — BUDDY_V15_STAGE2_RECONCILED_PURPOSE_AND_HANDOVER**

Include the brief corrected purpose, chosen module authority, selected ROI, deferrals, exact source identity, next action and the durable handover reference. Publish only with real permission and then read back; otherwise label **NOT_PUBLISHED**. This does not self-admit review, alter DELP progress, transfer a source lease, or authorize coding.

## Final output

Return the reconciled one-paragraph purpose, module decision map, top ROI choices, complete handover, issue publication URL or NOT_PUBLISHED, and **next engineer first source inspection**. Distinguish confirmed implementation reality, agent claims and pending independent acceptance. If the task requires a *new* engineering implementation, the existing authorized engineering workflow starts separately after this Stage 2 conclusion.
