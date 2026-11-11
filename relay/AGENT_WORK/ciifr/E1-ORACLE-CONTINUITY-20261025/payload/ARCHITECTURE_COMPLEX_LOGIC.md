# CIIFR E1 — ARCHITECTURE_COMPLEX_LOGIC: bytes → element slots → auxiliary owner evidence

**Public-safe Oracle source walkthrough · 25 October 2026 · PREPARED / NO ENGINEERING WRITER.**
Source inspected: [exact E1 R2 reader](https://github.com/reallakshman19/XML_Compare_Utilities/blob/2aeaf7372de66eda3bc082b8d81bf8db43c34f4b/tools/ciifr-wbs4/readonly-catalog.mjs), Git blob `32e24c684c687b11e68da6af5dd1abd3bbe6b818`; [synthetic tests](https://github.com/reallakshman19/XML_Compare_Utilities/blob/2aeaf7372de66eda3bc082b8d81bf8db43c34f4b/tests/ciifr-wbs4-readonly-catalog.test.mjs), blob `b7e5713dfb6665e031cabd8fb210e989a9647d36`; [E0/E1 engineering note](https://github.com/reallakshman19/XML_Compare_Utilities/blob/2aeaf7372de66eda3bc082b8d81bf8db43c34f4b/docs/ciifr/WBS4_ORACLE_E0_E1.md); [independent R2 observations](https://github.com/reallakshman19/XML_Compare_Utilities/issues/170#issuecomment-6401186110). Vendor v14 auxiliary layout is cited by the reviewer at [CAESAR II Version 14 Auxiliary Element Data](https://docs.hexagonppm.com/r/en-US/CAESAR-II-Users-Guide/Version-14/1471418), while direct v14 CONTROL layout authority remains unavailable in this proof set. Source interpretation is not a native engineering import.

## 1. Causal data path and trust tiers

```text
original file bytes (Uint8Array) -- MUST NOT CHANGE
  -> linesOf(): CR, LF, CRLF delimiters, byte start/end, exact ASCII text
  -> sectionsOf(): detect "#$" section header; attach NONBLANK physical lines
     -> #$ VERSION: reject non-v14
     -> #$ CONTROL: 4 physical count rows; main 6, auxiliary 6+6+1
          -> declared ELEMENTS, RIGID, NODENAME, REDUCERS etc logical counts
          -> IZUP is FLAG, not EQUIPMNT count
     -> #$ ELEMENTS: exactly main NUMELT × 15 physical lines
          -> 9 reals rows: 8×6 + 1×5 = 53 real 13-byte lexemes
          -> name row, physical Line Number row, display row
          -> last 3 pointer rows: 6+6+3 = 15 section-indexed integers
          -> resolve zero as ABSENT; nonzero as 1-based ordinal into own section
     -> #$ RIGID: two fixed 13-byte slots per indexed record = Weight, Type
          -> record-owner list across all referencing element ordinals
     -> #$ NODENAME: separate alias count + pointer #12 (not FROM/TO node identity)
     -> other declared auxiliary sections: range + presence + selective
        physical record-line cardinality; unsupported physical shape UNVALIDATED
  -> readOnlyCatalog() object: exact addresses, original lexemes, physical
     element ordinal, pointer associations, ownership and evidence tiers
  -> publicInventory() ONLY aggregate safe counts; never private labels/values
  X NO proposal / target mutation / new copy / Writer / engineering release
```

This separation matters: the *catalogue* preserves source evidence without applying any matching or mutation. Public output must use `publicInventory` and not serialize `catalogue.elements`, `catalogue.rigids`, element names, private paths or exact lexemes from customer data.

## 2. One worked physical-element and RIGID trace (invented, not customer data)

Suppose v14 CONTROL declares `NUMELT=2`, `NODENAME=1`, `RIGID=1`. ELEMENT #1 has **FROM 101, TO 102**, pointer #2 = **1**, pointer #12 = **1**. ELEMENT #2 has FROM 102, TO 103 and pointer #2 = **1** also. There is **one** RIGID record (index 1), with Weight `0` and Type `2`, stored in two fixed-width physical numeric slots. A different element with pointer #2 = `0` would have **no RIGID record**.

Correct trace:
1. `linesOf` preserves source-byte offsets; `fixedRow` requires *exact* two-character indentation plus the appropriate count of 13-character fields on supported ELEMENT/RIGID lines. From/To must parse as nonnegative integer numbers, and 53 real fields remain exactly the original numeric token lexemes including signed zero.
2. Element ordinal is local to that source file. A sorted/renumbered TARGET can change ordinal; SOURCE occurrence #1 must not be assumed the same pipe as TARGET occurrence #1.
3. Pointer #2's `1` is an **index of the first RIGID auxiliary record**; it is not the endpoint node 101, nor the current Weight value `0`, nor a byte offset. Both ELEMENTS owning pointer 1 produce `rigids[0].owners=[0,1]` in zero-based JavaScript element indexing.
4. Pointer #12 =1 references a **NODENAME alias occurrence** and does not override FROM/TO physical connectivity. A branch label is the element's length-prefixed text and does not prove ownership of shared endpoint 102.
5. `publicInventory` can count `rigidSharedRecords=1` without publishing identifiers. A future editor must detect shared owners, obtain correct engineering authority and avoid changing Weight for one element while silently changing another. This **does not mean** sharing occurred in the historical original (reported zero shared).

Contrary interpretation: treat `pointer2=0` as an existing RIGID whose Weight happens to be zero. The test with element #1 pointer=1/Weight=0 versus element #2 pointer=0 exposes that false equivalence. See [synthetic source](https://github.com/reallakshman19/XML_Compare_Utilities/blob/2aeaf7372de66eda3bc082b8d81bf8db43c34f4b/tests/ciifr-wbs4-readonly-catalog.test.mjs). This is the consequential original→record→potential effective-engineering path the successor must be able to reason about **without granting a writer**.

## 3. Exact 15-row ELEMENTS contract and 53 slots

| Physical ELEMENTS line | Reader interpretation | Engineering caveat |
|---|---|---|
| 1–8 | Six 13-character numbers after two spaces: 8×6 real slots | Raw field format; temperature versus thermal coefficient depends on context |
| 9 | Five 13-character numbers after two spaces: 5 real slots | Combined real slots 53; not 53 approved editable fields |
| 10 | Element name, serialized length field / text row | Name is not immutable identity across files |
| 11 | Physical Line Number/branch label, length-prefix + text | Not unique node ownership |
| 12 | Display/color/visibility metadata row | E1 does not read as an engineering real field |
| 13–14 | 6 + 6 integer auxiliary pointer slots | Pointer #2 = RIGID, #12 = NODENAME |
| 15 | Final three auxiliary pointer slots | #13 REDUCERS, #14 FLANGES, #15 EQUIPMNT |

Stored real field groups: ordinals 1–2 FROM/TO nodes; 3–5 signed ΔX/Y/Z; 6–9 OD, wall, insulation thickness, corrosion allowance; 10–18 temperature/**expansion coefficient** positions; 19–27 pressure; 28–36 moduli/densities/tolerances, seam/hydro; 37–45 hot modulus; 46–53 weight factor, orientation, cladding/refractory groups. A **Material Number** is **not established** as one of these 53 reals. Never enable it by inventing an ordinal. The [engineering E0/E1 note](https://github.com/reallakshman19/XML_Compare_Utilities/blob/2aeaf7372de66eda3bc082b8d81bf8db43c34f4b/docs/ciifr/WBS4_ORACLE_E0_E1.md) flags this and the sentinel/unit gaps.

`numberSlot(line, 2 + j*13)` creates each half-open `byteStart/byteEnd` exactly from original physical line start, not by searching for a number string. `-0`, `1E-10`, `9999.99`, exponent notation and decimal tokens remain physical lexemes; their **engineering meaning** is field-specific and unproven just from parsing.

## 4. CONTROL logical cardinality: source-hard problem

The code computes 6 main count slots from CONTROL row 1 and 13 auxiliary slots in rows 2–4 (6+6+1). It checks four **data** rows and parses the referenced 13-character positions. It then computes `pointerCounts`:
- Pointers #1–11 use auxiliary count fields #1–11.
- Pointer #12 uses **main `NONAM`**, **not** auxiliary #12. Auxiliary #12 is **`IZUP` (0/1 flag)**.
- Pointer #13 uses main `NORED`; pointer #14 main `NUMFLG`.
- Pointer #15 uses auxiliary #13, **EQUIPMNT** count.

This prevents the subtle false result: `IZUP=1`, EQUIPMNT declared count `0`, ELEMENTS pointer #15 `1` must fail (`WBS4_AUX_POINTER_RANGE`), not create a phantom equipment record.

**Critical F3 gap:** CONTROL data rows are not enforced via `fixedRow`; `numberSlot` verifies referenced **positions**, but **surplus appended numeric fields may remain accepted**. Reviewer proved that parser behavior. We do **not** yet know whether native v14 input admits or rejects those rows: official v12/v15 descriptions bracket but do not settle direct v14 admissibility. Hence `VERSION_BRACKETED_CONTROL_SHAPE_UNRESOLVED`, *not* unconditional PASS and *not* proven v14 importer FAIL. A successor must not harden blindly to `6+6+6+1` exact widths without vendor source or an importer contrast.

## 5. Logical index vs physical lines (the R1→R2 regression)

A logical auxiliary index is **not** the section's nonblank line count. A source pointer `BEND=1` means **one** BEND record even though it occupies **three** physical rows. Pointer `2` with declared count `1` must fail. The same principle applies to variable section record lengths:

| Section | Implemented known physical rows / record | Qualified claim |
|---|---|---|
| BEND | 3 | Range + nonblank cardinality only |
| EXPJT | 1 | Range + nonblank cardinality only |
| RIGID | 1 with 2 parsed fixed real slots | Local Weight and Type source lexemes, not Type semantics |
| NODENAME | 1 | Logical alias count/range; blank counted alias admissibility still unproven |
| **REDUCERS** | **2** (v14) | R2 F2 proven line count only; each line's 5 numeric slots **NOT validated** |
| FLANGES | 12 | Range + nonblank cardinality only |
| EQUIPMNT | 6 | Range + nonblank cardinality only |
| RESTRANT, DISPLMNT, others | Not qualified | Reject absent/empty positive count; populated bodies `UNVALIDATED_RECORD_SHAPE` |

R1 erroneously had `REDUCERS:1` (a version-12-like assumption) and allowed a present RESTRANT section with **zero data rows** through `lines=[]` being truthy. [R1 independent FAIL](https://github.com/reallakshman19/XML_Compare_Utilities/issues/170#issuecomment-6400040909) exposed both. R2 tests now verify missing section vs present zero rows and `REDUCERS:2`; independent [#170/6401186110](https://github.com/reallakshman19/XML_Compare_Utilities/issues/170#issuecomment-6401186110) replayed with separate invented inputs and accepted **only bounded F1/F2/all-15 source behavior**.

**Do not infer numeric field validity from section cardinality.** The reviewer deliberately used two nonblank REDUCERS lines with NaN/X or truncated tokens and observed `PHYSICAL_CARDINALITY_ONLY` acceptance. This is an intentional unverified content layer, not evidence that such input would import in CAESAR II.

## 6. Concurrency and immutability

- The parser accepts only `Uint8Array`, creates source-addressed lines and returns a catalogue without altering input bytes; synthetic LF and CRLF cases preserve addresses. No Writer/Apply/Export functions are imported or invoked.
- `sectionsOf` discards blank lines when counting physical bodies, so a nonblank cardinality check is not the same as validating complete body shapes. The difference is explicit in `recordShape` labels.
- Cross-file correspondence requires an *additional* graph/identity analysis, not a source-file ordinal or branch-label equality. That belongs to distinct WBS 3.x Geometry/read-only mapping or later justified E5 scope, not E1.
- For any later edit: exact TARGET0 digest, before-span SHA or lexeme, allowed fields, shared-index owners, version-scoped units/sentinels, no stale state, new-copy TARGET1 and Owner/native import are required. **None is produced by this E1 reader.**

**Source-access boundary:** This walkthrough inspected published R2 code and issue evidence, not original protected customer's 803,776 bytes nor native CAESAR runtime. Prior physical count notes belong to the earlier Oracle's historical report. The receiving Oracle must independently trace source meaning before asserting any effective field semantics; no generic field validator or Reader PASS closes that gap.
