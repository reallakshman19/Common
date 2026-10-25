# CIIFR E1 — CONCEPT_NOTE: Owner why, source properties, user outcome

**25 October 2026 · PUBLIC_SAFE · incumbent Oracle authored · PREPARED / READ_ONLY / NOT_CUTOVER.**
This is **CIIFR WBS 4.x ELEMENTS/RIGID**, not the **WBS 3.x G1 Geometry** feature or WBS 5.x MAP. Source order: [Owner/native #167](https://github.com/reallakshman19/XML_Compare_Utilities/issues/167) and parent [VNext three-tab purpose #139](https://github.com/reallakshman19/XML_Compare_Utilities/issues/139), actual [read-only implementation PR #168](https://github.com/reallakshman19/XML_Compare_Utilities/pull/168), [independent findings #170](https://github.com/reallakshman19/XML_Compare_Utilities/issues/170), then this author's interpretation. A source quote, parser test or GitHub HEAD is *not* an Owner-accepted field-edit result.

## Why the Owner needs this

The existing CII Find & Replace is chiefly able to handle the **NodeName** use case. The Owner wants to inspect and ultimately *selectively find and replace engineering properties* attached to real CAESAR II ELEMENTS and section-indexed auxiliaries: physical FROM/TO as graph identities, dimensions (OD/wall), coordinate differences, pressure, temperature/thermal coefficient, material properties *where source-qualified*, Line Number/branch label, and RIGID Weight/Type. The user must select a **typed field plus the correct physical element/branch or auxiliary-owner scope**. Replacing the first matching numeric string, or treating a displayed node label as an engineering occurrence, is unacceptable.

The desired **future** interaction, recorded in the [E1 Project Home on PR #168](https://github.com/reallakshman19/XML_Compare_Utilities/blob/2aeaf7372de66eda3bc082b8d81bf8db43c34f4b/docs/ciifr/WBS4_PROJECT_HOME_CONCEPT.md), is:

1. Load original TARGET0 CII as **immutable bytes with a known digest**, optionally SOURCE for provenance.
2. Choose an actual engineering field: a particular ELEMENTS real slot, physical Line Number, or *nonzero-pointer-resolved* RIGID Weight/qualified Type. See original element ordinal, FROM/TO graph nodes, indexed record ownership, exact source lexeme and **half-open byte address**.
3. Find candidates and compare *typed original versus proposed values*, units, field-specific sentinel/format policy, shared pointer owners and ambiguous scopes. Explicitly approve/hold/reject. Approve All does not bypass validation.
4. Under **separate later Writer qualification**, check exact allowed spans, preserved structure, stale-plan hash, width, numeric representability, nonoverlapping claims and engineering policy. Apply to a **new-copy TARGET1** while TARGET0 remains identical.
5. Audit every changed byte, reparse and compare against the approved source; ultimately verify in **native CAESAR II** and obtain Owner acceptance before replacing the production tile.

**This full workflow is NOT in PR #168.** E1's actual contribution is a read-only source catalogue that can show what offsets and pointers exist *without producing a proposal or editable postimage*. Successful pointer-range synthetic tests cannot turn it into a product writer.

## Owner's WBS and boundaries

[WBS root #167](https://github.com/reallakshman19/XML_Compare_Utilities/issues/167) established **4.0 E0 scope/intake → 4.1 E1 exact physical catalogue → 4.2 E2 typed numeric edits → 4.3 E3 pointer-resolved RIGID edits → 4.4 E4 Line/branch labels → 4.5 E5 writer and native qualification → 4.6 E6 structural/node renumbering HOLD**.

- **E0** records concept, source framework, fixture counts and controlled semantics, but does not qualify all field values.
- **E1** records the physical inventory (53 real slots, 15 pointers, element labels, range/section evidence) and independently falsifiable reader guards. **The R2 F1/F2/all-15 pointer-range slice is accepted only at its tested synthetic scope. E1 as an entire engineering field-map task remains PARTIAL.**
- **E2/E3/E4** are not released; each needs source-qualified field meaning plus separate engineering authority and negative tests. E3 *Weight* is the first proposed RIGID editor; *Type* requires code-specific semantics.
- **E5** requires actual before/after byte and native CAESAR acceptance; **E6** is specifically deferred. Never assume E1 itself gives Writer/TARGET1 permission.

The parent [VNext #139](https://github.com/reallakshman19/XML_Compare_Utilities/issues/139) chooses independent **Normal, Line/Node and Geometry** engines; integrates only after qualification and then, with Owner approval, replaces the legacy Find & Replace tile. An independent **WBS 3.x original-CII Geometry** [#166](https://github.com/reallakshman19/XML_Compare_Utilities/issues/166) produces read-only correspondence evidence and two SVGs; it is **not** an ELEMENTS/RIGID editing shortcut. The newer [MAP #179](https://github.com/reallakshman19/XML_Compare_Utilities/issues/179) reconciles with WBS 3.x and limits first work to original geometry/overlay; its 5.x proposal was declared superseded before implementation. It must not be mistaken for E1's successor or field/writer authority.

## Terms that change the engineering answer

| Concept | Actual meaning | Incorrect substitution |
|---|---|---|
| Element occurrence | One **15-physical-line** `#$ ELEMENTS` occurrence, indexed *within this source file*, tied to source bytes and SHA | Same ordinal in a different SOURCE/TARGET copy means same physical pipe |
| FROM/TO | Integer endpoint node numbers; shared graph incidences | Unique line label, `#$ NODENAME` alias or independent source-material identity |
| 53 real slots | Original fixed-position 13-character lexemes on 9 numeric rows (8×6 + 1×5) | 53 fully qualified editable fields or an invented Material Number slot |
| Physical Line Number | Separately length-prefixed textual element branch label | Ownership of every shared node or an exact topology match |
| Auxiliary pointer | One of 15 ELEMENTS slots referencing a **1-based section-local record index**; pointer 0 = no record | Byte offset, node number, string index, RIGID Weight 0 or an authorization to create a new record |
| `#$ CONTROL` | Declared logical cardinalities and IZUP flag; not the count of physical body lines | Trusting the number of body lines as the number of selectable records |
| Read-only recordShape | `ABSENT`, `PHYSICAL_CARDINALITY_ONLY`, or `UNVALIDATED_RECORD_SHAPE` evidence tier | Native-CAESAR record content validity |
| Owner acceptance | Observed original-based result and explicit authorized decision | Green self-tests, hashes, a new chat or a draft PR |

## Present value versus promises

- **What exists:** draft [PR #168](https://github.com/reallakshman19/XML_Compare_Utilities/pull/168) at exact reviewed `2aeaf7372de66eda3bc082b8d81bf8db43c34f4b` contains a read-only parser, its synthetic tests and recovery-first work report. Public digest-less read-only inventory functions; no production Tab 3 modification and no new-copy writer.
- **What has been tested:** author native **32/32** E1+NodeName tests (SELF_ASSESSED), exact-head hosted CI success, and independently invented V8 inputs on [#170/6401186110](https://github.com/reallakshman19/XML_Compare_Utilities/issues/170#issuecomment-6401186110) for **F1 missing/empty/whitespace auxiliary; F2 REDUCERS v14 2-line record cardinality; and all-15 pointer bounds**. Oracle accepted only these in [#170/6401405888](https://github.com/reallakshman19/XML_Compare_Utilities/issues/170#issuecomment-6401405888).
- **What is held:** **F3 strict v14 CONTROL physical row/trailing-field admissibility**, all full RESTRANT/REDUCERS content/units/inheritance/sentinel semantics, original private-file examination in this review, native v14 importer run, E2–E5 writer and final product approval.
- **Historical original:** a privately held v14 sample was reported as 803,776 bytes with 521 ELEMENTS, 177 NODENAME and 156 RIGID and SHA-256 `5715c23f250d683a6c29ba84c2db9f01aae25788791317b99064c845bc2cdd57` by the previous Oracle [E0/E1 source note](https://github.com/reallakshman19/XML_Compare_Utilities/blob/2aeaf7372de66eda3bc082b8d81bf8db43c34f4b/docs/ciifr/WBS4_ORACLE_E0_E1.md). **That private input was NOT transferred to the R2 reviewer/this successor packet.** These historical counts do not establish independent current byte custody.

**Handover principle:** the succeeding Oracle should first explain which Owner-visible typed edit is eventually sought, why the current exact-byte catalogue is only a prerequisite, which synthetically bounded bugs were closed, and why F3 lacks sufficient native-version evidence. Do not repeat E1 R2 tests by default or activate an old Cycle.
