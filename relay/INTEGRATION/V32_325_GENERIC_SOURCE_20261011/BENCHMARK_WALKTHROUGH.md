# BENCHMARK V1 — Five production HOLDS, reproducible source-first walkthrough

**Scope:** Common #325 → #289 → #5; chat `6acae92b`; comparison repository `reallakshman19/Common`. This is an **engineering acceptance benchmark**, **not** a throughput or performance benchmark, real positive CHECKPOINT_FACTS, qualified review, Owner-signed graph, production release, or no-chat Agent B. **User supplied no authentic private lab file.** The historical graph is deliberately cloned into a fake repository. The CLI uses **NO network, NO write methods and NO secrets**.

**Run from repository root (with PyYAML and jsonschema installed):**

    python -m pip install PyYAML jsonschema
    python relay/INTEGRATION/V32_325_GENERIC_SOURCE_20261011/benchmark_walkthrough.py > /tmp/v32-325-benchmark-synthetic.json
    python -m unittest discover -s relay/INTEGRATION/V32_325_GENERIC_SOURCE_20261011 -p 'test_*.py' -v
    python -m json.tool /tmp/v32-325-benchmark-synthetic.json

CI: the existing `.github/workflows/v32-325-generic-source-preflight.yml` runs the `test_*.py` suite on Python 3.11, 3.12 and 3.13. Use its **exact benchmark-branch HEAD**, not the CI from an earlier #326 head. The first command's JSON is a local user-generated transcript; do not describe it as a provider-issued/cryptographically attested result.

## Fixture provenance / acceptance baseline

- Existing *historical* native released graph: `.github/v32-evidence-spine/718-proposal-v2.json`, Git blob `d35019b416cb3b573280e166027d3f65ba61f59c` at benchmark starting source commit `6b138b63d4347500a4fba2cad59f1fcfed0bfaf2`. Source repo inside file is `reallaksh19/Common`, **not** current repo. The test helper `fixture_graph()` replaces strings with `example/Pipeline`, graph root `Pipeline#718`, leaf `Pipeline#733`, selected PR `Pipeline#740`.
- Synthetic candidate commit `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`; synthetic base `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`; pinned graph revision `9999999999999999999999999999999999999999`. They are arbitrary test identifiers, **not real commits**.
- T01/T02/T03 existing modules and fixture classes: `generic_source_preflight.py`, `generic_current_source.py`, `generic_publication_plan.py`, `test_generic_source_preflight.py`, `test_current_source_reconciliation.py`, `test_publication_plan.py`. Public response-shape replay: `test_rest_readonly_provider.py`, with **sanitized** #5/#325/#326 metadata and artificial bodies. All of these are reused; this benchmark does **not** fork native P/E/D/DE math or build another publisher.
- New actual benchmark runner: `benchmark_walkthrough.py`, machine-output record `v32-325-synthetic-benchmark-v1`; regression `test_benchmark_walkthrough.py`. No secrets, original Owner lab file or external benchmark dataset.
- Original private-lab input `reallaksh19/relay-v32-e2e-lab` — **NOT_AVAILABLE/NOT_TESTED**, no file path, bytes or sha256 attested. Current new-repo signed Owner graph — **NOT_ISSUED by this benchmark**. External required check / two independent reviewer identities — **UNVERIFIED**.

## Step-by-step cases (each must match an exact oracle)

| Case | Action through existing code | Expected signal | Production HOLD illustrated |
|---|---|---|---|
| B01 | T02 current source/graph double-read and native empty ledger | `READ_ONLY_RECONCILED_UNATTESTED` | G1 original Owner graph not authenticated |
| B02 | Deliberately replace current graph bytes | `SOURCE_GRAPH_NOT_CURRENT_RELEASED` | G1 graph provenance guard |
| B03 | Inject unauthorized `CHECKPOINT_FACTS_V1` from `stranger` into native ledger | Rejected fact; native E = 0 | G2 independent fact issuer/review |
| B04 | Change selected PR head between provider reads | `PROVIDER_MOVED_DURING_READ` | G2 candidate source currentness |
| B05 | Change leaf primary PR to full same-repo `example/Pipeline#740` | `NATIVE_RESPONSIBILITY_CORE_MATERIAL_BOUNDARY` | G3 protected native identity integration |
| B06 | Compute root+leaf+PR managed-content plan from native projection | `PLAN_ONLY_UNATTESTED`, original human bodies preserved, `writes=0` | G4 no live publication |
| B07 | Simulate just the leaf surface matching after plan | `INCOMPLETE_SYNC` | G4 partial GitHub failure must not be silent |
| B08 | Simulate all surfaces and native LIVE_STATUS matching | `OBSERVED_MATCH_NOT_AUTHORIZATION` | G4 simulated readback is never a real write grant |
| B09 | Simulate merged PR but no custody controller | `NO_AUTOMATIC_SUCCESSOR` | G5 independent Agent B not run |
| B10 | Normalize sanitized public GitHub GET envelope | `SANITIZED_REPLAY_SHAPE_VALID` | G1/G2 response compatibility ≠ Owner identity |

**PASS definition:** all **10 synthetic/negative scenarios** match their exact oracles; 5 distinct **production gates remain HOLD**; Owner AC stays **0/8**; `writes=0`; `ready_for_production=false`; all `source_authenticated` and `production_authorized` flags false where present. Any unexpected acceptance/crash/writer presence must make the benchmark RED. **Do not count a deliberate HOLD as production failure or as completed Owner AC.**

## How to move from this benchmark to a real end-to-end qualification (five Owner-facing actions)

1. **G1 (Owner/source):** Select/create a *candidate* new-repo graph derived from actual current Owner #5/#289/#325 approved claim units; independently verify original Owner amendments and exact graph source bytes. The Owner must explicitly accept its version and original input provenance. Replace synthetic provider with *authenticated repository-scoped GET reader*, capture issued graph ref, blob SHA and lab original file checksum. **Benchmark cannot sign itself.**
2. **G2 (evidence/review):** Record the effective required checks for one exact PR candidate HEAD, an authorized `CHECKPOINT_FACTS_V1` issuer, plus *two actual distinct independent qualified reviews* and immutable receipts; run both true positive and stale/forged negatives against native ledger. Expect a nonzero accepted E only with real qualified evidence. **Do not fabricate participants or lower policies.**
3. **G3 (protected native):** Request already-base-resident Owner exact-path grant for `skills/engineering-pr-delivery-v3.2/**`, then fix full `owner/repo#PR` without losing historical short-ref compatibility or foreign-repo rejections. Reuse native DELP and existing publisher; independent review, negative tests and exact-head CI required. Keep writer OFF.
4. **G4 (live GitHub):** After separate Owner publisher authorization, perform scoped compare-and-swap/readback on root issue, child issue and PR preserving human prose, native TITLE/LIVE_STATUS owner and one shared input digest; prove idempotence, partial-write detection and authorized recovery. **No live PATCH in this benchmark.**
5. **G5 (independent B):** External controller creates four genuinely isolated/no-chat context entries, revokes old A writer credential/lease, grants B only a scoped successor lease, and captures B continuation evidence. C6 document generation is not this physical test.

## Operator walkthrough/result interpretation

1. Checkout **benchmark branch exact commit**; execute the CLI and retain its JSON (no private inputs). Validate `test_cases_total=10`, `test_cases_pass=10`, `ready_for_production=false`, `writes=0` and all five HOLD gate IDs.
2. In CI, read the job logs at the *same commit* to verify the Python 3.11/12/13 unittest counts, the new five benchmark regression oracles and the existing 44 source regression tests. If any test fails, report RED with exact head, error, and source.
3. Compare current public #5/#325/#326 metadata live through GET separately; it is used only for a **currentness observation**, not as an Owner-approved graph or positive fact.
4. Require the five genuine inputs above before authorizing work on protected native source or initiating live publication; no Owner acceptance arises from this benchmark.
5. Record evidence on the owning issue #325, with the distinct benchmark branch/PR and exact-head run IDs. Keep parent #289 release HOLD and programme #5 AC0/8.

**Security/ownership:** benchmark is isolated from feature PR #326 to avoid concurrency and cannot modify `main`, Tab2, native V3.2 frozen source, `relay/STATE.yaml`, Local protocol selection, effective branch-policy, credentials, or real issue/PR managed blocks. No new authority, renderer, fake E, live GitHub writer or independent Agent B.
