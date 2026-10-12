# 182-S2-W05 — Source-bound QRT-JUSTIFY-D2 Owner decision packet with live H3 state

2026-10-12 | chat=6acc408a | issue Grade9v3.5 #182 | P4 | aim=v2.1.0 | outcome=O2 | PACKET_DONE | **OWNER_DECISION=NONE / 0 OF 28 ACCEPTED**

Outcome: O2
For the user: No real learner/public release changed. The Owner and named reviewer now have an **exact-head authenticated TEST HTML/print-receipt and independent browser-state trace** of the authored Core2A↔Core1A learning route, including the exact pre-attempt H3 wording and D2 protected-crux review question; this does not accept any QRT cell.
Proof: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38198786141

## Source and actual output binding

- **Named proposed cell:** `QRT-JUSTIFY-D2`; candidate `Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF` (**AUTHORED**, not SOF/NCERT/source Core2), connected Core1A `MIC-TEST-CORE1A-QUAL-G9-CONSECUTIVE-FACTOR-INVARIANTS`. Authored `stem`: “For an arbitrary positive integer m, prove that (m+1)(m+2)(m+3) is divisible by 6. Your argument must cover every m, not only examples.”
- **Question authored source:** `TEST/imo-research/pilots/core1a-render-qualified-divisibility.v1.json` Git blob `002fc44d1038ed5628f5121d7a5d95072b867a3a` on unmerged [PR #186@ef3d3e2](https://github.com/reallakshman19/Grade9v3.5/pull/186). SHA-256 source bytes recorded by CI `3fcd9909dc1d5cb0bff651e10b21299da9493722768807486a458db5ba57481e`. Earlier packet source blob `e8b1dca...` referred to the old authored *quick-check* before W02's localized content fix; **question, its H1-H3 and QRT candidate identity remain unchanged**, but **this refreshed receipt must use the new source SHA**.
- **Actual connected product:** `TEST/products/core-authored-qrt-repair-journey.manifest.json` (existing authored TEST selection), roles `CORE1A,CORE2A`, `core2=[]`. Exact hosted CI [38198786141](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38198786141) artifact `11724532767` contains actual `core2a.html`, `core1a.html`, both PDFs, `deploy-receipt.json`, `print-receipt.json`, browser evidence/screenshot and QRT qualification. Current Core2A HTML SHA-256 `50f89ccb1ba984b7b1e36757d38ed340d66c31e9b96b3a08df88a676e9bb7bab` and learner PDF SHA-256 `1ee26eab43f26a874784574210e7abb25e57b042d90f8ad1cc9b907868222e85`, **each matching print-receipt hashes**.
- **Authority and stable demands:** `Shared/quality/question-demand-matrix.v1.json` blob `3779a53ae7d20efbb4644bc3f9243909e93dc145` defines JUSTIFY as claim→warrant→conclusion, `W` as the decisive warrant/inference/proof step. `D2` protects **a short connection or choice plus its execution**: familiar principles may be presented but connection belongs to learner. Authored question `extensions.grade9v3:cognitive_demand.primary=JUSTIFY`, secondary `REPRESENT`; author five-score vector is (concept/model 1, representation 1, reasoning chain 1, computation 0, trap sensitivity 1) = **4 / D2**, **not independently accepted**. The canonical `answer.crux_move_ref` is **`MOVE-TEST-CORE2A-WARRANT`** (DECIDE), same move supported by H2/H3, not a new invented step.
- **Accepted matrix snapshot:** `TEST/imo-research/verification/qrt-proposed-coverage.v1.json` Git blob `c81b32875be6f239a877e8df95252be1b7741a00`, sample accepted numerator **0/28**. This authored question's proposed cell must not be counted as official sample acceptance. Existing Owner worksheet [182-T4](https://github.com/reallakshman19/Common/blob/main/coordination/Session_Oct09/Tab1_imo_core_blueprints/QRT_JUSTIFY_D2_REVIEW_PACKET.md) listed the 12 human asks but had `Actual Core1A/Core2A page URLs, bytes and SHA: NOT_RUN`; this exact-head work fills that **technical evidence** gap but deliberately not the human/Owner verdict.

## Actual pre-attempt browser state and three scaffold requests

LOCAL Chromium loaded **the exact UTF-8 Core2A HTML bytes from hosted artifact** through `page.set_content` (not public URL, not a human screen reader). Real DOM and click progression:

| State | Actual text presented to learner | Technical observation |
| --- | --- | --- |
| H1, page opening | “Keep m arbitrary. Can a few checked examples establish a result for every m? State what a general proof must ensure.” | **Visible initially**; universal goal clarified without the winning factor. |
| H2, first **Next hint** click | “What would it mean to guarantee divisibility of the whole product by 6? Identify the kind of general warrant you need, without deciding which factor provides it.” | **Requestable before attempt**; points toward claim/warrant, avoids choosing factor. |
| H3, second **Next hint** click | “Do not assume one factor supplies every divisor. Can you make separate universal claims about two coprime divisor contributions, and verify that each applies to every start?” | **Requestable before attempt**, while full solution remains closed; this names the two-contribution **coprime combination** at the **authored protected move**. D2 may allow familiar principles, but the remaining learner-owned connection is now ambiguous. **HUMAN/OWNER REVIEW REQUIRED**, not auto PASS/FAIL. |

**Gate on the actual page:** in initial/H3 states `details[data-requires-attempt]` had empty visible `[data-g9-payload-slot]`, `open=false`; clicking commit with a blank attempt **did not unlock** it. After filling an answer and committing, the detail became eligible but **remained closed and its payload stayed empty until explicit summary activation**, which inserted the protected complete four-move reasoning route. This is a functional UI gate, **not cryptographic security**: the full solution exists in an inert HTML `template` in source. Pre-attempt safe figure comprises three unmarked factors `m+1,m+2,m+3`, no explicit 2, 3 or residue conclusions; independent browser saw the exact one-line situation and the hosted print PDF showed that figure. **Only after the committed attempt** does visible full reasoning say parity, all residues 0,1,2 and coprime combination.

**Concept repair:** rendered learner `core2a.html` contains a Core1A anchor link `core1a.html#CU-TEST-CORE1A-QUAL-G9-CONSECUTIVE-FACTOR-PROOF`; exact-head accompanying `core1a.html` **contains that target id**. Hosted browser `journey-browser-report.json` records working browser route to Core1A and no errors across widths 320/390/768/1280/200%-text, with pre-attempt answer locked and post-attempt assistance. That proves technical routing, not pedagogy or a real learner understanding the proof.

**Independent mathematics:** For n=m+1, among consecutive n,n+1 is an even term, among n,n+1,n+2 is one term divisible by 3. Since gcd(2,3)=1 the full triple is divisible by 6 for every positive m. Exhaustive m mod6 classes can independently corroborate case coverage; they do not replace the general warrant. Verify current Core1A teaches the same parity/mod3/coprime construction and the changed four-factor/24 exit remains attempt-gated following prior W02 source fix; no original SOF source admitted.

## Every H/S/P/M Owner review field, no invented disposition

| ID | Exact observable fact or gap | Status for the Owner/reviewer |
| --- | --- | --- |
| **H1** | Initial H1 asks about universal evidence, no divisor witness | TECHNICAL OBSERVED; HUMAN VERDICT **NOT_REVIEWED** |
| **H2** | H2 asks for a general warrant, does not select a winning factor | TECHNICAL OBSERVED; HUMAN VERDICT **NOT_REVIEWED** |
| **H3** | H3 is freely requestable before attempt and names *two coprime divisor contributions*; risks supplying D2's learner-owned connection W | **PROTECTED-CRUX RISK; REVIEW REQUIRED**, no accepted/rejected judgment |
| **S1** | Initial unmarked 3-factor graphic has no proof annotations | TECHNICAL OBSERVED; HUMAN VERDICT **NOT_REVIEWED** |
| **S2** | No extra hint-bearing staged proof picture pre-attempt; single 3-factor stage is authored for orientation | APPLICABILITY TO REVIEW; not a reason to fabricate extra stages |
| **S3** | Same orientation-only figure leaves all residue/coprime execution absent; separate stages may be unnecessary | APPLICABILITY TO REVIEW; HUMAN VERDICT **NOT_REVIEWED** |
| **P1** | Gate initial/after H3 and empty answer rejected: protected full solution not visually released; H3 itself still poses disclosure risk | TECHNICAL PASS for full solution; H3 semantic disposition **NOT_REVIEWED** |
| **P2** | Real `core2a.html#...` repair link exists and its Core1A construction target exists | TECHNICAL PASS; instructional value **NOT_REVIEWED** |
| **P3** | Authored post-attempt route has 4 warrants (representation, parity, exhaustive mod3+coprime, mod6 check), each why-valid; correctness merits academic review | TECHNICAL/ARITHMETIC OBSERVED; HUMAN **NOT_REVIEWED** |
| **M1** | Authored wrong-route hypotheses: finite examples imply proof; chosen factor always provides divisor | HYPOTHESES ONLY, not demonstrated learner misconceptions |
| **M2** | No actual wrong learner responses/independent expert diagnostic differentiation | **NOT_RUN / NOT_REVIEWED** |
| **M3** | Technical repair route into Core1A and four-factor changed-case exit exist; no measured learner repair | TECHNICAL LINK EXISTS; HUMAN **NOT_REVIEWED** |

**Machine-level targeted checks:** 18/18 PASS from exact-head HTML + print-receipt SHA bindings, real Chromium pre/H1/H2/H3/blank-commit/answer-commit/open gating and Core1A repair-anchor existence. Earlier draft local probe erroneously expected the complete protected solution to materialize immediately after answer commit; **observed actual contract correctly keeps it unmaterialized until explicit disclosure**. Corrected the probe; **final 18/18** without product code change. No H3 learner-safe acceptance score is included in 18/18. Hosted exact-head Core1A/QRT journey run `38198786141` SUCCESS with browser `failures=[]`; this is separate from Owner's academic decision. No extra hosted CI run.

## Decision requested (Owner or named independent academic reviewer; do not fill automatically)

```text
Cell: QRT-JUSTIFY-D2 (PROPOSED, not one of the accepted 28)
Question: Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF (AUTHORED TEST)
Question/source Git blob: 002fc44d1038ed5628f5121d7a5d95072b867a3a
Exact rendered CORE2A HTML SHA256: 50f89ccb1ba984b7b1e36757d38ed340d66c31e9b96b3a08df88a676e9bb7bab
Exact CORE1A repair artifact: 38198786141 / artifact 11724532767
Independent reviewer named + credentials: NOT_ASSIGNED
Review date and mathematics/warrant validation: NOT_REVIEWED
H1, H2, H3: NOT_REVIEWED (H3 potential crux disclosure, exact text above)
S1, S2, S3: NOT_REVIEWED (visual-stage applicability must be judged)
P1, P2, P3: NOT_REVIEWED (technical gates observed, semantic signoff reserved)
M1, M2, M3: NOT_REVIEWED (no real learner errors or repair outcome measured)
Recommended disposition by human: NOT_YET_PROVIDED
Owner decision on H3 (preserve, narrow, gate to post-attempt): PENDING
Owner canonical named cell decision + ID/date: NONE
Owner approved goldens and academic/visual print: NONE
Real learner input: NONE (TEST authoring only)
Authentic source rights: NONE
QRT accepted numerator: 0 of 28 (UNCHANGED)
```

**What remains:** ask the **Owner/named independent QRT reviewer** whether pre-attempt H3's two-contribution coprime direction discloses D2's protected W, and if so authorize a precise H3 wording/sequencing revision; then formally decide the named cell using H1–H3, S1–S3, P1–P3, M1–M3. Do not self-accept or modify QRT registry. Both this packet and W03 QA can be completed technically while that Owner decision waits. Owner-parked A4 print issue must not be silently revived as an unrelated CI detour. No product/source/registry modifications during W05.
