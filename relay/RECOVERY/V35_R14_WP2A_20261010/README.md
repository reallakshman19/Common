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
