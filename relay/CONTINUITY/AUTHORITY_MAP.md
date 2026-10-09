# Relay continuity source-of-truth map — WP0 research checkpoint

**Source basis:** `Common/main@d60c36605e988dcc160647421973f170fd87e0eb` inspected for [#890](https://github.com/reallaksh19/Common/issues/890). Describes **observed repository surfaces**, not an Owner-approved replacement schema or deployed V3.5 execution. Historical `Common@13989969...` is a protocol reference, **not** proof of any Agent A task-start HEAD.

| Fact / requirement | Existing canonical or observed source | Markdown continuity consumer | Risk / outstanding verification |
| --- | --- | --- | --- |
| Active Relay lifecycle, EP, lease, custody epoch | `relay/STATE.yaml` currently declares `schema_version: relay-v3.1` and EP/lease/epoch | Messages **reference**, not rewrite | Cannot automatically assume V3.5 nested Coder owns this V3.1 state; resolve in #890 WP0 |
| Parent/EP roadmap and accepted denominators | `relay/ROADMAP/ROADMAP.yaml` plus authorized plan/version | Original Owner/coder identity field | Do not create a new EP, leaf, unit weight or approved scope through continuity |
| Event history | `relay/EVENTS.jsonl` | Evidence refs only | New free-text chat is not a logged authorized transaction |
| Accepted checkpoints and handover frontier | `relay/CHECKPOINTS/` and `relay/GENERATED/CURRENT_SNAPSHOT.yaml` | A current technical handover must cite exact checkpoint and observed SHA | Snapshot may be stale after head/plan movement |
| Transaction preparation and custody | `relay/TRANSACTIONS/`; [V3.5 handover source](../../skills/engineering-pr-delivery-v3.5/scripts/handover_context.py) | Technical handover MAY project exact facts from existing `HANDOVER_CONTEXT` | Never copy transaction as a second authority or mark agent prose as provider-observed |
| Lease, Local writer, reviewer and merge | `relay/LEASES/`, Local PR Delivery v1.1, external provider/credential authority | Owner decision contains **references only** | B may NOT gain actual write by possessing an MD token or approval phrase; old A direct GitHub rights must be revoked separately |
| Original Owner instruction | Authenticated Owner input where available, or citable GitHub mirror with explicit lower trust | Stage 1 source intake only | Original private-chat location may be UNKNOWN; do not cite a mirror as direct authenticated Owner |
| Current A implementation / PR and test SHA | Exact provider repository refs, committed code, current task evidence | Technical handover visible in Stage 2 | A claims != source/provider verification; original historical SHA != actual A start or latest candidate |
| Canonical progress / titles | V3.5 accepted `TASK_EVIDENCE` / `CHECKPOINT_FACTS_V1` and sole DELP projector | Continuity reports facts and references, not P/E | No issue-title/manual score edits, new denominators, duplicate progress system |
| Runner expected context consumed | Provider same-session used/usable telemetry, or labelled operator proxy / observed risk | Stage 1 intake trigger provenance | No automatic provider telemetry; DELP health/P/E do NOT measure context life |
| Task-blind two-pass request | [standalone Two-Pass schema](../../skills/two-pass-prompt-generator/schema.md); explicitly requested generator | Unplanned/no-prepared-B routing only when selected | Ordinary handover **does not** generate Two-Pass; task-aware planned Runner is different |
| Broader three-pass reasoning | [standalone Three-Pass generator](../../skills/three-pass-prompt-generator/SKILL.md) | Optional unplanned broadened recovery | Canonical 0.5/1/2/2.5/3 sequence; not a substitute for old-writer fencing |

### R14 typed-contract reconciliation and owner migration (source inspected at draft WP2/U01 head)

R14's current unmerged U1→U2→U3→U4→U5 source uses **typed, non-authoritative** identities: `PLAN_GRAPH_REVISION`, `SESSION_SOURCE_COMMIT`, `CODE_CANDIDATE_HEAD`. U2 Owner/session events are GitHub-mirror/actor **claims**, not authenticated Owner or executor fencing. U3's current PR/issue/test/review structure is **same repository** and exact HEAD, but a different reviewer label is not proof of distinct principal. U4 proves canonical bytes agree across languages; U5 calls real V3.2 DELP in a **read-only untrusted-evidence quarantine**, not a publisher. The Runner/technical handover must **reference** these values only after actual admission; no second R14 canonical data model in Markdown.

**Repository split:** Historical issues and PRs #890/#893 and R14 #891/#894/#895/#896/#897 exist in `reallaksh19/Common`; code and draft branches exist in `reallakshman19/Common`. The new repository initially lacks those old issue/PR objects (and has a new integration issue [#1](https://github.com/reallakshman19/Common/issues/1)). Git commit equivalence does **not** transfer issue, PR, review, workflow or credential identities. An R14 U2 exact-repo Owner-event locator cannot be made provider-authenticated by editing its owner slug. Preserve old URLs as historical facts, bind any new objects by fresh provider readback, and hold evidence/publish/writer transitions pending an approved explicit cross-repo lineage mapping.

### Negative authority assertions

- Neither `relay/CONTINUITY` Markdown nor a Stage 1 freeze can grant Owner approval, Local execution, PR publication, merge or GitHub push rights.
- No new `STATE.yaml` values, event kinds, Python dispatchers, YAML status shadow, schema migration or new source writer are introduced by this WP0/WP1 doc slice.
- A Stage 2 technical handover reads **actual** source and existing transaction/provider receipts; the handover record is a claim-and-reference envelope, not a new transaction.
- A successor asking for full repository/connector visibility **before** Stage 1 freeze cannot honestly claim clean independence.

### WP0 decisions still required

- [ ] Select one permitted existing-responsibility/episode naming rule and confirm whether `relay/CONTINUITY/episodes/` is necessary or the existing handover transaction should carry some records.
- [ ] Establish trusted actor/authentication and branch/visibility rules for each message class.
- [ ] Demonstrate actual Stage 1 restricted Git read paths or defer A reality publication to post-freeze.
- [ ] Confirm how current V3.1 Relay state, nested V3.5 Coder and Local writer map without state migration.
- [ ] Approve modified Stage 1 semantic acceptance before any live Runner rollout; record independent test results and source hashes.

**WP0 finding:** repository-grounded authority map compiled; controls/deployment/Owner review **NOT APPROVED**. Markdown is now the proposed human-agent communication surface, not the definitive operational control plane.
