# CIIFR Geometry — architectural decisions, alternatives and falsification register

**Knowledge status:** CIIFR Oracle source analysis / **SELF_ASSESSED**, not engineering acceptance. **Snapshot:** XCU `main=c823f0c0edbeb315c07fa2911390dc781968146f`, G1 [draft PR #174 head `9936d4078fb7f837ffe6f46805241efdb7bbc0e8`](https://github.com/reallakshman19/XML_Compare_Utilities/pull/174), Owner execution-first directive in [#166 comment 6400403221](https://github.com/reallakshman19/XML_Compare_Utilities/issues/166#issuecomment-6400403221), G2 updated [#177](https://github.com/reallakshman19/XML_Compare_Utilities/issues/177). Historical decisions in issues/comments are not automatically current; a new Owner revision prevails on its declared scope. The **3DC golden fixture supplied document structure, not CIIFR claims**.

Use [Concept](CONCEPT_NOTE.md) for WHY, [Complex architecture](ARCHITECTURE_COMPLEX_LOGIC.md) for code path, [Handover](ORACLE_HANDOVER.md) for current next actor and receipt.

## 1. Decisions and the rejected shortcuts

| Design question and source | Chosen approach and why | Rejected tempting shortcut and surviving risk | Discriminating evidence |
| --- | --- | --- | --- |
| **Authority of a physical correspondence** — [#166](https://github.com/reallakshman19/XML_Compare_Utilities/issues/166) / [Method C](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/docs/METHOD_C_ENGINEERING.md) | Original NODE/ELEMENT witnesses with member/raw hash/component, all alternatives, `REVIEW_ONLY`. Identity qualification and Writer are separate. | NodeName equality, nearest station as NODE, distance-only one-to-one match; fake certainty. | Source 4060 interior ELEMENT 900→905 is **SEGMENT_ONLY**, zero physical NODE match. |
| **Parser source of truth** — [original geometry](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-workspace-method-c-original-geometry.js) | Raw `Uint8Array` SHA, CONTROL, native units/COORDS, complete signed 15-row ELEMENTS, actual physical node/incident witness. | Derived Excel/CSV/golden map, deduplicating or accepting corrupt 15-row record; aliases original topology. | Change pointer/CONTROL/signed vector independently and insist on exact reject, same original hash. |
| **Registration observability** — [registration code](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-workspace-method-c-registration.js) | One anchor translation-only; two anchor twist unknown; 3+ noncollinear numeric fit remains untrusted physical identity. | Pretend unit-scale numeric fit proves source-anchored match, or allow reflection/scaling. | Rotate same source around single anchor; candidate changes without contradicting anchor. |
| **Source/target candidate enumeration** — [candidates](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-workspace-method-c-candidates.js) | Independent signed XYZ thresholds on real TARGET physical nodes; retain all choices and target collisions; separate segment-only projection. | Global ALL fallback, forced unique assignment, silent elimination of duplicates, bounding box ⇒ accepted identity. | Duplicate physical target alternatives / contested target retain status and witnesses. |
| **G1 visual structure** — [paired scene](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-fnr-vnext/geometry/scene.js) | Two distinct SOURCE and TARGET SVG DOMs, common metric viewBox in XZ/YZ/XY, ISO marked NON-METRIC, linked row/keyboard/zoom. | Two snapshots of same overlay, separate arbitrary auto-fit scales, SVG `node.click()` for keyboard. | DOM tree identity not equal, SOURCE marker absent from TARGET, same viewBox after pan/zoom, Enter/Space functional. |
| **Hash provenance** — [G1 R1 return](https://github.com/reallakshman19/XML_Compare_Utilities/issues/169#issuecomment-6398999288) | Always compute raw digest; only call `PINNED_SHA_VERIFIED` when a **trusted supplied** expected SHA matched. | Hardcode S1/T golden hashes in general-purpose customer upload, or call any computed hash original-authenticated. | Modify one byte: `SHA_COMPUTED` may still be valid label; explicit mismatching expected digest ⇒ `ORIGINAL_SHA256_MISMATCH`. |
| **Async evidence and exports** — [G1 controller](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-fnr-vnext/geometry/ui.js) | Epoch/snapshot invalidates old row, side-selection, SVG and CSV/JSON/SVG export on source/anchor/tolerance/projection changes. | Filename-based reuse or returning stale Promise paints old candidate on new source. | Delay digest; swap SOURCE and resolve old first; zero stale rows/exports. |
| **Normal versus Geometry coupling** — [shared VNext app](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-fnr-vnext/ui/app.js) | Reuse immutable shared SOURCE/TARGET0 snapshots but isolate Geometry read-only mount from Normal Writer proposals; preserve #172 CSV cleanup/nonconflict state. | New independent file cache that disagrees with Normal, or skip Normal parse guard globally just to enable Geometry. | Run real file inputs + Normal→Geometry→Normal; confirm untouched original bytes and existing approval behavior. |
| **G2 topology sequencing (Owner CORRECTED)** — [latest #177](https://github.com/reallakshman19/XML_Compare_Utilities/issues/177) | Disjoint source graph/signature/Boolean falsifiers and authorized **separate draft** may proceed in parallel with blocked G1 browser. Shared G1 UI integration/Owner G1 acceptance remains distinct. | Blanket G2 coding HOLD due to one unavailable browser, or overwrite shared G1 files to “integrate early.” | Verify exact file ownership, separate G2-only files; duplicate signature/target collision produces transparent evidence, no Writer. |
| **Pose-free mathematics** — [G2 #177](https://github.com/reallakshman19/XML_Compare_Utilities/issues/177) | Pose-free topology evidence; residual `NOT_EVALUATED` until a valid registered pose, Manual/Topology/OR/AND preserve source provenance/disagreement. | Invent 0 mm, merge candidate sets destructively, hide empty AND or force unique nearest. | No anchor + duplicate neighborhoods + OR/AND conflict tray, zero fabricated mm data. |
| **XML evidence bridge** — [F05 draft #157](https://github.com/reallakshman19/XML_Compare_Utilities/pull/157) | Later validate XMLv1.1 source/file/receipt/ordinal/field reference as **evidence only**. | Treat F05 Python prototype fields as replacement original CII physical nodes or promote to Writer output. | Forged/unsupported XML source fails to attach a verified locator; CII graph unchanged. |
| **Native validation vs release** — [G1 IR #175](https://github.com/reallakshman19/XML_Compare_Utilities/issues/175) | Source/author, controlled DOM, original served browser, distinct non-author check and Owner decision are separate. | Substitute author 9/9 synthetic DOM for actual original S1/T served-app PASS; old-head reviewer for new head. | Exact candidate SHA, actual `docs/cii-fnr-vnext.html` upload and negative cases independently repeated. |
| **Owner execution-first policy** — [#166 latest directive](https://github.com/reallakshman19/XML_Compare_Utilities/issues/166#issuecomment-6400403221) | Oracle attempts executable source/native/browser work and disjoint G2 prep first; asks Owner only for an unsolved source/permission issue or true release judgment. | Escalate known diagnostics or make review requirements gate **unrelated work**. | Record what was actually attempted, precise smallest stuck operation and next runnable alternative. |

A newly adopted Owner instruction may change *work order*, not redefine original physical semantics or grant a protected Writer/merge permission.

## 2. Original-source discriminatory wrong-case matrix

| Case | False positive that is easy to produce | Correct invariant / expected result | Current evidence quality |
| --- | --- | --- | --- |
| **S1 NODE 3910 → T NODE 875**, one anchor | 41/57 “matched nodes” | `TRANSLATION_ONLY`, rotation unknown; 41/57 **near** at XYZ ±100 mm, `qualifiedIdentityCount=0`. Rotated alternatives remain untested physically. | Builder originally reran; independent original pair served browser NOT_RUN |
| **S1 NODE 4060**, TARGET ELEMENT **900→905** | “NODE 905 has a match” by centerline proximity | Original `ELEMENTS#179`; segment fraction 0.76175 (guide expectation); **SEGMENT_ONLY**, no physical TARGET NODE proposal inside XYZ tolerance. | Method C engineering guide + builder tests; independent original-file browser NOT_RUN |
| **S1 NODE 4970** | Rounding, abs() or axis sign converts near-Z into PASS | Signed ΔZ approx **−300.57 mm** outside independent ±100 mm Z tolerance; preserve unresolved. | Method C guide and builder report; independent G1 browser NOT_RUN |
| **Two identically shaped topology neighborhoods** | First row/NodeName-only equality selects single target | Both genuine originals remain alternatives; `AMBIGUOUS`, original node and incident-edge witnesses; no synthetic 0mm. | G2 counterexample planned in #177, implementation not independently verified |
| **Two SOURCE nodes contest one TARGET** | Dedup target, hide collision | Explicit `TARGET_COLLISION`, all SOURCE occurrences and source/target component witnesses. | Source behavior present; disjoint G2 independent test pending |
| **One or two manual anchors** | Numeric transform labeled “identified” | One orientation undetermined; two twist undetermined; even 3+ numeric fit without Owner-anchor trust `qualified:false`. | Source-level registration code inspected |
| **Malformed CII v14 pointer/15 row** | A shorter parser silently accepts and graphs odd bytes | CONTROL/15-row counts, unit/COORDS/graph closure and original pointer checks fail closed; distinguish stronger Normal intake vs Method C. | Source code; static S1 structure checked in #175; original T Normal `parseCii` NOT_RUN |
| **S1 one-byte corruption** | Updated hash appears "verified" | `SHA_COMPUTED` only if no trusted digest; `ORIGINAL_SHA256_MISMATCH` if an expected hash is supplied. | R1 synthetic/Node negative reported; no authenticated general upload original proof |
| **Source swap while digest pending** | Old SOURCE evidence paints onto new S1 and export remains clickable | Revocation + epoch reject old Promise, no stale rows/export. | Author controlled DOM 9/9 includes stale case; served app original not run |
| **Source/target dual view** | Two SVGs have different scale/one overlay | Two distinct original-side SVG trees, true equal mm viewBox for XZ/YZ/XY, ISO NON-METRIC; linked keyboard/selection. | Static source plus author 9/9 synthetic DOM; served app NOT_RUN |
| **Normal → Geometry → Normal** | Cleanup/approval state lost or Geometry Validate leaks | Original bytes, existing CSV resolver/nonconflict decisions and Writer protected actions unchanged. | Builder reports same 1 inherited Normal branch-scope fail on base/main/head; independent rerun outstanding |
| **G2 OR/AND empty/disputed intersection** | AND filters disagreement row out without reason | Expose union/provenance, intersection, **visible disagreement/conflict tray**, unqualified status. | User request / G2 #177 spec only |
| **Old independent review of a new PR head** | Reviewer comment at old `a59f479` called signoff of `9936d407` | Same exact SHA and input/command required; old verdict stays historical PARTIAL. | GitHub IR #175 old head only |
| **Full T browser blocked** | Declared G1 or all G2 work blocked automatically | Try alternate native checkout/CI runner; report original-T unavailable for that *specific* check while continuing disjoint G2 source work. | Owner 25 Oct correction; T 2.86 MB connector retrieval absent |

Original-member expected SHA published in [builder #169](https://github.com/reallakshman19/XML_Compare_Utilities/issues/169#issuecomment-6398999288): S1 `9a9cb14db4c13f5aac41cc74a60e7e528722eb5003d09f07192762ab6bfb1a2b`, T `abfa3ffc9281fe75d4170b2d885d554cb1f120dadedae7c7ab609548b63cc060`. These digests are provenance **expectations**, not newly reproduced original bytes in this document.

## 3. Failure-classification / action tree (not a ritual gate)

```text
What outcome is being asserted?
  │
  ├─ G2 pure source/interface/topology research in disjoint files?
  │    ├─ Source available and actual native writer ownership qualified? → DO bounded work and report
  │    └─ Missing one fixture? → use a marked synthetic falsifier for only that claim,
  │                              list unrun original-data claims, don't edit G1 shared files
  │
  ├─ G1 original S1/T served application correctness?
  │    ├─ Actual full original hashes + runnable checkout? → run Normal parseCii + Method C,
  │    │                                               serve DOM, B1–B4 negatives
  │    ├─ Browser blocked before app? → try another native CI/host; label that browser test NOT_RUN
  │    └─ Shared parser failure found? → isolate exact version-14 field/guard,
  │                                   route bounded G1 PR #174 repair, same-head retest
  │
  ├─ Physical engineering correspondence/Writing/TARGET1?
  │    └─ ALWAYS separate explicit domain/Owner Writer authority and independent proof;
  │       neither Method C proximity nor Topology OR/AND grants this
  │
  └─ G1 product release/merge?
       ├─ Need exact-head original-input independent and Owner use/permission → obtain/verify
       └─ Still absent? → merge acceptance NOT_PROVED, do not convert a source PASS into release
```

**Escalation rule:** first try reproducible Oracle-capable diagnostics and unaffected disjoint implementation. Escalate only the smallest condition truly requiring unavailable source/permission/Owner acceptance. **Never** conflate blocked deployment with blocked safe source analysis.

## 4. Distinct authority and provenance of assertions

- **Owner** defines the target behavior and the execution-first priority; project #166 and amended G2 #177 are live scope sources. The Owner controls final merge/use acceptance; explicit Writer authority remains separate.
- **G1 builder `6addafaa`** produced local native original CII reports and published draft PR #174, backed-up changed modules and 27/27 Node + 9/9 synthetic DOM **self-runs**. These do not become independent simply because Common has their Cycle receipt.
- **Previous G1 reviewer** posted [PARTIAL / BLOCKED_BROWSER at old head `a59f479`](https://github.com/reallakshman19/XML_Compare_Utilities/issues/175#issuecomment-6397228570), including F1/F2 suspicions. Same GitHub account must not be misrepresented as authenticated independent approval.
- **Oracle code/source reviewer (this packet author)** read new R1 head and repo metadata and confirms source-layer files and current Owner directive; **did not** independently execute full T original byte parser or the served full browser. Its present interpretation is **SELF_ASSESSED** and must be challenged where source meaning is load-bearing.
- **G2 agent:** no confirmed recipient ID in Common Cycle rev4. A new G2 writer can be assigned disjoint native tasks subject to actual Appendix A/backup/ownership; do not invent a session, dispatch or PR.
- **Oracle successor:** **NOT ASSIGNED**, **NOT ACTIVATED**; the successor cannot become independent reviewer of the exact same code solely by using a fresh chat name.

## 5. Source conflict and permission map

| Surface | Evidence owner / who may act | Overlap/stop condition |
| --- | --- | --- |
| XCU G1 [PR #174](https://github.com/reallakshman19/XML_Compare_Utilities/pull/174): HTML, VNext app, G1 ui/scene/style, tests | Existing G1 qualified native branch writer, bounded same-PR repair | New G2 must **not edit these shared paths** without explicit reconciliation |
| XCU [G2 #177](https://github.com/reallakshman19/XML_Compare_Utilities/issues/177): disjoint topology/Boolean adapter, synthetic graph tests | Oracle source research now; actually qualified disjoint writer may make separate draft | No inferred G1 merge/browser PASS; no Writer entitlement |
| Method C parser/registration/candidate engine | Shared original-source contract; read-only first, protected existing owner | Don't replace original 15-row parsing or numeric pose to create topology convenience |
| Normal/Line/Config/Writer and merged #172 CSV/nonconflict | Existing native owners and mandatory regressions | No refactor or silent bypass to make Geometry green |
| Optional G3 F05 [PR #157](https://github.com/reallakshman19/XML_Compare_Utilities/pull/157) | Separate prototype writer | XML evidence locators cannot invent physical CII nodes |
| Common CIIFR Cycle, oracle continuity and project relay | Actual coordinating Oracle under canonical state/Owner | A documentation update is not a successor epoch or worker write permission |
| Progress Page CIIFR cards | **Sole authorized data writer and CLI** | No direct unreviewed JSON patch by Oracle |
| Original S1/T and private engineering artifacts | Actual authorized holder; checksum-receipt, no public raw bytes | Connector absence ≠ original semantic PASS; don't invent source transfer |

## 6. Recommended single discriminating diagnostic, tied to next work

**Immediate Oracle technical test:** at actual PR #174 head, run `parseCii` from VNext with **full original T bytes** and then `buildOriginalGraphFromBytes` with the expected T SHA and version-14 structural guards; compare parser verdicts. If both pass, serve real `docs/cii-fnr-vnext.html`, use S1/T file upload and inspect B1–B4. If Normal rejects T but Method C accepts, capture the exact section, field offset, record and guard on both parser branches before proposing a narrow repair; do not disable a whole class of original validation. If full T cannot be retrieved, report that precise blocker for **T intake only** and continue pure disjoint G2 duplicate-signature counterexample work.

**Next connected result:** one evidence-backed G1 original-input verdict or bounded code fix and a separate source-only G2 topology falsifier; only after compatible integration + Owner use could G1/G2 claim a runnable combined Geometry workbench.

**Checkpoint:** This decision log is source-bound reasoning, not an adopted ADR for every proposed G2 algorithm. Future contradictory original-file evidence should be added as new evidence with exact revision rather than silently editing a historical FAIL to PASS.
