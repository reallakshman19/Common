# Cycle Board — source-bound context and delta contract

**FROZEN owner projection — Task Evidence v2:** Reuse the existing source/CT-5 model to show source-backed [five-line cards](../../TASK_EVIDENCE_V2.md) for existing role-owned tasks on the **Board**, but **one acting-role-owned coordination card** in the Oracle's default `Cycle now` response; title/last-reconciled metadata are separate. No new reporting schema, WBS, actor assignment, Page write or technical PASS. Source status CURRENT/PARTIAL/UNKNOWN and TOTAL UNKNOWN denominators fail closed. [Merged Page PR #102](https://github.com/reallakshman19/progress-page/pull/102) implements the read-only renderer; live browser acceptance, agent delivery and engineering authority remain separate.

**Owner transaction surface:** Existing CT-5 may expose a compact, copy-ready [Action to Owner](../../TASK_EVIDENCE_V2.md#action-to-owner--one-copypaste-transaction-outside-five-lines) below the five-line cards. It is a read-only handoff surface: `CYCLE_NOW_TO_AGENT`, `CYCLE_NOW_TO_ORACLE`, `OWNER_DECISION`, or `NONE`, each source/role-bound; it must never count as delivery/ACK or bypass RECONCILE_FIRST/ACTOR_REVIEW_REQUIRED.

**Role / delivery boundary:** An Oracle coordination task must be grounded in actual existing evidence; do not invent a task/WBS simply to draw a third card. The Board's source-backed Agent/IR cards remain visible, not republished as Oracle work. CT-5 does not authenticate delivery/ACK; current-instruction `AWAITING_RELAY` needs a named actual relay actor.

**Status:** Contract merged in [Common PR #567](https://github.com/reallakshman19/Common/pull/567); implementations and human acceptance are independently reviewed. **AIM:** reusable information with minimal agent *and total* work. This remains an implementation interface for downstream agents, **not** a new coordination mode, required report, governing WBS, Cycle activation, or publication authority. Read [Cycle Board Protocols](CYCLE_BOARD_PROTOCOLS.md) for short Owner/Oracle commands and source-bound onboarding; [START_HERE](../../START_HERE.md) remains the role/mode router; see [vertical-slice handoffs](CYCLE_BOARD_VERTICAL_SLICES.md) for implementations.

## 1. Authority and product boundary

- `START_HERE.md` selects actual project, recipient, role, one governing Progress Page WBS, original inputs, and the already-selected OTM / standalone Oracle / direct Owner path.
- `Cycle now` remains the existing standalone invocation **only if** that project's Oracle Cycle is activated and assigned. Its canonical `oracle-cycles/<project>/CURRENT.json`, active assignment ID/generation/recipient, actual task, candidate, holds and accepted `ORACLE-CYCLE-RECEIPT v1` control execution. Never infer a Cycle from a Page key, a Board card, a short chat ID, a URL or this contract.
- Native issues, PRs, reviewed comments, tests and artifact-relay returns hold engineering evidence; the existing `ORACLE-CYCLE-RECEIPT v1` remains mandatory where the selected Cycle requires it. Never ask the worker to repost the same evidence in `CYCLE_TIMELINE_CARD v2`, a new Board form, or a second WBS ledger.
- **Cycle Board** is the read-only source-bound *current context, change discovery and continuation view*. It projects claims; it does not grant dispatch, acceptance, merge or Page write authority.
- **Audit Timeline** means the published append-only `data/<project>/audit.json`. `INFO_AUTO/SOURCE_RECORDED` derives from that audit without posting. Existing optional live `CYCLE_TIMELINE_CARD v2` events are separate reported observations, not a prerequisite to Board usability.
- **Page writer:** native source review → `pp_cli.py propose` / `pp_batch.py` dry-run → authorized Page update and checked append-only audit. No automatic `--apply`, Cycle state change or instant synchronization. Preserve `#/PROJECT/timeline-live` links if the UI is relabeled **Cycle Board**.
- The canonical rules in [Oracle Cycle](../../../../oracle-cycles/PROTOCOL.md), [Page modes](MODES.md), [Page data contract](DATA_CONTRACT.md) and [START_HERE](../../START_HERE.md) supersede a conflicting summary here. Implementation work begins in the reference `progress-page` repository, then syncs reviewed portable code into Common with parity checks.

## 2. Hard invariants

| ID | Non-negotiable invariant |
|---|---|
| CB-01 | No new mandatory worker/IR/Oracle Timeline post, check-in or repeated onboarding. Reuse native work, selected Cycle receipt and source-bound fixtures. |
| CB-02 | Exactly one governing project WBS (Progress Page). CT-1–CT-4 name *implementation slices*, not additional project WBS stages. |
| CB-03 | The Board is never the authority to start, reassign, retry, merge, release, accept or publish. A valid source link alone is not a verified claim. |
| CB-04 | Before any `CONTINUE_AUTHORIZED` advice under activated standalone Cycle, reread current canonical revision, assignment ID/generation, recipient/role, candidate, task, holds, source and relevant receipts. |
| CB-05 | Wrong recipient → `NO_ACTION`. Already returned + no new assignment → `AWAIT_ORACLE_RECONCILIATION`. Missing authoritative input → `UNKNOWN`, not a fabricated PASS or continuation. |
| CB-06 | An unbound project (notably CIIFR-Node) can show native/Page drift without a Cycle. It must show `UNMAPPED` and cannot infer one. OTM projects likewise do not acquire standalone Cycle semantics. |
| CB-07 | A matched `INFO/HANDED_OFF` can close only that communication Action; a *separate* independent technical IR action, test qualification or Owner decision remains distinct. No auto technical PASS. |
| CB-08 | One native source occurrence has one deterministic identity across Board, Agent Start, Oracle continuity, Smart Badges and proposed/published Page audit. Publication is not another engineering achievement. |
| CB-09 | Preserve six existing `project/type/key` Smart Badge types/IDs and source-or-UNKNOWN provenance: AIM, ROADMAP, WBS, PLAN, FIXTURE, ORACLE_CONTINUITY. They never imply approval. |
| CB-10 | Keep private/full chat IDs, private URLs, tokens and original restricted bytes out of public Page, Board snapshots, logs and issue comments; use public aliases/id8 or UNKNOWN. |
| CB-11 | Missing, inaccessible, ambiguous, stale, mismatched or contradictory sources fail closed with explicit cause and time. A viewer refresh is not a new source observation. |
| CB-12 | Source watcher/on-demand adapter may generate **regenerable ephemeral** output only; no parallel mutable tracker, implicit GitHub write, new scheduler, automated Page publisher or automatic coordinator selection. |

## 3. Shared read-model interface: `cycle-board.context/v1`

Downstream CT-1 produces this **read-only DTO**; CT-2 adds classifications; CT-3 consumes its source identities without treating it as proof. Use a pure constructor/validator independent of browser DOM and Page writes. Example below is structural, **not real project status**:

```json
{
  "schema": "cycle-board.context/v1",
  "project": "ciifr-node",
  "observedAt": null,
  "coverage": "UNKNOWN",
  "scope": {
    "wbs": "2",
    "pageCard": null,
    "mapping": "UNMAPPED",
    "pageRevision": "R1"
  },
  "cycle": {
    "binding": "UNMAPPED",
    "activation": "UNKNOWN",
    "canonicalRevision": null,
    "assignmentId": null,
    "generation": null,
    "recipientRole": null,
    "candidate": null,
    "authority": "NOT_ESTABLISHED"
  },
  "sources": [
    {
      "occurrenceId": "github:reallakshman19/XML_Compare_Utilities:pr-head:232:7f5dc773ac7bb08544d086be734e4337295088a0",
      "url": "https://github.com/reallakshman19/XML_Compare_Utilities/pull/232",
      "kind": "PR_HEAD",
      "immutableEventId": null,
      "headSha": "7f5dc773ac7bb08544d086be734e4337295088a0",
      "sourceAt": null,
      "observedAt": null,
      "claim": "SELF_ASSESSED",
      "evidenceStatus": "SOURCE_LINKED"
    }
  ],
  "delta": {
    "native": "UNKNOWN",
    "page": "UNKNOWN",
    "receipt": "NOT_APPLICABLE",
    "conflicts": []
  },
  "next": {
    "advice": "UNKNOWN_STOP",
    "responsibleRole": null,
    "sourceOccurrenceIds": []
  },
  "publication": {
    "status": "NOT_CHECKED",
    "auditEventIds": []
  },
  "badgeIds": []
}
```

**Required fields and semantics:** `observedAt` is the real successful source-read time (null if unobserved), never browser-render time. `coverage` = `COMPLETE | PARTIAL | UNKNOWN` for *explicitly configured* sources, not all possible GitHub activity. `scope.mapping` = `SOURCE_MATCHED | UNMAPPED | CONFLICT`. `cycle.binding` = `SCOPED | UNMAPPED | INVALID`; absent Cycle must not force native-source advice to UNKNOWN. Null means not established, not false. `sourceAt` comes from the upstream event if available; `immutableEventId` from GitHub when provided, never synthesized as a claim of independent identity.

An `occurrenceId` must distinguish distinct native occurrences (PR review, comment, commit, changed PR head) and remain identical when reread. For a PR-head observation, use immutable repo + PR number + exact head SHA; for comments/reviews use provider event ID and the inspected source ref. Do not use the mutable PR URL alone. Correlate published `audit.json` entries by original source identity, WBS and event kind; if linkage is ambiguous, `publication.status=REVIEW_REQUIRED` rather than claiming a unique match. Preserve audit IDs separately from native occurrence IDs. No new Page data schema is implied.

## 4. Deterministic delta and action contract

CT-2 classifies **independent axes**; do not compress authority, evidence and publication into one ambiguous `DONE` status.

| Axis | Allowed values | Decision |
|---|---|---|
| Native source | `UNCHANGED / CHANGED / UNKNOWN` | Compare exact event identity, candidate SHA and consequential claims; absence of a prior successful read is UNKNOWN, not UNCHANGED. |
| Page coverage | `CURRENT / STALE_PAGE / UNMAPPED / CONFLICT / UNKNOWN` | Compare governing WBS/Page source against fresh native evidence. Publication can lag without making native work invalid. |
| Cycle authority | `AUTHORIZED / WRONG_RECIPIENT / INACTIVE / UNMAPPED / STALE_ASSIGNMENT / UNKNOWN` | `AUTHORIZED` only after live canonical revision, generation, recipient, task, candidate and holds are verified. `UNMAPPED` is normal for non-Cycle projects. |
| Return state | `NOT_RETURNED / RETURNED_ACCEPTED / MISSING_ROUTING_RECEIPT / CONFLICT / NOT_APPLICABLE / UNKNOWN` | Retained native return ≠ missing Cycle routing receipt; repair the existing receipt only where required. |
| Evidence confidence | `NATIVE_OBSERVED / SELF_ASSESSED / INDEPENDENT_SCOPED / OWNER_DECIDED / UNKNOWN` | Preserve scope/limitations; never infer IR PASS, GPU/browser pass, Owner acceptance or release from a status marker. |

The derived `next.advice` is one of `CONTINUE_AUTHORIZED` (only after authority check), `NO_ACTION`, `AWAIT_ORACLE_RECONCILIATION`, `REVIEW_PAGE_DRIFT`, `SCOPED_CORRECTION_BRIEF`, `UNKNOWN_STOP`. It is **advisory**. A Board card must never cause a dispatch; display the exact authoritative source and responsible role or `UNKNOWN`. For a native-only Page drift, `REVIEW_PAGE_DRIFT` is permitted while Cycle remains `UNMAPPED`.

Interpret legacy v2 `ACTION` states `OPEN, IN_PROGRESS, BLOCKED, NEEDS_OWNER, WAITING`, `INFO` states `RECORDED, HANDED_OFF, DONE`, and audit-derived `INFO_AUTO/SOURCE_RECORDED` without forcing a new comment. Distinguish `PAGE_AUDIT.ACTION` (Owner decision audit) from `CYCLE_BOARD.ACTION` (operational pending step). Handoff resolution requires current matching `threadId`, `actionRef`, WBS and Page card; unmatched/stale follow-up stays unresolved. Do not default peer role to `REVIEWER_IR` without source evidence. A source can support `review requested` while `review started` remains UNKNOWN.

## 5. Minimal UI and consumer contract

First runnable URL: existing project Page with **Cycle Board** panel (retain `#/PROJECT/timeline-live` compatibility). Display only selected WBS/AIM, source freshness and coverage, current source-backed item/next, relevant native evidence, unresolved contradictions, and expandable prior Page audit; `INFO_AUTO` continues to work without a live comment intake. Separate canonical Cycle assignment from observed recommendation. A missing intake shows *No live intake configured*, never *all agents idle*.

`Agent Start` and `Oracle continuity` consume the **same immutable context/occurrence IDs**, scoped by existing task/WBS, not a rewritten summary or a new assignment. If no evidence justifies adding operational context, leave existing task packet intact. Exclude private IDs and unsupported badge claims.

**Existing UI reuse is required before a new Board presentation is authored.** [Progress Page PR #70](https://github.com/reallakshman19/progress-page/pull/70) merged the shared `cycle-board-context.js`, `cycle-board-delta.js`, `cycle-board-writer.js` and `timeline-live.js` integration; [PR #63](https://github.com/reallakshman19/progress-page/pull/63) merged the cross-view Smart Badge IDs. The CIIFR INFO-Auto surface derives current WBS-grouped source observations from **actual published Page audit** using `autoGeneratedTimelineCards`, `renderAutoGeneratedInfo`, `autoGeneratedPageBrief` and `smartBadgesForScope`. It preserves original audit IDs, source links, AIM/WBS/ROADMAP/PLAN/FIXTURE identifiers and the copyable grounding/Page brief. **Display operational task/WBS/INFO-Auto first, expandable source occurrence SHAs later**; never substitute a flat GitHub-URL list for the Cycle Board or fabricate agent status from Page data. [PR #100](https://github.com/reallakshman19/progress-page/pull/100) applied this reuse to TOPO-A/B, scoped to existing TopoFix Page WBS and original Adhoc native issues.

**CT-5 source-bound continuation, not authenticated messaging:** [Page PR #101](https://github.com/reallakshman19/progress-page/pull/101) reuses existing `agentStartModel` / `agentStartTaskText`, Oracle Continuity sources, `smartBadgesForScope`, original WBS/Page audit and native TOPO tasks in one shared read-only `cycle-board-continuation.js` viewer. **`Copy Cycle now` and private `My links` → `Resume Agent`** are copy/open controls only: no real message is sent, and no delivery, recipient identity, ACK or accepted return is claimed. GitHub issue posts are not conversation delivery. A Page `AGENT_RETURN` pointer is not recipient authentication; completed/returned/Owner- or reviewer-gated work stops for reconciliation. No project-wide public chat registry, new audit schema, WBS, Cycle dispatch or mandatory report. The [CT-5 trial documentation](https://github.com/reallakshman19/progress-page/blob/main/docs/CYCLE_BOARD_CT5_AGENT_CONTINUATION.md) separates verified code/browser behavior from the still-open human Oracle→Agent delivery/ACK test.

An established Oracle/agent may be told **"Cycle now"** as a *human-language native-task continuation shorthand*: actually read the Board, review relevant native source and prior return, then proceed only within the already-authorized native assignment. This is **not the activated canonical command** governed by the separate [GitHub Oracle Cycle protocol](../../../../oracle-cycles/PROTOCOL.md). The latter still requires actual `CURRENT.json` activation, recipient/generation and authority checks. **The coordination test fails** if the Oracle merely tells the Owner to start or re-onboard agents while never inspecting the Boards or previous returns; no new Timeline event or mandatory Board report is needed.


## 6. Integration and review rules

- No changes under `oracle-cycles/**/CURRENT.json`, native project task/issue, Page `data/**` or any independent review/Owner acceptance records in the contract PR.
- Use the existing `pp_cli.py cycle-preflight` **on consequential scoped Cycle/Oracle transitions**. It is read-only; `READY_FOR_REVIEW` is not binding activation or authorization.
- On-demand delta reconciliation first. `pp_watch_job.py` can provide the same read-only adapter when actual monitoring benefit and maintenance cost are measured; do not create a new scheduled obligation by default.
- Writer reviews originals and uses `pp_cli propose`, `pp_batch` dry-run, checker and reviewed publication through existing role authority. A proposed change is `PENDING` until actually merged; retain source→audit traceability and append-only ordering.
- Any downstream implementation must name the exact observed source revisions, actual executed tests, scoped NOT_RUN items, effort measurements and reproducible one-URL runnable artifact. An agent's statement or a schema-only implementation is not a passing user trial.
