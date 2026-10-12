# QRT-JUSTIFY-D4 pilot — independent-review handover (UNACCEPTED)
2026-10-12 | chat=new | Grade9v3.5 draft PR #194 | head=e39db6a8607bf64b09274d38bb222ed90f22459a
Issue: https://github.com/reallakshman19/Grade9v3.5/issues/182
Artifact: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38239770116/artifacts/11742381985
Hosted CI: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38239770116 -> SUCCESS
Renderer receipt: render_core/2, reference-depth gaps=0, six files including index, digest=c62088b265def4b7, semantic_digest=597494285f43d25c.
Upstream code ancestry: PR #190@67c34dababb0da0ef7d5f4a532bfcf3119754961 (UNMERGED H3 AFTER_ATTEMPT); D4 source is a draft stacked on that exact snapshot. No changes to renderer, registry, frozen golden, central QRT monitor or other agent's paths.

## X/Y/Z/W and pedagogical proof contract
X: Characterize all integer n for which 24 divides n^2-1.
Y: Use n^2-1=(n-1)(n+1) and independent requirements 8 and 3.
Z: Necessity: even n makes expression odd and 3|n makes expression 2 mod3. Sufficiency: odd n gives neighbors even and one divisible by4 (factor8); 3 not dividing n ensures a neighboring factor3; gcd(8,3)=1.
Protected learner W: Explicitly decide and warrant BOTH directions and exact allowed classes modulo6 {1,5}, not from finite examples. Core1A supplies constituent concepts and separately assesses m(m+2) mod8; its final W is not printed pre-attempt in Core2A.
Wrong idea: all odd n qualify. Diagnose at n=3 (odd but expression 8). Replace with iff odd and not divisible by3. Re-test n=15 (fails), n=17 (passes).
Core2B changed demand: 48 needs factor16 not8; 16 divides n^2-1 iff n mod8 in {1,7}; combined with 3 exclusion gives n mod24 {1,7,17,23}. n=5 is the old-rule false positive. This is a different task, not an unaltered copy.
Authorship/right: source origin AUTHORED, all SVGs/prose own TEST drafts, no official SOF exam Q/PDF/KEY/logo, no authentic Core2 source claim, academic/curriculum classification subject to independent reviewer.

## Five actual sole-renderer HTML files, pinned SHA256
Download artifact https://github.com/reallakshman19/Grade9v3.5/actions/runs/38239770116/artifacts/11742381985, open each named HTML in a browser. SHA256 is from hosted receipt of run 38239770116. The frozen fixture lock is golden/units/G-IMO-G9-FIVE-CORE-20261012/snapshot-lock.json @ Git blob 888678554c41257e6d96c802f0009983ccbb5328 and original_digest ad02fef42f0d505a.
role | generated HTML filename | frozen golden SHA256 | new rendered SHA256 | role/slot semantic correspondence
CORE1 | core1.html | f76831e21905d9ac712149a8a0983ca521d483bd865b50d68fb032b391bddd3e | dc1f46315f16eef95f3d645004acfebb9a5b86f94a9e304774ed28bd67a6e58b | identity, orientation
CORE1A | core1a.html | c58a4aec2b4318eaad83ffac236b6287ff2cdcb4532aa83aa4d3cd44b2d1b004 | 2b0a7d18ad355447955cca33dea90ce52d4fcbe9bc37faf89ed39fe6005db35d | identity, construction, repair_closure x2
CORE1B | core1b.html | 3c91ac07738cb7add05a275c957e728b762f883da8a60149d0189ac8a422c562 | 452e4f8c1e88a3e2ab08e296dd8008baaeb50e80d4d500bbc1b84aa8a83b136f | identity, attempt, reconstruction
CORE2A | core2a.html | e19a11206d8e6ca12b1f396e67e5f6497bcae841ec7470c75825836eeca47777 | 5316d5d018fc066770c45bddea3d03349cf1bffb28803f8302b7dd88ddeca724 | identity, attempt, reasoning, support
CORE2B | core2b.html | 91b6d5f2e77dcf051396eee7da88bd93f51a0a1bdc98cba6156da71e37453b39 | 4659b9d512bbdc1f398ff20a002bc46dba9fb90ffbf222ea6fa5b74440ea1426 | identity, attempt, post_attempt
Compared against exact frozen five-role markup without copying old mathematical content: tests/test_imo182_qrt_d4_justify.py asserts each role's full blueprint-slot sequence matches frozen golden and exact registered blueprint ref remains. Different HTML bytes expected, especially post-#190 H3. Frozen original is NOT changed. No claimed owner-designated successor golden; Owner decision D-182-3 OPEN.

## Twelve reviewer questions with author-observed evidence — no independent ratings
H1: Is the protected learner decision genuinely independent? Core2A initial screenshot shows the arbitrary integer iff question and written-answer field without full proof; reviewer should check Core1A conceptual rehearsal has not made W trivial.
H2: Can the learner request safe guidance before solution? Core2A visible H1 and next-hint control; authored H2 asks for factorization, not the completed iff condition; test inspects inert hints.
H3: Does the first answer-revealing rung wait for an attempt? Chromium browser run tests H3 inert at first load then after a nonblank committed written attempt H3 materializes; compare browser/core2a.png and browser/core2a-after-attempt.png in artifact.
S1: Does meaning originate in visible representations instead of a wall of prose? Four original named, accessible SVGs, each with registered metadata + MathML difference-of-squares; Core1A screen shows three navigable visual stages.
S2: Are the five learner tasks semantically differentiated? Core1 orientation, Core1A constituent construction/exit, Core1B odd-only misconception/reconstruction + boundary, Core2A iff practice, Core2B changed divisor48.
S3: Is the changed demand genuinely new and not a larger computation? Core2B needs modulo8 factor16 vs factor8 and falsifies the old rule at n=5; reviewer should judge D4 transfer novelty.
P1: Is necessity and sufficiency mathematically correct? 20,001 integer inputs (range -10000..10000) confirm exact criterion 24|(n^2-1) iff n mod6 in{1,5}; symbolic proof explicit in recorded answer.
P2: Is the failure signal diagnostic? n=3 falsifies odd-only; even n and n divisible3 are distinct universal obstructions; not mislabelled arithmetic slips.
P3: Is the independent check genuinely separate? Fresh Core1A 8|m(m+2) iff m even plus negative m=-4; Core2B changed condition 48 and mod24 exact residue exhaustiveness checked over same range.
M1: Is provenance/source rights clear? package.resources origin AUTHORED; manifest subject TEST, QRT accepted=false, authentic exam input/rights absent; reviewer may request grade-level suitability verification.
M2: Does registered renderer match frozen role anatomy? CI verifies zero reference-depth gaps, all five registered refs and matching slot sequences; no second composer; old golden unchanged.
M3: Is learner layout/accessibility robust? Headless Chromium 1280x900 five screenshots, SVG aria-label/title/desc and stage controls; reviewer should separately inspect tablet/narrow width, A4, screen reader and real classroom use (not yet claimed).

Academic reviewer: NOT ASSIGNED / verdict: BLANK
Owner QRT acceptance: BLANK; accepted=0/28
Owner D-182-3 successor golden: OPEN; original frozen fixture remains exact
Lead/qualified reviewer next action: examine artifact pages and screenshots, issue dated independent H1–M3 comments and curriculum-band / rights decision. No worker authority to self-accept.

## Worker implementation evidence
Outcome: O1 + O2 (authored TEST pilot; no academic admission)
For the user: Five registered blueprint-role TEST learner pages with distinct construction, misconception repair, supported proof and stronger-divisor transfer; not released.
Proof: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38239770116 SUCCESS @ e39db6a8607bf64b09274d38bb222ed90f22459a; real HTML/screenshots https://github.com/reallakshman19/Grade9v3.5/actions/runs/38239770116/artifacts/11742381985; render-receipt gaps=0.
Task: AGENT-D4/QRT-JUSTIFY-D4
Goal (issue AC): Original Grade9-appropriate necessary-and-sufficient D4 question; construct X/Y/Z/W, five sole-renderer Core roles, golden-semantic comparison, authored source rights, H3 gate, scoped tests and reviewer-ready packet.
Status: DONE
Met: yes
Done: Wholly AUTHORED iff criterion 24|(n^2-1) iff n mod6 in {1,5}; transfer 48|(n^2-1) iff n mod24 in {1,7,17,23}; independent Core1A exit 8|m(m+2) iff m even; five SVG role figures with stage markers and no preattempt protected answer.
Code: reallakshman19/Grade9v3.5 agent/imo182-qrt-d4-justify-pilot @ e39db6a8607bf64b09274d38bb222ed90f22459a | DRAFT PR #194 stacked on unmerged D-182-2-H3 PR #190 @ 67c34dababb0da0ef7d5f4a532bfcf3119754961
Tests: python -m unittest tests.test_imo182_qrt_d4_justify -v -> PASS (3 tests; 20,001-input oracle for 3 equivalences; five-role slot/golden contract); python tests/imo182_qrt_d4_justify_browser.py -> PASS (5 real Chromium pages, initial H3 protected, H3 unlocked after nonblank committed answer).
CI: 38239770116 -> SUCCESS; artifact 11742381985 includes actual HTML/receipt/6 screenshots (including Core2A after attempt).
Golden: G-IMO-G9-FIVE-CORE-20261012 original_digest=ad02fef42f0d505a; original five sha256 compared against five new html sha256 in Tab7 handover; five blueprint role/slot sequences MATCH, deliberately different content/bytes, frozen golden unchanged, new successor golden D-182-3 still OPEN.
Evidence: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38239770116/artifacts/11742381985 | https://github.com/reallakshman19/Grade9v3.5/pull/194 | coordination/Session_Oct09/Tab7_imo_qrt_d4/handovers/QRT-JUSTIFY-D4.md
AC: rendered Tab7 0/7 -> 1/7 (worker implementation); accepted QRT 0/28 -> 0/28 (qualified reviewer and Owner unsigned).
Claim: HOSTED_CI
Blocker: NONE
QRT: proposal only, source AUTHORED TEST, independent qualified reviewer verdict blank, Owner acceptance blank; no admission/merge/release.
Next: AGENT-D4/QRT-EXPLAIN-D4; qualified reviewer may independently assess the recorded H1–M3 packet; D-182-3 Owner successor golden remains OPEN.
