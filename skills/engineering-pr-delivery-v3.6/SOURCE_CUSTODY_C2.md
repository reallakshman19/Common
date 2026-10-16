# C2 — Native v3.6 source/actor custody (independent from legacy Relay)

**Owner parent:** https://github.com/reallakshman19/Common/issues/400  
**C1/C1A prerequisite:** draft PR #403 (unmerged); this C2 is independent, main-rooted, no imports of #403.  
**Source baseline:** Common main @ 0a7c4d45d3fa0787d3e80858a27015b09a85eac2.  
**Governing status:** additive read-only custody prototype; no Owner, reviewer, merge or release acceptance.

## Independence contract — hard requirement

The module `scripts/source_custody_v36.py` imports **Python standard library only**. It does not import, call, vendor or instantiate v3.5, v3.2, v3.1, DELP, Handover Master, BuddyRunner, coordinator or proposed #403 continuity modules. Python unittest tests are themselves independent of those versions. This is native v3.6 with future C1 adapter compatibility, not runtime continuity with older skills.

Cross-version checks in the shared Common repository are **regression safety checks**, not source/runtime dependencies. Full native v3.6 label, plan, evidence and title authority remains in its existing code and is untouched.

## What C2 actually does

With an explicitly pinned SHA40 repository revision, source path, expected Git blob SHA1 and independent SHA256/length, it:
1. GETs the file path at the declared full commit through GitHub Contents API to bind path and blob.
2. GETs the exact Git blob bytes, verifies Git blob SHA-1, SHA-256 and length; malformed data or wrong digest is CONTRADICTED.
3. Fetches issue or issue-comment metadata from the GitHub API; checks parent issue identity, provider `user.login`, date and optional content SHA. No private issue body is echoed to report.
4. Distinguishes `BYTE_VERIFIED_ON_PINNED_GIT_REVISION`, `PROVIDER_RECORD_OBSERVED_NOT_OWNER_AUTHENTICATED`, `CONTRADICTED_*`, `STALE_ISSUE_EDIT`, `NOT_FOUND_UNVERIFIED`, access failure and oversized/unavailable blob.
5. Explicitly refuses publication, canonical task evidence O2, title/label writes, Owner sign-off, semantic acceptance, merge and release.

**Important:** even a matched provider login is NOT an authenticated Owner policy decision. The script cannot recover unpublished private ChatGPT Owner input, decide a golden is semantically complete, or infer that a 404 issue was deleted. `oracle_complete` is a stated claim only. The root issue is the navigation index, not proof of byte origin on its own.

## Bounded pilot limits

Initial GET/JSON blob prototype handles declared files up to 16 MiB. Larger inputs return `SIZE_OUT_OF_C2_PILOT_RANGE_UNVERIFIED` without reading the blob. **This is not a change to 3D_Converters' separate Owner-approved 100 MiB / 2,000,000-occurrence product operating range.** Streaming custody for bigger artifacts is an independent C2 extension before larger fixture approval.

## Demonstration vs original product fixture

`tests/fixtures/c2-common-public-demo.json` points to the **real** 17-byte Common v3.6 `requirements.txt` at pinned commit and Git blob. This is explicitly `DEMONSTRATION_ONLY`, **NOT** the Owner's original 3D_Converters positive/negative fixture or a complete acceptance golden. It also references Common #400 to show current provider-actor observation. C1 still reports missing original product fixtures as UNKNOWN until independently attested. The fixture is not an Owner instruction.

## Execution

```bash
python3 -m unittest discover -s skills/engineering-pr-delivery-v3.6/tests -p 'test_source_custody_v36.py' -v
python3 skills/engineering-pr-delivery-v3.6/scripts/source_custody_v36.py --manifest skills/engineering-pr-delivery-v3.6/tests/fixtures/c2-common-public-demo.json
```

Actual second command is a **live read-only GitHub API attempt** using optional `GITHUB_TOKEN` (never logs the token). Its success/failure must be reported from the real run, not inferred from offline mocked tests. Offline CI tests inject a controlled provider response and never call GitHub. Run against a trusted environment only.

## Plan checklist — verified as of this PR's drafting

| Gate | Status | Grounded result |
|---|---|---|
| C0 | DONE (inventory) | #400 source/Owner intent, accepted #341, Handover Master #398, current main and distinct CoordinatorLandingpage #49 checked |
| C1 | CODE + CI DONE / NOT MERGED | #401 eleven-category validator reconciled into #403, source reported only |
| C1A | CODE + CI DONE / NOT MERGED | #402 coding and lineage/ad-hoc compatibility reconciled into #403 |
| C2 | PARTIAL IMPLEMENTATION (this PR) | Pinned Git byte/actor read-only adapter and synthetic negative tests; 16 MiB pilot; real original fixtures not certified |
| C3 | NOT STARTED | Original intent + byte proof + actual codepath into existing `successor_v36.py`; twelve-section source-backed reconstruction |
| C4 | NOT STARTED | Existing publisher only, lab backwards compatibility and smart human title preservation |
| C5 | NOT STARTED | Phase-filtered BuddyRunner/2-/3-pass and Handover Master without blind leaks |
| C6 | NOT STARTED | Genuine #274 and Physics #287 cold tenth-agent pilots using originals/negative tests |
| C7 | NOT STARTED | Independent semantic, protocol/privacy and Owner acceptance |
| C8 | OPTIONAL / NOT STARTED | Existing CoordinatorLandingpage read-only projection; separate approval; #49 already merged, do not duplicate |

## C2 remaining acceptance conditions

- Provider-readback on genuine original positive AND negative product fixture, full golden or explicit UNKNOWN with concrete custody reason.
- Actual matching Git bytes with pinned commit, byte count and true SHA-256, at known product source paths.
- Owner amendments sourced to attributable, authorized issue comments; no private chat assumptions.
- Large-file custody beyond pilot cap if the selected original exceeds 16 MiB.
- Independent review and exact candidate-head CI, then hand facts forward to C3. Do not claim "C2 DONE" before this.
- Reconcile only after #403 merge; keep main-rooted standalone PR until then.

**Safeguard:** No C2 result can be used as v3.6 task acceptance or a Coordinator NEXT_MOVE dispatch signal.
