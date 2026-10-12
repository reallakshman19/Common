# R7 W03 — executable-form PR-reference compatibility design; review-ready, protected source unchanged

**Chat=6acbb049. Owner direction:** "add all these in pending /known issues, proceed!!" On 2026-10-12. **Source authority:** original public lab `reallaksh19/relay-v32-e2e-lab`, numeric repo ID `1411550807`, `main@f0dfc590bd3fa53c50c1b645f17faf3f88e2f155`, original `governance/released-graph.json` Git blob `fde7e1fbd0c71efb64a678206f0bc9f32e36f6c8`. **Target existing native:** `skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py` Git blob `804cacca930e47c4528bb0d245efaf941996e4cf`; tests `skills/engineering-pr-delivery-v3.2/tests/test_delp_projection_v32.py` Git blob `da9484d04bb26c820530618072468aaf62d7173d`. **Independent governance:** [PR #316](https://github.com/reallakshman19/Common/pull/316) at `8f5a47dd2e67795b78bf66732a485dba2fca07d9`, chat Owner approval recorded, DRAFT and UNMERGED, reviews 0/2; main amendment absent. **No protected code or test implementation authorized until the approved governance grant is independently qualified, merged, and already base-resident.**

## Readback on owning #325 pending section — no duplication

The existing [Common issue #325](https://github.com/reallakshman19/Common/issues/325) body was re-fetched and starts with `<!-- TAB1-G7-R7-KNOWN-ISSUES-PENDING:start -->`, containing all four **unchecked** items: `R7-PENDING-01` reviewers 0/2; `-02` effective required CI policy UNKNOWN (API 403); `-03` qualified actual `CHECKPOINT_FACTS_V1` issuer and positive/hostile evidence UNKNOWN; `-04` governance #316 owner-chat-approved but **unreviewed/unmerged/non-base-resident**. These already satisfy user's explicit request to add three selected items to known issues and capture separate grant effectiveness, so **no duplicate issue, marker, comment checklist, or new policy authority was created**. Status #325 original T04/T05 OPEN, root #5 AC0/8. Frozen code and publisher OFF.

## Source-level mechanics and bounded implementation target

Actual native `parse_ref(value)` uses regex `^(?:(repo-name-with-optional-owner)#)?(positive-number)$`, returns `(repo_or_None, int(number))`. `validate_graph` stores and parses `primary_pr`, and `observe_github` derives provider PR from `ref_number(primary_pr)`. `project` computes source plan and input digests; `source_bound_responsibility_core` independently revalidates source graph/plan/input and checks leaf, then compares `primary_pr.startswith(programme.repository.rsplit("/",1)[-1]+"#")`. That final basename-only condition rejects the **three actual full owner/repo PR bindings** of the current original released graph (#8, #13, #15), if the core is reached with valid projection. Current native project/core Python **NOT_RUN** here.

**Review-ready minimal intent, not applied source patch:** Inside the already approved exact function and existing source/test paths (not a new adapter), replace *only* the basename-only prefix condition with strict parsing of a nonempty `primary_pr`, requiring a valid positive PR number and **either** the exact bound full `programme.repository` or its short basename, case-insensitively, disallow other owners/repositories and malformed/unqualified refs; preserve `RESPONSIBILITY_CORE_MATERIAL_BOUNDARY` fail-closed error. Preserve source graph bytes and V1 `input_digest`/DELP maths, lifecycle source authority, old short-ref fixture and no write side effects. Do **not** use `same_ref` as a substitute for strict source binding because its acceptance of missing/short owner context is designed for a different comparison contract. Reuse the existing graph validation and native provider material proof rather than inventing a new ledger/issuer.

**Crucial number/origin limitation:** A bare repository-shape predicate (old or proposed) **cannot itself reject a syntactically valid but *different* PR number**: graph authority binds a particular number per selected leaf. The wrong-number rejection must be proved by existing **immutable graph custody + plan/input digest + provider observation of that exact graph-bound PR** (and, where appropriate, new native tests of changed graph vs pinned graph and graph/material mismatch); do not falsely call `repo#999` invalid if an *authorized released graph* actually binds PR #999. `source_bound_responsibility_core` must not silently trust a caller-altered graph. This distinction is review-critical.

## Isolated design sanity table (NON-NATIVE, no facts/CI admission)

Using the public original `programme.repository = reallaksh19/relay-v32-e2e-lab`, an isolated JavaScript reproduction of the intended **reference-shape** rule yielded **9/9 expected** outcomes; this is *not* the Python native engine or source-level acceptance:

| Input | Expected source-bound repo/shape | Reason |
| --- | --- | --- |
| `reallaksh19/relay-v32-e2e-lab#8` | accept | Actual leaf #4 full PR |
| `reallaksh19/relay-v32-e2e-lab#13` | accept | Actual leaf #5 full PR |
| `reallaksh19/relay-v32-e2e-lab#15` | accept | Actual leaf #6 full PR |
| `relay-v32-e2e-lab#8` | accept | Old short same-repository binding |
| `other/relay-v32-e2e-lab#8` | reject | Wrong owner but same basename |
| `reallaksh19/other-lab#8` | reject | Same owner, different repository |
| `#8` | reject | No explicit repository identity |
| `reallaksh19/relay-v32-e2e-lab##8` | reject | Malformed double number delimiter |
| `reallaksh19/relay-v32-e2e-lab#0` | reject | Invalid zero PR number |

**Native post-grant direct tests required:** Call real `validate_graph`, `project` and `source_bound_responsibility_core` on exact original pinned graph #4/#5/#6, with original actual provider observations and honest absence of current admitted facts; test positive source-format shape without claiming eligible E. Include historical `Common#...` short fixture, foreign-owner same basename, wrong repository, malformed refs, changed graph vs unchanged `projection.plan_digest`, different bound PR under source-pin drift, wrong selected leaf and digest, and unchanged P/E/D/input digest arithmetic. At new exact patch HEAD test on actual Python versions and run real relevant CI. Distinguish native unit tests from real original eligible `CHECKPOINT_FACTS_V1` evidence (currently absent).

## Outcome and next critical-path gate

**Proactive W03 implementation-readiness analysis COMPLETE** (a read-only preparation unit only; **W03 PARTIAL**). Existing #325 pending checklist remains authoritative. No duplicate patch, new PR/commit touching frozen source, issued facts, reviewer assignment, protected manifest merge, CI invocation or production writer. To implement, the two **actual independent reviews**, effective required CI policy, and separately authorized merge of #316 onto main must first be proven; then create native fix on an already-approved base and run the real test oracle above. W02 requires an independently selected issuer/evidence policy and genuine original positive/hostile source; no invented source facts or fabricated acceptance.

```text
Task: TAB1-G7-W03-PREP (read-only review-ready acceptance design; not a new planned W0n)
Goal (issue AC): Debottleneck post-grant native exact owner/repo#PR patch without bypassing frozen source boundary
Status: DONE for preparation / W03 product PARTIAL
Met: partial for preparation only; #325 T04 and #5 AC remain unmet
Done: Verified prior pending issue markers, native parse_ref/observe_github/project/core, identified number-vs-source-custody boundary and nine actual original/hostile form cases
Code: reallakshman19/Common main source blob 804cacca930e47c4528bb0d245efaf941996e4cf | governance PR #316@8f5a47dd DRAFT; no protected change
Tests: isolated JS source-format design -> 9/9 expected (NON-NATIVE); Python native original cases -> NOT_RUN
CI: NOT_RUN for this preparation; exact governance PR #316 workflows 6 success/1 skipped; required policy UNKNOWN
Evidence: This file; original lab graph blob fde7e1fbd0c71efb64a678206f0bc9f32e36f6c8
AC: programme #5 0/8 -> 0/8; issue #325 T04/T05 OPEN -> OPEN
Claim: INDEPENDENT provider source GET; LOCAL reference-shape sanity only; NONE for qualified original positive or independent review
Blocker: PERSON:two qualified independent reviewers; OWNER:D02/D03 eligible fact/CI policy; #316 independent governed merge/base-residency
Next: Apply minimal approved patch with tests only after governance grant is effective; W02 issuer and positive source separately
```
