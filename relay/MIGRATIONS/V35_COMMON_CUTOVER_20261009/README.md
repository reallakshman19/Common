# Common V3.5 M0 — historical/current repository identity census

**Status:** AUTHOR-SIDE READ-ONLY SOURCE CANDIDATE · [new recovery parent #5](https://github.com/reallakshman19/Common/issues/5) · observed 2026-10-09 · **programme AC0/8**.

This folder is a bounded migration **reference** ledger and deterministic validator, not an implementation of the lifecycle, active OwnerIntent registry, secure GitHub provider attestation, or a GitHub writer. It does not modify existing V3.1/V3.2/DELP/Local/Runner code.

## Why this gate exists

Old repository `reallaksh19/Common` has stable GitHub repository ID `1207996454`, while proposed new source destination `reallakshman19/Common` has ID `1412133785`. At census both default branches pointed to exact `d60c36605e988dcc160647421973f170fd87e0eb`. **Equal source commits do not transfer GitHub issues, comments, PRs, independent reviews, CI, access controls or custody permissions.**

Source-only R14 chain #891→#894→#895→#896→#897 exists byte-identically in the new repo's branches, but remains old-repo **draft PR objects**. At provider refresh, old #893's Markdown branch had advanced **22 commits** to **new draft PR #3** (HEAD `aaf1a51926579098f2c8711435d210aadf5ec144`). Old Buddy #892 had advanced **6 commits** to **new draft PR #2** (HEAD `6255b759e20577c126c7b158e1c17ddc66bb80c7`). **These are moving observation-time values, never a standing claim of currentness.** There is also a **new issue #1** continuing the old #890 Runner purpose. These are relationships, not imported approvals.

A predecessor #1/#3 investigation already produced:
- [R14_SOURCE_INTERFACE_RECONCILIATION_V1.md](https://github.com/reallakshman19/Common/blob/cc4de8a87ec86ea66f02bb2f82184ad0f7a3d598/relay/CONTINUITY/REVIEWER_ONLY/R14_SOURCE_INTERFACE_RECONCILIATION_V1.md)
- [REPOSITORY_LINEAGE_AND_PR_COLLISION_V1.md](https://github.com/reallakshman19/Common/blob/cc4de8a87ec86ea66f02bb2f82184ad0f7a3d598/relay/CONTINUITY/REVIEWER_ONLY/REPOSITORY_LINEAGE_AND_PR_COLLISION_V1.md)

This M0 artifact **adds a strictly structured machine-checkable snapshot** rather than replacing those richer analytical documents or claiming a fresh independent WP0 reviewer.

## Inputs and reproducible check

```sh
node --test relay/MIGRATIONS/V35_COMMON_CUTOVER_20261009/*.test.mjs
# native live provider readback, fails closed on any stale object/HEAD/ancestry
GITHUB_TOKEN=<read-only-token> node relay/MIGRATIONS/V35_COMMON_CUTOVER_20261009/audit-native-provider-v1.cli.mjs
```

The validator may be consumed as:

```js
import {validateMigrationManifest} from './validate-migration-manifest-v1.mjs';
const receipt = validateMigrationManifest(manifest);
```

`receipt.valid=true` means **only** that a caller-supplied snapshot satisfies local shape/relationship constraints. Every structural receipt explicitly preserves `CALLER_REFERENCED_NOT_LIVE_ATTESTED`, `NOT_AUTHENTICATED`, `NOT_QUALIFIED`, `NOT_GRANTED`, `NOT_EVALUATED`. The separate `audit-native-provider-v1.mjs` reader obtains actual current GitHub GETs for old/new repository stable IDs, default branch HEADs, old/new issue/PR identities, new branch ref SHA and native compare ancestry; a live CLI observation yields `NATIVE_GET_VERIFIED_AT_OBSERVATION` **only for these bounded provider facts**, whereas the fully injectable native response-shape test returns only `CALLER_SUPPLIED_PROVIDER_RESPONSES_UNATTESTED`, while `reviewed:false`, `owner_authenticated:false`, `evidence_accepted:false` and `writer_authorized:false` remain invariant. The live CLI requires HTTP 200, same URL, bounded body, and fails on 404/403/rate limit, stale PR/head, changed ancestry and duplicated or forged mappings. The input JSON and runtime validator are safe to execute offline; the pure structural validation has no fetch, write token, shell execution, native GitHub claim, CI promotion, snapshot/evidence authority or Stage1 B admission. The separate read-only live audit is **not** an Owner/evidence/reviewer/provider security-policy authenticator and cannot confer permission.

**Strong negative checks:** same-ID confusion, old URL rewritten as new, old-only object invented as a destination, issue/PR path/type confusion, duplicate origin/destination, false branch equality, invalid/unknown relation, fabricated reviewer grant, forged 8/8 acceptance, false live writer, unexpected fields, nonexistent originating PR.

## Provider readback and refresh instructions (mandatory before cutover)

1. Independently GET both GitHub repositories and verify **stable ID, owner/name, default branch head SHA and permissions**.
2. GET native **old and new issue/PR objects** in the manifest. For every mapped destination verify provider returned a real object with its own ID, kind, current head, base, state and reviewer/check contexts; **never infer one from the old object number**.
3. GET each new branch ref and compare its current head to `destination_head_sha`. `SOURCE_ADVANCED` claims must be proven with actual Git compare/ancestor operation and exact ahead count; stale source means **REFRESH_REQUIRED**, not positive migration.
4. Update/correct the manifest by a new source commit and re-run tests. Preserve historical old URLs and provenance; material new PR/review/CI evidence must be created and read in the new repo.
5. Reconcile issue #1 / PRs #2/#3 before touching overlapping `relay/CONTINUITY/**` paths. Both PRs are draft and their overlapping files require explicit winner decisions; no automatic merge.
6. Obtain the governing independent #866 WP0 reviewer requirements, separate #869 R12 review, Owner schema/privacy/DELP policy decision and actual writer/lease permission separately. A M0 validation receipt cannot grant them.

## Source/consumer interface cut points for WP0

| Dimension | R14 U1–U5 | Runner #3 | HOLD until |
| --- | --- | --- | --- |
| historical/new repo identity | U1 same-programme-repo structural constraint, U2 same-repo Owner mirror, U3 repo#issue/PR facts | `AUTHORITY_MAP`, `TECHNICAL_HANDOVER`, `OWNER_DECISION` cite old/new separately | versioned stable provider-ID migration envelope and real source verification |
| plan vs session vs candidate commit | U1 typed graph/session/candidate roles | Stage1 historic cutoff and Stage2 current test HEAD | no SHA role promotion; current plan/head readback |
| Owner intent and session authority | U2 histories are **claims** | Stage1 source and external controller | authenticated original source, session disclosure policy and no private leaks |
| evidence/reviewer | U3 structural check; U5 quarantine; current author-side 130 PASS/3 skips | technical handover cites tests/review claims | actual native full-checkout and independently qualified review |
| progress/next | V3.2 vs V3.5 DELP policy not yet reconciled | MD is read-only communications | single approved programme DELP and same snapshot digest |
| successor/writer | U2 STOP_CLAIMED not fence | real Stage1 denied-read preflight + external lease | actual B isolation and A credential fencing |

**Decisions NOT made:** selecting a new authoritative programme graph/evidence schema, reconciling old/new actual identity in production, granting Owner decision, making PR #2/#3 merge-ready, unfreezing V3.2, enabling a producer or publisher. These require later governed WP0→WP1 admissions and independent source review.

**Next work:** independently refresh provider census; publish `TASK_EVIDENCE END` for this bounded reference artifact with exact commit/blob hashes and test results; then execute the real WP0 DELP source graph/policy falsifier and obtain two independent source-level verdicts. This document is not a `TASK_RESULT` for #787 AC1–AC8.

**CI evidence interpretation:** the four Node 22/24 × Windows/Ubuntu unit-test cells use synthetic provider-response injection to prove rejection behavior. A separate Ubuntu/Node 24 **live read-only provider job** compares the manifest with current GitHub object responses. PASS is a time-bounded census only. FAIL can indicate a genuine concurrent branch advance or unavailable GitHub API; classify as `REFRESH_REQUIRED`/HOLD, not a production defect or a retroactive acceptance decision. Source HEAD and raw job steps are mandatory for each checkpoint. The audit makes no new object publication and copies no historic reviews/permissions.


## M0-U3 — current source frontier without repeated manifest commits

A **migration mapping** is durable source history; a Runner PR HEAD is mutable source material. They must not share a version or be treated as the same type of fact.

The standalone `observe-moving-heads-v1.mjs` implements an **observed current-source vector** without changing `migration-manifest-v1.json`. For each mapped new PR, it executes native GitHub PR GET, exact branch ref GET, and native compare against the immutable original old PR HEAD. A second independent set of GETs through `auditNativeProvider` revalidates the complete old/new repository/issue/PR identities, old HEAD, new HEAD, source role and ancestry. If PR #3 advances during the two phases, the result is `REFRESH_REQUIRED`, **not** a silently accepted stale snapshot. A later movement after these two reads is not prevented; every consumer must independently recheck before a write.

```sh
# Offline native adversarial unit tests, fixed input/no network
node --test relay/MIGRATIONS/V35_COMMON_CUTOVER_20261009/*.test.mjs
# Live native old/new GET checks; read-only and current only at observation
GITHUB_TOKEN=<read-only-token> node relay/MIGRATIONS/V35_COMMON_CUTOVER_20261009/observe-moving-heads-v1.cli.mjs
# Optional strict source freeze (must match manifest-pinned destination HEAD)
GITHUB_TOKEN=<read-only-token> node relay/MIGRATIONS/V35_COMMON_CUTOVER_20261009/audit-native-provider-v1.cli.mjs
```

**Strict audit versus moving-read mode:** The older `audit-native-provider-v1.cli.mjs` deliberately returns stale if a destination HEAD differs from its historical manifest observation; retain it for pinned freeze verifications. The workflow's **live** job now exercises moving-head mode to avoid racing an actively updated Runner branch; it never overwrites the historical manifest, transfers CI/review or turns an observation into admission. The injected `observeMovingHeads` contract explicitly says `source_grade: INJECTED_UNATTESTED`. Only the fixed `observeLiveMovingHeads` path that calls the bounded GitHub GET transport can return `NATIVE_GITHUB_DOUBLE_READ_AT_OBSERVATION`. Both preserve `writer_authorized:false`, `reviewer_qualified:false`, `evidence_accepted:false`, and `programme_acceptance:NOT_EVALUATED`.

Race coverage includes a new SHA observed before/after a complete current read (positive), PR changes between first and second reads (HOLD), PR/branch mismatch (HOLD), wrong original PR currentness (HOLD), divergence from historical code commit (HOLD), mock response grade not becoming native, and incomplete GitHub responses (HOLD). Test-only source is not a reviewer or privacy grant.

**Scope:** This only solves current old/new *identity/material* observation for M0. It does not wire R3/R12 to accepted DELP evidence; approve the proposed WP0 architecture; qualify independent reviewers; freeze Runner B; or authorize live scoreboards. Those remain governed by #5 and #12.
