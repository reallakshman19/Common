# Golden reference — correct the input path before blaming the corpus

Materialize/check the base64 bytes, recompute the raw SHA-256 and use the declared
cp1252 codec strictly. Preserve that byte source; any decoded view is separate.
Strict UTF-8 rejects these bytes. Ignoring errors can drop meaningful characters,
including the standalone em dash, and change the apparent token count.

Under the specified algorithm the first text, `café — rouge`, has three tokens;
`bleu clair` has two. Both source claims agree. These are expected values from the
synthetic input, not a new execution receipt. Do not fabricate a weak row or call
the source defective because the sender used an invalid view.

Keep byte identity, codec declaration and content correctness separate. A hash
match does not authenticate the corpus; decodability alone does not infer a codec.
After correcting the interpretation, reassess affected findings and preserve the
prior report as history. No new product or shared-policy change is authorized by
the decoding observation.
