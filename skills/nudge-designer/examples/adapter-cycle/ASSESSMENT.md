# Actual role execution and reconciliation

## Start here

This is an archived local pilot from 18 October 2026, using synthetic raw tasks.
It is a worked reference, not raw input for a fresh-agent evaluation.

| Record | Where to start |
|---|---|
| Issued worker assignment | `worker/case.md`, `intent.json`, `plan.json`, `packet.json` |
| Worker native result | [diagnostic.md](worker/diagnostic.md), `probe.py`, `probe-output.json`, `return.json` |
| Issued specialist assignment | `specialist/case.md`, `intent.json`, `plan.json`, `packet.json` |
| Specialist native result | [study-note.md](specialist/study-note.md), [subject-check.md](specialist/subject-check.md), `arithmetic.py`, `arithmetic.json`, `return.json` |
| Separate review | [review.md](reviewer/review.md), `independent_check.py`, `independent-checks.json`, `return.json` |
| Current working education revision | [reconciliation.md](current-specialist/reconciliation.md), `current-specialist/intent.json`, `plan.json`, `impact.json`, Owner/successor packets |

Every role folder preserves issued inputs and actual outputs byte for byte.
`issued-artifacts.sha256.json` identifies those 65 archived files. The reviewer
folder also keeps the exact 22 supplied inputs and its before/after manifests.
Original runtime commands, paths and configuration limits are historical evidence;
the archival scripts deliberately retain them. Do not rerun packaging scripts over
this history or assume their machine paths exist on another host. Replay validation
and intake using the portable commands below, writing new outputs elsewhere.

## What actually happened

Three fresh agent threads received task-local raw inputs and the skill, with no
worked answers or other agent outputs except the artifacts explicitly assigned
to the reviewer. They were given real execution/review assignments, not told to
evaluate the skill. A separate thread and local recomputation are observed; actor
authenticity, formal qualification and model/reasoning configuration are UNKNOWN.

| Participant | Actual bounded work | Remaining outcome |
|---|---|---|
| Guided worker | Imported the unchanged supplied function; four calls in two fresh completion orders; found obsolete publication in each order and retained current-completion success | No repair or browser/product acceptance; CSV remains separate |
| Specialist | Drafted a learner-facing note; executed nine exact-arithmetic checks for 18 m/s, g=9 m/s²; reported inconsistent 20 m/s handover | No transfer material, learner response or learning gain |
| Reviewer | Imported the copied original function with its own oracle; recomputed six motion rows using Decimal rather than the specialist's Fraction script; eight review checks and seven numerical checks passed | Review was after seeing the reports, not blind or formally qualified acceptance |

The specialist detected an accidental stale `handover.next_action` in the issued
plan: 20 m/s conflicted with the raw case and `C-PHYSICS` at 18 m/s. The reviewer
confirmed this and noticed `F-PREREQ` asserted a learner misconception/prerequisite
that the new raw case did not supply. Neither error was planted as a known answer.
Structural validation had accepted both: this exposes its semantic limits.

The Designer read all native artifacts, retained the correct content, corrected
the working handover and reclassified `F-PREREQ` as a proposed scaffold. The new
revision preserves the original physics condition and unresolved learner evidence.
Original issued objects and returns are unchanged. `reconciliation-checks.json`
records successful historical intakes, rejection against the changed binding and
no accepted Owner outcomes. The next useful bounded work is transfer material;
an actual learner response is needed for learning assessment, not for drafting it.

## Portable intake and preservation checks

With Python 3.10+, `jsonschema` and `SKILL` pointing to this package, use a new
output directory. For each `worker`, `specialist` or `reviewer` folder:

```bash
python "$SKILL/scripts/nudge_designer.py" validate --intent intent.json --plan plan.json
python "$SKILL/scripts/nudge_designer.py" receive --intent intent.json --plan plan.json --report return.json
```

Run those from the chosen archived role folder; these stdout-only commands do
not change it. The focused tests verify all archived file digests, native snapshots,
issued bindings, reviewer manifests and the corrected current revision. They do
not execute archival packaging scripts or relabel a replay as the original run.
Current intake may include fields added after issue; compare preserved native
content/bindings rather than rewriting old worksheets to match the latest renderer.

No low-reasoning model was selected or benchmarked. These executions demonstrate
a usable local exchange and detected semantic errors; they do not establish live
UI repair, learner outcomes, FE solver validity or engineering acceptance.
