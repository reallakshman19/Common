# 182-S2-W01 | Core1A exact-head learner PRINT_PDF A4 comparison

2026-10-12 | chat=6acc408a | PLAN P4 | outcome=O1 | STATUS=FAILED_A4_LINK | TEST_ONLY | NO_PRODUCT_SOURCE_CHANGE

Outcome: O1
For the user: No real learner route changed. The exact-head Core1A TEST learner print control still opens a non-A4 280 × 175 mm PDF; a separate same-HTML A4 comparison is technically feasible but is **not** its linked PDF.
Proof: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38193075758

## Immutable input and two PDF identities

- Grade9v3.5 main at verification: `778eb35a70517a46108ad0a5dc01dfc89f61c0e3`; **PR #185 DRAFT/unmerged** head `752b9ba8315bbaa9be1f3b5aeee7322a93c87829`.
- Actual HTML and PDF were downloaded unchanged from exact-head workflow run `38193075758`, artifact `11722316202`, `imo-182-core1a-test-golden-owner-review` (not independently published in a learner route).
- Artifact `core1a.html` SHA-256 `a91e8c273a20adfeb2553406420649b3145c161a1da5a67b0915f70b2da86bb3`.
- Actual learner PRINT_PDF `href="core1a.pdf"`; same file SHA-256 `1e70460d855a729692a8a00735e1607fc74a5f4716bb6afddb690e906d00c17c`; 7 pages, **each MediaBox 793.92 × 497.04 pt** (280 × 175 mm, **FAIL ISO A4**). `print-receipt.json` binds this HTML hash and this PDF hash; `deploy-receipt.json` states `subject=TEST`, `draft=true`, `accepted=false`, `roles=[CORE1A]`, `pdf.status=PRINTED`.
- Separate locally generated same-HTML **A4 comparison only** `core1a-same-html-A4-preview.pdf`: SHA-256 `01cb1d54f71321d548b18a2db3d09abbac4d2f3653b8cefb14ec28c090d8379c`; 5 pages; MediaBox **595.92 × 842.88 pt**, browser `format='A4'`. It is not in the original artifact, not the `href` target, not hash-bound to the product print receipt; **no acceptance claim**.
- Source `tools/print/print-product.mjs` blob `6d98c081fa303f972becdebb5f7fbd48833729fa` pins `page.pdf({width:'280mm',height:'175mm', ...})`. `Shared/tools/deploy_test.py::print_pdfs`, blob `c57d6f6a12f393e8654e307ccc1849540703cef7`, calls that printer without a paper-size override. This is a printer/output boundary, not a missing blueprint component.

## Independent focused local probe (six checks; 4 PASS, 2 FAIL)

| Check | Result |
| --- | --- |
| Exact-head HTML/PDF hashes equal print/deploy receipts | PASS |
| TEST Core1A page actually links the original PDF and remains unaccepted draft | PASS |
| **Actual linked PDF is ISO A4** | **FAIL** |
| Separate Chromium A4 comparison has A4 dimensions and all proof markers | PASS |
| Both PDF outputs contain all three SVG/proof stage texts and independent exit | PASS |
| **A4 comparison is the learner-linked and receipt-bound PDF** | **FAIL** |

Proof marks extracted in the *linked* PDF on p4 and *A4 comparison* on p3: `Parity guarantee`, `Remainders modulo 3`, `Combine valid factors`, `so one is even: factor 2.`; the `Now you do one` independent exit appears in both. A local raster review of comparison p3 showed the three-stage figure text within the figure boundary. Neither PDF text extraction contained `Model answer` or `KEY PDF`; in the local print DOM the one `data-g9-reveal` disclosure's computed `display` was `none`. This is limited technical leakage evidence, **not** full security or independent human review.

## Local method and attribution limits

Downloaded exact hosted CI ZIP through the authorized GitHub connection, verified SHA-256 directly against artifact JSON receipts, parsed PDFs with `pypdf`, and generated the separate PDF via Python Playwright and installed Chromium using **the identical decoded UTF-8 artifact HTML** supplied to `page.set_content`, print-media emulation, `page.pdf(format='A4',prefer_css_page_size=False,print_background=True,margin=10mm)`. Browser `file://` navigation was blocked by the execution environment, so the A4 comparison was rendered from HTML content in an isolated DOM rather than from the exact file origin. No hosted CI was started for this comparison; no original print receipt was rewritten. Candidate A4 method is bounded by old unmerged #175 `tests/check_imo_173_a4.py` blob `edacafd3d1bfe401cc2a12ceffbb9b16d9c69bb5`; none of that stack was imported.

The locally generated proof file and raster are temporary technical outputs; this versioned record does not claim they are hosted product artifacts. Exact-head original artifacts remain available through run `38193075758` for the retention period. Owner physical A4 visual review, learner comprehensibility, academic approval, QRT acceptance, complete security review and release are **NOT_RUN / NOT_ACCEPTED**.

## Cause, smallest proposed correction and decision

**Result: W01 learner-link A4 criterion FAIL.** A separate A4 preview can preserve the source's proof text, but the original `core1a.pdf` link and receipt remain non-A4. A preview-only success is not O1 completion. The observed earliest cause is the explicit width/height in the shared printer, not a Core1A blueprint gap. Proposed conditional owner-scoped correction, **not authorized or applied here**: retain the existing renderer, manifest, TEST stamp, `core1a.pdf` target and SHA receipts, change the printer's learner-page format to standards-conformant A4 (using format+MediaBox verification) only with exact shared-module writer clearance and focused cross-role/KEY-regression evidence; do not overwrite the old stack or globally refactor source projection. Produce new exact-head draft page/PDF/receipt evidence and Owner visual check. If the printer owner cannot approve the shared change, record the precise route blocker rather than silently taking the #212 lease.

**Next independent non-blocked work:** `182-S2-W02` Core1A semantic golden comparison (T02/T03/T11), then `182-S2-W03` Core1B baseline preserve check; the failed W01 A4 link remains an O1 outstanding acceptance gate. This report creates **no QRT decision, release, rights, or blueprint version change**.
