# Native GitHub title, Chat ID and traffic-light hygiene — Agent/Oracle OnBoard

**Reusable guide; no new issue/PR tracker, role, gate, approval or progress authority.**
Use *only* when an Oracle/OTM or directly coordinating Owner has an assigned native task and the selected native project's instructions allow title maintenance. First read [Common START_HERE](../../START_HERE.md), [existing Oracle OnBoard guidance](ORACLE_ONBOARD.md), the actual project's `AGENTS.md`, and (if selected) [Engineering Relay v3.5](../../../engineering-pr-delivery-v3.5/SKILL.md).

## 1. Title owner comes first — do not fight v3.5 DELP

**V3.5 DELP-projected GitHub issue titles are computed, never manually authored by an agent or Oracle.** The executable DELP `CHECKPOINT_FACTS_V1` plus current PR head/graph/evidence feeds a single authorized projector, which owns traffic light, hierarchy, `R:P/E`, `Φ:D/E`, `Π:D/E`, leaf unit/frontier and progress status. Do **not** hand-edit or append a Chat ID to a DELP-managed issue title, calculate P/E/D, copy an emoji verdict into facts or create a competing projection. Instead retain Chat ID in the existing **native assignment / issue body / task receipt**; request the publisher's current projection and read back the generated title. If the projector is unavailable, call it `PROJECTION_STALE` and continue already-authorized technical work unless a separately governing visibility or safety rule actually requires a stop. `Simplified=ON` exists only under direct Owner selection and does not waive real writer, native engineering or release rules. See [V3.5 DELP projection](../../../engineering-pr-delivery-v3.5/SKILL.md#projection-authority--delp-agents-publish-facts-only) and [owner checkpoint](../../../engineering-pr-delivery-v3.5/OWNER_CHECKPOINT_PROJECTION.md).

**Native PR title hygiene (when the PR title is human-authored and not project-controlled):**

```text
[<TASK-ID>][<ROLE>:<CHAT-ID8>] <specific artifact / repair / tested outcome>
```

Example **invented, illustrative only**: `[WP-07][G1:abcd1234] Preserve exact occurrence identity in XML trace export`.

- Retain the project-native required prefix/convention; append `[<ROLE>:<CHAT-ID8>]` only if permitted and readable. If the title has a strict project/projection grammar or a review tool rewrites it, **do not alter it**. Put `CHAT_ID8` in the PR body/assignment instead.
- `CHAT-ID8` is the exact short ChatGPT chat locator **supplied or verified through the selected Owner/Oracle routing record**. It is a *display locator*, not authenticated author identity, GitHub principal, permission, or evidence of independence. If unknown, use `CHAT_ID8: UNKNOWN` **in the body**, not an invented eight-digit token in a title. Track the real actor/role separately.
- Stable task identity and meaningful subject **precede** the display chat label. If replacing the agent, keep the task ID and change the effective actor/generation in the actual assignment; don't rename history or imply a fresh chat revokes the old writer.
- Describe *what changed or will be checked*, not `DONE`, `PASS`, `100%`, generic `fix`, exaggerated release approval, stale candidate hash or manually computed health. When a PR is draft or the candidate moves, current evidence lives in the body/receipt, not an unaudited green title.
- One PR / issue must have a clear owning task, effective role, branch/head and source; do not fabricate a Chat ID or post private customer identifiers in titles.

**Native project/coordinator issue title hygiene (only when no DELP or other title projector controls it):**

```text
<🟢 | 🟡 | 🔴 | 🔵> [<TASK-ID>][<ORACLE/OTM-CHAT-ID8>] <one actual current responsibility>
```

Example **invented**: `🟡 [G2-01][O:abcd1234] Verify original-source topology evidence`. Use only if the project's existing issue-title rules allow it. The issue body/source-backed comments still carry exact state, assigned worker/reviewer IDs and recent evidence; the emoji is a readable projection, not authority. Native issue ownership may be the Oracle while a separate builder owns its implementation PR; show both bindings, not a misleading single identity.

## 2. Traffic lights refer to observed work, not guessed agent health

| Light | When justified in a manually maintained coordination issue | **Not** evidence of |
| --- | --- | --- |
| 🔵 `PREPARED / UNASSIGNED` | Work defined but actor or execution not yet active; source fact with explicit next actor | Engineering progress, assigned chat, HOLD |
| 🟢 `ACTIVE / CURRENT` | An actually authorized actor is making bounded progress and current relevant evidence exists; no currently known impediment to the **named next task** | Full engineering PASS, independent acceptance or merged release |
| 🟡 `ATTENTION / WAITING / UNKNOWN` | Current-head evidence, access, receipt, return, reviewer, or publisher is incomplete/aging; Oracle has a feasible action | Whole-project blocker, Owner must act |
| 🔴 `ACTUAL BLOCKER` | A specific unsafe operation **cannot proceed** after a documented attempt; name exact failure, dependent action and legitimate next resolver | A protocol ceremony or a missing optional document, automatic block on disjoint work |

A failed source integrity/writer security check is a real stop **for the affected unsafe operation**, regardless of its title color. An independent review or Owner trial remains a genuine required **release claim** when selected, not a reason to prohibit accessible source investigation or disjoint prototypes. Do not infer green from CI alone, draft PR existence, synthetic test, elapsed time or self-ACK. When evidence is stale, preserve `UNKNOWN` rather than derive a fake percentage or switch to green.

**Minimal Owner-facing checkpoint (existing issue comment, not new ledger):**

```text
TASK: <native issue | candidate head | effective Oracle/agent Chat ID8 if confirmed>
LIGHT: <observed blue/green/amber/red + basis and scope>
DELTA: <only what materially changed, cite native evidence>
BLOCKER: <NONE | exact failed action / consequence / attempted remedy>
OWNER_ACTION: <NONE | REQUIRED — ONE Owner-reserved decision with source>
NEXT: <one executable actor/action with return location>
```

Do not paste this comment on every tool call or create duplicate issues. Update on consequential new evidence, ownership/recipient change, source/PR head drift, genuinely changed block, Owner decision, review return, or actual progress-page publication. The selected [Progress Page](../../progress-page/README.md) remains a source-backed **separate** projection; do not mark `PAGE: SYNCED` until real CLI publication/readback. V3.5's renderer owns its own compact Owner checkpoint where selected—this Markdown example does **not** replace it.

## 3. One practical pre-send/readback contract

**For Agent PR:** Oracle verifies exact assigned task + role + reported/verified Chat ID8 + native PR title owner + candidate head + writer permission. Agent publishes the real result and source-bound issue/PR evidence. If the PR title is manual, use concise hygiene; otherwise rely on native/projected title and put identity in the body. **A coder does not hand-calculate or edit DELP titles.**

**For Oracle issue:** Oracle verifies existing canonical issue, mode, Owner AIM, active/stale worker assignments and traffic state. Update only permitted manual issue title; otherwise leave it under the projector. Write the effective `OWNER_ACTION`, one next actor/action and source link in the existing issue body/comment. Re-read the actual published title/comment permalink. `NOT_PUBLISHED` is not `SYNCED`.

**For handover:** Freeze none of these statuses as timeless truth. The successor rereads canonical main, current issues, exact PR head, native work/receipt, identity and writer surface before acting. Do not rely on an old emoji, a prior author PASS, a bare Chat ID or a proposed Cycle revision. No new approval gate is introduced by title formatting.

## 4. Failure cases this hygiene must survive

- **H1:** A DELP generated issue title is manually changed with an emoji/Chat ID: next projector overwrite or drift rejection → put the label in assignment/body and refresh the canonical projection.
- **H2:** `CHAT-ID8: UNKNOWN` is filled with a plausible-looking invented value → preserve UNKNOWN and ask the actual coordinator/Owner routing record, not the Owner to repeat the whole project.
- **H3:** Same account uses a different chat ID to review its own PR → remains author-exposed/self-assessed for the affected independent scope.
- **H4:** Reviewer checked PR head A, new commit B pushed; manual green persists → mark applicable scope stale, re-evaluate changed evidence.
- **H5:** Browser test NOT_RUN due to one runner, but source investigation can proceed → amber for that evidence/claim, not project-wide red.
- **H6:** Unsafe overlapping active writer or unverified private receiver → halt the specific write/transfer, preserve other work and route the exact remedy.
- **H7:** A status-only "progress" title has no actionable subject/task/return → replace with concrete task and one executable next action.
- **H8:** A Chat ID label is treated as GitHub authorship or credential → disclose actual authenticated principal and authority separately.

**No implementation changes to V3.5 projection engine, Local v1.1 authorizations or existing title schemas are made by this guide.**
