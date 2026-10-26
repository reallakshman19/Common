# CIIFR_GEO — concept note, revision 2

**26 October 2026 · Oracle-authored planning revision · PUBLIC_SAFE · no engineering release or control cutover.** The Owner requested the name **CIIFR_GEO**, comparison of two existing XML geometries, Method C/manual anchors and overlay evidence, reuse of the repository's existing 3D Edit/Load Calc graphics, and an updated concept/roadmap/WBS. These amendments continue existing Geometry **WBS 3 / 3.1–3.4**, milestones **M12–M16**. They do not create WBS 5.x or a new Progress project. The existing project key remains `ciifr`; other CIIFR workstreams keep their own scope.

Canonical native parent: [XCU #166](https://github.com/reallakshman19/XML_Compare_Utilities/issues/166). Current XML prototype: [#180](https://github.com/reallakshman19/XML_Compare_Utilities/issues/180), [PR #181](https://github.com/reallakshman19/XML_Compare_Utilities/pull/181). Next functional WBS: [3.2 / G2 / #177](https://github.com/reallakshman19/XML_Compare_Utilities/issues/177). Read the [revised roadmap and implementation plan](ROADMAP_AND_IMPLEMENTATION_PLAN.md), [architecture](ARCHITECTURE_COMPLEX_LOGIC.md), [decisions](ARCHITECTURE_DECISIONS_AND_CHALLENGES.md), and [handover](ORACLE_HANDOVER.md).

## 1. Owner outcome and WHY

The Owner needs to understand **which SOURCE node could correspond to which TARGET node, why that proposal exists, and where the models disagree**. A useful result connects the table, drawing, source records and exported evidence. A visually plausible overlay alone is insufficient: repeated topology, partial pose information, missing target nodes, unequal segmentation and contested targets can all produce misleading apparent matches.

The immediate product is a **read-only Geometry correspondence workbench**. The Owner loads two already-existing supported XML files, reviews manual anchor hypotheses and Method C candidates, inspects a common-scale overlay or linked views, and exports reproducible evidence. The planned topology method contributes independent candidate evidence; Manual/Topology/OR/AND make agreement and disagreement inspectable. No candidate is silently accepted as physical identity.

The larger source-to-target enrichment purpose remains context: a later, separately scoped phase may consume an accepted NodeMap, resolve element/end correspondence and ownership, preview selected field transfers, then produce an enriched target. **A NodeMap alone does not establish an ElementMap**, especially for parallel members, resegmentation or end-dependent fields. This Geometry phase neither constructs a CII→XML converter nor transfers properties or writes enriched CII.

## 2. Observable user journey

1. Open the local workbench and choose SOURCE XML and TARGET XML. Each side gets a measured byte SHA and explicit profile, units, coordinate-frame and component information.
2. Inspect original endpoint identifiers and source XML witnesses. Embedded original-CII hashes remain claims unless independent original bytes/receipts have actually been verified.
3. Add manual SOURCE→TARGET node anchor pairs. One anchor leaves orientation undetermined; two leave axial twist undetermined; three or more noncollinear anchors permit a proper rigid numerical fit, still without physical-identity approval.
4. Run existing Method C. Review every candidate alternative, signed XYZ residual, target collision, unmatched node and element-interior observation. A segment-only projection never creates a target node.
5. Inspect the geometry with linked table/selection. Use common-mm orthographic XY/XZ/YZ views for metric comparison; use a separately labelled perspective/3D mode for spatial inspection. The large-scene interactive path will reuse the existing 3D Edit viewer. SVG remains the reference/vector-export path.
6. In the next functional WBS, inspect independent pose-free topology suggestions and Manual/Topology/OR/AND evidence views. Before a pose, spatial residuals are `NOT_EVALUATED`.
7. Export current JSON/CSV/SVG evidence bound to inputs, graph version, anchors, pose, tolerances, projection, visible scope and revision. File/anchor/parameter changes immediately invalidate stale output.
8. Return to other CIIFR modes without changing original bytes, approvals or Writer state. Owner trial and engineering acceptance remain separate from native tests and publication.

## 3. Inputs and authority: two compatible routes with different claims

| Route | Authority | Preserved relationship |
|---|---|---|
| Existing original-CII G1 reference, PR #174 | Actual original bytes and measured SHA; a supplied expected SHA is a separate check | Original physical NODEs and original ELEMENT witnesses from the existing CII graph builder |
| Current two-XML preview, PR #181 | Measured XML bytes and exact supported geometry profile | XML-derived endpoint graph and section/record/row/field witnesses; embedded CII claims are `CLAIMED_NOT_REVERIFIED` |
| Later G3 receipt bridge | Verified relationship to independently available original CII, under a qualified receipt rule | Adds traceability; it is not another matcher or a route to fabricate original nodes |

The present XML profiles are F05 `RichInputXML-P1.v1.1` and R4 `RichInputXMLv2.1` / `CII-V14-ASCII-CRLF-B001`, UTF-8 and qualified native-mm geometry. This is not arbitrary-XML support or full engineering-schema certification. Signed element vectors, explicit seeds, closure and component rules must hold. Auxiliary-only references do not become geometry nodes.

Current preview safeguards are 32 MiB per XML, 50,000 elements and five million SOURCE×TARGET endpoint pairs. They are **prototype limits**, not demonstrated large-model capacity. Renderer scalability and matcher scalability require separate evidence; no limit is silently removed by choosing GPU drawing.

## 4. Graphics decision: reuse the existing 3D Edit viewing layer

Use the repository's existing [workbench viewer](https://github.com/reallakshman19/XML_Compare_Utilities/blob/c823f0c0edbeb315c07fa2911390dc781968146f/workbench3d/viewer/workbench-viewer.js), GPU picker, scene runtime, scene worker/scheduler and navigation state/controls. Existing 3D Edit hosts already call this shared viewer. Its source includes instanced batches, incremental chunks, level of detail, floating-origin coordinates, per-object selection/status, overlay/side-by-side modes and orthographic/perspective cameras.

The new work is a **thin CIIFR_GEO display adapter**, not another rendering engine or a replacement matching engine. Matching and evidence remain independent of renderer choice. The current dependency is Three.js **0.160.0**; preserve that API compatibility during reuse and package the dependency/worker assets locally for the downloadable workflow.

The viewer's registration input currently applies translation. The adapter must apply the complete Method C `R*p+t` **once to a display-only copy** and pass zero viewer registration translation, or qualify an explicitly controlled full-rigid-pose seam. Original graph coordinates stay unchanged. GPU floating-origin/float buffers are display details and never become authoritative matching coordinates.

Pick identities must include side, source hash and NODE/ELEMENT identity. The editor's visual machinery does not grant drag/edit, solver, Apply or transfer authority. CIIFR_GEO styles must preserve candidate, anchor-conflict, ambiguity, collision and segment-only meanings; existing editor `MATCHED` or `TRANSFER_READY` labels cannot be borrowed as semantic approval.

SVG remains valuable for reproducible vector evidence, review and a reference/fallback view. Its export is generated from the same graph/pose/ledger snapshot; a GPU screenshot is not a vector evidence export. Rendering filters or level of detail may reduce what is drawn, but must not remove unresolved evidence from the complete ledger.

## 5. Vocabulary that must remain distinct

| Term | Meaning |
|---|---|
| NODE identity | Side/member + actual file SHA + original or XML endpoint identifier; NodeName equality is not identity |
| ELEMENT witness | An actual source element occurrence and its endpoints/record/field references; a projected interior is not a new NODE |
| Manual anchor | An explicit hypothesis retained even when geometry/topology contradicts it |
| Method C candidate | Coordinate-near evidence after an experimental pose, including all alternatives and conflicts |
| Topology candidate | Pose-free graph-shape evidence; it can be ambiguous and has no registered spatial residual until a pose exists |
| Numerically acceptable fit | Proper scale-1, determinant+1 transform with stated residuals; not an authenticated physical correspondence |
| Display model | Derived geometry for the shared viewer; it cannot mutate source graphs or approve a mapping |
| SVG / GPU / ledger | Different presentations or exports of the same bounded evidence; none changes correspondence authority |
| Source candidate / Owner-tried / independently checked / accepted | Separate observations and decisions, scoped to exact inputs and candidate bytes |

## 6. Actual delivery and remaining proof

| Item | Observed evidence | Limit |
|---|---|---|
| Original-CII G1 | PR #174, head `9936d4078fb7f837ffe6f46805241efdb7bbc0e8`, draft/unmerged; Oracle native G1 5/5 and CSV 8/8 | Real served original-input B1–B4 and fresh independent acceptance remain unverified |
| XML input prototype | PR #181, head `683a1ac37b5e4457b3e67753cec1c951ec1a2dc9`, tree `964218af596d52925654b45d9dc1e37f96314bdf`; 21 new paths | Isolated preview, not integrated VNext or Owner accepted |
| XML native evidence | Builder and Oracle each ran 12/12 XML/geometry checks; HTTP delivery covers 18 imported modules; committed fixture hashes verified | Native DOM parser/module/HTTP checks do not establish browser interaction or actual downloads |
| Test pack | Exact-source subset plus launcher, instructions and both XML files; ZIP SHA `dd2c0f35c86e07f80238e80bad2b0f9666542e6f8f85aed9b2d5d729f5a1b974` | Pair is the same public S1 original in two profiles, not two independent engineering models; Owner trial not reported |
| GPU reuse | Source chain inspected; actual S1/T display-contract probe: 1,646 drawables, six chunks, unique identities, unchanged scene gives zero changed chunks | No GPU integration or browser performance PASS; optional external large fixture was absent |
| Topology source witness | S3910 has local-signature alternatives T875/1625/21860; S3940 and S3970 each have 319 alternatives under the simple signature | Falsifies greedy local uniqueness; it is not completed G2 |

Sources: [Oracle prototype reconciliation](https://github.com/reallakshman19/XML_Compare_Utilities/issues/180#issuecomment-6401933227), [G1 exact-head native checks](https://github.com/reallakshman19/XML_Compare_Utilities/issues/175#issuecomment-6401687179), [topology witness](https://github.com/reallakshman19/XML_Compare_Utilities/issues/177#issuecomment-6401698353), [viewer reuse investigation](https://github.com/reallakshman19/XML_Compare_Utilities/issues/180#issuecomment-6406475596).

The suspected original TARGET shared-parser rejection was not reproduced: actual `parseCii` accepted original S1 and T in this runtime. The separate R4 converter's populated `FORCMNT` rejection remains a converter-coverage issue outside this phase. The known Normal branch-scope assertion is 18/19 on both main and G1 candidate; inheritance is established, not waived. The build host's Chromium exits before a page opens; browser checks remain `NOT_RUN` and need a functioning host.

## 7. Roadmap and two-card horizon

Existing **3.1 / M13** continues with one opt-in shared-viewer adapter and same-scene SVG/GPU parity, keeping the XML candidate available for trial. Existing **3.2 / M14** is the **next functional WBS**: independent topology suggestions and Manual/Topology/OR/AND on the same graph/ledger. Its disjoint source/algorithm work may proceed while viewer/browser qualification is pending. Then **3.3 / M15** adds receipt-backed provenance and **3.4 / M16** hardens exports, scaling, regression, controlled integration and independently checked release.

The [implementation plan](ROADMAP_AND_IMPLEMENTATION_PLAN.md) supplies the two bounded cards, dependencies, file boundaries, proposed performance probes and return requirements. Their executors are **UNASSIGNED**; writing this revision does not dispatch a worker or change Common Cycle rev4. The existing Progress project/WBS IDs remain intact; a pending page projection is not a project-wide HOLD. The Owner's browser observations are still needed before finalizing the next UI integration.
