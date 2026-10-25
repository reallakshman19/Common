# CIIFR Geometry — project concept, Owner outcome and product mental model

**CIIFR-specific successor Oracle knowledge · 25 October 2026 · PUBLIC_SAFE / PREPARED / NOT_CUTOVER.** Based on actual [XCU Owner #166](https://github.com/reallakshman19/XML_Compare_Utilities/issues/166), source at G1 [PR #174 exact R1 head `9936d4078fb7f837ffe6f46805241efdb7bbc0e8`](https://github.com/reallakshman19/XML_Compare_Utilities/pull/174), [Method C engineering contract](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/docs/METHOD_C_ENGINEERING.md), and the **latest Owner execution-first correction** in [#166 comment 6400403221](https://github.com/reallakshman19/XML_Compare_Utilities/issues/166#issuecomment-6400403221) and updated [G2 #177](https://github.com/reallakshman19/XML_Compare_Utilities/issues/177). No original private bytes are attached. This is **Oracle-authored source interpretation**, not Owner-accepted engineering truth or release.

Read alongside [Architecture and complex logic](ARCHITECTURE_COMPLEX_LOGIC.md), [Decisions and challenges](ARCHITECTURE_DECISIONS_AND_CHALLENGES.md), and [Oracle handover](ORACLE_HANDOVER.md). The four documents are our CIIFR-specific equivalents of the *structural quality* of the 3DC golden fixture, not copies of 3DC's technical subject.

## 1. WHY — the Owner's actual requested improvement

[Owner's current request on XCU #166](https://github.com/reallakshman19/XML_Compare_Utilities/issues/166): integrate the existing **CII Find & Replace VNext · Standalone → Geometry** with **Method C** and the adjacent **XMLv1.1 F05 prototype** to show a *linked correspondence table and two side-by-side SVG canvases* for topology-based smart candidates, manual anchors or both.

The actual question is **which original physical pipe NODE or original ELEMENT on TARGET might correspond to this selected SOURCE geometry**, and *why*, even under partial rotation information, duplicate signatures, mismatched path lengths and missing physical nodes. The workbench needs to show originals and honest uncertainty, not produce a reassuring but fabricated one-to-one match. The Owner should be able to inspect SOURCE and TARGET0 at the same visual metric scale, select a node in one SVG or row and see the evidence on the other, inspect residuals and alternate candidates, then export audit evidence without silently changing the CII model.

This is a **read-only examination feature**, not a new command path into the existing Normal tab or Writer2. The User's expression “both combined” eventually means evidence-combination views, **not** implicit authority to merge geometry guesses into engineering output.

The updated Owner rule is **“no blocker unless unsolvable; no gates unless not solvable by Oracle”**: resolve reachable source/test questions directly; a failed browser in one environment is a limit on that test, not a veto on all disjoint work. [#166 comment](https://github.com/reallakshman19/XML_Compare_Utilities/issues/166#issuecomment-6400403221). Preserve actual permissions, original-byte requirements, protected writer controls and trustworthy release claims. This **supersedes** earlier blanket G2 code HOLD language in historical notes, without accepting G1's pending browser claims.

## 2. One Owner-visible user journey (and the limits)

```text
Open served VNext → choose original SOURCE S1.CII + TARGET0 T.CII
  → immutable Uint8Array snapshots with SHA provenance
  → original v14 CII CONTROL / 15-row ELEMENTS / physical NODE graph
  → G1 manual anchor 3910 → 875 and Method C experimental rigid registration
  → original physical NODE candidates + signed xyz residual / segment-only exceptions
  → correspondence ledger, complete alternatives/collisions, two separate SOURCE/TARGET SVGs
  → linked row/keyboard/canvas selection, XZ/YZ/XY true mm + ISO NON-METRIC, shared zoom
  → locally export source-hash-bound read-only JSON/CSV/SVG evidence (not Writer)
  → return to Normal without changing original SOURCE/TARGET0 or Normal decisions
Later, G2 disjoint: independent pose-free topology proposals + Manual/Topology/OR/AND
Later, G3: XMLv1.1 F05 source locator/receipt evidence, not new physical NODE authority
```

[Actual VNext served entry](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/docs/cii-fnr-vnext.html); [G1 controller](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-fnr-vnext/geometry/ui.js); [paired view source](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-fnr-vnext/geometry/scene.js).

## 3. Vocabulary a successor must not collapse

| Term | Positive meaning | It must not be confused with |
| --- | --- | --- |
| Original CII member and **raw SHA** | Immutable SOURCE/TARGET0 byte custody and exact content identity; optional trusted expected digest verified separately | A filename or a hash computed on modified customer input |
| Original physical **NODE** | Original CII engineering node ID plus member/SHA and real incident original ELEMENT records | `NODENAME`, arbitrary coordinate projection, label equality or inferred target |
| Original **ELEMENT** | 15-row signed original ELEMENTS record, ordinal, original endpoints and witness | A generated virtual NODE at its internal interpolation point |
| Registered pose | Proper rigid geometry transformation with scale 1, determinant +1, model of anchor observations | Owner-authenticated correspondence or Writer authorization |
| XYZ near candidate | Proposed original TARGET physical NODE within independent coordinate tolerances **after** pose | Unambiguous/qualified physical identity |
| `SEGMENT_ONLY` | Nearest interior projection on a **real TARGET ELEMENT** with witness | Physical TARGET NODE match, split/rewrite instruction |
| `Topology` before pose | Pose-free local graph evidence; spatial residual `NOT_EVALUATED` | Hidden zero residual or calibrated mm comparison |
| `Manual`, `OR`, `AND` | Views and combinations of *visible candidate sets with provenance/conflict reporting* | Force-picking a single target or applying geometry to TARGET1 |
| `SHA_COMPUTED` / `PINNED_SHA_VERIFIED` | Calculated local digest versus comparison to provided trusted expected SHA | Proof that any user upload is an original benchmark |
| Candidate / Browser / Independent / Owner accepted | Different levels of evidence or authority for precisely scoped claims | One green boolean and automatic merge |

Source: [Method C engineering](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/docs/METHOD_C_ENGINEERING.md); [graph builder](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-workspace-method-c-original-geometry.js).

## 4. Why the four stages are architecturally distinct

**G1 — manual Method C + dual SVG.** Work directly from original CII physical graph, preserved manual anchor hypotheses and a registered-only proximity/segment ledger. Reuse existing Method C parser, pose, candidate and SVG functions rather than rewriting the core. Its user-visible feature is a *real VNext tab* using original uploads. Draft [PR #174](https://github.com/reallakshman19/XML_Compare_Utilities/pull/174) is published but not merged.

**G2 — independent pose-free topology and Boolean views.** A separate graph-shape adapter should produce candidate sets even with no registered pose; it must retain duplicates/target collisions, provenance and `NOT_EVALUATED` residual. [Current authoritative G2 #177](https://github.com/reallakshman19/XML_Compare_Utilities/issues/177) explicitly permits Oracle source/interface/falsifier work and an *actually authorized worker's separate disjoint source-only draft* now. G2 must not edit G1-owned served HTML/shared app or claim a merged G1+G2 product. No G2 recipient has yet been verified or activated in [Common CURRENT](https://github.com/reallakshman19/Common/blob/main/oracle-cycles/ciifr/CURRENT.json).

**G3 — optional F05 XML evidence bridge.** The separate [XMLv1.1 F05 draft PR #157](https://github.com/reallakshman19/XML_Compare_Utilities/pull/157) can later attach original section/record/field locators if its source hash, schema, ordinal and receipt are verified. A Python loopback prototype is not itself a production physical CII identity oracle; no transformation/writer entitlement comes from a locator.

**G4 — export and robust integration.** Consolidate complete source- and candidate-hash-bound JSON/CSV/SVG evidence, negative-case UI, async races, mirrored served resources and regression proof, without changing Normal/Line/Config/Writer behavior. Not a claim that every G4 acceptance criterion has been achieved by G1.

## 5. What demonstrably exists at this checkpoint

As read from live GitHub on **25 Oct 2026**, XCU `main` is `c823f0c0edbeb315c07fa2911390dc781968146f`. G1 [draft PR #174](https://github.com/reallakshman19/XML_Compare_Utilities/pull/174) is **open/unmerged**, head `9936d4078fb7f837ffe6f46805241efdb7bbc0e8`. Direct source inspection found four authored/served module-pair Git blob matches, explicit SVG keyboard selector, local versus expected SHA language, and preserved CSV/nonconflict imports in VNext. Those are **code observations, not served product qualification**.

[Builder-native R1 return](https://github.com/reallakshman19/XML_Compare_Utilities/issues/169#issuecomment-6398999288) reports original S1/T SHA verification, 27/27 scoped Node tests, 9/9 controlled *synthetic* Chromium DOM tests, same pre-existing Normal assertion failure on base/main/head and a blocked **served application** browser (`ERR_BLOCKED_BY_ADMINISTRATOR`). [Previous independent issue #175 verdict](https://github.com/reallakshman19/XML_Compare_Utilities/issues/175#issuecomment-6397228570) is PARTIAL at the **older** head `a59f479...`, not an approval of R1. GitHub showed **zero exact-head G1 check runs** when queried. Current issue #175 explicitly directs Oracle to attempt available source/native/T parser/browsers first. Do not silently promote synthetic DOM, original NODE expectations, or hashes computed in someone else's session to independent original-file PASS.

## 6. Two connected useful improvements after this checkpoint

**First:** Oracle pursues original TARGET T full-byte/native `parseCii` intake compatibility and genuinely served S1/T B1–B4 checks at exact PR head, changing runner if the browser is blocked. Diagnose the smallest actual failing seam; secure non-author review for the portion requiring independence, and Owner trial before G1 engineering release.

**Second, in parallel where disjoint:** Oracle examines topology signatures and an ambiguity/collision counterexample under [G2 #177](https://github.com/reallakshman19/XML_Compare_Utilities/issues/177); a separately qualified owner of disjoint files can publish G2 source-only tests/adapter without waiting for G1 browser, while protected integration/Writer remains unapproved.

A third later connected improvement is G2's served-app Manual/Topology/OR/AND integration after G1 seam compatibility and original acceptance are established. Do not present these as completed outcomes.

## 7. Non-negotiable safety, source and custody

Original S1 SHA-256 expected from author report: `9a9cb14db4c13f5aac41cc74a60e7e528722eb5003d09f07192762ab6bfb1a2b`, 108,330 bytes. Original T expected: `abfa3ffc9281fe75d4170b2d885d554cb1f120dadedae7c7ab609548b63cc060`, 2,866,002 bytes. **Those are published expected receipts, not independently recomputed by this Oracle here.** Full T bytes were unavailable to the current Oracle's source connector. The separate WP8 independent original benchmark requires an immutable second checkout and cannot be replaced by author-only derived JSON.

Protect original bytes, all source-owned alternatives and collision witnesses, physical NODE vs ELEMENT distinctions, explicit no-Writer/Apply/TARGET1 boundary, and separate Old-Head/New-Head verdicts. Every successor must reread live PR, source, current issue and Cycle rather than assuming this snapshot persists.

**Status:** CONCEPT SOURCE-GROUNDED / SELF-ASSESSED; G1 accepted engineering release **NOT_PROVED**, G2 disjoint source work **PERMITTED UNDER REAL NATIVE AUTHORITY**, Oracle successor **NOT_ACTIVATED**.
