# CIIFR-Node · requirements trace matrix (R0–Release)

**Source of truth:** [Owner WBS #227](https://github.com/reallakshman19/XML_Compare_Utilities/issues/227). **Detailed semantics:** [Full concept at PR226 exact head](https://github.com/reallakshman19/XML_Compare_Utilities/blob/b2b695f66fc8dfc907f2b9a493b39bd4d4109570/docs/ciifr/property-transfer/CONCEPT_NOTE_v1.0.md). **Native build:** [PR226](https://github.com/reallakshman19/XML_Compare_Utilities/pull/226) DRAFT/HOLD. This file is a *public-safe requirements projection*, not a second WBS, engineering acceptance or agent assignment.

Status keys: `R0_CODE` = source committed but unqualified; `DESIGN` = future requirement; `HOLD` = independent/Owner gate absent. Each fixture is described in [FIXTURE_CATALOG.json](FIXTURE_CATALOG.json); positive synthetic witnesses are author exposed and cannot substitute for original/vendor acceptance.

| ID | Phase | Contract / invariant | Independent falsifier or acceptance | Fixture | Current |
|---|---|---|---|---|---|
| N-R01 | P0/P1 | Immutable SOURCE and TARGET0 byte snapshots, separate intake, SHA-256 and version trace | Loading/reloading never mutates inputs; new selection invalidates prior read-only index | F00 F05 | R0_CODE |
| N-R02 | P0/P1 | V14 profile is explicit; unsupported versions/markers fail closed | V11, indented/lowercase marker, duplicates and missing required sections fail | F00 F03 | R0_CODE |
| N-R03 | P1 | CONTROL.NUMELT equals ELEMENTS 15-row blocks | wrong NUMELT, truncated record rejected | F00 F03 | R0_CODE |
| N-R04 | P1 | CONTROL aux counts bounded; NUMNOZ, NOHGRS nonnegative; IZUP only 0/1 | negative hanger/nozzle and IZUP99 fail | F00 F03 | R0_CODE |
| N-R05 | P1 | MISCEL_1 RRMAT element-ordinal entries present and typed (IDs 1–699) | missing, nonnumeric, range invalid rejected; trailing MISC content unqualified | F00 F03 | R0_CODE |
| N-R06 | P1 | Node incident-element index has full FROM/TO ownership | shared node 500 lists E1 and E2 and different P1, not one property | F01 | R0_CODE |
| N-R07 | P1 | Path A exact oriented FROM→TO query, no inferred flow | 400→500 differs from 500→400; same-node no fan-out | F01 F04 | R0_CODE |
| N-R08 | P2 | TO-only discovery enumerates all candidates, requires explicit selection | multiple incoming elements share TO; no first-match selection | F04 | DESIGN |
| N-R09 | P2 | SOURCE/TARGET numbers are document-local; accepted node identity needs independent witness | same numeric IDs different models; ambiguous SOURCE correspondence held | F04 | DESIGN |
| N-R10 | P2 | Element identity includes orientation/ordinal/branch evidence; supports 1:N HOLD | parallel pair, reverse orientation, subdivided path not silently matched | F04 | DESIGN |
| N-R11 | P1/P2 | Element-attached pointers are 1-based auxiliary block indices, not node IDs | shared/out-of-range/orphan pointer rejected | F02 F03 | R0_CODE |
| N-R12 | P1/P3 | RESTRANT occurrence identity = owning element+ptr+slot+node; slot is not DOF direction | 6 physical slots, type/direction distinct, no wrong DOF claim | F02 F03 | R0_CODE |
| N-R13 | P1/P3 | Node/CNode invalid/negative/empty slot inconsistency explicit | negative refs, zero-node with nonzero type blocked | F03 | R0_CODE |
| N-R14 | P3 | Effective restraint stiffness/gap/friction/Tag/GUID require vendor and source semantics | mismatched CNode/direction/unknown tag is HOLD; no writer | F02 F03 | HOLD |
| N-R15 | P1/P3 | DISPLMNT spec belongs to exact node/owner; 9999.99 is free, not zero | original/synthetic positive record plus sentinel contrast | F02 F07 | R0_CODE_PARTIAL |
| N-R16 | P1/P3 | FORCMNT is applied input load, not computed restraint reaction | positive synthetic; original GLRD FORCMNT=0 cannot qualify positive vendor | F02 F06 | R0_CODE_PARTIAL |
| N-R17 | P1/P3 | RIGID belongs to exact element, not all incident node elements | shared node has one rigid owner only; weight/type meaning separate | F02 | R0_CODE |
| N-R18 | P1/P3 | Process T/P/density are element-owned raw lexemes; source-evaluated only when qualified | different P1 at same node, T versus expansion ambiguity, P-case mismatch | F01 F04 | R0_CODE_PARTIAL |
| N-R19 | P3 | Units, cases, material effective data and global configuration matter | same raw number with different units/case is not semantically equal | F04 F06 | HOLD |
| N-R20 | P3 | Material IDs require approved cross-model material identity; raw equal ID insufficient | RRMAT ID equal but actual database/material different remains HOLD | F03 F06 | HOLD |
| N-R21 | P2/P3 | User can resolve conflicting map and get an explicit next manual review instruction | conflict presents options, no default arbitrary choice, provenance recorded | F04 | DESIGN |
| N-R22 | P2/P4 | Any source/target/choice epoch change revokes approvals/exports | stale TARGET SHA or manual changed mapping disables action | F04 F05 | DESIGN |
| N-R23 | P4 | W1 existing-slot writer requires Owner field grant and exact changed-byte allowlist | unexpected field/width/rounding/side effects block export | F03 F07 | HOLD |
| N-R24 | P5 | W2 structural writer updates CONTROL/ELEMENTS/AUX/MISCEL_1 atomically | wrong pointer, RRMAT shift or unadjusted counts block TARGET1 | F03 F07 | HOLD |
| N-R25 | P1/P6 | New tab modules remain isolated from existing Nodal/Normal/Geometry engines | base-PASS/head-FAIL Nodal startup reproduced then fixed at exact head | F05 | R0_CODE_UNVERIFIED |
| N-R26 | P1 | Paired source/served modules are identical | six Git pairs compare bit-for-bit; no stale served module | F05 | AUTHOR_BLOB_PASS |
| N-R27 | P1/P6 | Native Node/Windows/Browser exact-head independent verification | N-01 runs old tests + new source/target UI and negative probes | F05 F07 | NOT_RUN |
| N-R28 | P0/P1 | Owner protected GLRD original remains private with separate receiver proof | N-02 checks actual private byte digest and count ledger; no public original | F06 | NOT_RECEIVED |
| N-R29 | P4/P5 | Licensed CAESAR II original/TARGET1 import and independent byte audit required for writers | vendor rejects byte-valid but invalid engineering file => FAIL | F07 | HOLD |
| N-R30 | P0/P6 | Progress Page project is an auditable source projection, never engineering authority | official CLI generated history, correct Home/WBS and actual published readback | F00 F05 | PAGE_NOT_PUBLISHED |
| N-R31 | P0/P6 | Common public-safe relay has producer/receiver distinct byte receipt | PR publication not equal receiver verification | F00 F06 | RECEIVER_NOT_RUN |
| N-R32 | P0/P6 | No cross-project Cycle/OTM or author self-review authority escalation | new Page project must not bind broad ciifr Geometry Cycle automatically | F05 F07 | HOLD |

## End-user operational flow

**Path A:** Open Property Transfer → choose Node→Element→Data → load locally authorized SOURCE/TARGET0 → enter exact oriented FROM and TO (R0) or TO-only candidate list (P2) → review distinct incident elements, source/target witnesses and manual ambiguity → after later explicit authority only, approve typed existing-field patches and independently validate new TARGET1.

**Path B:** Choose Node→Data → select numeric node → see owning element/pointer/aux group, REST six slots and CNode, displacements/forces and adjacent rigids → explicit occurrence identity and effective property interpretation, not generic node-wide replace → reviewed per-field correction later only after native engineering qualification.

**First three bounded tasks** are [N-01 #228](https://github.com/reallakshman19/XML_Compare_Utilities/issues/228), [N-02 #229](https://github.com/reallakshman19/XML_Compare_Utilities/issues/229), and [N-03 #230](https://github.com/reallakshman19/XML_Compare_Utilities/issues/230). They are PREPARED/UNASSIGNED. Priorities: first qualify existing R0 independently; then original V14 source; then read-only TO-only/identity. **Do not begin P4/P5 under this fixture publication.**
