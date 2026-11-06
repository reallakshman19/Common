# v0.4 Step 4 — difficult architecture, authority and exact-byte path

**Technical knowledge transfer; source-pinned, 2026-11-06; SELF_ASSESSED.** Read this alongside [concept](CONCEPT_NOTE.md), [decisions](ARCHITECTURE_DECISIONS_AND_CHALLENGES.md), and [frontier](ORACLE_HANDOVER.md). Lines and APIs are from v0.4 exact heads, not generic XML-to-CII assumptions.

## 1. Two connected output boundaries

```text
Owner original PSI116 XML + staged JSON + imported master workbooks + mappings/overrides
      -> hydrated supportConfigJson (all master row arrays present)
      -> Step 4 buildStrictLineAuthorityCorePreview
          -> wall evidence authority -> material code authority -> rating authority
          -> branchRows/nodeRows + diagnostics/provenance
      -> enrichStandaloneXmlForRun / applyStandaloneProcessParity
          -> xmlCiiDryRunPreview (Preview-derived values used in Run)
          -> converter-input enriched XML (713,474 bytes on GLRD candidate)
      -> runXmlCii2019Workflow / workflow-service / standalone engine
          -> browser Pyodide Python stage / bend-radius policy
          -> final exported enriched XML (LF 687,205 bytes)
          -> CII 2019 formatted file (997,859 bytes)
```

The exact production entry points are [Preview wrapper at PR3](https://github.com/reallakshman19/3D_Converters_v0.4/blob/027c5e3234d3a88c43375228d9a37f3493490e8a/tabs/xml-cii-2019-standalone/ui-adapted/xml-cii-adapted-preview-dryrun.js), [Run parity](https://github.com/reallakshman19/3D_Converters_v0.4/blob/027c5e3234d3a88c43375228d9a37f3493490e8a/tabs/xml-cii-2019-standalone/xml-cii-standalone-run-parity.js), [workflow API](https://github.com/reallakshman19/3D_Converters_v0.4/blob/027c5e3234d3a88c43375228d9a37f3493490e8a/tabs/xml-cii-2019-standalone/xml-cii-workflow-api.js), [service](https://github.com/reallakshman19/3D_Converters_v0.4/blob/027c5e3234d3a88c43375228d9a37f3493490e8a/tabs/xml-cii-2019-standalone/xml-cii-workflow-service.js), and [Pyodide engine](https://github.com/reallakshman19/3D_Converters_v0.4/blob/027c5e3234d3a88c43375228d9a37f3493490e8a/converters/xml-cii-2019-standalone/engine.js).

**Crucial implication:** writer/engine source blobs can be unchanged across heads while enriched XML differs if Preview computation changes. Source-identity of five writer modules was a useful scope check, **not** acceptance. Exact bytes and diagnostics must be checked at each output boundary.

## 2. PR #2 — staged-wall evidence index, not a new authority

[PR2 two production files](https://github.com/reallakshman19/3D_Converters_v0.4/pull/2/files) are `xml-cii-adapted-preview-wall-evidence.js` and `xml-cii-adapted-preview-bore-wall-authority.js` under `tabs/xml-cii-2019-standalone/ui-adapted/`. The former avoids repeated staged JSON parse/walk for each branch by constructing one invocation-local index; the latter uses it within wall/bore evidence review. The contract is preservation of branch owner resolution, *ordered duplicate evidence*, DTXR provenance, source identifiers, and invalid/empty behavior. A de-duplicating Map that reorders duplicate witnesses is unacceptable even if it is faster.

The isolated algorithm test on GLRD preserved 1,141 staged evidence records in original order and reported around 4.5x faster **for this one operation only**. PR2's whole Preview timing in the later flawed direct-function benchmark is essentially flat; never transfer the isolated speed factor to complete Step 4.

## 3. PR #3 — per-build Piping Class/ranking reuse and the repaired stale-cache counterexample

PR3 is [stacked on PR2](https://github.com/reallakshman19/3D_Converters_v0.4/pull/3) and introduces `xml-cii-adapted-preview-per-build-cache.js`. [The wrapper](https://github.com/reallakshman19/3D_Converters_v0.4/blob/027c5e3234d3a88c43375228d9a37f3493490e8a/tabs/xml-cii-2019-standalone/ui-adapted/xml-cii-adapted-preview-dryrun.js) creates a **fresh cache per `xmlCiiDryRunPreview` invocation**, sends it through strict line and rating computations, and releases it afterward. It reuses a 10,699-row Piping Class index and ranking results only for matching exact primitive contexts/options and config identities. Results are cloned so a consumer cannot mutate a cached candidate. An unsafe clone or unsupported input falls back to recomputation.

**Historical defect / repaired negative:** earlier PR3 `204f3248` could return a stale ranking when an agent mutated the same in-memory master/config object. The current `027c5e32` added content signatures, hit-path invalidation and nine adversarial Node tests for this case. The local agent reported 9/9 cache tests PASS; this is not a substitute for real source+output parity. Any later cache edit must preserve a same-array master-row edit and same-object setting edit as fail-different tests.

## 4. Imported master custody is not localStorage custody

The [config store](https://github.com/reallakshman19/3D_Converters_v0.4/blob/b856ddd01a66c0dbee8c519bfd0bd8118d1f3979/tabs/model-converters/core/config-store.js) intentionally strips `linelist.masterRows`, `pipingClass.masterRows`, `material.mapRows` and `weight.masterRows` on persistence. The [master-preserve patch](https://github.com/reallakshman19/3D_Converters_v0.4/blob/b856ddd01a66c0dbee8c519bfd0bd8118d1f3979/tabs/model-converters/xml-cii-master-preserve-patch.js) hydrates the active working session. Comparing with a saved localStorage config alone is an invalid effective-input comparison.

The first recovered local workbench config erroneously selected Excel sheet `Coversheet` (15 unmapped rows), because a `[data-xml-cii-sheet]` handler was bound in the retired shell, not the popup import shell. The local agent then built candidate config SHA-256 `706fed5b35e7f5449b44bc3237ae0b62339c8f28593f46f800dcf2a2a78ed001` with the correct `Linelist` worksheet: 8 real Line List lines / 16 normalized mapped rows; 10,699 class rows, 1,595 weight rows, 383 material rows and **eight empty overrides**. The reconstructed candidate is *not* attested as the Owner's historically active configuration. Preserve that label and ask for the smallest Owner decision only about its authority.

## 5. Exact-byte artifacts and domain limits

The **private evidence archive**, externally held by Owner, has SHA-256 `53309e54d3c79146bdc827cecdede635c0b38c690d62731a241d9d26d4a58f97`, 3,113,211 bytes, 66 ZIP entries; corruption test PASS. The outgoing Oracle recomputed:

| Group | Same bytes per item | SHA-256 (entire digest) | Number |
| --- | ---: | --- | ---: |
| Converter-input XML | 713,474 | `71d761444ee488dde624e79804bba88cd20aa4489be7d920cc723c32750204e7` | 9 |
| Pretty-printed diagnostics JSON on disk | 6,945,069 | `676dbe46ad8ce18c6fb3395310b6b9aab30b47a58ee76c5ab5ac5bbfa91b27a2` | 9 |
| Native Python final XML (Windows CRLF) | 703,548 | `39bfb79c349892bf52587020f0bb1c9014c54c6307a8bcd13567fa89519546cb` | 4 |
| Browser Pyodide final XML (LF) | 687,205 | `922efb9d62a74e87850b33226cc66e16d3e861d42c81d8f233af7a44e5d44e92` | 8 |
| Browser Pyodide CII | 997,859 | `41aea0cad32c6cc8f6ed2c9d60db1f00b8e7c3e6030a06c62b71b231b78a18f4` | 4 |

The canonical compact sorted-key diagnostics hash, **not** the pretty-printed on-disk hash, is `1116cba49128b5bd799dceb648715ddc681172436a898b215d3ce4bde9ca421f`. Re-serialization reproduced that canonical digest; do not mark the two distinct encodings a mismatch. There are 31 branch Preview rows, 268 node Preview rows, 6,176 reported authority comparisons with zero mismatches. Native final XML has 31 branches and 994 nodes; 202 source GASK nodes were dropped, while other component counts matched. These observations establish byte parity for **candidate inputs**, not correctness of material or CII physics.

The Windows output has exactly 16,343 CRLF pairs. Removing those CR bytes produces the exact LF browser file; the size reduction is 703,548-16,343=687,205 bytes. Do not compare a native CRLF output directly to browser LF bytes and allege code regression.

## 6. Material and pressure transitions where identical bytes can remain wrong

The Line List's nonblank process material `DSS` or `LTCS` takes precedence over Piping Class according to [material authority](https://github.com/reallakshman19/3D_Converters_v0.4/blob/b856ddd01a66c0dbee8c519bfd0bd8118d1f3979/docs/xml-cii/material-code-fuzzy-authority.md); an unresolved nonblank process value **does not fall back** to a guessed class code. Four branches / 114 nodes remain with `MaterialNumber=0` and no resolved `MaterialCode`. Code 338's `A790-S32803` vs `A790 UNS S31803` treatment is an **explicit curated alias in baseline source and tests**, not a license to assign code 338 to arbitrary `DSS`. The two material trade abbreviations need independent engineering decision; no auto-alias or retroactive approval in PR2/3.

The original PSI XML header says `<PressureUnits>pascal</PressureUnits>`; Line List's design pressure is labelled kPa(g). Enrichment stores `Pressure1=13001` rather than the worksheet's 13001.3; the CII generator writes `#$ UNITS` with KPa pressure and stores `13001.0`. The reported CII path therefore **does not show a thousandfold pressure scale shift**, but intermediate XML metadata and numeric rounding are real unresolved engineering semantics. Distinguish textual CII trace from independent CAESAR II vendor ingestion.

## 7. Why the purported UI benchmark is not an UI benchmark

The private package's `scripts/benchmark_step4_interactions.py` imports functions in a blank probe page rather than clicking the app UI. It passes no staged JSON to `xmlCiiDryRunPreview`, reads nonexistent `preview.rows` instead of `branchRows/nodeRows`, calls `applyPreviewRatingAuthority(preview2?.rows || [], config, sourceXml)` instead of **one options object** `{xmlText,config,stagedJsonText,result}`, and reads nonexistent Weight Match fields `matchedCount/matches` instead of `summary.issueCount/candidateCount/finalizedCount`. Consequently **every benchmark run reports previewRowCount=0, ratedRowCount=0 and weightMatchMatchedCount=0** while the true Run diagnostics show 31 branch rows. `fetchRatingMs=0` times a no-op. It is **not a qualified full UI benchmark**.

The direct-function medians are still a *possible compute speed signal*: cold 13.575s main vs 3.9715s PR3, warm 12.8087s vs 4.1365s, Run parity separate 19.128s vs 10.6733s on candidate GLRD. Do not claim `3.42x UI improvement` or nonzero Fetch Rating validation without corrected DOM click and row/state witnesses. Three timings per head do not establish reliable percentiles.

## 8. Known script custody defect

`scripts/SHA256SUMS.txt` correctly matches **5 of 6** entries. The packaged `verify_xmlcii_enriched_prepost_r2.py` changed four invalid codec spellings `utf8-sig` to `utf-8-sig` after the manifest was generated. Preserve old manifest, publish an explicit corrected digest/diff, rerun helpers, and never silently call it 6/6.

## 9. Discriminating next test

The successor's first source-grounded observation should contrast real 31-branch Preview data with the broken zero-row benchmark, then route a bounded *test-harness-only* repair that invokes the actual UI interactions and records nonempty branch/node/rating/weight witnesses plus exact-input digests and repeated time samples. **No production/writer/master/policy edit is authorized by this knowledge packet.**
