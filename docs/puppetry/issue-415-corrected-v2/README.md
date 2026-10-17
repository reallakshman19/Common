# Narasimha Puppet Show — Corrected v2 intake (DRAFT)

**Parent programme:** [#415](https://github.com/reallakshman19/Common/issues/415)  
**Related engineering study:** [draft PR #418](https://github.com/reallakshman19/Common/pull/418) / [issue #417](https://github.com/reallakshman19/Common/issues/417)  
**Earlier custody work:** [draft PR #416](https://github.com/reallakshman19/Common/pull/416)

## Purpose / previous defect

The prior user-facing ZIP was reported as **"all pdf have door only"**. The replacement `Narasimha_Puppet_Show_CORRECTED_v2.zip` was assembled in the ChatGPT working environment and **locally verified**: 47 entries, 29 PDF members, no bad ZIP member; the four quick-print PDFs are not identical and contain the intended King, Prahlada, Narasimha and four-scene storyboard content.

## This draft PR's actual content

- Verified candidate four-scene script with continuous 35/40/55/50-second allocations; one backdrop and permanently present pillar.
- Four distinct ASCII storyboards, plus individual scene Markdown files.
- `expected_package.json` containing the corrected local ZIP SHA-256 and four quick-print PDFs' SHA-256, page counts, content markers, and provenance.

**Important upload boundary:** The 1.8 MB corrected ZIP and its binary PDFs/PNGs are available as a ChatGPT conversation artifact but **are not yet committed to this GitHub branch**. A checksum manifest does not constitute binary custody. This PR is therefore deliberately an **INCOMPLETE DRAFT**, not a deliverable PDF PR. Never claim "47 original files on GitHub" until an exact SHA readback of their uploaded bytes is complete.

## Package categories when uploaded

- `00_START_HERE/` — index/README.
- `01_CHARACTERS/` — King, Prahlada and Narasimha.
- `02_SCENES/` — four scripts/PDFs.
- `03_STORY/` — complete dialogue and narrator lines.
- `04_STORYBOARD/` — combined four-panel ASCII storyboard and individual panels.
- `05_STAGE_AND_PILLAR/` — **only here** are actual pillar/door cutting sheets.
- `06_PARENTS_AND_REHEARSAL/` — handoffs, safety, and tests.
- `07_MECHANICS_SCIENCE/` — physical degrees of freedom.
- `QUICK_PRINT/` — three distinct character candidates and storyboards, NEVER door templates.

## Provenance / safety distinctions

King and Prahlada **new silhouettes** are creative candidates, NOT byte-identical recovered originals. Narasimha cutting template is an extracted page from the supplied original candidate guide, NOT a new field-tested mechanism. 1:1 PDF vector measurements do **not** show measured paper/cardboard dimensions. No full-scale build, assembly, M1–M3 or 180-second rehearsal has been independently passed.

## Binary upload completion (remaining)

1. Upload the **exact** corrected v2 ZIP and/or its extracted 47 member files to this draft branch under `docs/puppetry/issue-415-corrected-v2/source-package/`; do **not** regenerate the originals.
2. Compare archive SHA-256 to `expected_package.json`. Read back all committed files at the new GitHub head and verify individual SHA-256 identities.
3. Validate that the **three character PDFs are not the doors PDF** and match the recorded page counts and text markers. Inspect each first page visually.
4. Only then remove `BINARY_TRANSFER_PENDING` in a new auditable commit. Remain draft until engineering review and physical tests; do not merge as acceptance.

**Status:** `LOCAL_CORRECTED_PACKAGE_VERIFIED | GITHUB_BINARY_CUSTODY=PENDING | PR=DRAFT | PHYSICAL_TEST=NOT_RUN | BUDDY_1A=HOLD`.

## Source-level dimensional correction (17 Oct 2026; CANDIDATE ONLY)

The earlier review's unbounded bow and unexamined geometry now have a source-grounded correction proposal:

- [FABRICATION_CANDIDATE.json](FABRICATION_CANDIDATE.json): inherited body/arm dimensions, explicit hole coordinates and diameters, nominal DOF/BOM, control lengths, and 2.5D placement assumptions.
- [DIMENSIONAL_DECISIONS.md](DIMENSIONAL_DECISIONS.md): movement-by-movement justification, retained unknowns and the **cross-PR** dimensional amendment.
- [geometry_gate.py](geometry_gate.py): conservative source-only hole/DOF, Narasimha portal and bow-motion screen; deliberately does **not** approve real cut lines or operator mechanics.
- [story_parity.py](story_parity.py): checks exact text/clock parity among the 4 scene files and master story.
- 14 focused tests exercised by the editable-source CI job; separate PDF custody job still fails closed.

**Concrete candidate deltas:** move Prahlada's proposed stage centre **x625→660 mm**, retaining a whole-body bow trial of **15–20°**; raise the pillar aperture top **y245→255 mm** and trial leaf height **227→237 mm** to add 10 mm head clearance. Nominal 20° bow clearance changes from **overlap (−11.45 mm)** to **23.55 mm** using the recorded rectangular proxy. Actual clearance must include the mane, joints and rods.

**SOURCE GEOMETRY RECONCILED (not physically accepted):** [PR #418](https://github.com/reallakshman19/Common/pull/418) now uses x660/y255/69×237 in its separate draft source, at `92ec3442173062e642ca52c0a9dc9285192ee973`. Its [exact-head run](https://github.com/reallakshman19/Common/actions/runs/39046803009) passes 44 vector/configuration tests and generates a seven-page A4 trial PDF. The actual corrected-v2 character ZIP/PDFs are still missing from PR #419; no measured paper/cardboard fit, operator dry-run or 180-second rehearsal has occurred. Do not merge either draft as manufacturing acceptance.

The *actual corrected v2 PDF and ZIP bytes remain absent from GitHub*. Consequently no contour, hole centre, printed length, colour layer, scale bar or physical hinge in those PDFs has been certified. Source-green means **TESTED_CANDIDATE_ONLY**; `BINARY_CUSTODY=PENDING`, `DIMENSIONED_PDF_REVIEW=NOT_RUN`, `PHYSICAL_TEST=NOT_RUN`, `180_SECOND_REHEARSAL=NOT_RUN`. Keep draft.
