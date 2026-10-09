# R14 U1–U5 ↔ Runner continuity — source-level interface reconciliation

**Governance:** [new Common #1](https://github.com/reallakshman19/Common/issues/1). **Canonical code:** `reallakshman19/Common`, `main@d60c36605e988dcc160647421973f170fd87e0eb`. **R14 actual stacked source reviewed:** `892cb0d1eaccfe467b7db2c5f13b9df40b1ff043` (historical [old PR #897](https://github.com/reallaksh19/Common/pull/897)). **Continuity work:** `docs/relay-890-continuity-md-v1`. This is a **reviewer-only Markdown analysis**, not Stage 1 input, accepted WP0 review, runtime test or rollout.

## Source inventory and verdicts

| R14 contract at exact stacked head | Source verified / observed interface | Continuity rule and remaining gate |
| --- | --- | --- |
| U1 typed reference identities | `skills/engineering-relay-v1/schemas/lifecycle-v35/lifecycle-identity-v1.schema.json` blob `b804e1d02a277692bb8ddf3b234f4a6b0bd5a917` and `identity_contract_v1.py` blob `8bf1f9803175cd2c962b97615dff51c88d621c5d`. Typed PLAN_GRAPH_REVISION, SESSION_SOURCE_COMMIT, CODE_CANDIDATE_HEAD; UNKNOWN accepted. | Keep graph approval revision, original A start/session SHA, candidate PR base/head, test-head and historical research cutoff **distinct**. Caller-reference identity is not GitHub attestation or Owner authorization. |
| U2 Owner/session history | `owner_session_contract_v1.py` blob `a6c951cf47e7146edf36292cc4ddc4ae3ea6cb42`, schema blob `13cf695180ecb403947074a333a6046abfa210da`. _mirror_url demands an exact same-repo GitHub issue/PR comment URL. START_CLAIMED/STOP_CLAIMED/HANDOVER_OFFERED/RUNNER_PREPARED are actor observations, not verified lease/owner. | Don't encode historical old-repo comments as new-repo authenticated Owner events. Preserve immutable old URL, explicitly grade unverified mirror and keep new-repo source unknown until actual provider/migration proof. |
| U3 evidence/reviewer claims | `evidence_review_contract_v1.py` blob `4fe0c2513aedd8cf58e7a3acaee3f820c96cde9b`; schema blob `c8c5d9c0ce521ff889a10a27b8dd1f6e0180e2df`. Exact `repo#issue`, `repo#PR`, candidate/base and tested head binding, structural native DELP validation when installed; reviewer claim different label is not independent reviewer admission. | Handover records exact **provider repository + PR/issue identity**, tests at exact head, fixture/golden provenance. Do not promote CLAIМED_ACCEPTED or test PASS claims to admitted evidence. |
| U4 conformance | `lifecycle-conformance-v1.mjs` blob `15189f04b1d454171afc332d8ee195306a51160a`. Computes matching canonical digests, source authenticity NOT_CHECKED, reviewer/Owner not granted, exclusive lease NOT_PROVEN. | A digest protects bytes, not provider source, original chat, independent B isolation or write privilege. |
| U5 diagnostic R12 → DELP | `diagnostic_delp_bridge_v1.py` blob `614b31db833aca58e5b7f1bdc62404bf312add51`; `r12-to-delp-readonly-v1.mjs` blob `c05c6e079d173e02e442f89cfd4a24cf1eccaa2a`. Native DELP called with quarantined serialized source; no publishable snapshot, writer OFF. | No second DELP projector/status logic in Runner Markdown; diagnostic is NOT a handover or evidence-admission event. |

## Repository transition: five negative cases

| Case | Current source/provider finding | Required fail-closed judgment |
| --- | --- | --- |
| R01 — identical code commit across two repos | `main@d60c366...` and Runner branch `09ff375...` exist at new and old repo identities | Same SHA does **not** transfer Issue/PR identity, Owner history, reviews, Actions, ACL or writer session. |
| R02 — old Issue/PR URL silently rewritten | Old Common #890/#893 and R14 #891/#894/#895/#896/#897 are **not** new Common same-number GitHub objects | `HOLD_REPOSITORY_IDENTITY`; maintain exact historical provenance and explicit external mapping. |
| R03 — R14 U2 historical mirror assigned new programme.repository | `_mirror_url` requires same owner/repo as programme identity | Source-grade mismatch: HOLD; cannot fix by replacing URL text or reusing old comment ID. |
| R04 — R14 U3 old PR number/head used with new repo | U3 validates exact repo#issue / repo#PR / tested head but **doesn't GET provider objects** | `CALLER_REFERENCED_UNATTESTED`; no reviewer, E or DELP publication qualification. |
| R05 — handover STOP_CLAIMED treated as custody transfer | U2 actor-labelled STOP_CLAIMED is not credential fencing; Stage1 B MD freeze likewise not credential proof | `NOT_PROVEN_EXCLUSIVE` and writer HOLD until actual old-token denial + Local authority. |

## Scope and compatibility

**Nonoverlap:** R14 U1–U5 are new draft Python/Node/JSON *claim/diagnostic contracts*. Runner #893 is Markdown-only task-aware baseline-first thinking/dispatch/technical handover. These modify disjoint file paths, but both discuss Owner, session, repository, facts and custody; field semantics must agree before any source authority decision.

**Markdown modifications:** Existing `AUTHORITY_MAP.md`, `TEMPLATES/TECHNICAL_HANDOVER.md`, `TEMPLATES/STAGE2_RECONCILIATION.md`, `TEMPLATES/OWNER_DECISION.md` now explicitly require separate repository/graph/session/candidate/tested roles, historical old-repo reference, R14 reference-only grades and verified new-repo provider binding. These formats do not import or redefine R14 schema.

**Not qualified:** There are no R14 draft PR objects under new repository, no external Owner-approved migration mapping, no independent WP0 reviews, no full native R14 stacked test run by this agent, no clean Runner B trial, no Stage2 source-current reconciliation, no proven exclusive writer and no merge permission. Source branches retaining commits is insufficient.

## Next action

Owner/controller establishes how new-repo issues/PRs bind historical governance and whether the old archive remains the immutable source of Owner history. Only then choose a minimal *actual* provider-mapped proof using new repo issue/PR and a separate real Stage1 B. Do not alter R14 U1–U5 source, authorize the writer, merge drafts or publish positive DELP evidence via a Markdown report.

**Verdict:** `SOURCE_INTERFACES_RECONCILED_AS_REFS`; `REPOSITORY_LINEAGE_NOT_APPROVED`; `STAGE1_EXECUTION_NOT_RUN`; `R14_PRODUCTION_ADMISSION_HOLD`.
