# Tandem Execution protocol — parallel implementation, forward convergence

**Mode boundary:** the numbered B-final flow below is normative for PARALLEL/SERIAL only. For an explicitly assigned `TANDEM_IR`, [TANDEM_IR.md](TANDEM_IR.md) is the mode-specific contract: A implements, B independently challenges and contributes, A reconciles and delivers. Shared identity, isolation, genuine blocker, evidence and native authority principles still apply; do not apply B-final or no-handback rules to TANDEM_IR. The mode is not a coordination/engineering-release selection.

## 1. One assignment; both agents execute

The assignment records the original user-visible outcome, real source/input identities, A and B, common C0 or an explicit shared starting candidate, allowed paths/actions, protected invariants, finite done-list, budget, Drive folder and convergence boundary. PARALLEL is default. Both agents are authorized to write **their own isolated candidate** immediately. Explicit SERIAL is available when a first product must genuinely precede refinement. Routine edits, tests, permitted dependency restoration, safe rebase and conflict resolution are in the assigned envelope. No new permission is derived from this document, READY, a chat title or a passing test.

All handoffs, native packages and final delivery use the one assigned Google Drive folder. Do not use another handoff channel. A Git repository supplies source and may hold native implementation commits when permitted. Do not treat a PR comment as artifact transfer.

## 2. Separate write ownership from final delivery

| State | A | B | Candidate |
| --- | --- | --- | --- |
| PARALLEL_START | Implement in own workspace | Implement in own workspace | Immutable C0 |
| A1_WORKING / B1_WORKING | Fix, execute, resolve own failures | Fix, execute, resolve own failures | Two isolated candidates; no shared writes |
| A1_DELIVERED / B1_DELIVERED | Publish immutable native snapshot | Publish immutable native snapshot | Actual Drive bytes |
| CONVERGING | No writes to B's candidate | Exclusive owner of integration; continue corrections | B working lineage incorporating available A1 |
| FINAL | No routine action | Publish one final validated result | C2 or B-only final |

These are observations, not compulsory synchronized barriers. A and B may finish in either order. B need not wait for A to reach a state; B1 can be uploaded before A1. A continues in its own isolated tree until its assigned execution boundary. A may publish a checkpoint and keep working in a different mutable working tree; published snapshots remain immutable. A cannot edit the snapshot consumed by B. Neither may overwrite the other's branch or force-push a shared ref. Only B owns final integrated output.

### Scope allocation

Give each agent a meaningful primary correction area to reduce avoidable duplication; both are responsible for the task outcome. Necessary adjacent edits in an isolated candidate are allowed within assigned scope. Shared-file edits are not a conflict until integration. Do not reserve defects artificially, block a local fix because the peer "owns" a filename, or make both solve the whole problem merely to produce two patches. B can take unfinished A scope without a new routine approval. Across *different tasks*, protect shared upstream contracts and coordinate actual target integration, not individual isolated edits.

## 3. Convergence boundary — no indefinite wait

The assignment sets a practical final snapshot/budget: e.g. after B's own implementation and agreed combined regression attempt, using the latest **verified** A artifact available during the active invocation. It can also name an explicit agreed time or iteration bound if appropriate. Never impose sleep, repeated status pings, indefinite waiting or a new approval to declare that boundary. If A has not delivered at that point, B continues the full feasible outcome from B1/C0. A late package is historical after B-FINAL unless the user explicitly requests a new revision. If the assignment names no boundary, default to B's completion of its authorized implementation and regression run, with one final Drive folder refresh before delivery; do not pretend an inactive peer is running.

B may integrate incrementally as useful artifacts arrive. B's own code and tests must not wait on A's marker, final report or confirmation. If B completes its primary scope early, it takes remaining in-scope work rather than stopping at a prototype. If both have finished, B uses the actual immutable snapshots and makes one final convergence pass (including all necessary local correction iterations). A receives no routine repair request. An early B1 is a working deliverable, not necessarily final.

| Availability at convergence | Required action |
| --- | --- |
| A1 and B1 both verified | Compare both to C0, choose/combine fixes, test C2 |
| A1 absent / READY absent | Recover usable A bytes if available; otherwise finish from B1 |
| A1 corrupt or incomplete | Reject unsafe/unverified bytes; recover valid native delta or reconstruct affected fix; continue B1 |
| A interrupted | Do not wait for A; use verified immutable checkpoint if any; otherwise B-only |
| Execution budget exhausted before A can be reconciled | Deliver the best tested B candidate with the actual unintegrated A artifact noted; do not force another round |
| A changes after selected snapshot | Do not mutate or silently substitute selected bytes; consider a later snapshot only before final boundary if useful |
| B interrupted | Preserve B1 and current integration checkpoint; resume B when available, no automatic handback |
| Both solve same defect | Select sound implementation; retain useful tests and explicitly account for rejected alternative |
| Both introduce incompatible fixes | B derives original invariant, tests competing approaches, repairs forward |
| One candidate has a different base | Establish real ancestry; rebase/port verified changes within scope; test actual final source |
| A finishes after B final | Preserve late artifact; no automatic reopening, no competing final |

## 4. Semantic integration

B compares C0→A1 and C0→B1 as **three distinct objects**. Validate repository/paths/base and exact candidate digest or SHA; for a drifted base establish which upstream changes are already included. Never concatenate patches or cherry-pick conflicting changes by arrival order. For each material first-divergence contract, select A, B, a combination, or a new correction; record why against original requirements and the contrary case. A clean text merge is not proof of semantic compatibility. Inspect real entrypoint, data/identity schemas, configuration defaults, caches, boundary timing, and downstream consumers. Protect previously correct behavior, existing data, and compatibility with other accepted repairs.

Rerun all affected A/B positive and negative controls on the actual final candidate. Add at least one meaningful surviving-error test or integration observation derived from original intent, not just author test counts. Fix any regressions in B's current tree, retest and finish. B can remove an inferior A change; accurately distinguish considered, retained, adapted and rejected contributions. No code quota: a useful executable test can be a retained contribution even if its production patch is not chosen.

## 5. Explicit SERIAL alternative

If assignment explicitly selects SERIAL, A builds C1 and publishes recoverable native bytes. B may derive expectations, write local tests or isolated candidate repairs before C1 is available. To continue the same mutable candidate, A's conflicting writes must have ceased or B must use an isolated immutable snapshot. B incorporates C1 when recoverable, fixes surviving errors and delivers C2. If C1 cannot be recovered, B reconstructs on C0 or its own valid work and records B-only lineage. A READY marker is custody metadata, never a prohibition on independent implementation. Do not apply SERIAL's handoff condition to PARALLEL.

## 6. Recovery first; only real constraints narrow work

| Situation | Execute instead of blocking |
| --- | --- |
| Missing peer package, README or marker | Continue own implementation; search actual assigned Drive folder, recover known native files with verifiable source lineage |
| Missing dependency | Attempt permitted installation/cache/native module alternative; fix and test feasible parts |
| Missing historical/private input | Use authorized synthetic controls; mark authentic replay NOT_RUN |
| Ordinary patch conflict | Compare and correct locally; preserve source and tests |
| Shared branch currently written | Use isolated worktree; never overwrite a real external writer |
| Drive unavailable | Retry authorized access, finish local code/tests, retain recoverable ZIP; report NOT_DELIVERED rather than switching transport |
| Uncertain product requirement | Preserve authoritative existing behavior; isolate material decision only; continue unrelated fixes |
| Test fails | Treat as work; locate first divergence, repair and rerun |
| Budget exhausted | Publish best executable candidate and exact unresolved case; no manufactured PASS |

A real scope/authority boundary, unsafe archive, inaccessible essential input or protected irreversible operation remains a limit on that action. No missing administrative artifact, absent peer, failure of one test capability or unmerged upstream candidate creates a task-wide stop. Do not ask the user to relay routine feedback. Do not silently change task requirements to attain green tests.

## 7. Completion has three independent dimensions

- **Outcome:** COMPLETE for the agreed done-list on the final actual candidate; PARTIAL for unresolved required behavior or missing decisive evidence. A fully working B-only outcome can be COMPLETE. A combined implementation can be PARTIAL.
- **Lineage:** FINAL_COMBINED when actual contributions from both agents are retained in final code or executable evidence (state which retained/adapted/rejected; do not claim A authored code B independently reconstructed); FINAL_B_ONLY when no A contribution was retained, including absent, unverified, rejected or not reconciled before budget exhaustion; SERIAL_FINAL for a verified serial continuation. If only an A report was read, record that evidence separately, not an A implementation.
- **Delivery:** LOCAL_ONLY / NOT_DELIVERED / UPLOADED / BYTE_VERIFIED as actually observed. Final marker is an index, not an acceptance grant. Do not equate upload with recipient execution.

Use actual commands, source/candidate and input hashes, outputs and PASS/FAIL/NOT_RUN per control. B owns the cumulative final candidate and any feasible in-scope corrections until the selected boundary. The existing product acceptance/merge/release rules still apply, without adding a third participant. Both disclose their own authored changes/tests. No independent-approval claim follows from two authors agreeing.
