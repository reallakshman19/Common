# v3.6 Issue Continuity Chain v1

**Original design source:** [Common #400](https://github.com/reallakshman19/Common/issues/400). **Admission authority and scope:** [Common #409](https://github.com/reallakshman19/Common/issues/409) (Owner-approved #401 admission; no general project activation or write authority). **Accepted lifecycle:** [Common #341](https://github.com/reallakshman19/Common/issues/341). **Zero-exit adjacency:** [ONB #391](https://github.com/reallakshman19/Common/issues/391). **Illustrative reported source:** [3D_Converters #274](https://github.com/reallakshman19/3D_Converters/issues/274) (constructed example, not an attested real-run fixture).

This is an ADDITIVE native v3.6 contract. It imports NO v3.5/DELP runtime, changes NO v3.6 evidence/scoreboard/label/publisher code, and does not make BuddyRunner, two-pass and three-pass one protocol. It preserves accepted O1–O5.

## Why: source trace after ten agents

An issue must be an engineering evidence *spine*, not a stream of activity counts: original Owner WHY, technical conversation amendments and source, actual original input/golden, benchmark and measured acceptance, causal code path and implementation crux, every meaningful agent contribution, adopted and parked ideas and their decision rationale, current problems and clear next verification. A successor with only the issue URL should follow links and independently reconstruct; the native v3.6 outgoing terminal LOG remains mandatory; a cold successor must nevertheless report honestly when that LOG was not captured.

A GitHub issue **cannot recover unpublished/private chat**. Captured Owner-direct text is always **OWNER_DIRECT_REPORTED** in this validator, never authenticated merely by a source-class string; later external provider actor/source verification is not implemented by C1. Never turn an assistant quotation or older PR into Owner authority. Redact or explicitly keep private user files; do not auto-export conversation history.

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

**Two denominators:** `accounting_coverage_percent` is calculated as **validated mandatory category states / 11 × 100**, including `UNKNOWN` and `NOT_APPLICABLE`. Because this strict schema rejects absent categories, any *successful* validation necessarily yields **100% structural accounting**. A rejected/incomplete report produces `CHAINAGE_BLOCKED`, not partial approved progress. `verified_coverage_percent` remains ZERO: this offline C1 tool fetches no external sources and attests no bytes. Neither figure measures reliable engineering proof, truth or Owner approval. C2/C3 would need separate scoped, authenticated readers.

## Exactly what C1 implements

The additive `scripts/issue_chain_v36.py` is a **purely offline structural checker** over caller-supplied JSON. It checks:
- All eleven mandatory categories are present and ordered; each `PRESENT_REPORTED` category cites at least one record of its **permitted kind** (for example `ROOT_OWNER_INTENT→OWNER_INPUT`, `ORIGINAL_INPUT→FIXTURE`, `DECISION_AND_PARKED_IDEAS→IDEA/DECISION`). Explicit `UNKNOWN` or `NOT_APPLICABLE` states have reasons and no claimed evidence. This is *record-kind consistency*, not an attestation of what a record represents.
- Records have syntactically unique IDs and `related_ids` that point to **previously listed** records. This prevents forward links and cycles in the declared array, **not** falsified timestamps, event-order provenance, actual historic chronology, changed source age or staleness. There is no timestamp field, freshness comparison or provider chronology reconstruction.
- Repository names and SHA formats are checked for shape. The apparent `permitted_repos` set is **derived solely from untrusted `observed_main` fields inside the submitted JSON**. Thus the validator prevents undeclared cross-repository links *relative to that self-declared set*, but it is **not a trusted, externally approved repository allowlist**. A real approval gate must bind repository/scope using independent Owner/provider credentials and explicit authority before trusting any links.
- GitHub URLs are syntax-filtered; `visibility=PUBLIC` is a **claim made by the input**, not verification that a link is actually public or that private content was safely redacted. `source_revision` SHA-40 and optional `source_sha256` SHA-64 are **regex shape checks only**; no Git object, document, byte content or actual current head is fetched or hashed. A fabricated but well-formed SHA passes this layer. `UNKNOWN` event source class cannot be misused as an evidenced event.
- `ADOPTED_REPORTED` and `REJECTED_REPORTED` need a syntactically valid linked reported decision; non-decision kinds cannot be adopted/rejected, and a `PARKED` item requires a revisit trigger. These are source-*reported* dispositions and never authenticated Owner decisions. All declared records must appear in a compatible reported category or validation fails.

There is **no trusted cross-repository scope, real time-order verification, staleness detection, public/private inspection, actual SHA comparison, or independent semantic acceptance** in this C1 implementation.

It emits STRUCTURALLY_ACCOUNTED_NOT_SOURCE_VERIFIED with permission_to_write=false, may_change_titles_or_labels=false, may_merge_or_release=false. There is no network client, writer, workflow scheduler or acceptance engine.

## Constructed reported-only illustration referencing 3D_Converters #274 (not an authenticated fixture)

The source-reported Owner request in this constructed illustration was to preserve working Weight Match logic and reconnect to older robust UI via small adapters. Reported in the engineering discussion: 41 branches, 423 physical components and 2961 FactRecords = 7 per physical component, but at the cited observation ZERO accepted Match-1 and Final masses, 423 unresolved. The legacy DOM-only checklist changed visible cells without updating canonical readiness and reported 28/28 regex identity while newer context showed 41/41. Exact served JS asset SHA has NOT been proved. Native CII remains separately held for Final→engine transfer, native physical-slot consumption and release authority.

This has critical ambiguity: **complete Facts ≠ accepted weights ≠ valid native CII**. The known G0–G7 proposal and PR #281 are planning/draft observations, not adopted release decisions. The **locally authored reported-only JSON illustration** intentionally declares unknown Owner amendment chronology, original full input file, full Owner golden and actual-JSON performance benchmark. It is neither a synthetic golden/oracle nor a provider-verified real fixture; its construction and every retained report claim remain unverified without separate source retrieval. An agent ten cannot silently replace these with synthetic files or inferred thresholds.

## Informative references to other independently governed workflows (NON-NORMATIVE)

**This section is explanatory navigation ONLY**. It does not define, amend, activate, relax, or replace any Handover Master, BuddyRunner, two-pass, three-pass or zero-exit protocol. For actions and phase isolation, read the **actual selected native skill and controlling approved plan/version**. C1 neither invokes these tools nor grants their permissions.

- Handover Master selection is governed by its own current decision guide, **not** by this C1 document. Do not infer agent authority or role from this mention.
- BuddyRunner's actual versioned 1a HOLD → independent 1b → one predecessor 2 and optional separately-authorized Xb→Y use their own source and stage rules. The sequence here is illustrative, not an instruction to conduct or auto-close a handover.
- Native v3.6 two-pass and three-pass generators are distinct, stage-isolated workflows under their own source contract; this illustration must not contaminate an independent/blind first pass.
- Zero-exit ONB has a separate source-verification contract. C1 cannot satisfy it by an accounted 11/11 JSON report. Native v3.6 terminal LOG remains mandatory; a cold successor records a missing LOG as missing, not fabricated.

The C1 validator publishes nothing, has no private-chat access and confers no new acceptance, output release or provider write authority.

## Existing smart titles and unadmitted dynamic-label writes

The current v3.6 native `publisher_v36.py` (ECO-04/05) is the **sole title/managed-scoreboard writer**. It already has non-lab display selection, PR-specific E, attention precedence, human-title preservation, explicit target/surface restrictions, provider GET preflight and GET readback. That is **NOT** provider-atomic CAS. Native evidence, V/source attestation and Owner acceptance remain distinct; an accounted 11/11 continuity chain cannot upgrade native E or grant approval.

C1 adds only the reported/unknown chain contract and its pure validator. It **does not** call the publisher, turn on `scoreboard_v36.py` accounting integration, change titles or dynamic GitHub labels, alter the sticky Owner `relay/AIM/<WORK>.yaml`, change source cursors, or authorize a live write. A prospective state-label feature remains unadmitted and needs separate scope, source authority, privacy review, exact-target consent and readback protection of human labels. There is no global v3.6 rollout from admitting C1.


## CLI

~~~sh
python3 skills/engineering-pr-delivery-v3.6/scripts/issue_chain_v36.py --input skills/engineering-pr-delivery-v3.6/tests/fixtures/issue-chain-274-reported.json
python3 -m unittest discover -s skills/engineering-pr-delivery-v3.6/tests -p 'test_issue_chain_v36.py' -v
~~~

Illustrative local output: 11 structurally accounted, 7 PRESENT_REPORTED, 4 UNKNOWN, ZERO independently authenticated/attested/accepted; merge/release HOLD. The JSON arrangement was constructed from reported #274 information and does not establish actual fixture or benchmark custody.

## Remaining gates

C2 live actor and original Git blob custody; C3 provider issue spine and cold source/12-section crux; C4 future dynamic-label safe opt-in and independently reviewed producer/consumer integration (existing ECO-04/05 title publisher is already present); C5 Buddy/multipass stage-filtered views; C6 ten-agent cold exercise using #274 and another project; C7 independent semantic and Owner acceptance. Cross-repository actions and writes require explicit scope and authorization. The full Owner plan and cross-project evidence are in #400.

A green C1 unit test means only that **the reporting contract fails closed**, never that the underlying reported source claims are true.
