# WP2-A/U01–U02 — read-only current candidate and CI material

**Authority:** [parent #5](https://github.com/reallakshman19/Common/issues/5), [Rev2 plan](https://github.com/reallakshman19/Common/issues/5#issuecomment-6088631538), [leaf #20](https://github.com/reallakshman19/Common/issues/20), draft PR #21. Original Owner programme remains AC0/8, review gate #12 open, writer OFF.

## U01 current source identity (separate)
`current-candidate-material-v1.mjs` observes current repo ID, open root/leaf GitHub issue kinds and PR head/base refs twice. `observeCurrentCandidate` with injected reader never authenticates. Native path reuses M0 exact-head restricted GET transport on PR #9. A source-vector SHA256 does not confer original Owner/reviewer/CI/DELP or writer authority.

## U02 selected CI vs required policy (new)
`required-ci-material-v1.mjs` has a **separate** injected-reader and fixed read-only GitHub REST path. Its `observeLiveSelectedRequiredCi` reads:
1. Current PR exact head/base/repository binding.
2. `GET commits/{SHA}/check-runs?per_page=100` and `GET commits/{SHA}/status?per_page=100` — **selected / observed check material**, not proof of requirement.
3. Classic `GET branches/{base}/protection/required_status_checks` and active applicable `GET rules/branches/{base}` (including inherited branch rulesets) — **requirement provenance**, not permission to merge.
4. Repeats selected check/policy reads and candidate PR read. Rejects candidate/head/policy/CI movement, invalid shapes, incomplete/paginated responses, wrong app IDs and ambiguous duplicate check names.

If a protected-branch API returns 404/403, rules are unreadable, or classic checks and rules cannot both be established, **required_check_policy=UNKNOWN and required_checks_result=UNKNOWN**, even if selected checks are green. When no required checks are observed with both policies readable, result is `NO_REQUIRED_CHECKS_OBSERVED`, explicitly **not** `ALL_OBSERVED_REQUIRED_CHECKS_SUCCESS` or production mergeability. Positive `ALL_OBSERVED_REQUIRED_CHECKS_SUCCESS` is only a diagnostic of matching source records, not independently qualified evidence E; in particular neutral/skipped/duplicate/incomplete runs are not treated as valid pass.

**No external caller input or reader can mint a native grade**: injected reader always emits `CALLER_INJECTED_UNATTESTED`. Source SHA256 fingerprints are not access/custody grants. All outcomes hard-code `evidence_admitted:false`, `programme_progress:null`, `writer_authorized:false`, `owner_authenticated:false`, `reviewer_qualified:false`. No production DELP, R3/R12/R14, Runner, Local or GitHub title publisher was changed.

## Test protocol
`node --test relay/RECOVERY/V35_R14_WP2A_20261010/*.test.mjs`: U01 16 + U02 22 case declarations, including positive synthetic controls, failures, pending, ruleset/classic unions, app pinning, old-repo data, H1→H2, 403/429, and missing protection / selected-but-not-required green. Dedicated workflow runs Node 22/24 × Ubuntu/Windows and native read-only U01/U02 GitHub smoke on both OS. Read HEAD and job logs before calling any test hosted-green. These are source/fact observations only.

## Missing follow-up responsibilities
U03 native current-repository TASK_EVIDENCE issue-comment source and author/readback; U04 aggregated currentness/ref/review-policy reconciliation; U05 end-to-end property/regression tests. WP0 external independent review #12 + old R12 review #869 and Owner policy/privacy decisions remain explicit holds before any positive evidence admission, one canonical DELP snapshot, live publisher, merger or Runner custody transfer.

## U03 — native GitHub TaskEvidence comment material (2026-10-10)
`task-evidence-comment-v1.mjs` adds a separate **read-only** observation of the current `reallakshman19/Common` repository (stable ID 1412133785), parent #5, leaf #20, PR #21, and provider-issued comment/author/commit identities. It binds a comment to the leaf through its native `issue_url` and `html_url`, requires the actual author account returned by GitHub, verifies the full claimed SHA via independent `commits/{SHA}` GET, and checks the author-text anchors `TASK_EVIDENCE`, `Tested HEAD` and the current PR URL. It reads all six objects **twice**, and rejects edits/head moves between rounds.

**Trust boundary:** the comment body and expected author login are agent/caller claims, *not* Owner-source authentication or qualified external reviewer findings. A native `material_observed:true` proves only GitHub comment/source identities and their content at the time of double GET. A pinned older comment can remain `material_observed:true` but has `source_currentness:STALE_CANDIDATE_HEAD`, and is **never** admitted to evidence. With an injected reader, provenance is always `CALLER_INJECTED_UNATTESTED`. Failed/partial/rate-limited GET returns `UNKNOWN` and no source receipt. Original Owner/reviewer/DELP/progress/lease/writer flags stay negative/null.

### Native fixture deliberately exercises a stale prior source
`task-evidence-comment-v1.cli.mjs` reads provider-issued [leaf #20 U02 comment 6089024942](https://github.com/reallakshman19/Common/issues/20#issuecomment-6089024942), pinned to `f5a30225aea6adde20cef67ca5ab1111a11c3800`. Since PR #21's current code head has advanced, the **expected correct positive provider read** is `material_observed:true`, `source_grade:NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION`, `source_currentness:STALE_CANDIDATE_HEAD`, `body_claim_grade:CLAIMED_TEXT_ONLY`, `evidence_admitted:false`. The CLI exits nonzero if this bounded observation fails; this is not a production current-evidence PASS.

`task-evidence-comment-v1.test.mjs` contains 25 positive and adversarial tests: provider IDs and issue-kind swaps, historical comment URL, forged actor, copied PR binding, HEAD duplication/forgery, unresolved commit, 403/404/429, PR push/comment edit races, and attempts to promote injected authority. The dedicated GitHub workflow now executes U01+U02+U03 tests across Node22/24 and Windows/Ubuntu, plus native U03 on both OS.

### Still not implemented or accepted
U04 is a single **re-observed combined PR/CI/comment source vector** with explicit generation/policy and CAS-style currentness refusal; U05 requires integrated regression/acceptance checks. This module does not read a live task-evidence *approval*, does not qualify the commenter, and cannot invoke a canonical DELP projector. Reviewer [#12](https://github.com/reallakshman19/Common/issues/12), Owner evidence/privacy policy and Runner custody remain unresolved. Parent AC0/8; GitHub publishing writer OFF. Avoid creating artificial current-head comments solely to turn the test green.
