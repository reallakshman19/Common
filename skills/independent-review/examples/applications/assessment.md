# Prototype applications: evidence and limits

Three fresh task-local agents used the actual skill on synthetic inputs on
19 October 2026. The issued requests are preserved verbatim in
[issued.json](issued.json). None received the parent history, expected finding,
proposed fix or reference outcomes. Requests permitted ordinary native reports;
no JSON case/result, sibling module or extra participant was needed to do the work.

| Application | Observed result | Native evidence |
|---|---|---|
| DIRECT code review | Existing 3 tests passed; reviewer derived a delivery-threshold counterexample from the original rule and returned FAIL. | [report](direct/out/review.md), [script](direct/out/check_review.py), [execution log](direct/out/check.log), [all observations](direct/out/check_evidence.json) |
| GUIDED custody | Both file hashes matched; the same comparator rejected an altered disposable copy. Original bytes remained unchanged. No content/product approval was claimed. | [report](guided/out/review.md), [script](guided/out/verify_custody.py), [receipt](guided/out/custody-log.json), [altered copy](guided/out/owner.altered.md) |
| DIRECT learning resource | Reviewer recomputed the short lesson, returned PASS with no material finding, and retained learner/independence limits. | [report](lesson/out/review.md), [script](lesson/out/check_lesson.py), [calculation receipt](lesson/out/calculation-log.json) |

The parent inspected reports and source, checked preserved inputs and receipt
counts, reproduced an adjacent code counterexample and recomputed the lesson's
distance/displacement separately. See [parent checks](parent-checks.json) and
[their source](parent_checks.py). Parent verification is a disclosed contribution
to this assessment, not evidence of unaided worker integration or distinct P2.

## Setup and assistance

Each agent began with `fork_turns=none`, the actual skill path, copied task-local
raw inputs and its assignment. The GUIDED brief supplied a concrete hashing method
and altered-copy contrast. That design support was intended, not an unaided method
discovery claim. Workers reported no further assistance, and no corrective follow-up
was sent to these three workers. Their actual model/effort configuration and task
competence beyond the observations were not established; no override was selected.

Inputs, native reports, scripts and receipts were copied byte-for-byte into these
case directories. Historical absolute execution paths remain in native evidence;
the links above provide archive-relative navigation. To rerun a worker script,
copy its case into a fresh disposable directory first; do not overwrite historical
receipts. The custody script deliberately refuses to overwrite its altered copy.

These are fresh-context applications, not host-enforced access isolation. Workers
were instructed not to consult golden examples/other outputs and reported their
actual reads. Broad shared workspace/tool access was not prevented or authenticated.
All data and evaluation tasks were parent-authored; no reference-withheld transfer
or distinct-principal independence is certified by the setup.

## Package review and corrections

A separate fresh package reviewer checked the implementation against the Owner's
standalone/optional-adapter brief, without inspecting the application outputs.
Its [original report](prototype-review/findings.md) found duplicate issued IDs could
produce a misleading candidate MATCH, and a symlink loop could abort a byte-check
batch. Both were corrected with regressions. The original review remains attached
to its captured candidate; the [separate recheck](prototype-review/recheck-fixed/recheck.md)
records the corrected functional-file hashes, counterexamples and local test result.

The [local validation receipt](local-validation.json) records the final focused
helper tests, skill metadata check, and source/navigation inspection. These are
local checks; no CI workflow or project admission mechanism was added.

## What this establishes

The prototype can support direct source-grounded assessment, a bounded GUIDED
operation and an evidence-backed empty finding set using available participants
and native prose. These observations support usability of those applications.
They do not measure causal improvement, coordination ROI, performance of a
low-thinking configuration, substantive qualification in another domain, actual
LFEA/Writer2 behavior, Owner acceptance or release readiness. Long-project reuse,
live tracker integration and the real LFEA loop remain future applications.
