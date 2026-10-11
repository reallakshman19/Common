# Track B T01–T03 — Source-original bank question release-boundary qualification

**Date:** 2026-10-11. **Owning issue:** [Grade9v3.5 #174](https://github.com/reallakshman19/Grade9v3.5/issues/174); parent [#130](https://github.com/reallakshman19/Grade9v3.5/issues/130); programme [#137](https://github.com/reallakshman19/Grade9v3.5/issues/137); production [#127](https://github.com/reallakshman19/Grade9v3.5/issues/127). **Chat:** `new` (new chat ID was not provided directly; predecessor g4 ID must not be used as this chat's identity).

**Authority:** User approved the earlier detailed plan and said “proceed next”. That authorizes bounded source-first qualification T01–T03, **not** a V3.1 sole-writer lease, copyright/QRT admission or release. **No product source/PR/CI/Relay/source files edited.**

**Inputs:** [g5 BuddyRunner Stage2 12-section handover](https://github.com/reallakshman19/Common/blob/f1054e52594ed656e594cfcd77c3449c08c07bad/coordination/Session_Oct09/Tab2_track-b-source-custody/handovers/2026-10-11-g5-stage2.md) and [Stage2 PLAN_UPDATE](https://github.com/reallakshman19/Grade9v3.5/issues/174#issuecomment-6110440176); source files fetched from **current product main@778eb35a70517a46108ad0a5dc01dfc89f61c0e3**. This evidence does not rewrite Stage1/2 or claim Stage3.

## T01 — Exact baseline and owner gate: COMPLETED read-only

- Destination `reallakshman19/Grade9v3.5` `main`: `778eb35a70517a46108ad0a5dc01dfc89f61c0e3` reverified from GitHub branch/main.
- Protocol `relay/PROTOCOL_SELECTION.yaml` (blob `5e32a54b3424eeef3e7cd233ee2c643a1b914cd7`): `V3_1 ACTIVE`. `relay/STATE.yaml` (blob `b5c32e37c50bcefb54167a92243ca2d64782def6`): `ACTIVE/SERIAL`, `LEASE-ISS212-ATLAS-INDEX-V31-003`, `EP-ISS212-ATLAS-INDEX-V31-002`, primary destination ISSUE 212; fresh GitHub fetch returns **404**, does not revoke lease. #127 previous requests are inquiries, not grants.
- Eight exact candidate heads, all OPEN/DRAFT/UNMERGED: #145 `c723b0c94eefdd3922c2c0497d3321c33f476ac2`; #155 `a9e68883d71afd2e8b7a0c067eedc23ee4da7ef8`; #175 `6b1b17b7d1b548749f854c3b79ed58ae41dd92ce`; #176 `e9b89eec562c3eb8d4a53b8d5466c067541ad378`; #177 `e7a2e75f86385f278b102db4f850f509d5fa799d`; #178 `1c8d1472eec1ae45d25fcf9c2770fd5ebd075bf9`; #179 `b91096ec279294830e38c319ff5f095198ee503d`; #180 `7772166f1a2f0bb17d070b98736ceed4195d8f34`.
- Parent #130 remains OPEN, its latest current execution priority is **R0–R5 learner-first and exact-head recovery**, not earlier U01-first. #174 retains B0–B6 and Q004 HOLD. Crosswalk: T01 = R0/B0, T02–T03 = evidence for R2/B4/B6, conditional future T04 = narrow source-release assurance; no takeover of #155 R1/R3 content writer. Published #137 agent learner-first reset is *not* a source Core2/Owner rights permission.
- Source position census main blob `800a2f693e1b46162a026375c5854ad4b8b05257`: 68 records, admitted authentic source Core2 0/68, Q004 retained digest null, 7 grouped fidelity categories unverified, rights NOT_REVIEWED, no external-reference custody authorization. QRT coverage blob `c81b32875be6f239a877e8df95252be1b7741a00`: 0/28 accepted cells, Q004 REPRESENT-D1 only proposed. B-M1/B-M2 0/2; release HOLD. No prohibited PDF re-acquisition.

## T02 — Exact current call graph, product/publication seams: COMPLETED source inspection

### A. Canonical original source promotion (existing protection)

`source_pipeline.plan_ingestion` → `source_custody.validate_question` → `review_authority.validate_promotion` → `source_receipts.derive_coverage/verify`: verifies source snapshot/resource digest, question locus, nine original component statuses (7 Q004 research-ledger groupings map to finer nine schema fields), reviewed promotion and per-bucket sufficient source coverage. Valid source proof is **not** a publisher licence or QRT acceptance by itself.

- `Shared/library/source_custody.py` blob `0e2bcc9ac07270618b3bca7401867cea3b78cc1c`, `validate_question` lines 52–226, `valid_for_core2` lines 228–233.
- `Shared/tools/source_receipts.py` blob `14ed3ed4cc2c92c1a392f4e8c3165d5a027af5ae`, `derive_coverage` lines 71–129 and `verify` lines 130–262.
- `Shared/tools/review_authority.py` blob `d7345715869d9d23b3222afbedcf64b958781f5a`, `validate_promotion` lines 257–417: ORIGINAL/ADAPTED candidate promotions must pass source_custody; independent review and digest-bound receipt.
- `Shared/library/source-question-custody.schema.json` blob `48312db70340d5ebea9c98ec24fa831f7a37ffed`: explicitly requires acquisition_ref, resource_ref, source_item_locator, source_digest, custody_mode, comparison_status, demand_signature, nine components. **No rights/license, QRT or publication approval fields**. Those are deliberately separately governed, not implicitly satisfied by schema.

### B. Selection → attempted pages (generic, intentionally draft-selectable)

`Shared/tools/product_manifest.py validate_selection` (blob `1ccd4f743f177096390a34752c306b77c09943c4`) resolves selected `core2` IDs from `bank_index` and other roles from `package`, refuses unresolved/wrong-authority/duplicate/status outside blueprint policy. `_refuse_unselectable` accepts `CANDIDATE/REVIEWED/CURATED` for draft workflows per active blueprint and does not disallow absent status. This supports legitimate authored TEST scenarios; do **not** globally ban CANDIDATE. `Shared/tools/render_core.py context` (blob `9302174e1491138a459a80e9d3f176b83b19e6d7`, lines 3048–3177) calls `validate_selection(manifest, packages, bank)`; `source_projection` derives label/key annotations for indexed package items rather than granting original-source approval. `render_core.main` lines 3481–3551 refuses direct writing under public and generates exact PAGES/SINGLE_FILE receipts.

### C. Product acceptance path (verified **REQUIRED**, not advisory)

`Shared/tools/accept_product.py _release_decision` (blob `aa30fb1785b948cad1e6a2c687abd1551bc94709`, lines 230–267) reads `learner-release-default`; `Shared/assurance/policies/learner-release.v1.json` blob `5cbc28d8ed0930760dfb6b3e16d5a415ba47fccf` sets `acceptance_gate=REQUIRED`. Thus `accept_product` refuses products not `ELIGIBLE`; it independently refuses TEST subjects and rechecks exact output/render basis and print. `Shared/assurance/product.py assure_staged` (blob `881cbd6243834e043a4cc765c41879c9e6a6e6f9`, lines 40–58) runs verifiers on **manifest.package_refs and staged projections**, and explicitly documents `competitive banks are not packages and are not judged here`. `Shared/assurance/verifiers.py run` (blob `d68e377d685347642ed369763cafb94e61ac98a7`, lines 303–327) checks exactly passed package subjects and projections. **The selected `bank_refs` originals are not direct canonical assurance subjects.** No explicit Q004/68 research-ledger rights/QRT item-level check found along this route. Source fact unknowns/reviewer findings presented in `accept_product.accept` may be consented to by Owner; they are not question-specific statutory permission.

Owner waivers in `Shared/assurance/waivers/learner-release.v1.json` include `SOURCE_INTEGRITY` and other missing/inconclusive check types for all subjects, but **cannot waive FAIL or stale evidence**. A bank item omitted entirely from the subject list is **not the same as a failed source record**. No waiver here grants SOF publication rights, QRT acceptance or a new Track B writer lease.

### D. Separate governed canonical library release path (must not overlook)

`Shared/tools/release_authority.py evaluate` (blob `08cbcf2b1769b507ac2e44c0eae5df141cfa25c8`, lines 94–273) checks request SHA, live ready lifecycle, `compile_execution_packet` pin, canonical publication and library provenance, current `REVIEWED/CURATED` digest-backed authority for `inputs/library_records.json` / provenance record IDs, exact role set, and source receipt pin. `Shared/tools/compile_execution_packet.py verify` (blob `44dabe7ee2d9e3a99f1c02baa3dca6507a924a72`, lines 303–360) rejects stale/invalid source receipts when pinned. `tests/test_release_authority.py` already covers unbacked learner-facing canonical records, modified render/route, non-library material, self-authorizing manifests. This path is **stronger than a bare product draft**. Does it cover independently selected competitive bank IDs absent from the canonical `library_records` and their rights/QRT? **UNKNOWN until a route-specific negative fixture executes**. Do not claim both paths are equivalent or that any exploit is proven.

### E. Actual serving and learner scope

`accept_product` copies eligible staged PAGES from `publication/products` into `public/products`; `Shared/tools/build_pages_site.py` builds `docs/` mirror with manifest and link checks. Separately governed canonical `subject/content/*/publication` is handled by `release_authority`. Exactly which products/pages are live on the actual GitHub Pages runtime, cache and project root remains **NOT_RUN**. `public/mathematics/imo-grade9/index.html` is a research-only indexed QID browser. #176 adds 10 labelled source links, #179 adds 7 two-variable source links (drafts only). This is not source Core2 attempt→Core1A; neither source copyright nor final released URL is implied.

## T03 — Executed structural contract probe, and bounded runtime test design

**Executed in this run:** 12/12 non-mutating **GitHub source-structural assertions** all PASSED on exact main blobs (NOT unit tests or a release simulation). They assert:

1. CS01 `core2` selection uses `bank_index`.
2. CS02 CANDIDATE is intentionally permitted for draft selection.
3. CS03 `assure_staged` verifies package and projection subjects only.
4. CS04 Competitive-bank `bank_refs` are absent from that assurance subject collection.
5. CS05 Learner-release acceptance policy is REQUIRED.
6. CS06 TEST cannot be accepted as a normal product.
7. CS07 Renderer refuses direct public writes.
8. CS08 Renderer uses generic product `validate_selection`.
9. CS09 Source-custody schema requires source digest but no rights/QRT fields.
10. CS10 Source-receipt canonical Core2 coverage requires REVIEWED/CURATED plus valid source proof.
11. CS11 Assurance verifiers consume only supplied package subjects and projections.
12. CS12 The inspected `accept_product/assure_staged` calls contain no explicit `bank_refs` release evaluation.

**Scope limit:** these assertions demonstrate a **source-level omission in a call graph**, not end-to-end rejection success/failure, exploitability, eligible learner publication, or true legal permission. Runtime targeted negative tests remain **NOT_RUN** because no coherent authorized product checkout/writer is available in this task. No false `12/12 learner tests PASS`.

### Next authorized exact test (T03b) — where and how, without source copying

Run **only after** named V3.1 writer/branch/permission, in a scratch temp repo/temporary fixtures. Use existing `tests/test_assurance_acceptance.py`, `tests/test_assurance_core.py`, `tests/test_source_receipts.py`, `tests/test_release_authority.py` patterns and add **one targeted regression** in owning tests, ideally `tests/test_assurance_acceptance.py` (product path) plus a separate `tests/test_release_authority.py` canonical path check *if and only if* selected bank IDs can be carried through that route. Do not test with real SOF wording or unlicensed figures.

Synthetic fixture:
- One minimal valid subject package with canonical capability, independent worked Core1A/microtopic where relevant, plus `bank_refs` pointing to a fabricated competitive bank question id `SYNTH-ORIGINAL-BANK-Q001`, syntactically suitable stem/options and `origin=ORIGINAL`, `status=CANDIDATE`. Use synthetic source locator and fabricated digest only; **never assert it is a valid SOF source**.
- Build a staged exact PAGES receipt with existing `render_core` and clean temp paths, with static/print fixtures constructed per existing test expectations. Recompute `assure_staged` or `_release_decision` on that exact staged tree **without invoking `accept_product.accept` or writing `public/`**. Observe eligibility, selected question inclusion and per-item evidence (and whether baseline quality failures independently prohibit the test). Beware waived evidence types: never call waived NOT_RUN an actual source-rights PASS.
- Negative 1: no source digest/verified nine components, rights NOT_REVIEWED, QRT proposed only → expected **SOURCE_ORIGINAL_BANK_ADMISSION_HOLD**, not ELIGIBLE (when source-original eligibility is a release requirement).
- Negative 2: falsified `REVIEWED` status with no digest-bound promotion receipt → still HOLD.
- Negative 3: complete fake source component fields but missing publisher display permission → still HOLD.
- Negative 4: source proof/rights accepted hypothetically but QRT only proposed → still HOLD.
- Negative 5: external-reference mode with unresolved locator/component → still HOLD; **never copy fake original bytes publicly**.
- Positive control: an **entirely synthetic**, valid, independently-accepted fake rights/QRT/custody receipt as a policy **contract fixture only**, scoped solely to a private test environment; it must show valid source admission can pass *its own* new gate without implying an actual Owner grant, while existing mandatory full acceptance/print/CI may still fail.
- Compatibility: one authored TEST Core2A CANDIDATE and one genuinely reviewed non-original question should retain existing behavior. Control cases must not change all global `CANDIDATE` policy.
- Additional canonical `release_authority` fixture: selected bank QID **not** in the canonical `inputs/library_records.json` or provenance set; determine whether it is explicitly rejected rather than quietly omitted from reviewed record checks.

**Before declaring a defect:** inspect whether a reachable alternative verification path or mandatory projection check already consumes `bank_refs` and their original-source rights/QRT state. Record the exact evidence and finish with `NO_CODE_CHANGE` if the product already fails closed. A fixture that only fails because missing CSS/PDF/placeholder is **inconclusive** for source rights/admission.

**If the negative test demonstrates the specific gap:** nominate a **single authorized writer** to add a narrow source-original selected-bank-item eligibility guard at the existing pre-Owner `assure_staged`/release-decision boundary (or the already-approved authority owned by the same lifecycle). Consume approved existing source-custody/review/QRT+rights decisions by **ID and exact digest**, fail closed if absent, and do not create a second source ledger. Tests must include mutation/staleness of source/QRT/rights fixtures, complete selected QID set, and no status spoof. **No source code to be modified now.**

### Proposed commands for that future coherent checkout (NOT_RUN here)

```bash
git rev-parse HEAD
python3 -m unittest tests.test_assurance_acceptance tests.test_assurance_core tests.test_source_receipts tests.test_release_authority -v
python3 -m unittest tests.test_product_blueprint_safety tests.test_render_core -v
python3 -m unittest tests.test_test_source_custody tests.test_test_source_review -v
# Then exact-head normal workflows, reviewed actual browser and print/AT under owning gates
```

**Pass bar:** a selected invalid original bank question **cannot** make release ELIGIBLE even when unrelated page/layout/PDF checks pass, while an approved synthetic source contract and authorised authored TEST drafting retain behavior. **No extrapolation** to real Q004 or to unconditional product release. **Stop/rollback:** unknown legal grant, missing valid source/QRT owner receipt, wrong actual writer, absolute mandatory CI fail, injected TEST-to-production path, or source record duplication.

## T01–T03 result and next

| Unit | Evidence | Result |
|---|---|---|
| T01 exact ownership/source baseline | GitHub main + eight PRs + relay + #130/#174/#127 + Q004 | **DONE** |
| T02 both governed release chains | Exact product source blobs and call graph | **DONE**, remaining bank-route question isolated |
| T03 structural contract assertions | 12/12 read-only checks | **DONE — STRUCTURAL ONLY** |
| T03b true synthetic staged release negatives | Future scoped coherent checkout; no execution | **NOT_RUN / NEEDS_NAMED_WRITER** |
| T04 conditional source edit | Prove gap first and obtain explicit V3.1 delivery scope | **BLOCKED_NOT_STARTED** |
| Original source, academic/QRT and learner | Separate real authorities and human tests | **HOLD** |

**Decision:** `PROCEED_SOURCE_FIRST` and `VERIFY_FIRST`; no unverified claim that a real release bypass exists. Parent #130's learner-first authored Stage A/B remains with its owner. Track B #174 B-M1/B-M2 0/2, authentic source Core2 0/68, QRT 0/28, student release HOLD. **NEXT:** obtain coordinator's exact writer/issue route, then T03b synthetic fixture on one pinned review branch, not new Q004 acquisition.
