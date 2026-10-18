# N-REVIEW native review

The bounded review is COMPLETE. Independent local checks support the worker's
diagnosis and the specialist's study note. The issued education plan contains a
material handover inconsistency that needs reconciliation before reuse. Product
correctness and learner understanding remain unresolved.

## Findings against original conditions

1. **The diagnostic correctly exposes the original invariant violation.**
   `inputs/worker/source.py` ignores `request_revision` and unconditionally writes
   the payload. My own checker executed that supplied function four times; it did
   not execute `inputs/worker/probe.py`, replace the function, or implement a repair.
   Starting each order with current revision 10 and no result gives:

   | Completion order | Actual results after successive events | Required results | First violation |
   |---|---|---|---|
   | NEW rev10, OLD rev9 | NEW, OLD | NEW, NEW | Event 2 |
   | OLD rev9, NEW rev10 | OLD, NEW | null, NEW | Event 1 |

   Both current completions publish successfully. All four state transitions and
   oracle results match `inputs/worker/probe-output.json` and `diagnostic.md`.
   The reverse order's correct final result does not erase its earlier obsolete
   publication. This supports the original `R-CURRENT`/`C-SOURCE` failure, not a
   repaired or accepted product. The report correctly leaves CSV work separate.

2. **The study note is correct for the supplied 18 m/s example.** From
   `inputs/specialist/case.md` and `C-PHYSICS`, upward positive gives
   `v(t) = 18 - 9t` and `y(t) - y(0) = 18t - 4.5t²`. Independently computed exact
   Decimal values match all six rows in `arithmetic.json`: at 1.9, 2 and 2.1 s,
   velocities are +0.9, 0 and -0.9 m/s; the maximum rise is 18 m at 2 s. The
   velocity slope is -9 m/s² throughout free flight, including the turning instant.
   The held-at-rest contrast is sound because velocity remains zero over an
   interval and an upward holding force balances gravity. The note distinguishes
   instantaneous velocity from its rate of change and preserves signs and units.
   I recomputed the values without executing `inputs/specialist/arithmetic.py` or
   relying on its PASS field.

3. **Confirmed drift: the education handover says 20 m/s.**
   `inputs/specialist/plan.json` at `handover.next_action` conflicts with the
   explicit 18 m/s case and intent condition. The study note follows 18 m/s and
   the specialist correctly disclosed the conflict. Using 20 m/s would change
   the top time to 20/9 s and rise to 200/9 m. Preserve the issued snapshots and
   reconcile the working handover before reuse; refreshing a digest alone would
   not resolve the meaning. No input was edited here.

4. **Keep scenario assumptions and learning evidence distinct.** The original
   education intent's `F-PREREQ` describes a synthetic learner's prior knowledge
   and misconception, but the copied case supplies no learner assessment or
   evidence of those prerequisites. Treat that row as a synthetic scenario
   assumption unless an actual source is supplied on revision. Neither native
   report claims learning gain. `N-TRANSFER` remains unexecuted, and the original
   `O-CONTENT` completion condition still requires transfer assessment material.
   Correct worked content alone does not complete `O-LEARNING` or `R-LEARN`.

## Actual checks and preserved evidence

All substantive Python checks ran locally with `python -B`,
`PYTHONDONTWRITEBYTECODE=1`, and
`PYTHONPATH=/workspace/scratch/52eed2252c51/tmp/br20-deps`.
`independent_check.py` exited 0; its eight review checks and seven numerical
checks passed. The two detected invariant failures are diagnostic findings,
not failures to execute the checker. Exact commands and their results are in
`commands.json`; detailed observations are in `independent-checks.json`.

The skill CLI validated this review's issued intent/plan as STRUCTURALLY_VALID
and recomputed both supplied return intakes as RETURN_RECORDED. The worker's
native snapshot exactly matches `diagnostic.md`; the specialist's native snapshot
exactly matches `study-note.md` (its separate calculation report is
`subject-check.md`). Both recomputed worksheets match all shared fields in the
supplied worksheets. Current intake additionally emits
`native_representation: TEXT_SNAPSHOT`; this is no binding or content discrepancy.
`issued-binding.json`, obtained with `bind`, matches this review's supplied packet.
Validation and intake establish structure and binding, not semantic acceptance.

All six pinned source hashes in the review intent match the observed files.
`input-manifest-before.json` and `input-manifest-after.json` cover all 22 supplied
files and match exactly; final packaging preservation is recorded separately.

## Limits and next proposals

This is an independent local recomputation after reading the supplied reports,
not a blind review or authenticated proof of participant independence. Current
model/reasoning configuration and formal domain qualification are UNKNOWN. Python
execution was observed; role labels and synthetic capability declarations add no
qualification. Original worker/specialist packets, validation receipts, binding
receipts and the worker's packaging script were not supplied. Their historical
packet-comparison and execution claims cannot be authenticated from these copies.
The original source revisions are unpinned; the current byte hashes identify
observed content without authenticating origin.

The Designer can retain both native results as bounded evidence, reconcile the
20 m/s handover and synthetic prerequisite provenance in a new working revision,
and assess affected conclusions while preserving issued history. The measured
race supports scoping later repair under actual authority, with both event orders
and current-completion success retained. CSV requirements remain an independent
unresolved question. Separately prepare the planned transfer problem and rubric;
actual learner understanding, delayed retrieval and learning gain remain unknown.
No product edits, repair, learner contact, publication, browser execution or
external writes occurred in this review.
