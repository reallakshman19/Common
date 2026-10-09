# HANDOVER_TECHNICAL_V2 — self-contained successor engineering report (template)

**Visibility:** `STAGE2_AFTER_FREEZE_ONLY` — Stage 2 after independently authenticated Stage 1 freeze only. If read isolation is unverified, keep the actual Agent A implementation report on a controller-only surface; GitHub folder names do not enforce privacy. **Record type:** factual technical report / derived handover view, not a process plan, execution instruction, Writer grant or a new evidence/lease authority. Derive custody claims from the existing native `PLAN_HANDOVER`, `HANDOVER_CONTEXT` and provider readback. Where these are absent, state `NOT_PUBLISHED`, `NOT_VERIFIED` or `UNKNOWN` rather than manufacturing them.

> **Writing rule:** Fill this as ONE coherent report that an unfamiliar engineer can read from beginning to end. A list of file names or a status checklist cannot substitute for the original problem, implemented mechanisms, call flow, concrete test observations and precise resumption. Source refs are citations for verification—not prerequisites to understanding. Inapplicable sections must say why, not disappear.

## 1. Technical situation and outcome — read this first

Explain in 2–4 paragraphs: what problem the Owner needed solved, what the code currently does that it previously did not, what is demonstrably working, what is not yet implemented, and whether the feature is deployable. Make the difference between an implemented change, a CI-tested change, and an accepted/released result unmistakable. **Do not substitute a completion percentage or PR title for the explanation.**

## 2. Original problem, requirements and source of authority

Explain the actual user-facing/system defect or required behavior and why it matters, with a concrete original input→expected behavior example. Record the original Owner WHAT/WHY and acceptance requirements verbatim where short, otherwise faithfully paraphrase with exact source ref. Distinguish `OWNER_VERIFIED`, `SOURCE_VERIFIED`, `AGENT_A_CLAIM`, `INFERENCE`, and `UNKNOWN`. Explain constraints (scope, affected product flows, performance, fixtures, forbidden changes, reviewer or Owner decisions). **Do not rewrite later Agent A HOW as if it were the original requirement.**

## 3. Repositories, migration, branches and exact starting point

**R14 source-identity spine (when applicable):** Report `PLAN_GRAPH_REVISION` as the approved plan/graph identifier and digest; `SESSION_SOURCE_COMMIT` as the exact Agent A session source observation; and `CODE_CANDIDATE_HEAD` as the current proposed implementation Git commit. Each has its own provider readback time, distinct purpose and authority grade. Also record the original task-start commit and historical research cutoff **separately** from those three roles, the PR base, the latest tested head and the current `main` HEAD. When not independently available, state `UNKNOWN` rather than inventing an equivalence or copying one SHA into every slot.

**Provider-object migration:** For each historical and current issue/PR, identify the exact repository, provider object kind, canonical URL and freshly fetched identity (or `UNKNOWN`). An old-repository issue number does not become a new-repository issue, and a pull-request object returned by the GitHub issues endpoint is not an ordinary implementation issue. Keep current Owner/Local scope authorization separate from a successful provider-identity GET.

| Role | Repository and exact revision | Evidence and limitations |
| --- | --- | --- |
| Original task-start of Agent A | `<owner repository>@<SHA>` or `UNKNOWN` | Distinguish from an archival/research cutoff |
| Original historical research snapshot | `<repository>@<SHA>` or `UNKNOWN` | Original inputs/allowlist; not the task-start SHA |
| Current canonical repository and default branch | `<owner/repo>`, `main@<SHA>` | Provider-readback time |
| Current working branch, issue, PR and HEAD | `<branch>@<SHA>`, refs, draft/merge state | Candidate is NOT default branch |
| Source tested in each test run | `<SHA>`, command, run link | Never imply a previous head tests the current head |
| Former repository/old issue/PR references | `<old/repo>`, refs | State which discussions/metadata did NOT migrate |

Describe *how* the repository move affects Git histories, issue and PR numbering, clone/remote URLs, deployment/publication, and the next engineer's checkout. Name uncommitted local changes or say `UNKNOWN`; do not claim a clean workspace from GitHub alone.

## 4. Architecture and complete execution flow — HOW it actually works

Describe the **actual implementation**, including source-of-truth input, verified producer-to-downstream consumer edges and final user-visible behavior, not a speculative architecture or Agent A's claims. Cover the fault/recovery path, external read access and transaction integrity separately; absence of real consumer output must be `MISSING_CONSUMER` or `NOT_RUN`, never a hypothetical PASS.

Explain the **before and after** behavior in prose. Then trace one real path end to end, for example:

`original input or provider read → CLI/UI entrypoint → parser/validator → source module/functions → native transaction/worker → data or persisted output → downstream reader/consumer → visible or stored result`.

For EACH boundary, identify actual function/module names, input/output data shape, main invariants, error/rollback/cancellation or retry behavior, and dependencies including consumer call edges. Explain ownership of authority: what source is canonical, what is a derived read view, where authentication/isolation comes from, and what never becomes authority. If a piece was not examined, label `UNKNOWN` and give the source locus. A flow that simply repeats module names is not sufficient.

## 5. Exact implementation delta — what changed and why

| File/module, function or interface | Before → after behavior and reason | Consumers, compatibility and risk | Evidence |
| --- | --- | --- | --- |
| `<path>::<function>` | Explain actual semantic change, not `updated logic` | Caller(s), downstream flow, schema version, fallback | immutable diff/commit |

Include added, removed and untouched-but-relied-upon modules. Explain revisions to the initial design, alternatives rejected with reason, configuration values and bounds, transaction identities and naming, generated artifacts, tests, deployment wiring, and backwards-compatibility. Identify any work deliberately excluded. **No inaccurate `all implemented` claim where a missing integration or authority gate remains.**

## 6. Real inputs, outputs, fixtures and user-visible evidence

Present at least one source-grounded positive example and a negative/adversarial example. State provenance of every fixture (`REAL_ORIGINAL`, `SYNTHETIC`, `UNKNOWN`) and any expected golden output. For UI/product tasks show the actual browser route/steps/observed result and performance or error observations; if not run say `BROWSER_NOT_RUN`. For infrastructure tasks show the actual command or API request, input, output/receipt, exact location and failure mode. Separate simulated examples from production reality.

## 7. Tests, CI, performance and reproducibility

**Execution-grounded CI classification:** Record the whole-run conclusion **and the individual relevant job/step results** for each named check. A workflow marked SUCCESS with its relevant test steps SKIPPED is not evidence those tests passed. Record `EXECUTED_PASS`, `EXECUTED_FAIL`, `SKIPPED_NOT_EXECUTED`, `NOT_RUN`, and `ZERO_STEPS/NO_RUNNER` separately; the latter means a hosted job never actually reached test execution. A required check failing because legacy fixtures/workflows are absent on both base and candidate is an `INHERITED_BASELINE_FAILURE`, **still RED**, and must not be silently waived or counted as a code PASS. Show exact log/command/provider run ID, all expected cases, skip reasons, tested SHA, base SHA, current candidate SHA and discrepancy. Never equate a later report commit with the tested source HEAD.

**Per-source claim ledger:** Distinguish a source-level authored test, an actually executed test, a real-browser user journey, a fixture/golden parity observation and a source/peer review. Mark the result `NOT_VERIFIED` when provider logs, environment or required real output are absent.

| Exact candidate SHA | Command or workflow/run + environment | Actual executed cases and outcomes | Interpretation |
| --- | --- | --- | --- |
| `<SHA>` | `<literal command>`; Node/Python/browser/version | N PASS, M FAIL, SKIPPED or `NOT_RUN` with log links | Tested fact, expected RED, infrastructure problem, or open defect |

Provide reproducible commands and required fixtures/environment; record error text or representative failure lines, expected red versus new bug, negative tests, golden parity, and whether the *current* HEAD differs from tested HEAD. Benchmark only actually measured values with input size, hardware/browser/context, baseline and target; otherwise `NOT_BENCHMARKED`. Include real served-app/Chromium behavior when the task demands it. Never infer PASS from authored tests or a job with zero executed steps.

## 8. Known failures, unresolved decisions and technical debt

Classify each failure as `INHERITED_BASELINE_FAILURE`, `NEW_CANDIDATE_REGRESSION`, `ZERO_STEPS/NO_RUNNER`, `EXPECTED_RED`, `PERMISSION_HOLD` or `UNKNOWN`, with positive and negative evidence at the exact affected SHA. Do not conceal a red required check under an 'unrelated' label; report its actual disposition and whoever may authorize a repair or exception.

Discuss every material defect by symptom, reproduction, root cause if verified, impact/severity, affected branch/SHA, workaround, and proposed safe repair boundary. Separate `BLOCKER`, `RISK`, `EXPECTED_RED`, `UNRELATED_FAILURE`, `NOT_RUN`, `UNKNOWN`. Include failed strategies and why they were abandoned. Distinguish missing external permission/Runner capability from a code failure. Name what remains intentionally protected or on HOLD.

## 9. Current engineering and custody truth

**Authority partition:** `HANDOVER_CONTEXT` and the existing native `PLAN_HANDOVER` transaction retain custody truth, not the technical narrative. R14 `PLAN_GRAPH_REVISION`, `SESSION_SOURCE_COMMIT` and `CODE_CANDIDATE_HEAD` are separately graded sources and cannot impersonate Owner consent, Local writer admission, a frozen independent B Stage1, or accepted DELP evidence. Explicitly distinguish read-only Stage2 disclosure from source-write or merge authority.

Explain the latest actual native Relay state/checkpoint/lease/DELP/Local writer and Owner/reviewer authority **as externally verifiable**. Name current PR status, pending reviews, CI, live/deployed version, in-flight commits/API writes and recovery risk. If only a draft Markdown candidate exists, say it has **no** effect on native `PLAN_HANDOVER`, accepted TASK_EVIDENCE, P/E/D, exclusive writer custody or Stage 2 admission. Mention both confirmed and unverified facts.

## 10. Immediate successor entry point — reproduce and continue

State exact target repository/branch/HEAD and **the first command or code-reading action**. Explain what it should show, a bounded next engineering change if admission permits, which tests must run at the successor's resulting head, what outcome constitutes success, and what must be checked before making a write. Include concrete files/functions and the known failing case. Identify the conditions under which the successor must STOP or require Owner approval. This is **navigation of an existing technical state**, not a newly approved plan or an implicit write grant.

## 11. Source-grounded reconstruction questions

Provide three questions that would reveal a misunderstanding of the implementation, each with the **specific source anchors**, proof needed, a plausible but incorrect shortcut, and a falsifying test/read. Questions should cover (a) original requirement vs selected mechanism, (b) downstream consumer/authority or rollback, and (c) current exact-head test/defect and next permitted action. These are for post-freeze verification only, not Stage 1 hints.

## 12. Evidence index and explicit limits

Conclude with short linked primary sources: original Owner issue/intent, source commits and diff, native transaction/handover or `UNKNOWN`, tests/CI logs, browser/fixtures (or `NOT_RUN`), current PR/issue reviews, migration proof and any unresolved provider operations. Include a paragraph enumerating precisely which required claims are **not** established. Every claim about a test, actor identity or approval must be grounded in provider evidence rather than Agent A narration.

---

### Report authoring and release boundary

**Interruption attribution:** If the predecessor is no longer present, identify the report as `PROVIDER_RECONSTRUCTED` / `INTERRUPTED_NO_PACKET`; never attribute inferred choices, original motivation or private plan revisions to Agent A. Its original current implementation, source symptoms and positive/negative outcomes must be independently supported or marked `UNKNOWN`.

This report is **one finished technical explanation**, not a sequence of commands to prompt a model and not a new source-of-truth YAML schema. The existing `HANDOVER_CONTEXT` remains the native custody source; this Markdown is its detailed, source-verified engineer-readable companion. Prepare it before exit but do not expose its current Agent A HOW to independent Stage 1 B. On unexpected termination, the controller may create a `PROVIDER_RECONSTRUCTED` report and label unprovable Agent A plans `UNKNOWN`. Release to Stage 2 only after independently observed B freeze and actual read admission; still require existing Owner/Local source-writer permission.