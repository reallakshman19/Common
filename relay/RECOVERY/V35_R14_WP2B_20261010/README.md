# WP2-B B01–B03 — R12/U3→DELP pre-admission: VERSIONED, READ ONLY, NOT ADOPTED

**Responsibility:** [issue #30](https://github.com/reallakshman19/Common/issues/30), governing [programme #5](https://github.com/reallakshman19/Common/issues/5). **Source base:** [U05 draft PR #28](https://github.com/reallakshman19/Common/pull/28) exact head `98da09e40265becee5b15d4144813b99b38c0024`. Parent original historical [old #787 AC1–AC8](https://github.com/reallaksh19/Common/issues/787). **WP0 independent review #12 missing**, no Owner policy.

## What this code actually does

`pre-admission-boundary-v1.mjs` calls the physical prior U04 `observeCrossSource` (test input), or `observeLiveCrossSource` (fixed native provider GET). U04 in turn calls the real U01 new-repo candidate/ref reader, U02 selected/required check reader and U03 GitHub issue-comment reader twice.

The candidate input is strict: repository stable id **1412133785**, exact root/leaf/PR/head/base/comment claimed SHA/author and **fact schema line** (`V32` or `V35`). V3.2 `FACTS_SCHEMA=relay-v3.2-delp-checkpoint-facts` and V3.5 `FACTS_SCHEMA=relay-v3.5-delp-checkpoint-facts` are distinct. **Declaring a schema line is not a fact translation, Owner policy or semantic-contract authority.**

This module **cannot** call a DELP projector, patch GitHub, accept evidence E, promote serialized `source_acquisition_attested:true` to an R3 WeakSet witness, choose a reviewer/Owner or mint custody/lease. The caller is forbidden to supply any policy/reviewer/Owner/admission/writer fields. It emits a reason list even when all source refs match; genuine current comment is still **an author claim**, not independent admissibility.

**Non-negotiable blockers**:
- original Owner source not authenticated;
- `EvidencePolicyVersion` not adopted;
- two independent qualified reviewer verdicts absent;
- native R12/R3 witness not transferred via serializable content;
- R14/U3 positive admission not implemented;
- one canonical programme DELP policy/projector not selected;
- managed GitHub publisher unauthorized.

It also reports actual source objections for foreign/stale/moved PR, wrong repo/issue/comment identity, unverified CI policy or failed checks. If read consistency fails, `source_digest=null`. A successful source digest is strictly a fingerprint, **not** a source credential or lock.

## Physical verification

`node --test relay/RECOVERY/V35_R14_WP2B_20261010/*.test.mjs`

The test suite uses one GitHub-shaped provider fixture and invokes *real* U01–U04 modules under an injected transport. Includes positive diagnostic control (all required source checks green, still `NOT_ADMITTED`), clean current author claim, old repo, foreign/edited issue comment, unknown protection/ruleset, failed CI/app mismatch, moving head/CI, 429 and attempts to inject credentials/policy/review flags and to launder native grade.

Separate exact-head Node22/24 × Windows/Ubuntu workflow runs; native PR/issue/comment read is initially gated pending **this new PR's own issue-comment receipt**, later enabled with exact comment id and HEAD so the new head is correctly historical. No real GitHub mutation or write permission in CI.

## What must follow

B04: actual native GitHub readback + exact-head CI/error evidence, no GREEN claim before jobs. B05: independently challenge the proposed boundary, version-policy selection by Owner, concrete R12 native in-process provenance interface, exactly one adopted DELP, stable graph and clean reviewer roles. Only a *separately authorized* project could then implement positive evidence admission and snapshot publisher. **Recovery programme AC0/8, writer OFF.**
