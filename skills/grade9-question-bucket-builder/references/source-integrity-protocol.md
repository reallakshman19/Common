# Source Integrity Protocol

## Purpose

Every bucket must preserve the source as evidence. Do not silently repair, complete, rewrite, or replace a source question.

## Classification

Classify every source question used in a bucket.

### A. CLEAN

The source is mathematically and contextually valid.

Required action:

- solve normally;
- cite the page/question;
- still run normal checks.

### B. TYPOGRAPHIC/OCR AMBIGUITY

Visible source and extracted text differ, notation is damaged, or scan/OCR uncertainty is material.

Required action:

- inspect the rendered source page/image;
- treat parsed text as navigation evidence only;
- transcribe from the rendered page when possible;
- record the uncertainty in a Source Integrity Note;
- if essential symbols remain uncertain, ask or mark unresolved.

### C. MATHEMATICAL/DOMAIN ISSUE

The algebra may produce a value, contradiction, or identity, but the result violates context/domain or the wording asks for something that is not context-valid.

Required student-facing format:

```text
Algebraic model result:
Domain/context check:
Student-facing conclusion:
```

Preferred count-domain conclusion:

```text
As a count-of-people problem, this has no valid whole-number solution as written.
```

Do not write audit-heavy wording such as `source validity gate failed` in the student workbook. Put any source-custody detail in a compact Source Integrity Note.

### D. INCOMPLETE/AMBIGUOUS SOURCE

Essential wording, data, diagram, option, or condition is missing.

Required action:

- do not infer the missing condition as though it were printed;
- state exactly what is visible and what is missing;
- if a likely reconstruction is useful, label it `Possible intended reconstruction`, not `Source`;
- generated follow-up questions must be labelled as adapted/author-created.

## Source image authority over OCR

For scanned/image-heavy PDFs:

1. parsed text is navigation evidence;
2. rendered page/image is transcription authority when OCR is suspect;
3. material uncertainty must be recorded;
4. missing source text must not be silently reconstructed.

## Required source trace fields

```text
source_id:
page:
question_number:
rendered_source_checked: yes | no | not_needed
integrity_class: CLEAN | TYPOGRAPHIC/OCR_AMBIGUITY | MATHEMATICAL/DOMAIN_ISSUE | INCOMPLETE/AMBIGUOUS_SOURCE
student_facing_note:
teacher/source_custody_note:
```

## Delivery blocker

If the source question is INCOMPLETE/AMBIGUOUS and the missing information is essential, do not produce a false solved source item. Produce either:

- a diagnostic note; or
- an adapted reconstruction clearly separated from source.
