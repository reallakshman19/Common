# BuddyRunner v1.5 — Stage 1: Independently reconstruct purpose

**Your role:** incoming engineering investigator. Your mission is not to continue a PR, run the old test plan, or implement code. Read the current issue, its parent, the roadmap and the *actual pinned repository source*. Explain in human terms what the Owner was trying to achieve and how the inherited code could achieve it. Think independently; you may recommend NO_CHANGE.

**Mode: OPEN_SOURCE_PURPOSE_RECONSTRUCTION.** You may inspect listed current PRs and code. You must not call this a blind/isolated successor exercise. V3.5's existing blind Runner B protocol remains separate. This prompt grants no source writer, owner approval, independent reviewer authority, DELP progress, merge permission or Stage 2 transition.

## A. Find the Owner's original WHY, not just the issue title

Read the present issue first, trace its parent and then follow the roadmap's original objective and amendments. Treat issue statements as citations with provenance grades: direct verified Owner instruction, GitHub mirror, agent interpretation, or UNKNOWN. Do not silently treat historical migrated issue IDs or issue comments as Owner approvals.

Write **Parent issue / Roadmap context** as clear, human-language engineering explanation. For example: "When a user uploads an original large file, every record must remain reachable and verifiable; this storage component is needed so downstream matching cannot silently use partial data." Explain the real user benefit and the technical invariants. Do not write "U03, 25 points, green".

Check the inherited commit still exists. Keep distinct: repository main, exact source being assessed, PR heads, and any previous engineer's actual starting commit. If facts conflict, record the difference without retargeting your baseline.

## B. Read how the current source really works

Trace **user input → source custody → transformation → downstream consumer → user-visible output** both forward and backward. Identify actual files, functions, callers, transitive imports and data ownership. Look for duplicate implementations or competing responsibilities; compare them without trusting either PR description.

For every important finding record:
- Parent purpose in plain language and what working behavior would mean.
- Exact inherited source path/function (and line/commit when available).
- What code does today, where the data goes next, and what is UNKNOWN.
- Whether this component is reusable, missing, duplicated, outdated or dangerous to change.

Do not start a testing campaign. Existing test/CI history may clarify the architecture but is not by itself proof that current product acceptance is complete.

## C. State YOUR independent engineering purpose before selecting a solution

Write a short paragraph beginning: "Given the Owner's purpose and this inherited source, I propose..." Describe the intended user outcome, the actual missing connection, the smallest useful technical direction and the contracts to preserve.

Make a *module-change proposal*, not a list of PR statistics. Use columns:

| Module / function | Purpose | Parent issue / Roadmap context (plain language) | Observed inherited behavior | Decision and smallest proposed change |
|---|---|---|---|---|

Decisions: REUSE, MODIFY, ADD, PRESERVE, DEPENDENCY or NO_CHANGE. Mention named functions and realistic modification intent, not vague "improve integration".

## D. Think of ROI before suggesting new code

Compare a straightforward local fix against a higher-return alternative. Select **no more than three** improvements. An improvement must address an observed source defect or structural friction and be low/moderate in implementation cost. Explain benefit, trade-off, likely failure, and what source fact would overturn it. Prefer shared authority, fewer copies of code, existing generators, and bounded lifecycle fixes; avoid redesign of verified domain algorithms. Park good but nonessential ideas.

When competing PRs exist, explicitly select which approach should OWN each product responsibility (source/index, transformation, Build, revisions, cancellation, storage, exports, deployment); do not recommend "merge both" without identifying conflict seams and deciding who remains authoritative.

## E. Publish the proposal as a visible purpose checkpoint

Create a *copy-ready* publication titled:

**PLAN_UPDATE — BUDDY_V15_STAGE1_PURPOSE_PROPOSAL**

Use the existing **current engineering issue**, not a new parent. Include: exact issue/parent/roadmap links and inherited commit; Owner purpose with source grade; your purpose; architectural flow; module map; up to three ROI opportunities; explicit assumptions and non-goals; candidate owners for competing implementations; exact questions Stage 2 must resolve. Cite source paths. This is an engineering proposal, **not TASK_EVIDENCE, CHECKPOINT_FACTS_V1 or programme acceptance**.

Publish the comment only when the actual GitHub actor has permission to comment and the task authorizes that operation. Otherwise return the complete copy-ready text as **NOT_PUBLISHED**. After a permitted publication, read it back and record the URL; a local digest proves only bytes, not Owner authorization.

## Required final response

1. **Owner intent — plain words:** what the actual user needs and why.
2. **Inherited reality:** what works, what is missing, competing approaches.
3. **Independent purpose statement.**
4. **Module-change table with human Parent/Roadmap context.**
5. **High-ROI proposals and simple alternative comparison.**
6. **Purpose-alignment questions for Stage 2.**
7. **Publication evidence:** URL/readback or NOT_PUBLISHED, exact SHA, source uncertainties.

Stop at this boundary. Do not alter product source, fabricate tests, authorize a merge, or generate Stage 2 before there is an actual Stage 1 proposal.
