# PR238 native operator package — receiver readiness, 31 October 2026

Task: existing CIIFR-Node PR238 / issue231; READ_ONLY qualification. Receiver: root contributor, Chat ID UNKNOWN, author of PR238, source-exposed. This receipt is package inspection, not independent product execution or acceptance.

Received the actual attached R1 ZIP: **14,694 bytes**, SHA-256 **8b46b3af0450c02196d1a870be1e834ee7c92dbe4ccf285d865c6e77a82245bf**. It matches the non-author reviewer's recorded archive identity. ZIP CRC passes, all 13 manifest-listed members match lengths/SHA-256, both JavaScript files pass `node --check`, and the Bash runner passes `bash -n`. PowerShell and the four pinned native test scopes were NOT_RUN here. No repeated GitHub DNS clone attempt was made after the unchanged known blocker.

Actual live PR238 remains draft/unmerged at fa6e948eb0f71ba93fe8bab01625e3146d1df3a0. Its base is417bf6a954c5a6de72237537e94b05b285191350. Non-author source assessment and blocked-native attempt are PR238 comments6538416210/6538476365. That reviewer reports no correction authored in that session but earlier-session authorship UNKNOWN; review is source-exposed and uses the PR author's GitHub account. Preserve these limits.

The archive contains runners and the failed CLONE_BASE attempt, **not completed Windows/native receipts**. The failed clone is an environment result (exit128), not a product test failure. Existing hosted ISO/XML/Table checks do not run this VNext qualification. Overall non-author review remains PARTIAL / native NOT_RUN.

## Receipt consistency limitation found

`verify-results.mjs` requires a minimum hash-row count and known core modules, but does not require all 21 distinct VNext test paths. In a receiver probe explicitly marked SIMULATED, removing one test-file hash row from each otherwise internally consistent receipt still returns PASS_PINNED_NATIVE_TESTS with34 rows instead of35. `VERIFIER_COVERAGE_PROBE.json` records this harness-only result; neither synthetic input nor its PASS is product execution evidence.

This does not prevent the unmodified R1 runners from executing and collecting the intended evidence: they enumerate all21 tests and14 critical source/served modules. Keep the actual R1 ZIP unchanged. Treat its automatic PASS as a preliminary consistency result. Before closing the native gate, the receiver must independently verify **exactly35 distinct expected paths per checkout**, all21 test files, the14 core/mirror files, actual pinned Git identities, raw TAP/exit codes and the identity of the inherited failing test. PACKAGE_READBACK.json supplies the expected path inventory, checked against the independently retrieved pinned main tree. Do not accept row counts alone or duplicate rows.

The expected before/after cases are baseline-target18/1, candidate-target20/0, baseline-full94/1 and candidate-full96/0. A different failure with the same aggregate counts is not the expected inherited failure. Full raw logs, checkout hashes and command/exit metadata must be reconciled rather than relabeled to match expected totals.

## One next execution

Existing local Windows qualification agent01429edb is the proposed operator; actual recipient receipt/execution is NOT_RUN until that agent returns evidence. Confirm actual operator identity and non-authorship of PR238; do not call it blind or distinct-principal review. Run the unchanged package once from its extracted directory in a fresh output location, then return receipts through the existing Common task route and PR238. No original CII, browser trial, source repair, integration or full Property qualification rerun is requested.

`execution-meta.json` records the machine hostname. Retain the raw receipts locally; if publishing a sanitized copy, remove identifying host/path details and label that copy as a derivative while preserving raw evidence privately. Keep worktrees and credentials out of the public return. Receiver checks the complete evidence independently, including the coverage gap above.

GATE_R0, PR238/232/226 merge, P2, property writing, deployment and release remain HOLD. Publishing or retrieving this package is not executing it. No agent is launched or directly messaged by this receipt.
