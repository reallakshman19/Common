# v3.6 Issue Continuity Chain v1

**Governing plan:** [Common #400](https://github.com/reallakshman19/Common/issues/400). **Accepted lifecycle:** [Common #341](https://github.com/reallakshman19/Common/issues/341). **Zero-exit adjacency:** [ONB #391](https://github.com/reallakshman19/Common/issues/391). **Owner example:** [3D_Converters #274](https://github.com/reallakshman19/3D_Converters/issues/274).

This is an ADDITIVE native v3.6 contract. It imports NO v3.5/DELP runtime, changes NO v3.6 evidence/scoreboard/label/publisher code, and does not make BuddyRunner, two-pass and three-pass one protocol. It preserves accepted O1–O5.

## Why: source trace after ten agents

An issue must be an engineering evidence *spine*, not a stream of activity counts: original Owner WHY, technical conversation amendments and source, actual original input/golden, benchmark and measured acceptance, causal code path and implementation crux, every meaningful agent contribution, adopted and parked ideas and their decision rationale, current problems and clear next verification. A successor with only the issue URL should follow links and independently reconstruct; the outgoing final chat LOG is optional.

A GitHub issue **cannot recover unpublished/private chat**. Captured Owner-direct text is initially SOURCE_REPORTED until provider actor/source verification. Never turn an assistant quotation or older PR into Owner authority. Redact or explicitly keep private user files; do not auto-export conversation history.

## Mandatory issue chain categories (11)

| Key | Content or explicit missing reason |
|---|---|
| ROOT_OWNER_INTENT | Human original problem and WHY, durable attributed source |
| OWNER_AMENDMENTS | Later Owner-provided technical conversations and effective corrections |
| ORIGINAL_INPUT | Immutable original fixture Git object/hash and format |
| COMPLETE_GOLDEN | Full expected output, independent oracle coverage (partial != full) |
| MEASURED_BENCHMARK | Original real workload, expected thresholds, measured run, code SHA |
| SOURCE_IMPLEMENTATION_CRUX | Actual user input → UI/adapter/Worker/function → output and ownership |
| AGENT_CONTRIBUTIONS | Agent 2/3/10 outputs, commits, source/CI, superseded alternatives |
| DECISION_AND_PARKED_IDEAS | KEEP, PROPOSED, PARKED, ADOPTED_REPORTED, REJECTED_REPORTED, revisit triggers |
| KNOWN_FAILURES | Current known issues, counterexamples, causal analysis |
| SELECTED_NEXT_VERIFICATION | Current selected frontier, exact source/fixture/test and stop conditions |
| TECHNICAL_HANDOVER | One 12-section causal handover, Handover Master/Buddy receipt/source refs |

**Two denominators:** accounting_coverage_percent=100 means all 11 categories are recorded, even where UNKNOWN is explicitly stated. verified_coverage_percent is ZERO for this C1 tool because it makes no external requests or source attestations. That is NOT 100% reliable engineering evidence or Owner approval. Future C2/C3 attest bytes and semantics separately.

## Exactly what C1 implements

The current additive scripts/issue_chain_v36.py validates reported JSON from an owning issue, strict source identities and roles, public GitHub URLs, source-cut SHA40 and optional reported SHA256, exact categories, unique historical record IDs, backward-only references (no orphan/cycles), parent and cross-repository allowlisting, explicit UNKNOWN reason. It rejects private notes in PUBLIC reports and fake direct-Owner authentication. A protected adoption claim needs a **reported decision link** but the checker never promotes it into authenticated Owner approval. Parked ideas must state the revisit trigger. Every record must be included in the index.

It emits STRUCTURALLY_ACCOUNTED_NOT_SOURCE_VERIFIED with permission_to_write=false, may_change_titles_or_labels=false, may_merge_or_release=false. There is no network client, writer, workflow scheduler or acceptance engine.

## Source example: 3D_Converters #274 (reported facts, not certification)

The direct Owner request was to preserve working Weight Match logic and reconnect to older robust UI via small adapters. Reported in the engineering discussion: 41 branches, 423 physical components and 2961 FactRecords = 7 per physical component, but at the cited observation ZERO accepted Match-1 and Final masses, 423 unresolved. The legacy DOM-only checklist changed visible cells without updating canonical readiness and reported 28/28 regex identity while newer context showed 41/41. Exact served JS asset SHA has NOT been proved. Native CII remains separately held for Final→engine transfer, native physical-slot consumption and release authority.

This has critical ambiguity: **complete Facts ≠ accepted weights ≠ valid native CII**. The known G0–G7 proposal and PR #281 are planning/draft observations, not adopted release decisions. The example intentionally declares unknown Owner amendment chronology, original full input file, full owner golden and actual-JSON performance benchmark. An agent ten cannot silently replace these with synthetic files or inferred thresholds.

## Interlink with existing native phase boundaries

- Handover Master is the **single invocation**, choosing actual v3.6 vs standalone and approved version.
- BuddyRunner 1a receives only approved source/intake pointers and HOLD. Buddy 1b independently reconstructs original issue, source, fixture and history, proposes KEEP or IMPROVE. Buddy 2 reconciles **one** investigation, records reported adopted/parked decisions with links, writes the existing twelve-section handover once, then closes. One Xb→Y intervention is not another stage.
- v3.6 two-pass: independent first baseline is not contaminated with the predecessor solution; task-aware comparison comes later. v3.6 three-pass keeps the existing independent source/falsifier → implementation → validation division; no extra prompts added.
- Zero-exit ONB WP5 compiles the twelve-section report and BLOCKED verdict from issue/provider-linked context. A final predecessor LOG enriches but is never mandatory.

No disclosure of private source or authored solution into a deliberately blind stage. Owner approval, acceptance and output publication remain independent.

## Smart issue/PR title and dynamic label design (C4 pending)

V3.6 already has publisher_v36.py, currently projecting issue/PR titles from real provider evidence, CAS and GET readback. Do not introduce a second title writer. Current parent title is hard-coded with LAB; avoid forcing this into production. Preserve previously accepted lab prefix behavior until an explicitly authorized migration is tested.

Required future extension: safely strip/reapply managed prefixes while preserving the human title, clamp length, detect title drift and wrong PR attribution, and project real evidence E and chainage accounting C/verified V as DIFFERENT counters. Avoid acceptance from E2/2 or accounted 11/11. Dynamic GitHub state labels should be projected from verified source and explicit privileges and must never overwrite arbitrary human labels. Owner sticky label relay/AIM/<WORK>.yaml remains immutable source authority, NEVER a generated topic status label. C1 deliberately changes NO titles or labels.

## CLI

~~~sh
python3 skills/engineering-pr-delivery-v3.6/scripts/issue_chain_v36.py --input skills/engineering-pr-delivery-v3.6/tests/fixtures/issue-chain-274-reported.json
python3 -m unittest discover -s skills/engineering-pr-delivery-v3.6/tests -p 'test_issue_chain_v36.py' -v
~~~

Example status: 11 accounted, 7 source-reported, 4 UNKNOWN, ZERO authenticated/attested/accepted; merge/release HOLD. Avoid using example report as an Owner fixture or benchmark.

## Remaining gates

C2 live actor and original Git blob custody; C3 provider issue spine and cold source/12-section crux; C4 smart title/dynamic label safe opt-in and exact lab regression; C5 Buddy/multipass stage-filtered views; C6 ten-agent cold exercise using #274 and another project; C7 independent semantic and Owner acceptance. Cross-repository actions and writes require explicit scope and authorization. The full Owner plan and cross-project evidence are in #400.

A green C1 unit test means only that **the reporting contract fails closed**, never that the underlying reported source claims are true.
