# Oracle Continuity Protocol — review package

Version 1.0.0 · proposed reference contract · 23 October 2026

Start with [PROTOCOL.md](PROTOCOL.md). It defines initiation, bounded assignments,
evidence, decisions, worker replacement, Oracle succession, recovery and the actual
runtime responsibilities needed to enforce the contract.

## Contents

| File | Purpose |
|---|---|
| `PROTOCOL.md` | Human operating rules, lifecycle, concurrency and integration limits |
| `oracle-state.schema.json` | Draft 2020-12 schema for the canonical state |
| `oracle-command.schema.json` | Publication preconditions and exact proposed-state digest |
| `validate.py` | Read-only schema, reference, lineage, state and transition checks |
| `examples/initial.json` | One active Oracle and one executor assignment |
| `examples/worker-cutover.json` | Same task continued in a successor session |
| `examples/oracle-cutover.json` | New Oracle epoch adopting ongoing executor work |
| `examples/completed.json` | Illustrative candidate, assessment, user use and acceptance |
| `examples/learning-pending.json` | Domain-specific transfer criterion remains unobserved |
| `examples/*.command.json` | Publication envelopes for the three sequential transitions |
| `tests/test_contract.py` | Failure-oriented invariants and explicit limits |

Every example is synthetic, including its observed-witness and acceptance fields.
The included report text is real local example bytes for testing the optional hash
check. It is not a live product or execution result.

## Run

Requires Python 3.10+ and `jsonschema` 4.18 through 4.x. Dependencies are declared in
`requirements.txt`; install in your existing permitted environment if needed:

```sh
python -m pip install -r requirements.txt
python validate.py examples/initial.json
python validate.py examples/worker-cutover.json --previous examples/initial.json --command examples/worker-cutover.command.json
python validate.py examples/oracle-cutover.json --previous examples/worker-cutover.json --command examples/oracle-cutover.command.json
python validate.py examples/completed.json --previous examples/oracle-cutover.json --command examples/completed.command.json --artifact-root examples
python -B -m unittest discover -s tests -v
```

Validation performs no network requests or writes. `--artifact-root` explicitly
opts in to local artifact-byte checks and rejects paths resolving outside that root.
Without it, digests are checked for form and binding, not against file bytes.
Private/remote locators are never automatically fetched.

Keep locally prepared state files as proposals until the actual canonical publisher
commits them and supplies its receipt. A valid proposed history event or assignment
does not prove publication or transfer ownership. See PROTOCOL section 8.

Exit 0 means the supplied records satisfy the implemented contract. Exit 1 reports
contract violations; exit 2 reports input/usage errors. Supplying `--command` requires
`--previous`. JSON duplicate keys and non-finite numbers are rejected.

## Validation boundary

The checker detects declared writer conflicts, unknown/stale references, graph
cycles, unconfirmed capabilities/delivery, missing criteria/use/acceptance evidence,
declared author-review conflicts, unreconciled failures, history rewriting, invalid
cutovers, stale publication preconditions and payload-byte changes.

It cannot establish that a witness is genuine, a source was read, a principal is
independent, a private instruction reached an agent, a registered write scope covers
all overlapping paths, an approval is authorized, a learning outcome occurred or a
concurrent write was actually prevented. It does not check arbitrary domain criteria.
Authenticated adapters and substantive reviewers provide that evidence.

A second layer performs relational checks because JSON Schema alone cannot express
all cross-record/version relationships. An actual publisher must also implement
atomic compare-and-swap and command-receipt deduplication. The reference checker
does not install those mechanisms. See PROTOCOL sections 8–10 before live use.
