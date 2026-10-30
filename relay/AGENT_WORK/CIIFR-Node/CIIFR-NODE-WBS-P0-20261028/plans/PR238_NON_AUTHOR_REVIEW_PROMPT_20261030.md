# Non-author review prompt — CIIFR-Node PR238

You are the non-author reviewer for one bounded test correction. Review the actual source and physical fixture records before deciding whether the new expectation is justified. This is an informed, source-exposed review, not a blind review. State your actual agent/chat identity and any prior authorship or exposure; do not invent independence. If you authored this PR's correction, return that limitation rather than self-certifying it.

## Mission and authority

Determine whether PR238 correctly repairs an inherited test-oracle error while preserving the branch restrictions of the existing CII Normal NodeName writer. Your output is a source-backed PASS, FAIL or PARTIAL for this test-only change, with reasons and evidence.

READ_ONLY review: inspect source, create an isolated checkout, execute native tests and run existing code against public synthetic bytes in memory. Do not edit product files, change expected values, modify fixture construction, repair production code, merge, rebase, deploy, or grant R0/property-writing authority. Record a defect instead of repairing it within this review. No private original CII is required.

Use the existing task and Common artifact route. Read the repository's applicable AGENTS.md and current Common START_HERE for routing as needed; established participants need no repeated onboarding or protocol exam. The Owner withdrew Engineering PR Delivery on 26 October; do not reactivate that protocol or create a new lifecycle/Cycle for this review.

## Pinned inputs

- Product repository: https://github.com/reallakshman19/XML_Compare_Utilities
- Review PR: https://github.com/reallakshman19/XML_Compare_Utilities/pull/238
- Exact PR238 head: `fa6e948eb0f71ba93fe8bab01625e3146d1df3a0`.
- Exact base main: `417bf6a954c5a6de72237537e94b05b285191350`.
- Related repaired Property candidate PR232: `d3fbd4041ef4434b4cf5b3c22459f06167be2729`.
- Parent Property PR226: `b2b695f66fc8dfc907f2b9a493b39bd4d4109570`.
- Native task: https://github.com/reallakshman19/XML_Compare_Utilities/issues/231#issuecomment-6524394839
- Public evidence: https://github.com/reallakshman19/Common/tree/836aa0b553010df897323995333432ebbeabee1c/relay/AGENT_WORK/CIIFR-Node/CIIFR-NODE-WBS-P0-20261028/returns/P1-INTEGRATION-BASELINE-20261030
- Project Home: https://reallakshman19.github.io/progress-page/#/ciifr-node

Refresh live PR metadata once and report any difference from these pins. If PR238's head changed, do not silently review a different candidate or relabel old results. Main advancement does not invalidate a pinned-base review, but must be considered before actual integration.

Expected net diff: only `tests/cii-fnr-vnext-branch-scope.test.mjs` and `agents/PR238_workreport.md`. Retrieve and verify actual source bytes, not only the pasted report. Expected test Git blob: `4d2fa260fbd48487e1ae39871e663e7df782cc49`; SHA-256: `dfc12abfc1b93b613f6369a1098186c36437790ed22b6360afe7d8cbc89c17d1`. Expected report blob: `941c35ec3fcfcd20bd7a975af0a74d3b8dfd98d0`. These are expectations for your independent readback, not proof you received them.

Open these unchanged production files under `tabs/cii-workspace/cii-fnr-vnext/` at the pinned head:

- `ui/physical.js`: byte-addressed Normal naming parser.
- `normal/plan.js`: candidate selection, replacement and claim generation.
- `normal/branch-scope.js`: exact branch and logical-node incidence gate.
- `ui/normal-node-closure.js`: complete approval of existing named aliases.
- `ui/writer.js`: independent ownership, preimage, branch and changed-byte checks.

Also inspect the served mirrors under `docs/tabs/...`, the test's fixture constructor and the recovery report. Verify that this PR changes no production or served module and no fixture constructor.

## CII logic relevant to this review

The following describes the bounded layout consumed by this repository's Normal naming reader and synthetic tests. It is not a claim about every CAESAR version or the complete neutral-file grammar. Verify it against the current source.

**Physical records and byte spans.** Sections begin with markers such as `#$ VERSION`, `#$ CONTROL`, `#$ ELEMENTS` and `#$ NODENAME`. Fixed-width spaces and LF/CRLF terminators affect byte positions. The parser retains original line starts and field spans. All spans below are zero-based and half-open: `[start,end)` includes start and excludes end. ASCII fixture characters each occupy one byte. Do not trim or normalize whole files when comparing bytes.

**An element and a node are different objects.** An oriented element has FROM and TO node numbers. Several elements may meet at the same logical node. That incidence can matter to name consistency and branch safety, but it does not make all adjacent elements share temperature, pressure, section properties or rigid data. A name field's owner is found through the element's pointer; a matching string alone establishes no ownership.

**ELEMENTS records.** This Normal reader groups the ELEMENTS data into 15-card records. Within each record:

| Location, zero-based | Meaning used here |
| --- | --- |
| Card0, columns `[0,15)` | FROM node |
| Card0, columns `[15,28)` | TO node |
| Card10 | Length-prefixed branch label; 13-character prefix followed by exact label |
| Card13, columns `[67,80)` | NODENAME pointer |

The internal element witness is `zeroBasedElementIndex:from:to`. Thus `3:9000:9001` identifies the fourth physical element, not node3 or pointer3. Do not confuse this internal zero-based index with one-based ordinals used by another UI.

**NODENAME pointers.** A positive pointer is one-based: pointer1 refers to the first NODENAME card, pointer3 to the third. Zero means that element has no NODENAME record reference. It does not mean logical node0, the first record or a global node lookup. Multiple owners of one record and orphan records are distinct custody problems; eligible branch edits require one unambiguous owner.

**NODENAME fields.** For a card beginning at absolute byte `L`:

| Relative columns | Stored content |
| --- | --- |
| `[0,2)` | Leading prefix |
| `[2,28)` | FROM-name field, width26 |
| `[28,53)` | TO-name field, width25 |

The owning element's FROM/TO endpoints tell us which logical node each field names. Names are padded strings, not numeric node identifiers. Blank physical names remain blank under the existing Normal writer. This PR adds no missing-name allocation.

**CONTROL coverage limitation.** This minimal fixture is designed for the Normal naming parser, which reads NONAM from the first CONTROL card at `[41,54)` and verifies NODENAME cardinality, plus 15-card ELEMENTS grouping. The fixture contains five physical elements and three NODENAME cards; its first CONTROL token is2. It therefore does not establish full CONTROL.NUMELT consistency or vendor-import legality. That inherited fixture limitation is unchanged by PR238. Assess whether it affects the bounded branch claim, disclose it, and do not silently repair the fixture or present it as a qualified complete V14 model. The separate Property R0 V14 index has stricter structural checks and is not the parser being qualified by this test.

## Independently reconstruct the fixture

Use the literal fixture constructor to derive this table yourself. B1/B2 below abbreviate the complete labels; exact strings are `/SYNTHETIC"-BRANCH-001/B1` and `/SYNTHETIC"-BRANCH-001/B2`. The embedded quote is part of each label.

| Element index | FROM→TO | Branch | NODENAME pointer | Existing named endpoint |
| --- | --- | --- | --- | --- |
| 0 | 3130→3140 | B2 | 1 | TO = ALIAS-OLD |
| 1 | 3140→3150 | B2 | 2 | FROM = ALIAS-OLD |
| 2 | 3150→3160 | B2 | 0 | No referenced name card |
| 3 | 9000→9001 | B1 | 3 | FROM = ALIAS-OLD |
| 4 | 3130→3180 | B1 | 0 | No referenced name card |

The two B2 name fields both refer to logical node3140. They are two physical aliases, not two unrelated rename targets. The B1 name refers to node9000, which is branch-isolated in the default fixture.

In the `crossBranch:true` variant, element4 starts at3140 instead of3130. It then makes node3140 incident to B1 and B2 even though element4 has no NODENAME pointer. Unnamed incidence still matters: a branch-scoped partial rename must fail closed.

**Branch matching is exact.** It is not prefix, suffix, fuzzy or substring matching. The rule selects a complete branch label, then the gate requires a single record owner, that owner's exact branch, and every element incident to the named endpoint to belong to that branch. Writer-side validation checks this independently of proposal evidence. Existing named aliases for a touched logical node must all be approved consistently; blank names are excluded from that alias set and remain untouched.

For `ALIAS-OLD → NEW-4`, independently assess these author-proposed expectations:

| Selected branch | Expected physical claims | Basis to verify |
| --- | --- | --- |
| B2 with its last character removed | 0 | No complete matching label |
| B2 followed by `-WRONG` | 0 | No complete matching label |
| Exact B1 | 1 | Element3, pointer3, node9000 FROM field |
| Exact B2, default fixture | 2 | Both physical aliases of node3140 |
| Exact B2, cross-branch variant | 0 | Node3140 crosses B1/B2; diagnostic required |

The inherited test incorrectly put exact B1 in the first two negative cases and required zero for all three. PR238 retains the genuine negatives and gives exact B1 its own positive test. Decide from the physical fixture whether this repairs an incorrect oracle or conceals an implementation defect. A green test run alone cannot answer that question.

## Review the independent expected output

Trace B1 through physical element3 → pointer3 → third NODENAME card → FROM field → plan → explicitly approved writer result.

The new positive test requires exactly one claim, witness `3:9000:9001`, identity `NODENAME.FROM`, B1 evidence and no diagnostics. Its expected output is a copy of the original fixture with only the third card's FROM field replaced by `NEW-4` padded to26 characters.

Verify the offset derivation independently. The test's search token begins with the CRLF preceding the name card. Its `cardStart+4` means two terminator bytes plus the card's two prefix bytes. It must select the third record, despite the second and third name cards having identical text. Walk the section and count records to corroborate the last-occurrence search; do not use the production claim's byteStart/byteEnd as the expected-address oracle.

Compare every output byte to this independent expectation. Require unchanged file length, line endings, B2 names, blank fields, TO fields, branch labels, pointers, CONTROL and other records. Check that existing zero-match, cross-branch, forged-branch, width/ownership and source/served-parity assertions are retained. Use the existing assertions and a small focused probe only where needed; do not build a new test framework.

The writer operates on a new in-memory copy of synthetic TARGET0. Running that existing writer during this review is not permission to write real originals or introduce a Property Transfer writer. Hash identity proves byte identity; it does not prove effective engineering semantics.

## Native execution and falsifiers

Use an isolated exact-head checkout. On Windows, disable autocrlf before the first checkout, for example `git -c core.autocrlf=false clone --no-checkout <repository-url> <new-review-directory>`, then configure `core.autocrlf false`, fetch the pinned commit and switch the fresh directory to that detached head. Preserve other working trees. Verify raw bytes using `git hash-object --no-filters` against `git rev-parse HEAD:<path>`.

Run the targeted test at the exact base and exact candidate. Use separate clean directories or worktrees so the comparison cannot accidentally test changed files twice:

```sh
node --test --test-reporter=tap tests/cii-fnr-vnext-branch-scope.test.mjs
```

Then run the complete VNext suite at the pinned candidate. In Bash:

```sh
node --test --test-reporter=tap --test-concurrency=1 tests/cii-fnr-vnext-*.test.mjs
```

In PowerShell, explicitly expand the file list:

```powershell
$reviewTests = @(Get-ChildItem -LiteralPath .\tests -Filter 'cii-fnr-vnext-*.test.mjs' |
  Sort-Object Name | ForEach-Object { $_.FullName })
node --test --test-reporter=tap --test-concurrency=1 @reviewTests
```

Retain command arguments, versions, input commit, exit codes and raw output. Author-observed results to check, not adopt automatically: targeted base18/1 versus head20/0; full base94/1 versus head96/0 across21 files. The separately reported125/125 run used an isolated current-main+PR232+correction overlay with24 files; it is not a test of PR238 alone or evidence of an actual merge. Historical unchanged PR232 remains123/1. Review all unexpected results rather than changing expectations to reproduce these numbers.

High-value falsifiers: the B1 record does not own node9000; the expected splice uses a production-derived address or wrong duplicate card; a nonmatching branch becomes eligible; cross-branch incidence is ignored; only part of node3140's existing aliases can be approved; unrelated bytes change; or a production/fixture change is hidden in the diff. Any such observation needs a precise finding.

If native checkout or execution is unavailable, continue source/byte review and label the unavailable part NOT_RUN. Do not turn a downloaded source subset into a claimed clean full checkout. Do not repeat the completed public-fixture/Windows/original trials: application modules are unchanged by this PR. No original file upload, private digest or licensed CAESAR run is needed for this review.

## Broader property context — scope boundary

The Property Transfer work has two future mapping paths: node navigation to an exact oriented element for element-owned process/geometry/material/rigid data; and node navigation to individually owned restraint/displacement/force attachments. Shared endpoints do not establish shared process values, cross-file identity or transfer approval. Applied force records are not computed reactions. Restraints remain first priority for future writer qualification. PR238 qualifies none of those semantics and authorizes no new writer.

## Return and stop condition

Return one concise review of the exact pinned head: verdict, actual identity/authorship exposure, received-byte checks, changed-file boundary, independently derived B1 ownership and expected bytes, base/head native results, findings with source locations, inherited fixture limitations and exactly one next action. Distinguish non-author assessment from blind/distinct-human review and Owner acceptance.

Publish permitted review artifacts through the existing Common CIIFR-Node task relay with measured manifest/readback; keep originals and private material out. Put the primary review on PR238 and cross-link issue231 once. If your GitHub principal is the PR author, do not impersonate another reviewer or claim a formal independent GitHub approval; a clearly attributed review comment and artifact receipt can record your actual agent-level assessment.

PASS means this bounded test correction is justified and reviewed. FAIL names the defect. PARTIAL names the exact unexecuted or unresolved part. None authorizes merging PR238/232/226, lifting GATE_R0, P2 work, property writing, deployment or release. Root retains integration preparation; Owner retains R0 acceptance and merge authority. Stop after the review; do not begin the integration yourself.
