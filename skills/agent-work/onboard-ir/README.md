# OnBoard IR — cold-start independent reviewer onboarding

**Purpose:** make a new, authorized reviewer productive without importing the producer's answer as the review oracle. Read original intent and actual evidence first; review the solution second. Preserve a falsifiable verdict and its limitations through Oracle/Agent handovers.

**This is an onboarding adapter, not a second review skill, WBS, approval queue or delivery protocol.** The governing authority remains [Independent Reviewer](../independent-review/SKILL.md), its [independence distinctions](../independent-review/references/INDEPENDENCE.md), [Initial Mentoring](../initial-mentoring/SKILL.md), [Oracle Continuity](../oracle-continuity/PROTOCOL.md), [Task Evidence v2](../TASK_EVIDENCE_V2.md) and the project's **one** actual task/WBS and native review return.

## Select the smallest suitable path

- **Cold IR, already assigned one task:** use [the IR protocol](PROTOCOL.md) and [one actual read-only assignment](templates/IR_ASSIGNMENT.md). Derive and record the baseline before receiving author interpretations. The reviewer may discover project facts directly; the Oracle must not supply a seeded expected answer.
- **Already grounded IR:** check changed source, candidate, authority, fixture custody or newly discovered wrong cases only. Do not impose another onboarding or repeat unchanged checks.
- **Same principal / prior author exposure:** run useful SELF_REVIEW and disclose it; a new chat, separate model run or fresh prompt does not manufacture independent authorship.
- **Oracle successor:** use [continuity bridge](ORACLE_CONTINUITY_BRIDGE.md) for evidence lineage and live WBS/assignment reconciliation; this OnBoard is **not** Oracle control transfer.
- **Agent recipient:** use [agent handoff bridge](AGENT_ONBOARD_BRIDGE.md) for one WBS-level source-grounded brief. A review role is not permission to edit producer code.

## Two-stage evidence flow

1. **Source-first / baseline:** [Stage 1 prompt](templates/STAGE1_COLD_PROMPT.md) → reviewer derives source rules, unknowns and contrary cases. Freeze its original baseline *as an immutable native return with source/candidate references* before revealing producer diagnosis. A local template alone does not freeze or transfer it.
2. **Candidate / comparison:** [Stage 2 prompt](templates/STAGE2_SOLUTION_PROMPT.md) → inspect actual candidate and compare with recorded Stage 1; resolve each discrepancy with source and a falsifier. Do not edit unless separately authorized.
3. **Reconciliation:** [claim matrix](templates/CLAIM_EVIDENCE_MATRIX.csv), [findings](templates/FINDINGS_REPORT.md), [checklist](CHECKLIST.md), and existing task return → Oracle/Owner distinguishes reviewer verdict, decisions, current candidate, remaining HOLDs and next actor. The reviewer must not become the acceptance authority merely through this packet.

**Cold-start reference:** [methodology](METHODOLOGY.md), [continuity bridge](ORACLE_CONTINUITY_BRIDGE.md), [agent brief bridge](AGENT_ONBOARD_BRIDGE.md). Use only relevant sections, not all templates as compulsory forms.

## Golden: OBIR-G01 (XML229 engineering graph)

Start the reviewer with [raw case only](examples/xml229/RAW_CASE.md). The author-side [golden expected distinctions](examples/xml229/GOLDEN_WITHHOLD_UNTIL_AFTER_STAGE2.md) stay withheld until the reviewer has recorded Stage 1 and independently inspected the candidate. [Worked handoff](examples/xml229/WORKED_HANDOFF.md) shows a historically grounded approach, **not** actual V6 source replay or a successful engineering CII.

The public case is synthetic and sanitized. The original 21 production ambiguity claims are **NOT_EVIDENCED / NOT_RUN** without their exact original XML, JSON Trace, configuration, Final and private diagnostic under authorized custody. No "Golden PASS" certifies the real model.

## Why this module exists

An agent can pass author-written unit tests while being wrong about engineering identity. An Oracle can preserve a green status but lose the test's original oracle, its source revision or the exact failure it was supposed to catch. OnBoard IR couples source-first reviewer orientation with **oracle continuity**: every reused conclusion must preserve *what was expected, why, against which bytes, by which distinct participant/method, with which surviving wrong case and whose authority accepted it*.

**Not a general obligation:** the two-stage cold start is useful when prior producer diagnosis threatens expectation independence. Existing independent-review practice remains sufficient elsewhere. If real sources cannot be accessed, state the gap and continue authorized read-only work without asserting technical PASS.

See [Common agent-work role router](../START_HERE.md) and [reference index](../REFERENCE_INDEX.md).
