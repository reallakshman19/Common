# V3.2 PW04 — generic PR source-binding preview (non-admitting)

**Owner/issue:** [Common #289, PW04](https://github.com/reallakshman19/Common/issues/289#issuecomment-6100647890) · [parent #285](https://github.com/reallakshman19/Common/issues/285).

This workpack removes a prerequisite for generic V3.2 integration **without modifying the protected live publisher**. It reads an independently supplied raw graph and real-shaped GitHub GET repository/PR response, runs the *unchanged native V3.2 graph validator* from `skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py`, resolves the declared LEAF→`primary_pr` binding, and verifies the exact source blob, repository identity (name **and** GitHub numeric ID), branch, PR number and pinned candidate HEAD.

It emits an **opaque identity fingerprint and a read-only preview**; it **never** produces percentages, `CHECKPOINT_FACTS_V1`, Owner/SourceReceipt claims, issue/PR titles, managed content or mutation requests. It intentionally returns `publication_authorized: false`, `owner_source_authenticated: false`, `evidence_admitted: false`, `native_projector_executed: false` even for a coherent provider-looking input. An observation or self-supplied matching source hash is not an approved source. The fingerprint is **not** native DELP `input_digest` and cannot replace it.

This makes a generic leaf/PR/source contract usable on the historical Common graph **or** another repository's native-conformant graph, while the released V3.2 projector and current `trusted_scoreboard_v32.py`, `vertical_cycle_v32.py` and `pr_responsibility_view_v32.py` remain untouched. The actual generic live **writer is not implemented or authorized in this PR**. The path to production is still `READ_ONLY_CANARY → SCOPED_LAB_PILOT → V3.2_CUTOVER`; release must pass #289 D1–D5 / R1–R5, #285 G1–G5, an approved frozen-path amendment for any native edits, independent review, real provider readback, rollback and explicit Owner decision.

## API

`preview_source_binding(raw_graph: bytes, pins: PreviewPins, provider_repository: Mapping, provider_pull: Mapping, *, native_validate=_native_structure) -> dict`

`PreviewPins` contains independently sourced selectors (`repository`, numeric `repository_id`, `released_graph_blob_oid`, `leaf_ref`, `expected_pr_head_sha`). The module does **not** authenticate whoever supplied them. The caller must do that externally before any separate publisher can act. `provider_pull` must be the actual PR endpoint; non-GET data or a self-authored fixture has no independent evidentiary value. At this first bounded lab stage, foreign fork PR heads are refused rather than granting implicit cross-repo authority.

## Tests

```sh
python -m unittest discover -s relay/RECOVERY/V32_289_PW04_GENERIC_PR_SOURCE_20261010/tests -p 'test_*.py' -v
```

Public tests use only synthetic source. One extra test invokes the actual native V3.2 graph validator whenever the containing Common checkout is present; offline detached execution labels it skipped. Separately, the author exercised the module locally against an **uploaded authentic private lab graph** with blob `fde7e1fbd0c71efb64a678206f0bc9f32e36f6c8`: original R01/PR #8 source binding preview generated and wrong PR base target rejected. The private lab graph bytes or live PR comment/snapshot contents are **not committed in this public workpack**. That local probe used a mocked numeric repository ID and native-validation callback, **not** current GitHub source or real-native projection.

## What is next

1. Independently authorize released immutable Owner/OR ledger, current graph and source/actor policy; install authenticated provider read access.
2. Call this preview on a **fresh** private provider GET and the exact stored raw graph, followed separately by existing native `delp_projection_v32.plan_github` (read-only shadow) to obtain the sole native `input_digest` and rejected facts. Never treat this preview's fingerprint as native `input_digest`.
3. Under an approved **exact-path, base-resident** frozen amendment, extend the existing guarded native PR publisher to consume the authenticated released-graph binding and authorized native projection. Preserve disjoint issue-title / PR-managed-body writers, human text, R3/R12 trust, conflict and rollback behavior. Do not remove the old Common-specific guard without a replacement policy.
4. Run live **scoped lab-only** publication/readback, independent C6, S01–S26 and three full replays before Common production shadow and final Owner-governed cutover.