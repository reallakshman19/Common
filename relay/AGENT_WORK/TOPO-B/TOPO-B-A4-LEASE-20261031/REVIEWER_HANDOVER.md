# TOPO-B A4 · Independent reviewer handover (source exposed)

**TO:** proposed TopoFix independent reviewer IR `6ae2d5ac`, **only if genuine separate identity and nonparticipation are established**. If you are in the same chat/principal that performed Agent B or Oracle TOPO-B tests, do not claim independent reviewer identity; record conflict and decline. The previous same-chat conflict return is [#6541639348](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239#issuecomment-6541639348). **FROM:** coordinating Oracle; no assertion that this handover has reached the recipient.

**Existing task:** [XCU issue #239](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239). **Original source-exposed brief:** [#6541423437](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239#issuecomment-6541423437). **Scope correction:** [#6541455502](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239#issuecomment-6541455502). **Pin:** `417bf6a954c5a6de72237537e94b05b285191350`; no extra review cycle or production code.

## 0 — Mandatory eligibility and acknowledgment

Declare **actual identity**, whether you authored/contributed to the tested code or native test, whether you participated in **Agent B's V8 or native Node checks**, **Oracle's earlier execution**, fixture packaging, Oracle source derivation or A4 coordination, and prior source/expectation exposure. Identify distinct-person/independent principal basis, not merely a different chat nickname. Public source exposure is permitted, but expected values must be recomputed independently, not copied from Oracle/agent tables.

If identity is not established or participation exists, return `A4_REVIEWER_INELIGIBLE / NO_VERDICT` on **issue #239** without reviewing or scoring. Do not claim the current ChatGPT/Agent B/Oracle conversation is the proposed IR.

## 1 — Reuse existing evidence; do NOT replay completed tests

- [Agent 16 valid V8 checks](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239#issuecomment-6540241149): **16 PASS**, 1 invalid harness assertion excluded; disposable shim, not a real DOM parser.
- [Oracle native Node+xmldom execution](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239#issuecomment-6540928961) and [Agent B native receipt](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239#issuecomment-6541051780): **7 PASS / 0 FAIL / 0 SKIP**, actual Node v22.16.0, xmldom v0.9.8, unchanged `adapter.test.mjs`, pin/fixture source SHA, 20/20 before/after unchanged, ZIP recipient delivery/ACK.
- [Oracle last gate read](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239#issuecomment-6541589959): current strict reader APIs exist; **unimplemented universal router has no validation result**. Do not infer GLRD or physical engineering acceptance.
- The R4 and F05 XML public fixtures represent **one S1 source in two encodings**; not two independent engineering models. Original GLRD XML is protected/not a qualified P1.v1 reader input.

## 2 — Source-exposed independent geometry witness

Read original public fixture **raw fields and COORDS records first**:
- [S1-F05.xml](https://github.com/reallakshman19/XML_Compare_Utilities/blob/417bf6a954c5a6de72237537e94b05b285191350/prototypes/ciifr-map/tests/fixtures/S1-F05.xml)
- [S1-R4.xml](https://github.com/reallakshman19/XML_Compare_Utilities/blob/417bf6a954c5a6de72237537e94b05b285191350/prototypes/ciifr-map/tests/fixtures/S1-R4.xml)
- [fixture manifest](https://github.com/reallakshman19/XML_Compare_Utilities/blob/417bf6a954c5a6de72237537e94b05b285191350/prototypes/ciifr-map/tests/fixtures/manifest.json)
- [strict parser](https://github.com/reallakshman19/XML_Compare_Utilities/blob/417bf6a954c5a6de72237537e94b05b285191350/prototypes/ciifr-map/xml-profiles.js), [intake](https://github.com/reallakshman19/XML_Compare_Utilities/blob/417bf6a954c5a6de72237537e94b05b285191350/prototypes/ciifr-map/xml-intake.js), [graph](https://github.com/reallakshman19/XML_Compare_Utilities/blob/417bf6a954c5a6de72237537e94b05b285191350/prototypes/ciifr-map/xml-graph.js), [unchanged original tests](https://github.com/reallakshman19/XML_Compare_Utilities/blob/417bf6a954c5a6de72237537e94b05b285191350/prototypes/ciifr-map/tests/adapter.test.mjs).

Independently identify the source field/row locations and calculate signed metric geometry from seed and deltas for the **3790→3830→3840** chain. Predict **endpoint+signed-delta reversal** versus **sign-only ΔY mutation**, showing numerical differences and the raw source evidence you used. Existing Oracle/agent reports already disclose sample answers, so **derive your own worksheet before using them for comparison**. Challenge one plausible wrong parser/graph implementation, such as lost sign, anchor substitution, missing seed, or cross-generation stale result. Keep source XML SHA separate from any claimed original-CII SHA.

## 3 — Admission behavior and boundary

Independently assess source and existing native receipts for **supported F05 P1.v1.1 and R4 RichInputXMLv2.1**, and rejects on **unsupported F05 P1.v1 marker**, invalid root/schema, forbidden DTD/entity, unsupported units, field/count mismatch, absent/mismatched COORDS anchor, wrong expected digest, and stale generation. Mark each result `PASS / FAIL / NOT_RUN` with evidence class `implementation-coupled test` vs independently derived expectation.

Distinguish **generic detection**, **strict F05/R4 reader**, and **not-yet-built universal format-admission router**. Generic detector's F05-as-InputXML/R4-as-UNKNOWN classifications are not format-specific admission. Proposed behavior `UNSUPPORTED_INPUT` rather than zero-nodes success is an **implementation requirement**, not a verified present router result. GLRD `RichInputXML-P1.v1` 521 records remains **UNKNOWN_PROFILE**, not an approved XML graph nor a writer input. No writer/physical/connection authority.

## 4 — Scoring and return contract

Read [AGENTS.md Appendix A](https://github.com/reallakshman19/XML_Compare_Utilities/blob/417bf6a954c5a6de72237537e94b05b285191350/AGENTS.md): normally **A1 Production Trace, A2 Current Failure Isolation, A3 Authority/Invariant, A4 Independent Validation, A5 Minimal Patch; each ≥17/20, total ≥92/100**. Agent's prior `19/19/20/16/19 = 93/100` is **self-scored history**, not independent qualification. Report your **own justified A1–A5**, including actual A4 numerator and denominator, any decisive falsifier, precise source/field evidence, whether you accept the native receipts, and scope exclusions. Do not inflate A4 by automatically counting a same-tests rerun. A focused new original-field falsifier is optional only when truly discriminating.

Return one **`QUALIFIED_SCOPED / PARTIAL / NOT_QUALIFIED`** result to [native issue #239](https://github.com/reallakshman19/XML_Compare_Utilities/issues/239), separately documenting whether the **prospective two-new-file implementation takeover gate** is independently sufficient. If the early eligibility check fails, return **`INELIGIBLE / NO_VERDICT`** instead; do not force a score.

**HOLD:** READ_ONLY; do not modify files, open PRs, implement router, treat GLRD or CII Writer/Weight/Final as qualified, certify engineering connections or authorize merge.

**Required recipient receipt:** record exact reviewed `main` SHA, this relay PR head after actually fetching, actual source/expectation method, identity/independence, and decision URL in #239. This document is handover prepared, **not evidence of your receipt**.
