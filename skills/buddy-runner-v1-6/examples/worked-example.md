# Worked v1.6 interaction — illustrative record-export recovery

This is an offline quality example, not a real execution receipt. The sample/project URLs, SHA values, publications and digest strings in the JSON examples are fictional. They exercise request syntax only. A live 2/Y claiming these fictional publications must fail its provider prerequisite; never claim provider readback from this example. Replace intake-template.json placeholders with actual case values before use.

## 1a — G1 prepares and holds

Owner outcome: a user imports an original file, previews it and downloads a complete CSV that retains original record identities. The parent acceptance requires completeness, not merely a fast visible table.

Ask G2 to trace src/preview.py:build_preview through src/export.py:write_csv at the immutable baseline; inspect the original-occurrence oracle and actual download caller. The predecessor suspects the renderer, but labels that diagnosis a hypothesis. Preserve working parsing and source identity. Give G2 the investigation prompt, then HOLD. Do not start another investigation or product coding.

## 1b — G2 independently proposes

An illustrative source inspection finds that build_preview returns a complete authoritative result while a table view slices it for display. The download caller supplies that sliced view to write_csv. The first demonstrated failure is the export input contract; a missing original occurrence in a small fixture confirms it. This is not evidence that the parser lost data.

G2 proposes retaining the parser and preview builder, modifying the download caller to use the authoritative source-revision result, and preserving visible pagination. Compare this bounded correction with increasing the page size: the latter leaves completeness dependent on presentation configuration. The discriminating oracle compares exported original occurrence IDs and order with the authentic input-derived expectation. Publish/read back real 1b only in a live run; this illustrative narrative has no publication authority. Submit and stop.

## 2 — G1 makes the final direction and closes

In a real run G1 first verifies the exact 1b bytes/provenance, whether provider-backed or supplied directly, and refreshes source. Given the illustrative findings, G1 corrects its renderer diagnosis and selects the existing authoritative preview result as the export owner. There is no reason to wait for a parser rewrite.

| Task | Module owner | Action | Acceptance | Blocked work |
|---|---|---|---|---|
| EXPORT-01 | Download caller / export engineer | Pass the complete result from the same source revision to write_csv; preserve pagination | Fixture larger than one page exports every original occurrence exactly once in source order; changing pages cannot change export; a stale revision fails closed | Product writes still require the real existing writer authorization |

The full live response retains all twelve handover sections. For this compact illustration: Owner WHY is complete source-preserving export; identity is the supplied immutable baseline; parser, preview and export modules remain; flow is original → authoritative preview → view and download; the proposed caller change replaces the sliced input; original fixture/oracle provenance must be recorded; current execution is NOT_RUN; failure is a sliced export; ROI is reuse over rewrite; authority and protected expectations remain; release and authentic-case qualification remain open; exact next start is EXPORT-01 at the caller with a focused completeness/stale-revision check and caller-level rollback.

G1 ends with HANDOVER=CLOSED and PREDECESSOR=STOP. G2 does not perform another Stage 2 or return for review. The engineer continues under existing authorization.

## Xb → Y — new evidence, one intervention

Suppose new Task Evidence proves complete export for the unchanged source revision but shows stale source selection still reuses the previous result. Y verifies either the real publication or exact supplied body and independently inspects the assessed source before choosing CORRECT: bind download to the current source/result revision, and check that changing selection before download fails closed instead of exporting old data. Preserve the already-working completeness correction.

If evidence instead establishes both complete export and revision consistency, Y is CONTINUE / NO_CHANGE with a brief basis. Do not regenerate the handover. Record its canonical target and response ref on existing coordination after authorized readback. Reposting identical evidence gets the existing Y reference; materially changed evidence can receive its own intervention when submitted.

## Honest failure paths

- Missing or changed 1b body: one 1B_NOT_VERIFIED diagnostic; no invented response 2.
- Wrong Task Evidence digest or source: one TASK_EVIDENCE_NOT_VERIFIED diagnostic; no invented correction.
- All useful work actually depends on a reserved decision: BLOCKED with the exact decision and unblock condition, not a cosmetic task.
- Supplied duplicate receipt: verify the existing response, do not publish another substantive one. Without controller serialization, at-most-one behavior remains advisory.
