# Optional records and offline helpers

## Contents

- [Records](#records)
- [Identity and evidence](#identity-and-evidence)
- [Commands](#commands)
- [Limits](#limits)

## Records

Use native prose first when it already carries the meaning. Structured consumers
may select these self-contained JSON Schema 2020-12 contracts:

- `schemas/review-case.schema.json`: `independent-review.case/v1`.
- `schemas/review-result.schema.json`: `independent-review.result/v1`.

Case: identity, task/outcome, Owner intent, authoritative sources, one or more exact
candidates, claims/contrasts and action boundaries. Optional understanding,
method guidance, arrangement, return location and external bindings add context without creating
mandatory roles. A candidate revision may be `UNKNOWN`; disclose the identity limit
and capture a byte digest where possible. Do not invent a revision.

Result: case binding, distinct run identity, actual reviewed candidate vector,
reviewer author relation, exposure/expectation/method/execution/lineage declarations,
evidence, per-claim conclusions, findings, coverage, scoped verdict and next action.
Optional native-report location/hash preserves the existing report rather than
replacing it. `bindings` contains selected adapter identity/locator records, not
imported runtime objects or permissions. No additional external schema is resolved.

Claim statuses are `SUPPORTED`, `CONTRADICTED`, `INCONCLUSIVE`, `NOT_RUN`.
Verdicts are `PASS`, `NEEDS_WORK`, `FAIL`, `INCONCLUSIVE`, with explicit claim scope.
A PASS on one supported claim does not settle another NOT_RUN claim. Explain the
assessment in ordinary language; no automatic roll-up or majority vote applies.
Known failures and unknown checks survive together in the result.

Use `SELF_REVIEW` for SAME author relation. Use `SEPARATE_REVIEW` only with a
declared DISTINCT relation and its basis; a label is not authenticated principal
identity. Use `UNESTABLISHED` where the basis is unknown. Native project review
profiles retain their own role/status semantics, including stricter requirements.

## Identity and evidence

Distinguish task, candidate and run identity. A new candidate or review attempt
does not erase a historical result. A case may include product, QA, data and
integration subjects separately. Candidate identity compares locator, revision,
optional base revision and optional SHA-256. `local_path` is an access route,
not part of candidate identity.

The optional case binding is SHA-256 of Python JSON serialization with sorted
keys, separators `(',', ':')`, `ensure_ascii=False`, `allow_nan=False`, encoded
as UTF-8. This is a local deterministic recipe, not a claim of RFC 8785 numeric
canonicalization. A file-byte SHA-256 instead covers every original byte, including
line endings and BOM. Never substitute one identity for the other. Strict JSON
reading rejects duplicate keys and NaN/Infinity.

Evidence kinds describe what the record claims happened:

| Kind | Meaning |
|---|---|
| EXECUTED | Actual check on the declared candidate/input/environment; retain output and execution witness. |
| INSPECTED | Existing source/artifact/receipt actually read; not a fresh execution. |
| DERIVED | Reasoning or calculation with original givens and a recorded derivation. |
| SIMULATED | Model/synthetic result; state its applicability limits. |
| REPORTED | Someone's assertion not independently inspected. |
| NOT_RUN | Check not performed, with reason and affected scope. |

Each evidence record links declared source/candidate IDs and a locator, observation
or local artifact. A schema cannot establish the declaration is truthful. A
finding may introduce a new risk without pretending it was an issued claim; explain
its scope and evidence, then reconcile the assignment visibly.

## Commands

Run from the skill directory with Python 3.11+; only full JSON Schema validation
uses the optional `jsonschema` package. If unavailable, report `SCHEMA_NOT_RUN`
while performing available declaration checks. Do not require installation to use
the review method, render, binding, byte checks or supplied identity comparison.

```bash
python scripts/review.py bind examples/records/case.json
python scripts/review.py validate examples/records/case.json --result examples/records/result.json
python scripts/review.py render examples/records/case.json
python scripts/review.py check-evidence examples/records/case.json --result examples/records/result.json --root examples/records
python scripts/review.py compare examples/records/case.json --observations examples/records/current.json
```

`validate` checks structure when available, case/candidate bindings, duplicate
identities, internal references, declared claim/evidence coverage, PASS scope and
obvious authorship-declaration contradictions. It does not inspect witness truth.
`render` prints supplied meaning and every declared result field, without deriving
a verdict or modifying the native report.

`check-evidence` reads only explicit relative `local_path` files under the caller's
`--root`. It hashes original bytes incrementally, reports missing/mismatching files
individually, rejects resolved paths outside root and never follows a locator URL.
It does not execute commands embedded in a record. Supply a stable local snapshot;
the helper is not a sandbox for concurrently adversarial file replacement.

`compare` reads an explicit array of supplied current candidate identities. It
reports MATCH/CHANGED/NOT_OBSERVED/INCOMPLETE_OBSERVATION/NOT_IN_CASE, or
AMBIGUOUS_IDENTITY for duplicate issued/observed IDs. The caller
must establish observation source/time/freshness. The helper neither contacts GitHub
nor infers that old evidence is invalid for every claim after any change.

## Limits

Reports are advisory; successful parsing returns exit 0 even when inconsistencies
are found. Malformed/unreadable input returns exit 2, a technical invocation error,
not a project blocker. No auto-fix, auto-approval, workflow state, CI, network fetch,
participant qualification, dispatch, ownership registry or release command exists.

Local checks for maintainers:

```bash
python -B -m unittest discover -s tests -v
```

Tests exercise helper behavior and isolated reference cases. Fresh applications
exercise the method. Neither establishes actual LFEA acceptance, domain-qualified
independence or performance of an unobserved low-thinking model configuration.
