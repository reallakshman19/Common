# Repository lineage, native Buddy namespace, and PR collision audit — V1

**Record kind:** RELAY_REPOSITORY_LINEAGE_REVIEW_V1 · **Governing issue:** [new Common #1](https://github.com/reallakshman19/Common/issues/1) · **Source verification:** GitHub provider reads 2026-10-09 · **Authority:** REVIEWER_ONLY, candidate Markdown, no Owner or writer approval. **Never provide this file as a clean Runner Stage 1 input.**

## 1. Repository identity: immutable code ≠ GitHub identity

| Observed object | Old repository `reallaksh19/Common` | New canonical repository `reallakshman19/Common` | Relationship and admissible meaning |
| --- | --- | --- | --- |
| Repository/provider | Separate repository with its own issues, PRs, comments, runs and permissions | New repository ID `1412133785`, created 2026-10-09; independent GitHub issue/PR namespace | **Different provider identities**, no automatic evidence/Owner transfer |
| `main` source | `d60c36605e988dcc160647421973f170fd87e0eb` | Exact same commit SHA at verification | **CODE_EQUIVALENT only**; no issue/PR/credential equivalence |
| Original Runner concept issue | [old #890](https://github.com/reallaksh19/Common/issues/890) (OPEN) | [new #1](https://github.com/reallakshman19/Common/issues/1) (OPEN) | **PURPOSE_CONTINUATION**, not the same issue ID or authenticated imported Owner event |
| Runner implementation PR | [old #893](https://github.com/reallaksh19/Common/pull/893), head `09ff3751560bb49098e69c9c79918626078c7564`, draft | [new #3](https://github.com/reallakshman19/Common/pull/3), branch `docs/relay-890-continuity-md-v1`, initial reviewed head `dfd8fd6eb3a5f791ec6416fbfcc28cb197df86c8`, draft | **SOURCE_BRANCH_CONTINUATION** with added R14 reconciliation; different PR numbers, reviews, checks |
| Native V3.2 Buddy development | [old #889](https://github.com/reallaksh19/Common/issues/889) and [old draft PR #892](https://github.com/reallaksh19/Common/pull/892) | [new draft PR #2](https://github.com/reallakshman19/Common/pull/2) at observed head `dc8203b11a5484ea8c530efc09ed5c2d43c9e3f3` | **RELATED_NEW_IMPLEMENTATION**, not an imported old PR or merge/review transfer |
| R14 governing architecture / execution | [old #864](https://github.com/reallaksh19/Common/issues/864), [#878](https://github.com/reallaksh19/Common/issues/878) | No corresponding new R14 governing issues confirmed in new repo provider listing at audit | **HISTORICAL_REFERENCES_ONLY**, no new-repo Owner approvals |
| R14 draft PR chain | [old #891](https://github.com/reallaksh19/Common/pull/891) → [#894](https://github.com/reallaksh19/Common/pull/894) → [#895](https://github.com/reallaksh19/Common/pull/895) → [#896](https://github.com/reallaksh19/Common/pull/896) → [#897](https://github.com/reallaksh19/Common/pull/897), unmerged | No new-repo R14 PRs confirmed; Git source for chain available at `892cb0d1eaccfe467b7db2c5f13b9df40b1ff043` | **CODE_AVAILABLE, PROVIDER_PR_UNMAPPED**; tests/reviews not carried |

**Absolute rule:** No replacement of the old repository slug in a historical URL may create “new Owner provenance” or “new PR evidence.” The only safe claim is which real provider object was fetched, which Git blob/commit was read, and the relationship class above. Source SHA equality provides content lineage, not migration authentication.

## 2. Native PR #2 vs Markdown PR #3 — actual overlap and merge rule

Exact heads inspected: [new PR #2](https://github.com/reallakshman19/Common/pull/2) `dc8203b11a5484ea8c530efc09ed5c2d43c9e3f3`; [new PR #3](https://github.com/reallakshman19/Common/pull/3) `dfd8fd6eb3a5f791ec6416fbfcc28cb197df86c8`. Both based on `main@d60c366`. The provider PR changed-file lists overlap in **21 Markdown paths** under `relay/CONTINUITY/`.

Exact Git tree blob comparison for those 21 shared files: **17 byte-identical; 4 intentionally different** in PR #3:

| Shared path differing at inspected heads | PR #2 blob (imported old continuity) | PR #3 blob (R14-mapped wording) | Required merge disposition |
| --- | --- | --- | --- |
| `relay/CONTINUITY/AUTHORITY_MAP.md` | `cd1f47848c80e47088e8aaccdd88f6dd1121378a` | `d148660873f913864260b353b06253184e33b6f7` | Retain R14 source role / repository split warning |
| `relay/CONTINUITY/TEMPLATES/TECHNICAL_HANDOVER.md` | `59fe00d32dc1723efebb16c4612b66aefe7193e3` | `6e52ddc04f7e2e0af43cf27400533b10ab66182a` | Retain exact graph/session/candidate/old-new repo fields |
| `relay/CONTINUITY/TEMPLATES/STAGE2_RECONCILIATION.md` | `1175187a9300cc7b1107e43da5d89e7b12970d26` | `bf51060318734962eba0b7823f9a365cad0d5c0a` | Retain four-view source-current R14 claims / new-repo binding |
| `relay/CONTINUITY/TEMPLATES/OWNER_DECISION.md` | `9b84d165f6d9e16767e068909c0cffe16bb0a48c` | `b820a0868d318c4b011c96af7f22e3ece0c36e5f` | Retain old/new provider evidence split and no-authority claim |

**Commit/merge safety:** These are *two independent draft branches*, not a qualified stacked chain. Do not merge both blindly or accept a resolver that silently discards one party's contract. Qualify PR #2 native transaction semantics first; integrate exactly the four divergent fields after explicit source/Owner review. This ledger proposes an order, **not** merge permission.

## 3. Concrete native Buddy contract (candidate in PR #2) and its migration hazard

Source at `dc8203b...`: `skills/engineering-pr-delivery-v3.2/scripts/relay_tx.py` `publish_buddy_markdown` lines 1300–1357, and `transactionlib.py` command target/stage rules.

- **Proposed canonical issued message path:** `relay/CONTINUITY/episodes/ISSUE-<issue>/messages/TX.<issue>.<serial>-<STAGE>.md`. It is written by existing Relay `PUBLISH_BUDDY_MARKDOWN` transaction with a commit/digest receipt; no new YAML state shadow and no source-writer grant.
- **Observed native stages:** `READINESS`, `STAGE1_INTAKE`, `DISPATCH_REQUEST`, `DISPATCH_OBSERVATION`, `STAGE1_BASELINE`, `STAGE1_PLAN`, `STAGE1_FREEZE_CANDIDATE`. The latter is merely a **candidate** to externally freeze; it is not an independent B result or Stage2 admission.
- **Migration-specific P0 gap:** `publish_buddy_markdown(root, issue_number, tx_id, stage, actor, markdown)` accepts a **positive numeric issue number** and matches `TX.<issue>.<serial>` but does **not** accept, provider-fetch, or validate the `owner/repo` identity. In the new repository, an **old** issue number could be reused to produce a syntactically valid message in the new repo's `ISSUE-<number>` directory without proof that its governing issue actually exists *here*. A transaction receipt and digest would then prove only the local write, not the correct provider issue binding.
- **Required native negative test / Owner decision:** On canonical repo `reallakshman19/Common`, attempt an issue number that exists only in old `reallaksh19/Common` with a plausible `TX.<number>.<serial>`. Until there is a verified current-repo issue/approved lineage binding, enforce a **fail-closed HOLD** at dispatch/admission. If the native writer intentionally remains provider-blind, require an **external provider-verified issue-binding receipt** as a distinct gate; do not invent native provider access from local validation.

**Do not equate directory names:** Old static research samples `relay/CONTINUITY/episodes/CORE1B_GOLDENS_RUNNER_20261009/` are **not canonical native transaction messages** in PR #2. Keep as immutable historical fixtures; if accepted, active messages must use the *approved* `ISSUE-<new-repo issue>/messages/TX...-STAGE.md` path, not a second episode namespace. If PR #2 is not yet approved/merged, even this path is a **candidate**, not an active authority.

## 4. Semantic compatibility matrix — Runner thinking vs native transport

| Native candidate stage | Bounded V3.5 reasoning duty | Evidence required and prohibited upgrade |
| --- | --- | --- |
| READINESS | A's early advisory, actual usable-life grade | Not B started or progress % |
| STAGE1_INTAKE | Sanitized historical Original Owner WHAT/WHY + source closure | Agent A's current plan/risk/PR forbidden |
| DISPATCH_REQUEST | One external launcher assignment request | Stored request ≠ externally created B |
| DISPATCH_OBSERVATION | Actual controller-reported session/input gate | Textual actor claim ≠ independent tool/session denial |
| STAGE1_BASELINE | Fresh B's factual historical producer→consumer/output witness | Must precede options; cannot self-certify blindness |
| STAGE1_PLAN | **PROVISIONAL** original-problem hypotheses, options or NO_CHANGE | Not actionable current-head implementation plan/PLAN_UPDATE |
| STAGE1_FREEZE_CANDIDATE | Native transaction digest chain across prior Stage1 messages | **NOT** accepted external freeze, not Stage2 disclosure |
| Outside native Stage1 | Separate technical handover and Stage2 four-way reconciliation | Existing Relay/Local authorization; no writer grant |

## 5. Acceptance and failure oracles

- **L01 PASS (provider discovery only):** new issue #1, new PRs #2/#3 genuinely exist in `reallakshman19/Common`; old #889/#890 and #891–#897 are historical old repo objects.
- **L02 PASS (code hashes only):** new/old main share `d60c366`, former work branches and R14 stacked Git source available.
- **L03 PASS (conflict enumeration):** 21 shared Markdown files, 4 differing blobs at inspected heads. Changes to PR #2 or #3 require a fresh compare; do not assume this snapshot remains latest.
- **L04 FAIL-CLOSED pending live test:** Native publisher does not check current repository provider issue identity; possible old-number publication is **not qualified** under migration.
- **L05 NOT RUN:** actual independent B session, denied GitHub reads, output/freeze, current Stage2, and old-writer revocation.
- **L06 OWNER HOLD:** Native path selection, approved old→new issue lineage, R14 schema applicability and PR merge order not authorized by this reviewer record.

**Status:** `PROVIDER_OBJECTS_VERIFIED_AS_SEPARATE` · `PR_OVERLAP_21_BLOB_DIFFERENCES_4` · `NATIVE_ISSUE_BINDING_HOLD` · `STAGE1_NOT_EXECUTED` · `NO_MERGE_AUTHORITY`. This is a durable source-review message, not an attempt to issue new task credits.
