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
4. Write a compact brief from the task record: aim, why this task, actual inputs,
   decisions/constraints, result, checks, reserved judgments and next action.
5. Deliver through the actual supported route. Keep `prepared`, `sent`, `confirmed`
   and `uncertain` distinct. Only confirmed delivery supports `active` or `returned`.
6. Inspect a real result early. Update the checkpoint at meaningful artifact,
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
not qualify. Separate-review criteria reject declared authors and ancestor authors;
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

Choose a successor on observed understanding: source-grounded decisions, useful
results, detected contradictions and preserved invariants. Supply the current
baseline, decisions/alternatives, open uncertainties, pending returns and the next
two proposed deliveries with their connection. A capability probe and a real next
action give more useful evidence than ceremonial acceptance of a title.

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
