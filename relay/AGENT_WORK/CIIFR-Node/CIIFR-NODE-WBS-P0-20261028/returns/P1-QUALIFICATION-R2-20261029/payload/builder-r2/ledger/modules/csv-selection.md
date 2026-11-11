# Module: csv-selection
## Planned
Invalidate owning state before CSV await; cancel pending reads on clear; new negative/positive regression cases.
## Did
CSV selection/clear now invalidates before await and captures post-revocation revision; clears cancel older reads. Two regressions fail before and pass after.
## Technical details
Current handler invalidates after file.text; pending export uses old plan. Move revocation to selection boundary and capture revision after revocation.
## Files and symbols
Mirrored app.js CSV change handler, existing focused repair test, PR232 report addendum.
## Upstream/downstream impact
Normal owning CSV only; Property intake remains isolated; all protected engine/writer files unchanged.
## Validation
Before11pass/2fail; after focused13/13, required17/17, Geometry9/9. Full VNext123/1 retains independently explained inherited B1 assertion error. Syntax/mirrors PASS; actual uploaded four-file readback matches. Browser/Windows/original NOT_RUN.
## Patch and backups
Native receipts follow; patch derived from actual backups, independent of Git.
## Undo
Check current final SHA/no later changes, restore only matching native backups; never reset/revert.
## Remaining risks or follow-ups
Fresh exact-head non-author review required; browser/Windows/original NOT_RUN.

Final candidate d3fbd4041ef4434b4cf5b3c22459f06167be2729. Native backups9–12 and changed-files.json identify exact preimages/final digests. Patch modules/csv-selection.patch is derived from those preimages. Review remains a separate read-only recheck.
