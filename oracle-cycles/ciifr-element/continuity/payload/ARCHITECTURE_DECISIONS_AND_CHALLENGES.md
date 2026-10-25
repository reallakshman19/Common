# CIIFR Element — Architecture Decisions, Challenges and Falsifiers
**Oracle continuity · PUBLIC_SAFE · source-evidence claims, not a release decision**

## Decisions adopted for research and their rejected shortcuts
| Basis / decision | Rejected shortcut | Concrete surviving wrong case |
| --- | --- | --- |
| Owner's additive [WBS 4.x #167](https://github.com/reallakshman19/XML_Compare_Utilities/issues/167); [Geometry WBS3 #166](https://github.com/reallakshman19/XML_Compare_Utilities/issues/166) | Rename/repurpose Geometry Tab3, or create CIIFR-MAP 5.x as a competing Geometry plan | [#179](https://github.com/reallakshman19/XML_Compare_Utilities/issues/179) declares WBS5.x proposal superseded; WBS3.1–3.4 continues review-only, WBS4.0–4.6 adds Element properties |
| Fixed-field element occurrence identity | Generic whitespace parse, global SOURCE→TARGET node offset, or first matching FROM→TO pair | Adjacent negative real fields; duplicate directed pair and independently renumbered nodes must not produce a fabricated unique identity |
| Typed RIGID pointer distinguishes association from value | Unqualified array indexing `RIGID[p-1]` even for pointer 0; treat weight=0 as missing | p0 resolves absent, p1→weight0 resolves present; out-of-range and shared owners fail closed |
| Stored and effective values require independent rules | Copy temperature/pressure/density numbers by column alone | Alpha Tolerance makes 0.002 strain-like; identical stored density with FDM 1.0 vs 1.2 has different effective meaning; altered units/cases |
| V14 RIGID Weight and Type are separate physical items | Infer V14 TYPE preservation from 2019 converter output | `inputxml_to_cii2019.py` serializes only WEIGHT, while V14 vendor lists WEIGHT+TYPE; native import and V14 round-trip still untested |
| Research parser is not Writer | Upgrade author-reported 13/13 invented tests or original census to engineering PASS | The replacement specialist did not read original bytes or native importer; synthetic PASS retains only its local scope |
| Cycle transport != native task != Progress Page | Announce active `Cycle now` from an inactive CURRENT or post retroactive worker receipt | Element `CURRENT.json` remains rev0 PREPARED_NOT_ACTIVE; direct native #178 return exists; Common #493 is not a substitute |
| Independence must be declared | Oracle authors code/PR #176, source-probes own original, then self-certifies as independent reviewer | Source inspector disclosure SELF_ASSESSED, independent vendor research from replacement specialist but original-file proof still NOT_RUN |

## Explicit test matrix
1. **PASS synthetic:** `RIGID_pointer=1; WEIGHT=0; TYPE=2` must be an associated, weightless rigid. **PASS synthetic contrary:** `pointer=0` must be absent, never Python array `[-1]`. [Specialist #178](https://github.com/reallakshman19/XML_Compare_Utilities/issues/178#issuecomment-6401204309).
2. **PASS synthetic demonstration, REAL NOT_RUN:** raw `TEMPERATURE_1=0.002` under threshold 0.05 is interpreted as strain/expansion mode; without actual material/ambient/Alpha source cannot establish a real model's expected thermal loads.
3. **PASS synthetic arithmetic, REAL NOT_RUN:** stored fluid density 800 with FDM1 vs FDM1.2 yields modeled 800 vs 960 (consistent units). Require real operating-case mapping and actual units before claim of equal process state.
4. **NOT_RUN native:** Original V14 RIGID TYPE import and exact output replay; old converter is not a V14 provenance oracle. One original inspected by the Oracle had raw TYPE codes 0,2,4 but that does not establish the whole V14 code/behavior contract.
5. **NOT_RUN for real SOURCE→TARGET pair:** Duplicate pair identity, reversed direction and shared typed pointer across distinct elements; preserve alternatives/conflicts, do not adopt nearest candidate.
6. **Separate E1 catalogue boundary:** [PR #168](https://github.com/reallakshman19/XML_Compare_Utilities/pull/168) exact head `2aeaf7372de66eda3bc082b8d81bf8db43c34f4b`; [independent #170 R2](https://github.com/reallakshman19/XML_Compare_Utilities/issues/170#issuecomment-6401186110) passed scoped F1 empty-section and F2 two-line REDUCERS, all-15 auxiliary guards. F3 V14 CONTROL strict/trailing-slot rule **HOLD**, native importer/source data NOT_RUN. Not a Writer go-ahead.
7. **Separate NodeName Writer boundary:** [PR #176](https://github.com/reallakshman19/XML_Compare_Utilities/pull/176) draft, author contributed; structural pointer-zero creation requires independent original-file/out-of-scope byte review. Element semantic work does not satisfy it.

## High-risk false PASS pathways
- A ZIP digest proves only **input identity**, not engineering correctness; a synthetic test authored with its own expected answer is not an independent falsifier of the intended CII field.
- The protected original is available **in Oracle owner-only Drive staging** per [#178 latest reconciliation](https://github.com/reallakshman19/XML_Compare_Utilities/issues/178#issuecomment-6401449630), but the receiving specialist **has not** retrieved it; a file listed in a Drive folder is not recipient custody.
- Oracle's 353-element original is **different** from the separate WBS4 521-element private baseline in [#167](https://github.com/reallakshman19/XML_Compare_Utilities/issues/167). Never silently mix counts, hashes or acceptance claims.
- The Progress Page's WBS3 G0–G4 cards still reported NOT_STARTED relative to native G1 activity when inspected; it is a **stale projection**, not control authority. Owner's WBS4 cards concern a separate Element stream. Do not start a second CIIFR project tab to hide drift.

## A useful next decision, not a new approval ritual
The Oracle's next safe move is to close the **receiver side of the existing private original** handoff and distinguish external configuration that actually exists from fields still absent. Once receiver byte size/SHA and source/config are known, issue one bounded read-only original-to-effective-property trace. Do not hold unrelated source/WBS work behind native-import acceptance; do not release an Element Writer or reassign Geometry from an academic field-offset result.

## Deferred decisions to preserve
Type editing, new RIGID attachment/reindexing, FROM/TO graph-atomic renumbering, true SOURCE→TARGET mutator, native importer-qualified TARGET1, P3, merge/deploy, and any control-epoch transfer require their actual later authorized scopes. The successor may challenge these assumptions from source without receiving Writer authority.
