# Engineering Relay V3.5 — embedded Coder continuity/recovery for Local PR Delivery v1.1

## Status and lineage

V3.5 is an additive protocol line for **nested Coder engineering execution** under `Local_PR_Deliverty_v1.1`.

It was forked without modifying V3.2 from the exact Common basis:

```text
SOURCE_COMMIT: a29e67ae8beabaeca8a794343e72c01e37d067af
SOURCE_V3_2_TREE: 88ac97432a811f9a6b8d00bbe45cbec891e70d6a
SOURCE_PATH: skills/engineering-pr-delivery-v3.2
```

`skills/engineering-pr-delivery-v3.2/**` is frozen by #492/#494 and is not a V3.5 implementation surface.

The copied V3.2-named files under this V3.5 directory are retained only as compatibility/replay baseline. They do **not** select the active V3.5 state machine. Active V3.5 behavior is defined by this file plus the explicitly V3.5-named schema/script/tests.

## Nesting invariant

Local v1.1 owns the production responsibility and role lifecycle:

```text
LOCAL RESPONSIBILITY
PRD-017
  |
  `-- CODER stage
        |
        `-- V3.5 nested engineering execution
            ENG-PRD-017-CODER
```

V3.5 owns only continuity/recovery/provenance for the nested Coder engineering execution.

V3.5 MUST NOT own or infer Local:

- Reviewer or Coordinator/Super Reviewer transitions;
- writer-slot/start permission;
- Local stage timer accounting or watchdog truth;
- merge authority;
- acceptance-policy adoption;
- risk-relaxation authority;
- Local responsibility completion.

A V3.5 `TASK_RESULT` may complete `ENG-PRD-017-CODER`; it can never by itself complete `PRD-017`.

## Canonical nested identity

For Local responsibility `PRD-017`, the default nested engineering identity is:

```text
ENG-PRD-017-CODER
```

The active binding records both identities:

```yaml
local_responsibility_task_id: PRD-017
engineering_responsibility: ENG-PRD-017-CODER
role: CODER
result_scope: CODER_ENGINEERING_EXECUTION
local_responsibility_complete: false
```

Identity is explicit and durable. Do not derive Local completion from V3.5 state names such as `COMPLETE`.

## Exact protocol provenance

A native V3.5 nested execution records exact immutable refs for both governing layers:

```text
LOCAL_PROTOCOL_REF: owner/repo@<40-sha>:skills/Local_PR_Deliverty_v1.1
V3_5_PROTOCOL_REF: owner/repo@<40-sha>:skills/engineering-pr-delivery-v3.5
```

It also records the Local acceptance epoch/profile references supplied by the Local control plane. Those references are observed/bound context only; V3.5 cannot adopt or mutate them.

## Lossless Owner intent envelope

Direct Owner instructions are captured before workflow normalization. The canonical parser is `scripts/owner_commands.py`.

For a direct Owner utterance it preserves:

```yaml
owner_intent:
  verbatim_request:
  source_ref:
  primary_purpose:
  requested_deliverables: []
  target:
  custody_intent:
  assurance_request:
  modifiers: []
  boundary_constraints: []
  authority_ref:
```

The envelope is lossless request/custody/assurance context, not a new permission system:

- preserve `verbatim_request` exactly; normalization never replaces it;
- `source_ref` and `authority_ref` are references supplied by the caller and are never fabricated;
- compound deliverables remain compound (for example, handover package plus an exact-count successor reconstruction challenge);
- existing scalar `intent`, `workflow`, `reasoning_modes` and question-suppression fields remain derived compatibility views;
- quoted repository/file/fixture text cannot create an Owner envelope;
- the envelope creates no durable authority, role transition, merge authority or production authority.

Custody and reasoning are orthogonal. In particular:

```text
PLAN_HANDOVER
= prepare custody transfer

PLAN_HANDOVER
!= automatic Two-Pass request
!= automatic replanning
!= independent reconstruction
```

A handover workflow may reconcile live material and publish custody context, but it must not manufacture a new reasoning request merely because custody is changing. Replanning/assurance is separate and must be explicitly requested or independently required by the governing responsibility.

## Recorder-first continuity semantics

V3.5 retains the useful V3.2 continuity/recovery invariants for the nested engineering execution:

- material truth comes from Git/PR/tests/runtime/artifacts;
- durable task publications explain successor-safe engineering truth;
- material and semantic/evidence frontiers remain separate;
- passive frontier lag is not an engineering permission gate;
- replacement executors do not create a new nested responsibility;
- recovery evidence is required before the next material change after detected interruption/recovery;
- progress is denominator-based, never activity-count based;
- provider/reporting failure reduces observability, not engineering agency.

The publication family remains:

```text
IMPLEMENTATION_PLAN
PLAN_UPDATE
TASK_EVIDENCE        (carries the machine-readable CHECKPOINT_FACTS_V1 block)
TASK_RESULT
```

## Projection authority — DELP (agents publish facts only)

> **Agents publish facts. Everything else is recomputed from those facts.**

A nested Coder (and any reviewer) states, about its own leaf responsibility only: which declared units it reports complete, the verification result, the durable evidence refs, the candidate those refs cover, and the next unit — as a `CHECKPOINT_FACTS_V1` block inside `TASK_EVIDENCE`. It MUST NOT author, edit or paste a percentage, a title or title suffix, a weight, a frontier count, an activity epoch, an evidence-health verdict, or any phase/programme progress. Those are projections: the DELP projector derives them, a facts record that tries to author one is rejected and cannot move any number, and a hand-edited title is classified as drift and overwritten at the next projection.

```text
leaf          🟢 [#527 › #588 › #592 → PR#593] R:P65/E65 · U04 · ACTIVE — <responsibility>
intermediate  🟢 [#527 › #588 → #592/PR#593] Φ:D60/E58 · F2 · ACTIVE — <phase>
programme     🟢 [#527] Π:D72/E70 · F3 · ACTIVE — <programme>
```

`›` ownership/hierarchy, `→` material PR relation, `F` active frontier leaves; every percentage is scoped (`R:`, `Φ:`, `Π:`), a bare `P56% / E56%` is invalid. `E` counts a unit only while its evidence is **current** (verified result, durable refs, evidence candidate equal to the live PR head): a push lowers `E` and leaves `P` until the evidence is replayed. Ancestor `D/E` are weighted roll-ups recomputed from children, never incremented, never authored; weights and lineage are plan authority in the execution graph. `PRD`/Local delivery stays Local's: a Coder `P100` is `R:P100` and never means Local `D100` (declare `delivery_gates` for reviewer/super-review/hand-off weight).

Continuation commands (`continue`, `proceed`, `next`, `resume`, `reconcile`, `take over`, `keep going`) reconstruct first: resolve the leaf and lineage, observe the live candidate, read the latest valid facts, repair any evidence gap before new coding, let the projector refresh titles/status (compare-and-swap, read back), show the compact `CONTINUE CHECKPOINT`, then execute exactly the next bounded unit. A continuation never changes the parent, denominator, scope, priority or merge authority.

**Decomposition gate.** The existing `decompose-check` remains the mechanical pre-work gate over the execution graph (never agent facts): it checks unit count/share, outcome, verify step, write surface, size budget and write-surface ordering; `graph-diff` preserves denominator/plan conservation. V3.5 additionally has the pure `decomposition_classifier_v35.py` research-backed boundary classifier. It distinguishes `PASS / SPLIT / MERGE / DISCOVER_FIRST / REPLAN` from normalized semantic-cohesion, dependency/verification closure, uncertainty, change impact, execution horizon, mutation domains, recovery radius, handoff cost and stable-cut evidence. **It is not yet wired into `decompose-check` or admission.** `transformation_boundaries` are candidate evidence, not automatic split authority: independent falsifiability alone does not force a GitHub child. See `PROGRAMME_DECOMPOSITION_PROGRESS.md` for the stable-cut rule and the semantic-responsibility / semantic-unit / execution-transaction separation.

**Materialization.** Unknown is never published as zero. A leaf the provider shows work for (an open, merged or closed pull request, or a `candidate_ref` branch ahead of `programme.base_ref`) but whose ledger has no accepted facts is `UNMATERIALIZED` 🟡; its ancestors say their numbers are a lower bound; a continuation answers `MATERIALIZE_FACTS` — publish facts for exactly what current evidence supports (completion is never inferred from a merge). Publish a first facts block at START so a new leaf is never unmaterialized. A live `sync-github` only writes to the repository the plan declares in `programme.repository`; the shipped examples declare `example/delp-demo`.

**Handover frontier.** A handover is the predecessor's view at one instant, never current truth, and must carry no hand-computed number. `frontier` derives it (provider-observed base, candidate and divergence; derived state, exact `P/E`, evidence health; input digests) and `frontier-verify` checks a handed-over snapshot against live truth: any moved input (`BASE`, `CANDIDATE_HEAD`, `PR_STATE`, `LIVENESS`, `FACTS`, `PLAN`) exits 2 with `RECONCILE`. Every `CONTINUE CHECKPOINT` carries a `FRONTIER:` line.

**Agent health.** Health is observed or derived, never declared (a dead or looping executor cannot report it). With `programme.health_policy.mode: ADVISORY`, started leaves carry a `health` block of seven components (`materialization`, `evidence`, `checkpoint_distance`, `size`, `base_drift`, `interruptions`, `liveness`) using the programme's own written thresholds (250 / 500 lines, the third stream loss); the verdict is the worst component, `UNOBSERVED` is never healthy, and it is advisory: it never moves a number, state, title or admission answer. Telemetry constrains delivery; it does not measure value. `health` prints it; each `CONTINUE CHECKPOINT` carries a `HEALTH:` line.

The active DELP contract is:

- `operating-model/durable-execution-lineage-projection-v35.md` (normative);
- `schemas/delp-checkpoint-facts-v35.schema.yaml`, `schemas/delp-execution-graph-v35.schema.yaml`, `schemas/delp-live-status-v35.schema.yaml`;
- `scripts/delp_projection_v35.py` (`validate-graph`, `validate-facts`, `project`, `admit`, `health`, `frontier`, `frontier-verify`, `decompose-check`, `graph-diff`, `verify-titles`, `sync-github`);
- `templates/checkpoint-facts-v35.md` (agent template) and `examples/delp/`;
- `tests/test_delp_projection_v35.py`, `tests/test_continuity_derived_projection.py`, `tests/test_owner_commands_continuation.py`.

The copied `continuity_projection.py` baseline now defaults new snapshots to `projection_mode: DERIVED_FROM_FACTS` (E computed, `--evidenced` rejected, no title patching); `LEGACY_AGENT_ASSERTED` stays readable. The earlier candidate title forms `{P · E · A · U · STATE}` in `OWNER_CHECKPOINT_PROJECTION.md`, `PROGRAMME_DECOMPOSITION_PROGRESS.md` and `CHECKPOINT_AND_LIVENESS_CONTRACT.md` are superseded by this grammar; their other content is unchanged. The same fix is applied to the frozen V3.2 tree as an Owner-directed additive amendment (`delp_projection_v32.py`), guarded by `skills/Local_PR_Deliverty_v1.1/integration/frozen-v32-amendments.yaml`.

## Runner preparation — manual Owner command and 70%-consumed advisory

**Owner command: `Prepare for runner`.** For an active nested Coder, treat this as an explicit request to **prepare**, even when the usable context-life percentage is unavailable or below 70. Follow [`runner/PREPARE_FOR_RUNNER.md`](runner/PREPARE_FOR_RUNNER.md) and [`runner/STATIC_PACKET_FORMATS.md`](runner/STATIC_PACKET_FORMATS.md): assemble an original-source/Owner **WHAT/WHY-only Stage 1 packet** for a separately isolated Runner B and a **separately held Stage 2 Agent A reality packet** (current HOW, source, tests, defects, pending/parked work). Do not leak the latter to Stage 1. The primary Coder A continues its already authorized responsibility; preparation alone never stops A, launches B, creates a new leaf or changes a source writer.

**Agent A advisory: `Time for Runner`.** At ordinary bounded-unit checkpoints or when concrete context-loss/compaction risk is observed, proactively *suggest* preparation when reliable used/usable context-life observations approach **approximately 70% consumed**. State the observation source/denominator and `PROVIDER_MEASURED`, `OPERATOR_EPISODE_PROXY`, `AGENT_RISK_OBSERVED` or `UNKNOWN`. If true context telemetry is unavailable, do not invent a percentage. DELP task/phase `P/E`, seven-component agent health, issue/PR count, source lines and completed units are **not context-life consumption**. A risk-based early suggestion must say consumption is `UNKNOWN` if it is. Do not announce that a separate model has been spawned.

**Runner B reasoning and admission.** Fresh Stage 1 reads **only** [`runner/STAGE1_INDEPENDENT_RECONSTRUCTION.md`](runner/STAGE1_INDEPENDENT_RECONSTRUCTION.md) plus operator-pinned historical Owner/source/fixtures, and must build its own evidence-led design, competing alternatives, falsifiers, ROI triage and three original source-derived questions. Keep [`runner/STAGE2_SOURCE_RECONCILIATION.md`](runner/STAGE2_SOURCE_RECONCILIATION.md) and Agent A's current changes inaccessible until an independently enforced read boundary and immutable Stage 1 plan are verified. Stage 2 then challenges Owner intent vs frozen B belief vs A claims vs actual source, preserving the same governed responsibility. Reviewer/operator-only guidance: [`runner/THINKING_METHOD_AND_EXAMPLES.md`](runner/THINKING_METHOD_AND_EXAMPLES.md), [`runner/MANUAL_ACCEPTANCE_GUIDE.md`](runner/MANUAL_ACCEPTANCE_GUIDE.md); [`runner/README.md`](runner/README.md) is the role-specific index.

**Authority invariant:** This is **Markdown-only advisory and information preparation**. No platform telemetry API, automatic agent/session launch, writer promotion, credential revocation, model-context attestation, issue/PR publication, progress title editing, Local timing/watchdog truth, independent reviewer approval or merge authority is created by these instructions. V3.5/DELP projection rules and Local v1.1 role/Writer OFF/WP0 hold still govern. Until a separate controller proves exclusive new custody and current provider/head evidence, successor engineering writes are **HOLD**.

**Self-contained technical handover (canonical new-repo issue #1):** An Agent A handover deliverable must be ONE completed [HANDOVER_TECHNICAL_V2 report](../../relay/CONTINUITY/TEMPLATES/TECHNICAL_HANDOVER.md), not a process plan or sparse Stage 2 metadata. It explains original problem/Owner WHAT+WHY, exact code changes/functions/consumers, actual end-to-end flow, tests/CI/browser and genuine fixtures at tested HEAD, known failures/rejected options, old/new repository migration and the successor's precise first safe action. The native `HANDOVER_CONTEXT`/transaction remains custody authority; the narrative reports verified engineering reality, does not forge A's words after a crash, and stays withheld until Runner Stage 1 externally freezes. No markdown document mints writer/merge rights.

**Relay-native Markdown message transport (Common #890):** [`relay/CONTINUITY/README.md`](../../relay/CONTINUITY/README.md) provides the minimal governed communication envelopes; Stage 1 is factual historical baseline FIRST, source-grounded provisional interpretation SECOND, and technical handover/Stage 2 only after an externally attested freeze. Refer to the [authority map](../../relay/CONTINUITY/AUTHORITY_MAP.md); these Markdown messages do not replace `relay/STATE.yaml`, transactions, DELP, Local execution/merge admission, or Owner approval.

**Preparation-to-Runner dispatch (Common #890):** Historical packet/blob readback is an **input-integrity gate only**. Before any clean Runner claim, an external operator must apply [the Stage 1 release/read-boundary contract](../../relay/CONTINUITY/OPERATOR_STAGE1_RELEASE_CONTRACT.md), record a [preflight receipt](../../relay/CONTINUITY/TEMPLATES/STAGE1_RELEASE_PREFLIGHT.md), and actually deny current A/Stage 2 and alternate GitHub/browser/connector access **from B's identity**. A link-free prompt alone is not a sandbox. See [the Relay dispatch runbook](../../relay/CONTINUITY/RUNNER_DISPATCH_RUNBOOK.md): if no actual independent model/session launcher with enforced historical-source access is available, create at most one authorized [dispatch-request Markdown record](../../relay/CONTINUITY/TEMPLATES/RUNNER_DISPATCH_REQUEST.md), return `DISPATCH_BLOCKED_NO_SESSION_CAPABILITY` with one external operator action, and stop the preparation subtask. Never recheck unchanged blobs on successive “continue/check” prompts, pretend a separate model has started, or self-approve Stage 1 isolation/freeze. A controlled technical handover and unplanned Two-/Three-Pass remain distinct flows.

## Embedded Coder contract

The machine-readable active contract is:

- `schemas/embedded-coder-context-v35.schema.yaml`
- `scripts/embedded_coder_v35.py`
- `tests/test_embedded_coder_v35.py`

The contract validates:

1. exact Local and V3.5 protocol refs/digests;
2. `PRD-*` Local identity and namespaced `ENG-PRD-*-CODER` engineering identity;
3. role fixed to `CODER`;
4. acceptance epoch/profile binding as read-only Local context;
5. explicit denial of Local transition/timer/merge/policy/risk authority;
6. Coder-scoped result semantics;
7. `local_responsibility_complete: false` for every V3.5 result.

## Completion semantics

V3.5 uses:

```text
RESULT_SCOPE = CODER_ENGINEERING_EXECUTION
ENGINEERING_RESPONSIBILITY_COMPLETE = true | false
LOCAL_RESPONSIBILITY_COMPLETE = false
```

Even when engineering responsibility is complete:

```text
ENG-PRD-017-CODER COMPLETE
```

Local remains responsible for:

```text
Coder END
→ Reviewer
→ Coordinator/Super Reviewer
→ delivery / merge lifecycle
→ Local responsibility completion
```

## Version drift

V3.5 never silently falls back to V3.1/V3.2 as active authority merely because copied files, CI names, migration fixtures, generated state, or historical references contain those versions.

Historical/compatibility reads are allowed only when explicitly classified as such.

If a later Relay version appears, the current nested execution remains pinned until the Local/Owner control plane authorizes migration.

## CI

Dedicated V3.5 hosted validation is `.github/workflows/engineering-pr-delivery-v3.5.yml`.

It validates the V3.5 active contract and verifies that the frozen `skills/engineering-pr-delivery-v3.2/**` tree is not modified by #494 work.

The DELP projection contract is validated by `.github/workflows/delp-projection.yml`, which runs on every pull request (path relevance is classified inside the job so the check is always terminal). V3.2 and V3.5 DELP engines are regression-tested independently; intentional V3.5-only evolution does **not** require whole-engine text equality with frozen V3.2. The workflow still requires exact equality for explicitly shared compatibility surfaces such as `continuity_projection.py` and `owner_commands.py`. Amendments to the frozen V3.2 tree remain authorised only through the base-pinned manifest `skills/Local_PR_Deliverty_v1.1/integration/frozen-v32-amendments.yaml` (`scripts/frozen_tree_guard.py`).
