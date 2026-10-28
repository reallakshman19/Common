# External Citation Gate

## Purpose

Prevent fake official provenance. No source/year/question claim may be made unless mechanically verified.

## Official claim gate

A label such as any of the following is prohibited unless all checks pass:

- `IOQM 2024 Q5`
- `CBSE 2023 Q...`
- `NCERT Exemplar Q...`
- `IMO past question`

Required checks:

```text
[ ] official PDF/page opened
[ ] exact question found
[ ] year/question identifier checked
[ ] wording comparison performed
[ ] reference recorded
[ ] item labelled VERBATIM / PARAPHRASED / STRUCTURALLY INSPIRED
```

If any box is false, downgrade the label.

## Downgrade labels

Use one of:

- `IOQM-style adapted`
- `Olympiad-style adapted`
- `CBSE/NCERT-aligned adapted`
- `Author-created transfer`

## Allowed provenance classes

### VERBATIM

The item is copied exactly from an official source. Use only when quotation/copyright constraints allow it and the user needs it.

### PARAPHRASED

The mathematical structure and data are from an official source, but wording is rewritten. Must still cite exact official source and question identifier.

### STRUCTURALLY INSPIRED

The official item contains a comparable pattern, but the workbook item is newly written. State this clearly.

### STYLE-ALIGNED / ADAPTED

No exact official source claim. The item is generated to match syllabus or contest style.

## Preferred sources

1. official NCERT pages/PDFs;
2. official CBSE pages/PDFs;
3. HBCSE/MTAI/official olympiad pages/PDFs;
4. other reputable sources only when official sources are unavailable, and never for official year/question claims.

## Reference section requirement

For each external item, record:

```text
label:
source_url_or_file:
official_body:
year_if_verified:
question_number_if_verified:
use_class: VERBATIM | PARAPHRASED | STRUCTURALLY_INSPIRED | STYLE_ALIGNED
notes:
```

## Final wording examples

Good:

```text
IOQM-style adapted. No official IOQM question is claimed.
```

Good:

```text
Structurally inspired by official IOQM 2024 Q5; this workbook item is paraphrased/reduced and not a facsimile.
```

Bad:

```text
IOQM 2024 Q5
```

unless all gate checks pass.
