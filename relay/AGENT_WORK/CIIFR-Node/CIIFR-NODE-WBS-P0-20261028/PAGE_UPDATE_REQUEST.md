# CIIFR-Node — Progress Page P0–P6 publication request

**Source Owner task:** [CIIFR-Node WBS #227](https://github.com/reallakshman19/XML_Compare_Utilities/issues/227).  
**CLI contract:** [Common Progress Page pinned at `a353371d`](https://github.com/reallakshman19/Common/tree/a353371d5f1ea3d6df8214165ecdecebda9df41b/skills/agent-work/progress-page) and actual `reallakshman19/progress-page/tools/pp_cli.py`.

## Why this is separate
Existing Page project `ciifr` already covers Geometry WBS3, Element WBS4 and historical XML WBS5. The Owner requested a **new CIIFR-Node workstream**, so create project `ciifr-node` rather than silently modifying the broad `ciifr` project. This Page project is distinct from a new GitHub source repository: `reallakshman19/CIIFR-Node` did **not** exist at inspection.

### Intended published structure

- Project title: `CIIFR-Node`, standalone Oracle coordination; navigation on Home/Progress/WBS/Continuity pages.
- Milestones **M1–M15**, grouped under Page WBS roots **1–7**, representing engineering **P0–P6** (the Page CLI does not permit zero as a numeric WBS).
- Cards: `node-r0-code` (SUBMITTED, unqualified draft), `node-r0-ir` (NOT_STARTED, unassigned), `node-original` (NOT_STARTED, private access not established), `node-correspondence` (NOT_STARTED).
- Grounding fixtures: `CONCEPT_NOTE`, `ARCHITECTURE_CONCEPT`, canonical WBS, R0 PR, source/target relay status, original custody receipt, roadmap, real gates, next tasks.
- Audit: created only by official `pp_cli.py`, append-only and not manually edited.

## Reproducible authoring route

The exact **standard-library script**, [`payload/CIIFR_NODE_PAGE_UPDATE.py`](payload/CIIFR_NODE_PAGE_UPDATE.py), calls the **existing Page `tools/pp_cli.py`** for each project/milestone/fixture/card, and runs its `check`. It intentionally does not reimplement `pp_cli` or directly edit `audit.json`.

On the actual authorized page checkout:

```sh
python /path/to/CIIFR_NODE_PAGE_UPDATE.py --page-root .
# review dry-run list and source URLs; on same current checked-out base:
python /path/to/CIIFR_NODE_PAGE_UPDATE.py --page-root . --apply
python tools/pp_cli.py check
python tools/pp_cli.py check --base origin/main
python tools/pp_cli.py triggers
git diff -- data/
# open DRAFT data-only PR, inspect exact head / CI / page readback
```

If the page repo has changed from the verified base, reconcile with latest data before running. Fail closed if `ciifr-node` already exists; never duplicate audit. Before merge inspect native Page PR checks, page WBS rendering and Home fixture entries; no unsupported automatic Cycle bridge to broad `ciifr`.

## Current publication status
**SOURCE_WBS_CREATED** (native #227–#230), **COMMON_RELAY_IN_DRAFT_PR**, **PAGE_CLI_DRY_RUN=NOT_RUN**, **PAGE_DATA_NOT_WRITTEN**, **PAGE_PROJECT_NOT_PUBLISHED**, **BROWSER_NOT_RUN**. The Common relay script is prepared for a designated authorized Page writer with a real checkout. Do not claim a project page is live until Page PR and GitHub Pages deployment/readback succeed.

### Strongest surviving wrong case
A page that incorrectly marks a writer/CAESAR release PASS or associates broad `ciifr` Geometry Cycle with new `ciifr-node` would violate custody despite syntactically correct page JSON. Keep R0 read-only/PR226 draft/independent IR not run; original private bytes remain outside public GitHub.

**EXACT_NEXT_ACTION:** Authorized CIIFR-Node Page writer runs official CLI dry-run and check in current `progress-page` checkout, applies only its generated audited `data/` delta, opens reviewed draft PR, then confirms actual published page project and fixtures.
