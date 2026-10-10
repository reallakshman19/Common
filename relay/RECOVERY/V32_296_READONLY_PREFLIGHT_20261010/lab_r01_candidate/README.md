# B2 preparatory R01 CSV input candidate — NOT the authorized lab product

**Programme:** [Common #285](https://github.com/reallakshman19/Common/issues/285) P2.1; **work coordinator:** [Common #296](https://github.com/reallakshman19/Common/issues/296); **historical lab:** `reallaksh19/relay-v32-e2e-lab` (currently GitHub 404 to connected identity).

This tiny module is a **new, assistant-authored reconstruction** of the *described* R01 obligation, deliberately confined to the already scoped #296 prototype recovery PR. It is **not** the previously precommitted starter package, the old lab `src/csv_auditor/parser.py`, a released V3.2 leaf, an Owner-approved scope amendment, or positive evidence under DELP. There is no real product R01 PR or accepted `TASK_EVIDENCE` yet.

## Observable local contract

The parent #282/#285 names R01 **ID/header/duplicates** and asks it to preserve valid CSV values. The original starter ZIP `relay-v32-e2e-lab-starter.zip`, with original nine RED application cases, has *not* been retrieved or verified. The following locally specified behavior is consequently **provisional**, not a claim of exact historical acceptance compatibility.

- A string CSV input must contain one header row and exactly one `id` field, with unique, non-empty column names.
- Each data row must have exactly the declared field count and a nonblank `id`; identical, case-sensitive IDs may occur only once.
- CSV quoting, commas, embedded line breaks, value strings and the order of rows survive parsing into Python dictionaries; original byte-for-byte quoting is **not** preserved, and such byte fidelity is **not** claimed.
- Invalid inputs raise `CsvInputError` with explicit codes: `INPUT_TEXT_REQUIRED`, `MISSING_HEADER`, `EMPTY_HEADER_COLUMN`, `DUPLICATE_HEADER`, `MISSING_ID_COLUMN`, `ROW_WIDTH_MISMATCH`, `EMPTY_ID`, `DUPLICATE_ID`, `MALFORMED_CSV`.
- No file/network/GitHub access, writes, progress scores, candidate SHA selection, false CI facts, issue publication or Owner release occurs in this module.

**Preparatory tests:** `../tests/test_lab_r01_candidate.py` has ten new assertions, grouped to mirror U01 (ID unique/nonblank), U02 (header shape), U03 (fidelity + malformed/width rejection). These tests are **not** the original nine staged application tests. The old zip's exact test names/assertions/API were not available to check for compliance. A passing suite can prove only this preparatory contract.

**Actual RED→GREEN experiment:** first commit the test alone and retain the exact-HEAD GitHub Actions failure (`ModuleNotFoundError: No module named 'csv_input'`); then commit the implementation and run the same tests at the new exact HEAD. Do not call a green Common auxiliary suite an original lab PR/CI qualification.

## Required migration into a real lab

1. Restore access to the historical private lab **and** separately authenticate T05 Owner approval, or explicitly authorize a distinct disposable lab with real repo/root/leaf IDs and separated human/agent identity.
2. Retrieve and pin the **original** `relay-v32-e2e-lab-starter.zip` by original documented SHA256 `9f1c317494168bda0ea83baf31c5a6db4d6035085c102743b22c707c3f4a5030`, verify manifest/fixture contents and unchanged original nine test assertions.
3. On real lab `lab/r01`, run the authentic original R01 RED baseline. Compare its exact public parser API and semantic outcomes with this preparatory module. **Adapt product code, not precommitted original tests**, and use actual lab write scope only.
4. Commit R01 source to its declared lab `src/csv_auditor/parser.py` surface, open an actual lab PR and confirm executed HEAD CI. Publish real START/END `TASK_EVIDENCE`; have independently adopted evidence producer verify HEAD, comment source, run/job, required CI and original acceptance. No self-issued verified facts.
5. Only after eligible `CHECKPOINT_FACTS_V1`, reuse unchanged native DELP, guarded lab-only issue/PR publishing and source-bound C6. Production remains V3.1 pending separate #289 gates.

**State until migration:** `PREPARATORY_CODE_ONLY`; parent #285 G1–G5 **PENDING**; accepted evidence `null`; writer `OFF`.
