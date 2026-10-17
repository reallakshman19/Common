# Dimension and movement correction record — candidate only

**Owning draft:** [Common #419](https://github.com/reallakshman19/Common/pull/419). **Stage dependency:** [#418](https://github.com/reallakshman19/Common/pull/418) @ `74523866287ffddb231c21b7cf0314a1e827f61e`. **Owner:** [#415](https://github.com/reallakshman19/Common/issues/415).

**Boundary:** The corrected-v2 binary ZIP/PDFs are not in this PR. These coordinates are traced from earlier *candidate* generators; they are NOT measured from v2 PDF cut paths or physical prints. `FABRICATION_CANDIDATE.json` is a versioned design hypothesis / test oracle, not an accepted fabrication drawing.

## Deterministic character cutting reference (mm)

| Character | Cut pieces | Hole datum and pattern | Joint DOF | Controls |
|---|---|---|---:|---|
| King | Body 200×90; arm L & R each 90×20 | Body top-left H1=(15,70), H2=(75,70), Ø3; each arm pin (10,10), Ø3; active rod hole (10,80), Ø2 | 2 hinged, 1 actively controlled | Main stick 300–350; active arm rod 250–300 (overlap NOT SPECIFIED) |
| Prahlada | Fixed praying body 160×70 | Top-left tie holes Ø2: (28,94),(42,94),(28,120),(42,120); equivalent feet-origin x=±7, y=66/40 | 0 | Main stick 250; glued/tied overlap 90 |
| Narasimha | Body 180×90; active arm 80×20 | Body top-CENTRE H1=(+37,80), Ø3; ties x=±7 at y106/134, Ø2; arm hinge (10,10), Ø3; arm rod (10,70), Ø2 | 1 | Main 260 with 90 overlap; arm rod 220 |

Holes are bounded inside rectangular part boxes by `geometry_gate.py`. That check does **not** measure the shortest distance to the actual irregular silhouette or validate the brass-pin coupler. The earlier King proposal's one-fixed-arm simplification has **not** been adopted: 2 candidate hinges remain until the mechanism is physically evaluated.

## Scene-to-mechanism contract

- **Scene 1:** King preset arm raised ~120° from down, other arm raised to ~120° with control rod; Prahlada's folded hands fixed.
- **Scene 2:** King moves via main rod, actively points 90°, and synchronizes three safe non-impact taps with sound. No forceful strike.
- **Scene 3:** Doors open rearward. Narasimha active arm must remain DOWN (0°), roar by voice/whole-body movement. Only after clearing the portal can it extend. King tilts and exits.
- **Scene 4:** Narasimha blessing arm moves to 90° after passage. Prahlada tilts toward Narasimha in proposed 15–20° range, then returns upright.

## Measured *model*, NOT a cardboard pass

`geometry_gate.py` screens conservative rectangular envelopes and operator-stick reach using source-defined coordinates. It deliberately fails the prior unsafe movement/pillar variations.

| Parameter | PR #418 inherited | #419 proposed correction | Reason |
|---|---:|---:|---|
| Stage width / height / depth | 750/400/150 | Unchanged | Stay on fixed palace stage |
| Prahlada x centre | **625** | **660** | +35 mm right; create meaningful clearance during bow |
| Prahlada 15° worst-case gap | **15.18** | **50.18** | More than 10-mm minimum |
| Prahlada 16° worst-case gap | **9.80** (FAIL) | **44.80** | Child cannot reliably hold exactly 15° |
| Prahlada 20° worst-case gap | **−11.45** (overlap) | **23.55** | Proposed 15–20° range retains margin |
| Pillar clear opening width | 140 | Unchanged | Down-arm N approx 92 mm, 17-mm screened side gap |
| Portal opening top | **245** | **255** | Screened headroom rises from 10 to 20 mm |
| Trial leaf height | **227** | **237** | Same 1.5-mm top and bottom play, but 10 mm taller doors |
| Lintel within 280-mm pillar | 35 | 25 | Must be independently tested for frame strength |

### Critical cross-PR ownership seam

The 255-mm opening, 237-mm leaves and x=660 Prahlada position are **candidate proposals**, now adopted in PR #418 source at pinned head `92ec3442173062e642ca52c0a9dc9285192ee973`. The owning Stage-01 generator and its seven-page A4 vector trial PDF were rebuilt; [exact-head run 39046803009](https://github.com/reallakshman19/Common/actions/runs/39046803009) passed 44 focused tests. The generated vector sheet was read back (PDF SHA-256 `05c494e412dbdc0a52ed3f25ea927fc6ca9460ab1b546547a39b551125031e30`, seven A4 pages, two 69×237-mm vector doors, zero overlapping text spans). **This resolves the old SOURCE-GEOMETRY mismatch only.** The corrected-v2 *character* ZIP/PDFs remain unavailable in PR #419; physical mm print accuracy, actual pin/rod envelopes, build clearance, and rehearsal remain untested. PRs remain separate draft branches based directly on main.

### Remaining P0/P1 holds

1. **Actual v2 PDF pages:** must be committed/read back by hash; inspect every cut path, hole centre, calibration bar and print-at-100% paper size. The four key PDF hashes alone are **custody identities**, not measurements. None of the 29 PDF cut paths has been verified here.
2. **True silhouette/holes:** rectangular bounds do not prove clearance to mane edge or fabric strength. Adult to measure pin-to-cutout minimum distance, cardboard thickness and tear resistance.
3. **Arms and rods:** prove wrist coupler, link length, shoulder sweep and no snagging; fabricate secure/covered pins.
4. **Pillar and Narasimha:** real 110-mm fore-aft path, full 140-mm grip corridor below stage, string/tape-door sweep, hold-open actuator and sightline masking.
5. **Operator mock-up:** 5/5 consecutive opening/reveal/hold; real 15–20° bow clearance >=10 mm with actual rod envelopes, and timed 180-second complete rehearsal.

**Evidence grades:** `SOURCE_GEOMETRY=TESTED_CANDIDATE` vs `PDF_DIMENSIONS=NOT_INSPECTED` vs `PHYSICAL_OPERATION=NOT_RUN` vs `FULL_REHEARSAL=NOT_RUN`. BuddyRunner 1a remains HOLD, G2 not invoked.
