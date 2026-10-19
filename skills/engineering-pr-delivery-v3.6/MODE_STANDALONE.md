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

## ChatGPT-agent activity

For an explicitly identified **ChatGPT agent**, activity recording is mandatory
and BuddyRunner must be suggested when GitHub-access turns exceed five OR recorded
active-turn elapsed time exceeds **35 minutes**. The executing agent runs the
recorder; an available Oracle/lead reconciles its return. No Oracle is required.
ChatGPT Work and other hosts are exempt; UNKNOWN applicability remains visible.
Preserve partial observation honestly.
Follow [the activity policy](references/CHATGPT_AGENT_ACTIVITY.md); do not install
hooks, force a handover, count tool calls as turns or change coordinator mode.

## Owner and agent workflow

For cold/missing context, use [independent reconstruction](references/INDEPENDENT_RECONSTRUCTION.md),
never a Q1–Q5 questionnaire, pass mark or scored agent admission. The executing
agent derives its own account from original sources; no examiner/Oracle is needed.
If BuddyRunner, two-pass or three-pass is selected, use only its native stages.
After it is completed, additional reconstruction is **NOT_APPLICABLE**: reuse the
outputs and continue authorized work, with targeted updates for new facts.
Do not turn the task self-check below into a qualification exam.

For a usable Oracle OnBoard Prompt, check essential originals/current candidate
and execute the bounded task within authority. The Owner/available lead can prepare
it; no Oracle role or separate reconstruction report is needed. Correct a stale
explanation from evidence and return actual results, changed understanding,
remaining parent work and the next justified action. Native completion checks remain.

1. Owner supplies the source prompt/issue, actual label, approved plan,
   scope, protected files and task child issue. Agent checks the assignment
   against source words; it does not presume admission from a fixture.
2. Agent writes falsifiable tests first; record their failing commit and
   the full suite counts before committing the implementation.
3. Agent runs the complete applicable suite after the fix (or reports
   NOT_RUN), checks A13 against exact base/head and preserves evidence.
4. Before claiming DONE, apply the [standalone completion checklist](references/STANDALONE_COMPLETION.md)
   against every frozen criterion and the actual result. Publish native
   **SELF-CHECK v1** first; v2 scoring is optional supporting context. Use the
   standalone-only read-only helper if useful. Local checks are valid without CI;
   record that limit and do not invent a CI or reviewer dependency.
   For every completed task, publish the unchanged native eight-line
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

**Standalone-only invocation:** “Use engineering-pr-delivery-v3.6 in standalone
mode only; apply its standalone completion checklist before calling this task DONE.”
Keep this module in its current folder. No other skill or team role is required.
The extension uses native A14; it does not alter coordinator mode or shared tools.

**Start here:** the [standalone completion guide](references/STANDALONE_COMPLETION.md)
provides the pre-DONE method and template. The [standalone quickstart](QUICKSTART_STANDALONE.md)
also walks the Owner through a throwaway label, frozen criteria, native child
receipt, optional scored companion and Python CI checker, and final Owner decision.
C1–C18 checking and SELF-CHECK v2 are already available in native v3.6.
Keep A13/A14, original v1 companions, canonical evidence and LOG unchanged.
