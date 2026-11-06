# 3DC-XML-CII / v0.4 Step 4 — concept, user outcome, boundaries

**Oracle knowledge checkpoint, 2026-11-06. PUBLIC-SAFE / SELF_ASSESSED, not engineering acceptance.** This is a specific v0.4 performance slice, not a rewrite of the larger 3DC work plan. Read [architecture](ARCHITECTURE_COMPLEX_LOGIC.md), [decisions](ARCHITECTURE_DECISIONS_AND_CHALLENGES.md), [current handover](ORACLE_HANDOVER.md) and [successor prompt](ORACLE_SUCCESSOR_PROMPT.md) together.

## The Owner's problem

The [Owner's 3DC AIM v2.2.0](https://github.com/reallakshman19/Common/blob/b4546c3f586b93dbe875ad6a531abc85f701c583/relay/AIM/3DC-XML-CII.yaml) says: **“The XML→CII app freezes on large JSON, 4 Preview hangs, and weight decisions are split between Weight Match and \"Rigid Weights Need Review\"; fixes so far were patches.”** Its main aim is **“Large-JSON trace, Preview and Weight Match stay responsive on large inputs, traceable to source, with one weight review flow.”** Its O1, O2 and O3 outcomes and 100 MiB / two-million-occurrence O1 target belong to that *broader* project's label; the label's selected task is O1, **not** this fork's new engineering approval.

For the currently selected [v0.4 Issue #1](https://github.com/reallakshman19/3D_Converters_v0.4/issues/1), the immediate Owner direction is narrower: fix actual observed slowness in **4 Preview**, using reality-validated, bounded, low-risk optimizations; **no UI revamp, new worker/pagination design, writer/engine change, engineering authority or policy change**. Native scope: staged-wall evidence index (PR #2) and invocation-local exact-input Piping Class/weight cache (stacked PR #3). The performance change must not change any Preview decision, provenance, downstream enriched XML or CII byte for identical effective inputs.

## The experience that matters

The engineer imports an original source XML, staged original JSON and the selected Line List, Piping Class, weight and material masters. Step 4 Preview computes per-branch and node facts with traceable authority; the engineer can inspect/review rating and weight decisions. The Run path enriches XML and produces CAESAR II 2019 CII. A faster screen with empty rows, stale master data or changed material/pressure values is **not a success**. Equally, four matching output hashes do not prove the original engineering settings or CAESAR II interpretation are correct.

A representative current GLRD BM2 input has 31 source branches, 1,196 source nodes, 86 staged JSON BRANCH records, eight real Line List lines, 10,699 Piping Class rows, 1,595 weight rows and 383 material-map rows. These are Owner-supplied **private** engineering inputs; do not copy their bytes or unrestricted locators to this public relay. The native [Issue #1 receipts](https://github.com/reallakshman19/3D_Converters_v0.4/issues/1) record custody hashes and executed tests.

## Three distinct claims

1. **Performance parity:** for fixed original XML/JSON, masters, effective mappings/defaults and overrides, every optimization comparison must produce *identical bytes* and Preview authority decisions. Baseline must repeat deterministically, clean Chromium state, same exact commits.
2. **Performance benefit:** benchmark the computation actually exercised, not a zero-row no-op or invented UI click. Record method, repeated durations, branch/node counts, signatures and environment. A 3-run median is a narrow measurement, not a p95 guarantee.
3. **Engineering correctness / release:** material abbreviations, pressure-unit metadata, actual CII effective fields and independent CAESAR II interpretation need their own engineering-authority review. Existing identical wrong results remain wrong. The two performance PRs must not silently fix these.

## What has been observed and what has not

The incumbent Oracle and local validation agent independently inspected the uploaded R3 evidence archive (SHA-256 `53309e54d3c79146bdc827cecdede635c0b38c690d62731a241d9d26d4a58f97`). The incumbent **independently recomputed byte equality** for packaged XML, diagnostics and CII groups; **did not run** the local browser worktrees or CAESAR II vendor application. Local agent reported Windows Node suites 25/25 PR2 and 34/34 PR3, nine browser converter-input runs, and four browser `outputMode:'both'` runs. The resulting configuration was reconstructed, not a captured historical Owner session; it is **CANDIDATE_CONFIG_ONLY**.

Release boundary: [PR #2](https://github.com/reallakshman19/3D_Converters_v0.4/pull/2) and [PR #3](https://github.com/reallakshman19/3D_Converters_v0.4/pull/3) remain **DRAFT, UNMERGED, MERGE HOLD**. No independent engineering-critical final 92/100 score or Owner merge authorization.

## Scope and historical relationship

The older [3DC-XML-CII continuity golden fixture, immutable bf02e54e](https://github.com/reallakshman19/Common/tree/bf02e54e1b453c3206ae366de7d65f41c94ab0d4/relay/AGENT_WORK/3DC-XML-CII/oracle-continuity-20261025/payload) transfers the broader O1/O2/O3 architecture at its October snapshot; it is **historical context**, not the live WBS/current PR of `3D_Converters_v0.4`. Preserve their relationship as *broader project O2 intent -> this bounded v0.4 Step 4 performance issue*, with no invented shared Oracle epoch, approved scope merger or inherited release verdict.
