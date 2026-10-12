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
* **Authorized Target Lab:** `reallakshman19/relay-v36-stress-lab` (disposable lab)
* **Required CLI Arguments:**
  - Read: `--label relay/AIM/V36-STRESS.yaml --plan <PLAN_PATH> --lab reallakshman19/relay-v36-stress-lab`
  - Write: `--apply --confirm-scope reallakshman19/relay-v36-stress-lab#<PARENT_NUM>`
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
4. **Apply ST-01 & Proof PR Establishment:**
   - Execute decomposition with `--apply --confirm-scope reallakshman19/relay-v36-stress-lab#1`.
   - Create initial feature branch `test/st01-foundation-probe` and open test PR #1 against `main`.
   - Execute candidate test suite (e.g. `Tests: 90/90`) on the PR head.
   - Install trusted stress-lab publisher workflow on the default branch (`.github/workflows/publisher.yml`) using pinned v3.6 source.
   - Post genuine canonical 8-line `TASK_EVIDENCE v3.6` on child issue #2 (`V36-1-ST01`) linking to PR #1 and matching live candidate SHA.
   - Run publisher to update parent title to `[V3.6][PARENT][E1/6]` and verify transition via fresh GET readback.
   - **Publish ST-01 gate evidence before progressing to ST-02.**
   - **Gate ST-01:**
     - [ ] Clean isolation verified?
     - [ ] Negative authorization tests fail closed?
     - [ ] Parent index initialized with 6 stage tasks?
     - [ ] Real PR #1 created and live candidate SHA matched?
     - [ ] Trusted publisher installed and parent title transitioned to `E1/6`?
     - **Verdict:** If all YES → **GO to ST-02**. Else → **STOP**.

---

### Phase ST-02: Progressive Scale (300 Workload Issues under Parent #8)
1. **Workload Parent Initialization:**
   - Create workload parent issue #8 on `reallakshman19/relay-v36-stress-lab` with title:  
     `[V3.6][PARENT][PLANNED] Subject Workload 300-Task Decomposition Benchmark`
2. **Bounded Workload Decomposition (Pacing Strategy):**
   - *Pacing Constraint:* `decompose_v36.py` loops sequentially over missing tasks with no internal delay. Running all 300 in one invocation violates the $\le 15$ creates/min pacing rule and triggers secondary rate limits.
   - *Bounded Execution Strategy:* Execute decomposition in bounded slices ($\le 15$ issues per minute) across tiers:
     - Tier 2a: 20 issues
     - Tier 2b: Boundary test across 99, 100, 101 issue thresholds
     - Tier 2c: 125 issues
     - Tier 2d: Complete 300 issues via `skills/engineering-pr-delivery-v3.6/plans/V36-8-PLAN-01.yaml`
   - Command:  
     `python skills/engineering-pr-delivery-v3.6/scripts/decompose_v36.py --label relay/AIM/V36-STRESS.yaml --plan skills/engineering-pr-delivery-v3.6/plans/V36-8-PLAN-01.yaml --lab reallakshman19/relay-v36-stress-lab --apply --confirm-scope reallakshman19/relay-v36-stress-lab#8`
   - Observe, log, and measure any rate-limit interruptions, API latency, and memory growth.
3. **Pagination & Index Verification:**
   - Execute multi-page REST GET to verify all 300 workload issues exist.
   - Run second decomposition pass. Assert: **0 duplicate issues created**.
   - Profile memory usage (RAM MB) and duration across the 300 items.
4. **Stage Progression:**
   - Once all 300 workload tasks are verified, post genuine task evidence on child issue #3 (`V36-1-ST02`).
   - Run publisher to advance controlling parent title to `[V3.6][PARENT][E2/6]`.
5. **Gate ST-02 Evaluation:**
   - [ ] Exactly 300 workload issues created under Parent #8 and verified?
   - [ ] REST API pagination correctly navigated via `Link` header?
   - [ ] Replay creates 0 duplicate tasks?
   - [ ] Bounded pacing respected without unhandled 403 secondary limit lockout?
   - [ ] Top-level progress correctly advances to `[E2/6]` on child #3 (`V36-1-ST02`)?
   - **Verdict:** If all YES → **GO to ST-03**. Else → **STOP**.

---

### Phase ST-03: Evidence Processing & PR Attribution
1. **PR Lifecycle Initialization:**
   - Create 20 branches and open 20 PRs on the stress lab.
   - Distribute states: 10 Draft, 5 Ready, 3 Merged, 2 Closed.
2. **Evidence Staging via External Fixture Manifest (Task-Level Oracle):**
   - *Oracle Architecture:* `snapshot_v36.py` evaluates status **per task, not per comment**.
   - *Rule on Comment Bodies:* Do **NOT** append `FIXTURE:` or extra text to comments on GitHub. `validate_evidence()` strictly checks `text == expected` (canonical 8 lines); any extra lines cause `ContractError` and prematurely mark the task as `INVALID_EVIDENCE`.
   - Each workload task under Parent #8 receives its assigned clean mutation per [`V36-LOAD-FIXTURE-300.yaml`](file:///c:/Users/reall/Documents/antigravity/vibrant-heisenberg/skills/engineering-pr-delivery-v3.6/plans/V36-LOAD-FIXTURE-300.yaml):
     - **Tasks V36-8-LOAD001..150:** Genuine positive comments with valid PR Proof URL (`/pull/<PR>`) and matching candidate SHA $\rightarrow$ Expected status: `CURRENT_EVIDENCE`.
     - **Tasks V36-8-LOAD151..180:** Stale candidate SHAs $\rightarrow$ Expected status: `STALE_EVIDENCE`.
     - **Tasks V36-8-LOAD181..210:** Commit Proof URLs (`/commit/<sha>`) $\rightarrow$ Expected status: `UNVERIFIED_PROOF`.
     - **Tasks V36-8-LOAD211..240:** Mismatched Proof commit SHAs $\rightarrow$ Expected status: `UNVERIFIED_PROOF`.
     - **Tasks V36-8-LOAD241..260:** Foreign comment authors $\rightarrow$ Expected status: `INVALID_EVIDENCE`.
     - **Tasks V36-8-LOAD261..275:** Malformed 8-line format / missing headers $\rightarrow$ Expected status: `INVALID_EVIDENCE`.
     - **Tasks V36-8-LOAD276..290:** Task/outcome mismatch $\rightarrow$ Expected status: `INVALID_EVIDENCE`.
     - **Tasks V36-8-LOAD291..300:** Non-existent PR URL $\rightarrow$ GitHub 404 causes `get_pr()` to raise `ContractError`, caught as expected status: `PROVIDER_UNAVAILABLE`.
3. **Snapshot & Publisher Verification:**
   - Run `snapshot_v36.py`. Confirm: 100% of tasks match expected status in the classification matrix.
   - Run `publisher_v36.py --apply --confirm-scope reallakshman19/relay-v36-stress-lab#8`.
   - Verify issue titles reflect `[EVIDENCED]` for positive tasks and `[STALE]` for negative tasks.
   - Verify PR titles reflect accurate outcome attribution (e.g. `[O1/O2][DRAFT][E15/15]`).
4. **Stage Progression:**
   - Post task evidence on child issue #4 (`V36-1-ST03`).
   - Run publisher to advance controlling parent title to `[V3.6][PARENT][E3/6]`.
5. **Gate ST-03 Evaluation:**
   - [ ] 0 false or adversarial evidence accepted?
   - [ ] All 300 tasks match their expected external oracle state?
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
3. **Gate ST-05 Evaluation:**
   - [ ] Real fail-closed behavior on transient errors observed and recorded as finding?
   - [ ] Interrupted transaction resumes externally without data loss or duplicates?
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
