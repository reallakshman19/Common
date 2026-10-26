# PR185 F1 — bounded author repair, then required re-review
Task CIIFR-GEO-G1-PR185-F1-REPAIR / generation3 / coder6adedbc6 / Cycle10.
Starting candidate PR185 7f9ea25931777dda85686ad7cc9a1a011132a23c, treea6a2ea6820e97fbdedc2e1e96718dc2a26a67e3d, same task branch/stacked PR. No product merge.

## Complete review and actual witness
Read [the complete separate non-author verdict](https://github.com/reallakshman19/XML_Compare_Utilities/issues/186#issuecomment-6411018989) and the unchanged review artifacts in this folder. The reviewer independently verified all8,577 candidate blobs, reran18 baseline/21 candidate tests and HTTP30/assets on Node24.22.1 with actual test-only xmldom0.9.12, then found F1 despite the green existing tests. That is not browser/WebGL acceptance. Same-account/principal uncertainty and upstream exposure remain disclosed.

F1 is app.js lines92–104: revoked request A completes late, the real bridge correctly rejects/disposes stale A, but the old app continuation calls disableGpu() and tears down current B. Both new-before-old and FIFO startup completions reproduce. The observed JSON/CSV/SVG remained unchanged: this is known lifecycle/UI teardown, not a claim of demonstrated export corruption.
The review-only reproducer uses exact app/session/XML/bridge with synthetic DOM/WebGL factory. The script **exits0 when its defect assertions succeed**. Never cite that zero as a fixed-candidate PASS.

## One repair
Make post-await success, error cleanup and finally/UI state updates request-owned, so an obsolete operation cannot dispose, hide, relabel, re-enable or otherwise mutate a newer active/pending viewer. Preserve the real bridge's generation/current-binding rejection; do not remove invalidation to make this test green.
Limit product edits to app.js, focused actual-app lifecycle regression tests, required recovery workreport and README test command if actually necessary. Existing all-row picks, complete R*p+t once, source identities/components, graph/Method C/export semantics, shared viewer/Worker and pinned assets stay unchanged.
Reuse actual source receipt and qualified unchanged source understanding; verify exact affected preimages at the current PR185 head, run required native backups and history-independent patch ledger, use the already authorized expected-head-lease remote Git-data route. If the remote head drifted, reconcile before edits.

## Discriminating validation
Create a correct-behavior regression against the actual app continuation and real bridge/session, not only a pure bridge helper. Correct expectation: after obsolete A settles, current B remains active with its correct UI, and only obsolete resources are disposed. Preserve this same expectation across baseline and repair: fail before, pass after.
Exercise both independent review orderings plus obsolete rejection/error and finally/control-state cases, including B pending when A settles. Keep the original review reproducer/report immutable as evidence of7f9ea259; add a separate fixed-behavior regression rather than rewriting historical evidence.
Run focused regression and the necessary existing native/HTTP suites after the change. Record actual parser/runtime versions and original-file input hashes; do not silently relabel author0.9.8 checks as0.9.12. Synthetic/native tests are not served-browser PASS.

## Return and next actor
On #180, with a pointer on #186, publish exact repaired PR185 head/tree/parent, minimal changed scope and byte/preimage evidence, actual before/after regression and checks, recovery evidence and NOT_RUN. Then one rev10/gen3 v1 envelope on Common#482.
**Next actor is the separate non-author reviewer on #186**, who must inspect/run affected claims at the new exact head. An author PASS or Oracle source check cannot close that gate. If independently reviewed again with no source finding, actual served-browser/GPU and Owner trial remain separately BLOCKED until executed on a capable host.
No new onboarding, G2, Writer, acceptance, product merge/release or Oracle cutover. Proceed with this existing G1 repair without a routine permission pause; report a concrete new blocker promptly.
