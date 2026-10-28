# Work Order

Send a substantial outcome-oriented assignment. Do not nano-manage implementation.

**Relay protocol rule:** use Engineering Relay **V3.1 only** if Relay context is relevant. Do not consult or use V3 or V2.5 for live status, coordination, gating, recovery, handover, or Owner-command semantics.

```text
WORK_ORDER

WORKSTREAM
<alias / child issue>

PROGRAMME BASIS
<parent issue + current effective basis revision>

RELEVANT AMENDMENTS
- <only amendments that materially affect this workstream>

OUTCOME
<what must become true in production>

PRODUCTION BOUNDARY

OWNS
- ...

EXCLUDES
- ...

CURRENT DURABLE INPUTS
- <issue / commit / PR / artifact / canonical source>
- include observed head/digest/time only when it materially improves reconstruction

RELEVANT NEGATIVE KNOWLEDGE
- <rejected/disproved approach + evidence + reopen condition, only if relevant>

CURRENT MATERIAL
- branch / PR / exact head when material already exists

DEPENDENCY CONTRACTS

1. REQUIRED OUTPUT
   <actual missing production truth>

   PRODUCER
   <if known>

   WHY REQUIRED
   ...

   SATISFACTION EVIDENCE
   - ...

   WORK THAT MAY CONTINUE INDEPENDENTLY
   - ...

FALSIFIER
- <what would show the intended work is unnecessary/wrong/differently framed>

SUCCESS ORACLE
- <observable evidence that proves the owned outcome works>

EXPECTED NEXT OBSERVABLE
<the next useful production/evidence event, not a heartbeat>

Examples:
- implementation plan persisted;
- falsifier result;
- durable commit/PR;
- exact runtime evidence;
- producer handoff;
- dependency discovery;
- verified negative result.

CONSUMERS
- <who needs the result and what they consume>
- <what the consumer must not infer from this output>

SEMANTIC ESCALATION
Return early only if evidence materially changes:
- product meaning;
- shared architecture/interface ownership;
- this issue's responsibility;
- another workstream's durable assumptions;
- a genuine Owner decision.

OWNER DECISIONS ALREADY MADE
- ...

LIVE V3.1 BASIS
At session start/resume and before plan/result/readiness/merge/handover semantic boundaries, resolve current `reallaksh19/Common@main`. Record the exact SHA and current Two-Pass revision. If the SHA changed, reload the live V3.1/Two-Pass contract and revalidate the pending action only.

TWO-PASS / STEP-BACK RECONCILIATION
Pass 1 remains independent from the issue/history.

At Pass 2 / takeover, read relevant durable context in this order:

```text
1. Original Intent source
2. current Owner/Roadmap basis + explicit amendments
3. current EP / owned issue responsibility + current plan
4. relevant primary-agent conversation/reconciliation
5. latest AGENT_STATUS_V1 / Further task, when present
6. Local Agent / OFFLOAD provider issue(s), when relevant
7. RLL execution/state/results, when relevant
8. current PR/tests/runtime/material truth + latest TASK_EVIDENCE/TASK_RESULT
9. current Task Snapshot / Relay Handover
```

Do not treat these as equal authority. Original Intent is historical Owner source; current Owner/Roadmap amendments govern current semantics; agent reasoning is non-authoritative unless adopted; AGENT_STATUS_V1 is mutable derived continuity and unresolved FT-* must be revalidated; Local Agent evidence is bounded; RLL is transport; material evidence proves current engineering reality.

Emit `STEP-BACK RECONCILIATION` before Improvement Proposal(s), using materially applicable classes such as PRESERVED, SATISFIED, MISSING, DRIFTED, SUPERSEDED_BY_OWNER, ROADMAP_CHANGED, EP_ASSUMPTION_ONLY, LOCAL_AGENT_FINDING, RLL_TRANSPORT_ONLY, REALITY_CORRECTION and UNRESOLVED.

TWO-PASS / FIRST DURABLE AGENT PUBLICATION
When the two-pass flow is used, first show the Owner the evidence-backed Improvement Proposal(s) and DRAFT IMPLEMENTATION_PLAN in chat. Do not publish the durable plan, create/bind EPs, or materially implement from that proposal response.

After explicit Owner approval, refresh live reality. If the approval basis materially changed, show the delta and stop for renewed approval. Otherwise publish `IMPLEMENTATION_PLAN — rev 1` on the owned child issue before substantial modification when practical.

The publication must begin with that typed heading. Include a `PROTOCOL BASIS` block naming V3.1, the exact resolved current-main Common SHA, and current Two-Pass revision. In `BASIS`, record the child responsibility/provider ref and its observed body/contract digest when available, plus the exact live material basis. Include only approved Improvement Proposal(s), with quantitative basis, scope relation, falsifier and expected benefit.

The plan is agent-authored and revisable. Do not wait for coordinator/Relay approval after Owner approval and publication. If useful work already began before the plan could be posted, publish the current approved plan as soon as practical and continue within the approved action boundary.

During execution publish only meaningful semantic deltas:
- `PLAN_UPDATE — rev N` when evidence materially changes the approach, including a correction/narrowing that changes what material the agent now intends to produce;
- `TASK_EVIDENCE` when an intermediate result changes reconstruction or another workstream's next action;
- `TASK_RESULT` at the delivery/handoff boundary, including final exact-main acceptance when that is the owned outcome.

Use the typed heading as the first durable heading. Two-Pass reasoning, Improvement Proposal chat, or semantically equivalent correction/final report is still evidence, but should not replace the corresponding typed publication.

Do not post every command, file read, test retry, timer wake or chat update.

EP NOTE
An EP is V3.1's recorder identity for the bounded responsibility. Do not create a new EP merely because the plan was published or revised.

EXECUTION STYLE
Design the detailed implementation yourself.
Use falsifiers and validation appropriate to the issue.
Do not wait on coordination/reporting metadata.
If a dependency is missing, continue any explicitly independent work.
Return durable evidence and cross-workstream consequences.
```
