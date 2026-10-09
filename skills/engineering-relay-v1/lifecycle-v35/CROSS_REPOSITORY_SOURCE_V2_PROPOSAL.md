# WP1/U1–U2 — V2 source-identity migration proposal (read-only, NOT ADOPTED)

**Governing recovery:** [new Common #5](https://github.com/reallakshman19/Common/issues/5) · [WP0 independent reviewer gate #12](https://github.com/reallakshman19/Common/issues/12) · [WP0 native source audit draft PR #10](https://github.com/reallakshman19/Common/pull/10) · [M0 live identity snapshot draft PR #9](https://github.com/reallakshman19/Common/pull/9).

**Branch/base:** `recovery/5-wp1-u1-v2-crossrepo-identity-proposal-20261009`, based on preserved R14 WP1/U1 source `8754c2e8a2e04c8cc8fd24cd290f3f82b6ab390e` (historical old draft #891), **not** merged `main`. **Independent review NOT QUALIFIED; Owner EvidencePolicyVersion/privacy/Source cutover NOT ADOPTED; writer OFF; programme AC0/8.**

## Source of truth: V1 unchanged, V2 roles distinct

The actual existing `identity_contract_v1.validate_identity` remains the sole validator of current programme `PLAN_GRAPH_REVISION`, `SESSION_SOURCE_COMMIT` and `CODE_CANDIDATE_HEAD`; it intentionally fails if any current role belongs to another repository. The new `cross_repository_identity_v2.py` adds exactly one *historical origin issue* `{repository_id,repository,kind,number,url,source_grade}` and one independent *current execution issue* with distinct stable provider IDs, a relationship and separate old/current source-commit roles. **Historical issue #787 and current recovery #5 are different objects; an equal Git SHA never transfers comments, Owner authority, review, CI, issue title or publisher access.**

The strict JSON schema prevents additional/proxy approval fields and Owner/Review/lease promotion. The emitted digest covers source assertion bytes only and is **not** a verified-provider capability. `source_grade=CALLER_REFERENCED_UNATTESTED`, `owner_original_source=UNKNOWN`, `external_review=NOT_TRANSFERRED` and `writer_lease=NOT_GRANTED` are retained.

## New provider object/commit bound (U2 candidate)

`cross_repository_provider_v2.py` validates V2 + actual unchanged V1 first. Its injected-reader version verifies syntactic responses without ever claiming native acquisition (`CALLER_INJECTED_UNATTESTED`). Its **fixed-path**, read-only native HTTPS GitHub GET wrapper can label only the bounded public **source material observation** (`NATIVE_GITHUB_GET_AT_OBSERVATION`), *not Owner or reviewer permission*. It enforces:

1. Old and new **separate** provider repository stable IDs and exact full names.
2. Old historical issue and new execution issue are actual provider **issues, not PRs**; number, URL, state and source repo match.
3. Historical and current source commit SHAs are separately resolvable in their own GitHub repositories, without interpreting SHA equality as identity equivalence.
4. Current U1 graph/session commits exist at exact typed SHA. When graph source is REFERENCED, the exact file path at graph revision is read and the raw content SHA256 must equal the versioned reference. No paths from untrusted source without V1 validation.
5. Current candidate PR number, head and base SHA, head/base repo identities and branch ref must agree. The candidate PR and branch are re-read at a second call boundary; H1→H2 produces fail-closed disagreement.
6. No action writes GitHub. No actor claim, screenshot, issue title or serialized digest is promoted into reviewer/Owner/DELP E, source writer or adoption.

The fixed live transport has a **repository allowlist**, API route allowlist, HTTPS SSL, no redirects, finite body, 15s timeout and read-only GET. A successful transport snapshot is time-bounded, **not** an immutable security attestation; consumers needing a write must re-observe and satisfy the separately authorized lease.

## Reproducible tests

```sh
python -m unittest discover -s skills/engineering-relay-v1/lifecycle-v35 -p 'test_cross_repository*_v2.py' -v
```

The dedicated `.github/workflows/v35-wp1-crossrepo-v2.yml` runs both V2 identity and provider binding suites, Python 3.12/3.13 × Ubuntu/Windows, and prints the exact commit being tested. Fixtures are **synthetic**, with valid positive current graph raw SHA256 and PR facts supplied by an injected reader, plus old/new repo mixups, SHA/branch race, tampered graph content, wrong source commit, owner/reviewer promotion and source grade isolation. Passing the synthetic suite never proves an actual GitHub provider run or Owner authentication.

A **real-source observed fixture** with independently verified graph path bytes, new issue/PR and current HEAD remains necessary. Original private Owner authorization and reviewer evidence must be obtained separately. R14 U2, U3 and U5 production consumers are **not wired**; existing V3.2 C6, nested V3.5 Local and legacy DELP remain unchanged.

## Admission block / next actual consumer

- [ ] WP0 ADR versioned programme evidence policy + two different qualified reviewers on [#12](https://github.com/reallakshman19/Common/issues/12); separate historical R12 #869 review debt.
- [ ] Exact HEAD native Python matrix on this draft PR (no skip), independent source audit of V2 and the live-reader transport.
- [ ] Native old/new GET receipts and separate Owner source grade; a live GET verifies an object, not the Owner's private instruction.
- [ ] Typed versioned U2/U3 read-only adapter binds original/current issue and PR to **separately qualified** reviewer/evidence facts. U5 remains quarantine-only until a positive native R3/R12→DELP adapter is reviewed and approved.
- [ ] One accepted versioned programme DELP source for P/E/actual-next, one immutable snapshot digest, and guarded publisher/Runner only after external custody proof. No historical review/CI transfer and no second calculator.

**Disposition:** SOURCE-CANDIDATE / DRAFT / NO PROD ADMISSION / NO WRITE / AC0/8.
