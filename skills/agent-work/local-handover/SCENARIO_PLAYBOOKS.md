# Short scenario playbooks — choose only relevant rows

Each row is a **prompt to verify**, not an assertion that it was tested. Original Owner requirements and discipline-specific rules take precedence.

| Scenario | First original/baseline to inspect | Actual witness to produce | Contrary/failure case that exposes an easy fake PASS |
|---|---|---|---|
| Software patch/repo | authorized base SHA, dirty status, lockfile and original tests | forward patch check, unchanged protected paths, before/after tests, exact commit | clean-base patch rejects, test passes only under stub, skipped pre-existing failure |
| UI/UX/web app | original design and live route, source data | pointer/keyboard trace, actual state, screenshots at tested viewport, consumer output | click counter is only a comment; enabled Export but no downloaded file |
| Data import/export | source bytes/schema/counts/units | row-level reconciliation, checksum, target-system readback, export bytes | duplicated/lost rows, altered original, wrong locale/unit |
| Database/migration | schema/version, backup, existing queries | dry run/transaction log, idempotence, rollback, target query | partial failure leaves committed writes; second run duplicates |
| Scientific/FEA/numerical | givens, units, boundary conditions, independent oracle | solver input and numeric output, sign/frame/end, residual/benchmark, caveats | answer matches one golden but violates conservation or another load case |
| Research/fact checking | original question, primary references/date | source-to-claim table and accessible citations, contradictory evidence | quoted secondary source fabricated, stale source presented as latest |
| Spreadsheet/analytics | original data, schema, formulas, expected totals | recalculation, totals/control sums, spot checked formulas, source→dashboard | chart looks right but source rows missing/formula #REF hidden |
| Document/report | source document, audience/coverage N, current best version | text/source comparison and *rendered* pages, layout/citations | missing section despite clean formatting; text-only check misses clipped pages |
| Educational content | blueprint demand/coverage N, material, best baseline | per-item content and demand checks, learner-target evidence where available | test passes by answer cues or shallow retrieval instead of required explanation |
| Design/media | licensed source, target brief/spec, editable requirement | viewed rendition + editable source where requested, size/crop/export | attractive preview but wrong dimensions or flattened/noneditable deliverable |
| API/integration | contract, auth/scope, fixed requests and known response | request/response with safe redactions, idempotence and failure status | mocked HTTP 200 masks broken real integration or privacy leak |
| Automation/operations | permissions, target state, schedule and rollback | dry-run/current-state/actual run receipts, reversible side effects | automation claimed active but not scheduled; wrong timezone or repeat action |
| Local-agent handoff | original Owner criteria, previous full return, exact incoming bytes | manifest/ZIP identity, candidate review, baseline+retest, new scoped assessment | 31/31 manifest green while source behavior or required criteria fail |
| Blocked or read-only investigation | question, already accessible evidence, actual tool capability | attempted command/error, limited finding and one unblock request | network/tool missing described as a successful product test |
| Parallel multi-agent | issued tasks and immutable return snapshots | task/candidate/review identity table, conflicting claims preserved | fresh worker has seen prior answer but claims blind independence |

For sensitive/high-stakes tasks, the local agent should not convert a quick check into regulated professional signoff. State the limits and seek appropriate authorized oversight when required by the actual domain.