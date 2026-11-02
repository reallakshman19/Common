# OnBoard IR methodology — inspect the oracle, not only the implementation

## Core question

"What wrong output would still pass the author's tests and still look convincing?" Derive a discriminating observation from **original intent, input bytes and authoritative domain rules**. Distinguish a software invariant from an engineering assumption requiring an expert decision. Treat a passing receipt as evidence only for the exact scope it actually executed.

### 1. Reconstruct the model independently

Trace original source record → normalization/frame → identity/graph/ownership → transformation → accepted candidate → emitted product → user-facing outcome. Record where original identity or authority can change. For each boundary name actual source field, module, function, permitted mutation, no-go shortcut, and one contradictory input. Derive expected outputs before consulting producer fixtures or proposed decisions.

For a claim about multi-member data, enumerate **source members** and their distinct IDs; comparing only a deduplicated set of kinds is insufficient. For a claim about topology, show edge incidence, not only positions or node numbers. For a claim about mass, prove component-owner identity separately from node count. For a claim about generated output, independently parse actual emitted file.

### 2. Calibrate evidence levels

| Evidence type | Can establish | Cannot establish alone |
| --- | --- | --- |
| Original source/spec | Authoritative input, expected behavior if interpretation is justified | Actual runtime behavior |
| Static implementation inspection | Presence of logic, plausible bugs | That changed code ran on exact source and emitted correct file |
| Unit/contract test | Specific assertion on fixed input and executable | Integration, source authenticity, engineering correctness |
| Public benchmark with native output | Actual output for that benchmark and version | Owner private source outcome |
| Independent negative challenge | That checker rejected seeded known defect in that scope | Correctness for untested cases |
| Authentic owner-source → final → native artifact | Behavior for exact source/config/candidate | Engineering approval without qualified authority |
| Reviewer/Oracle signoff | Actor's reported assessment at given scope | Technical evidence or release authority by itself |

Recheck whether the checker shares the producer's source derivation; two runtimes using the same wrong fixture do **not** form an independent semantic oracle.

### 3. Adversarial controls

Select one relevant false positive and one false negative where practical. Challenge the *same* checker that produced a green claim: change one source member, gap, coordinate, branch junction, native ID, accepted mass or emitted restraint; require a typed detectable failure. If negative test cannot run, say NOT_RUN and narrow claim. Crash before reaching the target condition is **not** an observed rejection of that engineered defect.

Review an outcome with three independent lenses: **coverage** (what was input), **semantics** (what is intended), and **execution** (what was emitted). Do not substitute a census for ownership, a receipt for bytes, or a generated code file for a native application acceptance.

### 4. Compare with producer candidate after Stage 1

Use exact candidate SHA. Inspect integrated entrypoint and mode/feature flags; a correct helper unused by production is not an accepted fix. Classify author claims as supported, contradicted or untested; record any new issue absent from the author plan. Check default/no-JSON route and all actual downstream transformations that may erase an intermediate result.

A proposal that only adds HOLDs is useful safety work but cannot be reported as eliminating a production ambiguity. A read-only physical-vertex plan is not node renumbering. A native serializer passing a non-ambiguous input does not establish that an ambiguous source graph reached it correctly.

### 5. Return actionable findings

Use [findings template](templates/FINDINGS_REPORT.md) and [matrix](templates/CLAIM_EVIDENCE_MATRIX.csv). Each finding: severity, **exact source line/byte witness**, independently-derived expected outcome, observed behavior, causal mechanism, a reproducible challenge, affected current candidate, reviewer confidence/unknowns, corrective action and *responsible decider*. Include an explicit **surviving wrong case** even when verdict is PASS.

Verdicts: **GO** only for bounded claims proven at authorized scope; **CONDITIONAL** with named unknowns and holds; **NO-GO** when contradictory material source/output evidence is shown. Avoid inventing a score or a global approval gate. Keep production release separate.

## Recognize common invalid shortcuts

- Identical XYZ ≠ connected vertex; repeated negative node number ≠ common native node.
- Two independent same-kind supports ≠ one source member.
- Cleaned geometry ≠ identical edge graph.
- Valid final XML ≠ native-restraint/element/mass parity.
- A main-branch test ≠ exact-head PR test.
- An author-authored "golden" ≠ independent test oracle.
- A new chat ≠ non-author reviewer; a different model ≠ independent expectation.
- Private fixture unavailable ≠ source passed; public replacement fixture ≠ authentic replay.
- GitHub issue comment POSTED ≠ delivered independent review or accepted fix.

## Output focus

Prioritize one complete **original source → claimed meaning → real candidate → native/output observation** with a falsifying wrong case over multiple superficial green checks. Then extend only where the surviving error or risk warrants it. Do not turn this guidance into mandatory new task decomposition or boilerplate review ceremonies.
