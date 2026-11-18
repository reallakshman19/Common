# TA-G02 — parallel implementation and convergence (synthetic)

This is the stronger default execution pattern. It uses the original synthetic [raw requirements](../golden/RAW_CASE.md): repeated observations of the same scheduled occurrence collapse; distinct sessions sharing a URL survive; dismissing an ephemeral suggestion never deletes saved records or a sibling suggestion. No real NWv7 code, private records or actual Drive transfers are used.

## 1. Common base and independent fixes

C0 is [baseline.py](../golden/baseline.py). Both agents receive it simultaneously. A fixes the merge boundary in [candidate_a.py](../golden/candidate_a.py) (A1), B fixes the dismissal boundary in [candidate_b1.py](candidate_b1.py) (B1). B1 imports neither A1 nor its code. Both modify the same conceptual application file in separate workspaces. Each correction is native executable code, not a review comment. A1 still deletes saved siblings; B1 still merges different occurrences by URL. The incomplete intermediate snapshots illustrate complementary repair, not a rule to leave known defects deliberately.

## 2. Final convergence

B has its own working repair even if A has not uploaded. When A1 becomes available, B compares both to C0 and selects the occurrence-aware merge from A1 and suggestion-only dismissal from B1 in [candidate_b.py](../golden/candidate_b.py) (C2). B checks the combined boundary: feed retains two sessions and dismissing one leaves the other and all saved records.

| Observable | C0 | A1 | B1 | C2 |
| --- | --- | --- | --- | --- |
| Distinct scheduled sessions | 1 | 2 | 1 | 2 |
| Exact duplicate collapsed | yes | yes | yes | yes |
| Saved records after dismissal | 1/3 | 1/3 | 3/3 | 3/3 |
| Sibling suggestion remains | no | no | yes | yes |

A textual merge is not the acceptance criterion; final behavior is. B1 can be executed and delivered without importing A1. B may independently reconstruct the missing occurrence fix from original requirements if A never arrives. That fallback has the same tested behavior but B-only lineage, not fictitious A authorship.

## 3. Adverse execution conditions

The executable reference in [convergence.py](../../tools/convergence.py) separates permission to keep working from what may be reported about final lineage. Tests cover B-first, A absent, missing marker with recoverable bytes, unverified A, actual both-candidate reconciliation, incomplete combined work, late A after final and serial opt-in. It is an offline policy illustration, not a scheduler or authorization mechanism.

Run `python -m unittest discover -s tests -v` from the skill root. [test_parallel.py](../../tests/test_parallel.py) imports the actual four Python implementations and checks the contrast above and missing-peer outcomes. Existing TA-G01 tests remain as serial evidence.

## 4. Real transfer shape

A uploads A1 and A-READY; B uploads B1 independently, then reads available A1. If A1 is absent at final boundary, B finishes B-only; if A1 arrives before boundary, compare and retain useful work. Both candidates remain immutable; B alone publishes final. Example paths/IDs are not real uploads. No routine B→A repair cycle, no artificial blocker, no fictitious independent acceptance.
