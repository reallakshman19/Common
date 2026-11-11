# WP2 — Zero-exit, read-only GitHub observer

Owner issue: https://github.com/reallakshman19/Common/issues/391
Baseline: Common main ae3c0139a46bbffcc03d9a50f3d9067d59d78633
Current work: an independent additive main-rooted draft, with no imports from still-draft PRs #392 and #393.

## Aim and scope

The incoming engineer must be able to reconstruct verified repository progress without predecessor chat or final LOG. The observer establishes a source-bound GitHub snapshot, NOT a 12-section engineering report, source-code ownership, original-input verification, acceptance, Owner authorization, MCDA ranking, or automatic implementation.

Provider collector: adapters/github.py; v3.6-specific advisory link parser: adapters/v36.py. No v3.6 core, BuddyRunner, Software MCDA, Workflow Intelligence, monitoring or Dashboard files changed. A small PR/push-only (NOT scheduled) credential-free workflow runs offline tests with contents:read.

## Verified boundaries

- Explicit repository and issue number; canonical repo and default HEAD read from live provider.
- Exact PR head/base, draft/open/merged state, changed-file inventory and exact-head check-run observations. A passing check-run is not Owner acceptance.
- Paginated issue comments with author, provider id, time, SHA-256 of body and lexical marker presence. Public projection strips comment text and raw index marker strings.
- Fail closed for missing/contradictory source, bad pagination, wrong issue or foreign identity, duplicate comments, head drift during collection or wrong check SHA. Optional check-run 403 is UNKNOWN, not green.
- No outgoing agent participation, final handover, private chat, secret or local WIP assumed.
- Read-only GET transport, no write verbs, bounded response/pages, redirect blocked before token forwarding.
- v3.6 index lexical pointers are INDEX_LINKS_OBSERVED_NOT_VERIFIED and never child acceptance. Existing snapshot_v36.py remains semantic owner.
- Public record always execution_authorized=false, owner_acceptance_verified=false, original_fixture_sha256_verified=false.

## CLI and exact test command

~~~bash
python skills/relay-onboarding-rwi/adapters/github.py --repo reallakshman19/relay-v36-e2e-lab --issue 1 --pr 4
python skills/relay-onboarding-rwi/adapters/github.py --repo reallakshman19/XML_Compare_Utilities --issue 102 --pr 103
python -m unittest discover -s skills/relay-onboarding-rwi/tests -p 'test_provider_wp2.py' -v
~~~

Public CLI prints redacted onboarding.provider-snapshot/v1, not raw issue contents. Local runtime has no external DNS and the new CLI was NOT executed against live GitHub in this work. GitHub connector separately fetched the provider pilot refs and confirms actual current state.

## Pilot P-A: v3.6 accepted lab

- reallakshman19/relay-v36-e2e-lab parent #1: https://github.com/reallakshman19/relay-v36-e2e-lab/issues/1
- main c400b70e4641abf2cda79aa626b77e793f38e107
- PR #4 OPEN/DRAFT, head 61a71a038cca56507040bdb365edf76a9c0d2469, base 343bd50dd573ddf4418785fa6a05d0707a011c5a, 2 changed files
- Unique observed managed index comment https://github.com/reallakshman19/relay-v36-e2e-lab/issues/1#issuecomment-6116254353 names V36-1-PLAN-01 with children #2 and #3. Its presence is not independent proof.
- Separate Owner acceptance lives in Common #341 PLAN-07 https://github.com/reallakshman19/Common/issues/341#issuecomment-6119409109, not inferred from E2/2 title.

## Pilot P-B: cross-repo live engineering

- reallakshman19/XML_Compare_Utilities issue #102: https://github.com/reallakshman19/XML_Compare_Utilities/issues/102
- main 040f2f88b54a746808486615230e5a8625d04527
- PR #103 OPEN/DRAFT/UNMERGED, head a794f7bc8438faa67b35b3ac2d110da06436caa9, base 040f2f88b54a746808486615230e5a8625d04527, 44 changed files. Head moved since WP0 b1bb7d0dde39fbbf7e8c023844faca4d66be5650; older head-bound evidence is stale for this candidate.
- Original Owner #69 https://github.com/reallakshman19/XML_Compare_Utilities/issues/69 cites Benchmark/S1.CII, S2.CII, S3.CII and T.CII hashes; actual bytes were NOT downloaded/rehashed in WP2. Partial TEXPECTED postimage documents 36 semantic deltas (35 REPLACE, 1 CREATE), not full original Owner Phase 2 golden and not >=70% acceptance.
- Project AGENTS requires READ_ONLY engineering-critical takeover and Appendix A independent qualification before mutation; an ONB report cannot bypass it.

## Qualification

The new tests/test_provider_wp2.py defines 31 synthetic offline cases. They test wrong target, moved exact heads, duplicate/stale source evidence, pagination and 403, ambiguous v3.6 index, cross-repo child links, false green acceptance, absent predecessor exit and public body/marker redaction. They are implemented and **31/31 passed** on the exact-head hosted Actions run https://github.com/reallakshman19/Common/actions/runs/38762019597 at revision 8e5f93bf68b507b7c204424b62392d381d6b2c68; the same run independently executed credential-free live read-only CLI checks against P-A and P-B, with source heads and execution_authorized=false asserted. A prior public smoke exposed a REST allowlist bug (repo root metadata GET rejected); the allowlist and negative regression tests were corrected before the success receipt. This does NOT provide independent review, Owner approval or a 12-section handover.

Future WP3–WP5 must independently establish original Owner amendments, changed-function/source-code architecture, real original fixture custody, twelve-section technical handover and approved bounded KEEP/IMPROVE analysis. Neither PR merge nor a workflow run is automatic Owner release.
