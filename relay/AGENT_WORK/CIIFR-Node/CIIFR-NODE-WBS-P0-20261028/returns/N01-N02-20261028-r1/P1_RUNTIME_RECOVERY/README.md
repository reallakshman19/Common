# P1 builder continuation — verified local runtime route

**Governing WBS:** CIIFR-Node Page WBS2 (M3 / engineering P1.0), feeding WBS2.1 (M4 / P1.1); unchanged published plan in [data/ciifr-node/index.json](https://github.com/reallakshman19/progress-page/blob/79303edf1dd60ec93d9ff1680afe9e9f87848222/data/ciifr-node/index.json), project updatedAt `2026-10-28T14:37:51Z`. Native parent [#227](https://github.com/reallakshman19/XML_Compare_Utilities/issues/227).
**Recipient:** existing builder CHAT_ID8 `6ae20df5`. Task [#231](https://github.com/reallakshman19/XML_Compare_Utilities/issues/231), `CIIFR-NODE-P1-R0-REPAIR-R1`. This is delta-only continuation of that assignment; no new WBS, Cycle, recipient or role.
**Candidate:** PR226 head `b2b695f66fc8dfc907f2b9a493b39bd4d4109570`; base `fd86b21aa9dcbfbbe4f8a1d26133b7e9779448be`. DRAFT / GATE_R0 HOLD.
**Date:** 28 October 2026, Asia/Dubai.

## Reconciliation

The [builder checkpoint](https://github.com/reallakshman19/XML_Compare_Utilities/issues/231#issuecomment-6474330067) establishes assignment receipt and bounded source execution. It supplies no applied product commit, dependent PR, native repair regression or accepted Common patch relay. Its local six-file proposal has not been received by the coordinator. Do not treat it as an applied or reviewed repair.

The immediate environment claim is narrower than “repair cannot proceed without a clone.” At the exact candidate, [utils/backup.cjs](https://github.com/reallakshman19/XML_Compare_Utilities/blob/b2b695f66fc8dfc907f2b9a493b39bd4d4109570/utils/backup.cjs) (`7afc1567f770219eebe66fa7c01f43e6acba90ba`) implements `save` and `verify` using filesystem and crypto APIs. Those commands do not call Git or the network. Its `diff` command uses Git's no-index comparison, which does not require repository history. AGENTS explicitly requires a history-independent ledger that works without a Git repository.

Therefore a byte-verified exact-head filesystem snapshot can support the actual mandatory backup command, a genuine pre-edit ledger, and native Node execution. This is an execution route within the existing backup/ledger requirement, not a waiver or replacement by API preimages. It must be described as a source snapshot, never a complete Git checkout. An actual isolated branch/commit and draft dependent PR remain required for product delivery; the GitHub connector can create those remotely.

## Coordinator's fresh feasibility observation

The coordinator fetched the complete, non-truncated exact-head Git tree and compared each materialized file's Git blob ID and size against it. 108 files matched; all 23 files in the actual `tests/cii-fnr-vnext-*.test.mjs` glob were present. This bounded snapshot includes test/runtime dependencies, both source/served trees, package metadata, AGENTS, the native backup utility and its documentation. It is not the whole repository.

On local Linux with Node `v24.22.1` and Git `2.51.1`:
- Actual `node utils/backup.cjs save tabs/cii-workspace/cii-fnr-vnext/ui/app.js "Plan to demonstrate required pre-edit backup on verified unmodified source; no product edit in this proof"` exited 0. It created backup #1, the timestamped plan-log and checksum record.
- Actual `node utils/backup.cjs verify 1` exited 0. The saved bytes equal the 29,888-byte source, SHA-256 `d98a5e49cdfb04db1faba7062e676545863978eac655f6f1d60dd90de4b50eee`.
- The required three-test command exited 0: **17/17 PASS**. See `native-three.log`.
- The original N-01 reproducer was executed again against unchanged verified candidate files. It still observed Normal approval claims `1 → 0` and Validate enabled → disabled after Property → Normal. It also retained the negative-endpoint, BEND-range and residue observations. See `fresh-unrepaired-probe.log`; exit 1 is intentional unresolved-case evidence, not a repair test pass.
- All 108 materialized source files remained byte-identical after the proof.

These are coordinator-observed feasibility results on the old head. They do not count as this builder's execution, a new-head PASS, independent repair review, actual browser/Windows execution or protected-original qualification. The predecessor probe's “reject dormant slot” expectation is not vendor authority: F4 must remain an UNKNOWN residue diagnosis unless independently sourced.

## One executable next action — same builder resumes #231

First publish the actual existing local proposal, reproducer and recovery instructions as **UNAPPLIED / SELF_ASSESSED** public-safe artifacts in the task's Common relay, recording immutable commit, size/hash and readback. Do not recreate them from this note and claim they are the original returned package. Preserve their limits; no protected input bytes or private links.

Then establish your own local execution route:
1. Refresh PR226, remote base/head and overlapping claims. Reuse unchanged grounding. Do not restart onboarding.
2. Fetch `verified-source-manifest.json` alongside this note. Retrieve each needed file from the product repository at the pinned head through the GitHub connector using **base64**; materialize exact decoded bytes under their original relative paths in a fresh workspace. The manifest is an expected retrieval inventory, not proof of your access. Independently check byte lengths, SHA-256 and Git blob IDs (`SHA1("blob " + decimal byte length + NUL + bytes)`) against a fresh exact-head tree. Include any further dependency needed by your actual checks. Never invent missing files, successful imports or browser support.
3. Inspect local overlapping manifests. Create the required unique `.agent-worklogs/` manifest/module plans before product edits. Run the actual repository `backup.cjs save` on **every existing source, mirror and test file you will edit**; verify each backup and record pre-edit checksums. This coordinator's backup is not your backup and does not retroactively qualify your local proposal.
4. Create an isolated remote repair branch from the verified head through the connector (or a real local checkout if available). Record its exact identity. Preserve the author branch; do not fabricate Git history in the snapshot.
5. Execute the actual app/DOM F1 failure before applying the repair. Apply/rework F1–F4 within the original allowlist, keeping source and served mirrors equal. Preserve unchanged Normal/Nodal approvals across Property navigation/intake, while real owning input/rule changes still revoke stale authority. Keep zero semantics and dormant residue unqualified; reject proven impossible typed references without expanding full auxiliary semantics.
6. Run the original three native commands below plus meaningful fail-before/pass-after checks, immutable-byte and source/served/no-writer checks. Preserve the inherited broad-suite failure separately. Produce history-independent patches directly from real pre-edit snapshots; never derive the ledger from HEAD. Do not publish `.backups/` recovery state as product files.
7. Commit only the scoped tested product/report files to your isolated branch; open a **draft dependent PR targeting `codex/ciifr-property-two-path-r0-20261028`**. Bind test inputs and results to the uploaded bytes and exact new head, and actually read back changed files. Publish the return through Common, then return to #231 and link #227/#228 for a fresh non-author review.

```bash
node --test tests/cii-fnr-vnext-property-transfer-r0.test.mjs tests/cii-fnr-vnext-property-transfer-ui-regression.test.mjs tests/cii-fnr-vnext-nodal-ui.test.mjs
node --test tests/cii-fnr-vnext-*.test.mjs
node --test tests/cii-workspace-geometry-authority.test.js tests/cii-workspace-method-c-original-geometry.test.js
```

If your runtime cannot materialize files or execute the backup tool, report the actual attempted command/tool error and affected step. That blocks only dependent implementation/execution claims: the public-safe unapplied proposal can still be relayed through the connector. Do not repeatedly stop solely because GitHub DNS prevents cloning. The coordinator's workspace is not shared with the separate chat.

No protected parser/writer/other-engine/workflow changes, P2 expansion, property writer, merge, deployment or release. Do not mark the engineering gate PASS from this feasibility proof. The next accepted builder return is a concrete tested repair candidate (or a precise remaining execution failure), not another onboarding cycle.
