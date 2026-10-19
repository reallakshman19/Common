# Nudge Designer v1 — Owner intent and implementation plan

## Contents

- [Reconciled intent](#reconciled-intent)
- [Architecture and boundaries](#architecture-and-boundaries)
- [Work and acceptance](#work-and-acceptance)
- [Verification and publication](#verification-and-publication)

## Reconciled intent

Owner instruction, 18 October 2026: create a new folder in Common/skills and
proceed with the blueprint, two JSON schemas, Designer skill, a small profile
library and worked fixtures; reconcile intent and support multiple dimensions.

The intended result is a reusable agent skill that turns a short Owner request
and authentic context into useful, bounded nudges. It must preserve meaning
across decomposition, execution, correction and succession. It must help a
capable planner support narrower workers without treating response length,
configuration claims, filled fields or green component tests as understanding.

| ID | Requirement retained from this conversation | Planned evidence |
|---|---|---|
| R01 | Human purpose and original Owner conditions survive condensation | Source-linked intent items, explicit conditions, rendered worker context |
| R02 | One common reasoning contract across UI, logic, education and FEA | Composable profiles; four distinct worked cases |
| R03 | Thinking approach and evidence method are separate dimensions | Independent lists per nudge, validated against selected profiles |
| R04 | Break down large work by coherent outcomes and dependencies | Outcome/nudge hierarchy, declared coverage, DAG and branch checks |
| R05 | Every assignment contains the agreed seven elements | Required schema fields and complete worker renderer |
| R06 | The planner performs substantive synthesis; code checks mechanics | Agent instructions; structural-only validator with explicit limits |
| R07 | Investigation is useful work; missing facts do not block everything | Scoped uncertainty and independent work in every nudge |
| R08 | Preserve useful predecessor work and allow evidenced KEEP | LFEA reuses its existing exact-point diagnostic instead of inventing a rewrite |
| R09 | Lower-thinking workers receive context and decision boundaries | Knowledge requirements, reserved decisions, contrast and evidence instructions |
| R10 | No fixed phase count, innovation quota or mandatory extra approval | Advisory dependency graph; choice based on uncertainty and actual authority |
| R11 | Revision changes affect relevant conclusions, preserving history | Offline impact report from declared source/item/outcome dependencies |
| R12 | NextNudge remains optional and manually operated | Integration reference only; no UI edits, auto sends or delivery claims |
| R13 | Other protocols remain separately selected | No runtime imports or edits to BuddyRunner, Master or engineering delivery |
| R14 | Examples are honest about original/synthetic and reported/executed | Real-source LFEA case; synthetic logic, Grade 11 and FEA cases |
| R15 | Reuse worked examples without turning them into answer leakage | Raw-case inputs separate from worked outputs and reviewer expectations |
| R16 | Save to the user-selected Git repository | Scoped branch, exact remote readback and draft PR; no automatic merge |

The skill does not make a low-thinking agent qualified for a new architecture,
physical model, scientific source or pedagogical decision. Bound useful work,
retain the WHY, and route consequential unresolved judgment appropriately.

## Architecture and boundaries

Two semantic layers share one package:

1. **Intent Model:** reconstruct purpose, sources, requirements, constraints,
   observed facts, hypotheses, proposals, unknowns and outcome relationships.
2. **Nudge Designer:** select reasoning operations and evidence methods,
   decompose by outcome, and author draft instructions and result branches.

The model/agent makes those judgments. Python never pretends to infer intent or
generate a trustworthy plan from keywords. It validates caller-authored objects,
renders a worker brief and reports revision impact. No LLM provider, launcher,
network collector, executor, authorization service or scheduler is installed.

The two formal documents are `nudge-designer.intent/v1` and
`nudge-designer.plan/v1`. Bind the plan to the complete intent and selected
profile contents with canonical SHA-256 digests. A digest proves identity, not
source truth, source completeness, actor authenticity or acceptance.

Keep original sources and their assessments separate. Require source references
for substantive items; allow genuine UNKNOWN. Preserve conditions verbatim in
the working brief. Declared coverage is not a complete project risk census.

Suggested folder contents:

- `SKILL.md`, `agents/openai.yaml`
- `references/BLUEPRINT.md`, this plan, profile and integration guidance
- `schemas/intent.schema.json`, `schemas/plan.schema.json`
- `profiles/library.json`
- `scripts/` for strict JSON loading, cross-reference checks, rendering and CLI
- `examples/<case>/` with raw case, intent, plan and human assessment
- `tests/` plus a narrowly scoped CI workflow

Allowed engineering scope: the new `skills/agent-work/nudge-designer/` package and one
focused CI workflow. Preserve existing skills, historical evidence, product
repositories, NextNudge source/data, protected authorities and source fixtures.

## Work and acceptance

### W01 — freeze the intent and contract

- Record this requirement matrix and explicit exclusions.
- Define the two object contracts and the planner/worker responsibilities.
- Design positive and negative tests before implementation.

Done when: the contract is reviewable and tests express the required behavior.

### W02 — create the schemas and profile library

- Model source assessments without self-authenticating VERIFIED flags.
- Separate requirements, constraints, facts, hypotheses, proposals and unknowns.
- Support nested outcomes, hierarchical nudges, branches and dependency checks.
- Select profiles independently of domain and fixed phase count.
- Retain exact conditions and reserved decisions in relevant worker context.

Done when: all worked objects satisfy both schemas; malformed or inconsistent
objects fail with useful diagnostics. Profile composition is not exclusive.

### W03 — implement deterministic support

- Strictly parse JSON; reject duplicate keys and non-finite numbers.
- Validate schemas, unique IDs, references, cycles, content bindings and declared
  coverage. Reject stale plans and invented profile operations/methods.
- Render all seven assignment elements, relevant source/constraint context,
  required understanding and evidence expectations.
- Compare revisions using declared relationships; report affected work without
  modifying plans, sent instructions, evidence or authority.
- Support a custom profile library without hard-coded project dispatch.

Done when: actual CLI/API tests pass, source inputs stay unchanged, and all
reports state their structural and supplied-evidence limits.

### W04 — worked fixtures and realistic forward tests

- LFEA: preserve #47 intent, exact PR #48 basis, separately reported 2 PASS / 1
  FAIL, different profiles, missing CSS-point evidence and existing diagnostic.
- Logic: use a synthetic event-order problem with a concrete invariant and a
  discriminating experiment, preserving an unrelated pending concern.
- Education: use synthetic Grade 11 kinematics with prerequisite/misconception,
  worked example and transfer checks; do not claim actual learner evidence.
- FEA: use an explicitly synthetic axial-bar reference case, original units and
  assumptions; distinguish numerical verification from engineering acceptance.
- Exercise large/nested work, mixed profiles, deferred coverage and selective
  revision impact in focused regressions.
- Forward-test the skill with fresh agents using raw inputs and no worked answer
  leakage; keep their outputs isolated from each other and from the references.

Done when: machine checks and human assessment are separately reported; actual
forward-test outputs show source-grounded, usable instructions or expose issues
that are corrected. Live UI repair and learning/FEA qualification remain unrun.

### W05 — validate and publish

- Run focused Python tests, schema/example checks, CLI smoke checks, Skill
  Creator validation, local link checks and `git diff --check`.
- Keep authored files bounded and review the exact changed-file scope.
- Add path-scoped read-only CI on supported Python versions.
- Publish the package to a branch in Common and open a draft PR.
- Verify remote tree/head and report executed checks, failures and NOT_RUN.

Done when: the requested folder is available in the GitHub draft with a concrete
reviewable implementation. Owner merge remains separate.

## Verification and publication

Implementation checkpoint, 18 October 2026: W01–W04 are implemented, with the
two schemas, seven profiles, offline support and four worked references. Three
fresh-agent unseen-case pilots and their readability retests are recorded as
portable replays. The 49 focused checks pass locally on Python 3.12, including
actual CLI validation/rendering of all seven examples. Skill Creator validation,
syntax, metadata and local-link checks pass. See [verification](VERIFICATION.md)
for execution details and limits. W05 publication and hosted CI are reported on
the delivery PR; this checkpoint does not claim them in advance.

Do not convert the source-grounded LFEA example into a claim that its browser
diagnosis or repair was executed by this package. No lower-capability worker
benchmark, actual learner study or production FEA qualification was performed.

Use the source-bound raw cases for manual pilots before considering a NextNudge
import adapter or UI controls. A later adapter must preserve NextNudge's actual
version, instruction freezing, correction review and manual delivery semantics.

## Owner amendment — role and surface adapters

The later Owner request broadens end-to-end support for different thinking agents
and asks for robust applicable adapters. [The adapter plan](ADAPTER_PLAN.md) records
this extension without replacing the v1 requirements or historic checkpoint above.
Explicit `plan/v1.1` adds participants and per-task assignments within the same plan
schema. Seven audience views and five manual document surfaces retain native
reporting and separately selected protocols. No native import or UI change is added.

The extension includes actual worker/specialist execution, a separate local review
and a Designer working revision correcting observed semantic problems. Those
bounded observations do not qualify lower-thinking models or accept domain
outcomes. Current verification and limits are in [verification](VERIFICATION.md).

## Owner amendment — usable Oracle execution

Owner instruction, 19 October 2026: complete the outstanding skill support before
the live pilot. Implement [Oracle execution](ORACLE_EXECUTION.md), a short Owner/
Oracle entry, optional native episode aid and source-bound LFEA pilot entry. Keep
measurement design, actual return inspection, adaptive direction and integrated
verification allocated. Attribute parent assistance and actual configuration;
retain the original user outcome beyond component success.

Acceptance for this amendment is usable, linked operating support plus an actual
local application that exercises continuation with native artifacts and preserves
assistance/coverage limits. It does not require a new controller, schema, model
provider or app integration. The real LFEA browser repair, identified low-thinking
configuration and comparative reliability/ROI remain pilot evidence to obtain,
not completion claims that documentation or compatibility tests can satisfy.
