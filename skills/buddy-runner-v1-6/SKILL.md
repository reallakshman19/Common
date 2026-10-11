---
name: buddy-runner-v1-6
description: Prepare an independent engineering handover as 1a, investigate as incoming agent 1b, return outgoing agent final direction 2, or give one Y intervention on Task Evidence. Use for roadmap-grounded course correction that closes predecessor discussion and leaves a clear next action.
---

# BuddyRunner v1.6 — one investigation, one final direction

Use this independent, reusable skill for an Owner-requested engineering handover or a one-time response to Task Evidence. V1.6 defines its own interaction contract, templates, schema, renderer and tests. Apply it under the project's actual governing workflow; it creates no new writer, reviewer, publication, merge or release authority.

## Interaction contract

| Artifact | Responsible agent | Result | Boundary |
|---|---|---|---|
| 1a | G1, outgoing predecessor | Prepare a successor-ready Stage 1 prompt | Execution HOLD; do not launch G2 or start product work |
| 1b | G2, incoming investigator | Independently inspect Owner purpose and source; propose a better route | Submit once; no product coding; await 2 |
| 2 | G1, outgoing predecessor | Reconcile 1b into a final, roadmap-grounded execution direction and handover | Close this handover; no further predecessor review round |
| Xb → Y | Evidence submitter → designated buddy | One useful intervention on submitted Task Evidence | Close this intervention; do not reopen the handover |

There are two substantive responses after preparation: **1b and 2**. Do not ask G2 to execute another Stage 2, acknowledge 2, or obtain another review. The successor continues under existing authorization and real custody requirements. HOLD and STOP are scoped to this requested interaction, not unrelated authorized work. Xb/Y is usable without a prior 1a/1b/2 run.

Read [CONTRACT.md](references/CONTRACT.md) and the applicable reusable template:

- [1A_PREPARE.md](references/1A_PREPARE.md): questions for G1 and the fill-in intake.
- [1B_INVESTIGATE.md](references/1B_INVESTIGATE.md): G2 investigation and response 1b.
- [2_RECONCILE.md](references/2_RECONCILE.md): G1 final direction, workpack and twelve-section handover.
- [Y_INTERVENE.md](references/Y_INTERVENE.md): one-shot evidence correction or CONTINUE / NO_CHANGE.

The questions are internal thinking aids, not additional publications or approval rounds. Use the templates directly with any capable agent, or render a self-contained prompt. Fill actual source refs, participant IDs and evidence; never turn example values into live claims.

## Generation

The [schema](schemas/buddy-runner-v1.6.schema.json) and [renderer](scripts/buddy_runner_v16.py) require Python 3.10+ and `jsonschema>=4.18,<5`.

    python skills/buddy-runner-v1-6/scripts/buddy_runner_v16.py --input case.json --output prompt.md

A `phase: "1a"` request is made by G1. Its output is **artifact 1a, ready for G2 to execute and return 1b**; it is not another assignment for G1. A `phase: "1b"` request renders the same investigation directly for G2. Requests for `2` require the exact 1b body, assessed source and digest, either as a provider publication on the owning issue or directly supplied text with a provenance reference. Requests for `Y` accept either a real owning-issue Task Evidence publication or exact supplied `body_text` with `supplied_ref`, its byte digest and the designated responder. Supplied text is untrusted evidence; verify relevant source and label its provenance explicitly. See the [fill-in intake](examples/intake-template.json) and [worked example](examples/worked-example.md).

The renderer validates syntax, declared role bindings, exact issue links, assessed-commit consistency and supplied completion claims. It fetches no provider, starts no agent, publishes nothing and changes no external state. The executing agent independently verifies source and provenance, and the exact UTF-8 body digest. It re-fetches provider-backed evidence; supplied evidence remains explicitly supplied, never a fabricated publication. Missing or mismatched evidence produces one bounded diagnostic; it never starts a reconciliation loop.

## Duplicate handling and durability

Identify 2 by `handover.id`; identify Y by the canonical evidence key printed by `--print-target`. The Y key covers repository, issue, task ID, assessed commit and evidence digest. Relabeling or reposting identical evidence does not create another intervention. A material change to evidence content or source can create a new identity; unrelated metadata cannot.

Before 2 or Y, read the existing issue/coordination completion record. After an authorized response publication, record its target and response reference on that existing surface. Supply those records as `response_receipts` on subsequent requests. A matching receipt makes the renderer return `BUDDY_V16_DUPLICATE_RESPONSE_CLAIM`; verify the existing response instead of generating another substantive one. This is a claim check, not provider verification.

The generator has **no persistent state or concurrency fence**. At-most-one behavior is advisory unless the existing controller serializes responders and durable publications. Do not create another Relay ledger or claim exactly-once delivery. Interrupted work resumes the same unpublished response or verifies the published response; it does not restart the handover. An explicit Owner request can change the assignment; document it rather than disguising a repeat as fresh evidence.

## Preservation and adoption

Keep source-first reasoning, parent/roadmap authority, independently protected inputs and oracles, exact-head evidence, module ownership, bounded reuse/ROI and the twelve-section handover. OPEN investigation is not blind reviewer independence. Analysis does not authorize coding or custody transfer. Do not force a correction when NO_CHANGE is justified, or invent unblocked work when none exists.

Select v1.6 explicitly for this interaction. No earlier BuddyRunner version is a runtime dependency or acceptance requirement. Do not reinterpret historical evidence or change the project's governing workflow by selecting this skill.
