# PR232 scoped non-author code review — FAIL / GATE_R0 HOLD

Task: CIIFR-NODE-N01-PR226-R0-IR, native return issue228; CIIFR-Node Page WBS2.1 / engineering P1.1 following WBS2/P1.0. Review participant: `/root/n01_pr232_review`; external chat ID UNKNOWN. This report is anchored to **7f5dc773ac7bb08544d086be734e4337295088a0**, not any subsequent repair. Live GitHub PR232 was open, draft, unmerged, based on PR226 **b2b695f66fc8dfc907f2b9a493b39bd4d4109570**. Main/base: **fd86b21aa9dcbfbbe4f8a1d26133b7e9779448be**. Live snapshots and exact changed-file list are retained in `evidence/`.

## Result and finding

**F1 FAIL at owning CSV selection boundary; completed Property navigation preservation PASS within the exercised native DOM scope.** F2/F3/F4 bounded code checks PASS. No new defect was found in the six changed production files' Property reader/navigation behavior; however the broader F1 revocation claim remains incomplete because the unchanged CSV intake handler allows stale export while reading a newly selected CSV. The complete VNext command remains FAIL because of an independently dispositioned inherited assertion error. These are separate observations.

**IR-232-01 — owning CSV selection leaves old export authority live during asynchronous read (inherited, consequential).** At `tabs/cii-workspace/cii-fnr-vnext/ui/app.js:491–499` and its served mirror, the handler awaits `file.text()` before invalidating the plan, decisions, validation and applied output. Reproduction: approve/validate/apply `OLD-A → NEW-A`; select `changed-rules.csv` requesting `OLD-A → NEW-C`; hold its asynchronous text read pending; invoke Export. The actual application shell keeps Validate/Apply/Export enabled and exports bytes containing `NEW-A`, not `NEW-C`. The selected owning input has changed, yet its prior authority remains usable. The independent expectation is immediate revocation at selection, consistent with the task and the neighboring TARGET/SOURCE intake's selection-time revocation, rather than only after successful reading. Normal CSV selection with an immediate completed read does revoke correctly.

The same probe on exact base **fd86b21…** produces the same stale download. Candidate/base CSV handler snippets have identical SHA-256, recorded in `evidence/postrun-identity.json`. This is **inherited**, not introduced by PR232, but invalidates an unqualified claim that all real owning-input changes revoke authority. The author's repair assertion awaits the completed change handler and therefore cannot expose this interval. The probe captures the generated Blob in native Node; it is not evidence of a real browser download. No product or product test was edited.

## Executed checks

Commands ran in the isolated `n01-pr232-review/candidate` directory; Node v24.22.1 on Linux. Full expanded arguments and return codes are in `evidence/commands.json`.

| Check | Result | Evidence |
|---|---|---|
| `node --test tests/cii-fnr-vnext-property-transfer-r0.test.mjs tests/cii-fnr-vnext-property-transfer-ui-regression.test.mjs tests/cii-fnr-vnext-nodal-ui.test.mjs` | PASS 17/17 | `required-three.tap` |
| `node --test tests/cii-fnr-vnext-property-transfer-repair.test.mjs` | PASS 11/11 | `repair.tap` |
| `node --test --test-concurrency=1 tests/cii-fnr-vnext-*.test.mjs` (24 files, fully expanded in receipt) | FAIL: 121 PASS / 1 FAIL | `vnext-all.tap` |
| Same complete affected suite on exact base (21 existing files) | FAIL: 94 PASS / 1 FAIL | `base-vnext-all.tap`, `base-command.json` |
| `node --test tests/cii-workspace-geometry-authority.test.js tests/cii-workspace-method-c-original-geometry.test.js` | PASS 9/9 | `geometry.tap` |
| `node probe.mjs` | Executed; bounded semantic assertions PASS; stale owning-CSV export reproduced | `probe-candidate.log` |
| `REVIEW_SUBJECT=base node probe.mjs` | Executed; base branch/CSV assertions reproduce same inherited behavior; reader checks still use candidate explicitly | `probe-base.log` |

The tests use the real app module with the repository's lightweight native DOM, not browser rendering. F1 assertions inspect retained proposal count, decisions, validation/apply/export eligibility and output hash across Property intake and A/B changes; real completed rule, TARGET, SOURCE and CSV edits revoke. Nodal retained state and later TARGET revocation are exercised. Pending Normal validation is cancelled without deleting completed approvals. Legacy Normal/Config direct navigation behavior is retained. The full suite and bounded Geometry provide checked regression coverage, not universal regression freedom.

## Inherited branch-scope failure independently dispositioned

`cii-fnr-vnext-branch-scope.test.mjs:81–87` iterates two nonexistent branch strings **and exact existing B1**, expecting zero replacements for all three. The fixture explicitly gives element ordinal4 (`3:9000:9001`) exact branch B1, pointer3, and FROM name `ALIAS-OLD`; node9000 has no cross-branch incident. Therefore a B1 rule `ALIAS-OLD → NEW-4` should produce **one** FROM claim. Both nonexistent strings should produce zero.

The scratch probe derives expected counts 0/0/1 from those literal fixture records, confirms the B1 witness and FROM identity, invokes the writer and compares its output to a literal byte splice of only that expected field. Candidate and base agree. The failure is a faulty inherited test expectation; it is not accepted merely because base is red. The raw suite FAIL is preserved. This review grants no permission to alter that test.

## Independent physical falsifiers and limits

Fresh public SOURCE/TARGET0 fixture bytes, rather than author output, supply physical expectations: SOURCE endpoints400→500 and500→600; node500 has two incidents and one restraint; stored T1/P1/density pairs200/30/1.01 and180/20/1.01; TARGET0 T1/P1 from physical cards195/28 and175/18. The probe checks those literal values. Its first development run had a reviewer-written incorrect TARGET0 expectation (100/5 and90/4), failed, and was corrected only after reading the original TARGET0 physical cards; that false start is a probe error, not a product finding or candidate-derived oracle.

F2: negative, zero and fractional endpoint edits are rejected. Zero is explicitly an unsupported positive-node profile boundary, not a claim of vendor-invalid data. F3: physical splices challenge **all15** typed pointer families at negative, own-count+1 and fractional values, all rejected. All10 unsupported non-NODENAME typed families with count1/pointer1 and missing content remain visible UNKNOWN rather than qualified content. F4: a dormant slot containing lexical `1D-999` remains UNKNOWN despite numeric underflow; owner1/pointer1/slot2 and physical byte span retain the literal residue. The repair test additionally checks visible UNKNOWN/raw evidence on intake and in both modes. Original public input digests remain unchanged.

This does not establish engineering correctness for unsupported auxiliary content, active restraint DOFs/gaps/stiffness, effective process cases/units, arbitrary vendor lexical dialects or other populated families. A plausible remaining wrong result beyond these bounded cases is a vendor-specific unqualified auxiliary meaning; it must remain held. No property writer or transfer eligibility was added: inspected reader is read-only, Path A/B report `writeEligible:false`, panel `canWrite:false`, and changed files contain no new writer import or output mutation. All six source/served pairs match; their actual digests are in `postrun-identity.json`. Protected parser/writer files were not in PR232's changed-file list.

## Input identity, provenance and independence

Public fixture origin: Common commit **56dbc3a0af137c433ffb5fec48316fa2022d075c**, `relay/AGENT_WORK/CIIFR-Node/CIIFR-NODE-WBS-P0-20261028/payload/`.

| File | Bytes | SHA-256 | Git blob |
|---|---:|---|---|
| SYNTH_V14_SOURCE.cii | 8276 | c8de516c54767c7cf7d5239d404810be891ed3d56ec2111db3dc4c2b07dcdb0b | 7d00c13f5c5906a9bb2dba53287f133c8db06358 |
| SYNTH_V14_TARGET0.cii | 8276 | 0bbc3b0a8b7b1e73d655d0a0ffc267e6a698dec5ff66763c468cdc835cc19661 | dddf157895571802973b71904fbad0a679a7e271 |

Both files were freshly retrieved as base64 through GitHub and decoded without normalization; Git blob hashes verified. Candidate source initially came from the author's available workspace cache, copied into this isolated workspace; **109 retained files** were individually verified against the live exact-head Git tree. Exact-base cache reuse likewise verified **88 files** against the live base tree. Post-run rehash found no changed candidate/base files. This is verified cache reuse, not an independent checkout or blind acquisition. Repository benchmarks S1/S2/S3 are publicly committed benchmark bytes verified against the candidate tree; they are not the protected Owner original.

Read actual root AGENTS.md; docs/AGENTS.md has the same live Git blob. Applied scoped coordinator independent-review and engineering-data-fidelity instructions, plus Common independent-review SKILL, APPLYING_GUIDANCE and INDEPENDENCE at **d7365707dca0039f9a529f7309b635ff160c9dd0**. Withdrawn delivery protocol/adoption exam was not enforced. No new Cycle, product/test/oracle edit, branch update, approval, merge, deployment or duplicate GitHub comment was performed.

Authorship: this participant did not author PR232; root did. Exposure: parent task, live PR description, existing tests and available source/fixtures; author conclusions were visible, including reported test counts. Not blind. Same account/host/workspace is shared; distinct human/account/host independence **NOT_ESTABLISHED**. Method independence consists of inspected expectations, physical contrary splices, literal branch output expectation and the separately chosen deferred-input falsifier. Native reruns alone are implementation-coupled. No formal professional/engineering acceptance is claimed.

Real browser, Windows, protected original (**NOT_RECEIVED**), licensed CAESAR II and original-file acceptance: **NOT_RUN by this reviewer**. Root's separate browser attempt is reported blocked; no browser provisioning was duplicated and no browser PASS is claimed. GATE_R0 remains HOLD; native code checks cannot release it.

**One next action:** root, as the existing authorized writer, minimally revoke Normal CSV authority when selection starts, preserve fail-before/pass-after evidence, and return the new exact head for a separate read-only recheck. This report must remain unchanged on its reviewed head.
