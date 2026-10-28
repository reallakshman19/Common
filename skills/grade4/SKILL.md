---
name: grade4
description: Route Grade 4 learning-material tasks to the correct Mathematics, English, and publishing workflows. Use for Grade 4 source analysis, chapter creation, learning cells, question banks, worksheets, assessments, diagnostics, revision, Olympiad/HOTS extensions, and student/teacher PDF production.
---

# Grade 4 Router Skill

## Purpose

Use this skill as the entrypoint for Grade 4 educational-content work in this repository.

Do **not** apply one generic pedagogy across subjects. Route to the subject-specific skill first, then to the publishing skill only when a rendered product is requested.

```text
GRADE 4 REQUEST
   |
   +-- Mathematics --> ../grade4-math/SKILL.md
   |
   +-- English -----> ../grade4-english/SKILL.md
   |
   +-- PDF / book / workbook / teacher edition
                     --> subject skill first
                     --> ../grade4-publishing/SKILL.md second
```

## Routing rules

### Mathematics

Use `../grade4-math/SKILL.md` when the task concerns:

- number and operations;
- multiplication/division;
- fractions/decimals within Grade 4 scope;
- measurement;
- geometry;
- data handling;
- mathematical reasoning;
- school/HOTS/Olympiad mathematics;
- mathematics question banks or diagnostics.

### English

Use `../grade4-english/SKILL.md` when the task concerns:

- reading comprehension;
- vocabulary;
- grammar;
- writing;
- passages, stories, poems, informational texts;
- language diagnostics;
- English worksheets, assessments, or study material.

### Publishing

Use `../grade4-publishing/SKILL.md` only after subject content has been validated when the user requests:

- student textbook PDF;
- teacher edition;
- workbook;
- answer key;
- assessment booklet;
- screen/print PDF;
- page-plan or rendering work.

## Intent classification

Resolve the request into one or more modes:

```text
ANALYZE_SOURCE
BUILD_CHAPTER
BUILD_LEARNING_CELL
BUILD_QUESTION_BANK
BUILD_PRACTICE
BUILD_DIAGNOSTIC
BUILD_ASSESSMENT
BUILD_REVISION
BUILD_OLYMPIAD
BUILD_TEXTBOOK
BUILD_WORKBOOK
BUILD_TEACHER_EDITION
BUILD_PDF
```

If the user provides a source, preserve the source as the primary basis. Do not silently replace its terminology, order, examples, or scope with general knowledge.

## Shared Grade 4 rules

1. **Source fidelity first.** Keep original wording, models, answer structure, lesson sequence, and terminology when source-grounded work is requested.
2. **Stay at Grade 4 level.** Do not silently introduce higher-grade formalism.
3. **No silent scope expansion.** Tag extension/HOTS/Olympiad material separately.
4. **Separate source from authored content.** Preserve provenance.
5. **Child-facing language must be simple.** Internal metadata may remain sophisticated.
6. **Do not equate correctness with mastery.** Use the subject-specific mastery model.
7. **Do not treat similar questions as surface copies.** Use controlled structural transfer.
8. **Diagnostics must be causal.** Wrong answer -> hypothesis -> probe -> repair -> retry.
9. **PDF generation is downstream.** Never change pedagogy merely to fit a page.
10. **Run quality gates before completion.**

## Source policy

When supplied sources are the requested basis:

```text
SOURCE
  -> inspect structure
  -> preserve terminology and sequence
  -> extract faithfully
  -> identify gaps/ambiguities
  -> tag reconstruction or QC issues
  -> enrich only where permitted
```

Do not silently correct a defective source item. Preserve the original in provenance and mark the defect.

When outside research is requested or needed for provenance/verification, keep it visibly distinct from source-derived material.

## Minimum quality gates

A Grade 4 task is not complete until the applicable checks pass:

- `QG1 SOURCE_FIDELITY`
- `QG2 GRADE_APPROPRIATENESS`
- `QG3 COVERAGE`
- `QG4 LEARNING_PROGRESSION`
- `QG5 PRACTICE_VARIATION`
- `QG6 REASONING`
- `QG7 DIAGNOSTICS`
- `QG8 MASTERY`
- `QG9 TRANSFER`
- `QG10 PUBLISHING_QA` when rendered output is requested

## Output contract

Always state internally which subject workflow and mode are active. The final output should be the requested artifact/content, not a description of the workflow unless the user asks for the workflow itself.
