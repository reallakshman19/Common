# Standalone completion forward application — constructed documentation task

One fresh subagent received only the candidate task artifacts and a copy of the standalone skill. No expected verdict or suspected defect was supplied. The runtime/model configuration was inherited/default and is not a low-thinking qualification. This is one constructed local application, not a controlled effectiveness study, LFEA pilot, independent product review or Owner acceptance.

The copy under test predates two presentation-only updates: the helper output boolean was renamed from `done_supported` to `declaration_consistent`, and its result now carries issue/plan/label identifiers. It had the same checklist, witness checks and explicit semantic limitations. The raw returned output below is retained unchanged. Current code has the neutral boolean name and passed the focused checks afterwards.

## Exact task inputs

### owner.txt

Byte SHA-256: `fea6ebcff0087c4211796c4957dca5f5edec5162553ef32c109e35085f59efb3`.

```text
Document task: explain the word-count CLI, state that whitespace separates words, and explicitly document a missing-file error with nonzero exit. Preserve these two requirements. Task acceptance is the help text; Owner merge is separate.
```

### help.txt

Byte SHA-256: `53dc8f9283bbf8b7a6c2807303421f05af5e19333703b2a7ce0526718d8fc6cd`.

```text
Word count usage: python wordcount.py FILE
Whitespace separates words, including tabs and newlines.
```

### criteria.txt

Byte SHA-256: `6ad8be1d80a955c5f73c8e71b1799eda8bda25c798b2007deb94cc736ff6d576`.

```text
CRITERIA v1 · PILOT · FROZEN 2026-10-19 by Owner · source: #1 body
AC1 MUST "state that whitespace separates words" → Help states whitespace including tabs and newlines
AC2 MUST "explicitly document a missing-file error with nonzero exit" → Help explains missing-file behavior and exit status
Criteria: 2 (2 MUST · 0 CONSTRAINT · 0 JUDGMENT) · source coverage: every declared requirement
```

### verification.txt

Byte SHA-256: `096547430837f63dc9e970f60b1f963494fc0d94227e80b3452a5f6c57aca2ba`.

```text
Help text exists and has CLI usage. No CI for this documentation task. Self assessment: task complete.
```

### proposed-selfcheck.txt

Byte SHA-256: `66e962d883aa1f101e77174457f4981dbcdb799bab170f9e0a47fd6e30ee778c`.

```text
SELF-CHECK v1 · V36-1-WP1 · sample/project#2
Basis: plan V36-1-PLAN-01; label PILOT@1.0.0:abc1234; criteria sha256 6ad8be1d80a955c5f73c8e71b1799eda8bda25c798b2007deb94cc736ff6d576; candidate sample/project@b349457b307e86b3fe37a3531baabf594794b057; source #1 body
Done-when: SC_INTENT → MET ; proof: verification.txt ; sha256: 096547430837f63dc9e970f60b1f963494fc0d94227e80b3452a5f6c57aca2ba
Done-when: SC_INPUTS → MET ; proof: verification.txt ; sha256: 096547430837f63dc9e970f60b1f963494fc0d94227e80b3452a5f6c57aca2ba
Done-when: SC_SCOPE → MET ; proof: verification.txt ; sha256: 096547430837f63dc9e970f60b1f963494fc0d94227e80b3452a5f6c57aca2ba
Done-when: SC_FLOW → MET ; proof: verification.txt ; sha256: 096547430837f63dc9e970f60b1f963494fc0d94227e80b3452a5f6c57aca2ba
Done-when: SC_TESTS → MET ; proof: verification.txt ; sha256: 096547430837f63dc9e970f60b1f963494fc0d94227e80b3452a5f6c57aca2ba
Done-when: SC_CODE → MET ; proof: verification.txt ; sha256: 096547430837f63dc9e970f60b1f963494fc0d94227e80b3452a5f6c57aca2ba
Done-when: SC_PENDING → MET ; proof: verification.txt ; sha256: 096547430837f63dc9e970f60b1f963494fc0d94227e80b3452a5f6c57aca2ba
Done-when: SC_FRESHNESS → MET ; proof: verification.txt ; sha256: 096547430837f63dc9e970f60b1f963494fc0d94227e80b3452a5f6c57aca2ba
Done-when: AC1 → MET ; proof: verification.txt ; sha256: 096547430837f63dc9e970f60b1f963494fc0d94227e80b3452a5f6c57aca2ba
Done-when: AC2 → MET ; proof: verification.txt ; sha256: 096547430837f63dc9e970f60b1f963494fc0d94227e80b3452a5f6c57aca2ba
Scope: allowed task inputs; actual one result; protected data preserved
A13: no source change; stage assessment in result.txt
A13 review: self-assessed; no independent reviewer required for this task
Tests: local task check; no CI; evidence records limitations
Issue reconciliation: task acceptance assessed; Owner acceptance separate
Pending: none
Proposed claim: DONE · reason: bounded task witnessed
Native report: PENDING publication follows local verification
```

## Observed result and verification

The fresh agent returned PARTIAL: AC1 MET, AC2 NOT_MET. It inspected the complete two-line help, found no missing-file/nonzero-exit explanation, and rejected the author's generic completion witness despite the helper passing structure/bytes. It produced a native v1 companion with the missing obligation retained in this task. Its reported 7/8 checks are documentation/source inspections, not code-suite results.

Parent verification re-read the raw reports and source files, checked the missing content directly, verified every returned witness digest and confirmed the native v1 parser accepts the corrected record without nonconformant lines. The current helper also refuses this PARTIAL record as a DONE claim. No tracked candidate inputs were modified; no provider write occurred.

Raw return: [assessment](assessment.md), [native self-check](selfcheck-v1.txt), [read-only witness](verification-readonly.txt). Their absolute scratch paths and synthetic `sample/project` identities are historical receipt data, not live publication targets or portable authorities.

## Maintainer validation

Baseline: 336 existing tests passed. The first tests-only commit introduced 14 failing checks because the new verifier was absent; this was feature absence, not behavioral RED for a production application. Final suite: 356 tests passed, including 20 new standalone cases. All 17 existing runtime scripts and MODE_COORDINATOR.md were byte-identical to the base. No workflow, dependency, native format or coordinator default changed.

A checklist/hash pass does not prove task correctness. This case shows that a fresh agent could apply the semantic warning here; it does not establish that every agent will do so.
