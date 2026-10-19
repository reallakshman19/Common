# Worker return — T-SESSION

SELF-ASSESSED: the bounded repair passes the existing checks and focused local regressions. Integrated acceptance remains with the Oracle.

Changed `work/session.py`, ADAPTED from `raw/session.py` (original SHA-256 `316b565738204bab3c81b6e2143d7bedaa3d8b13bcacf9960dde07c7deb03512`). Both `finish` and `fail` now require the ticket's scope and sequence to match the current operation. `cancel` advances that sequence, revoking earlier tickets while retaining scope/query metadata. Signatures, ranked row order, deep copying, success/error state updates and current terminal-delivery behavior remain as supplied. Inspection confirmed the issued diagnosis; no change of method was needed.

Added `work/test_regression.py`, authored for this task. It checks both callback types for same-scope supersession, A→B→A, cancellation followed by late callbacks, and cancellation followed by reuse. Assertions cover exact Boolean returns and full snapshots while current work is busy and after success/error. Reuse checks also exercise current success, current errors, recovery, nested copy isolation and unsorted ranked rows.

Commands executed from the episode root:

| Command | Actual result |
| --- | --- |
| `python -B raw/test_existing.py -v` | Exit 0; 4 tests passed. |
| `python -B work/test_regression.py -v` | Exit 0; 10 tests passed against `work/session.py`. |
| `SEARCH_SESSION_SOURCE=raw/session.py python -B work/test_regression.py -v` | Exit 1, expected contrast; all 10 test methods expose defects, with 16 failures including subtests. |

Native stdout/stderr are retained in `out/worker-existing.*.txt`, `out/worker-regression.*.txt` and `out/worker-raw-contrast.*.txt`. `out/worker-session.diff` records the source change. Before/after SHA-256 comparison passed for the four designated raw inputs and `raw-manifest.json`; see `out/worker-input-hashes.json` and `out/worker-integrity.json`. No protected input was edited.

Assistance: the Oracle supplied the ownership model, guided method and task-local design. This worker implemented the patch and tests without additional agents, network, browser, app or external messages. Actual effective model/reasoning configuration is UNKNOWN. This is task-context isolation in a shared workspace, not verified blinding or an independent model benchmark.

Unreviewed limits: Oracle probes and integrated acceptance were not run or read by this worker. Malformed/forged/cross-session tickets, reentrant/multithread callbacks and duplicate terminal delivery semantics remain outside this repair. These local checks establish no live UI or production behavior.
