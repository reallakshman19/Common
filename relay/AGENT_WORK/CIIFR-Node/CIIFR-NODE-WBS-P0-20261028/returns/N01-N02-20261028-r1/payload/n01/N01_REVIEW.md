# N-01 read-only review return — CIIFR-Node

Task: `CIIFR-NODE-N01-PR226-R0-IR`, issue [#228](https://github.com/reallakshman19/XML_Compare_Utilities/issues/228), WBS [#227](https://github.com/reallakshman19/XML_Compare_Utilities/issues/227). Date: 2026-10-28.

**Verdict: GATE_R0 FAIL / retain DRAFT-HOLD.** The specified native command passes and the earlier Nodal crash is fixed, but an approved Normal plan is cleared by a Property Transfer visit. Contrary input probes also expose reader-contract gaps. This is a code-only review, not original-model, Windows, browser, vendor, writer, merge or release acceptance.

## Exact subject and custody

- Repository: `reallakshman19/XML_Compare_Utilities`.
- Head observed before and after review: `b2b695f66fc8dfc907f2b9a493b39bd4d4109570`.
- Base: `fd86b21aa9dcbfbbe4f8a1d26133b7e9779448be`.
- Historical failed head independently retrieved: `e2d2e4893713aa56bfbb5a5f6fd8d7ff57b16970`.
- PR remained open/draft. No product files, tests, commits, PR metadata, comments, deployments or writers were changed.
- I independently retrieved the immutable GitHub tree and exact candidate bytes through the GitHub connector. Materialized file lengths and Git blob SHA-1 identities were checked; SHA-256 values are in `evidence/candidate-manifest.json`. Base/old-head files were independently fetched when their blobs differed. Unchanged retrieved blobs were reused only after matching the pinned revision's tree identity.
- Public synthetic SOURCE and TARGET0 were independently fetched from Common commit `56dbc3a0af137c433ffb5fec48316fa2022d075c`, task path `relay/AGENT_WORK/CIIFR-Node/CIIFR-NODE-WBS-P0-20261028/payload/`. Both are 8,276 bytes. SOURCE blob `7d00c13f5c5906a9bb2dba53287f133c8db06358`, SHA-256 `c8de516c54767c7cf7d5239d404810be891ed3d56ec2111db3dc4c2b07dcdb0b`; TARGET0 blob `dddf157895571802973b71904fbad0a679a7e271`, SHA-256 `0bbc3b0a8b7b1e73d655d0a0ffc267e6a698dec5ff66763c468cdc835cc19661`.
- Governing sources independently read: issue #228, WBS #227 and its comments, exact-head AGENTS.md (blob `a39570bf6cdd1a66fb3db0aeed09e111734c5bbd`), candidate concept/plan, and Common `independent-review/SKILL.md`, `references/INDEPENDENCE.md`, `ARTIFACT_RELAY.md` at `a353371d5f1ea3d6df8214165ecdecebda9df41b`. The Common requirements matrix/catalog are author-exposed projections; their claims were not treated as independent execution.
- This output was staged locally for the lead to place in the governed Common return. At this participant's handoff it is **LOCAL_ONLY / NOT_TRANSFERRED**; no successful relay publication or receiver receipt is claimed here. The lead must append its actual immutable return locator/readback.

## Independence and environment

I am the separate `n01_native_review` agent, with no contribution to the candidate. This is a non-contributor review at the agent-work level, **not evidence of a distinct human or account principal**. The authenticated service principal is shared/unknown; no host isolation was established. I used the same shared Linux workspace and runtime as the lead, confined work to `n01-review/`, and did not read prior `pr226-review*` contents as an oracle. An initial file inventory exposed those filenames only.

Exposure includes the assignment's reported old failure/repair, author tests, candidate source, author-exposed public synthetic fixtures/catalog, shared WBS/specification, and later lead messages. I derived contrary expectations from the positive numeric-node, pointer-bound and tab-isolation contracts and then executed my own mutations. Author-test replay adds execution evidence without becoming a blind or vendor-independent engineering oracle. The lead subsequently reported its own fixture audit and suggested interpretation limits; those messages are exposure, not substituted review evidence.

Actual host: Linux 6.18.55 x86_64, glibc 2.39; Node v24.22.1. Windows was not available. No chromium, chromium-browser, google-chrome or firefox executable was found on PATH; checked common Chromium/Chrome locations also absent. No actual browser was launched or package/environment setup attempted. Controlled DOM results below are simulations of DOM events executing actual candidate modules, not browser rendering/file-dialog evidence.

## Findings

**F1 — P1: new Property Transfer navigation clears an approved Normal plan.** In `tabs/cii-workspace/cii-fnr-vnext/ui/app.js:29`, `state()` falls back to Normal for non-work tabs. The shared tab handler at **line 433** calls `invalidate(state())` on both sides of every transition; `invalidate` at **lines 32–35** clears the plan, decisions, validation and applied result. The new Property tab is registered at line 15 and therefore enters that path.

Reproduction: load the committed synthetic Normal demo, change OLD-A→NEW-A, Generate and Approve All; Validate is enabled with one claim. Click Property Transfer, then Normal. Observed before `{claims:1,validateDisabled:false}`, after `{claims:0,validateDisabled:true}`. The generic invalidation policy is inherited for older tabs; extending it to this new independent tab contradicts WBS preservation/no-cross-tab-state-loss. The new UI regression only snapshots the Nodal Preview button before any loaded/approved plan (test lines 14/28), so its PASS cannot cover this case. **Required action:** isolate new-tab navigation/intake from existing state, preserving the existing policy for older operations.

**F2 — P2: negative ELEMENTS endpoint accepted into the R0 node inventory.** Changing SOURCE element #1 FROM to -400 succeeds and creates a negative-node incidence. `cii-index.js:85–94` trusts `parseCii` endpoints; the inherited parser at `ui/physical.js:58–60` checks integer representation, not the new inspector's positive-node domain. R0's own selector rejects nonpositive nodes at `cii-index.js:184–188`, so accepted inventory contains an unreachable invalid logical node. This contradicts the negative-node fixture requirement. The added tests at R0-test lines 112–121 check restraint-node/CNode negatives only. **Required action:** reject negative ELEMENTS endpoints for the inspector, with an explicit policy for any legal zero sentinel; do not silently change the legacy parser's semantics.

**F3 — P2 contract gap: invalid nonqualified-family pointer is accepted without a family-specific HOLD.** Setting element #1 BEND pointer to 999 while CONTROL.BEND=0 is accepted. All 15 pointers are parsed at `cii-index.js:58–61`, but bounds/ownership checks at **lines 95–107** iterate only RIGID, RESTRANT, DISPLMNT and FORCMNT, from `ROWS` at line 9. Broad N-R11 and concept pointer-bound language exceeds what was checked. This observation does **not** qualify BEND semantics. **Required action:** reject impossible pointers or explicitly diagnose unsupported/unqualified families and narrow the public validity claim.

**F4 — unresolved semantic limit: nonempty dormant restraint residue is silently omitted.** A previously empty slot with node/type/CNode=0 and stiffness=123 is accepted and omitted by `cii-index.js:135–138`. Only type/CNode are examined when node is zero. This is an observed gap against the WBS's broad “zero-node nonempty restraint slot” negative; actual V14 legality of dormant numeric fields was **not independently established**. Do not call it vendor-confirmed corrupt data. Resolve the vendor rule, then reject or expose the residue/unsupported qualification instead of treating the slot as exhaustively empty.

Highest surviving wrong case in the supplied green suite: F1, an engineer's approved Normal plan disappears merely by visiting the new inspector. For the parser, a negative endpoint or a bad unsupported-family pointer still receives `readOnly:true` and the general ready status. “Read only” is not proof of complete structural validity.

## Executed evidence

Commands ran from the appropriate exact candidate/base/old directory unless stated otherwise. Full outputs accompany this report.

| Check / command | Observed result | Witness |
|---|---|---|
| `node --test tests/cii-fnr-vnext-property-transfer-r0.test.mjs tests/cii-fnr-vnext-property-transfer-ui-regression.test.mjs tests/cii-fnr-vnext-nodal-ui.test.mjs` | PASS 17/17, including 14 R0 tests | `evidence/native-three.tap` |
| `node --test tests/cii-fnr-vnext-*.test.mjs` — head | 110 PASS / 1 FAIL (111 total) | `evidence/vnext-all-complete.tap` |
| Same glob — base | 94 PASS / 1 FAIL (95 total) | `evidence/base-vnext-all-complete.tap` |
| Common failure | `branch identifier mismatch gives zero replacements, no prefix matching`, branch-scope test line 85: actual 1, expected 0 on both revisions | Logs above; inherited failure, not attributed to PR226 |
| Nodal original test — base / historical head / repair | PASS 1/1; historical head FAIL with null `addEventListener` at old panel.js:85; repaired head PASS | `evidence/base-nodal.tap`, `old-nodal.tap`, `native-three.tap` |
| Pinned-base focused DOM with actual repaired app | PASS Nodal startup with no new panel | Executed separately; supported also by historical-helper reproduction |
| `node --test tests/cii-workspace-geometry-authority.test.js tests/cii-workspace-method-c-original-geometry.test.js` — head and base | PASS 9/9 on each | `geometry-bounded.tap`, `base-geometry-bounded.tap` |
| CIIFR_GEO host suite | Its three tests pass within both complete VNext runs; URL prefixes/lazy frame preservation/Normal switching policy | Complete VNext logs |
| `node probe-r0.mjs` | 23 expected checks PASS; 3 expected rejections FAIL (negative endpoint, bad BEND pointer, dormant stiffness). Exit 1 deliberately preserves those observations | `evidence/probe-r0.log`, `probe-r0.mjs` |
| Controlled DOM integration in that script | SOURCE/TARGET intake; exact pairs; A/B selection clearing; stale async file completion ignored; approved Nodal state survives Property visit plus its independent TARGET0 intake | `probe-r0.log` |
| Mirrors | Six changed source/served pairs byte-equal; tree blobs equal | Manifest and table below |
| No new property writer | Inspected all four new JS modules: no writer import, CII mutation/export API or TARGET1 construction; explicit `writeEligible:false` and `canWrite:false`; original input equality test passes | Candidate source, required tests, own read-only observations |

Broader `cii-workspace-geometry-discrepancy-review.test.js` was **NOT_RUN technically**: attempted harness exited on missing local `Benchmark/T.CII` before testing behavior. The Contents API returned its identity with empty content (large-file behavior); a separate blob read returned text, but the full bridge dependency/fixture materialization was not completed. A mixed exploratory log records the missing input. No candidate FAIL/PASS is inferred from that missing-input exit. The complete repository test command, browser upload/rendering, Windows and licensed CAESAR II were not run.

The author R0 fixture generator uses the real first CONTROL field as NUMELT and material IDs at six-per-row MISCEL_1 positions. Its expected numeric values are literals rather than production-generated expected outputs, but its fixture layout shares implementation assumptions. The 14 tests do not exhaust endpoint signs, every family pointer, full Tag/GUID content or retained approvals. I added the independent IZUP=1 positive and deliberate count corruption, so “valid both flags” and fail-closed count behavior were actually exercised. Ownership observations preserve two incidents at shared node 500, distinct pressures 30/20, a single rigid owner, and restraint slot 1; no slot→DOF or applied-force→reaction claim is made. Vectors, cases, effective T, units, remaining MISC content and vendor semantics remain unqualified.

## Source/served identity

Paths below are under `tabs/cii-workspace/cii-fnr-vnext/ui/` and the matching `docs/` prefix. Equality is source-file evidence, not a deployed browser readback.

| Relative file | Git blob (both copies) |
|---|---|
| app.js | `2e63ce830057bce61f9f5f546d19657eeed05814` |
| property-transfer/cii-index.js | `c06de73caddd5379f4dd8cbbf79d52584f112258` |
| property-transfer/element.js | `853352955b657853dfa8855eb566c97df67676f0` |
| property-transfer/node.js | `35109c593474b191178918d2d6f2a16c6d710571` |
| property-transfer/panel.js | `79121795d426c2a8de14d8dd30c1a231e06567b0` |
| property-transfer/style.css | `d4c4980e1aad04b313bd3734b390ac1af3139ce3` |

## Gate return

PASS statements are bounded by their witness. Independent author/account identity, an unexecuted platform or unknown engineering semantics are not upgraded by a green Node result.

| Gate | Verdict | Bounded claim and plausible unchecked/wrong case |
|---|---|---|
| EXACT_HEAD | PASS | Same pinned head/base observed twice; does not cover later commits. |
| IND_INDEPENDENCE | PASS (bounded) | Non-contributor agent obtained its own bytes and ran probes; distinct human/account/isolated host UNKNOWN, fixture/author-test oracle exposed. |
| NATIVE_TEST | FAIL | Required command 17/17 passes; full affected VNext set still has one inherited base failure. Windows NOT_RUN; individual tests do not prove full tab preservation. |
| LEGACY_NODAL | PASS (bounded) | Old crash reproduced, base and repair pass, base focused DOM tolerated; actual browser-only behavior can survive mock DOM checks. |
| GEOMETRY | NOT_RUN (complete gate) | Bounded 9/9 base/head plus CIIFR_GEO host tests pass; broader discrepancy suite not executed with complete inputs. |
| BROWSER | NOT_RUN | No actual executable found; file dialogs, rendered layout and real browser event semantics untested. |
| ORIGINAL | NOT_RUN / NOT_RECEIVED | No protected original was supplied; original hashes/aggregates in WBS are reported-only and depend on N-02. |
| SOURCE_SERVED | PASS | Six exact source pairs match; stale deployment/cache remains possible. |
| WRITER_NONE | PASS (bounded) | New property code provides no writer/TARGET1; existing Normal/Nodal writers remain existing unrelated code. Future external integration is not covered. |
| GATE_R0 | FAIL | F1 and F2 contradict current R0 isolation/domain requirements; F3/F4 require explicit scope/semantic reconciliation. No original/browser/Windows/full-Geometry completion inferred. |

**EXACT_NEXT_ACTION:** Lead returns this unchanged scoped verdict to #228/#227 through governed Common custody; builder, under separate authority, fixes F1/F2 and resolves F3/F4 contract wording/behavior. Re-review the exact new head, rerun affected suites, then obtain the missing Windows/browser and protected-original receipts through their assigned work. No writer, merge or release promotion follows from this return.

