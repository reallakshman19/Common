# QRT-EXPLAIN-D4 — worker-finished cell review packet (NOT chat handover)
2026-10-12 | chat=6accb5b3 | issue=Grade9v3.5#182 | aim=v3.1.0 label_sha=2ff9246
PR: https://github.com/reallakshman19/Grade9v3.5/pull/195 (DRAFT), exact code head 6c00fae5c150cd580ab04c680414fba0a0c776e8
Stacked dependency: unmerged #190@67c34dababb0da0ef7d5f4a532bfcf3119754961 Owner-approved Core2A H3 AFTER_ATTEMPT.
Hosted CI run: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38242619673 -> SUCCESS.
Five generated HTML + 6 browser PNG + receipt: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38242619673/artifacts/11743552219.
Sole renderer: Shared/tools/render_core.py render_core/2; digest=4288fa8c817df8fe; semantic_digest=a25c7f4881d523c0; six HTML including index; held_to=REFERENCE; zero gaps.
Unchanged frozen benchmark: golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshot-lock.json original_digest=ad02fef42f0d505a; original_semantic_digest=9497e294361663f2; frozen HTML byte hashes preserved.
Source: TEST/imo-research/qrt-d4/explain-d4.package.json. Manifest: TEST/products/imo182-qrt-d4-explain.manifest.json.
Rights and status: all questions/SVGs authored TEST; official organizer stems/images/KEY/custody NOT represented; curriculum band and academic correctness await independent reviewer. Accepted=0/28. No merge/release.

## Actual five role HTML and benchmark (SHA256)
Use the exact hosted artifact, open the actual HTML. The first digest is immutable frozen golden; second is new exact-head output. The standalone source question intentionally differs, so byte-equality is NOT the comparison; tests assert blueprint refs and exact role-slot sequences from frozen golden for all five.
role | file | frozen owner SHA256 | authored new SHA256 | registered ref and slot sequence
CORE1 | core1.html | f76831e21905d9ac712149a8a0983ca521d483bd865b50d68fb032b391bddd3e | 20c877dc26d991157b8d943cc36ad6770e59da16753a6c0a6e56574a6e30b5c8 | BP-CORE1-ORIENTATION@1.1.0 | identity,orientation
CORE1A | core1a.html | c58a4aec2b4318eaad83ffac236b6287ff2cdcb4532aa83aa4d3cd44b2d1b004 | a37d7412d81d49df87e4867af20c5045361dd58adf17a20916ca0094e9876219 | BP-CORE1A-CONSTRUCTION@1.8.0 | identity,construction,repair_closure x2
CORE1B | core1b.html | 3c91ac07738cb7add05a275c957e728b762f883da8a60149d0189ac8a422c562 | e6523ad238cfed3a354417ef9b29febab7d7ba01f52770bdb853a0d5befcc964 | BP-CORE1B-RECONSTRUCTION@1.1.0 | identity,attempt,reconstruction
CORE2A | core2a.html | e19a11206d8e6ca12b1f396e67e5f6497bcae841ec7470c75825836eeca47777 | 5a4cd06d9d91ec69272653cb7977023b9a2880e129533caaeeea7f9be0693587 | BP-CORE2A-SUPPORTED-APPLICATION@1.1.0 | identity,attempt,reasoning,support
CORE2B | core2b.html | 91b6d5f2e77dcf051396eee7da88bd93f51a0a1bdc98cba6156da71e37453b39 | e2f6e9c2dadaf7bb5742652ccd9358ef91408e76562d3a34a26fa8234f57b337 | BP-CORE2B-TRANSFER@1.1.0 | identity,attempt,post_attempt
Index (non-role) SHA256 a46905d730c77174ea43a7c01a07634d1b0dceed11f4928f35d7ce5b95f7703e.
Core2A H3 retains previous OWNER choice AFTER_ATTEMPT. Prior frozen Core2A predates that fix; unchanged old HTML not a legitimate target for byte-match. Owner decision D-182-3 successor golden still OPEN.

## Pedagogical contract (X/Y/Z/W)
X: An initial L-digit positive multiple of11, with original nonzero first digit a, has its first digit moved to end. Explain WHY the modulo11 invariant survives at even L but fails at odd L. Numeric checks alone insufficient.
Y: Prelearned 10≡−1 (mod11) and fixed-width positions: N=a×10^(L−1)+B, R=10B+a. Core1A stages show neutral sign change, two-digit anchor and unclassified general form; its independent exit uses three-digit alternating digit sum and 209.
Z: Since N≡a(−1)^(L−1)+B and R≡a−B, even L gives R≡−N, while odd L with 11|N gives B≡−a and R≡2a. For 1≤a≤9, 2a nonzero mod11. This explains the causal difference.
W: Learner-owned written explanation of why original length parity changes the leading digit's positional sign, causing an invariant or an obstruction; not recognition of a memory tag.
Wrong route: unchanged digit sum or successful even-length samples prove all lengths. Diagnostic: 121→211 fails; 1210→2101 works. Core1B separate reconstruction/boundary: 110→101 fails at odd L; 1232→2321 succeeds at even L. Leading zeros do not reset original L.
Changed transfer Core2B: move TWO leading digits. N=A10^(L−2)+C, R=100C+A, with A a two-digit first block. At even L residues agree; at odd L with 11|N, R≡2A, so the NEW surviving odd-length case is 11|A. Compare 110→011 success (A=11) and 121→112 failure (A=12). Distinct task, not the single-digit rule repeated.
Adjacent-band difference: the learner must explain why a hidden original-length assumption reverses an apparent invariant and derive a new prefix-sensitive changed-operation exception. This is not D3 with bigger numbers.

## Twelve independent reviewer prompts with observed worker evidence, not assigned ratings
H1: Does Core2A demand a causal explanation rather than a bare yes/no proof? The stem explicitly asks WHY, the authored answer route has protected MOVE-CAUSE and two original lengths; review the live learner task.
H2: Are H1/H2 preattempt requests conceptual? H1 defines fixed original width; H2 asks what multiplying by ten does modulo11 without identifying correct length classes.
H3: Is the protected comparison only released after a nonblank written attempt? Chromium asserts blank commit does not set data-attempted, initial H3 stays inert, after committed text H3 materializes. Screens browser/core2a.png and browser/core2a-after-attempt.png.
S1: Is construction based on actual mathematical structure rather than prose? Core1A uses registered 3-stage accessible SVG of 10≡−1, two-digit swap, and symbolic rotation with stage controls; reviewer should assess its explanatory affordance.
S2: Are all five tasks distinct? Core1 orientation, Core1A sign and short anchor with independent exit, Core1B false rule and independent repair boundary, Core2A protected causal explanation, Core2B two-digit operation exception.
S3: Does Core2B genuinely change the transfer dimension? Odd length no longer necessarily fails; two-digit A may be a multiple11, and the learner must explain precisely why.
P1: Is underlying modulo11 mechanism valid? 10≡−1, leading original digit in1..9, even L R≡−N; odd L R≡2a. Hosted oracle verifies all original multiples11 at L2..4 and samples L5..6, totaling 2,727.
P2: Does wrong route diagnose an invalid generalization, not a slip? Compare 121 and1210 without saying changed digit sums; boundary 110 and1232 tests the repaired length rule.
P3: Is independent check separate? Core1A exit: for three digits a-b+c may equal 0 or11 (209→sum11), validated against all 900 three-digit inputs. Core2B is an independent two-digit prefix exception checked by same arithmetic oracle.
M1: Provenance/rights: resources origin AUTHORED; original SVG and text only; subject TEST; authentic organizer/print/KEY rights not asserted; curriculum/academic reviewer pending.
M2: Golden technique: same 5 blueprint refs and slot order sequences as frozen Owner fixture, zero reference-depth gaps; source mathematical text deliberately differs and frozen golden has not been changed.
M3: Layout/accessibility: hosted Chromium sees all 5 1280×900 roles, screenshots and original SVG aria-label/title/desc/stage attributes. Tablet/A4 screen-reader/human comprehension require independent verification; not claimed here.

Independent qualified reviewer: NOT ASSIGNED, verdict BLANK.
Owner QRT decision: BLANK. Owner D-182-3 successor golden: OPEN.
No author self-acceptance, merge, source admission or release.
Next worker task: AGENT-D4/QRT-APPLY-D4.

## Exact TASK EVIDENCE (also appended to Tab7 EVIDENCE.log and issue #182)
Outcome: O1 + O2 (authored TEST EXPLAIN-D4; no academic admission)
For the user: Five distinct learner-visible registered blueprint-role TEST pages explain decimal digit-rotation invariants and a two-digit-prefix transfer exception; not released.
Proof: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38242619673 SUCCESS at 6c00fae5c150cd580ab04c680414fba0a0c776e8; HTML and six Chromium screenshots https://github.com/reallakshman19/Grade9v3.5/actions/runs/38242619673/artifacts/11743552219; registered renderer receipt reference-depth gaps=0.
Task: AGENT-D4/QRT-EXPLAIN-D4
Goal (issue AC): A legitimate authored D4 EXPLAIN question with X/Y/Z/W, misconception and independent check, five roles from the sole renderer, frozen five-role golden technique benchmark, H3-after-committed-attempt QA, scoped source-rights/CI and independent-review packet.
Status: DONE
Met: yes (worker implementation only; independent academic/Owner approvals pending)
Done: Original N=a10^(L-1)+B and R=10B+a modulo11 causal explanation: for initial 11|N, one-digit left rotation preserves iff original L even; for odd L residue is 2a and cannot vanish for a=1..9. Core2B independently changes to two-digit rotation N=A10^(L-2)+C, R=100C+A, preserving at even L and at odd L precisely when 11|A. Core1B falsifies all-length rule via 121->211, repairs it, then tests 110 and1232; Core1A independent three-digit alternating-sum exit at 209. All original AUTHORED TEST.
Code: reallakshman19/Grade9v3.5 agent/imo182-qrt-d4-explain-pilot @ 6c00fae5c150cd580ab04c680414fba0a0c776e8 | DRAFT PR #195 stacked on unmerged H3 dependency PR #190 @ 67c34dababb0da0ef7d5f4a532bfcf3119754961
Tests: python -m unittest tests.test_imo182_qrt_d4_explain -v -> PASS (3 tests; arithmetic oracle 2727 qualifying numbers L=2..6, plus 900 three-digit independent exit candidates, schema, five golden slots, H3 release contract); python tests/imo182_qrt_d4_explain_browser.py -> PASS (five actual Chromium pages, blank attempt rejected, Core1B separate boundary gate, H3 only after nonblank committed attempt, six screenshots).
CI: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38242619673 -> SUCCESS; artifact 11743552219 actual HTML/six screenshots/zero-gap receipt.
Golden: G-IMO-G9-FIVE-CORE-20261012 original_digest=ad02fef42f0d505a preserved, same five registered blueprint refs/slot sequences as frozen snapshot; new source has intentionally different bytes, compare frozen/new sha256 per role in Tab7 cell handover; Owner successor golden D-182-3 OPEN.
Evidence: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38242619673/artifacts/11743552219 | https://github.com/reallakshman19/Grade9v3.5/pull/195 | https://github.com/reallakshman19/Common/blob/main/coordination/Session_Oct09/Tab7_imo_qrt_d4/handovers/QRT-EXPLAIN-D4.md
AC: Tab7 rendered worker implementations 1/7 -> 2/7; academically Owner-accepted QRT 0/28 -> 0/28; no qualified reviewer or Owner signature.
Claim: HOSTED_CI
Blocker: NONE
QRT: AUTHORED TEST candidate only; qualified reviewer verdict BLANK; Owner acceptance BLANK; frozen golden unchanged; no merge/release.
Next: AGENT-D4/QRT-APPLY-D4; independent reviewer to examine EXPLAIN-D4 H1-H3/S1-S3/P1-P3/M1-M3; Owner successor golden D-182-3 remains open.
