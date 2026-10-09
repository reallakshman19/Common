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
