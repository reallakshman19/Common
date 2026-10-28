---
name: grade4-english
description: Create and analyze Grade 4 English learning content using language-skill maps, text profiles, evidence/reasoning models, domain-specific Learning Cells, diagnostics, writing rubrics, mastery evidence, transfer, and textbook-quality publishing.
---

# Grade 4 English Skill

## Mandatory reference

Always load and follow:

- `../../Grade4EnglishSchema.md`
- `../../Primary/Architecture/PRIMARY_INTEGRATED_ARCHITECTURE.md`
- `../../Primary/Architecture/SEMANTIC_OWNERSHIP.md`

For interactive tutoring, adaptive teaching, diagnostic repair, repeated learner clarification, scaffold selection/fading, or learner-state interpretation also load:

- `../primary-teacher-runtime/SKILL.md`
- `../../Primary/Architecture/PRIMARY_TEACHER_RUNTIME.md`

For PDF/book production also load:

- `../../Grade4PublishingSchema.md`

Do not force English into the Mathematics learning model. The central relationship is:

```text
TEXT / LANGUAGE FEATURE
  -> SKILL
  -> EVIDENCE / LANGUAGE KNOWLEDGE
  -> REASONING
  -> RESPONSE
  -> DIAGNOSIS
  -> TRANSFER
```

For tutoring, the subject model runs inside the Primary Teacher Runtime:

```text
OBSERVATION
  -> RESPONSE DIAGNOSIS
  -> TEACHER DECISION
  -> TEACHER MOVE
  -> CHILD ACTION
  -> NEW EVIDENCE
```

Keep raw evidence separate from judgement, `SkillState` separate from `CurrentLearningState`, conceptual support separate from access/load adjustments, and acquisition/independent-use/delayed-retention/transfer evidence separate from one another.

## Domains

Route each task internally to one or more domains:

```text
READING
VOCABULARY
GRAMMAR
WRITING
```

Mixed tasks may combine domains, but each domain retains its own pedagogy and mastery criteria.

## Supported modes

```text
ANALYZE_SOURCE
BUILD_UNIT
BUILD_TEXT_PROFILE
BUILD_LEARNING_CELL
BUILD_QUESTION_BANK
BUILD_PRACTICE
BUILD_DIAGNOSTIC
BUILD_ASSESSMENT
BUILD_REVISION
BUILD_LANGUAGE_COMPETITION_EXTENSION
BUILD_TEXTBOOK
BUILD_WORKBOOK
BUILD_TEACHER_EDITION
BUILD_PDF
```

## Workflow

### Stage 1 — Resolve scope

Determine:

- grade = 4;
- English domain(s);
- unit/text/grammar/writing focus;
- source/curriculum basis;
- requested output;
- school/competition/extension target;
- whether strict source fidelity is required.

Do not silently increase text complexity, vocabulary level, grammar formalism, or writing expectations beyond Grade 4/source scope.

### Stage 2 — Load schema

Load `Grade4EnglishSchema.md` before designing content.

If the task is source-grounded, source structure takes priority over generic sequencing unless the user explicitly asks for a redesign.

### Stage 3 — Reverse-engineer source

When source material is supplied, inspect and preserve:

- passage/story/poem/informational text;
- genre and text structure;
- paragraph boundaries;
- dialogue, punctuation, capitalization, headings, captions, illustrations;
- vocabulary focus;
- reading skill sequence;
- grammar focus;
- writing outcome;
- worked/model responses;
- practice progression;
- assessment/question formats.

Do not silently rewrite a source text if the task is to study or build from it.

#### Simplified source taxonomy boundary

When a Grade 4 source teaches a simplified grammar taxonomy, preserve that model exactly. If an example does not fit cleanly, do **not** invent a new source category or silently switch to a fuller linguistic model.

Use the Primary source-boundary semantics:

```text
SOURCE MODEL
  -> attempt classification
  -> if no clean match: SOURCE_BOUNDARY / AMBIGUOUS
  -> child-friendly boundary explanation
  -> fuller canonical analysis kept separate
```

For example, if a workbook teaches adjective order only as `number -> opinion -> size -> age -> shape -> colour -> origin -> material -> purpose`, do not silently add `quality`, `condition`, or `quality/type` to force-fit words such as `heavy`, `broken`, or `handmade`.

### Stage 4 — Build language-skill architecture

Map content using the schema.

Typical Reading skills include:

```text
LITERAL_COMPREHENSION
KEY_DETAIL
SEQUENCE
CAUSE_EFFECT
MAIN_IDEA
SUMMARY
CHARACTER
SETTING
INFERENCE
PREDICTION
POINT_OF_VIEW
AUTHOR_PURPOSE
COMPARE_CONTRAST
TEXT_EVIDENCE
```

Typical Vocabulary skills include:

```text
WORD_MEANING
CONTEXT_CLUES
SYNONYM
ANTONYM
MULTIPLE_MEANING
PREFIX
SUFFIX
ROOT_WORD
IDIOM
FIGURATIVE_LANGUAGE
WORD_CHOICE
```

Typical Grammar skills include:

```text
NOUN
PRONOUN
VERB
TENSE
ADJECTIVE
ADVERB
ARTICLE
PREPOSITION
CONJUNCTION
SUBJECT_VERB_AGREEMENT
SENTENCE_STRUCTURE
PUNCTUATION
CAPITALIZATION
EDITING
```

Typical Writing skills include:

```text
IDEA_GENERATION
PLANNING
ORGANIZATION
TOPIC_SENTENCE
SUPPORTING_DETAILS
SEQUENCING
PARAGRAPHING
WORD_CHOICE
SENTENCE_CONSTRUCTION
REVISION
EDITING
NARRATIVE
DESCRIPTION
OPINION
SUMMARY_WRITING
```

### Stage 5 — Build prerequisite graph

Store prerequisite relationships with strength where useful.

Examples:

```text
INFERENCE
  <- sentence comprehension (CRITICAL)
  <- vocabulary (CRITICAL)
  <- locate details (CRITICAL)
  <- cause/effect (STRONG)

SUBJECT_VERB_AGREEMENT
  <- identify subject
  <- identify verb
  <- singular/plural
  <- present-tense forms
```

Diagnostics should descend this graph when errors occur.

### Stage 6 — Build text profile

For passages/texts record relevant demands such as:

- genre/text type;
- word count;
- sentence complexity;
- paragraph count;
- vocabulary load;
- dialogue load;
- pronoun-reference load;
- figurative-language load;
- inference density;
- information density;
- chronology complexity;
- background-knowledge demand;
- illustration/caption/table dependence.

Text length alone is not difficulty.

### Stage 7 — Build Learning Cells

A Learning Cell should define, as relevant:

- objective and success criteria;
- child-friendly meaning;
- prerequisites;
- language/text feature;
- worked/model example;
- `what_to_notice`;
- recognition cues;
- skill trigger;
- reasoning/language moves;
- evidence expectations;
- guided practice;
- controlled variation;
- independent practice;
- misconceptions;
- diagnostic probes;
- repair path;
- mastery evidence;
- transfer.

For tutoring, do not expose a Learning Cell as one long explanation. Instantiate it through the Primary Teacher Runtime as a learner-facing `LearningEpisode` with child actions, diagnostic evidence, repair, retry, and support fading.

### Stage 8 — Task archetypes

Do not create large banks from superficial wording changes.

Reading archetypes may include:

```text
LOCATE
SELECT
SEQUENCE
MATCH
COMPARE
INFER
PREDICT
SUMMARIZE
IDENTIFY_MAIN_IDEA
IDENTIFY_CHARACTER_TRAIT
FIND_EVIDENCE
JUSTIFY_WITH_EVIDENCE
```

Vocabulary archetypes may include:

```text
DEFINE
CONTEXT_MEANING
MATCH
SYNONYM
ANTONYM
WORD_PART_ANALYSIS
REPLACE
USE_IN_SENTENCE
```

Grammar archetypes may include:

```text
IDENTIFY
CLASSIFY
COMPLETE
CHOOSE
CORRECT
TRANSFORM
COMBINE
EDIT
APPLY_IN_WRITING
```

Writing archetypes may include:

```text
PLAN
GENERATE
ORGANIZE
DRAFT
EXPAND
REVISE
EDIT
SUMMARIZE
RESPOND_TO_TEXT
```

### Stage 9 — Language fingerprint

Each objective question/task should capture relevant fields such as:

- domain;
- skill/subskill;
- task action;
- text type;
- target language feature;
- evidence type;
- evidence location;
- recognition cues;
- reasoning moves;
- language knowledge;
- distractor logic where applicable;
- response form;
- expected reasoning path;
- transfer invariant.

### Stage 10 — Evidence and response model

For Reading comprehension distinguish:

```text
ANSWER
+ EVIDENCE
+ REASONING
```

A correct choice without support may indicate guessing rather than mastery.

For Writing do not force a single correct-answer model. Use a rubric appropriate to the task, e.g.:

- ideas/content;
- organization;
- evidence/details;
- vocabulary/word choice;
- sentence control;
- grammar;
- punctuation/capitalization;
- spelling when in scope;
- revision/editing independence.

### Stage 11 — Difficulty

Use a profile rather than only `easy/medium/hard`.

Consider:

- decoding demand;
- vocabulary demand;
- sentence-comprehension demand;
- text-location demand;
- evidence-integration demand;
- inference demand;
- grammar-knowledge demand;
- language-production demand;
- writing-organization demand;
- working-memory demand;
- distractor subtlety;
- response demand;
- text length;
- transfer distance.

### Stage 12 — Helpers and hints

Do not use one universal English hint ladder.

For Reading, typical progression:

```text
H1 LOOK
H2 REMEMBER
H3 FIND
H4 CONNECT / THINK
H5 RESPOND
```

For Grammar:

```text
H1 FIND THE TARGET
H2 REMEMBER THE RULE
H3 TEST THE OPTIONS
H4 REREAD
H5 APPLY
```

For Writing:

```text
IDEA
ORGANIZE
EXPAND
REVISE
EDIT
```

Hints should preserve productive struggle and avoid revealing the final response too early.

In interactive tutoring, record conceptual hint/support separately from access adjustments such as reduced language, one-step-at-a-time directions, read-aloud support, reduced writing, or oral response.

### Stage 13 — Diagnostics

Use domain-specific error classes such as:

```text
DECODING_ERROR
VOCABULARY_ERROR
REFERENCE_ERROR
TEXT_LOCATION_ERROR
LITERAL_COMPREHENSION_ERROR
INFERENCE_ERROR
EVIDENCE_ERROR
GRAMMAR_RULE_ERROR
APPLICATION_ERROR
RESPONSE_FORM_ERROR
WRITING_IDEA_ERROR
WRITING_ORGANIZATION_ERROR
SENTENCE_CONTROL_ERROR
EDITING_ERROR
SOURCE_MODEL_BOUNDARY
INSUFFICIENT_EVIDENCE
```

Use the causal loop:

```text
OBSERVED RESPONSE
  -> ERROR SIGNATURE
  -> HYPOTHESIS
  -> DIAGNOSTIC QUESTION
  -> EVIDENCE
  -> REPAIR
  -> RETRY
```

Example: a plausible inference with no supporting sentence may be an `EVIDENCE_ERROR`, not necessarily an `INFERENCE_ERROR`.

A short clarification such as `Large?` is evidence that category recognition may not yet be secure. Do not only return the label. Give the recognition cue and one tiny check-for-understanding item when in tutor mode.

After two unsuccessful attempts using substantially the same route, change a meaningful teaching dimension instead of repeating the same explanation at greater length.

### Stage 14 — Practice sequencing

Reading example:

```text
teacher model
-> explicit clue
-> one-clue reasoning
-> multiple-clue reasoning
-> choose best inference
-> justify with evidence
-> new passage
-> new genre
```

Grammar example:

```text
recognize
-> classify
-> select
-> complete
-> correct
-> transform
-> own sentence
-> apply in writing
```

Writing example:

```text
model
-> plan
-> shared/guided composition
-> independent draft
-> revision
-> editing
-> new prompt transfer
```

### Stage 15 — Mastery

Reading mastery may require evidence that the learner can:

- locate evidence;
- understand literal meaning;
- integrate information;
- infer;
- justify;
- transfer to unfamiliar text.

Vocabulary mastery should move from recognition to contextual understanding and appropriate use.

Grammar mastery should move from recognition to correction, explanation, and independent use.

Writing mastery should consider ideas, organization, development, language, sentence control, conventions, revision, and independence.

For Primary runtime state, do not collapse evidence into one mastery label. Track relevant evidence separately for:

```text
ACQUISITION
INDEPENDENT_USE
DELAYED_RETENTION
TRANSFER
STRETCH (optional)
```

Same-session correctness cannot establish delayed retention.

### Stage 16 — Transfer

Reading transfer may progress:

```text
same skill/same text
-> same skill/new text
-> longer text
-> new genre
-> multiple clues
-> multiple skills
-> evidence justification
-> cross-text reasoning
```

Grammar transfer may progress:

```text
identify
-> complete
-> correct
-> transform
-> new context
-> own sentence
-> independent writing
```

Writing transfer may progress:

```text
imitate model
-> change details
-> new prompt/same structure
-> new context
-> independent composition
```

## Source fidelity and provenance

For source-grounded tasks:

- preserve text exactly where reproduction is allowed and requested;
- preserve punctuation/capitalization/paragraphs when instructionally relevant;
- distinguish source questions from authored questions;
- do not silently simplify/rewrite passages;
- mark reconstructed or ambiguous source content;
- keep outside research visibly separate from source-derived content;
- do not silently introduce a grammar category absent from a simplified source taxonomy;
- use `SOURCE_BOUNDARY`/`AMBIGUOUS` when the source model cannot classify an example cleanly.

## English quality gates

A deliverable is incomplete until applicable checks pass:

- `E-QG1 SOURCE_FIDELITY`
- `E-QG2 GRADE4_TEXT_COMPLEXITY`
- `E-QG3 SKILL_COVERAGE`
- `E-QG4 PREREQUISITE_INTEGRITY`
- `E-QG5 TEXT_PROFILE_VALIDITY`
- `E-QG6 EVIDENCE_REASONING_ALIGNMENT`
- `E-QG7 TASK_VARIATION`
- `E-QG8 DOMAIN_SPECIFIC_HINT_QUALITY`
- `E-QG9 DIAGNOSTIC_CAUSALITY`
- `E-QG10 MASTERY_EVIDENCE`
- `E-QG11 TRANSFER_COVERAGE`
- `E-QG12 ANSWER_OR_RUBRIC_VALIDITY`
- `E-QG13 SOURCE_MODEL_BOUNDARY`
- `E-QG14 PRIMARY_RUNTIME_ALIGNMENT` when tutoring/adaptation is used

## Publishing handoff

If a rendered product is requested:

1. validate English content first;
2. load `../grade4-publishing/SKILL.md`;
3. pass validated texts, questions, model responses/rubrics, answer keys, teacher notes, diagnostics, and provenance;
4. never rewrite or shorten a source text solely to solve a layout problem unless the user explicitly approves an editorial adaptation.
