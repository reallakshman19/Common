# CIIFR-Element WBS4 — architecture, V14 record logic and trust boundaries

**Technical transfer · exact source baseline PR168 2aeaf7372de66eda3bc082b8d81bf8db43c34f4b / PR187 f1ffe90dee5b559c0781ce44f134e22f1f1da656 · SELF_ASSESSED explanation.** Not a new engineering semantic or release qualification.

## 1. System boundary and path to a future product

The [overall VNext #139](https://github.com/reallakshman19/XML_Compare_Utilities/issues/139) preserves independent Normal, Line/Node and Geometry proposal engines; the common writer alone may apply explicitly approved bounded patches to **new TARGET1**, never overwrite TARGET0. WBS4 is an **additional field-selectable Element/RIGID workstream**, while Geometry WBS3 remains separate/review-only. It is not implemented as a fourth released tab.

Conceptual path (future steps marked PLANNED):

1. Protected V14 CII original bytes + source SHA, supplied under authorized private custody (original identity and cases not inferred from a filename).
2. PR168 readOnlyCatalog: parse VERSION/CONTROL, sections, physical ELEMENTS (15 lines), fixed-width reals, auxiliary pointers and RIGID ownership. This is **source structure**, not native effective meaning.
3. PR187 inspectFiveFieldEvidence(bytes,{elementIndex}): validate every RIGID I13 pointer #2; select **one zero-based physical occurrence**; return five source fields, original lexemes/spans, RIGID record and all owners, absent record as null. Emit EFFECTIVE_UNKNOWN. Data stays local private.
4. PR187 publicFiveFieldSummary(report): allowlist five field names/effective status and blocker classes, never serialize source values, node IDs, names, SHA, private paths or physical spans. CLI handles direct-process errors with a source-neutral message; success LOCAL_ONLY_DIRECTORY contains private path.
5. **PLANNED E2/E3/E4:** independently source- and engineering-qualified typed proposals (numeric field/selected existing RIGID Weight/physical branch). Handle shared-pointer consequences, numeric width/sentinel semantics and ambiguous topology; not implemented by reader/inspector.
6. **PLANNED E5:** explicit validation/approval and common byte-patcher comparison against immutable TARGET0; reject overlapping changes/stale SHA, reparse exact TARGET1, independent result and native CAESAR import where warranted. Owner merge and product integration independently gated.

Important distinction: the public summary of *what cannot be inferred* can be useful before the private effective-property configuration is acquired. Lack of CAESAR does not forbid read-only structural inspection.

## 2. Physical record accounting: where the values actually reside

[PR168 reader implementation](https://github.com/reallakshman19/XML_Compare_Utilities/blob/2aeaf7372de66eda3bc082b8d81bf8db43c34f4b/tools/ciifr-wbs4/readonly-catalog.mjs) defines **53 real** source slots per ELEMENT occurrence across 9 fixed numeric lines (8 lines with 6 values, one with 5), then text name row, physical branch/Line Number row, display metadata row, and **three pointer rows with 15 I13 slots**. The exact row grouping and absolute byte addresses must come from the original bytes, accounting for LF vs CRLF. It is not 53 plus some implied material-ID real.

- Reals ordinal 1–2: FROM and TO; ordinals 3–5 DELTA X/Y/Z; 6 outside diameter; 7 wall thickness; 8 insulation thickness; 9 corrosion allowance.
- Real #10 (first of the temperature/expansion-related nine) is stored as **TEMPERATURE_1** in the five-field inspector. Its effective significance can depend on the active alpha/thermal expansion policy; do not say every original #10 lexeme is unquestionably a physical temperature in the analysis.
- Real #19: **PRESSURE_1**; real #32: **FLUID_DENSITY**. These are physical source slots but require actual unit case/FDM evidence to mean an effective applied analysis value.
- Pointer #2 is RIGID section-local ordinal, **0 absent**; nonzero p selects RIGID[p-1]. Its referenced physical line contains **WEIGHT** at [2,15) and **TYPE** at [15,28) relative to that RIGID content line.
- TEXT branch/Line Number row is independently length-declared; label is not implied by FROM/TO or geometry. Material identifiers can reside in **MISCEL_1** (R3 report); never relabel real #30 Pipe Density as a Material ID.

[Native R2 original field-address receipt](https://github.com/reallakshman19/XML_Compare_Utilities/issues/178#issuecomment-6402061761) independently reports row2 [41,54) for #10; row4 [2,15) for #19; row6 [15,28) for #32; pointer row13 [15,28), for its **353-element private original**. RIGID Weight and Type slots are as above. These offsets are relative to their corresponding physical lines; each selected source token additionally has a global [byteStart,byteEnd) offset. Do not confuse these with an output TARGET byte span.

## 3. Source identity and witness invariants

Source is a Uint8Array and its SHA-256. Every numeric lexeme is preserved as its **13 exact original bytes**; byteStart/end are half-open. A returned numeric JS Number is explanatory and can lose lexical features (e.g., negative zero/exponent), so it is not sufficient proof for a future byte-edit. The inspector checks that the reconstructed byte slice exactly equals the parsed slot lexeme and that it occupies exactly 13 bytes.

One ELEMENT's physical ordinal is **not** its FROM/TO identity; two or more physical ELEMENTS may carry the same endpoints and distinct physical branch labels. An independently serialized LF/CRLF fixture must check label value AND source span. A mutable displayed selection, branch match or node number can never silently remap the selected occurrence. Shared RIGID record owners are *all* physical ELEMENT ordinals referring to that RIGID index. Edit one RIGID record in future E3 and it can affect multiple elements—must explicitly expose/guard this.

The RIGID pointer is not a neutral float. [PR168 reader](https://github.com/reallakshman19/XML_Compare_Utilities/blob/2aeaf7372de66eda3bc082b8d81bf8db43c34f4b/tools/ciifr-wbs4/readonly-catalog.mjs) uses numberSlot on all numeric tokens: its general number parser accepts decimal and exponent representations then integer() checks value. This is looser than strict I13 pointer grammar. **PR187 compensates only for the RIGID #2 consumer** using raw physical 13-byte left ASCII 0x20 padding + optional sign + digits and BigInt source-pointer equivalence for *every* ELEMENT before consuming a shared-owner map. It rejects TAB/NBSP/control and 1.0/1E0 tokens that JS trim() would otherwise promote. Do not call this a fix for all 15 pointer types or the parent reader. [Parent source-owner defect #173](https://github.com/reallakshman19/XML_Compare_Utilities/issues/173) remains open.

The **absence semantics** are three-way: no RIGID association (pointer0), associated RIGID record holding numeric zero/negative zero Weight, and a malformed or out-of-range reference (FAIL CLOSED). Neither a null record nor a zero value authorizes invention of another RIGID association, and a shared record must not be silently split or reindexed.

## 4. Input interpretation and effective engineering boundary

PR187 exports a physical stored-source witness, not active CAESAR job interpretation. The R2 original only demonstrates storage and 38/38 referenced RIGID rows for that sample, **not native behavior of weight=0**. [R3 embedded-context report](https://github.com/reallakshman19/XML_Compare_Utilities/issues/178#issuecomment-6406533457) finds model-stored UNITS, MISCEL_1 material IDs and ambient. [R4 contradiction](https://github.com/reallakshman19/XML_Compare_Utilities/issues/178#issuecomment-6407053321) finds candidate binary unit factors differ from original stored conversions and candidate new-job ambient differs from original model ambient. Neither alone proves the applied active config, material database edition, chosen original load cases or per-case FDM. Therefore no conversion/default substitution; evidenceValue effective=EFFECTIVE_UNKNOWN remains correct.

For **RIGID.TYPE**, physical stored second real exists; the converter identified in R2 as inputxml_to_cii2019.py was only shown preserving Weight, not demonstrated to round-trip Type. This is **interoperability risk**, not proven deployed converter defect. Treat Type editable semantics as HOLD pending vendor/native original-job proof.

## 5. Real failure paths and source/authority boundaries

- Parse and source-layout failure: bad V14 VERSION, CONTROL shape/counts, 15-line cardinality, missing auxiliary section, pointer range or wrong lexeme => failure, not a complete-looking catalogue.
- PR187 F1 direct CLI errors: print generic SOURCE_REJECTED; never echo original private path, parser offset, identifier or source lexeme. Exported library exceptions still require trustworthy calling code not to log private details; direct subprocess safety does not certify arbitrary embeddings.
- PR187 F2/F3: strict I13 enforced at consumer for *all elements* even when selected element's pointer is valid; otherwise an unselected poisoned shared owner contaminates the association list.
- Local-only evidence and public summary: any source-derived report containing labels/values/hashes/spans is PRIVATE; whitelist-only public summary is a deliberate separate object. A successful CLI's LOCAL_ONLY_DIRECTORY stdout is a local path and must not be pasted into public CI logs.
- No mutation: no TARGET1, write claim, source-to-target match, NodeName/Geometry mapping or export acceptance happens in E1. Any future writer must be a separately reviewed module, with original-source SHA/CAS, before-slot equality, width/rounding policy, overlap rejection, explicit user approval and a full changed-byte audit.

## 6. Code and test sources for successor's first walk

Pinned exact source: [PR168 reader](https://github.com/reallakshman19/XML_Compare_Utilities/blob/2aeaf7372de66eda3bc082b8d81bf8db43c34f4b/tools/ciifr-wbs4/readonly-catalog.mjs); [PR187 inspector](https://github.com/reallakshman19/XML_Compare_Utilities/blob/f1ffe90dee5b559c0781ce44f134e22f1f1da656/tools/ciifr-wbs4/five-field-evidence.mjs); [F3 tests](https://github.com/reallakshman19/XML_Compare_Utilities/blob/f1ffe90dee5b559c0781ce44f134e22f1f1da656/tests/ciifr-wbs4-five-field-f3.test.mjs); [prior 17 tests](https://github.com/reallakshman19/XML_Compare_Utilities/blob/f1ffe90dee5b559c0781ce44f134e22f1f1da656/tests/ciifr-wbs4-five-field-evidence.test.mjs). IR3 source and false-digest counterexample: [#188/6423929691](https://github.com/reallakshman19/XML_Compare_Utilities/issues/188#issuecomment-6423929691).

Reviewer's Node v22 Linux Git-blob-identical subtree **24 PASS, 536 independent assertions** is bounded local evidence. The repository's hosted workflow only ran catalog13 + NodeName19. Full actual checkout, official backup-script compliance, hosted inspector24, Windows, protected original and native CAESAR remain NOT_RUN/UNVERIFIED. That is why the next proposed operational qualification is valuable and also why *more E1 synthetic tests alone* are not the highest-value new result.
