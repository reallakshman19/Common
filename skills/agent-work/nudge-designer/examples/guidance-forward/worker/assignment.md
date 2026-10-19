# One assigned diagnostic

Purpose: the Owner requires every published payload to belong to the currently
selected source AND its current revision; valid current completions must succeed.

Bounded task: execute the unchanged supplied receive function and report each
state transition against that invariant. Diagnose only; no repair.

Inputs: source.py in this directory. Each fresh state has selected_source='B',
current_revision=12 and result=None. Completions are ('A',12,'A12'),
('B',12,'B12') and ('B',11,'B11'). These are synthetic inputs, not production data.

GUIDED method: import the original function; record the input source/revision,
state before/after and the result expected under the invariant. Test A12 then
B12, B12 then A12, and a separate B11 then B12 using a fresh state per order.
Include any intermediate violation, not only the final state. State a concrete
prediction before comparing actual execution. Do not edit or mock the function.

Boundaries: Python is available for local computation. Write only new probe/output
files in this directory. Do not edit assignment.md or source.py, touch products,
publish externally or assume a model/reasoning setting. This is not implementation
authority. A separate CSV-unit question remains unassigned and independent.

Success: an actual reproducible trace covers source identity, revision and valid
current publication. An execution that silently substitutes a guarded implementation
does not qualify. Unknown production integration remains unresolved.

If a needed tool is unavailable, report its attempted use/restriction and affected
scope; retain feasible permitted work. Return diagnostic.md plus actual probe
and output artifacts in the native Markdown format. Keep wider acceptance and
CSV work unresolved, and propose the next feasible action.
