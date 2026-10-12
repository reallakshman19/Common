# AGENT-INTEGRATOR / 182 Tab8 execution plan r1

Pinned Grade9 main 778eb35a70517a46108ad0a5dc01dfc89f61c0e3; Common parent 71b777a9c3dc1746d8664fd8f124a6bdd2550189. Aim v3.1.0 / label_sha 2ff9246. Nothing public changes; TEST only; QRT accepted 0/28.
[28-cell link-first index](INDEX-28-CELLS.md) · [reviewer template](REVIEW-CHECKLIST.md)

| Task 182-INT- | Expected outcome | Working minutes (estimate) | Size | Initial status |
|---|---|---:|---|---|
| 01 | Live inventory and 28-cell index | 35 | M | PARTIAL |
| 02 | Diagnose guardrails/canonical on baseline and branch heads; fix without weakening | 60 | L | IN_PROGRESS |
| 03 | Inspect and merge CI concurrency #197 only under gate | 30 | M | PENDING |
| 04 | Decide #184–#189 supersede/fold/merge; preserve golden lock | 60 | L | PENDING |
| 05 | Gate #190 H3 after attempt and immutable golden then merge | 50 | L | PENDING |
| 06 | Retarget/integrate #191 D2 and #192 D1 one by one | 90 | L | PENDING |
| 07 | Retarget/integrate #193 D3 seven cells | 50 | L | PENDING |
| 08 | Integrate #194–#196/#198/#199 D4 five cells separately | 95 | L | PENDING |
| 09 | Fix MODEL-D1 and MODEL-D4 preattempt leakage then rerender | 60 | L | PENDING |
| 10 | Generate JUSTIFY-D1 five-role TEST | 50 | L | PENDING |
| 11 | Generate RETRIEVE-D4 five-role TEST | 50 | L | PENDING |
| 12 | Generate SYNTHESIZE-D4 five-role TEST | 50 | L | PENDING |
| 13 | Independently inspect all receipts, update canonical monitor without acceptance | 60 | L | PENDING |
| 14 | Issue evidence, Tab8 checkpoints, reviewer handover | 30 | M | ACTIVE |

## Live PR base-chain and mergeability
All listed PRs are OPEN DRAFT, mergeable=true GitHub metadata at preflight; zero merged. GitHub mergeability does not satisfy the stricter gate. #191–#196, #198–#199 target #190; the rest target main. All scanned broad shared guardrails/canonical red, scoped exact-head runs of 25 candidate cells green.

| PR | Head | Base | Carries | Check observation |
|---|---|---|---|---|
| [#184](https://github.com/reallakshman19/Grade9v3.5/pull/184) | 86f17fa | main | early Core2A | scoped candidate CI mixed/red |
| [#185](https://github.com/reallakshman19/Grade9v3.5/pull/185) | 752b9ba | main | early Core1A | scoped candidate CI mixed/red |
| [#186](https://github.com/reallakshman19/Grade9v3.5/pull/186) | ef3d3e2 | main | Core1A stage repair | scoped candidate CI mixed/red |
| [#187](https://github.com/reallakshman19/Grade9v3.5/pull/187) | c55c9d9 | main | Core1 + Core2B | scoped candidate CI mixed/red |
| [#188](https://github.com/reallakshman19/Grade9v3.5/pull/188) | badd51a | main | five-role preview + frozen golden | scoped candidate CI mixed/red |
| [#189](https://github.com/reallakshman19/Grade9v3.5/pull/189) | 6307e5d | main | golden exact rebuild | scoped candidate CI mixed/red |
| [#190](https://github.com/reallakshman19/Grade9v3.5/pull/190) | 67c34da | main | H3 after attempt; inherited golden | scoped candidate CI mixed/red |
| [#191](https://github.com/reallakshman19/Grade9v3.5/pull/191) | 6347253 | #190 | D2 7 | scoped candidate success; shared red |
| [#192](https://github.com/reallakshman19/Grade9v3.5/pull/192) | bf89f73 | #190 | D1 6 | scoped candidate success; shared red |
| [#193](https://github.com/reallakshman19/Grade9v3.5/pull/193) | 0a4d881 | #190 | D3 7 | scoped candidate success; shared red |
| [#194](https://github.com/reallakshman19/Grade9v3.5/pull/194) | e39db6a | #190 | D4 JUSTIFY | scoped candidate success; shared red |
| [#195](https://github.com/reallakshman19/Grade9v3.5/pull/195) | 6c00fae | #190 | D4 EXPLAIN | scoped candidate success; shared red |
| [#196](https://github.com/reallakshman19/Grade9v3.5/pull/196) | 0d36673 | #190 | D4 APPLY | scoped candidate success; shared red |
| [#197](https://github.com/reallakshman19/Grade9v3.5/pull/197) | a846174 | main | CI concurrency | scoped candidate CI mixed/red |
| [#198](https://github.com/reallakshman19/Grade9v3.5/pull/198) | c6cb89e | #190 | D4 MODEL | scoped candidate success; shared red |
| [#199](https://github.com/reallakshman19/Grade9v3.5/pull/199) | 84fe228 | #190 | D4 REPRESENT | scoped candidate success; shared red |

Exact-head merge gate: scoped CI green OR documented baseline-only red; sole renderer receipt zero gaps, SHA-256 match for 5 roles+index; five-role golden techniques and frozen original byte lock intact; blank attempt refused and H3 only after nonblank commitment; no hidden accessible preattempt answer; TEST only, no public route, accepted 0/28. If any fails, DO NOT MERGE. Do not touch Track A #166/#172/#175/#177/#178/#180/#181, Tab2 #183, Tab3, relay/STATE.yaml, shared printer, registry accepted field, or source rights. Owner decisions only reviewer, cell acceptance with IDs, D-182-3 successor Core2A golden, rights, release.

## r1 checkpoint 2026-10-12 after CI preflight
182-INT-03 DONE: #197 merged in Grade9 main@4dbedc6; baseline gate evidence in Tab8/EVIDENCE.log. 182-INT-02 PARTIAL: baseline guard 2385/272 and exact-base zero-new on #197; new issues on #191 requiring separate repair. 182-INT-01 PARTIAL (per-cell SHA/receipt URLs audit outstanding). Next CI run on main currently QUEUED, no other PR merges.

## r1.1 artifact audit checkpoint
182-INT-01 inventory/verification DONE within indexed scope (25 authored, 3 unstarted). 182-INT-13 PARTIAL: 25 downloaded hosted artifacts with zero gaps and six independently computed SHA, but no receipt per-page SHA. #190 exact frozen lock fails and needs legitimate correction without golden-byte mutation / Owner D-182-3 for changed H3. No additional PR merged. Technical content still blocked CI under strict gate.

## r2 checkpoint, 2026-10-12
182-INT-03 DONE #197 merged; 182-INT-04 DONE dispositions/fold of older #184–#189 source/Owner index; 182-INT-05 PARTIAL #190 strict frozen golden/H3/page SHA engineering subgates pass, waiting on exact canonical regression delta and tablet; 182-INT-02 PARTIAL shared baseline and two newly introduced golden-regression IDs repaired. 182-INT-01/13 PARTIAL 25 technical artifact sets and 28-row monitor, 0/28 accepted. 182-INT-06–12 remain unmerged/unfinished. [r2 handover](handovers/2026-10-12-tab8-int-r2.md) is the exact next-work contract.

## r3 successor workpack — chat 6acd3a5b (2026-10-12; supersedes r2 execution order, preserves history)

**Authority:** Owner v3.1.0 / label_sha 2ff9246; Coordinator closed BuddyRunner after verified 1b comment 6131617598 and 1a handover, with no Stage 2 wait. Authoritative instruction: take over, continue, fix and merge existing PRs under actual exact-head gates; one integrator, D1–D4 chats retired. **No new source, acceptance, merge-gate waiver, or release rights.** The integrator is the designated reviewer but must declare authorship/fix conflicts and cannot set accepted=true without QRT-specific sign-off AND Owner decision ID.

**Fresh provider preflight (not predecessor count):** Grade9 main `4dbedc6773482bbecb146ff8959614b2c32dcc6e`; of scoped PRs #184–#199, **#197 merged 1/16**, other 15 OPEN DRAFT. #190 head `865ef59b6ddd00adf7c12b738163f9c17fd7f69b`, unmerged, CI RED (same-head canonical 38297307793, guardrails 38297307819, Core1A tablet 38297307684 FAILED; golden 38297307827, H3 38297307764, five-role combined 38297307718 SUCCESS). Existing original Owner golden immutable; no accepted cells/28. Stacked PRs #191–#196/#198–#199 target an earlier #190 base, not a validated merged integration.

**First critical-path task is O1 Core1A page-to-golden.** Nonessential printer, route, lease, generic CI, and source-68 effort remain parked unless one blocks a named Core page. All estimates below are **working minutes, not task/aim percentage**; scoped results, not task counts, decide progress.

| Priority | Task ID | Expected observable outcome / stop condition | Outcome | Work min | Size | Status at r3 |
|---|---|---|---|---:|---|---|
| 1 | 182-INT-15 | Identify exact renderer-generated Core1A page and one named QRT cell; compare frozen Core1A golden T02/T03/T11, learner precommit/exit and source->blueprint->HTML provenance; record mismatch class or exact evidence boundary. If renderer inaccessible, BLOCKED, no handmade substitute. | O1/O2 | 45 | M | START |
| 2 | 182-INT-02 | Exact-base failed IDs for #190 canonical/guardrails/tablet; identify genuine introduced regressions; remedy only named Core-page blockers without weaker checks. | O1 prerequisite | 65 | L | PARTIAL carried |
| 3 | 182-INT-05 | At current #190 head, verify actual five-role renderer receipts/page SHA, immutable golden, H3 nonblank gate and browser/AT precommit; only merge if ALL section-6 gates met. | O1 | 60 | L | PARTIAL carried |
| 4 | 182-INT-04 | Re-review #184–#189 one-by-one under renewed Owner review/fix/merge; compare exact changed blobs against #190/main and eliminate duplicate/no-net-effect merges, satisfying exact-head gate for any safe merge. | O1/O3 | 80 | L | REOPENED |
| 5 | 182-INT-06 | Rebase/qualify #191–#192 authored D2/D1 against admitted #190; protect QRT cell mapping, golden and changed attempt semantics. | O1/O2 | 90 | L | PENDING |
| 6 | 182-INT-07 | Rebase/qualify #193 D3 authored TEST cells, exact head/role outputs. | O1/O2 | 60 | L | PENDING |
| 7 | 182-INT-08 | Rebase/qualify #194–#196/#198–#199 D4 authored TEST cells. | O1/O2 | 95 | L | PENDING |
| 8 | 182-INT-09 | Audit/fix MODEL-D1 and MODEL-D4 candidate preattempt cue concerns only where learner-surface evidence proves defect. | O2 | 60 | L | PENDING |
| 9 | 182-INT-10 | Author TEST QRT-JUSTIFY-D1 five-role journey only if still missing after current-head inventory. | O1/O2 | 50 | L | PENDING |
| 10 | 182-INT-11 | Author TEST QRT-RETRIEVE-D4 only if still missing after inventory. | O1/O2 | 50 | L | PENDING |
| 11 | 182-INT-12 | Author TEST QRT-SYNTHESIZE-D4 only if still missing after inventory. | O1/O2 | 50 | L | PENDING |
| 12 | 182-INT-13 | Independently reconcile hosted receipt hashes, 28 QRT rows, reviewer edit/conflict declarations, decision IDs; never auto-accept. | O1/O2 | 70 | L | PARTIAL carried |
| 13 | 182-INT-14 | Publish exact task evidence/coordination and handover; preserve Owner decisions, no fabricated acceptance. | O1/O2/O3 | 30 | M | PARTIAL carried |
| history | 182-INT-01 | Verify scope inventory and 28-cell link index; maintain only when an actual stale locator blocks a page. | O1/O2 | 35 | M | PARTIAL carried |
| history | 182-INT-03 | #197 concurrency-only PR merged before takeover; no further claim or retest from inherited receipts. | O1 prerequisite | 30 | M | DONE inherited |

**First task acceptance:** The named Core1A page must be traced from explicit authored QRT demand, manifest, registered BP-CORE1A-CONSTRUCTION and Shared/tools/render_core.py to the exact actual HTML; compare T02/T03/T11 and learner attempt/protected representation against a frozen SHA-locked Core1A snapshot. Return PASS/FAIL/UNKNOWN and mismatch owner; no accepted status. A necessary renderer inability is BLOCKED. All changes to protected golden require new Owner fixture, D-182-3 for Core2A successor remains reserved.

**Merge gate preserved:** exact current SHA; focused CI green or exact-base-only red with same failing IDs; renderer PAGES + zero REFERENCE gaps + 6/6 actual HTML receipt SHA; five registered role refs / printed golden techniques and old golden byte lock; Core2A H3 only after nonblank attempt, no visible/accessible/search preattempt decisive leak; TEST only, no source-righted Core2, no accepted-QRT change. `mergeable=true` alone not sufficient. No old-head green carryover. Track A/Tab2/Tab3 remain separate.

**Audit/report contract:** Every completed/partial task posts separately to issue #182 with first lines Outcome / For the user / Proof and required TASK EVIDENCE fields. Record real PR count as #merged/16 and QRT count only when source-reviewed accepted evidence is *merged* and Owner decision recorded. The next task after first Core1A oracle is #182-INT-02 or #182-INT-05 depending on observed blocker.
