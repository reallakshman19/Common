# Cycle Board Protocols — source-bound onboarding, continuation and Page reconciliation

**Type:** operational companion / index, **not** a new governing protocol, project WBS, Cycle activation or acceptance rule.  
**Status:** Operational companion merged through [Common PR #573](https://github.com/reallakshman19/Common/pull/573); this revision clarifies existing-agent continuation and the already-shipped CIIFR UI reuse. Linked live status still requires fresh verification.  
**Grounding:** [START_HERE pinned at Common main 999dd8d](https://github.com/reallakshman19/Common/blob/999dd8d1516af6a65a840d9f3f489b5f0115d261/skills/agent-work/START_HERE.md) · [START_HERE (current branch)](../../START_HERE.md) · [Cycle Board read-model contract](CYCLE_BOARD_CONTRACT.md) · [CT-1–CT-4 implementation slices](CYCLE_BOARD_VERTICAL_SLICES.md).

The Cycle Board is a **read-only, source-driven operational context and changed-only navigation layer**. It helps the Owner, Oracle, agents, independent reviewers and Page writer resume the *existing* workflow with minimal repeated reconstruction. The native issue, source bytes, Common relay, selected actual Oracle Cycle if any, governing Progress Page WBS and append-only audit retain their own authority.

> **One action, evidence once, reuse everywhere. No new mandatory Board report.**

## 1. "Cycle now" is the Owner's short continuation command — use the Cycle Board

The Owner can say **"Cycle now" in an existing Oracle or agent conversation**. Do **not** reflexively respond with fresh onboarding instructions, an invitation for the Owner to create two conversations, or a dry list of source URLs. Continue the *already established* project/task, check what changed, and do the assigned bounded work.

**Important two meanings (same words, different authority):**

| Context of "Cycle now" | What the recipient actually does | What the phrase **never** authorizes |
|---|---|---|
| **Established Oracle / agent with an existing native task, without selected active canonical Cycle** (current TOPO-A/B case) | Treat as an **informal, native-task continuation instruction**. Reuse previous grounding; open the relevant *Cycle Board as the operational start*, then inspect underlying native issue and consequential changes, reconcile return and propose/perform only what existing authority permits. | It does **not** turn the noncanonical task into an activated GitHub Oracle Cycle, assign a different task, verify private source custody, grant writer lease or technical PASS. |
| **Recipient of a selected and active canonical standalone Cycle** | Apply the unchanged [GitHub Oracle Cycle protocol](../../../../oracle-cycles/PROTOCOL.md): reread actual `CURRENT.json` on main and check activation, assignment ID/generation, recipient, scope, candidate, holds and receipts **before execution**. Board is supplementary context, never authority. | No implied authority from a Board URL, message, old assignment or agent nickname. |
| **Truly new/unbound participant or changed material assignment** | First source-grounded OnBoard: actual recipient, governing WBS, selected mode, native task, original input/fixture access, one falsifier and boundaries. | A prepared issue, chat created or Board card does not prove SENT / ACK / source-byte receipt. |
| **"Cycle Board refresh" specifically requested** | Perform a read-only source/Page and native occurrence recheck and report **delta**, not a new dispatch. | Refresh alone is not the full Oracle coordination loop and not a substitute for "Cycle now" when the Owner wants work continued. |

These instructions describe **how an established human-language conversation continues a native task**. They do **not** redefine the canonical invocation defined in `oracle-cycles/PROTOCOL.md`. Where no canonical ACTIVE Cycle was selected, label the mode **NATIVE_CONTINUATION / CANONICAL_CYCLE_UNMAPPED**; do not call its execution an `ORACLE-CYCLE-RECEIPT` run.

### Copy-ready Owner → existing TopoFix Oracle (current trial)

> **Cycle now — TOPO-A / TOPO-B; native coordination, no canonical Cycle activation.** Open and actually read the [TOPO-A Cycle Board](https://reallakshman19.github.io/progress-page/#/adhoc/topo-a/cycle-board) and [TOPO-B Cycle Board](https://reallakshman19.github.io/progress-page/#/adhoc/topo-b/cycle-board) **first**. Read AIM, WBS, existing INFO-Auto/Smart Badges, concept/architecture and fixtures, recorded next actions, live native source occurrence/delta and Page reconciliation. Then verify issues [#12](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/issues/12) and [#239](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239) and the agents' most recent actual returns. **Coordinate the existing agents, not the Owner**: give each one delta-only native-task continuation when already assigned, or one read-only grounding action when genuinely unbound. Preserve HOLDs; no duplicated onboarding, task, WBS, Page entry or report. Return what was actually observed on **each Board**, one status/next action per agent, blockers and any genuine Page drift. Do not merely tell the Owner to start agents.

### Copy-ready Oracle → established agents, or Owner in existing agent conversations

- **Agent 1, TOPO-A:** "**Cycle now — TOPO-A, continue your existing native [issue #12](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/issues/12) assignment.** First read the [TOPO-A Cycle Board](https://reallakshman19.github.io/progress-page/#/adhoc/topo-a/cycle-board) and its original WBS / INFO-Auto / CLOS source. Compare actual head/fixture/permissions and previous return; continue only one still-authorized read-only source trace or report AWAIT_ORACLE_RECONCILIATION. No XML edit or new Cycle activation."
- **Agent 2, TOPO-B:** "**Cycle now — TOPO-B, continue your existing native [issue #239](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239) assignment.** First read the [TOPO-B Cycle Board](https://reallakshman19.github.io/progress-page/#/adhoc/topo-b/cycle-board) and original WBS / INFO-Auto / format and fixture concept. Compare actual head/fixture/permissions and previous return; continue only one still-authorized read-only element-to-graph trace or report AWAIT_ORACLE_RECONCILIATION. No writer edit or new Cycle activation."

**If actual recipient identity, task selection or initial source grounding remains genuinely unverified**, the Oracle resolves only that missing gate. A message cannot verify who read it. The agent returns once in the **existing native issue and approved relay**, not a new `CYCLE_TIMELINE_CARD` or Page-only receipt. The Board reads the original records; no requirement to post a duplicate Board report.

## 2. End-to-end workflow — operational procedure

1. **Owner / Oracle grounding:** First read [START_HERE](../../START_HERE.md), actual Owner decisions, project concept and architecture, **one governing WBS**, current original inputs, exact source candidate and active HOLDs. For a genuinely new Oracle, use [initial mentoring](../../initial-mentoring/SKILL.md) and the [Oracle standalone protocol](../../oracle-standalone/SKILL.md); a prepared handover does not establish an exclusive control epoch.
2. **Observe, don't infer — actually use the Board before coordinating:** Open the project Board/Adhoc view and check exact native issue/PR source occurrences, observations and failures; **UNKNOWN** on first read with no comparable prior successful observation. Recheck source; `UNCHANGED` means the *configured* immutable occurrences match, not that all possible sources or engineering are done.
3. **Pick an existing task:** The Oracle names actual WBS step and native task issue. Resolve intended recipient identity, role, selected coordination/native engineering protocol, exact baseline/head, source/relay locator, current writer collisions and one return destination. **PREPARED → SENT → ACKNOWLEDGED → BYTES_VERIFIED** are distinct, never inferred from a prompt or Board.
4. **Agent read-only first:** Inspect original source (or explicitly NOT_RUN), one source-to-behavior rule, necessary concept map/architecture, fixture custody, wrong case, code reuse and protected edit surfaces. A private relay pointer and producer SHA do not constitute recipient byte receipt.
5. **One native evidence return:** The agent records actual attempted actions, findings, source/head identities, independently verifiable paths, test evidence, limits/UNKNOWN and **ONE proposed next safe step** in the owning issue or selected native receipt. No second Board report.
6. **Oracle reconciliation (not Owner handoff):** The Oracle inspects the Board and native returns directly, then compares source occurrence/generation/identity with the preceding view; preserve earlier valid evidence; reconcile newly observed changes, contradictory case, prior return, ownership and HOLD. Independent IR/Owner verdicts remain separate from author tests.
7. **Progress Page reconciliation (only when justified):** The authorized Oracle/OTM/Page writer checks existing Page WBS/fixtures/audit, then uses existing `pp_cli.py propose`, `pp_batch.py` dry-run, checker and reviewed data PR for eligible changes. **No automatic `--apply`** from the Board. A merged Page change is a *publication event*, never a technical PASS.
8. **Continue or stop:** Give one bounded next action to the correct actor, or `NO_ACTION`, `AWAIT_ORACLE_RECONCILIATION` or `UNKNOWN_STOP`. Preserve actual canonical Cycle receipts only if that mode was selected and activated.

This workflow is the read-only projection of [entry maps A–E](../../ENTRY_PROCESS_MAPS.md), [artifact relay custody](../../ARTIFACT_RELAY.md) and [Project Home/fixtures](../../PROJECT_HOME_GUIDE.md). It **does not** replace them.

## 3. Minimum Board display / source and authority contract

Show the original Owner aim/WBS link, current native task, exact source identity, last successful source observation, changed/unchanged/unknown delta, current agent/Oracle continuity, original concept/architecture and fixture pointers, existing Page audit correlation, blockers and **ONE next actor**. Use expandable evidence rather than a proliferation of duplicated cards.

**Keep these axes independent:**

| Axis | Examples / required fail-closed status |
|---|---|
| Native source | Immutable PR-head SHA or issue revision; `COMPLETE / PARTIAL / UNKNOWN` coverage of **explicitly configured** sources. A link, page load or 403 is not a successful observation. |
| Canonical Cycle | `AUTHORIZED` requires actually active canonical role/assignment/generation/task/hold checks. Otherwise `UNMAPPED / INACTIVE / UNKNOWN` and **no** authorization. |
| Agent and Oracle custody | PREPARED, actual sent/acknowledged status, original-file source access/hash, current incumbent writer and handover epoch; unverified = **NOT_VERIFIED**, not FAIL attributed to an agent. |
| Independent engineering qualification | Author tests and CI are `SELF_ASSESSED`; separate independent original-source review and Owner engineering intent required. `HOLD` survives a successful browser test. |
| Page reconciliation | Actual `data/<project>/audit.json` source occurrences and governing WBS, current/stale/conflict/unknown; draft PR is not publication and merge is not engineering acceptance. |

**Evidence rules:** Reuse exact source occurrence identity across Cycle Board, Agent Start, Oracle continuity, Smart Badges and Page proposals; never match an audited native event by mutable PR URL alone. Preserve private chat/full IDs, restricted XML and tokens outside public pages, issues and Common. The Board cannot infer hidden files, owner decisions, page coverage or fresh source ingestion from UI counts. No new mandatory schema or schedule.

### UI reuse and parity are part of the Cycle Board protocol — don't rebuild the context

The operational view starts with **what/why/which WBS/one next action**, not a tall flat list of GitHub SHA observations. Keep **INFO-Auto and current WBS task cards primary**, with raw immutable occurrences, SHAs and timestamps in an **expandable source-provenance section**. A source list by itself is an incomplete Cycle Board.

**Reuse these shipped Progress Page implementations and actual data, not new parallel widgets or status ledgers:**

1. **[Page PR #70](https://github.com/reallakshman19/progress-page/pull/70)**, merged as `5f138cd6f279d21ed0f51ce24d2ff026ae77a9df`: shared CT-1–CT-3 read-model/native-source observation, safe delta, reviewed writer proposal in `cycle-board-context.js`, `cycle-board-delta.js`, `cycle-board-writer.js`, `timeline-live.js` and `app.js`. No automatic publisher/dispatch.
2. **[Page PR #63](https://github.com/reallakshman19/progress-page/pull/63)**, merged as `b6805537c3b179f861d5f5ec138ef3fcc26c4c3a`: source-grounded **Smart Badge IDs** shared across Timeline/INFO-Auto, Agent Start, Oracle Continuity and writer. Retain AIM, WBS, ROADMAP, PLAN, FIXTURE and ORACLE_CONTINUITY IDs with source/UNKNOWN, rather than generating new uncorrelated tags.
3. **`timeline-live.js`** reuses actual published Page audits: `autoGeneratedTimelineCards(project)` constructs one latest source-backed INFO-Auto observation per existing WBS card/milestone; `renderAutoGeneratedInfo(...)` presents WBS-grouped task/evidence cards; `autoGeneratedPageBrief(info)` supplies **Copy grounding / Page brief**; Smart Badges preserve original identifiers, sources and the "recorded next step may be stale" warning. **A Page actor/INFO-Auto entry is not an agent interaction, new assignment, technical PASS or approval.**
4. **[Page PR #99](https://github.com/reallakshman19/progress-page/pull/99)**, merged as `2be8d70ed3e3afdc31a62ba38d753777aece9b86`: source-bound TOPO-A/B concept, architecture, discriminating original case and fixtures. **[Page PR #100](https://github.com/reallakshman19/progress-page/pull/100)**, merged and deployed as `f4d33345b71d9c693fb62700a29d0dca1b5f6d5b`: **reused the above CIIFR INFO-Auto renderer and existing published TopoFix Page WBS** in both Adhoc Boards, with exact source provenance collapsed and original task links maintained.

### CT-5 — existing-agent continuation and acknowledgement boundary (shared across projects)

[Progress Page PR #101](https://github.com/reallakshman19/progress-page/pull/101), merged as `bac64e7e55a7301c84f1235695cba5b9d0583399`, deployed the [bounded CT-5 implementation and test contract](https://github.com/reallakshman19/progress-page/blob/main/docs/CYCLE_BOARD_CT5_AGENT_CONTINUATION.md). **Reuse the original Agent Start task, Oracle Continuity source context, Smart Badge identities, native issue and published WBS**, rather than creating a second task record. The shared `cycle-board-continuation.js` appears on existing project Cycle Boards and TOPO-A/B Adhoc Boards. It presents `Copy Cycle now · not sent` and, **only with a browser-private `My links` shortcut**, `Resume Agent · open existing conversation (not sent)`.

**Delivery, ACK and return are separate evidence gates.** `PREPARED` task, native GitHub instruction post, clicked/copy action or private conversation URL are **not** proof of message delivery or intended-agent acknowledgment. CT-5 therefore displays `NOT_VERIFIED`; a source-linked Page return is **a return pointer only**, not accepted technical/Oracle reconciliation. A returned/completed task or one whose next actor is Owner/reviewer yields **reconciliation-only instructions**; historical or archived projects must not resume work. Verify true ACK through the actual existing recipient conversation or an authorized authenticated transport, then original source-bound native return; never self-promote an ACK from the Board. **No automatic send, no new reporting duty, WBS, canonical Cycle activation, source-byte authority, engineering edit or Page publication.** The remaining real delivery/ACK trial is **NOT_VERIFIED**, regardless of green unit/Chromium checks.

**Acceptance falsifier:** If an Oracle says "open read-only onboarding instructions" after being asked "Cycle now" but has **not inspected the actual Boards, WBS/INFO-Auto current context, native changes and existing agent returns**, the coordination trial is **NOT_DEMONSTRATED**, regardless of a green UI test. For an inaccessible Board, report `BOARD_NOT_READ / UNKNOWN` and inspect original linked sources; do not invent success. The Owner should not need to manually marshal a second onboarding cycle for existing agents.


## 4. Two live Adhoc test workspaces (31 October 2026 baseline)

| | **TOPO-A — Assisted Connection Repair** | **TOPO-B — Universal XML Topology Adapter** |
|---|---|---|
| Adhoc Overview | [TOPO-A](https://reallakshman19.github.io/progress-page/#/adhoc/topo-a/overview) | [TOPO-B](https://reallakshman19.github.io/progress-page/#/adhoc/topo-b/overview) |
| Cycle Board | [TOPO-A Board](https://reallakshman19.github.io/progress-page/#/adhoc/topo-a/cycle-board) | [TOPO-B Board](https://reallakshman19.github.io/progress-page/#/adhoc/topo-b/cycle-board) |
| Original task | [TopoFix issue #12](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/issues/12) | [XML Compare issue #239](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239) |
| Existing governing WBS | [TopoFix WBS R1 issue #3](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/issues/3), 3.2 / 4.1 | Same WBS, 2.1 → 4.1; universal format-adapter extension remains proposed until actually governed |
| One first return | Explain why Node 6880 RIGID (branch 31) and Node 6450 FBLI (branch 30), **240.6 mm** / OD **114.3 mm**, are suppressed by declared **CLOS**; show review-only discovery path, source receipts and overlap | Produce a read-only format admission matrix, F05/R4 one-element FROM/TO/Δ/units/seed → graph trace, original receipts and overlap |
| Critical contrary case | Legitimately closed ends in separate systems must **not** be joined from geometry or matching OD; automatic ≤25 mm threshold remains | Unsupported profiles must show `UNSUPPORTED_INPUT`, not successful 0-node topology; F05/R4 56 elements ≠ GLRD 521 node claim |
| Initial authority | **PREPARED / READ_ONLY FIRST**; actual recipient, private bytes, writer lease, engineering review unverified | **PREPARED / READ_ONLY FIRST**; same limitations |

Each workspace contains **Overview, Cycle Board, Sources & fixtures, Oracle/agent continuity and Test cases**. They are optional Adhoc **views**, not new `data/projects.json` projects, WBS, agent task issue, sources of authority or a separate reporting system.

Both Boards read the configured native task issue, governing WBS issue #3, [Common relay draft PR #572](https://github.com/reallakshman19/Common/pull/572), and [Page PR #95](https://github.com/reallakshman19/progress-page/pull/95) **as source observations**. Since [Page PR #100](https://github.com/reallakshman19/progress-page/pull/100), the same Adhoc pages also reuse the actually published TopoFix `index.json`, `cards.json`, `audit.json`, the shared CIIFR-style `INFO_AUTO` WBS cards and original `Copy grounding / Page brief`. Neither native observations nor the published Page records establish agent dispatch or engineering acceptance. For this baseline **Common PR #572 is draft**; **Page PR #95 merged** at `0fc9257c65dc3451912a20f9fc0f451401bd76da`. The published TopoFix Page index still identifies **R1** as current, so the **format-adapter scope and R2** must not be asserted published by a Board label. Read fresh metadata before acting.

Original protected XML (Owner Handoffs) is not the same as a public grounding fixture. Original source access/receiver SHA is **NOT_RUN** until the actual agent confirms bytes. If unavailable, continue safe read-only public-source work and report dependent claims UNKNOWN.

## 5. Other Cycle Board work completed / unfinished — evidence register

This section is a **dated register of implementation and tests**, not a parallel WBS or ongoing status feed. For current status, follow the linked PR, original issue, exact head and actual Page audit; this paragraph becomes historical after changes.

| Work | Native evidence | As of 31 Oct 2026 | What that proves / does not prove |
|---|---|---|---|
| Source-bound CT-1–CT-4 **contracts** | [Common PR #567](https://github.com/reallakshman19/Common/pull/567) | **Merged** into Common `999dd8d1516af6a65a840d9f3f489b5f0115d261` | Contract and four implementation slices, **not** a real-cycle activation |
| Shared Smart Badges and Cycle Board runtime | [Page PR #63](https://github.com/reallakshman19/progress-page/pull/63) merge `b6805537c3b179f861d5f5ec138ef3fcc26c4c3a`; [PR #70](https://github.com/reallakshman19/progress-page/pull/70) merge `5f138cd6f279d21ed0f51ce24d2ff026ae77a9df` | **Merged, shipping** | Shared AIM/WBS/ROADMAP/PLAN/FIXTURE/ORACLE_CONTINUITY badge IDs; read-model, native delta, writer preview and INFO-Auto audit-derived WBS cards. Not a new task protocol or engineering approval. |
| CT-1/2/3 experimental stacked candidate branches | [Page PRs #69](https://github.com/reallakshman19/progress-page/pull/69), [#76](https://github.com/reallakshman19/progress-page/pull/76), [#79](https://github.com/reallakshman19/progress-page/pull/79) | **Closed, unmerged**, historical candidates | Do not cite these as merged. Current functionality and tests are separately present on Page `main`. |
| CT-4 effort accounting / falsification | [Page PR #83](https://github.com/reallakshman19/progress-page/pull/83) `24b5dea74bf5e5708082a6804107da4608e0cb98`; [PR #86](https://github.com/reallakshman19/progress-page/pull/86) `67ed8711e58e0f689a834130698ecb8484ae88f2` | **Merged** | 3-project adversarial tests and effort-input method; **actual matched five-role baseline vs pilot saving remains unmeasured**. The [CT-4 acceptance issue #80](https://github.com/reallakshman19/progress-page/issues/80) remains **OPEN**. |
| Oracle → agent → Page/fixture/concept-map lifecycle stress | [Page draft PR #89](https://github.com/reallakshman19/progress-page/pull/89) | **Draft, unmerged** (64-seed lifecycle and extended Adhoc stress test candidate) | Synthetic/source-link/CLI regressions are not independent live agent onboarding or private original receipt. |
| Two actual Adhoc Cycle Board trial workspaces | [Page PR #97](https://github.com/reallakshman19/progress-page/pull/97) squash merge `df9dcfe146f19079bfa4bf1e3d3de85028deed8e` | **Merged and Pages deployed** | Separate TOPO-A/B native issue observations, status, fixtures, read-only continuity; author-side 7/7 new Node falsifiers, 321/321 Python, 230/230 Chromium (exact candidate tests). No agent dispatch. |
| Historical Page status reconciliation for manual repair | [Page PR #95](https://github.com/reallakshman19/progress-page/pull/95) merge `0fc9257c65dc3451912a20f9fc0f451401bd76da` | **Merged** | Preserves original TopoFix WBS R1 audit, preview implementation status. Does **not** accept connectivity/Weight/Final engineering. |
| Source-grounded TOPO concepts / fixtures | [Page PR #99](https://github.com/reallakshman19/progress-page/pull/99) merge `2be8d70ed3e3afdc31a62ba38d753777aece9b86` | **Merged** | Detailed A/B concept/specification/fixture links; private originals remain unverified until recipient byte receipt. |
| CIIFR INFO-Auto / WBS reuse on TOPO-A/B | [Page PR #100](https://github.com/reallakshman19/progress-page/pull/100) merge `f4d33345b71d9c693fb62700a29d0dca1b5f6d5b` | **Merged and deployed** | Existing TopoFix WBS, Owner AIM, audit-derived INFO-Auto, Smart Badge IDs and copyable grounding briefs now precede collapsed source provenance on each TOPO Board. Browser/CI PASS is not actual Oracle/agent utilization or engineering PASS. |
| Missing Adhoc tabs from stale browser cache | [Page PR #98](https://github.com/reallakshman19/progress-page/pull/98) merge `45471bed9fd600e5cfb10bfbeecc8b6f60a4970a` | **Merged, deployed** | Public Pages now stamps **72** JS/CSS references across 32 scanned packaged files with exact deployed commit. All 324 Python tests PASS. Corrects asset freshness; not original engineering acceptance. |

**Freshness caution:** A green CI check, UI view or status report does **not** establish cold-start recovery by actual agents, current private source receipt, engineering design intent, non-author independence or the Owner's effort-reduction result. All these gates remain separately reviewable. Likewise, no new recurrence/polling is required to fulfill this document.

## 6. Scope-specific cold-start and continuation checks

**Oracle first source-walk:** Can the incoming Oracle point to the actual Owner outcome, full WBS, the last source candidate, each agent's exact current task, separate write surfaces, original files/relays, latest verified Page revision and one surviving wrong case? Can they demonstrate a source-to-output rule in their own words? If not, keep any dependent authority unverified while continuing safe independent groundwork.

**Agent first return:** Each agent states role and id8/UNKNOWN, exact task/WBS/head, inspected original sources and specific source rule, protected bytes/access actual status, code/PR overlap, meaningful negative control, current HOLD and **ONE requested bounded next implementation action**. Oracle reviews before any write. The return should live in the *native issue* and authorized relay if actually used, not in a Board-only report.

**Returning participant (ordinary short instruction: “Cycle now”):** Open the existing project's Cycle Board as the context/delta start, then check last verified task and subsequent consequential delta. If still the same task and authority, continue native protocol without recreating a full OnBoard packet; if already returned and awaiting Oracle, do not re-run; if source/recipient/candidate changed or private custody unclear, stop that dependent action.

**Owner usability and acceptance:** Verify the actual Adhoc Page displays current correct tabs, each Board loads its own task/WBS, 403 or stale source is explicit, both source and Page axes are separate, no duplicate audit/WBS, and actual user/role active minutes vs baseline are measured. The exact original design-intent cases need the authorized engineering reviewer and source bytes. Report PASS/PARTIAL/HOLD/NOT_RUN by *gate*, never as a universal single PASS.

## 7. Maintainers, changes and precedence

- Canonical precedence: [START_HERE](../../START_HERE.md), [Oracle Cycle protocol](../../../../oracle-cycles/PROTOCOL.md) **when active**, [Page modes](MODES.md), original native issue/WBS and source/relay custody, [Cycle Board data interface](CYCLE_BOARD_CONTRACT.md) and [vertical implementation slices](CYCLE_BOARD_VERTICAL_SLICES.md).
- This file gives the **short operational route and accurate historical implementation register**. It should not be used as a second mutable status ledger. When state changes, update the original issue/PR/Page audit, then make a small source-linked clarification here **only if the protocol meaning or navigational entry changed**.
- The [Progress Page](https://reallakshman19.github.io/progress-page/#/adhoc/progress-page/cycle-board) Adhoc navigation is an optional way in; the governing project Page Home/WBS and its original sources remain first-class.
- No implementation engineer, Page author or new Oracle self-certifies independent review merely by using a second chat or this document.
