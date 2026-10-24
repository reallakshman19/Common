# P2.5-B Oracle Cycle — plan first

Status: PROPOSED / NOT ACTIVATED · 2026-10-24 · Mode: STANDALONE (no OTM)

## 1. Owner outcome

An Owner talks naturally to an Oracle, sees a current routing board and progress in that Oracle chat, and sends at most a **one-line trigger** to an existing coder, independent reviewer or new participant. The recipient opens the project-specific GitHub folder, discovers its assigned task and sources, does the bounded work, and posts a traceable GitHub receipt. Private ZIPs and engineering material stay in the Owner's Google Drive Handoffs folder. Oracle reconciles the receipts and updates the Progress Page. No need for the Owner to ferry full prompts or repeat context.

This is a shared-file *manual* cycle, not an always-on bot, OTM route, controller, automatic chat broadcast, or Owner acceptance delegate.

## 2. Evidence from inspected sources

- `Common/relay` at `04226c944f417482d8335829faedfb77eafcae1a` already has a V3.1 execution/custody ledger for **another active work package**. Reuse its ideas (checkpoint, explicit handover, expected state, unique transaction) but **do not edit** `relay/STATE.yaml`, leases, events or transactions.
- `Common/skills/agent-work/oracle-chat-routing/STANDALONE.md` provides human-facing chat-id8 routing, manual handoff and evidence labels; it is not itself a GitHub message bus.
- `progress-page` presently requires all writes through `python tools/pp_cli.py`; this preserves its append-only Timeline and checks data. Existing `ciifr` cards describe an older workstream with a placeholder aim, so do **not** silently overwrite them.
- The Owner's existing Drive **Handoffs** folder contains real engineering files. Folder listing is not proof that particular files are protected, shareable to any participant, or hash-verified. Public GitHub must not contain restricted files or their direct links.
- Progress Page PR #8 proposes an opt-in `OWNER_APPROVED_PUBLIC_FOLDER` fixture URL exception; it is a **draft, not merged** as inspected. Do not rely on it until merged.

## 3. One canonical pointer and minimal files

Proposed public-safe project folder:
`https://github.com/reallakshman19/Common/tree/main/oracle-cycles/p25b`

| File/surface | Purpose | Writer |
|---|---|---|
| `oracle-cycles/PROTOCOL.md` | One-line grammar, receipts, validation, safety | Reviewed protocol PR |
| `oracle-cycles/p25b/CURRENT.json` | **Single canonical current assignment and gate state**, once merged | Oracle proposal; Owner-controlled merge |
| `oracle-cycles/p25b/README.md` | Stable project entrypoint linking CURRENT, protocol and transport | Oracle reviewed change |
| Dedicated GitHub issue (created on activation) | Append-only **inbox** for actor return receipts, with stable issue number | Authorized worker/reviewer comments |
| Existing Google Drive Handoffs / project subfolder | Private ZIP bytes and private evidence manifest | Authorized custodians |
| Progress Page `p25b` tab (separate from old `ciifr`) | Sanitized **projection** of accepted current state | Oracle through official CLI + reviewed PR |

A GitHub issue comment is **a proposed receipt**, not a mutation of the canonical `CURRENT.json`. No participant edits project state directly. Oracle reconciles receipts, issues a fresh proposed state on a branch, and Owner-controlled merge advances the canonical revision.

This two-part transport is the minimum needed to avoid agents racing to overwrite shared JSON. It is not a second task tracker: the issue is an event inbox and CURRENT is the only effective snapshot; Progress is a presentation of that snapshot.

## 4. One-line command and bootstrap

Established chat (after one-time successful registration):
`Cycle now`

New, cold or replaced chat (must include locator once):
`Cycle now: https://github.com/reallakshman19/Common/tree/main/oracle-cycles/p25b`

The second form is the **default** whenever there is any uncertainty about prior registration. A chat cannot infer the repository/folder, access a different chat, wake other agents or run in the background. An agent without tools/access must say BLOCKED and ask for an authorized file/issue relay.

The respondent reads fresh `main` at invocation, checks its own Owner-registered **display** ID and role against the active assignment, checks the expected candidate/version and authority, and performs only its assigned next step. The eight-character chat suffix is a routing label, never proof of agent identity, principal or review independence.

## 5. Minimum transaction

Actor submits one public-safe GitHub issue comment headed `ORACLE-CYCLE-RECEIPT v1` with:
`receipt_id`, `project`, `assignment_id`, `observed_current_revision`,
`role`, `chat_id8`, `action`, `result`,
`candidate_id`, `public_evidence_ref`, `private_receipt_token` if required,
`limits`, and `next_claim`. The issue-comment permalink is the durable
readback receipt. Repeated `receipt_id` means **idempotent conflict/retry**;
a conflicting payload must not be silently overwritten.

Only Oracle proposes `CURRENT.json` advancement. It cites exact receipt permalinks, compares the current revision/head with the revision read before evaluation, and avoids force-overwriting concurrent updates. The public board can show "Owner reported sent", "recipient confirmed", "bytes verified", "self-tested", "independently tested", and "Owner accepted" separately.

## 6. GitHub-first, Drive private fallback

Normal message transport: GitHub issue comments and PRs. Artifact transport: a public-safe GitHub artifact only if explicitly appropriate; otherwise **private Drive**. Never upload a customer CII/XML, protected-code ZIP, private signing key, unrestricted Drive child URL or full chat URL to the public Common repo, public issue or Progress JSON.

Each private artifact is named by an opaque private receipt and hashed from **downloaded bytes** by the receiving agent. A file name or coder manifest cannot verify identity. When GitHub commenting is unavailable, save a private fallback receipt in Drive and relay only its opaque reference; mark receipt not yet GitHub-confirmed. When neither mechanism is accessible, stop that transfer without fabricating confirmation.

## 7. Progress Page projection

Oracle reads owner intent + canonical `CURRENT.json` + evidence receipts, chooses one justified next state, and updates a separate standalone `p25b` project through the **real `pp_cli.py`**, not manual JSON changes. Suggested four cards: Oracle, Coder, Independent Reviewer, Owner Windows. Store short chat IDs and opaque receipt references; never mirror the private manifest into public data. Use `OWNER_PRIVATE_REF:<opaque-id>` for private sources.

If Oracle cannot execute the official CLI in an actual checkout, it prepares a reviewed update request/PR and reports **PENDING PROJECTION**; it must not claim the live Progress Page has been updated. Do not bypass repository checks by GitHub API editing data JSON. Every CLI write includes the existing Timeline record; there is no separate user-facing timeline workflow to impose.

## 8. Pilot sequence and test conditions

1. **Protocol review:** create a draft documentation PR in Common; confirm no private identifiers or live relay modifications.
2. **Activate only after Owner review:** create the dedicated GitHub receipt issue, insert its actual URL in a fresh `CURRENT.json` state proposal and merge using authorized project controls. Verify the first cold-chat URL opens that main-branch folder.
3. **One real bounded handoff:** coder receives "Cycle now", reads only its assignment, confirms candidate bytes (from private Drive if permitted), and posts a safe receipt; read back comment permalink.
4. **Oracle cycle:** invoke Oracle "Cycle now"; it reconciles exactly that receipt, advances canonical revision via reviewed PR, and uses the Progress CLI in an actual checkout to update the page; confirm the link and new audit event from real GitHub state.
5. **Reviewer cycle:** review new exact candidate and post scoped tests or NOT_RUN; Oracle preserves protected baseline and does not promote injected browser tests to Windows acceptance.
6. **Owner decision:** actual Windows acceptance remains explicitly Owner-controlled; P3 stays deferred without new authority.

### Falsifiers

- A cold agent given only "Cycle now" invents a folder or task → protocol FAIL; use URL form.
- A comment from the wrong chat/role or an obsolete revision advances state → FAIL.
- A GitHub PR is prepared but not merged and Progress Page says LIVE → FAIL.
- A code-only archive is merely mentioned in an issue and marked hash VERIFIED → FAIL.
- Two simultaneous receipts cause a lost update or silent reapproval → FAIL.
- A public issue reveals a private child Drive link or customer data → FAIL.
- No authorized CLI executor exists yet → status PENDING; don't fabricate progress.
- GitHub is inaccessible but a private receipt exists in Drive → record fallback with truthful bounds; don't claim GitHub posted.

## 9. Explicit non-goals in this first PR

No modification of the active `Common/relay` V3.1 custody model, private Drive permissions, code, P2.1 engineering backend, Progress Page live data, or user chat settings. No autonomous scheduling, automatic inter-chat messages, impersonation or unconditional acceptance. The design should remain easy to execute by an Owner sending **one line to one chat**.
