# G7 R7 W03 re-entry — current ORIGINAL lab graph establishes full owner/repo PR prefix incompatibility; protected edit HOLD

**Chat=6acbb049. Task=TAB1-G7-W03. Owning issue [#325](https://github.com/reallakshman19/Common/issues/325); parent #289; programme #5.** G1 final [BuddyRunner v1.6 handover](https://github.com/reallakshman19/Common/issues/325#issuecomment-6111153465) final direction. G7 R7 plan [6111234594](https://github.com/reallakshman19/Common/issues/325#issuecomment-6111234594). User has now made original lab public and explicitly identified `reallaksh19/relay-v32-e2e-lab` as original. Physical W02 source receipt: `RECON/2026-10-11/16-g7-public-original-source-restored-w02.md`, Git blob `7b1fdfb6505bb3693bdcb856df554be873a202d3`; exact `main@f0dfc590bd3fa53c50c1b645f17faf3f88e2f155`. **W03 STATUS PARTIAL: real current graph path compatibility defect can now be evaluated from authenticated GET, protected code remains not authorized.**

## First actual source boundary, before any artificial fixtures

**Original lab** `reallaksh19/relay-v32-e2e-lab`, numeric repo ID **1411550807**, public/current default `main@f0dfc590bd3fa53c50c1b645f17faf3f88e2f155`. Native released graph `governance/released-graph.json`, **Git blob `fde7e1fbd0c71efb64a678206f0bc9f32e36f6c8`**, read from pinned ref and current `main` repeatedly, byte-identical at git-blob identity. Root `reallaksh19/relay-v32-e2e-lab#1`, original three leaves:
- Leaf `reallaksh19/relay-v32-e2e-lab#4` → original **full** `reallaksh19/relay-v32-e2e-lab#8`; actual PR #8 MERGED, source head `8ced7c13d5e9f9ba6870899ae8c62ec5501011b4`;
- Leaf `reallaksh19/relay-v32-e2e-lab#5` → original **full** `reallaksh19/relay-v32-e2e-lab#13`; actual PR #13 MERGED, source head `14de12587d5b5b88cee65b0fde447833be92e7c2`;
- Leaf `reallaksh19/relay-v32-e2e-lab#6` → original **full** `reallaksh19/relay-v32-e2e-lab#15`; actual PR #15 MERGED, source head `073016d244becf84e06fd2e72a8f72c2d964f55c`.

**Native frozen authority:** `skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py`, exact Git blob **`804cacca930e47c4528bb0d245efaf941996e4cf`**. Its graph `validate_graph` stores `primary_pr` and calls `parse_ref`, allowing actual graph's full owner-qualified bindings. But `source_bound_responsibility_core` line 4181 onward rejects candidate string unless it starts with `str(indexed["programme"]["repository"]).rsplit("/",1)[-1] + "#"` and raises `RESPONSIBILITY_CORE_MATERIAL_BOUNDARY`.

For this **actual selected original graph** native prefix evaluates to `relay-v32-e2e-lab#`, whereas each of the original full strings begins `reallaksh19/`. Therefore **3/3 actual current released graph primary PR strings fail this exact guard condition**. This establishes a deterministic, **current authentic-provider-source incompatibility** at the source-bound material boundary **conditional on reaching this guard with a valid projection**; it is not merely a hypothetical wrong-format synthetic fixture. The runtime's separate `project` and full `source_bound_responsibility_core` were **NOT executed** in this chat; do **not** report a native test FAIL, positive E or exact full error raised by an executed original H1/H2 computation. Earlier original public old-Common graph `d35019b...` with short `Common#` refs did not exercise this case. Source compatibility regression must preserve short `repo#PR` and accept exact same-owner full `owner/repo#PR`, while rejecting same basename with wrong owner, wrong repo, wrong bound PR number, malformed tail, stale source, caller-forged graph and mismatched candidate head.

**Existing integration** #326 `relay/INTEGRATION/V32_325_GENERIC_SOURCE_20261011/generic_current_source.py` blob `75287ef9ace8fea0f45d7b97d4bd9bde974ae789` delegates `project` then native core and translates this error to `NATIVE_RESPONSIBILITY_CORE_MATERIAL_BOUNDARY`, but draft unmerged read-only integration is not an authorized publisher. No second projector/adaptor may be created; fix only approved protected native owner.

## Authorizing gate is still independent of source visibility

Main/base `skills/Local_PR_Deliverty_v1.1/integration/frozen-v32-amendments.yaml` **blob `ffe93467d8e75beebb6889f295205a8ba61bf620`** lacks `AMEND-V32-289-PRREF-017`. Draft [Common PR #316](https://github.com/reallakshman19/Common/pull/316) head `7e9fd7bb83d61c58295ac47ae4cd665cdb12dfc7`, OPEN DRAFT and UNMERGED, 0 submitted formal reviews at last current poll; proposed manifest blob `98c62d48bd5f623f409adc25eb3103cd9ae3378e` explicitly sets `owner_authorized:false` for `AMEND-V32-289-PRREF-017`. It names only frozen native `delp_projection_v32.py` and test `test_delp_projection_v32.py`. The frozen grant must be Owner-approved, independently reviewed, merged and **already present at the eventual code PR base**. Branch policy GET returned **403**; unknown checks cannot be waived. The public lab repository is read-only to this connected actor, and making it public grants **neither** a Common frozen-file edit nor license to create checkpoint facts or mutate live issue/PR state.

**W03 result:** concrete source-level **3/3 original lab full-ref guard incompatibility identified**, but **Met partial**, native runtime exact-head positive/negative + patched tests NOT_RUN; #325 original T04 OPEN, root #5 AC0/8, V3.2 production writer OFF, no protected file change or PR.

## Smallest permitted critical-path continuation

1. Owner explicitly approves **exact** `AMEND-V32-289-PRREF-017` for frozen native source/test, independent review plus effective checks; merge independent governance amendment on Common main **before** basing any real code/test PR on it. **Do not self-approve or modify protected path in a branch containing its own grant.**
2. After grant, make a **minimal same-repo PR reference parser** repair in existing native source; full owner/repo#PR actual lab positive, short historic positive, foreign owner/same basename, foreign repo, wrong number, wrong graph and stale candidate negatives; unchanged native P/E/D/input digest; exact-head focused and freeze regression CI. The actual adopted Owner graph never needs to be modified/rewritten to match a broken prefix.
3. W02 independently qualified source-native positive E remains blocked on genuine eligible `CHECKPOINT_FACTS_V1` issuer and effective required checks/reviews: full current graph+material alone cannot make E>0. Only following these independent gates should the native read-only vertical be replayed. Real root/child/PR live publication/readback and independent C6/B custody need their own permissions later.

### TASK_EVIDENCE — W03 re-entry
```text
Task: TAB1-G7-W03
Goal (issue AC): #325 T04 native full owner/repo PR compatibility for original real graph; #5 AC4/AC5
Status: PARTIAL
Met: partial — deterministic original source binding incompatibility found, protected fix not authorized
Done: Fetched true public original graph at pinned/current SHA and full primary refs #8/#13/#15; demonstrated all 3 fail native basename-prefix requirement; verified frozen grant unresolved
Code: reallakshman19/Common main native Git blob 804cacca930e47c4528bb0d245efaf941996e4cf | Common PR #316 draft 7e9fd7bb unapproved; no code changes
Tests: real current source ref prefix discrimination 3/3 fail guard as expected (source exact condition); full native positive/negative -> NOT_RUN
CI: NOT_RUN this task; effective required-check policy UNKNOWN
Evidence: This file; original current graph Git blob fde7e1fbd0c71efb64a678206f0bc9f32e36f6c8
AC: #5 0/8 -> 0/8; #325 T04 OPEN -> OPEN
Claim: INDEPENDENT provider/source GET; LOCAL deterministic guard evaluation; NONE for native runtime or qualified E
Blocker: OWNER:AMEND-V32-289-PRREF-017 base-resident frozen edit grant and independent reviews/checks; W02 genuine independently eligible CHECKPOINT_FACTS
Next: Request explicit frozen-path governance grant and qualified native evidence issuer/check-policy, then tiny existing-native fix and read-only same-head full-positive/hostile tests
```
