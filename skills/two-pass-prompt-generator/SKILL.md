# Two-Pass Prompt Generator

This standalone skill generates exactly two copy-pasteable prompts for a capable engineering agent.

Canonical surfaces:

```text
skills/two-pass-prompt-generator/SKILL.md
skills/two-pass-prompt-generator/schema.md
skills/two-pass-prompt-generator/validate.py
```

## Entry rule

Before target reasoning:

1. fetch `skills/two-pass-prompt-generator/schema.md` from current `main`;
2. establish its live protocol revision and content SHA;
3. emit the schema execution handshake first;
4. only then inspect the supplied target/context;
5. generate exactly the two prompts defined by the schema;
6. validate the generated artifact with `validate.py` when executable validation is available;
7. return the two-prompt artifact and stop.

## Core separation

Pass 1 is an **independent system-understanding prompt**. It may inspect the live repository/application, but must not receive or reveal the actual task/issue, current PR, proposed fix, requested improvement, or further action. It ends at current-state understanding.

Pass 2 receives the Pass-1 result plus the actual task/issue and current live evidence. It must:

- reconstruct relevant provenance in order: Original Intent → current Owner/Roadmap authority → EP responsibility/current plan → primary-agent reasoning → latest AGENT_STATUS_V1/Further task → Local Agent/OFFLOAD evidence → RLL transport → material truth/TASK_EVIDENCE/TASK_RESULT → Task Snapshot/Handover;
- emit an explicit STEP-BACK RECONCILIATION before proposing changes;
- keep historical intent, current authority, agent reasoning, mutable execution continuity, delegated evidence, transport state and material truth semantically distinct; revalidate unresolved FT-* items against live material truth before carrying them forward;
- identify zero or more legitimate high-ROI improvements only after reconciliation;
- quantify each proposal from evidence instead of inventing numbers;
- reject rewrite/novelty pressure;
- reconcile the actual task against the independently understood system;
- show the Owner the Improvement Proposal(s) and a draft implementation plan in chat;
- stop for explicit Owner approval before durable plan publication, EP creation/binding, or material implementation;
- after approval, refresh volatile reality, publish the approved `IMPLEMENTATION_PLAN` on the original issue including approved Improvement Proposal(s), bind/create EPs by responsibility, refresh Task Snapshot/Handover, and proceed only within the approved/authorized boundary.

The four V3.1 durable engineering publications remain:

```text
IMPLEMENTATION_PLAN
PLAN_UPDATE
TASK_EVIDENCE
TASK_RESULT
```

`IMPROVEMENT PROPOSAL` is not a fifth publication type. Approved proposals are embedded in the implementation plan or routed to a separate responsibility when genuinely adjacent.

## Fail closed

If the live schema cannot be fetched, do not reconstruct it from memory. Emit only the handshake failure required by the schema.
