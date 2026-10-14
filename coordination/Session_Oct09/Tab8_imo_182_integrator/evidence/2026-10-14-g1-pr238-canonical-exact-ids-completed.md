# G1-R6-01 — PR #238 exact-head canonical regression closure (14 Oct 2026 UTC)

**Task owner:** Tab8 IMO #182 integrator successor. **Intent:** take over formerly in-progress exact-head CI of existing draft PR #238, prove whether narrow relation-symbol source correction resolved its introduced regression, and stop before unrelated source/schema authority changes.

## Immutable verified GitHub identities

- PR: https://github.com/reallakshman19/Grade9v3.5/pull/238 **OPEN, DRAFT, NOT MERGED**
- Corrected exact head: `cbed195cdda74e8dcf7ff3c6bb450a392d6f6f40`; preceding head: `28511cb4b82c17f90892867cae85955fc29c21d8`; unchanged PR immediate base: `main@4dbedc6773482bbecb146ff8959614b2c32dcc6e`.
- Six current corrected-head workflows **COMPLETED**: [question-bank 38511100262](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38511100262) SUCCESS; [v31 relay 38511100248](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38511100248) SUCCESS; [SOF seed integrity 38511100222](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38511100222) SUCCESS; [learner-platform 38511100208](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38511100208) SUCCESS; [guardrails 38511100238](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38511100238) FAILURE; [canonical 38511100323](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38511100323) FAILURE. Both canonical jobs named "Regression delta (exact test ids)" and "Assurance (no worse than the baseline)" failed; informational release-status succeeded but is **NOT release approval**.

## Direct exact failure-ID source comparison

GitHub **canonical run 38511100323 job 115679790201** downloaded as a full original job log, and previous **canonical run 38497212010 job 115635603741** independently inspected. Two comparisons in each job have *different* reference baselines; do not conflate them.

| Comparison | Pre-correction at 28511cb4 | Corrected head cbed195c | Actual interpretation |
|---|---|---|---|
| Exact canonical FAIL/ERROR IDs **versus immediate PR base** | **2 NEW; 1 FIXED; 152 still failing** | **0 NEW; 2 FIXED; 151 still failing** | Introduced representation-symbol regression removed. Not full canonical PASS. |
| Exact canonical FAIL/ERROR IDs **versus separately pinned main** | **8 NEW; 20 FIXED; 146 still failing** | **5 NEW; 20 FIXED; 146 still failing** | Broader pinned comparison still red for five other IDs; do NOT grant exception or equate with PR immediate-base regression. |
| Guardrails full FAIL/ERROR ID set preceding vs corrected head | **154 distinct**; 2952 tests, 120 FAIL + 34 ERROR | **151 distinct**; 2954 tests, 117 FAIL + 34 ERROR | **0 new, 3 removed**; 7 skipped in both. Both workflows FAILURE. |

**Canonical exact removed-vs-base IDs** (corr head): `test_library.DepictionIsBackedByTheContract.test_every_committed_bridge_names_a_drawn_part_and_a_used_symbol`, figure `REP-TEST-IMO-G9-RESIDUE-TABLE`, symbols `n mod 3 ∈ {0,1,2}` and `n, n+2, or n+1`. **Guardrails old→new three removed:** same assertion/figure with symbols `n mod 3 ∈ {0,1,2}`, `n+1`, `n+2`. No new failing IDs in either measured scoped comparison. These are distinct direct comparisons; do not claim their different removed-ID lists are contradictory.

Current source candidate `TEST/library/imo-g9-divisibility-core1a.v1.json` blob `51a38081e103f56204e373e5a50f7147c15db0c2` correctly declares relation symbols `n,n+1,n+2` and uses residue mapping n mod3 0→n, 1→n+2, 2→n+1, preserving parity. Current validator `2e9fea1a494575b1b46fec247f653137205d4468` and tests `a4bef98de50fb915af090c016114cbb5e8a8c8c9` include missing/misnamed symbol falsifiers. **No new source patch made in this follow-up**, and original HTML blobs remain unchanged.

**Assurance is separate:** canonical run 38511100323 job `115679790310` FAILED with 20 new canonical findings and **62 ledger-worse page measurements**, from wider repo/baseline checks; release-status `115679790365` informational SUCCESS. These do not establish release readiness. Full scoped source 11/11 direct checks in prior G1 report remain valid, but cannot supersede actual broad failure.

## Unresolved contracts and authority boundary

- `TEST/adapter/CoreContracts.json` blob `2f44a2babc7be8a04737aad1d9ffd744a93f6ab2` declares only VECTOR/VECTOR_SUBTRACTION PROPOSED kinds, whereas authored TEST source requires `TABLE_OF_VALUES`; broad guardrails still reports `REPRESENTATION_KIND_UNDECLARED`. Proper adapter module owner must determine whether to admit kind and with what cross-module tests. Do not add a kind blindly.
- Four `exit_task.oracle.verification.bindings` claim raw strings `positive_integer`, `24`, `0..23`, `n(n+1)(n+2)(n+3)` with `data=[]`; generic `Shared/library/package.schema.json` requires valid governed datum references, not fake data IDs. Source/schema owner must choose an honest typed parameter/data contract. Do not suppress oracle/gate or fabricate data rows.
- Separate unqualified human academic review of D1 SYNTHESIZE/JUSTIFY, 12 H/S/P/M checks, learner comprehension/altitude evidence, original Core2 rights (#183), frozen golden successor Owner D-182-3, separate Owner QRT cell decisions **0/28**, 0/7 D1, merge and release HOLD. No change of Owner decision, qualified reviewer assignment, Q003 private source, general renderer, blueprint or release status.

**Technical disposition:** `G1-R6-01_EXACT_CI_VERIFIED_TARGETED_REPAIR=PASS`; `G1-R6-01_BROAD_GUARDRAILS=FAIL`; `G1-R6-01_CANONICAL=FAIL`; `MERGE_ALLOWED=NO`; `OWNER_QRT_ACCEPTED=0/28`. **Next:** G1-R6-02 source/adapter + oracle contract owner decision (not unauthorized patch), G1-R6-03 qualified independent review and Owner QRT verdict; maintain draft and separate review branch stack.

**Proof references:** direct Actions job logs linked in above run URLs; earlier [issue #200 guardrails note](https://github.com/reallakshman19/Grade9v3.5/issues/200#issuecomment-6161028660) and [previous guardrail delta report](./2026-10-14-g1-pr238-guardrails-three-ids-cleared.md). All reported test IDs are from real completed job logs; no local GitHub CI run was fabricated.
