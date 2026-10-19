# Affected recheck of corrected prototype helpers

No unresolved findings remain within the two affected helper behaviors. IR-01 and IR-02 from the original `../findings.md` are resolved for the new file bindings below. The original report, manifest and failure receipts are preserved unchanged.

## New candidate binding

| File | SHA-256 |
|---|---|
| `scripts/review_records.py` | `e798793664730465db0c9c5f721a817eaa44c9b9bc582f038ef5f27e5f28764f` |
| `scripts/review.py` | `d9bb71768a41c92a92cf66a57fc80e7ad9703df1c5801c1234c75404b357496e` |
| `references/CONTRACTS.md` | `705065c97335b62eefda5c58edfe2f9565b816247e87de8fc82770f54eb85d53` |

`affected-manifest.json` also records both test-file hashes. All three supplied functional hashes matched the files read and executed for this recheck.

## Observed fix results

- **IR-01, duplicate candidate comparison:** the original schema-valid duplicate-issued-ID case now returns `SUBJECT: AMBIGUOUS_IDENTITY` and a scoped `DUPLICATE_ID` contradiction. CLI exit remains the declared advisory 0. Source inspection confirms both issued and observed duplicates enter the ambiguous set; the contracts document the new status. Exact receipts are in `duplicate-result.json`.
- **IR-02, symlink loop continuation:** the original direct three-record check now returns `MISMATCH`, `UNAVAILABLE`, `MATCH` in order. The CLI preserves the known mismatch and classifies the loop as unavailable, with exit 0 and no traceback. Source inspection confirms per-record `RuntimeError` handling and technical input handling at the CLI boundary. Exact receipts are in `loop-result.json`.

The local suite passed **29 tests**, including new regressions for duplicate issued/observed identities and symlink-loop continuation. It also checks command use without optional packages, both self-contained schemas, byte/path handling, binding and reference consistency, scoped PASS, self-review declarations and known-failure/NOT_RUN preservation. Command, exit code and input hashes are in `unit-tests.receipt.json`; complete test output is in `unit-tests.stderr.txt`.

The recheck used the preserved reproduction driver with a new output directory:

```bash
PYTHONPATH=/workspace/scratch/52eed2252c51/tmp/br20-deps \
  python -B /workspace/scratch/52eed2252c51/tmp/ir-prototype-review/reproduce.py \
  /workspace/scratch/52eed2252c51/tmp/ir-prototype-review/recheck-fixed
```

## Scope and independence

I reviewed the two corrections, contracts adjustment and relevant local tests, and reran the preserved counterexamples. I did not author these corrections, edit the package, inspect other agents' application returns, or review a later `examples/applications` archive/navigation addition. Prior package exposure and the earlier reported counterexamples are retained; this is an affected recheck, not a fresh blind application.

The finding set for this recheck is **empty**. This conclusion establishes the corrected local behaviors only. It creates no publication/release gate or new acceptance authority and supplies no actual AA3/LFEA/Writer2 acceptance or participant qualification evidence. The original scoped assessment of the standalone method remains in `../findings.md` with its original candidate limits.
