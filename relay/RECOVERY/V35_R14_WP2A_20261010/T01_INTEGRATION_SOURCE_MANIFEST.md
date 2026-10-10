# T01 — Pinned WP2-A U02/U03/U04 source consolidation

**Status:** integration source candidate ONLY; read-only, negative diagnostic, no Owner/Local admission.
**Programme goal:** [#294](https://github.com/reallakshman19/Common/issues/294) · [task plan](https://github.com/reallakshman19/Common/issues/294#issuecomment-6098284958).
**Existing source owner:** [#20](https://github.com/reallakshman19/Common/issues/20). **Repository:** `reallakshman19/Common`, native ID `1412133785`.
**Integration branch:** `codex/294-t01-wp2a-u02-u03-u04-pinned`.
**Immutable stacked base:** [PR #28](https://github.com/reallakshman19/Common/pull/28) `98da09e40265becee5b15d4144813b99b38c0024` (not `main`).
**Source preservation:** the following original draft PRs remain separate, draft and unmodified by consolidation. For each path, the integration Git blob must be IDENTICAL to the source Git blob. There are no semantic edits, rebase or protocol rewrites.

| Existing producer | Exact source commit | Carried path (relative to this directory) | Required identical Git blob |
|---|---|---|---|
| [#303 — U02](https://github.com/reallakshman19/Common/pull/303) | `af9a7c604ba2dd2a752d5c6b33bf051d7ad92395` | `required-ci-material-v1.mjs` | `3eac046128202fdee88a5ad47bb1df82e3304ca1` |
| #303 | same | `required-ci-material-v1.test.mjs` | `e1da8e166cb7e560f76f13500e629f4a0be0f877` |
| [#305 — U03](https://github.com/reallakshman19/Common/pull/305) | `f0fc8ee9946b43b9f6a6c90fa0057a45e7e82ab2` | `task-evidence-comment-v1.mjs` | `79cffd2e3d2828ac1727afad7763267768c56ad5` |
| #305 | same | `task-evidence-comment-v1.test.mjs` | `e78b852d0e28c8f7a13fe66baf60662e4b7c6789` |
| [#301 — U04](https://github.com/reallakshman19/Common/pull/301) | `6bbd3825c6c1f9106d83bae84db1a6d01b4e3bf6` | `cross-source-vector-v1.mjs` | `e5843e4ab141a49950cd8e2b380540eca8f8f938` |
| #301 | same | `cross-source-vector-v1.test.mjs` | `c0074ed41ee6a35e7fe0bbc4387b89e6ccf083fb` |

## Inherited original contract (no promotions)

- U02: real current selected CI read-only, required policy **UNKNOWN unless independently readable**, failed changing selected-checks vector remains a refusal, not skipped.
- U03: immutable repo/root/leaf/PR/comment/commit native sources, 2 original observations, typed body is **claim only**; stale text never counts as evidence.
- U04: serial U01→U02→U03 two-round composition, explicit source-grade/route/HEAD/CI/claim binding and readback. Preserve `UNKNOWN`, `NOT_CALCULATED` and `evidence_admitted:false`; source-controlled refusal stages never expose raw secrets.
- No source or test under `skills/engineering-pr-delivery-v3.2`, no V3.5 DELP projector, graph, issue state/title/index writer, Local v1.1 writer/custody, review or publishing change.
- **T01 is complete only after** GitHub readback verifies all six blob IDs at one actual integration HEAD, the new draft PR's base equals PR #28 and original PR HEADs are unchanged. This document cannot itself bind its own final commit SHA. The final SHA and CI run IDs belong in GitHub TASK_EVIDENCE.
- **T02 later** qualifies one same-head composed **native** U01+U02+U03+U04 run with dedicated CI wiring; individual diagnostic green jobs alone cannot satisfy T02. Native refusal is a real finding, not automatically a coding failure; do not coerce PASS.

This material is source custody/navigation and not an accepted `CHECKPOINT_FACTS_V1`, Owner execution graph selection, evidence admission or production release.
