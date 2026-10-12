# V3.6 Full-Scale Stress Test Plan (V36-STRESS-PLAN-01)

> **Document Status:** PROPOSAL — RECONCILED WITH ALL OWNER CORRECTIONS  
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

### 1.2 Boundary & Authority Rules
1. **GitHub Recoverability:**
   - All artifacts (this specification, sticky label proposal, execution prompt, stage plans, bounded pacing harness, and workload fixtures) are published to GitHub on branch `proposal/v36-stress-plan-01` in `reallakshman19/Common`.
   - Any cold successor agent can recover 100% of the plan, authority definitions, and prompt contracts directly from GitHub without relying on local machine files.
2. **Owner Approval Requirement:**
   - The sticky label `relay/AIM/V36-STRESS.yaml` and the lab directive `Writable lab: reallakshman19/relay-v36-stress-lab` are **proposals**, not pre-approved authority.
   - Execution is held on **HOLD** until the Owner reviews Change Card `CP-V36-STRESS-01`, approves the label, and provisions `reallakshman19/relay-v36-stress-lab`.
3. **Repository Isolation:**
   - All live test writes are strictly confined to the dedicated disposable repository: `reallakshman19/relay-v36-stress-lab`.
   - **ZERO writes or mutations** to `reallakshman19/Common`, `reallakshman19/relay-v36-e2e-lab`, or existing product repositories.
   - Historical evidence from [Common #341](https://github.com/reallakshman19/Common/issues/341) and the accepted v3.6 benchmark remains immutable read-only context.
4. **Execution Safety & Containment:**
   - Pinned v3.6 source only; trusted workflow runs; never execute untrusted PR code with elevated permissions.
   - Every CLI execution must bind explicit arguments: `--label relay/AIM/V36-STRESS.yaml`, `--plan <PLAN_PATH>`, and `--lab reallakshman19/relay-v36-stress-lab`.
   - Write operations require `--apply --confirm-scope reallakshman19/relay-v36-stress-lab#<PARENT>`.

---

## 2. Architecture: Stages vs. Workload & Numbering Reservation

To prevent inflated progress reporting and avoid numbering collisions, the test architecture strictly separates the controlling test stages from the generated workload tasks:

```
+---------------------------------------------------------------------------------+
| Parent Issue #1: Stress Test Orchestrator (Denominator: 6 Stages, Progress: E0/6 to E6/6) |
|   ├── V36-1-ST01: Foundation & Boundaries (Size S, Outcome O1)                   |
|   ├── V36-1-ST02: Progressive Scale & Pagination (Size L, Outcome O1)           |
|   │     └── Subject Load: 300 Workload Tasks (V36-8-LOAD001..300) under Parent #8|
|   ├── V36-1-ST03: Truthful Evidence & PR Attribution (Size L, Outcome O2)       |
|   │     └── Subject Load: 600 Evidence Comments (300 Positive / 300 Adversarial)|
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
- **Exact Denominator:** Strictly **6**. The parent issue title reflects progress in terms of proven test stages (e.g. `[V3.6][LAB][E1/6] ...`).
- A stage is marked evidenced only after its specific acceptance criteria and GO-gate evidence are proven and posted on its dedicated child issue.

### 2.2 The Subject Workload: 300 Workload Tasks under Parent #8
- Workload Plan File: `skills/engineering-pr-delivery-v3.6/plans/V36-8-PLAN-01.yaml` (plan_version `V36-8-PLAN-01`)
- Workload Parent Issue: `reallakshman19/relay-v36-stress-lab#8`
- Workload Fixture Specification: `skills/engineering-pr-delivery-v3.6/plans/V36-LOAD-FIXTURE-300.yaml`
- Task IDs: `V36-8-LOAD001` through `V36-8-LOAD300`.
- **Integration with decompose_v36.py:** `V36-8-PLAN-01.yaml` is a fully compliant input to `decompose_v36.py`, providing a separate real parent (#8) and stable task IDs prefixed with `V36-8-`.
- **Preservation of Denominator:** Parent issue #1 maintains a strictly bounded denominator of **6** (`progress=E0/6` to `E6/6`). Materializing the 300 child tasks under Parent #8 fulfills the acceptance check for **Stage ST-02 (`progress=E2/6`)** on child issue #3 (`V36-1-ST02`).

### 2.3 GitHub Unified Issue/PR Sequence Counter & Reservation of Parent #8
- **Unified Numbering Rule:** GitHub maintains a single sequence counter shared across issues and pull requests.
- **Collision Prevention Sequence:**
  1. Initialize Parent Issue #1 (`reallakshman19/relay-v36-stress-lab#1`).
  2. Decompose stage tasks, creating Child Issues #2 through #7 (`V36-1-ST01` through `V36-1-ST06`).
  3. **RESERVE PARENT #8:** Workload Parent Issue #8 (`reallakshman19/relay-v36-stress-lab#8`) **MUST** be created immediately after child issue #7 *before* opening any Pull Request. Verify via GET that it receives issue sequence number #8.
  4. **OPEN PROOF PR:** Open the ST-01 Proof Pull Request *subsequent* to parent #8. It will consume sequence number **#9** (`reallakshman19/relay-v36-stress-lab/pull/9`).
  5. **BOND EVIDENCE:** All ST-01 evidence records and workload tasks referencing the live Proof PR bind `https://github.com/reallakshman19/relay-v36-stress-lab/pull/9`. This eliminates numbering drift and preserves `V36-8-PLAN-01.yaml`.

---

## 3. Truthful Evidence & Two-Wave Workload Architecture (600 Comments)

Evidence represents factual, reproducible test execution results:

### 3.1 Positive Evidence Rules
1. **Genuinely Verified Test Facts & PR Proof URL:**
   - `snapshot_v36.py` requires a GitHub Pull Request URL (`https://github.com/<owner>/<repo>/pull/<N>`) matching the repository. Commit URLs (e.g. `/commit/<sha>`) are rejected by `proof_pr()` as `UNVERIFIED_PROOF`.
   - The candidate SHA must match the live PR's `head.sha` for the task to be recognized as `CURRENT_EVIDENCE`.
   - Canonical valid example for ST-01:
     ```text
     Outcome: O1
     For the user: Stress lab foundation and boundaries verified with live PR attribution
     Proof: https://github.com/reallakshman19/relay-v36-stress-lab/pull/9
     TASK_EVIDENCE v3.6
     Task: V36-1-ST01
     Child issue: reallakshman19/relay-v36-stress-lab#2
     Candidate: reallakshman19/relay-v36-stress-lab@3f4a8b9c0d1e2f3a8b9c0d1e2f3a8b9c0d1e2f3a
     Tests: 94/94
     ```
2. **Never Imply Owner Acceptance:** Evidence confirms candidate test state; it does not constitute Owner signoff or delivery release.

### 3.2 Full 600-Comment Volume Across Two Measured Waves
`snapshot_v36.py` evaluates status **per task, not per comment**, picking the latest eligible comment (`eligible[-1]`). To evaluate both negative control classifications and verify that invalid comments cannot corrupt valid evidence, 600 comments are staged across two measured waves per [`V36-LOAD-FIXTURE-300.yaml`](../plans/V36-LOAD-FIXTURE-300.yaml):

> **CRITICAL CONTRACT RULE:** Comments posted to GitHub must NEVER contain inline `FIXTURE:` annotations or extra text. `validate_evidence()` in `lifecycle_v36.py` strictly verifies `text == expected` (canonical 8 lines); any extra lines cause immediate `ContractError` and prematurely mark the task as `INVALID_EVIDENCE`. All tracking is maintained externally in `V36-LOAD-FIXTURE-300.yaml`.

#### Wave 1: Baseline Evidence & Control Injection (300 comments)
- **Positive Controls (150 tasks, `LOAD001`..`LOAD150`):** 150 canonical valid comments referencing Proof PR #9 with matching head SHA $\rightarrow$ Expected status: `CURRENT_EVIDENCE` (150).
- **Negative Controls (150 tasks, `LOAD151`..`LOAD300`):**
  - Stale candidate SHA (50 tasks, `LOAD151`..`LOAD200`) $\rightarrow$ Expected status: `STALE_EVIDENCE` (50).
  - Unverified proof (40 tasks, `LOAD201`..`LOAD240`): 20 commit Proof URLs (`/commit/<sha>`) + 20 mismatched PR commit URLs (`/pull/9/commits/<sha1>` where sha1 != candidate sha2) $\rightarrow$ Expected status: `UNVERIFIED_PROOF` (40).
  - Invalid evidence (40 tasks, `LOAD241`..`LOAD280`): 20 foreign comment authors + 20 malformed syntax/outcome mismatches $\rightarrow$ Expected status: `INVALID_EVIDENCE` (40).
  - Non-existent PR URL (20 tasks, `LOAD281`..`LOAD300`): Proof URL references non-existent PR `/pull/99999` (HTTP 404 raises `ContractError` in `get_pr()`) $\rightarrow$ Expected status: `PROVIDER_UNAVAILABLE` (20).
- **Wave 1 Snapshot Oracle:** Exactly 150 `CURRENT_EVIDENCE`, 50 `STALE_EVIDENCE`, 40 `UNVERIFIED_PROOF`, 40 `INVALID_EVIDENCE`, 20 `PROVIDER_UNAVAILABLE`, 0 `verified_complete`.

#### Wave 2: Invariance Verification & Recovery (300 comments)
- **Verification of Non-Overwrite Invariant (150 tasks, `LOAD001`..`LOAD150`):** Post 150 invalid/malformed comments on the tasks that already have valid Wave 1 evidence.
  - *Observed Behavior:* `snapshot_v36.py` discards invalid comments prior to eligible sorting; `eligible[-1]` remains the Wave 1 valid comment.
  - *Key Invariant Verified:* **Invalid comments MUST NOT overwrite or degrade previously valid evidence.**
  - *Expected Status:* All 150 tasks remain `CURRENT_EVIDENCE`.
- **Verification of Recovery / Superseding (150 tasks, `LOAD151`..`LOAD300`):** Post 150 fresh positive comments on `LOAD151`..`LOAD300` referencing PR #9 with matching head SHA.
  - *Observed Behavior:* New valid comments are added to eligible and chronologically supersede prior negative/control states.
  - *Expected Status:* All 150 tasks transition to `CURRENT_EVIDENCE`.
- **Wave 2 Snapshot Oracle:** Exactly 300 `CURRENT_EVIDENCE`, 0 `STALE_EVIDENCE`, 0 `UNVERIFIED_PROOF`, 0 `INVALID_EVIDENCE`, 0 `PROVIDER_UNAVAILABLE`, 0 `verified_complete`.
- **Volume Total:** 300 positive + 300 negative/adversarial = **600 comments**.

---

## 4. Staged Execution Plan & Gate Criteria

Execution follows a strict gate-driven sequence:

| Stage | Focus | Primary Workload | Gate Invariant / Exit Check |
| :--- | :--- | :--- | :--- |
| **ST-01** | Foundation & Boundaries | Lab #1, Parent #8 reserved, Proof PR #9, trusted publisher | Clean lab verified; unauthorized write scopes rejected; create parent #1 and children #2..#7; reserve workload parent #8; create feature branch & test PR #9; run tests; install trusted stress-lab publisher; post child #2 evidence; verify `[V3.6][LAB][E1/6] Full-Scale Stress Test Lifecycle Stage Progression` via GET readback. |
| **ST-02** | Progressive Scale & Bounded Pacing | Lab #8, 300 child issues via `pacing_harness_v36.py` | Execute bounded batch harness `pacing_harness_v36.py` ($\le 15$ issues/min, batches of 15, 4.0s item pause, 60.0s batch pause) to avoid tripping GitHub secondary rate limits; materialize 300 tasks under parent #8 via `V36-8-PLAN-01.yaml`; record interruptions and timing; assert 0 duplicates and intact parent index. |
| **ST-03** | Evidence & PR Attribution | 600 comments, 20 PRs across Two Waves | Execute Wave 1 (300 comments) and Wave 2 (300 comments) per [`V36-LOAD-FIXTURE-300.yaml`](../plans/V36-LOAD-FIXTURE-300.yaml); verify 100% of task statuses match the classification matrix across both waves; confirm invalid comments do not overwrite valid evidence; PR titles accurate. |
| **ST-04** | Concurrency & Event Storms | 1 → 3 → 5 → 8 concurrent workers | All 8 workers settle cleanly; zero race conflicts; replay yields zero changes. |
| **ST-05** | Faults & Real Behavior | API 429/5xx, timeouts | Test real client behavior: `GithubClient` has no native retries and fails closed with `ContractError`; record operational finding `FINDING-ST05-RETRY-01` (not counted as proof of recovery capability); verify external idempotent resumption creates zero duplicates. |
| **ST-06** | Cold Successor & Endurance | Cold agent, BuddyRunner 1a/1b/2 | 100% state reconstructed from GitHub alone; prompt generators run clean; 5 cycles stable. |

---

## 5. Execution Order & CI Investigation Status

* **Plan Preparation:** Complete locally (updated with all remaining execution-contract corrections).
* **GitHub Publication & Approval:** Published on branch `proposal/v36-stress-plan-01` via [PR #355](https://github.com/reallakshman19/Common/pull/355). Owner decisions D-STRESS-01 (`CP-V36-STRESS-01`) and D-STRESS-02 (repo provisioning) pending.
* **CI Investigation:** The failure on PR #355 in `validate-v3-1-foundation` ([Run 38267158083](https://github.com/reallakshman19/Common/actions/runs/38267158083)) has been investigated and documented in [`CI_INVESTIGATION_RUN_38267158083.md`](CI_INVESTIGATION_RUN_38267158083.md). The 7 failures (6 FileNotFoundError for retired v2.5/v3 workflows, 1 AssertionError for diff string) stem from legacy v3.1 test table expectations triggered by matching `relay/*`. No tests have been suppressed or modified.
* **ST-01 Foundation:** **HOLD** (Awaiting Owner approval of label and repository provisioning of `reallakshman19/relay-v36-stress-lab`).
* **ST-02 through ST-06:** **Not started**.
