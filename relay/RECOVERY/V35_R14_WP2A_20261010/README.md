# WP2-A/U01 — read-only current candidate observation

Parent: [#5](https://github.com/reallakshman19/Common/issues/5), [rev2 plan](https://github.com/reallakshman19/Common/issues/5#issuecomment-6088631538); leaf [#20](https://github.com/reallakshman19/Common/issues/20).

The module `current-candidate-material-v1.mjs` checks a fixed current-repository ID and name, open root and leaf issue identities, native PR head and base roles, and exact GitHub branch refs. It reads all six provider objects twice, rejecting moved, malformed, missing or foreign sources. A canonical source-vector SHA256 is a content fingerprint, **not** an attestation or authorization.

The injected-reader entrypoint always returns `CALLER_INJECTED_UNATTESTED`. The live entrypoint reuses the fixed read-only `nativeGithubGet` from M0 draft #9. The candidate branch is intentionally stacked on M0 exact head `cc5403b17feed2a8590d0cff9f4168061bcd347c`; no production consumers have been changed.

Scope and limits: U01 only. `ci_required_status=UNKNOWN`, `task_evidence_status=NOT_CHECKED`, `evidence_admitted=false`, `programme_progress=null`, `writer_authorized=false`; no Owner/reviewer/lease validation. Later U02–U05 must separately acquire required-versus-selected CI, original current TaskEvidence, atomic-currentness policy, and independently tested live integration. No status/PR writer or canonical DELP admission until WP0 issue #12 review and Owner policy decisions.

Local tests: `node --test relay/RECOVERY/V35_R14_WP2A_20261010/*.test.mjs`; 16 synthetic positive/adversarial cases including wrong repository, historical URL, PR-as-issue, wrong head/base, H1→H2, 403/429. They are not live provider proof. Programme AC0/8.
