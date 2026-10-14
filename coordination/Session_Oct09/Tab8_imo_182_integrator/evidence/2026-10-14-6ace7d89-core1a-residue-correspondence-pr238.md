# r6 P1 — first isolated authored TEST package fix: residue correspondence

**UTC:** 2026-10-14 | **Chat:** `6ace7d89` | **Programme:** [#182](https://github.com/reallakshman19/Grade9v3.5/issues/182) | **D1 coordination issue:** [#200](https://github.com/reallakshman19/Grade9v3.5/issues/200) | **Code:** [draft PR #238](https://github.com/reallakshman19/Grade9v3.5/pull/238).

## Exact isolated scope and source integrity

- PR #238 head `28511cb4b82c17f90892867cae85955fc29c21d8` from repository `main` base `4dbedc6773482bbecb146ff8959614b2c32dcc6e`; **OPEN/DRAFT and not merged**. Separate from D1 reviewer-only branch stack #208→#223→#228→#231.
- Only **six** files changed: authored candidate `TEST/library/imo-g9-divisibility-core1a.v1.json`, its local canonical-shape research validator, its direct unit test, the source-pinned static-review receipt, that receipt's validator, and reviewer guidance. **No public HTML, renderer, general library schema, generated data, golden, Q003 source or publication changed.**
- Candidate source Git blob old `cbcfe1ffe69b7453a53ca3608f5b563b0f91776e` → new **`31ec1141eaea2a0f49fffafa9dd2a740620c70b0`**, changing ONLY the `REP-TEST-IMO-G9-RESIDUE-TABLE.correspondence` mapping. Existing five `required_elements` retained unaltered; parity as a separate mathematical warrant remains required.
- Precise correspondence now four rows: `n mod 3 ∈ {0,1,2}` maps the declared ordered-row element, and the three residue classes map to **`n`**, **`n+2`**, **`n+1`** for residues `0`, `1`, `2` respectively. Each correspondence now literally names a `required_elements` string, not a merely similar phrase. This addresses **two** known exact CI representation-correspondence failures without making any new source question or grading claim.
- The specialized validator now requires exactly four ordered `(element,symbol)` pairs, member-only declared elements, non-empty warrant descriptions and unchanged parity entry. Unit tests include one positive exact-map assertion and four deliberately invalid mutations (missing element, wrong factor, dropped row, erased parity). This increases specificity rather than relaxing global library admission.
- The receipt `core1a-test-review-receipt.v1.json` now points to new source blob `31ec...`; receipt validator `PKG_BLOB` and active guide repinned. **The unchanged static preview HTML Git blobs** remain `4072574779e26682071210dd2176aae6236f6971` (both `public/test` and `docs/test`), and the unchanged mathematics-topic HTML blobs remain `5876b54db5699cf13139d64e40d3ff24b88541c1`. Repinning source does **not** re-render, independently browser-test, fix missing TEST banner, or validate public navigation.

### Evidence at PR creation

Full GitHub branch readback of exactly six files passed **12 authored structural/custody checks**, including four membership pairs, factor ordering, original five required elements and independent parity, authored-only `TEST`/`CANDIDATE`, zero source question or datum and no QRT/publication status, strict validator and falsifiers, three exact source pin references and unchanged four HTML/navigation receipts. `get_pr_info` and `list_pr_changed_filenames` independently confirmed exactly six files and OPEN/DRAFT status.

**CI not green:** At initial check on exact head `28511cb4`, GitHub workflows [guardrails 38497211734](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38497211734), [canonical 38497212010](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38497212010), [SOF seed 38497211800](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38497211800) and others were **QUEUED**. No test success claimed before the run jobs complete.

### Deliberate unresolved constraints

- **Canonical generic intake of the TEST package still not admitted**: `data=[]` yet its exit-task `oracle.verification.bindings` names four literal non-datum values (`positive_integer`, `24`, `0..23`, `n(n+1)(n+2)(n+3)`). `Shared/library/intake.py` requires references to declared datum IDs. Do not invent rows, strip oracle checking, or award canonical/academic acceptance silently; separate owning research decision and correct contract required.
- Other upstream failures remain: two TEST links on public IMO Grade 9 learner index, missing visual TEST banner on draft preview, linear-equations fixture's schema-invalid `PUBLISHED`/`VERIFIED_CANONICAL` statuses, and public Core-learning generated data potentially admitting TEST buckets. These are not patched by #238.
- Owner goal/O1–O3, registered blueprints, sole `Shared/tools/render_core.py`, frozen Owner golden `G-IMO-G9-FIVE-CORE-20261012`, #183 actual Q003 custody, academic reviewer signature and Owner QRT IDs stay unchanged. **0/7 D1 and 0/28 programme accepted; no rights/merge/release.**

## Next verification
1. Fetch exact-head scoped TEST candidate and review validator job logs when completed. Require actual success on fixed checks and note whether strict generic admission still fails; do not equate local 12/12 readback with CI.
2. If scoped regressions appear, repair only the implicated TEST candidate/source pin. The four undeclared oracle targets need an independent declared-data design with the package's research owner, not a cosmetic bypass.
3. Keep #238 draft and share root-cause explanation with #200. Product public-route TEST isolation and generator/fixture compatibility changes remain separate governed lanes.

LOG | Outcome=draft PR #238 source-local 4-row correspondence fix, source pins and falsifiers implemented | For user=two provable representation contract errors targeted without publication or semantic downgrade | Proof=GitHub six-file readback, old/new source SHA, queued CI | Open=exact CI, 4 binding/data references, other product/global gates and Owner 0/28.
