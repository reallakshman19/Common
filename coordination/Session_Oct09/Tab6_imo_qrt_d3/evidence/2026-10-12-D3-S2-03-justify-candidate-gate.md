# D3-S2-03 | JUSTIFY-D3 independent candidate mathematics and role gate | 2026-10-12

Outcome: **O1** — determine whether the last D3 cell has a mathematically sound, independently defensible authored TEST question suitable for a registered-blueprint/golden five-role journey; **O2 prerequisite only** — prepare a qualified-reviewable protected JUSTIFY move without claiming a QRT decision.
For the user: **Nothing yet in the real/public learner workflow**. No QRT-JUSTIFY-D3 five-role page was authored, rendered, accepted or published by this task; the decision is a read-only evidence gate for a bounded next implementation.
Proof: exact existing authored [PR#155@a9e68883](https://github.com/reallakshman19/Grade9v3.5/blob/a9e68883d71afd2e8b7a0c067eedc23ee4da7ef8/TEST/imo-research/pilots/core1a-qrt-justify-d3-authored.v1.json), [PR#166@48007ccf](https://github.com/reallakshman19/Grade9v3.5/blob/48007ccf962ed03f9f6a5423fe7525eaba9cfdf1/TEST/imo-research/pilots/blueprint-first-five-transfer.v1.json), and this read-only mathematical proof/check; [current-head #193 SYNTHESIZE workflow](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38277127996).

## Decision

**PASS_MATH / CONDITIONAL_ENGINEERING_CANDIDATE; ACADEMIC_D3_UNREVIEWED; FIVE_ROLE_NOT_DELIVERED.** Prefer adapting the **PR#166 `Q-TEST-IMO-164-TRIPLE-12-IFF-BOUNDARY`** AUTHORED TEST mathematics into a *new distinct five-role* QRT-JUSTIFY-D3 package in the conditional next workpack task D3-S2-04, subject to retaining learner ownership of the key inference and separate independent qualified academic review. This is not an accepted D3 cell or a source/merge/release authorization. A current author-derived difficulty score or computational proof check alone cannot replace a qualified D3 learner judgment. If real preattempt pages cue the successful residue classes or Core1B/transfer repeat the main answer, return REVISIONS_REQUIRED rather than claim technical delivery.

Why NOT blindly copy: #155's `Q-TEST-IMO-G9-AUTHORED-001-JUSTIFY-D3` states the same universal claim `6|n(n+1)(n+2)` already made by its `Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF` (explicit D2), despite rewording it as prove/disprove and adding examples discussion; it does not demonstrate added D3 protected work. #155 also has separate unadmitted `TEST/imo-research/pilots/justify-d3-boundary-24.authored-proposal.v1.json` (blob `406e77dfd95677b1239041be23967111ca073cf2`), combining false 12 claim with a universal four-factor/24 assertion that overlaps the existing Core1A independent exit. #166's isolated iff-12 alternative focuses the genuinely changed mathematical demand without bundling that already-taught exit as novel. Neither PR#155 nor #166 currently delivers all five QRT-JUSTIFY-D3 roles.

## Exact provenance / scope

- Current owning issue [#182](https://github.com/reallakshman19/Grade9v3.5/issues/182), [r2 plan](https://github.com/reallakshman19/Grade9v3.5/issues/182#issuecomment-6127768791), G1 closed BuddyRunner Stage2 [handover](https://github.com/reallakshman19/Common/blob/main/coordination/Session_Oct09/Tab6_imo_qrt_d3/handovers/2026-10-12-g1-2.md). Chat `6accf855`; task is **READ ONLY** in Grade9v3.5.
- #155 draft HEAD `a9e68883d71afd2e8b7a0c067eedc23ee4da7ef8`; package blob `9231182895e460e02b9658763bf2ff633679a7fb` (AUTHORED, `grade9v3:qrt_admitted=false`).
- #166 draft HEAD `48007ccf962ed03f9f6a5423fe7525eaba9cfdf1`; package blob `3a1c862dd1c6e83c9e2530cdc540c24050c054bd`. Candidate question `Q-TEST-IMO-164-TRIPLE-12-IFF-BOUNDARY`: origin `AUTHORED`, `grade9v3:qrt_status=PROPOSED_NOT_ACCEPTED`, `band=D3` **PROPOSED ONLY**, author-derived score 7 from `(2,1,2,0,2)`, primary cognitive demand JUSTIFY, protected move `MOVE-IMO-164-BOUNDARY-CRUX`, answer reasoned under author verification but **not independent academic acceptance**.
- #166 isolated candidate [boundary-12 manifest](https://github.com/reallakshman19/Grade9v3.5/blob/48007ccf962ed03f9f6a5423fe7525eaba9cfdf1/TEST/products/imo-g9-blueprint-boundary-12-transfer.manifest.json) blob `003aded9e141d77a5fba030227c4e0ae12736980` selects exactly **CORE2A, CORE1A, CORE2B**. Its main CORE2A selection is `Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF` (D2), while **the 12 iff candidate is its CORE2B**. The alternative [five-factor/120 manifest](https://github.com/reallakshman19/Grade9v3.5/blob/48007ccf962ed03f9f6a5423fe7525eaba9cfdf1/TEST/products/imo-g9-blueprint-first-five-transfer.manifest.json) likewise selects only three roles and chooses five factors/120 as CORE2B. Both have `selection.core2=[]`. The alternative is NOT an already built five-role D3 main-question journey.
- PR#166 [transfer-comparison author worksheet](https://github.com/reallakshman19/Grade9v3.5/blob/48007ccf962ed03f9f6a5423fe7525eaba9cfdf1/TEST/imo-research/pilots/transfer-comparison-164.v1.json) has `selected_academic_variant=null`, `independent_math_review=false`, `qrt_accepted=false`, `reviewer_name=null`, all twelve H/S/P/M review slots `NOT_REVIEWED` and verdict `UNDECIDED_NO_INDEPENDENT_REVIEW`. The resulting D3 label cannot be self-signed by this technical gate.
- Authored resource `SRC-TEST-IMO-164-AUTHORED` is `origin=AUTHORED`, `rights_status="Original independent authoring only; no publisher rights asserted"`; no official 68-question SOF material is admitted. The same is true of Core1A AUTHORED source. Reuse concerns mathematical ideas; preserve provenance and create an independent owned TEST record rather than altering or merging competing pilot #166.
- Canonical [JUSTIFY matrix](https://github.com/reallakshman19/Grade9v3.5/blob/55107247ddcbeeb0cb1d160e114dc7bcff5c7984/Shared/quality/question-demand-matrix.v1.json) defines protected W as **the decisive warrant, inference, or proof step establishing the conclusion**; a counterexample alone does not finish the iff classification.

## Complete proof of iff — independent, not sample-based

Let `P(n)=n(n+1)(n+2)`, `n∈Z_{>0}`. Every three consecutive integers contain a multiple of 3, so **`3|P(n)` for every n**. Because `gcd(3,4)=1`, **`12|P(n) ⇔ 4|P(n)`** (this is a factorization into coprime requirements; `6|P` by itself is insufficient).

| n mod 4 | Congruence of the factors, 4-divisibility | Result for 12 | Why |
| --- | --- | --- | --- |
| 0 | n itself divisible by 4 | YES | n supplies factor four |
| 1 | n,n+2 odd; n+1 ≡2 mod4 is sole even factor | **NO** | product ≡2 mod4, exactly one factor of two |
| 2 | n+2 divisible by 4 | YES | n+2 supplies factor four |
| 3 | n+1 divisible by 4 | YES | n+1 supplies factor four |

All four residues are exhaustive and exclusive. Sufficiency for residues 0,2,3 follows because 4 divides their product and 3 always does; necessity follows because residue 1 **cannot** supply a factor 4 (v2 exactly 1). Hence, for every positive n,
`12 | n(n+1)(n+2)  ⇔  n mod 4 ∈ {0,2,3}`.
The false universal claim is refuted at n=1, `P(1)=6`; this is a **counterexample only** and not proof of the classification. Independent local Python arithmetic corroborated all twelve residues modulo 12 (n=0,...,11) and 10,000 positive n with **zero mismatches**; those checks do not replace the four-class proof.

Extra transfer **mathematical possibility, not an adopted source item or academic verdict**: on the *same triple*, change requirement from `12|P` to `24|P`, which calls for one further factor of 2. For even n, n and n+2 are both even, one divisible4, so 8 divides P; for odd n, n+1 is the sole even factor, so 8 divides P iff n+1 divisible8, i.e. n≡7 mod8. Since factor3 is still guaranteed,
`24|P(n) ⇔ (n even) OR (n mod 8=7)`.
A new changed-decision transfer could test why n=3 yields P=60 (12 yes, 24 no), while n=7 yields P=504 (24 yes), and require a full new iff proof. Independent local Python verified all n=1..10,000 against this formula and all eight residues modulo8, zero mismatches. Qualified reviewer still must judge whether this transfer is distinct/appropriately D3 and does not get pre-cued by Core1A's four-factor/24 exit.

## Protected learner W / review gate for actual five-role adaptation

Question X: given false inference “triple always divisible by 6 therefore always divisible by 12”, decide truth and **classify exactly** all successful positive n. Held Y: even-factors, modulo-3 completeness and coprimality of 3 and 4, not a published successful residue list. Z: separate a counterexample to “every” from an exhaustive positive-and-negative congruence proof. **Protected W**: the learner must independently identify missing 4-divisibility, choose modulus 4, prove all residues 0/2/3 suffice and 1 fails, and state/prove the iff; not just type `n=1` or repeat `6|P`.

For current #166 candidate, preattempt [SVG](https://github.com/reallakshman19/Grade9v3.5/blob/48007ccf962ed03f9f6a5423fe7525eaba9cfdf1/TEST/imo-research/pilots/assets/triple-boundary-12-attempt-safe.svg) blob `2755ffe0d43e504043bb3448694e2818987d06f6` shows neutral factors and asks universal 12 without marking an answer. H1 asks distinction between counterexample and general classification, H2 advises periodic residue reasoning without naming 4, H3 asks which divisor is guaranteed and which remains without listing residues; current #166 guided Core2B H3 is post typed commitment, and Owner #190/#193 requires AFTER_ATTEMPT, not preattempt result. These textual/asset observations are **not** proof of the future newly authored Core2A actual browser timing, accessibility, safe scene stages, or independent student choice.

Conditional D3-S2-04 authoring acceptance gates (not actions done in this task):
1. CORE1: only the proof principle and exact prerequisite; do not reveal modulus4 successes.
2. CORE1A: three staged, registered BP-CORE1A-CONSTRUCTION units supporting parity/exhaustive proof language with independent *new* exit. Current Core1A four-factor/24 exit and universal triple/6 proof can be **reused** as prerequisites but must not masquerade as fresh JUSTIFY-D3 main W.
3. CORE2A: make the conditional triple/12 iff claim the MAIN supported authored TEST attempt; preattempt figures H1/H2 must not select residue4 or cases; H3 and worked solution are post actual commitment per Owner.
4. CORE1B: a distinct counterexample or wrong-route repair/boundary decision, not merely retype the iff solution. Distinguish “6 implies12”, “one counterexample proves exact iff”, and “all odd n fail” as different misconceptions, with a separate written commitment before disclosure. Reviewer must reject any Core1B duplicate of CORE2A.
5. CORE2B: change the actual mathematical decision (e.g. conditional triple/24 requires v2>=3 vs prior v2>=2) and demand a new defensible universal/conditional proof, not just substitute 24 for 12; do not pre-reveal its successful residues. The exact transfer and academic band are *conditional*, not selected/released.
6. All five role pages plus index must come from the existing five registered blueprints through sole `Shared/tools/render_core.py build --manifest TEST/products/imo182-qrt-d3-justify.manifest.json --out build/imo182-qrt/d3/justify --draft --reference`, `selection.core2=[]`, original AUTHORED figures with zero slots/reference gaps, registered golden T01–T15 technique comparison, exact-head math/schema tests, browser/attempt timing, CI and SHA receipts. No original 68-source Core2 questions or frozen golden change.
7. Independent **qualified academic** reviewer evaluates main D3 protected W, learner profile and all H/S/P/M review probes; Owner alone decides QRT acceptance/golden successor, source admission, merge and release. If true D3 distinction fails at learner level, classify REVISIONS_REQUIRED or propose appropriate band, do not silently claim 7/7.

## Fresh CI / counts / close

PR#193 draft HEAD remains `55107247ddcbeeb0cb1d160e114dc7bcff5c7984` (D3-S2-02 single-field change). The exact-head scoped [SYNTHESIZE workflow 38277127996](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38277127996) is **COMPLETED SUCCESS**, not queued, with [five-role HTML and receipt artifact 11760151621](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38277127996/artifacts/11760151621) and all job steps success, including sole-renderer build, scoped unit tests and H3/Chromium gates. This is evidence for earlier Task 02's new HEAD SYNTHESIZE regression, NOT a JUSTIFY run or a QRT acceptance. No new product tests/CI/build executed for D3-S2-03; independent local mathematical arithmetic checks were performed.

| Named D3 QRT cell | Technical authored TEST status | Independent academic/Owner acceptance |
| --- | --- | --- |
| QRT-MODEL-D3 | Previously rendered five roles | NOT_ACCEPTED |
| QRT-RETRIEVE-D3 | Previously rendered five roles | NOT_ACCEPTED |
| QRT-EXPLAIN-D3 | Previously rendered five roles | NOT_ACCEPTED |
| QRT-APPLY-D3 | Previously rendered five roles | NOT_ACCEPTED |
| QRT-REPRESENT-D3 | Previously rendered five roles | NOT_ACCEPTED |
| QRT-SYNTHESIZE-D3 | Previously rendered five roles; metadata corrected #193@5510724, current-head scoped CI SUCCESS | NOT_ACCEPTED |
| **QRT-JUSTIFY-D3** | **LAST OPEN — mathematical gate PASS/academic D3 pending; five-role authored package UNSTARTED** | **NOT_ACCEPTED** |

The **technical authored count remains 6/7** and **D3 academic/Owner acceptance remains 0/7** (central 0/28). This read-only gate does not change technical cell count, authorize new blueprint, or claim learner adoption. **Task D3-S2-03 DONE as independent mathematical/gate analysis; qualified human academic validation and conditional D3-S2-04 five-role delivery remain next.**
