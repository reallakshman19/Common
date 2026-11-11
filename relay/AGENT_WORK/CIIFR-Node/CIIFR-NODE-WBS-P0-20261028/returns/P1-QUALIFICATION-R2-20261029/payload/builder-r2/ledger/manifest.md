# P1 R2 pending CSV selection revocation

Task CIIFR-NODE-P1-R0-REPAIR-R1, #231 / PR232. Baseline7f5dc773ac7bb08544d086be734e4337295088a0. Owner previously directed root to implement F1 and has now authorized qualification continuation. Reviewer independently found pending owning CSV selection retains prior applied/export authority. Root contributes repair; reviewer does not edit product. No new scope/Cycle/writer/merge authority.
Pre-existing product dirt: none in four target files; local ignored R1 ledger/evidence exists and is preserved. Baseline is actual filesystem bytes in baseline.json, not Git history. Browser/Windows/original remain NOT_RUN.
Plan before edits: invalidate Normal approval/applied state immediately upon every owning CSV selection/clear, advance sequence before awaiting text, keep stale read guards and original parser/writer intact. Add a controlled pending-read and actual export challenge, plus clear/cancel case. Preserve independent Property behavior.

| Module | Status | Planned | Did | Validation | Patch | Backups | Undo |
|---|---|---|---|---|---|---|---|
| csv-selection | planned | Immediate owning selection epoch revocation | Pending | Pending | modules/csv-selection.patch | Native pre-edit backups | Verify final hashes then restore exact preimages only |
