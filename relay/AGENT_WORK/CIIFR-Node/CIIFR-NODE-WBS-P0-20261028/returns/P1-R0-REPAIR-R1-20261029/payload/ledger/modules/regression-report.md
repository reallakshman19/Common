# Module: regression-report
## Planned
Add actual-app DOM and physical-splice tests and a recovery-first builder workreport; preserve existing test oracles.
## Did
Implemented and executed scoped native checks; candidate remains SELF_ASSESSED / independent gate HOLD.
## Technical details
See agents/PR232_workreport.md for state transitions, pointer/domain contracts, lexical-zero/UNKNOWN residue handling and upstream/downstream limits.
## Files and symbols
See changed-files.json and the module patch; regression/report new files have no task preimage. WIP report allocated to PR232 after native backup #8.
## Upstream/downstream impact
Property R0 only; protected engines and CII bytes preserved.
## Validation
Required17/17, focused11/11, bounded Geometry9/9 PASS. Complete VNext121/1 vs predecessor110/1 and base94/1; same inherited failure. Browser/Windows/original NOT_RUN. See Common return raw outputs and validation-summary.json.
## Patch and backups
Pending.
## Undo
Verify recorded final SHA first; restore only native pre-edit backup bytes. New exact files may be removed only after SHA check and no later changes. Never use history-based reset/revert.
## Remaining risks or follow-ups
SELF_ASSESSED; fresh non-author review and real browser/original qualification still required.

Final patch: modules/regression-report.patch. Existing-file preimages are native backups1–6; intermediate new-test backup7 and report-allocation backup8 do not replace their ABSENT task baselines.
