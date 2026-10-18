# Raw synthetic findings and improvement case

Original requirement R-ID: every displayed comparison result must belong to the
currently selected source revision. Existing scope permits read-only diagnosis,
local planning and test design, not product edits. A native report contains:

- Actual synthetic trace: current revision 4 publishes a rev3 payload after rev4.
- Proposal: reuse an existing prepared-target cache; no timing/profile was run.
- Observation: CSV heading “mass” has no declared unit; its requirement is unresolved.
- Existing issued plan says “trace pending”; a new handover says “all fixed.”

The trace exists, but no repair, production journey or performance check occurred.
Owner asks to reconcile and choose the highest-value next action. Keep useful
existing code where supported, without a compulsory rewrite or novelty quota.
