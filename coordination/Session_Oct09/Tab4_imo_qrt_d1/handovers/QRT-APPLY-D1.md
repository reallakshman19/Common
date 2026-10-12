# QRT-APPLY-D1 — per-cell academic and technical review packet
2026-10-12 | chat=6accb51c | issue #182 | AIM v3.1.0 / 2ff9246.
This is an original AUTHORED TEST candidate only; not official examination material, no Core2 rights, no merge, no release, no Owner acceptance. Accepted canonical cells 0/28.
X: apply the supplied area formula to a measured rectangle, distinguish area from adding side lengths.
Y: rectangular mat measures length 7 cm and width 4 cm, with A=length×width explicitly supplied.
Z: substitute into given A=l×w, multiply and report squared units.
W: independently write A=7×4=28 cm² and justify unit-square tile counting. Formula application is protected, not preprinted on the given-only SVG.
Core1A distinct worked 3×5 rectangle, independent 8×2 exit.
Core1B wrong route: classmate adds 5+3 and calls area 8 cm², instead of 15; reconstruction explains count of rectangular tiles; changed 4×4 square boundary distinguishes squared area units from length units.
Core2B changed inverse: given A=24 cm² and width 4 cm, find length 6 cm by dividing; then reverse check 6×4=24.
D1 provisional: model/formula and dimensions provided, one multiplication and unit labeling; D2 would require identifying an unstated rule, composite-shape decomposition, or extended relation selection.
Core roles via registered sole renderer only, no handwritten learner HTML:
CORE1 BP-CORE1-ORIENTATION@1.1.0 orientation.
CORE1A BP-CORE1A-CONSTRUCTION@1.8.0 distinct 3×5 construction/exit.
CORE1B BP-CORE1B-RECONSTRUCTION@1.1.0 real misconception, repair and separate boundary attempt.
CORE2A BP-CORE2A-SUPPORTED-APPLICATION@1.1.0 protected 7×4 substitution, H1/H2 concept, H3 AFTER_ATTEMPT.
CORE2B BP-CORE2B-TRANSFER@1.1.0 independent inverse 24÷4 transfer.
Worker golden-technique asks: H1/H2/H3, S1/S2/S3, P1/P2/P3, M1/M2/M3; do not mark PASS without inspecting actual HTML.
Owner frozen G-IMO-G9-FIVE-CORE-20261012 exact SHA locks must remain immutable, compare registered blueprint names and role-slot anatomy, not newly authored content bytes.
Academic reviewer identity/verdict/date BLANK; Owner decision ID/date BLANK. 0/28 accepted.
Initial exact-head CI run and generated SHA/browser follow-up are pending; append outcomes only upon verification.
This path is a cell review artifact, NOT a successor-chat handover; LOG handover=no.

TECHNICAL COMPLETION RECEIPT | 2026-10-12 | chat=6accb51c
Source exact commit Grade9v3.5 PR#192@771f808b5000ddef11d74bde45835eee0905cdc4; branch agent/imo182-qrt-d1-represent, stacked on PR#190. No shared tool code rewritten and no merge.
Hosted sole renderer: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38253294826 -> SUCCESS; job 114824789972 SUCCESS; artifact 11749865966 "imo182-qrt-d1-apply-five-core-html".
CLI: python Shared/tools/render_core.py build --manifest TEST/products/imo182-qrt-d1-apply.manifest.json --out build/imo182-qrt/d1/apply --draft --reference -> PASS, six HTML incl index, ZERO reference-depth gaps.
Schema/frozen golden/role/H3 tests: python -m unittest tests.test_imo182_qrt_d1_apply -v -> 6/6 PASS; arithmetic python TEST/imo-research/qrt-d1/verify_apply.py -> 625 area/inverse roundtrips + 6 authored boundary fixtures PASS.
Exactly five generated HTML SHA256, each confirmed byte-for-byte against d1-apply-evidence.json in artifact:
core1.html | 0ac978f6b3aab9c7e515f004358ab2c30afe61e9e2d5507eab2d7989b959ed26
core1a.html | 2cb0a241098b4ed6051e945ef32209526f2947fd699a3d3fb47c13afadf8da45
core1b.html | fdc8face9582eb44a5ad3624a0a7c07d75f61b16a74c0907aa1c92a771dd4b86
core2a.html | 834975b6b6d5d06d576e129852261a8197fecb3ba48249129868103bc0ac5440
core2b.html | 0499a1a28f23a4f9c21549cdba7cf5166e51582b54f7bd3363596facf40269e4
Worker technique benchmark against Owner frozen G-IMO-G9-FIVE-CORE-20261012, snapshot SHA locks 5/5 PASS, source original golden untouched:
CORE1 BP-CORE1-ORIENTATION@1.1.0 slots identity,orientation -> SAME; teaches area as unit-square count.
CORE1A BP-CORE1A-CONSTRUCTION@1.8.0 slots identity,construction,repair_closure,repair_closure -> SAME; staged 3x5 example, independently gated 8x2 exit.
CORE1B BP-CORE1B-RECONSTRUCTION@1.1.0 slots identity,attempt,reconstruction -> SAME; repairs 5+3 addition misconception, independent 4x4 unit boundary.
CORE2A BP-CORE2A-SUPPORTED-APPLICATION@1.1.0 slots identity,attempt,reasoning,support -> SAME; target 7x4 protected W, H1/H2 preattempt, H3 AFTER_ATTEMPT and independent solution disclosure.
CORE2B BP-CORE2B-TRANSFER@1.1.0 slots identity,attempt,post_attempt -> SAME; changed given A=24cm2,width=4cm asks for missing length, gated 24/4 inverse.
Chromium Playwright of EXACT SHA-verified hosted HTML via local static page.set_content: 37/37 assertions PASS, 0 page JS errors; all five role refs and slot anatomy, initial/blank/committed H3 and full solution, Core1A stage+exit, Core1B reconstruction and separately gated boundary, Core2B inverse transfer gates verified. Browser script local: /mnt/data/imo182-qrt-d1-apply-browser-qa.py, not claimed hosted.
Worker H/S/P/M technical technique pass: H1/H2/H3 (no early 28, H3 after committed text); S1/S2/S3 (given-only mat, different 3x5 example, independent 8x2); P1/P2/P3 (safe SVG/title, Core1A learning link and answer after attempt with 4x7 tile check); M1/M2/M3 (actual 5+3=8 incorrect claim, count-by-tile repair, independent 4x4 unit boundary). This is NOT an independent academic efficacy study or acceptance.
Broad PR CI remains separate: at last check head 771f808b, guardrails 38253294957 and canonical assurance 38253294877 in progress; no PR-wide green claim. Earlier head bc4debf shared red guardrails raw-intake / evidence snapshot / search index was reproduced to technical lead in PR#192 comment 6123776631; NOT this author-owned APPLY cell. APPLY own scoped CI fully green.
Qualified academic review identity, verdict, date: [BLANK].
Owner acceptance decision ID, verdict, date: [BLANK]; canonical QRT acceptance remains 0/28.
O1 technical complete; O2 pending independent reviewer and Owner; O3 shared blueprint change NOT_NEEDED. This document is a cell artifact; chat successor handover=no.
