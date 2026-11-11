# Narasimha-only evidence intake — Owner-supplied ZIP (17 Oct 2026)

**Source:** Conversation attachment named `Narasimha_Puppet_Show_Individual_Files(1).zip`.  
**SHA-256:** `c2d7c5ea597f46167b40f629f7b8b20981587f4141f3be3410bed64ccb4342c0`; **size 1,552,528 bytes**.  
**ZIP checks:** 43 entries, **22 PDF files**, `ZipFile.testzip()==None`. Its own inventory contains 41 listed content files; all **41/41** relative entries have the expected byte sizes and SHA-256 digests. Original Narasimha source is included; source extraction was byte-preserving.

## Owner authority clarification

**King and Prahlada: ALREADY PROVIDED ELSEWHERE.** Use the earlier originals/candidate source custody in [draft PR #416](https://github.com/reallakshman19/Common/pull/416) and the Owner's previous project backup, subject to exact-byte readback. **Do not** ask the Owner to provide them again, rebuild their silhouettes, or treat this attachment's King and Prahlada rectangles as real cutting patterns.

**The new attachment is to be used for Narasimha source reconciliation only.** Although the outer ZIP includes a full-show index, text, separate guides and stand-in King/Prahlada envelopes, those are NOT replacements for the previously supplied character artifacts. The ZIP's README explicitly warns that the included King/Prahlada PDFs are **bounding-box gauges**, not the originals.

**Not the previously expected v2 corrected package:** `expected_package.json` names `Narasimha_Puppet_Show_CORRECTED_v2.zip` with SHA-256 `f31114ef...`, 47 members and 29 PDFs. This attachment instead hashes `c2d7c5ea...` with 43 members and 22 PDFs. Never rename/substitute it to satisfy the v2 binary-custody check; that gate remains blocked until the exact expected source is supplied or a new, explicitly approved artifact version is generated and its manifest changed transparently.

## Original Narasimha source from this archive

Within `01_CHARACTERS/03_Lord_Narasimha/Original_Candidate_Source/`:

| File | SHA-256 | Source status |
|---|---|---|
| `Narasimha_Puppet_Candidate_Guide.pdf` | `4d40d54f932fbf56017d70ce9024261ac9e3837a676c0e89037663fb4d992e84` | Candidate, 4 A4 pages |
| `make_narasimha.py` | `0ff032972378e95c4f1265dad74fd6877b8a639ff20c8ff2f10e3079b7339670` | Editable candidate generator |
| `MEASUREMENTS_CANDIDATE.json` | `c5c91d7e0d053c55b4c1f1350ccb47e81561cd81c49b9e9e275ffc2d9c92ee15` | Machine-readable candidate geometry |
| `page-1.png` ... `page-4.png` | Recorded in attachment's `00_START_HERE/FILE_MANIFEST.json` | Reference previews, not 1:1 paper prints |

## Direct vector PDF dimensional inspection — Narasimha only

Inspected **original four-page** PDF, cutting sheet **page 2**, using PDF vector coordinates (72 pt/inch to mm), rather than merely reading its labels:

- Piece A (body): drawing outer bounds **x=22..112, y=51..231 mm** on A4 = **90 × 180 mm** maximum.
- Piece B (moving arm): outer bounds **x=145..165, y=89..169 mm** = **20 × 80 mm**.
- Body H1 drawn centre **(104,131) mm** on page = local body coordinate `(+37,80)`, Ø3 mm.
- Body mounting M1–M4 centres on page: **(60,157), (74,157), (60,185), (74,185) mm** = top-centre local x=±7 at y106 and 134; each Ø2 mm.
- Arm A1 (pivot) drawn at page centre **(155,99) mm** = local (10,10), Ø3; C1 at **(155,159) mm** = local (10,70), Ø2.
- Vector calibration line from x130..180 mm = **50 mm**, present. Printed paper has **NOT** been checked with a ruler.
- Total 7 punched holes; **one shoulder-rotation joint**; body + one separate active arm. Candidate sticks: main 260 mm with 90 mm overlap, active arm rod 220 mm.

**IMPORTANT movement discrepancy:** The original `MEASUREMENTS_CANDIDATE.json` says hidden arm 0°, roaring arm **120°**, blessing **90°**, and original storyboard says lift the arm to roar in Scene 3. The integrated 140-mm pillar aperture and corrected narrative require the arm **DOWN until completely clear**, with the roar by voice/body motion, followed by blessing at 90°. The *original* PDF must remain unchanged for source custody; any corrected Scene-3 cutting/assembly/storyboard PDF must be a **new version** with distinct SHA/provenance and must be dimensionally checked. Do not silently claim this original PDF already reflects the integrated choreography.

## Current boundaries

- The exact bytes of this **conversation ZIP** are not committed to this PR. This GitHub file is the **source audit/receipt**, not itself uploaded binary custody.
- The source vector dimension findings are confirmed **only for Narasimha's original candidate cut template**, not the stage-plus-rod physical envelope.
- PR #418's revised **140×240-mm opening and 69×237-mm doors** remain a candidate; Narasimha's arm-down width ≈92 mm and arm-extended width ≈155 mm require actual paper/cardboard and moving-control clearance tests.
- The real hinge/pin strength, wrist coupler, operator hand count, 5/5 door cycles and 180-second timed show remain **NOT_RUN**.

**Disposition:** `NARASIMHA_SOURCE_RECONCILED | KING_PRAHLADA_REUSE_EXISTING | ATTACHMENT_NOT_V2_PACKAGE | BINARY_GITHUB_CUSTODY=PENDING | PHYSICAL_ACCEPTANCE=HOLD`.
