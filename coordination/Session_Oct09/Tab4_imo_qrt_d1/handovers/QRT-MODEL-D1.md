# QRT-MODEL-D1 — per-cell qualified review packet | AUTHORED TEST
Date: 2026-10-12 | chat=6accb51c | issue #182 | Owner AIM v3.1.0 label_sha 2ff9246.
Owner-accepted QRT: 0/28. No qualified academic review/verdict, official IMO source rights, production learner route, merge, release or Owner decision. This is a CELL ARTIFACT, not successor-chat handover.

Task D1-MOD-05 / QRT-MODEL-D1 / technical O1 complete on exact Grade9v3.5 PR#192 draft head 0949e4866b06aefd8b866fc3d2565f434e19bb93, stacked on unmerged draft H3 PR#190 @67c34dababb0da0ef7d5f4a532bfcf3119754961.
Authored package: TEST/imo-research/qrt-d1/model.v1.json
Role-only manifest: TEST/products/imo182-qrt-d1-model.manifest.json, core2=[].
Original SVG: model-groups-staged.v1.svg, model-core2a-trays.v1.svg, model-core1b-addition.v1.svg, model-core2b-inverse.v1.svg, each authored TEST and 28-unit accessible text, viewBox width 760; no assessed answer in initial asset alt/desc.
Dedicated independent oracle: TEST/imo-research/qrt-d1/verify_model.py.
Focused regression: tests/test_imo182_qrt_d1_model.py.
Sole renderer command: python Shared/tools/render_core.py build --manifest TEST/products/imo182-qrt-d1-model.manifest.json --out build/imo182-qrt/d1/model --draft --reference.

Semantic X/Y/Z/W:
X: choose and construct an equal-groups mathematical MODEL rather than sum unlike counts.
Y: SIX equally filled trays, FOUR seedlings in EACH tray.
Z: distinguish trays=count of groups versus seedlings/group=size, construct/draw six distinct groups of four, select multiplication 6×4 and check against repeated addition.
W: learner independently generates six groups of four, 6×4=24 seedlings, explains why 6+4=10 is not a total model. Stem, H1/H2 and initial asset DO NOT prefill group model or product.
Core1A distinct worked: three bead packets, five beads each -> 3 groups of 5, 15; separate Core1A exit five tins × two pencils -> ten.
Core1B diagnostic: classmate writes four shelves with two lanterns per shelf as 4+2=6; actual model 4×2=8, repaired by dot grouping. Independently changed boundary: two bags with ONE card each -> 2×1=2, not 2+1=3; learner commits separately.
Core2B changed inverse: given 24 seedlings total and four per tray, find UNKNOWN tray count by group model 24÷4=6 trays, reverse-check 6×4=24. This moves unknown from TOTAL to NUMBER OF GROUPS, distinct from forward question and separate worked example.
Proposed D1: word EACH fixes equal-group family, groups and sizes are supplied, learner owns one model-representation choice and result, no multistep unknown structure. Adjacent D2 would require choosing among multiple plausible models, unknown uneven group structure or justifying extra assumptions. Independent qualified academic verdict STILL PENDING; worker cannot assign acceptance.
O3: same Owner-registered five blueprints sufficient, no change requested to shared schema/renderer/registry.

Hosted run: https://github.com/reallakshman19/Grade9v3.5/actions/runs/38258022860 — SUCCESS; job 114841032291; artifact ID 11751335796 "imo182-qrt-d1-model-five-core-html".
Hosted sole renderer output: six HTML including index; zero REFERENCE depth gaps. Six dedicated Python unittests 6/6 PASS, JSON schema and answer/H3 policy PASS, frozen five golden locks PASS; independent 625 equal-group construction/inverse roundtrips plus six authored boundary fixtures PASS.
Actual HTML SHA256, exact byte-for-byte against artifact's d1-model-evidence.json:
core1.html ecdaa38d492a90d5ba242c6a96335ad026c0f7bb87f57a814afc8d1a796255e6
core1a.html 13f79ad487209c70edf65e30914708e051096bda16c5db26d27b2be3672a985c
core1b.html 56051d4ff15e99a8109da19622d22ee4c1ac59524bbdf572d324cf9904486b08
core2a.html f030388452c680c8eb8d32af9bc3544ca60b0249ef067375bb7515ed9b774656
core2b.html 23b267d2e0a337f69b6a166c21f60e481ca430b787d8a85e97c470fb5a8dafc6
Local Chromium Playwright on byte-identical downloaded hosted HTML: 37/37 PASS, zero JS errors. File /mnt/data/imo182-qrt-d1-model-browser-qa.py. Tested initial attempt/blank attempt, H3 AFTER_ATTEMPT, full-answer separate disclosure, registered staged 3×5, independent exit, Core1B reconstruction/boundary two separate commitments, and inverse Core2B review gating.

Owner immutable five-role golden G-IMO-G9-FIVE-CORE-20261012 snapshot-lock.json source unchanged and five SHA locks PASS. Worker benchmark of SAME registered blueprint refs and ordered slot anatomy:
CORE1 BP-CORE1-ORIENTATION@1.1.0 — identity, orientation — PASS; equal-group orientation and distinct semantic quantities.
CORE1A BP-CORE1A-CONSTRUCTION@1.8.0 — identity, construction, repair_closure, repair_closure — PASS; different model construction and independently gated exit.
CORE1B BP-CORE1B-RECONSTRUCTION@1.1.0 — identity, attempt, reconstruction — PASS; real wrong additive route, no copied worked proof, independently gated new boundary.
CORE2A BP-CORE2A-SUPPORTED-APPLICATION@1.1.0 — identity, attempt, reasoning, support — PASS; protected model-choice W, H1/H2 safe and H3 after written attempt.
CORE2B BP-CORE2B-TRANSFER@1.1.0 — identity, attempt, post_attempt — PASS; changed inverse model and independent response gate.
The novel content is intentionally not byte-equal to frozen golden; compare registered roles/slots/teaching moves, not novel narrative hashes.

Worker H/S/P/M (NOT qualified independent academic acceptance):
H1 PASS semantic role labeling no full 6×4 model; H2 PASS compare equal groups vs sum without selecting target total; H3 PASS AFTER_ATTEMPT.
S1 PASS target given-only cards; S2 PASS distinct three-by-five dot worked; S3 PASS independent five-by-two exit/two-by-one boundary.
P1 PASS figure alt/ARIA/H1/H2 withhold protected total and model; P2 PASS Core1A path to model family; P3 PASS gated postattempt reason and six repeated groups check.
M1 PASS false concrete 4+2 claim; M2 PASS classmate confuses groups and objects/group (not a slip); M3 PASS repaired product model and changed group-size-one boundary.
This is a worker technical benchmark, not causal learning-efficacy evidence.

CI responsibility: scoped MODEL source and 6/6 runner PASS. Older broad red PR#192@771f808, guardrails run 38253294957, was SHARED CI failure in raw intake, external evidence-snapshot and broad shared tooling/learner-state checks, NOT the D1 APPLY authored code. Technical-lead reproduction PR#192 comment 6125240175. Current PR#192@0949e48 guardrails run 38258022475 still in progress when recorded; no PR-wide green claim.
Independent academic reviewer identity/verdict/date: [BLANK].
Owner cell decision ID/status/date: [BLANK].
Accepted QRT numerator: 0/28. No agent self-acceptance.
Next authored cell: D1-SYN-06; do not merge or release. LOG chat handover=no.
