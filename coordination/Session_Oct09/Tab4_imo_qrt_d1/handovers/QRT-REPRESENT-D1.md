# QRT-REPRESENT-D1 — reviewer packet, authored TEST only
Date 2026-10-12 | chat=new | issue Grade9v3.5#182 | AIM v3.1.0 / label_sha 2ff9246.
State: GOLDEN_TECHNIQUE_PASS (worker's *technical* comparison). Qualified academic review NOT_RUN; Owner acceptance NOT_GIVEN; canonical accepted 0/28. No source rights, merge, release or public learner route.
Source PR: https://github.com/reallakshman19/Grade9v3.5/pull/192; branch agent/imo182-qrt-d1-represent @ 630900aaeb379ee38c0f2a8760ffe83581f5ad86. This PR is a DRAFT deliberately stacked on upstream PR190 @ 67c34dababb0da0ef7d5f4a532bfcf3119754961. The H3 fix is not assumed merged to main.
Actual five-role GitHub CI: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38237708811 -> dedicated run 38237708811 SUCCESS; job 114772381671 SUCCESS, artifact 11741437776 (imo182-qrt-d1-represent-five-core-html). The artifact contains index.html and five actual renderer-generated role HTML files, d1-evidence.json and render-receipt.json. Renderer: Shared/tools/render_core.py build --manifest TEST/products/imo182-qrt-d1-represent.manifest.json --out build/imo182-qrt/d1/represent --draft --reference. Zero REFERENCE depth gaps, CORE2 source selection empty. Explicit QRT and renderer SHA provenance in source ref.
Five actual role HTML exact SHA256:
core1.html | a477bf1132ee4704bbc617c983e08cee77472ceec6dacdce71ada4577fb03931
core1a.html | 298d277ef623b89267f602187a7775fe4482e1a1f1fc82805c965a12e99bc889
core1b.html | eeca2fc7ac620bf66dd620eef0b336996ebcac4f06a6cbc86b9ebc05ff8074dd
core2a.html | a8c0acfef176967a44777a57634076a8157b016c78d26a4a1d3207dc521de300
core2b.html | 087b2ec74ebfc568e618e9e2b12daca42ffc56d3afc30f2de596f41abfd0c9cf
index.html | 671eff41ee84f795a0b59d9cfd6c6fd1ab802c4d47fabdf44fc0251d1cb7cb06
Owner frozen baseline: G-IMO-G9-FIVE-CORE-20261012, source commit f87d2f627e3f05476d39fb04d7f26e453661dc68; all five snapshot-lock SHA256 checks PASS UNCHANGED. Do NOT claim different question bytes must match frozen bytes or edit the frozen golden. Successor candidate golden designation Owner-only.

Learner item: "A surveyor starts at the origin of an east-positive/north-positive square grid. She records a displacement of 4 grid units EAST and 2 grid units SOUTH. Write the displacement as a signed ordered pair (x,y), with horizontal first. Explain the sign of its second entry." Correct (4,-2), from signed axes. Distinct Core1A sample 3 west / 1 north -> (-3,+1); distinct Core2B inverse pair (-3,+5) -> 3 west / 5 north. TEST authored from scratch, not official sample Q004, which remains research only.
X: a meaning-preserving translation between words and an ordered pair.
Y: supplied convention +x east, +y north; horizontal-first/vertical-second.
Z: map magnitudes and signs then reverse-translate.
W: learner independently fixes sign and ordered coordinates for the surveyor's displacement (4,-2).
Wrong idea: positive travelled distance means positive coordinate even when travelling south.
M1 diagnostic: learner disputes classmate (-2,+3) for 2 west / 3 south.
M2 difference between conception and slip: reverse-translate +3 as 3 NORTH and ask what south requires; changed givens confirm.
M3 replacement: signs encode direction relative to axes, not just positive magnitudes; independent east2/south3 boundary -> (+2,-3).
Independent mathematical verifier: 289 signed-coordinate inverse round-trips on [-8,8]^2 plus 3 specific asserted author boundaries PASS hosted.

Technique comparison of five corresponding frozen Owner golden roles and the actual novel D1 content (matched blueprint identity + ordered slots):
CORE1 | BP-CORE1-ORIENTATION@1.1.0 | frozen/new slots [identity,orientation], orientation and axis meaning present | PASS worker technical
CORE1A | BP-CORE1A-CONSTRUCTION@1.8.0 | frozen/new slots [identity,construction,repair_closure,repair_closure], 3-stage progressive teaching with different worked example and independently gated exit | PASS worker technical
CORE1B | BP-CORE1B-RECONSTRUCTION@1.1.0 | frozen/new slots [identity,attempt,reconstruction], misconception prediction, separate attempt/reconstruction and fresh boundary attempt | PASS worker technical
CORE2A | BP-CORE2A-SUPPORTED-APPLICATION@1.1.0 | frozen/new slots [identity,attempt,reasoning,support], H1/H2 pre-attempt, H3 AFTER_ATTEMPT, full solution gated independently; old frozen H3 is different by approved #182 Owner timing | PASS worker technical, Owner successor-golden decision pending
CORE2B | BP-CORE2B-TRANSFER@1.1.0 | frozen/new slots [identity,attempt,post_attempt], *inverse representation* change from original forward translation, independent commitment & changed solution | PASS worker technical

Twelve owner-review H/S/P/M semantic asks — worker preliminary statuses, *not* qualified assessor verdict:
H1 PASS: orient on x/y placement, no pair answer leaked.
H2 PASS: bridge directions to fixed positive-axis convention, not target signs.
H3 PASS: post-attempt after nonblank commitment; the full pair answer remains separately gated.
S1 PASS: initial Core1A figure displays the axes and origin, not the surveyor's target pair.
S2 PASS: distinct west/north worked correspondence used, not 4 east/2 south.
S3 PASS: reverse-translation of a distinct sample; target mapping still learner-owned.
P1 PASS: given-only Core2A SVG and accessible desc/title/aria; H1/H2 not disclosing target pair, H3 gated.
P2 PASS: Core2A concept route core1a.html#CU-TEST-IMO182-D1-AXES links to an extant Core1A DOM fragment; link tested in actual generated output.
P3 PASS (authored maths + renderer checks): post-attempt why-valid reasoning and 289 independent inverse checks.
M1 PASS: concrete wrong-sign claim for west/south reproduced.
M2 PASS (worker diagnostic, learner empirical study PENDING): +3 is explicitly interpreted as north; changed-givens test distinguishes sign rule from transcription slip, not proven by learner outcomes.
M3 PASS: changed east/south route boundary and independent reconstruction required; learned outcome unverified.
All PASS here are *worker technical test judgments*, neither academic validation nor Owner acceptance. No qualified assessment of grade D1 difficulty, cross-band distinction, or real learner evidence yet.

Browser QA: local Chromium/Playwright on the exact downloaded hosted HTML bytes using page.set_content (file:// and localhost navigation disallowed by environment); 27/27 assertions PASS, 0 JS errors in 4 tested roles. Core2A initial/after H2 H3 hidden, blank attempt inert, nonblank attempt permits explicit H3 and independent full answer; Core1A stages/gated exit; Core1B reconstruction and separately gated boundary; Core2B initial inverse task/reveal after valid attempt. Screen captures reviewed locally (not independently).
CI wider scope: dedicated 38237708811 SUCCESS. Earlier same-PR commit guardrails run 38237704419 FAILURE; current-head guardrails 38237708812 and canonical-assurance 38237708740 still in progress at last check. Do NOT claim PR-wide green. Other current-head learner-platform, SOF research integrity, and relay checks succeeded. Broad checks/integration require lead diagnosis, not a fake all-green.
Artifact output includes PDF header control where publication PDF is absent; A4 publication is parked, not claimed. No public deployment.
Source-rights status: all three question records origin AUTHORED; official organizer Q004 is research-only; no CORE2 or KEY.
Blueprint change O3: NO_CHANGE; existing registered roles express the target work.
Academic review identity/verdict/date: [blank] / [blank] / [blank].
Owner QRT acceptance ID/date: [blank] / [blank]; numerator remains 0/28.
Open decision: successor Owner golden designation for changed H3 is outside this cell and remains OPEN upstream; no redundant Owner question raised by agent.
Next: qualified reviewer independently judge REPRESENT-D1 band/pedagogy + Owner accept/revise; agent moves to D1-RET-02 on a separate original TEST task without treating human review wait as blocking.
CI STATUS FOLLOW-UP (append-only): 2026-10-12 exact-head broader guardrails run 38237708812 reached FAILURE (job 114772382111), including raw-intake independent fixture mismatch and external evidence snapshot connection reset. Dedicated D1 workflow 38237708811 remains SUCCESS. PR-wide green NOT achieved; technical lead owns cross-repository/baseline integration diagnosis, not the D1 authored package. Issue TASK EVIDENCE was posted at https://github.com/reallakshman19/Grade9v3.5/issues/182#issuecomment-6122778125.
