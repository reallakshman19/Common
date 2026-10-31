# CIIFR-Node PR238 — source-exposed non-author review

**Disposition: PARTIAL — bounded oracle correction justified by physical bytes and unchanged guard source; independent native base/head execution NOT_RUN.** No merge, R0 acceptance, Property Transfer approval, implementation or release authority.

## Reviewer identity and provenance
Reviewer: **ChatGPT / GPT-6**, evaluating this request in the present conversation on 2026-10-31. I did not write the PR238 correction in this review session; authorship in other sessions is **UNKNOWN**, not independently proved. I read the complete brief, author work report, author relay evidence, and actual source files and am **source-exposed, not blind**. Authenticated GitHub principal: `reallakshman19`, the same principal as PR author. **This is an agent-level assessment/comment, not an independent-principal or formal GitHub approval.**

## Pins, exact Git blobs and boundary
- [PR238](https://github.com/reallakshman19/XML_Compare_Utilities/pull/238) refreshed once: draft/open, live head `fa6e948eb0f71ba93fe8bab01625e3146d1df3a0`, pinned base `417bf6a954c5a6de72237537e94b05b285191350`; **no head/base drift**.
- Exact base→head comparison: 2 commits; only `tests/cii-fnr-vnext-branch-scope.test.mjs` (+20/-1) and `agents/PR238_workreport.md` (new +32).
- Test Git blob base `c69511a8c5234f46d9d678b88e5de53955b26c79`, head `4d2fa260fbd48487e1ae39871e663e7df782cc49`.
- Independently calculated SHA-256 from fetched UTF-8 file content: base `1f5e7a9a2e5745013e1bfc8e873ec396ed602eb41c5ff20b33bb56c3b5aebb81` (14,334 bytes), candidate `dfc12abfc1b93b613f6369a1098186c36437790ed22b6360afe7d8cbc89c17d1` (15,301 bytes).
- Recovery report Git blob `941c35ec3fcfcd20bd7a975af0a74d3b8dfd98d0`, SHA-256 `a444598113ca36d035707a642c909070d2020ba333a7fec445d0d52f23ab1ad0` (3,968 bytes).
- Identical base/head/served Git blobs: `ui/physical.js` `a0a5d5e`, `normal/plan.js` `2c12781`, `normal/branch-scope.js` `02732a2`, `ui/normal-node-closure.js` `1931cfc`, `ui/writer.js` `15e383e`, `ui/source-provenance.js` `40b4b2c`, `ui/app.js` `f5fb8e3`. The complete SHA values are fetchable from the pinned files. The unchanged fixture constructor is at [test lines 8–31](https://github.com/reallakshman19/XML_Compare_Utilities/blob/fa6e948eb0f71ba93fe8bab01625e3146d1df3a0/tests/cii-fnr-vnext-branch-scope.test.mjs#L8-L31).
- Git blob readback establishes repository source identities. **A clean checked-out worktree and `git hash-object --no-filters` were NOT_RUN** because this environment cannot resolve github.com through Git; do not confuse fetched blobs with worktree verification.

## Independent physical fixture finding
Reconstructed the constructor as ASCII fixed-width bytes, then independently counted line starts, 15-card ELEMENTS groups, length-prefixed exact branch labels, pointers in card13 [67,80), and NODENAME cards. Default synthetic V14/CRLF fixture: 6,280 bytes, 84 physical lines, 5 elements, 3 names, three one-based NODENAME pointers 1,2,3 and two zero pointers. The complete branch labels are `/SYNTHETIC"-BRANCH-001/B2` and `/SYNTHETIC"-BRANCH-001/B1`.

| Physical element | FROM→TO | Exact branch | Pointer | Existing physical name |
|---|---|---|---|---|
| 0 | 3130→3140 | B2 | 1 | NODENAME.TO=ALIAS-OLD, node3140 |
| 1 | 3140→3150 | B2 | 2 | NODENAME.FROM=ALIAS-OLD, node3140 |
| 2 | 3150→3160 | B2 | 0 | no name pointer |
| 3 | 9000→9001 | B1 | 3 | NODENAME.FROM=ALIAS-OLD, node9000 |
| 4 | 3130→3180 | B1 | 0 | no name pointer |

**Expected branch claims independently derived** for ALIAS-OLD→NEW-4: truncated B2=0; B2+`-WRONG`=0; exact B1=1; exact B2 default=2; B2 with `crossBranch:true`=0. The B1 name is on node9000, which is isolated to B1, even though identical text occurs at B2-owned physical names. In the cross variant element4 FROM becomes3140; its pointer remains zero but its B1 incidence prevents B2 rename. Pointer0 is absence of NODENAME reference, not node0 or first record.

The three name cards begin at absolute bytes 6115, 6170, 6225. The second and third cards have identical text. The exact B1 field is **third card FROM, half-open [6227,6253), width26**, witness `3:9000:9001`. The literal CRLF-prefixed search token starts at6223; `cardStart+4=6227` skips CRLF(2) and prefix(2), independent of production claim offsets. The independently constructed output replaces this one 26-byte field with padded `NEW-4`. Fixture SHA-256 `0a43de71b6c37f9251201fe680baaf8994bdea9ba794e49ffb684ccad712254d`; independent output SHA-256 `6bcfe0a0ddbb60df26751965a6d4bfbd56b5db20037c670a016016de9ea1020a`. Output remains 6,280 bytes; exactly 9 byte *values* change, all within [6227,6253). Comparing all 6,280 bytes with an independent direct field-slice splice yields equality; all B2 name records, other name fields, fixed records, CONTROL, branch strings, pointer fields and CRLFs are preserved. **Actual production writer output was NOT_EXECUTED locally**; this is a physical expected-output oracle and code trace, not a claim of a native end-to-end result.

## Implementation safeguards and coverage retained
- `ui/physical.js:33–81`: scan line byte starts; CONTROL NONAM at [41,54); 15-card grouping; card0 FROM/TO; card10 exact branch with declared length; card13 one-based pointer; two fixed name field spans; shared/orphan flags.
- `normal/plan.js:56–108`: exact branch match by equality, then `branchContainsNode`; ambiguous/missing name refused; proposed byte-range owned by pointer/element; missing branch yields ZERO_MATCHES.
- `normal/branch-scope.js:2–8`: one unambiguous owner on selected exact branch and all endpoint-incidence elements on that branch.
- `ui/normal-node-closure.js:6–45`: writer-side approval closure of every existing named physical alias on logical node; blanks protected; consistent original and proposed alias names.
- `ui/writer.js:16–80`: original SHA check; explicit approval; independent field/branch/witness/preimage/width validation; no blank edit; closure; structural reparse; unchanged off-span bytes.
- `tests/cii-fnr-vnext-branch-scope.test.mjs:81–107`: correction removes B1 only from two false-negative cases and requires explicit one-claim B1 witness, FROM field, exact branch, empty diagnostics, literal independent output. Remaining checks include cross branch refusal (109–137), SOURCE physical alignment (165–181), forged branch writer rejection (242–251), invalid branch filter (253–260), source/served parity (268–275).

**Finding F1 (oracle):** the inherited `branch identifier mismatch` test treated exact B1 as nonexistent. Actual fixture establishes a B1-owned FROM name; expecting zero is erroneous. PR238 fixes the oracle without changing production or fixture. No product defect discovered in this bounded trace.

**Finding L1 (inherited fixture qualification):** CONTROL's first token is 2 while there are 5 physical elements. The Normal reader validates NONAM=3 and 15-card grouping but not full CONTROL.NUMELT consistency. The fixture is suitable for this bounded name/branch test; it is **not** a verified vendor-importable or complete CAESAR V14 model. Property R0 has separate stricter validation. This limitation predates PR238 and is not to be silently repaired here.

## Execution provenance
Reviewer: Node `v22.16.0` used only for isolated **reviewer-owned public synthetic physical-byte oracle**, PASSED. Attempted repository `git ls-remote` failed: `Could not resolve host: github.com`. Independent exact-base and candidate native targeted/full suites, worktree-byte comparisons, and actual production writer execution = **NOT_RUN**. No Windows, licensed solver or private original trial is required.

Author's Common relay evidence was inspected as separate provenance, not re-executed: `main-before.tap` shows 95 tests/94 pass/1 fail/exit1; `main-after.tap` 96/96/exit0 (21 VNext files); `combined-after.tap` 125/125/exit0 (24 files). The latter is an unmerged PR232 source overlay, **not** PR238-alone or an integrated head. Targeted 18/1 and 20/0 are author-reported, not independently rerun. PR232 historical 123/1 remains unchanged.

## Overall disposition and exactly one next action
**PARTIAL:** source/physical assessment supports the corrected B1 test oracle; lack of a separate clean native execution prevents a complete independent qualification and no formal GitHub approval is possible from this connected author account.

**Next action:** an authorized non-author operator runs the targeted test at separate clean pinned base/head checkouts and the full 21-file VNext suite at the candidate, preserving raw TAP/exit codes and `git hash-object --no-filters` proofs against `HEAD:<path>`, then attaches that evidence to PR238 for gate completion. Root retains integration preparation, Owner alone retains merge and GATE_R0 acceptance. No PR238/232/226 merge, P2, Property Transfer writer, deployment or release is authorized.