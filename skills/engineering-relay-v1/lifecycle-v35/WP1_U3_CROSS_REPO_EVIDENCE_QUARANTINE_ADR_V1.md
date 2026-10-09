# WP1/U3 — native cross-repository evidence reconciliation: quarantine first

**Candidate only · NOT ADOPTED · recovery parent [#5](https://github.com/reallakshman19/Common/issues/5) · independent review [#12](https://github.com/reallakshman19/Common/issues/12).**

## Source grounding and why a typed boundary is required

Original R14 [old #787](https://github.com/reallaksh19/Common/issues/787) controls the historical programme requirement. Old repo `reallaksh19/Common` provider ID `1207996454` and new repo `reallakshman19/Common` ID `1412133785` have **different GitHub issue, PR, review, comment, run and permission identities** even if a Git commit is shared. New [recovery parent #5](https://github.com/reallakshman19/Common/issues/5) has not accepted any programme AC; the exact current source is still moving through other agents' PRs #2/#3. [Draft M0 #9](https://github.com/reallakshman19/Common/pull/9) has a native read-only double source census. [Draft WP1/U1–U2 #15](https://github.com/reallakshman19/Common/pull/15) independently proposes typed old/current provider binding. Neither grants review/Owner/DELP evidence policy or writer custody.

Actual R14 U1 `identity_contract_v1.validate_identity`, U2 `owner_session_contract_v1.validate_owner_session`, U3 `evidence_review_contract_v1.validate_evidence_review` and U5 `diagnostic_delp_bridge_v1.preview_diagnostic` are preserved on the stacked source ref `892cb0d1eaccfe467b7db2c5f13b9df40b1ff043`. U3 validates shape, bound current candidate/leaf PR, source history and native V3.2 DELP **facts structure** (when full checkout present). U3 **does not authenticate Owner or reviewer**, and U5 correctly quarantines `untrusted_author` rather than admitting E.

## Contract

This independent, additive versioned `cross-repo-u3-evidence-quarantine-v1.schema.json` and `cross_repo_u3_evidence_quarantine_v1.py` take **two separate complete U3 evidence envelopes**, not one historical U3 object with its repository fields rewritten.

The validator calls the *actual unchanged* U3 function twice (and therefore real U2/U1 and actual V3.2 DELP facts structure when available), then binds origin and current repo IDs/names/root/leaf/pr references to their respective U3 payloads. Historical `COMPLETE+VERIFIED`, PASS CI, evidence refs or claimed accepted reviewer remain quarantined. Current-repo initial transfer stage is allowed only when new Owner source grade is **UNKNOWN**, a different explicitly claimed producer session exists, new leaf units have zero imported evidence refs and `NOT_RUN`/`PENDING` results, tests are `NOT_RUN`/`UNKNOWN` without inherited run refs, and reviewer is `NOT_SUBMITTED`.

This is an intentionally narrow **initial re-verification obligation**. After independent current-repo evidence is genuinely obtained, a future separately reviewed positive path may accept it through a versioned policy; this code **does not make that policy decision**. A source digest is a byte fingerprint, not a native provider receipt. It does not convert a copied GitHub URL, verified code SHA, ReviewClaim or serialized R12 source-acquisition boolean into authority.

Return fields always state `historical_evidence:QUARANTINED_NOT_TRANSFERRED`, `current_evidence:NEW_REPOSITORY_REVERIFICATION_REQUIRED`, `source_grade:CALLER_REFERENCED_UNATTESTED`, `provider_acquisition:NOT_EXECUTED`, `delp_evidence_admission:NOT_ADMITTED`, `canonical_delp_projection:NOT_CALCULATED`, `programme_progress:null`, `writer_authorization:NOT_GRANTED` and `successor_lease:NOT_PROVEN`.

## Direct tests, adversarial matrix and bounded next steps

```sh
python -m unittest discover -s skills/engineering-relay-v1/lifecycle-v35 -p 'test_cross_repo_u3_evidence_quarantine_v1.py' -v
```

The tests use actual R14 source U3 test fixtures and validators, but synthetic historical/current repo issue numbers (including new issue #100 / PR #101 as **test placeholders, not provider objects**). They test old VERIFIED/PASS nontransfer, rewritten old evidence refs, copied CI and review, forged author/owner mirror, reused session, wrong root/leaf/pr, changed evidence digest, claimed STOP without fence, source role-swaps and structural progress/lease grants. Native exact-HEAD CI covers Python 3.12/3.13 on Ubuntu and Windows in the **full repository**.

Admission dependencies: (1) complete native test results, (2) independently qualified two-principal WP0 G1 review #12 and old R12 review #869, (3) Owner accepts EvidencePolicyVersion and source identity/retention rules, (4) type-check against WP1 V2 stable-ID native GET source receipts at a later exact source boundary, (5) independently re-verified current-repo facts/reviewer policy, (6) *one* canonical existing DELP projector with same snapshot/hand-over, (7) external writer/Runner custody fence. No source files in existing R14 U1–U5/DELP/Runner/Local are modified in this proposal. **No merge until governed review; AC0/8; writer OFF.**
