# 182-P6 | Technical lead shared-CI follow-up: queue amplification and D4 APPLY failure

2026-10-12 | Tab1 | chat=6acc408a | Issue Grade9v3.5 #182 | aim=v3.1.0 label_sha 2ff9246 | O1 (real five-role renderer/golden CI prerequisite) | ac=0/4 | **CI remediation proposed, not merged or active globally**

Outcome: O1
For the user: No live learner workflow changed. The technical lead independently diagnosed the queue amplification and the D4 specific source-figure failure, avoided an unnecessary duplicate D4 fix/push, and created an isolated single-commit draft workflow throttle that preserves all PR checks and main runs. The existing queue has NOT been canceled and the throttle is NOT YET applied to workers.
Proof: [CI mitigation draft #197](https://github.com/reallakshman19/Grade9v3.5/pull/197) · [D4 failing run 38245419910](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38245419910) · [issue #182](https://github.com/reallakshman19/Grade9v3.5/issues/182)

## Trigger: Coordinator fact and independently verified live API

Coordinator at 2026-10-12 16:25 Asia/Muscat: over 100 queued/30 running; branch `agent/imo182-qrt-d1-represent` 111 queued after 13 pushes in six minutes, each push fans out about ten workflows on both `push` and `pull_request`; D2 APPLY-D2 and D3 EXPLAIN-D3 marked `BLOCKED_RENDER` due to queue, D4 `38245419910` actual renderer workflow failed. Coordinator already requested workers proceed to next cell; lead owns CI follow-up, not blocked worker ping-pong.

**Live GitHub Actions GET observed during triage:** at first read **159 queued, 31 in_progress**, second read **151 queued, 32 in_progress** (these totals are changing snapshots, not a trend claim). Query `GET /repos/reallakshman19/Grade9v3.5/actions/runs?branch=...&status=...&per_page=50` then returned:

| Branch, candidate | Queued | In progress | Important interpretation |
| --- | ---: | ---: | --- |
| `agent/imo182-qrt-d1-represent` (#192) | 85 | 17 | many older heads, push+PR duplicated; 111 earlier Coordinator observation was a different time |
| `agent/imo182-qrt-d2-justify-20261012` (#191) | 4 | 7 | queued exact-head APPLY/EXPLAIN-D2 does **not** mean renderer failed |
| `agent-d3/imo182-qrt-model-d3` (#193) | 30 | 7 | queued MODEL/APPLY/EXPLAIN-D3 mix; do **not** mark output failed until specific workflow executes |
| `agent/imo182-qrt-d4-apply-pilot` (#196) | 9 | 4 | failed old SHA + latest queued head are separate |
| `agent/imo182-qrt-d4-model-pilot` | 3 | 0 | newer pushes add queue load even before additional PRs |

The first page of 100 queued runs had **69 pull_request + 31 push**. Among them `guardrails` 18, `v31-relay` 18, `learner-platform-code-tests` 17, other source checkers and worker-local QRT five-role workflows. Main shared `guardrails.yml`, `learner-quality.yml`, `v3-relay.yml` use `push branches: ["**"]` AND `pull_request`, and source-specific workflows also run; `canonical-assurance.yml` uses PR + main push. This directly explains amplified work per small source commit.

## D4 APPLY-D4 root cause, test verdict, new-head proof

- **Failed run** [38245419910](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38245419910), workflow `IMO 182 QRT APPLY D4 authored TEST (sole renderer)`, PR #196 *old* SHA `93fcc6152a4ae57c92fb8dae0ad808845686f9ad`:
  - `test_compatible_incompatible_and_corrected_arithmetic` **PASS**;
  - `test_registered_renderer_golden_anatomy_and_protected_answer` **PASS**;
  - `test_schema_rights_and_h3` **FAIL** because pre-attempt `<desc>` text `All phases and inclusive interval only, no solution class.` includes prohibited substring `no solution` in `tests/test_imo182_qrt_d4_apply.py` line 39. It is an authoring/a11y-descriptor + literal leakage-test mismatch; **NOT a failed renderer, not arithmetic proof failure, not even an observed answer leakage**. Keep the invariant: pre-attempt accessible text must not give winning residues or outcome.
- **Current PR #196 head** `0d36673633e115ecaa261917ee2066a80c3accc2` is distinct. The actual four `TEST/imo-research/qrt-d4/figures/apply-core1a.svg,apply-core1b.svg,apply-core2a.svg,apply-core2b.svg` source `<desc>` was fetched: **none contains “no solution”**, nor the previously leaked conclusion. At this read latest `IMO 182 QRT APPLY D4 authored TEST (sole renderer)` run **38248875649 queued**. Code-level remediation visible; **latest test PASS not yet confirmed**. No extra push or rerun was made, avoiding further CI flood.
- Lead directive: do not conflate **`BLOCKED_CI_QUEUE`** (hasn't run) with **`BLOCKED_RENDER`** (renderer ran and failed); preserve exact failed head and latest repaired head as separate evidence. New D4 pass only when latest exact SHA's workflow concludes SUCCESS and SHA-bound output is checked.

## Remediation proposed in a single atomic draft commit (not merged)

[DRAFT PR #197](https://github.com/reallakshman19/Grade9v3.5/pull/197), branch `agent/issue-182-shared-ci-concurrency-lead-6acc408a`, exact head **`a846174607ab93e3a3a0f7eb7cc799a803c55ab1`**, base `main@778eb35a70517a46108ad0a5dc01dfc89f61c0e3`.

**Six existing shared workflow files** changed only by adding the same top-level workflow concurrency policy: `guardrails.yml`, `learner-quality.yml`, `v3-relay.yml`, `canonical-assurance.yml`, `question-bank-platform.yml`, `imo-research-validation.yml`. Exact PR diff proves original `jobs:` subtree, triggers, paths and permissions remain **untouched**. One Github Git-data tree/commit/ref update, rather than six pushes.

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.event_name }}-${{ github.head_ref || github.ref_name }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}
```

Rationale: for any worker branch, supersede obsolete **same-workflow + same-event + same-branch** runs after new commit, while retaining all latest SHA checks and keeping PR-specific policy evaluations separate from push checks. Main-branch runs cannot be automatically canceled under this rule. It intentionally does **not** remove or path-filter required `guardrails` or `canonical-assurance` tests; no hidden `continue-on-error`, no reduced test count. Since worker-local QRT workflows were authored on each branch, their own trigger/concurrency should be updated by each worker *in a batched change*, with lead review, not silently touched by this six-file proposal.

**Limitations:** The available GitHub connector has **no cancel-workflow-run action**; GET-only GitHub API fetch cannot cancel 100 existing queued runs. This PR is **DRAFT/unmerged**, so its mitigation is not effective across worker branches/main yet and cannot be reported as eliminated congestion. CI-owner/Owner may decide whether to land the policy after ensuring GitHub branch checks remain required. Proposal itself queued workflow checks; no whole CI green statement.

## Operational no-Owner-ping-pong instructions (workers/lead)

1. **During congestion** workers continue authoring *without repeated tiny pushes*; consolidate logically coherent cell fixes and push only once the cell has valid schema/math/semantic logic, not for every figure-string edit. A queued exact-head test is `BLOCKED_CI_QUEUE` (or CI_PENDING), not `BLOCKED_RENDER` or green.
2. Each worker's scoped QRT workflow should preserve `pull_request` and `workflow_dispatch` while considering **`push` only for main** or same-event branch concurrency; do not drop required PR event, the sole-renderer test, exact SHA receipt, golden role QA, or D2 H3 after-attempt security check. Update local branch workflows **only with a well-defined ownership and CI event policy**.
3. Lead follows latest **PR head SHA** and exact workflow name/run; old failure on SHA A never blocks recognizing fixed source on newer SHA B, but newer source is not a PASS until hosted CI completes. Avoid rerunning failed old jobs with known fixed source (adds congestion).
4. No direct repo-wide workflow merge, main/PR required checks, source rights, QRT accepted field, Owner frozen golden or release was touched. Owner decision remains required for global CI policy merge and academic QRT acceptance.

## Outcome / status to report

- O1 prerequisite: **CI congestion verified; mitigation proposed in code on draft PR #197; backlog not canceled**. D2/D3 **WAIT_FOR_EXACT_HEAD_CI**, not actual renderer failure. D4 actual old failure diagnosed; newer source corrected; latest run queued. This is real operational engineering work, not an O1 learner page accepted milestone.
- O2 still **0/28 accepted**; no academic review claim. Previously existing authored five-role pages remain unmerged.
- A4 printer parked, authentic Core2 rights separate, Owner golden unchanged.
- Next: CI owner review draft concurrency policy / workers batch pushes; lead checks exact D2/D3/D4 latest runs and repairs true failed attempts without causing another flood. If no CI owner merges PR, congestion remains unsolved; never claim otherwise.
