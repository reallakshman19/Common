# Candidate validation receipt — 2026-10-13

Basis: Common main `e9a08282b2f75db14b00cf18479c99a7bbfa2a6a` plus this additive package. The PR's exact head identifies the candidate; this receipt does not claim main adoption.

Environment: local Windows, bundled Python 3.12.14. No real agent session was registered or activated for these checks.

| Check | Actual result | Limit |
|---|---|---|
| `tools/casp.py demo` | PASS: four sessions, two projects, four correlated exchanges | Fictional offline data; live source authentication and delivery NOT_RUN |
| `python -m unittest discover -s coordination/session-protocol/tests -v` | 20 tests passed | Offline contracts/CLI; no durable intake or live provider execution |
| `python -m unittest discover -s coordination/tests -v` | 121 tests run: 116 passed, five skips, zero failures | Four Windows symlink privilege skips; one dedicated Windows PowerShell job-only class skipped |
| Independent `jsonschema.Draft202012Validator` | Four schemas well-formed; four session and eight message fixtures accepted | Independent schema engine, not an independent engineering reviewer; semantic checks require CASP helper/project policy |

Existing runtime queue, dashboard and engineering policy implementation files are unchanged. The existing coordination CI discovers the package through one additive test wrapper. The workflow example remains outside `.github/workflows` and has no write operation. Hosted CI status must be read from the actual PR head; local checks do not claim hosted PASS.

Not executed/implemented here: private mailbox setup, authenticated intake, live edit/delete delivery, durable admission/replay, real SEND, multi-worker fencing, live rate-limit/crash tests, project acceptance, deployment or merge. These remain explicit integration requirements in CONFORMANCE.md.
