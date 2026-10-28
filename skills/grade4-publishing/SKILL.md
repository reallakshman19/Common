---
name: grade4-publishing
description: Convert validated Grade 4 Mathematics or English content into visual-first, child-friendly student products and separate teacher/parent/workbook/answer-key editions with structured instructional visuals, reusable page components, page-image QA, and explicit release gates.
---

# Grade 4 Publishing Skill

## Mandatory references

Always load and follow:

- `../../Grade4PublishingSchema.md`
- `../../Grade4VisualPublishingAcceptance.md`

Also load the active subject schema and any chapter-specific publishing contract.

Known example:

- Division -> `../../Grade4MathDivisionPublishingContract.md`

If the source task is interactive/adaptive or requires diagnosis, also load the relevant Primary Teacher Runtime / subject skill before publishing. Publishing must not invent pedagogy.

## Core principle

Publishing is downstream from pedagogy, but **child usability is a release criterion**.

```text
VALIDATED SUBJECT CONTENT
  -> OUTPUT PROFILE
  -> CHAPTER / UNIT PLAN
  -> PAGE PLAN
  -> PAGE COMPONENTS
  -> VISUAL / MODEL RENDERING
  -> EDITION FILTERING
  -> PDF RENDER
  -> RENDER EVERY PAGE TO IMAGE
  -> CHILD-USABILITY + LAYOUT + PEDAGOGY QA
  -> FINAL PRODUCT
```

Never alter mathematical meaning, reading text, grammar target, answer logic, rubric criteria, source fidelity, or learning progression merely to make content fit a page.

A technically correct PDF that reads like a research paper or adult notes is **not** an acceptable Grade 4 student product.

---

## Preconditions

Before publishing, confirm the subject workflow has produced the applicable validated content:

- chapter/unit structure;
- Learning Cells;
- questions/tasks;
- answers or writing rubrics;
- worked examples/model responses;
- instructional visuals/models or specifications;
- teacher notes/diagnostics where relevant;
- provenance/source metadata.

If content is pedagogically incomplete, return to the subject skill rather than solving the gap with layout.

---

## Supported output profiles

```text
STUDENT_TEXTBOOK
TEACHER_EDITION
TEACHER_PARENT_KEY
WORKBOOK
ANSWER_KEY
ASSESSMENT_BOOKLET
REVISION_BOOKLET
SCREEN_PDF
PRINT_PDF
```

An output may combine profile + medium, e.g. `STUDENT_TEXTBOOK + PRINT_PDF`.

Resolve at least:

```yaml
edition: STUDENT | TEACHER | TEACHER_PARENT_KEY | WORKBOOK | ANSWER_KEY | ASSESSMENT
medium: PRINT_PDF | SCREEN_PDF
page_size: A4 | source_required_size
color_mode: COLOR | GRAYSCALE
answer_visibility: HIDDEN | VISIBLE
hint_visibility: HIDDEN | SELECTIVE | VISIBLE
diagnostics_visibility: HIDDEN | TEACHER_ONLY
provenance_visibility: INTERNAL | APPENDIX | VISIBLE
visual_profile: VISUAL_FIRST | SOURCE_FAITHFUL_TEXT_HEAVY
```

For normal Grade 4 study guides, revision guides, and concept booklets, default `visual_profile` to `VISUAL_FIRST` unless the source explicitly requires another format.

Do not expose teacher-only diagnostic metadata in a student edition.

---

## Student product contract — VISUAL_FIRST

A Grade 4 student-facing concept/worked-example page should normally have:

- one dominant learning idea;
- at least one meaningful instructional visual/model/organizer when one exists;
- short child-facing chunks instead of long paragraphs;
- generous whitespace and large readable diagrams;
- one visible child action such as notice, point, match, draw, choose, complete, explain, solve, or check;
- response space proportional to the expected work.

Avoid:

- walls of text;
- research-style explanations;
- teacher terminology or architecture language;
- many dense bullet lists without a model/example;
- tiny instructional diagrams;
- several consecutive explanation-only pages;
- shrinking text/diagrams just to fit more content.

When content does not fit child-readably, split or redesign the page plan.

Visuals must be instructional where possible. Decorative imagery may support engagement but must not substitute for the mathematical/language model.

---

## Student / adult edition separation

Prefer separate outputs:

```text
STUDENT PRODUCT
  child-friendly concept visuals
  worked examples
  short cues
  practice
  reasoning / transfer
  self-check

TEACHER / PARENT PRODUCT
  what to watch for
  possible error patterns
  diagnostic probes
  H1-H3 quick hints
  repair suggestion
  independent retry
  support-fading / stop rule
```

A child study guide must not become a diagnostic manual.

A teacher key may reuse the same immutable questions/content, but expose adult-only overlays.

---

## H1-H3 Teacher / Parent quick-hint profile

The canonical Grade 4 Math hint ladder may contain more levels internally. For a quick visual Teacher / Parent key, publish the first three roles as:

```text
H1 NOTICE
  Point to the important feature without supplying the method.

H2 REMEMBER
  Trigger a relevant fact, rule, relationship, place-value idea, or unit fact.

H3 REPRESENT
  Change or externalize the representation: groups, bar model, place-value chart,
  number line, unit chain, multiples strip, sentence pattern, organizer, etc.
```

Use progressively:

```text
H1
  ↓ only if insufficient
H2
  ↓ only if insufficient
H3
  ↓
NEW INDEPENDENT RETRY
```

If H1 works, stop. Do not show H2/H3 automatically.

If H3 works, fade/remove the representation on the next independent retry where appropriate.

Hints restart thinking; they must not become staged answer revelation.

For teacher/parent misconception cards, prefer this visual structure:

```text
WHAT YOU MAY SEE
      ↓
VISUAL EXAMPLE / STRUCTURE
      ↓
H1 NOTICE
      ↓
H2 REMEMBER
      ↓
H3 REPRESENT
      ↓
INDEPENDENT RETRY
      ↓
STOP / FADE RULE
```

---

## Chapter and page planning

The subject schema defines **what must be learned**. The chapter/page plan defines **how the learner experiences it**.

Useful page types include:

```text
CHAPTER_OPENER
CONCEPT_DISCOVERY
CONNECT_REPRESENTATIONS
WORKED_EXAMPLE
GUIDED_PRACTICE
INDEPENDENT_PRACTICE
WORD_PROBLEM_LAB
REASONING_PAGE
MISCONCEPTION_CLINIC
CHECKPOINT
TRANSFER_CHALLENGE
MIXED_REVIEW
ASSESSMENT
ANSWER_KEY
TEACHER_GUIDANCE
```

Every page should have an explicit `page_type` and ordered semantic components. Do not make the renderer infer pedagogy from raw prose.

Prefer reusable components such as:

```text
LessonHeader
LearningObjective
LaunchContext
InstructionalModel
WhatShouldINotice
WorkedExample
GuidedPractice
IndependentPractice
TryIt
RememberBox
MistakeDetective
ReasoningChallenge
TransferChallenge
ReviewBlock
AnswerKeyBlock
TeacherNote
HintLadderCard
IndependentRetry
```

---

## Structured visual models

Whenever possible, store instructional visuals as structured data rather than only raster screenshots.

Math examples:

```text
COUNTERS
EQUAL_GROUPS
ARRAY
BAR_MODEL
NUMBER_LINE
PLACE_VALUE_MODEL
FACT_FAMILY
MULTIPLES_STRIP
EQUATION
WRITTEN_PROCEDURE
UNIT_CHAIN
REMAINDER_CONTEXT_MODEL
ERROR_COMPARISON
```

English examples:

```text
STORY_SEQUENCE
CHARACTER_EVIDENCE_MAP
MAIN_IDEA_DETAIL_MAP
COMPARE_CONTRAST_MAP
GRAMMAR_PATTERN_STRIP
SENTENCE_MODEL
WORD_FAMILY_MAP
WRITING_PLANNER
TEXT_EVIDENCE_HIGHLIGHT
```

For English, preserve source text/illustrations when instructional meaning depends on them. Visual organizers support evidence and pattern recognition; they do not replace the text.

---

## Division-specific publishing expectations

When publishing Grade 4 Division, load `Grade4MathDivisionPublishingContract.md` and ensure the student product visually supports relevant items such as:

- equal sharing vs equal grouping;
- multiplication/division fact family;
- estimation before exact division;
- multiples strip for 2-digit divisors;
- long-division place-value alignment;
- zero in the quotient;
- word-problem structure;
- quantity/unit chains such as dozen -> items -> money;
- remainder meaning in context;
- mistake-detective comparison.

For Teacher / Parent Division keys using hints, include visual H1-H3 sequences for high-value patterns such as:

- wrong operation choice;
- missing zero in quotient;
- unit/dozen conversion chain;
- 2-digit divisor / multiples support;
- remainder interpretation.

Each repair sequence must end with a fresh independent retry.

---

## Workbook / answer-key rules

### Workbook

Favor:

- response space;
- concise reminders;
- guided -> independent progression;
- mixed review;
- visual prompts where useful;
- minimal exposition.

### Answer key

Keep question IDs/numbers stable. Provide enough reasoning to verify answers without turning the key into a second textbook unless explicitly requested.

---

## Rendering and QA pipeline

Preferred pipeline:

```text
STRUCTURED CONTENT / PAGE PLAN
  -> RENDER PDF
  -> RENDER EVERY PAGE TO IMAGE
  -> INSPECT PAGE IMAGES
  -> FIX PAGE PLAN / VISUAL / TYPE / SPACING
  -> RE-RENDER
  -> REPEAT UNTIL PASS
```

A DOCX intermediate is acceptable when editability is the priority, but final PDF QA is still mandatory.

Do not approve a Grade 4 PDF from source text, extracted text, or code alone.

### Content QA

Check:

- no missing questions/tasks/answers;
- model/equation/text consistency;
- stable question numbering;
- valid cross-references;
- correct edition visibility;
- source fidelity/provenance preserved.

### Layout QA

Inspect every rendered page for:

- overflow/clipping;
- overlaps;
- orphan headings;
- awkward page breaks;
- tiny/illegible diagrams;
- broken symbols/equations;
- overcrowding;
- inadequate response space;
- accidental answer visibility;
- inconsistent navigation/margins.

### Child-usability QA

For student pages ask:

```text
Does this look designed for a Grade 4 child, or like adult notes placed into a PDF?
Is there enough visual structure?
Is prose short and child-facing?
Can the learner tell what to notice and what to do next?
Does the page ask the learner to do something?
Would an average child need an adult simply to decode the page design/explanation?
```

If the last answer is YES, the product is not finished.

### Pedagogical render QA

Also verify:

- instructional model matches the learning content;
- answer key matches the rendered question;
- early hints do not leak final answers;
- adult diagnostics are hidden from student pages;
- sequence preserves intended learning progression;
- repair sequences include independent retry;
- H1/H2/H3 are progressive rather than duplicate phrasings;
- writing/working space matches task demand.

---

## Product validation record

Retain at minimum:

```yaml
product_id: ...
edition: ...
source_content_version: ...
visual_profile: VISUAL_FIRST | SOURCE_FAITHFUL_TEXT_HEAVY
page_count: ...
content_qa: PASS | FAIL
layout_qa: PASS | FAIL
child_usability_qa: PASS | FAIL
pedagogy_qa: PASS | FAIL
hint_ladder_qa: PASS | NOT_APPLICABLE | FAIL
known_issues: []
```

---

## Publishing quality gates

A rendered product is incomplete until all applicable gates pass:

```text
P-QG1  VALIDATED_INPUT_CONTENT
P-QG2  OUTPUT_PROFILE_COMPLETE
P-QG3  CHAPTER_UNIT_PLAN_VALID
P-QG4  PAGE_PLAN_COMPLETE
P-QG5  COMPONENT_BINDINGS_VALID
P-QG6  VISUAL_MODEL_SEMANTICS_VALID
P-QG7  EDITION_FILTERING_VALID
P-QG8  CONTENT_QA_PASS
P-QG9  FULL_PAGE_RENDER_COMPLETE
P-QG10 LAYOUT_QA_PASS
P-QG11 PEDAGOGICAL_RENDER_QA_PASS
P-QG12 FINAL_PRODUCT_RECORD_COMPLETE
P-QG13 CHILD_FACING_VISUAL_FIRST
P-QG14 CHILD_LANGUAGE_AND_DENSITY_PASS
P-QG15 STUDENT_ADULT_EDITION_SEPARATION
P-QG16 INSTRUCTIONAL_VISUAL_COVERAGE
P-QG17 LEARNER_ACTION_DENSITY
P-QG18 HINT_LADDER_RENDER_VALID
P-QG19 INDEPENDENT_RETRY_VISIBLE
P-QG20 PAGE_IMAGE_CHILD_USABILITY_PASS
```

For a normal Grade 4 student study/revision guide, failure of P-QG13, P-QG14, P-QG16, P-QG17, or P-QG20 blocks release.

For a Teacher / Parent diagnostic key that exposes hints, failure of P-QG18 or P-QG19 blocks release.

---

## Cold-start handoff checklist

Before delivery, the producing agent must answer YES to all applicable items:

```text
[ ] Is the intended reader explicit?
[ ] Is the student edition visual-first unless source constraints require otherwise?
[ ] Does every major new concept have a meaningful visual/model when one exists?
[ ] Is prose chunked and child-friendly rather than research-style?
[ ] Are adult diagnostics separated from student content?
[ ] Are there observable learner actions, not only explanations?
[ ] If hints are shown to adults, are H1 NOTICE, H2 REMEMBER, H3 REPRESENT progressive?
[ ] Does repair end with an independent retry?
[ ] Were all PDF pages rendered to images and visually inspected?
[ ] Would an average Grade 4 learner understand how to use the page without repeatedly asking what the page means?
```

If the last answer is NO, revise the product before delivery.

## Handoff rule

If publishing exposes a missing concept, ambiguous answer, weak diagnostic, unsuitable question, or source discrepancy, return the issue to the appropriate subject skill. Do not repair pedagogical content inside the publishing layer without updating the source content record.
