# Relay continuity — Markdown messages for planned and unplanned agent succession

**Contract:** RELAY_CONTINUITY_MD_V1 · [canonical-repository integration issue #1](https://github.com/reallakshman19/Common/issues/1) · [historical Owner/plan issue old #890](https://github.com/reallaksh19/Common/issues/890) · **candidate, not admitted production protocol**. These files are the transport/communication language for a Controller, Coder A, independent Runner B and Owner. They are **not** a second event store, lease, scoreboard, agent-launch engine or GitHub authorization mechanism.

## Which mode is this?

| Cause | Route | Agent-facing work |
| --- | --- | --- |
| Planned, A still active | Runner / buddy | Stage 1 independently reconstructs historical system **before** evaluating the original Owner problem. A continues coding. |
| Planned exit | Technical handover transaction | Exact current material, tests, uncertainty and custody facts; separate from an independent design exercise. |
| Unplanned A termination without a clean frozen B | External Two-Pass | Task-blind live-repo baseline, then disclose issue/history, reconcile, draft plan and seek Owner approval. |
| Unplanned A termination requiring broad app expansion | External Three-Pass | Explicitly select programme- and local-level imagination before reality/reconciliation/action; not the automatic default. |

If A terminates **after** an independently frozen Stage 1, a Controller may offer Runner B emergency Stage 2 using current provider evidence and explicit `missing-A` statements. Neither route may invent an A handover.

## Stage 1 original-file mapping: one B session, two original records

The [native Stage 1 record bridge](STAGE1_NATIVE_RECORD_BRIDGE.md) maps one independently reasoned B submission onto exactly **two separately B-authored original UTF-8 documents**: `# STAGE1_BASELINE` (factual Part A completed first), then `# STAGE1_PLAN` (provisional Part B). If B supplied only a combined answer, preserve the actual unchanged bytes and **HOLD**; Agent A or a controller must not synthesize two B-authored files by splitting or retyping it. Native `STAGE1_FREEZE_CANDIDATE` is a five-receipt local integrity check with `Isolation verdict: NOT_ATTESTED`, **not** the external `STAGE1_FREEZE_V1` decision or a Stage 2/writer grant. The separate [Stage 1 response template](TEMPLATES/STAGE1_RECONSTRUCTION.md) is only a format for a genuinely isolated B and is never a controller-authored answer.

## Communication sequence and file roles

The *operator*, not Agent A, binds a continuation to the **existing, provider-verified parent/leaf/Local responsibility and its repository identity**. The proposed native V3.2 [PR #2](https://github.com/reallakshman19/Common/pull/2) would use `relay/CONTINUITY/episodes/ISSUE-<current-repo-issue>/messages/TX.<issue>.<serial>-<STAGE>.md` through the existing `PUBLISH_BUDDY_MARKDOWN` transaction. **This is a candidate, not yet admitted production transport.** Historical `episodes/CORE1B_GOLDENS_RUNNER_20261009/` files are research fixtures and are **not** native transactional messages. Avoid a second active episode namespace, a new EP or a duplicate progress denominator.

| Step | Record template | Who authors it | Visibility/decision |
| --- | --- | --- | --- |
| 0 | [STAGE1_SOURCE_PACKET](TEMPLATES/STAGE1_SOURCE_PACKET.md) | A drafts; operator curates/pins | B sees historical approved source and minimal Owner constraints **only** |
| 1 | [STAGE1_RECONSTRUCTION](TEMPLATES/STAGE1_RECONSTRUCTION.md) | **Fresh B** | **Part A factual historical system witness FIRST**; Part B original-problem hypotheses SECOND; nothing published as a current plan |
| 2 | [STAGE1_FREEZE](TEMPLATES/STAGE1_FREEZE.md) | Independent controller | Verify original bytes, immutable readback, actual denied-read isolation; no self-attestation |
| 3 | [COMPLETE TECHNICAL HANDOVER V2](TEMPLATES/TECHNICAL_HANDOVER.md) | **Agent A** (or clearly attributed source-only reconstruction after termination), using existing transaction/provider receipts | **One self-contained engineering reality report**: original problem, built architecture/code/flow, exact tests and CI, real defects, repository migration and next-engineer starting point. Controller keeps it unreadable by B before verified Stage 1 freeze; it does not create custody. |
| 4 | [STAGE2_RECONCILIATION](TEMPLATES/STAGE2_RECONCILIATION.md) | Same B after release | Four views: Owner, frozen B, A claims, actual current repo/provider. Detailed next plan is **DRAFT** |
| 5 | [OWNER_DECISION](TEMPLATES/OWNER_DECISION.md) | Authenticated Owner/controller | Approve/hold plan and refer to externally evidenced Local writer admission. Markdown **never mints credentials** |

The templates are **formats only**. They must not be handed to a clean Stage 1 B as a directory. A Stage 1 session receives exactly the filtered Step 0 input and the Stage 1 response instructions; no Stage 2 templates, current issue/branch/PR feed, task-specific answer keys or predecessor current state.

## Dispatch between preparation and independent reconstruction

**Required transition: preparation is not launch.** Once the original source packet/snapshot have been checked **once**, publish a single [RUNNER_DISPATCH_REQUEST_V1](TEMPLATES/RUNNER_DISPATCH_REQUEST.md) through an authorized Relay message, naming a real external launch operator, immutable input refs, actual isolation mechanism and expected independent B output. Consult the [dispatch/no-progress runbook](RUNNER_DISPATCH_RUNBOOK.md).

If the preparing agent cannot create a fresh separately restricted B session, record `DISPATCH_BLOCKED_NO_SESSION_CAPABILITY` and stop the preparation subtask; escalate **one** exact operator action and immutable request ref. Do not recertify the same input files on every follow-up. Only a controller-observed distinct session and actual restricted tool/access denial permits `RUNNER_STARTED_ATTESTED`; B's independently authored output and controller freeze are **later separate gates**.

[Core1B repeated-verification failure](EXAMPLES/CORE1B_20261009_DISPATCH_POSTMORTEM.md) is the dispatch regression: nine correctly copied source files and a stable packet do not launch Runner B. [Reviewer-only cross-domain prompt review](REVIEWER_ONLY/CROSS_DOMAIN_PROMPT_CONTRACT_REVIEW_V1.md) probes the same reasoning contract on R-PROJECTION and LFJ; do **not** put the reviewer note in a Stage 1 input envelope. No new event exists when an unchanged blob is checked again.

## Release preflight and actual access evidence

The [operator Stage 1 release contract](OPERATOR_STAGE1_RELEASE_CONTRACT.md) and [controller-only preflight receipt](TEMPLATES/STAGE1_RELEASE_PREFLIGHT.md) make the B read boundary measurable: fresh session, actual input bytes, allowed historical source read, denied current A/PR/issues/Stage 2, and denied alternate raw-URL/connector/shared-memory routes. Keep these controller instructions **out of B's Stage 1 input envelope**. A single unresolved or untested negative probe means NOT_BLIND rather than clean. A historical source packet's Git hash is input integrity only.

## Confidentiality and real blindness

A committed Markdown path is not private from other users or tokens with read access to the repository. **GitHub does not provide path-level confidentiality to a reader with whole-repo rights.** The safe options are (1) external tool/ref/path enforcement plus auditable denial, or (2) do not publish the current A reality on *any* B-readable ref until its independent Stage 1 is sealed. Folder names, HEAD pins, an instruction "don't read" and content hashes are not equivalent to isolation.

If either the Stage 1 context cannot be separated or a forbidden fact was available, report `STAGE1_BLINDNESS_UNVERIFIED` / `STAGE1_CONTAMINATED`, do not grant Stage 2 independence credit; restart B if a clean trial is needed. An open PR, issue comment or a GitHub branch can expose withheld material—control **tools and scopes**, not just filenames.

## Standalone technical report acceptance

A completed [HANDOVER_TECHNICAL_V2](TEMPLATES/TECHNICAL_HANDOVER.md) is an **engineering explanation**, not a form of process instructions. It must be readable on its own: what original problem and Owner scope existed; what changed with path/function/source evidence; how a real input travels through validation/transforms/downstream consumers to a user output; which positive/negative/browser, fixture/golden and CI runs actually passed or failed at precise SHAs; known defects/risks/rejected attempts; old/new repo-object identities; and the exact first safe source/command for the successor. A table of HEAD/PR/issues and “see code” links alone is **NOT a handover report**. Keep current A material Stage 2-only and treat A's authored explanation as a claim until independent source/provider readback. External Owner/Local/Relay remains custody authority.

## Current source-backed examples and integration authority

The [actual V3.2 Buddy integration handover candidate](REVIEWER_ONLY/TECHNICAL_HANDOVER_COMMON_889_890_V1.md) and the [V3.5/R14 example](REVIEWER_ONLY/EXAMPLE_COMPLETE_TECHNICAL_HANDOVER_PR3_V1.md) explain different work at different source HEADs. They are **separate controller/reviewer-only evidence examples**, not two live technical handover authorities or Stage 1 input packets. When emitting one complete Stage 2 report use the canonical [HANDOVER_TECHNICAL_V2](TEMPLATES/TECHNICAL_HANDOVER.md) narrative and reference existing native `HANDOVER_CONTEXT` for custody. A candidate committed to a public GitHub branch remains readable by any Runner with unrestricted repository access: never treat the `REVIEWER_ONLY` directory label as access control.

The [PR #2 / PR #3 consumer convergence record](REVIEWER_ONLY/BUDDY_R14_CONSUMER_CONVERGENCE_V1.md) gives the exact source provenance and fail-closed provider-binding test matrix. The native transaction can authenticate local message bytes; it cannot independently prove the current-repository issue binding, fresh B identity, denied reads, freeze, Owner decision or writer custody.

**Current V3.5 handover example:** The [source-observed V2 technical report](REVIEWER_ONLY/EXAMPLE_COMPLETE_TECHNICAL_HANDOVER_PR3_V2.md) improves the older example with concrete tested-vs-skipped CI evidence and true inherited baseline classification. Both examples remain controller-only worked reports, **never input to a clean Stage1 B**.

## Versioned Markdown envelope

Each actual message contains: `Record kind/version`, `existing responsibility and episode`, `writer/role`, `origin and observation timestamp`, `immutable source SHA or UNKNOWN`, `visibility and claims vs source-backed facts`, `payload with source references`, `STOP/next permitted operation`. Prefer a short Markdown table and substantive evidence over repeating fields. Corrections create an **amended new version**; never rewrite an already-frozen B response.

Commit in a governed branch/PR and read back at an exact immutable SHA. No agent silently publishes, approves, or merges its own decision; use existing Local role/Owner and provider controls.

## Authoritative state is elsewhere

See [authority and source map](AUTHORITY_MAP.md), [R14 schema/interface review](REVIEWER_ONLY/R14_SOURCE_INTERFACE_RECONCILIATION_V1.md) and the [old/new repository lineage + PR #2/#3 collision ledger](REVIEWER_ONLY/REPOSITORY_LINEAGE_AND_PR_COLLISION_V1.md). Historical old-repo issue/PR URLs are immutable provenance, **not new-repository evidence**. Native PR #2's numeric issue-scoped path requires actual new-repo provider binding; a local transaction digest cannot certify the issue exists in the target repository. Existing `relay/STATE.yaml`, `relay/EVENTS.jsonl`, `relay/ROADMAP/`, `relay/LEASES/`, `relay/CHECKPOINTS/`, `relay/TRANSACTIONS/` and `relay/GENERATED/` remain the authority for what they already record. In V3.5, accepted source-bound facts and **DELP** own derived status; Local v1.1 owns source writer, reviewer/coordinator transitions and merge gates. An agent message cannot advance a lifecycle epoch or earned progress.

## Current release state

`TEMPLATES_AVAILABLE` does not mean `B_ACTUALLY_STARTED`, `BLINDNESS_VERIFIED`, `FREEZE_PERFORMED`, `STAGE2_ADMITTED`, `OWNER_APPROVED`, `WRITER_REVOKED` or `RUNNER_ADVANTAGE_PROVEN`. Until externally demonstrated, those remain **NOT_RUN / UNKNOWN**. See Common #890 for WP0–WP5 and explicit design/authority decisions.
