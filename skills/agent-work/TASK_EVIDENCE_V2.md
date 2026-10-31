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

## Cycle now Fast Lane — bounded execution within the existing native task (F1)

**Activation:** Every established `Cycle now` first reconciles changed Board/native evidence, verifies the *acting role* and selected native/formal transport, then checks whether the **existing native instruction already authorizes the next substep**. Fast Lane is an interpretation of the *same approved assignment*, **not** an AUTO MODE, new WBS, new Cycle, new role, self-granted authority, asynchronous task or cross-chat dispatcher. An illustrative envelope never retroactively authorizes past or future work.

### Execution Envelope — subsection of the original native issue instruction only

The Oracle/coordinator may authorize a **bounded sequence of related substeps** within one existing task issue. The envelope must identify: existing task/issue and WBS; actual Agent/IR recipient; authorizing actor plus exact native instruction permalink; pinned original source/PR head, SHA/config/generation and permitted fixtures; selected mode; read-only or other already-established permission; **enumerated permitted substeps**; expected evidence/output and *single original return*; explicit `CONTINUE_WHEN`, `STOP_WHEN`, HOLD/prohibited actions. **No separate envelope file, registry or receipt schema**. The Agent may inspect and compare these fields, but cannot author, expand, silently renew or reinterpret the envelope. Mere NEXT text on the Board is never an envelope.

- `WITHIN_AUTHORIZED_ENVELOPE`: same authentic recipient/task/source scope, explicit permitted next substep, still-valid pinned baseline and authority, no critical contrary result, no scope/risk/actor change, and no stop condition. **Execute the remaining permitted related work now in the active invocation** without asking the Owner/Oracle to reapprove each microstep; preserve original evidence identities. A writer-related HOLD does not prohibit unrelated, separately authorized read-only work.
- `NEW_AUTHORIZATION_REQUIRED`: task/substep not explicitly permitted; scope exhausted or different actor/source SHA/config/permission/risk; engineering interpretation/private bytes/independent acceptance/writer lease requested; critical falsifier failed; or proof of any required identity/authority missing. Stop the **affected** action, record actual contradiction/UNKNOWN and send it to the existing Oracle/authorized decider. Do not bootstrap permission from passing tests.

**Scoped HOLD:** `PRODUCT_WRITE`, exclusive writer, physical design intent (including TOPO-A 240.6 mm join), unsupported GLRD/CII profile, independent browser/original-file evidence, merge and release are separate gates. Apply a HOLD to the affected action and source scope; unrelated explicitly authorized read-only investigation may still proceed. A changed source SHA/generation requires requalification of affected evidence before its reuse. Never treat implementation-coupled or agent self-tests as independent engineering PASS.

### Oracle's same-cycle decision and changed-only return

An Oracle receiving a newly returned result must **perform any source review, qualification, existing-authority decision or feasible coordination in the same invoked turn**, rather than outputting `NEXT → ORACLE: investigate` for work already within its competence, available sources and authorization. Where genuinely missing authorizations or independent authority are required, state the exact `OWNER_DECISION`, independent-review handoff or scoped HOLD and stop only that dependent action. Review a completed assignment as `RETURNED / ORACLE_RECONCILED` without reflexively issuing the next Agent microtest. A newly selected actor or new execution envelope requires actual authorized handoff; copy/open still does not send or ACK.

**Evidence once:** Reuse previously verified 3/3, 6/6, 8/8, 12/12 or 7/7 examples as source links; do not rerun them without source change or explicit independent-review requirement. Append **one meaningful changed-only native issue/approved relay return** for newly executed scope, contradiction or decision; do not repeat old history. No new evidence, decision, authorized execution or genuine blocker change means **no new substantive native status comment**—the acting-role five-line card may simply say `NO_MATERIAL_DELTA` with original links and `Action to Owner: NONE` when accurate.

**Fast Lane completion:** `Cycle now` → reconcile changed native evidence → check exact bounded authorization → execute **all related permitted substeps in this active invocation** / perform immediately available Oracle decision → return one evidence delta at original source → five-line acting-role Task Evidence v2 → `Action to Owner` **only for a real Owner-dependent relay/decision**. No background execution after the conversation ends, no new transport, no new approval from this instruction.

**Conservative fast-lane falsifiers:** completion of a substep with an explicitly permitted successor may continue; exhausted assignment cannot dispatch; returned work goes to Oracle review; unknown writer custody blocks only writes; changed source/authority invalidates the affected envelope; critical failure stops affected scope; Board unavailable falls back to native `NOT_OBSERVED`; Copy/Open never proves delivery/ACK; independent validation remains a separate approval gate; no Owner dependency yields `Action to Owner: NONE`. These are behavior requirements, **not prior engineering test results**.

## Action to Owner — one copy/paste transaction (outside five lines)

After the acting participant's five-line Task Evidence v2 card, show a **small `Action to Owner` section** only if the Owner must paste a message, make a decision, supply protected input, or unblock a verified dependency. This is presentation of the same native task/relay and not a sixth information line, new task, report, or automatic dispatch. If no action is required, write **`Action to Owner: NONE — [source-backed reason]`**, without an inert copy block.

**Select exactly one primary transaction type per accountable next actor:**

- **`CYCLE_NOW_TO_AGENT`** — Oracle has an *existing authorized* next instruction for a named established Agent/IR, but actual chat delivery/ACK remains unverified. Provide the exact existing recipient chat label (private URL only in private UI), native task, original instruction permalink, current scope/HOLD, expected return and evidence destination. If two independent recipients genuinely require manual delivery, supply **one separately labeled block per necessary recipient**, each linked to its own original issue. Never infer authorization merely from a Page NEXT label.
- **`CYCLE_NOW_TO_ORACLE`** — acting Agent/IR has returned native evidence and needs Oracle reconciliation, or Oracle must resolve stale/unknown scope before agent work. Tell the Owner which **existing Oracle chat** receives this message, and include the exact native return/issue so Oracle can continue without onboarding.
- **`OWNER_DECISION / OWNER_INPUT`** — a genuine Owner-only acceptance, custody/access or direction gate remains. State the *specific decision/input* and native issue; do not bury this behind an executable Agent prompt or invent a permission.
- **`NONE`** — Oracle can proceed through an actually authorized channel and no Owner dependency exists. State this explicitly; `POSTED` alone is insufficient to claim the work reached the Agent.

**Minimal Owner presentation (only when an action is needed):**

**Action to Owner · [CYCLE_NOW_TO_AGENT / CYCLE_NOW_TO_ORACLE / OWNER_DECISION] · Recipient: [existing chat/role or decision owner] · Status: [AWAITING_RELAY / BLOCKED]**

Copy into the *existing* [Agent / Oracle] conversation (not sent):

```text
Cycle now — [Project] / [existing role] / [original native issue or task].
Read [Cycle Board] and [latest native instruction/return permalink].
[One bounded authorized next action OR request for missing Owner decision; no replay].
Return [specific evidence/output] to [original native issue / approved Common relay].
Preserve [READ_ONLY / writer ownership / HOLD / no merge].
```

**Other issues needing Owner attention:** [one short source-linked item, or NONE]. Avoid duplicating issue histories or printing subordinate Agent cards.

**Hard gates:** The current actor supplies a **real actionable instruction and exact recipient**; do not generate a generic role-swapping prompt when those are UNKNOWN. A previewed/copied block is **NOT_SENT**. Require actual recipient delivery/ACK or source-bound subsequent return before `CONTINUED`. If a current native Agent instruction is stale, completed, unverified or awaiting Oracle review, default to **`CYCLE_NOW_TO_ORACLE` for reconciliation only**, never to an executable Agent dispatch. This applies to direct Agent/IR returns as well as Oracle coordination reports, and to the Board's copy-only CT-5 view.

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
