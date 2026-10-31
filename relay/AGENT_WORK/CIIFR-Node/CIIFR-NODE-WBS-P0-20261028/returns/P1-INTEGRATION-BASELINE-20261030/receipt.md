# CIIFR-Node integration baseline and inherited test correction

Task: existing CIIFR-Node WBS P1 / issues231,228,229, parent227. Date: 2026-10-30, Asia/Dubai. Executor: root contributor, Chat ID UNKNOWN, author-exposed. This is an implementation/test assessment, not an independent acceptance or merge decision.

Current main is `417bf6a954c5a6de72237537e94b05b285191350`, 86 commits after the original base `fd86b21aa9dcbfbbe4f8a1d26133b7e9779448be`. The 43 changed main paths have **zero exact-file overlap** with the 22 net PR226+PR232 paths. Both recursive Git trees were retrieved without truncation. Product PR232 remains draft at `d3fbd4041ef4434b4cf5b3c22459f06167be2729`, parent PR226 remains draft at `b2b695f66fc8dfc907f2b9a493b39bd4d4109570`. No existing branch is rebased or merged.

The branch test, parser, branch gate, Normal planner and writer have identical Git blobs on current main and PR232. The fixture explicitly contains B1 element 9000->9001 with pointer3 and a branch-isolated ALIAS-OLD FROM name. The inherited test incorrectly groups exact B1 with two nonexistent identifiers and expects zero for all three. Production returns the correct one B1 claim; no product defect is established here.

The proposed separate test correction retains both nonexistent-identifier zero-match checks and adds a positive B1 test. It requires witness `3:9000:9001`, FROM-field identity, B1 evidence and no diagnostics. Writer output must equal an independently constructed literal splice of the final synthetic NODENAME card's 26-character FROM field; the expected address does not come from production claim offsets. The fixture constructor and every production module remain unchanged.

| Native check, Node v24.22.1 on Linux | Result | Evidence |
| --- | --- | --- |
| Current-main complete VNext suite before correction, 21 files | FAIL: 94 pass / 1 fail; exit1 | main-before.tap |
| Current-main complete VNext suite plus test correction, 21 files | PASS: 96/96; exit0 | main-after.tap |
| Current-main plus all 22 PR232 net paths and test correction, 24 files | PASS: 125/125; exit0 | combined-after.tap |

These were **individually Git-verified source subsets**, not full cloned or merged Git worktrees. Every VNext test file is present. The baseline snapshot has 95 verified files; the combined snapshot has 112 verified unchanged files plus the corrected test. Both source inventories, full commands/exit codes and raw TAP output accompany this receipt. The combined check is an isolated source overlay, not a published merge or a new Windows run. The unchanged historical PR232 still has its reported 123/1 result; it is not relabeled green. Existing public/original Windows evidence is retained at its actual d3fbd404 identity and prior evidence limits.

Checked relevant active CII PR171,176,145,226,232 file lists: none edits the target branch test. Current PR226/232 have no submitted GitHub PR reviews; the existing issue/Common non-author code review and local Windows attestations retain their scoped provenance. Their successful hosted checks are ISO engineering and XML/Table suites, not native Property Transfer acceptance.

Native backup #1 and a history-independent local patch ledger were created before editing the existing test. Its preimage SHA-256 is `1f5e7a9a2e5745013e1bfc8e873ec396ed602eb41c5ff20b33bb56c3b5aebb81`; corrected SHA-256 is `dfc12abfc1b93b613f6369a1098186c36437790ed22b6360afe7d8cbc89c17d1`. Public patch headers are repository-relative. No private original, private digest or raw original field is included.

**Disposition:** the inherited test-oracle defect has a concrete test-only correction for a separate draft PR against current main. P1 native integration uncertainty is narrowed by the passing overlay. Remaining integration gates are non-author review of this correction, a controlled combined exact-head check after actual integration, and the Owner's R0-only HOLD/merge decision. Preserve the existing PR chain: the small test fix can enter main first; PR232 can then enter PR226, and current main can be incorporated without discarding its 43 changed paths, subject to actual merge authorization. Validate the resulting real head and compare application module identities with d3fbd404; repeat only checks justified by changed dependencies.

**GATE_R0 remains HOLD.** No product implementation, writer, workflow, runtime, canvas, fixture constructor, existing candidate head, private original, correspondence authority, deployment or release changes. P2 and later property writing remain held. A test-only green suite is not engineering or release acceptance.

**Next actor/action:** a non-author reviewer (identity not assigned by this receipt) reviews the small test correction and literal expected-byte derivation; root retains integration preparation, and the Owner retains merge/R0 acceptance authority. No new agent is launched or directly messaged by this report.
