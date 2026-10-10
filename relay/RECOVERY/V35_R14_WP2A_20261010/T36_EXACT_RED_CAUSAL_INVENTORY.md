# T36 — Pinned original full WP2-A RED baseline and causal inventory

**Engineering scope:** #294 PLAN-13 first Owner-independent source task, material owner #20. This is an executable **negative source snapshot**, not programme acceptance, release qualification, a waiver, or a new DELP/Owner/evidence policy. All comparisons refer to the **original immutable source** `reallakshman19/Common@b6b6daabe6defb253bac9dd00ce7ad48081a1000` (draft PR323), **not** to the current diagnostic branch's own HEAD.

## Original provider witness, no inferred green

- Full original WP2-A job: [Actions 38092613496 / Ubuntu Node22 job 114331966026](https://github.com/reallakshman19/Common/actions/runs/38092613496/job/114331966026), source HEAD `b6b6daabe6defb253bac9dd00ce7ad48081a1000`; exact run `node --test relay/RECOVERY/V35_R14_WP2A_20261010/*.test.mjs`.
- Terminal report: **283 tests / 262 pass / 21 fail / 0 skipped**. Other windows and Node configurations and native job results must not be inferred from this one log. Existing CI workflow is **FAILURE**, not PASSED.
- Distinct scoped U02 source tests **48/48 × 4** pass and two real T35 provider reads **safely refuse** `SOURCE_READBACK/SELECTED_CHECKS_DRIFT`; those scoped results cannot qualify whole programme, effective required CI, admitted E, DELP, independent successor, reviewer or writer.
- Exact original 21 test titles are in **`t36-full-suite-red-baseline.mjs`** grouped in `FAILURES` (3+3+7+8). That script runs the **full real test directory** on the separate checkout of pinned PR323 SHA, parses actual Node TAP process failures, refuses **even one additional/missing/renamed failure**, validates 283/262/21/0 and returns `EXACT_21_FAILURE_RED_BASELINE_REPRODUCED` only for exactly this known negative. A green job means negative baseline reproduced, **not** source/product GREEN. If the source/provenance changes, do not silently rebaseline it.

## Actual causal source/fixture analysis

| Suite / failed | Observed falsifier | Physical source proof | Owner-directed next action |
|---|---|---|---|
| T03 selected-check drift **3/5** | `SELECTED_CHECKS_PAGE_OR_RESPONSE_INVALID` instead of selected drift/stable | `t03-selected-ci-drift.test.mjs:data()[route.status]` uses `{sha:H,statuses:[]}` **without `total_count`**. Original current U02 `selected()` rejects it at **FIRST_SELECTED**, before drift comparison; test expects `SOURCE_READBACK/SELECTED_CHECKS_DRIFT` / stable | **T37:** supply valid, complete status count `0` to input fixtures and re-run real drift/negative tests. Do NOT relax U02 total/count rules |
| T05 WP2-B negative consumer **3/9** | `UNKNOWN` instead of `REFERENCES_COHERENT_BUT_UNADMITTED` | `t05-wp2b-same-head.test.mjs:data()[status]` also uses `{sha:H,statuses:[]}` without count; U02 refuses, U04/consumer correctly cannot join a complete vector | **T37:** repair fixture completeness, still assert `NOT_ADMITTED`, no R3/DELP/reviewer/writer. Do not redefine UNKNOWN as evidence |
| T14 historical 8-blobs **7/7** | First test's expected `3eac046128202fdee88a5ad47bb1df82e3304ca1` vs actual `3033b177d645810c6cb647ca831308893fd006c0`, cascading across seven tests | `t14-source-blob-closure.mjs:ORIGINAL_FILES` explicitly pins **historical PR308** `087cf43193febffc31375e71359e767489d3ae68`; verified via two genuine immutable GitHub file reads: **PR308 blob `3eac046...`**; **PR323 blob `3033b177...`** for `required-ci-material-v1.mjs`. But `t14-source-blob-closure.test.mjs:fixtures()` uses `git show HEAD:<path>` and compares to PR308's old blob, inevitably failing at PR323. | **T38:** preserve historical `ORIGINAL_FILES` exactly, make test Git reads use **pinned historical commit** instead of current HEAD, check independent HEAD/current identity and anti-spoof outcomes. Never rewrite the expected historic hash to today's blob blindly |
| Original physical WP2-A U01–U04 **8/14** | `source_consistent=false`, `SOURCE_MATERIAL_UNVERIFIED` instead of verified negative joined vector or second-round source drift | `wp2a-integration-v1.test.mjs:fixture()[statusPath]` uses `{sha:H,statuses:[]}` without count; original U02 FIRST_SELECTED refuses, so U04 stops before downstream intended observations (including edited comment, run ID, base tip second-round change) | **T37:** supply genuinely complete status count to fixture, preserve wrong App/duplicate checks/digest/stale/negative behavior; only then reach intended U04 stages |

**Important distinction:** This source reconciliation supports *plausible, directly visible causal fixture mismatch* for 14 tests, and confirmed historical/current blob mismatch for 7; the **actual exact-head full-suite host matrix** is the independent reproduction oracle. Do not claim these proposed fixes already passed. The 21 are a **real unqualified regression set**, not waived inherited noise.

## Reproduction and guard rails

The dedicated [`.github/workflows/v35-294-t36-pinned-red.yml`](../../../.github/workflows/v35-294-t36-pinned-red.yml) checks out this diagnostic draft PR and independently checks out PR323 **at its exact immutable SHA**, then:
```bash
node --test report/relay/RECOVERY/V35_R14_WP2A_20261010/t36-full-suite-red-baseline.test.mjs
node report/relay/RECOVERY/V35_R14_WP2A_20261010/t36-full-suite-red-baseline.mjs pinned
```
Expected harness result: `EXACT_21_FAILURE_RED_BASELINE_REPRODUCED`, exit 0 **only if** the original test command exits nonzero with exactly those 21 failures and 262 passes. If additional failures, missing expected errors, wrong source SHA, wrong test suite count, or surprise full green: `BASELINE_UNVERIFIED`, nonzero exit. Node22/24 on Windows/Ubuntu runs are independently reported; CI queue/race statuses must be verified at the exact diagnostic HEAD. No actual original source/fixture tests are modified by T36.

## Decisions, task frontier

- **T36**: establish falsifiable original RED baseline, *no repairs* and no production attestation.
- **T37**: fix/qualify the three stale full U02 combined-status fixture sources (T03/T05/U01–U04); test exact intended semantics and all negative rejects.
- **T38**: version historical PR308 byte witness apart from changed PR323; retain authentic negative tamper tests.
- **T39**: original full Win/Ubuntu CI + genuine WP2-A→WP2-B same-current-source negative consumer. Do not write E.
- **T40**: choose genuinely Owner-admitted eligible positive leaf, if available; otherwise exact `HOLD_AUTHORITY` and responsible #289/#12/#288/#4/#6 actors.
- **Blocked until actual external authority:** #289 D1–D5, original #294 T06–T10 positive lifecycle, #5/#284 AC0/8. `CHECKPOINT_FACTS_V1` not published, E not admitted, Local writer/publisher off.

This is an engineering source report, not a synthetic independent review, owner source, stale immutable-head replacement, or merged production proof.
