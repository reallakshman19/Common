# V3.2/V3.5 Buddy recovery — P0 evidence and P1 frozen-scope proposal

**Record:** P0_SOURCE_RECONCILIATION_V1 · **Governing new issue:** [Common #6](https://github.com/reallakshman19/Common/issues/6)
**Record provenance:** GitHub provider reads on 2026-10-09. This is a source/readback and CI observation report, NOT a local full-checkout test or authenticated Owner/Runner verdict.
**Status:** P0 inventory partially completed; P1 exact-scope *proposal* committed with `owner_authorized: false`. Neither native Stage1 isolation nor merged implementation acceptance is granted.

## 1. Immutable source identity and migration

| Authority / role | Exact observed ref | Status and meaning |
|---|---|---|
| Canonical source repository | `reallakshman19/Common` main `d60c36605e988dcc160647421973f170fd87e0eb` | Current migration baseline observed; independent GitHub provider objects |
| Legacy source repository | `reallaksh19/Common` main `d60c36605e988dcc160647421973f170fd87e0eb` | Same Git commit at audit, NOT same GitHub issue/PR identity |
| Legacy V3.2 issue / PR | [old #889](https://github.com/reallaksh19/Common/issues/889), [old PR #892](https://github.com/reallaksh19/Common/pull/892) `97d9f384ac1cfe4458b2db2302f5e7170a99e06d` | HISTORICAL_ONLY; Git branch preserved |
| Legacy V3.5 issue / PR | [old #890](https://github.com/reallaksh19/Common/issues/890), [old PR #893](https://github.com/reallaksh19/Common/pull/893) `09ff3751560bb49098e69c9c79918626078c7564` | HISTORICAL_ONLY |
| New V3.2 implementation | [new issue #2](https://github.com/reallakshman19/Common/issues/2), [new PR #2](https://github.com/reallakshman19/Common/pull/2) `e5cdf5fb1de26992ab9fa5fd7752f4f5e7f74da5` | DRAFT, 28 changed paths at observation, base `d60c3660` |
| New V3.5/R14 source interface | [new issue #1](https://github.com/reallakshman19/Common/issues/1), [new PR #3](https://github.com/reallakshman19/Common/pull/3) `cc4de8a87ec86ea66f02bb2f82184ad0f7a3d598` | DRAFT, 31 changed paths at observation, base `d60c3660` |
| Parent recovery responsibility | [new #6](https://github.com/reallakshman19/Common/issues/6) | This recovery plan; not a new accepted graph/lease or Owner-authentication source |
| Existing source/receipt repair | [old #865](https://github.com/reallaksh19/Common/issues/865), [old #872](https://github.com/reallaksh19/Common/issues/872) | Separate open dependency; no Buddy acceptance shortcut |

**Reconciliation rule:** A Git SHA can identify the same tree across migrated repositories, but does not establish that a GitHub issue number, PR review, Owner decision, API identity, permission or credential was migrated. Historical links remain exactly historical. R14 U1/U2/U3/… source roles may require current repo-specific proof; fail closed.

## 2. Exact V3.2 code scope and guard cause

New PR #2 modifies these four *frozen* V3.2 paths:

1. `skills/engineering-pr-delivery-v3.2/schemas/transaction.schema.yaml`
2. `skills/engineering-pr-delivery-v3.2/scripts/relay_tx.py`
3. `skills/engineering-pr-delivery-v3.2/scripts/transactionlib.py`
4. `skills/engineering-pr-delivery-v3.2/tests/test_relay_tx.py`

The current `main` version of `skills/Local_PR_Deliverty_v1.1/integration/frozen-v32-amendments.yaml` has **no enabled grant** for these four exact paths. The native `frozen_tree_guard.py` reads the manifest from the **PR BASE SHA** and rejects a grant introduced only at candidate HEAD.

The exact PR #2 [Local guard run #37968836973](https://github.com/reallakshman19/Common/actions/runs/37968836973) failed in the step **Verify frozen V3.2 tree unchanged (or amended only by a base-pinned Owner amendment)**. Prior run [#37968065067](https://github.com/reallakshman19/Common/actions/runs/37968065067) listed the same four paths and exit 1 in the job log. This is a **real authorization gate failure**, not an indication that Python code is invalid.

**Safe repair procedure:** independent Owner-reviewed grant on a separate branch → merge that governance amendment → create/rebase the implementation *after the new base contains the grant* → rerun native frozen guard and exact-head tests. Do **not** modify #2 to self-authorize; do **not** merge #2 on its existing unauthorized base.

The sibling governance branch contains an additional `AMEND-V32-BUDDY-017` entry set to `owner_authorized: false`. This is intentionally ineffective: the parent issue requested a recovery process and the Owner said "start fix", but did not specifically approve these protected paths as a new admitted code scope. Only a later explicit scope decision can enable it.

## 3. Actual hosted regression observations

| Exact head | Workflow | Provider result | Interpretation |
|---|---|---|---|
| PR #2 `e5cdf5fb1de26992ab9fa5fd7752f4f5e7f74da5` | [V3.2 #37968836955](https://github.com/reallakshman19/Common/actions/runs/37968836955) | **SUCCESS**, actual V3.2 job steps executed | Source test gate at this head is green. Does not override Local frozen guard or independent B test. |
| same PR #2 HEAD | [Local #37968836973](https://github.com/reallakshman19/Common/actions/runs/37968836973) | **FAILURE** | Frozen V3.2 unauthorized paths |
| same PR #2 HEAD | DELP #37968837007 | **SUCCESS** | No independent writer/custody qualification inferred |
| older PR #2 test head | [V3.2 #37968064952](https://github.com/reallakshman19/Common/actions/runs/37968064952) | **FAILURE**, 38 native Relay tests executed, 1 failed | Earlier `test_baseline_first_sequence_with_claimed_external_dispatch` expected `MISSING_STAGE1_BASELINE` but received `BUDDY_STALE_STAGE_CHAIN`; not the current-head verdict |
| PR #3 `cc4de8a87ec86ea66f02bb2f82184ad0f7a3d598` | [V3.2 #37968845643](https://github.com/reallakshman19/Common/actions/runs/37968845643) | **SUCCESS / NOT_APPLICABLE for V3.2 paths** | Docs PR does not qualify transaction code |
| same PR #3 HEAD | [Local #37968845645](https://github.com/reallakshman19/Common/actions/runs/37968845645) | **SUCCESS** | No frozen V3.2 code change |
| PR #2/#3 at observed heads | V3.1 workflow | **FAILURE** | Earlier #3 log reveals missing legacy `engineering-pr-delivery-v2.5.yml` / `engineering-pr-delivery-v3.yml` files in six V3.1 CI-terminal-check assertions. Must assess as a separate baseline/migration issue, not certify as passing or automatically widen Buddy scope. |

**No local checkout tests** were run by this report author: public GitHub checkout was unavailable in the local execution environment (DNS failure). Hosted GitHub job steps are independently retrievable and take precedence over speculative local outcomes. No fresh B test was run.

## 4. One transport contract — reconciliation decision candidate

**Canonical operational path (from draft new PR #2):**

`relay/CONTINUITY/episodes/ISSUE-<issue>/messages/TX.<issue>.<serial>-<STAGE>.md`

New PR #2 redirects `relay/BUDDY_RUNNER/README.md` as historical guidance and retains native `PUBLISH_BUDDY_MARKDOWN` / transaction digest/immutability/ordered receipt candidate semantics. New PR #3 improves V3.5 baseline-first, original Owner source roles, current candidate/tested-head separation and R14 U1–U5 interface. The #3 Markdown branch has newer source amendments and is **not** the identical PR #2 snapshot. Explicitly reconcile those diffs before one combined head.

**Single authority invariant:** transactional bytes are record integrity, not original Owner source authentication, tool blindness, final freeze, DELP acceptance, Local reviewer/merge clearance or exclusive writer. A `STAGE1_FREEZE_CANDIDATE` must say `Isolation verdict: NOT_ATTESTED`; a real controller's attested read gates and final freeze are a separate prerequisite before Stage2 disclosure.

## 5. Acceptance trace against old parent issues

| Old issue criterion | Existing candidate | P0 finding / pending gate |
|---|---|---|
| #889 R1, governed transport | new PR #2 | TRANSPORT_CANDIDATE, Local authorization FAIL |
| #889 R2, sanitized Owner/historical intake | PR #2/#3 templates | NOT EXECUTED on real B |
| #889 R3, baseline before independently chosen HOW | native stage ordering + #3 instructions | Host native ordering test PASS at current PR #2, semantic independent baseline NOT_RUN |
| #889 R4, restricted input/output and freeze | #2 five-phase candidate; #3 operator preflight | External admitted B + denied reads + final freeze NOT_RUN |
| #889 R5, native technical HANDOVER | existing native V3.2 handover and #3 view | No actual controlled integration |
| #889 R6, four-view Stage2 and single-writer admission | #3 Markdown stage design | NOT_RUN, writer OFF |
| #889 R7, one genuine controlled A→B code continuation | no qualified trial | NOT_RUN |
| #890 WP0/WP1, source maps/templates | #3 and #2 docs | Draft/partial; new R14 currentness needs reconciliation |
| #890 WP2–WP5, actual blind Runner, Stage2, custody, matched experiments | no qualified trial | NOT_RUN |
| Wider #718/#865 evidence spine | native V3.2 | separate acceptance, no progress/merge inflation |

## 6. Mandatory negative checks before advancing P2 and P4

- Frozen authorization: main remains unchanged; disabled grant yields no accepted paths; enabling grant in a PR head while base is unchanged must still fail. Only base-resident, explicitly approved exact paths may pass. Unlisted file/renamed file must fail.
- Transaction: wrong repo/issue/stage, duplicate/disordered TX, superseded intake, forged digest, symlinked latest message/receipt, partial write/recovery, conflicting freeze verdict must fail.
- Independence: B fresh context and actual positive allowed historical read P01; N01 current A branch, N02 issue/PR/search, N03 Stage2/reviewer, N04 alternate connector/raw/browser/shared workspace, N05 packet leaks, N06 distinct effective B session identity must be observed by independent controller. Any NOT_RUN is HOLD.
- Custody: A technical handover only after authenticated freeze and explicit stage admission; no old direct-writer credentials, in-flight/unknown operations or stale HEAD; no fake Owner approval.
- Unplanned routing: interruption with no clean B cannot be misreported as planned Stage2; ordinary native handover cannot auto-create Two-/Three-Pass.
- Browser/end-to-end only where app/UI relevant, with authentic fixtures, positive and negative user-output assertions, source/consumer trace and exact tested SHA.

## 7. Current next actions

1. **OWNER REVIEW / GOVERNANCE:** review the four exact paths and decide whether to explicitly authorize `AMEND-V32-BUDDY-017` on a separately merged grant; no implied consent from this report.
2. **CODE:** only then rebase the Buddy implementation to that actual grant-containing base and rerun exact-head frozen guard, native Relay unit tests and relevant cross-version tests.
3. **INTEGRATE:** reconcile PR #2 canonical messages against PR #3's latest R14 source-identity Markdown without a competing active namespace.
4. **OPERATE:** separately controlled independent B with denied read probes; no simulated self-attestation.
5. **HANDOVER/REVIEW:** native custody, Stage2 four-way comparison, external writer fencing, first source-verified action, end-to-end oracles and normal TASK_EVIDENCE.

**Stop condition:** PR #2 and PR #3 remain DRAFT; no production qualified Buddy launch, Stage2 read release, Owner approval, Local writer grant or merge is implied by this record.
