# Estimator review

Review `inputs/rate.py` against the Owner's rule in `inputs/owner.md`. Use the
participants and tools available. Show evidence, limitations and the next useful
action.

**Verdict: FAIL against the stated rule.** One reproducible correctness finding
remains. The review is complete for the supplied estimator and request; it is not
an assertion of Owner acceptance. No input artifact was edited or published.

## Finding F1 — Delivery incorrectly triggers the item discount

**Major correctness defect, `inputs/rate.py:4`.** The condition is
`subtotal + delivery >= 10000`. The Owner explicitly requires the item subtotal
alone to reach 10000 cents and says delivery never counts toward that threshold.

| Inputs `(subtotal, delivery)` | Required result, cents | Observed result, cents | Evidence label |
| --- | ---: | ---: | --- |
| `(9999, 0)` | 9999 | 9999 | `below_threshold_no_delivery` |
| `(9999, 1)` | 10000 | 9001 | `delivery_one_crosses_threshold` |
| `(9000, 999)` | 9999 | 9999 | `delivery_just_below_crossing` |
| `(9000, 1000)` | 10000 | 9100 | `delivery_hits_threshold` |
| `(4000, 6000)` | 10000 | 9600 | `small_items_large_delivery` |

For `(9999, 1)`, the item subtotal is below 10000, so there is no discount and the
answer must be `9999 + 1 = 10000`. The candidate instead discounts
`9999 // 10 = 999` cents, producing 9001. Increasing delivery by one cent thus
reduces this estimate by 998 cents.

For valid built-in integer inputs, the incorrect-output region is exactly
`10 <= subtotal < 10000` and `delivery >= 10000 - subtotal`. The estimate is too low
by `subtotal // 10`, up to 999 cents. Subtotals 0 through 9 can take the same wrong
branch but the zero-cent rounded discount masks the error. This characterization
comes from inspecting the two formulas; the finite sweep corroborates it.

**Next useful action:** Have the estimator's author change the eligibility
condition to `subtotal >= 10000`, retaining integer discount rounding and final
delivery addition. Add a regression for `(9999, 1) -> 10000` and an adjacent
non-crossing case, then rerun the existing and saved checks against the changed
candidate. This review did not make that repair.

## Authority, binding and method

The sole behavioral authority was the original request in `inputs/owner.md`:
nonnegative integer cents, booleans rejected, item-only threshold of 10000,
10% discount rounded down, delivery added after that decision. The implementation
and existing tests were inspected as evidence, not used to define the rule.

These are the SHA-256 hashes actually computed from the read input bytes. The
check script recomputed them after execution and reported all three unchanged.

| File | SHA-256 |
| --- | --- |
| `inputs/owner.md` | `52af62ddd92b4d0a061a2724b624921f3d00f2aa4dd42f7907f243737d20fd32` |
| `inputs/rate.py` | `d8124e99da3e6bdc1db4fdf9b0b4c4f545704c4b6381a878d140b1be45627829` |
| `inputs/test_rate.py` | `680a2296cc580466419170ffce870ef2a960c03aa94ade4cf2e0f8c71f6dcc01` |

I read the Owner request before reading the candidate and tests, deriving the
item-only threshold, integer floor rounding and invalid-input expectations from
that request. I then inspected all five candidate lines and every existing test.
The saved checks use both hand-derived concrete expected values and an integer
formula derived from the Owner request. The deliberate contrary condition is a
below-threshold subtotal whose delivery brings the combined amount to 10000.

## Actual execution and evidence

Executed in the supplied workspace with Python 3.12.14 on Linux, using `-B` and
`PYTHONDONTWRITEBYTECODE=1` so the input directory needed no bytecode writes:

```text
python -B /workspace/scratch/52eed2252c51/tmp/ir-forward/direct/out/check_review.py > /workspace/scratch/52eed2252c51/tmp/ir-forward/direct/out/check.log 2>&1
```

The script imports the exact candidate by absolute path. It also actually ran the
existing suite in the input directory using the same interpreter with
`-B -m unittest -v test_rate`. Its exit was 0: all three existing tests passed.
The overall review script exited 1 because the additional requirement checks
found mismatches; this is a recorded failing review result, not a missing run.

| Executed check group | Passed | Failed | What it checks |
| --- | ---: | ---: | --- |
| Existing unittest methods | 3 | 0 | Existing large/small cases and three invalid subtotal values |
| Concrete requirement cases | 12 | 4 | Zero, delivery crossing, item threshold, rounding steps |
| Large integer case | 1 | 0 | Exact arithmetic at `10**100 + 9`, delivery 37 |
| Boundary sweep | 744 | 273 | 1017 pairs across 87 subtotals, delivery and threshold boundaries |
| Invalid arguments | 24 | 0 | Each of 12 invalid values in each argument position |

The 1058 additional checks contain 277 failures, all explained by F1. Some cases
overlap between groups; these counts are observations, not separate defects or
independent replications. The invalid set was `-1`, `-10000`, `0.0`, `0.5`,
`True`, `False`, `None`, `"10000"`, `[1]`, `1+0j`, NaN and infinity. Each was
rejected with `ValueError` in both the subtotal and delivery positions.

Preserved witnesses, all in this report's directory:

- `check_review.py`: full disposable check source and reproduction command target.
- `check.log`: actual interpreter/platform, existing-suite output, counts,
  concrete observations, sample sweep failures and before/after hashes.
- `check_evidence.json`: every additional check's inputs, expectation and observed
  result or exception, plus original-suite output and input binding.

## Coverage and limits

| Owner requirement | Assessment | Basis |
| --- | --- | --- |
| Discount only if items reach 10000 | Contradicted | F1, concrete crossing witnesses and boundary sweep |
| Round 10% discount down to cents | Supported for eligible built-in integers | `subtotal // 10` is exact floor arithmetic; item threshold, fractional-cent cases and a large integer passed |
| Delivery never changes eligibility | Contradicted | Delivery-dependent branch; adjacent crossing witnesses |
| Add delivery after item discount | Arithmetic supported; overall rule fails | Return expression does add delivery last, but F1 makes the selected discount wrong |
| Reject negatives and non-integers, including booleans | Supported in inspected implementation and tested values | Type/nonnegative guard, plus 24 rejection observations |
| Return integer cents | Supported for the valid built-in integer domain inspected | Integer-only operations and all valid executed observations |

The existing suite misses the defect because its valid cases put both the item
subtotal and combined total on the same side of the threshold. It also tests
invalid subtotal inputs only, with no delivery crossing or rounding-boundary
assertion. Passing those tests cannot establish the Owner's complete rule.

This assessment covers the supplied Python function, its input validation and
local tests. The finite sweep is not exhaustive execution of all integers; static
reasoning supports the stated failure region. No caller, deployment, external
consumer or broader system was supplied or assessed. Integer subclass or
third-party numeric-scalar policy is unspecified and was not separately decided.
There was no author claim, release receipt or broader acceptance claim to verify.

## Independence, access and assistance

This was one available participant performing a DIRECT review, interpretation and
execution. I wrote the disposable checks and this report; I did not contribute to
or alter the candidate during this assignment. Candidate authorship and any
relationship to its original producer were not supplied, so distinct-principal
independence is **UNKNOWN**, not certified by this review.

My exposure includes the assignment, visible conversation and the three supplied
task-local inputs. I read candidate and existing tests before writing the check
script; the expected behavior was derived from the Owner text rather than author
assertions. The oracle legitimately shares that authoritative source with the
implementation, and the concrete witnesses make its threshold interpretation
reviewable. No second reviewer, outside execution or independent Owner acceptance
is claimed. Workspace isolation from other files was not established or claimed.

Actual material read: `inputs/owner.md`, `inputs/rate.py`,
`inputs/test_rate.py`, the independent-review `SKILL.md`, and its
`references/INDEPENDENCE.md` and `references/APPLYING_GUIDANCE.md`; I also read the
produced execution log. No golden examples, other agents' work or unrelated
project history were consulted. No packaged review helpers or other participants
were used.

No assistance was needed to complete the scoped review. The next action requires
the estimator author to repair F1 and submit the changed candidate for affected
checks; that repair and acceptance remain outstanding.
