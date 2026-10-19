# Reconcile evidence without losing the project

Let the available lead, Owner or reviewer hold this responsibility. Do not require
an Oracle role or another participant merely to reconcile a small review.

Read the actual return and cited artifacts. Separate receipt/format checks from
technical support. Retain the reviewer's original findings and verdict; record the
consumer's acceptance, disagreement or additional evidence alongside them. Never
rewrite a historical review as if the reviewer assessed a later candidate.

Record concisely in the existing project record:

- Reviewed task and exact candidate(s); current observations and their time/source.
- Claims supported or contradicted, with evidence and remaining uncertainty.
- Findings accepted, disputed or superseded and the reason for each material choice.
- Affected work/dependencies, integration still needed and the next useful actor/action.

Use these responses selectively:

| New information | Response |
|---|---|
| Candidate/base/input changed | Compare the changed surface with reviewed claims and dependency assumptions. Keep old evidence attached to the old subject; justify any reuse. An unchanged file alone may still depend on changed integration. |
| One resource inaccessible | Preserve valid checks; state attempted action, observed restriction, affected scope and next feasible route. A complete reconstruction is not execution of the repair. |
| Known defect and an unavailable test | Retain both; never flatten the defect into UNKNOWN or the missing test into FAIL. |
| Wrong test oracle/premise | Preserve execution evidence; route correction of the contested authority under existing permissions. More runs of the same oracle do not settle the premise. |
| Components pass but journey fails | Keep component results; investigate the integrated user outcome. |
| Reviewers disagree | Compare observations, assumptions, methods and scope. A reproducible counterexample is not outvoted by several unsupported PASS labels. |
| Unrelated useful issue discovered | Record a source-backed finding/proposal; create separate work only within actual authority. |
| No consequential defect found | Accept an empty finding set if evidence supports it; do not manufacture novelty. |

Reopen only affected claims/tasks plus relevant integration consumers. Use an
existing Task Decomposer impact operation if selected; it cannot discover every
undeclared semantic dependency. For a long project, keep original intent and
deferred outcomes linked rather than sending every worker the entire history.

Review verdicts inform existing acceptance and release authority. This module
neither creates a merge gate nor treats PASS as a release command. Missing coverage
should lead to an honest scoped result and useful continuation, not a global stop.
