# CIIFR_GEO R2 — Progress Page projection proposal

**26 October 2026 · Oracle-authored · PUBLIC_SAFE · PREPARED, NOT PAGE:SYNCED.**

The Owner requested an updated concept, roadmap, existing WBS and next implementation plan. The five source documents are published on the Common review branch `docs/ciifr-geo-roadmap-r2-20261026`, planning commit `ca196c6ea5f5599a7c19cff9a828f1cf785a9f9c`. Native XCU issues #166, #177, #179 and #180 were updated in place. No product implementation, worker dispatch, acceptance, merge or Cycle change is claimed.

## Destination and writer custody

Destination is the **existing CIIFR Progress Page writer**, identity UNKNOWN, through [progress-page PR #18](https://github.com/reallakshman19/progress-page/pull/18). Its observed head is `98f9cb7f9a8a37732ead0d937c237a5dbdc7c3de`, branch `pp/ciifr-r4-home-onboarding-protocol-20261025`, open/draft. The proposal does not write that branch or create another Page PR.

The governing [Progress Page MODES](https://github.com/reallakshman19/Common/blob/d81e1e034b647ea64a90e4944b8071f2a5286434/skills/agent-work/progress-page/references/MODES.md) states: “One writer per project at a time. The open DRAFT pull request … is the claim; another agent waits for its merge or its closing.” This checked handback preserves that writer's claim and every existing WBS4/E1 projection.

## Proposed data changes

- Retain project key `ciifr`, existing WBS 3 / 3.1–3.4, milestone IDs M12–M16, card/group IDs and the project's R4 revision and aim.
- Revise only the five Geometry milestones, five `geo-g0`…`geo-g4` cards and two existing Geometry group labels. The native CLI also refreshes the project attribution/time metadata.
- Record PR181 as a native-validated XML **CANDIDATE**. Viewer/browser/Owner acceptance remain unverified. Current WBS3.1 plans reuse of existing 3D Edit graphics with SVG retained; next functional WBS3.2 is independent topology plus Manual/Topology/OR/AND and visible conflicts.
- Add four repository references: revised concept, implementation plan, next-WBS card and viewer-reuse source evidence. Keep all prior fixtures intact.
- Append 16 Timeline events: PR18's existing 398-event prefix is unchanged, resulting in 414 events. No new agent/chat binding or unrelated workstream status is created.

Only `data/ciifr/index.json`, `cards.json`, `fixtures.json` and `audit.json` differ from the observed PR18 head. No Page viewer, workflow or CLI code is changed.

## Artifacts and regeneration

- [PAGE_PR18_GEOMETRY_R2.patch](PAGE_PR18_GEOMETRY_R2.patch): 25,788 bytes; SHA-256 `2aa80c6feda731e0226194527668681c118fd7e3475f9d04a8f5e9c65093bc86`.
- [PP_CLI_COMMANDS.json](PP_CLI_COMMANDS.json): the 16 final native CLI argument arrays used to generate this proposal. Each array follows `python tools/pp_cli.py`; run only once on a verified clean destination or regenerate selectively against its current data. Do not blindly replay fixture additions or duplicate Timeline entries.

All proposed JSON changes were made with the checked-in `tools/pp_cli.py`. Initial length-validation failures rolled back their failing operation; the final corrected commands and data passed the contract. No JSON was edited by hand.

The existing writer should first verify its current branch/head and clean working tree. If the head is still the exact value above, download the patch, verify its SHA, then run:

```bash
git rev-parse HEAD
git apply --check PAGE_PR18_GEOMETRY_R2.patch
git apply PAGE_PR18_GEOMETRY_R2.patch
python tools/pp_cli.py check --base origin/main
git diff --stat
```

If the branch advanced, reconcile against the latest native #166/#177 and current Page data; regenerate with the supplied CLI commands as appropriate. Do not force-overwrite another writer's data or reset its audit history. Review/commit on the existing PR only. Exact-head hosted checks, merge authority and published browser readback remain that writer's separate responsibilities.

## Executed checks

On a local proposal checkout based on exact PR18 `98f9cb7…`, both `check --base origin/pr18` and `check --base origin/main` returned **OK**. The finished patch was then checked and applied to a second clean checkout of the same exact head; both checks again returned **OK**. Its four resulting files were byte-equal to the original CLI-generated proposal.

Scope assertions passed: existing audit prefix, non-Geometry milestones/cards/groups and prior fixtures unchanged; project aim, revision, rules and chat bindings unchanged; only routine attribution/time metadata changed outside the named Geometry entries. Native `triggers --json` showed no Geometry owes or nudges; unrelated CIIFR alerts are outside this task and were not dispatched or rewritten.

These are data-contract and patch checks, not browser/deployment or engineering acceptance. The source handover also passed the existing Common WBS-continuity regression, 4/4 tests, without modifying that validator or its protocol inputs.

## Source of truth and next action

[Concept Note R2](https://github.com/reallakshman19/Common/blob/ca196c6ea5f5599a7c19cff9a828f1cf785a9f9c/oracle-cycles/ciifr/continuity/payload/CONCEPT_NOTE.md) and [Roadmap / WBS / implementation plan R2](https://github.com/reallakshman19/Common/blob/ca196c6ea5f5599a7c19cff9a828f1cf785a9f9c/oracle-cycles/ciifr/continuity/payload/ROADMAP_AND_IMPLEMENTATION_PLAN.md) are review-branch sources, not merged-main documents. Native parent is [XCU #166](https://github.com/reallakshman19/XML_Compare_Utilities/issues/166); next functional card is [WBS3.2 / M14 / #177](https://github.com/reallakshman19/XML_Compare_Utilities/issues/177).

The existing Page writer reconciles/applies this proposal. Oracle may independently qualify one fresh builder for the written current viewer card and one actual G2 source assignment when appropriate. The prepared documents do not assign either recipient. Page synchronization is not a hold on disjoint, authorized product source work.
