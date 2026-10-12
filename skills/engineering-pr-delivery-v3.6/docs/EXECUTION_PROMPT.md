# Turnkey Local Agent Execution Prompt: V3.6 Full-Scale Stress Test (ST-01 through ST-06)

> **Mandatory Pre-Flight Instruction:**  
> **CURRENT STATUS: ST-01 IS ON HOLD.**  
> Do NOT execute any write operations against `reallakshman19/relay-v36-stress-lab` until:  
> 1. The Owner approves Change Proposal Card `CP-V36-STRESS-01` for `relay/AIM/V36-STRESS.yaml`.  
> 2. The Owner creates and provisions the dedicated disposable repository `reallakshman19/relay-v36-stress-lab`.  
> Once Owner approval and repository access are confirmed, execute **ST-01 ONLY** and publish its gate evidence before progressing to ST-02.  
> **Under NO circumstances may you write to or modify `reallakshman19/Common`, `reallakshman19/relay-v36-e2e-lab`, or existing product repositories.**

---

## 1. Governance & Boundary Parameters

* **Baseline Source:** Pinned `skills/engineering-pr-delivery-v3.6` from `Common/main` (`bd8ee38`)
* **Governing Label Proposal:** `relay/AIM/V36-STRESS.yaml` (v1.0.0-draft, `engineering_critical=critical`)
* **Controlling Plan (Stages):** `skills/engineering-pr-delivery-v3.6/plans/V36-1-PLAN-02.yaml` (plan_version `V36-1-PLAN-02`)
  - Parent issue: `reallakshman19/relay-v36-stress-lab#1`
  - Controlling denominator: **6** (`E0/6` to `E6/6`, corresponding to stages `V36-1-ST01` through `V36-1-ST06`)
* **Subject Workload Plan:** `skills/engineering-pr-delivery-v3.6/plans/V36-8-PLAN-01.yaml` (Parent #8, 300 tasks `V36-8-LOAD001` through `V36-8-LOAD300`)
* **Workload Fixture Classification Map:** `skills/engineering-pr-delivery-v3.6/plans/V36-LOAD-FIXTURE-300.yaml`
* **Hardened Bounded Pacing Harness & Shared Rate Limiter:** `skills/engineering-pr-delivery-v3.6/scripts/pacing_harness_v36.py`
* **Authorized Target Lab:** `reallakshman19/relay-v36-stress-lab` (disposable lab)
* **Required CLI Arguments:**
  - Read: `--label relay/AIM/V36-STRESS.yaml --plan <PLAN_PATH> --lab reallakshman19/relay-v36-stress-lab`
  - Write: `--apply --confirm-scope reallakshman19/relay-v36-stress-lab#<PARENT_NUM>`
* **Enforced Rate-Limit Pacing Rules:**
  - Hard parameter limits: `batch-size <= 15`, `item-delay >= 4.0s`, `batch-delay >= 60.0s`.
  - Global write budget: $\le 15$ writes per 60 seconds aggregate across all workers via `SharedRateLimiter` (`.v36_rate_limiter.json`).
  - On HTTP 429 / HTTP 403 `retry-after`: sleep requested seconds + 2s jitter.
  - Maximum concurrent Actions workflow runs: 3.

---

## 2. Sequential Phase Instructions & Gate Protocol

### Phase ST-01: Foundation & Boundaries (HOLD until Owner Approval)
1. **Verification & Authorization Pre-flight:**
   - Confirm Owner approval of `CP-V36-STRESS-01` and verify that `reallakshman19/relay-v36-stress-lab` is created and accessible (no longer 404).
   - Verify local authenticated git/gh access.
2. **Contract & Negative Boundary Check:**
   - Run `python skills/engineering-pr-delivery-v3.6/scripts/lifecycle_v36.py validate-label relay/AIM/V36-STRESS.yaml`. Must PASS.
   - Run negative test attempting `--lab reallakshman19/Common`. Assert immediate `ContractError`.
   - Run negative test with mismatched `--confirm-scope`. Assert immediate `ContractError`.
3. **Parent Issue Initialization:**
   - Create parent issue #1 on `reallakshman19/relay-v36-stress-lab` with title:  
     `[V3.6][PLAN] Full-Scale Stress Test Lifecycle Stage Progression`
   - Run dry-run decomposition:  
     `python skills/engineering-pr-delivery-v3.6/scripts/decompose_v36.py --label relay/AIM/V36-STRESS.yaml --plan skills/engineering-pr-delivery-v3.6/plans/V36-1-PLAN-02.yaml --lab reallakshman19/relay-v36-stress-lab`
   - Verify output predicts required child issues #2 through #7 without mutations.
4. **Apply ST-01 & Parent #8 Reservation Sequence:**
   - Execute decomposition with `--apply --confirm-scope reallakshman19/relay-v36-stress-lab#1`.
   - This creates child issues #2 through #7 (`V36-1-ST01` through `V36-1-ST06`).
   - **CRITICAL NUMBERING RESERVATION:** GitHub shares a single counter across issues and PRs. Immediately create workload Parent Issue #8 *before* opening any PR:  
     `gh issue create --repo reallakshman19/relay-v36-stress-lab --title "[V3.6][PLAN] Subject Workload 300-Task Decomposition Benchmark" --body "Parent issue #8 for V36-8-PLAN-01.yaml 300-task decomposition benchmark"`
   - Verify via GET that Parent #8 is confirmed as issue #8.
5. **Proof PR Establishment (#9):**
   - Create initial feature branch `test/st01-foundation-probe` and open test PR. Since issue #8 was reserved, this PR receives number **#9** (`https://github.com/reallakshman19/relay-v36-stress-lab/pull/9`).
   - Execute candidate test suite (e.g. `Tests: 99/99`) on the PR head.
   - Install trusted stress-lab publisher workflow on the default branch (`.github/workflows/publisher.yml`) using pinned v3.6 source.
   - Post genuine canonical 8-line `TASK_EVIDENCE v3.6` on child issue #2 (`V36-1-ST01`) linking to PR #9 and matching live candidate SHA.
   - Run publisher to update parent title:  
     `python skills/engineering-pr-delivery-v3.6/scripts/publisher_v36.py --label relay/AIM/V36-STRESS.yaml --plan skills/engineering-pr-delivery-v3.6/plans/V36-1-PLAN-02.yaml --lab reallakshman19/relay-v36-stress-lab --apply --confirm-scope reallakshman19/relay-v36-stress-lab#1`
   - Verify via fresh GET readback that Parent #1 title updates to:  
     `[V3.6][LAB][E1/6] Full-Scale Stress Test Lifecycle Stage Progression`  
     (Assert exact `[V3.6][LAB][E1/6]` prefix generated by `publisher_v36.py` and preserved suffix).
   - Verify child issue #2 title: `[V3.6][O1][EVIDENCED] V36-1-ST01 — stress lab foundation boundary and authorization gates`.
   - Verify PR #9 title: `[V3.6][O1][OPEN][E1/1] Stress Test Proof Harness and Lab Configuration`.
   - **Publish ST-01 gate evidence before progressing to ST-02.**
   - **Gate ST-01 Evaluation:**
     - [ ] Clean isolation verified?
     - [ ] Negative authorization tests fail closed?
     - [ ] Parent index initialized with 6 stage tasks?
     - [ ] Workload Parent #8 reserved before PR creation?
     - [ ] Real PR #9 created and live candidate SHA matched?
     - [ ] Trusted publisher installed and parent title transitioned to `[V3.6][LAB][E1/6]`?
     - **Verdict:** If all YES → **GO to ST-02**. Else → **STOP**.

---

### Phase ST-02: Progressive Scale (300 Workload Issues under Parent #8)
1. **Workload Parent Verification:**
   - Confirm Parent Issue #8 is present and verified on `reallakshman19/relay-v36-stress-lab#8`.
2. **Hardened Workload Decomposition (Pacing & Limiter Enforcement):**
   - *Baseline Observation:* Native unpaced `decompose_v36.py` is documented as a baseline constraint.
   - *Enforced Execution Strategy:* Execute decomposition using the hardened pacing harness `pacing_harness_v36.py`:
     ```bash
     python skills/engineering-pr-delivery-v3.6/scripts/pacing_harness_v36.py \
       --label relay/AIM/V36-STRESS.yaml \
       --plan skills/engineering-pr-delivery-v3.6/plans/V36-8-PLAN-01.yaml \
       --lab reallakshman19/relay-v36-stress-lab \
       --apply --confirm-scope reallakshman19/relay-v36-stress-lab#8 \
       --batch-size 15 --item-delay 4.0 --batch-delay 60.0 \
       --rate-limit-file .v36_rate_limiter.json
     ```
   - Parameters are validated fail-closed (`batch_size <= 15`, `item_delay >= 4.0s`, `batch_delay >= 60.0s`).
   - The harness durably synchronizes the managed index comment on Parent #8 after every batch.
   - Observe, log, and measure rate-limit responses, API latencies, and memory consumption.
3. **Pagination & Index Verification:**
   - Execute multi-page REST GET to verify all 300 workload issues exist.
   - Run second decomposition pass. Assert: **0 duplicate issues created**.
   - Profile memory usage (RAM MB) and duration across the 300 items.
4. **Stage Progression:**
   - Once all 300 workload tasks are verified, post genuine task evidence on child issue #3 (`V36-1-ST02`) linking to PR #9.
   - Run publisher to advance controlling Parent #1 title to:  
     `[V3.6][LAB][E2/6] Full-Scale Stress Test Lifecycle Stage Progression`.
5. **Gate ST-02 Evaluation:**
   - [ ] Exactly 300 workload issues created under Parent #8 and verified?
   - [ ] REST API pagination correctly navigated via `Link` header?
   - [ ] Replay creates 0 duplicate tasks?
   - [ ] Hardened pacing respected without unhandled 403 secondary limit lockout?
   - [ ] Top-level progress correctly advances to `[V3.6][LAB][E2/6]` on child #3 (`V36-1-ST02`)?
   - **Verdict:** If all YES → **GO to ST-03**. Else → **STOP**.

---

### Phase ST-03: Evidence Processing & PR Attribution (600 Comments across Two Waves)
1. **PR Lifecycle Initialization:**
   - Create 20 branches and open 20 PRs on the stress lab (IDs #10 through #29).
   - Distribute states: 10 Draft, 5 Ready, 3 Merged, 2 Closed.
2. **Evidence Staging via External Fixture Manifest ([`V36-LOAD-FIXTURE-300.yaml`](../plans/V36-LOAD-FIXTURE-300.yaml)):**
   - *Oracle Architecture:* `snapshot_v36.py` evaluates status **per task, not per comment**, selecting `eligible[-1]`.
   - *Rule on Comment Bodies:* Do **NOT** append `FIXTURE:` or extra text to comments on GitHub. `validate_evidence()` strictly checks `text == expected` (canonical 8 lines); any extra lines cause `ContractError` and prematurely mark the task as `INVALID_EVIDENCE`.
3. **Wave 1 Execution (300 comments):**
   - Post 150 positive canonical 8-line comments on `V36-8-LOAD001`..`LOAD150` referencing PR #9 with matching candidate SHA.
   - Post 150 control comments on `V36-8-LOAD151`..`LOAD300`:
     - 50 tasks with stale candidate SHAs (`LOAD151`..`LOAD200`).
     - 40 tasks with unverified proofs (`LOAD201`..`LOAD240`: 20 commit URLs, 20 mismatched commit SHAs).
     - **Foreign Author Cases (20 tasks, `LOAD241`..`LOAD260`):** Check for `GITHUB_TOKEN_2`. If configured, post live foreign comments with token 2. If absent, execute as **SIMULATED_CONTROL** in test fixtures and report telemetry as simulated; never claim live multi-user verification without a second account.
     - 20 tasks with live malformed syntax/outcome mismatches (`LOAD261`..`LOAD280`).
     - 20 tasks with non-existent PR URLs (`LOAD281`..`LOAD300`: `/pull/99999` returning 404).
   - Run `snapshot_v36.py`. Assert Wave 1 Oracle:
     - `CURRENT_EVIDENCE`: 150
     - `STALE_EVIDENCE`: 50
     - `UNVERIFIED_PROOF`: 40
     - `INVALID_EVIDENCE`: 40 (20 simulated, 20 live)
     - `PROVIDER_UNAVAILABLE`: 20
     - `verified_complete`: 0
4. **Wave 2 Execution (300 comments):**
   - **Test Non-Overwrite Invariant:** Post 150 invalid/malformed comments on `V36-8-LOAD001`..`LOAD150`.
     - *Verified Oracle Behavior:* `snapshot_v36.py` discards invalid comments before eligible sort; `eligible[-1]` remains the Wave 1 valid comment. Status for all 150 tasks **remains `CURRENT_EVIDENCE`**.
     - **Security Invariant Verified: Invalid comments MUST NOT overwrite or degrade previously valid evidence.**
   - **Test Recovery / Superseding:** Post 150 fresh positive comments on `V36-8-LOAD151`..`LOAD300` referencing PR #9 with matching candidate SHA.
     - *Verified Oracle Behavior:* New valid comments are added to eligible and chronologically supersede prior negative states. Status for all 150 tasks **transitions to `CURRENT_EVIDENCE`**.
   - Run `snapshot_v36.py`. Assert Wave 2 Oracle:
     - `CURRENT_EVIDENCE`: 300
     - `STALE_EVIDENCE`: 0
     - `UNVERIFIED_PROOF`: 0
     - `INVALID_EVIDENCE`: 0
     - `PROVIDER_UNAVAILABLE`: 0
     - `verified_complete`: 0
   - Volume Verified: 300 positive + 300 negative/adversarial = **600 comments**.
5. **Publisher Verification & Stage Progression:**
   - Run `publisher_v36.py --apply --confirm-scope reallakshman19/relay-v36-stress-lab#8`.
   - Verify issue titles reflect `[EVIDENCED]` for all 300 tasks.
   - Verify PR titles reflect accurate outcome attribution (e.g. `[V3.6][O1/O2][DRAFT][E15/15] ...`).
   - Post stage evidence on child issue #4 (`V36-1-ST03`) linking to PR #9.
   - Run publisher to advance controlling Parent #1 title to:  
     `[V3.6][LAB][E3/6] Full-Scale Stress Test Lifecycle Stage Progression`.
6. **Gate ST-03 Evaluation:**
   - [ ] 0 false or adversarial evidence accepted?
   - [ ] All 300 tasks match their expected external oracle state across both waves?
   - [ ] Invalid comments confirmed NOT to overwrite previously valid evidence?
   - [ ] Foreign-author verification truthfully labeled (live if token 2 present, simulated otherwise)?
   - [ ] Progress advances to `[V3.6][LAB][E3/6]` on child #4 (`V36-1-ST03`)?
   - **Verdict:** If all YES → **GO to ST-04**. Else → **STOP**.

---

### Phase ST-04: Concurrency & Event Storms (1 → 8 Workers with Shared Rate Limiter)
1. **Multi-Worker Execution:**
   - Spawn parallel worker processes (1 → 3 → 5 → 8 workers).
   - All workers bind `--rate-limit-file .v36_rate_limiter.json` via `SharedRateLimiter`.
   - Aggregate write rate across all concurrent workers is strictly capped at $\le 15$ writes per 60.0s window.
   - Workers execute concurrent reads, decomposition checks, and publisher updates.
2. **Convergence & Idempotence:**
   - Allow worker queues to drain.
   - Run single-threaded publisher pass.
   - Assert: **0 proposed title mutations, 0 index corruptions, 0 title thrashing**.
3. **Stage Progression:**
   - Post stage evidence on child issue #5 (`V36-1-ST04`) linking to PR #9.
   - Run publisher to advance controlling Parent #1 title to:  
     `[V3.6][LAB][E4/6] Full-Scale Stress Test Lifecycle Stage Progression`.
4. **Gate ST-04 Evaluation:**
   - [ ] 8 concurrent workers complete without deadlock?
   - [ ] SharedRateLimiter bounds aggregate writes <= 15 writes/min across all 8 workers?
   - [ ] Settled replay produces exactly 0 mutations?
   - [ ] Progress advances to `[V3.6][LAB][E4/6]` on child #5 (`V36-1-ST04`)?
   - **Verdict:** If all YES → **GO to ST-05**. Else → **STOP**.

---

### Phase ST-05: Fault Injection & Real Behavior Verification
1. **Real Behavior Testing (Operational Finding):**
   - Inject simulated HTTP 429 rate limit and HTTP 503 error.
   - Observe real behavior: `GithubClient` in `decompose_v36.py` has no native retry/backoff logic and immediately raises `ContractError`.
   - Record finding in final report: `FINDING-ST05-RETRY-01: GithubClient lacks native exponential backoff/retry; fails closed with ContractError on transient 429/5xx`.
   - **Important:** Missing retry is an operational limitation/finding; it must NOT be counted as proof of recovery capability. Do NOT quietly add retries in the test harness.
2. **External Idempotent Resumption:**
   - Trigger process interruption mid-transaction.
   - Re-run reconciler/decomposition from fresh external process.
   - Verify: External retry reads true GitHub state, safely resumes, and produces **0 duplicate entities**.
3. **Stage Progression:**
   - Post stage evidence on child issue #6 (`V36-1-ST05`) linking to PR #9.
   - Run publisher to advance controlling Parent #1 title to:  
     `[V3.6][LAB][E5/6] Full-Scale Stress Test Lifecycle Stage Progression`.
4. **Gate ST-05 Evaluation:**
   - [ ] Real fail-closed behavior on transient errors observed and recorded as finding?
   - [ ] Interrupted transaction resumes externally without data loss or duplicates?
   - [ ] Progress advances to `[V3.6][LAB][E5/6]` on child #6 (`V36-1-ST05`)?
   - **Verdict:** If all YES → **GO to ST-06**. Else → **STOP**.

---

### Phase ST-06: Cold Successor & Endurance
1. **Clean-Room Successor Run:**
   - Spawn a cold agent process with zero conversation history.
   - Input only GitHub issue URL and label path.
   - Execute BuddyRunner v1.6: 1a HOLD → 1b independent reconstruction → 2 reconciliation.
2. **Generators & Endurance:**
   - Execute `prompt_2pass_v36.py` and `prompt_3pass_v36.py`. Verify clean outputs.
   - Run 5 consecutive evaluation cycles, profiling memory and latency.
3. **Stage Progression:**
   - Post stage evidence on child issue #7 (`V36-1-ST06`) linking to PR #9.
   - Run publisher to advance controlling Parent #1 title to:  
     `[V3.6][LAB][E6/6] Full-Scale Stress Test Lifecycle Stage Progression`.
4. **Gate ST-06 Evaluation:**
   - [ ] Cold successor reconstructs 100% of state from GitHub alone?
   - [ ] Memory remains flat across 5 endurance cycles?
   - [ ] Progress advances to `[V3.6][LAB][E6/6]` on child #7 (`V36-1-ST06`)?
   - **Verdict:** If all YES → **PASS STRESS TEST**. Else → **FAIL**.

---

## 3. Reporting & Deliverables

1. `STRESS_TEST_REPORT.md`: Comprehensive narrative covering timeline, worker scaling, latencies, and gate evidence.
2. `stress_results.json`: Machine-readable results and metrics.
3. Terminal Agent LOG Line footer.
