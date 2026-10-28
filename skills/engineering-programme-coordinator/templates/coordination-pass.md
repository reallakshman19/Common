# Coordination pass

Use this prompt for ChatGPT Work or another programme coordinator to re-observe a live multi-agent programme.

This is a reasoning/reporting pass. It does not authorize or deny production.

```text
COORDINATION PASS

Read current durable programme + production reality first:

- linked Original Intent source when present;
- governing parent Programme Specification;
- current effective amendment index and referenced Owner/programme amendments;
- active child / EP responsibility contracts;
- relevant primary-agent conversation/reconciliation refs;
- latest AGENT_STATUS_V1 / unresolved Further task for active custody, when present;
- relevant Local Agent / OFFLOAD provider issues;
- relevant RLL execution/state refs as transport context only;
- dedicated [Relay Handover] operational ledger;
- each agent's latest durable implementation plan;
- every nonterminal PR and its exact head/lifecycle;
- current branch/commit/test/runtime/artifact evidence;
- recent durable producer→consumer handoffs;
- negative knowledge / do-not-reopen findings;
- local engineering coordinator snapshot/returns when available;
- relevant canonical source truth;
- parent EXIT criteria;
- source freshness.

Treat the Handover issue as an index. Verify material claims against linked durable evidence where a consequence depends on them.

Before workstream recommendations, revalidate any unresolved FT-* continuity items against live provider/material truth, then perform a compact STEP-BACK RECONCILIATION across historical Original Intent, current Owner/Roadmap authority, current responsibility, agent/delegated reasoning, mutable execution continuity and live material truth. Distinguish PRESERVED / SATISFIED / MISSING / DRIFTED / SUPERSEDED_BY_OWNER / ROADMAP_CHANGED / EP_ASSUMPTION_ONLY / LOCAL_AGENT_FINDING / RLL_TRANSPORT_ONLY / REALITY_CORRECTION / UNRESOLVED only where material.

Relay protocol rule: **V3.1 only**. Do not consult or use V3 or V2.5 for live coordination, status, gating, recovery, or Owner-command semantics.

Do not treat chat activity, timers, V3.1 recorder state, leases, checkpoints or coordinator metadata as production permission.

For each workstream, reconstruct:

1. ISSUE RESPONSIBILITY
   What does this issue actually own?

2. PLAN
   Is a durable implementation plan PRESENT, MISSING, STALE or UNKNOWN?
   Missing/stale reduces confidence only.

3. EXPECTED
   What concrete production/evidence event was expected next?

4. OBSERVED
   What is actually true now?
   Cite durable evidence.

5. COMPLETION AXES
   Reconstruct independently:
   - plan progress;
   - child/work-issue acceptance;
   - current task/EP acceptance;
   - verification state + failure origin;
   - delivery/PR lifecycle;
   - programme contribution;
   - provider issue lifecycle.

   Use explicit EXIT-*/AC-*/STEP-* denominators where present.
   If no denominator exists, report UNKNOWN / UNMAPPED.
   Do not infer completion from PR count, commit count or test count.

6. PLAN CONFORMANCE
   Classify:
   ALIGNED
   MINOR_DEVIATION
   MATERIAL_DEVIATION
   PLAN_STALE
   PLAN_CONTRADICTED
   INSUFFICIENT_EVIDENCE

   Judge unreconciled semantic deviation, not harmless implementation churn.

7. DEPENDENCIES
   For each real dependency state the required production output.
   Classify:
   SATISFIED
   MISSING
   UNCERTAIN
   DISCOVERED
   SUPERSEDED

   Also state what work may continue independently.

8. HELPER NEED
   Would a bounded local/browser/runtime helper materially reduce uncertainty or protect production?
   Recommend only when useful.

9. EVIDENCE SCOPE
   Which evidence is LOCAL_ONLY?
   Which is SHARED_DURABLE?
   Does anything need promotion because another workstream now depends on it?

10. UNCERTAINTY
   Distinguish:
   OPEN_QUESTION
   RISK
   FALSIFIER_IN_FLIGHT
   UNKNOWN

11. CONSEQUENCE
    What, if anything, follows for another agent, this plan, the Owner or next observation?

12. SUGGESTED ACTION
    Only if useful.
    State target, reason, action, affected workstreams, evidence and whether Owner judgement is required.

Then reconcile cross-workstream reality:

- newly discovered dependencies;
- newly satisfied dependencies;
- work that can now run or run partially;
- conflicting assumptions;
- overlapping ownership / shared integration surfaces;
- producer results that should be routed immediately to consumers;
- stale dependency watches that can be retired;
- local evidence that now needs promotion;
- negative-knowledge entries that should prevent repeated dead ends;
- nonterminal PRs missing from the operational ledger;
- parent EXIT criteria advanced / unchanged / regressed;
- any semantic-boundary change.

Ask whether a genuine semantic boundary changed:

- product goal/meaning;
- governing issue meaning;
- ownership;
- shared architecture/interface contract;
- fundamental capability assumption.

If NO:
keep prior direction and make the smallest coordinator move.

If YES:
identify exactly what changed and whether fresh Two-Pass reasoning is warranted.

OPERATIONAL LEDGER

Propose the minimal [Relay Handover] updates needed for zero-context reconstruction:
- Original Intent / latest reconciliation refs;
- workstream / EP / primary-conversation refs;
- current AGENT_STATUS_V1 ref/custody epoch and unresolved FT-* IDs;
- Local Agent / OFFLOAD and RLL refs when relevant;
- workstream/material refs;
- dependency state;
- nonterminal PR carry-forward;
- producer→consumer handoff;
- negative knowledge;
- Owner decision need;
- next coordinator action / observation.

Do not rewrite the ledger merely because time passed.

OWNER

Report only genuine decisions or material risks that belong to the Owner.

NEXT OBSERVATION

State why another observation would be useful and what evidence would make it informative.
Do not create a timer merely to have one.

OUTPUT

Produce a coordination observation matching
engineering-coordinator-observation-v1.

Populate when available:

- programme_context: parent ref, current basis revision, Handover ref, effective amendment refs;
- nonterminal_prs: every draft/open/changes-requested/conflicted/reviewable PR still in play;
- negative_knowledge: programme-significant do-not-reopen findings + reopen condition;
- exit_criteria: each relevant parent EXIT-* criterion with exact evidence and OPEN/PARTIAL/SATISFIED/DEFERRED/NOT_APPLICABLE state.

The central calculation is:

EXPECTED
→ OBSERVED
→ CONSEQUENCE

If nothing meaningful changed:
say so.
Do not manufacture an intervention.
```
