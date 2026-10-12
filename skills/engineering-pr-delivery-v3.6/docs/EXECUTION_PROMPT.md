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
* **Workload Fixture Plan:** `skills/engineering-pr-delivery-v3.6/plans/V36-LOAD-FIXTURE-300.yaml` (300 tasks `V36-LOAD-001` through `V36-LOAD-300`)
* **Authorized Target Lab:** `reallakshman19/relay-v36-stress-lab` (disposable lab)
* **Required CLI Arguments:**
  - Read: `--label relay/AIM/V36-STRESS.yaml --plan <PLAN_PATH> --lab reallakshman19/relay-v36-stress-lab`
  - Write: `--apply --confirm-scope reallakshman19/relay-v36-stress-lab#1`
* **Rate-Limit Pacing Rules:**
  - $\le 1$ write per second per worker.
  - $\le 15$ issue/comment creations per minute total.
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
     `[V3.6][PARENT][PLANNED] Full-Scale Stress Test Lifecycle Orchestration`
   - Run dry-run decomposition:  
     `python skills/engineering-pr-delivery-v3.6/scripts/decompose_v36.py --label relay/AIM/V36-STRESS.yaml --plan skills/engineering-pr-delivery-v3.6/plans/V36-1-PLAN-02.yaml --lab reallakshman19/relay-v36-stress-lab`
   - Verify output predicts required child issues #2 through #7 without mutations.
4. **Apply ST-01 & Gate Evaluation:**
   - Execute decomposition with `--apply --confirm-scope reallakshman19/relay-v36-stress-lab#1`.
   - Post genuine task evidence on child issue #2 (`V36-1-ST01`).
   - Run publisher to update parent title to `[V3.6][PARENT][E1/6]`.
   - **Publish ST-01 gate evidence before progressing to ST-02.**
   - **Gate ST-01:**
     - [ ] Clean isolation verified?
     - [ ] Negative authorization tests fail closed?
     - [ ] Parent index initialized with 6 stage tasks?
     - **Verdict:** If all YES → **GO to ST-02**. Else → **STOP**.

---

### Phase ST-02: Progressive Scale (20 → 125 → 300 Child Issues)
1. **Workload Fixture Decomposition:**
   - Using `skills/engineering-pr-delivery-v3.6/plans/V36-LOAD-FIXTURE-300.yaml`, materialize subject workload tasks across tiers:
     - Tier 2a: 20 issues
     - Tier 2b: Boundary test across 99, 100, 101 issue thresholds
     - Tier 2c: 125 issues
     - Tier 2d: Full 300 issues (`V36-LOAD-001` through `V36-LOAD-300`)
   - Paced execution: 1 write/sec with retry backoff.
2. **Pagination & Index Verification:**
   - Execute multi-page REST GET to verify all 300 workload issues exist.
   - Run second decomposition pass. Assert: **0 duplicate issues created**.
   - Profile memory usage (RAM MB) and duration across the 300 items.
3. **Gate ST-02 Evaluation:**
   - [ ] Exactly 300 workload issues created and verified?
   - [ ] REST API pagination correctly navigated via `Link` header?
   - [ ] Replay creates 0 duplicate tasks?
   - [ ] Top-level progress correctly advances to `[E2/6]` on child #3 (`V36-1-ST02`)?
   - **Verdict:** If all YES → **GO to ST-03**. Else → **STOP**.

---

### Phase ST-03: Evidence Processing & PR Attribution
1. **PR Lifecycle Initialization:**
   - Create 20 branches and open 20 PRs on the stress lab.
   - Distribute states: 10 Draft, 5 Ready, 3 Merged, 2 Closed.
2. **Evidence Staging (600 Comments):**
   - **300 Genuine Positive Evidence Comments:**
     - Must link to verified test runs in the lab repository matching candidate commit SHAs.
     - Tests field must report actual passing counts (e.g. `Tests: 84/84`).
   - **150 Negative Control Comments:**
     - Mark explicitly with `FIXTURE: NEGATIVE_TEST`.
     - Include stale candidate SHAs, mismatched Proof URLs, missing headers.
   - **150 Adversarial Comments:**
     - Mark explicitly with `FIXTURE: ADVERSARIAL_TEST`.
     - Include foreign comment authors, malformed YAML, cross-repo commit links, prompt injection payloads.
3. **Snapshot & Publisher Verification:**
   - Run `snapshot_v36.py`. Confirm: 100% of positive comments accepted; 100% of negative/adversarial fixtures flagged stale/invalid.
   - Run `publisher_v36.py --apply --confirm-scope reallakshman19/relay-v36-stress-lab#1`.
   - Verify issue titles reflect `[EVIDENCED]` for positive tasks and `[STALE]` for negative tasks.
   - Verify PR titles reflect accurate outcome attribution (e.g. `[O1/O2][DRAFT][E15/15]`).
4. **Gate ST-03 Evaluation:**
   - [ ] 0 false or adversarial evidence accepted?
   - [ ] Exact PR head matching enforced?
   - [ ] Progress advances to `[E3/6]` on child #4 (`V36-1-ST03`)?
   - **Verdict:** If all YES → **GO to ST-04**. Else → **STOP**.

---

### Phase ST-04: Concurrency & Event Storms (1 → 8 Workers)
1. **Multi-Worker Execution:**
   - Spawn parallel worker processes (1 → 3 → 5 → 8 workers).
   - Workers execute concurrent reads, decomposition checks, and publisher updates.
2. **Convergence & Idempotence:**
   - Allow worker queues to drain.
   - Run single-threaded publisher pass.
   - Assert: **0 proposed title mutations, 0 index corruptions, 0 title thrashing**.
3. **Gate ST-04 Evaluation:**
   - [ ] 8 concurrent workers complete without deadlock?
   - [ ] Settled replay produces exactly 0 mutations?
   - [ ] Progress advances to `[E4/6]` on child #5 (`V36-1-ST04`)?
   - **Verdict:** If all YES → **GO to ST-05**. Else → **STOP**.

---

### Phase ST-05: Fault Injection & Interrupted Recovery
1. **Fault Simulation:**
   - Simulate HTTP 429 rate limit with `Retry-After: 5`.
   - Simulate HTTP 503 error on POST.
   - Simulate process interruption mid-transaction.
2. **Resumption & Verification:**
   - Verify exponential backoff and jitter operate properly.
   - Re-run reconciler from fresh process. Assert clean resumption with **0 duplicate entities**.
3. **Gate ST-05 Evaluation:**
   - [ ] Backoff logic respects rate-limit headers?
   - [ ] Interrupted transaction resumes without data loss or duplicates?
   - [ ] Progress advances to `[E5/6]` on child #6 (`V36-1-ST05`)?
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
3. **Gate ST-06 Evaluation:**
   - [ ] Cold successor reconstructs 100% of state from GitHub alone?
   - [ ] Memory remains flat across 5 endurance cycles?
   - [ ] Progress advances to `[E6/6]` on child #7 (`V36-1-ST06`)?
   - **Verdict:** If all YES → **PASS STRESS TEST**. Else → **FAIL**.

---

## 3. Reporting & Deliverables

1. `STRESS_TEST_REPORT.md`: Comprehensive narrative covering timeline, worker scaling, latencies, and gate evidence.
2. `stress_results.json`: Machine-readable results and metrics.
3. Terminal Agent LOG Line footer.
