# Outgoing G1 — final reconciliation 2, then close the handover

**Your assignment:** turn 1b into a clear, roadmap-grounded execution direction. You are the outgoing predecessor, not another incoming Stage 2 investigator. Follow the shared grounding contract. Verify 1b's exact body/digest, source SHA and provenance before relying on it. Re-fetch a claimed provider publication; accept directly supplied 1b text with a provenance reference and label it SUPPLIED_UNVERIFIED. Independently inspect its key source findings. Missing publication alone does not block reconciliation. On failure return the bounded 1B_NOT_VERIFIED diagnostic and stop.

**Think:** Given these independent findings, which assumption, dependency, ordering or ownership choice should change so the successor can make useful progress now?

Ask internally:
- Which finding corrects my previous understanding? Which working capabilities should remain authoritative?
- Is the current route itself the bottleneck? Compare a local patch with a bounded alternative grounded in the parent/roadmap.
- Can the successor start without another interpretation from me, and what observable result would support or overturn the direction?

Reconcile four viewpoints: Owner outcome, frozen 1b proposal, predecessor/competing claims, and independently observed source/evidence. Explain your own mistaken assumptions when relevant. Keep the pinned and observed live source distinct. Resolve one module owner per responsibility and choose at most three high-ROI corrections. KEEP/NO_CHANGE is valid; do not force change. VERIFY_FIRST needs a falsifiable benchmark and result-dependent actions. If all useful work is blocked, state the precise missing decision/input and unblock condition.

## Response 2 — decision first

Return a plain-language **RECONCILED_PURPOSE**, what changed in your understanding, chosen route and why it helps the Owner outcome. Give a compact module decision map and one immediate bounded workpack, or an honest BLOCKED decision:

| Task ID | Responsible engineer / module | Exact source baseline and files/functions | Action and Owner benefit | Acceptance oracle and result branches | Effort / rollback | Existing authorization or precise blocker |
|---|---|---|---|---|---|---|

Separate executable work from blocked work and name the exact decisions genuinely reserved to the Owner/controller. This analytical response creates no coding or custody authority; existing authorization need not be requested again.

## Self-contained technical handover — preserve all twelve sections

Ground each section in source/evidence or mark UNKNOWN/NOT_RUN. Include the content; do not replace it with links to predecessor chats.

1. **Original problem and Owner WHY:** real user experience, parent/roadmap acceptance and non-goals.
2. **Repository migration and identity:** actual repo/issue/PR boundaries, main, inherited/current/assessed/tested SHAs, branch and drift.
3. **What exists:** reusable modules/functions, one owner per responsibility and actual runtime/deployment entrypoint.
4. **How data flows:** original inputs through custody/transformation/consumers to complete user outputs and authority seams.
5. **What changed and why:** surviving implementation choices, corrections, tried/rejected routes and superseded assumptions.
6. **Input provenance and acceptance oracles:** every available original/attached/benchmark/golden input, path/hash/ref, authentic vs derived vs synthetic, unavailable inputs and protected expectations.
7. **Actual execution evidence:** commands/CI/browser results and the exact source each proves; NOT_RUN and missing checks.
8. **Known failures and unresolved defects:** earliest failure/unproven boundary, signatures, cause vs hypothesis and product effect.
9. **Reconciled ROI decisions:** selected bounded route, local alternative, parked/rejected changes, risks and dependencies.
10. **Authority, security and preservation:** source integrity, consent/exports where applicable, real writer/reviewer/Owner boundaries and rollback.
11. **What remains:** product, source, deployment, semantic qualification and release responsibilities; executable vs blocked work.
12. **Exact next engineer start:** task ID, engineer/module owner, raw SHA and source locations, first action, acceptance oracle, rollback/stop conditions and precise unblock conditions.

Prepare PLAN_UPDATE — BUDDY_V16_2_FINAL_DIRECTION_AND_HANDOVER on the existing issue if authorized. Read it back and record `phase: "2"`, target `handover.id`, and response ref on the existing coordination surface. Otherwise return copy-ready NOT_PUBLISHED. Publication or a byte digest never certifies release or grants a writer.

Return the final direction and complete handover once. Do not ask G2 to perform another Stage 2, acknowledge this response, or return for another review. The successor can continue through the existing authorized workflow. End predecessor involvement in this handover.

Required ending: `2 | HANDOVER=CLOSED | NEXT=successor follows final direction under existing authorization | PREDECESSOR=STOP`
