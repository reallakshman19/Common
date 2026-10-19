# Neutral task-map contract

`schemas/task-map.schema.json` is the field/type authority. The Python validator
adds declared reference, graph and coverage checks. Its verdict is structural only.

| Field | Meaning |
|---|---|
| `schema`, `id`, `revision` | Versioned map identity; revisions increase after substantive changes |
| `scale` | PROGRAMME or SINGLE_PROBLEM; neither imposes a task count/depth |
| `request`, `purpose` | Original Owner wording and reconstructed intended outcome |
| `performer_context` | Description, OBSERVED/SUPPLIED/UNKNOWN basis and limitations; no qualification |
| `sources` | Stable ID, locator, exact revision or null, kind and read assessment |
| `items` | Typed source-grounded statements; only UNKNOWN may lack a source |
| `scope` | Supplied permitted/forbidden work with its source basis; not a grant |
| `preserve_refs` | Constraints that every task must retain; rendered verbatim |
| `tasks` | Hierarchy, relationships, deliverable, understanding, decisions and acceptance |
| `coverage` | Each declared requirement/constraint/unknown exactly once |
| `focus`, `focus_reason` | Planner-proposed near-term BOUNDED designs and reasoning |

Kinds OWNER/SOURCE/RECEIPT/SYNTHETIC/UNKNOWN and read assessments READ_THIS_RUN,
SUPPLIED/NOT_INSPECTED record provenance, not source authenticity. A fact needs a
source; a source classification does not establish that a claim is correct.

Each task has one proposed deliverable. `parent_id` supplies context; `depends_on`
names prerequisites. Parent and dependency graphs must be acyclic; dependencies
cannot point to ancestors/descendants. EXPANDED needs children. BOUNDED/DEFERRED
have none. SPLIT needs at least two children and a stated cut (output, oracle,
consumer, benefit, cost). Code cannot prove that cut beneficial. MERGE is a design
choice with reasons, not a command to delete history. No issue creation is implied.

`understanding` states prerequisites for correct reasoning. `decision_refs` names
UNKNOWN/HYPOTHESIS/PROPOSAL items whose judgment remains open. `acceptance` states
an observable result, relevant contrast and remaining integrated outcome. `limits`
retains task-specific boundaries. It does not prescribe a recipient's whole method.

Task item context includes its own and ancestor basis/decision refs plus global
preserved constraints. A local constraint can live on a parent shared only by its
descendants. Do not put an obligation on a broad parent unless it applies there.
Rendered text keeps statements as quoted data and source locators explicit.

Only UNKNOWN items have `blocks`; name exactly affected task IDs. The tool follows
their children and dependency descendants. Empty `blocks` means an unallocated or
nonblocking uncertainty, not a global stop. A SUPERSEDED unknown stops propagating;
retain the old map, add source-grounded replacement understanding and reconcile.
Changing the text or type of an existing ID is a substantive impact change.

Coverage dispositions are PLANNED, UNRESOLVED, DEFERRED, EVIDENCE_REPORTED and
SUPERSEDED. PLANNED needs a task retaining the item. EVIDENCE_REPORTED needs source
evidence and cannot resolve an item still typed UNKNOWN. It is a report, not
acceptance. Tasks need not be created for every deferred/unallocated question.

Frontier lists BOUNDED task designs as DESIGN_CANDIDATE, HAS_PREREQUISITES or
DISCOVER_OR_DECIDE and separately retains deferred work and unallocated unresolved/
deferred obligations. Unallocated items remain visible without a global stop.
These labels do not prove
dependency satisfaction, permission or completion. The tooling does not dispatch,
prioritize by score, grant writers, perform approvals or mutate its inputs.

Rendering binds map ID/revision, task ID and SHA-256 over sorted compact UTF-8 JSON
(`ensure_ascii=False`, `allow_nan=False`). This is canonical content binding, not a
file-byte digest or standard signature. Preserve actual issued packets separately.
The CLI refuses to overwrite any input or existing output. It writes a requested
new file only; no automatic directory creation or external write occurs.

Impact compares same-ID maps at increasing revisions. It considers changed task
definitions, referenced sources/items, explicit blocking scope and dependencies.
It reports integration ancestors separately so reviewing a parent does not itself
invalidate all siblings. Global request/purpose/scope/performer changes warrant
broad review. Removed obligations are explicit. Declared coverage/impact can miss
undiscovered risks and undeclared relationships; agents reconcile meaning.
