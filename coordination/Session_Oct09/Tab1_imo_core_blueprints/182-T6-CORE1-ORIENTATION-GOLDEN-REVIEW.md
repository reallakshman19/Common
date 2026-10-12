# 182-T6 | Core 1 registered orientation page versus candidate golden T14

2026-10-12 | chat=6acc408a | P4 successor | Grade9v3.5 #182 | aim=v2.1.0 | outcome=O1 | TEST page built | GOLDEN CANDIDATE / NOT OWNER ACCEPTED

Outcome: O1
For the user: No real learner/public workflow changed. A reviewable TEST Core 1 orientation page now exists from the registered blueprint, teaching arbitrary positive-integer scope, necessary parity/modulo-3 prerequisites, the governing consecutive-product relation and a compact worked concept.
Proof: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38210827543

## Immutable production chain (no source rights or release)

- Existing TEST authored source: `TEST/imo-research/pilots/core1a-render-qualified-divisibility.v1.json`, exact original `main` blob `e8b1dcae1014f9a9a2cce7c2489b21b36c049f81`, confirmed unchanged on #187. New selection `TEST/products/imo-182-core1-orientation.manifest.json` selects only Core1 and existing microtopic `MIC-TEST-CORE1A-QUAL-G9-CONSECUTIVE-FACTOR-INVARIANTS`, `core2=[]` and `core2a=[]`. No SOF source item is admitted.
- Existing registered `BP-CORE1-ORIENTATION@1.1.0` in `Shared/web/interactive-page-blueprints.v1.json` blob `591ba061b8771c30fdffc4506aa720ca9ba89335`, original sole renderer `Shared/tools/render_core.py` blob `9302174e1491138a459a80e9d3f176b83b19e6d7`; unchanged.
- Isolated [draft PR #187](https://github.com/reallakshman19/Grade9v3.5/pull/187), exact head `c55c9d927c09a4dfdb45eba5d038983e0f562275`; hosted run `38210827543` **SUCCESS**, downloaded exact-head artifact `11729430238` (`imo182-core1-core2b-blueprint-golden-review`). Actual `build/imo182-core1/core1.html` SHA-256 **`605c57fe7fff8b0f128ad41ef813f8db2717f603cfc7793545ded401330d578f`**, direct byte read-back matches `build/imo182-evidence.json`. `render-receipt.json`: `roles=[CORE1]`, `pages=[core1.html,index.html]`, `gaps=[]`, `held_to=REFERENCE`, digest `d55b678060a3bfb8`, `draft=false` meaning **no renderer gaps only**, NOT Owner approval or release.
- Golden candidate `golden/units/G-MATH-LINEAR-CONSTRAINT/records.json`, blob `3e63b03b8b549d014124932c852ad226f1d692ef`; corresponding `core1.html` generated in the same hosted run via `Shared/tools/build_golden.py`, not an independently authenticated static Owner-blessed oracle. Its original concept checks what the variable means in a linear-equation statement; ours checks what 'every positive integer' demands for a consecutive-factor proof. Comparing method/learner decision, **not identical mathematical text**.

## Actual Core 1 vs golden move

| Test | Golden move | Actual source-to-render Core 1 | Verdict |
| --- | --- | --- | --- |
| **T14 prerequisite bridge** | Identify the domain of x and the meaning of a constraint before using substitution, without delivering the full equation-solving lesson | Authored entry assumptions define positive integer start, parity, residues mod3 and coprime-divisor rule. The actual page states the hard transition from examples to universal factor guarantees, projects a related representation, supplies the governing factor relation, and a short 'why a modulo-3 factor is guaranteed' anchor | **PASS (technical)**; genuine prerequisite orientation, not copied linear-equation content |
| **O1 registered page structure** | `identity` then `orientation` via existing BP-CORE1-ORIENTATION | Actual `data-blueprint-ref=BP-CORE1-ORIENTATION@1.1.0`, exactly the two golden slot IDs/order and `hard_transition`, `governing_relation`, `compact_anchor`, `exit_prompt` component content | **PASS** |
| **Owner acceptance** | Candidate teaching/golden independently checked by a qualified reviewer | No real learner, Owner-blessed fixture or academic/figure screen-reader acceptance | **PENDING** |

**Tests:** hosted `python -m unittest tests.imo_182_core1_core2b_golden -v` **7/7** pass across joint batch (T6/T7); Core1-specific semantic prerequisite, original authored-selection, blueprint/slot and no-gap checks all pass. Independently read recovered actual HTML bytes and locally opened it in Chromium: visible orientation header and exactly two role slots. No fresh PDF printing was attempted because shared A4 printer decision is parked with the Owner. Candidate whole-fixture `REFERENCE` build in memory reports two *unrelated* CORE1A findings; none applies to Core1 or Core2B and they were **not repaired, suppressed or promoted to Owner success**. The golden's standard `build_golden.py` floor-mode reported 0 gaps but is still CANDIDATE.

**Decision:** T6 BUILD AND TECHNICAL GOLDEN COMPARISON **DONE**; O1 Owner acceptance **NOT_MET / PENDING**. Nothing in T6 establishes a new blueprint gap (O3), O2 named accepted QRT cell (0/28), original source custody, print A4, QRT academic/learner test, public route or merge. No modifications to existing blueprint/renderer/core1 authored source. Next T7 in the same Owner-requested batch.
