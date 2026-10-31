# TOPO-B · Conditional two-new-file writer lease and Agent B continuation handover

**Recipient later:** existing TOPO-B Agent 2 / Agent B. **DO NOT DISPATCH IMPLEMENTATION UNTIL LEASE ACTIVE.** This is **not** new onboarding or task reassignment.

**Authority:** Owner's [conditional approval #6541471409](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239#issuecomment-6541471409) applies to **existing Agent B** and exactly two **new paths**. The public-path precheck by Oracle is [#6541589959](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239#issuecomment-6541589959): XCU `main@417bf6a954c5a6de72237537e94b05b285191350`, **9,398** untruncated Git tree entries, proposed paths absent, **59/59** open PR changed-file lists inspected, zero exact collisions and zero modified `prototypes/ciifr-map/` paths in those public open PRs. **Unpublished/local competing writer claim UNKNOWN** and non-author A4 **NOT_RUN**; no active exclusive lease yet.

## Sole prospective writer scope

```text
prototypes/ciifr-map/xml-format-admission.js
prototypes/ciifr-map/tests/format-admission.test.mjs
```

**Every other file is read-only.** No workspace file, viewer, current reader, `xml-profiles.js`, `xml-intake.js`, `xml-graph.js`, `xml-compare`, Workbench3D, TopoFix parser/Worker/UI, CII source, Writer, Weight, Final, GLRD or private original file changes. No engineer-approved auto-fix or evidence graph → CII writer path.

## Lease activation sequence — Oracle only

1. **Independent A4:** obtain an eligible separate non-author reviewer ACK and source-derived A1–A5 verdict in existing [#239](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239), threshold normally ≥92 total and each ≥17. The author/Oracle cannot self-qualify this.
2. **Exclusive custody:** at activation recheck **live** main ref, open PR path lists, pinned API imports and active unpublished same-file claims; existing Agent B must explicitly attest no competing same-file writer/branch and accept sole ownership for exactly two files. Current GitHub public noncollision alone is not an unpublished-claims clearance.
3. **Explicit Oracle receipt:** only after both gates pass, write a single `LEASE_ACTIVE_TWO_NEW_FILES_ONLY` receipt on **#239** with exact authorized source/base and current two-path lease; then deliver one bounded instruction to the existing Agent B. No renewed Owner approval for *exactly* the conditionally approved scope is required.
4. If either gate fails, **HOLD** and report the one precise blocker; no implementation, PR, or new task cycle.

## Proposed bounded implementation *after* activation (not now)

Develop a read-only fail-closed **profile-admission adapter** and a new focused test in the two paths only. Reuse existing verified interfaces from unchanged main:
- `prototypes/ciifr-map/xml-intake.js` exports `readXmlGraph` (Git blob `00c4379816f49002ddea47fbaa496b8a173154b5`);
- `prototypes/ciifr-map/xml-profiles.js` exports `extractXmlProfile` (blob `b72a970ef1fad83f78563b15f070135c23be34a1`);
- `prototypes/ciifr-map/xml-graph.js` exports `buildXmlGraph` (blob `c1c510001c913bc6fe2de64ac6f20330d3ed78e0`).

Admit explicitly supported **F05 RichInputXML-P1.v1.1** and **R4 RichInputXMLv2.1** only under strict required source root/schema/version/units/count/seed/field constraints. Return a source-SHA/epoch-scoped, nonmutating evidence graph or an explicit, non-actionable `UNSUPPORTED_INPUT`/validation error for unsupported/ambiguous data. **Never return zero findings as successful admission of foreign XML**. Existing generic marker detection is not authoritative admission. Preserve `writerEligible=false`, `physicalIdentityQualified=false` and `XML_GEOMETRY_PREVIEW_ONLY` meaning; no claim of physical connection proof. GLRD P1.v1 = **UNKNOWN_PROFILE**, not silently coerced to F05 v1.1. Do not call TopoFix PSI116 mutation code.

The **new** `format-admission.test.mjs` must cover the new router's genuinely untested boundary: positive F05/R4, unsupported GLRD/profile/root, empty/zero-graph false-success rejection, invalid seed/units/DTD/count/digest, wrong parser/field namespace, signed-delta/endpoint reversal, stale epoch, nonmutation, origin witness preservation. Reuse prior 16 V8 and native 7/7 receipts as baseline; do **not** rerun them simply for status. Newly introduced behavior requires new tests when authorized. Record exact source head, test commands/results, before/after source file hashes and negative-case outcomes. A writer-run test is not independent acceptance.

No existing-file integration approval is a prerequisite for the **isolated two-new-file stage**. A later request to wire the new adapter into InputXML Workspace/TopoFix/CIIFR UI or change existing code must obtain the affected owners' approvals *at that later integration stage*, independently review the candidate and preserve the engineering/merge HOLD.

## Exact handover return location

- [TOPO-B native issue #239](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239): Agent B assignment receipt, exclusive-lease acceptance, actual changed-file list, native tests and Task Evidence v2. One agent, one issue.
- Common relay register in this packet: artifact custody only; does not replace native task or independently authorize writes.
- Future **product draft PR only after activation** and separate bounded implementation instruction; this Common **documentation draft PR is not the product PR**.
