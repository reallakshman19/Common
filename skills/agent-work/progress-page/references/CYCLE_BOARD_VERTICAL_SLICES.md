# Cycle Board — downstream vertical-slice execution contracts (draft v0)

**Purpose:** hand an independent downstream agent four bounded, reviewable delivery slices. **AIM:** *reuse current Cycle/native/Page evidence with less total work, and deliver a runnable Owner-facing result first*. Companion interface: [source-bound contract](CYCLE_BOARD_CONTRACT.md). This is a delivery plan **within the existing selected project WBS**, not a second governing WBS or a compulsory four-stage journey for every agent.

## 0. Execution entry and custody

**Downstream agent reads in order:** actual Owner/Oracle assignment and task issue → [START_HERE](../../START_HERE.md) → selected native mode and current WBS/Page task → [contract](CYCLE_BOARD_CONTRACT.md) → the **one selected slice below**. Do not infer that receiving this file assigns the agent a role, chat identity, Cycle or write access.

**Owner / coordinator** owns scope, source and acceptance; **Coder** implements the selected authorized slice; **IR** independently challenges exact evidence; **Page writer** alone proposes/publishes audited Page changes under existing [MODES](MODES.md). The downstream agent must keep one task per slice and obtain any protected engineering/Cycle/Page authority through its ordinary protocol. If the assigned repository or source/candidate differs, re-ground the affected facts and report the discrepancy; do not silently change scope.

**Repository sequencing:** implement/viewer-test production in `reallakshman19/progress-page` first; after reviewed result, bring the portable assets into `reallakshman19/Common/skills/agent-work/progress-page/`, preserving blob parity and relevant local/offline/browser tests. Common is the portable skill copy, not an automatic publisher. No unapproved merges.

**Source snapshots to revalidate** (observed 2026-10-29; not live task claims):
- Common base `05672bacc8933dd714c51dc8ebd823635aa73bad`; current portable `viewer/timeline-live.js` supplies v2 Action/Info and `INFO_AUTO`; `scripts/pp_watch_job.py` supplies scoped read-only preflight/reconciliation.
- [CIIFR-Node Page](https://reallakshman19.github.io/progress-page/#/ciifr-node/progress): published R1, WBS 2/P1.0 based on [PR226](https://github.com/reallakshman19/XML_Compare_Utilities/pull/226), WBS 2.1/P1.1 review. [Issue231](https://github.com/reallakshman19/XML_Compare_Utilities/issues/231) and dependent [draft PR232](https://github.com/reallakshman19/XML_Compare_Utilities/pull/232) at `7f5dc773ac7bb08544d086be734e4337295088a0` record a newer **SELF_ASSESSED** repair and fresh non-author review pending in [#228](https://github.com/reallakshman19/XML_Compare_Utilities/issues/228), **GATE_R0 HOLD**. There is no `oracle-cycles/ciifr-node/CURRENT.json`; Cycle authority remains **UNMAPPED**. This is a native/Page drift case, not a reason to activate a Cycle.
- [CIIFR](https://reallakshman19.github.io/progress-page/#/ciifr/home): standalone canonical [CURRENT.json](https://github.com/reallakshman19/Common/blob/main/oracle-cycles/ciifr/CURRENT.json) was ACTIVE at revision 20, Owner trial/acceptance next at inspection. Existing [PR185](https://github.com/reallakshman19/XML_Compare_Utilities/pull/185) and [IR return](https://github.com/reallakshman19/XML_Compare_Utilities/issues/186#issuecomment-6425272554) provide source-limited historical replay; GPU and Owner acceptance were not established by that return. **No new Coder/IR dispatch**.
- [Grade9v3.5](https://reallakshman19.github.io/progress-page/#/g9v35/home): Page project `g9v35` uses OTM mode. Read live native/Owner evidence from its actual task before claiming progress; no standalone Cycle is selected by the Board.

## 1. The four bounded vertical slices

| Slice | Outcome the Owner can use | Inputs / depends on | Produced artifacts | Mandatory independent boundary |
|---|---|---|---|---|
| **CT-1 · Current context** | Open a project URL showing source-bound current WBS, original evidence, prior Page audit, possible Cycle and one next evidence-linked cue | Existing Page viewer, native task/PR, optional canonical Cycle; [context schema](CYCLE_BOARD_CONTRACT.md#3-shared-read-model-interface-cycle-boardcontextv1) | Pure context constructor + minimal UI + focused source fixtures/test | Read-only: unknown if unobserved; no new comment/assignment |
| **CT-2 · Delta/continuation** | Same URL distinguishes unchanged/changed, wrong recipient, already returned, stale Page and UNKNOWN, without re-onboarding | CT-1 DTO; selected protocol + exact current candidate/receipt where Cycle active | Pure delta classifier + decision table + adversarial unit cases | `CONTINUE_AUTHORIZED` only with actual canonical authority; native-only observation never dispatches |
| **CT-3 · Reviewed reconciliation** | Designated writer can inspect the exact source/identity, generate one *review-required* Page proposal and see its audit linkage later | CT-2 source identities and evidence; existing CLI, dry-run and checker | Proposal/trace preview (not auto apply) + dedup replay test | Protected Page write only through existing authority/PR; no automatic acceptance |
| **CT-4 · Falsification and effort pilot** | Owner tries one runnable URL; independent falsifier verifies negative cases; total active role effort is measured against baseline | Integrated CT-1–CT-3 read-only behavior and one real authorized workflow, or historical replay marked as replay | Exact-head test report, replay fixtures, active-minutes worksheet, Owner trial/NOT_RUN, portability/parity report | No claim of saved time or accepted production until measurements; no synthetic PASS |

**Verticality rule:** each slice must end with a runnable command/test and an inspectable user-facing output, not just a schema/diagram. Later slices consume the *same* source context and identifiers; they may add fields but must not reinterpret earlier observed evidence. A failing predecessor means next dependent work is **BLOCKED**, not silently reimplemented.

### CT-1 agent contract — source-bound context, not more posts

**Single responsibility:** in a source-configured project, combine existing Page WBS/AIM, last audited entries, native task/PR/receipt pointers and optional explicitly bound canonical Cycle into `cycle-board.context/v1` with provenance; render a minimal Cycle Board view without depending on `Common#564` comments.

**Inputs:** exact project key, governing Page WBS/selected task locator, public source URL(s), existing Page data; optional selected standalone Cycle locator. An unconfigured source is `NOT_CONFIGURED/UNKNOWN` and cannot erase valid `INFO_AUTO` Page history.

**Output:** pure deterministic adapter + one project URL/view + source link(s) and source-observed-at label. Reuse existing Smart Badge IDs and current `INFO_AUTO`; do not require new full chat ID registration or extra Page form.

**Acceptance:** 1) CIIFR-Node sources remain visible with Cycle UNMAPPED; 2) a working clickable URL shows native and prior audited evidence separately; 3) repeat read produces identical source occurrence IDs; 4) no production mutation; 5) actual browser/viewer tests and offline bootstrap coverage; 6) Owner can distinguish source revision from render refresh time. **Reject:** a screenshot-only deliverable, a fake WBS link, a forced Cycle, or a manual `CYCLE_TIMELINE_CARD` report prerequisite.

**Handoff CT-1 → CT-2:** DTO field/schema version, exact observed source/event IDs, configured project/WBS, source fixture links and tested viewer URL; explicit UNKNOWN fields and test outputs. No narrative duplicate work report.

### CT-2 agent contract — cheap on-demand delta preflight

**Single responsibility:** compare current native/selected Cycle/receipt/Page source against **last successfully observed comparable** context; only revalidate changed or consequential original facts, with fail-closed rules. Do not require a scheduled watcher for correctness.

**Inputs:** CT-1 context + prior verified context (if any), current native refs, live canonical `CURRENT.json` *only if selected/bound*, optional `pp_cli cycle-preflight` on consequential scoped transitions. Missing prior baseline is **UNKNOWN**, not 'unchanged'.

**Output:** independent axes `native/page/cycle/return/evidence`, one of the advisory `next.advice` values from the contract, source comparison/contradictions and original-source links. No new global workflow stage or task assignment.

**Acceptance cases:** same valid assignment/candidate/receipt → only changed facts reviewed; changed candidate or HOLD → requalification; wrong recipient → NO_ACTION; already returned but unreconciled → AWAIT_ORACLE_RECONCILIATION without another native/accepted receipt; missing mandatory Cycle receipt → repair its existing routing envelope, not redo native work; missing/stale evidence → UNKNOWN_STOP; Page behind source → REVIEW_PAGE_DRIFT. **CIIFR-Node:** published WBS2 source PR226 vs newer issue231/PR232 yields `STALE_PAGE` or `REVIEW_PAGE_DRIFT` (subject to exact inspection), independent IR remains HOLD, Cycle `UNMAPPED`, no WBS advance or assignment. **Reject:** relying solely on role label/id8, a prior HEAD, or a Board status for canonical authority.

**Handoff CT-2 → CT-3:** stable native occurrence IDs; classification and contradiction codes; exact URL/SHA/reviewer limits; source-to-WBS mapping; Page audit events already correlated; no conflation of `PAGE_AUDIT.ACTION` and operational `CYCLE_BOARD.ACTION`.

### CT-3 agent contract — existing writer route, not a second publisher

**Single responsibility:** give the designated writer a source-scoped suggestion with `PENDING`/reconciliation health; use the **existing** reviewed Page tooling. No automatic `--apply`, audit edit, acceptance or Cycle write.

**Inputs:** CT-2 `REVIEW_PAGE_DRIFT` result, actual original task/PR/review, existing WBS revision and audit, existing `pp_cli propose` + `pp_batch` dry-run/check commands. A candidate link does not prove claims without inspection.

**Output:** reviewable manifest and source→Page reconciliation trace, preserving original source occurrence identity (separate from Page audit ID) and prior audit links. Actual Page update is permitted only when separately authorized; otherwise display `PROGRESS_UPDATE_PENDING`.

**Acceptance:** repeat observation/proposal yields no additional engineering achievement and no spurious second audit event; a source already published is `ALREADY_RECONCILED` only on exact supported linkage; ambiguous correlation = `REVIEW_REQUIRED`; append-only checker and protected Page review govern actual publication. **CIIFR-Node:** a proposal may describe the newer self-assessed repair and pending independent review, never mark WBS2/2.1 verified or change project scope. **Reject:** auto-merge, edited `audit.json`, automatic `cycle` binding, invented fixture receipt or Owner approval.

**Handoff CT-3 → CT-4:** source-linked proposal preview or reviewed PR URL, dry-run output/check results, audit correlation keys, outstanding NOT_RUN/HOLD; no assertion that a PR draft is published.

### CT-4 agent contract — falsify the whole claim and measure value

**Single responsibility:** independently test exact-source behavior, measure baseline vs pilot total effort and show the Owner a working result.

**Minimum matrix:**

| Project/case | Falsifying expectation |
|---|---|
| CIIFR-Node PR226→issue231→PR232 `7f5dc773` | Detect newer self-assessed P1.0 repair, retained P1.1 fresh-IR HOLD, stale Page R1 link; no standalone Cycle or independent PASS inferred |
| CIIFR activated Cycle | Wrong id/generation/recipient/candidate or already-returned state fails closed; prior IR scoped PASS cannot become GPU or Owner PASS; no fresh Coder dispatch |
| Grade9v3.5 OTM | Context and WBS remain usable without any standalone Cycle; no OTM→Oracle authority transfer or duplicate WBS |
| Missing or conflicting source | UNKNOWN with actual failure, not empty/healthy or invented Source/GitHub timestamp |
| Duplicate PR/head/comment and Page audit | Stable occurrence across Board/Agent Start/Oracle; audit publication is a separate *record*, not new engineering completion |
| Handoff race | INFO with old `actionRef`, wrong WBS/card or unsourced IR acknowledgment cannot close a newer Action; independent technical Action stays open |
| Privacy and portable parity | No public full chat ID, private link, token or restricted bytes; pinned source/portable tests and exact asset parity where applicable |
| One actual authorized native workflow | Native work + selected required Cycle receipt only; Board shows current next/evidence; Owner opens URL and tries result; record NOT_RUN if no authorized live pilot |

**Effort measurement:** compare **active minutes** for Coder, IR, Oracle/OTM, Owner, Page writer and maintenance; exclude idle/Owner-wait. Record time-to-first-runnable, number of additional mandatory reports (=0), continuation-recovery minutes, duplicate-source handling and operational/CI cost. Use `T_total(N)=sum(role active minutes)+maintenance per run+build/setup/N` with explicit N. One pilot supports *feasibility*, not an unmeasured system-wide savings claim. Preserve baseline and unavailable observations as UNKNOWN/NOT_RUN; independent challenges must cover seeded stale head, absent receipt, false technical PASS and private-data leakage.

**Handoff CT-4 → Owner:** actual runnable URL, source/head pin, tests and contrary cases, measured role effort and limitations, open HOLD/NOT_RUN, whether Page was *actually* published, and one decision recommendation. No automatic release or merge.

## 2. Mapping of original G0 packages to the four slices

| G0 item | Decision | Where it lives |
|---|---|---|
| P0 · WBS reconciliation preflight | KEEP, on consequential scoped transitions | CT-2, with existing `cycle-preflight` and native source checks |
| P1 · Decomposer → Page adapter | DEFER full automation | CT-3 uses existing Decomposer/Oracle judgment and Page writer proposal only if WBS meaning changes |
| P2 · Agent Start completeness | KEEP/reuse | CT-1 DTO consumed by existing exact task/WBS Agent Start; CT-2 supplies changed-only context |
| P3 · Oracle continuity | KEEP | CT-1/CT-2 latest unresolved WBS frontier and receipts; no routine full onboarding |
| P4 · Drift detection | SPLIT | CT-2 on-demand first; optional existing watcher after demonstrated value |
| P5 · Regression | KEEP | CT-4; focused tests must accompany each earlier slice |

## 3. Original 12-gap traceability

| Original gap | Closure slice | Delivery rule |
|---|---|---|
| #1 Entry discovery | CT-1 | Minimal links in START_HERE/SKILL; selected modes unchanged |
| #2 Dual Timeline meaning | CT-1 | Board operational context vs append-only published audit |
| #3 Native activity capture | CT-1+CT-2 | Existing sources, no mandatory `CYCLE_TIMELINE_CARD` post |
| #4 Assignment authority | CT-2 | Canonical checks before any continuation advice |
| #5 Handoff lifecycle | CT-2+CT-4 | Evidence-bound link and stale handoff falsifier |
| #6 Agent identities | CT-1+CT-2 | Actual ID8/alias where known; full private IDs do not enter public snapshots; UNKNOWN otherwise |
| #7 WBS reconciliation | CT-2+CT-3 | One governing WBS, reviewed source mapping |
| #8 Cross-view continuity | CT-1+CT-2 | Same DTO/occurrences in Agent Start/Oracle, no second task packet |
| #9 Owner visibility | CT-1+CT-2 | Distinguish actual requested decision from warning/unknown |
| #10 Cross-source dedup | CT-1+CT-3 | Stable occurrence and separately linked audit ID |
| #11 Multi-project support | CT-1+CT-4 | Source configured per project; CIIFR-Node/OTM no Cycle inference |
| #12 Interactive Test Lab | DEFER | Optional later isolated scenarios; **not a prerequisite** to an Owner-usable real-evidence pilot |

Traceability means a **contracted test**, not a claim of PASS. The first runnable slice only implements sufficient coverage for its selected project; broader support follows verified usefulness and effort savings.

## 4. Downstream handoff discipline and stopping rules

Every downstream PR/task packet must declare: **AIM**, exact **CT slice**, actual **governing project WBS**, selected coordination/native protocol, role and recipient, source URL + exact candidate/head, read-model schema version, touched modules, explicitly out-of-scope writes, one runnable command/URL, measured active effort, tests and known contrary case, **NOT_RUN/UNKNOWN**, and one next handoff. This document is never evidence that an assignment was made. The authorized coordinator supplies the packet; the contractor executes only it.

Do **not** start CT-3 publication work on an unverified CT-2 source correlation, do not treat CT-4 replay as a live role assignment, and do not expand to scheduled monitoring or Test Lab solely because it is technically possible. If no actual Owner trial or effort baseline is available, mark outcome measurement NOT_RUN/UNKNOWN and do not declare the AIM achieved.
