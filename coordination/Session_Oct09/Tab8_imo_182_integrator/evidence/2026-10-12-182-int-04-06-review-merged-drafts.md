# 2026-10-12 Tab8 r3 — 182-INT-04 and 182-INT-06 exact-head review; chat=6acd3a5b

**Aim:** v3.1.0, label_sha 2ff9246; Owner O1 registered blueprint via sole Shared/tools/render_core.py and frozen golden, O2 named QRT with *separate* accepted decision, O3 only observed gap. TEST-only, no official Core2 or 68-source admission, QRT accepted=0/28, no public learner change, no source/merge/release exceptions. GitHub PR-level metadata and exact blob/commit comparisons independently read back. No legacy Buddy 1b rerun.

## TASK EVIDENCE — 182-INT-04

Outcome: O1; O3 only if a demonstrated blueprint gap emerges (none demonstrated).
For the user: Nothing changed in the real/public learner workflow. Existing Owner-frozen five HTML bytes remain intact, and stale overlapping branches did not overwrite their newer renderer/golden implementation.
Proof: https://github.com/reallakshman19/Grade9v3.5/pull/190/files ; https://github.com/reallakshman19/Grade9v3.5/actions/runs/38297307827 ; this document.

At Grade9 main `4dbedc6773482bbecb146ff8959614b2c32dcc6e`, #190 `865ef59b6ddd00adf7c12b738163f9c17fd7f69b` remains OPEN DRAFT and technically red by its **generated publication** / broad checks; merging any of #184–#189 into main would bypass that integrated gate or duplicate partial evidence.

| PR | Exact head | Independent assessment versus #190 | Decision |
|---|---|---|---|
| #184 | 86f17fa | Three unique early Core2A-only workflow/manifest/test files; test compares a CANDIDATE golden and acknowledges absent actual learner/A4/math verdict. Not the Owner-designated frozen five-role golden or postattempt H3 | HOLD as outdated pilot. No independent safe merge under current gate; do not discard authored pilot before integrated main |
| #185 | 752b9ba | Two early Core1A-only workflow/test files; tests include pypdf/PDF-A4 receipt work not yet Owner-designated as critical path. Current #190 has staged learner/real golden/renderer tests; old tests not exact code-equivalent and should be revisited only for a demonstrated gap | HOLD, do not replay optional print detour |
| #186 | ef3d3e2 | Three staged source/figure/test files; Core1A staged SVG is same preserved blob `b8f54b89706eaba84b2e631458c87360711c32be` at #188/#190, source evolved for H3; replay would regress latest source | FOLDED/EVOLVED in #190; no duplicate merge |
| #187 | c55c9d9 | GitHub compare `#187...#190` status ahead, behind 0: actual ancestor of #190 | FOLDED ancestry; no duplicate merge |
| #188 | badd51a | GitHub `#188...#190` divergent only because #190 evolved; independently fetched Owner golden snapshots five HTML, snapshot-lock, records Git blobs identical across both, and `golden/INDEX.md` blob `c6d8305dbe536a9366f03754ae84ca147f71992f` identical. Combined CI golden test already in #190 | FOLDED exact goldens/index; avoid older duplicate merge |
| #189 | 6307e5d | GitHub compare `#189...#190` status ahead, behind 0: actual ancestor; strict frozen lock tests present in #190 | FOLDED ancestry; no duplicate merge |

**Owner direction** was "review, fix and merge" under exact-head gate. This **review/disposition is PARTIAL rather than closed merge** because #190 and old heads still lack whole green/non-worsening gate. Old drafts remain OPEN DRAFT, no cherry-pick or close; no QRT, source-rights or release claims. Reassess only incremental unique safe checks after #190 admitted to main, not by blindly counting six merges.

Original preserved SHA/blob identity: `snapshot-lock.json@888678554c41257e6d96c802f0009983ccbb5328`; `records.json@cd5ef962f47808a05cfebec3a8a4f836ef0695cf`; original frozen CORE1/1A/1B/2A/2B HTML `d297bfafc40c4882b24fb7fe291e3b5b57aac20c, 200f3fbc2f3bd7d848668a415411880c613790f7, 6be9b95314f67cd29135cdd733325d38bb2bd2de, be69d9eee4f012398d16328dd71fcc1a181f52b8, cb03f78d526f42a41a6ff9e9474b8a2b8d00e7fe`, checked directly both refs. Owner D-182-3 successor Core2A golden still OPEN.

## TASK EVIDENCE — 182-INT-06

Outcome: O1 technical integration prerequisite to separately reviewed O2.
For the user: Nothing changed publicly. 13 distinct authored TEST QRT cells now render at the latest upstream draft #190 tree with page-hash receipts and verified Core2A after-attempt controls; academic acceptance remains 0/28.
Proof: https://github.com/reallakshman19/Grade9v3.5/pull/191 ; https://github.com/reallakshman19/Grade9v3.5/pull/192 ; hosted same-head per-cell artifact links below.

**Base and preserving merge:** Original QRT #191 head `634725381baa0ef0f332f14bb02393ebecce4cef`, #192 `4ddb109a52df05f2a70a340f30c6300518401657`, both diverged and **four #190 commits behind** at common base `67c34dababb0da0ef7d5f4a532bfcf3119754961`. Exact GitHub diff from this ancestor to #190@865ef59 includes precisely six changed files: combined golden workflow, `Shared/tools/render_core.py`, `golden/INDEX.md`, `tests/test_build_golden.py`, two H3/golden tests. No path overlaps either QRT changed-file set. Create merge commits with **first parent the old authored branch head, second parent the latest #190 head**, overlaying only the six identical upstream blobs, and perform **non-forced expected-old-head ref updates**. Verify branch ref, new two-parent commit and diff against latest #190:
- #191 D2: `eb3cf06646f00bf208084e794b41b4d8d83135b6` on `agent/imo182-qrt-d2-justify-20261012`, 54/54 files QRT-D2-only vs #190, no unexpected paths, 7 distinct D2 named cell workflows. GitHub Actions fresh head all **7/7 SUCCESS**.
- #192 D1: `089b57c98d697a0e19683c3d78e0d51220b9174a` on `agent/imo182-qrt-d1-represent`, 60/60 QRT-D1-only paths vs #190, no unexpected paths, 6 distinct D1 named cell workflows. GitHub Actions fresh head all **6/6 SUCCESS**.

**13 independently downloaded hosted ZIPs, exact PR heads:** `render_core/2`, `PAGES`, six actual HTML (CORE1,1A,1B,2A,2B,index), five exact blueprint refs, `gaps=[]`, and newly inherited `render-receipt.json:page_sha256` **78/78 matches independently recomputed SHA-256**. Old original receipts without per-page SHA were not used as proof. No authentic core2 page; all manifests `subject=TEST`, `selection.core2=[]`.

| Cell | Workflow exact head / run | Hosted actual generated artifact | Independent receipt SHA / browser |
|---|---|---|---|
| APPLY-D2 | 38310547146 | [11773669703](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38310547146/artifacts/11773669703) | 6/6, H3 2/2 |
| EXPLAIN-D2 | 38310547155 | [11774955065](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38310547155/artifacts/11774955065) | 6/6, H3 2/2 |
| JUSTIFY-D2 | 38310547181 | [11774572433](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38310547181/artifacts/11774572433) | 6/6, H3 2/2 |
| MODEL-D2 | 38310547126 | [11773779616](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38310547126/artifacts/11773779616) | 6/6, H3 2/2 |
| REPRESENT-D2 | 38310547118 | [11773979109](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38310547118/artifacts/11773979109) | 6/6, H3 2/2 |
| RETRIEVE-D2 | 38310547112 | [11774870273](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38310547112/artifacts/11774870273) | 6/6, H3 2/2 |
| SYNTHESIZE-D2 | 38310547108 | [11773864638](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38310547108/artifacts/11773864638) | 6/6, H3 2/2 |
| APPLY-D1 | 38310599423 | [11773734606](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38310599423/artifacts/11773734606) | 6/6, H3 2/2 |
| EXPLAIN-D1 | 38310599324 | [11773769541](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38310599324/artifacts/11773769541) | 6/6, H3 2/2 |
| MODEL-D1 | 38310599417 | [11774372882](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38310599417/artifacts/11774372882) | 6/6, H3 2/2 |
| REPRESENT-D1 | 38310599416 | [11774497648](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38310599416/artifacts/11774497648) | 6/6, H3 2/2 |
| RETRIEVE-D1 | 38310599474 | [11774222940](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38310599474/artifacts/11774222940) | 6/6, H3 2/2 |
| SYNTHESIZE-D1 | 38310599455 | [11774880288](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38310599455/artifacts/11774880288) | 6/6, H3 2/2 |

**Independent actual browser checks:** Chromium headless via Playwright on exact hosted `core2a.html` for each of 13 cells at **390×844** and **820×1180**, **26/26 viewport cases pass**, each requiring six assertions: before attempt H3 not in `document.body.innerText`, not in accessibility snapshot; early hint summary click denied; blank commit denied; a separately typed nonblank learner attempt followed by explicit summary click reveals H3 visible and in accessibility snapshot. Total **156/156 individual assertions**. No independent human academic verdict is claimed; these are technical attempt-timing checks. Frozen Owner bytes unchanged, D-182-3 reserved.

**Still blocking main merge:** #190 remains OPEN DRAFT/RED; both stacked PRs have fresh scoped CI green but broad canonical/guardrail runs in progress or failing inherited checks, no exact-head all-gates-cleared. No merges into main or QRT `accepted` mutations; **1/16 PRs merged** (#197 only), **0/28** QRT accepted. Even though 13 pages have technical evidence, their cell-level Owner acceptance/signoff remains unawarded. Correct status PARTIAL until #190 admitted + base/head merge gate + per-cell independent review where required.

**Next tasks:** 182-INT-02 generated-drift exact-base delta, 182-INT-05 #190 whole gate, 182-INT-04 final PR dispositions after integrated merge, then 182-INT-07/08 as dependency permits; 182-INT-13 monitor verification without acceptance.
