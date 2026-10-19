---
name: independent-review
description: Review an exact artifact, implementation, calculation or learning resource against original intent and actual evidence. Use for source-grounded assessment, adversarial checks, review evidence collection, self-review with disclosed limits, or a distinct review. Adapt to available participants and project type; use optional Task Decomposer, Nudge Designer and project-policy adapters without requiring them.
---

# Independent Reviewer

Prototype v1.0. Review directly from the Owner's request, original sources and the
actual candidate. Use ordinary prose or the project's native reporting format.
Treat structured records, scripts and other skills as optional conveniences.

Start with: **"Review <candidate> against <purpose/sources>. Use the participants
and tools available. Show evidence, limitations and the next useful action."**

## Choose the smallest useful arrangement

| Available arrangement | Apply it this way |
|---|---|
| One agent | Reconstruct, inspect, check and reconcile in one session; disclose authorship and prior exposure. Keep useful self-review evidence. |
| A narrower worker and a lead | Give the worker a coherent GUIDED evidence operation; retain interpretation and coupled decisions with the lead. |
| A separate reviewer | Establish the relevant independence basis; select DIRECT or GUIDED support for the actual task. |
| A team | Split only where durable evidence can travel without losing necessary state or judgment. Name who integrates the returns. |

These are arrangements, not qualification levels. One participant can hold several
responsibilities. The Owner or lead can reconcile without an Oracle title. Do not
wait for a missing role, module, schema, calibration count or CI. Continue feasible
work and state precisely which claim the available evidence cannot establish.

## Apply the review method

Use these responsibilities in the order the problem needs, combining or revisiting
them when useful. They are not compulsory passes or a lifecycle controller.

1. **Recover meaning.** Read original purpose, amendments and applicable criteria.
   Separate FACT, REPORTED CLAIM, HYPOTHESIS and UNKNOWN. Challenge an incomplete
   brief or faulty premise without silently changing the assignment. Preserve the
   parent outcome when reviewing only a component.
2. **Bind the actual subject.** Identify task, candidate(s), source revisions and
   this review attempt separately. Inspect the real artifact and inputs. Record
   byte hashes where identity matters; a filename, copied hash or PR summary is
   insufficient. Name unavailable resources and continue unaffected checks.
3. **Disclose independence.** State authorship, inherited context, reference access,
   expected-behavior derivation, execution and upstream shared assumptions. Use
   [independence guidance](references/INDEPENDENCE.md). Fresh context alone proves
   neither distinct authorship nor independent judgment. Never rename self-review.
4. **Select a discriminating method.** Derive expected behavior from authoritative
   sources, inspect implementation and integration, and try a relevant contrary
   condition. Ask what plausible wrong result could survive the proposed check.
   Inspect the test oracle, not only its green result. Use
   [applying guidance](references/APPLYING_GUIDANCE.md) for domain and capability
   choices. Add discovered risks even if absent from the initial claim list.
5. **Inspect actual evidence.** Connect each conclusion to source, candidate,
   observation/derivation and a retrievable witness. Distinguish executed checks,
   inspected existing receipts, simulations and NOT_RUN. A command string alone
   does not prove execution; a digest proves bytes, not their technical meaning.
6. **Return a scoped assessment.** Report supported and contradicted claims,
   findings, untouched scope, uncertainty and next useful action. Preserve known
   defects alongside missing checks. An evidence-backed empty finding set is valid.
   Review completion, coverage, independence and Owner acceptance are distinct.
7. **Reconcile and continue.** Have the available lead/Owner/reviewer compare the
   return with the original outcome and current candidate. Preserve the reviewer's
   actual verdict and record any disagreement separately. Revisit only affected
   claims and dependencies; keep integrated acceptance visible. Use
   [reconciliation guidance](references/RECONCILIATION.md) when work spans attempts.

Review findings do not grant product-edit, publication, merge or release authority.
Use authority already given by the Owner/project. If an authorized repair is made,
record the new candidate and the reviewer's contribution; reassess affected work.

## Match support to the task

Use **DIRECT** support when the participant can select and justify a method. Use
**GUIDED** support for a bounded operation with explicit input access, method,
decision rules, negative condition and native return. Keep the WHY and necessary
understanding; shortening context must not remove a load-bearing decision.

Use [review prompts](assets/prompts.md) and [record templates](assets/templates.md)
as needed. A tidy ACK or repeated format compliance is not evidence of model,
safety or architectural judgment. Adjust support from observed task performance;
do not assign competence from a model label. No fixed worker or review count applies.

## Connect only the adapters that help

Read [optional adapters](references/ADAPTERS.md) only when using an existing task
map, participant brief, project review profile or tracker. Modules exchange issued
records and references; no sibling imports, automatic invocation, dispatch or
permission service is required. Adaptation must preserve task meaning and source
authority. Absence of an adapter does not waive an already applicable project rule.

Use [contracts and helpers](references/CONTRACTS.md) only for structured records or
repeatable checks. Two optional JSON schemas describe a Review Case and Review
Result. Helpers can inspect bindings, supplied freshness observations and local
bytes. They do not certify reasoning, identity, independence or acceptance.

## Reference cases and prototype use

Read [golden cases](examples/INDEX.md) for sound work, wrong shared oracles, stale
candidates, partial evidence, self-review and narrow evidence collection. Keep
golden outcomes away from a participant whose independent discovery is being
assessed. Use raw inputs separately for fresh applications.

For the next real LFEA application, use [the pilot prompt](assets/lfea-pilot.md).
Refresh the actual AA3 sources and authority first. Prototype tests and synthetic
applications do not constitute LFEA diagnosis, repair or acceptance.
