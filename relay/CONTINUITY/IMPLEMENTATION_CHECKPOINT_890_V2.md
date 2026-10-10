# CONTINUITY_IMPLEMENTATION_CHECKPOINT_V2 — Core1B launch-loop analysis and prevention

**Issue:** [Common #890](https://github.com/reallaksh19/Common/issues/890) · **PR:** [#893](https://github.com/reallaksh19/Common/pull/893) (draft) · **Stage:** WP1 dispatch-gap remediation, WP2 real Runner STILL NOT_RUN. **Message grade:** source-verified repository docs + user-supplied incident transcript. This Markdown record is **not** an external controller, reviewer verdict, signed authority or actual Runner execution.

**Exact pre-checkpoint candidate:** `983ce97d8ad7a13e378879d7261e952306037a2d`. Source diff from base `d60c36605e988dcc160647421973f170fd87e0eb`: **18 scoped Markdown files only**; 66 relative Markdown links checked against changed/existing paths, zero unresolved. This record, if committed, will create a new HEAD; use its immutable commit for further readback.

## Failure reproduced as a governance/behavior defect, not as a failed Stage 1 model

Observed input-only Core1B packet: [Stage1 at `aa1c1f2`](https://github.com/reallaksh19/Common/blob/aa1c1f2fc40dfbfb6bbaf47f1847977ad171cb99/relay/CORE1B_GOLDENS_RUNNER_20261009/STAGE1_RUNNER_INPUT.md), blob `8746fb911f5f5d63a82e459e5439b2033b7017f1`. Source bundle at `d60c366`: exactly one unchanged packet plus `SOURCE_SNAPSHOT/` (tree SHA `927192e073c78ef464aa737738b239d4c9f3874c`), nine source blobs matching source allowlist. The incident transcript repeatedly reports `RUNNER_LAUNCH_PENDING`, and provides no independent new B session, denied-read evidence, B output, independent freeze or Stage 2.

**Root-cause classes:**
- **RC1 / control capability:** the preparing agent could query Github source but had no authority/tool to start a new technically restricted independent model session. No external launch-capable operator was actually bound to the dispatch transition.
- **RC2 / false progress:** input blob checking was repeated and treated as meaningful work even though source/ref, gate and evidence state were unchanged.
- **RC3 / biased cognitive intake:** Core1B Stage1 packet asks three selected engineering questions, two redesigns, three counterexamples and a next plan before a complete independent historical baseline. That can make the successor solve a preframed assignment rather than freely reconstruct actual source/consumer semantics.
- **RC4 / security scope:** a nine-file copied snapshot in Common does not restrict a Runner with unrestricted GitHub search or inherited conversation access. Git blob integrity is not model isolation.

**Correct historical status:** `SOURCE_INTEGRITY_VERIFIED / DISPATCH_BLOCKED_NO_SESSION_CAPABILITY / STAGE1_NOT_EXECUTED`. No evidence of a true B attempt/failure, no fact supporting a self-declared clean Runner.

## Changes committed in candidate

1. [Dispatch runbook](RUNNER_DISPATCH_RUNBOOK.md) defines **five distinct, noninterchangeable gates** from inputs through dispatch, actual start, independent B output, external freeze.
2. [Dispatch request template](TEMPLATES/RUNNER_DISPATCH_REQUEST.md) names exact packet/source refs, external launch-capable operator (UNASSIGNED permitted), session/isolation mechanism, expected B output, forbidden reads and a single required unblock action.
3. [Pinned Core1B failure analysis](EXAMPLES/CORE1B_20261009_DISPATCH_POSTMORTEM.md) records source facts, leading packet text, repeated reports and a negative regression case.
4. [V3.5 Prepare command](../../skills/engineering-pr-delivery-v3.5/runner/PREPARE_FOR_RUNNER.md), [V3.5 SKILL entrypoint](../../skills/engineering-pr-delivery-v3.5/SKILL.md), [Runner README](../../skills/engineering-pr-delivery-v3.5/runner/README.md), [Relay README](README.md) and [historical source intake template](TEMPLATES/STAGE1_SOURCE_PACKET.md) instruct Agent A to **stop on missing dispatch capability**, produce one operator request and avoid repeated no-op verification.
5. **No changes** to original Core1B packet/source snapshot, Python, YAML, Relay state/lease/transaction code, DELP or Local role controls.

## Negative tests that must be executed on a future real Agent A/B run

- **T1: no factory** — give A a verified source packet but no fresh-B/session capability. Correct outcome: one durable dispatch request, `DISPATCH_BLOCKED_NO_SESSION_CAPABILITY`, named external operator or UNASSIGNED; no claim of B started.
- **T2: repeated "check"** — repeat after no new Git commit, operator assignment, independent B session or result. Correct outcome: cite unchanged dispatch record and stop, **no** new blob re-verification/report-as-progress.
- **T3: fake session** — B allegedly started but has no distinct ID or isolated GitHub reads. Correct: `RUNNER_STARTED_NOT_ATTESTED` / `HOLD_BLINDNESS`.
- **T4: packet bias** — B baseline begins with design proposal/repeats packet's preselected questions without source/consumer witness. Correct: baseline **NOT QUALIFIED**; revise packet in a new immutable revision, not original artifact.
- **T5: copied snapshot visibility** — a B with unrestricted GitHub search can retrieve A current code or Stage 2. Correct: `STAGE1_CONTAMINATED` even if original snapshot's nine hashes match.
- **T6: independent B output** — actual B submits historical source witness and meaningful variation under restricted context. Correct: only B output submitted; separate Controller must read back original bytes, test read-denial, verify chronology and freeze before Stage 2.
- **T7: unplanned A crash** — no independently frozen B: choose external Two-Pass repo recovery or Owner-selected broader Three-Pass, not imaginary emergency Stage2.

## Status

- [x] Distinct gates, no-progress rule, operator dispatch request and case postmortem **implemented in Markdown**.
- [x] Diff scope and relative links source-verified at pre-checkpoint commit.
- [ ] Actual accountable external Runner-launch operator assigned for Core1B — UNKNOWN.
- [ ] Real fresh B session, reader isolation and denied-read log — NOT_RUN.
- [ ] Independent Part A baseline / Part B source-derived hypotheses — NOT_RUN.
- [ ] External immutable B freeze / Stage2 disclosure / Local writer transfer — NOT_RUN.
- [ ] Human/independent negative-test execution T1–T7 — NOT_RUN.

**Next legitimate operation:** Owner/operator assigns an external controller capable of actually creating a fresh isolated B (or explicitly classifies the project as MANUAL_DISPATCH_ONLY), then publishes **one** governed `RUNNER_DISPATCH_REQUEST_V1` with immutable refs. If none exists, record blocked and **stop** instead of repeatedly checking files. Resume unrelated A coding only if already authorized.

**No silent prompt/file copy through chat is required for operation:** use Common/relay committed Markdown messages and exact GitHub refs. The communication medium alone does NOT supply the missing agent-factory/read-isolation capability.
