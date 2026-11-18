# TA-IR-G01 — reciprocal challenge on saved occurrences (synthetic)

This is an executable local example, not a real NWv7 repair or independent agent run. All four native functions are in [candidates.py](candidates.py); the requirements are fixed below before candidate interpretation.

## Original contract (C0)

R1: Dismissing a suggestion never changes any durable saved/manual record or metadata.
R2: Dismiss only the exact identifiable occurrence, not another session sharing a URL.
R3: A missing, empty, whitespace-only or non-string target occurrence ID is not actionable; preserve all suggestions and saved records.
R4: Repeating a valid dismissal is idempotent; inputs are not mutated.

## A → B → A worked record

| Candidate / actor | Native contribution | Evidence / disposition |
| --- | --- | --- |
| C0 | URL-based removal from saved and suggestions | Same URL across two sessions deletes saved data and unrelated suggestions. |
| C1 — A | Preserve saved records | R1 improves; R2 still fails for two distinct IDs sharing URL. |
| B's source-first review of C1 | Expect distinct occurrence identities and construct opposite case | Frozen finding: C1 deletes E and manual suggestion when dismissing M. |
| C2 — B contributor | Filter suggestions by occurrence ID, preserve saved records | R1/R2 now pass for valid M; B's authored change is self-assessed. |
| A reciprocal review | Challenge missing target identity against R3 | C2 equates missing IDs and removes multiple unidentifiable suggestions. |
| C3 — A reconciles | Retain B's ID filter, add guard for unidentifiable target | R1–R4 pass for tested cases, including repeat and invalid targets. |

Run from the Tandem Execution directory:

```bash
python -m unittest discover -s tests -p 'test_tandem_ir.py' -v
```

A would publish final C3, not B. The synthetic contribution lineage is A_AND_B, with A's final guard and B's occurrence filter/negative control retained. Actual independence, real Drive transfer and product acceptance are NOT_RUN in this example. No third-agent gate or actual production access is implied.
