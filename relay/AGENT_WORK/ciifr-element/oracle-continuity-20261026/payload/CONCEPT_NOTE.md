# CIIFR-Element WBS4 — Owner concept, user journey and purpose

**Oracle continuity, 26 October 2026 · knowledge authored by incumbent Oracle chat 6ade522f · SELF_ASSESSED / SOURCE_GROUNDED / NO ENGINEERING ACCEPTANCE.**

Read with ARCHITECTURE_COMPLEX_LOGIC.md, ARCHITECTURE_DECISIONS_AND_CHALLENGES.md, ORACLE_HANDOVER.md, and ../WBS_CONTINUITY_MAP.md. This concerns **CIIFR-Element only**, not CIIFR Geometry or the XML→CII converter. This packet has no Writer, TARGET1, merge, production deployment or Oracle control transfer effect.

## 1. WHY the Owner started CIIFR, and why WBS4 was added

The controlling [standalone VNext charter, XCU #139](https://github.com/reallakshman19/XML_Compare_Utilities/issues/139) seeks to replace the existing CII Find & Replace tile **only after an independent three-tab standalone implementation and qualification**. It deliberately reuses the *visual journey*, not the current tile's matching, session, validation or mutation logic. The three original engines are: Tab 1 Normal field-aware literal/regex editing and common patcher; Tab 2 Line Number/Node Name explainable selection; Tab 3 SOURCE/TARGET signed 3D Geometry/branch reconstruction. Integration and replacing the existing tile are gated separately.

On 25 October, the Owner directed an **additive** WBS4 in [XCU #167](https://github.com/reallakshman19/XML_Compare_Utilities/issues/167): expand Find & Replace beyond NodeName to the **ELEMENTS block** (FROM/TO, geometry, diameter, wall thickness, temperature/expansion, pressure, material-related physical fields, Line Number/physical branch label) and its auxiliary pointers, especially **RIGID**. This is not an instruction to repurpose Geometry WBS3, renumber nodes early, rewrite arbitrary 13-character slots, or override P2/P2.1 frozen scope. The Owner also asked that WBS intent/roadmap/grounding fixture be reflected in the **existing CIIFR Progress Page**, not a competing project register.

**Owner-desired user experience, once later WBS stages are actually approved:** select a specific original CII or SOURCE/TARGET context; see physical ELEMENT occurrence, original field/auxiliary record, units/semantic basis, byte-span and before value; choose a typed property or Line Number/branch; propose a change to existing precisely selected fields; inspect ambiguous/shared dependencies and changed-byte audit; Validate; explicitly approve; apply to an **immutable TARGET0 -> new TARGET1 copy**, export; independently check reparse, original/target evidence and, where required, **actual native CAESAR II** meaning. There must be no silent modification of input or reuse of stale authorization. This **journey is planned**, not implemented or qualified by current E1 inspector.

## 2. What exists TODAY versus that user journey

- [PR #168](https://github.com/reallakshman19/XML_Compare_Utilities/pull/168), draft head **2aeaf7372de66eda3bc082b8d81bf8db43c34f4b**, contains a source-only V14 neutral-file catalog: version/CONTROL/15-line ELEMENTS and source slots; it does not authorize edits. Its global strict integer-pointer grammar and native-policy qualification remain separate.
- [PR #187](https://github.com/reallakshman19/XML_Compare_Utilities/pull/187), draft head **f1ffe90dee5b559c0781ce44f134e22f1f1da656**, adds a **read-only Five-Field Evidence Inspector** to witness stored TEMPERATURE_1, PRESSURE_1, FLUID_DENSITY, RIGID.WEIGHT and RIGID.TYPE and to separate local private evidence from a public-safe summary. It explicitly reports EFFECTIVE_UNKNOWN, transferAuthority NONE and nativeCaesarValidation NOT_RUN.
- Three independent reviewer rounds on [#188](https://github.com/reallakshman19/XML_Compare_Utilities/issues/188) found and corrected F1 (stderr leak), F2 (malformed decimal/exponent I13) and F3 (TAB/NBSP I13 padding); [IR3 at new exact head](https://github.com/reallakshman19/XML_Compare_Utilities/issues/188#issuecomment-6423929691) reports **scoped PASS** on stored-source behavior: 17+7 tests, 536 synthetic assertions. Not a native repository checkout, hosted inspector CI run, or CAESAR engineering approval.
- [Common Element Cycle revision 8](https://github.com/reallakshman19/Common/blob/6bb6b52a200ed5dee02f801ae5f290b8c5b663a4/oracle-cycles/ciifr-element/CURRENT.json) identifies **Owner decision** as next, not another automatically dispatched coder/reviewer task. [R8 evidence and gate packet](https://github.com/reallakshman19/Common/blob/6bb6b52a200ed5dee02f801ae5f290b8c5b663a4/relay/AGENT_WORK/ciifr-element/field-authority-20261025/PR187_IR3_RECONCILIATION_R8.md) is controlling reconciliation.
- WBS4 typed numeric proposals, pointer-resolved RIGID transactions, branch-label proposals, Writer/TARGET1, importer validation and structural renumbering remain **future** stages, not features delivered by #187.

## 3. Words that must retain distinct meanings

| Term | Meaning | Dangerous substitution |
| --- | --- | --- |
| Physical ELEMENT occurrence | One specific 15-row ELEMENTS record with an original byte position/ordinal | Engineering FROM/TO node number, which can repeat |
| Logical NodeName alias | A separately stored name/pointer and its closure over shared node ownership | One ELEMENT endpoint or one row label |
| Line Number/branch label | Physical text field held at the ELEMENT occurrence's branch row | Geometrically inferred branch, topology identity or an entire set of elements |
| RIGID pointer #2 | I13 auxiliary index scoped to a RIGID record; 0 = **no record** | RIGID Weight of numeric 0 or a false array-last index |
| Shared RIGID | Multiple ELEMENT occurrences may point to the same record | One editable property exclusively owned by selected row |
| Stored value | Neutral-file lexeme, precise half-open original byte span, slot/index | Effective stress/force/density/expansion in the selected job |
| Candidate configuration | Reported ZIP/factors/defaults whose bytes have their own custody | Proven applied CAESAR job config or source-units substitution |
| Five-field E1 inspector | Read-only private witness and safe public summary | E2 numeric editor, writer, native importer, SOURCE/TARGET transfer |
| Reviewer PASS | Independently challenged **limited local source behavior** at an exact PR head | Native build/backup, release authorization or engineering equivalence |

## 4. Original-source distinction that a successor must not erase

**Two public source reports refer to different test inputs.** [WBS4 issue #167](https://github.com/reallakshman19/XML_Compare_Utilities/issues/167) reports a *private benchmark* of **803,776 bytes, 521 ELEMENTS, 177 NODENAME and 156 RIGID**. A later actual [restricted R2 recipient read](https://github.com/reallakshman19/XML_Compare_Utilities/issues/178#issuecomment-6402061761) reports **a different protected original** of **612,613 bytes, 353 ELEMENTS, 38 RIGID, 315 absent pointers and 38 nonzero occurrences**. The two are **not two measurements of the same sample**. Never combine a count from one with the byte hash, sample-specific ownership or effective-property claim from the other. Exact private original bytes, filenames, detailed field values and restricted Drive child locators are excluded from this public packet.

The protected R2 report physically located the three numeric slots and RIGID pointer/Weight/Type, and reported no zero-weight RIGID in that original; a synthetic zero-weight countercase is **not an original witness**. The later R3/R4 reads found original embedded UNITS/material/ambient data and a **candidate-unit/default contradiction**. Original-job selected active units/material edition, load cases/FDM and native CAESAR interpretation remain unproven. See decisions document.

## 5. User-visible value now and two connected next deliverables

**Immediate confirmed value** is a reusable exact-source witness and independently tested read-only helper for safely researching existing E1 fields. It is **not a usable editing feature in VNext**. The next proposed delivery (subject to an actual Owner decision) is **genuine PR187 repository/Appendix A and hosted 24-test operational qualification**, no edits unless an observed issue calls for them. Its downstream consumer is **PR168 reader-wide pointer/parser qualification plus E2 typed field transaction design**, each with separate ownership. These enable future E3/E4 and eventually E5, without implying writer permission.

**Progress Page freshness:** WBS4 issue #167 requests projection, and Cycle rev8 says PROGRESS_UPDATE_PENDING. The live rendered page could not be read in this preparation. Mark **PAGE: PENDING RECONCILIATION**; do not call it updated or infer it from Cycle success.

**Owner control:** The acting Oracle chat is 6ade522f; current builder label 6ade42a6; separate-method reviewer label 6adf3dbf. These labels are Owner-supplied routing facts, not independently authenticated GitHub principals, actual private-byte access, or succession authorization.
