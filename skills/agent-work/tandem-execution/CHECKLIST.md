# Tandem execution checklist — useful work before paperwork

**Scope:** the checklist below tests PARALLEL/SERIAL. For TANDEM_IR use the compact completion checks in [TANDEM_IR.md](TANDEM_IR.md#completion-and-fallback); A is the final owner, B's return to A is intentional, and evidence-only contributions can be valid when no legitimate repair remains.

Use only checks relevant to the current assignment. Do not turn these into a separate gate or new reporting cycle.

| Check | Acceptable evidence | Falsifier |
| --- | --- | --- |
| Both authorized in parallel | One actual assignment with isolated A1/B1 writes | B only allowed to prepare tests until A uploads |
| Native work starts | Source delta and actual tests in each active agent's workspace | Missing A marker stops B |
| Candidate isolation | Different mutable trees/branches; immutable published snapshots | A/B concurrently overwrite same ref |
| Original behavior | Exact source/input, expected wrong and right output | Reported PASS is used as requirement |
| Both contributions considered | Actual diffs and meaningful tests, selected/rejected reasons | Blind concatenation or fake contribution |
| Missing peer recovered | B1 proceeds; verified available A bytes considered | No READY treated as global HOLD |
| Semantic convergence | Final combined entrypoint and opposing controls | Text merge clean but user state lost |
| Final ownership | B corrects all feasible remaining defects | B returns defect list to A |
| Finite boundary | B's actual final run and agreed snapshot; late work historical | Indefinite wait, reopening by filename timestamp |
| Truthful final | Outcome, lineage and delivery separately stated | B-only complete called partial solely for missing A; partial combined called complete |
| Drive exchange | Native ZIP, actual file ID/hash, verified bytes | Link/sandbox/issue comment claimed as delivered |
| Safety | Protected data/permissions preserved; unaffected work continues | Fake PASS, forced shared overwrite, forbidden prod action |

**Minimal acceptance:** demonstrate the actual required outcome and a meaningful contrary case on the final candidate. A passing offline example tests the recipe, not a real multi-agent deployment.
