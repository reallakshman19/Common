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

### 2.2 The Subject Workload: 300 Workload Fixture Tasks
- Plan file: `skills/engineering-pr-delivery-v3.6/plans/V36-LOAD-FIXTURE-300.yaml`
- Task IDs: `V36-LOAD-001` through `V36-LOAD-300`.
- **Purpose:** Subject workload generated during ST-02 and exercised during ST-03/ST-04 to test pagination, REST `Link` header navigation, memory scaling, and race safety.
- **Rule:** Successfully generating and reconciling all 300 workload issues fulfills the acceptance check for **Stage ST-02 (`progress=E2/6`)**. It does NOT change the top-level denominator or create false progress.

---

## 3. Truthful Evidence & Explicit Fixture Markings (Correction 4)

In accordance with the v3.6 contract, evidence represents factual, reproducible test execution results:

### 3.1 Positive Evidence Rules (300 Cases)
1. **Genuinely Verified Test Facts:**
   - Every positive `TASK_EVIDENCE` comment must report actual test results executed against candidate commits on test branches in the stress lab.
   - Example valid record:
     ```text
     Outcome: O1
     For the user: Workload child task V36-LOAD-042 materialized and verified via paginated GitHub REST readback
     Proof: https://github.com/reallakshman19/relay-v36-stress-lab/commit/a8b9c0d1e2f3
     TASK_EVIDENCE v3.6
     Task: V36-LOAD-042
     Child issue: reallakshman19/relay-v36-stress-lab#43
     Candidate: reallakshman19/relay-v36-stress-lab@a8b9c0d1e2f3a8b9c0d1e2f3a8b9c0d1e2f3a8b9
     Tests: 84/84
     ```
2. **Never Imply Owner Acceptance:** Evidence confirms candidate state and test execution; it does not constitute Owner signoff or delivery release.

### 3.2 Negative & Adversarial Fixture Rules (300 Cases)
1. **Explicit Fixture Header:** Every simulated negative or adversarial comment must contain an explicit fixture tag in the body:
   `FIXTURE: NEGATIVE_TEST (Simulated test fixture for ST-03; not real work)` or  
   `FIXTURE: ADVERSARIAL_TEST (Simulated test fixture for ST-03; not real work)`.
2. **Verification Oracle:**
   - `snapshot_v36.py` must reliably flag stale candidate SHAs, mismatched Proof URLs, missing required headers, and foreign comment authors as `STALE` or `INVALID`.
   - Title publisher must reflect `[STALE]` or `[PENDING]` without corrupting issue state or granting false progress.

---

## 4. Staged Execution Plan & Gate Criteria

Execution follows a strict gate-driven sequence:

| Stage | Focus | Primary Workload | Gate Invariant / Exit Check |
| :--- | :--- | :--- | :--- |
| **ST-01** | Foundation & Boundaries | Lab #1, label & plan validation | Clean lab verified; unauthorized write scopes rejected; dry-run matches target plan. |
| **ST-02** | Progressive Scale | 20 → 100/101 → 125 → 300 child issues | 300 workload issues materialized; 0 duplicate issues; parent index intact; pagination verified. |
| **ST-03** | Evidence & PR Attribution | 600 comments, 20 PRs | 100% positive comments verified; 100% negative/adversarial fixtures rejected; PR titles accurate. |
| **ST-04** | Concurrency & Event Storms | 1 → 3 → 5 → 8 concurrent workers | All 8 workers settle cleanly; zero race conflicts; replay yields zero changes. |
| **ST-05** | Faults & Recovery | API 429/5xx, timeouts, dropped ACKs | Exponential backoff verified; transaction resumed without duplicates; state reconciled. |
| **ST-06** | Cold Successor & Endurance | Cold agent, BuddyRunner 1a/1b/2 | 100% state reconstructed from GitHub alone; prompt generators run clean; 5 cycles stable. |

---

## 5. Execution Order & Current Status

* **Plan Preparation:** Complete locally (updated with all 4 corrections).
* **GitHub Publication & Approval:** In Progress (published to `proposal/v36-stress-plan-01` on `reallakshman19/Common`; Change Card `CP-V36-STRESS-01` pending Owner approval).
* **ST-01 Foundation:** **HOLD** (Awaiting Owner approval of label and repository provisioning of `reallakshman19/relay-v36-stress-lab`).
* **ST-02 through ST-06:** **Not started**.
