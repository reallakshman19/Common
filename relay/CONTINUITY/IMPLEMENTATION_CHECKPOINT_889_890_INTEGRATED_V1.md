# Integrated Relay Continuity — source/test/governance checkpoint V1

**Repository:** `reallakshman19/Common` (canonical after migration).
**Responsibility/governance:** [new issue #4](https://github.com/reallakshman19/Common/issues/4), [integration PR #2](https://github.com/reallakshman19/Common/pull/2), [disabled governance PR #7](https://github.com/reallakshman19/Common/pull/7).
**Historical original-intent context:** former `reallaksh19/Common` issues #889 and #890 and PRs #892/#893; the old issue tracker was **not** migrated to the new repository.
**Basis:** PR #2 source HEAD `dc8203b11a5484ea8c530efc09ed5c2d43c9e3f3` **before adding this Markdown checkpoint**. Source was checked by GitHub readback; no live tool-isolation trial.

## Bounded integration accomplished

1. Canonical communication home: `relay/CONTINUITY/` and issue-scoped `relay/CONTINUITY/episodes/ISSUE-<n>/messages/`. Historical `relay/BUDDY_RUNNER/README.md` now redirects. Do not publish two competing live message namespaces.
2. Imported the other agent's Markdown-only operator release contract, source/baseline-first reconstruction, reviewer-only negative probes, dispatch postmortem, and Stage 2/handover reference formats.
3. Retained existing V3.2 `transactionlib` atomic/recoverable transaction path, explicit `PUBLISH_BUDDY_MARKDOWN` command and schema enum, same-issue/latest stage chain, SHA-256 readback and content-bound `STAGE1_FREEZE_CANDIDATE`.
4. Transaction actor and claimed session references are not independent provider identities. Stage 1 actual blindness, final seal and Stage 2 disclosure are NOT_ATTESTED / HOLD; native technical handover/lease remains authoritative.

## Exact source-level test evidence

- Original PR #2 integration HEAD `65ba9d4ea1283d5f7a519afca0f2d8b8a8375817`: [V3.2 run 37968064952](https://github.com/reallakshman19/Common/actions/runs/37968064952) ran native `test_relay_tx.py` **38 tests: 37 PASS, 1 FAIL**. The sole failure was an error-code expectation: absent Stage1 baseline returned `BUDDY_STALE_STAGE_CHAIN` rather than `BUDDY_STAGE_ORDER_MISSING_STAGE1_BASELINE`.
- Corrective commit `dc8203b11a5484ea8c530efc09ed5c2d43c9e3f3`: immediate prerequisite now checked before stale-chain condition. [V3.2 run 37968469829](https://github.com/reallakshman19/Common/actions/runs/37968469829) **SUCCEEDED**, including native `test_relay_tx.py` **38/38 PASS**, continuity/replay/handover/V3.5 parity/isolation workflow steps.
- [DELP run 37968469849](https://github.com/reallakshman19/Common/actions/runs/37968469849): **PASS** at corrective commit.
- [Local PR Delivery 37968470110](https://github.com/reallakshman19/Common/actions/runs/37968470110): **BLOCKED BY INTENDED GOVERNANCE**, not by a Buddy unit test. Frozen-tree guard lists four changed V3.2 paths without base-pinned Owner amendment.
- [V3.1 run 37968469824](https://github.com/reallakshman19/Common/actions/runs/37968469824): **FAIL**, six errors for missing `.github/workflows/engineering-pr-delivery-v2.5.yml` and `.github/workflows/engineering-pr-delivery-v3.yml` (legacy workflow-file assumption in `test_ci_terminal_checks.py`). No claim this is related to new transport.

## Frozen-tree exception is explicitly UNAPPROVED

[Issue #4](https://github.com/reallakshman19/Common/issues/4) names exact four requested frozen paths:

- `skills/engineering-pr-delivery-v3.2/schemas/transaction.schema.yaml`
- `skills/engineering-pr-delivery-v3.2/scripts/relay_tx.py`
- `skills/engineering-pr-delivery-v3.2/scripts/transactionlib.py`
- `skills/engineering-pr-delivery-v3.2/tests/test_relay_tx.py`

[Draft governance PR #7](https://github.com/reallakshman19/Common/pull/7) contains a separate manifest proposal with **`owner_authorized: false`**. It does not unblock PR #2. Explicit Owner approval and a distinct base-pinned governance merge are prerequisites to product merge; a generic continuation or source-level PASS does not grant that authority.

## Next real controlled Runner acceptance

An external independent Runner operator must launch a fresh agent B with demonstrably restricted original-source-only reads, run positive historical read and negative current-A/PR/Stage2/alternate-tool denied-read probes, attest session/tool visibility externally, obtain real Stage1A source→function→consumer→output evidence and Stage1B competing hypotheses, then freeze exact output bytes. **None of that was performed by this checkpoint.**

**STOP:** Do not merge PR #2, claim final Stage1/Stage2 admission, transfer a writer/lease, forge DELP P/E/D or mutate root `relay/STATE.yaml`. This document is durable Markdown communication of verified facts, not a new schema or an acceptance authority.