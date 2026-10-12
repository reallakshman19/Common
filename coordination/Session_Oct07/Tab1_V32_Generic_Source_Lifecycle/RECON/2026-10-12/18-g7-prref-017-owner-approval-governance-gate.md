# G7 R7 W03 — Owner approval recorded on proposed frozen amendment, independent release gates still open

**Chat:** 6acbb049. **Date:** 2026-10-12 Asia/Muscat. **Owner instruction in this chat:** selected text was "Approve AMEND-V32-289-PRREF-017 to permit the narrowly scoped V3.2 native PR-reference fix. Independent review and required checks will still apply. Confirm the evidence policy: Who is authorized to issue CHECKPOINT_FACTS_V1, and which CI checks and independent reviewers are required?" Owner replied **"approved"**. This is clear approval of the named narrowly scoped amendment and confirmation that review/check gates remain. It does **not** supply names of eligible CHECKPOINT_FACTS fact issuers, which GitHub CI workflows are mandatory, or two distinct independent reviewer identities. Do not manufacture or treat a generic acknowledgement as those missing policy values.

## 1. Actual scoped governance code change

**Current governance PR:** [Common #316](https://github.com/reallakshman19/Common/pull/316), original head `7e9fd7bb83d61c58295ac47ae4cd665cdb12dfc7`, base `main`, one changed file. Exact branch `governance/v32-289-xs-core-ref-grant-proposal-20261011`.

Read existing manifest `skills/Local_PR_Deliverty_v1.1/integration/frozen-v32-amendments.yaml` at original PR head Git blob **`98c62d48bd5f623f409adc25eb3103cd9ae3378e`**; original `AMEND-V32-289-PRREF-017` had `owner_authorized:false`, expressly proposed-only.

Applied the **Owner-approved governance-only** revision to **the same PR #316 branch**, commit **`8f5a47dd2e67795b78bf66732a485dba2fca07d9`**:
- Set only `AMEND-V32-289-PRREF-017.owner_authorized: true`.
- Replaced its `owner_basis` text to identify this explicit 2026-10-12 chat approval and its two exact permitted paths; label it as **engineer transcription of Owner chat, not independent GitHub Owner authentication**.
- Preserve unchanged the original `summary` and exact frozen **`allowed_paths`**:
  - `skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py`
  - `skills/engineering-pr-delivery-v3.2/tests/test_delp_projection_v32.py`
- State that **independent review, required CI policy, and merged/base-resident amendment are separate**. No issued facts, Owner source policy, generic publisher, C6 lease, V3.5 change, or production authority.
- GitHub GET readback verified exact contents of resulting YAML text, Git blob **`25fc44e168106fba76548ec1644c36fdab9a5227`**. Re-fetched PR patch: **only one file** (the governance manifest), with `+ owner_authorized: true`; no protected code/test file modified and no unrelated amendments changed.

**PR #316 new exact head:** `8f5a47dd2e67795b78bf66732a485dba2fca07d9`, still **OPEN, DRAFT, UNMERGED**, independent review submissions **0**, requested reviewers **0**. At check current Common `main@58ba6476552d1347e2bad4da9cc829e129ae7048`, base manifest Git blob **`ffe93467d8e75beebb6889f295205a8ba61bf620`** still contains **no** `AMEND-V32-289-PRREF-017`. A product code PR cannot use this unmerged/self-base grant. Frozen native source blob remains **`804cacca930e47c4528bb0d245efaf941996e4cf`** unchanged.

## 2. Actual authentic lab evidence proving need — but not acceptance

Original lab `reallaksh19/relay-v32-e2e-lab`, public repository ID **1411550807**, owner-nominated source, current main **`f0dfc590bd3fa53c50c1b645f17faf3f88e2f155`**. Released graph `governance/released-graph.json` Git blob **`fde7e1fbd0c71efb64a678206f0bc9f32e36f6c8`**, pinned/current equal. Three leaf original PR bindings all use full `reallaksh19/relay-v32-e2e-lab#8/#13/#15` and PRs merged at recorded immutable heads. Native current core checks `candidate_pr.startswith(repository_basename + "#")`, so **three of three actual source full references fail that *source predicate***; full native `project→core` original-source runtime not executed. These are physical original-source facts, not fabricated fixtures or admitted evidence.

Original lab #4/#5/#6 complete 12 comments, eight textual CHECKPOINT_FACTS_V1 mentions but **zero native-fenced eligible CHECKPOINT_FACTS_V1 blocks**; no accepted positive E, positive/adversarial same-head native replay, reviewed fact issuer or effective required CI policy. Root Common #5 AC0/8; Common #325 original T04/T05 OPEN. Current source GET access is **restored**, not a blocker.

## 3. Evidence-policy interpretation of one-word approval — no invented issuer/check/reviewer

Native DELP `delp_projection_v32.py` Git blob **`804cacca...`** defines `TRUSTED_ASSOCIATIONS={"OWNER","MEMBER","COLLABORATOR"}` as code default for potential comment authors **unless explicit `programme.fact_authors` overrides**. This is only a parser trust boundary, not an Owner-issued acceptance of any existing comment, CI results, or review. No eligible native-fenced facts presently published. The user's single "approved" authorizes the amendment but does **not** enumerate issuer accounts or select an exact adopted evidence-policy revision.

Required CI: `GET /branches/main/protection` still returns **403 Resource not accessible by integration**; ruleset absence or arbitrary workflow SUCCESS does not establish required-check policy. At exact PR #316 head `8f5a47d...` GitHub initially showed **7** workflow entries (one skipped scoreboard, two PASS native projection/v3.1, four queued), so do not claim all passed or required policy met without later refreshed, exact-head readback. Independent PR #316 submitted reviews 0; [Common #12 reviewer policy](https://github.com/reallakshman19/Common/issues/12) requires two distinct qualified actors independent of the product author, not two self-posted comments. Specific identities not designated or granted here.

## 4. Unblock order, guardrails and task accounting

1. **Already done now:** Owner approval transcribed into existing **independent governance PR #316** only; exact YAML/patch and new head verified. No main mutation or protected source/tests; no merge.
2. **Reviewer/controller:** Obtain two independently attributable qualified review verdicts on governance grant, complete effective required policy and exact-head CI; approved amendment must be merged onto Common main **separately** before native code PR can be based upon it. Current PR #316 remains DRAFT and no reviewers requested since no independent eligible identities provided. Do not self-review.
3. **Then** tiny existing frozen native `source_bound_responsibility_core` fix for current original **same repo full `owner/repo#PR`** plus short backward-compatible refs, wrong-owner/wrong repo/same basename/wrong-number negatives, native projector unchanged semantics, exact SHA/tests CI. This is conditional on approved **base-resident** grant, not granted by an unmerged PR branch.
4. **Separately W02:** qualified real independent CHECKPOINT_FACTS_V1 issuer, positive+adversarial original current fact, effective CI policy/check results, independent reviewer receipts. Missing values must be explicitly identified, not invented. Then current original native read-only source positive and stale H1→H2 rejection; no issue/PR publisher, C6/B or programme acceptance before separate gates.

**W03 TASK_EVIDENCE status PARTIAL / Met partial**, now Owner approval for proposed amendment recorded (previously missing) while independent qualified review and effective merge/base-residency are NOT COMPLETE. **W02 PARTIAL**, source currentness proven but genuine positive evidence absent. **R7 1/3 fully done** (only W01 scope), **#5 AC0/8**, #325 T04/T05 open, V3.2 production writer OFF. No test command run in this chat; CI is independent queued/running results and must not be claimed passed beyond observed jobs.

```text
Task: TAB1-G7-W03
Goal (issue AC): #325 T04 Owner-approved frozen native PR-ref patch governed under amendment 017; #5 AC4/AC5
Status: PARTIAL
Met: partial — Owner chat approval recorded on governance PR, independent review/merge/base grant and actual native fix not complete
Done: Updated PR #316 owner_authorized true and explicit limited Owner chat basis, preserved exact two allowed paths, verified new branch/patch and main grant absent
Code: reallakshman19/Common governance/v32-289-xs-core-ref-grant-proposal-20261011 @ 8f5a47dd2e67795b78bf66732a485dba2fca07d9 | PR #316 OPEN DRAFT
Tests: explicit one-manifest-only PR patch/readback -> PASS; V3.2 native compatibility tests NOT_RUN
CI: exact-head PR #316 workflow runs QUEUED/PARTIAL; required CI policy UNKNOWN due protection GET403
Evidence: This file; GitHub PR #316/commits/8f5a47dd2e67795b78bf66732a485dba2fca07d9
AC: #5 0/8 -> 0/8; #325 T04 OPEN -> OPEN
Claim: INDEPENDENT exact GitHub branch/patch readback; NONE for reviewer verdict/valid E/native fix
Blocker: PERSON:two distinct eligible independent reviewers; OWNER:D02/D03 specified eligible fact issuer/required-check policy; CI:exact-head and required-check qualification; grant not merged/base resident
Next: Reviewer and check qualification on independent governance PR; merge only with separate authorization, then protected native fix; issue qualified evidence separately for W02
```
