# G1-R6-01 — actual guardrails negative-test delta after relation-symbol repair

**Date:** 2026-10-14 UTC | **Chat:** 6ace7d89, active successor g1 workpack | **Tracker:** [Grade9v3.5 #200](https://github.com/reallakshman19/Grade9v3.5/issues/200) / programme [#182](https://github.com/reallakshman19/Grade9v3.5/issues/182). **No Owner acceptance or merge authority conferred.**

## Exact two-head GitHub read

| Metric | Initial authored repair HEAD | Revised same draft PR #238 HEAD |
|---|---|---|
| Commit | `28511cb4b82c17f90892867cae85955fc29c21d8` | `cbed195cdda74e8dcf7ff3c6bb450a392d6f6f40` |
| PR base | `main@4dbedc6773482bbecb146ff8959614b2c32dcc6e` | **Same** base |
| Guardrails run/job | [38497211734](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38497211734) / `115635602209` | [38511100238](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38511100238) / `115679783175` |
| Actual workflow result | **FAILURE** | **FAILURE** |
| Python suite | 2952 tests, 120 FAIL + 34 ERROR, 7 skipped | 2954 tests, 117 FAIL + 34 ERROR, 7 skipped |
| Unique full FAIL/ERROR identity strings extracted | **154** | **151** |
| New exact failed IDs on revised HEAD vs initial HEAD | — | **0** |
| Removed exact failed IDs on revised HEAD | — | **3**, all from intended residue correspondence |

The **exact three removed failures** are `test_library.DepictionIsBackedByTheContract.test_every_committed_bridge_names_a_drawn_part_and_a_used_symbol`, all for `REP-TEST-IMO-G9-RESIDUE-TABLE`, with previous failing symbol values:
1. `n mod 3 ∈ {0,1,2}` — old table row label not a declared linked relation symbol; replaced by `n` while row text explains the exhaustive modulo-3 classes.
2. `n+2` — now declared as an exact derived symbol in the linked relation.
3. `n+1` — now declared as an exact derived symbol in the linked relation.

These are concrete passed-previously-failed corpus assertion identities **in the completed guardrails suite**. The specialized candidate still has two stronger negative mutations, and the new head's two additional guardrail Python tests are present in the total run count. **No separate standalone test command or locally executed Python test is claimed**; exact-head GitHub full log is the proof.

## Scope, preserved gates, and new bounded source finding

The updated authored TEST package `TEST/library/imo-g9-divisibility-core1a.v1.json` Git blob **`51a38081e103f56204e373e5a50f7147c15db0c2`** at revised PR #238 head carries exact relation-symbol definitions `n,n+1,n+2`, unchanged separate parity guarantee and four literal element/symbol pairs. Source validator Git blob **`2e9fea1a494575b1b46fec247f653137205d4468`**, adversarial tests **`a4bef98de50fb915af090c016114cbb5e8a8c8c9`**, source receipts repinned. Previous direct GitHub readback **11/11** source/receipt predicates PASS. Same six TEST-only files in draft PR, no public HTML, renderer, golden, rights or release change.

**Additional, distinct still-open source-contract problem verified:** `TEST/adapter/CoreContracts.json` actual Git blob **`2f44a2babc7be8a04737aad1d9ffd744a93f6ab2`** declares **only** `VECTOR` and `VECTOR_SUBTRACTION` as PROPOSED representation kinds, but this authored Core1A research source declares **`TABLE_OF_VALUES`**. Corpus guardrails therefore still reports `REPRESENTATION_KIND_UNDECLARED` for its representation; merely defining relation symbols does not make the figure kind supported/implemented. Changing the TEST adapter is a separately owned subject-level policy/compatibility decision; **do not add an arbitrary kind to the adapter from a D1 reviewer patch just to silence the test**.

The other independent **generic intake** blocker remains: `data=[]` while the exit oracle `verification.bindings` names `positive_integer`, `24`, `0..23`, `n(n+1)(n+2)(n+3)`. Canonical `Shared/library/intake.py` expects bound governed `data[].id`, not these raw domain/range/constant/expression values. Authored candidate **not admitted**; math and academic review NOT granted.

**Broader CI on revised exact head:** question bank run [38511100262](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38511100262), v31 relay [38511100248](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38511100248), SOF integrity [38511100222](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38511100222), learner-platform [38511100208](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38511100208) **SUCCESS**. Guardrails [38511100238](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38511100238) **FAILED**; canonical assurance [38511100323](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38511100323) **Assurance (no worse than baseline) FAILED**, `Regression delta (exact test ids)` job `115679790201` still **IN_PROGRESS** at latest check; final canonical compare **not yet independently verified**. Informational release job SUCCESS **does not grant release**.

## Direction, scope boundary and next exact check

- **G1-R6-01 substantial step DONE at guardrails level:** 3 of 3 intended old failed corpus identities cleared without adding new failing guardrail IDs; main-based draft #238 still **OPEN, DRAFT, unmerged**. Targeted technical progress only; user receives a better provenance-correct TEST source, **not** a changed production learner page nor accepted QRT.
- **Still task G1-R6-01 OPEN for canonical comparison:** once job `115679790201` finishes, record `NEW/FIXED/SHARED` for current head versus PR base and pinned main, and check that old three correspondence failures truly no longer in canonical exact IDs; do not assume guardrails implies canonical.
- **G1-R6-02** source/schema owner must resolve *both* `TABLE_OF_VALUES` subject representation-kind declaration and executable oracle parameter-vs-datum semantics with negative/admissibility tests. If owner unavailable, HOLD. Public learner TEST navigation, banner, fixture status and TEST generated data remain separate upstream owner issues.
- Qualified independent SYNTHESIZE/JUSTIFY H/S/P/M/COI and actual learner observations, Owner cell decision IDs **0/28**, Owner D-182-3 golden, private original SOF Q003 #183 rights, global CI, merge and release all **OPEN**. No waiver or live site action.

LOG | Outcome=exact guardrails 154→151 failed test identities, 0 new and 3 fixed in TEST representation corpus | Proof=job115635602209 vs job115679783175 full job logs and source/adapter blobs | Open=canonical exact-ID job115679790201, adapter/oracle source owner, QRT Owner 0/28 and release.
