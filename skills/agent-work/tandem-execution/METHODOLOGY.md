# Tandem methodology — derive, implement, compare, converge

**Mode routing:** the B-convergence methodology below applies to PARALLEL/SERIAL. For TANDEM_IR use [the dedicated route](TANDEM_IR.md), which composes [OnBoard IR](../onboard-ir/SKILL.md), [Independent Review](../independent-review/SKILL.md) and [Contribution & Handoff](../CONTRIBUTION_HANDOFF.md); reuse the source-grounding and evidence calibration principles below, with A performing final semantic reconciliation.

Core question: **What materially wrong result can survive either implementation, and how can the two agents produce one stronger working result without waiting or handing defects backward?**

## 1. Establish original behavior, not a preferred patch

Both derive the actual source → normalization/identity → transformation → consumer → observable outcome. Identify the exact original input and source authority. Before executing a control, write the expected output and a plausible wrong alternative. Locate the earliest failing boundary. Preserve true positives while rejecting false positives; e.g. merge repeated observations of one event but retain different sessions, or suppress a suggestion while preserving explicitly saved records. Follow real upstream/downstream dependencies rather than inventing a depth quota.

Existing discovery may be reused. Independent investigation is useful, not an extra mandatory cold stage. Do not repeat unchanged source work or withhold essential requirements. Share original evidence via Drive; avoid seeding the other agent with an unproved diagnosis as an authoritative requirement.

## 2. A and B implement in parallel

Each fixes its primary area against its actual baseline/checkpoint, adds executable regression controls, runs native functions/entrypoints, corrects regressions and publishes a runnable delta. B can start by fixing the most consequential defect even if A is still investigating. Use isolated copies or worktrees; same filename in different trees is safe. Prefer minimal coherent changes to unused scaffolding. A need not intentionally leave a defect; B need not manufacture extra edits. If a primary repair exposes a related first divergence, fix it within the assignment or record the actual external dependency.

Keep a compact claim/finding matrix in each native package: original ID, actual input, expected, observed before/after, source boundary, changed paths, tests, candidate identity, limitations. Reconcile naming differences without a reporting round. A test that crashes before reaching the target wrong condition is not a successful falsifier.

## 3. B's semantic three-way convergence

| Stage | Question | Actual operation |
| --- | --- | --- |
| Identify | What bytes and base did each agent change? | Verify native archive, base SHA/digest, diffs, dependency/config changes |
| Compare | Same symptom or same failing contract? | Map A/B by boundary and intended output; detect duplicate and complementary fixes |
| Select | Which behavior satisfies original intent? | Test both where contested; select, adapt, combine or replace using evidence |
| Integrate | Can the chosen repairs coexist? | Apply/rebase in B-owned integration tree; resolve text and semantic conflicts |
| Challenge | What wrong output would pass both original tests? | Run a combined adverse case, positive controls and actual consuming entrypoint |
| Correct | Did any defect survive or appear? | B fixes it directly, retests changed dependencies |
| Deliver | Which actual contributions and limitations remain? | Publish final bytes, per-claim results, lineage and disposition |

Do not assume a diff without overlapping lines is compatible. Example: one agent changes an identity producer, another relies on the old identity in a saved-record consumer; the textual merge succeeds but user data can disappear. Use a cross-boundary control. For overlapping edits, compare original behavior and both proposed variants rather than selecting by author, test count, freshness or preference. Keep valid changes/tests even when rejecting a redundant patch. A missing A artifact limits comparison to B's actual candidate, not the ability to complete the outcome.

## 4. Calibrate evidence

| Evidence | Can establish | Cannot alone establish |
| --- | --- | --- |
| Original input/spec | Expected contract if justified | Actual behavior |
| Source inspection | Reachability/mechanism | Executed integrated behavior |
| Native focused control | Observed case on exact candidate | Universal correctness |
| Negative control reaching wrong condition | Detection of that failure | Unrelated correctness |
| Historical replay at recorded clock | Behavior for snapshot/input | Current live coverage |
| Native integrated/browser output | Actual routed result under given config | Release permission |
| Verified Drive bytes | Artifact identity/transfer | Execution, correctness or peer availability |

Use SUPPORTED, CONTRADICTED, NOT_RUN, UNKNOWN at claim level. Preserve original and current source, input hashes, expected/actual output, runtime flags, commands/exit status, protected behavior. Do not carry green status across a changed semantic boundary without requalification. Distinguish self-authored tests/changes from the other agent's evidence. B's combined tests are valuable but are not automatic independent approval.

## 5. Convergence without ceremony

No extra report review before fixing. No return to A for corrections. B's local loop is reproduce → repair → rerun until the bounded outcome is done or actual limit. Use the defined boundary and final Drive refresh. If A is absent, B can finish from B1 and return a complete B-only implementation. If A's late packet comes after final delivery, preserve without mandatory reopening. Distinguish technical completeness from peer participation. Do not hold a correct product hostage to a missing marker, or claim a combined result without actual A contribution.

The [parallel golden](examples/parallel/WORKED_HANDOFF.md) demonstrates independent native A1 and B1, same-file integration and absence fallback. The [serial golden](examples/golden/WORKED_HANDOFF.md) remains an explicitly chosen alternative.
