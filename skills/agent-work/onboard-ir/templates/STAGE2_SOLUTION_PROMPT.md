# Stage 2 — compare candidate to frozen source-first reviewer model

**Prerequisite:** identify the reviewer's actual Stage-1 native return (URL/revision and exposure). If no Stage-1 return, report that the blind-baseline condition was not demonstrated; review may proceed but may not claim independent Stage-1 derivation.

Now reveal the producer candidate **at an exact current commit SHA**, its PR diffs, implementation paths, claimed outputs, tests and CI. Read actual changed files and integrated runtime, not just PR descriptions. The original source/spec and Stage-1 findings remain the independent reference.

For every material author claim:

- Compare to your Stage-1 expected behavior, preserve the original reasoning, and explain any source-backed correction.
- Inspect where it is consumed in the real entrypoint, and how later operations might erase or duplicate the result.
- Find at least one plausible wrong product or source interpretation that the existing test suite could accept.
- Independently inspect actual emitted file/return where available; otherwise mark NOT_RUN.
- Seed or identify a minimal negative case: a tampered slot, member, coordinate, disconnected junction, mass owner, serialized record, stale head, reused identity or similar domain-specific failure. State the exact checker and whether the *expected* failure was observed.
- Rank defects with file/symbol/line and minimal reproduction. Missing private evidence must remain unknown, not "correct by analogy".

Use [findings report](FINDINGS_REPORT.md) and [source/claim matrix](CLAIM_EVIDENCE_MATRIX.csv) where useful. Preserve independent judgment alongside any disagreement with the author. Disclosure of prior solution exposure is mandatory. If authorized contribution is separately requested, disclose changed role and affected self-review scope; this task alone remains READ_ONLY.

Return to the **same** native review task with SUPPORTED / CONTRADICTED / UNKNOWN / STALE claims, affected WBS/dependency, first-divergence evidence and scoped GO / CONDITIONAL / NO-GO. The Oracle/Owner reconciles; do not invent approval authority or publish protected fixtures.
