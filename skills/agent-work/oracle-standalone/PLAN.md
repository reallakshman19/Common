# Oracle Standalone — skill implementation plan

**Proposal** · v0.1 · 2026-10-24 · **Mode: STANDALONE / NOT OTM**

This is a **plan for a new optional skill**, not an installed, activated,
or tested skill. Do not create `SKILL.md` until its contract and negative
tests have been reviewed. Planning this skill does not activate a
project's `CURRENT.json`, create a receipt issue, publish Progress Page
data, contact another chat, or grant access to Google Drive.

## 1. Owner's desired experience

The Owner discusses intent with Oracle in ordinary chat. Oracle displays a
compact, current **Agent routing board** showing role, Owner-supplied chat
display ID, actual evidence status, one next actor, and a one-line prompt.
The Owner sends only the line `Cycle now` to a registered coder,
reviewer or successor agent. An unregistered/cold chat receives one line
including the project's GitHub workspace URL.

The recipient fetches the **current GitHub state** and its own bounded
assignment, checks authority and actual files, does the permitted task,
and posts a traceable GitHub issue receipt. Restricted bytes use the
Owner's authorized Google Drive handoff folder. Oracle reconciles
receipts into an authorized next-state proposal and updates the
existing Progress Page via the official CLI when genuinely able.

**User success:** At the end of a real cycle the Owner can tell which
chat owns the next action and see the **same bounded status** in Oracle
chat and Progress Page **without copying a multi-paragraph brief**.
A prepared prompt, message sent, GitHub comment posted, hash verified,
test PASS, independently reviewed result, and Owner acceptance are
separate facts.

## 2. Established sources and non-negotiable limits

| Source | Responsibility | Limit |
|---|---|---|
| [Oracle Cycle protocol](../../../oracle-cycles/PROTOCOL.md) | One-line grammar, role checking, issue receipts and GitHub state publication | GitHub folder alone does not dispatch |
| [Example pilot current state](../../../oracle-cycles/p25b/CURRENT.json) | Exact project assignment and gate statuses | Currently `PROPOSED_NOT_ACTIVE`, revision 0 |
| [Manual routing convention](../oracle-chat-routing/STANDALONE.md) | Owner-readable role/ID and one-action board | A short chat ID is not identity authentication |
| [Oracle continuity contract](../oracle-continuity/PROTOCOL.md) | Optional durable session/assignment/decision relations | Not a compulsory second state store |
| [Progress Page](https://github.com/reallakshman19/progress-page) | Published project/agent cards and existing audit Timeline | Use `python tools/pp_cli.py`, not hand-edited JSON |
| [Drive policy proposal](https://github.com/reallakshman19/progress-page/pull/8) | Opt-in approved public **folder** URL in fixture field | Still a draft at planning; no reliance on merge |
| Existing `Common/relay/**` | Separate V3.1 execution/custody ledger | Do not edit or repurpose active `relay/STATE.yaml` |

The skill **cannot** watch other chats in the background, automatically
send messages to their text UI, authenticate a ChatGPT chat from an
eight-character URL suffix, claim control of Drive sharing, or grant
merge/release/engineering approval. It must refuse an action that needs
capabilities or authority the current runtime lacks. No OTM routing.

Writing a `SKILL.md` in GitHub will **not** by itself install the skill
in other ChatGPT conversations. A cold worker must still be given
the canonical workspace URL or use an available installed skill/connector.

## 3. Scope and boundaries

### Skill entry points (future)

1. **Owner intent:** update understanding and prepare one bounded next
   assignment while preserving original aim, frozen baselines, deferrals,
   and needed engineering approvals; do not fabricate state publication.
2. **Oracle `Cycle now`:** read canonical `CURRENT.json` at freshly
   observed GitHub main HEAD; read receipt issue events since the last
   accepted receipt; reconcile contradictions and select one safe action;
   update the chat board. Propose state/Progress writes only within
   authorized GitHub/checkout capabilities and verify readbacks.
3. **Coder/reviewer `Cycle now`:** read fresh canonical state and
   validate recipient role/short ID, active assignment and candidate;
   execute only the permitted scope; return actual evidence and a safe,
   read-back GitHub issue comment.
4. **New chat bootstrap:** `Cycle now: <absolute GitHub project-folder URL>`.
   Missing/ambiguous locator or multiple registered projects means
   request the specific URL; never guess.
5. **Read-only status:** a user asking about progress should not
   trigger write actions. Always show last-checked commit and separate
   current GitHub, received evidence, and Progress Page publication.

### Non-goals in v1

No daemon, cron, automatic notifications, multi-agent chat impersonation,
new role admission exam, approval automation, GitHub-to-Drive mirroring,
new Progress timeline, production controller, complex schema migration
or mandatory three-agent sequence.

Use existing repository protections and review policies. Workers may
do useful independently safe work when a separate dependency is blocked;
do not add a universal gate.

## 4. Proposed skill file tree

```text
skills/agent-work/oracle-standalone/
  PLAN.md                 # this proposal (first contribution)
  SKILL.md                # future host-facing concise instructions
  references/
    FRESH_CYCLE.md        # read order, roles, check before execution
    BOARD_AND_STATUS.md   # Owner routing board + freshness/status projection
    RECEIPT_AND_CAS.md   # issue transport, idempotency, stale return reconciliation
    PRIVATE_ARTIFACTS.md # Drive custody and public-safe reference strategy
    PROGRESS_ADAPTER.md  # official CLI commands, audit and publication readback
  examples/
    SYNTHETIC_CYCLES.md  # fictional plan→coder→IR→Owner paths and errors
  tests/
    test_cycle_contract.py  # optional read-only fixture/transition validator
```

Start with `SKILL.md`, `BOARD_AND_STATUS.md` and
`RECEIPT_AND_CAS.md` as the smallest coherent usable slice.
Create helper code only if a manual pilot finds a repeatable failure
that code can actually prevent. Do not duplicate the complete
`oracle-cycles/PROTOCOL.md` in the skill; **link to its pinned
effective revision** and read the live project state for work.

## 5. Board contract: derived, not independently edited

**Refresh on invocation**, not on a timer. The board's authority comes
from (a) the exact GitHub main commit + current state revision,
(b) accepted scope-bound receipt references, and
(c) independently read Progress Page publication status. Show
`UNVERIFIED_FRESHNESS` when any needed live source cannot be read.

Display:

```text
ORACLE CYCLE — <project> · <ACTIVE|NOT ACTIVE|BLOCKED>
Checked: Common/main @ <SHA short> · CURRENT revision <N> · <UTC/UNKNOWN>
Oracle   · chat <id8> · coordination        · <evidence-based status>
Coder    · chat <id8> · deliverables        · <evidence-based status>
Reviewer · chat <id8> · independent checks  · <evidence-based status>
Owner                  · acceptance         · <PASS|NOT_RUN|PENDING>
NOW → <one actor/id8 or “activate protocol first”>
PASTE → <exact one-line “Cycle now” or no message>
RETURN → <one exact receipt or artifact needed>
STOP IF → <one material hash/auth/role mismatch>
PAGE → <published revision|PENDING|OUT_OF_SYNC>
```

Prefer a compact card UI when supported, with meaningful text labels
and neutral status. Badges only if one status warrants attention;
never communicate PASS by green icon alone. Follow the Owner's
small routing-board visual, not a huge phase-by-phase wizard.

**Derive visible state:**
- If `activation != ACTIVE`, display **NOT ACTIVE**; a stored
  `next.recipient_role` is only **PROPOSED**, not dispatched.
- If `receipt_issue_url` is absent, do not say “worker can transact.”
- `Owner reports file attached` ≠ recipient received ≠ bytes verified.
- A review of a v0.1.1 runnable candidate does not verify its
  code-only package or the native Windows workflow.
- Only current candidate/revision evidence may support a current
  Gate PASS. `NOT_RUN` and failures remain visible.
- `Progress Page in sync` needs readback of the published project
  data + audited update, **not** merely a prepared PR or CLI command.
- When `CURRENT.json` changes, reevaluate affected old evidence and
  board text; don't carry a general PASS forward.
- When sources conflict, show the conflict and restrict only the
  affected next action. Do not auto-infer which chat is truthful.

The board itself is a **view**—never edit it as a separate GitHub
artifact. Only update canonical state and actual Progress projection.

## 6. GitHub/Drive/Progress transaction contract

### Fresh read

1. Resolve the explicit project folder, branch policy and main HEAD.
2. Fetch `CURRENT.json` and the protocol at the actual commit;
   validate schema, `mode=standalone`, activation and revision.
3. Check role/id8 binding and actual target assignment/generation.
4. Fetch real issue comments when an issue URL exists; dedupe receipts;
   locate accepted receipt IDs. If not activated, show board/STOP.
5. Consult actual private artifact only when authorized and needed.
6. Record `checked_commit`, `checked_revision`, observation method,
   data gaps and returned result in the current response.

### Recipient posting

Issue comment header `ORACLE-CYCLE-RECEIPT v1` with project,
receipt_id, assignment_id, observed_revision, role, id8, action,
candidate, bounded result, public evidence pointer, opaque private
receipt token, limits and next suggestion. Fetch the comment
permalink after posting. If posting fails, do not claim delivery.
Same receipt ID and same body can be treated as a retry; conflicting
body or stale revision is rejected/quarantined.

### Oracle publication

Oracle reconciles only applicable returns, preserves old failures,
then prepares a new candidate state on a branch. Publication requires
compare-with-current revision/HEAD and an authorized merge. Never
force-overwrite concurrent changes. An unmerged PR is a proposal,
and raw issue comments do not mutate the canonical `CURRENT.json`.
Owner acceptance is a separately authorized, source-grounded decision.

### Private artifacts

GitHub stores *public-safe metadata*. Private Drive stores real
protected ZIPs, engineering models and full manifests. The sender
may provide expected private SHA-256 and size, but the recipient must
download bytes and independently compute them; no filename/Drive
listing/ZIP CRC alone justifies “BYTES_VERIFIED.”

If GitHub is down, a restricted Drive fallback receipt may be used
only when actual access and permissions exist, marked
`FALLBACK_NOT_POSTED` until reconciled through an authorized
channel. Never paste customer details, unrestricted Drive child
links, approval keys or full chat URLs to public GitHub.

### Progress Page

Use existing `pp_cli.py` on an actual checked-out repository:
`plan chat`, `card set`, `fixture add`, relevant `check`,
`check --base`, GitHub PR/merge and server readback. Each write
requires `--actor`, `--src` and reason; no direct editing of
`data/<project>/audit.json` or shortcuts with GitHub file writes.

Projections keep the actual accepted claim scope. A public approved
Drive folder *may* be linked under an explicit policy if its URL
publication is authorized and the checker change is actually merged.
Private Drive child links remain off the public page. If no suitable
CLI execution environment is available, write
`PROGRESS_UPDATE_PENDING` and stop claiming synchronization.

## 7. Plan to build and prove

| Slice | Deliverable | Required demonstration |
|---|---|---|
| **S0 — Plan** | Owner-reviewed plan, source boundaries, scope | Correct link to Canonical Cycle protocol; no changed live state |
| **S1 — Minimal skill** | Short `SKILL.md`, board/status and receipt references | One read-only `Cycle now` displays accurate NOT ACTIVE P2.5-B board |
| **S2 — Writer receipts** | GitHub issue transport + small synthetic receipts | One assigned participant posts; readback permalink, duplicates idempotent, conflicting stale not adopted |
| **S3 — Oracle state advance** | Reconciliation guide + one actual authorized state PR | `CURRENT.json` revision advances only after merged commit verified |
| **S4 — Progress projection** | Actual `pp_cli.py` projection + tests | Public-safe standalone card update, audit event, base checks and published readback |
| **S5 — End-to-end pilot** | One private artifact checked + IR receipt + Owner walkthrough | Board/Progress refer to same claim, and remaining NOT_RUN stays honest |

**Pilot dependency:** the existing P2.5-B `CURRENT.json` must be
activated via a real dedicated issue + separately authorized revision 1.
A merged protocol/plan alone does not activate a task.

Do not automatically create more agents or repeat already decisive
engineering investigations merely to exercise the cycle.

## 8. Negative test matrix (must fail correctly)

1. Protocol PR merged but `CURRENT.activation=PROPOSED_NOT_ACTIVE`
   → board says NOT ACTIVE; `Cycle now` does **not** dispatch coder.
2. Cold chat receives only `Cycle now` without project/role context
   → ask for exact workspace URL, no guessed task.
3. Two projects registered with the same chat ID and bare command
   → ask which project, no silent selection.
4. Wrong chat ID/role or unknown Issue URL → NO ACTION/BLOCKED.
5. Owner says ZIP sent but receiver has not hashed it → OWNER_REPORTED.
6. ZIP checksum differs → STOP affected transfer; don't fix bytes.
7. Duplicate receipt ID exact retry → one logical receipt; conflicting
   payload → investigation, no silent state advance.
8. Stale old-version test PASS when candidate changed → old evidence
   retained, new claim NOT_RUN until applicable checks.
9. Reviewer self-reviews the code/premises it authored → scoped
   SELF-ASSESSED exposure, not universal independent PASS.
10. Browser injection PASS but no Windows run → Windows NOT_RUN.
11. Progress update PR open but not merged → PAGE PENDING, not SYNC.
12. Unauthorized/public Drive child URL or customer identifier
    → prevent publication and flag exposure.
13. GitHub posting tool not installed → blocked/fallback truth,
    not fabricated receipt permalink.
14. Concurrent `CURRENT.json` edits → reread canonical revision,
    no force-overwrite.
15. Owner asks only for status → no mutation or new participant.

Independent review of the skill itself should challenge at least
one plausible wrong result that would pass its happy-path demo.

## 9. Decisions reserved for Owner and integration

- Decide whether to activate `p25b` first or pilot with synthetic
  non-sensitive project; do not confuse activating a workflow with
  approving engineering data transfer.
- Decide what project-specific public routing metadata may be exposed;
  real private Drive URLs and full chat links remain private unless
  separately authorized.
- Keep cross-project role IDs scoped. A browser chat suffix alone
  never grants permission to post, approve, write or review.
- Owner controls any final software release or protected model change.
- Source-specific policies like frozen P2.1 and deferred P3 remain
  in the project state; the generic skill must not hardcode them.

## 10. Acceptance and release boundary for the skill

The first version can be called **usable as a standalone skill**
only when a fresh worker can discover it, render the correct
read-only board, execute one permitted GitHub receipt in an actual
repository, and show a safe negative case. A separate Project Cycle
pilot is needed before claiming a complete Owner→Coder→IR→Progress
closed loop. A copied document or passing static check is not
runtime deployment, cross-chat access, or Owner acceptance.

No `SKILL.md` is published in this planning PR. The implementation
will be a separate, reviewable PR after this design is approved.
