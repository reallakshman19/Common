# Source claim review

COMPLETE for the bounded packet. No token-count defect was found in the supplied
synthetic artifact: both actual records match their claims. The original source
and issued packet were preserved.

| Record / source line | Text field | Whitespace tokens | Claimed | Computed | Verdict |
|---|---|---|---:|---:|---|
| R-A / 1 | `crème — vert clair` | `crème`, `—`, `vert`, `clair` | 4 | 4 | MATCH |
| R-B / 2 | `bleu ciel` | `bleu`, `ciel` | 2 | 2 | MATCH |

The executed method was strict base64 validation, an SHA-256 over the resulting
89 raw bytes, strict decoding with the artifact's declared `cp1252` codec, exact
record-field parsing, then `len(text.split())`. Only the text field contributes
tokens. A standalone punctuation token counts, as stipulated; field labels do
not count. No header or blank line was present.

The declared and computed raw-byte SHA-256 are identical:
`aa7d52b1e43de631793b18a9ffabe6aeca73498fe4aebabab9e043c189f70af8`.
Strict decoding and re-encoding also reproduced the exact raw bytes. This payload
digest differs from the SHA-256 of the containing JSON file, which is separately
recorded in `computation.json` and `receipt.json`.

Before execution, the contrast was that standalone punctuation should contribute
one token under this algorithm. The observed R-A tokens include `—` (U+2014,
declared-codec byte `97`), so its actual count is four. The other non-ASCII character
is `è` (U+00E8, byte `e8`). The sender's earlier ignored-error UTF-8 view is not a
valid basis for rejecting these original-byte claims. That view was not supplied
or recreated; its exact output and causal history remain unverified. The evidence
does not support the suspected source defect, and no repair is warranted here.

Coverage was checked from the decoded source: two nonempty lines; candidate
record lines `[1, 2]`; parsed and reviewed lines `[1, 2]`; unique IDs R-A and R-B;
zero unmatched nonempty lines and zero mismatches. There is no unreviewed record
in this artifact. These are computed observations, not a supplied expected total.
No interpretation or access restriction occurred.

`check.py` was actually executed with
`PYTHONDONTWRITEBYTECODE=1 python -B check.py` under Python 3.12.14 and exited 0.
It wrote `computation.json`; decoded source bytes remained in memory. The script
uses exclusive creation and intentionally refuses to overwrite that output.
Both input-file preservation checks passed. The receipt identifies the exact
issued inputs and newly produced files using SHA-256 over each file's bytes.

Limits: this is one worker's executed computation and self-check, with shared
parsing assumptions, rather than independent review. A matching digest and strict
decodability do not independently establish the intended encoding or general
source truth; the declared encoding governs this bounded assignment. Host model,
reasoning configuration and formal qualification remain UNKNOWN. No wider
product outcome was assessed or accepted, and no external writes, source edits,
product changes or delegation occurred.

The next eligible continuation is sender reconciliation against these exact
inputs and evidence, including an independent check if consequential. Retain the
declared-codec interpretation for any authorized subsequent use; the current
assignment supplies no wider product task.
