# RECON 3/4 — Product flow and AC coverage (retrospective synthesis)

Date: 2026-10-11 Asia/Muscat. Status symbols: I=IMPLEMENTED in code; C=CONNECTED within tested read-only seam; P=PROVEN for stated test scope only; H=HOLD for full Owner acceptance. A single suite proving synthetic code behavior cannot lift Owner AC.

## Current flow
Owner historical WHAT/WHY (#5/#289/#325; original auth OPEN) → original released graph (real current Owner release OPEN) → T01 `generic_source_preflight` checks repository/leaf/PR/head + double provider GET (I/C/P synthetic) → T02 `generic_current_source` checks pinned graph raw bytes vs default-branch twice; reads native comment ledger/PR observations, calls unchanged `delp.project` and source-bound core (I/C/P synthetic; full-PR identity incompatible in frozen native) → T03 `generic_publication_plan` plans native DELP issue title/status, managed issue bodies and guarded PR metadata separately; checks whole-body digests/idempotence and classifies partial readback (I/C/P synthetic; zero writes) → real trusted Owner/CI/checkpoint admission OPEN → live publisher default OFF → C6 source reconstruction exists separately, automatic Agent B handoff unqualified.

## AC1–AC8 current reconciliation (Owner acceptance is AC0/8)
| AC | Requirement | Implemented | Connected | Proven | Release result |
|---|---|---|---|---|---|
| AC1 | Authentic Owner intent and amendments | Historical requirement preserved in current issue/graph files | Parent #5, gate #289 and child #325 linked textually | Requirement existence only; no original private receipt | HOLD |
| AC2 | Claim-first decomposition / source released graph | Native graph validation/decomposition; T01 binding | T01 graph/leaf/PR and T02 pinned branch graph | Synthetic graph rebinding; no new Owner-approved graph | HOLD |
| AC3 | Owner→session→module/commit/PR/evidence lineage | Exact GitHub PR/head captures, native core/custody | #326 file/source-to-PR mapping | Named code/commit evidence only; no complete bidirectional real session | HOLD |
| AC4 | START/END/RECOVERY facts + real required CI/review | Native ledger/fact validation; T02 reads native facts | T02 fake comments and native DELP; stale/foreign refusal | 34-case suite/3 Python; no authenticated positive checkpoint / reviewer | HOLD |
| AC5 | One native DELP snapshot | `delp.project`, `source_bound_responsibility_core`; no second engine | T01/T02/T03 consume same native APIs/digests | Read-only synthetic equality, not accepted positive E | HOLD |
| AC6 | Live issues/PR titles, LIVE_STATUS, blocks; preserved Owner prose | Native publisher/managed block functions; T03 pure plan | T03 disjoint surfaces, idempotence/partial readback | No GitHub PATCH/POST/readback, writer OFF; no atomic cross-surface CAS | HOLD |
| AC7 | Finding→source→Owner decision→claim/code/evidence | Code provenance and issue updates present | T03 no-progress-authority contract | No authentic Owner accept/reject event through production pipeline | HOLD |
| AC8 | Four cold contexts, independent successor | Native source-bound C6 and custody primitives separately exist | Not wired to independent Agent B with lease transfer | No isolated no-chat B or old-A revocation/new-B writer test | HOLD |

## Inputs and acceptance oracles
- Included: current checked-in 718 Proposal-V2 JSON **historical** and re-bound `example/Pipeline` synthetic graph; fake provider issue title/body, PR head/base, comments and current graph bytes; native V3.2 functions; three Python versions; single test workflow source AST scan.
- Negative cases: foreign repo/PR, stale or changing head, changed issue bodies/default-branch blob/native comment ledger, duplicate JSON keys/nonfinite values, native full `owner/repo#PR` HOLD, changed human title/body managed markers, forged native DELP input/progress, partial/racy readback, missing/stale LIVE_STATUS.
- Missing real inputs: authenticated original Owner receipt, current approved graph & revision for new repo, authorized GET credentials to private lab, genuine material change and required CI statuses, accepted `CHECKPOINT_FACTS_V1`, separate reviewers, production writer grant, verified cold successor outputs.

## Contradictions to carry, not silently resolve
- Old `reallaksh19/Common` graph != new `reallakshman19/Common` owner release.
- Green focused #326 matrix != all checks passing (#326 inherited V3.1 failure); separately passing #327 != #326 passing.
- `C6_CURRENT_READ_ONLY`/source-bound reconstruction != independent writer/Agent B takeover.
- In-memory matching managed blocks != committed, provider-confirmed, authorized REST writes.
- Source-current on injected GET facade != authenticated Owner source and evidence/CI trust.
- `SIMPLIFIED=ON` != actual V3.2 runtime production switch; active Local stack nests V3.5.

Result: DEV_READ_ONLY_USABLE; V3.2_PRODUCTION_HOLD; AUTO_AGENT_B_HOLD.
