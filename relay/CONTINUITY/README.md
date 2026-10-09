# Relay continuity — Markdown messages for planned and unplanned agent succession

**Contract:** RELAY_CONTINUITY_MD_V1 · [governing issue Common #890](https://github.com/reallaksh19/Common/issues/890) · **candidate, not admitted production protocol**. These files are the transport/communication language for a Controller, Coder A, independent Runner B and Owner. They are **not** a second event store, lease, scoreboard, agent-launch engine or GitHub authorization mechanism.

## Which mode is this?

| Cause | Route | Agent-facing work |
| --- | --- | --- |
| Planned, A still active | Runner / buddy | Stage 1 independently reconstructs historical system **before** evaluating the original Owner problem. A continues coding. |
| Planned exit | Technical handover transaction | Exact current material, tests, uncertainty and custody facts; separate from an independent design exercise. |
| Unplanned A termination without a clean frozen B | External Two-Pass | Task-blind live-repo baseline, then disclose issue/history, reconcile, draft plan and seek Owner approval. |
| Unplanned A termination requiring broad app expansion | External Three-Pass | Explicitly select programme- and local-level imagination before reality/reconciliation/action; not the automatic default. |

If A terminates **after** an independently frozen Stage 1, a Controller may offer Runner B emergency Stage 2 using current provider evidence and explicit `missing-A` statements. Neither route may invent an A handover.

## Communication sequence and file roles

The *operator*, not Agent A, establishes a unique episode identifier pointing to the **same existing** parent/leaf/Local responsibility. Future instance records may be committed under `relay/CONTINUITY/episodes/<episode-id>/` only after release/visibility is resolved. Do **not** create a new EP or progress denominator merely because the executor changes.

| Step | Record template | Who authors it | Visibility/decision |
| --- | --- | --- | --- |
| 0 | [STAGE1_SOURCE_PACKET](TEMPLATES/STAGE1_SOURCE_PACKET.md) | A drafts; operator curates/pins | B sees historical approved source and minimal Owner constraints **only** |
| 1 | [STAGE1_RECONSTRUCTION](TEMPLATES/STAGE1_RECONSTRUCTION.md) | **Fresh B** | **Part A factual historical system witness FIRST**; Part B original-problem hypotheses SECOND; nothing published as a current plan |
| 2 | [STAGE1_FREEZE](TEMPLATES/STAGE1_FREEZE.md) | Independent controller | Verify original bytes, immutable readback, actual denied-read isolation; no self-attestation |
| 3 | [TECHNICAL_HANDOVER](TEMPLATES/TECHNICAL_HANDOVER.md) | Existing A/Relay custody projector + source-grounded report author | **One self-contained technical report:** original problem, changed functions/consumers, architecture and actual flow, test/CI/goldens, defects, repo migration and exact successor starting point; **not readable by B before Step 2** |
| 4 | [STAGE2_RECONCILIATION](TEMPLATES/STAGE2_RECONCILIATION.md) | Same B after release | Four views: Owner, frozen B, A claims, actual current repo/provider. Detailed next plan is **DRAFT** |
| 5 | [OWNER_DECISION](TEMPLATES/OWNER_DECISION.md) | Authenticated Owner/controller | Approve/hold plan and refer to externally evidenced Local writer admission. Markdown **never mints credentials** |

The templates are **formats only**. They must not be handed to a clean Stage 1 B as a directory. A Stage 1 session receives exactly the filtered Step 0 input and the Stage 1 response instructions; no Stage 2 templates, current issue/branch/PR feed, task-specific answer keys or predecessor current state.

## Technical handover must explain the actual engineering, not just custody

The [technical handover template](TEMPLATES/TECHNICAL_HANDOVER.md) is a **narrative, self-contained report**, not a process plan or a one-table module inventory. A successor must be able to answer **what the original Owner needed, what was built and why, exactly where and how data flows across changed functions and consumers, what tests actually ran at which head, what failed, how repositories/PR identities migrated, what remains, and the first safe reproducible step** from that report alone. An `UNKNOWN` is better than guessed task-start SHAs, tests, author identity, deployment, writer custody or progress. Three source-grounded reconstruction questions test technical understanding after the report.

[Source-grounded example: Common V3.2 integration](REVIEWER_ONLY/TECHNICAL_HANDOVER_COMMON_889_890_V1.md) is an actual engineering report, **not an admitted native handover**. It is published on a GitHub-visible draft branch; the `REVIEWER_ONLY` path is an audience label, **not technical confidentiality**. Do not supply its current Agent A HOW to a clean Stage 1 B. Actual post-freeze disclosure requires external tool isolation and native custody authority. The existing `HANDOVER_CONTEXT` remains canonical for its verified transaction and lease facts; the Markdown narrative must not invent or replace them.
## Stage 1 output/transaction mapping — do not manufacture B provenance

The [native-record bridge](STAGE1_NATIVE_RECORD_BRIDGE.md) reconciles this operating model's **one independent Stage 1 reasoning submission** with the candidate native transaction's **two separate B-origin records** (`STAGE1_BASELINE`, then `STAGE1_PLAN`). Actual B must author two original deliverable Markdown documents in the same fresh restricted session; neither A nor a controller may reconstruct them by splitting/retyping a combined answer. The native `actor` and session-ref strings remain unverified claims unless externally authenticated. A native `STAGE1_FREEZE_CANDIDATE` binds five committed receipts and must say `NOT_ATTESTED`; it is **not** the separate external `STAGE1_FREEZE_V1` approval. If original two-file B bytes, verified read boundary or final external authorization are missing, **HOLD** and do not publish current A handover to B. See the controller-only mapping and negative acceptance cases before attempting any live succession.

## Dispatch between preparation and independent reconstruction

**Required transition: preparation is not launch.** Once the original source packet/snapshot have been checked **once**, publish a single [RUNNER_DISPATCH_REQUEST_V1](TEMPLATES/RUNNER_DISPATCH_REQUEST.md) through an authorized Relay message, naming a real external launch operator, immutable input refs, actual isolation mechanism and expected independent B output. Consult the [dispatch/no-progress runbook](RUNNER_DISPATCH_RUNBOOK.md).

If the preparing agent cannot create a fresh separately restricted B session, record `DISPATCH_BLOCKED_NO_SESSION_CAPABILITY` and stop the preparation subtask; escalate **one** exact operator action and immutable request ref. Do not recertify the same input files on every follow-up. Only a controller-observed distinct session and actual restricted tool/access denial permits `RUNNER_STARTED_ATTESTED`; B's independently authored output and controller freeze are **later separate gates**.

[Core1B repeated-verification failure](EXAMPLES/CORE1B_20261009_DISPATCH_POSTMORTEM.md) is the dispatch regression: nine correctly copied source files and a stable packet do not launch Runner B. [Reviewer-only cross-domain prompt review](REVIEWER_ONLY/CROSS_DOMAIN_PROMPT_CONTRACT_REVIEW_V1.md) probes the same reasoning contract on R-PROJECTION and LFJ; do **not** put the reviewer note in a Stage 1 input envelope. No new event exists when an unchanged blob is checked again.

## Release preflight and actual access evidence

The [operator Stage 1 release contract](OPERATOR_STAGE1_RELEASE_CONTRACT.md) and [controller-only preflight receipt](TEMPLATES/STAGE1_RELEASE_PREFLIGHT.md) make the B read boundary measurable: fresh session, actual input bytes, allowed historical source read, denied current A/PR/issues/Stage 2, and denied alternate raw-URL/connector/shared-memory routes. Keep these controller instructions **out of B's Stage 1 input envelope**. A single unresolved or untested negative probe means NOT_BLIND rather than clean. A historical source packet's Git hash is input integrity only.

## Confidentiality and real blindness

A committed Markdown path is not private from other users or tokens with read access to the repository. **GitHub does not provide path-level confidentiality to a reader with whole-repo rights.** The safe options are (1) external tool/ref/path enforcement plus auditable denial, or (2) do not publish the current A reality on *any* B-readable ref until its independent Stage 1 is sealed. Folder names, HEAD pins, an instruction "don't read" and content hashes are not equivalent to isolation.

If either the Stage 1 context cannot be separated or a forbidden fact was available, report `STAGE1_BLINDNESS_UNVERIFIED` / `STAGE1_CONTAMINATED`, do not grant Stage 2 independence credit; restart B if a clean trial is needed. An open PR, issue comment or a GitHub branch can expose withheld material—control **tools and scopes**, not just filenames.

## Versioned Markdown envelope

Each actual message contains: `Record kind/version`, `existing responsibility and episode`, `writer/role`, `origin and observation timestamp`, `immutable source SHA or UNKNOWN`, `visibility and claims vs source-backed facts`, `payload with source references`, `STOP/next permitted operation`. Prefer a short Markdown table and substantive evidence over repeating fields. Corrections create an **amended new version**; never rewrite an already-frozen B response.

Commit in a governed branch/PR and read back at an exact immutable SHA. No agent silently publishes, approves, or merges its own decision; use existing Local role/Owner and provider controls.

## Authoritative state is elsewhere

See [authority and source map](AUTHORITY_MAP.md). Existing `relay/STATE.yaml`, `relay/EVENTS.jsonl`, `relay/ROADMAP/`, `relay/LEASES/`, `relay/CHECKPOINTS/`, `relay/TRANSACTIONS/` and `relay/GENERATED/` remain the authority for what they already record. In V3.5, accepted source-bound facts and **DELP** own derived status; Local v1.1 owns source writer, reviewer/coordinator transitions and merge gates. An agent message cannot advance a lifecycle epoch or earned progress.

## Current release state

`TEMPLATES_AVAILABLE` does not mean `B_ACTUALLY_STARTED`, `BLINDNESS_VERIFIED`, `FREEZE_PERFORMED`, `STAGE2_ADMITTED`, `OWNER_APPROVED`, `WRITER_REVOKED` or `RUNNER_ADVANTAGE_PROVEN`. Until externally demonstrated, those remain **NOT_RUN / UNKNOWN**. See Common #890 for WP0–WP5 and explicit design/authority decisions.
