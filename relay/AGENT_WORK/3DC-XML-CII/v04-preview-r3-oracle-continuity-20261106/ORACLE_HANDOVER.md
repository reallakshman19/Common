# ORACLE HANDOVER — 3D_Converters_v0.4 Step 4 R3 → R4

**Prepared:** 2026-11-06. **Mode:** PUBLIC-SAFE knowledge checkpoint; producer/Oracle self-assessed; engineering-critical; successor **UNASSIGNED**. **Status:** KNOWLEDGE_PACKET_PREPARED; control handover **NOT ACTIVATED**; `MERGE_HOLD`. Read [concept](CONCEPT_NOTE.md), [architecture](ARCHITECTURE_COMPLEX_LOGIC.md), [decisions](ARCHITECTURE_DECISIONS_AND_CHALLENGES.md), then [successor prompt](ORACLE_SUCCESSOR_PROMPT.md).

## A. Identity / no imaginary cutover

Outgoing role: this ChatGPT session served the Owner as Oracle/coordinator for the v0.4 performance/GLRD parity track and authored earlier R2 comparator instructions/helpers, then independently inspected supplied artifacts. **It is therefore not a conflict-free independent implementation reviewer.** Stable session ID: **not exposed / UNKNOWN**. Incoming Oracle: **UNASSIGNED**; incoming session/observed capabilities: **UNKNOWN**. Canonical Oracle state, active epoch n, activated Cycle, exclusive writer lease and selected successor authority: **NOT ESTABLISHED** for this v0.4 project. No fabricated n→n+1, no asserted `ORACLE_CONTROL_TRANSFERRED`, no successor adoption, no score/merge.

Use the selected project native Issue and PRs as continuity state. The broader [Common 3DC AIM](https://github.com/reallakshman19/Common/blob/b4546c3f586b93dbe875ad6a531abc85f701c583/relay/AIM/3DC-XML-CII.yaml) covers O1/O2/O3 and selected O1; this v0.4 Issue #1 is an adjacent bounded O2-style performance task, **not an automatic revision of O1 or inherited worker roster**. A v0.4 project-specific Progress WBS page and canonical Cycle were **not located/verified** in this preparation; successor must read current Home/WBS if one exists and reconcile, not create a parallel roadmap.

## B. Live native parent → current → next map (checked 2026-11-06)

| Native identifier / relation | Candidate or returned evidence | Actor / receipt | Status / next |
| --- | --- | --- | --- |
| [v0.4 Issue #1](https://github.com/reallakshman19/3D_Converters_v0.4/issues/1) — **root** `XML-CII-V04-PREVIEW-PERF-A1` | Owner scope, exact-bm2 validation requirements | Owner native issue; local agent returns comments | OPEN, scope unchanged |
| [PR #2](https://github.com/reallakshman19/3D_Converters_v0.4/pull/2) — first slice | `a45ec1be5039462d345cccdda87e716b177c507e`, base main `b856ddd0...` | Implementer session ID UNKNOWN; [PR2 work report](https://github.com/reallakshman19/3D_Converters_v0.4/blob/a45ec1be5039462d345cccdda87e716b177c507e/agents/PR2_workreport.md) | DRAFT, UNMERGED, 25/25 native Node **local-agent-reported** |
| [PR #3](https://github.com/reallakshman19/3D_Converters_v0.4/pull/3) — depends on PR2 | `027c5e3234d3a88c43375228d9a37f3493490e8a`, base PR2 `a45ec1be...` | Implementer session ID UNKNOWN; [PR3 work report](https://github.com/reallakshman19/3D_Converters_v0.4/blob/027c5e3234d3a88c43375228d9a37f3493490e8a/agents/PR3_workreport.md) | DRAFT, UNMERGED, 34/34 native Node **local-agent-reported** |
| R3 GLRD parity validation — consumes both | [Issue #1 R3 receipt](https://github.com/reallakshman19/3D_Converters_v0.4/issues/1#issuecomment-6679670740), private ZIP digest `53309e54...` | Local Windows validation agent returned via issue; incumbent Oracle independently audited archive | **RETURNED, SCOPED ARTIFACT PARITY PASS**; candidate config only; benchmark defect unresolved |
| **R4 proposed** — consumes R3 findings | Correct real UI benchmark and checksum manifest, no production code change | Local test agent may be re-engaged; delivery/assignment **NOT YET SENT** | PLANNED, priority 1, not to be counted active |
| **R5 proposed** — consumes R4 & Owner fixture attestation | Exact-head conflict-free independent engineering-critical review | Reviewer identity and session **UNASSIGNED** | PENDING; no score or release |
| Owner-only decision — parallel gate | Fixture authority, material/pressure engineering follow-up boundaries, possible merge | Owner | OPEN; no approval presumed |

No other v0.4 issue or PR was returned by the GitHub repository issue/PR listing at preparation. A local validator's exact session/live progress was **not observed** after its receipt; do not cancel or redispatch blindly. **Author/return time, evidence read time and published knowledge time are different.**

## C. Pinned source/evidence custody

- Root `main` `b856ddd01a66c0dbee8c519bfd0bd8118d1f3979`; PR2 and PR3 exact SHAs above. Both PRs are draft, unmerged. No PR review submissions and no exact-head pull-request-triggered workflow runs were returned by the current connector query. This is **not a claim that other native local tests did not run**.
- Actual Owner GLRD engineering inputs (six files plus manifest) were hash-verified by local agent; incumbent rechecked the supplied input ZIP. Original bytes are **PRIVATE / NOT_TRANSFERRED through this public relay**. Recipient needs authorized Owner copy, not public GitHub.
- Candidate config: 8,750,897 bytes, SHA-256 `706fed5b35e7f5449b44bc3237ae0b62339c8f28593f46f800dcf2a2a78ed001`—`Linelist` Sheet 3, eight actual lines, 16 normalized rows, eight override dictionaries empty. **Never describe as verified historical in-session configuration**.
- R3 evidence ZIP: 3,113,211 bytes; SHA-256 `53309e54d3c79146bdc827cecdede635c0b38c690d62731a241d9d26d4a58f97`; 66 archive members, archive corruption check PASS. Private bytes were uploaded to the incumbent Oracle's conversation; no successor retrieval or hash-confirmed receipt yet.
- Independent artifact audit: nine 713,474-byte converter-input XMLs identical, nine diagnostics JSONs identical, four 703,548-byte Windows CRLF XMLs identical, eight 687,205-byte browser LF XMLs identical, four 997,859-byte CII files identical. Saved diagnostics on-disk hash `676dbe46...`, canonical sorted-key hash `1116cba4...`. 31 Preview branches, 268 node Preview rows, 6,176 authority comparisons/zero mismatches. Browser process provenance supported by scripts/output **but browser itself not rerun independently**.
- Production engine source and comparison examples are detailed in [architecture](ARCHITECTURE_COMPLEX_LOGIC.md). Formal CAESAR II vendor importer/solver or effective material stress correctness: **NOT_RUN / NOT_ACCEPTED**.

## D. Open blockers and their bounded scope

1. **R4 benchmark invalid:** direct-module probe misreads `preview.rows`, calls Rating with an array rather than an options object, uses nonexistent Weight Match count fields, omits staged JSON, and never clicks actual app UI. Zero-row / 0ms Rating figures are no-ops. The reported 13.575s→3.9715s cold compute delta remains indicative only; a complete UI acceptance claim is **NOT QUALIFIED**.
2. **One stale checksum:** 5/6 script digests match in `scripts/SHA256SUMS.txt`, corrected `utf-8-sig` runner not reflected in manifest. Repair evidence custody before any final IR.
3. **Owner fixture authority:** `glrd-candidate-step4-config.json` has correct Line List sheet, but design-versus-working source selection and empty override intent were not explicitly Owner-attested. A fixture-only approval is enough to qualify *parity on that fixture*, not material/pressure engineering acceptance.
4. **Separate engineering concerns:** 114 nodes on four branches have `MaterialNumber=0` (unresolved `DSS`/`LTCS`), and PSI intermediate `pascal` header conflicts with numeric kPa-derived data while CII uses `KPa`. Source design pressure 13001.3 appears as CII 13001.0 (rounding). Do not patch any of these inside performance PRs. Require separately scoped engineering-authority review if pursued.
5. **Independence/merge:** The incumbent Oracle contributed validator design. It cannot self-award independent implementation score. No score >=92/100 with >=17/20 each dimension, no Owner merge permission. Both PRs HOLD.

Do not globally block source analysis or script-only repair because Owner material-code decisions are pending. Respect the affected operation's real guard.

## E. Two connected next deliveries

**D1 (immediate, bounded, local test agent; proposed, not dispatched):** Repair only `scripts/benchmark_step4_interactions.py` and `scripts/SHA256SUMS.txt`, rerun true click-driven Step 4 Build/Rebuild/Fetch/Apply Rating/Weight Match and Run with full staged source and candidate config at three pinned heads. Verify 31 `branchRows`, meaningful node/rating/weight observations, clean/warm samples, exact configuration hashes, no stale state, performance measured with nonzero work. Retain raw old invalid benchmark and publish new receipt explicitly superseding old timing claims. Post actual evidence and counts to Issue #1. **Do not edit production, masters or PR code; no merge.**

**D2 (consumes D1 and Owner fixture attestation; future independent reviewer):** Source-first review exact PR2/PR3 diff and original code invariants, inspect full private evidence archive through authorized route, reproduce a selected original-model case, check valid benchmark and all declared authority rules; record separate score and decision. Owner alone approves merging and any real engineering changes. If R4 shows no net benefit or unsafe regression, park/rethink, no forced PASS.

## F. Single immediately executable continuity action

**Actor:** *incoming Oracle candidate, READ_ONLY* until explicitly appointed; if already appointed, stay within actual authority. **Source:** [Issue #1](https://github.com/reallakshman19/3D_Converters_v0.4/issues/1), pinned PR3 `027c5e32`, this archive digest, `benchmark_step4_interactions.py` in the private ZIP, and [Preview wrapper](https://github.com/reallakshman19/3D_Converters_v0.4/blob/027c5e3234d3a88c43375228d9a37f3493490e8a/tabs/xml-cii-2019-standalone/ui-adapted/xml-cii-adapted-preview-dryrun.js). **Action:** independently reconcile the three benchmark API mismatches and live root→PR2→PR3→R3→R4→R5 native map; produce a bounded correction brief/disposition using the *actual* script and code. **Expected observation:** `preview.branchRows.length=31` in Run diagnostics versus `previewRowCount=0` in original benchmark; classify zero time as no-op, not speed. **Native return:** a concise read-only reconciliation/correction report on Issue #1 (or Owner reply if issue write isn't authorized), explicitly labelled `NO_CODE_CHANGE / NO_IR_SCORE`. Then, only an authorized Oracle routes D1 to the local test agent. Re-check the issue for later returns before posting to avoid duplicate side effects.

## G. Pending-delivery and control ledger

| Item | Current status | Boundary |
| --- | --- | --- |
| Prior local R3 instructions and returns | **DELIVERED/RETURNED** via Issue #1 comments; local agent session ID unknown | Do not resend whole R3 assignment |
| R4 correction instructions | **PROPOSED / NOT_DISPATCHED**; no Owner-approved undelivered exact instruction independently established | Proposed text lives in D1 above; recipient/session locator UNKNOWN |
| Successor Oracle prompt | **PREPARED / NOT_DELIVERED**; successor UNASSIGNED | [ORACLE_SUCCESSOR_PROMPT.md](ORACLE_SUCCESSOR_PROMPT.md); do not call a published link receiver receipt |
| Private GLRD source and 3.1-MB evidence ZIP | **LOCAL_ONLY / NOT_TRANSFERRED** to successor | Actual authenticated transfer and receiver hash check required; no public raw-file release |
| Canonical Oracle state and epoch cutover | **UNKNOWN / NOT_ACTIVATED** | Owner/native control decision, selected successor, old-writer isolation, exact epoch/CAS readback and explicit assignment disposition required |

**Proposed state is not canonical control.** This packet makes knowledge retrievable; even if committed to Common and read back, it does not establish WBS adoption, independent engineering acceptance, recipient understanding or `ORACLE_CONTROL_TRANSFERRED`. On actual appointment, the incoming Oracle checks native WBS/Page and activated Cycle if available, resolves source contradictions within its authority and records precisely what ongoing work it adopts.

## H. First-source-walkthrough for receiving Oracle (not an exam)

Use [Common Initial Mentoring](https://github.com/reallakshman19/Common/blob/b4546c3f586b93dbe875ad6a531abc85f701c583/skills/agent-work/initial-mentoring/SKILL.md): explain in source-grounded prose (a) why localStorage alone is not a complete effective Step 4 config, (b) how a 31-branch Preview can coexist with a zero-row benchmark and what the wrong signature is, and (c) why byte-identical CII still doesn't authorize code-338 material reassignment. Return one real source correction or native observation, not a ceremonial acceptance or score.
