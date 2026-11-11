---
name: qrt-blueprint-mapping-agent
description: Map a source-traced Grade 9 mathematics question to its genuine QRT cognitive demand and difficulty, reuse registered Core blueprints and Owner golden comparators, render actual native learner pages, falsify protected-work and transfer leaks, and produce an unsigned review-ready evidence record. No self-adjudicated academic or Owner acceptance.
---

# QRT Blueprint Mapping Agent — evidence-first, native-only

## Purpose / trigger

Use for: "map this question to QRT", "select the right blueprint", "build Core pages from an existing fixture", "benchmark against golden", "create a source-safe QRT candidate", "why did this Core page not match its golden?", or "audit question → Core1A → Core2A → Core2B progression."

**The reusable insight:** **classify the actual learner decision before choosing hints, visuals, Core pages or blueprints.** Separate **QRT semantics** from **blueprint structure**, and distinguish **golden technique** from **source-specific content**. Begin with the question, not page generation.

This skill is a reusable **instruction package**, not a running autonomous agent, user-rights license, signed mathematics reviewer, independent person or Owner approval. It can be loaded by a compatible agent/workspace, and may run actual repo tools only when the host has access and the work's authorization is clear.

## Required project truth; reconstruct afresh, pin exact refs

For Grade9v3.5, read these **actual repo files at the chosen candidate SHA** before any authoring. Do not assume that the references below are still current after later revisions:

1. `docs/method/QUESTION-REVIEW-MATRIX.md`: QRT semantic meanings, seven primaries, four bands, five component scores, X/Y/Z/W and H1–H3 / S1–S3 / P1–P3 / M1–M3.
2. `Shared/quality/question-demand-matrix.v1.json`; `Shared/vocabularies/cognitive-demand.v1.json`; `Mathematics/adapter/DemandReview.json` where present; `Shared/tools/question_review_matrix.py`. Generated `question-demand-templates.v1.json` is a checked projection, **not an editable authority**.
3. `Shared/web/interactive-page-blueprints.v1.json` (sole registered page blueprint catalog, current role versions and required slot/component order); `Shared/tools/render_core.py` (sole native renderer); `Shared/library/package.schema.json`, product manifest schema, applicable gates and current repo instructions.
4. An **Owner-designated immutable golden** and its `snapshot-lock.json`, **only if there is a valid comparator for the selected Core role/question**. Example `golden/units/G-IMO-G9-FIVE-CORE-20261012/` is a five-role, originally TEST-content golden; its bytes are not universal page HTML. Never mutate frozen golden snapshots.
5. Source-record eligibility / provenance, actual original question assets and publication rights; present learner state if available. Issue #183 authentic/private Q003 is a **different** source from seven wholly authored #191/#205 TEST examples.

For Common engineering self-review, use `skills/common-reviewer-protocol-v1.0/SKILL.md` plus the **pinned project-specific protocol**. The same agent reviewing its own work must emit `SELF_REVIEW; PRINCIPAL_INDEPENDENCE=NONE`, never an independent verdict.

**Source/rights fail-closed:** exact original text, options, diagram, exam attribution and authentic Core2 require authoritative source bytes and eligible rights. If unavailable, classify as `SOURCE_UNVERIFIED` or `AUTHORED_TEST`; no silent reconstruction, publication, official past-paper claim or real-source Core2 admission. A mathematical result is not publication permission.

## Execution order — DO NOT reorder

### 0. Freeze task identity, scope and authority

Record issue, intended outcome, current candidate and stacked base **full 40-character SHAs**, Owner decisions/constraints, source rights, output mode (`ANALYZE_ONLY | DRAFT_TEST_BUILD | REVIEW_ONLY`) and excluded publication routes. Work in a new isolated draft branch only if authorized; never write to main, merge, mark approved or alter relay state without authority. If the source is protected/private, never move it to public GitHub artifacts.

### 1. Analyse the **exact source question** and independently solve it

Transcribe from the true source without "fixing" it silently. Record source SHA/provenance/eligibility, all givens/units/options/figures, domain constraints, *primary* worked solution, independent numerical/proof oracle, misconception candidates and a **changed-condition countercase**. Confirm any false/missing/ambiguous source before going further. Treat arithmetic oracle correctness and learner cognitively appropriate presentation as **separate** results.

### 2. Resolve **primary QRT cognitive demand** and D band BEFORE Core authoring

Select the primary demand by the **decisive unaided learner act**, not a verb in the stem, labels, course, topic, or hint count:

- `RETRIEVE`: select/reconstruct fact, property, category, unit or condition.
- `EXPLAIN`: explain why a relation/pattern holds.
- `APPLY`: execute a known relation/procedure under its conditions.
- `MODEL`: choose/formulate the governing variables, constraints, model or method.
- `REPRESENT`: faithfully translate mathematical meaning across representations.
- `SYNTHESIZE`: coordinate dependent ideas/steps when route choice is substantive.
- `JUSTIFY`: establish a conclusion using valid warrants/evidence.

Record strongest **competing demand**, a concrete falsifier, the expected protected step **W**, and what the stem ALREADY gives. If `MODEL` stem chooses `x`, do not claim W includes variable-category selection. If `RETRIEVE` stem says "apply the Pythagorean relation and calculate," independently question whether APPLY dominates. A mixed question gets **one** primary, with explicit secondary tags.

Use the existing five canonical difficulty components: `concept_model_selection`, `representation_translation`, `reasoning_chain_length`, `algebra_computational_load`, `trap_exception_sensitivity`; cite concrete evidence for each value under current project rules. Challenge D1 vs D2 vs D3 vs D4. Specifically D2 needs **a short connection/choice + execution**, not automatic D2 because two calculations appear. Record X (what turns on), Y (learner-demonstrated relevant bridge), Z (crux), W (protected decisive move); if no actual learner profile exists, mark Y **HYPOTHETICAL/NOT_OBSERVED** rather than fabricate prior mastery. QRT resolver `resolve` and subject adapter supply a **draft worksheet**, not an accepted cell.

**Stop pre-render** if the primary demand is contradictory, mathematically false, source-uncertain, or the W contract is already substantially supplied. Output a revision/reclassification proposal rather than generating flawed five-role packages.

### 3. Pick registered blueprints; map each Core role to the SAME crux

Use `Shared/web/interactive-page-blueprints.v1.json` active role IDs and versions, no guessed IDs. Do **not** create one blueprint per question, one per QRT cell, or new global Core2/Core1A for a cosmetic mismatch.

| Role | Learner job and protected boundary |
| --- | --- |
| **CORE2** (when eligible) | Authentic source attempt: faithful wording/choices/figures and attempt-first access; private/original source requires explicit rights. Do not fabricate it from an authored TEST problem. |
| **CORE2A** | Supported new attempt: H1 clarifies X, H2 connects to held Y; **H3 available only after a nonblank learner attempt**. Precommit text/ARIA/SVG cannot supply W or answer. The post-attempt hint opens Z; the learner still does W. |
| **CORE1A** | Teach the *underlying stable construction* fully, with its own independently new exit/changed question. Do not copy learner-specific W as a universal fact or give away Core2 attempt. |
| **CORE1B** | Learner reconstructs the core reasoning and independently faces a changed-boundary/exception; validate blank-blocking and fresh attempt. |
| **CORE1** | Orientation / choice of relevant mathematical terrain without solving the main assessed W. |
| **CORE2B** | Transfer: a genuinely changed condition, invariant, representation, feasibility or countercase requiring **new learner commitment**, not number substitution; protect `transfer.protected_move_ref` when present. |

Role count follows **actual authorized manifest**. #201's seven authored D2 TEST examples have five roles `CORE1, CORE1A, CORE1B, CORE2A, CORE2B`, with `selection.core2=[]`. Do **not** generalize that absence to genuine Core2 source-bearing work. Keep source, package references, manifest and selection roles traceable.

Before writing learner content, create a role-mapping table: `role → current blueprint ID/version → intended learner act → allowed disclosure → protected W → independent exit/transfer → acceptance oracle`.

### 4. Generate only **native renderer** outputs

Create/reuse valid source package and product manifest; run the **repository's actual commands**, including:

```sh
python Shared/tools/question_review_matrix.py check
python Shared/tools/question_review_matrix.py write --check
python Shared/tools/render_core.py gaps --manifest TEST/products/<exact>.manifest.json
python Shared/tools/render_core.py build --manifest TEST/products/<exact>.manifest.json --out build/<task>/native --draft --reference
```

Treat this as an **illustrative command pattern**; confirm actual CLI flags at pinned renderer SHA. Inspect `render-receipt.json`, page SHA256, role selection, missing required fields and reference-depth gaps. Never count hand-coded, composer-made or screen-only mock HTML as a native Core page; no shared renderer/blueprint changes unless a reproduced structural gap has been isolated. No auto-publish.

### 5. Benchmark against the correct immutable golden **technique**

Pin Owner `snapshot-lock.json` and check its five original hashes against unchanged bytes. Compare semantic construction: role intent, registered blueprint ref, ordered required slots/components, disclosure/attempt boundaries, actual teaching moves, relevant visual stage and exit/transfer design.

- **Same source + same renderer/mode/conditions:** exact HTML byte/snapshot parity may be meaningful.
- **Different source question:** **do not demand or advertise byte-equivalence.** Compare structural/semantic technique, then require a qualified content review.
- **Legitimate policy delta:** state precisely what changed and why; e.g. #201 post-golden Core2A H3-after-attempt policy. It is **not** permission to rewrite or bless a new golden.
- **Mismatch:** classify `INPUT | RENDERER | BLUEPRINT | ORACLE` with observed native mismatch, source/target refs and reproduction. Fix INPUT first when content/data is at fault. Propose BLUEPRINT optimization only if the registered blueprint genuinely cannot express a required golden move, with before/after learner proof and separate approval.

### 6. Falsify actual learner behavior, not merely DOM existence

Use local HTTP or an equivalent production-faithful origin serving **real site CSS, JS and assets**. Test all required roles, selected phone/tablet/desktop viewport sizes, H1/H2 **precommit**, blank submit **does not unlock**, H3 after **nonblank** attempt, solution reveal, independent Core1B exit and Core2B transfer. Assert no JavaScript exceptions, failed asset fetches, unintended page overflow, accessible SVG title/description pre-attempt answer leaks and control focus/legibility as appropriate.

Collect precommit H2 and postattempt H3 **visible text** and real screenshots with SHA. Automated answer-string sentinels are **limited**: a mathematically worded hint can spoil W without displaying the exact numeric answer. Explicitly distinguish `BROWSER_STATIC_PASS` from `H2/P1_QUALIFIED_PASS`. A screenshot is evidence for human visual review, not human/academic signoff. For PDF/A4, inspect the actual linked learner-renderer PDF; a separate preview is **not** equivalent.

### 7. Publish an unsigned evidence tile and request independent review

Use existing QRT `7×4` viewer / cell-tile protocol **if already registered**. Carry exact source and manifest git blob SHAs, active blueprints, five-role native HTML SHA256, immutable original golden snapshot digests, math/transfer oracle results, named protected W and competing demand, QRT H1-H3/S1-S3/P1-P3/M1-M3 rows all initially **PENDING**, and actual scoped CI run/artifact URL.

Produce a **candidate review packet** plus the mapping record in `templates/mapping-record.template.json`. Test the record's structural and non-approval assertions with `scripts/validate_mapping.py`. A completed automated checklist does not satisfy 12 independent human semantics.

Qualified subject reviewer must record identity, appropriate mathematics/QRT credentials, nonauthor independence and COI, dated justification for each ask, primary/competing demand, five difficulty components and D band, and ACCEPT/REVISE/RECLASSIFY/REJECT. **Owner** separately records ACCEPT/REVISE/REJECT and unique decision ID, and separately approves any successor golden, source rights, public release or merge. Preserve `NOT_RUN`, `PENDING`, `BLOCKED` and 0/28 where applicable; do not invent verdicts.

### 8. Recheck exact-head CI, publish truthful handoff

Fetch the live PR HEAD and stacked base from GitHub, verify tests actually ran against that HEAD (not synthetic merge), compare exact failing test IDs against the real stacked base when repository-wide workflows are red. **Zero newly failing IDs ≠ green CI.** Recheck on final modified SHA; review statuses and eligible rights stay separate. Publish a durable link to the exact manifest/source SHA, native render receipts and the unanswered questions. Draft PR must remain draft until authorized otherwise.

## Immediate stop conditions

Stop and surface a classified blocker on: absent verified source rights; materially contradictory QRT demand/claimed W; invalid math/domain; unavailable/invalid registered blueprint; zero native receipts; altered frozen golden; preattempt reveal of W; JS/asset/print leak; shared blueprint change without reproduced structural cause; global regression attributable to branch; missing qualified independent reviewer; or missing Owner decision for publishing/acceptance. **No hidden workaround, fabricated reviewer or one-off private renderer.**

## Mandatory companion files

- [Operating contract and anti-pattern table](references/operating-contract.md): staged role design, hard falsifiers and the review decision flow.
- [Machine-readable candidate record](templates/mapping-record.template.json): input/provenance/QRT/role/golden/browser/review fields, all initially unsigned.
- `scripts/validate_mapping.py`: **structural preflight only**, no academic approval.
- [Starting task prompt](references/START-HERE.md): paste into a new agent with a specific user-selected task and host/tool permissions.

## Example only — never portable acceptance

[Grade9v3.5 #201](https://github.com/reallakshman19/Grade9v3.5/issues/201), [draft PR #205](https://github.com/reallakshman19/Grade9v3.5/pull/205) demonstrate native five-role authored TEST output, seven 7×4 D2 draft tiles, actual browser H2/H3, 147 SHA-verified screenshot states and a source-safe frozen-golden technique comparator. They also exposed RETRIEVE-vs-APPLY and MODEL-variable-W mistakes. **Do not** treat these exact dated SHA/fixture references, issue decisions or 0/28 as invariant values for future tasks. Refresh from repository truth every run.

**Output acceptance labels are intentionally distinct:** `MATH_ORACLE_PASS` / `NATIVE_RENDER_PASS` / `BROWSER_PASS` / `GOLDEN_TECHNIQUE_PROVISIONAL` / `ACADEMIC_REVIEW_PENDING` / `OWNER_DECISION_PENDING`. There is no derived all-green `QRT_ACCEPTED` flag.
