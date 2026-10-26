# CIIFR_GEO — revised roadmap, WBS and implementation plan

**Planning revision 2 · 26 October 2026 · Oracle-authored / SELF_ASSESSED.** Implements the Owner's direction to use the name CIIFR_GEO, compare existing XML inputs, reuse the existing 3D Edit graphics, and plan the next WBS. This revises Geometry's plan, not the whole Progress project's R4 revision or another CIIFR workstream. No implementation release, Owner acceptance or new agent assignment is created.

Read [Concept Note R2](CONCEPT_NOTE.md) and the native sources [#166](https://github.com/reallakshman19/XML_Compare_Utilities/issues/166), [#179](https://github.com/reallakshman19/XML_Compare_Utilities/issues/179), [#180](https://github.com/reallakshman19/XML_Compare_Utilities/issues/180), [next G2 #177](https://github.com/reallakshman19/XML_Compare_Utilities/issues/177). Historical WBS 5.x proposals were superseded before product implementation. Existing `ciifr` and M12–M16 remain the recording locations.

## 1. WBS retained and revised

| Stable WBS / milestone | User-visible result | Current evidence/state | Revised continuation |
|---|---|---|---|
| **3 / G0 / M12** | A source-bound, owned path into Geometry | Original G1 source/ownership work exists; PR165 is merged, so its old overlap blocker is historical | Refresh actual candidate/access and new builder's allowed files; do not restart the project or replay returned G1 assignments |
| **3.1 / G1 / M13** | Load SOURCE/TARGET, anchor nodes, review Method C candidates and linked geometry, export evidence | Original-CII PR174 and two-XML PR181 are draft candidates; XML native12/12 and HTTP18 supported, browser/Owner trial pending | **Current implementation card A:** thin read-only adapter to the existing GPU viewer, preserving SVG reference/export and current XML semantics |
| **3.2 / G2 / M14** | Compare independent topology suggestions with Manual evidence through OR/AND and a conflict tray | Real ambiguity source probe exists; implementation NOT_STARTED, executor UNASSIGNED | **Next functional WBS, card B:** pose-free candidate sets plus provenance-preserving Boolean ledger; source work can proceed disjointly from card A |
| **3.3 / G3 / M15** | Inspect verified source-record/field provenance for a selected pair | XML witnesses already exist in PR181; original-CII receipt verification bridge is NOT_IMPLEMENTED | Verify actual original/XML/receipt relationships and expose mismatch/unverified states; no converter rewrite |
| **3.4 / G4 / M16** | Reproducible exports and a supported, integrated workbench at qualified scale | Native checks and exports are partial foundations; real browser, large-model, independent and acceptance proof incomplete | Harden stale epochs, large-model CPU/GPU/table costs, evidence completeness, Normal/Writer isolation and exact-head review; controlled VNext integration and Owner release |

Deferred parent purpose: accepted NodeMap → separately resolved element/end correspondence → field-specific ownership/unit/condition rules → previewed authorized transfer → enriched target. This has no current Geometry writer entitlement or new WBS number.

## 2. Source and baseline inventory

| Source | Exact candidate / authority | How reused |
|---|---|---|
| XCU main | `c823f0c0edbeb315c07fa2911390dc781968146f` | Current shared Method C and existing 3D viewer source |
| Original-CII G1 | PR174 `9936d4078fb7f837ffe6f46805241efdb7bbc0e8` | Separate CII/dual-SVG reference and protected integration seam; not replaced or independently accepted |
| XML Geometry preview | PR181 `683a1ac37b5e4457b3e67753cec1c951ec1a2dc9`; tree `964218af596d52925654b45d9dc1e37f96314bdf` | Reference candidate for the new display adapter; not an Owner-finalized baseline |
| Existing shared viewer | `workbench3d/viewer/workbench-viewer.js`, blob `5135395ceb1daabb0301d96014a34f5c353d3793` | Viewing layer only: instancing, cameras, overlay/split, picking, selection, navigation and resource lifecycle |
| Scene runtime/scheduler | Runtime blob `02bc23fc7363493b20ea906d14da4f08a140de3d`; scheduler `e0a41544ff278848c4e93847a08ec88b0c244dc2` | Floating origin, chunks/LOD/index, worker revision guards; cache fingerprints are not source SHA authority |
| Actual current fixtures | Public S1 original 108330 bytes, SHA `9a9cb14db4c13f5aac41cc74a60e7e528722eb5003d09f07192762ab6bfb1a2b`; T 2866002 bytes, SHA `abfa3ffc9281fe75d4170b2d885d554cb1f120dadedae7c7ab609548b63cc060` | Original-source witnesses and Method C regression; do not substitute metadata for actual byte access |
| Two supplied XML fixtures | PR181 `tests/fixtures/S1-F05.xml`:882735 bytes/SHA `1154c980d08344b1f803cda3bd9884b169753148b150641a745c9bfcb15de995`; `S1-R4.xml`:1426775 bytes/SHA `a332dd7b2551faae51de3c016941762c3b795cdf19073b373817354e309526e6` | Same-original cross-profile parity, not independent physical mapping acceptance |

Source/result relay: [R3 assignment](https://github.com/reallakshman19/Common/blob/2627ff590ba26faf4329427ca4bde36177a233ae/relay/AGENT_WORK/ciifr-map/MAP-P1-20261025/IMPLEMENTATION_R3.md), [result](https://github.com/reallakshman19/Common/blob/2ac8c4327083ac9159ecf863f9cfd626ed1ffca1/relay/AGENT_WORK/ciifr-map/MAP-P1-20261025/RESULT_R3.md), [Oracle receiver verification](https://github.com/reallakshman19/XML_Compare_Utilities/issues/180#issuecomment-6401933227). Historical `ciifr-map` paths/branch names remain valid immutable locators; new work is named CIIFR_GEO.

## 3. Implementation architecture and order

### Step A — close the display seam within WBS3.1

Use one immutable, source-qualified graph snapshot per side and the existing Method C pose/candidate ledger. Create a **derived VisualGeometryModel.v1** for the shared viewer: nodes become pickable markers and original elements become display segments with source witnesses. Preserve registered component/coordinate-frame scope and expose unregistered components explicitly. A centerline display radius is a rendering choice, not an inferred engineering diameter.

Apply the complete `R*p+t` to the display SOURCE once, leaving its original graph untouched; set the existing viewer's registration translation to zero. Keep double-precision authoritative calculations and local/floating-origin GPU coordinates separate. Verify side/hash/NODE-or-ELEMENT identity through `onPick` and table selection. Use the existing orthographic camera and a common world-to-screen scale for XY/XZ/YZ; perspective is a labelled inspection mode.

Expose an opt-in GPU view in the same preview workflow, retain SVG reference/export, and package pinned Three.js0.160.0 and worker dependencies locally. Reuse the original viewer APIs; do not activate its editing, drag, solver or transfer actions. Preserve the reference candidate as an immutable comparison point while the new branch is tested. This is not a general viewer rewrite.

### Step B — next WBS3.2 topology and Boolean evidence

G2 consumes the same graph/ledger contract, regardless of SVG/GPU rendering. It computes pose-free shape proposals from qualified rotation/translation-invariant observations: degree, incident lengths, local connectivity and optionally neighboring angles. Global signed XYZ deltas cannot be compared as a rotation-invariant signature. Optional OD/wall/branch/name evidence must declare its source/semantic qualification; it must not gate candidates on invented inherited property values.

The initial signature may remain weak; ambiguity is a valid result. SOURCE3910 has local-signature alternatives TARGET875/1625/21860; SOURCE3940 and3970 each have319 alternatives under degree+incident-length+neighbor-degree. These are source-grounded falsifiers for greedy selection. More context may narrow a set, never certify physical identity by itself.

Keep three evidence roles explicit: **A** user anchor hypotheses, **C** registered coordinate candidates, **T** independent topology proposals. Manual review M displays A∪C with the roles intact; Topology displays T; OR displays M∪T; AND displays M∩T. A pair may carry several evidence tags. Anchor contradictions, excluded alternatives and empty intersections remain in a visible conflict tray; an AND result is not acceptance. Topology without pose has spatial residual `NOT_EVALUATED`. A later pose may add separate residual evidence without rewriting the topology observation.

All sets use stable side/hash/node pair identities, not row indices or labels. Preserve all alternatives, target reuse, original/XML witnesses, component scope and parameter/version bindings. Segment-only observations are separate typed evidence and never enter a NodeMap as fabricated target nodes.

### Steps C/D — evidence bridge and hardening

G3 adds verified original-CII/XML receipt relationships to existing XML locators; mismatched, missing or merely claimed provenance stays explicit. G4 adds complete export/regression, measured scaling and controlled VNext integration. Rendering changes do not accelerate XML parsing, nearest-node/segment searches or HTML ledger population automatically. Profile those paths separately; meaningful index/worker/table changes require their own bounded ownership and checks.

## 4. Card A — current WBS3.1 continuation

**ID:** `CIIFR-GEO-G1-VIEWER-REUSE-1` · **WBS:**3.1/M13 · **state:**written/PREPARED · **executor:**UNASSIGNED, chat ID UNKNOWN. This card is not dispatch. Oracle owns the brief/reconciliation; a qualified builder authors code. Check:self for a review-only prototype; independent assessment remains required before consequential engineering use/release. **Timebox:**4 builder hours to first useful prototype; re-slice if it cannot be shown.

**Overall journey / upstream / downstream:** The Owner loads existing XML geometries, hypothesizes node anchors, reviews correspondence evidence and exports a reproducible record. This card builds on PR181's measured XML graphs, Method C and ledger plus the existing 3D Edit viewer. It prepares the shared graph/selection/evidence seam consumed by WBS3.2 topology/Boolean review, without depending on G2 being implemented.

**User can:** choose an opt-in GPU view for the same current comparison, select SOURCE/TARGET nodes or elements, inspect the same ledger and switch back to SVG without changing the correspondence evidence.

**Branch/file boundary:** create a separate branch from the verified PR181 candidate; prefer a stacked draft targeting its branch so only the renderer delta is reviewed. Do not mutate PR181's tested head. Existing `prototypes/ciifr-map/` is a legacy path, not another project; bounded app/index/view/styles/server/README edits there are permitted only under the issued card. New adapter modules use `geo-*` names, plus focused tests, a uniquely named workreport and a pinned local dependency directory such as `vendor/ciifr-geo/three-0.160.0/`. Existing shared `workbench3d/**`, Method C modules, live G1 HTML/app mirrors, converters, workflows, Writer and Page source stay unchanged in this first slice. If a shared fix is actually needed, return that exact seam and coordinate it before editing.

**First builder action:** retrieve the exact card/input relay, source and candidate; verify real byte access, local backup/patch ledger, API compatibility and one representative source→display/pick rule. Prefer a builder with a functioning local browser/WebGL page. Missing browser execution limits its GPU claim, not disjoint source work. Preserve source qualification requirements and prior exposure; do not re-onboard returned G1 coder6addafaa or assume it is this recipient.

**Planned run:** extend the candidate's existing `python3 prototypes/ciifr-map/server.py` and Windows launcher. The GPU option/asset routes are not delivered yet. The server must serve the actual shared viewer, worker and vendored dependency with correct MIME; its current restrictive path allowlist and dependency-discovery smoke check need bounded extension, including dynamic Worker/Three.js assets.

**Demo, on real supported files:**
1. Load the supplied SOURCE F05/TARGET R4 XML pair; show measured XML hashes and unverified CII claims.
2. Add3790→3790, then3830→3830 and3840→3840; show the same pose/candidate counts and limitations in both renderers.
3. Switch SVG/GPU and overlay/split views; pick a source node, its target alternatives and an element; the same hash-scoped table/witness selection follows.
4. Choose XY/XZ/YZ at a common mm scale and a separately labelled perspective view; pan/zoom/fit without rebuilding all data for a selection change.
5. Change a file/anchor/parameter during pending scene work; old selection, drawing/evidence and exports cannot masquerade as current.
6. Export the same JSON/CSV/SVG evidence and run a labelled large-scene renderer probe; unavailable WebGL has an explicit SVG fallback or diagnostic.

**Done-when:** same graph/pose/ledger snapshot drives both renderers; full rigid transform occurs once; picking returns real identities; no stale epoch or hidden authority; local package resolves all assets and runs on a functioning supported browser. Report measured frame/pick/load/memory behavior, never infer it from instancing code or native tests. A native-only return is partial for this UI claim.

**Keeps:** current 12 XML/geometry checks, HTTP import graph plus newly explicit worker/dependency checks, meaningful retained Method C cases, hash provenance distinction, ±XYZ semantics, proper fit limitations, complete ambiguity/collision/segment evidence, export revocation and no Writer/Apply. Original-CII G1 4060 segment900→905 and4970 signed-Z discrepancy remain source regressions; same-original XML parity is not independent-model acceptance.

**Decisive contrary cases:** known90° rotation plus translation detects omitted/double-applied transforms; equal node numbers across sides/files detect identity collision; large world coordinates challenge GPU precision; stale worker result after file replacement challenges revocation; two competing target nodes challenge pixel-pick versus correspondence; orthographic scale/export parity challenges misleading perspective distance.

**Return:** exact head/tree, allowed paths and parity, one runnable package/demo, actual input hashes, commands/observations, browser/GPU versus native/NOT_RUN labels, measured limitations, Common artifact receipt and native #180 evidence. No merge/deploy or accepted NodeMap claim.

## 5. Card B — NEXT FUNCTIONAL WBS3.2

**ID:** `CIIFR-GEO-C-G2-TOPOLOGY-BOOLEAN-1` · **WBS:**3.2/M14 · **native task:**#177 · **state:**written/PREPARED · **executor:**UNASSIGNED, chat ID UNKNOWN. Existing disjoint-source GO remains valid; this plan binds no new Cycle recipient. **Timebox:**4 builder hours for the first inspectable candidate-set prototype. Check:self for the draft; later independent/hardening policy remains intact.

**User can:** run Topology without anchors, see every proposed pair and witness, then compare it with Manual evidence using OR/AND and a conflict tray without losing manual hypotheses or unresolved cases.

**Builds on:** current XML/original-CII graph contracts and provenance distinctions, PR181's ledger/session, G1's source facts, and the real duplicate-signature witnesses. **Prepares for:** WBS3.3 receipt-backed source-field inspection and WBS3.4 reproducible integration/release.

**First implementation:** pure pose-free signature/candidate and evidence-set modules plus a small inspectable table/JSON result under disjoint task-owned files. Do not edit card A's app/viewer files concurrently. SVG/GPU integration consumes that same output later, after explicit file-custody/compatibility reconciliation. GPU completion is not a prerequisite for the pure G2 result.

**Demo:**
1. Load the supported graphs and run Topology with no anchors. Inspect source/node/element witnesses and `NOT_EVALUATED` spatial residuals.
2. Inspect duplicate neighborhoods and a target used by multiple source candidates; no best candidate is auto-admitted.
3. Add an anchor set and run existing Method C, preserving A/C/T evidence separately.
4. Switch Manual/Topology/OR/AND; inspect a disagreement, an empty intersection and retained anchor conflict.
5. Select the same pair in table/drawing and export complete version-bound evidence; replace a file and verify stale output is revoked.

**Done-when:** pose-free results need no pose and invent no XYZ residual; set operations operate on stable pair identities; every alternative/target collision/conflict remains accessible; zero qualified physical identities/Writer actions; exact input and algorithm-version binding; runnable source-only result and subsequent controlled UI demonstration are reported separately.

**Expected wrong cases:** repeated equal-length neighborhoods; partial/resegmented routes; branch/label coincidences; rotation/translation and node renumbering; target reuse; source node falling inside a target segment; conflicting anchor outside tolerance; zero topology overlap with manual evidence; delayed mode/input changes. Signed global-axis vectors, OD sentinels or names must not be used as unqualified identity rules.

**Return:** native #177 PROTOTYPE RETURN, exact source/fixture/graph identities, all pair sets/conflicts in inspectable JSON/table, meaningful positive/contrary checks, limitations and one downstream action. Oracle reviews actual artifacts; Owner trial and required independent release remain separate. No field transfer, new converter, source graph edit or writer activation.

## 6. Scaling evidence and release boundaries

Planned renderer probes: actual public fixtures plus labelled synthetic scene tiers such as1k/10k/50k elements per side. These are **probe sizes**, not guaranteed product capacity; renderer-only tests can be separated from the preview's current matcher/input guards. Proposed usability targets are pan/zoom≥30fps and selection p95≤100ms on the declared Owner/browser/GPU setup; record actual results and adjust from Owner use, not a universal SVG cutoff.

Measure parse/graph build, matching, table/selection, scene derivation/upload, first usable draw, frame times, pick latency and memory separately. The existing tolerance-grid candidate search does not eliminate all nearest-node/segment work. Do not conceal a CPU/matcher or label/table bottleneck with a faster renderer claim.

Performance simplifications may cull offscreen geometry or labels and update only changed chunks, but preserve domain identities and complete evidence. Browser context/worker errors fail visibly, stale scenes cannot be exported as current, and repeated file loads must release resources. No native test count, screenshot or GPU source inspection establishes real browser performance.

Product merge, deployment, full VNext integration and any engineering transfer remain separately controlled. The known inherited Normal assertion and G1's true served-browser gap stay explicit. Common Cycle rev4 is not edited by this planning revision. The existing Progress Page writer PR18 remains the projection claim; provide a CLI-generated, checked patch there rather than creating a competing project/data writer or silently changing unrelated WBS4 data.

## 7. Immediate actor and action

**Oracle, chat ID UNKNOWN:** publish/read back this revision in the existing concept/native WBS sources, preserve the returned PR181 candidate, and prepare card A for one qualified builder. Card B is the next functional WBS and is ready for disjoint source execution under an actual assignment. No builder is dispatched merely by this document. The Owner can continue the existing test pack; its observations finalize the next UI integration. Unrelated authorized G2 source work continues while browser qualification or Page publication is pending.
