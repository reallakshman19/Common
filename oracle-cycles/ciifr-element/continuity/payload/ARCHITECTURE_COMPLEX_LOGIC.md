# CIIFR Element — Complex Architecture and Original CII Semantics
**Oracle continuity · public-safe knowledge, not implementation authority**

## Architecture: original-byte identity before property transfer
```text
SOURCE raw CII / SHA / VERSION / UNITS         TARGET0 raw CII / SHA / VERSION / UNITS
         |                                              |
         +---- exact fixed-field physical index --------+
                      |                 |
              ELEMENT occurrence   ELEMENT occurrence
              FROM/TO local NODE   typed aux pointers
              53 numeric reals     RIGID/NODENAME/etc
                      \                 /
                       -> correspondence evidence ledger
                          (candidate != qualified identity)
                       -> field-specific semantic interpreter
                          (raw+units+case+material+sentinels)
                       -> READ-ONLY before/after proposal
                          with ambiguity, conflict, provenance
                          X Writer/TARGET1 (separate WBS4 E5)
```
An independently renumbered TARGET may not share node numbers with SOURCE. Two physical ELEMENT occurrences may share directed FROM→TO. The right operation starts with an original occurrence witness and typed field identity; it never derives global `targetNode=sourceNode+offset` or assumes `FROM+TO` uniquely proves cross-model element identity. See [CII Compare source concept](https://github.com/reallakshman19/XML_Compare_Utilities/blob/main/docs/CIIcompareconceptnote.md).

## V14 physical format, explicit indexing and boundaries
ELEMENTS cards are 15 physical rows. First-row widths `[15,13,13,13,13,13]` identify `FROM,TO,DX,DY,DZ,DIAMETER`. The numeric real rows are format `2X,6G13.6` and auxiliary index rows `2X,6I13`. A legal adjacent negative number may touch its preceding numeric field: whitespace tokenization cannot be authoritative. The V14 specification identifies 53 real slots and typed pointers. [Vendor Basic Element Data](https://hexagonppm.fluidtopics.net/r/en-US/CAESAR-II-Users-Guide/15/337040?contentId=HqjdhjZN1T3GBYq_vr7AWQ).

Use **one-based physical card row** but **zero-based half-open field interval within that row** (not whole-file offset):
| Engineering key | V14 physical slot | Effective-meaning dependency |
| --- | --- | --- |
| ELEMENTS.TEMPERATURE_1 | real #10, row 2 `[41,54)` | Alpha Tolerance (default 0.05 reported), temperature/strain, ambient/material/case |
| ELEMENTS.PRESSURE_1 | real #19, row 4 `[2,15)` | pressure units, operating/hydro/static load cases |
| ELEMENTS.FLUID_DENSITY | real #32, row 6 `[15,28)` | density conversion (CNVFDN), source SG rules, FDM load case |
| ELEMENTS RIGID pointer #2 | row 13 `[15,28)` | typed, 1-based `#$ RIGID` record ordinal |
| RIGID.WEIGHT | RIGID real #1 `[2,15)` | stored dry weight, effective added fluid/insulation rules |
| RIGID.TYPE | RIGID real #2 `[15,28)` | V14 type enumeration, importer/native use |

These spans are supported by the [replacement specialist's vendor-source ledger](https://github.com/reallakshman19/XML_Compare_Utilities/issues/178#issuecomment-6401204309); physical fields alone do **not** establish an admissible raw copy. V12 RIGID layout was reported as different: reject guessed cross-version reuse. A full absolute offset requires the real source row's byte start. Do not copy the pre-existing ELEMENTS first-row interval onto every 13-column row.

## Auxiliary ownership and the significant RIGID falsifier
For a typed RIGID pointer `p` and actual number of RIGID records `N`:
```text
p = 0       -> NO_ASSOCIATED_RIGID
1 <= p <= N -> RIGID record ordinal p (array[p-1])
otherwise   -> INVALID_POINTER / HOLD
```
Presence with `weight=0` is an **associated weightless RIGID**, not a missing record. This requires inspecting the pointer and referenced record separately. A naive Python `rows[p-1]` with `p=0` returns `rows[-1]` and attaches the last record incorrectly. Synthetic pointer0/pointer1-weight0 negatives and thermal/FDM contrasts were independently performed by the replacement specialist (not native CAESAR importer). Review shared/orphan references and cardinality before proposing any target mutation.

NODENAME pointers and node aliases have a different contract. Physical ELEMENT occurrence is not a logical NODE; editing a node's displayed name may require multiple endpoint-record updates. Existing author-contributed [draft NodeName PR #176](https://github.com/reallakshman19/XML_Compare_Utilities/pull/176) adds its own pointer-zero handling and remains separate, not qualified as RIGID writer logic.

## Effective value vs stored value
- A small `TEMPERATURE_1` can be thermal strain rather than a temperature, depending on Alpha Tolerance plus expansion material/ambient context. [Vendor Alpha Tolerance](https://docs.hexagonppm.com/r/en-US/CAESAR-II-Users-Guide/Version-14/334800).
- Base stored fluid density may be modified by a case-specific Fluid Density Multiplier. Synthetic `800 × 1.2 = 960` is only arithmetic, not proof of this particular customer's effective cases. [Vendor FDM](https://docs.hexagonppm.com/r/en-US/CAESAR-II-Users-Guide/Version-14/1182985).
- Pressure P1 meaning depends on source/target units and actual model/static-case definitions. Stored `0` can be a real value; never globally normalize every sentinel/zero as missing.
- RIGID zero weight has special fluid/insulation effects; TYPE is a distinct V14 field. [Vendor V14 Auxiliary Data](https://docs.hexagonppm.com/r/en-US/CAESAR-II-Users-Guide/Version-14/1471418).

## A real converter incompatibility *as evidence limit*
[XCU `converters/scripts/inputxml_to_cii2019.py`](https://github.com/reallakshman19/XML_Compare_Utilities/blob/main/converters/scripts/inputxml_to_cii2019.py) at verified blob `60a88e881af00a09fce26dcd0dcb6b915ff9d920` uses `_parse_rigid_weight`: absent RIGID XML -> `None`, present zero -> real 0. Its `_build_rigid_payload` adds one-based pointer but serializes **a single formatted weight real**, not a second RIGID.TYPE real. The V14 specification above has two items. Therefore the 2019-oriented converter **cannot be used as proof of complete V14 RIGID.TYPE preservation**. This is a *source interoperability qualification limitation*, not a proven production bug or authority to edit the converter.

## Actual code, fixtures, execution boundary
- [Public-safe research payload](https://github.com/reallakshman19/Common/tree/main/relay/AGENT_WORK/ciifr-element/field-authority-20261025/payload): `fixed-cii-index.mjs`, `element-identity.mjs`, `property-adapters.mjs`, `transfer-planner.mjs`, synthetic fixtures/tests and BENCHMARK_REPORT. Unqualified adapters are HOLD, writerEligible false; these are exploratory modules, not production CII app authority.
- Specialist independently checked **51/51** manifest entries and synthetic falsifier, did not rerun author-side 13/13 Node tests. Synthetic index 353/1000/3000 element timings used 1 warm-up+3 samples, not an estimator of browser/native safety.
- Oracle self-checked one private original: 353 elements, 38 rigid, 315 zero RIGID pointers, 38 distinct valid nonzero pointers; no zero-weight rigid in that sample. **Different** from Owner WBS4 [#167](https://github.com/reallakshman19/XML_Compare_Utilities/issues/167) 521-element benchmark. No protected original bytes in public Common.
- [Private staging receipt](https://github.com/reallakshman19/XML_Compare_Utilities/issues/178#issuecomment-6401449630): Oracle uploaded/retrieved exact protected bytes within owner-only Drive custody. **Receiver has NOT yet verified**, and external operating/material case references remain missing. Thus field-level effective SOURCE→TARGET equivalence and native CAESAR II import are NOT_RUN.

## Hard architectural invariants
Original SOURCE/TARGET0 bytes preserved; typed section/ordinal/owner indexed correctly; absent pointer != weight zero; per-version field semantics, units and case conditions; candidate identity != permission to write; deterministic HOLD on missing source; explicit provenance and SHA state; negative-byte mutation boundary and Writer held until separately approved. Geometry WBS3 remains REVIEW_ONLY.
