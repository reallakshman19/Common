# WP2-A/U05 — Integrated source acquisition regression and authority boundary

Governing [recovery #5](https://github.com/reallakshman19/Common/issues/5), [implementation plan Rev2](https://github.com/reallakshman19/Common/issues/5#issuecomment-6088631538), and [execution leaf #20](https://github.com/reallakshman19/Common/issues/20). This document describes a **candidate test result and proposed future interface**, **not** an adopted DELP schema or policy.

## Original Owner acceptance mapping

- AC3/AC4: verify cross-agent code/evidence lineage from authentic provider objects, not author assertions.
- AC5: one canonical governed snapshot and actual-next; U01–U04 do not yet produce that adopted programme snapshot.
- AC6: future live issue/PR publication must come only after independent policy/reviewer/Owner/admission gates. Writer remains OFF.
- AC8: a successor must challenge source currentness; seeing a plausible handover or SHA256 is insufficient.

## Real call graph under test

`wp2a-integration-v1.test.mjs` builds a single GitHub-shaped provider response corpus. It passes a real injected reader into **the production-candidate modules themselves**, not fabricated module outputs:
`observeCrossSource` → `observeCurrentCandidate` (U01 issue/PR/head/base refs)
→ `observeSelectedRequiredCi` (U02 native-shaped checks + classic protection + active rulesets)
→ `observeEvidenceComment` (U03 real-shaped current repository issue-comment author/body/commit)
→ repeated second U04 cycle, then bounded source-vector identity digest.

All U01/U02/U03 returns are still `CALLER_INJECTED_UNATTESTED` inside this regression. The fixture cannot grant `NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION`, Owner authentication, independent reviewer qualification or accepted evidence. Only the dedicated existing U04 live test (and this PR's separately gated smoke) can exercise actual GET acquisition. Native observations still cannot assert atomicity after the last read.

## Specific falsifiers

The bounded test set includes a nominal checked candidate, stable digest, success vs required policy UNKNOWN, failed required CI, wrong GitHub App, wrong repository ID/issue URL, foreign issue comment, edited comment, moved PR head/base, changed CI, HTTP 429 and ambiguous duplicate checks. The positive control deliberately produces `ALL_OBSERVED_REQUIRED_CHECKS_SUCCESS` as **diagnostic observation**, while the fixture still forces `evidence_admitted=false`, `programme_progress=null`, `required_ci_qualified=false`, `writer_authorized=false`. That is intentional.

## Contract needed BEFORE a positive DELP bridge

Proposed *typed and versioned* handoff boundary, not an additional reducer:

`MaterialSourceEnvelopeV1 {stable_repo_id, exact_root_leaf_pr, provider_object_refs, candidate_head, base_head, observed_check_runs, required_policy_status, comment_source_digest, comment_claimed_head, native_source_grade, source_vector_digest, bounded_observation_time, unknowns}`.

The consumer would separately require `EvidencePolicyVersion` adopted by Owner, independent reviewer/author identity source, required-vs-selected CI policy resolved, actual current candidate with no stale claim, native R3/R12 provenance/witness (not serialized flags), and versioned V3.2/V3.5 `FACTS_SCHEMA` mapping. It may then *attempt* eligibility validation through **the single adopted native DELP programme path**. Neither material observation nor a hash may be promoted straight to E.

Failure and unknown require `NOT_ADMITTED` and `programme_progress:null`. Preserve V3.2 C6 source-native path and frozen implementations. Do not edit the currently competing DELP semantics silently; WP0 review #12 and Owner policy ADR remain blocking.

## Workflow & STOP
Dedicated U05 workflow will run the whole existing U01–U05 source suite under Node22/24 × Windows/Ubuntu. All jobs checkout the exact event head without persisted credentials. The U05 native full-chain smoke is gated until a PR-specific issue-comment evidence receipt exists, because the older comment on PR #27 must not be passed as the new PR's source. The smoke will use **read-only GitHub requests only**; partial/racing data should refuse the vector, not invent success.

Success of tests means regression evidence for the Coder source candidate, not acceptance of AC1–AC8. Local/reviewer/publisher/merge authority remains elsewhere. No production write, no protected source mutation, no blind Runner B or policy adoption is attempted here.
