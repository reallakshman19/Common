# Buddy V3.2 → V3.5/R14 consumer contract — exact-source convergence V1

**Governing recovery parent:** [new Common #6](https://github.com/reallakshman19/Common/issues/6). **Integration nature:** DRAFT / READ_ONLY_REFERENCE / NOT_STAGE2_ADMITTED. No root Relay graph, lease, Local grant, DELP numerator or stage authority changes.

## Verified provider-object regression (GitHub API reads; 2026-10-09)

- `GET reallakshman19/Common/issues/4` → ISSUE (existing governance issue) and `/issues/6` → ISSUE (recovery parent).
- `GET reallakshman19/Common/issues/2` → **PULL_REQUEST** URL `/pull/2`, not a separate issue. Never label #2 an implementation issue or use the #2 number as a native issue-scoped Runner episode without a true provider-bound responsibility.
- `GET reallakshman19/Common/issues/889` and `/issues/890` → HTTP **404 NOT_FOUND**, while `GET reallaksh19/Common/issues/889` and `/issues/890` → actual historical ISSUE objects. Git SHA and numeric issue ID cannot substitute for exact repository and issue-kind readback.
- [Typed source golden](REPOSITORY_ISSUE_BINDING_PROVIDER_NEGATIVES_V1.json) and format-only unit oracle in `test_repository_issue_binding_contract.py` preserve these positive/negative observations. The fixture is an observed-snapshot record, **not** an authenticated runtime GET for any future dispatch, nor a Model B isolation witness. Even confirmed ISSUE objects (#4 governance, #6 recovery parent) have **dispatch_authorization: NOT_ASSESSED**; issue existence is necessary for binding but NEVER sufficient for Owner-approved responsibility or Runner launch.
- Earlier [PR #8](https://github.com/reallakshman19/Common/pull/8) duplicates the disabled four-path grant already proposed under [#4 / PR #7](https://github.com/reallakshman19/Common/pull/7). Preserve its unique P0 audit under [V32 recovery source audit](V32_BUDDY_RECOVERY_P0_GOVERNANCE_20261009.md) and do not maintain two competing grant IDs or treat two inactive drafts as approval.

## Source basis and compatibility

| Source owner | Exact inspected Git head | Consumer responsibility |
| --- | --- | --- |
| New Common [PR #2](https://github.com/reallakshman19/Common/pull/2) | `6255b759e20577c126c7b158e1c17ddc66bb80c7` | Native V3.2 immutable issue-scoped transactional Markdown, receipt digest, ordered Stage1 and Stage1 freeze **candidate** |
| New Common [PR #3](https://github.com/reallakshman19/Common/pull/3) | `d9f785394840840775775be81a526228edd3c00d` | V3.5 baseline-first reasoning, R14 source roles, complete technical narrative, four-view Stage2 reference |
| New Common [PR #11](https://github.com/reallakshman19/Common/pull/11) | `ae17843c48cefc9ece7166bb235e6a42af2bf70f` | Current-repo dispatch table structural repair, two-column positive/negative tests, V3.5 base-pinned frozen-tree guard |
| Historical Common [#889](https://github.com/reallaksh19/Common/issues/889) / [#890](https://github.com/reallaksh19/Common/issues/890) | Previous repository provider objects | HISTORICAL_ONLY; old GitHub issue numbers and PR review/Owner/credential identities do not migrate merely because commits do |

**One operational Markdown namespace:** `relay/CONTINUITY/episodes/ISSUE-<verified new-repo issue>/messages/TX.<issue>.<serial>-<STAGE>.md`, via native `PUBLISH_BUDDY_MARKDOWN`. `relay/BUDDY_RUNNER/` is a historical redirect. The Core1B episode examples are historical fixtures, not native transactional messages.

## Contract decisions and preserved fields

| Conflict / concern | Decision in this candidate | Falsifier / still required |
| --- | --- | --- |
| 21 shared Markdown paths across two independent PRs; several divergent R14 and handover texts | Preserve native #2 immutable publisher and adopt #3's **complete** `HANDOVER_TECHNICAL_V2` narrative, Stage2 typed fields, Owner decision, R14 role map and README. Retain #2's actual handover example, label it non-native | No second live handover/controller or implicit admission; verify consumer compatibility and exact source on final combined head |
| Historical issue number may look like new `ISSUE-<number>` | Dispatch template demands fresh provider GET of the **new repository issue** + observed ref/time, or `HOLD_REPOSITORY_IDENTITY`; old URL stays historical | Numeric TX and file SHA are **not** provider issue proof; external gate must reject old-repo-only issue even if publisher accepts syntax |
| R14 graph/session/source/Owner and evidence claims | Keep `PLAN_GRAPH_REVISION`, `SESSION_SOURCE_COMMIT`, `CODE_CANDIDATE_HEAD`, tested HEAD, old/new provider URL, actor claim and actual authenticated grant as **distinct trust classes** | STOP_CLAIMED, reviewer CLAIMED_ACCEPTED and R12→DELP read-only quarantine cannot become lease or evidence acceptance |
| `STAGE1_FREEZE_CANDIDATE` exists in native command | Only a locally validated predecessor digest chain with `Isolation verdict: NOT_ATTESTED` | Real separate B session, P01 allow and N01–N06 denied probes, externally authenticated final freeze still NOT_RUN |
| Technical handover when Agent A exists vs disappears | One self-contained source-verified `HANDOVER_TECHNICAL_V2` narrative with actual caller/consumer path, before/after, goldens/tested SHA/failed checks, original task-start separately from research cutoff, unknowns and next safe action; cite native `HANDOVER_CONTEXT` | On crash mark A reasoning UNKNOWN; narrative cannot simulate A-authored speech or transfer writer |
| Stage2 / Owner / writer | Same B reconciles four views **only after** external final freeze and admitted disclosure; Owner and Local writer grants separate | Native Buddy Stage1 command must reject Stage2/technical handover as native published stages; old-A write fencing not replaced by Markdown |
| Protected V3.2 code paths | Do not edit frozen source. The #2 implementation is still against base lacking four exact-path grant | [canonical governance issue #4](https://github.com/reallakshman19/Common/issues/4) / [disabled proposal PR #7](https://github.com/reallakshman19/Common/pull/7) entry remains `owner_authorized: false`; current parent #2 code may not merge |

## Complete V3.5 guidance retained without a second live transport

The source-pinned V3.5 `SKILL.md` and all seven `runner/*.md` files from PR #3's inspected `d9f785394840840775775be81a526228edd3c00d` were imported as role-specific thinking/dispatch/manual acceptance guidance. They are **instructional consumers** of the single `relay/CONTINUITY` message record, not new Runner launch engines, state/lease files or alternative issue-scoped active paths. The PR #3 complete V3.5 technical report example also remains controller/reviewer-only and cannot be made accessible to a truly blind Stage1 B.

**Latest source refinement:** PR #3 later advanced to `bf4af494505cca6b655fa9163d6731ed2b1ad160`, adding `HANDOVER_TECHNICAL_V2` classifications for per-step SKIPPED vs executed tests, inherited missing-workflow baseline RED, and ZERO_STEPS/NO_RUNNER. This candidate incorporates that exact template blob and the V2 full engineering example as further source-attested disclosure-only content, without changing the native transaction or claiming a fresh independent Runner.

## Stable GitHub provider identity versus Owner/Local scope

At source review, GitHub returned repo `reallakshman19/Common` with stable repository ID `1412133785`, new ISSUE #4 object ID `5782308813`, new ISSUE #6 object ID `5782315682`, and PR #2 issue-endpoint object ID `5782250162` with `pull_request` present. A provider-issued object identity is not just `owner/repo#number`. The dispatch request, controller-only preflight and release contract now demand the controller's own fresh repository+issue GET at use time, matching stable IDs, exact URL, kind and response `repository_url`, **then a separate Owner/Local responsibility scope decision**. This is one Markdown contract and its negative regression suite, not an authenticated agent launcher. Dated [fixture](REPOSITORY_ISSUE_BINDING_PROVIDER_NEGATIVES_V1.json) is only an observed snapshot; it cannot self-attest runtime authority.

## Real acceptance gates vs structural checks

**This candidate's executable source-level regressions** inspect the actual PR #2 `transactionlib.py` stage allowlist and publication path, compare the V3.5 dispatch identity + handover + Stage2 + Owner decision contracts, and negatively mutate missing provider binding and the complete technical handover requirement. These tests prove *contract consistency only*. They do not test real browser behavior, authentic provider issue GET at dispatch time, a fresh isolated B, future Owner decision or old A credential revocation.

**Next genuine operational acceptance:** separately approved frozen-path base amendment → rebuild PR #2 against the authorized base → independently gated P01 allowed historical source and N01–N06 denied reads → actual B Part A/B source-grounded artifact + controller freeze → native A technical handover + Stage2 source verification → fenced exclusive writer admission and first exact-head engineering TASK_EVIDENCE.

**STOP:** Do not merge PR #2 because this stacked document or CI runs pass; do not merge PR #3 independently without reconciling overlapping Markdown. Do not call this a real Runner exercise.
