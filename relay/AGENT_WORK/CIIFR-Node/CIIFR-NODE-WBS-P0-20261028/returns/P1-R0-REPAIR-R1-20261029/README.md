# P1 R0 repair return — PR232

**Governing WBS:** CIIFR-Node Page WBS2/M3 (engineering P1.0) → WBS2.1/M4 (P1.1), unchanged plan. Task [#231](https://github.com/reallakshman19/XML_Compare_Utilities/issues/231); parent #227; non-author review lane #228.
**Date:** 29 October 2026 (Asia/Dubai).
**Producer:** root, now the Owner-directed **builder**, replacing the unable `6ae20df5` builder. This is **SELF_ASSESSED** work, not independent acceptance.
**Product:** [draft dependent PR232](https://github.com/reallakshman19/XML_Compare_Utilities/pull/232), final head `7f5dc773ac7bb08544d086be734e4337295088a0`; tested code commit `bb479a851bb2c9b92918352be64967ef86c89bf5`. The second commit only allocates the report. Parent PR226 remains `b2b695f66fc8dfc907f2b9a493b39bd4d4109570`, draft and unmerged.

[Recovery-first report](https://github.com/reallakshman19/XML_Compare_Utilities/blob/7f5dc773ac7bb08544d086be734e4337295088a0/agents/PR232_workreport.md) provides source trace, profile limits, Appendix A, changed-file and undo details.

The repair preserves completed Normal approvals/validation/applied state across Property navigation/intake, rejects negative endpoints and explicitly holds zero endpoints outside the supported positive-node profile, bounds all 15 typed pointers, and visibly retains unsupported auxiliary/dormant restraint evidence as UNKNOWN with physical trace. It changes no CII bytes or protected writer/parser. Six existing mirrored files, one new regression test and one work report are the complete final PR diff.

| Execution | Result |
|---|---|
| Focused original wrong cases before implementation | 1 PASS / 9 FAIL |
| Focused final repair suite | 11/11 PASS |
| Existing required three tests | 17/17 PASS |
| Bounded Geometry | 9/9 PASS |
| Complete sequential VNext on repair | 121 PASS / 1 FAIL |
| Same suite on predecessor | 110 PASS / 1 FAIL |
| Same suite on base | 94 PASS / 1 FAIL |
| Six source/served mirrors, public fixture identity/immutability | PASS |
| Product exact-head readback | Eight final files retrieved and matched |
| Browser / Windows / protected original / licensed CAESAR II | NOT_RUN; original NOT_RECEIVED |

All three broad runs retain the same unmodified branch-scope failure at test line85 (actual1/expected0). It is not suppressed or repaired here. The first default-concurrency log lacked a completion summary; the `*-complete.tap` logs are the authoritative broad runs. The existing controlled DOM is explicit simulated UI evidence running the actual app module, not a real browser.

The actual Playwright CLI browser launch failed: Chromium distribution `chrome` was not found at `/opt/google/chrome/chrome`. No browser interaction, screenshot, Windows or original-model acceptance is claimed. Zero endpoint meaning, dormant restraint legality and auxiliary content beyond the four qualified structural families remain unqualified.

## Custody and recovery

Storage: **COMMON_RELAY_PAYLOAD** on the existing draft Common PR561 branch. This directory is a public-safe builder return; original N-01/N-02 returns are unchanged. `ARTIFACT_MANIFEST.json` records measured byte size/SHA-256 for the payload files. Product code remains in the exact immutable PR232 commit; `product-readback.json` records actual retrieval, not just a producer SHA claim. Receiver/reviewer receipt is **NOT_RUN** until that recipient retrieves and measures bytes.

The three module patches were generated directly from real native pre-edit backups (new files from an ABSENT baseline), independent of Git history. Each passes `git apply --check` against the verified predecessor snapshot. Backup metadata and final checksums support precise reversal; **actual .backups recovery bytes remain local and are not committed**. Before undo, verify the current file's final hash and absence of later edits, then restore only its preimage/reverse the recorded patch. Never reset/revert or overwrite unrelated work.

**Disposition:** implemented/tested builder candidate; **GATE_R0 HOLD** pending fresh non-author review and outstanding platform/original qualification. No merge, property writer, release or downstream P2 promotion.

**ONE NEXT ACTION:** a fresh non-author #228 reviewer retrieves PR232 `7f5dc773ac7bb08544d086be734e4337295088a0` and these exact artifacts, reproduces the bounded failure/repair and stale-input tests, and returns its own verdict/limits. The contributing root cannot supply independent approval for its patch.
