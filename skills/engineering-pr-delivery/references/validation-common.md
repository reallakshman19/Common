# Common Validation Contract

Every material validation has three independent dimensions.

## Status
`PASS`, `FAIL`, `NOT_RUN`, `NOT_APPLICABLE`.

## Observation
`LOCAL_EXECUTION`, `REMOTE_EXECUTION`, `SOURCE_INSPECTION`, `ARTIFACT_INSPECTION`, `USER_SUPPLIED`, `INFERRED`, `NOT_OBSERVED`.

## Oracle independence
`NONE`, `IMPLEMENTATION_COUPLED`, `INDEPENDENT_REPRODUCTION`, `ANALYTICAL`, `AUTHORITATIVE_REFERENCE`, `CROSS_SOLVER`, `EXPERIMENTAL`.

A regression PASS with an implementation-coupled oracle is valid regression evidence but is not independent verification.

Record tested implementation HEAD/basis, exact command or evidence, expected and actual results, tolerance when meaningful, and limitations.

Classify failures/warnings as `PREEXISTING`, `INTRODUCED_BY_PR`, `RESOLVED_BY_PR`, or `UNKNOWN_ORIGIN`.

Negative assurance is required for sensitive work: state behavior intentionally changed, behavior that must remain unchanged, and evidence of invariance.

Never convert missing tooling, CI no-start, environment blockage, or unexecuted checks into product PASS.
