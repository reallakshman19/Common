---
name: prototype-first
description: Deliver each project step as a runnable prototype on the real inputs, recorded as a slice card. Use when decomposing an aim into steps, briefing or onboarding a builder agent, deciding how much checking a step needs, or recording what the user can do today. The Oracle slices, the builder ships something the user runs, and checks scale with the consequence of a mistake.
---

# Prototype-first delivery (slice cards)

Lesson 2 (Owner, 23 Oct 2026: CoordinatorLandingpage #1 comments 6354803323,
6354928122 and 6354995849; proposal and adoption: CoordinatorLandingpage #156).
One builder chat, steered by the Owner on the Owner's real file, gave the Owner a
tool to run locally in about seven hours. The Owner estimated the multi-agent route
at 40+ hours and five agents, with nothing to run at the end. Progress is what the
user can do, per unit of cost.

## Rules

1. **Build first, on the real inputs.** Each step's first deliverable is something
   the user runs with one command or one URL, on the real files from the first hour.
   Synthetic data may add test cases; it never replaces the real input.
2. **Slice thin.** A step is the smallest change the user can see and try. If a
   step cannot show something runnable within its timebox, the Oracle re-slices it.
3. **The user tries it.** A step is not progress until the user (the Owner, or the
   learner for a learner product) has run it. Their reaction drives the next card.
4. **Prove in proportion.** Evidence is written after a working prototype, not
   demanded before one. An independent check runs where a mistake would reach the
   real world (see [check levels](#check-level-by-consequence)), before that use.
5. **Harden what is kept.** What the user keeps moves into the repository with tests
   and a launcher, and from then on the normal delivery and review rules apply.
6. **Record what the user can do.** Each step carries one line in the user's words,
   updated after use.

The Owner may steer the builder directly in its chat. The Oracle records the change
afterwards as a visible card or WBS change; there is no relay and no silent drift.

## Benchmark R0: CIIFR-S1

The reference case every project is compared with: [examples/CIIFR-S1.json](examples/CIIFR-S1.json).
One builder chat (id8 6ada4669), the Owner's real CII model attached in chat, the
Owner correcting meaning as it built (blind round trip versus reconstruction, missing
blocks, which field a value belongs to), a pivot away from a dead-end writer, and a
deliverable with a launcher, a demo and tests. Evidence: XML_Compare_Utilities PR
#156 comment 6354748854. Its next step, with an independent check before real use:
[examples/CIIFR-S2.json](examples/CIIFR-S2.json).

## The slice card

One card per WBS step. Schema: [schemas/slice-card.v1.json](schemas/slice-card.v1.json);
checker: `python scripts/slice_check.py CARD.json` (standard library only).

| Field | Meaning |
|---|---|
| `slice`, `wbs` | the step's id and WBS number; never renumbered when an agent changes |
| `state` | `written`, `building`, `runnable`, `tried`, `accepted`, `hardened`, `verified` |
| `user_can` | one sentence in the user's words: what they will be able to do |
| `user` | who runs it: Owner, learner or reviewer |
| `real_inputs` | each real input and where it lives (a folder or "attached in chat"); never a link |
| `runnable`, `demo` | the one command or URL, and 3 to 6 steps the user performs |
| `done_when`, `keeps` | what the user observes on the real input; earlier benchmarks that must still pass |
| `timebox_h` | builder time before the Oracle re-slices (at most 40) |
| `check`, `why_check` | `none`, `self` or `independent`, and why, set by consequence |
| `probe` | the builder's capability probe (from `building` on) |
| `after_use` | when and by whom it was tried, verdict, gaps, the can-do line, evidence |
| `hardening`, `check_verdict` | repository and exact head with evidence; the independent PASS |
| `owner_steering` | links to the Owner's direct corrections, recorded after the fact |

Private data never enters a card: no chat, Drive or OneDrive links; files are named
by folder, file name and, where useful, SHA-256.

## Lifecycle

```
written -> building -> runnable -> tried -> accepted -> hardened -> verified
                          ^          |
                          +-- gaps --+  (next round of the same card, or a new card)
```

| State | Needs | Progress page `cap` | Gatekeeper label |
|---|---|---|---|
| written | the card | NOT_DEMONSTRATED | — |
| building | a builder with a `probe` | NOT_DEMONSTRATED | — |
| runnable | `runnable` and `demo` that work for the builder | CANDIDATE | DRAFT |
| tried | `after_use` from the user's own run | CANDIDATE | DRAFT |
| accepted | the Owner's words (`after_use.accept_src`) | AVAILABLE for that use | personal-use release where that profile applies |
| hardened | code, tests and launcher in the repository at an exact head | BENCHMARK_SUPPORTED | CHECKED |
| verified | an independent PASS at that head (`check: independent` only) | INDEPENDENTLY_VERIFIED | VERIFIED |

## Roles

| Role | Does | Never |
|---|---|---|
| Oracle | slices the aim into thin steps that each end in something runnable; writes cards; sets `check`; turns the user's reaction into the next card; records Owner steering and pivots | writes long packets before anything runs; demands proof before a prototype exists |
| Builder | answers the probe; builds on the real inputs; asks the user when meaning is unclear; ships launcher, demo and tests; returns a short [prototype return](assets/prototype-return.md) | publishes private inputs or packs; claims `tried` or `accepted` |
| Owner / user | talks to the builder while it builds; tries each runnable; accepts | — |
| Coordinator (OTM) | provisions chats, inputs and launch details; records `after_use` from a read of the chat; keeps cards moving; routes independent checks | relays every message; gatekeeps a prototype |
| Independent checker | checks `done_when` and `keeps` at the exact candidate | reviews its own or its briefer's work |

## Onboarding a builder

1. Send the [capability probe](assets/capability-probe.md) first; record the answer as `probe`.
   Shape the card to what the builder can do: a chat that cannot open links gets files
   by attachment; a builder whose browser is blocked does not get a browser-only step.
2. Send the [builder brief](assets/builder-brief.md) with the card and the real inputs.
3. When inputs live on the Owner's computer and the step needs a file system or a real
   browser, prefer a local builder (Codex, Antigravity, a Claude Code session) over a
   browser chat.

## Check level by consequence

| A mistake would... | `check` |
|---|---|
| cost only the user's time to notice | `none` |
| mislead the user's next decision | `self`: the builder's tests and `keeps` |
| reach the real world: an engineering analysis, a learner's understanding, money, publication or other people's data | `independent`, before that use |

## With the other modules

- [Task Decomposer](../task-decomposer/SKILL.md): its project-level output is a sequence of
  slice cards; [ORACLE_USE.md](../task-decomposer/references/ORACLE_USE.md) binds the Oracle.
- [Nudge Designer](../nudge-designer/SKILL.md): its Oracle prompts start from this default.
- [Independent Reviewer](../independent-review/SKILL.md): scope is the card's `done_when` and
  `keeps`; it runs for `check: independent` cards and at hardening.
- [Gatekeeper](../gatekeeper/SKILL.md): labels apply from `runnable` on as in the table above.
- [Progress Page](../progress-page/README.md): each step shows its can-do line, how to run it
  and when it was tried.
- Engineering PR Delivery applies from `hardened` on, not to a prototype.

## Failure modes and guards

| Risk of going fast | Guard |
|---|---|
| prototype sprawl | timebox; the Oracle checks every card against the aim |
| unchecked real-world use | `check: independent` before that use |
| a prototype only one machine can run | hardening moves code, tests and launcher into the repository |
| the user becomes the bottleneck | an untried runnable is raised to the user after 24 hours |
| builder limits found late | the probe comes before the card is final |
| private data leaks | cards name files, never links; packs stay in the private handoff folder |

## Measures

Compare each project with R0: time to first runnable, slices tried per week, user
hours, agents per accepted slice, tokens per accepted slice and the share of slices
reworked after use.
