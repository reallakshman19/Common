# Composable profiles

Profiles are a small library of questions and methods, not phases, capability
certificates, authorization policies or mandatory domain pipelines. Choose those
that improve this task; keep unused guidance out of the worker brief.

| Profile | Required understanding | Typical discriminating evidence |
|---|---|---|
| `core` | Purpose, conditions, provenance, uncertainty | Source trace, counterexample, integrated use |
| `ui` | User journey, state, interaction, recovery | Actual browser action, state comparison |
| `logic` | Invariant, state owner, event/data ordering | Controlled event order, runtime probe |
| `education` | Prerequisites, misconception, intended transfer | Worked method, contrast, actual learner response |
| `quantitative` | Givens, units, conventions, assumptions | Reproducible derivation, unit and sensitivity checks |
| `fea` | Intended use, physical model, boundary conditions, numerical error | Compatible reference, equilibrium/error checks, sensitivity |
| `coding` | Source boundary, protected behavior, delivery protocol | Meaningful regression and integrated behavior |

A UI issue may use core + UI + logic + coding; an FEA teaching exercise may use
core + education + quantitative + FEA. Compose dimensions without concatenating
four compulsory workflows.

## Custom library

Supply `--profiles path/to/library.json`. The library has
`schema: "nudge-designer.profiles/v1"` and a nonempty `profiles` array. Each object
has exactly these fields:

| Field | Contract |
|---|---|
| `id` | Stable letter-first ID using the schemas' ID syntax |
| `revision`, `label` | Nonempty text |
| `knowledge` | Nonempty unique text array: required understanding |
| `reasoning_moves` | Nonempty unique text array: operation identifiers |
| `evidence_methods` | Nonempty unique text array: evidence identifiers |
| `review_questions` | Nonempty unique text array: substantive review prompts |
| `pitfalls` | Nonempty unique text array: misleading shortcuts and limits |

Operation/evidence names come from selected profiles, not a fixed domain enum.
A translation profile can add `compare_register` and `bilingual_review`. Legal or
financial use needs current primary sources and appropriately reserved judgments.
Adding words to a library does not qualify a worker.

Bind selected profile contents into the plan. Editing one makes the old binding
stale; changing an unselected profile does not. Custom libraries retain the same
structural and semantic limits.

## Supporting narrower workers

Supply a concrete method, example or contrast where it reduces ambiguity, with
source-specific context and why the work matters. Reserve consequential decisions
for a capable Designer or relevant reviewer; state what the worker should bring
back. The worker still needs adequate tools and capability.

Do not expose target answers as proof of independent understanding. Keep raw
cases separate from worked outputs and reviewer expectations. A useful reference
pack may include a method, changed-condition problem, expected reasoning, failure
signs and a return condition. The four bundled cases demonstrate this separation
without building a second recipe platform.

| Case | Read for | Deliberately unresolved |
|---|---|---|
| `lfea` | Ordinary-pointer oracle and existing exact-point diagnosis | Fresh trace/CSS observation, complete application acceptance |
| `logic` | Invariant and event-order falsifier, unrelated export work | Runtime evidence and actual repair |
| `grade11` | Misconception, worked method, transfer prompt | Learner response and learning gain |
| `fea` | Units, derivation, compatible numerical comparison | Production solver execution and physical/design qualification |
