# Worked recovery: source reuse and a disproved blocker

This is the synthetic six-file [local-recovery](local-recovery/issue.md) snapshot used in a fresh-agent exercise. It is intentionally incomplete and contains a demonstrated entry-point defect. It is not production code, an Owner approval, an engineering benchmark or a complete application.

**Owner outcome:** An older search response must not replace the current result; a current response must display normally.

**Direction:** IMPROVE by reusing the existing epoch guard. The first permitted diagnosis has actually run; product repair and browser acceptance remain NOT_RUN.

## Source and continuation proof

- [view.py](local-recovery/src/view.py) returns the payload without checking the response epoch.
- [core.py](local-recovery/src/core.py) already provides the missing equality guard.
- [cases.json](local-recovery/cases.json) specifies the two synthetic expectations.
- [previous_report.md](local-recovery/previous_report.md) says an authenticated checkout/browser is required and the guard is missing.
- [workreport.md](local-recovery/workreport.md) repeats the missing-guard claim and records SESSION-RESET as unresolved.

Fresh read-only execution of the actual supplied functions produced:

| Response epoch; current epoch 8 | Expected | Public `finish` | Existing helper |
|---|---|---|---|
| 7 | None | old: FAIL | None: PASS |
| 8 | new | new: PASS | new: PASS |

All six supplied files remained byte-identical. The public entry passes 1/2; the helper passes 2/2. Reproduce the documented fixture result with:

```sh
python -m unittest discover -s skills/buddy-runner-v2-0/tests -p 'test_goldens.py' -v
```

The executed diagnosis demonstrates a local failure boundary and reuse opportunity. It does not prove the asynchronous UI, cancellation behaviour or a repaired product. A helper returning None may still clear an accepted display if its consumer blindly assigns the return value.

## Reconstructed twelve-section view

| Section | Source-grounded content |
|---|---|
| 1. WHY | Preserve current results against late older responses; allow current responses |
| 2. Source identity | Six-file synthetic local snapshot; repository revision and migration history UNKNOWN |
| 3. Existing capability | Core guard exists; view bypasses it; authorship and actual writer ownership UNKNOWN |
| 4. Data flow | Epoch-bearing response reaches finish, which reads payload only |
| 5. Surviving choices | Preserve working epoch logic; loader rewrite has no demonstrated need |
| 6. Artifact authority | Local issue defines this read-only exercise; cases are synthetic expectations |
| 7. Execution | Fresh function experiment, exit 0; 1/2 versus 2/2; six unchanged files; no browser run |
| 8. Gaps | Entry bypass demonstrated; SESSION-RESET and actual result-assignment consumer unresolved |
| 9. ROI | Reuse guard: S, direct benefit, consumer risk; KEEP: XS but retains failure; rewrite: M/L without evidence |
| 10. Authority | Read-only experiment permitted; writes/publication not attempted because explicitly excluded |
| 11. Dependencies | Actual display/cancellation consumer and implementation scope needed for further product work |
| 12. Next start | Reproduce cases, inspect result assignment/reset, then bounded integration only under actual authority |

## Material dispositions and reporting separation

| Item | Disposition and basis |
|---|---|
| ENTRY-BYPASS | RETAIN: current entry returns stale payload |
| MISSING-GUARD | SUPERSEDED here: source helper exists and passes both supplied cases |
| NO-EXPERIMENT | SUPERSEDED here: the local non-mutating experiment ran without checkout authentication/browser |
| SESSION-RESET | RETAIN: relevant consumers are absent; no resolution proof |

Reconstruction is source-grounded, not independently semantically certified. Continuation is an actually executed diagnosis, not publication alone. Product repair and acceptance are unproven. Launcher configured model/effort observations must retain their backend-attestation limits; fixture prose does not establish anyone's model setting or implementation qualification.

The next bounded assignment should inspect the missing display/reset consumer and test whether ignoring stale responses preserves already accepted output. Do not ask a diagnosis-only deliverable to certify that the whole product has been repaired.
