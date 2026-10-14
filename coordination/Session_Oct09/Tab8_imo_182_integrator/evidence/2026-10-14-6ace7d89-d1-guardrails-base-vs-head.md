# D1 r6-00 guardrails failure-ID delta: #228 base vs #231 current head

**Prepared:** 2026-10-14 UTC. **Chat:** `6ace7d89`. **Issue:** [#200](https://github.com/reallakshman19/Grade9v3.5/issues/200). **State:** analytical read-only CI evidence; **not** an approved gate exception.

## Precise compared heads

| | Immediate base | Current head |
|---|---|---|
| Draft | [#228](https://github.com/reallakshman19/Grade9v3.5/pull/228) | [#231](https://github.com/reallakshman19/Grade9v3.5/pull/231) |
| Commit | `b1839f692ce0a47985d794f093d5dc945a522229` | `a924eeb518c3aba035cd5320a0f76b3cf3c6823f` |
| Guardrails run | [38485239547](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38485239547) | [38489492978](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38489492978) |
| Guardrails job ID | `115597165129` | `115611065033` |
| Job result | **FAILED** | **FAILED** |
| Tests executed | **2957** | **2959** |
| Failing tests | **119 FAIL + 34 ERROR = 153** | **119 FAIL + 34 ERROR = 153** |
| Skipped | **7** | **7** |
| New exact failure entries on head | – | **0** |
| Removed exact failure entries on head | – | **0** |

### Method

- Fetched both complete **GitHub Actions raw job logs**, not only run summaries, using job IDs above.
- Extracted each line matching `FAIL: test_...` or `ERROR: test_...`, including the full `test_module.Class.method` identity and FAIL/ERROR severity. Deduplicated exact entries, compared both directions.
- Found **153/153 identical FAIL/ERROR entries**, no additions/removals. Python runner summary exact: base `Ran 2957 tests ... FAILED (failures=119, errors=34, skipped=7)`; head `Ran 2959 tests ... FAILED (failures=119, errors=34, skipped=7)`. This is a *strict scoped identification of no new failing tests across this pair*, not proof of error-message equality or absence of all integration regressions.
- New head #231 includes evidence cross-record and academic packet regression tests; those did **not** create an additional named guardrail failure in this job.

### Other exact-head gate evidence and limits

- At head `a924eeb`, D1 scoped reviewer run [38489493068](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38489493068) **SUCCESS**; learner-platform code tests, v31 relay and SOF seed integrity also **SUCCESS**.
- Guardrails **still FAIL**. The canonical [run 38489492996](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38489492996) had **Assurance (no worse than baseline) FAILURE** and **Regression delta (exact test ids) IN_PROGRESS** at this readback. On base #228, canonical run [38485239380](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38485239380) **FAILED**. Exact canonical delta needs its final provider job output before independent attribution.
- This comparison is **not** against `main`, nor a whole-branch merge graph. It does not retest source maths, actual hosted 6-HTML ZIP SHA, reviewer competence, academic W or Owner QRT status. Do not rename two red jobs as green or disable strict enforcement.
- **No Owner QRT acceptance**, no global release, no merge, no Q003 original source rights or frozen golden change.

## Next control point

Once the canonical exact-test-ID job finishes, capture its precise ID and base-relative failure sets. If new failures are attributable to #231, isolate the specific test/data/CI cause and correct only the measured defect. If results match inherited baseline, retain FAILED gate and request appropriate scoped Owner merge disposition only after all explicit gates and academic conditions; **no waiver implied**.

LOG | Outcome=guardrails head/base raw-log exact-ID comparison 153/153 identical, 0 added/removed | For the user=truthful inherited-name evidence without green badge | Proof=two exact job IDs/log summaries | Open=canonical exact-delta/whole gate and qualified reviewer/Owner acceptance.
