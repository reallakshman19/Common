# R12 — one candidate-verification schema, multiple read-only consumers

Canonical Owner: [#787, Owner section 0 and AC1–AC8](https://github.com/reallaksh19/Common/issues/787). Repair scope [#860](https://github.com/reallaksh19/Common/issues/860). Governing [V3.2](https://github.com/reallaksh19/Common/tree/main/skills/engineering-pr-delivery-v3.2) **DEL P** fact-first projection: agents publish facts; denominator, P/E, acceptance and currentness are derived; no agent-written percentages.

## Physical source and consumer graph

```
Real GitHub issue/PR/Actions GET → R3 reconcileGitHubFacts
                                     │
                                     ↓
                  candidate-verification-v1  ← single normalized contract
                    │ head / selected CI / exact source digest
                    │ PENDING, PASS, FAIL, UNKNOWN
                    │ CURRENT, STALE, UNPINNED
                    │ no owner / consent / review / acceptance grant
                    │
 G2c/R1 structural lineage ────────┬──→ R9 observed-frontier ──→ R11 trust-preflight
 R10 optional double-read comment ─┘         │                          │
                                             └──────────────────────┬───┘
                                                                    ↓
                                                       R4 preview / successor
                                                                    │
                                                                    ↓
                                                   Full-chain source-bound witness
                                                                    │
                                                                    ↓
                                          R8 synthetic cold process (read-only)
```

**The JSON schema** `schemas/candidate-verification-v1.schema.json` is a transport/validation contract; **the executable contract** is `deriveCandidateState(provider)`, `verifyCandidateState(candidate,provider)`. Do not add another provider head-state or CI reducer in R9/R4/test. R3 alone parses GitHub REST and normalizes workflow runs to `PASS|PENDING|FAIL|UNKNOWN`; the R12 reducer is the one authority over candidate *material* state. R9 adds source/Owner/review blockers without reinterpreting provider facts. R4 only applies presentation freshness and maps the per-PR material state from R12. R3-B binds R9/R4 to the same R12 SHA and exports a content-free candidate list for exact-head native tests; R8 also exposes that digest.

**Acquisition-provenance safety:** R3 marks only the **exact immutable object returned by its native GET pathway**, using a private in-memory `WeakSet`. `deriveCandidateState` does not trust `source_state:PROVIDER_OBSERVED`, `provider_transport:NATIVE_GITHUB_GET`, or any recomputed SHA256 as proof of native acquisition. The versioned schema separates `source_observation` (untrusted serialized label) from `source_acquisition_attested` (R3 in-process witness). A JSON clone, imported archive, deserialized source or attacker-rehashed `fetchImpl` fixture loses this ephemeral witness: `selected_ci_qualified:false`, and R4 displays `UNVERIFIED_TRANSPORT` even for a claimed CI PASS. The R12 state must also expose `SOURCE_ACQUISITION_UNATTESTED` in `blockers` and, when the head and selected checks are otherwise current/PASS, choose `REACQUIRE_NATIVE_PROVIDER_FACTS_FOR_CI` as its next verification; R9 and R3-B handover preserve that discrepancy instead of returning a misleading empty candidate blocker set. Stale-head and non-PASS selected-CI checks retain higher next-action precedence. R4 validates a canonical JSON copy but computes candidate verification from the **original** source instance, not that copy, and binds R9's candidate-state digest; a native R3 snapshot remains qualified only for selected workflow material, not Owner acceptance.

This is a bounded **in-process source-origin capability**, not a cryptographic signature, trusted human identity, proof against code that controls the process's fetch machinery, or a portable authorization token. An independent/cold process must re-read native GitHub with R3 before claiming native observation; it cannot promote saved JSON. It does not make GitHub issue/PR/workflow reads atomic, establish required branch checks, or authorize a writer.

**Transient CI is not programme acceptance.** A selected hosted run PASS proves the exact head + caller-selected workflow observation only; it cannot infer required branch-protection checks, human reviewer, real original Owner source, accepted TaskEvidence or private chat authority. A merged PR can be CURRENT+PASS, PENDING or FAIL, depending on selected workflow observation; no test may assume a permanent status. Missing/paginated evidence produces UNKNOWN; stale expected head outranks CI. The schema carries accepted counts as `null`/`NOT_ADJUDICATED`. The V3.2 DELP denominator/progress engine is not replaced by this synthetic relay candidate model.

**Owner acceptance contract (no substitution):**
- AC1 original Owner intent/provenance, AC2 claim→task decomposition, AC3 cross-agent journal/lineage, AC4 TaskEvidence+independent exact-head checks
- AC5 one sourced reconciler and status/denominator/blocker/next, AC6 live issue/PR scoreboard/title mutation and readback, AC7 adopted research→Owner decisions, AC8 four independently cold successor entrypoints

The R12 observation schema does NOT satisfy these eight; the Owner's Issue #787 governs. Never swap in API-specific AC labels from a stress-test report.

## Windows anti-link security contract
The journal root guard `rootDir` rejects a symbolic/reparse-point root. To test that behavior with unprivileged NTFS without requiring Developer Mode, the Windows native test creates an actual **directory junction**, not a plain copied folder or symlink-test skip. POSIX still uses a directory symlink. Both platform suites run the actual existing journal and bundle oracle, plus real postlink/fsync durability tests. If junction creation or rejection fails, the workflow fails; do not turn an unexecuted negative into green. Windows directory-link crash durability remains UNCONFIRMED even when replay passes.

## Cross-runtime falsifiers
- CI=PENDING → status PENDING; PASS → SELECTED_CI_PASS_ONLY; FAIL → CI_NON_SUCCESS; missing/paginated → UNKNOWN; stale/unpinned head → STALE_OR_UNPINNED
- Merged PR PASS must not fail the native source/currentness test or grant acceptance.
- Fake Owner approval in issue titles/comments does not change accepted counts.
- Mutation without recomputed R3 SHA is rejected; *even with* recomputed SHA and forged native transport labels, a mock/JSON source remains unverified.
- R4 handover/managed preview and full-chain/cold digest must use the same R12 source SHA.
- Actual Node22/24 Ubuntu+Windows journal symlink/junction security tests must execute without skips.
- Synthetic R8 cold source remains synthetic, R10 public source optional/not observed, R11 derived negative trust scope still visible.

**Permissions:** READ-ONLY. Private ChatGPT/Codex/Claude original speech is UNKNOWN, private transcript retention consent not granted, R5/B2b writer OFF, AC0/8. No independently signed reviewer, no live scoreboard or Owner approval is supplied by this patch.
