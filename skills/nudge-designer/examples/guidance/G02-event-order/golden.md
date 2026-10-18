# Golden reference — a guided experiment with an invariant

Assign one diagnostic trace, not a combined diagnosis/repair/export task. Read the
invariant, import the unchanged function, and start a fresh state for each order.
Record request/current revision, before/after result and expected publication at
every event. Compare NEW→OLD and OLD→NEW and retain current-completion success.

The oracle follows the Owner invariant, not the implementation:

| Order | Expected result after each event | Predicted original-function result |
|---|---|---|
| NEW, OLD | NEW, NEW | NEW, OLD |
| OLD, NEW | None, NEW | OLD, NEW |

These are derived predictions until actually executed. The worker must return the
real trace and distinguish it from this reference. In the second order a correct
final result hides an earlier obsolete publication. A future repair rejecting
every completion also fails the required valid-current contrast.

Keep CSV unresolved and independently eligible under actual scope. A measured
race can support a later bounded repair; it does not authorize implementation here.
Do not rewrite the original function into a guarded mock and use that as evidence
about its behavior. The [assignment template](../../../assets/prompts/assignment.md)
adds purpose, exact input, boundaries, return condition and native continuation
around this concrete method without requiring another approval ritual.
