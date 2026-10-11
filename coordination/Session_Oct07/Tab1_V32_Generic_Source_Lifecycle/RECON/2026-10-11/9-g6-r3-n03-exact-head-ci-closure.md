# R3-N03 — exact-head candidate tests, applicability and original-goal reconciliation

**Owner issue:** [#325](https://github.com/reallakshman19/Common/issues/325); [R3 plan 6109161373](https://github.com/reallakshman19/Common/issues/325#issuecomment-6109161373). **Date:** 2026-10-11; **chat:** `6acb76ac`. **Candidate:** [stacked draft PR #337](https://github.com/reallakshman19/Common/pull/337), immutable tested head **`8882aab2965e8beed3fbb641406bf3b0d1463b98`**, base **`690dd1565bfb4c15067528a51c7146fc0f75faaf2`** from draft #313, branch `feature/tab1-g6-r3-capture-surface-20261011`. GitHub metadata reread confirms **OPEN/DRAFT/UNMERGED**. Source candidate is not the assessed inherited #326 `6b138b63...` or the moving main. This is technical evidence, **not** current Owner-gated approval.

## 1. Changed-source and scope guard

GitHub PR #337 changed-file list returned EXACTLY:
- `relay/RECOVERY/V32_289_PW04_GENERIC_PR_SOURCE_20261010/v32_capture_current_source.py`, source blob **`a4c3d5f351703ba1477c6b799632c8c5d3007de2`**
- `relay/RECOVERY/V32_289_PW04_GENERIC_PR_SOURCE_20261010/tests/test_current_source_capture.py`, source blob **`e79e9cabc7312a091a1fc878d29dabe5c052b5e1`**

No protected `skills/engineering-pr-delivery-v3.2/**` paths changed, no `relay/STATE.yaml` or Local protocol stack change, no production GitHub workflow or native writer changed. Local frozen-tree guard **actually executed** on exact candidate workflow [38140657233](https://github.com/reallakshman19/Common/actions/runs/38140657233) and succeeded. Main `frozen-v32-amendments.yaml` at this recheck still has Git blob `ffe93467d8e75beebb6889f295205a8ba61bf620`, no `AMEND-V32-289-PRREF-017`. Draft #316 remains `owner_authorized:false` unmerged; this candidate deliberately avoids that gate.

**Intended change:** #313 original GET-only capture validates and retains real provider `issue.number/state`, `PR.draft` with safe typed HOLD on absent/bad metadata; original graph/raw Git-blob, repo numeric ID, head/base, human issue/PR text, finite comments, 0600 private storage and native in-memory shadow unchanged. Eight new focused fixture cases, two-pass drift tests and original suites.

## 2. Exact-head hosted Actions and actual job-step applicability

| Workflow at exact SHA `8882aab...` | Run / inspected job result | Real executable coverage |
| --- | --- | --- |
| Dedicated **V3.2 PW04 generic PR source binding (read only)** | [#38140657232](https://github.com/reallakshman19/Common/actions/runs/38140657232) SUCCESS, jobs **114473673361** (Python3.11), **114473673422** (3.12), **114473673293** (3.13), each job step `Confirm no mutation and run source contract tests` **SUCCESS**. Independently fetched logs. | **112/112 actual named tests RUN and PASS per Python interpreter** (previous 104 + new eight) => **336/336 named hosted executions**, with no Owner lab. |
| **Local PR Delivery v1.1 integration** | [#38140657233](https://github.com/reallakshman19/Common/actions/runs/38140657233) SUCCESS, job **114473673246**. | `Compile integration runtime`, `Validate stack manifests`, `Run activation adversarial suite`, `Replay live Common selector conflict`, `Frozen-tree guard tests`, `Verify frozen V3.2 tree unchanged` and integrated coordinator checks all **RUN/SUCCESS**. |
| **V3.1 foundation** | [#38140657239](https://github.com/reallakshman19/Common/actions/runs/38140657239) SUCCESS, job **114473673236**, `Run V3.1 foundation tests` **RUN/SUCCESS**; raw log `Ran 275 tests in 53.527s`. | **275/275 named V3.1 tests RUN and PASS** on #337 exact source, not the older #326 historical failed head. |
| Dedicated **V3.2 native continuity** | [#38140657238](https://github.com/reallakshman19/Common/actions/runs/38140657238) workflow SUCCESS, job **114473673232**. | `Detect V3.2 path relevance` ran and said `V3.2 scope not applicable`; actual native `Run V3.2 continuity regressions`, audited reality, custody/handover and parity steps **SKIPPED**. **DO NOT count native V3.2 tests as PASS.** |
| Dedicated **DELP** | [#38140657296](https://github.com/reallakshman19/Common/actions/runs/38140657296) workflow SUCCESS, job **114473673287**. | `Detect DELP path relevance` ran and said `DELP scope not applicable`; actual `Run DELP regressions`, schemas/continuity native checks **SKIPPED**. **DO NOT count DELP regressions as PASS.** |

GitHub commit checks at the exact source SHA included **ten+** check entries: three dedicated PW04 success, Local success, V3.1 success, V3.2/DELP workflows with skipped native steps, plus separately SKIPPED `audit-readback` and `trusted-reconcile` events; do not equate status-aggregator/readback skip with required policy. Current branch protection GET 403 `Resource not accessible by integration` and accessible rulesets `[]`, so effective required checks **UNKNOWN**. Formal GitHub review submissions for draft #337 = **0**; not certified by two independent reviewer principals. GitHub Actions workflow success is scoped test evidence, **not** mandatory checks/adopted Owner/source authorization.

**No local shell suites were run from current chat** because test output comes from hosted GitHub job logs; no private original lab or production publisher was executed. No source SHA after `8882aab...` is allowed to inherit these results.

## 3. R3 task accounting vs original actual acceptance

| Accounting line | Correct conclusion |
| --- | --- |
| Stage2 completed `S2-N01/S2-N02` | 2/2 analysis/doc-only; not original product |
| R3 `N01` | Actual #313-stack source metadata completeness change and focused hosted tests DONE on draft #337; no merge/release |
| R3 `N02` | Ten real-public GET operations and one pinned historical graph source inspection, all public issue/PR field metadata stable inside read window, [source canary](8-g6-r3-n02-public-provider-canary.md); real current Owner graph absent, so `PUBLIC_GET_SURFACE_COHERENT_UNQUALIFIED` |
| R3 `N03` | This exact-head hosted/job-step applicability and frozen-path/reviewer policy source closure DONE |
| **Original #325 `V32-GEN-T04`** | **OPEN**. Native `source_bound_responsibility_core` still refuses correct full `owner/repo#PR`; protected grant #316 absent/disabled. Scoped true generic native external publisher and qualified independent review remain open |
| **Original #325 `V32-GEN-T05`** | **OPEN**. Authenticated original Owner/lab source 404 to actor, true positive E/required check/reviewer policy, live root/leaf/PR body+title readback, genuine C6/B, Owner release unproven |
| **Root #5 Owner AC1–AC8** | **AC0/8**, unchanged. `relay/STATE.yaml` V3.1 and Local `LOCAL_V1_1_V35` active, V3.2 writer OFF |

**Outcome:** R3 three NOW tasks have useful **bounded source/candidate and current public source verification** but **do not complete original physical vertical**. PR #337 remains DRAFT/STACKED and must not be merged/rebased or treated as a release without separate review/Owner permissions. Older #313 snapshots still omit newly captured fields; no provider-complete #326 T02 adapter or original source access was implemented. The parent #289 holds B2-N06 authentic original lab + D07/external access, B2-N07 native full-ref approved base-resident amendment, B2-N08 evidence/review/policy, B2-N09 real publisher, B2-N10 independent B.

**Future non-Owner engineering:** A small additional compatible unprotected source transport adapter might be feasible, but don't create a third transport or perform invasive speculative architecture without real input. The only currently verified unavoidable blockers to original T04/T05 remain genuine Owner D07/source lab and frozen grant, then independent evidence/reviewer/CI/write/custody. If no further authorized scope, **stop at coherent tested draft candidate and decision gate**; no repeat extra tests solely to inflate a 3/3 counter. **release=HOLD, handover=no, tests=PW04_336/336+V31_275/275; V32_NATIVE=SKIPPED; DELP_NATIVE=SKIPPED**.
