# V3.2 #325 — Generic graph-bound GET-only native DELP source preflight

**Status:** T01 engineering candidate; **DRAFT / UNMERGED / NO LIVE GITHUB WRITER**.
**Source basis:** [Common main at 27fd8afbe76b45546e4512b252e1ea15045567f0](https://github.com/reallakshman19/Common/commit/27fd8afbe76b45546e4512b252e1ea15045567f0).
**Tracked plan:** [child #325](https://github.com/reallakshman19/Common/issues/325), linked to [parent #289](https://github.com/reallakshman19/Common/issues/289).

This is a **pure function**, deliberately **not** a new GitHub publisher or authenticated current-source protocol:

```python
from generic_source_preflight import preflight, SourceHold

report = preflight(
    graph=actual_proposal_v2_graph,     # caller must establish current Owner graph custody
    repository="authorized-owner/real-project",
    leaf_ref="real-project#123",
    pr_number=456,
    expected_head="a" * 40,            # pin from independently observed actual PR
    provider=read_only_get_provider,   # must expose get_issue/get_pull/get_commit_sha
)
assert report["writes"] == 0
assert report["production_authorized"] is False
```

The example is interface illustration only: `"a" * 40` is **not** a real PR HEAD, graph or policy grant. Never call it genuine evidence.

## What T01 actually enforces

1. Native `delp.validate_graph` and `delp.decomposition_report` must accept the complete supplied graph; selected leaf must be a declared `LEAF`, with exact bound PR in the *same* repository and graph identity.
2. Explicit repository and provider repository identities must match the supplied graph. Foreign head/base repositories, wrong base branch, wrong PR number or changed candidate SHA refuse with deterministic safe codes.
3. Two separate GET-only passes read the branch tip, root/leaf issue title and body digests, and PR identity, head/base, metadata and body digest. If those observations move, fail closed; do **not** describe an arbitrary GitHub provider object as self-authenticating.
4. Calls the **unchanged native** `delp.project(graph, [], observations)` for P/E/D and plan/input digest. An empty fact ledger is intentional; no synthetic result can earn `E`.
5. Returns `READ_ONLY_SOURCE_OBSERVED_UNATTESTED` and explicit `writes: 0`, `source_authenticated: false`, `evidence_admitted: false`, `production_authorized: false`, `automatic_successor: false`. Safe error codes do not interpolate private issue/PR texts.
6. A separate CI guard scans the module for transport/network/provider mutation implementations. The provider is injected and checked for the three GET methods; this module does not obtain tokens or invoke `gh api`.

## What T01 does NOT do

This function does not authenticate whether its caller's graph is *actually current and Owner-released*, validate GitHub API token authority, verify real required checks, read or admit `CHECKPOINT_FACTS_V1`, update GitHub titles/bodies/comments, or switch the active protocol. It does not perform a real C6 cold successor or issue a Local writer lease. A caller could inject a dishonest provider; this result stays `UNATTESTED`.

The pinned historical example `.github/v32-evidence-spine/718-proposal-v2.json` is bound to **old** `reallaksh19/Common`. Unit tests deep-clone/rebind that complete Proposal-V2 example to `example/Pipeline` to prove **source shape portability only**. This does not constitute Owner authorization of the synthetic project and does not rewrite the checked-in graph.

## Next gates (Issue #325 T02–T05)

T02: bind a *real* authorized provider and exact default-branch released graph (blob and double-read custody), reuse native `ledger_from_github`/observations and resolve or correctly HOLD native full-`owner/repo#PR` material-ref inconsistency. T03: pure disjoint publisher plan, no writer. T04: explicitly Owner-authorized base-resident frozen native amendment and independent review. T05: real private lab positive evidence→DELP→issue+PR readback→C6 and genuine independently authorized A→B execution. Retain the existing DELP as sole P/E/D/DE owner.

## Test command

```sh
python -m pip install PyYAML jsonschema
python -m unittest discover -s relay/INTEGRATION/V32_325_GENERIC_SOURCE_20261011 -p 'test_*.py' -v
```

Dedicated CI: `.github/workflows/v32-325-generic-source-preflight.yml`; Python 3.11, 3.12, 3.13; `permissions: contents: read`. Tests exercise a **synthetic** provider against **real native Common V3.2** functions.
