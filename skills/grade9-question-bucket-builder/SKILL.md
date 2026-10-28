---
name: grade9-question-bucket-builder
description: Convert Grade 9 mathematics source questions into concept-first buckets with source integrity classification, invariant closure, faded transfer ladders, citation gates, and hard PDF preflight.
---

# Grade 9 Question Bucket Builder Skill

## Purpose

Use this skill when the user asks to analyse a Grade 9 Mathematics question set by pattern, group questions into concept buckets, create source-traced question-bank pages, revise an existing bucket, or produce PDF-ready concept-bucket material.

This skill is separate from a general `grade9-math` skill because its primary object is the **question-pattern bucket**, not a chapter or formula list:

```text
SOURCE QUESTIONS
  -> SOURCE INVENTORY
  -> SOURCE INTEGRITY CLASSIFICATION
  -> PATTERN FAMILY
  -> ONE INVARIANT
  -> CORE QUESTION
  -> CONCEPT / APPLICATION / SOLUTION
  -> FADED EXTENSION LADDER
  -> CITED PDF / WORKBOOK PAGE
```

## Mandatory references

Load and follow these references when applicable:

- `references/bucket-output-template.md`
- `references/source-integrity-protocol.md`
- `references/pedagogy-progression.md`
- `references/transfer-depth-ladder.md`
- `references/external-citation-gate.md`
- `references/pdf-layout-contract.md`
- `references/pdf-preflight-checklist.md`
- `references/benchmark-revision-protocol.md`
- `references/bucket-coverage-ledger.md`

For PDF production, `pdf-layout-contract.md` and `pdf-preflight-checklist.md` are mandatory hard gates.

## Trigger phrases

Use this skill for requests such as:

- "Analyse the pattern, not just answer."
- "Crack the concept."
- "Group the questions."
- "Create Group 1 / Group 2."
- "Bucket 1 / Bucket 2."
- "Concept -> application -> solution."
- "Similar variation from CBSE / IOQM / IMO."
- "Create PDF with citations."
- "How many groups still?"
- "Benchmark this bucket."
- "Revise the PDF layout."

## Core execution algorithm

```text
INGEST
  -> SOURCE INVENTORY
  -> SOURCE INTEGRITY CLASSIFICATION
  -> VERIFY SOURCE IMAGE / OCR
  -> FIND PATTERN FAMILIES
  -> DEFINE ONE INVARIANT
  -> INVARIANT CLOSURE TEST
  -> SEE -> REALIZE -> UNDERSTAND -> ADOPT
  -> WORKED -> PARTLY WORKED -> YOU DO -> TRANSFER
  -> ANSWER KEY + SOURCE LEDGER
  -> PDF PREFLIGHT
  -> PASS: DELIVER / FAIL: REGENERATE
```

Do not deliver a PDF merely because it was generated. Deliver it only after the preflight gate confirms it is student-readable, source-faithful, citation-safe, and free of broken glyphs.

## Source integrity is P0

Do not silently replace, repair, complete, or reinterpret source questions.

Every source question used in a bucket must be classified as one of:

- **CLEAN**: mathematically and contextually valid.
- **TYPOGRAPHIC/OCR AMBIGUITY**: visible source and extracted text differ, notation is damaged, or scan/OCR uncertainty is material.
- **MATHEMATICAL/DOMAIN ISSUE**: algebra may produce a result, but the result violates context/domain or the equation gives contradiction/identity unexpectedly.
- **INCOMPLETE/AMBIGUOUS SOURCE**: essential wording/data is missing; do not infer the missing condition as though it were printed.

For MATHEMATICAL/DOMAIN ISSUE, use exactly this student-facing structure:

```text
Algebraic model result:
Domain/context check:
Student-facing conclusion:
```

Preferred count-domain conclusion:

```text
As a count-of-people problem, this has no valid whole-number solution as written.
```

## Source image authority over OCR

For scanned/image-heavy PDFs:

1. parsed text is navigation evidence;
2. rendered source page is transcription authority when OCR is suspect;
3. never silently reconstruct missing source text;
4. record material OCR/scan uncertainty in a Source Integrity Note.

## Core pedagogy

Follow the Grade 9 Mathematics method:

```text
SEE -> REALIZE -> UNDERSTAND -> ADOPT
```

Question-bank solving follows:

```text
RECOGNIZE -> SOLVE -> CHECK -> TRANSFER
```

Mathematics mastery target:

```text
PATTERN -> INVARIANT -> STRUCTURE -> TRANSFER
```

## Invariant closure test

Each bucket must pass this test before writing solutions or a PDF:

```text
Could a student state in one sentence what remains mathematically unchanged across every source question in this bucket?
```

If not, either the bucket is too broad or the instructional explanation is incomplete.

The invariant must be the spine of the page sequence:

```text
REPRESENTATION
  -> INVARIANT
  -> METHOD
  -> SOLUTION CLASSIFICATION
  -> TRANSFER
```

## Faded pedagogical progression

A bucket should normally progress as:

```text
Level 0  Pattern Crack
Level 1  Fully worked anchor
Level 2  Worked source extension
Level 3  Partly worked adapted item
Level 4  Independent same-structure item
Level 5  Structural transfer
Level 6  Olympiad-foundation/generalisation
```

Do not merely add similar questions. Fade support deliberately.

## Transfer depth rule

Transfer questions must change reasoning, not merely numbers.

Use this ladder:

- **Level A - Near transfer**: same invariant, changed numbers/representation.
- **Level B - Structural transfer**: student must first recognize which invariant applies.
- **Level C - Generalisation**: introduce parameters, prove a pattern, derive a condition, classify possibilities, or work backwards.
- **Level D - Olympiad-foundation**: require an additional structural insight beyond routine execution.

An IOQM-style or IMO-foundation item must not be only the source question with harder numbers.

## Method comparison

If two pedagogically useful methods exist, include a compact Method Choice card:

```text
Method | Core idea | Best when | Main risk
```

Examples: rotation vs equal-distance; elimination vs substitution; LCM-first vs combine-fractions-first; forward conservation vs reverse-from-final-state.

Do not invent a second method merely to satisfy the template.

## Check taxonomy

Use the relevant check types explicitly:

1. **Algebraic check**: substitute into the original equation/system.
2. **Structural check**: verify the invariant is satisfied.
3. **Domain/context check**: integer count, positive length, permissible value, units.
4. **Reasonableness check**: magnitude, sign, order, and story plausibility.

## First-move contract

Every bucket must answer:

```text
If a student sees a new problem of this family, what should they write in the first 10-20 seconds?
```

Examples:

- Fraction equation: `LCM = ...`
- Redistribution: `Let initial first group = x; second group = total - x.`
- Hidden coordinate variables: first recover the actual coordinates.
- Equilateral third vertex: `Let P(x,y); write PA^2 = AB^2 and PB^2 = AB^2.`

## Misconception format

Use this diagnostic format, not a bare list of traps:

```text
Mistake:
Why it happens:
How to detect it:
Repair move:
```

## Student-facing voice

The workbook must not sound like an audit report.

Use student-safe language such as:

```text
Check whether the answer makes sense as a number of people.
```

Avoid source-governance language in student pages, such as:

```text
Source validity gate failed.
```

Teacher/source-custody language may appear only in a compact Source Integrity Note.

## Citation policy

Never invent year tags. A label such as `IOQM 2024 Q5`, `CBSE 2023 Q...`, `NCERT Exemplar Q...`, or `IMO past question` is prohibited unless the External Citation Gate passes.

If any verification box fails, downgrade to:

- `IOQM-style adapted`
- `Olympiad-style adapted`
- `CBSE/NCERT-aligned adapted`
- `Author-created transfer`

## Bucket format

Every bucket should contain:

```text
Group N / Bucket N - <concept title>

1. Source trace and integrity classification
2. Why these questions belong together
3. Invariant closure sentence
4. Pattern crack / recognition card
5. Anchor source question
   - Concept
   - Application
   - Solution
   - Check taxonomy
6. Extension source questions
7. Misconception -> Diagnostic -> Repair
8. Faded transfer ladder
9. Method comparison, if useful
10. Exit ticket / first-move test
11. Answer key / compact solutions
12. Source trace and references
```

## PDF notation and preflight are P0

Use PDF-safe notation unless broad Unicode rendering has been verified.

Prefer:

- `t1`, `t2`
- `1/2`
- `x^2` when needed
- `sqrt(3)` if glyph support is uncertain
- `->`
- `+/-`
- `AUTHOR-CREATED`, `IMO-FOUNDATION`

Avoid relying on subscript glyphs, superscript glyphs, special fraction characters, unusual arrows, or special hyphen/dash variants unless the embedded font and rendered output are verified.

Embed DejaVu Sans or another broad Unicode font when generating PDFs.

Before delivery, run the full PDF preflight checklist. If any required item fails, do not deliver; regenerate and rerun the complete preflight.

## Coverage ledger

For a mixed source set, maintain a bucket coverage ledger:

```text
Q1 -> Group 1
Q2 -> Group 2
...
MCQ1-7 -> Group 7
```

At completion report:

```text
SOURCE COVERAGE
numbered questions assigned:
image-section questions assigned:
unassigned:
duplicated with stated reason:
```

## Benchmark-before-revision

When revising an existing bucket:

1. inspect a strong existing bucket if available;
2. compare pedagogical functions, not appearance;
3. identify what is missing;
4. preserve the current bucket's mathematical identity;
5. do not copy wording, problems, layouts, or visual composition;
6. regenerate only after gap analysis.

## Recommended group planning for uploaded mixed Grade 9 linear/geometry sets

Use this default grouping if the source resembles the current `math.pdf` mixed set:

1. **Straight line as hidden object** - line through intersection, price-demand line, graphical systems and area, collinearity, intercepts.
2. **Equilateral vertex from two coordinates** - rotation/symmetry/equal-distance/quadratic structure.
3. **Relative speed as simultaneous linear equations** - boat/current and plane/wind.
4. **Fractional linear equations** - clearing denominators, sign safety, and solution-set classification.
5. **Hidden variables in coordinates** - ordered-pair parameter decoding and line membership.
6. **Redistribution before-after balance** - conservation, transfer, equalisation, and domain feasibility.
7. **Euclid foundations** - optional MCQ/definition/axiom bucket if present.

## Final response style

When reporting completion, include:

- branch/PR/merge status if repository changes were made;
- files changed;
- validation summary;
- PDF preflight result if a PDF was created;
- NOT_RUN items, if any.
