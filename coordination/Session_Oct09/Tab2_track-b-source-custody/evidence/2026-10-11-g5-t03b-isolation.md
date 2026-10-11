# Track B T03b — Isolated synthetic original-bank assurance runtime falsifier

**Date:** 2026-10-11. **Execution scope:** local, isolated, no checkout or writes in `reallakshman19/Grade9v3.5`. **Owning:** [Track B #174](https://github.com/reallakshman19/Grade9v3.5/issues/174), [parent #130](https://github.com/reallakshman19/Grade9v3.5/issues/130), [production coordinator #127](https://github.com/reallakshman19/Grade9v3.5/issues/127). Continues [T01–T03 read-only evidence](https://github.com/reallakshman19/Common/blob/b70ebfc4d43a7ff4ebbb72c61c9c1794e69d46a3/coordination/Session_Oct09/Tab2_track-b-source-custody/evidence/2026-10-11-g5-t01-t03-release-boundary.md).

## Basis and authority

- Fresh live product main `778eb35a70517a46108ad0a5dc01dfc89f61c0e3` confirmed with GitHub. `relay/STATE.yaml` unchanged, blob `b5c32e37c50bcefb54167a92243ca2d64782def6`, ACTIVE/SERIAL `LEASE-ISS212-ATLAS-INDEX-V31-003`; destination issue #212 still 404.
- #127 history refreshed: new Owner note [#127 comment 6110810680](https://github.com/reallakshman19/Grade9v3.5/issues/127#issuecomment-6110810680) **parks prior Atlas-index work only for separately scoped Track A print-renderer writer**, grants issue #173 and ChatGPT in a DIFFERENT chat one branch based on #180 and renderer/print tests; **this is NOT a Track B release-assurance writer grant**. The [Track B T03b routing request #6110811311](https://github.com/reallakshman19/Grade9v3.5/issues/127#issuecomment-6110811311) remains unanswered.
- Internet DNS is unavailable from the sandbox container: `git ls-remote https://github.com/reallakshman19/Grade9v3.5.git refs/heads/main` failed `Could not resolve host: github.com`. This prevents a direct full checkout. The GitHub provider allows independent readback of exact source files.
- Used **exact provider-returned 3,446-byte `Shared/assurance/product.py`**, copied unmodified into local scratch. Local `git hash-object` = `881cbd6243834e043a4cc765c41879c9e6a6e6f9`, exactly equal to GitHub main's content blob. This is stronger than a hand-recreated outline or substituted implementation.
- The caller `assure_staged(slug, repo)` is the **actual unchanged Python function** imported from that source, not a rewritten model. `manifest_of` and `staged_projections` execute unchanged too. **Injected mocks replace `Shared.assurance.aggregate`, `verifiers` and `contract`**, with transparent trace collection, and supply synthetic `ELIGIBLE` or `INELIGIBLE` decisions for control tests.
- Fixtures are written only into a temporary local directory: actual synthetic `products/mathematics/synthetic.manifest.json`, `Mathematics/library/synthetic-core1a.v1.json`, `Mathematics/library/exam-bank/competitive-exam-question-bank.v2.json` containing invented `SYNTH-ORIGINAL-BANK-Q001`, and a minimal `publication/products/mathematics/synthetic/render-receipt.json`. They are **not production-schema validated or an actual renderer build**, and there is no genuine publisher content or permission claim.
- Local test script checksum **SHA-256 `58fdd8b90ec986b9771654f95b137ff9d0303e8a29d9ea06282b8d5a1ace6f5e`**, stdout/stderr log SHA-256 **`109bb846407b1b568f1ce779008bb43afc1124c45b0b1c86b4b82d28f09e45ce`**. These are local sandbox receipts, *not GitHub blobs*. The script/log are available as output artifacts in the initiating chat; exact source fixture is not claimed to be committed to product.

## Execution and six result cases

Command actually run:

```bash
python3 /mnt/data/t03b_scratch/test_bank_assurance_isolation.py
# 6 tests, ~0.013 s, unittest OK
```

| Test | Outcome | Verified meaning |
|---|---|---|
| Exact source file matches Git blob | PASS | Actual loaded `product.py` matches main blob `881cbd62...` |
| Five invalid source-bank variants compared to synthetic approved variant | PASS | `assure_staged` passes **identical** package and projection inputs to underlying mocks; changing selected bank record does not affect those arguments |
| Canary selected bank QID has no representation in forwarded assurance inputs | PASS | Selected `SYNTH-ORIGINAL-BANK-Q001` absent from verifier/evaluator argument traces |
| Changing `package_refs` does propagate | PASS | Canonical package change *does* change assurance inputs as expected |
| Missing staged product receipt is rejected | PASS | Real `staged_projections` raises `ContractError` before mock assurance |
| Mock `INELIGIBLE` verdict remains `INELIGIBLE` | PASS | Real wrapper returns what underlying evaluator decided; it does not override denial |

**Exact negative scenarios changed in the synthetic bank file:**
1. ORIGINAL CANDIDATE missing source digest and publication rights; QRT PROPOSED.
2. ORIGINAL `REVIEWED` but missing promotion receipt/digest (status forgery).
3. Source digest provided but rights explicitly NOT_GRANTED.
4. Mock rights `GRANTED_SYNTHETIC` with QRT still PROPOSED.
5. EXTERNAL_REFERENCE with unresolved source digest, rights and QRT.
6. Positive **synthetic-only** comparison has hypothetical REVIEWED, invented digest, fictitious `GRANTED_SYNTHETIC` and `ACCEPTED_SYNTHETIC` values. **It is not a real authorization and is never exported as learner content**.

**Result: 6/6 local `unittest` PASS, no runtime exception.** The source input layer of `assure_staged` does **not distinguish** these bank variants because it does not pass `bank_refs` or the selected QID to verifiers or aggregate eligibility. This observation is source-proven under explicit mock boundaries; it confirms the exact per-bank-subject omission, not every possible release path.

## Scope limits (mandatory honesty)

**NOT A FULL-PATH LEARNER RELEASE BYPASS.** The mocked aggregate was configured to return `status=ELIGIBLE` for inspection; that value is **not** the real policy engine's verdict. The tests do NOT run real schema validation of synthetic bank/manifest, `product_manifest.validate_selection`, `render_core.build`, actual `verifiers.run`, actual `aggregate.evaluate_release`, `accept_product._release_decision`, `release_authority.evaluate`, browser/CI, `accept_product.accept`, or real GitHub Pages. Another real gate may independently block the source-invalid item. Nothing was published or tested under official source rights.

The exact product source permits TEST candidate rendering and contains other genuine protections: `source_custody` and `review_authority` for REVIEWED/CURATED promotion; `source_receipts` for sufficient original Core2 source; `learner-release-default` REQUIRED; `accept_product` TEST exclusion and exact render checks; separate `release_authority` canonical-library review, provenance and source-pin path. None are waived by this isolation report.

## Decision and next bounded action

**T03b-ISO: DONE — SIX PASS / bank input invisibility verified. T03b-INTEGRATION: NOT_RUN / blocked by named V3.1 writer and working full product checkout. T04: NOT_STARTED, conditional on an independent functional full-policy negative case.**

One correct next engineering step: in a **named authorized branch** owned by production #127, add a synthetic-only regression to the existing `tests/test_assurance_acceptance.py` and optionally distinct `tests/test_release_authority.py` to create an actual complete staged product fixture, make all unrelated release requirements valid, then mutate only an ORIGINAL `bank_refs` QID's source-rights/QRT admission and observe real `ELIGIBLE` versus `INELIGIBLE/INCOMPLETE` outcomes. If the current final system rejects the candidate, record **NO_CODE_CHANGE**. If it accepts ineligible originals, request a **separately scoped** minimum per-QID check using existing source-custody, rights, reviewed admission and QRT records; preserve valid authored TEST and reviewed non-original candidates; no new source ledger or renderer changes.

**Preserved constraints:** Owner development approval for the 68 source identity references is not source-wording/figure reproduction rights. No repeated Q004 private PDF fetch. Source originals admitted **0/68**; QRT cells accepted **0/28**; Track B B-M1/B-M2 **0/2**; learner release **HOLD**. No live product, PR, Relay, academic, legal, QRT or release alteration.
