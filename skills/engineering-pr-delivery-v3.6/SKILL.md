# Engineering PR Delivery v3.6 — independent, reusable GitHub lifecycle

**Scope:** A v3.6-only lifecycle: an approved parent plan, real child issues, verified own-child task evidence, automatically updated issue/PR titles, and GitHub-only successor continuation. The [Common #341 lab benchmark](https://github.com/reallakshman19/Common/issues/341#issuecomment-6119409109) was Owner-accepted (7/7 workpacks, O1–O5); that benchmark is an example, **not** a fixed label, repo, or lab default. v3.6 has no runtime dependency on v3.5, v3.2, v3.1, Local v1.1, or DELP.

**Agent addendum (A01–A14, incl. Owner-required A13 coding practice and A14 pre-claim SELF-CHECK):** [CODING_PRACTICES_ADDENDUM.md](CODING_PRACTICES_ADDENDUM.md). It is additive. The canonical 8-line evidence and the terminal LOG are unchanged.

**Admitted C1 issue-history structural reader (#401 / #409):** [CONTINUITY_CHAIN_V1.md](CONTINUITY_CHAIN_V1.md) and `scripts/issue_chain_v36.py` with synthetic/reported-only [fixture](tests/fixtures/issue-chain-274-reported.json). These **account for 11 categories** while explicitly preserving UNKNOWN, missing originals and zero external source attestation. This is a pure JSON validator (no network, provider writes, new task evidence, approval, automatic scoreboard A promotion, title or label updates). It is **not** the active approved label/plan for any work, and it does not replace the canonical 8-line receipt, self-check or mandatory terminal LOG. Real provenance verification and activation are separate Owner-scoped gates.

## 1. Mandatory inputs — work-specific, never silently default

- **Label path:** an explicit, Owner-approved `--label relay/AIM/<WORK>.yaml` from that work's repository. The work ID comes from the filename and must match the label's `work`. **There is no default V35-LIFECYCLE label.** A copied test fixture is not approval.
- **Plan path:** an explicit `--plan <selected-plan.yaml>`, bound to the chosen label's `work`, `version`, `label_sha`, and real parent issue. Its `parent: owner/repo#N` is the explicit target for reads/writes; it may be the label's repository or the label's authorized writable lab.
- **Writable lab:** read `guidance.notes` for **exactly one** `Writable lab: owner/repo` directive in the selected label. Resolve it using `lifecycle_v36.writable_lab(label)` and supply **`--lab <LAB_REPO>`** to every lab-target CLI (decompose, snapshot, publisher, successor cold, 2-pass and 3-pass). The selected lab parent in `--plan` must use that exact repository. CLI calls targeting the label's own coordination repository omit `--lab`. No hard-coded lab, no inference from old `Lab:` notes, `done_when`, old sample paths, or predecessor chats. If the label has no `Writable lab:`, read-only `validate-label` can still succeed, but **lab writes and lab-target plans are unauthorized** until the Owner supplies a valid directive. Multiple/invalid directives fail closed.
- **Write consent:** for a write, require a separately authorized repo/issue scope, actual GitHub credentials and the relevant explicit `--apply --confirm-scope owner/repo#N`; default dry-run, then provider GET readback. Never assume permission from documentation. The trusted default-branch lab workflow is a separately scoped integration, not permission to execute untrusted PR code.

To select a work, supply paths explicitly; substitute the actual chosen work and plan rather than using a preloaded V35 example:

```sh
python -m pip install -r skills/engineering-pr-delivery-v3.6/requirements.txt
python skills/engineering-pr-delivery-v3.6/scripts/lifecycle_v36.py validate-label relay/AIM/<WORK>.yaml
python skills/engineering-pr-delivery-v3.6/scripts/decompose_v36.py --label relay/AIM/<WORK>.yaml --plan <PLAN_PATH>
python skills/engineering-pr-delivery-v3.6/scripts/successor_v36.py cold --label relay/AIM/<WORK>.yaml --plan <LAB_PLAN_PATH> --lab <LAB_REPO_FROM_LABEL> --pr <PR_NUMBER>
```

The label can declare fewer than five outcomes (e.g. O1–O3) and can declare `engineering_critical: critical`; validation preserves the actual Owner text and metadata. Outcome identifiers in a plan must be declared in **that** label. **Do not** write to another work's repository merely because its label validates read-only. The Owner controls changes to the label and material scope.

## 2. O1–O5 end-to-end process

1. **O1 — Decompose:** `scripts/decompose_v36.py` validates a label-bound plan with stable tasks/sizes/AC, observes real child issues and a unique managed parent index; default dry-run and duplicate-safe apply.
2. **O2 — Evidence:** `scripts/lifecycle_v36.py` strictly renders a canonical finished-task record; publish on that task's child issue. `scripts/snapshot_v36.py` checks true provider author, selected issue/outcome, exact candidate SHA, Proof PR/commit consistency and current PR head. Stale, missing or unverified evidence never counts as current and never auto-proves acceptance.
3. **O3/O4 — Titles:** `scripts/publisher_v36.py` projects parent/child titles and **PR-specific** outcomes from live evidence and PR draft/open/merged state. The approved lab's default-branch event runner uses immutable pinned v3.6 source, validates Git blobs, applies scoped title updates, GET-verifies results and replays to zero changes. Never checkout untrusted PR code in a `pull_request_target` workflow.
4. **O5 — Cold successor:** `scripts/successor_v36.py` reads current Owner label/plan, child index, own-child evidence and live PR heads directly from GitHub, emits a portable packet, and supports BuddyRunner v1.6 **1a HOLD → 1b independent source reconstruction → 2 one reconciliation**, with optional one-shot Y only after later Xb evidence. Prompts are not executions or approvals.
5. **O5 — Separate generators:** `scripts/prompt_2pass_v36.py` independently generates evidence-grounded plan→execution prompts; `scripts/prompt_3pass_v36.py` independently generates source/falsifier→implementation→independent validation prompts. Both accept explicit `--label --plan --lab --task-id --pr` for lab targets and preserve exact Owner words. Never combine them into one mode-driven generator.
6. **Integrated acceptance:** execute a **real** parent→child→evidence→title→PR attribution→cold continuation in the **selected authorized** writable lab, with positive/negative cases, hosted CI and provider readbacks. Evidence count `E2/2` is not automatic Owner signoff. Record the Owner's actual acceptance separately. Do not use an old lab as a writable fallback.

For the accepted **example only**, the label was `relay/AIM/V35-LIFECYCLE.yaml` v1.2.1, whose `Writable lab:` explicitly named `reallakshman19/relay-v36-e2e-lab`. The real parent is [lab #1](https://github.com/reallakshman19/relay-v36-e2e-lab/issues/1), children #2/#3, linked draft PR #4 and unrelated PR #5. The positive/negative trusted runs [38214023565](https://github.com/reallakshman19/relay-v36-e2e-lab/actions/runs/38214023565) and [38214091849](https://github.com/reallakshman19/relay-v36-e2e-lab/actions/runs/38214091849) and accepted [PLAN-07](https://github.com/reallakshman19/Common/issues/341#issuecomment-6119409109) are historical receipts, not a generic target.

## 3. TASK_EVIDENCE — exact opening and independent proof

Every finished task posts **on its own child issue**. Start with these three human-readable lines in exactly this order, then the canonical v3.6 record. A link, test total, and current head are *evidence*, not automatic final Owner acceptance.

```text
Outcome: <O# declared by the selected label>
For the user: <real user-visible workflow change or nothing yet>
Proof: <concrete test/run/output link>
TASK_EVIDENCE v3.6
Task: <task ID from selected plan>
Child issue: <owner/repo#number>
Candidate: <owner/repo@40-character git SHA>
Tests: <passed>/<run>
```

The source formatter `render-evidence` rejects placeholder Proof and invalid task/test fields; the snapshot rejects foreign authors and mismatched Proof commit SHA. Publish canonical comments unchanged, and refer to acceptance separately. Never rewrite historical authored evidence to inflate title counts.

## 4. Agent LOG line — mandatory terminal footer

Every execution or handover response ends with exactly **one LOG line in its own plain text code block**. The successor finds this contract in this GitHub-hosted skill, without prior chats. Fill every field from the selected label, current GitHub issue/plan, actual test result and latest **published log commit**, never from guesses. Use `@NOT_WRITTEN:<reason>` if the log file could not be updated. `aim` is **the selected label's version**, not a hardcoded example; `outcome` is an actual O# from the selected work.

```text
LOG | chat=<chat-id> | tab=<tab> | folder=<coordination/path>@<latest-log-commit> | issue=<owner/repo#number> | plan=<revision> | progress=<done>/<total> | done=<task IDs or none> | next=<task IDs or none> | ac=<met>/<total> | blocker=<NONE/OWNER/PERSON/CI/MACHINE/EXTERNAL> | PR=<number>@<sha7>:<green/red/queued/not-run/none> | tests=<passed>/<run> | handover=<no/due/ready:path> | aim=<label version> | outcome=<O#> | user=<yes or no>
```

**Owner constraints:** Owner controls decisions and merges; engineering-critical doubt must stop the risky action. A generated packet/LOG, stale GitHub snapshot or passing check cannot invent an accepted task. Never merge, close, release, or silently change the Owner's aim without authorization.
