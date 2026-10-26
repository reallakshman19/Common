# CIIFR_GEO — current architecture and retained complex logic

**Revision2 · 26 October2026 · Oracle-authored / SELF_ASSESSED.** The current concept and task frontier are [Concept Note R2](CONCEPT_NOTE.md), [revised roadmap/WBS/implementation plan](ROADMAP_AND_IMPLEMENTATION_PLAN.md) and [current handover](ORACLE_HANDOVER.md). The source-level CII/Method C detail below is retained from the prior checkpoint; its old delivery/access/next-action claims are historical wherever superseded by this revision.

## Current input, evidence and rendering architecture

1. **Authoritative inputs:** either actual original-CII graphs (PR174 reference) or measured XML-profile graphs (PR181). Side/hash/endpoint identities, signed vectors, seeds/components and original/XML record witnesses remain distinct. An embedded CII SHA is not proof of original-byte custody.
2. **Evidence:** existing Method C computes proper rigid pose and coordinate/segment candidates. Next G2 produces independent pose-free topology pairs. Manual anchor, coordinate and topology evidence remain separate roles in one source-bound ledger; none is a Writer plan.
3. **Display:** a thin CIIFR_GEO adapter derives VisualGeometryModel.v1 for the existing shared Three.js/WebGL workbench viewer. Source/domain graphs are unchanged. SOURCE display points use the complete Method C R*p+t once; the existing translation-only viewer input is zero after this pretransform. Side/hash/node-or-element IDs round-trip through GPU picks and table selection.
4. **Shared viewer reuse:** instanced geometry, GPU color-ID picker, orthographic/perspective cameras, overlay/split, scene worker/revision scheduler, incremental chunks, floating origin, LOD and spatial index. Pin the current Three.js0.160.0 interface and package local dependency/worker assets. Reuse viewing APIs; leave editor mutation, drag/solver, Apply and transfer inactive.
5. **Reference/export:** SVG is retained and generated from the same graph/pose/candidate snapshot. XY/XZ/YZ use common-mm orthographic comparison; perspective/oblique inspection is labelled separately. Drawing culling/LOD does not prune the full ledger. JSON/CSV/SVG remain bound to actual source hashes, selected components, pose, anchors, parameters and epoch.
6. **Invalidation:** file reading, hashing, matching, scene-worker completion, mode changes and exports share source/revision guards. Changing a file clears the old side/anchors/results before asynchronous reads; a renderer may not keep displaying/exporting an old snapshot as current.

Source implementation: [PR181 input/ledger](https://github.com/reallakshman19/XML_Compare_Utilities/tree/683a1ac37b5e4457b3e67753cec1c951ec1a2dc9/prototypes/ciifr-map), [shared viewer](https://github.com/reallakshman19/XML_Compare_Utilities/blob/c823f0c0edbeb315c07fa2911390dc781968146f/workbench3d/viewer/workbench-viewer.js), [runtime](https://github.com/reallakshman19/XML_Compare_Utilities/blob/c823f0c0edbeb315c07fa2911390dc781968146f/workbench3d/viewer/scene-runtime.js), [actual reuse investigation](https://github.com/reallakshman19/XML_Compare_Utilities/issues/180#issuecomment-6406475596). GPU adapter integration is planned, not implemented.

**Important claim update:** original S1/T bytes were retrieved/rehashed and the shared parseCii accepted both in this Oracle runtime. Original served B1–B4 and GPU/browser performance remain NOT_RUN. R4 producer FORCMNT coverage is a separate converter issue. See the current handover for exact candidates, measured input identities and evidence lineage.

## Retained prior source/format explanation (25 October2026)

The following checkpoint preserves original causal/source detail and known wrong cases. It is not the current project-status board; use the R2 documents above for current inputs, graphics and WBS.


**Technical continuity / immutable source reference:** XCU [G1 PR #174 R1 head `9936d4078fb7f837ffe6f46805241efdb7bbc0e8`](https://github.com/reallakshman19/XML_Compare_Utilities/pull/174), base `c823f0c0edbeb315c07fa2911390dc781968146f`, and [Method C original engineering documentation](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/docs/METHOD_C_ENGINEERING.md). **Source-inspected, Oracle interpretation, NOT independently run original-input integration.** This document explains causality and incorrect-but-plausible alternatives; it is not a new approved domain format contract.

Read with [Project concept](CONCEPT_NOTE.md), [Decision/falsifier register](ARCHITECTURE_DECISIONS_AND_CHALLENGES.md) and [Oracle handover](ORACLE_HANDOVER.md).

## 1. Trust-boundary architecture

```text
Original SOURCE and TARGET0 file inputs (BYTES; never modified)
   │
   ├── VNext shared intake: snapshot Uint8Array / fileSeqs / Normal parseCii
   │      (a rejection HERE prevents Geometry even if Method C is more permissive)
   │
   └── Geometry G1 mount/setFiles receives name, cloned bytes, optional trusted expected SHA
         │
         ├── SHA-256 over ORIGINAL bytes per member
         ├── if explicit trusted expected hash: mismatch => ORIGINAL_SHA256_MISMATCH
         ├── parse CONTROL, units, COORDS, NODENAME, signed 15-row ELEMENTS
         │       → original NODEs, original ELEMENT endpoints/ordinals,
         │         component and seed coordinate frames, witnesses, SHA-scoped identity
         ├── Method C manual anchor(s) / proper rigid pose status
         │       → numeric pose != trusted physical correspondence
         ├── component-limited physical TARGET NODE proximity, all alternatives,
         │       nearest original TARGET ELEMENT-only station/projection
         │       → ledger, signed XYZ residuals, AMBIGUOUS/COLLISION/SEGMENT_ONLY
         ├── one SVG Method C scene => split into TWO separate SVG DOMs
         │       → common XZ/YZ/XY metric viewBox, synchronized selection/pan/zoom
         └── SHA/pose/projection/tolerance/epoch-bound read-only CSV/JSON/SVG exports

G2 separate disjoint adapter:
  same verified original graphs → pose-free graph signatures/evidence sets
  → Manual/Topology/OR/AND, all ambiguity and conflict witnesses
  → NO spatial residual before valid pose: NOT_EVALUATED
  → G1 UI/served app integration ONLY after shared-file ownership proven
G3 XMLv1.1 F05 is optional evidence/locator enrichment, not original NODE source.

NON-PATH: Geometry candidate → Writer Apply / Validate / TARGET1 / Normal approval
                                         (never authorized by this architecture)
```

**Primary actual modules:** [VNext app](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-fnr-vnext/ui/app.js), [original graph parser](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-workspace-method-c-original-geometry.js), [rigid registration](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-workspace-method-c-registration.js), [candidate engine](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-workspace-method-c-candidates.js), [Method C SVG](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-workspace-method-c-svg.js), [G1 Geometry controller](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-fnr-vnext/geometry/ui.js), and [paired SVG scene](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-fnr-vnext/geometry/scene.js).

## 2. Original signed physical graph: why 15 rows and actual pointers matter

[`cii-workspace-method-c-original-geometry.js`](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-workspace-method-c-original-geometry.js) contains `ROWS_PER_ELEMENT=15`, 13-wide numeric CII fields after the row prefix, explicit `CONTROL` ELEMENT count check, v14 `NODENAME` pointer handling on element row offset 12, original native-unit validation and 3D signed coordinate graph traversal. `buildOriginalGraphFromBytes({bytes,member,expectedSha256,cryptoRef})` clones the input and computes a real SHA-256 using WebCrypto; returns member, raw digest, byte length, physical graph, original row ordinal/witness, coordinate frame and component. A malformed signed-vector cycle, missing coordinate field, invalid unit, bad pointer, or incomplete 15-row record must not become a usable graph.

**Original 15-row ELEMENT** and **NODENAME** are separate concepts. A physical graph node is keyed by original NODE ID plus member and raw SHA (and component/incident witnesses); a textual NodeName is a possible label/auxiliary reference, not a matcher authority. The graph reconstructs physical NODE coordinates from signed ELEMENT vectors and COORDS seeds. An *interior point on a TARGET ELEMENT* is a geometric projection only and must not enter the `nodeIndex` as a manufactured physical NODE.

**Subtle parser seam:** [shared VNext `ui/app.js`](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-fnr-vnext/ui/app.js) invokes the Normal `parseCii(snapshot.bytes)` path before `geometry.setFiles(...)`. A valid Geometry candidate may thus be rejected by a **different intake parser** before Method C sees the bytes. [XCU #175 Owner correction](https://github.com/reallakshman19/XML_Compare_Utilities/issues/175) says S1 v14 static has 56 original ELEMENT records, 49 NODENAME entries and apparently valid Normal structural pointer/endpoint fields. That is **S1-only static evidence**; the original T full-byte `parseCii` behavior and served file-picker route were still unverified in this Oracle runtime. This is an actionable **technical test**, not an excuse to stop disjoint G2.

## 3. Proper rigid registration: what is and is not observable

[`registerMethodC`](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-workspace-method-c-registration.js) first checks that anchor IDs exist and are on valid original components; it checks anchor-specified source/target digest when present. Its default numeric transform has **unit scale** and **proper determinant +1**. The implementation branches by number of independent anchors:

| Case | Calculated geometric condition | Honest conclusion |
| --- | --- | --- |
| 0 anchors | `NO_ANCHOR`, identity preview | No registered physical comparison |
| 1 anchor | Translation with preview orientation/identity, `TRANSLATION_ONLY_EXPLORATION / ORIENTATION_UNDETERMINED` | Unobserved three-dimensional rotation; do not call identity |
| 2 anchors | Align observed axis; compare separation and allow preview twist | Twist around anchor axis remains unobserved; incompatible separation is a conflict |
| 3+ noncollinear | Proper rigid numeric fit, leave-one-out and residuals | Numerically comparable, but owner-anchor authentication and actual physical correspondence still false |

The returned object explicitly includes `qualified:false`, `identified:false`, `ownerAnchorAuthenticated:false`, `physicalNodeCorrespondenceQualified:false`, `qualifiedIdentityCount:0`, `writerEligible:false`. Even a small numeric fit is not a source-trusted identity receipt. Without source-authenticated physical anchors, the display is *experimental registered proximity*.

**Real benchmark counterexample:** [G1 builder #169](https://github.com/reallakshman19/XML_Compare_Utilities/issues/169#issuecomment-6398999288) reports manual SOURCE 3910→TARGET 875 yields `TRANSLATION_ONLY` and 41/57 SOURCE nodes with candidates at independent XYZ ±100 mm. These numbers represent candidates *under that preview*, **not 41 approved physical matches**, and have not been independently reproduced on the original full pair in this Oracle session.

## 4. Candidate inventory: nearest NODE and nearest ELEMENT are different types

[`findMethodCCandidates`](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-workspace-method-c-candidates.js) indexes genuine original physical target nodes in the registered **TARGET component**, checks each signed X/Y/Z residual independently against configured bounds, retains every qualifying alternative and separately records nearest physical NODE outside the bounds. It independently projects onto eligible original TARGET ELEMENT centerline segments for a nearest station/witness; a projection on the interior of segment 900→905 is not target NODE 900 or 905. Multiple SOURCE nodes contesting the same TARGET become `TARGET_COLLISION`, not silent first-row or global one-to-one assignment. The row can also be `AMBIGUOUS` or `SEGMENT_ONLY`.

The [Method C engineering guide](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/docs/METHOD_C_ENGINEERING.md) gives discriminating original-witness observations:
- S1 **4060**: original TARGET `ELEMENTS#179` endpoints **900→905**, projection fraction `0.76175`, station `6094 mm`, no nearby physical target NODE; source-only record must remain `SEGMENT_ONLY`, not a geometry-created physical NODE.
- S1 **4970**: signed nearest discrepancy **ΔZ ≈ −300.57 mm**; do not flip sign, increase tolerance silently or snap into a good match.
- Candidate inventory in a one-anchor experiment is **41/57**, not a one-to-one assignment. Duplicates and collisions are source data, not a display defect to hide.

**Counterexample that can fool naive tests:** a test that counts rows and sees 41 near candidates passes while a UI secretly drops second-best alternatives, rewrites a target element interior point as a node, or coalesces two SOURCE claims to one target. Correct tests assert original witness, all alternative identities, collision membership, status and negative absence of any physical-identity entitlement.

## 5. Dual SVG is real UI state, not a picture of one overlay

[`methodCSvgScene`](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-workspace-method-c-svg.js) initially generates source + target physical graph primitives and projection marks in one scene. [`pairedMethodCViews`](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-fnr-vnext/geometry/scene.js) DOM-parses it, creates two **distinct SVG nodes** and removes TARGET primitives from SOURCE, and SOURCE primitives from TARGET. It assigns `data-side=SOURCE` and `TARGET` with a **shared viewBox**. XZ/YZ/XY use linear millimetre view geometry; ISO intentionally uses oblique illustration and is labeled nonmetric. A shared `sharedViewBox` function controls zoom/pan so both panels share real units; table row/SOURCE/TARGET node keyboard selection must update the linked selection, not invoke `SVGElement.click()` unsupported by some Chromium implementations.

G1 repaired source explicitly uses `selectOriginalNode(node)` for pointer and Enter/Space on SVG original NODE groups and table Enter. The [9/9 controlled Chromium DOM author tests](https://github.com/reallakshman19/XML_Compare_Utilities/issues/169#issuecomment-6398999288) are not a full hosted app with original CII browser upload. A screenshot that merely shows two canvases is insufficient to verify shared physical-mm viewBox, original-input route, scroll/selection synchronization or file-swap races.

## 6. Async snapshot/epoch invalidation and evidence-export authority

The [G1 controller](https://github.com/reallakshman19/XML_Compare_Utilities/blob/9936d4078fb7f837ffe6f46805241efdb7bbc0e8/tabs/cii-workspace/cii-fnr-vnext/geometry/ui.js) increments `state.epoch` and revokes rows/selection/exports for changed file or geometry parameter. `run()` captures `ticket=state.epoch`, clones both byte arrays and awaits original graph parse; after the await and before painting it checks `ticket !== state.epoch`. Only current source/tolerance/projection/pose evidence may render or download. The Method C exporter rechecks source hashes and snapshot/projection invariants; CSV guards against formula injection in imported labels.

**Race wrong case:** replace SOURCE with a byte-identical filename but different content while an earlier async digest is unresolved. A simplistic `filename` or `same SHA` check could repaint stale results or keep exports enabled; source generation and current epoch protect the actual selected bytes. A verifier must force the reorder, not merely change the file after the old run finishes.

The two provenance labels are distinct: `SHA_COMPUTED` proves local bytes were hashed; `PINNED_SHA_VERIFIED` means a **trusted explicit** expected hash was supplied and compared. Computing hash on corrupted S1 cannot inherently reject the mutation unless an expected digest is available, but an explicit mismatching expected digest must fail closed.

## 7. Pose-free G2: technical independence and combined evidence, not combined authority

The [latest authoritative #177](https://github.com/reallakshman19/XML_Compare_Utilities/issues/177) supersedes earlier blanket G2 HOLD. Disjoint graph signatures can be investigated now from the actual original graph contract, and an authorized writer may publish a separate G2-only, **nonoverlapping draft**. Structural signatures may use original physical degree, adjacency, signed element lengths and OD/wall/branch attributes **only when present with known provenance**. Repeated neighborhoods yield multiple target candidates, not identity. Without registration, residual value MUST be `NOT_EVALUATED`; zero would be mathematically false.

Mode semantics: **Manual** only original G1 registered evidence; **Topology** separate pose-free topology proposal set; **OR** union with provenance; **AND** intersection of supported candidate identities but retain a visible conflict/empty/disagreement tray so analysts can diagnose missing intersection. Provenance is `which process suggested this pair`, not physical certification. A signed registered residual can later be attached **separately** after valid pose, never retroactively fabricated for pose-free rows.

Work ownership: G1 [PR #174](https://github.com/reallakshman19/XML_Compare_Utilities/pull/174) owns shared VNext HTML/app and Geometry UI; G2 can author independent `topology` modules/tests only after native XCU Appendix A and actual exact-file ownership. No live integration by overwriting G1 app while it remains draft; final integration has independent compatibility and Owner user-trial implications. [G3 PR #157](https://github.com/reallakshman19/XML_Compare_Utilities/pull/157) remains optional field/section source evidence only.

## 8. Real runtime risk: shared Normal parser vs Method C graph acceptance

The static served entry imports authored-to-served mirrors and the shared Normal `parseCii(snapshot.bytes)`. Current G1 source includes #172 CSV resolver and nonconflict review imports and keeps Normal proposal state separate. **A static source inspection does not establish that original TARGET T passes both Normal and Method C parser paths.** The XCU #175 correction records a bounded original S1 static Normal parser analysis (56 ELEMENT records, 49 NODENAME rows, no observed structural endpoint/pointer failures). T is ~2.86 MB and not fully retrievable through the Oracle's GitHub connector in this session; a real native checkout or CI runner is the next technical route.

If there is a parser incompatibility, isolate which parser rejected, precisely which original version-14 field/record or pointer caused it, and whether the discrepancy represents a real invalid original input or an overstrict Normal path. Never bypass `parseCii` across the entire Normal/Writer product just to make Geometry look green.

## 9. Validation and claim lattice

| Statement | Evidence needed | Latest observed as of this packet |
| --- | --- | --- |
| Authored/served source parity and F1/F2 code existence | Exact SHA/blob content inspection | Oracle checked four pairs, F1 handler and F2 labels in R1 PR |
| Original graph numbers 41/57, 4060, 4970 | Actual full original S1/T bytes, independently derived graph/candidates or WP8 separate parser | Builder reports original tests; independent Oracle complete T re-run NOT_RUN |
| 27/27 scoped Node | Exact-head command in checked checkout | Builder locally reports PASS, no exact-head hosted CI |
| 9/9 keyboard/two-pane/epoch DOM | Controlled Chromium with synthetic evidence | Builder locally reports PASS; **not real served app** |
| Real served VNext input route and Normal isolation | Live original S1/T upload and B1–B4 browser operations | BLOCKED in author environment, Oracle genuine served re-run NOT_RUN |
| Correct G2 topology and Boolean mode | Disjoint real/synthetic graph falsifiers including duplicates and collision | SOURCE_WORK_GO but no published G2 implementation proof observed |
| Independent non-author review and Owner acceptance | Distinct role/actual tested bytes, authenticated review where required, Owner real workflow | New R1 exact-head independent verdict and trial NOT_RUN |
| Engineering Writer2 / TARGET1 release | Separate explicitly authorized source-bounded writer qualification | **OUT OF SCOPE; NEVER INFER** |

A local `page.set_content` stub fixture cannot prove original T parser/served import, and a matching raw hash cannot prove NODE semantics. A successful Oracle self-test can solve technical diagnostic questions without being misrepresented as an independent review. Distinguish actual test execution, platform inability, original-data absence and protected release choice.

## 10. Successor actions (no new gate ritual)

Read current XCU main, PR #174 exact SHA, WBS #166, latest Owner #166 correction, G2 #177 source scope, and Common CURRENT before action. Then attempt **one native original-T/served file-picker diagnostic** using a reachable checkout/CI/browser, reporting exact command and result. In parallel, examine one **disjoint** pose-free topology signature/duplicate case from the original graph and document whether it can proceed without touching G1 files. Escalate only a non-solvable precise environment/permission/source ambiguity or a genuinely Owner-only acceptance/merge decision.

**Authority:** No raw inputs rewritten, no validation bypass, no secret/public data leak, no new physical-node identity claim, no Geometry Writer/Apply/TARGET1, no G2 shared-app integration without ownership, no independent PASS by source author, and no successor Oracle activation just because this knowledge file exists.
