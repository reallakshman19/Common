# {{PROJECT}} — Agent OnBoard design decisions, alternatives and falsifiers

**TEMPLATE — fill from actual Owner/native decisions, not fabricated architecture.** Recorder `{{Oracle/OTM}}`; effective project/task revision `{{...}}`. Disclose unresolved alternatives instead of presenting a preference as settled.

## 1. Chosen and rejected alternatives: causal record

| Decision and authority | Chosen mechanism and why | Rejected shortcut and why it fails | What remains unknown |
| --- | --- | --- | --- |
| `{{Owner/native decision ref}}` | `{{required behavior}}` | `{{plausible but unsafe shortcut}}` | `{{UNKNOWN/none}}` |
| `{{source owner/code ref}}` | `{{state/identity/review boundary}}` | `{{incorrect cache, inheritance, optimistic PASS, silent overwrite}}` | `{{source/test scope}}` |
| `{{original receiver/evidence ref}}` | `{{actual transfer/test method}}` | `{{local ZIP or author's hash asserted as recipient receipt}}` | `{{measured digest or NOT_RUN}}` |

Do not create extra ADR IDs merely to fill this table. Link existing engineering ADR/WBS/issue decisions, preserve earlier rejected ideas and distinguish Owner-adopted rules from Oracle suggestions.

## 2. Surviving wrong cases and discriminating checks

**F1 — Original source meaning differs from a synthetic mock.** `{{one concrete original source element and alternate field/unit/default}}` → `{{opposite prediction and source spec}}`. A synthetic PASS is not a verified original-meaning contract.

**F2 — Wrong candidate or stale state.** `{{input, selection, source/head/request generation changes}}`; a previously green test/result is read under a new candidate. Inspect exact bytes/epoch and retry **affected** check only.

**F3 — Similar-looking output aliases two originals.** `{{repeated IDs, non-unique node numbers, collapsed paragraphs, duplicate geometry}}` and its false success. Discriminator preserves *actual source occurrence/slot* identities.

**F4 — Writer conflict or forbidden output.** `{{two actors editing same path/owner-only operation}}`. Native branch/custody check, not title/role inference; no release based on a generated draft.

**F5 — Hash-only or link-only transfer.** A `sandbox:` URL or producer-provided SHA appears correct yet the recipient has never downloaded the file. Check the receiver's Option 1/2 exact bytes; report `LOCAL_ONLY / NOT_TRANSFERRED`.

**F6 — Author review falsely independent.** A fresh chat on the author account checks the PR; still `SELF_ASSESSED` for affected independence, even if negative testing is technically useful. Disclose authorship and review expectation exposure.

**F7 — Missing one runtime check freezes the entire project.** One specific browser/native fixture cannot run, but meaningful source, disjoint tests or other safe tasks are possible. Mark only that claim `NOT_RUN` and execute an independent authorized next step; reserve acceptance where actually required.

**F8 — All green but user cannot use result.** E.g. isolated parser tests PASS but launcher/export/Owner real-file trial fails. Keep prototype usability, native acceptance, independent review and product release separate.

*Replace these illustrations with real project-specific positives and opposite cases; don't supply the target answer to an independent reviewer whose job is to derive the expectation.*

## 3. Evidence/decision boundary

| Evidence actually obtained | Permitted assertion | Forbidden upgrade |
| --- | --- | --- |
| Source read / old native report | `SOURCE_INSPECTED` or `REPORTED` at exact revision | Actual fresh browser PASS |
| Own build/tests | `SELF_ASSESSED` scoped to executed cases | Authenticated independent review |
| Published artifact relay receipt | `RELAY_REGISTERED` | Receiver download, `BYTES_VERIFIED`, engineering PASS |
| Distinct review of exact candidate | Scoped independently evidenced verdict if identity/expectation checks succeed | Universal Owner acceptance/release |
| Owner acceptance on one trial | That observable user outcome under stated inputs | All downstream engineering approval |

**Decision after contradictory evidence:** `{{source → revised hypothesis/claim → narrow repair or reviewer request → next action, not a blanket gate}}`.

## 4. Release and false-confidence boundary

For every consequential claim, identify original expected behavior, candidate/input SHA, one plausible surviving error, actual executed command and observable outcome. If not available, say `UNKNOWN/NOT_RUN` and continue unaffected authorized work. Independent reviewer checks may be required **for actual engineering use** even when Oracle can diagnose a defect without a second permission loop.

**Source links:** `{{actual Owner text; current repo module; one concrete test; issue/PR decision}}`. **Status:** `SELF_ASSESSED / SOURCE_DERIVED / UNVERIFIED`, as warranted.
