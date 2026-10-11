# R5 — live public historical source witness and native evidence parser boundary

**Date:** 2026-10-11, chat `6acb76ac`; Owner [Common #325](https://github.com/reallakshman19/Common/issues/325), governing [#289](https://github.com/reallakshman19/Common/issues/289), root #5 (AC0/8). **Plan:** [R5 `PLAN_UPDATE` comment 6110347359](https://github.com/reallakshman19/Common/issues/325#issuecomment-6110347359). **Purpose:** falsify real-source assumptions using read-only *public historical* GitHub. **Not:** authentic original private lab, Owner D07 adoption, new release, accepted E, native protected fix, live mutator or independently fenced successor.

## 1. Reconciled original goal and unchanged gates

The source-owned child #325's checked T01–T03 were only **unmerged read-only/pure publisher-plan engineering**. Original **T04** still requires protected native `owner/repo#PR` responsibility-core correction, approved/reviewed/base-resident frozen #316 grant and governed real GitHub publisher. Original **T05** still requires independently authenticated Owner original graph/source, positive `CHECKPOINT_FACTS_V1` issuer, effective required CI and qualified independent reviews, truly linked native DELP P/E/D/E, actual managed root+child+PR GET-readback, then C6 and independent A→B writer fencing. Root #5 AC0/8, V3.2 writer OFF, active V3.1/Local intact. Private original `reallaksh19/relay-v32-e2e-lab` remains **HTTP404** to current actor, not proof of deletion. #316 grant still unapproved and absent from actual main base manifest. #337 stacked #313 and #338 stacked #326 remain draft/unmerged.

## 2. Physical GET witnessed source: matching PUBLIC OLD repository only

Read original GitHub REST `GET /repos/reallaksh19/Common`, `GET /commits/main`, `GET /issues/{number}`, `GET /pulls/{number}` and `GET /issues/{leaf}/comments?per_page=100&page=1` (first and second passes on issue/PR and comment identity). Also read `.github/v32-evidence-spine/718-proposal-v2.json` twice by `main` plus by immutable commit SHA. These are real current public responses, not fake fixtures or a native production GET-authority certificate.

| Historical public identity | Real observed value |
| --- | --- |
| Repository `full_name`, numeric ID, default branch | **`reallaksh19/Common`**, **`1207996454`**, `main`; distinct from canonical new `reallakshman19/Common` ID **`1412133785`** |
| Beginning/ending public main commit SHA | **`d60c36605e988dcc160647421973f170fd87e0eb`** both observations |
| Graph pathname and exact Git blob | **`.github/v32-evidence-spine/718-proposal-v2.json`**; blob **`d35019b416cb3b573280e166027d3f65ba61f59c`**, `main` bytes equal immutable commit bytes; public graph source length 26,476 characters; graph declares `programme.repository=reallaksh19/Common`, `root=Common#718`, `base_ref=main` |
| Root/leaf issue GET numbers and states (both passes) | `#718 OPEN`, `#720 CLOSED`, `#724 CLOSED`, `#733 OPEN`, `#793 OPEN`; original titles and body present; states/identities stable in the bounded read window |
| Released graph leaf `primary_pr` refs | `Common#720→Common#722`, `Common#724→Common#728`, `Common#733→Common#740`, `Common#793→Common#800` |
| PR GET numbers / source repository IDs (both passes) | `#722/#728/#740/#800` all **CLOSED/MERGED**, `draft=false`, base ref `main`, both head+base numeric repo ID **1207996454**, all heads stable |
| PR exact heads (#722/#728/#740/#800) | `b3dfba3becf829d3a4e21d6eaa54983f05317b65`; `7ef9fbdd0c6f0f941fd573c1663c7a142fc41414`; **`d511fc0210ee823272f41c43621bc90bc290e739`**; `82ba85564d284f87cadfdedaba5d449cf3c7bc7f` |
| Four leaf issue comment GETs; first/second pass | `#720:7`, `#724:8`, `#733:20`, `#793:15` → **50 observed rows**. Each page length under 100, so no second page needed under REST `per_page=100`; all positive strict ascending GitHub integer IDs, author `user.login`, `author_association` and original comment body fields present; first/last IDs unchanged between passes. No original bodies replicated in durable report |

**Scope of two-pass stability:** Only specified returned REST fields, comment counts/id bounds and graph bytes/commit were compared. GitHub is not a global atomic snapshot. Public former Owner repo matching its old graph is **not** evidence of Owner D07-A original private release or a new `reallakshman19/Common` graph. The original private lab and full D01–D08 policy remain unverified.

## 3. Native-delivered evidence boundary — actual facts cannot be inferred from mentions

Checked the **exact source code** of native [`delp_projection_v32.py` at #326 head `6b138b63...`](https://github.com/reallakshman19/Common/blob/6b138b63d4347500a4fba2cad59f1fcfed0bfaf2/skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py), lines 851–872 and 4330–4360: `ledger_from_github` loops leaf issues and calls `extract_facts_blocks` for each comment. The native `_FENCE` requires a fenced YAML/plain document **starting with `CHECKPOINT_FACTS_V1:` on the first content line and closed with triple backticks**, not casual prose quoting that phrase.

A read-only parser-syntax check on all **50 current real public** comment bodies using the native `_FENCE` pattern's equivalent produced:

| Leaf | Comments | Bodies mentioning text `CHECKPOINT_FACTS_V1` | Actual native-compatible fenced blocks found |
| --- | ---: | ---: | ---: |
| `Common#720` | 7 | 0 | **0** |
| `Common#724` | 8 | 0 | **0** |
| `Common#733` | 20 | 12 | **0** |
| `Common#793` | 15 | 0 | **0** |
| **Total** | **50** | **12** | **0** |

**Falsifiable determination:** The mere **12 mentions** must **not** be admitted as twelve facts. Under native `extract_facts_blocks` regex, these observed bodies yield **zero checkpoint fact blocks**; absent any other source, this public mirror cannot provide a *positive eligible E* in the selected leaf. This conclusion is based on direct text/regex source comparison; **a full authenticated native `ledger_from_github/project` run was NOT executed** by this review and is not falsely labeled PASS. A future permitted native run must verify graph schema, completeness, fact author policy and actual E rather than accepting this derivation as release evidence.

## 4. Real observed selected material and correct negative inference

Selected live public historical graph leaf `Common#733` maps to actual PR [#740](https://github.com/reallaksh19/Common/pull/740), `state=CLOSED, merged=true, draft=false`, original head **`d511fc0210ee823272f41c43621bc90bc290e739`**; source base `main`. Exact GitHub compare `main...d511fc0210ee823272f41c43621bc90bc290e739` responded **`status=behind, ahead_by=0, behind_by=453`** at current public main. Original historical PR base SHA `da79e02c9fded16aaed48886a253aad06ee51bf7` compared to PR head answered `status=diverged, ahead_by=38, behind_by=45`. These are actual Git ancestry observations. **A merged historical PR naturally being behind current main is NOT by itself evidence of stale/forged `CHECKPOINT_FACTS`, unsuccessful merge or qualified E**; maintain separate material head/currentness/Owner evidence boundaries.

All four graph leaves declare a `primary_pr`; native `observe_github` on such nodes calls `get_pull`, not `compare`. Therefore the R4 `BoundNativeReadOnlyGitHubProvider.compare` path is correctly an adapter capability for **branch-only graph leaves**, **not exercised by this public historical graph**. This public witness says nothing about whether branch-only selection or original lab access works.

## 5. Decision and handover-grade stop

**R5-N01 = DONE_READ_ONLY_PUBLIC_HISTORICAL_GET_CENSUS**: real source identity, graph/branch pin and complete bounded public comment-page census observed twice, no actual writing/issuer claim. **R5-N02 = DONE_FAIL_CLOSED_NATIVE_FENCE_AND_MATERIAL_GRADE**: 12 mentions ≠ 0 properly fenced checkpoint blocks, PR #740 real ancestry and exact head verified; no positive E or independent current private source. This is **historical public diagnostic** only, **NOT original Owner-approved vertical**, and does not justify a new synthetic suite.

**Original T04/T05 remain OPEN**. The original approved graph and trusted positive issuer plus private read-only actor still depend on `OWNER:D07 / EXTERNAL:PRIVATE_LAB_ACCESS`; native fully-qualified `owner/repo#PR` protected change on `OWNER:AMEND-V32-289-PRREF-017` reviewed/base-resident exact grant; required checks, two independent qualified reviewers, native live publisher and real B remain parent #289 D01–D08. Neither same-repo old source identity nor direct public GET grants authority to mutate any issue/PR. **HOLD until those actual gates; root #5 AC0/8; release=HOLD; handover=no.**
