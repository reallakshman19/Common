# Raw synthetic UI case

Owner: “In the model app, selecting branch B with an ordinary pointer action must
show B's header and details. Preserve keyboard selection.” Read-only diagnosis
and local test design are authorized; no product edit or browser runtime is available.

Candidate revision UI-C4 is supplied as text. A reported test called
`buttonB.click()` and observed B. A keyboard receipt also observed B. Another
supplied screenshot shows header B and details A after a pointer interaction,
but contains no coordinates, target identity or state trace. The last handover
says “probably an overlay; remove its pointer events.” Deployed revision is unknown.
An existing diagnostic can record `elementsFromPoint` and selected branch IDs.
No actual hit-test or native pointer-event trace has been supplied.
