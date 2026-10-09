# WP2-A/U04 — one non-authoritative, read-only cross-source vector

Parent [recovery #5](https://github.com/reallakshman19/Common/issues/5), bounded [WP2-A leaf #20](https://github.com/reallakshman19/Common/issues/20), preceding [U01–U03 draft PR #21](https://github.com/reallakshman19/Common/pull/21). U04 is a separate stacked draft to avoid modifying the overlapping PR21 source branch.

**Original owner outcome:** one source-current graph/snapshot feeding lifecycle projections. **This U04 is not that accepted snapshot.** It only checks that three already implemented, independent read-only observers refer to the same CURRENT GitHub source candidate and verifies that an older TASK_EVIDENCE comment remains historical evidence. No DELP invocation or programme P/E, no Owner authenticating, reviewer acceptance or publication.

## Physical flow
`observeLiveCrossSource` imports the actual U01 `observeLiveCurrentCandidate`, U02 `observeLiveSelectedRequiredCi`, and U03 `observeLiveEvidenceComment` without editing or reimplementing them. A caller-injected `observeCrossSource` is only test-grade. Each pass calls U01 → U02 → U03 in that order; each existing module internally obtains TWO native reads. U04 repeats the entire triplet (six stage calls, approximately 68 provider GETs) and requires identical canonical inputs and observer output hashes across its two passes.

The source vector records exact new-repository ID, root/leaf, current PR number/head/base, U01 candidate digest, U02 observed selected/required CI digest and policy grade, U03 issue-comment receipt digest, original claimed SHA and currentness. If any source fails, moves or cannot be reconciled, result is `source_consistent:false`, and contains no status, authority or progress. The digest is a snapshot fingerprint, never an attestation or lock.

**Trust barriers:** an injected reader never becomes native because of a caller flag; the three stage results must carry the expected source grade and explicitly deny `evidence_admitted`, `writer_authorized` and progress. U02 selected-green with required policy UNKNOWN cannot be called PASS. U03 a previously published comment from an older SHA is recorded as `CONSISTENT_HISTORICAL_EVIDENCE_ONLY`, not current accepted E. An exact-current `TASK_EVIDENCE` comment would still be only `CONSISTENT_AUTHOR_CLAIM_ONLY`, not admission.

**Concurrently moving data:** GitHub does not provide an atomic multi-object read. U04's repeated source observations can identify movement but cannot prove the PR was locked after the final read. Consumers must refresh before relying on this digest; no downstream publisher is connected.

## Verification
- `node --test relay/RECOVERY/V35_R14_WP2A_20261010/cross-source-vector-v1.test.mjs`
- Synthetic positive and negative sources, explicitly downgraded `CALLER_INJECTED_UNATTESTED`.
- Dedicated Node22/24 × Windows/Ubuntu hosted source suite.
- Native Windows/Ubuntu smoke must be enabled **only after PR22 has its own GitHub-issued TASK_EVIDENCE comment**, with a cited commit and correct current PR URL; another PR's comment cannot be reused as current.
- Native U04 checksum may return a deliberate source race if CI or GitHub comment moves; report the exact failure and retry at the same immutable source, never claim invented green.

## Still blocked
U05 native system regression and acceptance; WP0 two independent reviewers #12, historical R12 source review #869, Owner original/private source and evidence policy, single adopted DELP reducer, authorized issue/PR publisher, and independent Runner isolation/custody. Programme AC0/8. Separate authors' U01–U03 source is not touched.
