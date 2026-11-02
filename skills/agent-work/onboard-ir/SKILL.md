---
name: onboard-ir
description: Source-first cold onboarding for an independent reviewer on an existing WBS task, with baseline-before-proposal exposure, falsifiable claim evidence, Oracle-continuity bridge, templates and sanitized withheld synthetic golden.
---

# OnBoard IR

Use when an Owner/Oracle asks to bring an independent reviewer into an unfamiliar complex project **without importing the producer's conclusions as expected answers**, or to preserve the resulting source-backed review oracle across participant/Oracle handovers.

1. Identify the **existing** WBS/task, current authoritative Owner outcome, recipient, permissions, private source custody, baseline source commit and exact native return. This skill does not grant new roles, dispatch or release authorization.
2. For a genuine cold reviewer, send only original intent, baseline, original authoritative source, constraints and [Stage 1](templates/STAGE1_COLD_PROMPT.md). Reviewer reconstructs a material source→output rule and wrong case, discloses previous exposure, and returns the initial model to the existing native task before receiving candidate interpretation.
3. After the recorded Stage-1 return, disclose candidate PR/head, producer explanation and tests; use [Stage 2](templates/STAGE2_SOLUTION_PROMPT.md) to compare actual code/native output with the reviewer's original source derivation and independently challenge a surviving wrong result.
4. Return an evidence-backed bounded assessment with [findings template](templates/FINDINGS_REPORT.md); Oracle/Owner reconciles on the same task, keeping independent reviewer verdict and decision separate.
5. If handover occurs, use [Oracle continuity bridge](ORACLE_CONTINUITY_BRIDGE.md) to preserve original expectation, candidate SHA, negative controls, exposure, missing sources, current status and next actor; use [Agent OnBoard bridge](AGENT_ONBOARD_BRIDGE.md) for one-WBS recipient briefing.

**Before using the golden:** Read [README](README.md) and [protocol](PROTOCOL.md); the original test task is [OBIR-G01 raw](examples/xml229/RAW_CASE.md). The [expected golden](examples/xml229/GOLDEN_WITHHOLD_UNTIL_AFTER_STAGE2.md) is author-side reference, intentionally **not** supplied to the cold IR. Public fixture is not a real Owner-source replay.

This module complements, rather than supersedes, [Independent Reviewer](../independent-review/SKILL.md), [Initial Mentoring](../initial-mentoring/SKILL.md), [Oracle Continuity](../oracle-continuity/PROTOCOL.md) and [Task Evidence v2](../TASK_EVIDENCE_V2.md). Self-review with disclosed limits is legitimate; a separate chat alone cannot certify independence. Established participants receive changed-only deltas.
