# Two-Pass Prompt Generator Schema

CANONICAL LAUNCHER:
`skills/two-pass-prompt-generator/SKILL.md`

CANONICAL SCHEMA:
`skills/two-pass-prompt-generator/schema.md`

# SCHEMA EXECUTION HANDSHAKE

A generated artifact must begin with:

```text
# SCHEMA EXECUTION HANDSHAKE

PROTOCOL REVISION:
TPG-2P-2026-09-28-R3

GENERATOR MODE:
TWO_PASS_ONLY

SCHEMA FETCH STATUS:
LIVE_THIS_RUN

SCHEMA CONTENT SHA:
<actual current blob/content SHA>

HANDSHAKE STATUS:
PASS
```

If the live schema cannot be fetched or its SHA cannot be established, emit only:

```text
# SCHEMA EXECUTION HANDSHAKE
HANDSHAKE STATUS:
FAIL
```

and stop.

## Purpose

Generate exactly two prompts.

### PASS 1 — INDEPENDENT SYSTEM BASELINE

The future agent is told the repository/application/system and broad human outcome, but **not** the actual issue/task, current PR, requested fix, Improvement Proposal, desired implementation, or next action.

Pass 1 must sound like one experienced human asking another to understand the system. It must tell the agent to inspect live repository/application reality and independently establish:

- what the user experiences today;
- where authoritative truth/state comes from;
- how the important path flows from input/evidence to result/consumer;
- one representative real witness worked end-to-end;
- one load-bearing variation and the invariant/falsifier it exposes;
- one genuinely independent verification route;
- known facts versus uncertainty/contradiction;
- the exact live material/runtime basis inspected.

Pass 1 must end at understanding. It must not recommend an improvement, select a next task, draft an implementation plan, or infer the hidden issue.

Required Pass-1 output concept:

```text
INDEPENDENT_SYSTEM_BASELINE

SYSTEM / USER OUTCOME
CURRENT BEHAVIOUR
REAL PATH / AUTHORITY FLOW
CONCRETE WITNESS
INVARIANTS / FAILURE BEHAVIOUR
INDEPENDENT VERIFICATION
CURRENT MATERIAL BASIS
KNOWN
UNCERTAIN
```

No "what we should do next" section.

### PASS 2 — IMPROVE, RECONCILE, PLAN

Pass 2 receives:

- the actual Pass-1 baseline;
- the actual next issue/task;
- current repository/application/provider evidence;
- programme/Owner constraints and approved authority;
- the linked Original Intent source when one exists;
- current Roadmap/programme basis and explicit Owner amendments;
- the current EP/owned responsibility;
- relevant primary-agent conversation/reconciliation refs;
- latest AGENT_STATUS_V1 / Further task continuity when one exists;
- relevant Local Agent/OFFLOAD provider refs;
- relevant RLL execution/state refs;
- current Task Snapshot and [Relay Handover] refs.

The future agent must first refresh live reality, then reconstruct **authority and provenance in order** rather than treating all historical text as equally authoritative:

```text
Original Intent historical source
→ current Owner/Roadmap authority + amendments
→ current EP / owned issue responsibility
→ relevant primary-agent reasoning
→ latest AGENT_STATUS_V1 / Further task
→ Local Agent / OFFLOAD evidence
→ RLL transport state/results
→ current PR/test/runtime material truth
→ current Task Snapshot / Handover index
```

Historical Original Intent explains what the Owner originally meant; later explicit Owner amendments may supersede current meaning. Agent reasoning is not Owner authority. AGENT_STATUS_V1 is derived execution continuity only: it tells the successor where the predecessor believed execution stood, but every unresolved FT-* item must be revalidated against live provider/material truth before continuation. Local Agent evidence is scoped to its offload. RLL is transport and never proves engineering acceptance by itself.

#### A. Step-back reconciliation

Before proposing improvements, emit:

```text
STEP-BACK RECONCILIATION

PRESERVED
Original intent/current requirement still represented correctly.

SATISFIED
Original/current expectation already proved by live evidence.

MISSING
Owner intent/input/expected output is absent from the current issue/plan.

DRIFTED
Current issue/plan has moved away from the still-effective Owner intent.

SUPERSEDED_BY_OWNER
A later explicit Owner decision intentionally replaced the earlier meaning.

ROADMAP_CHANGED
Current Roadmap/programme authority changed the execution/consumer consequence.

EP_ASSUMPTION_ONLY
A prior engineering-agent assumption exists but was never Owner/programme authority.

LOCAL_AGENT_FINDING
A delegated/helper result changes or constrains current reasoning.

RLL_TRANSPORT_ONLY
Observed RLL state is operational transport context, not acceptance evidence.

REALITY_CORRECTION
Live repository/app/material truth contradicts an earlier Owner/agent assumption.

UNRESOLVED
Evidence or human judgement is still genuinely missing.

CONSEQUENCE
NONE | ISSUE_CLARIFICATION | IMPROVEMENT_PROPOSAL |
PLAN_CHANGE | ROADMAP_PROPOSAL | SEPARATE_RESPONSIBILITY |
OWNER_DECISION_REQUIRED
```

Include only classifications that materially apply. Cite refs/evidence; do not copy full conversation transcripts into the reconciliation.

#### B. High-ROI improvement scan

Find **zero or more** legitimate improvements. Prefer no proposal to a speculative proposal.

Reject:

- rewrites merely because a cleaner architecture is imaginable;
- cosmetic cleanup presented as strategic improvement;
- scope expansion;
- novelty quotas;
- telemetry such as PR/file/commit counts used as capability evidence.

Every proposal must use:

```text
IMPROVEMENT PROPOSAL — IP-XX

OBSERVED GAP
LIVE EVIDENCE
WHY IT MATTERS
CURRENT → PROPOSED

QUANTITATIVE EFFECT
Use actual before/after measures where available.
If a quantity cannot be established, write UNKNOWN.
Never invent precision.

ESTIMATED CHANGE SIZE
files / approximate LOC / test surfaces / interfaces, where evidence permits.

IMPACT
1–5

EVIDENCE STRENGTH
1–5

REUSE / CROSS-TASK VALUE
1–5

EFFORT
1–5, where 1 is very small

CHANGE RISK
1–5

CONFIDENCE
0–100%

RELATIVE ROI
(impact × evidence_strength × reuse × confidence_fraction)
/
(effort × change_risk)

FALSIFIER
What would show the proposal is unnecessary or wrong.

SCOPE RELATION
IN_SCOPE | ADJACENT | UNRELATED | FALSIFIED
```

The score is a relative heuristic; concrete before/after quantities are more important.

#### C. Reconcile the actual task

Determine from live evidence:

- what the issue actually owns;
- whether its assumptions are still true;
- whether its responsibility should be PRESERVE, AMEND, SPLIT, SUPERSEDE, or is already SATISFIED;
- which proposals are actually in scope;
- which approved adjacent proposals require a separate child responsibility/EP rather than contaminating the issue.

#### D. Draft plan in chat

Before any durable issue mutation, EP creation/binding, branch/PR creation, or material implementation, show:

```text
DRAFT IMPLEMENTATION_PLAN — NOT YET PUBLISHED

BASIS
MY UNDERSTANDING
ISSUE DISPOSITION
IMPROVEMENT PROPOSALS
OWNED OUTCOME
APPROACH
PLAN SLICES (stable STEP-* IDs)
EXPECTED CHANGED SURFACES
DEPENDENCIES
INDEPENDENT WORK
FALSIFIER
VALIDATION
PRESERVE
UNCERTAINTIES
EXPECTED NEXT OBSERVABLE
CONSUMER / HANDOFF
```

Then finish the first Pass-2 response with:

```text
APPROVAL REQUIRED

No durable plan publication, EP creation/binding, or material implementation has been performed from this proposal response.
```

#### E. After explicit Owner approval — same Pass 2

This is a continuation of Pass 2, not a third pass.

1. Refresh live issue/repository/PR/runtime state.
2. If a material change invalidates the approved plan, show the approval delta and stop for renewed approval.
3. Otherwise publish `IMPLEMENTATION_PLAN — rev 1` (or the appropriate revision) on the **original owned issue**.
4. Include only approved Improvement Proposal(s) in the plan, with their quantitative basis, scope relation, falsifier, and expected benefit.
5. Reuse the existing EP for the same bounded responsibility; create a new EP only for a genuinely new responsibility.
6. If an approved proposal is ADJACENT, create/use a separate child responsibility and EP rather than silently widening the original issue.
7. Refresh the issue-local Task Snapshot and programme Handover index so the coordinator can consume:
   issue → plan → expected observable → PR/head/result → consumer consequence.
8. Execute only if the Owner's approval/authorized actions include execution. V3.1/Relay metadata is never production permission.
9. During execution keep the four durable publication types: `IMPLEMENTATION_PLAN`, `PLAN_UPDATE`, `TASK_EVIDENCE`, `TASK_RESULT`.

## Required generated artifact shape

After the handshake and a short schema basis, emit only:

```text
## PASS 1 — INDEPENDENT SYSTEM BASELINE

<one complete copy-pasteable prompt>

## PASS 2 — IMPROVE, RECONCILE, PLAN

<one complete copy-pasteable prompt>
```

Do not emit a third prompt, Prompt 0.5/1/2/2.5/3, a qualification questionnaire, or extra admission/certification stage.

## Pass-1 visibility rule

Pass 1 may include the repository/application/system identity and broad human outcome.

Pass 1 must not contain:

- issue or pull-request URLs/numbers;
- current branch/PR status;
- issue acceptance criteria;
- the hidden task title;
- Original Intent issue/content;
- prior primary-agent conversation/reconciliation;
- AGENT_STATUS_V1 / Further task continuity;
- Local Agent/OFFLOAD or RLL task history;
- "Improvement Proposal";
- implementation-plan instructions;
- proposed next action;
- requested change.

The generator may know these internally; it must quarantine them until Pass 2.

## Pass-2 evidence rule

Pass 2 must tell the future agent to distrust stale prose when live provider/material evidence is available. Historical handoff explains what to inspect next; live reality determines what is true now.

Pass 2 must distinguish provenance from authority:
- Original Intent = historical Owner source;
- later explicit Owner/Roadmap amendments = current semantic authority when applicable;
- primary/local-agent reasoning = non-authoritative reasoning/evidence unless adopted by Owner/programme authority;
- AGENT_STATUS_V1 = mutable derived execution continuity; stale status never outranks Git/material truth;
- unresolved FT-* = predecessor continuity hints that a successor must revalidate before continuing;
- RLL = transport state;
- PR/tests/runtime/artifacts = material truth;
- Task Snapshot/Handover = derived/indexing views.

## Approval rule

Human approval governs the transition from proposal to durable engineering intent.

Relay/coordinator approval is not required after Owner approval. After the plan is durably published and bound to the responsibility, execution may continue within actual production authority and the approved action boundary.
