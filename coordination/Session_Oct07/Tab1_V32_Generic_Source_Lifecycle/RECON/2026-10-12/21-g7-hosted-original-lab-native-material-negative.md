# G7 R7 W02/W03 — LIVE ORIGINAL LAB GITHUB ACTIONS NEGATIVE CHARACTERIZATION PASS (not eligible E)

**Chat:** 6acbb049. **Timestamp:** 2026-10-12 Asia/Muscat. **Owner instruction:** "proceed now", followed by "done?". **Owning issue:** [Common #325](https://github.com/reallakshman19/Common/issues/325), root [#5](https://github.com/reallakshman19/Common/issues/5), plan [R7](https://github.com/reallakshman19/Common/issues/325#issuecomment-6111234594). **Read-only candidate PR:** [#326](https://github.com/reallakshman19/Common/pull/326), exact **`541110b37e3eab2d88a607b37ba03c2062236cbe`**, DRAFT and UNMERGED. **Hosted proof:** [Actions run #38225649205](https://github.com/reallakshman19/Common/actions/runs/38225649205), event `push` on this exact candidate commit, final `completed/success` for all 3 matrix jobs. **Production V3.2 writer OFF; no source facts issued, reviewers impersonated, protected native edit, amendment merge or publication.**

## 1. Actual change scope and chronology (no false prior CI)

Existing unmerged read-only integration PR #326 (T01/T02/T03) gained **only non-frozen candidate source and CI**:
1. Candidate `relay/INTEGRATION/V32_325_GENERIC_SOURCE_20261011/live_original_lab_boundary.py` created at commit `91672e7ebbccf3d613ad4c5c2388e415c1f4bae5`, corrected fixed-GET whitelist at subsequent `fd4f9c0ee9ce9a90bfe0ca6b460b157ddd671d6b`, and corrected read-only repository metadata `GET /repos/{owner}/{repo}` whitelisting at `640c6508aa2360b5d3bfa1cbe7d79c10d67dd629`, latest source Git blob **`488f242957d04a2434da4ff1c0d5f0177035e6e7`**.
2. Candidate **already-existing** `.github/workflows/v32-325-generic-source-preflight.yml` gained an explicitly opt-in `V32_PUBLIC_LAB_LIVE=1` Python 3.11 test step at `5afb2862947c57a0e4ae4f5f369316ba624be4e9`. Initial exact-head PR head `5afb286...` and `640c650...` had **only one scoreboard workflow SKIPPED and no relevant test workflow**, so no false queued/green claim.
3. Diagnosed absent test trigger: candidate CI workflow not installed on default main yet. Added narrowly branch-scoped `on: push` (only `feature/v32-325-graph-bound-readonly-integration`, only candidate integration/workflow paths) **without altering job permissions `contents: read`**, final candidate commit **`541110b37e3eab2d88a607b37ba03c2062236cbe`**, workflow Git blob **`50d9eb7dfba85d5c83dda22b20806ca13ef19e72`**. GitHub triggered the real `push` workflow [#38225649205](https://github.com/reallakshman19/Common/actions/runs/38225649205).
4. Existing Common frozen native source `skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py` was **unchanged**, Git blob **`804cacca930e47c4528bb0d245efaf941996e4cf`**. Candidate work is not in main and no protected source/test path was edited.

## 2. Provider source actually traversed, scoped to real original lab

Physical original lab `reallaksh19/relay-v32-e2e-lab` is PUBLIC and independently source-visible, numeric repo ID **1411550807**. Original released graph `governance/released-graph.json`, immutable `main@f0dfc590bd3fa53c50c1b645f17faf3f88e2f155`, Git blob **`fde7e1fbd0c71efb64a678206f0bc9f32e36f6c8`**, leaf `reallaksh19/relay-v32-e2e-lab#4` primary full PR ref `reallaksh19/relay-v32-e2e-lab#8` at merged source HEAD **`8ced7c13d5e9f9ba6870899ae8c62ec5501011b4`**.

The live test uses a bound, fixed-path, GET-only provider with exact identity checks: original repo metadata/ID/default `main`, immutable graph contents and current `main` graph Git blob, original root/leaf issue #1/#4, actual PRs #8/#13/#15, all original leaf #4/#5/#6 comment pages (one page plus empty page 2), and exact branch HEAD. No POST/PATCH/PUT/DELETE, no API mutation method and no forged original facts. Only within `V32_PUBLIC_LAB_LIVE=1` does it call **existing** `generic_current_source.reconcile_current_source(...)`, which uses native `delp.validate_graph`, `ledger_from_github`, `observe_github`, `project`, and unchanged `source_bound_responsibility_core` with repeated graph/source reads. It asserts the **exact** fail-closed `SourceHold("NATIVE_RESPONSIBILITY_CORE_MATERIAL_BOUNDARY")` with at least 20 bounded GETs and a safe path whitelist; any earlier graph/source/currentness failure or an unexpectedly accepted full PR would FAIL. The original graph binds full `owner/repo#PR`; native core still expects basename `repo#PR` prefix. The test intentionally passes on this negative outcome, **not** on a successful native core/accepted positive E.

## 3. Exact-head HOSTED CI job and step readback

| Job | Job ID | Exact result | Source-specific note |
| --- | --- | --- | --- |
| `generic-source-preflight (3.11)` | `114732376372` | **SUCCESS** | Existing candidate **44/44** named synthetic-provider tests PASS; physically executed **one live original public lab** GET-only native boundary test **1/1 PASS** (~9.96s); AST read-only/no direct network writer guard PASS |
| `generic-source-preflight (3.12)` | `114732376594` | **SUCCESS** | Existing candidate **44/44** synthetic-provider tests PASS; live physical GET step **SKIPPED intentionally** (3.11-only); read-only guard PASS |
| `generic-source-preflight (3.13)` | `114732376554` | **SUCCESS** | Existing candidate **44/44** synthetic-provider tests PASS; live physical GET step **SKIPPED intentionally** (3.11-only); read-only guard PASS |

**Total:** 132 existing synthetic-provider named test executions + **1 real original-lab live negative** = **133/133 PASS**, all at candidate commit `541110b37e3eab2d88a607b37ba03c2062236cbe`. Verified GitHub job steps and decoded logs: Python3.11 `test_real_released_graph_reaches_expected_native_material_hold ... ok`, `Ran 1 test in 9.962s`; earlier synthetic suite `Ran 44 tests` and `OK`. Python3.12 `Ran 44 tests in 0.338s`, Python3.13 `Ran 44 tests in 0.306s`. Workflow result `completed/success`, event `push`, exact SHA. **This is not a required-branch-policy PASS**, not an independent review result, not a positive admitted E, not a C6/readback publisher test, not an actual frozen-file repair. The run merely confirms the actual original source reaches **the precise known native material boundary**.

## 4. Remaining blocking release gates — do not turn a negative characterization into T04/T05

- [#325 known issues](https://github.com/reallakshman19/Common/issues/325) still lists **all four unchecked**: `R7-PENDING-01` 0/2 independent reviewers; `-02` effective required CI policy UNKNOWN (branch protection API 403); `-03` original eligible `CHECKPOINT_FACTS_V1` issuer and genuine accepted positive/hostile facts UNSELECTED; `-04` separate governance frozen grant not base-resident.
- [Governance PR #316](https://github.com/reallakshman19/Common/pull/316) exact head `8f5a47dd2e67795b78bf66732a485dba2fca07d9` remains DRAFT/UNMERGED with zero submitted reviews; Owner chat approved scope and manifest `owner_authorized:true` on the PR, but main frozen manifest Git blob **`ffe93467d8e75beebb6889f295205a8ba61bf620`** still has **no** amendment. The newly hosted candidate test **does not change** the grant's effective state.
- Original lab has 12 leaf comments and **zero** native fenced `CHECKPOINT_FACTS_V1`; genuine independent authorized positive `E>0`, positive/hostile H1→H2, required CI/reviewer qualification and live managed GitHub readback are **NOT_PROVEN**.
- **Progress:** R7 W01 DONE classification, W02/W03 PARTIAL; this *negative original-lab characterization unit* DONE only, not a fully closed W03/T04. Programme root #5 AC0/8 and original #325 T04/T05 OPEN. No false P/E/D, source ownership or native product acceptance. Production writer remains OFF.

**Next exact authorized work:** Obtain authentic independent reviewer and effective CI policy receipts on governance #316, separately approved merge so amendment is **already base-resident**, then implement the smallest existing frozen core+test fix accepting authentic full and historic short PR refs while rejecting wrong owner/repo/graph/number and rerun same actual lab/source positive+negative in fresh exact-head CI. Separately Owner selects eligible fact issuer and genuine original CHECKPOINT_FACTS facts before W02 positive. All blockers are recorded on owning issue as known items; no duplicate issues or synthetic substitution.

```text
Task: TAB1-G7-W03-LIVE-NEGATIVE (subtask of existing W03; not product T04 closure)
Goal (issue AC): Establish the real original lab full owner/repo PR failure at exact unchanged native core, read-only and hosted; no false native E credit
Status: DONE negative characterization / W03 PARTIAL, W02 PARTIAL
Met: yes negative only; no positive E/product AC
Done: Real hosted GET-only original lab native material-boundary negative, pinned immutable source, step-level PASS readback, 44 synthetic tests on 3 Python versions, scoped draft-branch workflow trigger
Code: reallakshman19/Common feature/v32-325-graph-bound-readonly-integration @ 541110b37e3eab2d88a607b37ba03c2062236cbe | PR #326 DRAFT; PR #316@8f5a47d DRAFT separate
Tests: Python3.11 44/44 + physical original lab 1/1 PASS; Python3.12 44/44 PASS (live SKIP); Python3.13 44/44 PASS (live SKIP) => 133/133 named executions PASS
CI: GitHub Actions run 38225649205 -> SUCCESS, original lab live step PASS on 3.11; not a required CI policy qualification
Evidence: https://github.com/reallakshman19/Common/actions/runs/38225649205 and this Tab1 report
AC: #5 0/8 -> 0/8; #325 T04/T05 OPEN -> OPEN
Claim: HOSTED_CI / INDEPENDENT live GitHub source GET; NONE for qualified original positive E, independent reviewer or protected-fix release
Blocker: PERSON:two qualified independent reviewers; OWNER:D02/D03 authentic evidence/policy; PR #316 separate approved merge/base-resident before protected edit
Next: Wait qualified governance review/merge; then small native fix and genuine positive/negative original lab replay; publisher/C6/B separate
```
