# WP5 — Full 12-section source-referenced handover and independent verifier

Owner issue: https://github.com/reallakshman19/Common/issues/391
Future UI consumer: https://github.com/reallakshman19/CoordinatorLandingpage/issues/21
Team Protocol: https://github.com/reallakshman19/CoordinatorLandingpage/issues/7

## Original problem and practical result

The Owner wants one complete, standalone engineering handover — not PR statistics — that explains WHY a project exists, the actual code flow and changes, decisions/rejected approaches, original input/golden/benchmark, authentic CI/test status, known failure and one precise successor starting verification. It must survive an unannounced predecessor exit with no private chat or final LOG. The later RWI step may recommend one bounded, implementable root-cause improvement if that better preserves the Owner outcome; KEEP is valid and score/approval must not be invented.

WP5 writes three synchronized files by a pure compiler: ONBOARDING.md, onboarding-manifest.json and onboarding-verdict.json. It does not modify source repos or trigger an engineering generator. The independent verifier recomputes the packet/report/manifest digest chain, checks the 12 section headings, 22 evidence-claim identities, explicit UNKNOWN and authority gates, and can re-fetch actual GitHub main and candidate PR HEADs immediately before the handover is used.

## Exact work now in this PR

Files new and limited to the new ONB skill directory plus one PR-scoped test workflow:

- reporting/compile_report.py — strict typed input parser and 12-section complete Markdown renderer; deterministic SHA-256 binding to input/manifest/verdict. Source text is quoted JSON to prevent untrusted headings or embedded instructions from escaping its data context.
- reporting/validate_report.py — independent parser and digest/section/evidence/authority validator (no compiler import), plus public, token-free read-only current GitHub default-branch and selected PR-head checks; stale, unavailable or tampered input is BLOCKED.
- reporting/fixtures/onb391-real-public-input.json — substantial public-source-referenced report for Common #391's actual ONB project with 12 sections, 22 individually linked or UNKNOWN claims, four CII original input custody entries and three exact-head test receipts. Not a synthetic source-only collection; authentic bytes/runs were verified earlier, but current input claims are SOURCE_REPORTED / UNKNOWN, not Owner VERIFIED.
- tests/test_report_wp5.py — 35 unit and negative tests for all section, citation, source, manifest, drift, RWI, privacy, Owner authority and tampering boundaries.
- .github/workflows/onb-rwi-wp5.yml — no schedule, PR/push only, contents:read, no tokens. Builds the real 12-section packet, verifies it independently, reads three external repository HEADs plus five current draft PR HEADs from GitHub, and uploads the public outputs as one review artifact for 30 days.

All files are independent of unmerged ONB WP1a #392, WP1b #393, WP2 #394, WP3 #395 and WP4 #396; the branch is directly rooted at Common main ae3c0139a46bbffcc03d9a50f3d9067d59d78633. Cross-WP installation/integration is not yet proven or merged, and the two-/three-pass v3.6 delivery generators are untouched.

## Actual generated outputs and hosted receipt

Hosted source at head 3bc16aa2c19f113b7b267b7c10fb8bce4b90a610:

https://github.com/reallakshman19/Common/actions/runs/38776193538

Public output package (ONBOARDING.md, onboarding-manifest.json, onboarding-verdict.json):

https://github.com/reallakshman19/Common/actions/runs/38776193538/artifacts/11992894898

Observed from hosted job logs:
- 35/35 offline Python focused tests PASS.
- 12/12 substantive numbered sections validated, 22/22 cited/unknown claim IDs synchronized.
- Input/source packet SHA-256: c74cbb1266dc669e77a15e77a0fed460db3e7f7e364b9484d7f20f6c6366da56.
- Rendered ONBOARDING.md SHA-256: c080d74c157411411cc65e959ba7b3ecc1c4d42f742c641af25676102af90815.
- Manifest canonical SHA-256: 46bd537e31f06af7f9461d20672b0f169cb6756e86592e5709e842191d8de204.
- All three main HEADs and all five ONB draft PR heads matched the exact stored revisions at the hosted UTC observation.
- Verdict = BLOCKED, execution_authorized = false, Owner approval = false, RWI = NOT_EVALUATED.
- SHA-256 of uploaded zip artifact: 9b8fd4c7926141716c8c7bedb638bef400da94a8df4a392d581d3fd9ef953b9c. Artifacts are not public-product deployments and have limited retention.

Commands to regenerate and validate from a future checkout:

    python -m unittest discover -s skills/relay-onboarding-rwi/tests -p 'test_report_wp5.py' -v
    python skills/relay-onboarding-rwi/reporting/compile_report.py --input skills/relay-onboarding-rwi/reporting/fixtures/onb391-real-public-input.json --out /tmp/onb-output
    python skills/relay-onboarding-rwi/reporting/validate_report.py --input skills/relay-onboarding-rwi/reporting/fixtures/onb391-real-public-input.json --report /tmp/onb-output/ONBOARDING.md --manifest /tmp/onb-output/onboarding-manifest.json --verdict /tmp/onb-output/onboarding-verdict.json --live

## What is still NOT proved

- Current GitHub revisions and Git byte hashes are real evidence, but alone do not authenticate an Owner approval, a complete PS-to-SL mapping, a semantic code path or a user-visible accepted product result.
- XML Compare original four files were SHA-verified by WP4; the ordered source-set aggregate digest recipe, complete Owner functional golden and 70% correspondence acceptance remain unproven. The 36-delta TEXPECTED postimage is partial.
- Only the ONB module's technical source history is currently reported. No independent reviewer has established all runtime entrypoint→owning layer→downstream call-edges, complete product acceptance, or full integration of still-draft workpacks.
- The full handover can be *generated* despite those gaps, and must display BLOCKED explicitly. An unavailable or stale provider cannot be overridden by editing the manifest.
- RWI policy/rubric and change eligibility are not yet Owner-approved, so no high-ROI score, change proposal or execution authorization is emitted.
- CoordinatorLandingpage remains an existing separate site with its own actor/registry/protocol gates. No dashboard revamp, core protocol changes, agent scheduler, new coordinator or private-data projection is authorized.

## Exact next work

1. Obtain independent review of WP5's CLI security, source completeness, manifest/verdict tamper resistance and the generated real twelve-section text at the exact final head.
2. Reconcile WP1a–WP5 source contract compatibility and integrate a single reviewed read-only ONB entrypoint without stacked unauthorized merges.
3. Independently trace one real program entrypoint, owning layer, and downstream consumer at pinned source and validate against the complete Owner functional oracle, rather than relying on Git SHA and PR descriptions alone.
4. Calibrate and approve the bounded RWI KEEP-versus-IMPROVE noncompensatory Owner intent gate and the existing Software MCDA interface; otherwise remain NOT_EVALUATED.
5. Any future status-only handoff into CoordinatorLandingpage must be separately admitted by its #21/#7 owners and use its existing public read-only ingestion seam.

No independent merge/release permission or product production qualification is claimed.
