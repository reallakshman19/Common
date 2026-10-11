# INPUTS — Tab1 V3.2 Generic Source Lifecycle (source and evidence manifest)

Date: 2026-10-11 Asia/Muscat | chat `6acae92b` | repo `reallakshman19/Common` | owner #325, parent #289, programme #5.
`RECON/2026-10-11/4-report.md` is historical and reconstructed from source; this file records **present read inputs and missing original acceptance inputs**, not a new release grant.

## Current checked identity (source-first)
- **Draft PR #326:** `feature/v32-325-graph-bound-readonly-integration`, observed head `dc41b6420fd5dfe1be1734007530b72eb505902f`, base last synchronized from `c75b0c49cecf0624961b8d1c2841a787d6c3fd51`; draft, unmerged. Its merge HEAD was `b14b9930aa4edea4dee4763888632d6f65d84637`.
- **Default branch observed in this handover turn:** `main@579902f70ba61376e46e5b0a08a472ba2a664d55`; already newer than the synchronized base, predominantly independent coordination changes. Never claim automatic continuing sync. Re-fetch on succession.
- **Native reverse PR #328:** head `main@c75b0c4`, base #326 feature at `8bab9d7`, merged to feature only. **Separate draft PR #327:** `8b9d767a236c21257a0514b1563ea7b37263b21b`, isolated V3.1 test-file fix reused by #326.
- **Tab report:** `coordination/Session_Oct07/Tab1_V32_Generic_Source_Lifecycle/RECON/2026-10-11/4-report.md`, Git blob `409e8f290dc72b5b8a24778bfc4298d2a210b034`; its historic date/head are not current CI.
- **Entry requirements:** source #5, parent #289, child #325, actual PR diff and native scripts, current branch/protocol/CI per exact SHA. Historical `reallaksh19/Common` is a different repository from current `reallakshman19/Common`.

## Physical source and fixture inventory
- `relay/INTEGRATION/V32_325_GENERIC_SOURCE_20261011/generic_source_preflight.py` T01: graph/leaf/PR/head and two provider GET passes (UNATTESTED).
- `generic_current_source.py` T02: graph bytes pinned vs current branch and two native DELP ledger/observation passes (UNATTESTED).
- `generic_publication_plan.py` T03: pure three-surface desired-state/readback and non-atomic conflict classification (NO WRITES).
- `rest_readonly_provider.py` + `test_rest_readonly_provider.py`: injected GET contract, nested/flattened GitHub envelopes incl. `issue_number` alias; tests replay sanitized public #5/#325/#326 responses rather than genuine source authority.
- Native functions in `skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py`, `trusted_scoreboard_v32.py`, `vertical_cycle_v32.py`, `handover_context.py`, `relay_tx.py` are **reuse-only**, not modified in this child.
- `.github/v32-evidence-spine/718-proposal-v2.json` (blob `d35019b416cb3b573280e166027d3f65ba61f59c`) belongs to **historical `reallaksh19/Common` programme #718**. New tests rebind/copy to synthetic `example/Pipeline`; this is not original new-repo Owner authorization.
- `relay/STATE.yaml` (blob `86c6c5f4e4ddbcbfb595f59c479d5f9a74cfa4b7`) is legacy V3.1 state; Local stack `skills/Local_PR_Deliverty_v1.1/integration/protocol-stack.yaml` (blob `17587545dc3b3f4d825dadb6a56746c10da26d81`) selects nested V3.5 and explicitly forbids V3.2 as active. Historical/production references must not be conflated.

## Executed checks on PR #326 exact pre-log head `dc41b6420fd5dfe1be1734007530b72eb505902f`
- Focused [run 38108470192](https://github.com/reallakshman19/Common/actions/runs/38108470192): 44 Python tests on each 3.11/3.12/3.13; 132 named executions PASS; AST no-network/direct writer guard pass for T01–T03.
- V3.1 [run 38108470239](https://github.com/reallakshman19/Common/actions/runs/38108470239): 274 tests PASS.
- Native V3.2 [38108470281](https://github.com/reallakshman19/Common/actions/runs/38108470281) and DELP [38108470201](https://github.com/reallakshman19/Common/actions/runs/38108470201): workflow success, **native substantive path NOT_APPLICABLE**, as job logs state explicitly.
- Local [38108470221](https://github.com/reallakshman19/Common/actions/runs/38108470221): workflow success; job logs include test groups of 26, 4 and 15.
- `[skip ci]` log-only commits after this exact head do not inherit these five runs as same-HEAD evidence.

## Missing original inputs and authority — NEVER fabricate
Authentic new-repository Owner-released graph and amendments; original private lab `reallaksh19/relay-v32-e2e-lab` accessible source bytes; genuine accepted positive/negative CHECKPOINT_FACTS and issuer identity; effective branch-protection required checks and independent reviewer policy; qualified two-reviewer evidence; authorized live three-surface GitHub write/readback; no-chat C6 four-context Agent B continuation and old-A revocation; new-repo Owner acceptance AC1–AC8. These remain unproven; programme #5 **AC0/8**, production **HOLD**, V3.2 live writer **OFF**.

## Evidence links
- [#325 revision 3](https://github.com/reallakshman19/Common/issues/325#issuecomment-6104485981), [XS/S evidence](https://github.com/reallakshman19/Common/issues/325#issuecomment-6104535513), [revision 4 branch+CI](https://github.com/reallakshman19/Common/issues/325#issuecomment-6105035722).
- [#289 M/L future roadmap](https://github.com/reallakshman19/Common/issues/289#issuecomment-6104487421), [PR #326 reviewer checkpoint](https://github.com/reallakshman19/Common/pull/326#issuecomment-6105037022).
