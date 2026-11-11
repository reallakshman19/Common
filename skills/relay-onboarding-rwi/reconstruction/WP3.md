# WP3 — Source-first engineering reconstruction, CoordinatorLandingpage consumer

Parent: https://github.com/reallakshman19/Common/issues/391
Common base main: ae3c0139a46bbffcc03d9a50f3d9067d59d78633
Scope: read-only independent claim-history normalization, not full technical handover or Owner acceptance.

## Owner purpose

A new engineer must reconstruct the original problem, evolving Owner intent, actual investigations, rejected options, changed code path, tests and the exact first verification even when the outgoing engineer disappears without a report or a final LOG. The successor must not blindly accept the predecessor's design; later RWI must evaluate a bounded KEEP-versus-IMPROVE recommendation without changing the Owner's destination.

## Controlling consumer correction

The Owner explicitly replaced Dash V2/Common #360 with **CoordinatorLandingpage #21**:
https://github.com/reallakshman19/CoordinatorLandingpage/issues/21

The governing Team Protocol is v2.3 FINAL CANDIDATE #7:
https://github.com/reallakshman19/CoordinatorLandingpage/issues/7

CoordinatorLandingpage main observed at 5c7497386f0e45082284e3dc598814ef0a5b7c8b; protocol blob ca0520aec69831cb6e62da61ffa56861743cb92d. The existing public Pages site, its eight views, owner-input issue form, inbox #1, registries and real TeamCoordinator own the live two-way process. No UI revamp, duplicate dashboard, altered protocol, new coordinator, scheduled poller, new Owner authority, or automatically generated messages. Do not edit CoordinatorLandingpage code or logs from WP3; a later **separately authorized read-only public-data projection** can use its existing intake seam.

## Technical slice

1. `reconstruction/history.py` takes source-scoped claims on one original issue, source revisions, optional current PR heads, Owner decisions/amendments, investigations/rejections, code-path hypotheses and test records. It refuses wrong repositories, duplicate identities, unsafe URLs, contradictory timelines, invalid supersessions, stale claim promotion and a claimed NOT_RUN with a fabricated observation. No actual owner-role verification follows from free text.
2. `reconstruction/source.py` calculates actual SHA-1 Git blob and SHA-256 UTF-8 line-span identity from supplied bytes, without asserting that the caller is a trusted provider or that source-call edges are semantically correct.
3. `schemas/reconstruction.v1.schema.json` defines typed input. The runtime validator checks cross-field relationships beyond the JSON schema.
4. `tests/test_reconstruction_wp3.py` provides 41 offline oracles for abrupt exit, scoped landing-page amendment, main-vs-candidate revisions, stale code, missing original Owner issue, false Owner approval, rejected paths, source byte mismatch, invalid URLs/path traversal, privacy redaction and no unauthorized writes.
5. `examples/coordinatorlandingpage-public-reconstruction.json` retains observed public issue/pr/run links from Common #391, CoordinatorLandingpage #21 and WP2 draft PR #394 as explicit **source claims**, not independently authenticated evidence. Code path is intentionally empty, producing `CURRENT_CODE_TRACE_MISSING`.

## Reproduce

    python -m unittest discover -s skills/relay-onboarding-rwi/tests -p 'test_reconstruction_wp3.py' -v
    python skills/relay-onboarding-rwi/reconstruction/history.py --input skills/relay-onboarding-rwi/examples/coordinatorlandingpage-public-reconstruction.json --markdown

Output is a **partial technical reconstruction scaffold (NOT VERIFIED)**, not the requested complete 12-section handover. Its semantic source edges, Owner authority, historic decisions and fixture bytes still need independent provider readbacks/review. Status remains CONDITIONAL/BLOCKED; reported Owner approvals never become verified. RWI is NOT_EVALUATED; execution_authorized=false, and predecessor-exit/LOG is not required.

## Existing dependencies and nonoverlap

Common #392 (WP1a), #393 (WP1b), #394 (WP2) are draft/unmerged; this WP3 branch starts directly at main and imports none of those unpublished modules. No changes to the accepted v3.6, BuddyRunner, existing Software MCDA, Workflow Intelligence, landing site/protocol, or business/product repos. When previous PRs are admitted, reconcile type schemas rather than stack unreviewed patches.

## Test and adoption gates

The 41 source tests are definitions until hosted Actions logs for the exact WP3 commit are read. The public example is not a live connector run. A valid GitHub URL and comment actor label are not source authority. Even a byte-exact digest proves only identity, not correct pipeline behavior, release, protected approval or complete Owner golden.

WP3 source/reconstruction tests and independent reviewer are prerequisites to the next stage. WP4/WP5 must authenticate code-path architecture, original input hashes, complete test oracles and final 12-section Markdown manifest/verdict. WP8 may later expose a **small, sanitized, read-only** projection through the existing CoordinatorLandingpage intake, only with its actual Owner/TeamCoordinator approval. No PR merge or release authorized.

**Exact next action:** re-fetch Common #391, landing #21 and protocol #7; recheck draft PR #394 at current head and its real source files, verify the first owner-layer failure path and acceptance oracle independently; then bind evidence into the approved history manifest without filling missing facts by guess.
