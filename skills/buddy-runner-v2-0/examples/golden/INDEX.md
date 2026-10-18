# Golden workflow references

These ten cases are synthetic workflow references. Their declared expected outputs are regression oracles for report behaviour, not project goldens, live Owner grants, configuration attestations, engineering truth or product acceptance.

For a complete source-backed example, read [the worked recovery](WORKED_RECOVERY.md). Its six raw input/source files, two explicit expectations and observed result remain reproducible; the intentionally broken fixture is not an implementation to deploy.

Each JSON overlays `tests/support.py` base request/reconstruction shapes. `request_patch` and `record_patch` provide the scenario; `expected` was written explicitly, not generated from the implementation. `human_checks` identify semantic obligations that the automated test does not certify.

| Fixture | Scenario | Expected distinction |
|---|---|---|
| [01](01-recovery-probe.json) | Recovery runs a public-entry probe | Execution is reported; authenticity/acceptance are separate |
| [02](02-unsupported-blocker.json) | Checkout declared impossible without support | BLOCKER_UNSUPPORTED; require actual restriction evidence |
| [03](03-scoped-authority-restriction.json) | One write explicitly prohibited | No forbidden attempt required; preserve read-only alternatives |
| [04](04-onboard-awaiting-approval.json) | Reconstruction submitted | Normal Owner wait; unchanged full recovery reasoning |
| [05](05-onboard-approved-waiting.json) | Approved, no task | ONBOARDED_AWAITING_TASK; no old task/timer |
| [06](06-onboard-new-task.json) | Approved plus a different task | Actual new task governs; no automatic invocation |
| [07](07-profile-unverified.json) | Profile lacks observed evidence | Retain investigation; do not qualify the takeover |
| [08](08-stale-report-risk-retained.json) | Stale report corrected; risk retained | Source-backed dispositions without claiming universal risk coverage |
| [09](09-risk-omitted.json) | Declared material risk omitted | Surface the omission; no unrelated global stop |
| [10](10-publication-is-not-execution.json) | Reconstruction published only | Continuation remains NOT_STARTED |

Fixture `owner_source` data is interpreted by an explicit synthetic trusted-host seam in `tests/test_goldens.py`. Production JSON/CLI files cannot install that seam or authenticate those decisions. Do not copy fixture approval flags or model observations into real work as authority.

Run the reference suite with the existing native dependencies available:

```sh
python -m unittest discover -s skills/buddy-runner-v2-0/tests -p 'test_goldens.py' -v
```

Use the closest case as a comparison, not a prescribed route. A justified KEEP may outperform an improvement; an unrelated red CI may be irrelevant to the selected action. Genuine decisions and restrictions remain scoped to the actions they affect.
