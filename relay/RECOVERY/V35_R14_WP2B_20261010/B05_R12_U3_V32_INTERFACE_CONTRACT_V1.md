# B05 — R12/U3 ↔ V3.2 DELP native evidence interface (candidate, NOT ADOPTED)

**Responsibility:** [Common #30](https://github.com/reallakshman19/Common/issues/30), nested in [#5](https://github.com/reallakshman19/Common/issues/5), aligned with [#289](https://github.com/reallakshman19/Common/issues/289).
**Base:** [PR #31](https://github.com/reallakshman19/Common/pull/31) exact `708416ebd05c300571097859fc6c1e3596cd7224` (stacked via #28/#27/#21/#9).
**Decision state:** SPECIFICATION + SOURCE CONTRACT TESTS ONLY. Not a new programme graph, receipt version, Owner EvidencePolicyVersion, reviewer verdict, admitted fact, DELP score, custody or writer grant.
**Scope:** only `relay/RECOVERY/V35_R14_WP2B_20261010/**`; leave native V3.2/V3.5, R3/R12 and Local paths untouched.

## 1. Existing physical call boundary (not an end-to-end assertion)

```text
R3 reconcileGitHubFacts() --> one WeakSet-tagged in-process native object
   └─> R12 deriveCandidateState() --> selected-workflow state only
           │  serializing R12 output does NOT serialize WeakSet authority
WP2-A U01 actual candidate --WP2-A U02 selected+required checks ---> U04 twice-observed source vector
WP2-A U03 issue comment ----/               |
                                     WP2-B B01–B03 inspectLivePreAdmission()
                                      => NOT_ADMITTED even when coherent
                  [MISSING reviewed native-provider/Owner/reviewer eligibility]
                  [MISSING authorized current new-repo graph/policy]
                  [MISSING admitted V3.2 CHECKPOINT_FACTS_V1 ledger]
                                            |
                                  existing V3.2 project() ONLY
                                            |
                                  existing V3.2 C6 handover
                   [MISSING new-repo scoped publisher authorization]
```

Native physical source read: `skills/engineering-relay-v1/provider-facts-v1.mjs` exports `reconcileGitHubFacts` and `hasNativeProviderAcquisition`; only a direct native GET may insert its exact frozen object into the private WeakSet. Injected fetch or a JSON copy cannot acquire the capability. `candidate-verification-v1.mjs` uses that function and emits `workflow_policy: CALLER_SELECTED_NOT_REQUIRED_POLICY`. A R12 selected-green state is **not** a U02 provider-qualified required-check state and neither is eligible evidence. The U03 GitHub comment remains an **author claim**.

U04 `cross-source-vector-v1.mjs` imports and calls U01/U02/U03 real reader modules twice. Its source digest is a fingerprint of a bounded non-atomic observation, not independent human identity or custody. WP2-B's `pre-admission-boundary-v1.mjs` intentionally has no positive path or DELP/writer call.

## 2. Proposed typed source-to-eligibility contract (future Owner/reviewer decision)

| Type / role | Physical producer and mandatory binding | Must NEVER inherit |
|---|---|---|
| `CurrentExecutionRef` | Native provider repo ID=1412133785, exact new repo root/leaf/PR, current candidate HEAD/base | Historical `reallaksh19/Common` issue/comment/check/review identity |
| `CandidateObservation` | Native R3/R12 in-process source proof **or** separately reviewed Python re-acquisition; read/write API separated | Caller `source_acquisition_attested` / static digest masquerading as WeakSet capability |
| `RequiredCiObservation` | U02 selected-vs-effective-required policy and executed exact-head check results | R12 selected workflow PASS, skipped/neutral, unresolved rulesets or 403 as required PASS |
| `EvidenceCommentReceipt` | U03 provider-observed comment ID, author, leaf ID, comment bytes, claimed test HEAD | Reviewer independence, Owner identity, code quality or an accepted CHECKPOINT fact |
| `EvidencePolicyVersion` | Separately adopted Owner-governed policy on selected eligible graph and required methods | Author-proposed ADR or any `policy_adopted:true` payload |
| `IndependentReviewerVerdict` | Two separately attributable qualified #12 principals under effective policy | Two PR comments by same actor or author self-review |
| `NativeV32Fact` | Strict V3.2 schema from a qualified producer, exact graph responsibility and source | V3.5 `FACTS_SCHEMA` silent coercion or V1 `input_digest` rewrite |
| `DelpCurrentProjection` | Existing `delp_projection_v32.project(graph,ledger,observations)` | Author-asserted percentages or competing R14/continuity programme E |
| `C6Frontier` | Existing native `plan_handover.py` / `handover_context.py` on default-branch-released graph | Frozen but *unreleased* candidate graph, self-selected writer lease |
| `GitHubManagedProjection` | Separately Owner/Local-authorized scoped new-repo publisher with readback | Any authority from observing source or successfully computing DELP |

### Proposed API sequence (not implemented; eligibility is a pending decision)

1. **Acquire** current native GitHub material on the *same* new repository, recheck exact PR HEAD, comment HEAD and effective required CI, preserving any unknown policy.
2. **Resolve native material witness** by approved same-process R3 capability or external issuer / independent scoped reacquisition. Never deserialize a Boolean and call it native.
3. **Join separately supplied independent authority** for original Owner source grade, adopted graph and EvidencePolicyVersion, signed/attributed reviewer verdicts. Distinguish `UNKNOWN` from `REJECTED` and `QUALIFIED`.
4. **Translate into native V3.2 facts only under the adopted versioned mapping**, preserving archived raw V1/V3.5 semantics and rejecting dropped generation/digest/receipt identities.
5. **Call one existing V3.2 DELP** with current qualified ledger + observations. Verify H1→H2 P retention/E downgrade and genuine exact-H2 requalification.
6. **Render** root/leaf/PR/C6 from that one immutable accepted source basis; **publish only under a separately authorized scoped writer** with provider re-read and explicit partial-write status.

No part of B05 supplies authority for steps 2–6. The adapter and policy itself require #12 independent review and Owner adoption. The released 718 graph blob `d35019b416cb3b573280e166027d3f65ba61f59c` still names **old** `reallaksh19/Common`; do not rewrite historical identity to obtain new-root E.

## 3. Acceptance / falsifiers to implement before positive admission

| Case | Preconditions | Expected result |
|---|---|---|
| S1 material clean | Exact new-repo current candidate, valid U02 required checks, current U03, no Owner/reviewer policy | B01–B03 may classify coherent source; `NOT_ADMITTED`, E unavailable, no DELP/writer |
| S2 native capability spoof | JSON `source_acquisition_attested:true`, recomputed digest, copied native-looking R12 | No native R3 attestation; no admitted fact |
| S3 policy forgery | Caller adds `owner_authenticated/reviewer_qualified/policy_adopted` | Reject input without provider calls; E unavailable |
| S4 stale material | H1 comment on candidate H2, modified CI policy, unknown protection, foreign repo/actor | Explicit HOLD/UNKNOWN; no E |
| S5 schema swap | Use V3.5 `relay-v3.5-delp-checkpoint-facts` as V3.2 `relay-v3.2-delp-checkpoint-facts` | No automatic fact conversion |
| S6 historical graph | `COMMON-718...` graph old repository vs target repo ID 1412133785 | No new-repo release/cutover claimed |
| S7 qualified positive **future** | Independent valid source, executed required test, adopted current new graph and review policy | Only then expect native `project()` to compute nonzero eligible E (NOT YET RUN) |
| S8 revalidation **future** | H1 qualified → push H2 → actual required H2 test + evidence | P retained; E drops at H2 and restores only after H2 qualification (NOT YET RUN) |

`b05-native-interface-contract.test.mjs` executes the present source-level negatives and compatibility assertions. These are not S7/S8 real positive tests.

## 4. Boundaries for reviewers and successor

- **#12**: provide two *independent* authenticated reviewer outcomes against exact current source, with actual native calls and failures; author comments never count.
- **#276**: decide SourceReceiptV2/EvidenceBasisV2 and V1 byte-for-byte digest fidelity without weakening older test contracts.
- **Owner #289/#5**: select one V3.2 programme evidence policy and authorize a versioned new-repo graph; `SIMPLIFIED=ON` does not select policy.
- **#285**: private old-lab 404 is *unobservable*, not evidence of current PASS or FAIL. Reuse only after authorized access.
- **#4/#6**: separately decide and repair protected Buddy same-issue transaction race; B05 adds no Local custody.
- **Publisher**: OFF; generic new-repo writer, dynamic GitHub titles/PR body, and cold C6 E2E remain unqualified.

**Stop condition:** if a fact could earn nonzero E merely by a generated digest, source filename, GitHub author comment, fabricated review or local boolean, reject the change. The first legitimate next implementation is an independently reviewed native-producer integration using an Owner-approved policy, not replacing `NOT_ADMITTED` with `ADMITTED`.
