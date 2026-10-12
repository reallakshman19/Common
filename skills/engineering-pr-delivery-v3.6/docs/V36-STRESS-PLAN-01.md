# V3.6 Full-Scale Stress Test Plan (V36-STRESS-PLAN-01)

> **Document Status:** PROPOSAL — RECONCILED WITH FOUR OWNER CORRECTIONS  
> **Execution Status:** NOT EXECUTED — PLANNING & PUBLICATION STAGE ONLY (0 Writes / 0 Mutations to GitHub Lab)  
> **Target Release:** Engineering PR Delivery v3.6 (merged to `Common/main` via PR #344 / commit `bd8ee38`)  
> **Proposed Disposable Lab:** `reallakshman19/relay-v36-stress-lab` (currently 404; pending Owner creation and write authorization)  
> **Governing Label Proposal:** `relay/AIM/V36-STRESS.yaml` (v1.0.0-draft, Change Card `CP-V36-STRESS-01`)  
> **Date:** October 12, 2026  

---

## 1. Executive Objective & Strict Governance Boundaries

### 1.1 Objective
Determine whether the merged v3.6 lifecycle can reliably manage large, concurrent, real GitHub projects under production-grade pressure—moving beyond unit tests and the historical two-child lab demonstration ([Common #341](https://github.com/reallakshman19/Common/issues/341)).

This is a write-enabled integration stress test designed to execute in an explicitly authorized, dedicated disposable repository once approved and provisioned by the repository Owner.

### 1.2 Boundary & Authority Rules (Reconciled Corrections 1 & 2)
1. **GitHub Recoverability (Correction 1):**
   - All artifacts (this specification, sticky label proposal, execution prompt, stage plan, and workload fixtures) are published to GitHub on branch `proposal/v36-stress-plan-01` in `reallakshman19/Common`.
   - Any cold successor agent can recover 100% of the plan, authority definitions, and prompt contracts directly from GitHub without relying on local machine files.
2. **Owner Approval Requirement (Correction 2):**
   - The sticky label `relay/AIM/V36-STRESS.yaml` and the lab directive `Writable lab: reallakshman19/relay-v36-stress-lab` are **proposals**, not pre-approved authority.
   - Execution is held on **HOLD** until the Owner reviews Change Card `CP-V36-STRESS-01`, approves the label, and provisions `reallakshman19/relay-v36-stress-lab`.
3. **Repository Isolation:**
   - All live test writes are strictly confined to the dedicated disposable repository: `reallakshman19/relay-v36-stress-lab`.
   - **ZERO writes or mutations** to `reallakshman19/Common`, `reallakshman19/relay-v36-e2e-lab`, or existing product repositories.
   - Historical evidence from [Common #341](https://github.com/reallakshman19/Common/issues/341) and the accepted v3.6 benchmark remains immutable read-only context.
4. **Execution Safety & Containment:**
   - Pinned v3.6 source only; trusted workflow runs; never execute untrusted PR code with elevated permissions.
   - Every CLI execution must bind explicit arguments: `--label relay/AIM/V36-STRESS.yaml`, `--plan <PLAN_PATH>`, and `--lab reallakshman19/relay-v36-stress-lab`.
   - Write operations require `--apply --confirm-scope reallakshman19/relay-v36-stress-lab#1`.

---

## 2. Separation of Test Stages vs. Workload Tasks (Correction 3)

To prevent inflated progress reporting and maintain a verifiable denominator, the test architecture strictly separates the **controlling test stages** from the **generated workload tasks**:

```
+---------------------------------------------------------------------------------+
| Parent Issue #1: Stress Test Orchestrator (Denominator: 6 Stages, Progress: E0/6 to E6/6) |
|   ├── V36-1-ST01: Foundation & Boundaries (Size S, Outcome O1)                   |
|   ├── V36-1-ST02: Progressive Scale & Pagination (Size L, Outcome O1)           |
|   │     └── Subject Load: 300 Workload Fixture Tasks (V36-LOAD-001..300)       |
|   ├── V36-1-ST03: Truthful Evidence & PR Attribution (Size L, Outcome O2)       |
|   │     └── Subject Load: 600 Evidence Comments (300 Positive / 300 Fixtures)   |
|   ├── V36-1-ST04: Concurrency & Event Storms (Size M, Outcome O3)               |
|   │     └── Subject Load: 1 -> 8 Concurrent Local Workers                        |
|   ├── V36-1-ST05: Fault Injection & Recovery (Size M, Outcome O3)                |
|   └── V36-1-ST06: Cold Successor & Endurance (Size M, Outcome O5)                |
+---------------------------------------------------------------------------------+
```

### 2.1 The Controlling Denominator: 6 Stages (`E0/6` to `E6/6`)
- Plan file: `skills/engineering-pr-delivery-v3.6/plans/V36-1-PLAN-02.yaml` (plan_version `V36-1-PLAN-02`)
- Parent issue: `reallakshman19/relay-v36-stress-lab#1`
- Tasks: `V36-1-ST01` through `V36-1-ST06`.
- **Exact Denominator:** Strictly **6**. The parent issue title reflects progress in terms of proven test stages (e.g. `[E1/6]`, `[E2/6]`, ..., `[E6/6]`).
- A stage is marked evidenced only after its specific acceptance criteria and GO-gate evidence are proven and posted on its dedicated child issue.

### 2.2 The Subject Workload: 300 Workload Tasks under Parent #8
- Workload Plan File: `skills/engineering-pr-delivery-v3.6/plans/V36-8-PLAN-01.yaml` (plan_version `V36-8-PLAN-01`)
- Workload Parent Issue: `reallakshman19/relay-v36-stress-lab#8`
- Workload Fixture Specification: `skills/engineering-pr-delivery-v3.6/plans/V36-LOAD-FIXTURE-300.yaml`
- Task IDs: `V36-8-LOAD001` through `V36-8-LOAD300`.
- **Integration with decompose_v36.py:** Unlike the top-level specification file, `V36-8-PLAN-01.yaml` is a fully compliant input to `decompose_v36.py`, providing a separate real parent (#8) and stable task IDs prefixed with `V36-8-`.
- **Preservation of Denominator:** Parent issue #1 maintains a strictly bounded denominator of **6** (`progress=E0/6` to `E6/6`). Materializing the 300 child tasks under Parent #8 fulfills the acceptance check for **Stage ST-02 (`progress=E2/6`)** on child issue #3 (`V36-1-ST02`).

---

## 3. Truthful Evidence & Explicit Fixture Markings (Correction 4)

In accordance with the v3.6 contract, evidence represents factual, reproducible test execution results:

### 3.1 Positive Evidence Rules (300 Cases)
1. **Genuinely Verified Test Facts & PR Proof URL:**
   - `snapshot_v36.py` line 16 requires a GitHub Pull Request URL (`https://github.com/<owner>/<repo>/pull/<N>`) matching the repository. Commit URLs (e.g. `/commit/<sha>`) are rejected by `proof_pr()` as `UNVERIFIED_PROOF`.
   - The candidate SHA must match the live PR's `head.sha` for the task to be recognized as `CURRENT_EVIDENCE`.
   - Canonical valid example:
     ```text
     Outcome: O1
     For the user: Workload child task V36-8-LOAD001 materialized and verified on live test PR
     Proof: https://github.com/reallakshman19/relay-v36-stress-lab/pull/10
     TASK_EVIDENCE v3.6
     Task: V36-8-LOAD001
     Child issue: reallakshman19/relay-v36-stress-lab#9
     Candidate: reallakshman19/relay-v36-stress-lab@a8b9c0d1e2f3a8b9c0d1e2f3a8b9c0d1e2f3a8b9
     Tests: 84/84
     ```
2. **Never Imply Owner Acceptance:** Evidence confirms candidate test state; it does not constitute Owner signoff or delivery release.

### 3.2 External Fixture Classification Oracle (Task-Level Evaluation)
`snapshot_v36.py` evaluates status **per task, not per comment**. Each task in the workload under Parent #8 is assigned a specific mutation in the external manifest [`V36-LOAD-FIXTURE-300.yaml`](file:///c:/Users/reall/Documents/antigravity/vibrant-heisenberg/skills/engineering-pr-delivery-v3.6/plans/V36-LOAD-FIXTURE-300.yaml).

> **CRITICAL CONTRACT RULE:** Comments posted to GitHub must NEVER contain inline `FIXTURE:` annotations or extra text. `validate_evidence()` in `lifecycle_v36.py` strictly verifies `text == expected` (canonical 8 lines); any extra lines cause immediate `ContractError` and prematurely mark the task as `INVALID_EVIDENCE`, defeating the test of specific mutations.

| Fixture Category | Subtype / Mutation | Expected Status in `snapshot_v36.py` | Rationale in Source Code |
| :--- | :--- | :---: | :--- |
| **Positive Control** | Valid Candidate & Head | `CURRENT_EVIDENCE` | `candidate[2] == live["head"]["sha"]` |
| **Negative Control** | Stale Candidate SHA | `STALE_EVIDENCE` | `candidate[2] != live["head"]["sha"]` |
| **Negative Control** | Commit URL in Proof | `UNVERIFIED_PROOF` | `proof_pr()` requires `/pull/<N>`, returns `None` |
| **Negative Control** | Mismatched Proof Commit | `UNVERIFIED_PROOF` | `proof[1] is not None and proof[1] != candidate[2]` |
| **Adversarial Control** | Foreign Author Comment | `INVALID_EVIDENCE` | `actor.get("login") != client.repo.split("/")[0]` |
| **Adversarial Control** | Malformed 8-line Format | `INVALID_EVIDENCE` | `validate_evidence(body)` raises `ContractError` |
| **Adversarial Control** | Task/Outcome Mismatch | `INVALID_EVIDENCE` | `(evidence["task_id"], evidence["outcome"]) != declared` |
| **Adversarial Control** | Non-existent PR URL (404) | `PROVIDER_UNAVAILABLE` | GitHub 404 raises `ContractError` in `get_pr()`, caught as `PROVIDER_UNAVAILABLE` |

---

## 4. Staged Execution Plan & Gate Criteria

Execution follows a strict gate-driven sequence:

| Stage | Focus | Primary Workload | Gate Invariant / Exit Check |
| :--- | :--- | :--- | :--- |
| **ST-01** | Foundation & Boundaries | Lab #1, genuine PR, trusted publisher | Clean lab verified; unauthorized write scopes rejected; create initial feature branch & test PR; run tests; install trusted stress-lab publisher on default branch; post child #2 evidence; verify `[V3.6][PARENT][E1/6]` via GET readback. |
| **ST-02** | Progressive Scale & Pacing | Lab #8, 300 child issues | Execute bounded batch strategy ($\le 15$ issues/min) to avoid tripping GitHub secondary rate limits; materialize 300 tasks under parent #8 via `V36-8-PLAN-01.yaml`; record interruptions and timing; assert 0 duplicates and intact parent index. |
| **ST-03** | Evidence & PR Attribution | 600 comments, 20 PRs | Use external fixture manifest [`V36-LOAD-FIXTURE-300.yaml`](file:///c:/Users/reall/Documents/antigravity/vibrant-heisenberg/skills/engineering-pr-delivery-v3.6/plans/V36-LOAD-FIXTURE-300.yaml); verify 100% of task statuses match the classification matrix (`CURRENT_EVIDENCE`, `STALE_EVIDENCE`, `UNVERIFIED_PROOF`, `INVALID_EVIDENCE`, `PROVIDER_UNAVAILABLE`); PR titles accurate. |
| **ST-04** | Concurrency & Event Storms | 1 → 3 → 5 → 8 concurrent workers | All 8 workers settle cleanly; zero race conflicts; replay yields zero changes. |
| **ST-05** | Faults & Real Behavior | API 429/5xx, timeouts | Test real client behavior: `GithubClient` has no native retries and fails closed with `ContractError`; record operational finding `FINDING-ST05-RETRY-01` (not counted as proof of recovery capability); verify external idempotent resumption creates zero duplicates. |
| **ST-06** | Cold Successor & Endurance | Cold agent, BuddyRunner 1a/1b/2 | 100% state reconstructed from GitHub alone; prompt generators run clean; 5 cycles stable. |

---

## 5. Execution Order & CI Investigation Status

* **Plan Preparation:** Complete locally (updated with all remaining execution-contract corrections).
* **GitHub Publication & Approval:** Published on branch `proposal/v36-stress-plan-01` via [PR #355](https://github.com/reallakshman19/Common/pull/355). Owner decisions D-STRESS-01 (`CP-V36-STRESS-01`) and D-STRESS-02 (repo provisioning) pending.
* **CI Investigation (Correction 5):** The failure on PR #355 in `validate-v3-1-foundation` ([Run 38267158083](https://github.com/reallakshman19/Common/actions/runs/38267158083)) has been investigated and documented in [`CI_INVESTIGATION_RUN_38267158083.md`](file:///c:/Users/reall/Documents/antigravity/vibrant-heisenberg/skills/engineering-pr-delivery-v3.6/docs/CI_INVESTIGATION_RUN_38267158083.md). The 7 failures (6 FileNotFoundError for retired v2.5/v3 workflows, 1 AssertionError for diff string) stem from legacy v3.1 test table expectations triggered by matching `relay/*`. No tests have been suppressed or modified.
* **ST-01 Foundation:** **HOLD** (Awaiting Owner approval of label and repository provisioning of `reallakshman19/relay-v36-stress-lab`).
* **ST-02 through ST-06:** **Not started**.
