# Evidence-based score rubric

All criterion ratings are benefit ratings on a fixed 1–5 scale: 1 = poor, 3 = adequate, 5 = strong. Invert raw cost, delay and risk before rating.

| Criterion | 1 | 3 | 5 | Preferred evidence |
|---|---|---|---|---|
| Development cost/time | Exceeds budget / long delay | Meets the baseline | Materially faster and cheaper at equivalent scope | Comparable hours, plan and dependency estimates |
| Maintainability | Coupled, unclear ownership | Manageable debt, usable tests | Modular, easy to change, well tested | Actual code and regression data |
| Performance/scalability | Fails SLO | Meets SLO | Verified operating headroom | Reproducible load tests and profiles |
| Technical risk | No credible rollback | Manageable migration | Low residual risk, exercised rollback | Test logs, security review and migration plan |
| Technology alignment | Violates platform policy | Partial alignment | Matches approved standards | Platform constraints and team capabilities |

Evidence classes:
- OBSERVED: reproducible, candidate-bound source, benchmark or test.
- ESTIMATED: documented assumptions, method and uncertainty.
- ASSUMED: illustrative scenario, not live decision evidence.
- UNKNOWN: do not force a score or claim eligibility.

Document the exact evidence source, decision configuration revision, criterion mapping and assessed commit where relevant. Never use comments or the fact that a test exists as proof that it passed. Hard requirements are eligibility gates outside the weighted sum; unresolved mandatory requirements must remain unresolved.

Test plausible alternative weight distributions. The illustrative sample has a cost crossover of 7/17 (approximately 41.17647%); that value applies only to those supplied scores and proportional rescaling. Do not treat it as a universal decision threshold.
