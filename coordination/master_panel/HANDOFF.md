# M1 first-slice candidate handoff — Dash V2 #373

**Status: implementation candidate, not an acceptance claim.** Owner parent: [#360](https://github.com/reallakshman19/Common/issues/360), leaf: [#373](https://github.com/reallakshman19/Common/issues/373), Draft PR: [#377](https://github.com/reallakshman19/Common/pull/377). Source base: `7c1543a3e3ee5ba08314c20a4a70c1d94299476a`; use GitHub PR exact head (do not interpret moving `main` as replay qualification). Root AGENTS.md selects v3.2 policy. M1 C1 source/backend is the only edited responsibility; M2/M3 remain independent.

## Implemented (candidate code, all validation scope still to be established)

- M1-U01: `models.py`, `CONTRACT.md`, v1.0.0 typed source/identity/claim/independent-review/freshness/absence seam and fixture pair. Source basis `coordination/indexer.py`, `projections.py`, `contracts.py`, `command_service.py`.
- M1-U02: `github_source.py`, `storage.py`, `report_parser.py` plus focused tests. Bounded Common + AA3 GitHub issue/PR-as-issue/comment pages, exact repository identity, persistent per-source cursor, body revisions/edit/replay/reversion A→B→A, absence tombstone after completed scan and restoration. Structured 401/403/429/network failure remains per project. CASP report parser **only** exposes whitelisted reported identities; never registers provider assertions as trusted binding.
- M1-U03: `read_api.py`, `demo_fixture.py` plus focused tests. Loopback read-only `/api/master/v1/projects`, `/sources`, `/rows` with generation-bound cursor and sanitized reported metadata; no raw comment bodies, private route, token, browser-probe inference, command state or real SEND. Strict loopback Host/Origin; no cross-origin approval header.
- M1-U04: private command seam not enabled. Existing `command_service.py` has Owner-authenticated local submission but **no selected/authorized coordinator consumer**; C3a can only follow an actually selected private destination/authentication and the ordered observable-panel phase.

## Deterministic synthetic fixture profile — runnable, not live source parity

From repository root, *with the exact candidate checked out*:

```bash
python -m unittest coordination.tests.test_master_panel_contract -v
python -m unittest coordination.tests.test_master_panel_intake -v
python -m unittest coordination.tests.test_master_panel_report_parser -v
python -m unittest coordination.tests.test_master_panel_read_api -v
python -m unittest discover -s coordination/tests -v
python -m coordination.master_panel.demo_fixture --db /tmp/dash-m1-demo.sqlite
python -m coordination.master_panel.read_api --db /tmp/dash-m1-demo.sqlite --port 8777
# separate terminal; never publish private bearer tokens:
curl http://127.0.0.1:8777/api/master/v1/projects
curl http://127.0.0.1:8777/api/master/v1/sources
curl 'http://127.0.0.1:8777/api/master/v1/rows?project_id=common&limit=10'
```

Use a **fresh non-existing** SQLite path for the demo; existing data is not overwritten. Fixture values and commit SHAs inside fixture are synthetic, never current-head acceptance. At preparation, GitHub Actions `coordination-ci` Python 3.11/3.12 for PR #377 were QUEUED; **PASS NOT OBSERVED**, installed/live source parity NOT_RUN, workload load test NOT_RUN, M3 independent verification NOT_RUN. Read the latest exact-head job verdict before any review; unrelated path-scoped/skipped/old-head green is not acceptance.

## Known limitations to carry into qualified Codex corrections and M3 oracles

1. **C1 coverage still partial:** the scanner ingests issues, PR issue metadata and issue comments. PR detail/current-head checks and all relevant paginated check-run/job sources are not ingested or normalized into this new API. No live full Common/AA3 replay/CI applicability assertion.
2. **Attribution remains unbound by default:** CASP envelope reports are untrusted source claims, not authenticated provider registrations. Authorized registry bindings, independent reviewer sources, coordinator browser observations and evidence judgments must be supplied and tested through an explicit seam; no current full multi-agent operational truth from issue text alone.
3. **Page drift/restarts:** SQLite cursor persists during bounded partial scans, but GitHub page-number/issue changes can shift entries across pages between passes; full-scan deletion semantics require an independent stable-snapshot/drift safety qualification. Current unit tests are only static synthetic page fixtures; do not claim complete edit/delete proof for concurrent changing live GitHub.
4. **Private command C3a intentionally gated:** actual Owner-controlled private destination, authentication and coordinator consumption/readback receipt policy are not specified/verified. No real SEND, worker, dispatch or authority grant enabled.
5. **Validation/benchmark:** Python tests on exact submitted head, expected-value assertions and independent M3 negative scenarios must run before acceptance; **NOT_RUN** is never PASS. Do not infer liveness from public GitHub silence or upgrade self-reported PASS to independent review.
6. **Base drift:** `main` has moved since the M1 source pin. Qualified phase reviewer must perform exact-head base comparison/rebase applicability without rewriting the pinned source or changing protected project policy.

## One-writer/correction boundary

When M1 posts final handoff on issue #373, **M1 stops material writes** to PR #377 and all backend files. Codex alone owns corrections; independent M3 tests corrected exact heads and Codex performs qualified phase review/merge only with retained authority. M2 owns UI/C3b and does not modify backend during M1 writer phase. Do not merge/deploy, change workflow/AGENTS/skills/oracles, activate real SEND, expose private data or grant acceptance by waiving the above gaps.

Prepared as an M1 **partial first-slice handoff**, not a claim that C1/C3a or the complete Owner panel is accepted.
