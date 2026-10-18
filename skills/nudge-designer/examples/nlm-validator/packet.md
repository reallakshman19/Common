# NLM validator packet — synthetic GUIDED example

Purpose: independently check three sample items against their original evidence.
Inputs: `sample-items.txt` (UTF-8); keep its exact bytes and source identity.
Method:
1. Read each item and quote one decisive source line or give a computed value, with location.
2. Record `Item | Quoted evidence or computed number | Finding | Source`.
3. Recompute the item count (3) from the supplied input, not a reported total.
4. Name the three weakest items and why each deserves a second look.
5. Check that no row is answered with an unsupported yes/no verdict.
Return: write ONE `nlm-p3-result.md`, then reply with one line:
`SAVED-P3 · rows=<n> · file=nlm-p3-result.md · sha256=<result-file-sha256>`
