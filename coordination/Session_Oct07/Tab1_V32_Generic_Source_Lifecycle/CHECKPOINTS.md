# CHECKPOINTS — Tab1 / V3.2 Generic Source Lifecycle (append only)

This Tab1 coordination record is separate from `Tab2_Lifecycle_Evidence_Reconciliation` (Common #294). Owning implementation Common #325 / source candidate PR #326; parent release gate #289 and programme #5. **RECON only.** The new Tab1 folder did not exist on current main or PR #326 when the RECON 4/4 instruction arrived. Do not treat it as a previously frozen Owner ledger, review, accepted check or production permission.

## 2026-10-11 — Plan revision 1: original implementation owner plan (reference, not rewritten)
- Issue #325 published T01 generic GET-only binding; T02 current graph/source custody and native fact-ledger; T03 disjoint issue/PR publisher pure plan; T04 governed protected native adapter; T05 physical source/evidence/DELP/GitHub/C6/B qualification.
- Source tasks **T01/T02/T03 IMPLEMENTED and SYNTHETIC-TESTED** on draft PR #326 at source head `51f5bccbdab50c000ca9eb30c872ca23acdee441`, 34/34 tests per Python version 3.11/3.12/3.13, **102 named test executions PASS**, guard no network/direct mutations PASS ([CI #38101237687](https://github.com/reallakshman19/Common/actions/runs/38101237687)). **4/5 workflows SUCCESS, inherited V3.1 FAIL** due to six missing-retired-workflow FileNotFoundError ([#38101237697](https://github.com/reallakshman19/Common/actions/runs/38101237697)).
- Separate draft PR #327 at `8b9d767a236c21257a0514b1563ea7b37263b21b` repairs only V3.1 test inventory; its exact-head V3.1 run [#38100594082](https://github.com/reallakshman19/Common/actions/runs/38100594082) has **274/274 PASS**. **It has NOT been integrated into #326.** Do not cross-credit.
- Other V3.2/DELP/Local green workflows on #326 may be path-`NOT_APPLICABLE`; they are not an executed positive Owner lifecycle. Owner programme #5 **AC0/8**; writer OFF; V3.2 production NO, automatic Agent B NO.

## 2026-10-11 — Plan revision 2: RECON 4/4 successor sequence (next; NOT STARTED)

**Binding report:** `RECON/2026-10-11/4-report.md`. Its `1-why.md`, `2-source.md`, `3-acceptance.md` were retrospectively reconstructed **in this RECON documentation pass** from actual pinned code/CI; they are not independent earlier RECON approvals. Main verified at `366114205d9395fe4ba4f679059ec8fc38bb7a21` before report. After docs-only PR commits, re-read HEAD and CI; the test CI on code HEAD cannot be transferred to documentation HEAD as current exact-head qualification without verification.

| Order | Task / size | Reuse-first source path | Outcome and exact acceptance |
|---|---|---|---|
| 1 | **N1 / S** | reuse tested fix in draft PR #327 `skills/engineering-pr-delivery-v3.1/tests/test_ci_terminal_checks.py`; candidate PR #326 workpack `relay/INTEGRATION/V32_325_GENERIC_SOURCE_20261011/` | Governed same-branch/same-HEAD integration of test-only retired workflow expectation fix; one new exact head passes V3.1 274/274 and focused 34/34 each 3.11–3.13, no new/retired production workflows, no cross-SHA pass claim. |
| 2 | **N2 / M** | reuse native `skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py`, `trusted_scoreboard_v32.py`, `vertical_cycle_v32.py` and existing T01–T03 pure code | Requires already-base-resident explicit Owner exact-path freeze grant and independent review; fix full `owner/repo#PR` identity, generalize existing **single** native writer/identity, maintain OFF until release; targeted original current graph/foreign-ref/readback negative tests PASS at same head. **HOLD pending grant.** |
| 3 | **N3 / L** | reuse existing native DELP, `handover_context.py`, `relay_tx.py`, Buddy renderer; private lab and #289 production gate | Real authorized lab Owner/current graph, externally checked original material/required CI and independent positive `CHECKPOINT_FACTS_V1` → native positive E → single native GitHub issue+PR writer/readback → genuinely isolated four-context C6 and exclusive old-A revoked/new-B lease. Independent reviewers and Owner AC1–AC8 adjudication. **HOLD pending source/access/reviews/policy.** |

### Handover checkpoint / closure
- **RECON 4 report:** `RECON/2026-10-11/4-report.md` consolidated owner WHY, source, flow, AC1–AC8, inputs/oracles, contradictions, blocker map, usability, three tasks and evidence/unknowns.
- **Next engineer:** verify current main and PR heads first; read report before issues/PR narrative; own tasks N1→N2→N3 subject to Owner grants; do not touch Tab2 or claim fake evidence/auth, merge or launch B from these docs.
- **Status:** HANDOVER_DOCUMENT_READY; **T04/T05 remain HOLD**. No T04/T05 coding, merge or production activation initiated by this RECON turn.
