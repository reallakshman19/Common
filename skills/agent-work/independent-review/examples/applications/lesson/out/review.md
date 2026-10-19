# Local review of the constant-acceleration lesson

Review `/workspace/scratch/52eed2252c51/tmp/ir-forward/lesson/inputs/lesson.md` against its stated purpose: a short worked task for a learner who knows signed velocity to distinguish motion direction from change in velocity. Use the available single reviewer and local tools. Show evidence, limitations and the next useful action.

**Verdict: PASS for the stated source-level purpose.** The worked example is mathematically correct under its stated one-dimensional, constant-acceleration assumptions. Its reversal example and zero-acceleration comparison support the intended distinction. No material correctness or scope defect was found. This is a judgment about the supplied page, not a measured learning outcome or Owner acceptance.

## Subject and scope

- Candidate: `../inputs/lesson.md`, all 20 lines, read directly with line numbers on 2026-10-19.
- Candidate SHA-256, recomputed from its bytes: `8e9748eca50afce7c28013528c17fc79ad706a0fa1ea76f29cf817ebeecbf6ac`.
- Purpose and learner prerequisite: lines 3–5. Review boundary: lines 18–20.
- Reviewed: numerical claims, sign convention, units, reversal, displacement versus distance, the zero-acceleration limiting case, and alignment with the short worked-task aim.
- No project-specific review profile or optional module was supplied or required. The Common `AGENTS.md` overlay was read while locating the skill; its engineering change policy does not turn this separate local lesson review into a Common engineering change.
- The input was not edited. No publication or external action was performed.

## Evidence and reasoning

The givens are treated as the authoritative model assumptions, not as experimental facts about a real cart. Expected results were derived from the definition of constant acceleration, `dv/dt = a`, and displacement as signed velocity-time area. Distance requires the area of `|v|`, splitting the interval wherever velocity changes sign. These definitions provide the criterion for checking the page; the page's displayed answers were not treated as an oracle.

| Source claim | Recalculation or inspection | Assessment |
|---|---|---|
| Lines 7–9: `v(t)=3−2t`, final velocity `−5 m/s`, moving left | `v(4)=3−2×4=−5 m/s`; `Δv=−8 m/s`. The negative final velocity gives leftward direction, while the negative acceleration gives decreasing signed velocity. | Correct. |
| Line 9: instantaneous rest at `1.5 s`, followed by reversal | `3−2t=0` gives `t=1.5 s`. Velocity is positive before this time and negative after it within `[0,4]`. | Correct; this is an instant of rest, not a finite interval without motion. |
| Line 10: signed displacement `−4 m` | Integrating velocity gives `3×4−4²=−4 m`. Signed triangular graph areas independently reproduce `2.25−6.25=−4 m`. | Correct. |
| Lines 10–12: distance `8.5 m`, comprising `2.25 m` rightward and `6.25 m` leftward | First triangle: `½×1.5×3=2.25 m`. Second magnitude: `½×2.5×5=6.25 m`. Distance is their sum, `8.5 m`, rather than the magnitude of net displacement. | Correct. |
| Line 12: zero velocity does not imply zero acceleration | At `t=1.5 s`, `v=0` and the stipulated acceleration remains `−2 m/s²`. | Correct and relevant to the target misconception. |
| Lines 14–16: with zero acceleration, final velocity `+3 m/s`, displacement and distance `12 m`, no reversal | The velocity stays positive and constant: `v=3`, `s=3×4=12 m`, and the signed velocity never crosses zero. | Correct limiting/contrary case. |
| Line 16: preserve units and signs | `a×t` has units `m/s`; `v₀×t`, `a×t²`, and velocity-time areas have units `m`. Directional signs and nonnegative distance are consistent throughout. | Correct by inspection. |

The Python witness, [check_lesson.py](sandbox:/workspace/scratch/52eed2252c51/tmp/ir-forward/lesson/out/check_lesson.py), executed successfully and wrote [calculation-log.json](sandbox:/workspace/scratch/52eed2252c51/tmp/ir-forward/lesson/out/calculation-log.json). It uses exact fractions to integrate each interval and cross-check the main case with velocity-time triangles. All 17 arithmetic and interval assertions passed; the run returned exit code 0. The log records the execution timestamp and the source byte hash. The geometric check and the integration share the stipulated constant-acceleration model, so they are alternative arithmetic routes rather than separate validation of that physical premise.

Two additional reasoning checks discriminate direction from acceleration:

- In the supplied example, at `t=0.5 s`, `v=+2 m/s` and `a=−2 m/s²`: the cart moves right while its signed velocity decreases. At `t=2 s`, `v=−1 m/s` with the same acceleration: it moves left and speeds up. These snapshots were inspected mathematically; no learner response was observed.
- A reviewer-created contrary case, `v₀=−4 m/s`, `a=+1 m/s²`, over `6 s`, was computed in the witness. At `t=1 s`, it still moves left (`v=−3 m/s`) even though signed velocity is increasing; it reverses at `4 s`, finishes at `+2 m/s`, and has displacement `−6 m` and distance `10 m`. This guards against treating acceleration's sign as motion direction. It is a reviewer consistency probe, not evidence of learner transfer.

## Aim, findings and uncertainty

The page explicitly presents a worked task, so its fully supplied answers do not contradict its stated format. Its positive initial velocity with negative acceleration, later negative velocity, nonzero acceleration at rest, and zero-acceleration contrast expose the intended distinctions within a compact example. It also correctly distinguishes displacement from distance. A complete mechanics curriculum, independent learner assessment, UI, original research or classroom trial is not part of its promise.

**Material findings: none.** An optional clarity improvement is to state the direction/change distinction directly in one sentence, for example: “Negative acceleration makes signed velocity decrease; the cart first slows while moving right, then speeds up while moving left.” This is an enhancement to an already consistent worked example, not a correction required by this review.

Established facts are the inspected source bytes and the executed calculation results. The page's instructional aim is a stated intention. Alignment with that intention is this reviewer's source-based judgment. Actual comprehension, retention, misconceptions after use, accessibility in a delivery environment, and classroom effectiveness are unknown and were not tested. No missing learner trial is recorded as a source defect.

## Independence and exposure

| Dimension | Actual basis and limit |
|---|---|
| Authorship/principal | One reviewing agent performed this attempt and did not author or modify the candidate in this attempt. The candidate's original author/principal was not authenticated. A distinct-principal independent review is therefore not established. |
| Context/exposure | The inherited task named the candidate, purpose, output directory and review boundaries. The full page, including its answers, was read before calculations were derived. No golden examples, unrelated histories, other agents' outputs or optional schema/template were read for this review. Workspace or training exposure beyond this attempt cannot be authenticated. |
| Expected behavior | Derived after source exposure from elementary constant-acceleration definitions and the stipulated givens; no hidden expected-answer set or blind discovery claim. |
| Method | Direct source inspection, exact rational calculations, geometric area cross-check, dimensional inspection and a newly chosen contrary example. |
| Execution | The local Python witness actually ran on the recorded source binding. Source prose and conceptual claims were manually inspected. No browser, learner experiment, simulation of classroom performance, benchmark or generator was run. |
| Upstream lineage | All main-case checks share the page's given initial velocity, acceleration and duration, as appropriate to checking that example. The alternative calculations do not establish independent source provenance or validate a real-world cart model. |

## Read/run record and continuation

Read in full:

- `/workspace/scratch/52eed2252c51/Common-independent-review/skills/independent-review/SKILL.md`
- `/workspace/scratch/52eed2252c51/Common-independent-review/skills/independent-review/references/INDEPENDENCE.md`
- `/workspace/scratch/52eed2252c51/Common-independent-review/skills/independent-review/references/APPLYING_GUIDANCE.md`
- `/workspace/scratch/52eed2252c51/Common-independent-review/AGENTS.md`
- `/workspace/scratch/52eed2252c51/tmp/ir-forward/lesson/inputs/lesson.md`

Executed: line-numbered source inspection; SHA-256 calculation on the candidate and the three skill files; `python --version` (Python 3.12.14); and `python /workspace/scratch/52eed2252c51/tmp/ir-forward/lesson/out/check_lesson.py` (successful exit). A final local Python sanity check confirmed the source hash remained unchanged, the report contained that binding, the JSON log parsed, and the witness contained 17 assertions; the report was then read back in full. File-existence checks found no additional `AGENTS.md` on the enumerated workspace/input/skill parent paths. The calculation log is the durable arithmetic witness.

**Next useful action:** retain the page as a correct short worked example. The author may optionally add the single explanatory sentence above if the direction/change distinction should be more explicit. No additional role or assistance is needed to complete this source review. Any later claim about learner performance would require separate evidence and is outside this verdict. Owner acceptance remains separate from review completion.
