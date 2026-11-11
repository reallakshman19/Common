# Stage-01: submitting the first REAL cardboard and operator evidence

**Project:** [parent #415](https://github.com/reallakshman19/Common/issues/415)  
**Physical mock-up workpack:** [#417](https://github.com/reallakshman19/Common/issues/417)  
**Draft research PR:** [#418](https://github.com/reallakshman19/Common/pull/418)  
**Current physical state:** **ALL NOT_RUN**. This document is an intake procedure, not test evidence.

## What the parent/adult actually needs to do

1. Print the seven-page [A4 trial kit](https://github.com/reallakshman19/Common/actions/workflows/puppet-415-stage01.yml) at **100% actual size** and physically measure its 100-mm calibration line. If it measures outside the proposed 99–101 mm range, stop and correct print scaling.
2. Assemble one temporary, safely supported 180×280-mm cardboard frame with a 140×240-mm clear opening; two 69×237-mm rearward-opening doors. Mount it apart from the solid rear palace wall, not flush against it.
3. Preserve an open rod corridor for the real Narasimha puppet, shoulder actuator and main stick; do not place a solid tabletop across the 110-mm front/back translation and leave at least 140 mm free beneath the puppet baseline.
4. Start with manually opened and positively held doors. Use the **real candidate Narasimha silhouette WITH its control rods**, not just the 92×180-mm rectangle gauge.
5. **M1:** record minimum physical gap, measured in millimetres, at **approach**, **door plane** and **emerged** positions, including all rods/connectors. Proposed acceptance threshold is 10 mm in each case.
6. **M2:** perform five distinct full open/hold/reveal trials; record each attempt, including failures, jams and door-closing.
7. **M3:** count real participating operators and hands; record who holds the door, body and moving arm. State explicitly whether an unplanned extra hand was needed. Inspect for instability, unsafe edges and pinch points.
8. Take front, top and under-stage photos showing a ruler and mechanism. No identifiable photos of children are necessary. Attach the resulting GitHub URLs in the record.
9. Copy [M1_M3_RECORD_BLANK.json](M1_M3_RECORD_BLANK.json) to a new, locally filled evidence file; replace each null only from actual observation. Add exact evaluated repository commit and photos/measurements. Post that file or its contents to **issue #417**. Do not modify the blank template to fictional values.
10. Run:
    ```bash
    python3 docs/puppetry/issue-417-stage01/physical_evidence_gate.py /path/to/filled-real-observations.json
    ```

Output `INCOMPLETE_HOLD` means recorded data is missing; `RECORDED_FAILURE_HOLD` means a failed threshold/sequence/safety case; `READY_FOR_INDEPENDENT_HUMAN_REVIEW_NOT_APPROVED` means only that the record is complete and its self-reported values meet the numeric criteria.

**This parser does not check photograph authenticity, measure any real cardboard, verify who operated it, or approve child safety.** A separate qualified adult/reviewer must examine the photographs, measurement provenance and actual repeatability before a physical pass can be recorded.

## Do not conflate approvals

- Geometry CI passing ≠ paper actually printed at 100%.
- Seven A4 vector pages ≠ complete stage mechanism.
- A machine-readable complete M1–M3 record ≠ independently validated physical evidence.
- Even independently approved M1–M3 ≠ M4–M8 complete or 180-second performance accepted.
- This protocol does **not** constitute BuddyRunner 1b or authorize a G1 final response 2.

**If there is no physical prototype, the correct answer is `HOLD`** with Owner/adult and M1–M3 as dependencies.