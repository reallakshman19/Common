# Technical engineering handover — Common V3.2 Relay/Buddy continuity integration

**Report:** `TECHNICAL_HANDOVER_COMMON_889_890_V1` · **Source review date:** 2026-10-09 · **Visibility:** CONTROLLER/OWNER/POST-STAGE1 ONLY · **Release:** `CANDIDATE_FACTUAL_REPORT — NOT_NATIVE_HANDOVER / NOT_STAGE2_ADMISSION`.

**Purpose:** This is one self-contained explanation of what was requested, what was implemented, the real module/call flow, exactly what GitHub CI measured, remaining defects and the precise next engineer entry point. It is NOT a successor process plan. It does not transfer a lease, certify Runner B, or assert an accepted `HANDOVER_CONTEXT` transaction. This file is on a GitHub-visible draft branch; a directory named `REVIEWER_ONLY` is not a technical access restriction. A clean Stage1 B must not be given this material.

## 1. Technical situation and result

The Owner's original engineering problem was planned transition of a still-active Agent A to an independent Runner B, without losing the original problem, the actual source implementation or native engineering custody. A Runner should study an immutable original-source/Owner WHAT-WHY intake and first reconstruct how the historical system really behaves before proposing alternative HOWs. Only after a genuinely independent Stage 1 has been sealed may it receive A's current source, defects, test history and technical handover to reconcile with its earlier analysis. Ordinary unplanned termination retains a separately triggered Two-Pass/Three-Pass route. The Owner later required communication through Common `relay/` in durable Markdown rather than ad hoc chat prompts or unmanaged files.

The original approach had a real failure: Core1B Stage1 source was correctly pinned and checked repeatedly, but there was no independent Runner launch. `INPUTS_VERIFIED` was mistaken for progress. Two historical Common workstreams responded: [former #889 / PR #892](https://github.com/reallaksh19/Common/issues/889) built an issue-scoped transactional Markdown transport, and [former #890 / PR #893](https://github.com/reallaksh19/Common/issues/890) established the reasoning-first and external isolation/release format in `relay/CONTINUITY`. Both source branches survived the repository move; their PR/issue metadata did not transfer under the same numbers.

The current integration candidate combines their mechanisms in [new PR #2](https://github.com/reallakshman19/Common/pull/2). **Coded and hosted-test verified:** a `buddy-message` CLI/transaction records immutable Stage1 Markdown under canonical `relay/CONTINUITY/episodes/ISSUE-<n>/messages/`, enforces staged predecessor receipts, rejects tampering/role changes and can create an *unattested* five-phase freeze candidate. **Not built:** real second AI process launch, restricted GitHub/browser tool access, externally authenticated isolation, successful live B reconstruction, final Stage1 freeze, Stage2 release, Owner consent or writer promotion. Thus the implementation is a draft control candidate, not production handover.

## 2. Original problem, operational invariants and scope

Expected original workflow: A continues its assigned engineering work; a separate operator freezes an allowed historical source and original WHAT/WHY packet; fresh B studies original data producer→consumer→observed result and only then drafts provisional approaches. The release operator must prove positive allowed historical reads and deny current A code, new PRs/issues, Stage2/reviewer answers and alternate GitHub/browser/connector/shared-workspace routes. A source SHA proves content integrity only—not that B was blind. After a real Stage1 freeze, native technical handover supplies the current reality and a separately authorized Stage2 reconciliation can begin.

Immutable core constraints: no shadow execution state; no new DELP P/E/D calculator; no bypass of `relay/STATE.yaml`, native `PLAN_HANDOVER`, Relay lease/epoch, Local PR Delivery/Owner consent or reviewer acceptance; no invented Agent A true task-start SHA or accepted fixture result. `READINESS`, `DISPATCH_REQUEST` and a synthetic `RUNNER_EXECUTION_OBSERVED` Markdown claim cannot mint source-write authority. The earlier draft method used the language of 70% episode lifetime as an advisory, not a mechanism proven or implemented here.

**Provenance:** these intent/scope statements are grounded in [former #889](https://github.com/reallaksh19/Common/issues/889), [former #890](https://github.com/reallaksh19/Common/issues/890), and the imported `relay/CONTINUITY` records. The original standalone Agent A task-start commit for each historical Runner case is **UNKNOWN** in this integration; do not substitute the Common research/base commit for it.

## 3. Exact repositories, migration and source heads

| Source role | Verified value | Why it matters |
| --- | --- | --- |
| Canonical repository | `reallakshman19/Common` — `https://github.com/reallakshman19/Common.git` | All NEW commits, issues and PRs live here |
| Former source/tracker | `reallaksh19/Common`, historic #889/#890, PR #892/#893 | Source discussions retained only on former issue/PR URLs; do not reuse numbers as new IDs |
| New `main` / PR #2 base | `d60c36605e988dcc160647421973f170fd87e0eb` | Historical repository baseline, not Agent A's task start |
| Old transactional source branch | `feat/v32-889-relay-buddy-markdown-transaction@97d9f384ac1cfe4458b2db2302f5e7170a99e06d` | Original native recorder/test input to integration |
| Other agent's Continuity branch | `docs/relay-890-continuity-md-v1@09ff3751560bb49098e69c9c79918626078c7564` | Source of reasoning/release templates and operator runbook |
| First integrated commit | `65ba9d4ea1283d5f7a519afca0f2d8b8a8375817` | Consolidated canonical Markdown namespace and both mechanisms |
| Corrected tested runtime commit | `dc8203b11a5484ea8c530efc09ed5c2d43c9e3f3` | Hosted V3.2 native 38/38 PASS after one source fix |
| Verified integration/evidence checkpoint commit | `e5cdf5fb1de26992ab9fa5fd7752f4f5e7f74da5` | V3.2 and DELP PASS, frozen-tree guard still fails as intended |
| Current template revision (pre-report) | `446b7fc8d219be33466e66db3582ba6ec9c43310` | New comprehensive TECHNICAL_HANDOVER.md format, not a runtime/source change |
| New PRs and governance | [#2](https://github.com/reallakshman19/Common/pull/2) draft integration; [#7](https://github.com/reallakshman19/Common/pull/7) draft disabled grant; [issue #4](https://github.com/reallakshman19/Common/issues/4) | These are NEW issue/PR identities after migration |

**Checkout for an authorized engineer:** `git clone https://github.com/reallakshman19/Common.git && cd Common && git fetch origin integrate/v32-relay-continuity-889-890-20261009 && git checkout integrate/v32-relay-continuity-889-890-20261009`. Provider evidence currently establishes committed branch HEADs, not the engineer's local working-tree cleanliness. Verify `git rev-parse HEAD`, `git status --short`, `git diff main...HEAD --name-status`, and current PR base before editing.

## 4. Architecture and actual data/call flow

**Original authority:** V3.2's existing `relay/STATE.yaml`, `relay/TRANSACTIONS/`, checkpoint/lease/events and native `HANDOVER_CONTEXT` remain authoritative for the parts they govern. The other agent's Continuity Markdown files are documentation and authoring formats; the new `buddy-message` operation is an additive transaction recorder, *not* a second admission engine.

**Normal message publication path:**

1. An operator supplies an existing UTF-8 Markdown payload and explicit issue/TX ID, actor and stage to `skills/engineering-pr-delivery-v3.2/scripts/relay_tx.py . buddy-message --issue-number <n> --tx-id TX.<n>.<serial> --stage <STAGE> --actor <claimed-role> --markdown <source-file>`.
2. `relay_tx.main()` parses the command and calls `publish_buddy_markdown()`. The publisher checks issue/TX binding, stage membership, claimed actor, size, UTF-8, initial Markdown heading, and lack of a pre-existing target. The canonical destination is `relay/CONTINUITY/episodes/ISSUE-<n>/messages/TX.<n>.<serial>-<STAGE>.md`.
3. `transactionlib.execute()` calls `_prepare()`. For `PUBLISH_BUDDY_MARKDOWN`, `_validate_buddy_markdown_transaction()` enforces a single target, the exact issue/transaction/path/stage identity, Markdown content, immutability and the native predecessor chain even if a caller bypasses the CLI.
4. `_prior_buddy_message()` reads earlier, same-issue messages and **COMMITTED** receipts from `relay/TRANSACTIONS/TX.<n>.<serial>/manifest.yaml`. It checks actual byte digests, paths and no symlink fallback. `_require_buddy_sequence()` checks latest intake→dispatch request→dispatch observation→baseline→plan in increasing TX order; blocked dispatch cannot advance, revised intake supersedes stale evidence; the operator/B actor strings must differ at baseline and remain consistent for the plan.
5. A `STAGE1_FREEZE_CANDIDATE` checks the five real TX references and SHA-256 digests, rejects duplicated/conflicting fields, and requires literal `Isolation verdict: NOT_ATTESTED`. It is a **candidate** only, not a final freeze.
6. The existing atomic/recoverable transaction engine commits the bytes and manifest with target before/after digests. `publish_buddy_markdown()` reads back the target bytes and returns the SHA-256 and `admission: NOT_ATTESTED_BY_MESSAGE_TRANSPORT`. Interrupted work uses the existing `recover_all()` instead of blindly duplicating a TX.
7. **External boundaries:** a real Git provider commit/readback is separate from a locally committed transaction, and a real independent AI session/tool firewall is separate from both. Neither exists automatically because files were written under `relay/CONTINUITY/`.

**Downstream consumers:** The operator/Reviewer reads the immutable Markdown packet and external session/read-denial evidence; a genuine Stage1 B sees only sanitized original intake after an external release gate. Native handover remains `relay_tx.publish_handover()` / existing `PLAN_HANDOVER` and `HANDOVER_CONTEXT`; it produces `relay/GENERATED/HANDOVER.md` and event/snapshot effects under existing custody policy, not through `PUBLISH_BUDDY_MARKDOWN`. A successfully written Markdown message never directly updates root Relay state, native lease, DELP status, accepted TASK_EVIDENCE or Stage2 gate.

## 5. Exact changed modules, why and compatibility

| File / main function or contract | What changed and why | Downstream effect |
| --- | --- | --- |
| `scripts/relay_tx.py::publish_buddy_markdown`, `main` | Added explicit Markdown-only stage publication CLI and actual byte readback; stops uncontrolled free-form copies masquerading as handovers | Current and future Relay operator can record preparation/Stage1 messages, but cannot create writer admission |
| `scripts/transactionlib.py::COMMAND_TARGET_PATTERNS`, `BUDDY_MESSAGE_STAGES`, `_validate_buddy_markdown_transaction` | Narrow canonical path/stage/issue/immutable validation at transaction-core boundary; avoids bypass by direct API caller | Existing `execute` still owns atomic commit and recovery |
| `transactionlib.py::_prior_buddy_message`, `_require_buddy_sequence` | Native committed receipt/digest verification, strict latest stage ordering, supersession, actor-claim continuity | Prevents loose/tampered/stale historical Stage1 records becoming predecessor evidence; not proof of true AI identity |
| `transactionlib.py::_validate_freeze_candidate` | Requires exact five-phase TX identity/digest references and non-attesting verdict | Reviewer can inspect frozen bytes without treating them as permission for Stage2 |
| `schemas/transaction.schema.yaml` | Added `PUBLISH_BUDDY_MARKDOWN` command to the existing transaction enum | Reuses same native transaction schema, not a new schema family |
| `tests/test_relay_tx.py` | Added 15 Buddy-specific regression methods within the existing native suite; kept historic transactional tests | Hosted CI executes both new and legacy paths |
| `.github/workflows/engineering-pr-delivery-v3.2.yml` | Added execution of `test_relay_tx.py`; previously absent from V3.2 pipeline | CI now tests the new transaction path rather than giving misleading workflow-level green |
| `relay/CONTINUITY/**` | Imported source/reasoning/dispatch/preflight/Stage2/technical handover Markdown from the other agent; added integrated checkpoint and this comprehensive handover format | Canonical human/agent communication location; not a privacy firewall |
| `relay/BUDDY_RUNNER/README.md` | Replaced active instructions with a historical redirect | No second live message namespace |

**Deliberately unchanged:** native `relay/STATE.yaml`, `relay/EVENTS.jsonl`, `relay/LEASES`, `relay/ROADMAP`, existing checkpoints, DELP calculator, Local writer admission, `handover_context.py`, `plan_handover.py` and accepted V3.1/V3.2 handover schemas. The other agent's V3.5 source files were **not** copied into PR #2; only relevant `relay/CONTINUITY/` Markdown was integrated.

## 6. Source-based examples and what was observed

**Synthetic positive control (UNIT-TESTED, NOT A REAL RUNNER):** In `BuddyMarkdownRelayTests`, tests record a fake `STAGE1_INTAKE` with issue 889, followed by TX-scoped `DISPATCH_REQUEST` and `DISPATCH_OBSERVATION` with claimed session/read refs, an independently claimed baseline, a plan and a hash-bound freeze candidate. A successful transaction returns `COMMITTED` with `NOT_ATTESTED_BY_MESSAGE_TRANSPORT`, and does not create `relay/STATE.yaml` or a lease. This proves transaction logic, not a real AI agent.

**Negative controls:** absent baseline produces `BUDDY_STAGE_ORDER_MISSING_STAGE1_BASELINE` after correction; block observation prevents baseline; changed stage message bytes/receipt, wrong issue, duplicate message, symlink fallback, role substitution, stale chain, incorrect freeze digests and attempted `STAGE2_RECONCILIATION` are rejected. Source test method names and exact artifacts live in `tests/test_relay_tx.py`.

**Real observed failure:** The Core1B Stage1 packet and nine historical files were byte-verified on old Common `main`, but no independently isolated fresh B was ever launched. Operators repeated the same source checks and returned `RUNNER_LAUNCH_PENDING`. The Continuity runbook specifically requires a true launch or a terminal `DISPATCH_BLOCKED_NO_SESSION_CAPABILITY` status instead of this loop.

**Browser/product observation:** `BROWSER_NOT_RUN` for the Buddy continuity control integration. No standalone Chrome end-to-end / authentication-denial experiment or measured performance advantage of a 70%-life preparation has been executed, and no fabricated golden output is asserted.

## 7. Exact tests, CI and currentness

| Candidate | Actual check/run | Observed outcome | What it proves |
| --- | --- | --- | --- |
| `65ba9d4` initial integrated source | [V3.2 #37968064952](https://github.com/reallakshman19/Common/actions/runs/37968064952) | Continuity 195 PASS, replay 5 PASS, Relay native 37/38 PASS (1 failure) | One implementation test expectation was wrong; not a product release |
| `dc8203` corrected runtime | [V3.2 #37968469829](https://github.com/reallakshman19/Common/actions/runs/37968469829) | **SUCCESS, native Relay 38/38 PASS**, V3.2 downstream suites completed | Source-level functionality at that exact commit |
| `dc8203` corrected runtime | [DELP #37968469849](https://github.com/reallakshman19/Common/actions/runs/37968469849) | SUCCESS | Existing DELP compatible at that head |
| `dc8203` corrected runtime | [Local PR Delivery #37968470110](https://github.com/reallakshman19/Common/actions/runs/37968470110) | FAIL, frozen-tree guard on four V3.2 files | Valid governance block: base lacks authorized amendment |
| `dc8203` corrected runtime | [V3.1 #37968469824](https://github.com/reallakshman19/Common/actions/runs/37968469824) | FAIL, six missing legacy workflow-path errors | Separate legacy workflow issue, not a failure of 38 native tests |
| `e5cdf5` checkpoint-only successor head | [V3.2 #37968836955](https://github.com/reallakshman19/Common/actions/runs/37968836955); [DELP #37968837007](https://github.com/reallakshman19/Common/actions/runs/37968837007) | SUCCESS / SUCCESS | Confirms unchanged source with Markdown checkpoint |
| `e5cdf5` checkpoint-only successor head | [Local #37968836973](https://github.com/reallakshman19/Common/actions/runs/37968836973) | FAIL, governance block persists | No exact-path Owner approval established |
| `446b7fc` template change | GitHub source/blob readback | COMMITTED, **workflow outcome pending/unknown for this new head** | A Markdown format edit is not automatically CI qualified |

**Reproduce tests:** `python -m pip install PyYAML jsonschema` (project CI dependency setup); `python -m unittest discover -s skills/engineering-pr-delivery-v3.2/tests -p 'test_relay_tx.py' -v`. CI workflow `.github/workflows/engineering-pr-delivery-v3.2.yml` adds this suite. Do not claim an unrun newest HEAD is tested merely because a prior source HEAD passed.

**Performance:** `NOT_BENCHMARKED`. No actual distinct-model preparation-time advantage, source leakage rate, browser responsiveness or load performance measured. There are no real Core1B B test passes to report.

## 8. Current failures, unproven assumptions and protected risks

**Release-blocking governance:** [new issue #4](https://github.com/reallakshman19/Common/issues/4) and [draft PR #7](https://github.com/reallakshman19/Common/pull/7) enumerate the four exact frozen source paths (`transaction.schema.yaml`, `relay_tx.py`, `transactionlib.py`, `test_relay_tx.py`). PR #7 is explicitly `owner_authorized: false`, even though its six workflows pass. A proposed grant in the product PR cannot authorize its own changed files; the Owner must first explicitly approve a separate base-pinned governance change. PR #2 cannot merge on functional green alone.

**Unverified safety boundary:** Markdown `actor`, `Session ref`, `Read-scope ref` and a `STAGE1_FREEZE_CANDIDATE` cannot prove the B runtime was fresh or unable to read current A/Stage2 via GitHub, browser/search or shared memory. The source repo contains Stage2/controller material, so unrestricted access defeats independence. This remains `NOT_ATTESTED`, not a solved isolation design.

**Native custody:** PR #2 does NOT produce or validate a live `PLAN_HANDOVER`, real accepted HANDOVER_CONTEXT state, tested exclusive writer lease or owner decision. An actual technical handover remains future work. The present report is a factual description for review, not a native transaction.

**Other CI:** V3.1 missing `.github/workflows/engineering-pr-delivery-v2.5.yml` and `engineering-pr-delivery-v3.yml` surfaced in old `test_ci_terminal_checks` assumptions. This is distinct from the Buddy source failure and has not been repaired on this branch.

**Migration risks:** new issue/PR numbers differ; the historical old repository discussions are not metadata of new Common. `main@d60c` has separate future branches and PRs. Never refer to former PR #892 as PR #892 in the new repo. Any open API/provider operations or uncommitted local files of another engineer are `UNKNOWN` until provider/working-tree readback.

## 9. What the successor is permitted to infer about custody

**Source fact:** new integration PR #2 is DRAFT, not merged. Its HEAD includes committed transactions/control code and Markdown, while new issue #4 and governance PR #7 are separately open. The canonical V3.2 root `relay/STATE.yaml` was not changed by PR #2. The GitHub provider does not show an accepted new-issue task lease, a real B independent run, an admitted Stage2 session, or a native HANDOVER transaction for this case. Thus release, production deployment, merge authorization, transfer of source writer and any live DELP progress are **NOT ESTABLISHED**. Treat these as unknown/blocked, not inferred from Git branches or a well-written report.

## 10. First successor engineering step — exact starting point

An appropriately authorized successor should first read [PR #2](https://github.com/reallakshman19/Common/pull/2), this report, `relay/CONTINUITY/README.md`, `OPERATOR_STAGE1_RELEASE_CONTRACT.md`, `TEMPLATES/STAGE1_SOURCE_PACKET.md`, and native `transactionlib.py::_require_buddy_sequence`. Verify HEAD with `git rev-parse HEAD` and diff against `main@d60c` before making any edits. Run the focused native command above and check the *actual* log/exit code. A proper source baseline needs one synthetic positive path and blocked/forged negative controls, including the specific missing-immediate-prerequisite error.

**Next bounded engineering dependency:** governance must be resolved first. Verify the four exact changed files against the frozen-tree guard. The Owner must decide if a V3.2 code exception should be allowed; if yes, a separate approved amendment must be merged to the PR BASE before rebasing source PR #2 and rerunning Local/V3.2/DELP checks. If not approved, work only in already permitted Markdown surfaces and do not circumvent the guard. The parallel, separately launch-capable operator must test actual fresh B access with positive historical source reads and negative current-A/PR/Stage2 and alternate-tool read denials, then source-verify a genuine B baseline/plan before asking for a final freeze. Neither source green nor this document authorizes automatic B promotion.

**STOP immediately** for absent Owner grant, unqualified provider read isolation, a nonmatching exact SHA, a changed underlying native HANDOVER/lease, a source provenance mismatch, new unreviewed commits, or a failed direct test. There is no legitimate 'merge if green' shortcut across frozen-tree authority.

## 11. Three reconstruction questions for successor technical review

1. **Why does `buddy-message` not hand over execution?** Trace `relay_tx.main → publish_buddy_markdown → transactionlib.execute/_prepare` and explain the allowed destination/manifest and what state/lease/event it never writes. Negative control: call `PUBLISH_BUDDY_MARKDOWN` with a forbidden `STAGE2_RECONCILIATION` or an attempted `relay/STATE.yaml` target; a successful promotion would falsify the contract.
2. **How are stale prior Runner claims rejected?** Trace `_prior_buddy_message`, `_require_buddy_sequence`, `_validate_freeze_candidate`. Show an exact latest five-phase TX/digest chain, then replace the original intake or insert a later dispatch. Expected: a newer intake/dispatch invalidates earlier baseline/plan and a freeze cannot reuse them. A clean SHA of old source alone is not adequate.
3. **What is actually preventing merge now?** Compare [V3.2 SUCCESS #37968469829](https://github.com/reallakshman19/Common/actions/runs/37968469829), [Local frozen-tree failure #37968470110](https://github.com/reallakshman19/Common/actions/runs/37968470110), [issue #4](https://github.com/reallakshman19/Common/issues/4) and the disabled [PR #7](https://github.com/reallakshman19/Common/pull/7). Explain why 38/38 green native tests cannot satisfy base-pinned Owner authorization. Falsifier: a supposedly authorized source PR whose BASE still lacks a true independently approved manifest.

## 12. Evidence and limits

Primary references: [canonical Common PR #2](https://github.com/reallakshman19/Common/pull/2), [Owner/governance issue #4](https://github.com/reallakshman19/Common/issues/4), [disabled governance PR #7](https://github.com/reallakshman19/Common/pull/7), [former #889](https://github.com/reallaksh19/Common/issues/889) and [#890](https://github.com/reallaksh19/Common/issues/890), the actual new-branch `relay/CONTINUITY/` code and Markdown, [V3.2 successful run](https://github.com/reallakshman19/Common/actions/runs/37968469829), [DELP successful run](https://github.com/reallakshman19/Common/actions/runs/37968469849), and [Local frozen-tree failed run](https://github.com/reallakshman19/Common/actions/runs/37968470110). The old source commits and source migration were read back in the new repo; former issue/PR metadata stayed at the old URLs.

**Not established:** actual original Agent A task-start for the historical experiments; any authenticated independent Runner B; real read-denial probe results; actual Stage1A/B engineering artifact or final freeze; controlled Stage2 admission; native active-hand over; exclusive Writer grant; live deployment; production-browser journey; time or performance improvement; working tree cleanliness on anyone else's machine; and Owner approval of the frozen V3.2 source exception.

**Report status:** source-reviewed technical handover *candidate for Owner/controller*, not a native accepted transaction, independent review, or Stage2 release. Reverify exact branch HEAD/CI after this Markdown report is committed.