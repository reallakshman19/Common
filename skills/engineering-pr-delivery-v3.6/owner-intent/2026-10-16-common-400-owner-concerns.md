# Owner Statement of Concerns, Requirements and Proposed Concepts
## Engineering Relay v3.6 — Issue-Centred Continuity, Evidence and Agent Traceability

**Document type:** Formalised Owner-intent statement  
**Date:** 16 October 2026  
**Programme:** `reallakshman19/Common` — Engineering PR Delivery v3.6 / Handover Master  
**Authorial basis:** The Owner's requests and technical examples in the conversation. The wording is formalised; it must not be mistaken for additional Owner approvals.  
**Primary tracking issue:** [Common #400](https://github.com/reallakshman19/Common/issues/400)

> **Governing intent.** Even the tenth incoming agent must be able to determine what the second agent did, which original inputs and goldens were used, which technical instructions the Owner later supplied, which improvements were adopted or parked, why those decisions were made, and what remains genuinely unresolved—without relying on access to the predecessor's chat.

## 1. Problem statement

The current engineering relay has made progress in tracking issues, pull requests, workpacks, checks and handover stages. It does not consistently preserve the **meaning and causality** of the work across long chains of agents. A handover can present passing tests, current PR status and a next task while losing the original engineering problem, actual production fixture, benchmark, root cause, prior decisions, Owner corrections and unimplemented high-value ideas.

The Owner's concern is **continuity of engineering truth**, not merely improved reporting. A future agent must be able to reconstruct *why* work began, *what physically or functionally happened*, *which evidence established that*, *how the architecture evolved*, and *which permissions remain withheld*.

## 2. Concerns and observed failure patterns

| Ref | Owner concern | Consequence to prevent |
|---|---|---|
| C-01 | The original human-language problem and Owner intent fade behind later workpack summaries. | A successor optimises a local PR instead of the requested product outcome. |
| C-02 | Significant technical inputs supplied by the Owner through chat are not reliably captured on the owning issue. | Later agents cannot distinguish a direct correction from an agent's interpretation. |
| C-03 | Original positive/negative fixtures, complete goldens and benchmark definitions are difficult to recover. | Synthetic inputs, partial outputs or green CI are mistaken for the original acceptance oracle. |
| C-04 | Agent-to-agent history is not navigable beyond the last handover. | Work and findings of agents 2 or 3 disappear before agent 10 starts. |
| C-05 | Reports emphasise PR counts, test counts and stage state rather than the implementation crux. | The real failure mode and source-to-output flow are lost. |
| C-06 | High-ROI improvements proposed during BuddyRunner or multipass reasoning lack durable disposition. | Parked ideas are forgotten, rejected ideas recur, and adopted changes lose their rationale. |
| C-07 | Issue succession is not always traceable, particularly if an intermediate issue becomes invalid, inaccessible or superseded. | Historical work is silently removed from the chain. |
| C-08 | An ad-hoc agent told to use v3.6 may omit task evidence when no coordinator established the formal workpack. | Useful technical progress has no durable, attributable receipt. |
| C-09 | Current dynamic titles and labels do not expose the completeness or drift of intent, fixture and decision chainage. | Visible progress appears healthier than the underlying evidence. |
| C-10 | The original ChatGPT agent conversation behind a GitHub PR is not readily discoverable. | GitHub identifies an account, but not the responsible conversation, prompts or handover context. |
| C-11 | Handover, BuddyRunner, two-pass, three-pass and zero-exit workflows are distributed across source folders. | Agents select inconsistent protocols or fail to use the proper mode. |
| C-12 | Existing v3.5 coding/continuity disciplines are not comprehensively expressed in native v3.6. | Source-first recovery, material-drift detection and issue-based evidence become discretionary. |

## 3. The central concept: an issue is a traceable engineering artifact

The Owner proposes that the **owning GitHub issue** be the durable navigation point for the entire engineering chain. The issue should not be a mere message history or a list of commits; it should index the definitive evidence and technical decisions that give those commits meaning.

At minimum, the issue should make the following discoverable:

1. **Original Owner intent:** the first problem, intended outcome, constraints, operating range and acceptance rules, in human language.
2. **Later Owner technical input:** important corrections, chat-supplied facts, changed decisions, attachments and why they supersede earlier assumptions.
3. **Original materials:** exact original source fixtures, negative examples, goldens, benchmark definitions, hashes, versions and evidence of completeness—or an honest declaration that they are missing.
4. **Implementation crux:** causal source code path from user input through parser/adapter/worker/decision authority to consumed output, with changed functions and demonstrated behaviour.
5. **Contribution chain:** significant analysis, coding, tests, failures, decisions and handovers by successive agents; not just their names or PR numbers.
6. **Improvement register:** KEEP, proposed IMPROVE, adopted high-ROI change, rejected alternative and parked candidate with the reason and a revisit condition.
7. **Current truth:** live main and candidate PR heads, exact tests and actual workloads, unresolved failures, reviewer/Owner gates and the next reproducible verification.
8. **Agent and conversation provenance:** links to relevant agent conversations or appropriately restricted references, where available, alongside their owning issues and work products.

**Owner's meaning of “100% chainage”:** the required history must be accounted for end-to-end. Missing material must be made conspicuous rather than inferred away. An explicitly recorded `UNKNOWN` is not a verified source; therefore completeness of *accounting* must not be confused with completeness of *proof*.

## 4. Lossless issue lineage, including invalid or deleted intermediate steps

The Owner's proposed visual model is:

**Issue #123 → ~~Issue #125~~ → Issue #126**

If #125 is later found invalid or superseded, it must remain at its historical position, visibly struck through, with a reason and a trace to the disposition. The chain must not be rewritten as if #125 never existed. Its analysis, technical evidence and Owner inputs may still explain why #126 took a different direction.

Formalised requirements:

- Preserve the original hop, successor link, issue identity, date/source and reason for invalidation or supersession.
- Display a struck-through node only when the disposition is specifically reported and source-linked; distinguish an assertion from independent confirmation.
- Treat an inaccessible, permission-denied or 404 issue as **unverified availability**, not automatically as a deleted issue.
- Keep the chain usable in both human-readable issue text and a structured evidence index.
- Support non-linear history, corrections and alternatives without destroying the chronological path.

The numbered example is **illustrative**, not an assertion that those particular GitHub issues are invalid.

## 5. Task evidence: governed and ad-hoc use must differ

The Owner observes that a coordinator normally enforces task evidence, but a newly introduced ad-hoc agent may receive only the instruction “follow v3.6” and leave no useful record.

The requested behaviour is conditional:

| Situation | Required interpretation |
|---|---|
| A formally governed v3.6 parent, AIM label, plan and owned child exist | Keep the established native task-evidence rule; do not silently weaken it. |
| The project supplies a different explicit evidence protocol | Follow that protocol, not an unsolicited v3.6 substitute. |
| A genuine ad-hoc task has no specified evidence protocol | Offer an **optional lightweight evidence receipt** that records useful work and source pointers. |
| The agent has no authorised issue destination | Provide a copyable receipt rather than publishing it somewhere arbitrarily. |

The optional receipt should capture the human outcome, exact source revision, implementation crux, original inputs/golden/benchmark, tests, issue chain, known gaps, parked ideas and one next verification. It must not pretend to satisfy a governed task's official completion, Owner acceptance or release requirement.

## 6. v3.5 coding practices the Owner wants ported

The Owner asks that effective v3.5 coding and continuation disciplines be available as a **v3.6 addendum** rather than merely as inaccessible historical folders. The intended practices include:

- Reconcile the original Owner roadmap and current repository state **before** proposing changes.
- Work **source-first**, not from PR descriptions or predecessor assertions alone.
- Preserve stable components and existing authority; favour bounded, high-value integration over patchwork or duplicate engines.
- Explain causal implementation changes—input, code path, owning module, state boundaries, consumer and observed output.
- Bind evidence to exact commits, fixtures, benchmarks and test runs, and mark stale evidence honestly.
- Maintain meaningful child-work ownership and separate facts from completion projections and protected approvals.
- Record accepted improvements, rejected approaches, parked proposals and why each disposition was chosen.
- Write a complete technical handover with the original problem, source files, tests, known defects and exact successor starting point.
- Detect drift when live source, Owner decisions, fixture identity or PR ancestry changes.
- Preserve prior evidence instead of overwriting or simplifying history after a correction.

Port the **practices**, not a dependency on the v3.5 runtime or an indiscriminate new protocol controller.

## 7. Dynamic issue labels and smart titles

The Owner specifically requests the useful dynamic marking, progress detection and smart draft-title behaviour associated with v3.5 to be made available in v3.6.

The visible issue and PR state should distinguish real task evidence from missing Owner input, missing original fixtures, stale test heads, unresolved acceptance and broken chainage. Title updates should preserve the meaningful human title, identify the true issue or PR, and avoid promoting a draft or partial evidence count into Owner acceptance.

The approved **AIM label** is a source of governance and should remain distinct from automatically derived GitHub workflow/status labels. An invalid or missing issue link should be displayed as chainage degradation, not silently hidden.

## 8. Connecting BuddyRunner, multipass and Handover Master

The Owner wants a single usable entry point without losing what makes each process valuable:

- **Handover Master** selects the appropriate native method and exposes where its authoritative sources live.
- **BuddyRunner** preserves the outgoing/incoming agent challenge, reconciliation and parked-improvement decisions without endless handover loops.
- **Two-pass / three-pass** methods preserve genuinely independent early analysis and subsequently record the reconciliation between ideas and engineering reality.
- **Technical handover** preserves the full implementation explanation, original fixture and remaining risks—not just process statistics.
- **Zero-exit onboarding** permits a new agent to reconstruct the project from issues, GitHub source and evidence even if no predecessor submitted a final LOG.

The same underlying issue history should support these methods while respecting blind-stage isolation and each method's existing phase boundaries.

## 9. Real examples that motivate the requirements

### 9.1 3D_Converters: Issue #274

The Owner highlighted a case where a Worker reported **41 branches, 423 physical components and 2,961 FactRecords**, yet the cited session showed **zero accepted Match-1 weights, zero accepted Final weights and 423 unresolved physical weights**. A summary saying “Preview is ready” would hide the actual remaining mass/decision problem.

The investigation also distinguished a DOM-only readiness projection from canonical readiness, a legacy **28/28** regex message from the **41/41** selected branch context, and an unproven served-asset version. A valid handover must preserve those distinctions and the separate native CII qualification/release gate. These numbers are a historical reported observation, **not a newly measured benchmark or acceptance**.

### 9.2 Common: PR #398

When the Owner asked for the agent conversation responsible for Handover Master PR #398, GitHub showed the contributing account and commits, but no ChatGPT conversation URL in the PR description or comments. This illustrates the difference between **Git author identity** and **agent-session provenance**.

The desired outcome is for future work to make the responsible agent's conversation or a privacy-safe trace discoverable where permitted, without assuming GitHub automatically possesses ChatGPT conversation identifiers.

### 9.3 Physics QRT continuity

The Physics programme supplies a cross-project check: a structurally verified shared blueprint map and passing CI are not the same as independent academic acceptance. A successor must find the original NLM question, reviewer disposition, source SHA and remaining human review gate, rather than summarising “27 tests passed.”

## 10. Owner-required acceptance demonstration

A newly onboarded agent who receives **only an owning issue URL** should be able to:

1. State the original Owner outcome and every material later correction with attributable sources.
2. Identify the original positive and negative input fixtures, full golden and benchmark, or name the exact evidence that is unavailable.
3. Trace the actual current input-to-output code path and explain what prior agents changed.
4. Explain why a promising idea was **adopted**, **rejected** or **parked**, including its author and revisit condition.
5. Follow the full issue chain, including invalid/superseded middle issues, without losing their history.
6. Find the relevant agent handover or conversation reference when it was recorded, or state that it was never captured.
7. Separate passing structural checks from substantive engineering or academic acceptance.
8. Produce a complete technical successor handover and one reproducible next action.
9. Detect a stale SHA, missing fixture or changed Owner decision instead of proceeding on false assumptions.
10. Respect existing safety, evidence, reviewer, privacy and Owner-approval boundaries.

**Success is reconstruction of the engineering truth, not simply production of a longer issue comment.**

## 11. Boundary between Owner concepts and implementation proposals

The preceding sections formalise the Owner's concerns, examples and requested outcomes. They do **not** prescribe an exact JSON schema, an autonomous title publisher, automatic ChatGPT history capture, or a new GitHub permission model.

Those mechanisms are architectural choices for engineering qualification and are defined separately in **Document 2: Detailed Architecture and Implementation Plan**. Any proposal requiring new access, a changed evidence protocol, publication of private chats, or release authority needs explicit governance and acceptance.

## 12. Reference record

- [Common Issue #400 — source-first continuity programme](https://github.com/reallakshman19/Common/issues/400)
- [Common PR #401 — draft issue-chain validator](https://github.com/reallakshman19/Common/pull/401)
- [Common PR #402 — draft coding-practices addendum](https://github.com/reallakshman19/Common/pull/402)
- [Common PR #398 — merged Handover Master](https://github.com/reallakshman19/Common/pull/398)
- [Common Issue #341 — accepted v3.6 lifecycle](https://github.com/reallakshman19/Common/issues/341)
- [3D_Converters Issue #274 — technical continuity example](https://github.com/reallakshman19/3D_Converters/issues/274)
- [Physics QRT Issue #287 — scientific review source](https://github.com/reallakshman19/Grade9v3.5/issues/287)

**Status of this document:** A formalised statement for review and implementation planning. Not an additional Owner acceptance record and not a substitute for the original conversation and issue sources.
