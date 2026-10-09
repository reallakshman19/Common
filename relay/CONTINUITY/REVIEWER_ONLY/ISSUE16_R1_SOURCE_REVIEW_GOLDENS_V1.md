# ISSUE #16 / R1 — source-backed adversarial reviewer goldens (NOT Stage 1 Runner input)

**Purpose:** test the HOW/WHAT questions and handover evidence criteria against **observed, existing repository code**, without giving an independent historical Stage1 Runner a pre-solved answer or pretending that reviewer prose equals executed tests.

**Classification:** `REVIEWER_ONLY / CURRENT_SOURCE / OPERATOR_EXPECTED_ANSWERS`. A path containing `REVIEWER_ONLY` is not an access control. A clean B must receive neither this file, current-code refs, nor an unfiltered repository browser before Stage1 freeze. These cases cannot be rebranded as authentic original Agent A task-start/Owner fixtures; no real independent B or browser/user-journey run was performed here.

**Pinned code repository:** `reallakshman19/Common@3afd78e0635957e496cfef99f6727590001f94cd` (2026-10-09 readback).

## Case G1 — Embedded Coder identity and false Local completion

**Source:** [embedded_coder_v35.py](https://github.com/reallakshman19/Common/blob/3afd78e0635957e496cfef99f6727590001f94cd/skills/engineering-pr-delivery-v3.5/scripts/embedded_coder_v35.py), blob `5b2d4b1bf4653cbc36c3d993012393d9db938d68`. Executable test source: [test_embedded_coder_v35.py](https://github.com/reallakshman19/Common/blob/3afd78e0635957e496cfef99f6727590001f94cd/skills/engineering-pr-delivery-v3.5/tests/test_embedded_coder_v35.py), blob `7b1f330c96fd752717200b4e64be6f3c6c849cc4`.

**Producer/consumer:** `engineering_responsibility("PRD-492-A")` produces the nested `ENG-PRD-492-A-CODER` identity; `build_context` materializes Local-bound provenance and explicit denied powers; `validate_context` rejects role/protocol/authority drift; `build_task_result` preserves `local_responsibility_complete=False`, which `validate_task_result` enforces even when engineering scope is marked completed.

| Probe | Input / change | Source-derived expected observation | Existing test witness |
| --- | --- | --- | --- |
| G1-P positive | `PRD-492-A` with pinned valid Local+Relay protocol refs and acceptance profile; `role=CODER` | nested `ENG-PRD-492-A-CODER`; valid Coder result does **not** complete Local | `test_nested_identity_is_namespaced_below_local_responsibility`, `test_engineering_complete_never_completes_local_responsibility` |
| G1-N1 negative | `local_responsibility_complete=True`, even after re-digest | reject with Local completion denial; content digest **alone** isn't authority | `test_forged_local_complete_is_rejected` |
| G1-N2 negative | change `role` to `REVIEWER` | reject Coder-only role | `test_role_is_coder_only` |
| G1-N3 negative | replace V3.5 pinned protocol ref with V3.2 | reject wrong active protocol | `test_v32_protocol_ref_is_not_valid_v35_authority` |

**Falsifying question:** “If all Coder implementation checks succeed, can the Relay result complete the Local delivery responsibility or grant a Reviewer role?” **Correct based on inspected code:** NO. Even a valid `TASK_RESULT` is `CODER_ENGINEERING_EXECUTION` scope, not Local Reviewer/merge completion. **False shortcut:** `digest` matching or `P100` proves a Local handoff. **Missing observation grade:** test methods exist; no execution is claimed at this pinned SHA by issue #16.

## Case G2 — DELP agent fact publication versus derived percentage/title

**Source:** [delp_projection_v35.py](https://github.com/reallakshman19/Common/blob/3afd78e0635957e496cfef99f6727590001f94cd/skills/engineering-pr-delivery-v3.5/scripts/delp_projection_v35.py), blob `a6eb1219e736f7a3847505987a25b042ab4c9d5e`; [test_delp_projection_v35.py](https://github.com/reallakshman19/Common/blob/3afd78e0635957e496cfef99f6727590001f94cd/skills/engineering-pr-delivery-v3.5/tests/test_delp_projection_v35.py), blob `529c120b56624d8f5302af49c628c5cec35ea3ae`.

**Producer/consumer:** existing Agent-authored leaf `TASK_EVIDENCE` carries a `CHECKPOINT_FACTS_V1` source fact; `forbidden_fields(facts)` recursively scans mappings and strings for derived or plan-authority fields and progress/title notation; `validate_facts(facts)` rejects forbidden fields, missing current candidate SHA/issue and wrong record shapes; after accepted graph/facts/material observations, `compute_leaf` derives leaf projection. No agent-composed title/weight/percentage is accepted as an input fact.

| Probe | Input / change | Source-derived expected observation | Actual evidence state |
| --- | --- | --- | --- |
| G2-P positive | canonical checkpoint facts `responsibility.issue`, `material.candidate_sha`, bounded unit results/evidence refs; no authored `P/E/D` | input can be validated; computed P/E and ancestor title depend on separate accepted graph/current provider material | validator source and test fixture constructors present; runtime result **NOT_RUN here** |
| G2-N1 negative | insert author-supplied `P`, `E`, `D`, `weight` or `title` within purported facts | `forbidden_fields` identifies agent-derived/plan-authority content; `validate_facts` emits violations | direct code at `forbidden_fields` / `validate_facts` inspected |
| G2-N2 negative | interpolate progress/title notation inside a string field | `_walk_strings` plus `_NOTATION` rejects injected derived projection text | direct source inspected |
| G2-N3 negative | remove `material.candidate_sha` or change its 40-hex format | `validate_facts` emits candidate SHA requirement | direct code inspected |

**Falsifying question:** “Can handover markdown or a well-formed digest update root completion by including `D100` in an Agent fact?” **Correct based on code contract:** NO. The authorized DELP projector derives scope-weighted values; source-current provider observation and graph determine whether evidence remains accepted. **False shortcut:** a PR comment showing `100%` or old-head workflow success changes the authoritative scoreboard. **Missing observation grade:** tests were not run by issue #16 and no live provider graph was evaluated in this file.

## Case G3 — merged full technical report completeness vs partial draft

**Sources:** current [main 12-section handover template](https://github.com/reallakshman19/Common/blob/3afd78e0635957e496cfef99f6727590001f94cd/relay/CONTINUITY/TEMPLATES/TECHNICAL_HANDOVER.md), blob `a907295e31dbfc22b9af3a425c53bd9ebb48cc51`, contrasted with [draft PR #14 ten-section template](https://github.com/reallakshman19/Common/blob/ced4c262c3114cfa3dd278271908612efcdc7922/relay/CONTINUITY/TEMPLATES/TECHNICAL_HANDOVER.md), blob `af08d1b2e2fa543a1232b7a685d54020ddf48ef7`.

**Expected:** preserve **all twelve semantic information dimensions** of main's merged V2 with explicit post-freeze disclosure, native `HANDOVER_CONTEXT` authority, original WHY and complete HOW, actual source symbols/consumers, migration/HEAD/tested-HEAD distinction, negative fixtures, CI step truth, known defects, first safe command, three adversarial successor reconstruction questions and honest UNKNOWNs. Draft V2 in #14 has valid additional R14 typed roles and richer failed-attempt details, but cannot overwrite the merged contract under the same label without reconciling exact consumer requirements.

**False success:** PR text calls the handover “complete,” or current `main` has a template, while actual Agent A authored report / native handover receipt / separately authenticated B / same-B Stage2 are `NOT_RUN`. **Falsifier:** cold successor asked to reproduce one real source-to-output flow cannot identify function, tested SHA or negative golden from the completed report.

## Manual reviewer protocol (not a fake model run)

1. Review code at the pinned source SHA; check G1 and G2 function definitions, direct tests, actual producer→consumer semantics and negative variants. Grade unexecuted observations `SOURCE_DERIVED_EXPECTATION`, not `PASS`.
2. For any later **authentically isolated historical** B trial, construct independent original-only intake from the real A task start (or `UNKNOWN`). Do **not** inject current G1/G2 answer keys, this reviewer file or current code/PRs. Do not require fixed numbers of arbitrary alternative designs when `NO_CHANGE` is evidence-based.
3. Only after an external freeze may a reviewer use these current-source probes to test B's claims in Stage2. Record actual read-denial attempts, provider/fixtures, exact test head and results separately.
4. Run the focused `test_issue16_handover_contract.py` to protect the merged report structure; a static template test is not a real Stage2 or new-writer acceptance.

**Acceptance:** the fixtures give concrete, falsifiable *reviewer* expectations in two code domains; **no real independent Runner launch, frozen prompt, test command execution or benchmark is claimed** by their publication.
