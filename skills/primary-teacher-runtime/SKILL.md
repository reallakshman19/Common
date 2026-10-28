---
name: primary-teacher-runtime
description: Apply the canonical Grade 4–5 Primary Teacher Runtime: observe learner evidence, form bounded hypotheses, choose the smallest useful teacher move, require child action, change route after repeated failure, separate conceptual support from access support, fade scaffolds, and seek independent/retention/transfer evidence.
---

# Primary Teacher Runtime Skill

## Mandatory references

Always load and follow:

- `../../Primary/Architecture/PRIMARY_INTEGRATED_ARCHITECTURE.md`
- `../../Primary/Architecture/PRIMARY_TEACHER_RUNTIME.md`
- `../../Primary/Architecture/PRIMARY_DIAGNOSTIC_REASONING.md`
- `../../Primary/Architecture/SEMANTIC_OWNERSHIP.md`

Then load the relevant subject schema/skill. This skill does not replace Math or English pedagogy.

When the task includes Grade 4–5 mathematical notebook/classwork, handwritten intermediate work, operation-selection evidence, grouped units/rates, or multi-step working that can change the diagnosis, also load:

- `../../Primary/Architecture/PRIMARY_MATH_WORK_EVIDENCE.md`

## When to use

Use for interactive Grade 4–5 teaching, adaptive tutoring, diagnostic repair, learner-response analysis, scaffold selection/fading, or when a child is repeatedly asking for clarification.

Do not force this runtime into passive reference-material tasks when the user explicitly asks only for notes, a worksheet, or a static study guide.

## Runtime loop

```text
OBSERVATION
→ RESPONSE DIAGNOSIS
→ TEACHER DECISION
→ TEACHER MOVE
→ CHILD ACTION
→ NEW EVIDENCE
↺
```

When more than one explanation is plausible, use the stricter diagnostic loop:

```text
OBSERVABLE EVIDENCE
→ STRUCTURAL FEATURES / CONTRAST SET
→ 2–3 BOUNDED HYPOTHESES
→ DIAGNOSTIC PROBE
→ OBSERVED PROBE RESULT
→ CONFIDENCE UPDATE
→ TEACHER DECISION
→ TEACHER MOVE
→ INDEPENDENT RETRY
```

When intermediate mathematical work is available, preserve it before diagnosis:

```text
CHILD WORK
→ MATHEMATICAL WORK EVIDENCE
→ ERROR SIGNATURE / STRUCTURAL PATTERN
→ BOUNDED RESPONSE DIAGNOSIS
→ SMALLEST DISCRIMINATING PROBE
→ TEACHER MOVE
→ INDEPENDENT RETRY
```

A diagnosis is a hypothesis, not a child label.

## Required distinctions

Keep these separate:

```text
long-lived SkillState ≠ CurrentLearningState
raw evidence ≠ pedagogical judgement
conceptual support ≠ access/load adjustment
provided representation ≠ child-selected ≠ child-produced
child-produced strategy support ≠ child-initiated strategy
child-produced strategy support ≠ teacher-provided hint
child work ≠ teacher annotation/correction
error signature ≠ durable learner trait
contrast set ≠ arbitrary pattern matching
diagnostic probe ≠ extra practice question
acquisition ≠ independent use ≠ delayed retention ≠ transfer ≠ stretch
```

`CHILD_PRODUCED` records who physically produced a representation or strategy support. It does not prove independent strategy selection. Preserve strategy initiation separately when observable: actor + mode (`SPONTANEOUS`, `GENERAL_PROMPT`, `STRATEGY_PROMPT`, `EXPLICIT_DIRECTION`, `UNKNOWN`).

## Smallest useful move

Prefer the smallest teacher move that makes the child do the next piece of thinking.

Do not answer a repeated clarification with only a label or conclusion when the learner needs a reusable recognition cue.

Example:

```text
Child: "Large?"

Better:
"Large tells us how big something is. Words that tell how big go in SIZE. Now try: where would tiny go?"
```

This answers, teaches the cue, and checks transfer.

## Diagnostic probe rule

When multiple explanations are plausible, do not jump directly from evidence to a confident diagnosis.

Maintain 2–3 bounded hypotheses and choose a probe that states:

```text
which hypotheses it discriminates
which feature it manipulates
which unrelated loads it keeps low
how major outcomes update confidence
```

Prefer controlled one-step probes, partial completions, small prerequisite checks, or example/non-example pairs over harder or longer practice.

A diagnostic probe is for information gain, not challenge.

## Contrast-set rule

Contrast-based diagnosis must be deliberate.

A valid contrast set identifies:

```text
focal diagnostic feature
shared background structure
cases where the focal feature is present/absent or otherwise deliberately varied
```

Do not let the runtime infer an arbitrary correlation simply because several attempts are available.

## Same-route failure

If the child has two unsuccessful attempts on the same target with substantially the same teaching route, the next move must change a meaningful dimension:

- representation;
- language load;
- concrete context;
- task size;
- response mode;
- problem structure;
- prerequisite probe;
- example/non-example contrast.

Do not repeat the same explanation at greater length.

## Child action

In tutor mode, substantial teaching should normally be followed by observable child action such as classifying, showing, choosing, explaining, completing one step, or solving a near-isomorphic retry.

## Conceptual support and access support

Conceptual help may use subject-specific H-levels and moves such as prompt, hint, model, think-aloud, or worked example.

Access adjustments may include reduced language, one-step-at-a-time instructions, oral response, reduced writing, read-aloud support, or additional visual spacing.

Do not record an access adjustment as conceptual hint dependence.

## Mathematical work evidence

When intermediate Math work exists, do not reduce it to final correctness.

Preserve where observable:

```text
operation selected
ordered work steps
successful substeps
incorrect substeps
quantity/unit relationships
representations
child-generated strategy supports
strategy initiation when observable
self-corrections
step-level provenance/certainty where useful
teacher annotations with separate provenance
```

Use `PRIMARY_MATH_WORK_EVIDENCE.md` for Math evidence semantics and `PRIMARY_DIAGNOSTIC_REASONING.md` for diagnostic comparison/probe semantics.

Important rules:

- an incorrect final answer does not erase correct intermediate reasoning;
- a child-produced multiplication/multiples table can be positive strategic evidence;
- a child-produced table after explicit teacher direction is not equivalent to spontaneous strategy selection;
- teacher-written corrections are not independent child evidence;
- ambiguous handwriting remains `AMBIGUOUS`/`NOT_OBSERVED` rather than being invented;
- preserve provenance at mathematically meaningful work-step level when it affects independence or diagnosis;
- if several structurally related items exist, compare them through an explicit focal feature before concluding the whole topic is weak;
- for word problems with grouped units, rates, money or conversion, inspect `QUANTITY → UNIT → ROLE → RELATIONSHIP → UNKNOWN → OPERATION(S)` before teaching from keywords.

## Error handling

Wrong answer does not automatically mean reteach.

Consider at least:

```text
CONCEPTUAL_MISCONCEPTION
PREREQUISITE_GAP
PROCEDURAL_ERROR
LANGUAGE_COMPREHENSION_ERROR
REPRESENTATION_ERROR
TASK_INTERPRETATION_ERROR
MEMORY_RETRIEVAL_FAILURE
PERFORMANCE_LAPSE
ATTENTION_OR_RUSHING_CANDIDATE
RESPONSE_FORM_ERROR
SOURCE_MODEL_BOUNDARY
INSUFFICIENT_EVIDENCE
```

Subject-specific error signatures may narrow a generic diagnosis, but remain evidence patterns rather than durable learner traits.

For example:

```text
PROCEDURAL_ERROR + DIV_QUOTIENT_ZERO_PLACE_VALUE
```

may be a better bounded hypothesis than `weak in division` when controlled contrast evidence supports it.

When multiple explanations are plausible, ask the smallest diagnostic question that separates them and interpret the result against the competing hypotheses.

## Evidence-family boundary

Not every renderer observes the same evidence.

```text
LearningEvidence
  |- AttemptEvidence
  |- MathematicalWorkEvidence
  |- OralResponseEvidence
  |- TeacherObservationEvidence
```

Do not require a game renderer to invent intermediate work it cannot observe. Use only evidence the renderer can faithfully capture or transport.

## Repair and retry

After meaningful conceptual repair, give an independent retry on an isomorphic or appropriately varied item before treating the skill as independently available.

Worked-example success is not independent evidence.

## Support fading

When evidence permits, reduce help by removing conceptual hints, reducing provided structure, asking the learner to select/produce a representation, or moving to transfer.

## Source-model boundary

If a child's textbook teaches a simplified rule, preserve that rule. If an example falls outside its taxonomy, mark the boundary rather than inventing a new child-facing category.

Keep fuller canonical analysis separate from the source model.

## Feedback policy

- preserve the correct part of the child's thinking;
- identify one useful next action;
- use child-friendly language;
- avoid fixed-ability labels;
- avoid long lectures immediately after errors;
- give a reusable cue or method, not only the answer;
- keep mistakes safe to reveal.

## Stop rule

End, defer, or change the activity when the target evidence has been obtained, repetition adds little value, a different prerequisite episode is needed, source ambiguity blocks reliable teaching, or current session signals indicate that continuing is not useful.

## Mastery evidence

Never infer durable mastery from one session or one game score.

Track relevant evidence separately for:

```text
ACQUISITION
INDEPENDENT_USE
DELAYED_RETENTION
TRANSFER
STRETCH (optional)
```

Competition preparation belongs primarily to stretch/assessment-demand extensions and must not redefine ordinary curriculum mastery.
