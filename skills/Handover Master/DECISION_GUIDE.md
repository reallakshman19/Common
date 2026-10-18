# Handover Master — single entry, decision guide and good practices

**Canonical single link:** [skills/Handover Master/SKILL.md](SKILL.md)

**Why:** The same engineering handover work was split across technical templates, old v3.5 scripts, standalone two-pass/three-pass prompt generators, v3.6's *different* two-/three-pass generators, BuddyRunner and ONB-RWI. A successor should never have to pick a folder and infer whether it carries Owner authority. This folder is the front door and **navigational registry**; unchanged native sources are the executors.

## Decision table (what an agent should choose)

| Actual need | Choose in Master | Canonical next source | Output and non-negotiable boundary |
|---|---|---|---|
| Give successor complete factual implementation explanation after authenticated blind freeze | `technical` | `relay/CONTINUITY/TEMPLATES/TECHNICAL_HANDOVER.md` | Exactly 12 coherent sections; Stage2 only, derived from native handover/custody |
| Study system independently first, then see task and reconcile | `two-pass`, `standalone` | `skills/two-pass-prompt-generator/SKILL.md`, `schema.md` | 2 prompts; Pass 1 cannot know issue/PR/proposed fix; approval before material execution |
| Broader imagination/rethink vs actual project/issue reality | `three-pass`, `standalone` | `skills/three-pass-prompt-generator/SKILL.md`, `schema.md` | 0.5/1/2/2.5/3 prompts; no extra stages; schema-first handshake |
| Project already under v3.6, wants two prompts | `two-pass`, `v3.6` | `skills/engineering-pr-delivery-v3.6/scripts/prompt_2pass_v36.py` | v3.6 plan→execution; explicit Owner AIM label/plan; do not swap standalone schema |
| Project under v3.6, wants three-pass | `three-pass`, `v3.6` | `skills/engineering-pr-delivery-v3.6/scripts/prompt_3pass_v36.py` | v3.6 source/falsifier→implementation→independent validation |
| G1/ G2 handover challenge, one final predecessor answer | `buddy`, version pinned, exact phase | `skills/buddy-runner-v1-6/SKILL.md` or `v1-7` | 1a→1b→2; 1a/HOLD; 2 concludes, no acknowledgment cycle |
| One-time buddy response on a newly posted Task Evidence | `buddy`, phase `Y` | selected BuddyRunner native skill | Xb→Y once; exact issue/evidence digest and duplicate fence |
| Outgoing engineer disappeared, no final LOG or chain | `zero-exit` | `skills/relay-onboarding-rwi/reporting/compile_report.py` | Source-referenced 12-section report+manifest+verdict; BLOCKED until proof |
| “What is status/progress?” | `status` | `skills/universal-workflow-progress/SKILL.md` | Read-only view, no new agent action |
| Historical v3.5 handover | `technical` / `v3.5` | `skills/engineering-pr-delivery-v3.5/SKILL.md` and native handover | History/version-pinned; not the default for v3.6 |
| We have an ROI alternative and objective evidence | Native module plus `skills/software-mcda` | `skills/software-mcda/SKILL.md` | Separate assessment only after Owner outcome/eligibility filters |

A task might use a sequence of **different modes**, e.g. zero-exit reconstruction first, then two-pass design review. They remain separate work products with explicit stage/authority transitions, not additional steps grafted into a native generator.

## 1. Entry-point decision algorithm

1. **Check Owner's exact request:** generate prompts? start a particular handover phase? reconstruct a technical report? assess existing evidence? publish anything? If unclear, use the zero-write router for a suggestion and ASK before action.
2. **Establish programme version and effective Owner amendments:** project label/plan/current issue/roadmap first; a word `v3.6` in the governing source is not proof the active work is v3.6 without an actual linked approved work label.
3. **Check whether blind isolation applies:** Technical template is expressly `STAGE2_AFTER_FREEZE_ONLY`. Two-pass and three-pass early prompts must not see task answers. Avoid reading task/PR before building quarantined first-pass prompt, even when current agent knows it.
4. **Detect the deliverable shape:** Two-pass requires schema-defined two prompts, three-pass exactly its five prompt objects, Buddy exactly its three role messages or one intervention; technical handover requires one coherent report; zero-exit requires source-referenced original problem/evidence gaps/report.
5. **Refetch native controlling files at current main; compare protocol revision and content/blob SHA:** current main is a mutable name. A checked-in Master registry is a pointer, not the protocol SHA or authorization. Use GitHub connector or Git locally when available.
6. **Read native validation and authorizations:** v3.6 mandatory `--label`, `--plan`, `--lab` for lab commands, explicit `--apply --confirm-scope` for any writes. Standalone prompt validators are strictly mode-bound. Buddy duplicate receipt and role review are native. Don't run scripts by guessing flags.
7. **Run approved mode, validate its outputs, read back GitHub writes:** default write status HOLD. If source/role/oracle/permission is stale or unavailable, report a diagnostic and stop.
8. **Produce ONE useful result:** selected mode, WHY, exact native source, source freshness/CI/oracle evidence, completed phase, genuinely unknown aspects, next exact verification. No invented success badges.

## 2. Source authority: separate five layers

**Owner intent:** actual problem/WHAT/WHY + later explicit amendments (e.g. CoordinatorLandingpage rather than Dash V2). A recorded Owner statement may have a source URL but still needs actor/authenticity readback. Reviewer/agent text cannot approve on the Owner's behalf.

**Canonical code:** real branch/ref commit/PR head and changed files; do not confuse historical research cut, current `main`, candidate PR SHA, CI-tested SHA and deployed SHA. Git blob match is identity, not execution semantics.

**Original inputs/fixtures:** checksum measured from authentic source bytes vs caller-supplied bytes. A partial postimage is not a complete Owner golden. Independent positive and negative tests must use appropriate native fixtures.

**Process continuity:** AGENT_STATUS, snapshot, predecessor handover, Buddy messages and progress dashboards are derived. They can help navigate but cannot replace code, Owner or tested output reality.

**Permissions/acceptance:** owner-writer scope, protected decisions, review and merge gates are independent of the above. HOLD when uncertain. A generator producing valid text is not permission to create EPs, PRs, plans, writes or release.

## 3. Good practices for every handover

- Explain original user problem in plain human language, and use one real original input→expected result example.
- Describe **causal call flow**, not file inventory: input→entrypoint→parser/validator→owning module→worker/transaction→consumer/output; name actual functions, types, cancellation and rollback boundaries, with source anchors. Mark uninspected edges UNKNOWN.
- Preserve before→after behavior and rejected alternatives with evidence and falsifiers; avoid patchwork and false “all complete” claims.
- Present exactly the authorized native stages. No fourth BuddyRunner round, fake Pass 0, unsolicited reviewer cycle, duplicate coordinator or status poller.
- Use exact-current HEADs and match tests to tested SHA. Green check on a different SHA is historical only. Link both successful and failing job logs.
- Avoid a standing innovation quota. An effective KEEP is valid. Only propose measured high-ROI change with falsifier and Owner approval path; no drift from original Owner WHAT/WHY.
- Protect blind agent inputs: do not pass issue, PR, proposed fix, predecessor analysis or current solution into a supposedly independent baseline. GitHub repo visibility != confidential isolation.
- Never treat a file/folder rename as protocol migration without checking all workflows/imports, links, handover markers and tests. Keep native paths stable.
- Don't place secrets/private actor notes in public reports or CoordinatorLandingpage. Read-only public projection requires separate Owner/TeamCoordinator approval under its actual v2.3 protocol.
- Source revision *and* file SHA should appear in the output; if either is unknown, state UNKNOWN. Pin current source before action.
- One named next action includes exact issue, repo/head, source locus, success/failure witness, tests and stop conditions.
- For large projects, separate agent roles **vertically by independent responsibility and actual file ownership**, not multiple agents concurrently patching a single core pipeline.
- If predecessor disappears, new engineer must start from native GitHub evidence; final chat LOG is optional enrichment, not a prerequisite to reconstruct.
- If a workflow phase is already published, check its receipt and don't issue duplicate publications by renamed request IDs.

## 4. Source and protocol migration discipline

**Do not physically copy/move existing modules today.** Two-pass and three-pass have hardcoded schema paths, validation handshakes, and published contracts. v3.6 native generators differ from standalone. Buddy v1.6 and v1.7 have version-specific role verification. Relay native technical report has a Stage-1 privacy boundary. WP5 ONB is merged but WP1a–WP4 remain draft. A naive mass move would break invocations and leak or falsely promote authority.

When there is a future Owner-approved actual relocation, first inventory import references and GitHub Actions scripts, add compatibility aliases, run real cross-repo cold entry and published protocol validation, update all calling repos then remove aliases only after expiry. Until then the Master registry + one invocation is the stable entry.

## 5. Concrete agent invocations

~~~sh
# Decision only (never executes):
python "skills/Handover Master/route.py" --intent "Need a completely independent baseline then roadmap and task review"
python "skills/Handover Master/route.py" --mode three-pass --workflow standalone
python "skills/Handover Master/route.py" --mode three-pass --workflow v3.6
python "skills/Handover Master/route.py" --mode buddy --workflow v3.6 --phase 1a
python "skills/Handover Master/route.py" --mode buddy --buddy-version 1.7 --phase 1b
python "skills/Handover Master/route.py" --mode technical --stage1-freeze-verified
python "skills/Handover Master/route.py" --mode zero-exit
python "skills/Handover Master/route.py" --mode status
~~~

`--stage1-freeze-verified` is ONLY a caller assertion for route preflight. The agent must independently validate the actual Stage1 freeze/recipient isolation before reading or disclosing protected technical material. The CLI never asserts external verification.

## 6. Exact output / handover acknowledgment

Return compact human summary: `MODE`, `GOVERNANCE`, `LIVE SOURCE (path, SHA, revision)`, `WHY THIS MODE`, `PHASE`, `AUTHORITY`, `EVIDENCE`, `BLOCKERS`, `GENERATED ARTIFACT`, `NEXT VERIFY`. If insufficient evidence: `HOLD` and list missing source/role/approval, rather than inventing a selected answer.

**Do not** turn this Master into a new Common lifecycle skill, Dashboard v2, protocol governor, Project Coordinator or automated actions service. See [MODULE_INDEX.md](MODULE_INDEX.md) for all actual links, [SKILL.md](SKILL.md) for canonical agent instruction and [sources.json](sources.json) for machine navigation.


## 7. v3.6 tenth-agent issue continuity (Common #400)

For v3.6 engineering work, read [native continuity chain contract](../engineering-pr-delivery-v3.6/CONTINUITY_CHAIN_V1.md) after choosing the governing work/label. The owning issue is the durable source of the original Owner WHY and significant Owner-supplied technical amendments, original fixtures and complete golden, measured benchmark, causal implementation crux, what agents 2/3/10 contributed, PARKED and high-ROI adopted ideas (with the actual Owner decision reference), failures and a reproducible next verification.

The additive C1 `issue_chain_v36.py` only validates that all 11 categories are explicitly represented or marked UNKNOWN. **100% accounted is not 100% verified.** Re-fetch live issue/source and independently authenticate input bytes, actor and semantic result before engineering acceptance. A technical handover report is a filtered, source-referenced view; a last chat or predecessor LOG is never its only source.

BuddyRunner 1a/1b/2 and Xb→Y, and separate native v3.6 2-/3-pass generators may consume **phase-safe issue evidence pointers** only. Early independent stages must not receive predecessor solutions. Do not append an extra phase or automatically promote a proposed improvement as adopted. This entrypoint remains a router, not an Owner decision issuer or GitHub title writer. Smart title/label enhancement is a later opt-in publisher workpack, not part of C1.
