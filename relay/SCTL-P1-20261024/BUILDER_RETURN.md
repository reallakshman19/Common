# SCTL-P1 — Builder probe and blocked intake return (v1)

**Role:** Coding Builder; return to standalone Oracle.  
**Date:** 2026-10-24.  
**State:** INTAKE_BLOCKED; implementation NOT_STARTED; Owner acceptance NOT_CLAIMED.  
**User-can goal:** Open an original Word source page, see the missing Notes table, select it, and inspect exactly what was not captured by conversion. This is traceability, **not conversion repair**.

## Original invariants and bounded slice

- Preserve **100% traceability at source level as the eventual product aim**; this P1 only scopes the real Notes table, not whole-document coverage or a 100% PASS.
- Missing, ambiguous, or unsupported source/target evidence must remain visible, not suppressed as a success.
- No edits to original files, conversion engine, prior R5 ZIP, or Word-to-Table PR #4.
- Source Table #2 identity must come independently from DOCX structure; similar target text cannot establish identical occurrence.
- `NOT_CAPTURED_CONFIRMED` is permitted only when source ID, original location, target inspection and exclusion evidence actually support it.
- Page fidelity must be demonstrated against an authentic Word render; a convenient replacement renderer does not earn Microsoft Word equivalence by assumption.

## Capability probe (this chat, bounded)

| Capability | Result | Basis or limitation |
| --- | --- | --- |
| Execute Python/JavaScript/tests | YES | Python 3.13.5 and Node v22.16.0 installed and version commands executed |
| Create downloadable ZIP/launcher | YES, capability only | Filesystem and archive tooling available; SCTL ZIP NOT_BUILT |
| Read actual R5 DOCX/HTML bytes | NO currently | Current conversation file inventory empty; local R5 inputs absent |
| Real browser including localhost | PARTIAL | Chromium installed; earlier UI probe reported headless DOM interaction PASS, but localhost/file/data navigation BLOCKED_BY_ADMINISTRATOR |
| GitHub branch/draft PR | YES for Common | Authenticated connector and Common write permission observed; documentation relay branch created |
| Owner-authorized private files | UNVERIFIED/UNAVAILABLE | Google Drive connected; named R5 source/target search had zero matches |
| Authentic Microsoft Word rendering | NO demonstrated | LibreOffice available; Word not installed; equivalent pagination/format fidelity NOT_VERIFIED |

## Checks performed and missing real evidence

- Read `Common@acb3a61b3d89a622a5f29f9f2a87c0405e0f6bee` pinned Oracle Standalone, Prototype First and builder-brief files using GitHub.
- Inspected current conversation file inventory: **zero files**.
- Searched authorized connected Drive for R5 source and target names and SCTL context: **no matches**.
- Executed Python/Node version and LibreOffice/Chromium executable checks, and inspected `/mnt/data`: no R5 DOCX/HTML.
- Actual source DOCX SHA-256: UNKNOWN / NOT_MEASURED.
- Actual target HTML SHA-256: UNKNOWN / NOT_MEASURED.
- Original page count/dimensions, table location and segments: NOT_RUN.
- Table #2 source ID/fingerprint: NOT_RUN.
- Target correspondence and omission classification: NOT_RUN.
- Mandatory P1 negative tests: NOT_RUN.
- Local launcher, static viewer, reproducible R5 build, ZIP: NOT_BUILT.
- Browser product acceptance, independently verified Word render and Owner trial: NOT_RUN.
- No code files, conversion files, source documents or private packages modified.

## Smallest executable slice when genuine inputs are supplied

1. Verify raw DOCX and HTML SHA-256 and prohibit overwriting inputs.
2. Extract Table #2 directly from DOCX with deterministic occurrence identity and content fingerprint.
3. Render original Word pages using documented tool/page metrics and verify fidelity; locate every rendered table segment.
4. Inspect actual converted HTML and record candidate matches, contradiction/ambiguity and supported omission class without imagined filter events.
5. Generate a self-contained offline HTML report with page navigation, zoom, clickable table highlight and evidence inspector.
6. Supply a one-command launcher, a source/dependency bundle, demo steps and five negative checks (wrong-table identity; similar text; PDF/hash unavailable; ambiguous match; input overwrite).

**Output contract for P2:** `sctl.source-occurrence.v1` records original source and target hashes; renderer/version/fidelity/page dimensions; deterministic occurrence ID/content hash; page segment bounding boxes; target candidate evidence; explicit classification and uncertainty, without claiming population-wide coverage.

## STOP / next handoff

**STOP condition met:** authentic R5 inputs inaccessible; demonstrably authentic Word page render also unavailable. Do not substitute synthetic source or claim absence of a private Notes table on evidence not inspected.

**Next actor:** Oracle/Owner to supply the exact real DOCX and HTML through authorized private custody; preferably a Word-exported PDF as the authentic page reference, plus optional earlier evidence package. Log each transaction in `ARTIFACT_REGISTER.md`, including a session-only `/mnt/data` locator if supplied, then have the builder actually retrieve and re-hash the bytes. If PDF is missing, rendering is uncertain and must be disclosed. Product work resumes only after the applicable STOP condition is removed.

This file is a **public-safe handoff return**, not the final P1 prototype, a private artifact carrier, an Oracle receipt issue, a Progress Page update, a release or acceptance.
