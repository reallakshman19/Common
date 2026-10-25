# Agent / Oracle OnBoard — GitHub PR and issue title hygiene

**Reusable instruction for selected native work, not a new naming engine.** Owner asked that every dispatched agent's PR and coordinating Oracle issue be identifiable by **Chat ID**, with an evidence-grounded **traffic light** for Oracle work. The existing project-native naming convention, repository title limits and governing automated projector always win.

## 1. Identity: record two distinct facts, do not invent either

- **Chat ID8:** the short, eight-character chat display identifier copied from the **actual assigned conversation/Owner routing record**. It is a *routing locator*, not GitHub author authentication, reviewer independence or permission. Do not fabricate it. Before a recipient exists, use `chat:UNASSIGNED`; once legitimately known, update the *human title base* if the actor is still assigned.
- **GitHub principal:** the actual authenticated PR/issue commenter/author login, recorded in the body or existing native issue/PR metadata. A GitHub login never proves that a claimed Chat ID8 corresponds to that chat.
- **Stable assignment:** issue/WBS, existing Cycle role/assignment generation, parent and exact PR head; a successor gets a new generation while the original task identity remains. Changing a title does not reassign a writer or validate a reviewer.

## 2. Agent PR titles — human-readable base only

For **non-projector-managed** native PRs, suggested human title:

`[<PROJECT>][<ROLE>][chat:<ID8|UNASSIGNED>][<WBS-or-task>] <specific observable deliverable>`

Examples (ILLUSTRATIVE IDs, not issued participants):
- `[Project-X][CODER][chat:abc123de][T14] Reject stale source-pointer mappings`
- `[Project-X][SPECIALIST][chat:UNASSIGNED][F03] Trace original source field contracts`

**High-ROI accompanying PR metadata:** include actual native issue/WBS URL, parent objective, current baseline and exact head, permitted files/Writer grant (if relevant), original input/relay receipt identity, tested positive and *wrong* cases with commands/results, the remaining unverified test or consumer, and one next return/actor. Name the reviewer separately from the author. The PR title should not become a compressed evidence report. A PR created in the author account does **not** independently authenticate the claimed chat ID.

**When v3.5 DELP owns the issue/title projection** ([normative DELP source at Owner-pinned commit](https://github.com/reallakshman19/Common/blob/c9bf31fd6d88037c6a8e079e944485e33fcecd5e/skills/engineering-pr-delivery-v3.5/operating-model/durable-execution-lineage-projection-v35.md#title-grammar-generated-never-authored)), keep the stable project/task/chat label inside the **human responsibility suffix**, never hand-edit its generated `🟢 [#parent › #leaf → PR#N] R:P../E.. · U.. · STATE —` prefix. `CHECKPOINT_FACTS_V1` may publish only the declared leaf facts, candidate, evidence and next unit; agents **must not invent `P/E/D` percentages, activity epochs, progress weights, liveness, traffic lights or ancestor status**. Let the authorized projector derive status and correct title drift. If the native PR title is not DELP-managed, the human convention above is advisory and does **not** pretend the projector automatically manages PR titles.

**Human title hygiene:** concise action verb + bounded observable effect; one project and task; ID8 if actually known; avoid `DONE`, `PASS`, `MERGED`, `100%`, `INDEPENDENT`, `GREEN` or `RELEASED` unless the corresponding actual evidence/authority exists. No protected filenames, customer identifiers or Drive child links.

## 3. Oracle coordinating ISSUE titles — traffic light with evidence

Use on a **native coordination issue that is NOT already managed by a title projector**. When a selected Cycle or DELP controls a particular title, do not hand-edit generated output; put status and Chat ID in the permitted human title base or body / issue comment.

Suggested unmanaged Oracle issue:

`<LIGHT> [<PROJECT>][ORACLE][chat:<ID8|UNASSIGNED>][<cycle/WBS>] <one active decision or evidence frontier>`

Illustrative (not a real issue or asserted status):
- `🟢 [Project-X][ORACLE][chat:abc123de][T14] Source check running; next worker assigned`
- `🟡 [Project-X][ORACLE][chat:abc123de][T14] Exact-head evidence pending reconciliation`
- `🔴 [Project-X][ORACLE][chat:abc123de][T14] Private source unavailable after tested retrieval paths`
- `⚪ [Project-X][ORACLE][chat:UNASSIGNED][T14] Preparation only; actor not yet bound`

Traffic-light **scope is the specific next action**, not a synthetic whole-project completion score:

| Light | What must be OBSERVED | Action |
| --- | --- | --- |
| `🟢 GREEN` | Current actor and next work actually established; required sources/authority are usable for **this action**; no decisive contradiction in this bounded scope | Oracle executes/reconciles the next bounded task |
| `🟡 AMBER` | An important original/evidence/reviewer return is genuinely pending, stale, or partial, but useful source/other work can continue | Oracle resolves accessible uncertainty and states one actual next action |
| `🔴 RED` | A **concrete** unsafe or presently insoluble dependency after attempted remedies (e.g., unavailable protected input, active dual writer, conflicting Owner-only authority), with the blocked operation precisely named | Stop only the affected operation; report remedy attempted, required decision and continue unaffected work |
| `⚪ UNKNOWN/PREPARED` | Recipient not bound or actual source/observations missing; cannot yet honestly assert green/yellow/red | Inspect native truth, do not claim active or passed |

**Status source / update rule:** the issue body or existing native return records `OBSERVED_AT`, exact issue/Cycle revision or candidate SHA, source link, actual actor, `NEXT →`, `RETURN →`, and the smallest affected `STOP IF`. Only the authorized Oracle/OTM publisher updates an unmanaged issue title **after meaningful status change** and reads it back. No timer-based repaint, manual progress percentages, invented liveness or automatic Owner escalation. Blue `WAITING_*` and yellow `EVIDENCE_STALE` in v3.5 DELP are **projector-owned semantics** and must not be casually collapsed into this manually maintained RAG label on a DELP-managed issue.

**Liveness is external:** an agent cannot assert its own `QUIET`/`STALE` absent an actual observer; a last comment timestamp is not proof of substantive progress. If a PR head changed after review, note `EVIDENCE_STALE` for affected claims and recheck only those claims. Color never grants authority, acceptance, writer lease or release.

## 4. Minimal Oracle routing strip in the issue body

```text
AIM → <original Owner outcome + source>
ORACLE → <Chat ID8 as reported; actual authenticated GitHub principal separately>
CURRENT → <real active Cycle revision or native issue; PR SHA; observed_at>
ACTORS → <Coder/reviewer chat IDs, task/generation and latest return; or UNASSIGNED>
TRAFFIC → <LIGHT and one-line source-grounded reason; only affected action>
NOW → <one Oracle/agent action already authorized>
RETURN → <one native receipt/PR/issue permalink or NOT_POSTED>
STOP IF → <concrete unsolvable permission/source/writer conflict, not a ritual gate>
PAGE → <SYNCED only with actual authorized Progress Page write/readback; else PENDING>
```

No additional issue is required merely to hold this strip; update the **existing** Oracle project/WBS issue. The Progress Page Home/WBS projects reconciled native state through its existing `pp_cli`, not by copying this title or using a new private dashboard. **Owner intervention is reserved for an actual Owner-only scope/acceptance or a demonstrated inaccessible dependency; otherwise Oracle must execute.**

## 5. Drift, replacement and completion

On every actual actor/candidate handoff reconcile the human Chat ID, native assignment generation, write surface, exact input relay, current PR head and return destination **once**. Do not replay an already `RETURNED_RECONCILED` coder merely because the title still points at them. A stale title is repaired from current canonical evidence; the task and output remain the same. Successful merge is not proof of an original-file user trial, reviewer independence, recipient-byte custody or Owner product acceptance.
