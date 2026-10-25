# Agent-work operating guide: modules and detailed reference

**Documentation navigation:** [START HERE — role/mode entry](START_HERE.md) · [Entry process maps A–E](ENTRY_PROCESS_MAPS.md) · [Project Home and fixture custody](PROJECT_HOME_GUIDE.md) · [Extended operating reference](OPERATING_GUIDE.md). Read only the branch relevant to your current task; these are not four compulsory stages.

**Artifact transactions:** For current Oracle↔agent inputs and returned files, use [Common artifact relay](ARTIFACT_RELAY.md) (public-safe Common `relay/` path preferred; private Google Drive custody only for restricted bytes/fallback). The [Project Home guide](PROJECT_HOME_GUIDE.md#fixture-maintenance-and-oracleagent-artifact-exchange) describes how the page records the exact source for new agents. This extended guide preserves historical methodology; for current execution enter through START HERE and the five maps.

## Contents

- [Start with a short request](#start-with-a-short-request)
- [Choose only useful modules](#choose-only-useful-modules)
- [Contribute before handing over](#contribute-before-handing-over)
- [Use an Oracle OnBoard Prompt](#use-an-oracle-onboard-prompt)
- [Find task-specific support](#find-task-specific-support)
- [Adapt to available participants](#adapt-to-available-participants)
- [Carry work end to end](#carry-work-end-to-end)
- [Preserve the handoff](#preserve-the-handoff)
- [Use schemas when helpful](#use-schemas-when-helpful)
- [Follow the worked examples](#follow-the-worked-examples)
- [Start the real LFEA test](#start-the-real-lfea-test)

Use this as an operating guide, not another skill, runtime controller or required
sequence. Start from human intent and actual sources. The available agent maintains
records and selects useful support. Roles, modules, JSON and helper scripts are
optional; no CI, role quota or new execution/acceptance gate is introduced.
The optional Gatekeeper module adds label rules (DRAFT, CHECKED, VERIFIED,
RELEASED) for work that will be shown or released. They are label rules, not
execution gates: work continues, and only the label shown is limited. Each check
has a fallback, and a missing anchor narrows or qualifies the label.
When selecting a separate delivery protocol, follow its scoped requirements; see
the task-specific support below. This guide does not silently select one for you.

## Start with a short request

Owner, for end-to-end work:

> Use this guide for <goal>, using <original sources/candidate>. Select the modules
> that help and use the participants/tools available. Carry the authorized work
> through execution, evidence inspection and integrated verification; keep the
> records and unresolved outcomes for me.

Owner, for review only:

> Review <exact candidate> against <original purpose/sources> using Independent
> Reviewer. Show actual evidence, findings, coverage, independence limits and the
> next useful action. Use the available participants; preserve the original artifact.

Supply natural language and available references. The agent reconstructs missing
context from accessible authoritative records, distinguishes unknowns and asks only
about consequential missing meaning/authority when needed. A source link is not a
claim its contents were read. Keep the Owner's interface short.

When a skill is installed, use its name. Otherwise read its `SKILL.md` at the
selected source revision and follow the relevant guidance with available tools.
Record the revision used; merely naming a skill does not install or invoke a host
capability. A reference to another module does not create a dependency on it.

**Owner-selected artifact relay (24 October 2026):** For Oracle↔agent handoffs that include a file/workpack/output, follow [Common artifact relay](ARTIFACT_RELAY.md) even if the file was initially supplied through an upload, `/mnt/data`, or a `sandbox:` link. Such a link is staging, not verified cross-chat delivery. Use the separate public-safe `relay/AGENT_WORK/` namespace or an authorized private byte store with a sanitized relay record; do not touch the active V3.1 `relay/` execution ledger. Preserve the selected protocol's custody rules and Owner acceptance boundary.

## Aim first, and keep the modules in sight

Lesson 1 (Owner, 22 Oct 2026, Lesson 1: CoordinatorLandingpage #1 comments 6339599529, 6339795835, 6339862645): twenty agents and thousands of lines produced no learner output because no aim was written down and the process was built for a corporate product. So:

- **No work without a written aim.** The project's aim is the Owner's words, on its Progress page tab (`project aim`). If it is missing, ask the Owner before planning.
- **Match the quality bar to the use.** A personal-use product skips rights, publication, custody and whole-bank gates ([Gatekeeper](gatekeeper/SKILL.md), personal-use profile).
- **The learner is the measure:** one topic end to end and in front of the learner before the next; small pieces, merged often.
- **Keep the modules visible** where people already look: every task packet carries an `Aim:` line and a `Modules:` line naming the module each step uses; every Oracle prompt carries the table below; each Progress page tab links the modules under its aim.

Lesson 2 (Owner, 23 Oct 2026: CoordinatorLandingpage #1 comments 6354803323, 6354995849; #156): one builder chat, steered by the Owner on the Owner's real file, gave the Owner a tool to run locally in about seven hours, where the multi-agent route was estimated at 40+ hours and five agents. So, by default ([Prototype-first](prototype-first/SKILL.md)):

- **Build first, on the real inputs.** Every step ends in something the user runs with one command or one URL; the Oracle writes each step as a slice card.
- **The user tries it, then the next card.** Evidence follows a working prototype; an independent check runs where a mistake would reach the real world, before that use.
- **The benchmark is R0** (CIIFR-S1): compare each project's time to first runnable and its cost with it.

## Choose only useful modules

This parent is a collection of independent packages. Select the nested folder
containing the module's own `SKILL.md` when reading, copying or registering a
module with an available host. Keep the names `task-decomposer`, `nudge-designer`,
`independent-review` and `gatekeeper`. There is no parent skill to install and no
assumption that a host scans nested folders automatically. The four source roots are
`skills/agent-work/task-decomposer/`, `skills/agent-work/nudge-designer/`,
`skills/agent-work/independent-review/` and `skills/agent-work/gatekeeper/`. Copy only the selected package when
using it alone; the shared guide is optional and introduces no runtime import.

| Need | Select | Input → useful output |
|---|---|---|
| Understand long/difficult work and choose coherent boundaries | [Task Decomposer](task-decomposer/SKILL.md) | Intent/original sources → task map, dependencies, required understanding and selected task designs |
| Prepare guidance for a particular participant | [Nudge Designer](nudge-designer/SKILL.md) | Intent or selected task, actual tools/capability → self-contained operational brief and return contract |
| Assess an actual artifact or engineering/learning claim | [Independent Reviewer](independent-review/SKILL.md) | Candidate/original criteria → evidence-backed findings, coverage and scoped assessment |
| Decide what a deliverable may be labelled, shown or released as | [Gatekeeper](gatekeeper/SKILL.md) | Deliverable, baseline, sealed targets and available evidence → a label (DRAFT/CHECKED/VERIFIED/RELEASED) with sha, x of N, untested scope and deviations |
| Keep a traceable, visible record of project progress, Owner decisions and nudges | [Progress Page](progress-page/README.md) | Agent evidence on GitHub → a static page backed by JSON, with a Timeline, a checker, an editing tool and triggers. A runnable toolset: copy the whole folder, read its README, use its tools |
| Deliver a step as something the user runs, and size the checking to the risk | [Prototype-first](prototype-first/SKILL.md) | Aim, real inputs and what the user can do today → a slice card per step, a capability probe and builder brief, a short prototype return, and a checker for cards |
| Run a source-grounded Oracle in **standalone** mode with compact ID routing, `Cycle now` GitHub handoffs and succession safety | [Oracle Standalone](oracle-standalone/SKILL.md) | Owner aim + canonical project state + real receipts → one current board, next authorized action, changeover advice and scoped Progress projection; no OTM, automatic dispatch or publication |
| Prepare a **successor Oracle** to inherit a working product, files and truthful project status | [Oracle handover protocol](oracle-standalone/references/ORACLE_HANDOVER_PROTOCOL.md) | Current prototype + Owner acceptance outcome + landing/fixtures + original sources → five useful next actions, one next actor, private custody gaps and a read-only successor packet; **cutover remains separate** |

Use a module alone when that satisfies the request. Plan-only ends with usable
task designs; brief-only ends with usable instructions; review-only ends with an
assessment. For an execution request, creating those artifacts is preparation:
the available lead still owns actual execution, return inspection and continuation.

Do not load every reference. Read the selected module's core, then only the
applicable domain/support/adapter guidance. If an optional module is unavailable,
perform the useful native work and disclose the omitted support. Continue
unaffected work rather than waiting for an entire toolchain.

For Oracle work across temporary sessions, use the optional
[Oracle continuity protocol](oracle-continuity/PROTOCOL.md). It separates durable
tasks, temporary assignments/sessions, exact-version evidence and ownership cutover.
Its [reference package](oracle-continuity/README.md) contains schemas, a read-only
validator and synthetic worker/Oracle transitions. Keep native maps and reports;
use structured records where they help. Actual dispatch, identity, write exclusion
and atomic publication require the selected transport and execution adapter.

For an Owner manually routing files and instructions among several chat windows,
use optional [Oracle Chat Routing — standalone](oracle-chat-routing/STANDALONE.md).
It renders role + Owner-supplied conversation display ID, the one next destination,
exact artifact and return receipt, and keeps reported attachment distinct from
verified bytes. It needs no runtime, schema, new role or other module; a chat ID
does not authenticate an agent, establish independence or grant authority.

When the Owner **explicitly selects a GitHub transaction-based relay** rather than
copy-pasting full handoffs, use [Oracle Cycle — standalone](../../oracle-cycles/PROTOCOL.md)
and its [project workspace example](../../oracle-cycles/p25b/README.md). The one-line
`Cycle now` trigger reads the current task and posts safe GitHub receipts;
private bytes use authorized Drive. This is optional and separate from the
existing manual routing and `relay/**` V3.1 execution ledger. No automatic
cross-chat dispatch or Progress Page publication is implied.

For an Oracle coordinating that selected route, the optional
[Oracle Standalone skill](oracle-standalone/SKILL.md) wraps the existing
[Oracle continuity](oracle-continuity/PROTOCOL.md) rules, the
[Oracle OnBoard](nudge-designer/references/ORACLE_ONBOARD.md) prompt,
[changeover/succession guidance](oracle-standalone/references/CHANGEOVER.md),
the [outcome-first Oracle handover protocol](oracle-standalone/references/ORACLE_HANDOVER_PROTOCOL.md)
and the [standalone Progress Page publication mode](progress-page/references/MODES.md).
A new skill file does **not** install itself in other chats or activate
a Cycle project; use its project URL bootstrap and activation checks.

## Contribute before handing over

Apply **No PASS beyond evidence** and **No consequential PASS without a
surviving-error challenge** to both agents and Oracle. Bind verdicts to exact
claims, expectation sources and actual checks; strengthen inadequate evidence or
narrow the verdict. See [the two rules](CONTRIBUTION_HANDOFF.md#bound-every-pass).

Choose the next bounded task from the evidence: implementation when the contract
and important failure modes are established; suitably independent falsification
when correctness remains disputed or consequential errors can evade existing
checks. Oracle then challenges integration; separately required independent review
and authorized Owner acceptance remain distinct. This is an adaptive arrangement,
not a compulsory three-agent sequence. Oracle-authored patches are contributor work.

When the Owner wants an Oracle or reviewer to contribute before a coder continues,
use [contribution and handoff guidance](CONTRIBUTION_HANDOFF.md). Select High/Medium
ROI work from actual context advantage and project benefit, implement a bounded
usable result within existing authority, and preserve decisions, checks and exact
continuation in native records. Treat ROI as a prospective judgment unless measured.

Review-only work remains review-only. A contributor's checks of affected claims
are SELF-ASSESSED; another role label or chat cannot make them independent. Keep
selected coordinator separation and independently required review intact. Stop at
an Owner-requested handoff boundary; a checkpoint alone does not end an execution
assignment. This recipe adds no controller, required role or approval gate.

## Use an Oracle OnBoard Prompt

For established context and a useful next task, ask:

> Prepare an Oracle OnBoard Prompt for <task> from <original sources/current context>.
> Preserve the whole outcome, a usable direction, evidence-based corrections and the next authorized action.

Use the [guide](nudge-designer/references/ORACLE_ONBOARD.md) and
[template](nudge-designer/assets/prompts/oracle-onboard.md). This is an optional
instruction type; the Owner/available lead can prepare it without another Oracle
or module. The receiver checks essential originals/current state, executes within
authority and returns actual evidence, changed understanding and unfinished parent
work. No separate reconstruction report or exam is added. Reuse completed
BuddyRunner/two-pass/three-pass outputs directly; do not repeat those flows.

## Find task-specific support

Choose the relevant row after selecting the task and available participants. Read
the linked guidance when applicable, rather than loading every module/reference.

| Situation | Use | Applying guidance |
|---|---|---|
| Moving work between fast/local agents, including agent ↔ ChatGPT | [Local-agent operating protocol](local-handover/AGENT_PROTOCOL.md) and [handover forms](local-handover/README.md) | Re-read originals and bytes, report actual execution and missing tests, self-check all criteria; use original task-issue comments and a verified file: in the Owner's Drive or OneDrive handoff folder, named in public text by subfolder, file name, size and SHA-256 only (never the link), or a public-safe Common one-file DRAFT PR, without promoting transfer to acceptance. |
| Taking over work under separately selected v3.6, in either mode | [Continuation/reconstruction applicability](../engineering-pr-delivery-v3.6/references/INDEPENDENT_RECONSTRUCTION.md) | Use a usable Oracle OnBoard Prompt directly; independently reconstruct only cold/missing context. No Q1–Q5 exam or agent pass mark. A selected BuddyRunner/two-pass/three-pass uses only its native stages; after completion, additional reconstruction is NOT_APPLICABLE. Reuse outputs and continue authorized work. |
| Coding with separately selected v3.6 standalone delivery | [Standalone mode](../engineering-pr-delivery-v3.6/MODE_STANDALONE.md) and [pre-DONE self-check](../engineering-pr-delivery-v3.6/references/STANDALONE_COMPLETION.md) | Before calling the task done, complete the native SELF-CHECK v1 with source/candidate bindings, common checklist, frozen task criteria, actual witnesses and pending work. Keep coordinator mode separate. |
| ChatGPT agent using that standalone protocol | [Activity and BuddyRunner policy](../engineering-pr-delivery-v3.6/references/CHATGPT_AGENT_ACTIVITY.md) | Recording is mandatory for this surface. Suggest the selected BuddyRunner once when distinct GitHub-access turns >5 OR recorded active-turn elapsed time >35 minutes. ChatGPT Work and other hosts are exempt. |
| Learning-item task design | [Task Decomposer guidance](task-decomposer/references/APPLYING_GUIDANCE.md) | Preserve the source-defined verb, response type and an off-demand contrast: explain needs causal reasons, justify needs an argument, and retrieval may recognise a unit/sign. |
| Selected-response item generation | [Generator guidance](nudge-designer/references/SELECTED_RESPONSE.md) | Select the optional `selected-response` profile when useful. Before handing over, script option lengths and correct-only shared question words; inspect flags, grammar and verb fit, retain actual results and label producer judgments SELF-ASSESSED. |
| Selected-response item review | [Reviewer guidance](independent-review/references/SELECTED_RESPONSE_REVIEW.md) | Inspect length, reasoning-word, grammar, verb and word-overlap cues before subject judgment. Ask whether the key is selectable without the intended knowledge; disclose exposure and state what plausible wrong result could survive each verdict. |
| Producing, showing or releasing a learner product, page or item bank | [Gatekeeper checks](gatekeeper/SKILL.md#checks) | Before building, locate the blueprint, the existing best version and the content source. Seal baseline-relative targets before the candidate is first measured. Pair each label-raising check with a seeded defect, and verify freshly on the exact bytes. Label by evidence, state x of N from the blueprint, and release only on the Owner's words or a recorded grant. For a personal-use product, the Owner's recorded personal-use words are that release: see Gatekeeper's personal-use profile. Each check has a fallback. Its walkthrough contains worked answers; withhold it from fresh exercises. |

The executing ChatGPT agent runs its own activity record; no extra worker is
needed. An available Oracle/lead preserves the duty in assignments and checks
returned summaries. Without one, the executing agent owns both responsibilities.
Keep each agent/project episode across nudges; calls are not turns, and closed
active intervals exclude idle/user-wait gaps. Retain unavailable observations and
UNKNOWN applicability explicitly. A known lower bound crossing either threshold
still requires a suggestion. Follow the [Oracle responsibility guidance](task-decomposer/references/ORACLE_USE.md#owner-selected-chatgpt-agent-activity-duty)
for optional composition. The recorder is agent-invoked, not installed host telemetry;
the recommendation does not force handover or stop useful work.

For learning material, reasoning words can be essential to the required explanation
or argument; inspect asymmetric cues rather than banning those words. A no-flag
script result does not approve the subject model, demand or learner transfer.
An exposed reviewer remains exposed even when using only exact supplied files.
Keep those limits visible without adding a compulsory role or review pass.

## Adapt to available participants

| Available participants | Practical arrangement |
|---|---|
| One agent | Hold planning, instruction, execution and reconciliation responsibilities as needed. Label contribution/self-review honestly; do not manufacture another role. |
| Lead and narrower worker | Lead selects the coherent task and usable method; worker captures bounded evidence; lead interprets it and retains coupled decisions/integration. |
| Separate reviewer available | Assign a meaningful assessment with original sources and necessary knowledge. Disclose authorship, context/reference exposure and shared assumptions separately. |
| Several workers/specialists | Split only where a durable output makes the handoff worthwhile. Name the available participant who integrates results and retains unresolved work. |

Oracle, Designer and reviewer are responsibilities, not compulsory people or
competence certificates. Use DIRECT/OPEN support when the participant can justify
the method; use GUIDED support when avoidable decisions should be removed. Give
the WHY and necessary model/state knowledge in either case. A short prompt, model
label or correct ACK does not establish sound judgment. Keep consequential model,
architecture and acceptance interpretation with a participant who can justify it;
if unavailable, retain that limit while gathering useful evidence.

A coordinator that issues work does not also produce, repair or assemble that
deliverable; inserting items into a page counts as producing it. Send a repair back
as a new brief. Gatekeeper's GK3 sets the one exception, a labelled typo-level fix.
The coordinator's own checks are notes, unless the role setup names it the
reviewer of record; then its review counts as (coordinator review) only on
Gatekeeper's conditions. Labels
move on evidence the coordinator cannot rewrite, or on a disclosed fallback. A
check limits a label, never the work. See Gatekeeper's
[role setups](gatekeeper/SKILL.md#who-does-what) and its
[rules against using checks as excuses](gatekeeper/SKILL.md#no-check-is-a-reason-to-stop-work).

## Carry work end to end

Apply these responsibilities as useful; combine, skip or revisit them according to
the problem. They are not fixed passes or a requirement to run every module.

1. Reconstruct the original outcome and amendments. Establish actual sources,
   candidate/input identity, environment, available authority and prior useful work.
   For a product, locate the blueprint's definitions and coverage set, the existing
   best version (the quality bar) and the content source before building anything.
   If one is missing, ask one specific question per missing input and continue
   with the work that doesn't depend on the answer. If no earlier product exists,
   build against the blueprint and label the result NO-BASELINE.
2. Select the next uncertainty or deliverable that can change the outcome. Use
   Task Decomposer if boundaries/dependencies need clarification. Keep coupled
   state/model decisions coherent and retain integration/deferred outcomes.
3. Prepare executable work. Use Nudge Designer when participant guidance helps.
   Establish who designs the observation, executes/sends it, finds the return and
   interprets it. The available lead retains unallocated responsibilities. Use the
   actual authorized/manual channel; these modules do not dispatch or watch it.
4. Execute under existing task authority. Capture the actual inputs, commands or
   interactions, observations and artifacts. A plausible wrong result should be
   distinguishable. A missing tool/resource affects its dependent checks; retain
   attempted action, observed restriction, affected scope and next feasible route.
5. Inspect the return. Use Independent Reviewer when useful. Check original
   requirements, actual candidate and witness, not just COMPLETE/PASS/count/hash.
   Review the test oracle and a relevant contrary condition. Preserve supported
   claims, known defects, NOT_RUN items and independent-assessment limits together.
   Where the result will be judged, seal the targets before the candidate is first
   measured (in coordinator mode, before the return is read). Use an external
   timestamp such as a comment id, or else the Owner's chat. Show that each check
   whose PASS raises a label fails on a seeded defect.
6. Reconcile against the whole outcome. Preserve the original report and record
   the consumer's response separately. Correct affected inputs/methods/work, issue
   a visible revision where meaning changed, and verify the actual integrated
   behavior. Continue authorized work; reserve only genuinely unresolved decisions.
   Show or release work only under the label its evidence supports, with its sha,
   x of N and untested scope. Say in the same message when a step was skipped or
   a fallback was used.

Select evidence for the project: original interaction/state traces for UI, source
rules and real consumers for logic, accurate material and learner evidence for
claimed learning outcomes, or original givens/units/model assumptions and suitable
comparisons for calculations/FEA. A shared operating loop does not supply domain
qualification. Follow already applicable project criteria and authority.

## Preserve the handoff

**Optional local-agent work:** [agent operating protocol](local-handover/AGENT_PROTOCOL.md)
and [handover forms](local-handover/README.md) guide source-first work,
source-bound self-checks and [GitHub comment handover](local-handover/COMMENT_RELAY.md)
without Owner copy/paste. A verified Google Drive ZIP or public-safe, single-file
Common DRAFT PR transports bytes only; it never verifies the product or grants
acceptance. No fifth required skill/role, exam, gate or native-protocol waiver.

Carry this minimum meaning in the existing native record. Add only missing fields;
this is a prose aid, not a new shared schema or mandatory return envelope.

```text
Purpose: <Owner outcome, original source and applicable amendment>
Task/subject: <coherent deliverable or claim, task identity, exact candidate/input>
Understanding: <WHY, necessary model/state context, established decisions>
Inputs: <accessible originals/revisions; byte hashes where consequential>
Boundaries: <allowed work, preserved behavior, reserved judgments>
Method/result: <usable method, observable success/contrary case, actual evidence>
Continuation: <uncertainty, remaining parent work, return location and next action>
Optional bindings: <selected module/version, map/task, assignment/tracker/run IDs>
```

Keep task, candidate and review-run identities distinct. Link details rather than
passing the entire chat. Preserve issued snapshots and native returns. A new
candidate does not erase old evidence; assess affected claims and integration
before reuse. A changed observation alone need not invent a new task-map revision.
Use [adapter mappings](independent-review/references/ADAPTERS.md) for identity/transport details and
[reconciliation guidance](independent-review/references/RECONCILIATION.md) for findings and drift.

## Use schemas when helpful

| Module | Optional structured contract |
|---|---|
| Task Decomposer | [Task Map](task-decomposer/schemas/task-map.schema.json), `task-decomposer.map/v1` |
| Nudge Designer | [Intent](nudge-designer/schemas/intent.schema.json) and [Plan](nudge-designer/schemas/plan.schema.json); select its documented v1/v1.1 contract |
| Independent Reviewer | [Review Case](independent-review/schemas/review-case.schema.json) and [Review Result](independent-review/schemas/review-result.schema.json) |

A Task Map is source input to Nudge Designer, not native Nudge Plan JSON. The
consuming agent creates that module's objects from the selected task meaning when
structured support is useful. Bind a review result to its actual review case and
candidate; keep any selected project review profile/native report alongside it.
No automatic converter or single universal end-to-end object exists here.

For a Markdown-only use, keep the same meaning without filling JSON. If an optional
validator is unavailable, record its NOT_RUN status and perform available checks.
Structural validity, byte identity and schema intake do not establish technical
correctness, distinct-principal independence or integrated Owner acceptance.

## Follow the worked examples

Standalone examples:

- Task Decomposer: ask it to plan a long UI investigation from the original goal,
  retaining uncertain future work. It returns source-grounded designs; it does not
  claim the UI was repaired. Use its [entry prompts](task-decomposer/assets/entry-prompts.md).
- Nudge Designer: give it a custody task, manifest and actual worker tools. Request
  a GUIDED brief for byte hashing and an altered-copy contrast. It returns usable
  instructions; sending/execution remains with the authorized lead/host. Use its
  [assignment template](nudge-designer/assets/prompts/assignment.md).
- Independent Reviewer: review the short learning page against its stated aim.
  The [actual standalone application](independent-review/examples/applications/lesson/out/review.md)
  preserves recalculation, an empty finding set and learner/independence limits.
- Selected-response generation/review: [G14 raw case](nudge-designer/examples/guidance/G14-option-demand/raw.md)
  illustrates verb/cue distinctions; its [fresh application receipt](nudge-designer/examples/guidance/G14-option-demand/forward/RECEIPT.md)
  retains actual generation, script checks and a separate review with exposure
  limits. Withhold completed returns/goldens during another discovery test; this
  application does not establish learner performance, a qualified P2 or an LFEA fix.

Illustrative composed example — review an estimator against its original rule:

| Handoff | Meaning and artifact |
|---|---|
| Owner → available lead | Review the supplied estimator against the item-only discount rule; preserve source bytes and make no product edit. |
| Task Decomposer → brief preparation, if selected | KEEP one coherent review boundary; retain source authority, threshold/rounding knowledge, candidate identity and the no-edit boundary. Do not create a separate agent/task for every line. |
| Nudge Designer → evidence execution, if selected | Issue a bounded comparison using actual files, original rule, boundary cases, required evidence and native return. A narrower worker receives a usable method; it does not choose the business rule. |
| Worker → assessment | Return actual inputs/outputs, source identity, runtime receipts, unchanged-byte checks and limits. Original tests passing does not settle rule coverage. |
| Independent Reviewer → reconciliation, if selected | Establish that delivery can wrongly trigger the discount, with a concrete witness. The [actual standalone review](independent-review/examples/applications/direct/out/review.md) shows this evidence; it was not generated through a three-module run. |
| Available lead → Owner | Preserve the failed bounded claim and valid evidence; the requested review is complete, while any repair needs the applicable task authority and a changed-candidate check. No release claim follows. |

This table is an illustration of composition, not evidence that all three modules
were executed together. It contains a worked answer: withhold it when assessing
fresh discovery on this same fixture. The [application archive](independent-review/examples/applications/assessment.md)
and the Nudge Designer [Oracle episode](nudge-designer/examples/oracle-execution/ASSESSMENT.md)
record the separate actual applications, assistance and limits. Do not combine
their PASS labels into an unperformed integrated pilot.

## Start the real LFEA test

Use [the LFEA entry prompt](independent-review/assets/lfea-pilot.md), choosing direct review or
optional composition according to the actual need. Refresh AA3 original intent,
amendments, candidate/deployment, trace access and existing authority. Preserve the
whole findings → locate → supported correction → fresh checks → Output aim.

Begin with a discriminating observation rather than a speculative repair. Preserve
actual failed-click coordinates and preparation differences; do not substitute a
force-click, guessed center or easier segment. Retain useful source review if the
runtime route is unavailable. Measure actual outcomes and assistance; prototype
checks do not establish LFEA acceptance, low-thinking qualification or causal ROI.
