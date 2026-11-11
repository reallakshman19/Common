# SCTL-P1 — Builder intake and runnable prototype return (2026-10-24)

**Status:** BUILDER_BYTES_VERIFIED / RUNNABLE_CANDIDATE / WORD_FIDELITY_NOT_VERIFIED / OWNER_NOT_TRIED.  
**Custody:** Public-safe metadata only. The private ZIP, original source/target content, full report and page images are **not stored in GitHub**.  
**Direction:** Oracle/Owner → Builder (input receipt); Builder → Oracle/Owner (private prototype artifact).  
**Origin:** Real R5 ZIP uploaded directly to Builder's conversation; do **not** treat a session-local `/mnt/data` link as a durable cross-agent object.  
**Code carrier:** Private prototype ZIP in the Builder conversation; *no public implementation repo/PR*.

## A03–A05 — Independent Builder private input receipt

| Artifact | Bytes | SHA-256 | Builder state |
| --- | ---: | --- | --- |
| Original R5 evidence ZIP | 804396 | `d5392096dfcb7da81b95af02d56d74f526f65ef4dc0dd4e9539d2f6bfd6b7aa6` | BYTES_VERIFIED, ZIP CRC PASS, 16/16 manifest SHA-256 PASS |
| `R5.docx` | 706605 | `7508f9575b799efa49d2070e27099edc98819e046e8933b43ec261ba7350862c` | BYTES_VERIFIED |
| `R5_after.html` | 108765 | `ab02ee8c46a58a1990df943e35c0c42bab71859b7ce9b265a3fe04f777d056e7` | BYTES_VERIFIED |

Source and target originals were not overwritten. A03/A04/A05 supersede the earlier *Builder not received* observation **for this Builder session only**. Oracle's prior record remains historically correct.

## A06 — Source render

- SOURCE_STRUCTURE_VERIFIED: body-level DOCX Table #2 is titled `Notes`; deterministic source occurrence ID derives from actual DOCX bytes and table cell paragraphs. This is not a whole-document census.
- LibreOffice PDF-preview page count **13**; six occurrence-specific text anchors place source Table #2 on PDF page **2**.
- **WORD_FIDELITY_NOT_VERIFIED**. No independently authenticated Microsoft Word-exported PDF is present; original Word line breaks/table geometry are not certified. Any claim of exact original Word-page parity must remain HOLD.

## A07 — Private runnable prototype candidate

| Property | Value |
| --- | --- |
| File | `SCTL_P1_Missing_Source_Lens_R5_Private_Prototype.zip` |
| Bytes | 1888155 |
| SHA-256 | `8b5e5c8f3184f6a68dab4888ee38165473345cb37daa9a34d122532c6b1d1805` |
| Transport | Private Builder chat sandbox file; **SESSION_ONLY / CROSS_AGENT_RETRIEVAL_NOT_VERIFIED** |
| Launch | Extract privately and run `python launch.py`; Windows `START.cmd`; prebuilt `report/index.html` offline |
| Included | Unchanged original input files, source/dependencies/tests, static report with embedded source-page images, evidence JSON, README, private prototype return and file checksums |
| Code revision | Exact ZIP SHA-256 above and internal `SHA256SUMS.txt`; public repo does not contain private code/output |
| Builder checks | ZIP CRC PASS; unpack + launcher invocation PASS; 6/6 unittest PASS; Chromium injected-page DOM check PASS (highlight click, inspector, navigation, jump, zoom; zero JS errors) |
| Runtime limitations | Browser `file://` navigation BLOCKED_BY_ADMINISTRATOR in this environment; not asserted to have passed. No real Owner-run, no authentic Word fidelity check |
| Acceptance | RUNNABLE_CANDIDATE, not Owner accepted or independently verified |

## Scoped source/target observation

- Actual target `R5_after.html` contains 44 HTML tables; `Notes` heading and five distinctive source content anchors were not found.
- P1-only target classification: `NOT_CAPTURED_CONFIRMED` **for this supplied converted HTML**; conversion-filter cause **UNKNOWN**. A similar or ambiguous target remains ambiguous.
- Browser main view is the source preview, with a clickable Notes overlay and original-table inspection. Report is static, standalone and does not repair conversion.
- Never interpret this one-table observation as a document-wide 100% traceability PASS.

## Return to Oracle

**NOW:** Owner privately downloads and runs the candidate, compares its page-2 Notes highlight against Microsoft Word/Word-exported PDF, and reports visual fidelity/interaction findings. Oracle reconciles those observations without changing the original Builder return; if fidelity mismatch survives, P1 remains unaccepted and must correct only the bounded source rendering/location layer.

**STOP/hold:** No merge or deployment. Preserve PR #473 draft status. Do not publish the private ZIP or any protected source content to Common.