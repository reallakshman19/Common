# Count-check assignment

Purpose: establish whether the supplied record claims match their original texts.
Deliverable: one concise report.md with actual results and supporting computation.
Input: payload.json, UTF-8. Preserve its bytes; record their computed SHA-256.

Method: read every object in its records array, including an empty text value.
Compute tokens as Python `len(text.split())` (whitespace, including tabs), compare
each with claimed_tokens, and record the text/algorithm/count supporting its verdict.
Recount coverage from the actual array, not a reported total. A valid empty string
has zero tokens; an empty text record still counts as a reviewed record.

Python computation and local drafting only. Write new report/check/script files
here, disable bytecode, and do not edit packet.md or payload.json. No external
writes, product changes or delegation. Native verdicts are allowed with evidence;
report actual uncertainty, without a fixed weakness count. If blocked, record the
attempt/restriction and affected scope. Wider acceptance, runtime model/effort and
qualification are unknown. Propose the next feasible action from actual observations.
