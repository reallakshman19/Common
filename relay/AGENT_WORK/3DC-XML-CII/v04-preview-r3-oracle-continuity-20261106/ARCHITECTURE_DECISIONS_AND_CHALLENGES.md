# v0.4 Step 4 — preserved decisions, rejected shortcuts and surviving wrong cases

**2026-11-06 · PUBLIC-SAFE · Oracle-prepared / SELF_ASSESSED.** [Owner native Issue #1](https://github.com/reallakshman19/3D_Converters_v0.4/issues/1) and [Common Oracle Protocol](https://github.com/reallakshman19/Common/blob/b4546c3f586b93dbe875ad6a531abc85f701c583/skills/agent-work/oracle-continuity/PROTOCOL.md) govern scope and continuity; this document grants no new authority.

## Decisions to preserve

| Decision / status | Rejected shortcut and why | Surviving wrong case | Discriminator / action |
| --- | --- | --- | --- |
| D1 Owner scope: only staged-wall index and per-build cache for slow v0.4 Preview | Redesign UI/worker, change writer, strict-line authority, engineering master values or defaults to achieve speed | Faster output achieved by silently deleting data or bypassing review | Compare original/PR2/PR3 Preview diagnostics and byte-identical outputs; reject changed engineering semantics; separate other fixes |
| D2 PR2 index preserves ordered evidence, duplicates and provenance | Deduplicate source evidence by name or reorder it | Same wall thickness but wrong witness/DTXR source | Fixture with duplicate staged evidence, exact array order and provenance |
| D3 PR3 cache is invocation-local with content and exact-context validity; clone results | Object-identity cache without content check | Same object edited 10→20 returns stale cached 10, or shared ranking mutated by caller | Same-object weight edit and same-array Piping Class edit plus fresh-build negative; source/test at `027c5e32` |
| D4 Same effective input means **hydrated** current master arrays, mapping/defaults/overrides, not filenames or localStorage | Persisted config has stripped master arrays; accidental `Coversheet` gives apparent low-cost run | A valid-looking 0-row Preview “passes” speed test | Inspect `Linelist` sheet, 8 real rows, master counts, field keys, config digest and 31/268 Preview rows |
| D5 Enriched converter-input XML and final exported XML/CII are separate gates | Treat identical unmodified writer source or same XML parsed tree as byte-parity proof | Preview-derived wall/rating fields change in converter-input despite identical engine module | Repeat baseline and compare raw bytes, diagnostics, final Pyodide XML and CII separately |
| D6 Corrected script evidence must be append-only | Rewrite `SHA256SUMS.txt` without explaining stale value | Reviewer cannot reproduce delivered source | Preserve old manifest, specify four codec corrections, regenerate six hashes and compare |
| D7 Review authority is separate | Incumbent Oracle supplied R2 comparator and also audited uploaded artifacts | A self-review is labelled conflict-free 92/100 | Different non-author reviewer reads exact PR diff and original sources; no contributor claim to final IR |
| D8 Original material/pressure semantics outside performance PRs | Force `DSS`/ `LTCS` to an unapproved code; scale all pressures blindly | 114 nodes get wrong grade, or an intermediate XML downstream consumer honors `pascal` and scales wrongly | Owner engineering material basis and pressure consumer trace as separate task; protected release |
| D9 Owner controls merge; candidate fixture limited to testing | Promote reconstructed config to “historically used Owner config” or accept one speed sample as production qualification | Wrong setting gets engineering sign-off | Explicit fixture-only attestation or genuine hydrated capture, corrected benchmark, independent review, Owner merge decision |

## Important exact observations and conflicts

- **Four outputs can be equal and still semantically imperfect.** Uploaded R3 XML and CII equality is strong *regression* evidence on one reconstructed fixture; it says nothing about whether the selected material codes, design-pressure rounding or full CAESAR II vendor import are correct. A CII syntax/census check also does not independently prove stress loads.
- **Zero-row speedups are unsafe evidence.** In `step4_interactions_benchmark.json`, all rows say `previewRowCount=0`, `ratedRowCount=0`, `weightMatchMatchedCount=0`. This is a measurement bug. Source Preview's `branchRows/nodeRows` contains 31/268 on the actual Run. A “3.42x full UI” statement needs correction; computational timing can survive as narrower reported evidence.
- **Cold vs warm and changed config are distinct.** Browser contexts must be isolated across repeats; a rebuilt Preview after a mutable master edit must not retain old decisions. No persistent stale result is justified by shared source hashes.
- **Pressure source/target:** original PSI116 XML header retains `pascal`; Line List has `kPa(g)`; final CII `#$ UNITS` includes `KPa`. The final CII numerical example `13001.0` does not imply a 1000x error in that path, but note source 13001.3 and intermediate metadata mismatch. Engineering acceptability remains unresolved.
- **Material source/target:** the [baseline material policy](https://github.com/reallakshman19/3D_Converters_v0.4/blob/b856ddd01a66c0dbee8c519bfd0bd8118d1f3979/docs/xml-cii/material-code-fuzzy-authority.md) explicitly withholds class fallback for nonblank unresolved process material. The map's `S32803` alias to `S31803` is curated in existing source/tests; it does **not** establish equivalence for generic `DSS` or `LTCS`. Treat 114 nodes with zero material number as unresolved engineering risk.
- **No actual scoped Owner approval observed:** all eight candidate override maps are empty. They may be intended, but the original browser session is unavailable. Permit controlled benchmarking under candidate label, not production engineering acceptance.

## Fixed near-term done-list (do not expand to endless review rounds)

**R4 local test-harness correction, not production PR repair:**
1. Repair Preview API signature and capture full staged JSON; assert 31 `branchRows`, expected `nodeRows`, and repeatable provenance.
2. Exercise actual app Build/Rebuild and Fetch/Apply Rating UI event path with nonempty row/state witnesses; distinguish no-op from meaningful actions.
3. Exercise Weight Match with actual summary and at least one applicable positive or explicit N/A; preserve candidate counts and selected evidence.
4. Repeat baseline/PR2/PR3 with clean/warm controls and real BM2 candidate config; report valid medians/sample counts and browser build/environment, no p95 claim from three runs.
5. Correct script checksum manifest and record original-vs-fixed scripts/digests without changing production code.

A genuine new unsafe-accept observation (wrong output, stale engineering decision, bypassed release) blocks regardless of list. Other unrelated improvements become separately scoped follow-ups.

**R5 independent acceptance:** after R4 and Owner fixture authority, one non-author reviewer checks exact PR2/PR3 heads, source diff, original regression invariants, R3 ZIP and R4 UI evidence. Score per project bar >=92/100 and >=17/20 each dimension; disclose actual author/source exposure. A passing score still does not authorize merging. Do **not** rerun a dozen unbounded repair rounds merely because a reviewer requests unrelated extra unit tests; use the fixed list and explicit Owner scope decision.

## Alternative next moves if R4 cannot be qualified

- **Recommended:** accept the sound byte-parity evidence as scoped, repair **harness only**, then review; this preserves the sizable claimed PR3 compute benefit.
- **If Owner's full UI trial reveals no real speed gain:** park PR3 (or remove only ranking memoization in an explicitly authorized new scope), preserve independently useful PR2, compare objectively; do not force a speed claim.
- **If the reconstructed fixture proves nonrepresentative:** preserve R3 as candidate-only evidence and run an authentic hydrated Owner configuration separately. Do not rewrite past results as FAIL or PASS outside their scope.

## Two connected outcomes

Next D1 is a **trustworthy, source-bound Step 4 UI benchmark and repaired custody manifest**. It is consumed by D2, a **scored independent PR-chain qualification and Owner release decision**. Neither can substitute for separate material/pressure engineering acceptance.
