# PW04 consolidated V3.2 lifecycle prototype — READ-ONLY / NO RELEASE

**This is the one integrated engineering work package**, not additional independent
production progress items. It combines fresh private GitHub GET capture, source/PR
binding, the **unchanged native** DELP reducer, native issue LIVE_STATUS/title
in-memory publication, the **unchanged native PR managed-section renderer**,
and native C6 frontier on **one source snapshot and one native input digest**.

### Executable end-to-end workflow (Owner/private workspace only)

These commands require installed GitHub CLI access to the **original private**
`reallaksh19/relay-v32-e2e-lab`, the released unmodified six-node graph,
and the real current PR HEAD. Never commit snapshots or reports: both contain
private issue/comment text and the capture/report create mode-0600 files.

```bash
python relay/RECOVERY/V32_289_PW04_GENERIC_PR_SOURCE_20261010/v32_capture_current_source.py \
  --graph /private/released-graph.json \
  --repository reallaksh19/relay-v32-e2e-lab \
  --graph-blob fde7e1fbd0c71efb64a678206f0bc9f32e36f6c8 \
  --output /private/lab-current-get-only.json

python relay/RECOVERY/V32_289_PW04_GENERIC_PR_SOURCE_20261010/v32_integrated_shadow.py \
  --graph /private/released-graph.json \
  --snapshot /private/lab-current-get-only.json \
  --repository-id REAL_NUMERIC_REPOSITORY_ID_FROM_FRESH_CAPTURE \
  --leaf reallaksh19/relay-v32-e2e-lab#4 \
  --graph-blob fde7e1fbd0c71efb64a678206f0bc9f32e36f6c8 \
  --head EXACT_CURRENT_PR8_HEAD_SHA \
  --output /private/lab-current-shadow.json
```

The capture uses only GitHub API GET. It pins the graph bytes against the real
current default-branch file Git blob and rejects a changed issue body/title,
bound PR head/base, issue comments, main commit or numeric repository identity
during its bounded two-pass capture. It refuses missing or overlong sources.
The capture also refuses non-canonical/invalid graph blob base64 while accepting
standard GitHub CR/LF-wrapped base64, requires at least one graph LEAF before
any GET, caps each fetched comment body at 1,000,000 characters (oversize is
a hard HOLD, never truncation), and re-GETs the repository identity after
the final main SHA check to detect source transfer/replacement. Graph bytes
remain untouched. Both CLIs refuse pre-existing output paths; the capture
CLI's POSIX tests verify private 0600 output and reject symlinks *before*
source access. Additional read-only preflight rejects non-ASCII or padded
issue/PR numbers rather than letting Python Unicode-digit parsing alias GitHub
identities. The first and final default-branch commit responses must be JSON
objects; missing/malformed observations produce bounded HOLD reasons instead of
attribute exceptions. Each GitHub issue-comment page is capped at 100 entries;
the total captured comment text is capped at 5,000,000 characters **per leaf**,
while each individual comment keeps its 1,000,000-character bound. Overflow
is rejected and never truncated, including on the second read. The `gh api`
GET-only subprocess has a 30-second **per-request timeout**, explicit CLI
unavailability/timeout reason codes and never surfaces raw stderr, tokens or
private issue text as a diagnostic. This bounds each read, **not** the overall
multi-request end-to-end capture duration. Synthetic tests cover clean
100+0 pagination, numeric ambiguity, malformed commit responses, page/aggregate
overflow, timeout and missing CLI; all authentic current provider facts and
Owner authority still require independent verification. These synthetic/transport
protections do not issue evidence, attest human Owner approval or make the
inaccessible original lab current.
The **offline shadow input** now independently rejects raw graph duplicate JSON
keys, invalid UTF-8 and non-finite JSON before native V3.2 executes, without
rewriting the pinned graph bytes. Its GET-only snapshot adapter refuses absent
or incorrectly typed issues/pulls/comments maps and missing/malformed pinned
main SHA, rather than allowing raw Python lookup errors. The unchanged native
managed PR block renderer is exercised through a *second* reconciliation pass
and must return a byte-identical body, including untouched original human PR
prose. Shadow report output remains exclusive-create mode 0600 on POSIX; if
serialization fails after opening the file, the incomplete private artifact is
unlinked. None of these offline assertions converts a snapshot into human
Owner attestation, an independently admitted fact, or a live publication.
The shadow refuses drift, malformed input and moved PRs, runs **real** native
`plan_github`, `ledger_from_github`, `observe_github`, `project`,
`source_bound_responsibility_core` where compatible and `frontier`, reuses
the frozen `render_pr_block/reconcile_managed_block` and
`sync_projection` **only with native `InMemoryStore`**, checking
second-pass idempotence and identical source digests. It has no GitHub write
capabilities and never awards Owner approval or eligible evidence by itself.

### Important source-discovered blocker (not silently fixed)

Original lab graph links use **full** `owner/repo#PR` GitHub references. The
unchanged native `source_bound_responsibility_core()` currently rejects those
with `RESPONSIBILITY_CORE_MATERIAL_BOUNDARY` because its check expects a
short `repo#PR` reference. Other native graph, DELP, title, status and C6
calls can still complete, but the shadow reports
`native_core=null, native_core_hold=RESPONSIBILITY_CORE_MATERIAL_BOUNDARY`;
it **never synthesizes an alternate core** or normalizes/rewrites an approved
graph to disguise the mismatch. This must be corrected **within the existing
native owner** under an approved frozen-source grant, then reverified against
real exact-head source. It is a genuine production admission blocker.

### Review/authorization boundary

- Every included hosted Python test is **synthetic GET source**, except that
  each integration test calls the real unchanged V3.2 source in the Common
  checkout. The Owner's archive has been tested locally separately (original
  app acceptance 9/9; lab unit 118/118), but current private provider 404
  blocks running these two CLIs against real current lab material.
- The PR is intentionally **DRAFT**. It is NOT a generic live GitHub writer,
  fact issuer, independent reviewer, actual cold successor, Owner T05 release,
  approved new Common root graph, or production activation.
- After original provider access, run exact native capture/replay; fix the
  native core full-ref mismatch only with the separately approved amendment;
  independently admit evidence; extend guarded native issue/PR publisher under
  field-separated ownership and approved exact-path grant; prove real lab
  GET-back, C6 cold successor, adversarial replay, Common shadow and Owner
  rollback/cutover. V3.1 remains production until those gates PASS.

**Tests**:
```bash
python -m unittest discover -s relay/RECOVERY/V32_289_PW04_GENERIC_PR_SOURCE_20261010/tests -p 'test_*.py' -v
```

---

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