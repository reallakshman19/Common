# V3.2 lifecycle on relay-v32-e2e-lab: aligned plan (PAUSED)

**Status: PAUSED by the Owner on 12 Oct 2026.** No work continues on this branch until the Owner resumes it. Plan only; no code in this change.

## Owner's aim (verbatim, 12 Oct 2026)

> Main aim: to fix the life cycle issue of V3.2:
> Parent issue>Task decomposition>live scoreboard on issue title>smartPRtitle>Handover
> improve this with traceable key parameters like detailed child issue, task evidence etc

## Sticky label `V32-LIFECYCLE` (draft card CP-V32-LIFECYCLE-01, waiting for the Owner)

- **Problem:** You cannot see from GitHub what agents did or how far a work has got; each successor starts half-blind.
- **Main aim:** From one parent issue, GitHub alone shows the plan, evidence and live progress; any successor continues without chats.
- **Outcomes:** O1 a parent issue is decomposed into child issues with a visible plan; O2 each finished task posts its evidence on its child issue; O3 issue titles show live progress, updated automatically; O4 PR titles say what they deliver and their state, automatically; O5 a successor continues from GitHub alone, without chats.
- **Owner constraint:** the V3.2 lifecycle (skill engineering-pr-delivery-v3.2), not another version.
- **Task aim (O1–O5):** One real parent issue on the V3.2 lab runs end to end; its titles update themselves as evidence lands.
- **Done when:** On relay-v32-e2e-lab: a parent issue with child issues and evidence; issue and PR titles update automatically; a successor continues unaided.

## Where the work stands (repository facts, 12 Oct 2026)

- #325 T01–T03 are read-only candidates in draft PR #326 (head `6b138b6`, this PR's base): a generic current-source provider, a preflight and a publication plan for issue titles, LIVE_STATUS and PR metadata. Nothing is written to GitHub.
- #316 proposes the native full PR-reference amendment (inactive, `owner_authorized:false`); #313 is an integrated read-only shadow. The V3.2 writer is disabled.
- The lab reallaksh19/relay-v32-e2e-lab is public since 11 Oct; the agent reports its three bound PRs merged and 12 leaf-issue comments without native CHECKPOINT_FACTS_V1 blocks.

## Plan, aligned to the outcomes (to run only after the Owner resumes)

| Step | Work | Outcome | Size | What changes for the user | Needs |
|---|---|---|---|---|---|
| P1 | Run the #326 publication plan in dry run against one real parent issue on the lab; publish the titles and status block it would write | O3, O4 | S | you see the live titles before any write | — |
| P2 | Decompose that parent issue into child issues; each finished task posts its evidence (Outcome / For the user / Proof) on its child issue | O1, O2 | M | the plan and evidence are on GitHub | lab write access |
| P3 | Enable the generic writer on the lab only; titles and one PR title update as evidence lands | O3, O4 | M | titles update themselves | Owner grant: AMEND-V32-289-PRREF-017 (#316) |
| P4 | Generate the handover from GitHub alone; a cold successor continues from it | O5 | M | no chat needed to continue | — |

## Decisions

- **Held for the Owner:** AMEND-V32-289-PRREF-017 (#316) — needed for P3.
- **Proposed as not needed for this demonstration** (the Owner decides): D02 / D03 on qualifying "native" checkpoint evidence of the original lab. The demonstration shows the lifecycle working on the lab; it does not certify the lab's historical evidence.
- **At resume:** the independent v3.6 skill planned in reallakshman19/Common#341 may supersede the V3.2 lifecycle. Decide then whether V3.2 continues P1–P4 or hands its findings (the generic provider and publication plan of #326) to v3.6.

---
Prepared by the Coordinator (Claude Code) on the Owner's instruction, 12 Oct 2026.
