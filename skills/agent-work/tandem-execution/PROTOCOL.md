# Tandem execution protocol — continuous correction, forward-only ownership

## 1. Assignment is the permission envelope, not a sequence of approvals

The user assigns one outcome to A and B at the start. Both receive the same original requirement, baseline source locator, allowed changes, protected behavior, finite done-list, execution budget and exact private or authorized Drive folder. A can write during its turn; B is preauthorized to write after the handoff condition. A and B are names for these two assigned turns, not additional roles. Do not infer merge, deployment, destructive production changes, private data use or ungranted cross-task writes. Routine code fixes, tests, refactoring necessary to fix the contract, dependency restoration from approved sources and scope-preserving conflict resolution are part of the authorized turn. A new task or an actual change of permission is not.

One task can start with an immutable baseline, or an already existing working candidate. Preserve baseline and compare actual bytes. Changes to the candidate caused by the current agent are expected progress, not an authorization blocker. If upstream source moved, preserve the pinned candidate and safely rebase/test within the assignment when allowed; stop only a truly conflicting write or prohibited action.

## 2. Ownership and flow

| Phase | Agent A | Agent B | Authoritative candidate |
| --- | --- | --- | --- |
| Start | Own initial correction | May derive independent tests, no shared writes | Baseline C0 |
| A working | Reproduce, fix, test, close regressions | Prepare contrary cases if active | A scratch candidate |
| A handoff | Stop writes, upload package, publish READY last | Read/verify same package | C1 from Drive |
| B working | Finished; no repair handback | Own all feasible in-scope defects, fix and validate | B cumulative candidate |
| B delivery | No action | Upload complete C2, actual evidence, remaining limits | C2 from Drive |

If A finds a known defect, A attempts the fix; never intentionally leave a bug so B has work. If B finds a defect in A's patch, B owns it. If B's change breaks A's earlier control, B restores the invariant. If either discovers unrelated improvements, keep them as notes rather than expanding the done-list. No A→B→A cycle. Neither a failed test nor a disagreement changes the active writer.

## 3. Completion and recoverable handoff

A delivers the best coherent candidate at the end of its assigned turn, even if incomplete. Include the native runnable patch or source and dependencies/commands, original inputs, actual test output, negative controls, precise failures, and enough context to resume. A uploads only to the assigned Drive task folder, verifies the package and publishes `A-READY.json` last. A's marker explicitly records it has stopped writing the candidate. The planned successor permission takes effect when B can verify this recoverable checkpoint and no actual conflicting writer remains. No further routine approval, manual receipt ceremony or request for the same evidence. B verifies what is necessary to work; that verification is recorded with B's work, not sent back to A.

If a package is incomplete but the actual source/patch is recoverable from the folder or authorized baseline, B repairs the custody gap, records what is missing and continues. If A is interrupted, a previously complete Drive checkpoint plus verified cessation or isolation of the old writer can be used; B need not obtain an extra report from A. Do not select a late A upload once B has taken the candidate; preserve it as historical if useful. A's shared-branch writes after handoff are forbidden. Do not force-push over a real external concurrent writer. Prefer isolated local candidate trees; native Git commit/PR mechanics do not constitute the handoff.

## 4. B owns convergence

B reconstructs the required outcome from original intent and examines A's actual changes, not just the status summary. B identifies the most consequential surviving wrong result, runs the relevant negative case, fixes it if observed, reruns positive controls and checks the combined production entrypoint. Repeat local correction within the assignment's budget. Default: one A implementation turn and one B implementation turn; B may perform as many routine local edits/checks as the agreed budget permits. No per-test permission or arbitrary round counter. A failed check is an input to B, not an exit or a handback. If a final check uncovers a new in-scope failure, B fixes it in the same turn when feasible. Do not return only a list of defects when an authorized correction remains executable.

## 5. No artificial blockers — recovery first

| Situation | Required action |
| --- | --- |
| Report missing, file names inconsistent, stale log | Inspect code/fixture, reconstruct the relevant evidence, proceed. |
| Test dependency unavailable | Try approved setup, use actual module-level execution/alternate harness where valid, continue code/tests; mark unavailable full run NOT_RUN. |
| A's fix partial, erroneous or contradicts B | Reproduce, correct forward; never return the defect to A. |
| A already fixed every known issue | Add valuable negative/integration check; no gratuitous production change. |
| Patch conflict or ordinary baseline drift | Reconcile/rebase if authorized and verify; otherwise preserve separate working patch and continue unrelated work. |
| A upload incomplete | Recover available native source or apply verified delta from Drive; reconstruct missing logs locally; do not demand a polished report. |
| Private fixture unavailable | Use authorized representative synthetic controls, label scope; don't pretend actual private replay. |
| Drive temporarily unavailable | Retry available authorized connection; prepare local native checkpoint and execute feasible local work; mark transfer NOT_DELIVERED until real Drive upload. Do not substitute another handoff channel. |
| A still writing the same shared candidate | Isolate B in read-only/scratch work; no overlapping shared writes. Resume write turn when cessation/isolation is established. |
| Missing input prevents one test | Mark that test NOT_RUN; execute all unrelated feasible work. |
| Real requirement ambiguity | Choose an existing safe behavior when justified; document assumption. Ask only if materially irreversible or incompatible with explicit requirement. |
| Budget exhausted with material defects | B delivers runnable partial candidate, exact unresolved failing cases, and single next decision. Never label complete. |

## 6. Done-list and final status

Keep a finite task-specific set: reproduce/fix material defects, preserve valid behavior, run discriminating negative controls, verify actual integrated output where possible, deliver cumulative native code plus reproducible evidence. Completion means the specified observable outcome is supported on C2. A source inspection cannot establish runtime correctness. `COMPLETE` is scoped to proven agreed criteria; `PARTIAL` records useful work with missing or failed criteria; `NOT_DELIVERED` describes real Drive transfer failure, not whether local work happened. Use actual PASS/FAIL/NOT_RUN per check, not a generic gate. A and B disclose authored code/tests; no assertion of independent approval of both contributions. Existing acceptance and release rights do not change, and no additional participant is required by this recipe.
