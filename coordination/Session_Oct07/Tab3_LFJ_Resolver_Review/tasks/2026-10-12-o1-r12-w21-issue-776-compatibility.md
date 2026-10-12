# TAB3-O1-R12-W21 — #60 migrated #776 Match-1 acceptance compatibility

Outcome: O1 (prerequisite #60, original input → valid Match-1 → export authority)
For the user: Candidate regression confidence restored for candidate-click and typed-manual Match-1 acceptance, stale source review instead of silent fallback. No public UI released.
Proof: https://github.com/reallakshman19/3D_Converters/actions/runs/38285854891 — focused-regressions + wsw-browser-e2e **2/2 hosted jobs SUCCESS**.

## Authorized scope and backup
Owner chat `6acd0d5f`: "ok proceed" after requested temporary exclusive #60 writer transfer. Temporary custody announced https://github.com/reallakshman19/3D_Converters/issues/60#issuecomment-6129440465; ONLY `tests/xml-cii-issue-776-match1-acceptance-paths.test.mjs`. Pre-edit backup branch `backup/60-776-pre-fix-20261012-6acd0d5f` points to `31b8bac1e67558d9375a96c8d2b79cd290661ec9`. Neither protected engine, renderer, O1 source, #98 or #203 touched. Existing GitHub immutable commit also retained. No product merge/deploy.

## Root cause
Hosted #776 former red run https://github.com/reallakshman19/3D_Converters/actions/runs/38284889927: sole failing focused Match-1 test asserted obsolete literal `withXmlCiiRigidWeightMatch1(clean, candidates, proposalMeta)`, and also an obsolete automatic `withXmlCiiRigidWeightFinal(withXmlCiiRigidWeightMatch1(...), manual)`. Actual current `xml-cii-adapted-weight-match-v2.js` explicitly stages `{...candidates,...manual}` into Match-1 and calls `persistConfig`, never silently grants Final Match-2; `weight-match-renderer.js` dispatches candidate selection and typed manual input as explicit acceptance with distinct provenance. Existing Match-1 core provenance, stale validation and downstream run/legacy suppression tests and browser E2E already positive. Six adjacent legacy WSW baseline failures were on both base and PR head, classification `baseline-only-failures`; not newly introduced or waived.

## Implemented
One commit only on original draft PR #228 branch `lfj/226-t3-main-worker-intake-20261012`:
`42c37e2a610a1c92ee8e0053847badcbca0da6fd`.
Compare preceding `31b8bac1` → new `42c37e2` = one test file, +115/-2. Replaced static retired API/Final assertions with preserved current-path guards and executable direct core contract:
- unaccepted proposal gives zero Match-1 accepted records;
- positive candidate and typed-manual provenance accepted into Match-1 at distinct selected values;
- absent auto-Final, manual final must be explicitly accepted separately;
- changed original length, Rating and master revision invalidate affected entries, no fallback to retained 77/88 kg legacy weight, no auto rerank.
No runtime source/renderer changes, no assertion weakened without replacement.

## New-hosted proof
Run https://github.com/reallakshman19/3D_Converters/actions/runs/38285854891: `focused-regressions` PASS (focused **48/48**, C03 rigid type **26/26**, same adjacent WSW six historical fails head/base classified baseline-only), `wsw-browser-e2e` PASS including 10k/50k/100k browser scale; GitHub workflow 2/2 jobs SUCCESS.
#118 predecessor repair V4.1 still PASS new head run https://github.com/reallakshman19/3D_Converters/actions/runs/38285854344.
As of assessment, integrated #228@42c37e2 has 43 workflow runs 17 SUCCESS/17 FAILURE/9 PENDING (O1 W10/W15 in progress). No global PASS claim or release. #98 and #203 still owner-controlled.
Full TASK EVIDENCE published with provider exact readback https://github.com/reallakshman19/3D_Converters/issues/60#issuecomment-6129484113.

## Task contract
Task: TAB3-O1-R12-W21
Goal: #776 bounded Match-1 integration regression
Status: DONE, #776 workflow green
Met: YES
Done: one-file acceptance test correction, real runnable source-bound positive/negative assertions
Code: `42c37e2a610a1c92ee8e0053847badcbca0da6fd`
Tests: focused 48/48, C03 26/26; 2/2 jobs
CI: #776 GREEN; global 17 FAILED, 9 pending at observation
Evidence: https://github.com/reallakshman19/3D_Converters/actions/runs/38285854891
AC: 2/2 #776 hosted jobs
Claim: #776 release gate green on PR #228 head only
Blocker: #98/#203 independent release checks
Next: separate next task for #98 with own authorization boundary, then #203. Owner only final merge/deploy.
