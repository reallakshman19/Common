# Neutral task design

Design data under existing authority; use a selected consumer for execution instructions.
Map: search-session-map | revision: 1 | task: T-SESSION
Canonical map SHA-256: f050392d7d06db8d23ca818baa6094c049766c1cb3f380dc112bfa1ed2975fc3
Digest covers sorted compact UTF-8 JSON, not authentication or acceptance.

## Original request
> # Owner request
> 
> Fix this small local search-session component. Users sometimes see an older search
> replace newer results, including after returning to a previous project filter.
> Cancellation must leave the view idle and empty even if the cancelled operation
> finishes later. Preserve normal successful results, genuine current errors and
> reuse after cancellation. Rows are already ranked; preserve their supplied order.
> 
> The source is work/session.py. The original source and existing native checks are
> in raw/. Keep raw/ byte-identical and change only work/ and out/. Add focused checks
> where useful. Use the provided Python runtime; no network, browser or live repo
> actions are needed or authorized. Deliver a working component and concise evidence
> of what actually happened, what changed direction and what remains unestablished.

## Purpose
> Repair local search-session callback authority and cancellation while preserving ranked rows, current responses and reusable state.
> Repair local search-session callback authority and cancellation while preserving ranked rows, current responses and reusable state.

## Coherent deliverable
> Repaired work/session.py with focused executable event-order regression checks and a native report.

## Source-grounded basis (quoted data)
C-LOCAL — CONSTRAINT — sources: S-OWNER, S-ACCESS
> Change only this episode work/ and out/; use the provided Python runtime; no network, browser, live repository, app service or external message actions.
Declared coverage: PLANNED
> Retained in coherent repair and Oracle integration checks.
C-RAW — CONSTRAINT — sources: S-OWNER
> raw/ and raw-manifest.json remain byte-identical.
Declared coverage: PLANNED
> Retained in coherent repair and Oracle integration checks.
F-BASE — FACT — sources: S-BASE, S-EXISTING
> Original candidate matches raw source; original native checks pass 4/4, while Oracle event-order witnesses fail 10/10.
F-GUARD — FACT — sources: S-SOURCE
> Original begin issues increasing sequence values, but finish/fail compare only scope and cancel does not revoke tickets.
R-CANCEL — REQUIREMENT — sources: S-OWNER
> Cancellation leaves the view idle with empty rows and no error even when the cancelled operation later finishes or fails.
Declared coverage: PLANNED
> Retained in coherent repair and Oracle integration checks.
R-LATEST — REQUIREMENT — sources: S-OWNER
> Only the latest noncancelled search operation may update the view, including repeated queries in one project and return to a previous project filter.
Declared coverage: PLANNED
> Retained in coherent repair and Oracle integration checks.
R-ORDER — CONSTRAINT — sources: S-OWNER
> Rows are already ranked; preserve their supplied order.
Declared coverage: PLANNED
> Retained in coherent repair and Oracle integration checks.
R-PRESERVE — REQUIREMENT — sources: S-OWNER, S-TESTS
> Preserve normal successful results, genuine current errors, reuse after cancellation and detached snapshots.
Declared coverage: PLANNED
> Retained in coherent repair and Oracle integration checks.

## Required understanding
> A project filter is not an operation identity: A→A and A→B→A can have obsolete callbacks with the current scope.
> Oracle established the public-state model before delegating: the latest begin owns the view, while cancel revokes that ownership; stale success/error callbacks return False without any snapshot change.
> Sequence already exists in issued tickets; maintain a lifetime identity across begin and cancel, preserve source API and copy/order behavior.
> Worker implements one coherent state repair and regression artifact; Oracle retains interpretation, scope choices, source/probe inspection and integrated acceptance.

## Acceptance and contrast
> observable: Native checks and original Oracle schedules pass on the actual candidate; current result/error is accepted and old/cancelled callbacks are rejected with full state unchanged.
> contrast: The same fixed Oracle schedules fail on the original source, including A→A, A→B→A and cancellation before late success/error.
> integration: Oracle inspects actual returned source/tests and reruns the source-derived event schedules plus preserved native checks; no live UI claim.

## Scope and reserved decisions
> Permitted: Read selected methods and episode raw inputs.
> Permitted: Repair work/session.py; add focused local checks and out/ evidence.
> Permitted: Use one fresh worker for coherent repair under Oracle retained judgment.
> Forbidden: Write outside episode work/ or out/.
> Forbidden: Modify raw inputs or raw-manifest.json.
> Forbidden: Read worked answers, unrelated folders or other agent outputs.
> Forbidden: Use network, live repositories, browser, apps or external messages.
> Single-threaded public callback schedules only; real UI and production integration are not represented.
> Malformed/forged tickets, cross-session tickets, reentrant callbacks and duplicate terminal delivery semantics are outside this local repair.
> Oracle retains integrated judgment; worker self-checks are SELF-ASSESSED.

## Open decisions
> none declared

## Prerequisites and uncertainty
> Blocking unknown refs: none declared
> These are declared dependencies, not proof that prerequisites are satisfied.

## Boundary basis
> KEEP
> Callback identity and cancellation share one state invariant. One repair deliverable avoids splitting coupled finish/fail/cancel semantics; Oracle keeps diagnosis and integrated verification.

## Sources
S-ACCESS: SOURCE / READ_THIS_RUN
> /workspace/scratch/52eed2252c51/tmp/oracle-execution-application/raw/access.md
Revision: sha256:20ac0efe244cf52ceaa0ab62b32f21d95ffc859d30345762933059d4443fd39f
S-BASE: RECEIPT / READ_THIS_RUN
> /workspace/scratch/52eed2252c51/tmp/oracle-execution-application/out/baseline-probe.stdout.txt
Revision: sha256:13c7ecd692d0a0909c1a33e066c257b59ec98b21270c253e37963f081f5ff11e
S-EXISTING: RECEIPT / READ_THIS_RUN
> /workspace/scratch/52eed2252c51/tmp/oracle-execution-application/out/baseline-existing.stderr.txt
Revision: sha256:6023d9f7a5805a0c1abd576e1130784d180c38cae9c8f41bb03254237ab09ffc
S-OWNER: OWNER / READ_THIS_RUN
> /workspace/scratch/52eed2252c51/tmp/oracle-execution-application/raw/owner.md
Revision: sha256:215813d15d8ea3d9404a8ba9e25c8006025139da3978618b8cf94c40dbdbdf59
S-SOURCE: SOURCE / READ_THIS_RUN
> /workspace/scratch/52eed2252c51/tmp/oracle-execution-application/raw/session.py
Revision: sha256:316b565738204bab3c81b6e2143d7bedaa3d8b13bcacf9960dde07c7deb03512
S-TESTS: SOURCE / READ_THIS_RUN
> /workspace/scratch/52eed2252c51/tmp/oracle-execution-application/raw/test_existing.py
Revision: sha256:20b52ced9a30e0367994675446e056e7efd51ee31dc5c94cd79d0be43360dcca

## Performer context
> Oracle with a fresh task-local worker through the available collaboration tool; actual model and reasoning setting UNKNOWN.
> Basis: OBSERVED
> Freshness is prompt/context isolation, not access enforcement.
> No low-thinking model or independence qualification.

## Continuation
> Preserve this issued binding and native evidence. Return discoveries or unresolved judgment to the planner. Refinements must visibly preserve or propose changes to original conditions. No completion, authority or product acceptance is inferred.
