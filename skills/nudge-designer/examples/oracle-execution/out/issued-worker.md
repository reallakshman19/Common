# Issued task-local repair — N-REPAIR / T-SESSION

Purpose: users must not see an older search overwrite the newer view, including
when they return to a previous project filter. Cancellation must stay idle and
empty after late callbacks. Repair the component and add focused regressions.

Inputs: read raw/owner.md, raw/access.md, raw/session.py, raw/test_existing.py and
work/session.py in this episode. Original source/candidate SHA-256 at assignment:
316b565738204bab3c81b6e2143d7bedaa3d8b13bcacf9960dde07c7deb03512.
Neutral design: out/task-design.md, map search-session-map r1, T-SESSION.
The Oracle supplied the model/method below; you need no previous conversation.

One deliverable: repair work/session.py, add work/test_regression.py, and save
out/worker-return.md plus any out/worker-* check evidence. Keep raw/ and
raw-manifest.json byte-identical. Write no other paths. No network, browser, app,
live repository or external message work. Do not edit the Oracle probe/plans.
Read no unrelated output, examples, goldens, verification archive or other episode.

GUIDED method and WHY: source inspection and Oracle execution established that
tickets already contain an increasing sequence but the callbacks check only
scope. Four existing tests pass, yet ten event-order witnesses fail. Project
scope alone cannot distinguish old/new operations within A or after A→B→A.
The latest begin owns the view; cancel revokes that ownership. A stale or
cancelled success/error callback must return False and leave the full snapshot
unchanged, even while the current request is busy or after it has completed.
Maintain operation identity over begin/cancel, check it consistently in finish
and fail, and preserve signatures, current success/error behavior, scope/query
metadata, deep copying, and ranked rows in their supplied order.

Evidence: add focused checks with both finish and fail for same-scope supersession,
A→B→A, cancel→late callback, cancel→begin→old callback, and valid success/current
error after reuse. Check intermediate snapshots and return values, not just final
rows. Run `python -B raw/test_existing.py -v` from the episode root and run your
new checks. Preserve a contrast that fails on raw/session.py if useful; do not
weaken existing assertions or sort rows. Oracle will rerun its prewritten checks
against your actual source after inspecting your return.

Boundaries and uncertainty: Oracle retains the state model, scope decisions and
integrated acceptance. Malformed/forged/cross-session tickets, reentrant/multithread
callbacks and duplicate terminal delivery semantics are outside this repair.
If a required input or instruction fails, report the specific restriction and
retain useful work; do not invent a global blocker or expand scope.

Return: concise native Markdown at out/worker-return.md identifying changed files,
actual commands/results, concise decision basis, assistance and unreviewed limits.
Describe artifact provenance as ADAPTED from raw/session.py and self-check verdicts
as SELF-ASSESSED. Actual effective model/reasoning configuration is UNKNOWN unless
the host truly exposes it; do not infer it from your role. Return a short final
receipt pointing to your report. This is task-context isolation with shared
workspace permissions, not verified blinding or an independent model benchmark.
