# Grade 9 Question Bucket PDF Layout Contract

## Purpose

The PDF is a student-facing workbook artifact with source custody. It must be readable, source-faithful, citation-safe, and preflighted before delivery.

## Page types

Use these page types in order unless the user requests otherwise.

1. **Cover page**
   - Group number and bucket title.
   - One-sentence invariant.
   - Source status and integrity summary.

2. **Source trace and integrity page**
   - Table of source questions, pages, roles, and integrity classes.
   - Note OCR/notation cleanup.
   - Source Integrity Note only when needed.

3. **Pattern crack page**
   - Representation.
   - Invariant.
   - First-move recognition card.
   - Common wrong start.

4. **Anchor solution page**
   - Source question.
   - Concept -> Application -> Solution -> Check.
   - Keep long algebra in numbered steps.

5. **Worked source extension page(s)**
   - Extension questions from the same source group.
   - What changes / what stays invariant.

6. **Faded transfer page(s)**
   - Partly worked adapted item.
   - Independent same-structure item.
   - Structural transfer.
   - Olympiad-foundation/generalisation.

7. **Misconception and repair page**
   - Mistake.
   - Why it happens.
   - How to detect it.
   - Repair move.

8. **Exit ticket page**
   - First-move prompts.
   - Short independent questions.
   - Compact answer key.

9. **References page**
   - Uploaded source references.
   - Repository methodology references.
   - External official citations and use class.

## Page economy

Prefer one dominant learning job per page.

Do not:

- shrink text merely to fit another card;
- create many micro-cards;
- leave half a page empty when the next concept naturally fits;
- pack dense algebra into tiny tables.

Aim for:

- readable Grade 9 workbook typography;
- 2-4 major visual regions per page;
- algebra split into meaningful steps;
- whitespace for thinking/work, not accidental emptiness.

## Student-facing language

Use supportive workbook language:

```text
Check whether the answer makes sense as a number of people.
```

Avoid audit-heavy language in the workbook body:

```text
Source validity gate failed.
```

Teacher/source-custody language belongs only in a compact Source Integrity Note.

## Source and generated question separation

Visually distinguish:

- source questions;
- adapted practice;
- official verified/paraphrased items;
- author-created transfer items.

Use labels such as:

- `[S1] Source`
- `[A1] Adapted`
- `[R1] Reference`
- `[IOQM-style adapted]`
- `[IOQM verified bridge]` only when the citation gate passes.

## PDF-safe notation

Prefer conservative notation unless the embedded font and rendered output are verified.

Prefer:

- `t1`, `t2`
- `1/2`
- `x^2`
- `sqrt(3)` when glyph support is uncertain
- `->`
- `+/-`
- ASCII hyphen labels such as `AUTHOR-CREATED`, `IMO-FOUNDATION`

Avoid relying on:

- subscript glyphs;
- superscript glyphs;
- special fraction characters;
- unusual arrows;
- special hyphen/dash variants;
- invisible/private-use characters.

Broad Unicode math such as `sqrt` glyphs, superscripts, or arrows may be used only when font embedding and rendered output are verified.

Embed DejaVu Sans or another broad Unicode font when generating PDFs.

## Design rules

- Use A4 portrait unless geometry diagrams need wider layout.
- Use clear margins and readable font sizes.
- Use cards for Concept, Application, Formula/Tool, Misconception, First Move, and Exit Ticket.
- Keep source questions visibly separate from generated variations.
- Put citations/source notes at the bottom of the page or in a final reference page.
- Avoid cramped full-page algebra; split long solutions into numbered steps.
- Include diagrams where the concept is geometric and diagrams improve recognition.

## Preflight

This contract delegates hard delivery checks to `pdf-preflight-checklist.md`.

A PDF that has not passed that checklist must not be delivered.
