# T5 Owner evidence packet — Q003 original Core2 + authored-concept Core1A

**Issue [#183](https://github.com/reallakshman19/Grade9v3.5/issues/183)** · chat `6acd1e6b` · plan **r7** · aim **v3.1.0** · 13 Oct 2026 Dubai · task **183-T5-G2-W1 / O3** · **SOURCE-SAFE, DEVELOPMENT-ONLY CANDIDATE — NOT ACCEPTED**

**Outcome: O3**  
**For the user:** A real native Core2/Core1A **TEST pair** now exists solely on the Owner's local secure machine as Coordinator-reported rendered pages with zero structural gaps. The Core1A has been exercised in a real browser by the Coordinator on the Owner's machine, but has **not** been accepted by the Owner for visuals, pedagogy or QRT. This package queues the precise Owner/independent reviewer decisions; it does NOT accept or merge a QRT cell, license original text, assert printed-source custody, or publish learner pages.  
**Proof:** [Coordinator Core1A native receipt](Q003_G4_R7_COORDINATOR_CORE1A_ZERO_GAP_RECEIPT_2026-10-13.json), [Core1A secure browser checklist](Q003_G4_R7_SECURE_CORE1A_BROWSER_ORACLE_2026-10-13.md), [Owner-approved narrow private Core2 contextual comparison](Q003_G4_R7_OWNER_CONTEXT_COMPARISON_2026-10-12.json).

## 13 Oct 2026 A4 preflight correction — Route B chosen

Coordinator's new preflight is **LOCAL, NOT_RUN**: Node v22.23.2 is present; Playwright 1.63.0 reports installed globally, but Node import from clone and browser executable still need the real run; `pdfinfo` is absent. This is not authority to install Poppler. **Route B selected**, requiring NO third-party installation: the private TEST audit script now traverses the generated PDF page tree to validate page count and all portrait A4 MediaBoxes using built-in Node only. It rejects unknown/corrupt PDFs, wrong page counts or sizes and missing Chromium with sanitized error. Native Core1A source SHA, original HTML and Shared production printer remain untouched.

**Exact code head** `reallakshman19/Grade9v3.5:agent/183-q003-private-core2-test-6acc303b@c62b1cc50d98efcf5ccf400337b34f862a0e440e`; **command from repo root:** `node TEST/imo-research/core2-q003/audit_private_a4.mjs`. Do not run `--include-core2` unless that frozen exact SHA page is independently available in same checkout; Core1A alone is the primary audit.

No protected page/PDF may be published. Generated PDF/receipt remain under ignored `.private/a4-audit`. The actual A4 audit **NOT_RUN** until Coordinator executes it and returns only [source-safe receipt](Q003_G4_R7_A4_AUDIT_NO_POPPLER_CORRECTION_2026-10-13.json) or sanitized error. Successful A4 box geometry would still **not** equal Owner legibility/page-break approval or licensed production PDF link resolution. Keyboard/accessibility remains **DEFERRED_BY_USER**, rights **NOT_GRANTED**, Owner QRT **0/28**.

## 13 Oct 2026 scope reconciliation — no in-chat HTML-upload gate

**Issue #183 does NOT require posting an exact protected/private native HTML page or unredacted screenshot into this chat.** Its O1/O2/O3 acceptance obligations are authentic native renderer-generated pages, source/lesson quality and golden comparison, and the Owner's per-QRT-cell decision under the source-rights/A4 gates. The exact two role pages and candidate golden are already kept in the authorized Owner-local environment; the Coordinator reports they are side by side. This fulfills *review access*, not the Owner's *review verdict*.

Disposition of a proposed request to attach `core1a.html` here: **NOT_REQUIRED_BY_ISSUE / WITHDRAWN**. Do not create a new blocker or seek public transfer of the original stem/options, protected HTML, source JSON, unredacted screenshots, or local PDFs. The Owner may review privately and communicate a source-safe decision with exact SHA, qualitative defects and approval/hold status. If the Owner expressly asks for an in-chat view, only a separately reviewed, independently authored and source-safe illustrative extract may be used; it must **never be presented as the exact native page**. Such an illustration is optional and earns no acceptance credit.

**Unchanged blockers:** actual Owner visual/pedagogic and independent academic verdict (not yet supplied); per-cell QRT decision; original-source Owner confirmation; rights; same-page A4 local run (NOT_RUN). Keyboard/AX check remains **DEFERRED_BY_USER**. The next technical gate remains the SHA-pinned private A4 audit; no extra HTML upload task.

## 13 Oct 2026 technical priority change — keyboard parked; A4 source-page geometry next

The user explicitly instructed **skip and park the remaining keyboard/accessibility inspection** on [issue #183](https://github.com/reallakshman19/Grade9v3.5/issues/183#issuecomment-6136262143). This is **DEFERRED_BY_USER**, not a pass or a waived blueprint requirement. No further keyboard operator prompts should block the current technical lane.

**Next technical work is source-faithful A4, NOT a new rendering or a live QA result.** The registered production `tools/print/print-product.mjs` currently prints **280×175 mm**, which is not an A4 receipt. A separate TEST-only tool [`audit_private_a4.mjs`](https://github.com/reallakshman19/Grade9v3.5/blob/agent/183-q003-private-core2-test-6acc303b/TEST/imo-research/core2-q003/audit_private_a4.mjs) has been committed on the isolated branch (no Shared/renderer changes). It requires the existing SHA `d1fe23c43d1eeae67c69600beef1b5054c361854c3e5cd6742545859592998c0` and native zero-gap receipt; prints that same local native page as private A4 portrait through Playwright with 10mm margins; verifies the PDF page-tree count and **every A4 page MediaBox** using Node built-ins without `pdfinfo`/Poppler; outputs only a source-safe local SHA/geometry receipt. Coordinator preflight found Node 22 and global Playwright 1.63.0 but an unverified Chromium binary; **no third-party installation is authorized or needed**. Route B TEST correction is at `c62b1cc50d98efcf5ccf400337b34f862a0e440e`, with source-safe [A4 preflight/correction receipt](Q003_G4_R7_A4_AUDIT_NO_POPPLER_CORRECTION_2026-10-13.json). The actual private print **has NOT been run**. A4 physical geometry alone is not legibility/page-break acceptance and does not validate the production PDF link. The Owner retains separate A4, display rights and QRT decisions.

## 13 Oct 2026 addendum — Coordinator real-browser evidence (supersedes earlier NOT_RUN fields below)

The Coordinator reports real private-browser testing of the **unchanged** Core1A `f030a0aca51038575778de3489f75d1d629a6b74` / SHA-256 `d1fe23c43d1eeae67c69600beef1b5054c361854c3e5cd6742545859592998c0`, Chromium `152.0.7977.130` inside a desktop app pane on local `127.0.0.1` with clean session/local storage. This is **Coordinator-reported LOCAL**, not G4-independent review or Owner acceptance. [Exact source-safe browser receipt](Q003_G4_R7_COORDINATOR_CORE1A_BROWSER_RECEIPT_2026-10-13.json).

| Check | Reported observation | Disposition |
| --- | --- | --- |
| A0/A1 structure | SHA matched 76,401 bytes; 2 construction headers, 2 worked explanations, 2 result/check blocks, 2 quick checks, 2 formulas, 2 clinics, independent exit | **PASS**, structural observation only |
| A2 mathematical formula tiles | Both open, relationship/meaning readable; 561 characters and 1 math element each; no protected original Q003 stem/options | **PASS**, no independent academic judgement |
| A3 staged visual by mouse | **3 distinct stages/captions per unit, 6 total chips**, selected/pressed state changes, Next/Previous works | **PASS for mouse**; keyboard stages not exercised; no aria-live observed |
| A5 narrow viewport | **375×812**, document width 375px, no body horizontal scrolling; 35 visible controls all **at least 48×48 CSS px**; nested table scroll intentionally; stage graphic **318×67px** and 14px CSS text | **PASS** for measured responsive controls; Owner must decide whether narrow diagram is legible |
| A6 pre-commit independent exit | Blank response and no paper checkbox -> commit refused, focus returns to response, model answer 0 displayed characters/unopenable; one inert source template exists | **PASS** for tested UI (not a claim all protected source bytes absent) |
| A7/A8 commitment | Typed response unlocks 274-character model answer; keyboard Tab→commit/Enter→answer summary/Enter works | **PASS** for exit mouse+keyboard |
| A4/A9/A10/A11 | A4 only exit keyboard tested; clinic/check content not read; Owner's matched visual comparison not judged; Core2 complement not redone | **PARTIAL / NOT_RUN** as specified |
| A4 print, screen-reader, pixel diff, Owner academic, individual QRT | No run or decision | **NOT_RUN / PENDING**, rights NOT_GRANTED |

**Owner/user 13 Oct decision:** focused staged-control keyboard, secondary-disclosure keyboard and browser accessibility-tree checks are **DEFERRED_BY_USER / PARKED**, not PASS or accepted. Do NOT request more keyboard/accessibility operator work in the current lane. No `aria-live` by itself is a **review note, not established failure**. Owner to inspect the 318×67px small diagram and actual teaching quality, while qualified academic reviewer checks two clinics/two quick checks, independent transfer and proposed demand/band. Separate original-paper personal Owner confirmation, A4, QRT and rights gates remain **PENDING**, with **0/28 accepted**. The native `LEARNING_TRANSITIONS` slot remains expected absent (OPTIONAL, no portal root).

## A. Exact two-page private preview to open locally

| Role | Source/renderer identity | Private exact artifact/grounded state | Owner review task |
|---|---|---|---|
| Authentic-source `CORE2` | `BP-CORE2-SOURCE-QUESTION`, native sole `Shared/tools/render_core.py`; frozen source TEST `agent/183-q003-private-core2-test-6acc303b@98ae06741f4d90865fcd313d609aeabba46826e2` | Owner-relayed native `core2.html`: **62,277 bytes**, SHA-256 `827a8a99128601721c3c13dfd99806b5a563624526edfd8ba137ab8d4b64b6a0`, **0 reported gaps** against `G-CORE2-R2` **0**; private 10/12 golden component roles, Owner “approve. conceptually ok” for that **contextual TEST comparison only**. Separate Coordinator browser click/keyboard at 375px reported PASS on named attempt/disclosure checks, not independent review. | Inspect exact original printed question fidelity, answer/crux and faithful ordered options on the Owner's private machine; keep the already Owner-accepted TEST badge/labels/no CONDITIONS/no SOURCE_PDF/one-rung differences out of repair queue. |
| Authored concept `CORE1A` | `BP-CORE1A-CONSTRUCTION@1.8.0`, native sole `Shared/tools/render_core.py`; isolated branch `agent/183-q003-private-core2-test-6acc303b@f030a0aca51038575778de3489f75d1d629a6b74` | Coordinator-reported new native `core1a.html`: **76,401 bytes**, SHA-256 `d1fe23c43d1eeae67c69600beef1b5054c361854c3e5cd6742545859592998c0`, **0 gaps**; candidate `G-MATH-LINEAR-CONSTRAINT` Core1A **64,626 bytes**, SHA-256 `27547f2e31b84f53a2e506ceff137ce1ae4b403c195c79080709fa5f505063d6`, **0 gaps**. Both `render_core/2` and benchmark exit **0** `STRUCTURAL_CHECK_ONLY`. Coordinator has placed the pages side by side and now **reports real Core1A browser tests** (exit gate, typed/keyboard commit, mouse stages, 375px and 48px targets); no Owner visual/pedagogy verdict and no screen reader/A4. | Visual comparison of authentic learner layout to candidate technique golden and concept-specific maths/pedagogy; watch both staged constructions, independent exit, evidence/representative examples; do not count a static role list as approval. |

**Private-only files remain on Owner machine:** `TEST/imo-research/core2-q003/.private/rendered/core2.html` (frozen Core2 receipt), `TEST/imo-research/core2-q003/.private/core1a/rendered/core1a.html` (new), and `golden/units/G-MATH-LINEAR-CONSTRAINT/rendered/core1a.html`. Do not copy the original question, four printed options, original answer, private JSON, full HTML, screenshots or PDF into issue comments/Common. Share only source-safe hashes, role slots, qualitative defects and explicit Owner verdicts.

## B. Core1A native comparison decision — no filler

- **Golden roles:** 13. **Q003 Core1A overlaps 12 of 13 (~92.3%)**, plus the concept-specific `QUESTION_BRIDGE` and `SECTION_ROUTE`. `EQUATIONS` and `STAGED_VISUAL` were missing in the first draft, genuinely authored using relation and independently authored SVG stages, and now appear. No native gaps remain **as reported by Coordinator**, not independently reproduced.
- **`LEARNING_TRANSITIONS` deliberately absent:** the blueprint marks this slot **OPTIONAL**. Native `_core1a_learning_transitions` requires a real site portal root to derive valid Learn/Practice/Question Bank navigation. Private TEST manifest `home_href=index.html` has no parent portal root and `output_roles=[CORE1A]`, so this slot should **not** be fabricated. **Decision: EXPECTED ABSENT / NO TEST CODE ADDITION**, subject to new review only for an actual permitted future deployed portal.
- **Digest non-equality is normal:** `render_core.render_digest` fingerprints renderer plus each manifest, package, bank and other authority file; native original and candidate golden have different source records. Reported Q003 digest `bce31f18481cb4da` versus golden `8433c0370f6a1999` is **not** a demand for identical digests. Exact same input reruns can be checked for reproducibility instead.
- **Maths basis (independently previously reviewed against school-mirror original):** Q003 tests whether one relation accounts for three numerical input-output pairs and one exception; the inferred residual method is `y - x²`, with **+4** for three *printed* source pairs. This fact is a source-safe method description, not a substitute for exact private stem/options custody or the Owner's own examination of the paper.
- **Clearly AUTHORED transfer:** concept worked visual/new pair sequence `(4,23),(6,43),(7,58),(9,88)`: residuals `7,7,9,7`. A **different** independent exit case `(2,9),(3,14),(5,30),(6,43)`: residuals `5,5,5,7`. Neither is an original IMO option; the constructed teaching/visual must preserve that label. Source-specific reasoning must not be inferred solely from the answer key.
- **Actual construction quality to inspect:** two construction units with two action/why-valid/output steps each; equation meaning and validity scope; real staged authored visuals; hardest original Q003 crux connected using source-private authenticated bank ref; bounded misconception/repair and meaningful quick checks; exit demands learner's own changed-case residual decision.

## C. QRT hypothesis — a proposal for review, **not** an accepted classification

Candidate `QRT-MODEL-D2` (**MODEL / Connected reasoning, D2**). The plausible decisive learner act is to **choose and consistently test** one square-offset model instead of re-fitting a different rule per pair. A short model-selection-plus-checking decision, not mere reading of a printed formula, could justify D2; the reported private difficulty assessment is D2, 4/10 overall, 2/4 conceptual. This is an **AUTHOR / G4 PROPOSAL ONLY**. An independent academic reviewer must adjudicate whether the real printed source task instead primarily demands `APPLY` or `REPRESENT`, and whether D2 is justified in the visible learner workflow. Do **not** count the row as proposed in canonical coverage register merely by appending this packet.

No `QRT-MODEL-D2` owner decision ID exists for Q003 here; the 2026-27 sample-only canonical QRT proposal row already has a *different* sample question, and this 2023-24 Q003 does not replace it. No accepted QRT cells change.

### 28-cell visibility for Owner (no canonical ledger mutation)

| Base QRT cell | This packet's scoped Q003 status | Owner acceptance state |
|---|---|---|
| `QRT-RETRIEVE-D1` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-EXPLAIN-D1` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-APPLY-D1` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-MODEL-D1` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-REPRESENT-D1` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-SYNTHESIZE-D1` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-JUSTIFY-D1` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-RETRIEVE-D2` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-EXPLAIN-D2` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-APPLY-D2` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-MODEL-D2` | **Q003 tentative placement; not reviewed** | **NOT ACCEPTED** |
| `QRT-REPRESENT-D2` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-SYNTHESIZE-D2` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-JUSTIFY-D2` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-RETRIEVE-D3` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-EXPLAIN-D3` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-APPLY-D3` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-MODEL-D3` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-REPRESENT-D3` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-SYNTHESIZE-D3` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-JUSTIFY-D3` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-RETRIEVE-D4` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-EXPLAIN-D4` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-APPLY-D4` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-MODEL-D4` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-REPRESENT-D4` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-SYNTHESIZE-D4` | No Q003 claim in this cell | **NOT ACCEPTED** |
| `QRT-JUSTIFY-D4` | No Q003 claim in this cell | **NOT ACCEPTED** |

Canonical 28-cell matrix authority: `Shared/quality/question-demand-matrix.v1.json` (7 demands × 4 bands); current accepted coverage **0/28**, unchanged. Q003 contributes **one candidate placement at most**, not 28 cells of evidence.

## D. Review observations still required before any Owner cell decision

| Review proof item | Present/source | Reviewer status / what is missing |
|---|---|---|
| Source custody & precise original | Private input SHA `b263644cd1dd8aca689582232c9b8495f05ec07f3ffeaff3a18f414e6e1227f9`; source item SHA `31ce624340b8d223c50c27797d6e5f7211b03f9365f2f0db387461e7375051b2`; school-mirror printed page 2/Q003 public visually inspected by G4; private stem/options exact-match Coordinator-reported. | **Owner personally confirming original printed-paper inspection is UNCONFIRMED**. Publisher authenticated PDF binary custody absent. Request source-private original-vs-transcript comparison and explicit Owner confirmation (or reject provenance string `PYQ_VERIFIED_OWNER_INSPECTED_FOR_DEVELOPMENT_ONLY` until true). |
| Native Core2 and golden | Coordinator/Owner reports 0 gaps Core2; 10/12 context roles; Owner approved limited TEST differences. | No academic QRT decision from that approval; protected answer consistency with source must be visually adjudicated on secure machine. |
| Native Core1A & golden | New Coordinator report 0/0 gaps and 12/13 slots, extra bridge/route; `LEARNING_TRANSITIONS` optional/absent as expected. | **Structural portion met, LOCAL claim**; Owner visual and independent pedagogical assessment PENDING. |
| Actual Core1A browser | **Coordinator-reported LOCAL test completed in Chromium 152.0.7977.130** on exact 76,401-byte SHA: real mouse stage chips/Next/Previous, equation disclosures, 375px/no body overflow, 35 controls ≥48px, blank attempt refusal, typed commit and keyboard-only exit model answer. [Full source-safe A0–A11 receipt](Q003_G4_R7_COORDINATOR_CORE1A_BROWSER_RECEIPT_2026-10-13.json). | **Deferred by user:** keyboard-only stage/chip, formula and clinic traversal (A4 PARTIAL). **Still open separately:** semantic diagnosis/quick-check review (A9 NOT_RUN); actual Owner golden side-by-side review (A10 NOT_RUN). No aria-live in staged diagram reported (not automatically a violation). |
| H1/H2/H3, S1/S2/S3, P1/P2/P3, M1/M2/M3 matrix | Canonical `Shared/quality/question-demand-matrix.v1.json`, 12 semantic asks. Core2 source-specific first hint and post-attempt support are Coordinator-reported, original Core1A teaching visual and exit rendered only. | **Reviewer verdict PENDING for each ask**: PASS/FAIL/NOT_APPLICABLE+why/UNKNOWN with source-private rationale; do not force 3 source hint rungs or a Core2 source visual into an item that lacks them. Core1A teaching stages are not a substitute for Core2 protected stage evidence. See review grid below. |
| Accessibility/real devices | Core2 keyboard+375x812 reported by Coordinator; Core1A Chromium 152 local at **375x812** PASS no document sideways scroll, all 35 visible interactive controls ≥48×48 CSS px, independent exit keyboard PASS. Staged diagram 318×67 px at reported CSS 14px type; per-component table scroll is intentionally nested. | **DEFERRED_BY_USER:** full keyboard traversal of stage controls/disclosures and accessibility-tree state inspection; NOT passed or closed. Actual screen reader NOT_RUN; Owner small-diagram legibility decision pending. |
| Same-page native A4 | **NOT_RUN**. TEST-only SHA-gated geometry audit `audit_private_a4.mjs` now committed, but no private A4 PDF receipt produced. Existing registered Shared printer currently requests **280×175 mm**, not A4. | **Next technical gate:** local QA print of the exact existing native HTML to A4, verify physical PDF geometry and page count; then Owner evaluates clipping/legibility and separately authorizes the proper deployment print path. No print acceptance inferred. |
| Publisher/public use | Rights `NOT_GRANTED`; development-only isolated TEST display approved for local study, no publication. | **Owner separate rights/display-mode decision reserved**; no unlicensed publishing/merge. |
| CI and PR | No new hosted CI; product code in isolated TEST only, no PR; main/Shared writer serial #212. | Native operator local exit 0 is not a hosted CI run. No release or writer-lease bypass. |

### Canonical 12-ask review grid (to be filled by an authorized academic reviewer)

| Ask | Evidence required to judge on original private page / authored lesson | Qualified reviewer verdict | Owner cell disposition |
|---|---|---|---|
| H1 | Pre-attempt source-authored orientation clarifies rule-selection crux without revealing answer. | PENDING | PENDING |
| H2 | Connects relevant known square relation to input-output checks only at allowed disclosure stage. | PENDING / N/A with reason | PENDING |
| H3 | Posture opens route while preserving the D2 learner-owned relation test until actual attempt; no forced fabricated source rung. | PENDING / N/A with reason | PENDING |
| S1 | Source-role stage safely sets up question; if no original source image/stages, written N/A justified. | PENDING / N/A | PENDING |
| S2 | Visual supports meaning of invariant; distinguish authored Core1A teaching stages from original Core2 source image. | PENDING / N/A | PENDING |
| S3 | Progressive stage helps without revealing original Core2 final exception before the permitted attempt. | PENDING / N/A | PENDING |
| P1 | Protected original Core2 answer/crux not revealed before typed commitment; Core1A independent exit independently attempted. | PENDING | PENDING |
| P2 | Core2 to concept bridge/repair links to exact corresponding constructed reasoning move. | PENDING | PENDING |
| P3 | Post-attempt solution warrants are valid and separately verified (not merely pattern-matching four choices). | PENDING | PENDING |
| M1 | Plausible wrong route (change rule mid-list or infer from one pair) is represented. | PENDING | PENDING |
| M2 | Diagnostic differentiates true misconception from one arithmetic slip. | PENDING | PENDING |
| M3 | Repair establishes one fixed residual procedure, then the changed authored exit independently tests transfer. | PENDING | PENDING |

## E. Owner decision placeholders — **intentionally unanswered**

1. **Original source fidelity and printed-paper inspection:** `CONFIRMED_BY_OWNER / NEEDS_CORRECTION / HOLD` — Owner name/date/secure evidence fingerprint: **PENDING**. Do not infer from code's source-status string.
2. **Core1A academic, concept and visual review:** `ACCEPT_PRIVATE_TEST_VISUAL / REVISE / HOLD` — exact local Core1A SHA and any specific problem: **PENDING**.
3. **QRT primary demand and difficulty:** `MODEL-D2 / ANOTHER_CELL_WITH_REASON / REJECT_CLASSIFICATION / HOLD`, with qualified independent academic review and Owner decision ID: **PENDING**.
4. **12 cognitive review asks:** review each above in the private environment and record independent evidence; **PENDING**, no automatic PASS from structural gaps=0.
5. **Owner QRT cell** `QRT-<DEMAND>-<D1..D4>`: `ACCEPT / REVISE / HOLD`, exact source+page digests, reviewer ID/verdict and decision date — **PENDING**; accepted count remains **0/28** until authenticated accepted event.
6. **Same-page A4:** `ACCEPT / REVISE / HOLD`, exact native A4 artifact SHA, print/legibility review — **NOT_RUN**.
7. **Original embedding, publisher rights, and public release:** `RIGHTS_GRANTED_WITH_EVIDENCE / LINK_ONLY_AUTHORISED / DEVELOPMENT_ONLY / HOLD` — rights **NOT_GRANTED**, publication **FORBIDDEN**; do not assume TEST embed approval permits public distribution.
8. **Real browser Core1A and cross-page integration:** operator-reported safe receipt per [QA oracle](Q003_G4_R7_SECURE_CORE1A_BROWSER_ORACLE_2026-10-13.md) — **PENDING**.

**Owner review should use the actual private native Core1A side-by-side with candidate G-MATH-LINEAR-CONSTRAINT already displayed on the Owner's machine.** No public screenshot or protected data is requested.

## F. Workflow next, release boundary

1. Keyboard/accessibility follow-up is **DEFERRED_BY_USER** and should not be requested or performed. The next TECHNICAL gate is privately running the source-safe A4 geometry harness from the already-rendered exact HTML. Semantic/Owner academic inspection of A9/A10 remains separately outstanding.
2. Owner and qualified academic reviewer inspect the private authentic Core2 vs paper and actual Core1A vs golden; decide maths, teaching, layout and provisional QRT classification. If a demonstrated defect exists, authorize/fix it in isolated TEST; no cosmetic slot inflation.
3. Owner alone gives **separate** QRT/A4/rights/display approvals. Only after the exact original Core2 + concept Core1A pair and QRT placement are accepted can `183-T6` / 68-question repetition be unparked.
4. Product main, `Shared/tools/render_core.py` and #212 writer lease unchanged. No PR, no merge, no released learner artifact; existing Coordinator rendering remains **private TEST**.

**Current count: accepted authentic Core2 0/68 · admitted Core1A 0 · Owner accepted QRT 0/28.** This packet is a deliverable, not a quality or publication verdict.
