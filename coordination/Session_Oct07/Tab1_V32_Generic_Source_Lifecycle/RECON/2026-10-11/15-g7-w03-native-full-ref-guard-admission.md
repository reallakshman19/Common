# G7 R7 W03 — Native PR full-ref compatibility: source check and frozen grant HOLD

**Chat:** 6acbb049. **Task:** TAB1-G7-W03. **Owning issue:** [#325](https://github.com/reallakshman19/Common/issues/325). **R7 plan:** [6111234594](https://github.com/reallakshman19/Common/issues/325#issuecomment-6111234594). **W02:** [BLOCKED 6111382656](https://github.com/reallakshman19/Common/issues/325#issuecomment-6111382656), source report `RECON/2026-10-11/14-g7-w02-original-positive-native-readiness.md`. **Main source assessed:** `8387c14529ce4a1173d67c4aea6c33e00633df3b`, not an authorized Owner graph. **Status:** `PARTIAL`, static inspection done, authentic graph execution/protected fix blocked.

## 1. Source-verified first boundary and exact logical inspection

Native unique projection owner `skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py`, **blob `804cacca930e47c4528bb0d245efaf941996e4cf`**, `validate_graph` around line 1330, `source_bound_responsibility_core` line 4158. The native source reads `candidate_pr=source.get("primary_pr")`; then rejects if not a string or **not** `candidate_pr.startswith(str(indexed["programme"]["repository"]).rsplit("/",1)[-1] + "#")`, raising `DelpError("RESPONSIBILITY_CORE_MATERIAL_BOUNDARY")`. Earlier `validate_graph` stores `primary_pr=raw.get("primary_pr")` and uses `parse_ref(node["primary_pr"])`; the latter is a different semantic gate from basename-only `startswith`.

Pure isolated prefix-expression probe, using actual old public repository `reallaksh19/Common` → prefix `Common#`: `Common#740` = true; `reallaksh19/Common#740` = **false** (same-repository full syntax rejected by core); `other/Common#740` = false; `Common#999` = **true** (prefix check alone cannot prove correct PR number or material eligibility). **These four are source-expression checks, NOT native `validate_graph/project/core` executed together or real Owner evidence.** A valid full-form primary PR may pass the upstream parser but hit the core boundary. The existing #326 source handler `generic_current_source.reconcile_current_source`, **blob `75287ef9ace8fea0f45d7b97d4bd9bde974ae789`**, calls native `project` and `source_bound_responsibility_core`, translating material boundary errors to `NATIVE_RESPONSIBILITY_CORE_MATERIAL_BOUNDARY`, after source pin/readback guards. It remains a read-only candidate on draft PR #326, not a production writer.

## 2. Actual graph/input discriminator NOT_RUN

Freshly fetched main `.github/v32-evidence-spine/718-proposal-v2.json` Git blob **`d35019b416cb3b573280e166027d3f65ba61f59c`** declares old repository `reallaksh19/Common` **ID 1207996454**, root `Common#718`, primary short refs `Common#722`, `Common#728`, `Common#740`, `Common#800`. It is old public history, NOT canonical new repository `reallakshman19/Common` **ID 1412133785** or approved programme root #5. The old graph's short PR refs do not exercise the full-form branch. [#340 prior hosted GET native public history run 38150656871](https://github.com/reallakshman19/Common/actions/runs/38150656871) genuinely gave 50 old comments, compatible fact blocks=0, native E=0 and writer=0, not full-form positive/negative Owner input.

[#285 Owner-provided offline ZIP source record](https://github.com/reallakshman19/Common/issues/285#issuecomment-6100597830) claims historic private released graph blob `fde7e1fbd0c71efb64a678206f0bc9f32e36f6c8`, but ZIP had no current GitHub metadata. Original `reallaksh19/relay-v32-e2e-lab` is still GET404 for connected actor at W02. #289 D07 unselected. Therefore W03 **cannot establish** that an approved *current original Owner graph* uses a full-form primary PR. No artificial graph conversion, fake fact, or W02 source substitution is allowed. Thus exact-native authentic graph discrimination is **NOT_RUN**.

## 3. Frozen-path grant: proposed does not mean approved

Main `skills/Local_PR_Deliverty_v1.1/integration/frozen-v32-amendments.yaml` Git blob **`ffe93467d8e75beebb6889f295205a8ba61bf620`** does **not** contain `AMEND-V32-289-PRREF-017`. [Draft #316](https://github.com/reallakshman19/Common/pull/316) head `7e9fd7bb83d61c58295ac47ae4cd665cdb12dfc7` is OPEN, DRAFT, unmerged and has **zero submitted reviews**. Its proposed manifest blob **`98c62d48bd5f623f409adc25eb3103cd9ae3378e`** explicitly records `AMEND-V32-289-PRREF-017` with `owner_authorized: false`; allowed paths only `delp_projection_v32.py` and `test_delp_projection_v32.py`. Proposal says an Owner engineering objective does not itself authorize protected code change; a future code PR requires Owner-qualified independent approval/review and amendment **already base-resident**. Branch protection GET at current connection **403**: required-check policy remains UNKNOWN, not waived. #316 is not a grant. The exact root product T04 remains OPEN.

## 4. Exit matrix, decision and re-entry

| W03 piece | Outcome | Qualification |
| --- | --- | --- |
| Inspect frozen native and separate parse/core semantics | DONE, source-exact blob | INDEPENDENT GET |
| Isolated prefix logic, short/full/foreign/wrong number | 4/4 expected expression outputs, NOT native | LOCAL-only diagnostic |
| Real original released Owner graph and native source same-head core on qualified facts | NOT_RUN, W02 original blocked / lab 404 | BLOCKED, NONE |
| Protected same-repo full-ref correction + frozen tests/CI | NOT_RUN, actual input unverified and effective #316 missing | BLOCKED, NONE |
| Native owned publisher, actual managed GitHub GET-back, cold B | NOT_AUTHORIZED, separate gates | NONE |

**Task status PARTIAL, Met=partial only for static source triage; no original T04 or #5 acceptance.** This is a genuine conditional source-level incompatibility, but **not** an observed failure on the authenticated original Owner graph. No product code was changed, no PR created, no native test executed or hosted CI run. Do not silently turn a static prefix observation into a production defect acceptance, and do not self-grant frozen path exceptions.

**Precise re-entry:** Owner D07 source and approved graph/current lab actor → W02 real permitted current original same-head positive+negative → W03 run full native short/full and wrong-owner/repo/number cases on approved graph. If actual authentic original input fails the boundary, seek Owner-released independently reviewed, merged/base-resident `AMEND-V32-289-PRREF-017` before protected edit. Otherwise record `NO_CHANGE`. Production GitHub publisher and independent B separately authorized. **STOP now**.

```text
Task: TAB1-G7-W03
Goal (issue AC): #325 T04 protected native material compatibility; #5 AC4/AC5 release safety
Status: PARTIAL
Met: partial (read-only static inspection only; authentic original execution no)
Done: Source-verified native graph/core guard, isolated prefix 4-case probe, original graph scope, draft grant/main manifest/reviews and effective policy
Code: reallakshman19/Common main @ 8387c14529ce4a1173d67c4aea6c33e00633df3b | PR none, protected source unchanged
Tests: source-exact prefix expression 4/4 expected (NOT native); authentic graph native test NOT_RUN
CI: W03 NOT_RUN; earlier public #340 38150656871 historical E0 unrelated to live full-form case
Evidence: This file; native blob 804cacca; draft #316 manifest blob 98c62d48; #325 W02 issuecomment-6111382656
AC: #5 0/8 -> 0/8; #325 T04 OPEN -> OPEN
Claim: INDEPENDENT source GET, LOCAL expression probe; NONE for original native acceptance
Blocker: OWNER:D07 original approved source/issuer; EXTERNAL:PRIVATE_LAB_ACCESS; OWNER:AMEND-V32-289-PRREF-017 if actual original failure; reviewer/required CI
Next: STOP protected edit and new tests until W02 approved original vector; then native discrimination and grant-or-NO_CHANGE
```
