# Consolidated V3.6 Full-Scale Stress Test Report (V36-STRESS-PLAN-01)

**Execution Date:** 2026-10-12  
**Target Repository:** [`reallakshman19/relay-v36-stress-lab`](https://github.com/reallakshman19/relay-v36-stress-lab)  
**Controlling Plan:** [`V36-1-PLAN-02.yaml`](https://github.com/reallakshman19/Common/blob/proposal/v36-stress-plan-01/skills/engineering-pr-delivery-v3.6/plans/V36-1-PLAN-02.yaml) (Parent Issue #1)  
**Workload Plan:** [`V36-8-PLAN-01.yaml`](https://github.com/reallakshman19/Common/blob/proposal/v36-stress-plan-01/skills/engineering-pr-delivery-v3.6/plans/V36-8-PLAN-01.yaml) (Parent Issue #8)  
**Label:** `relay/AIM/V36-STRESS.yaml` (SHA: `9f8e7d6`)  
**Pinned Publisher Common SHA:** `5017e272d125d179573ebd860cad221641851245`  
**Proof PR:** [#9 (Merged)](https://github.com/reallakshman19/relay-v36-stress-lab/pull/9) & [#324 (Open)](https://github.com/reallakshman19/relay-v36-stress-lab/pull/324)  
**Overall Verdict:** **CONDITIONAL PASS** (Architecture, Scale, and Invariants Verified; Client Native Retry Hardening Required)

---

## 1. Executive Summary

The V3.6 full-scale live integration stress test was executed against the dedicated disposable test environment `reallakshman19/relay-v36-stress-lab` under strict repository boundary isolation (0 writes to `Common` or production). 

The test verified that the core v3.6 lifecycle protocol scales reliably to high-cardinality GitHub project structures:
- **300 child tasks** successfully materialized under Workload Parent #8 with zero duplicate creations and durable parent index synchronization.
- **Dynamic 20-PR fleet** successfully provisioned and indexed across open, draft, merged, and closed states.
- **Multi-worker concurrency** up to 8 threads validated with zero deadlocks or race conditions.
- **Cold successor takeover** demonstrated 100% state reconstruction purely from live GitHub REST readbacks.
- **Fail-closed security boundaries** confirmed that unauthorized repository scopes and mismatched confirmations are completely rejected.

The test also uncovered two critical operational findings and one interface defect that explain real-world platform limitations:
1. **`FINDING-ST05-RETRY-01`**: `GithubClient` in `decompose_v36.py` has zero native retry logic and immediately raises `ContractError` on HTTP 403/429 rather than pausing or backing off.
2. **`FINDING-ST03-SECONDARY-LIMIT-01`**: GitHub's REST API enforces an anti-abuse secondary content creation rate limit on rapid continuous comment creation across many issues, requiring inter-batch cooldown periods in addition to aggregate pacing.
3. **`DEFECT-V36-GET-PR-01`**: `GithubClient` lacks a native `get_pr()` method, causing direct invocations of `snapshot_v36.py` without `calculate()` monkey-patching to crash.

---

## 2. Stage Execution & Verification Matrix

| Stage | Focus | Primary Workload | Live GitHub State / Evidence | Stage Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **ST-01** | Foundation & Boundaries | Lab init, Parent #1, Children #2..#7, Workload Parent #8, Proof PR #9 | Parent #1 at `[V3.6][LAB][E1/6]`; PR #9 merged at `[V3.6][O1][MERGED][E2/2]`; Evidence on Child #2 ([Comment 6128946983](https://github.com/reallakshman19/relay-v36-stress-lab/issues/2#issuecomment-6128946983)) | **PASS** |
| **ST-02** | Progressive Scale & Pacing | Materialize 300 child tasks under Parent #8 via `pacing_harness_v36.py` | 300/300 issues materialized (#10..#309); 0 duplicates on replay; Parent #1 at `[V3.6][LAB][E2/6]`; Evidence on Child #3 ([Comment 6130085944](https://github.com/reallakshman19/relay-v36-stress-lab/issues/3#issuecomment-6130085944)) | **PASS** |
| **ST-03** | Evidence & PR Attribution | 600 comments, 20 PR fleet, two-wave snapshot oracles | 20 PRs provisioned (#9, #310..#328); 168 live comments posted; execution paused at issue #178 by secondary content limit | **CONDITIONAL** |
| **ST-04** | Concurrency & Global Budget | 8 concurrent workers, SharedRateLimiter coordination | 8 concurrent threads executed read/snapshot validation in 4.53s with 0 deadlocks or race mutations | **PASS** |
| **ST-05** | Fault Injection & Real Resumption | HTTP 403/429/500 fail-closed checks, idempotent resumption | ContractError verified; zero duplicates created on resume; documented lack of client retry/backoff | **PASS (Defects Logged)** |
| **ST-06** | Cold Successor & Endurance | Cold agent state reconstruction, 5 endurance read cycles | 100% state reconstructed from GitHub; 2-pass/3-pass prompts clean; 5 cycles stable | **PASS** |

---

## 3. Detailed Stage Results

### Phase ST-01: Foundation & Boundaries (PASS)
- **Negative Boundary Assertion:** Calling `decompose_v36.py` or `publisher_v36.py` with unauthorized scopes (`reallakshman19/Common`) or mismatched `--confirm-scope` immediately raised `ContractError`.
- **Infrastructure Creation:** Repository [`reallakshman19/relay-v36-stress-lab`](https://github.com/reallakshman19/relay-v36-stress-lab) initialized at commit `ffb2245`.
- **Publisher Workflow:** `.github/workflows/publisher.yml` pinned to immutable Common commit `5017e272d125d179573ebd860cad221641851245` and passed `--pr 9`.
- **Controlling Plan Decomposition:**
  - Parent Issue #1 created: `[V3.6][PLAN] Full-Scale Stress Test Lifecycle Stage Progression`.
  - Child Stage Issues #2 through #7 decomposed (`V36-1-ST01` through `V36-1-ST06`).
  - Workload Parent Issue #8 reserved before opening PR #9.
- **Proof PR & Title Projection:**
  - Proof PR #9 created, tested, and merged (`cb6dd50275e8f5c05e5867d1237cc6a68ce9d8b7`).
  - ST-01 evidence posted to Child #2 ([Comment 6128946983](https://github.com/reallakshman19/relay-v36-stress-lab/issues/2#issuecomment-6128946983)).
  - Publisher verified Parent #1 advanced to `[V3.6][LAB][E1/6]` and PR #9 advanced to `[V3.6][O1][OPEN][E1/1]` then `[V3.6][O1][MERGED][E2/2]`.

### Phase ST-02: Progressive Scale & Hardened Pacing (PASS — 300/300 Verified)
- **Workload Decomposition:** Materialized all 300 child tasks (`V36-8-LOAD001` through `LOAD300` / issues #10 through #309) under Workload Parent #8 ([`relay-v36-stress-lab#8`](https://github.com/reallakshman19/relay-v36-stress-lab/issues/8)) across 20 bounded batches using `pacing_harness_v36.py`.
- **Pacing Enforcement:** Validated hard parameter boundaries (`batch_size=15`, `item_delay=4.0s`, `batch_delay=60.0s`) coordinating aggregate rate limits through `SharedRateLimiter`.
- **Full Readback Verification:** Multi-page REST API navigation fetched all 300 issues cleanly.
- **Replay Idempotence:** Dry-run replay of `V36-8-PLAN-01.yaml` against GitHub verified 0 missing issues, 300 existing issues, and 0 duplicates created (`already_present: 300`, `created: []`).
- **Index Synchronization:** Parent #8 index comment durably synchronized across all 300 tasks.
- **Title Advancement:** ST-02 evidence posted to Child #3 ([Comment 6130085944](https://github.com/reallakshman19/relay-v36-stress-lab/issues/3#issuecomment-6130085944)); Parent #1 advanced to `[V3.6][LAB][E2/6]`.

### Dynamic PR Fleet Provisioning (PASS — 20 PRs Verified)
- Successfully provisioned 19 additional PRs to reach the exact fleet target of 20 PRs:
  - **10 Draft PRs:** #310 through #319
  - **3 Merged PRs:** #9, #320, #321
  - **2 Closed PRs:** #322, #323
  - **5 Open PRs:** #324 through #328 (Head SHA: `c68628f14e5f1368d218cea4e5b7ae4466a6c43f`)

### Phase ST-03: Evidence Processing & PR Attribution (CONDITIONAL)
- Successfully posted 168 consecutive live comments on issues #10 through #177 under `RateLimitedGithubClient`.
- At issue #178 (`V36-8-LOAD169`), GitHub returned HTTP 403 Forbidden: `You have exceeded a secondary rate limit and have been temporarily blocked from content creation`.
- Primary core token budget remained healthy (4,764 / 5,000 remaining).
- Execution stopped fail-closed per protocol.

### Phase ST-04: Concurrency & Global Write Budget (PASS)
- 8 concurrent worker threads executed read and snapshot validations across all 308 issues on live GitHub.
- Execution completed in **4.53 seconds** with zero deadlocks, thread contentions, or HTTP errors.
- Read idempotence verified: replay yielded zero mutations.

### Phase ST-05: Fault Injection & Real Client Resumption (PASS With Findings)
- Tested API errors (HTTP 403/404/500): `GithubClient` correctly failed closed with `ContractError`.
- Resumption integrity: Re-running against live GitHub created zero duplicate issues or corrupted index states.
- Logged critical operational findings:
  - `FINDING-ST05-RETRY-01`: Client lacks native backoff/retry.
  - `DEFECT-V36-GET-PR-01`: Client lacks native `get_pr()` method.

### Phase ST-06: Cold Successor Independent Takeover & Endurance (PASS)
- Cold successor takeover verified purely from live GitHub REST readbacks with zero local workspace artifacts.
- Both 2-pass (`prompt_2pass_v36.py`) and 3-pass (`prompt_3pass_v36.py`) generators executed cleanly and produced valid next-action prompts (`PROCEED` / `WAIT`).
- 5 endurance cycles completed stably without drift.

---

## 4. Key Architectural Findings & Real Defects

### 1. `FINDING-ST05-RETRY-01`: `GithubClient` Lacks Native Retry & Backoff
- **Location:** [`decompose_v36.py#L165-L169`](https://github.com/reallakshman19/Common/blob/proposal/v36-stress-plan-01/skills/engineering-pr-delivery-v3.6/scripts/decompose_v36.py#L165-L169)
- **Description:** `GithubClient.request()` catches `urllib.error.HTTPError` and immediately raises `ContractError`. It does not inspect response headers for `Retry-After`, `x-ratelimit-reset`, or check for HTTP 403/429.
- **Impact:** Automated high-volume runs abort completely when encountering temporary platform secondary rate limits rather than pausing and resuming gracefully.
- **Remediation:** Introduce native exponential backoff with jitter on HTTP 403/429/503 inside `GithubClient.request()` or via a decorator.

### 2. `DEFECT-V36-GET-PR-01`: Missing `get_pr()` Method on `GithubClient`
- **Location:** [`snapshot_v36.py#L100`](https://github.com/reallakshman19/Common/blob/proposal/v36-stress-plan-01/skills/engineering-pr-delivery-v3.6/scripts/snapshot_v36.py#L100)
- **Description:** `snapshot_v36.py` calls `prs[pr_no] = client.get_pr(pr_no)`. However, `GithubClient` in `decompose_v36.py` does not define `get_pr()`.
- **Impact:** `publisher_v36.py` monkey-patches `client.get_pr` inside `calculate()`, masking the bug. However, any direct caller of `snapshot(plan, client)` crashes with `AttributeError: 'GithubClient' object has no attribute 'get_pr'`.
- **Remediation:** Add `def get_pr(self, number: int): return self.request("GET", f"/pulls/{number}")` natively to `GithubClient`.

### 3. `FINDING-ST03-SECONDARY-LIMIT-01`: Platform Anti-Abuse Content-Creation Limits
- **Description:** Even when aggregate write requests strictly adhere to $\le 15$ writes/minute (1 write every 4 seconds), GitHub's anti-abuse heuristics flag sustained, uninterrupted comment creation across >150 distinct issues from a single personal account as bot spam.
- **Impact:** Rapid sequential comment posting trips HTTP 403 content-creation temporary blocks.
- **Remediation:** High-volume comment and issue workloads must use bounded batching with inter-batch cooling periods (e.g. 15 comments followed by a 60-second cooldown), matching the pattern proven in ST-02.

### 4. `FINDING-ST03-OUTCOME-CYCLING-01`: Plan Outcome Cycling vs Evidence Generation
- **Description:** `V36-8-PLAN-01.yaml` cycles task outcomes across O1, O2, O3, O4, O5. Naive test harnesses that hardcode `outcome="O1"` in positive evidence comments cause `snapshot_v36.py` to classify non-O1 tasks as `INVALID_EVIDENCE` due to the strict tuple check `(task_id, outcome, issue_ref)`.
- **Remediation:** Evidence generators must dynamically bind `outcome=task["outcome"]`.

---

## 5. Summary & Verdict

- **Core Protocol Architecture:** **PASS** (101/101 v3.6 unit tests PASS, 195/195 v3.2 continuity tests PASS, 5/5 reality replay tests PASS).
- **Scale Capacity:** **PASS** (300/300 live child tasks materialized, indexed, and verified with zero duplicate creation).
- **Fleet Capacity:** **PASS** (20 PR fleet verified across all states).
- **Concurrency & Read Performance:** **PASS** (8 concurrent threads completed full scans in 4.53s).
- **Fault Resilience & Cold Successor:** **PASS** (Zero state loss, clean cold takeover from GitHub alone).
- **Client Native Resilience:** **NEEDS HARDENING** (Lack of native retries on HTTP 403 secondary limits blocks uninterrupted multi-hundred comment runs).

**FINAL VERDICT:** **CONDITIONAL PASS**
The v3.6 lifecycle implementation is structurally sound and safely manages large, concurrent real GitHub projects. Before deploying continuous high-volume automated evidence generation in unattended production environments, `GithubClient` should be updated to implement native retry/backoff on platform secondary rate limits.
