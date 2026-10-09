# HANDOVER_TECHNICAL_V2 — complete engineering reality report

**Deliverable:** One **self-contained Markdown technical handover report**, authored by the predecessor when available, checked against exact Git/source/provider observations, and released as **Stage 2 technical reality only**. The report explains what was requested, what was implemented, **how the actual system works**, what passed/failed, and precisely where a successor resumes. It is **NOT** a procedure for planning a handover, an independent redesign proposal, a substitute for a frozen Runner Stage 1 answer, or an execution/writer authorization. Do not respond with this empty template: fill it with actual engineering facts.

**When Agent A has terminated:** A cannot author the report. An independently identified controller/successor may reconstruct it from provider/source/evidence with each missing A-specific fact marked `UNKNOWN` / `INTERRUPTED_NO_PACKET`. Never attribute inferred reasoning to A.

**Disclosure:** `STAGE2_AFTER_FREEZE_ONLY`. Keep current A source/PR/evidence unreadable by a clean Stage 1 Runner B before its actual independent freeze and external admission. In a public/broadly readable GitHub repository, a folder name or Markdown instruction does not enforce that boundary: postpone publication on B-readable refs unless actual read restrictions are independently attested.

## Handover identity and immediate readout

| Field | Actual verified value, timestamp / UNKNOWN |
| --- | --- |
| Report identity and author | `HANDOVER_TECHNICAL_V2`, [A / external reconstruction, attribution grade, UTC] |
| Governing Owner objective and responsibility | [original issue, parent, existing leaf, Local assignment **with repository owner/name**] |
| Code repository **today** | [canonical owner/repo, main SHA, working branch, exact candidate head/base, observed UTC] |
| Historical repository and GitHub governance | [old owner/repo and old issue/PR exact URLs; state as fetched; not automatically migrated] |
| Actual new-repo issue/PR | [freshly fetched owner/repo/number and URLs **or UNKNOWN**; identical commits do not establish object identity] |
| Original task-start vs research cutoff vs source-head vs tested-head | [**four separately named SHAs** / UNKNOWN, never conflated] |
| R14 references (when applicable) | [PLAN_GRAPH_REVISION path/digest; SESSION_SOURCE_COMMIT; CODE_CANDIDATE_HEAD; Owner/session/evidence claims and their independent authority grade] |
| Overall result at handover | [what concretely works; what is incomplete, **not percentage asserted by A**] |
| Current admission/merge/writer | [DRAFT/HOLD/UNKNOWN with actual provider and Local receipts; markdown creates none] |

**Read this first — a 5–10 sentence engineering summary.** [Explain the original user-facing problem, actual completed engineering outcome, key architecture change, strongest real test/browser evidence, highest-impact remaining failure, current exact HEAD, and the next safe investigation. Avoid “work completed, see PR” without content.]

**Successor's first safe action:** [ONE specific read/verify action in the correct repository at the checked source HEAD, with concrete path/symbol/test and observable success/failure; distinguish it from authorization to code.]

## 1. Original problem, Owner WHAT/WHY and acceptance

Write the original defect or requested product behavior **in technical and user terms**: what input/user action used to fail or was missing, its observed harm, the actual Owner request (direct authenticated quotation or `MIRROR` / `UNKNOWN`), and the desired result.

| Acceptance seam | Original observable requirement | Owner/source reference and approval grade | Current evidence / gap |
| --- | --- | --- | --- |
| [user operation → output] | [actual positive behavior/invariants, not a code implementation assumption] | [exact issue/Owner message and repository, original/mirror/inferred] | [real observation or NOT_RUN] |
| [negative/variation] | [error/rollback/no-match/stale/ambiguity treatment] | [source] | [observation / UNKNOWN] |

Separate **accepted scope**, explicitly rejected/parked proposals and **later Owner amendments** by timestamp/revision. Do not silently promote A's desired solution, a reviewer suggestion or an old repository's issue to a current Owner authorization.

## 2. Starting state and what changed

State the real starting architecture/behavior at the **verified task-start commit**, or `TASK_START_UNKNOWN` and the nearest independently pinned historical baseline. Explain what A found, why the previous behavior was inadequate and which invariant could not be broken.

Then narrate the changes in causal order—not just a list of commits. Include why the selected approach was preferable to specific rejected alternatives **when actual evidence exists**, what feature paths were intentionally untouched, and decisions revised while coding.

| Source/module and exact symbol | Before / defect | Implemented behavior and WHY | Direct callers and downstream consumer / output | Commit or PR diff proving change |
| --- | --- | --- | --- | --- |
| [file:function @ SHA] | [prior observed behavior] | [specific change, algorithm, tradeoff] | [actual call edge and final user-visible result] | [commit/line/PR, or UNKNOWN] |
| [test/fixture/worker/UI adapter] | [before] | [after] | [consumer and rollback/error path] | [exact ref] |

**Complete file inventory:** Summarize every changed production module and notable fixture/test/schema/CI file, highlighting unrelated changes (if any). For a very large diff, include a grouped inventory **in this report** and pin the exact comparison with enough symbol-level detail to follow the feature without reconstructing history from comments. Link to full diff as a *supplement*, never as the report itself.

## 3. Actual implementation architecture and end-to-end flow — HOW it works

Write an understandable prose walk-through from real input to observable output, preferably one *real positive* and one *real negative/changed-boundary* journey. The successor should be able to locate and explain the data and control flow **without assuming the original author is available**.

1. **Entry/input:** [UI/API/CLI event, input file or provider event, accepted formats/identity/source of truth].
2. **Admission/validation:** [exact module:function, permissions, source/plan/graph/lease/revision checks, rejection reason].
3. **Processing/data model:** [producer, transform, Worker/async boundaries, indexes, matching or calculation, persistent state; name exact source functions and invariants].
4. **Consumers and result:** [downstream modules, events, CSV/DOM/status/issue/PR/API output and actual externally observed behavior].
5. **Error, cancellation, retry and rollback:** [what happens on stale HEAD, invalid input, crash, partial write, denied access; actual observable result and cleanup].
6. **Deployment/run environment:** [build/serve paths, version/flags, browser/runner compatibility, external dependencies and whether live environment was inspected].
7. **Security/custody and trust:** [which bytes are code, authenticated Owner input, provider observation, agent claim, reviewer claim; where a read-only diagnostic ends].

| Flow edge | Exact producer and consumer at source SHA | Input identity / output invariant | Positive proof | Negative/variation proof |
| --- | --- | --- | --- | --- |
| [A → B] | [path:function → path:function] | [source identity / type] | [test/trace or NOT_RUN] | [case/trace or NOT_RUN] |

If the actual downstream consumer is not inspectable, write **`MISSING_CONSUMER`**, not an invented end-to-end PASS. Explain nonobvious ordering, configuration and background operations. A diagram is optional; the **prose walk-through and source edges are mandatory**.

## 4. Source state, repository migration and traceability

| Distinct identity | Exact value and verification time | Meaning / limitation |
| --- | --- | --- |
| Original Owner/governing history repository | [old owner/repo issue/PR numbers + direct URLs] | Historical GitHub objects; **not** new-repo mirrors |
| Current code repository / ID | [new owner/repo, provider-observed identity] | Source and current GitHub API namespace |
| Original task-start commit | [SHA or UNKNOWN] | True start, not protocol version |
| Historical research cutoff | [SHA or UNKNOWN] | Runner original source only |
| Approved plan graph revision | [R14 path/digest or UNKNOWN] | Accepted scope graph, distinct from code SHA |
| Agent A session source | [R14 session commit or UNKNOWN] | Caller reference, not attested Owner/executor custody |
| Candidate branch and PR | [new repo branch, actual PR or NONE, base/head] | Unmerged changes if any |
| Most recent verified test HEAD | [SHA per test, possibly different from candidate] | Test results do **not** automatically cover newer code |
| Checkpoint/transaction | [existing Relay handover transaction, snapshot and provider readback / UNKNOWN] | Custody context, not a new source of authority |

**Migration explanation:** Which Git refs/branches survived? Which original issues, PRs, comments, checks, review decisions, Actions and permissions did **not** transfer? Record independently fetched new-repo issue/PR numbers if they exist. Never transform historical URLs by text substitution, reuse a PR number across two repositories, or assign old reviewer/source authority to a new repo without an authenticated mapping.

## 5. Tests, fixtures, goldens, CI and browser evidence (exact, reproducible)

Separate **test code present**, **command actually executed**, **hosted CI run**, **real UI/browser acceptance** and **source-head currentness**. Report each as `PASS / FAIL / SKIPPED / NOT_RUN / BLOCKED / UNKNOWN`. Never report "tests green" solely from a PR description or a test file.

| Evidence type | Exact command/run URL, environment, fixture + golden hash | Commit/tested SHA, timestamp | Observed totals/result and failure excerpt | Current at candidate HEAD? |
| --- | --- | --- | --- | --- |
| Focused source test | [command, Node/Python version, OS, fixture hash] | [SHA/time] | [N passed/failed/skipped or NOT_RUN] | [YES/NO/UNKNOWN] |
| Full regression/native tests | [command and source] | [SHA/time] | [actual totals; failures] | [grade] |
| Hosted CI | [real workflow/run/job URL and conclusion; if pending/never scheduled say so] | [SHA/time] | [passed/failed/cancelled/no-runner/zero steps] | [grade] |
| Browser or real user flow | [actual deployed URL/Chromium version/actions/input/artifact] | [SHA/time] | [positive output, negative variation, console/network/long task where measured] | [grade] |
| Source verification only | [Git blob/commit and file/diff path] | [SHA/time] | [hash/path check; NOT test execution] | [grade] |

**CI result classification:** Record the **whole-run conclusion AND individual relevant job/step conclusions**, especially steps skipped by path/relevance filters. A successful workflow with source tests skipped is **not** proof those tests passed. A failure caused by files missing on both base and candidate is **INHERITED_BASELINE_FAILURE**, but remains a genuine red required check until authorized disposition; it must never be reclassified as PASS or omitted from the report. Distinguish `ZERO_STEPS/NO_RUNNER` infrastructure failures from an executed failing test and give the exact command/log excerpt. Match every claimed test result to its own tested SHA, not the report publication SHA.

State **how to reproduce** with exact working directory, invocation, setup/test fixture, expected observable result, known environmental limitations and where logs/artifacts are stored. If an original golden is unavailable, mark `GOLDEN_NOT_AVAILABLE`; do not create a convenient fake and call it authentic. Identify every exact-head gap, disabled CI, unexpected failure, skipped test and browser-not-run reason.

## 6. Known defects, failures, rejected approaches and risks

| ID / severity | Reproduction trigger and observed behavior | Root cause known / hypothesized (grade) | User/system impact + evidence | Workaround / status / owner boundary |
| --- | --- | --- | --- | --- |
| [D1] | [input, command, output, observed SHA] | [verified source or hypothesis] | [why it matters, downstream consumer] | [OPEN/BLOCKED/RESOLVED, permitted follow-up] |

Include **unsuccessful investigations and negative knowledge** that would otherwise be retried: methods tried, why they failed, what was ruled out by a reproducible negative test, and circumstances where tests/CI misled. Distinguish genuine defects from unrun tests or inaccessible systems. Describe high-priority unresolved acceptance separately from optional improvements.

## 7. Completed work, unfinished work and source boundaries

| Governed semantic unit | Actual code/evidence backing completion | Still incomplete / required acceptance | Scope priority and Owner disposition |
| --- | --- | --- | --- |
| [existing unit/leaf, no new EP] | [source and observed test / UNKNOWN] | [one measurable missing behavior, owner] | [HIGH/parked MEDIUM etc, accepted vs proposed] |

No unsupported progress percentages or "90% done" claims; no new workstream weight, owner-approved feature, plan rewrite or roadmap item hidden in a technical handover.

## 8. Outstanding operations and custody truth

Document **dirty/uncommitted paths**, open/in-flight tool calls, ambiguous push/merge/CI events, stale cached state, simultaneous actors, unreviewed security/privacy decisions, actual writer credentials and current provider HEAD (or `UNKNOWN`). This is a technical *state-of-the-world* report: the authoritative Relay transaction, Local writer/reviewer/Coordinator and Owner approval live elsewhere. An R14 `STOP_CLAIMED`, different reviewer label, or digest match **does not revoke a credential or prove independent acceptance**.

**Authority/status at publication:** [source-verified / claims only / HOLD]; **old writer revoked?** [YES with external negative GitHub mutation proof / NO / UNKNOWN]; **new writer admitted?** [external Owner+Local ref / NOT_GRANTED].

## 9. Successor starting point — exact first actions, not a new process plan

**Before editing:** [canonical repo URL, branch, candidate SHA, existing issue/PR and checked timestamp]. Verify current provider HEAD/dirty state and compare to the tested SHA. If moved, stop and reconcile; don't work from a stale screenshot or use a historical PR number.

1. **First safe read:** [actual path:function / artifact with exact ref and expected invariant].
2. **First diagnostic command or browser reproduction:** [one exact invocation/input and expected pass/fail observed historically; if untested, mark exploratory].
3. **Smallest missing acceptance unit:** [already governed responsibility, specific consumer path and acceptance result; source evidence and dependencies].
4. **Do not touch:** [protected source, files owned by another agent, accepted goldens, custody/DELP/Owner scope].
5. **Explicit blockers requiring decisions:** [real Owner/Local/reviewer, migration, security, unknown write, CI access].
6. **Condition for safe continuation:** [real execution gate and source-current outcome; technical handover alone NEVER admits a writer].

This is a **precise resumption waypoint**, not a speculative multi-phase implementation programme. If no execution authority is available, the first permitted action is read-only verification and the current status is **HOLD**.

## 10. Essential source references and source-grounded reconstruction questions

Cite the smallest set of original Owner decisions, exact changes/PR diff, native transaction/HANDOVER_CONTEXT, accepted fixtures/outputs, test logs, CI URLs and known-failure evidence. **Everything material still needs to be described above**; no critical fact may exist solely behind an external link. Mark unavailable documents `NOT_FOUND` / `UNKNOWN` and describe the consequence.

Original questions for a successor (count only when Owner/contract requires it): [genuine ambiguous points with source paths, test or falsifier; distinguish A's questions from B's frozen Stage 1 questions]. A Runner's questions belong to its independent Stage 1 and must be quoted unchanged in Stage 2, never manufactured here to force a quota.

### Author's self-check before publication (not a second document)

- [ ] Would an engineer unfamiliar with this task understand **original problem, user workflow, implementation HOW, exact modules/callers/consumers and observable outcome** solely from this report?
- [ ] Does each important completed result cite tested/current source, and are real test commands, CI run URLs, browser/fixtures/goldens and defects included with true `NOT_RUN` when missing?
- [ ] Are original task-start, historical cutoff, graph revision, session source, candidate/base HEAD, **tested** HEAD, old issue/PR repo and new issue/PR repo separated?
- [ ] Does it give an exact first safe action, known blockers and protected surfaces **without** pretending the report is an execution plan or authority grant?
- [ ] Does the report remain Stage 2-only until verified independent Stage 1 freeze and controller read admission?

**STOP:** Publish one complete `HANDOVER_TECHNICAL_V2` report as an allowed **Markdown message under Common/relay** or preserve as a withheld operator report if access isolation is not established. Link the existing authoritative `HANDOVER_CONTEXT`/transaction instead of duplicating its lease, DELP or Owner approval. It is an engineering narrative and factual checkpoint; it does **not** create a new EP, Start/Stop authorization, Stage 1 answer, Local reviewer verdict, merge or successor writer.
