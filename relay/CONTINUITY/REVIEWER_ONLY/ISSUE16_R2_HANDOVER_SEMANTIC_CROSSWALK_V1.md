# ISSUE #16 / R2 — full technical handover semantic compatibility decision (12-to-10 map)

**Role:** reviewer-only source-verified acceptance crosswalk, not a Stage 1 input or Owner-authorized schema migration. Original [historical #890 WP3](https://github.com/reallaksh19/Common/issues/890) requires a **single source-complete technical handover**, not a particular heading count. New [#16](https://github.com/reallakshman19/Common/issues/16) owns reviewer acceptance; separate [#1 / PR #3](https://github.com/reallakshman19/Common/pull/3) and [PR #14](https://github.com/reallakshman19/Common/pull/14) own R14 prompt/consumer changes.

## Verified competing candidates and exact consumers

- **Merged main** `reallakshman19/Common@3afd78e0635957e496cfef99f6727590001f94cd`, `relay/CONTINUITY/TEMPLATES/TECHNICAL_HANDOVER.md` blob `a907295e31dbfc22b9af3a425c53bd9ebb48cc51` is `HANDOVER_TECHNICAL_V2`, **12 numbered substantive sections**, merged by [PR #13](https://github.com/reallakshman19/Common/pull/13). Its own authoring guidance explicitly disallows a generic process plan in place of engineering facts.
- **Draft PR #14** `@40956b99c646b32ae35738af20220ca289bbcb52`, same path, blob `af08d1b2e2fa543a1232b7a685d54020ddf48ef7` is ALSO `HANDOVER_TECHNICAL_V2` but has an identity/readout section plus **10 numbered sections**. It additionally specifies distinct plan graph, session, source candidate and tested-head roles; rich CI failure/skipped evidence; detailed causal delta and rollback; native handover is non-authoritative.
- **Direct downstream Stage2 reader** at PR #14 `skills/engineering-pr-delivery-v3.5/runner/STAGE2_SOURCE_RECONCILIATION.md`, blob `c817af0052c64c45654bb715a5c1d81a68f041b2`, links this template and requires a **filled, source-verifiable complete report** after external Stage1 freeze. `STATIC_PACKET_FORMATS.md` blob `2f12aeae12740b23ce08c697638060446a57bfa5` also links the report and says its table is *not* the handover deliverable. The Stage1 prompt has no such links; one GitHub path name or README is not a security gate.

## One semantic contract — actual twelve dimensions, not a quota on headings

| Required engineering information dimension already landed in main V2 | Main numbered section | Corresponding draft PR #14 location | Must remain explicit after reconciliation |
| --- | --- | --- | --- |
| H01 full technical situation: what works, deployability, remaining gap | 1 | Identity/readout summary + 7 | One self-contained technical conclusion grounded in current source, not PR status/progress |
| H02 original Owner defect and WHY, unchanged acceptance/constraints | 2 | 1 | Preserve direct OWNER vs MIRROR/CLAIM/UNKNOWN grading and real input/output seam |
| H03 true A start, historical source cutoff, migrated repo, current candidate, **each tested SHA** | 3 | 4 + identity/readout table | Keep old/new **GitHub object** identities, graph/session/current/tested heads and migration limitations distinct |
| H04 HOW: end-to-end input → producer → native transaction/transform → downstream consumer → output, errors and rollback | 4 | 3 | Actual symbol/call edges, shapes, writer/source authority, negative path, deployment when applicable |
| H05 exact BEFORE/AFTER source delta and WHY/alternatives | 5 | 2 | File/function and direct/indirect consumers, immutable diff, rejected approach, version compatibility |
| H06 real positive and negative inputs, fixtures/goldens and user-visible result | 6 | 3 + 5 | Original vs synthetic provenance, hash/expected output, browser `NOT_RUN` rather than invented success |
| H07 tests, source currentness, CI steps, performance and reproduction | 7 | 5 | Test command, environment, actual totals, exact tested SHA vs latest HEAD, skipped steps, baseline-failure classification, authentic cost metrics only |
| H08 material defects, negative knowledge, root cause and Owner decisions | 8 | 6 | Reproduction/impact, attempted fixes, OPEN/BLOCKED/UNKNOWN; avoid repeating disproven approach |
| H09 native Relay, Local writer/lease, pending calls and actual custody | 9 | 8 | Authenticated provider/native `HANDOVER_CONTEXT`, in-flight writes, actual writer denial or UNKNOWN; no new authority in Markdown |
| H10 exact starting checkout, first safe command, first legitimate bounded unit, STOP conditions | 10 | 9 | Exact HEAD/readable locus, reproduced failure, test+negative, permit-to-write separately checked |
| H11 original **three source-grounded successor questions where instructed**, with falsifiers | 11 | 10 | Three when original contract requires, each tied to real symbols, anti-shortcut and test; preserve frozen B's existing questions separately |
| H12 linked evidence index and unsupported-claim boundary | 12 | 10 + author self-check | Direct authoritative GitHub/source/test/browser refs, native HANDOVER_CONTEXT or UNKNOWN, candid NOT_RUN and limitations |

**Assessment:** the 10-section draft contains plausible locations for **all twelve information classes** and adds valuable R14/CI provenance. Its different numbering **alone is not proof of a lost semantic requirement**. Equally, template text saying to fill a requirement is not evidence that any *completed technical report* fulfilled it. `FORMAT_COVERAGE=SOURCE_MAPPED`; `REAL_AGENT_A_REPORT=NOT_RUN`; `STAGE2_QUALIFICATION=NOT_RUN`.

## The actual incompatibility to resolve (not by taking 'ours' or 'theirs')

Both revisions use the same identifier **HANDOVER_TECHNICAL_V2** but have changed structural layout and section numbering. Existing tests on [PR #19](https://github.com/reallakshman19/Common/pull/19) currently safeguard the twelve landed numbered sections, rejecting the ten-section replacement by design. This is an intentional pre-migration guard, **not a verdict that draft PR #14 is technically inferior**. Before modifying or removing that guard:

1. Have the R14/PR #14 owner declare **one canonical representation** (retain 12 sections and add R14 fields, or approve semantic-preserving V2 profile/migration with a new explicit format marker). Do not silently keep the same public version identifier with incompatible section expectations.
2. Update the **same** downstream Stage2 reader, static packet index, operator/reviewer examples and contract test to consume the chosen version. Preserve the twelve **semantic** H01–H12 expectations, not invented filler sections or mandatory novelty quotas.
3. Test positive filled report with actual source/function/consumer/test-head facts and negative variants that remove each H01–H12 dimension; run old-vs-new side-by-side on the same source task to disprove information loss. A keyword-only template linter does not certify a report is source-correct.
4. Verify stage disclosure/freeze, native `PLAN_HANDOVER`/`HANDOVER_CONTEXT` referencing, no shadow Local/DELP/lease, and actual downstream owner/runner consumption. Static documents cannot enforce GitHub path access.
5. Rebase stacked PR #14 onto the actual native PR #2/current main, repeat relevant tests at new exact head, and record Owner/Local acceptance for any governed material changes before merge. Preserve protected V3.2 fork boundaries.

## Independent source and CI findings at PR #19 exact head

- [Focused CI run #37984968123](https://github.com/reallakshman19/Common/actions/runs/37984968123) completed **18/18 PASS** at `7848a0242bc8580475fcc30dff02a4f62a799573` (7 handover-template regression + 11 original Stage1 byte/heading tests; actual executed log and HEAD inspected). This proves static source contracts at that SHA only; not an independent B session or a tested native publisher.
- Local v1.1, DELP and coordinator jobs GREEN. V3.2 workflow GREEN but path gate **skipped** its V3.2 regression steps, so no native ingress proof. V3.1 foundation RED: 274 tests, 6 FileNotFoundErrors because inherited `.github/workflows/engineering-pr-delivery-v2.5.yml` and `.github/workflows/engineering-pr-delivery-v3.yml` are absent; unrelated to the five issue16 source artifacts but an honest red required check.
- PR #14 Stage1 blob `5bcca08960e0a7800173ff24aaffa5f334b62912` requires B-authored files headed `# STAGE1_BASELINE` and `# STAGE1_PLAN`; PR #2's `transactionlib.py` blob `07368987c1156fb687a76139150dd58556c92269` only checks generic `# ` heading. That **native runtime** repair belongs to protected PR #2 and its Owner grant #4/#7, not this PR.

## Decision / scope / next action

**R2 decision:** `INFORMATION_CLASSES_RECONCILED / FORMAT_MIGRATION_NOT_APPROVED / ACTUAL_REPORT_NOT_TESTED / STAGE2_NOT_RUN`. A draft PR can use ten headings **if** its source-grounded H01–H12 report remains actually complete and all consumers deliberately migrate; neither diagram shape alone nor two CI PASS strings can authorize release. Retain PR #19's protective 12-section test until the integration contract and downstream consumers are explicitly versioned and tested. No rewrite of either competing template on this issue #16 branch.

Next bounded unit: integration owner reconciles one canonical report and actual consumer test; #16 performs source-current evidence qualification and the genuine externally isolated B experiment only after real read boundaries, original historical inputs and native permissions are proven. All actual execution authority remains Owner/Local; no PR/Markdown grants a writer.
