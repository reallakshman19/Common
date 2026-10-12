# P6 H3 | Owner-selected after-attempt Core2A hint, adapted from mature Core2

2026-10-12 | chat=6acc408a | Tab1 | issue Grade9v3.5 #182 | aim=v3.1.0 label_sha=2ff9246 | outcome=O2 prerequisite | REVIEW-ONLY TEST draft

Outcome: O2 (prerequisite, **NOT** QRT acceptance)
For the user: Nothing changed in live/public learner flow. The revised TEST Core2A page now keeps the potentially decisive H3 hint unavailable until **after a learner writes and commits an answer**, while H1/H2 remain requestable and the full solution requires separate disclosure.
Proof: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38231707376 (exact-head 7/7), local Chromium 16/16 on identical SHA-bound artifact.

## Owner decision and mature reuse

Owner message at 2026-10-12T09:23:26Z "H3 Hint, follow you recommendation!" resolves `D-182-2-H3` **timing** to `AFTER_ATTEMPT` as suggested earlier. [Decision on #182](https://github.com/reallakshman19/Grade9v3.5/issues/182#issuecomment-6121493094). This is NOT a scientific/academic determination that wording is perfect and does not accept `QRT-JUSTIFY-D2`; accepted canonical QRT remains **0/28**.

- Reuses existing `Shared/tools/core2_v2.py` support release contract, **not** a duplicate new hint policy: schema-shaped question extension `grade9v3:core2_support_plan` declares `protected_move_refs=[MOVE-TEST-CORE2A-WARRANT]`, support `scaffolds[2]` completes that move and is `AFTER_ATTEMPT`. Mature validator checks actual crux refs, prevents PRE_ATTEMPT_SAFE when support completes protected work, and rejects unknown support refs.
- The legacy Core2A `_ladder` did not consume this mature plan; before adaptation all H1-H3 were revealed via NEXT HINT before attempt. The narrow opt-in adjustment in `Shared/tools/render_core.py` invokes existing `core2_v2.project_support(q)` **only for Core2A with an explicit plan**. Keeps H1/H2 in precommit queue and migrates H3 to existing inert `reveal(...gated=True)` with `data-requires-attempt`. Unknown/invalid release plans fail closed and report an AUTHOR_HINT_RELEASE_POLICY gap.
- No component added to `Shared/web/interactive-page-blueprints.v1.json`. The registered Core2A `support` slot already allows `pedagogical_scaffolds`; use its existing affordance. Original mature `BP-CORE2-SOURCE-QUESTION@1.11.0` rights/custody remain untouched. No authentic source Core2 admitted.
- Two TEST authoring packages carry the same policy: 2-question `TEST/imo-research/pilots/core1a-render-qualified-divisibility.v1.json` and independent 3-question `TEST/imo-research/pilots/imo182-core2b-transfer-pilot.v1.json`. H3 authored wording unchanged; only reveal timing changed. H1/H2 and previously tested Core1A accessible SVG remain intact.
- Isolated [DRAFT PR #190](https://github.com/reallakshman19/Grade9v3.5/pull/190) exact head `67c34dababb0da0ef7d5f4a532bfcf3119754961`, forked from #189 at `6307e5dd97f9ae72a052fc7f3e88c368a4cc5434`; predecessor #186/#187/#188/#189 remain DRAFT, unchanged. No merge/release, shared printer, KEY, route, QRT acceptance or source rights.

## Exact-hosted technical evidence

[Workflow 38231707376](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38231707376) job `114752508174` **SUCCESS**, test command `python -m unittest tests.test_imo182_core2a_h3_after_attempt -v` **7/7 PASS** and sole CLI renderer `Shared/tools/render_core.py build --manifest TEST/products/imo-182-five-core-integrated-review.manifest.json --out build/imo182-h3-after-attempt --draft --reference` generated six real pages (5 Core roles + index), `gaps=[]`. Downloaded exact workflow artifact `11738482602` named `imo182-core2a-h3-after-attempt-actual-html`; all **6/6 page SHA-256 values match source-run `h3-evidence.json`**; digest `ceb127be3014e72a`.

| Actual role | Hosted HTML SHA256 |
| --- | --- |
| `core1.html` | `35616872153faedef728024a7d174f6045fb0d591a86bde836aab1542537370e` |
| `core1a.html` | `cbf4a9aefee5b9dd65a92988a62b4fb1ec87c88e791e359267a62069f7b9fd08` |
| `core1b.html` | `e172362aeb154e3eae2e0485be20ff6f06c32eecc7e8fcdf3af00f18941b53f8` |
| `core2a.html` | `ec78f359f7157def2b00e3d5c5b29452e22719e669aac2d31a9917e1caf36d27` |
| `core2b.html` | `8f6cb1bf6caf82f55057b509a1a49cdf7faa486617242d418efd01609f9bf6c0` |
| `index.html` | `d27dfdfef846374447256cd44f590df7c5d82ca2edb08854171fbc6d9daa5460` |

**Local Chromium** `page.set_content()` with exact byte-identical hosted `core2a.html` (SHA above), **16/16 intended interaction checks PASS, 0 JS errors**: H3 absent from initial visible body; H1 available, NEXT HINT displays H2 then disables; H3 absent after H2; premature H3 summary click cannot open; blank attempt commit does not unlock; nonblank typed attempt unlocks but keeps H3 closed and slot empty; explicit H3 summary click opens and displays H3, independent FULL SOLUTION remains closed. Inert HTML `<template>` markup is inspectable in page source (not cryptographic secrecy), but not shown as learner hint before commit.

**Golden delta independently compared** with previous frozen Owner `G-IMO-G9-FIVE-CORE-20261012` snapshots: after replacing only the 16-character render authority digest, `core1.html`, `core1a.html`, `core1b.html`, `core2b.html` are **identical**; in `core2a.html`, only `<section data-blueprint-slot="support">` changed. This is asserted by the seventh hosted regression; the original golden snapshots were **not edited**.

## Known expected red and Owner review

- [Older exact Owner snapshot lock 38231707266](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38231707266) on PR #190 must **fail** because the source/presentation now differs from the old frozen pre-H3 Owner snapshot. This is **not** a false green and cannot be bypassed; request a new Owner-designated successor golden with exact Core2A HTML after visual review. Existing old golden is preserved for historical behavior. Until successor designation, **full O1 new-version acceptance is BLOCKED_OWNER** even though new H3-specific technical proof is green.
- Some PR-wide workflows on this draft are still red/pending (including `core1a-tablet-browser` generated publication checks on intermediate head); neither source-rights nor broad integration is authorized. Do not merge or publish and don't claim overall CI green.
- QRT D2 can be reviewed on these new exact bytes, but **QRT accepted stays 0/28**, reviewer identity and H1-H3/S1-S3/P1-P3/M1-M3 academic verdict remain not recorded; after-attempt timing only is settled.

## Reuse audit link and work sequencing

Complete [recent PR / mature blueprint audit](182-P6-RECENT-PR-REUSE-AND-MATURE-BLUEPRINT-AUDIT.md) distinguishes direct tests, authored research candidates and source-restricted official samples, and maps Core2/1A/1B adaptation for the 4×7 matrix. The [28-cell monitor](182-P6-28-CELL-AGENT-MONITOR.json) lists all cells with 0 accepted and concrete safe PR reuse leads. No four agents have been dispatched in the user session: readiness and audit are real, autonomous background monitoring is **NOT_ACTIVE**.

**Disposition:** H3 data and renderer TEST proof **DONE**; **Owner visual decision required for new Core2A HTML** before successor frozen golden; independent academic QRT approval and merge/release still reserved. No blueprint capability gap requiring registry mutation has been proven.
