# DECISIONS — Tab1 V3.2 Generic Source Lifecycle (append-only)

Date: 2026-10-11 Asia/Muscat | Current chat: `6acae92b` | owner: Common #325 | production gate: #289 | programme: #5.
Read in conjunction with `RECON/2026-10-11/4-report.md` (retrospective source reconciliation) and `CHECKPOINTS.md`. These are engineering coordination decisions, **not** an Owner graph release, acceptance, path-grant or production writer authorization.

## D01 — Reuse the existing native DELP (AC1–AC8 remain HOLD)
- **Decision:** T01/T02/T03 under `relay/INTEGRATION/V32_325_GENERIC_SOURCE_20261011/` remain read-only / pure; never author a second DELP or production GitHub publisher. The source `skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py` remains native P/E/D/DE and issue TITLE/LIVE_STATUS owner. Separate existing guarded adapters own issue managed BODY and PR title/body.
- **Why:** Original Owner goal is the source- and evidence-governed whole lifecycle; passing synthetic validations does not authorize evidence or writes. Native responsibility core still rejects some full `owner/repo#PR` identities.
- **Evidence:** #325 T01–T03 issue comments 6103901027, 6104036057, 6104112633; `4-report.md` sections 3–8.
- **Result:** GET-only source observation usable for development; native V3.2 production writer OFF, programme #5 AC0/8.

## D02 — Integrate tested V3.1 fixture repair without restoring removed workflows
- **Decision:** Reuse draft PR #327's single-file `skills/engineering-pr-delivery-v3.1/tests/test_ci_terminal_checks.py` correction in #326, not a retired-workflow resurrection.
- **Proof:** #326 commit `82b45eb0a947ffde8931448989c6e6b002c042fb`; source blob `60b9485eed42451d5173de18cd94d768fe3b8dfe` matched #327; 274 tests V3.1 and focused suite at same SHA succeeded. #327 itself remains separate draft and unmerged.
- **Boundary:** Different heads never share CI credit.

## D03 — Owner-approved XS/S scope only; M/L kept on parent roadmap
- **Decision:** Implement XS1 evidence/plan/log correction, S2 controlled base reconciliation and S3 sanitized public GET envelope contract. Parent #289 [future M/L backlog](https://github.com/reallakshman19/Common/issues/289#issuecomment-6104487421) contains authentic graph/issuer, native generic publisher and physical C6/B as **future improvements**, not blockers to this small-workstream completion.
- **Proof:** #325 plan revision 3 comment 6104485981; results comment 6104535513. User's chat ID `6acae92b` is the lineage anchor.
- **Boundary:** Existing release gates still HOLD; no automatic transition to M/L tasks.

## D04 — Main-to-feature integration is permitted; feature-to-main production merge is not
- **Decision:** Use native reverse PR #328 (head `main`, base feature branch) after head/base double-check and zero overlapping changed paths. Merged the verified `main@c75b0c49cecf0624961b8d1c2841a787d6c3fd51` into feature at `b14b9930aa4edea4dee4763888632d6f65d84637`. Preserve other Tab2/Tab4/Oct09 files without editing them.
- **Proof:** [#328 merged](https://github.com/reallakshman19/Common/pull/328); [#325 plan revision 4 evidence](https://github.com/reallakshman19/Common/issues/325#issuecomment-6105035722).
- **Boundary:** Draft PR #326 is unmerged to `main`. Later `main` drift does not invalidate previously observed exact-head CI, but means the branch is no longer literally current to the latest main. Do not enter a recurring merge loop.

## D05 — Separate executed test evidence from terminal NOT_APPLICABLE workflows
- **Decision:** `dc41b6420fd5dfe1be1734007530b72eb505902f` is current PR #326 HEAD before this log-only package. All five workflows terminal SUCCESS, but native V3.2 and DELP job logs explicitly say `NOT_APPLICABLE` on relevant native paths. Count focused 44 each on three Python versions and V3.1 274 only at exact head; Local ran additional small suites.
- **Proof:** focused run 38108470192; V3.1 38108470239; V3.2 38108470281 (NOT_APPLICABLE); DELP 38108470201 (NOT_APPLICABLE); Local 38108470221 (tests run). Later coordination-log commits are different heads and must be checked separately.
- **Boundary:** CI success is not Owner acceptance or genuine material/positive E.

## D06 — Readiness-review and cold-boarding continuation, no live work
- **Decision:** Next safe XS/S continuation is read-only reviewer preparation: inspect current PR-to-main diff, file ownership, source/fixture/CI provenance, confirm issue and PR evidence consistency and publish a transparent readiness report. Do not assert reviewers or branch policy where access is absent.
- **Boundary:** No original private Owner graph, independent issuer/reviewers, live publisher, production cutover or Agent B launch without separately established authority. Tab2 #294 out of scope. Do not alter native protected V3.2 code, any active protocol/lease/state or issue/PR managed body/title blocks.

## D07 — Publish cold reviewer packet and hold at independent qualification boundary
- **Decision:** Publish [`handovers/2026-10-11-review-readiness.md`](handovers/2026-10-11-review-readiness.md) as a self-prepared source/review packet and link owner [#325 TASK_EVIDENCE](https://github.com/reallakshman19/Common/issues/325#issuecomment-6105503964). No reviewer status is inferred from its existence.
- **Reason:** The XS/S code/CI plan is done, but the Owner's required independent review, protected native modification grant, real Owner graph, lab and effective branch policy are not qualified. A same-session paper packet cannot serve as external reviewer, C6, or Agent B.
- **Handover boundary:** preserve five tab files and historical RECON; do not merge draft PR #326 to `main`, turn on writer, issue facts or initiate B. PR branch log-only commits are not credited with prior source-head CI.


## D08 — Explicit 12-section report on main; no Stage 2/Runner B authority
- User requested BuddyRunner PR #307's 12-section structure **only**, not a Stage 2 run; no Stage 1 digest, independent Runner B, live publisher or release grant was created. The exact technical report was committed on `main» at `0f0aa00a5b25a23b2e295f130bc6277f57aac55c» and published in full as #325 PLAN_UPDATE `6105639710»; parent #289 comment `6105641933» records chat-only Section 6 and all 44 named test cases/fixture grades.
- This is a documentation main-branch publication, **not** a merge of #326 or #327 into main. The report and these Tab1-only log copies cannot inherit CI from feature `dc41b642» or attest Owner AC. Stop all new work after the boarding brief.
