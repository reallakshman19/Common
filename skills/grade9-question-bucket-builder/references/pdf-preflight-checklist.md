# PDF Preflight Checklist

## Delivery rule

Do not deliver a PDF merely because it was generated.

A PDF may be delivered only after the complete preflight passes.

## Required preflight

```text
[ ] render every page
[ ] visually inspect every page
[ ] extract PDF text
[ ] search for U+FFFD replacement character: �
[ ] search for ￾
[ ] search for ■
[ ] search for □
[ ] no clipped right-margin text
[ ] no clipped equations
[ ] no orphan headings
[ ] no broken badge labels
[ ] no unexpected blank pages
[ ] source questions visually distinct
[ ] adapted/generated questions correctly labelled
[ ] answer key present
[ ] Source Trace and References present
[ ] broad font embedded or rendering verified
```

If one item fails:

```text
DO NOT DELIVER
-> regenerate
-> rerun complete preflight
```

## Text extraction scan

When possible, programmatically extract text from the generated PDF and scan for:

- `�`
- `￾`
- `■`
- `□`
- unexpected missing math symbols
- broken label text such as `AUTHOR￾CREATED`

## Visual inspection focus

Inspect for:

- clipped equations;
- badge labels split badly;
- page footer/header overlapping content;
- too-small algebra;
- source and adapted questions visually confused;
- large accidental whitespace;
- dense micro-card clutter.

## PDF-safe notation

Prefer:

- `t1`, `t2`
- `1/2`
- `x^2`
- `sqrt(3)` when glyph support is uncertain
- `->`
- `+/-`
- ASCII hyphen in labels: `AUTHOR-CREATED`, `IMO-FOUNDATION`

Avoid relying on:

- subscript glyphs;
- superscript glyphs;
- special fraction characters;
- unusual arrow glyphs;
- nonstandard hyphen/dash variants;
- invisible or private-use characters.

Broad Unicode notation may be used only when the embedded font and rendered output have been verified.

## Final response requirement

Report:

```text
Pages rendered/inspected:
Broken-glyph scan:
Clipping check:
Answer key:
Source/reference page:
NOT_RUN:
```
