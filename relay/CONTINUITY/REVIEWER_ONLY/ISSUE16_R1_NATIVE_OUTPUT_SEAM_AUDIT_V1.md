# Issue #16 — Stage 1 native-output seam audit

**Classification:** reviewer/operator source evidence, NOT input to an independent blind Runner. New issue [#16](https://github.com/reallakshman19/Common/issues/16), recovery parent [#6](https://github.com/reallakshman19/Common/issues/6), historical original [#890 WP1–WP2](https://github.com/reallaksh19/Common/issues/890). No source-writer or Owner permission arises from this audit.

## Exact observed source roles

| Observed source | Source identity | Contract |
| --- | --- | --- |
| PR #14 Stage 1 prompt | b6d07eaba7faea0f0b134de3998745df265bdb82 / blob 5bcca08960e0a7800173ff24aaffa5f334b62912 | Two separate B-authored original UTF-8 documents, headings `# STAGE1_BASELINE` and `# STAGE1_PLAN`; if unavailable: TWO_NATIVE_FILES_UNAVAILABLE and HOLD |
| PR #3 historical Stage 1 prompt | bf4af494505cca6b655fa9163d6731ed2b1ad160 / blob 8c2c870ddce2082a9b47610e5454dfe6ad09a7e6 | Baseline-first Part A then provisional Part B, including evidence-based NO_CHANGE; two-file packaging addition not yet present |
| PR #2 Stage1 reconstruction template | blob 09249062535e645fa6caed9624779d5df68445d3 | Requires the two original authored raw files; operator must NOT retrofit headings or split combined response |
| PR #2 native transactionlib.py | blob 07368987c1156fb687a76139150dd58556c92269 | `_validate_buddy_markdown_transaction` accepts generic `# ` heading after stage/path/UTF-8 validation; does NOT require exact stage-specific heading for baseline/plan |
| PR #2 native test_relay_tx.py | blob 6f6207b0f95315ca18b6d89f19374525921ea06c | Existing native positive cases use generic headings `# Source producer and consumer witness` and `# Two alternate HOWs and falsifiers` |

These SHA/blob references are a pinned observation, not permanent current PR heads. The repository is NEW reallakshman19/Common; original reallaksh19/Common issues #889/#890 remain historical.

## Physical gap and impact

An otherwise-valid PUBLISH_BUDDY_MARKDOWN transaction can commit a Stage1 baseline or plan with a generic Markdown heading. Native transaction digest proves committed bytes and stage order, but generic content validation does not enforce the required B-authored file *identity*. Actor strings and five-phase STAGE1_FREEZE_CANDIDATE are likewise NOT proof of fresh independent B, denied reads or authenticated external freeze.

**Correct owner boundary:** Enforce stage-to-payload heading at the sole native ingestion boundary common to CLI and direct execute(); include wrong-heading, combined-file, same-actor, stale receipt, symlink, and happy two-original-file negative/positive cases. That change touches protected frozen V3.2 code, owned by PR #2 and governance issue #4 / draft #7, NOT by this issue #16. Do not create a second Python message engine or bypass that governance.

## Focused actual local evidence

The reviewer-only `skills/engineering-pr-delivery-v3.5/tests/test_issue16_stage1_output_contract.py` validates original B-file byte and heading shape independently of native execution. The previous local test run executed **11/11 PASS** under Python unittest using source-grounded synthetic examples: valid baseline, valid plan, NO_CHANGE, wrong generic baseline/plan headings, cross-stage relabel, combined output, empty body, invalid UTF-8, unsupported stage and substituted string-for-byte payload. Exact command:

```bash
python -m unittest discover -s skills/engineering-pr-delivery-v3.5/tests -p 'test_issue16_stage1_output_contract.py' -v
```

This is a local reviewer-fixture success, not a native transaction or real B result. On the original PR #2 source the regression still lacks runtime enforcement: direct execute() and CLI must both reject generic-heading stage messages at the native owner boundary. After an authorized native patch, run these routes at exact HEAD plus base-pinned frozen guard.

## Parent acceptance and next action

| Requirement | Grade |
| --- | --- |
| Old #890 WP1 baseline-first source semantics and two original Stage1 documents | DOC PRESENT / native enforcement gap |
| Old #890 WP2 real B independent fresh context and deny probes | NOT_RUN |
| Old #889 A03/A05/A06/A10/A11 | PARTIAL / no authenticated positive+negative whole episode |
| Native Stage1 heading byte validation | SOURCE_GAP; protected owner approval HOLD |
| Native Stage1 freeze external attestation and same B Stage2 | NOT_RUN |

Next V3.5 #16 unit: finish source-only test/contract publication, run focused tests against the exact current checkout, and reconcile Stage1 semantic consumers with moving PR #14 while preserving full twelve-section technical handover in main. Any protected V3.2 source change must occur on PR #2 under its separate Owner authorization.

## Follow-up execution: real protected native PR #2 code, pinned RED

**This upgrades the prior SOURCE_GAP finding with physically executed negative evidence.** [GitHub Actions run #37990462121](https://github.com/reallakshman19/Common/actions/runs/37990462121), job `Native PR2 Stage1 ingress conformance (RED until native fix)`, completed **FAIL** against **two explicitly checked-out immutable commits**:

- Reviewer test and workflow code: `reallakshman19/Common@622c4bc55b669f854bf361766b39653e254ea57a`.
- Native protected PR #2 code: `reallakshman19/Common@da3680459c5b48f44cda822ccf5009be4b035eef`.
- Test script: `skills/engineering-pr-delivery-v3.5/tests/probe_issue16_native_stage1_candidate.py`, executed with Python 3.12 and installed native import dependencies (`PyYAML`, `jsonschema`). It imports actual native `transactionlib.py` from a second **read-only candidate checkout** and calls `_validate_buddy_markdown_transaction`.
- The code **mocks only `_require_buddy_sequence`** to prevent missing predecessor receipts from hiding the heading/payload gate; it does NOT exercise `execute()` disk commit, CLI wrapper, real session identity, external access denial or actual freeze. That limited scope is explicit in both test code and CI job.

| Adversarial input at actual native ingress | Execution outcome |
| --- | --- |
| Canonical `# STAGE1_BASELINE` positive | PASS (native accepted proper format) |
| Canonical `# STAGE1_PLAN` positive, evidence-based `NO_CHANGE` | PASS (native accepted proper format) |
| Generic baseline heading | FAIL — native **incorrectly accepted** |
| Generic plan heading | FAIL — native **incorrectly accepted** |
| Baseline file labelled as plan | FAIL — native **incorrectly accepted** |
| Combined baseline and plan H1 inside one file | FAIL — native **incorrectly accepted** |
| Combined file with CRLF second heading | FAIL — native **incorrectly accepted** |
| Combined file with padded second heading | FAIL — native **incorrectly accepted** |
| Combined file with second heading at EOF | FAIL — native **incorrectly accepted** |

**Job truth:** `Ran 9 tests ... FAILED (failures=7)`, exit code 1. This is a genuine **native payload contract RED**, not an import/setup failure and not a false `9/9 PASS`. It is safe to retain as a **blocking evidence gate** while native source remains uncorrected; once an authorized PR #2 fix exists, update the pinned native SHA and rerun these same tests plus the native publisher wrapper/direct `execute()` flows. The ordinary issue #16 reviewer contract tests remain separately green and are **not** an alternate native admission implementation.

**Required native-owner fix acceptance:** same source-level exact heading and combined-output rejection must apply to actual native CLI/wrapper **and direct `execute()`**, preserve original author-supplied bytes, not fabricate missing historical B source, and still acknowledge `NOT_ATTESTED` for external identity/freeze. The existing native test suite must update its old generic-heading positives and add these negatives. Owner freeze governance #4/#7 remains separate; this reviewer PR neither requests nor implies permission to mutate those paths.

## Full native receipt chain + wrapper/direct execute() RED (next bounded batch)

**Expanded executed source witness:** [run #37991111370](https://github.com/reallakshman19/Common/actions/runs/37991111370), distinct real head checkouts issue16 `51f942f075533f56f173397cab2d6371ddda3c5c` and protected native PR #2 `da3680459c5b48f44cda822ccf5009be4b035eef`. The new `probe_issue16_native_full_buddy_chain.py` **does not mock any native function**: before each submission it really commits a synthetic intake, dispatch request and dispatch observation; for plans it also commits a valid baseline. The invalid file is then submitted using either actual `relay_tx.publish_buddy_markdown()` or direct `transactionlib.execute(command='PUBLISH_BUDDY_MARKDOWN')`. Each case uses a temporary root; the protected native checkout is read-only, and no production state/lease is changed.

| Exact runtime route | Valid control | Adversarial tests requiring rejection | Actual result |
| --- | --- | --- | --- |
| Normal native `publish_buddy_markdown()` | Canonical `STAGE1_BASELINE` → COMMITTED; PASS | Generic baseline, generic plan, baseline-as-plan, combined two H1s, CRLF second H1, padded second H1, EOF second H1 | **7 FAIL**: each malformed payload **actually committed**; no correct native reject |
| Direct `transactionlib.execute()` | Canonical `STAGE1_PLAN` / `NO_CHANGE` → COMMITTED; PASS | Same seven payload classes | **7 FAIL**: each malformed payload **actually committed**; wrapper checks cannot protect direct transactions |

**Hosted log:** `Ran 16 tests in 5.217s`, `FAILED (failures=14)` with `NATIVE_FULL_INGRESS_GAP: ... committed malformed B-authored original document` for all fourteen negatives. Both positive controls passed. Existing isolated pure-ingress probe in the same [run](https://github.com/reallakshman19/Common/actions/runs/37991111370) also fails its original seven negatives, confirming independent diagnostic consistency. The full-chain test controls **synthetic** `actor`, `Session ref` and `Read-scope ref` strings—successful sequencing and `COMMITTED` manifests do not prove actual external Runner B independence, forbidden-read denials or authenticated external freeze.

**Repair design obligation, not an unauthorized code patch:** PR #2's native single ingestion point `_validate_buddy_markdown_transaction` must enforce stage/payload heading concordance and reject embedded second Stage1 H1 forms, including CRLF/trailing spaces/EOF. Existing native `test_relay_tx.py` includes generic-heading positive fixture rows; update them and add real wrapper/direct transaction negatives that confirm neither message nor transaction is committed on rejection. CLI and public wrapper must not have a bypassable weaker duplicate validator. Native Owner #4/#7 permission remains `NOT_GRANTED` on inspected issue state. Rerun both separate conformance jobs against the **new exact native PR #2 head** after an authorized source repair; never update a SHA merely to make the CI run green.
