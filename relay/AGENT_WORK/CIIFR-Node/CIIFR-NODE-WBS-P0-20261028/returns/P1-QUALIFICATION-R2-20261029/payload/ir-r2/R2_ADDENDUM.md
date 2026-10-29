# PR232 R2 exact-head recheck — bounded code PASS; GATE_R0 HOLD

Task: CIIFR-NODE-N01-PR226-R0-IR / issue228, CIIFR-Node Page WBS2.1 / engineering P1.1. Read-only reviewer `/root/n01_pr232_review`; external chat ID UNKNOWN. Reviewed exact head **d3fbd4041ef4434b4cf5b3c22459f06167be2729**, following reviewed R1 **7f5dc773ac7bb08544d086be734e4337295088a0**. Live PR232 remains open, draft and unmerged, targeting PR226 **b2b695f66fc8dfc907f2b9a493b39bd4d4109570**. Main/base remains **fd86b21aa9dcbfbbe4f8a1d26133b7e9779448be**. The live PR body's older R1 counts/head were stale at capture; live head and fresh exact-ref bytes govern this recheck.

**Disposition:** IR-232-01 is **resolved on this exact head in the exercised native application shell**. Selection-time revocation, pending-read cancellation by clear, fresh successful import, explicit reapproval/revalidation/reapply and literal expected exported bytes all PASS. F1 navigation and bounded F2/F3/F4 regressions remain PASS. No additional defect was found within this delta review. This is a bounded code verdict, not whole-GATE_R0 release or Owner acceptance.

## Fresh source and unchanged prior evidence

Retrieved both mirrored app.js files, focused repair test and PR232 work report afresh through GitHub at the exact R2 ref, decoded base64 bytes and verified Git blob identities. The two app modules have blob **74891ccd948782b54b8f7781168e996c65d2af9e**, focused test **ff96b9e9447875f54a42436dffefded35b626327**, work report **bc8ea2417c3ca735fbf279dd8fd37bd7c3c8c1f8**. The isolated R2 copy reuses the prior verified candidate cache for unchanged files; all **109 retained files** were verified against a freshly retrieved, nontruncated R2 Git tree and rehashed after execution. Those four files are the only retained-file deltas from R1. Six source/served pairs match exactly. Source/served app SHA-256: **7c246390253ee6a4a891927f8f27bdb5575a57494244ebd3afcc0085bd614817**.

The app-shell delta increments csvSeq and invalidates the owning state before any asynchronous read, including empty selections, then captures the new revision guard. Clearing increments the request sequence, so an older read cannot regain authority. No parser, property reader, property panel, writer, legacy engine or effective-engineering interpretation changed in this delta; no property writer was introduced. The reviewer made no product/test/oracle edits, branch update, approval, merge or deployment.

R1 report/probe/logs were not overwritten. R1 report SHA-256 remains **fc6c520ac950736868343048f392c94d6cef74cad6b12a9c5e7428b11b6f36e5**. Its FAIL remains valid for R1, and its exact-base comparisons retain their original provenance.

## Independent reproducer and expected result

`node probe-r2.mjs` ran the actual R2 app module with the repository native DOM helper. It reuses the R1 physical/branch falsifiers and independently extends the deferred-input check; the author test's green result is not its oracle.

1. Generate, approve, validate and apply `OLD-A → NEW-A`, establishing export eligibility. Select a changed CSV requesting `OLD-A → NEW-C` while its `.text()` promise remains pending. Before release, require zero claims and disabled Validate/Apply/Export. Invoke the real Export handler directly and capture Blob creation: **zero downloads**. A Property roundtrip retains the revoked state.
2. Release that read. Confirm the rule is NEW-C but export remains disabled. Regenerate, explicitly approve, validate and apply, then export. Require exactly one Blob and compare every exported byte to the original demo with only the literal `OLD-A` field replaced by `NEW-C`. **Byte equality PASS**; the expected image is a literal splice, not production writer output.
3. Starting from newly applied state, select another deferred CSV, then clear its input before releasing the old read with `OBSOLETE` rules. Require the prior visible NEW-C rule to remain, no claims, all authority revoked, and a direct Export to emit **zero Blobs**. **PASS**; the stale read cannot reinstall rules or output.

The same probe reruns literal public SOURCE/TARGET0 stored-value and ownership expectations, endpoint negative/zero/fraction rejection, all15 typed pointer negative/count+1/fraction challenges, all10 unsupported non-NODENAME typed-family count1/pointer1 UNKNOWN checks, and lexical-underflow dormant-restraint UNKNOWN span evidence. **PASS**. These checks deliberately test failures and wrong outcomes, not just successful parse or digest equality.

## Native execution

Node v24.22.1, Linux; isolated `n01-pr232-r2-review/candidate`. `evidence/commands.json` preserves complete arguments and actual exit codes; whole raw output is retained.

| Command/check | Actual result | Raw log |
|---|---|---|
| `node --test tests/cii-fnr-vnext-property-transfer-r0.test.mjs tests/cii-fnr-vnext-property-transfer-ui-regression.test.mjs tests/cii-fnr-vnext-nodal-ui.test.mjs` | PASS 17/17 | `required-three.tap` |
| `node --test tests/cii-fnr-vnext-property-transfer-repair.test.mjs` | PASS 13/13 | `repair.tap` |
| `node --test --test-concurrency=1 tests/cii-fnr-vnext-*.test.mjs` (24 files, expanded in receipt) | **FAIL: 123 PASS / 1 FAIL** | `vnext-all.tap` |
| `node --test tests/cii-workspace-geometry-authority.test.js tests/cii-workspace-method-c-original-geometry.test.js` | PASS 9/9 | `geometry.tap` |
| `node probe-r2.mjs` | PASS, including direct-export and literal-byte expectations | `probe-r2.log` |

The one broad-suite failure remains the unchanged branch-scope assertion at line85. It groups exact existing B1 with two nonexistent branch strings and incorrectly requires zero for all. Literal fixture facts: B1 element `3:9000:9001` has pointer3 and FROM `ALIAS-OLD`, and node9000 has no cross-branch incident; a B1 `ALIAS-OLD → NEW-4` rule must produce one claim. The R2 independent probe confirms expected counts **0/0/1**, confirms the B1 witness/FROM field, and compares its writer result to a literal expected field splice. Exact-base R1 run was **94 PASS / 1 FAIL** with this same assertion. That supports an inherited test-oracle error; it does not turn the raw whole-suite FAIL into PASS. No test was changed or suppressed by this reviewer.

## Inputs and limitations

Public synthetic fixtures reused without normalization from the R1 fresh GitHub retrieval: Common **56dbc3a0af137c433ffb5fec48316fa2022d075c**, `relay/AGENT_WORK/CIIFR-Node/CIIFR-NODE-WBS-P0-20261028/payload/`.

| Fixture | Bytes | SHA-256 |
|---|---:|---|
| SYNTH_V14_SOURCE.cii | 8276 | c8de516c54767c7cf7d5239d404810be891ed3d56ec2111db3dc4c2b07dcdb0b |
| SYNTH_V14_TARGET0.cii | 8276 | 0bbc3b0a8b7b1e73d655d0a0ffc267e6a698dec5ff66763c468cdc835cc19661 |

Those exact digests were rechecked in R2. Repository public Benchmark S1/S2/S3 bytes are also Git-verified; their Geometry checks do not establish the protected Owner-original result. Actual original remains **NOT_RECEIVED** here. Browser, Windows, protected original, licensed CAESAR II and original acceptance remain **NOT_RUN by this reviewer**; no reprovisioning was attempted.

This participant did not author R1 or R2; root did. Same host/account/workspace and prior exposure to author reports, tests and R1 findings remain explicit: **not blind; distinct human/account/host independence NOT_ESTABLISHED**. Independence of expectation is limited to the literal physical records, literal byte splices, branch analysis and independently chosen deferred-input check. The native DOM is a lightweight repository test environment and cannot prove actual browser event/render/download behavior. Unsupported auxiliary/effective-engineering meaning remains unqualified; a vendor-specific unqualified meaning can survive these checks and must remain held.

**One next action:** root relays this unaltered R2 addendum and native receipts, reconciles the bounded code PASS with the preserved whole-suite FAIL, and advances only the still-required runtime/original qualification through authorized custody. **GATE_R0 HOLD; no merge/release approval is given.**
