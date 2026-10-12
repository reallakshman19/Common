# Issue #183 / Tab2 — Quality benchmark from G-IMO-G9-FIVE-CORE-20261012

2026-10-12 | chat=6acc4eaa | plan=r5 benchmark addendum (no plan or sticky-label change) | aim=v3.1.0 / label_sha=64a4e9c | Outcomes O2 and O3; O1 reference limitation.

**Pinned source:** https://github.com/reallakshman19/Grade9v3.5/blob/68d8e70c20b0fa304e860f12f6ccd66bd3d3a270/golden/units/G-IMO-G9-FIVE-CORE-20261012/GOLDEN.md. The exact Owner-designated fixture is on Grade9v3.5 commit `68d8e70c20b0fa304e860f12f6ccd66bd3d3a270` (GOLDEN.md Git blob `57442b155ed4f99ad9303cf5cb3ccf37b068506c`). As checked during this review, the file does **not** exist at product `main@778eb35a70517a46108ad0a5dc01dfc89f61c0e3`; always pin this ref when comparing and do not assume availability from main alone.

## Authority and exact content verified

- Status **`OWNER_DESIGNATED_EXACT_HTML_SNAPSHOT`**, not Owner academic/QRT acceptance. Owner directive “save this as a golden fixture” was recorded 2026-10-12T07:30:37Z.
- Five byte-frozen TEST pages: `CORE1`, `CORE1A`, `CORE1B`, `CORE2A`, `CORE2B`. **No `CORE2`**: `manifest.json` explicitly has `output_roles=[CORE1,CORE1A,CORE1B,CORE2A,CORE2B]`, `selection.core2=[]`, and `bank_refs=[]`. The authored subject is TEST; this is *not* an authentic SOF IMO source-question Core2 oracle.
- `snapshot-lock.json` pins five SHA256s, renderer `render_core/2`, mode `PAGES`, 0 reference-depth gaps, original render digest `ad02fef42f0d505a`, semantic digest `9497e294361663f2`, source run `38215683516` and source commit `f87d2f627e3f05476d39fb04d7f26e453661dc68`. Exact Core1A SHA256 `c58a4aec2b4318eaad83ffac236b6287ff2cdcb4532aa83aa4d3cd44b2d1b004`.
- `tests/test_imo182_owner_golden_snapshot.py` declares byte-lock assertions and uses `render_core.build_report(...,held_to="REFERENCE")` to check regeneration equals frozen per-role HTML **after replacing only the manifest-specific 16-character digest**. Source inspection of that test is not a new test execution. Fixture recipe: `python Shared/tools/build_golden.py --id G-IMO-G9-FIVE-CORE-20261012 --check` at the pinned tree.
- Exact `snapshots/core1a.html` carries `data-blueprint-ref="BP-CORE1A-CONSTRUCTION@1.8.0"`, `data-g9-cu` and real `data-g9-step="TC-01"...TC-04`, staged `data-g9-stage-mode="cumulative"`, native attempt and derivation-bridge markup. HTML source inspection verifies structural provenance; no independent visual/browser run was executed for this review.

## Concrete teaching quality to adopt without copying unrelated mathematics

Canonical fixture's *authored* mathematics is **universal divisibility of three consecutive integers by 6**, not Q003's original **input–output numerical-pair exception**. The pedagogical architecture, not its numbers, should transfer:

1. One clear inferential decision per `construction_units[]`: the universal claim follows from exhaustive remainder classes, not sampled examples. Q003's distinct unit must construct *and test* one consistent numerical relation across ordered pairs, then justify the sole exception.
2. Four `teaching_path` stages `TC-01..TC-04`, each with action/why valid/output. Q003 must have its own directly justified steps (form a candidate relation, test against multiple pairs, falsify exceptions, independent changed-case check), not borrow the divisibility proof's academic content.
3. Semantically necessary `TABLE_OF_VALUES` representation `REP-TEST-CORE1A-QUAL-G9-RESIDUE-TABLE`, staged as `DIV-STEP-PARITY`, `DIV-STEP-RESIDUES`, `DIV-STEP-COPRIME`. Q003 should use a question-appropriate progressive pair-rule table or stage sequence, with explicit waiver only if no representation helps; not paragraphs masquerading as a lesson.
4. `relation_refs`, model contract/assumptions, a compact worked anchor, a named wrong path/diagnose/repair, and an independent check/exit, followed by navigation into its question or practice. Source question must remain distinctly source-labeled; authored lesson must remain distinctly AUTHORED.

## Revised benchmark obligations against task aim

| Task | Outcome | Exact comparator and oracle | Limit |
|---|---|---|---|
| 183-T2-G2-W1 | O1 | Actual Q003 original-source `BP-CORE2-SOURCE-QUESTION@1.11.0` native `Shared/tools/render_core.py` build; source component SHA, typed attempt/protected hint and receipt | Five-role golden has **no CORE2**. Keep `G-CORE2-R2` as relevant Core2 source-question exemplar |
| 183-T3-G2-W1 | O3 | Actual Q003 Core2 versus native `G-CORE2-R2`, with structural + viewport + behavior delta | No page/fixture execution or Owner QRT decision yet |
| 183-T4-G2-W1 | O2 | Q003-specific native `BP-CORE1A-CONSTRUCTION@1.8.0` against **Owner-designated five-role Core1A snapshot**: concept route, step warrants, staged representation, equation/ref, worked anchor, repair, changed-case exit; supplement with `G-MATH-LINEAR-CONSTRAINT` technique if useful | No automatic curricular/academic acceptance; cannot copy unrelated divisible-by-6 content |
| 183-T5-G2-W1 | O3 | Honest source-safe QRT packets and same-renderer A4 after actual generated pages | Snapshot pins do not grant QRT (0/28), Core2A H3, exam rights, A4, merge or learner release |
| 183-T6 | O1/O2/O3 | Scale only after first faithful native page and native matched construction verified | No task-count progress claimed |

**Current result:** Evidence-review task completed; actual product task remains **BLOCKED** under v3.1.0 because Q003 has no observed native renderer output; this source review is not a substitute for building. The old standalone Q003 preview remains rejected. No source, HTML, golden or blueprint file changed by this review. Product native Core2 0/68, accepted Core1A 0, Owner QRT 0/28. No native test or snapshot/browser execution was performed for this reference-only audit.
