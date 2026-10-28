# Superseded material — immutable provenance archive

This is the designated **/superseded/** root for *proven retired* project workspaces and documents. This directory does **not** select live protocols or authorize a replacement workflow. Use [Common Handover Master](../skills/Handover%20Master/SKILL.md) as the one agent invocation.

## Archived (source-first)

- [Dash V2 coordination history](coordination/Session_Oct07/Tab6_Dashboard_V2/) — historic workspace for Common #360; Owner explicitly superseded its consumer by [CoordinatorLandingpage #21](https://github.com/reallakshman19/CoordinatorLandingpage/issues/21). Original Git blob SHA-1s **LINEAGE f7acbb145c79877a380912a3cfb6def6fa9d9b2f**, **LOG defbb06f615d6a290d15fc7e4d69d83b11232329** (no content rewrite). Old location has a redirect README; immutable source at [pre-archive main eff86f7885d759449c4125c9c8c346376caa871e](https://github.com/reallakshman19/Common/tree/eff86f7885d759449c4125c9c8c346376caa871e/coordination/Session_Oct07/Tab6_Dashboard_V2).

## Archive eligibility — required for every future move

1. Show explicit Owner/source evidence that a module is **retired**, not merely old or difficult to find.
2. Check all current internal/external consumers, imports, workflow jobs, exact hardcoded paths, issue protocols, generated artifacts and link history. A search gap is not proof that external consumers do not exist.
3. No canonical active skill, runtime dependency, test fixture or protocol selector may be removed/repointed in a simple archive PR.
4. Move original file bytes **without modification**; record original blob SHA and immutable source commit, keep an old-path reader pointer if useful, and rerun relevant CI and cold-source tests.
5. This archive never makes private Stage-2 content public or upgrades an old Owner claim to acceptance.
6. Any change requiring cross-project migration, broken path repair, compatibility redirects or privileged protocol updates needs its own Owner-scoped migration/qualification plan.

## Explicitly **not** archived

The following remain canonical or version-pinned and are NOT superseded merely by Handover Master: `relay/CONTINUITY/TEMPLATES/TECHNICAL_HANDOVER.md` (Stage2 gate); `skills/two-pass-prompt-generator`; `skills/three-pass-prompt-generator`; `skills/engineering-pr-delivery-v3.6`; `skills/engineering-pr-delivery-v3.5` (historical pinned); `skills/buddy-runner-v1-6` (pinned by v3.6); `skills/buddy-runner-v1-7` (separately selectable); `skills/relay-onboarding-rwi` (WP5 merged). Moving those would break active links, native validation or privacy/isolation contracts.

**Do not move based on age or version number alone.** Keep actual source identity separate from claims of functional/Owner acceptance.
