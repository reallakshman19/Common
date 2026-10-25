# Two source-grounded mentoring examples — historical, NOT live qualification

These examples are reconstructed from the Owner's supplied **Word-to-Table** and **CIIFR/CII** discussion excerpts. They illustrate how an Oracle teaches and checks consequential understanding with approximately three conversational questions. **Neither is an executed acceptance trial**; original private Word files/screenshots/CII bytes are not included in this public example. An Oracle must reopen the actual permitted originals, current Project Home, implementation and vendor/schema sources before assigning or verifying work.

## Example A — Word .doc/.docx → structured tables

### What the Owner was actually asking for

A converter that allows **user-selected header rows and dynamic record-row merging** while giving every part of the original source a visible outcome: structured content, header/context, explicit exclusion or **unconverted/orphan content with location and reason**. "95% structured, 100% accounted for" is the guiding distinction—not a demonstrated performance figure. Missing 5% must remain inspectable rather than silently disappearing. Flexible table semantics include zero/one/two-level headers, spanning columns, headers separated into another table, matrices, nested tables, page continuations and row/column context. The supplied discussion mentioned 131 top-level Word tables and nine nested ones in one historical fixture; **these were user-supplied historical observations, not independently retrieved here**.

**Mentor + new agent, during source walkthrough:**

**Q1 / why:** "A document reports 95% converted. What makes that useful—or still incorrect—for its user?"

- Helpful alignment: every inventoried source fragment is accounted for, every output value has source provenance, unresolved text is accessible, and **semantic correctness is separately reviewed**. Coverage is not correctness; an orphan ledger is as important as the structured table.
- If the agent says "95% is a PASS, so we drop the remainder," show one original unmatched line/cell and update the design assumption.

**Q2 / difficult model:** "The visible heading is in a separate Word table; the next table contains two-level column headings and merged record rows. How do you get one logical dataset without changing the original?"

- Trace original document identity → table path/row/cell/span → selected logical header/data purpose → join table blocks **versus** combine record rows → mapped value and transformation rule → reverse source location. Preserve hierarchical headings; do not confuse an empty cell, omitted grid position, merge continuation and literal hyphen. A matrix value can depend on both row and column headers.
- Plausible wrong case: a flattened table looks complete but a merged-cell continuation or a residual cell fragment vanishes; verify source-fragment disposition and a meaningful opposite example.
- The historical proposal used `ARCHITECTURE.md`, `SCHEMAS.md`, `ROADMAP.md`; **the existence/current content of those local documents is not verified by this example**.

**Q3 / next connected result:** "What is the smallest genuine user-facing demonstration that makes the next table types safe?"

- Candidate bounded task: on an **authorized original source sample**, demonstrate selectable 0/1/2 header levels, row/block joins, structured preview, clickable source-backed exception list, and inventory reconciliation. Report mapped/unresolved/excluded separately. Validate opposite cases such as a header-only block and an uncovered text span; do not silently manufacture headings.
- Downstream result: only after source accounting and mapping are trustworthy, extend to document-wide import/legacy `.doc` qualification or semantic review. Do not assume legacy `.doc` import is already correct.

**Mentor's recovery if confused:** open the relevant original table and screenshot; explain the particular row/cell layout; revise only the affected mapping idea, then return to the issued task. No score or repeated onboarding.

## Example B — CIIFR/CII effective engineering meaning

### Why the first Oracle step matters

In the supplied conversation, the Oracle initially discussed coordination before it could explain the actual CII engineering record. The Owner challenged it to inspect the CII and the Hexagon CAESAR II v14 **Basic Element Data** documentation. The key distinction is **stored element fields vs effective engineering properties**, where verified field-specific defaults/inheritance/auxiliary references and units may affect following elements even without changing their raw bytes. The historical Oracle reported that CII identity had been checked, but the **actual field-by-field layout, inheritance encodings, auxiliary relationships and RichInputXML schema had not yet been fully reconciled**. The lesson is to ground the Oracle, not to force a fast confident explanation.

**Q1 / why:** "Is the goal to copy CII values into XML tags, or to transfer the same effective piping model?"

- Helpful alignment: preserve engineering semantics, node connectivity, effective material/property/auxiliary meaning, provenance and conditions through a supported CII ↔ RichInputXML transformation. Successful parsing or unchanged bytes alone is not sufficient.

**Q2 / difficult model:** "A later element stores no new explicit value. If an earlier element's pressure/property changes, can the later element's effective value change even though its bytes do not? What about auxiliary pointer zero and the documented `9999.99` examples?"

- Trace one actual CII element and the relevant auxiliary records using **the specific CAESAR II version's authoritative field definitions**, applicable units and parser code; distinguish *explicit/inherited/unspecified/unverified* meaning with its origin. Pointer `0` denotes no associated auxiliary record in the cited pointer context; the `9999.99` examples are field-specific, **not universal**. In the historical discussion the pressure A→B→C carry-forward was *illustrative*, **not verification of the numeric encoding in the provided file**.
- Plausible wrong case: changing B explicitly changes effective property at C without changing C's raw fields; or treating `9999.99` as a genuine displacement. A raw-file diff alone would miss the engineering drift.
- Do not assert that all such fields inherit, or that the supplied file uses a particular sentinel encoding, until field-level source reconciliation.

**Q3 / next connected result:** "Before authorizing a CII→XML reconstruction or scoped property transfer, which original element and export must we trace, and how would we detect an incorrect downstream engineering change?"

- First bounded read-only task: on a permitted CII source at a verified hash, trace one complete element through the existing parser and relevant v14 documentation; identify its effective fields, auxiliary pointers, units and one downstream dependent. Compare against an **authentic corresponding RichInputXML example/schema**, if actually available. Report exact unverified field rules, provenance and a positive/negative contrast.
- Next dependent delivery: only once that interpretation has real source support, implement/qualify scoped transfer and validate both raw-byte changes **and** effective engineering state outside the intended scope. Do not claim a complete converter from a schema sketch.

**Mentor's recovery if confused:** acknowledge exactly what documentation was read and what file semantics remain unknown; trace an original record before delegating engineering changes. A prepared plan, reviewer label or merged config PR is not evidence that the CII↔XML workflow was qualified.

## CIIFR failure pattern — knowing process is not engineering grounding

The Owner's supplied CIIFR exchange records an Oracle first acknowledging the Common protocol, then creating an ambitious **26-file local framework** (five JavaScript modules, synthetic fixtures, tests and a benchmark). It reported **13/13 native tests** and a read-only original CII inventory (353 ELEMENTS, 258 NODENAME, 38 RIGID records and two node-565 appearances with pointer `0`). Those are useful *structural/algorithmic observations*, not a qualification of the effective ELEMENTS process fields, RIGID type/weight meanings, field-specific sentinel rules, downstream propagation or authorized writer behavior. The local ZIP's manifest was checked, but **Common/GitHub relay publication was BLOCKED**; a local ZIP is not a handover another agent can retrieve.

The improved Oracle sequence is **not** "run a three-question test, then build the same framework":

1. Trace one real ELEMENTS record and referenced auxiliary record through the existing parser plus authoritative v14 field documentation. Distinguish observed bytes/pointers from assumptions about *effective* engineering behavior.
2. State one plausible misleading-success case (for example, unchanged later element bytes with changed inherited effective properties). Name the exact source/field rule needed to distinguish it. Until verified, keep related modules **EXPLORATORY/READ_ONLY** and conclusions `UNKNOWN` rather than asserting a qualified engineering architecture.
3. Select the smallest next useful deliverable and the **actual** artifact recipient/relay route. Distinguish synthetic 353/1,000/3,000-element timing from a *single* Owner original-file timing; record warm-up, sample size, platform and statistic, never call the slowest of three samples a credible empirical p95. If relay is blocked, return `NOT_TRANSFERRED`, preserve reusable work and identify the smallest permitted transport remedy—do not repack the entire framework as a new "completed handover."

This is a **historical adverse example** from the user's pasted chat, not a replay of the real source or proof of the current CIIFR implementation. When a new Oracle arrives, the current revision, actual project Home, active writer/assignment and private input custody must be rechecked before dispatch or cutover.

## If the incoming participant is the Oracle

Use **the same three themes**, but require the person to **inherit the work context**, not just one file:

- WHY: state actual project outcome and original Owner constraints in accessible source terms.
- HOW: trace the highest-risk source-to-result path, preserve two consequential decisions, one rejected shortcut and its contrary case; expose remaining unknown semantics.
- NEXT: identify existing agents/returns, one meaningful frontier result, the following dependent result, exact ownership and what must remain read-only until the actual control/lease cutover.

No new chat is an authenticated Oracle successor merely because it can answer these questions. Record a source-linked correction in the **existing** handover when consequential; do not create a universal four-file package, quiz or new acceptance gate.
