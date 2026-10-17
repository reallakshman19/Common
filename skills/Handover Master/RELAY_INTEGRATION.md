# Handover Master: relay integration (Common #408 HM-02)

**What this adds:** how a handover keeps a project's **meaning** across many runners, and **who** owns each transfer fact. It is guidance over existing records. It is **not**:
- a new lifecycle;
- an evidence block or ledger;
- a scheduler or dispatcher.

Mode selection stays in [SKILL.md](SKILL.md) and [DECISION_GUIDE.md](DECISION_GUIDE.md), and the native modules keep their own phases and contracts. Source: [#408](https://github.com/reallakshman19/Common/issues/408) (plan, Codex review, frozen contract).

**The goal, in the Owner's words:**
- runner six must know what runner three did **and why**;
- runner ten must still know the original Owner intent and every later Owner change.

## 1. The work outlives its runner

The project is not its current chat. Before writing a handover, and again on taking one over, make these **findable from existing records**: the owning issue, the native evidence, the plan/registry, PRs and decisions. Mark each one UNKNOWN when it is missing; never invent it.

| Must be recoverable | Where it normally lives | If missing |
|---|---|---|
| Original Owner words, and every later amendment with its full conditions, expiry and non-goals | owning issue body/comments; the project decision record | UNKNOWN, and name the gap; do not paraphrase it into a fact |
| Project → Aim → Task: the current stable task, done-when, accountable owner | plan / label / registry | ask the controller; do not choose your own task |
| The authentic oracle: original positive/negative inputs, full vs partial golden, benchmark | fixture paths at an exact SHA + hash | ORIGINAL / SYNTHETIC / PARTIAL / MISSING, never "verified" by name alone |
| Separate source identities: inherited, assessed, live, tested | commit SHAs per role | one ambiguous SHA is a defect |
| Done / PARTIAL / FAILED / NOT_RUN / UNKNOWN work and pending actions (incl. uncertain sends) | native evidence + the controller's records | a pending action is never dropped by a handover |
| **Earlier causal decisions**, rejected alternatives, retired contributions, and why a route survived or was superseded | the evidence history and the decision records | link the older record; a short brief is an **entry point, not the whole history** |
| Own and peer responsibilities, authority/custody limits, the smallest next action | registry/control; this guide §3 | — |

**Private and blind inputs:** disclose task knowledge only at the native phase that permits it ([DECISION_GUIDE §3](DECISION_GUIDE.md)). A public 8-character chat id is a locator, not identity.

## 2. Four situations: help, planned succession, disappearance, status

| Situation | Route | Who stays responsible |
|---|---|---|
| **The runner lacks a capability** (local run, browser check, private file) | Ask the controller for **one bounded operation**: source, exact operation, expected output, privacy/stop limits. The helper returns source-bound evidence | **The original runner keeps the task.** Help is not a replacement, a takeover or a reason to redesign |
| **Planned succession** (the outgoing runner is still alive) | Native selected method, e.g. BuddyRunner 1a → 1b → 2. Own-words, source-grounded understanding belongs **inside 1b**; the final direction belongs in **2**. No acknowledgement round, no phase 4 | Outgoing until cessation and custody transfer; incoming only after activation |
| **Disappearance** (no final LOG; the chat is gone) | `zero-exit` reconstruction from GitHub. If the project uses BuddyRunner, the authorised coordinator may act as G1 for 1a and 2 from cited records, marking inherited claims as **hypotheses** | the controller, until a qualified successor is activated |
| **Status only** | `status` mode: read-only | nobody acts because of a status read |

**When to start a planned succession:** only under the project's **recorded** standby/launch grant, at a real trigger (a self-reported warning, a measured meter where one exists, or a real chat-end sign). Slowness alone means triage, not a launch. Not having started early enough is a reason to fix the trigger, never to skip the native phases.

## 3. Transfer facts and their owners

The router can preview; it never verifies. These facts belong to the **caller/controller**, and each must be established separately:

| Fact | Owner | Not established by |
|---|---|---|
| Version/phase selection is governing (incl. a version amendment) | governing project/native contract, checked by the controller (see SKILL.md, "v3.6 version amendments") | a router `PROVISIONAL_ROUTE`, a URL, a CLI exit code |
| Real delivery / pickup, and uncertain sends | the single authorised deliverer, with supported receipts | publishing a packet or a comment |
| Incoming understanding | the incoming investigation (1b), judged by a responsible reviewer | a filled template, a citation count, CI |
| Outgoing cessation, exclusive custody, current work grant | project control/registry | silence, a full chat, a generated handover |
| Grant / expiry / HOLD / counters | authoritative project state, kept across the handover | a restart, a rename, a new chat |

**A reservation that expires never clears an uncertain send.** Reconcile it before any resend.

## 4. Every handover leg should leave value (without forced novelty)

- Record at least one **considered** improvement with its disposition: ADOPTED, PARKED (with a revisit trigger), or REJECTED (with a reason). Alternatively, record an evidenced **KEEP / NO_CHANGE** (reuse beats novelty).
- Reuse the native slot where one exists: BuddyRunner v1.7 G2's "up to 3 high-ROI actions, each with a falsifier".
- Medium/low-ROI ideas stay recorded as PARKED with their revisit trigger, so runner ten can find them.
- **Scope changes go to the controller/Owner.** A drift finding does not authorise a redesign.

## 5. A useful final report: NEXT VERIFY

Keep the existing report headings ([DECISION_GUIDE §6](DECISION_GUIDE.md)). Make the single next verification concrete:

```text
NEXT VERIFY: <actor> runs <exact command/check> on <repo>@<sha40> (<issue/PR>)
  expected: <observable result>      if different: <what it means, who decides>
  stop if: <HOLD / missing grant / stale head / missing original>      unblock: <event>
```

## 6. What invalidates what

A change to any of these invalidates **only the conclusions that depend on it**:
- the Owner decision or amendment;
- the source SHA or PR head;
- the fixture/golden identity;
- a grant/expiry/HOLD;
- an edited evidence body.

History stays. Never silently retarget a frozen baseline, and never re-mark stale evidence as fresh.

## 7. Out of scope for Handover Master

- **Drift during ongoing work** belongs to the controller's grounding: gap-specific questions from the evidence, never a CI rule.
- **Watchers, schedulers, dispatch, capability brokering, grant/lease runtimes** belong to the controller.
- **Acceptance, release, rights** belong to the Owner.

Master points to these responsibilities; it does not implement or verify them.
