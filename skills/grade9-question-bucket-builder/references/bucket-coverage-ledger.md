# Bucket Coverage Ledger

## Purpose

Make source coverage explicit so no source question disappears and no question is duplicated without reason.

## When required

Use a coverage ledger whenever the user provides a mixed source set or asks:

- how many groups remain;
- whether all questions are covered;
- to continue the next group;
- to produce a complete question-bank/PDF set.

## Source inventory format

```text
source_file:
source_page_count:
source_sections:
rendered_pages_checked:
ocr_risk:
```

## Question assignment table

```text
Source item | Page | Integrity class | Bucket | Role | Status | Notes
Q1          | p.1  | CLEAN           | G1     | anchor/extension | done | ...
Q2          | p.1  | CLEAN           | G2     | anchor           | done | ...
MCQ7        | p.2  | INCOMPLETE/AMBIGUOUS_SOURCE | G7 | diagnostic | pending | missing wording
```

## Completion report

At the end of a batch, report:

```text
SOURCE COVERAGE
numbered questions assigned:
image-section questions assigned:
unassigned:
duplicated with stated reason:
incomplete/ambiguous:
mathematical/domain issue:
```

## Status values

- `not_started`
- `mapped`
- `in_progress`
- `pdf_created`
- `preflight_passed`
- `blocked_source_ambiguity`
- `needs_revision`

## Duplication rule

A source question may appear in more than one bucket only if its role differs and the reason is stated.

Example:

```text
Q14 appears in Group 1 as straight-line intercept evidence and in a later graphing practice appendix as an axis-intercept drill.
```

## Remaining-groups answer rule

When the user asks `How many groups still?`, answer from the coverage ledger, not memory.
