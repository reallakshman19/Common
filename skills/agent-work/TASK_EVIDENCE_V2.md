# Task Evidence v2 — FROZEN Owner-facing Cycle now projection

**Owner decision: APPROVED / FORMAT FROZEN (31 Oct 2026).** This five-line card is a compact, read-only view of *existing* project evidence. It is not a new task, WBS, receipt, report, transport, acceptance or engineering authority.

**Scope:** one card per **existing role-owned task**, exactly **five information lines** under the task title, with a separate last-reconciled/source-status header. The Cycle Board may show all source-backed tasks; the acting participant's `Cycle now` response defaults to **its own task only**. Reuse the current governing Progress Page WBS, original issue/PR/relay records, Page audit and canonical Cycle only if actually selected.

## Exact frozen format

Task Evidence v2 · [Project / Agent / Task]

Last reconciled: [actual recorded reconciliation time, else NOT_VERIFIED] · Source status: [CURRENT / PARTIAL / UNKNOWN]. An ordinary source fetch time cannot be relabeled as Oracle reconciliation.

1. **TASK:** [repository] · WBS [ID] · [native issue] · PR [number/verified state, else STATUS UNKNOWN] · [Progress Page]
2. **PROGRESS:** [completed/agreed deliverables] · current task [completed/total or TOTAL UNKNOWN] · acceptance [level and asserting/verified authority]
3. **WORK & PROOF:** [actual work/measurements] · [original evidence permalinks] · tests [PASS / FAIL / NOT_RUN / UNKNOWN within executed scope]
4. **BLOCKERS & RELAY:** [native return/link or NOT_VERIFIED] · [review/authority] · [blockers and engineering/release HOLD]
5. **NEXT → [ONE ACTOR]:** [one bounded still-authorized action] → [expected evidence/output] → [exact original return location]. [permission/restriction]

Do not guess totals, percentages, completion, timestamp, recipient delivery/ACK, original bytes, PR status or technical acceptance. **TOTAL UNKNOWN** is not zero. Work performed, native evidence returned, acceptance and release are **four separate levels**. An Oracle-labeled GitHub comment is an Oracle-*reported* claim until its actor and authority are established. No native return/PR link alone proves engineering PASS.

## TE2-ROLE — acting role, Board hierarchy and cycle completion (O4)

**Mandatory on every `Cycle now`** (including native-task continuation). First establish the already-authorized **acting role**, its *own* actual task/responsibility, and the selected transport/mode. Do not acquire Oracle/Agent/IR authority from a nickname, Board card, chat URL or Task Evidence heading.

- **Agent / Builder:** one five-line card for its assigned engineering task and scoped evidence. It never publishes a coordinator report.
- **Independent reviewer:** one five-line card for its assigned independent review; distinguish review from agent PASS.
- **Oracle / OTM coordinator:** by default **one five-line coordination card per real coordination responsibility**, covering subordinate agents through original native evidence links. Report the coordinator's own reconciliation, decisions, acceptance/rejection, current instruction, delivery/ACK, blockers and next coordination action. **Do not republish subordinate cards as the Oracle's work.** Do not create an Oracle task or WBS simply to fill a card. If coordination provenance is missing, state NOT_VERIFIED.
- **Cycle Board:** may display all *existing* source-backed role-owned cards. This does **not** require the Oracle to reproduce them in chat. When the Owner explicitly asks for team/agent detail, provide subordinate cards with original evidence links and unchanged ownership.

**Current-instruction closure:** Treat `PREPARED`, `POSTED`, `DELIVERED`, `ACKNOWLEDGED`, `EVIDENCE_RETURNED` and `ORACLE_RECONCILED` as distinct *observations* scoped to the **current next instruction**, not automatically completed stages. A native issue comment is POSTED only; CT-5 copy/open proves neither delivery nor ACK. A later verified native return may evidence continuation even if separate chat ACK was not captured. Previous return/acceptance does not prove delivery of a subsequent instruction.

After coordination, declare exactly one outcome **outside the five lines** (never a sixth information line):

- `CONTINUED` — intended agent acknowledged the **current** assignment, or its source-backed later execution/return establishes continuation.
- `AWAITING_RELAY` — current authorized instruction is ready/posted but actual delivery/ACK is unverified; name the missing route and one accountable relay actor.
- `BLOCKED` — actual identity, custody, source, authority or engineering restriction prevents this next action; name the blocker/owner. Unrelated authorized work need not stop.

**Owner relay boundary:** If the Oracle has no authenticated way to send to a separate agent conversation, identify one minimum copy-ready Owner relay where actually necessary; the Oracle retains overall coordination. Do not say no Owner action is needed if delivery depends on that action. Never claim background dispatch or monitoring.

**Mode guard:** An established **native-task** continuation does not require an activated `oracle-cycles/<project>/CURRENT.json`. Read the formal Cycle activation, assignment/generation and receipt gates **only if that formal transport was explicitly selected**. Its authority then remains controlling; neither route relaxes engineering HOLDs.

**Freshness guard:** Compare latest native evidence against the published Board occurrence. A newer return requires a source-backed delta or `PARTIAL / NOT_RECONCILED`, not stale totals. Browser `NOT_OBSERVED` is not evidence failure and does not block unrelated authorized work.

**Acceptance falsifier:** One existing Oracle responsibility covering two agent tasks → Oracle `Cycle now` response defaults to **one Oracle-owned five-line coordination card**; Board may show the two agent cards; if the current instruction is posted but no actual delivery/ACK or subsequent return exists, outcome is `AWAITING_RELAY`. Two subordinate cards alone fail this rule.

## Required when Cycle now is triggered

1. **Read Cycle Board first** as the operational read-view: current AIM, one WBS, INFO-Auto, Smart Badges, task, source revision and delta, prior return, active actor and HOLD. This is not a new coordination mode, assignment or source of authority.
2. **Reconcile original evidence** from native issues, PRs, source bytes and Common relay. If the Board cannot be rendered or is stale, use original sources and report BOARD_NOT_OBSERVED / PARTIAL / UNKNOWN, not a fabricated successful Board check.
3. **Select by acting role:** Oracle shows one own coordination card by default, Agent/IR shows its own task. Board may show every role-owned card; show subordinate cards in Oracle chat only if explicitly requested. Do not create an Oracle task solely to produce a card.
4. **Resolve the current next action:** Oracle selects one actor/action, dispatches only via an authorized route, or states `AWAITING_RELAY` and the minimum relay needed. Keep POSTED, DELIVERED and ACK separate. Agents follow only existing authorized work. CT-5 does not send.
5. **Return evidence once** in the original native issue/approved Common relay, and update Page through its existing reviewed writer route if a material source-backed status changed. Page publication is not technical acceptance.

For an explicitly activated formal GitHub Oracle Cycle, main CURRENT.json, active assignment, generation, recipient and receipt gates remain controlling; the Board and five-line card are supplementary.

## Reuse, tests and limits

Use the existing Progress Page Cycle Board and CT-5 context; **no parallel tracker, WBS, task schema, status log or reporting duty**. The existing renderer merged through [Progress Page PR #102](https://github.com/reallakshman19/progress-page/pull/102), reusing [CT-5 PR #101](https://github.com/reallakshman19/progress-page/pull/101). Source code merge is **not** proof of live interaction, agent-message delivery/ACK, original-source qualification or technical acceptance; use native occurrences for freshness.

Negative cases: wrong project/WBS/issue/comment/PR identity, forged acceptance, reported-vs-independent review, missing/stale source, UNKNOWN denominator, unexecuted test, private-chat leak, and any attempt to turn copying a prompt into agent ACK. Keep all source details behind original links.

**Owner instruction:** `Cycle now` in existing Oracle chat → verify own role/mode → Board and latest native evidence → **one Oracle-owned five-line coordination card** → one authorized action + `CONTINUED / AWAITING_RELAY / BLOCKED`. Agent/IR chat selects that actor's own task. The Board may display all role-owned cards. No long reconstruction unless requested.
