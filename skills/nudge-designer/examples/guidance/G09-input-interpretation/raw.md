# Raw synthetic input interpretation task

The sender reports a broken source benchmark after decoding text with UTF-8 and
`errors='ignore'`. The original byte artifact is represented losslessly as base64
in [artifact.json](artifact.json), with its declared cp1252 codec and claimed raw
SHA-256. Local byte checking and drafting are permitted; do not change the source.

Each nonempty record is `id | claimed_tokens=<n> | text=<text>`. Count whitespace
tokens in the text field only; a standalone punctuation token counts under this
declared algorithm. Determine whether the source claims agree with actual counts.
Report the actual interpretation and coverage, not a required number of defects.
No live agent execution has occurred in this golden reference.
