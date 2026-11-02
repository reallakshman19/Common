# Oracle continuity bridge — transfer the expectation lineage, not an inherited PASS

This is a **read model / handover recipe**, not a new Oracle state machine, owner of the WBS, Cycle, decision registry or publication authority. Use existing [Oracle Continuity](../oracle-continuity/PROTOCOL.md), the project's canonical issue/Progress WBS, original issue/PR evidence, existing task assignments and any actually selected native Cycle.

## Missing link: oracle continuity of test oracles

Project history normally tracks candidate/version, tests and status. For engineering review it must additionally preserve **why the expected answer was believed** and **which alternative wrong outcome the test discriminates**. Otherwise a later Oracle inherits "tests green" and inadvertently upgrades a shared assumption to an engineering truth.

For each consequential reused finding, preserve the following in the existing native return (no duplicate ledger necessary):

| Chain link | Minimum durable reference | Invalidation trigger |
| --- | --- | --- |
| Owner outcome | Aim revision, actual task/WBS and original Owner requirement | Changed Owner intent or acceptance boundary |
| Original evidence | Source byte SHA, custody, config/unit/Datum, admissible private fixture status | Source/config or custody changed; source not actually read |
| Expected behavior | Reviewer Stage-1 native return, source derivation, rejected alternative, domain authority | Domain meaning corrected or expectation unsupported |
| Candidate | Exact branch/head, feature flags, actual entrypoint and product output SHA when available | Code head, runtime, configuration or output changed |
| Falsifier | Minimal wrong-case input, observable difference, actual executed checker/witness | Changed checker or scope; prior negative test no longer relevant |
| Judgment | Reviewer principal/exposure, method, verdict, limitations and first divergence | Same-principal contribution, new shared source premises, stale candidate |
| Decision | Reconciler/Owner decision, existing issue, scope-specific HOLD, adoption/exception rationale | New decision/authorization or conflicting later return |
| Next actor | One still-authorized WBS action, exact return and next consumer | Task/recipient/writer generation changed |

A copied summary with only a CI link is **not** oracle continuity. A newer run with a different SHA or fixture does not supersede the earlier verdict; it creates a new evidence subject. Preserve the old result historically, mark affected current claims STALE, and identify which oracle/witness needs requalification.

## Three independent axes

1. **Knowledge correctness:** expected source behavior and domain premise trace to original authority. An author-supplied "golden" is a hypothesis to be challenged, not a substitute for this.
2. **Execution continuity:** exact source/config/candidate/native output and negative control have observed witnesses. GitHub posted, browser opened, file transferred, actual recipient bytes verified and execution completed are different facts.
3. **Control continuity:** acting Oracle, Owner/OTM delegation, selected mode, writer isolation, task assignment, Progress WBS, pending or late returns and approval authority. A detailed IR report cannot activate a successor or authorize release.

Never compress these into "handover complete". An incoming Oracle should reconstruct one **original source → expectation → candidate → emitted evidence → surviving wrong case** in their own words, then reconcile the next two connected WBS deliverables and active roles. This is adaptive mentoring, not an extra exam.

## Change-impact/invalidation walk

For a changed source file, unit/frame, support policy, PR head, native serializer, fixture, reviewer role or Owner decision, locate downstream claims. Compare the change's actual dependency path (source → model → validation → native artifact), classify affected verdicts CURRENT / STALE / UNKNOWN / NOT_RUN, keep unaffected recorded evidence, and assign one bounded next verification. Do not replay every test or blindly carry forward the green total.

For an **Oracle replacement**, record the incumbent's live task/return/late writer state and next exact source challenge. The successor's read-only investigation is permitted if authorized; adopting control or concurrent writer privileges follows actual existing cutover rules. When a reviewer later contributes code, their previously independent verdict stays bound to the earlier candidate; changed scope becomes SELF_REVIEW pending suitable non-author check.

## Required counterexamples for a usable handover

- Stage-1 reviewer did not receive private original bytes → report source completeness UNKNOWN and production replay NOT_RUN; independent public microtest may still PASS.
- Native test green at old head, code changed → old head remains PASS in history, current candidate verdict STALE for affected scope.
- Reviewer and author share the same invented expected fixture → two passes are not independent semantic confirmation.
- Writer A returns after successor B's cutover → record late return, do not silently select the stale artifact.
- Oracle says "reviewer ACK" on a posted GitHub note without recipient receipt → only POSTED; route to actual existing receiver.
- Review finds incorrect semantic premise but no executable fixture → preserve CONTRADICTED_SOURCE or inspected defect and runtime NOT_RUN, not "no findings".

Return one existing native, source-backed Task Evidence card if Cycle now is invoked. Do not create a parallel WBS/Board/agent-report stream.
