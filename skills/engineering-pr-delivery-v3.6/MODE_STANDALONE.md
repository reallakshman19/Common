# v3.6.1 Standalone mode

**Selection:** `mode: standalone` in an approved
`relay/AIM/<WORK>.yaml`. No mode means **coordinator**, not standalone.
Both modes use the identical native v3.6 O1–O5 lifecycle, formatter,
plan/label source guards, successor reader and separate two-/three-pass
generators. A standalone project is one Owner working with one coding agent.

## Isolation: enforce it before any provider operation

A standalone label must not name a `CoordinatorLandingpage` repository
as its `repository` or its `Writable lab:` target. Every label/target
CLI calls the shared `lifecycle_v36` label validation and explicit-target
resolver before constructing the GitHub client or making a read or write.
The guard rejects the coordination repository case-insensitively for
both GET and mutation paths. A rejected target must produce zero provider
operations. It is not enough to refuse only `--apply`; read-only cold,
snapshot, publisher and prompt-generation paths must also refuse it.

Standalone has **no** TeamCoordinator, OwnerTeammember, Oracle, shared
coordination registry, logged chat-send route, team mirroring or NextMove
dependency. Local configuration and sources cannot indirectly grant
coordination-repository access. The Owner may use a separate NextNudge
Tab later, but it is **not** an implemented dependency in WP1.

## Owner and agent workflow

1. Owner supplies the source prompt/issue, actual label, approved plan,
   scope, protected files and task child issue. Agent checks the assignment
   against source words; it does not presume admission from a fixture.
2. Agent writes falsifiable tests first; record their failing commit and
   the full suite counts before committing the implementation.
3. Agent runs the complete applicable suite after the fix (or reports
   NOT_RUN), checks A13 against exact base/head and preserves evidence.
4. For every completed task, publish the unchanged native eight-line
   record **on the real child issue**, with a separate A14 self-check and
   the terminal LOG line. Do not create a team evidence mirror.
5. Owner reviews the source-bound evidence, limitations and actual
   work. A qualified independent reviewer is optional for standalone.
   The agent never self-approves. **The Owner merges and accepts.**
6. Owner may run the v3.6 cold successor packet from GitHub directly.
   A packet or a test result is never itself Owner acceptance.

## A01–A14 disposition for both modes

**Core** remains mandatory in both. **Simplified** retains the core
safety outcome without the team-specific machinery. The coordinator
additions below are **coordinator-only**, not a second execution engine.

| ID | Classification | Standalone meaning / coordinator-only addition |
|---|---|---|
| A01 | Core | Approved label, plan, child and actual permission; coordinator checks registry/custody too |
| A02 | Core | Reconcile original Aim, amendments, benefits and exclusions; coordinator checks Owner #1 |
| A03 | Core | Source-bound Owner input and private custody; coordinator also attributes relayed words |
| A04 | Core | Identify originals, hash and golden/benchmark completeness, or explicitly UNKNOWN |
| A05 | Core | Trace input through code to consumer and falsifier; no invented integration |
| A06 | Core | Own-child canonical evidence plus separate context; coordinator-only evidence-issue mirror |
| A07 | Core | Report genuine failures, NOT_RUN and unresolved capabilities |
| A08 | Core | Preserve previous contributions and sourced historical issue lineage |
| A09 | Core | Record KEEP/IMPROVE/PARK with rationale and source; no unauthorized redesign |
| A10 | Simplified | Child issue to PR/evidence and permitted private-chat reference; no team registry |
| A11 | Core | Use selected native successor/two-/three-pass stages without mixing blind-phase inputs |
| A12 | Simplified | Supply truthful facts to native lifecycle titles/scoreboard; no coordinator NextMove publisher |
| A13 | Core | 300-line ratchet, ~50-line cohesive functions, no duplicate engines, tests and counts |
| A14 | Core | Source-bound self-check before claims; Owner assesses, not the doer |

The coordinator-specific routing, role tags, independent review and team
mirror live in [MODE_COORDINATOR.md](MODE_COORDINATOR.md). The exact native
A01–A14 wording remains in [CODING_PRACTICES_ADDENDUM.md](CODING_PRACTICES_ADDENDUM.md);
this table classifies it without weakening any protected part.

**Staged additions:** C1–C18 and the unified checker arrive in WP2;
CRITERIA v1 and SELF-CHECK v2 scoring arrive in WP3. Until then use
existing A13/A14 and SELF-CHECK v1. No canonical evidence/LOG changes.
