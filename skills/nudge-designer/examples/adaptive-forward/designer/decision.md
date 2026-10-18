# Local correction and draft next assignment

Correct packet identity before rerunning the affected R20 review. Fresh SHA-256 over the packet strings' UTF-8 bytes confirms:

| Packet | Computed SHA-256 | Data count | Supplied receipt relation |
|---|---|---:|---|
| R19 | `5de494784c2972e275405ed4d2aafeb14a975ed3ef199e952bf3be0bc4ac0a53` | 3 | Delivered and recipient digests |
| R20 | `ecdf59bbe62530aa7ad34a6563ac0d45414ee98f48390ed4972f29588562d138` | 4 | Issued digest |

The count excludes the revision header and empty lines. Preserve the prior R19 count of 3 and its witnesses X-1–X-3. R20 additionally contains X-4. The native “R20 complete, all checks pass” conclusion exceeds its cited R19 source and examined scope. The supplied receipts support a sender/input mismatch despite the R20 delivery label; actual transport was not inspected.

Retain the useful counting method. Select GUIDED source binding and a stale-packet contrast for the next bounded task. Switching models and adding two passes does not repair the demonstrated mismatch. Model, reasoning configuration, formal qualification and broader worker capability remain UNKNOWN; correct R19 counting supports that task only.

[R20-draft.txt](sandbox:/workspace/scratch/52eed2252c51/tmp/nd-adaptive-forward/designer/R20-draft.txt) is an exact local UTF-8 view of `packets.json["R20"]`, prepared without delivery. [audit.py](sandbox:/workspace/scratch/52eed2252c51/tmp/nd-adaptive-forward/designer/audit.py) and [audit.json](sandbox:/workspace/scratch/52eed2252c51/tmp/nd-adaptive-forward/designer/audit.json) preserve the reproducible computation, line witnesses and unchanged input hashes. Contract validation/render startup failed because Python lacks `jsonschema`; structural checks and machine rendering are NOT_RUN. The prose assignment below was manually inspected. [checks.json](sandbox:/workspace/scratch/52eed2252c51/tmp/nd-adaptive-forward/designer/checks.json) records those limits. No JSON intent/plan or machine-rendered brief is claimed.

## Purpose

Supply source-linked R20 record-count evidence for the Owner's review, correcting stale-source use while preserving useful R19 history.

## One bounded task

Produce one new native Markdown record-count report. Use this GUIDED method:

1. Select R20 from `packets.json`. Encode the exact string strictly as UTF-8, retaining the final newline. Check the header is exactly `R20`; compute SHA-256 over the string bytes and compare with the issued digest in `receipts.json`. If using `R20-draft.txt`, verify byte equality with that source first.
2. Check the R19 string against the same R20 pin as a stale-source control.
3. For verified R20, use `splitlines()`. Exclude the first header line and empty lines; enumerate/count every later nonempty line with its physical line number. Do not strip or deduplicate. Derive the count from source, not this reconciliation's expected value.
4. Report the bounded verdict and identify the historical conclusion's source-scope error without changing `prior-review.md`.

## Authoritative inputs

All files are under `/workspace/scratch/52eed2252c51/tmp/nd-adaptive-forward/designer/`: `owner.md`, `packets.json` (R19 and R20), `receipts.json`, `prior-review.md`. The draft text is a derived view, not new authority.

Preserve: “Owner requires the review of R20 with retained source identity.” Hashing means “UTF-8 bytes of the packet string, not this JSON container.” Receipt metadata and the historical report are supplied claims; neither establishes actual delivery or acceptance.

## Boundaries

Create only a new local report in this designer directory. Preserve supplied inputs/native history. No sending, dispatch, product edits or shared-policy changes. The Owner permits file reading and Python when available; the next worker's actual access is unobserved. Model, effort, qualification and other task fit remain UNKNOWN.

Reserve consequential source/revision/scope conflicts, broader participant allocation and integrated acceptance for Designer/Owner under existing authority. Add no approval or iteration ritual.

## Success criteria

Return actual source/header, representation, computed digest, parsing rule, every counted record/line and source-derived count. Map material claims to witnesses. Native PASS/FAIL verdicts and justified empty additional findings are acceptable with coverage.

The R20 pin must reject R19 bytes despite an R20 label, while verified R20 remains eligible. A conflicting header/digest/count changes the conclusion. Record-count evidence cannot establish “all checks pass.”

## Uncertainty handling

Attempt relevant reads/tools. If a source is unavailable, unreadable or conflicts with its pin, stop dependent counting and return the attempt, observed restriction, affected claim and exact source/tool needed. Do not substitute R19 or change codec silently.

Without Python, readable-source manual enumeration and historical reconciliation remain useful; mark hashing NOT_RUN and return partial evidence. Review criteria beyond this supplied record/source check remain UNKNOWN.

## Evidence and continuation

Return the new native report's actual locator, method/code, digest or NOT_RUN, record witnesses, contrast result, attempted operations, coverage and limits. Preserve the old report. A receipt is not evidence of claim correctness or acceptance.

The sender/Designer should inspect the actual return and independently recompute its consequential R20 digest/count from raw source. The current sender-side audit is a baseline, not next-worker execution or a separate review. Correct the specific gap and adapt support/participant only from actual corrected-task evidence.

Wider R20 review and production acceptance remain unresolved. This is a local draft assignment; no worker was dispatched and no delivery occurred.
