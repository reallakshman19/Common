# B0 — V3.2 source and lab recovery baseline (non-admitting)

**Reconciled:** 2026-10-10 (Asia/Muscat). **Owner objective:** recover an executable V3.2 prototype on the existing Common #285 E2E programme, not a V3.5 or production cutover. **Scope:** B0 source audit and next input requirement only. This file is a *point-in-time source-recovery inventory*, not an independently approved V3.2 graph, native R3 receipt, status calculator, evidence issuer, or GitHub publisher.

## Observed provider identity and exact source pins

| Surface | Provider-observed at inventory | Authority/classification |
|---|---|---|
| New Common repository | `reallakshman19/Common`; stable GitHub repository ID `1412133785`; default branch `main` | Real repository identity; not the historical provider |
| Common base at PR #299 read | `main@29dffef9ad9582fa6c24e75f13326d8eecf677dc` | Observed pinned comparison base; re-fetch before execution |
| Existing native V3.2 skill | `skills/engineering-pr-delivery-v3.2/SKILL.md`; Git blob `c6cbe524915281760b516660d4330ba0f51d44b4` | V3.2 additive candidate, V3.1 still production |
| Native DELP | `skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py`; Git blob `804cacca930e47c4528bb0d245efaf941996e4cf` | Reuse `project()`, no second P/E/D reducer |
| Native C6 | `skills/engineering-pr-delivery-v3.2/scripts/handover_context.py`; Git blob `ecae36055a63155aaa84b6b66d4a19ff0e3cffaf` | Source-bound read model, no authority grant |
| Historical graph checked on new Common base | `.github/v32-evidence-spine/718-proposal-v2.json`; Git blob `d35019b416cb3b573280e166027d3f65ba61f59c` | **Historical-only:** JSON still declares `programme.repository=reallaksh19/Common`, `programme.root=Common#718`; **not** a new-repo released graph |
| Recovery candidate before this inventory commit | Draft PR #299, branch `prototype/v32-296-readonly-provider-preflight`, exact original read `0aaf325c40935b4480941930da6ef6fd24f3caf8` | Unmerged; 66 ahead / 0 behind base; only 20 added isolated recovery/workflow files; no native frozen source changes |
| PR #299 targeted CI on preceding tested head | [Run 38059689616](https://github.com/reallakshman19/Common/actions/runs/38059689616), 7/7 scoped jobs; 122 tests each on Python 3.11/3.12/3.13 plus 276 direct native DELP and 49 direct native C6, total **691/691 test executions** | Historical **exact-HEAD** diagnostic evidence for `0aaf325c`; DO NOT transfer to a later head without new run |
| Other inherited CI | `validate-v3-1-foundation` FAIL at prior candidate; six missing retired workflow YAML paths among 274 tests | Separate V3.1 failure, not qualified overall green |
| Independent reviews and required checks | Submitted PR #299 reviews: 0; classic required-status policy: UNKNOWN at H11 provider witness | No qualified reviewer or effective D5 required-check policy |

Repository/source URLs:
- [New Common repository](https://github.com/reallakshman19/Common)
- [Draft PR #299](https://github.com/reallakshman19/Common/pull/299)
- [Common #285 — E2E recovery parent](https://github.com/reallakshman19/Common/issues/285)
- [Common #296 — implementation companion](https://github.com/reallakshman19/Common/issues/296)
- [Common #289 — separate production admission](https://github.com/reallakshman19/Common/issues/289)
- [Common #282 — historical lab checklist](https://github.com/reallakshman19/Common/issues/282)

## Historical lab visibility and custody boundary

The connected GitHub identity receives `404 NOT_FOUND` for `reallaksh19/relay-v32-e2e-lab` on 2026-10-10. Searches for `relay-v32-e2e-lab`/V3.2-labelled repositories exposed no accessible replacement. A private repository can return 404 when not authorized; **do not claim deletion, missing code, or absent historical actions**.

History documented in parent #285 and lab #282, **not independently re-observed in the private lab in this recovery pass**:
- Historical lab ROOT #1, phases #2/#3, leaves #4/#5/#6, original three-claim Proposal-V2, and P3.0 initial six managed issue zero-status writes/readback.
- Historic approval T05 is blocked/waived rather than a valid human Owner release.
- Real product R01/R02/R03 PRs, source-current positive facts, live nonzero P/E/D, dynamic PR publisher, cold C6 successor and S01–S26 remain unqualified.
- The original private lab Owner and automation reportedly shared an account/token identity; do not treat any agent-authored approval as an independent Owner act.
- `COMMON_READ_TOKEN` source/scope cannot be verified through current connected GitHub and must not be copied, disclosed or presumed read-only.

## Acceptance gap against parent #285

| Parent obligation | Status at B0 |
|---|---|
| P0/P1 current source manifest, repo/actor separation, human-authorized current lab graph | **PARTIAL**; current Common identity pinned; real lab/access/grant UNKNOWN |
| P2 real R01/R02/R03 source PRs + all nine original app goldens | **NOT VERIFIED / NOT DONE in observed current scope** |
| P3 accepted live source evidence → *one* native DELP → nonzero issue/ancestor status and H1→H2 stale/reverify | **NOT QUALIFIED**; only historical zero-only writer + synthetic tests |
| P4 generic safe PR metadata issuer, current real GitHub readback, one digest | **NOT QUALIFIED**; native historical `trusted_scoreboard_v32.py` rejects non-`Common#718/#733/#740` bindings |
| P5 native C6 current-graph frozen handover, different no-predecessor-chat successor | **NOT QUALIFIED** |
| P6 adversarial S01–S26 and P7 three clean replays | **NOT EXECUTED end-to-end** |
| G1–G5 final parent acceptance | **ALL PENDING** |

## Recovery branch choice / actual next executable step

**A — Recover historical private lab:** owner grants independently scoped GitHub GET access, separately provides a genuine T05 Owner approval for exact graph SHA+digest and authentic repository/leaf binding; re-run initial source/test baseline before any issuer/writer.

**B — Authorize replacement lab:** owner identifies a new accessible disposable repo and approves its synthetic CSV workload, graph/root/leaf scope, separate human/agent identities, minimal read/write fields and expiration. Build a fresh graph using provider-returned repository/issue IDs; never remap `Common#718` as though source authority followed the Git copy.

**Until A or B exists:** `B0=PARTIAL_SOURCE_AUDITED / BLOCKED_LAB_ACCESS`, `ACCEPTED_EVIDENCE=null`, `LIVE_GITHUB_WRITER=OFF`, `C6_INDEPENDENT_SUCCESSOR=NOT_RUN`, `PRODUCTION=V3.1`. The user's approval to *proceed with B0/B1 engineering* does not itself identify the missing target repository or grant a specific lab/production writer lease.

**Next engineer start:** re-fetch current PR #299 HEAD/base, `main`, exact graph bytes, branch policy and genuine GitHub lab access; read [#296 plan update](https://github.com/reallakshman19/Common/issues/296#issuecomment-6099239271) and parent #285; either recover A or select B with actual Owner scope. Once available, B1 must capture an actual current graph+source digest and original nine precommitted RED tests; only then perform real R01 B2→B4 positive evidence→DELP→GitHub demonstration.

No credentials, raw private comments, synthetic accepted facts, manually authored progress or writer grants belong in this file.
