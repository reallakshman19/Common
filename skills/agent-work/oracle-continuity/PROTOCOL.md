# Oracle Continuity Protocol

Version: 1.0.0 · Status: proposed reference contract · 23 October 2026

## Contents

- [Purpose and limits](#purpose-and-limits)
- [Responsibility layers](#1-three-layers-of-responsibility)
- [Role and identity](#2-role-and-identity-model)
- [Core records](#3-core-records)
- [Initiation](#4-initiation)
- [Execution and evaluation](#5-execution-and-evaluation)
- [Worker replacement](#6-worker-replacement)
- [Oracle succession](#7-oracle-succession)
- [Publication and recovery](#8-publication-concurrency-and-recovery)
- [Version and history](#9-version-and-history-rules)
- [Progress projection and adoption](#10-progress-projection-and-adoption)

## Purpose and limits

Preserve a project's purpose and useful work while temporary agent sessions execute,
return results and are replaced. The contract applies to software, learning,
research and engineering. Domain criteria describe what quality means; the core
describes identity, responsibility, evidence and continuity.

This package contains schemas, a read-only reference validator, examples and tests.
It does not start chats, deliver instructions, authenticate people, acquire locks,
publish changes, inspect remote witnesses or establish domain correctness. A valid
record can contain a false declaration. The examples are synthetic; their witness
references and approvals are illustrative and confer no live authority.

## 1. Three layers of responsibility

1. **Protocol:** responsibilities, lifecycle, recovery and decision rules.
2. **Record contract:** JSON structure plus relationships checked by `validate.py`.
3. **Execution adapter:** actual authenticated delivery, compare-and-swap publication,
   exclusive write control, file access, evidence collection and Progress projection.

Deploy layers 1 and 2 for one existing task first. Add an adapter only where it
removes observed manual work. A JSON document alone cannot enforce a transaction.

## 2. Role and identity model

The Oracle maintains purpose, task boundaries, decisions, integration and the next
useful action. It supplies load-bearing context to an executor and retains judgments
not allocated to a capable participant. Medium-reasoning executors receive either a
concrete guided method or an investigation with competing explanations and a useful
discriminating observation. Role/model labels do not establish competence.

**Initial understanding is mentor-supported, not exam-scored.** New agents and
incoming Oracles use [Initial Mentoring](../initial-mentoring/SKILL.md)'s
[First-source-walkthrough alignment](../initial-mentoring/SKILL.md#1-first-source-walkthrough-alignment)
within existing onboarding for the Owner outcome, difficult architecture and
connected next result. Established participants reuse only their own
demonstrated, still-applicable understanding and refresh affected source deltas.
Neither another Oracle's explanation nor a document readback establishes it.

The coordinator owns actual routing and receipts. The executor owns its bounded
artifact. The reviewer inspects the relevant claims without being an author of the
artifact or its declared ancestors. A runner supplies execution where needed. The
Owner controls actual scope/acceptance authority; `authority` references record that
basis without manufacturing it. Responsibilities may share a session where the
project permits, but authorship separation still applies.

Keep these identities distinct:

| Identity | Lifetime | Change rule |
|---|---|---|
| Project | Whole outcome | Stable ID; aim changes increment `aim_revision` |
| Task | One coherent outcome | Stable ID across worker changes; meaning changes increment task revision |
| Logical agent | A named participant across sessions | `agent_id` identifies continuity, not a verified principal |
| Session | One actual execution context | New `id` and generation on replacement |
| Assignment | One task revision, role and executor binding | New ID/generation on reassignment; prior binding retained |
| Artifact | Exact returned bytes | New ID/digest for changed bytes; retain declared parent lineage |
| Oracle epoch | Current project-control generation | Increment exactly once per activated Oracle handover |

An Oracle cutover changes who may issue control commands. Existing executor
assignments can continue when the new Oracle explicitly adopts them. The epoch
does not reset their task identity or imply their execution stopped.

## 3. Core records

`oracle-state.schema.json` defines a closed core: unknown fields and incompatible
schema versions fail. Do not encode consequential facts in unvalidated extensions.

| Collection | Contents |
|---|---|
| `project`, `control` | Aim and its source, domain, active Oracle, epoch |
| `sessions` | Temporary instances, declared roles/lifecycle, capability observations |
| `tasks` | Outcome, real inputs, invariants, dependencies, criteria, current candidate, completion policy, checkpoint |
| `assignments` | Task/revision, recipient, role, generation, delivery, required capabilities, declared write resources, authority |
| `artifacts` | Source assignment, locator, SHA-256, authors and declared ancestry |
| `evidence` | Exact task/artifact binding, method, observer, reported/observed basis, result, witness and limitations |
| `assessments` | Criterion-specific verdict, supporting evidence, exposure, concise rationale and surviving error |
| `decisions` | Method/scope/acceptance/late-return adoption, rationale, alternatives and authority/source |
| `handovers` | Participants, checkpoint, successor binding, cutover status and adopted ongoing work |
| `history` | Ordered publication receipts with unique command IDs |

A source names a version or capture time. An unversioned live source must have a
capture time; merely putting a locator in JSON is not proof that it was read.
Artifacts bind exact bytes. Large inputs may be externally stored and privately
referenced; the core does not require copying them into the public record.

## 4. Initiation

1. Establish a canonical record under existing project authority. Record the Owner's
   aim, best useful artifact, known sources and current uncertainties. Bootstrap with
   revision 1, epoch 1 and one active Oracle. Mark imported claims as reported.
2. Choose one coherent task that advances the aim. Preserve its end-to-end outcome;
   keep later work coarse. Domain criteria specify observable results, and whether
   non-author review, actual user use and acceptance are needed for this task.
3. Confirm executor access and return capability through a small real operation.
   Add browser/runtime/repository requirements only when needed. An active assignment
   requires observed positive evidence for its declared capabilities, including input
   access and artifact return. Capability observations are dated, not permanent.
4. **Before writing a consequential engineering brief or qualifying a new framework**,
   apply [First-source-walkthrough alignment](../initial-mentoring/SKILL.md#1-first-source-walkthrough-alignment).
   The Oracle independently grounds the affected engineering premise and execution
   frontier. Missing sources or unverified meaning limit the dependent claim/action,
   not unrelated safe exploration; do not replace grounding with an exam or new approval.
5. Write a compact brief from the task record: aim, why this task, actual inputs,
   decisions/constraints, result, checks, reserved judgments and next action.
6. Deliver through the actual supported route. Keep `prepared`, `sent`, `confirmed`
   and `uncertain` distinct. Only confirmed delivery supports `active` or `returned`.
7. Inspect a real result early. Update the checkpoint at meaningful artifact,
   decision or evidence boundaries. Resume from the latest trusted checkpoint after
   unexpected session loss; do not wait for a hidden context percentage.

No scored onboarding exam or Owner approval at every checkpoint is required. Reuse
existing authorization and useful completed work. Inspect essentials and act.

## 5. Execution and evaluation

Task lifecycle is `planned`, `in_progress`, `blocked`, `submitted`, `complete`,
`deferred` or `cancelled`. This describes work administration, not confidence or
learning. Evidence and user use are separate records.

Assignments move among queued/active/blocked/returned and terminal
superseded/cancelled states. A returned assignment may resume a repair within the
same task definition. Meaning changes require a new task revision and an adopted
scope decision; a new assignment binds that new revision. Changing the recipient
requires a replacement binding and worker handover.

The Oracle reads the artifact, compares the original criteria and invariants,
reconciles findings, and selects a bounded continuation. Capture a concise decision
rationale, not private reasoning traces. A difficult unallocated measurement or
model judgment remains the Oracle's responsibility to resolve or route.

A supported assessment requires observed positive evidence for the exact task
revision, criterion and artifact. A reported PASS, missing witness or NOT_RUN does
not qualify. **A synthetic-fixture PASS, source-file count, hash check or local
ZIP-integrity test is evidence only for its measured scope**: it does not establish
original-model semantic transfer, meaningful benchmark performance on the Owner
input, a recipient-accessible Common relay, or engineering release. Record
benchmark method, actual sample size, environment, warm-up and measured source
separately; three timed samples cannot justify a reliable empirical p95 claim.
For material Oracle-authored artifacts retain `SELF_ASSESSED` and
`NOT_TRANSFERRED` where independently checked engineering meaning or actual
receiver retrieval is missing. Separately reconcile the original model/field
source and access path before downstream use. Separate-review criteria reject declared authors and ancestor authors;
the record must disclose source/fixture exposure. Different sessions establish only
declared session separation, not authenticated principal independence or blindness.

Current observed failures cannot be omitted while the current claim remains
supported. Correct a faulty measurement using a new evidence record that explicitly
supersedes the original, with a source and explanation; retain both records. Update
affected assessments explicitly. Do not rewrite a failed result into a PASS.

`complete` requires supported current criteria, plus observed use and scoped
acceptance when required by that task's policy. A technical check or successful
supported repeat cannot establish independent learning/transfer: that must be a
separate criterion with suitable observations. Unrelated checks are not imposed on
every task, and one task's failure does not globally stop other work.

## 6. Worker replacement

1. Save actual artifacts and a checkpoint: current outcome, known facts/claims,
   source/decision references, unresolved issues and exact next operation.
2. Inspect delivery and in-flight side effects. Attempt to stop/reconcile the old
   executor through its actual transport. Mark unknown execution as unknown.
3. Prepare a successor session and assignment with the same task ID, next
   assignment generation and `replaces_assignment_id`. Confirm its capabilities.
4. Publish one cutover: predecessor assignment becomes superseded/cancelled,
   successor binding becomes current, and the handover becomes activated.
5. Successor checks essential originals/current bytes and performs the next action.
   Preserve historical verdicts with their original scope; reassess affected claims.

Do not activate a successor on the same uncontrolled write surface when the old
executor may still write. Revoke actual write access or use isolated branches/output
locations until reconciled. Declared resource IDs catch exact-ID conflicts only;
the adapter must map overlapping paths/resources to a common scope and enforce it.

Late predecessor returns remain historical. Selecting one as the current candidate
requires an explicit adopted `adopt_return` decision for those bytes and revision.
Useful work can be salvaged without silently restoring old authority.

## 7. Oracle succession

### Live WBS continuity is the handover, not just the four files

**Concrete regression from CIIFR (25 October 2026):** A genuinely published four-document Geometry handover mentioned G1/G2 and linked the Progress Page, but did not itself reconcile existing **WBS 3 / 3.1–3.4** against the live milestone status and the newer **CIIFR-MAP WBS 5.x** work. The successor accurately repeated physical NODE/ELEMENT facts and flagged a Cycle rev4/G2 contradiction, yet a later Oracle still planned new Geometry work without first explaining whether it **continued, superseded or reused** WBS 3.x. **Document readback and the successor's concept summary were not proof of WBS continuity.** Source witnesses: [existing Progress Page CIIFR](https://reallakshman19.github.io/progress-page/#/ciifr/progress), [XCU Geometry #166](https://github.com/reallakshman19/XML_Compare_Utilities/issues/166), [CIIFR-MAP #179](https://github.com/reallakshman19/XML_Compare_Utilities/issues/179), and [CIIFR Cycle rev4](../../../oracle-cycles/ciifr/CURRENT.json). Each is a time-varying source; do not promote an old page snapshot to active authority.

**Outgoing Oracle's actual executable handover:** For the **entire selected project**, name the current WBS root and relevant live branches with **stable identifiers**, parent/child dependencies, owner and assigned chat (when actually known), accepted/returned/pending receipt, exact code/fixture candidate, next **one task/action**, and its **immediate downstream WBS**. Read the latest existing native roadmap/issue, canonical activated Cycle (if any), and Progress Page Home/WBS *when present*. Distinguish **live native facts**, **page projection and its observed freshness**, and the outgoing Oracle's interpretation. A directory of links or four knowledge documents alone does not provide this task/actor/next-work map. Reuse existing WBS records and links, not a new master register or another mandatory document.

**Receiving Oracle's first actual continuity action:** *(G9v3.5 regression, 28 October 2026: a directly Owner-appointed OTM-as-Oracle skipped this step, and the inherited WBS lived only in a handoff folder while the Progress page showed an older plan; a parallel WBS followed. This action applies to every receiving Oracle, including a coordinator the Owner appoints as Oracle. Read the inherited WBS from the project's Progress page tab, its current revision and WBS milestones; if the WBS is not on the page, putting it there is the first act, before any new card.)* Compare that inherited WBS root/branches to **current** native issues/PR heads/returns, Owner amendments, existing Page 3.x/5.x (or whatever this project uses), and any activated Cycle. Explicitly say which WBS continues, depends on, replaces or coexists with which earlier WBS **before creating a parallel workstream or issuing an Agent OnBoard**. If two authorities conflict, reconcile the smallest existing record *within the receiving Oracle's real authority*; do not just note the contradiction and continue as if it did not affect routing. A candidate successor in **READ_ONLY** mode reports a **concrete proposed source/record correction to the incumbent** rather than editing state or dispatching. An already Owner-appointed active Oracle resolves it and advances work. No new permission slip or ritual review is required for normal source/coordination work.

**Worker's WBS-context minimum:** An Agent OnBoard must communicate the **overall user journey and current project stage in a short paragraph**, the agent's specific WBS and upstream returned evidence, and the **next WBS/result** that consumes its output, including a source/wrong-case coupling. This avoids a context-free leaf while keeping project-wide WBS/people/control ownership with the Oracle. A worker does **not** recreate every project handover or obtain Oracle control.

**Truthful completion language:** `KNOWLEDGE_CHECKPOINT_PUBLISHED` means the knowledge bytes were published and read back, **not** `WBS_RECONCILED` or `SUCCESSOR_CAN_CONTINUE`. Only claim *WBS continuity observed* after the recipient's actual source-grounded comparison and one executable native return. Missing/old Page data becomes a clearly attributed `PAGE: PENDING` source-reconciliation task, **not** a blanket project HOLD. Carry any genuinely unsolvable Owner-only decision separately while independent work continues. This paragraph strengthens the already existing source/continuity expectation; it adds **no new onboarding gate or acceptance status schema**.

### Four-document no-loose-end knowledge handover (Owner, 25 October 2026)

**Source-backed reference for this Common protocol project:** [CONCEPT_NOTE](../../../relay/AGENT_WORK/common-agent-work-oracle-continuity/knowledge-20261025/payload/CONCEPT_NOTE.md), [ARCHITECTURE_COMPLEX_LOGIC](../../../relay/AGENT_WORK/common-agent-work-oracle-continuity/knowledge-20261025/payload/ARCHITECTURE_COMPLEX_LOGIC.md), [ARCHITECTURE_DECISIONS_AND_CHALLENGES](../../../relay/AGENT_WORK/common-agent-work-oracle-continuity/knowledge-20261025/payload/ARCHITECTURE_DECISIONS_AND_CHALLENGES.md), [ORACLE_HANDOVER](../../../relay/AGENT_WORK/common-agent-work-oracle-continuity/knowledge-20261025/payload/ORACLE_HANDOVER.md), and [the successor prompt](../../../relay/AGENT_WORK/common-agent-work-oracle-continuity/knowledge-20261025/ORACLE_SUCCESSOR_PROMPT.md). These are **Common Agent-Work's own knowledge sources**, modeled in depth/claim discipline on the immutable *other-project* 3DC golden fixture. Reuse the same four knowledge classes **for each real target project** from that project's actual Owner words, original code/fixtures, decisions and native evidence. **A status-only checklist, one URL or a generic copy of this Common packet is not that project's domain knowledge.**

**Close loose ends without extra gates:** The incumbent Oracle must make the conceptual, architectural, decision and execution frontier retrievable at immutable source revisions; reconcile stale active/returned assignments and native/relay evidence; provide one **immediately executable** action with owner, source, expected observation and native return; and preserve two connected outcomes. The Oracle should **attempt and resolve** all source/coordination/custody steps within its current authority instead of requesting an Owner approval or independent review to perform them. A missing test limits only its tested claim, not disjoint safe work. An actual protected native writer/merge/release guard still applies to the **affected operation**. Escalate **only** an unsolvable permission/input/authority conflict or a reserved Owner decision, identifying what was attempted and the smallest Owner response needed. No compulsory five-step list or new review status is created.

**Two distinct outcomes:** `KNOWLEDGE_CHECKPOINT_PUBLISHED` requires a genuinely published/read-back exact-source packet, not an unmerged PR or local ZIP. `ORACLE_CONTROL_TRANSFERRED` separately needs actual selected successor identity, Owner/native cutover authority, epoch/CAS readback, previous writer isolation and explicit adoption or disposition of **every** active/pending worker and reviewer. A successor may be **UNASSIGNED** while the incumbent continues ordinary work; source comprehension, static CI, a different chat ID and a packet link cannot silently activate control. Use the established artifact-transfer priority: **Common public-safe Option 1 FIRST; Owner-designated Google Drive Option 2 NEXT; either mandatory for completed artifacts; `sandbox:` is `LOCAL_ONLY / NOT_TRANSFERRED`**. Receiver measurement, independent technical review and product release each remain separate.



**When to prepare a handover:** apply observed project continuity, repeated corrected failure, demonstrated missing capability or explicit Owner/governing OTM preference. The [measurable agent/Oracle trigger pilot](../oracle-standalone/references/CHANGEOVER.md#2a-measurable-handover-triggers--optional-evidence-based-pilot) is **proposed guidance**, not a compulsory numerical takeover rule or authority grant. Normal Oracle refresh is changed-evidence-only; neither long chats nor task completion alone requires succession. Follow the actual native coordination mode and existing cutover authority.

Choose a successor on observed understanding: source-grounded decisions, useful
results, detected contradictions and preserved invariants. Supply the current
baseline, decisions/alternatives, open uncertainties, pending returns and the next
two proposed deliveries with their connection. A capability probe and a real next
action give more useful evidence than ceremonial acceptance of a title.

### Knowledge transfer — Owner-selected golden fixture

**Golden content reference:** [3DC-XML-CII Oracle continuity package, immutable commit `bf02e54e`](https://github.com/reallakshman19/Common/tree/bf02e54e1b453c3206ae366de7d65f41c94ab0d4/relay/AGENT_WORK/3DC-XML-CII/oracle-continuity-20261025/payload). The Owner selected this project-specific package as the **minimum-quality example** for Oracle handover knowledge, not as a universal XML/CII method, validated engineering result, or published control-epoch change. Its four linked documents are a project concept note, complex architecture/logic, architecture decisions/challenges, and an outcome/evidence/assignment handover.

Before describing a handover packet as complete, the incumbent must make the following **four knowledge classes** retrievable and understandable from actual cited source material:

1. **Concept:** original Owner aim/amendments, why the product exists, user journey, expected outcome and prohibited scope.
2. **Architecture and difficult logic:** current component/data/control flow, critical state/identity boundaries, non-obvious algorithms and invariants, with explanations or concrete examples of *why* they exist.
3. **Decisions and challenges:** consequential design choices, considered/rejected alternatives and their rationale, surviving wrong cases and a discriminating check.
4. **Execution frontier:** exact working candidate and verified versus reported results, fixture custody/access, active assignments/returns, HOLDs, two connected next deliveries and **one immediate authorized action**.

A status-only A–G checklist, a set of unread links, or an agent roster does **not** establish these knowledge classes. Reuse existing Project Home or project-native architecture/decision records wherever sufficient; **four distinct new files are not mandated**. If content is genuinely absent or inaccessible, label the specific knowledge gap and keep its assurance unknown rather than inventing an explanation or claiming full transfer.

The successor checks the relevant original sources and demonstrates usable understanding by explaining an important design invariant, a rejected alternative or surviving wrong case, and the next evidence-bearing operation. This is targeted source reconciliation, **not a scored onboarding exam**, engineering review, file-byte receipt, independent PASS, or grant of Oracle control. Follow the selected native authorization and epoch/cutover rules below.

**Successor mentoring and source challenge:** Apply [First-source-walkthrough alignment](../initial-mentoring/SKILL.md#1-first-source-walkthrough-alignment)
and its [incoming-Oracle boundary](../initial-mentoring/SKILL.md#3-special-case--incoming-oracle).
The successor independently grounds the project and challenges stale claims; it
does not inherit demonstrated understanding from the outgoing session. A candidate
reports concrete corrections read-only. A directly Owner-appointed active Oracle
uses its actual coordination scope without predecessor endorsement; shared-write
replacement still needs the real native cutover and isolation below. Preparation,
appointment and actual control/custody remain distinct, with no mentoring approval gate.

In a CII example, ELEMENTS/RIGID/NODENAME counts, node/pointer census and 13 green synthetic
parser tests **do not verify** field-specific inheritance, sentinel
semantics, auxiliary ownership or downstream effective properties. Mark those
unknown until independently grounded in original CII, existing parser and
appropriate vendor layout; if uncertain, the first successor task is bounded
**read-only source reconciliation**, not fresh writer/transfer modules. This
conversation provides understanding, **never automatic control or approval**.

Prepare a handover with the old/new Oracle sessions, epoch n to n+1 and a checkpoint.
At cutover, retire the prior Oracle instance, activate the new control binding and
explicitly list ongoing assignments it adopts. Their execution can continue.
Record any scope or priority changes separately; succession itself does not rewrite
the aim, reset reviews, create new release authority or silently cancel all workers.

The validator checks the declared handover/epoch chain. The execution adapter must
reject stale Oracle control commands; it cannot rely on the old chat obeying a text
instruction after retirement.

## 8. Publication, concurrency and recovery

`oracle-command.schema.json` binds a proposed state file's exact bytes to a command
ID, project ID, enrolled actor, expected previous revision and Oracle epoch.

Keep proposed files separate from the canonical published record. Validation does
not activate their assignments or turn their proposed history entries into actual
publication receipts. The same state shape is used for preparation and publication;
its trusted storage reference and committed receipt establish which it is, rather
than a self-declared draft/live flag. Do not point Progress or dispatch tooling at
an uncommitted proposal. Preparation timestamps are not evidence of actual delivery.

The actual publisher must execute the following as one controlled operation:

1. Authenticate the actor and resolve authority outside the supplied JSON.
2. Look up the command ID. For an exact retry, return the original receipt. Reuse
   with different payload bytes is a conflict. Do not resend external messages.
3. Read the canonical revision/epoch. Compare with both command preconditions.
4. Validate the proposed state against that exact previous snapshot and command.
5. Commit using atomic compare-and-swap against the same previous state. Store the
   new state and receipt together, then expose the new revision.

For a file/Git adapter, use one actual publisher and an exclusive local lock or
conditional update against the expected Git object. Atomic rename alone does not
resolve two readers validating against the same preimage. A database adapter uses
a transaction and conditional revision/epoch update. The supplied checker performs
none of these writes or locks.

External side effects need an intent and reconciliation record: save intent before
sending, inspect the destination afterward, and preserve uncertainty after a crash.
A timeout or failed readback never means the first send did not happen. No
exactly-once delivery guarantee is made. If the predecessor is unavailable, recover
from authoritative records and actual target observations, leaving gaps explicit.

## 9. Version and history rules

- Artifact/evidence/assessment/decision/publication records are append-only across
  compared snapshots. Corrections use explicit supersession, preserving history.
- Sessions and assignments retain stable identity fields. Superseded/cancelled
  assignments and retired sessions cannot revive under the same identity.
- A task revision change requires an adopted scope decision. Aim revisions preserve
  their source. Keep previous state snapshots to retain prior task definitions.
- Unknown schema major versions fail. Additive contract changes require an explicit
  schema/version migration and tests; a field typo never becomes a silent extension.
- A single snapshot check cannot prove that history was preserved. Use `--previous`
  against the actual canonical predecessor; keep the external version history.
- Publication history is an audit chain, not a full event-sourcing implementation.
  It neither reconstructs unknown pre-baseline activity nor authenticates timestamps.
- Timestamps require an offset and a valid calendar value; this reference profile
  excludes leap seconds. Capability age limits are domain/environment policy.

## 10. Progress projection and adoption

One canonical task record supplies a Progress milestone. Render its outcome,
candidate/launch reference, assignments, latest applicable verdicts, actual use,
acceptance, checkpoint and next actor. Keep author-return time, evidence observation
time and last publication time distinct. Recompute applicable evidence on candidate
or task revision changes. Do not average these facts into a completion percentage.

Existing fields can remain adapters:

| Existing Progress field | Canonical basis |
|---|---|
| aim / aimSrc | project aim / source |
| wbs or milestone identity | stable task ID mapping, stored once |
| canDo | task outcome qualified by actual use/evidence |
| cap / capSrc | conservative projection of applicable assessments, use and acceptance |
| agent block | one assignment generation with its task and session |
| next actor / next text | unresolved responsibility plus checkpoint next action |
| fixtures | task inputs and domain sources |
| Timeline | publication history linking the original evidence/decisions |

No projection may upgrade a verdict. Public views use an explicit allowlist; private
inputs, actual chat links, credentials and unrestricted checkpoint text stay private.
This core intentionally has no automatic public exporter.

Adopt in one current task: create the state, confirm capabilities, attach actual
receipts, validate changes and exercise a simulated worker/Oracle cutover on a copy.
Keep the canonical records private until a public projection is deliberately built.
Demonstrate a real successful continuation before enabling unattended publication.

## Source basis

- Common Oracle guidance: https://github.com/reallakshman19/Common/blob/main/skills/agent-work/task-decomposer/references/ORACLE_USE.md
  (inspected blob 56ce02b6677c6a196f95dc9051e444d484154d9e).
- Existing prototype-card schema: https://github.com/reallakshman19/Common/blob/main/skills/agent-work/prototype-first/schemas/slice-card.v1.json
  (inspected blob 8b9765a46386b8bd1a2923011452e52152945162).
- JSON Schema Draft 2020-12: https://json-schema.org/draft/2020-12
- Conditional schema validation: https://json-schema.org/understanding-json-schema/reference/conditionals

This is a new proposed contract, not a claim those repositories implement it.
