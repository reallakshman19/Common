# Team, surface and native-return adapters

## Contents

- [Roles and capability](#roles-and-capability)
- [Choose support from the work](#choose-support-from-the-work)
- [Two-schema compatibility](#two-schema-compatibility)
- [Audience and surface APIs](#audience-and-surface-apis)
- [Tracker identity and transport](#tracker-identity-and-transport-examples)
- [Native-return envelope](#native-return-envelope)
- [Reconcile and resume](#reconcile-and-resume)
- [Examples and limits](#examples-and-limits)

## Roles and capability

Separate domain profiles from roles, support needs and transport. A UI researcher
can need specialist investigation, a worker can run a precise numerical contrast,
and a teacher can need both education and quantitative profiles. No fixed pass
count, compulsory agent count or automatic model upgrade is added.

For copyable role prompts and the thought process for applying them, use
[Applying guidance](APPLYING_GUIDANCE.md). It explains support/evidence selection,
assumption discipline and concrete pitfalls, with paired golden cases. These aids
do not change the schema/API contracts below or the native project's authority.

| Audience | Responsibility of the view |
|---|---|
| `owner` | Purpose, proposed direction, conditions, evidence changes and real decisions |
| `designer` | Reconstruct/challenge assumptions, choose valuable work, reconcile returns |
| `worker` | Execute one bounded task with method/support and meaningful evidence |
| `specialist` | Apply relevant domain expertise and expose applicability/assumption limits |
| `reviewer` | Assess original conditions, returned artifacts and falsifiers; report independence limits |
| `coordinator` | Assess task fit, dependency relationships, unresolved work and next candidates |
| `successor` | Recover source/plan identity, actual evidence, remaining work and separately selected protocols |

Roles are not thinking levels or authority grants. One participant can hold several
roles. A lower-thinking worker needs appropriate guidance and tools; a deeper
problem needs sound synthesis. Neither can be established from a model name or
a self-declared high effort setting. Ask for a meaningful prediction/contrast at
fragile boundaries; use actual evidence rather than an acknowledgment as support.

For actual execution use [Oracle execution](ORACLE_EXECUTION.md). Oracle combines
appropriate existing Designer/coordinator responsibilities; it is not an eighth
`audience` value or a new participant role enum. Its entry prompt assigns operating
duties, while these APIs continue to prepare documents and inspect declared records.

## Choose support from the work

The Owner can say: “Use Nudge Designer on this problem. Keep the original goal,
check what is known, and give the available agent the next useful assignment.”
The Designer maintains sources, task fit and records. Add a constraint such as
“the worker has no browser” or “I want onboarding before a new task” when relevant;
the Owner need not specify schemas, roles or a pass count.

| Situation | Practical adaptation | Evidence that changes direction |
|---|---|---|
| Narrower or unfamiliar worker | GUIDED method, concrete inputs, bounded deliverable, worked contrast where useful and reserved judgment | A prediction/trace plus actual positive and negative results; adjust support if it exposes misunderstanding |
| Capable generalist, uncertain diagnosis | OPEN investigation with competing explanations and a discriminating observation | Observation that rules out an explanation; do not prescribe a speculative patch |
| Deep domain question | Qualified specialist task with model assumptions, units/applicability and a separate challenge when valuable | Domain evidence against original conditions; qualification remains outside role names |
| Mixed team or unavailable tool | Fit each task separately; use available readers/workers; keep source and shared-write ownership explicit | Actual access restriction and affected scope; retain useful independent work |
| One available agent | Hold several roles explicitly; self-check and expose correlated/qualification limits | Real checks, without calling a second view independent review |
| Recovery or onboarding | Successor reconstructs source identity, issued history, current understanding and native results | Reconciled differences and a current start reference; use the selected handover protocol for mode/approval semantics |
| Large cross-domain work | Parent outcomes, coherent child tasks and composable profiles | Integrated result plus scoped impact; child completion alone cannot accept the parent |

For deeper work, improve the explanation/model and choose evidence with enough
power to distinguish alternatives. For a narrower worker, reduce avoidable choice
and supply the concrete reasoning support. Complexity alone is not a reason to
multiply phases or create more agents. Tool failure, unsupported judgment or a
contradicting result calls for scoped revision, not another identical attempt.

## Two-schema compatibility

`intent/v1` is unchanged. `plan/v1` remains valid with no team fields. Explicit
`plan/v1.1` permits `participants` and per-nudge `assignment`. New fields under
`plan/v1` fail; old consumers must not silently strip or downgrade the new version.
There remain exactly two JSON schema documents.

Participant fields: `id`, `label`, `roles`, `capabilities`, `tools`, `model`,
`reasoning_effort`, `configuration_basis`. Each capability/tool claim has `id`,
`status` AVAILABLE/UNAVAILABLE/UNKNOWN, `basis` OBSERVED/REPORTED/UNKNOWN,
`evidence_refs` into intent sources, and `note`. OBSERVED requires references,
but references are not independently authenticated by this package.

Assignment fields: `role`, nullable `participant_id`, `capabilities`, `tools`,
`support` GUIDED/OPEN, nullable `method`, nullable `worked_example`,
`reserved_decisions`, `review_of`. Needs have `id` and `importance`
ESSENTIAL/HELPFUL. GUIDED requires a concrete method. No requirements yields
NOT_ESTABLISHED, not automatic fit. Unassigned legacy work uses supplied global
worker context without inventing a participant.

`fit` returns RECORDED_FIT, REPORTED_FIT, NOT_ESTABLISHED or MISSING_REQUIREMENTS.
All retain `qualification_verified=false` and `execution_authorized=false`.
Missing requirements affect that assignment only. Capabilities and tools are
declared records; the host or relevant reviewer establishes actual suitability.

## Audience and surface APIs

`adapt(intent, plan, nudge_id, profiles, audience, surface, recipient_id=None,
report=None)` returns a packet containing `content`, exact issued `binding`,
fit information, exact prepared-content SHA-256 and delivery/verification limits.
It never mutates inputs. Preserve a delivered packet and its digest in the existing
native record; re-rendering later does not prove which instruction was actually sent.
The selected audience/recipient views the work; it does not change the assigned
actor or reserved decisions. A reviewer viewing its own recorded contribution
gets SAME_RECORDED_PARTICIPANT; even different IDs cannot prove independence.

| Surface | Prepared output and boundary |
|---|---|
| `plain` | Portable Markdown content inside the packet |
| `github` | Proposed Markdown body; no issue/PR posting |
| `nextnudge-manual` | Manual-copy draft using the existing type vocabulary; no native import or sent instruction |
| `buddy-checkpoint` | Supporting reconstruction/evidence material; no mode/stage completion or continuation approval |
| `delivery` | Brief for the explicitly selected delivery protocol; no implicit version, thinking or handover default |

These adapters prepare documents, not service-native write requests. For a native
application import or automatic transport, first inspect the exact target contract
and obtain task-appropriate authorization. No target UI or external system is
changed by these APIs. Keep NextNudge Copy/Mark sent and frozen-instruction rules.

CLI `adapt` writes packet JSON; the presenting agent shows its `content` to the
appropriate audience. Owners need not run commands or operate internal fields.
`render` remains the direct seven-element Markdown output and now honors per-task
participant/support data. GUIDED examples are references, not proof of transfer.
Audience selection is a view, not a new allocation. Use a separate issued nudge
when assigning a new specialist/review deliverable; cross-plan review inputs are
source references to the other task's immutable records.

## Tracker identity and transport examples

Before issuing a manual packet, identify the existing system of record. Distinguish
canonical assignment ID/revision/binding, a tracker's move ID and the reply's link
to that move. Preserve an explicit mapping; do not silently replace a frozen packet's
ID or treat a new app ID as the old task. Reserve a tracker ID before issue, record
an external ID verbatim, or document an unambiguous alias according to the actual
surface contract. These are choices, not a universal preference for app IDs.

Where the channel uses `ACK <id>`, state which mapped ID the response echoes.
Link the reply to the corresponding issued snapshot; refuse ambiguous correlation
until reconciled. Preserve the designed content, purpose/conditions, inputs, scope,
return/uncertainty rules and actual send history. An ACK neither establishes task
execution nor replaces full content binding. The manual adapter prepares content;
it does not implement tracker-native import, reply linking or a watcher.

Example: assignment `A-OBSERVE` revision 2 is recorded as move `MOVE-71`; the chosen
channel contract requests `ACK MOVE-71`. Its returned artifact still names/binds
`A-OBSERVE` revision 2. A reply about `MOVE-70` must not be admitted as that return
merely because its prose looks similar.

An unreliable transport can add a leading BOM, garble decoded punctuation or
duplicate a summary while the original file remains correct. Keep original bytes
and compare the artifact's full byte digest separately. If the channel permits it,
strip one leading BOM only in a separate working view for ACK matching; record that
interpretation and retain the raw copy. Report mojibake/duplicates instead of silently
repairing evidence. A prefix is display convenience, not full digest verification.
These examples add no automatic normalization to `receive` or any app. Watching the
actual reply destinations is a controller responsibility, not a thinking-skill API.

## Native-return envelope

Preserve a textual native report as an exact content string. For a PDF, spreadsheet,
image, solver output or other binary artifact, use `content: null` with a locator;
intake records REFERENCE_ONLY and does not invent decoded content or a digest.
Use an authorized domain reader to assess it. Do not parse PASS, merge
status or prose into authority. Use `bind` to obtain the header for the issued
snapshots. Its plan/nudge/intent digests detect content substitution; they do not
authenticate the actor or establish truthful execution.

The strict intake API uses exactly these top-level fields:

| Field | Required substance |
|---|---|
| `binding` | Exact output of `bind` for the issued snapshots and task |
| `actor_id` | Assigned participant ID, or null when genuinely unassigned |
| `claimed_status` | COMPLETE, PARTIAL, BLOCKED or NOT_RUN; still a claim |
| `native_report` | `format`, nullable `locator`/`revision`, exact text `content` or null with a required artifact locator |
| `attempts` | Nonempty objects: `id`, `action`, EXECUTED/NOT_RUN/BLOCKED `state`, `observed`, locator-list `evidence` |
| `findings` | Objects: declared `kind`, `text`, `item_refs`, `attempt_refs` |
| `source_observations` | Objects: `source_id`, nullable observed `revision` |
| `contributors` | Recorded participant IDs contributing to the work |
| `unresolved` | Remaining facts, evidence and integrated outcomes |
| `next_proposal` | Suggested continuation within actual authority |

Finding kinds: OBSERVATION, DRIFT, IMPROVEMENT, NEW_ISSUE, ASSUMPTION_CONFLICT.
DRIFT names at least one original requirement/constraint. A declared finding is
not semantically classified by Python. References outside the nudge context stay
visible for scope assessment; they do not expand the assignment.

COMPLETE requires at least one claimed EXECUTED action. A completed publication
can still leave the intended repair NOT_RUN; distinguish the bounded deliverable
from the parent outcome. BLOCKED records the attempted action, observed restriction,
affected context and next feasible proposal. Preserve independent useful work.

`receive` validates structure/binding and returns the native content unchanged with
its UTF-8 SHA-256. Evidence locators are checked for display syntax, not fetched.
Mismatched source revisions are recorded as discrepancies rather than discarding
historical observations. Unobserved/unpinned sources remain explicit; no freshness
authentication, accepted outcome, verified execution or authority is produced.

## Reconcile and resume

1. Keep issued intent/plan and original native return immutable and discoverable.
2. Intake against the exact issued snapshots; a changed plan is not the old task.
3. Designer assesses evidence, competing explanations, scope and remaining outcomes.
4. Correct drift, revise disproved hypotheses, record new issues and assess useful
   improvement proposals under existing authority. Ask the Owner only for a real
   unresolved choice; unrelated eligible work can continue.
5. Update the working intent/plan, run `impact`, review affected conclusions and
   issue a visible correction when needed. Preserve sent instructions/history.
6. Check the integrated outcome separately. Publish the native evidence through
   the project's existing authorized path, then leave a current start reference.

Dependency, parent and `review_of` descendants participate in impact/independence
candidate calculations. Candidates are advisory and need current source/tool/scope
assessment. The adapter is not a scheduler and does not create workflow locks.
The coordinator retains actual assignment, shared-write ownership and execution
budget responsibilities under the selected project protocol. Multiple readers of
a source do not imply conflicting writers. No adapter spawns agents, starts timers
or chooses an automatic continuation count.

## Examples and limits

The `team-cycle` example demonstrates participants, a guided worker, review
relationship and native-return envelope. Its supplied return is explicitly NOT_RUN;
automated runtime/replay tests are reported separately. Fresh role execution/review
pilots use isolated task folders and actual local artifacts, without reading worked
answers. They do not establish lower-model capability, learner outcomes, live UI
repair, FE solver validity or engineering acceptance.

The [actual role-cycle reference](../examples/adapter-cycle/ASSESSMENT.md) preserves
worker, specialist and reviewer issued snapshots/native outputs, plus a separate
Designer revision. It shows an inconsistent handover and unsupported learner fact
being caught and reconciled after structural checks passed. Start from its current
reference for direction and original snapshots for historical intake.

If a host lacks Python, present the prose assignment and retain NOT_RUN checks.
Do not substitute it for a project's required validation. Deeper reasoning and
appropriate domain qualification remain responsibilities of the selected agents.
