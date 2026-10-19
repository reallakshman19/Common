# Compact operational reference — T-INVESTIGATE

Parent-authored refinement after inspecting the native consumer output. This is a
proposed operational view, not an issued task or a fresh recipient application.
The original [native brief](consumer/worker.md) remains unchanged.

**Purpose.** Establish what the supplied evidence shows about a wrong-source result,
so a later production investigation starts from the right identity condition.
The result must correspond to the currently selected **source and revision**.

**One deliverable.** One investigation note for `T-INVESTIGATE`. Keep trace
reconstruction, the invariant and discriminating contrasts in the same task.

**Inputs.** Read the original [request](single/owner.md), unchanged
[guard](single/guard.js) and [events](single/events.json). Use the issued
[task design](single/task-design.md) and [map](single/task-map.json) as context;
[the input manifest](consumer-issued-inputs.sha256.json) supplies byte hashes.
Binding: `MAP-SINGLE-SOURCE-IDENTITY`, revision 1, task `T-INVESTIGATE`; canonical
map SHA-256 `199638e23fdad84eacd8e0eaa80dd315d4fb8bbb3636fd29681b7560833c72c3`.
The [analytical receipt](single/analysis-checks.json) is a claim to check, not an
application reproduction. Use these archived relative files; absolute source
locators in the native map record the historical workspace.

**Boundary and method.** Preserve this exact order: select ALPHA@11 → start
ALPHA@11 → select BETA@11 → complete ALPHA@11 → display ALPHA@11. Reconstruct a
state table for selected, started, completed and displayed identities. Evaluate
the literal guard separately from the Owner identity condition. Derive a current
matching completion and a same-source stale-revision contrast. Show both predicates
and inputs for all three cases. Use Python with `-B` for local finite analysis;
any later assigned note would be a new artifact in `consumer/`. Product changes
and architecture decisions are outside this proposed task.

**Success.** The note connects exact source rows and actual computations to the
identity distinction. It explains why revision equality alone does not establish
source identity. Blocking all completions or testing only stale revisions would
not satisfy this task. Distinguish supplied events, finite analysis and ordinary
application behavior.

**Uncertainty.** Model/effort and task-specific fit remain UNKNOWN. Production
caller/state/publication behavior and a suitable remedy are unestablished. If an
input or premise differs, report the affected claim and observation; retain useful
local analysis. Do not infer a production cause from this synthetic helper case.

**Return.** Provide the note, input hashes, state table, reproducible checks, actual
results, unresolved judgments and proposed next investigation. Preparation does not
execute this task or establish production acceptance.
