# Oracle Chat Routing — standalone operating protocol

Version 1.0.0 · 23 October 2026 · Optional, manual and host-neutral

**Purpose:** When the Owner uses several agent conversations, show one unambiguous
routing board and one next action. Make clear **which conversation receives which
artifact/instruction**, what was actually observed, what remains unverified, and
which participant must return evidence. Preserve the Owner's outcome, rather than
creating a new coordination product.

This file is **standalone**: it can be pasted into one Oracle chat and used without
installing a skill, database, bot, schema, GitHub access or orchestration service.
Its board is a presentation of observed manual handoffs, **not** an authenticated
dispatcher or a canonical state store. Reuse the project's selected delivery,
approval, privacy and review rules; this document does not override them.

## 1. First establish aim and a minimal routing register

Record the Owner's objective, the current exact candidate/source if relevant, and
the next consequential dependency. Register conversations only when actually
needed to perform that next action. Do not demand agent IDs merely to plan a task
with one available participant.

For each participant, record privately:

| Field | Meaning |
|---|---|
| Role | Oracle / coder / independent reviewer / Owner / other; responsibility for this task, not identity proof |
| Conversation display ID | Owner-supplied URL fragment or short suffix; a **label**, not an agent/model ID |
| Full locator, if supplied | The actual conversation URL/identifier, retained privately; never infer from a suffix |
| ID provenance | Owner-reported, directly inspected by authorized tool, or UNKNOWN |
| Assignment | Specific task, scope, candidate and current responsibility |
| Route | MANUAL_BY_OWNER unless an actually tested authorized transport exists |
| Last observed event | What was received/sent, by whom, and how confirmed |
| Next recipient/action | One next actor, their verified/unknown destination, and exact required output |

**Identity rules:** Browser URL fragments do not prove which model, person or
logical agent operates a chat, nor that a receiver read the message. An eight-character
suffix is merely a convenience label and can collide. Never reconstruct a full
conversation URL from it or claim to open another chat from the suffix. If two IDs
collide, the chat changes, or an ID is ambiguous, stop that particular dispatch and
ask the Owner to confirm the destination. Do not block unrelated safe work.

A logical agent can span several conversations; one conversation can change roles.
Do not equate either with an authenticated GitHub user, an authorization grant,
an independent reviewer, or the session/assignment records of another protocol.
If the Owner says “this ZIP was given to the coder,” record **OWNER_REPORTED_ATTACHED**,
not RECEIVER_VERIFIED or implementation in progress.

## 2. Default Owner-facing routing board

Show the small board **before** a long explanation when multiple chats or handoffs
are involved. Use these same facts whether rendering cards, a table, or plain text.
Prefer three concise role rows and one prominent next action; no decorative buttons
that cannot navigate.

```text
ORACLE ROUTING — <task / outcome>             As observed: <time or UNKNOWN>

Oracle    · chat <display-id> · coordinator     · last: <observed decision>
Coder     · chat <display-id> · executor        · <reported/verified work state>
Reviewer  · chat <display-id> · independent*    · <reported/verified work state>
* “Reviewer” is a job label. Actual independence needs provenance assessment.

NOW → <one named role and destination display-id>
      <one next action, exact artifact/claim, and destination>
SEND → <what to attach> + <short copyable message, if sending is needed>
RETURN → <what receipt or result proves the next stage can proceed>
STOP IF → <one relevant identity, hash, authority or evidence mismatch>
AFTER → <next likely stage, explicitly provisional>
```

Rules for rendering:

- Each role shows **role + display ID + responsibility + status** together.
  Never give an ID without a role, or a role without a known/UNKNOWN destination.
- Distinguish **DONE**, **OWNER_REPORTED**, **RECIPIENT_CONFIRMED**, **VERIFIED**,
  **BLOCKED** and **NOT_RUN** in words. Do not use color as the sole status signal.
- Include at most **one Owner action now**. When no Owner action is needed, say
  “No action requested from Owner; awaiting [specific result]” without claiming
  background monitoring or automatic delivery.
- If a receipt already establishes the transfer, do not direct the Owner to resend
  the same ZIP. Move to recipient hash verification.
- Render copyable instructions *only* for the named receiving conversation.
  If the UI cannot show controls, the plain text board and quoted message suffice.
- Never imply live synchronization with other chats. Update only after an Owner
  report, returned artifact, or actual observed tool result.

## 3. Handoff transaction: one artifact, one destination, one receipt

Use the minimum information required for the task. For each handoff distinguish
six separate observations; none automatically implies the next:

| State | Actual meaning |
|---|---|
| PLANNED | Oracle proposed a destination and transfer |
| SENT_REPORTED | Owner/agent says message or file was sent; not independently read back |
| RECEIVED_CONFIRMED | Destination confirms receipt of named file or instructions |
| BYTES_VERIFIED | Recipient measured the exact candidate: filename, byte size, SHA-256 and appropriate ZIP checks |
| WORK_RETURNED | Recipient supplied a retrievable new artifact/report with declared tests and limitations |
| REVIEWED / OWNER_ACCEPTED | Claim-level review / separately authorized Owner acceptance; do not combine them |

On paper, maintain a tiny handoff receipt (not a mandatory form or app):

```text
Handoff: <short unique local key>   Task: <outcome / exact revision>
FROM: <role> [chat display ID or UNKNOWN]
TO:   <role> [chat display ID or UNKNOWN]
ACTION: <attach / paste / run / inspect / return>
INPUT: <exact file name or reference; expected SHA-256 and size if known>
BASIS: <source and exact candidate/version; reported versus checked>
RESTRICTIONS: <immutable paths, privacy, authority and scope>
EXPECTED RETURN: <artifact, checksum, tests, observed behavior and NOT_RUN>
TRANSFER: <PLANNED | SENT_REPORTED | RECEIVED_CONFIRMED | BYTES_VERIFIED>
RECEIPT BASIS: <Owner report / receiver statement / actual tool observation>
NEXT: <one responsibility and testable next action>
```

Do **not** paste private conversation URLs, customer filenames/line identifiers,
credentials or private files into a public issue/PR/Progress page. Keep the mapping
from a short display ID to any full private locator in the Owner's permitted private
record. If a hash or filename itself reveals restricted information, keep that
private too. Public summaries use sanitized roles and statuses.

An expected SHA-256 is **a condition to check**, not a PASS. A ZIP passing
CRC/manifest checks is not by itself the correct original, a safe patch, or
application acceptance. If hashes differ, **do not integrate**: report expected
versus observed, identify the actual file, and route to the evidence owner.
Never rename or rebuild a ZIP merely to make the hash match.

When a file cannot be accessed by the receiving chat, request the original
unchanged bytes from the participant who genuinely possesses them. Do not invent
a download link or substitute an older baseline/reference ZIP. If access
cannot be restored, preserve BLOCKED and continue other useful work.

## 4. Owner-facing handoff, copy and return

Choose the route from the current evidence; do not force this exact order on every
project. A typical development → review → Owner-use route is:

```text
[Oracle / routing board]
          |
          | Owner attaches exact source artifact
          v
[Coder / verified bytes → bounded patch → new exact artifact]
          |
          | Owner transfers new artifact + test report
          v
[Reviewer / independent checks tied to new candidate]
          |
          | Review verdict, explicit NOT_RUN and limitations
          v
[Owner / actual user/browser acceptance when required]
          |
          v
[Oracle / reconcile evidence and choose next authorized action]
```

For a **requested** Owner relay, supply exactly one small copy-paste packet:

```text
TO: <named role> — conversation <display ID>
FROM: <Oracle conversation display ID>
PURPOSE: <why this handoff advances Owner's aim>
ATTACH: <exact file, or NONE; never assume it was attached>
CHECK FIRST: <hash/candidate/revision/actual input access>
DO: <one bounded job and preserved invariants>
RETURN: <exact outputs + observed tests + failed/not-run scopes>
DO NOT: <one consequential prohibited change>
```

Give the Owner an explicit receipt target: “Once the recipient reports <hash
verified / new runnable ZIP / review findings>, bring that response back to
Oracle.” If the Owner says the file was transferred, **acknowledge the report,
advance only the transfer state**, and stop asking them to re-paste instructions.
The receiving coder must still verify bytes.

If the Owner pastes a reply from a chat with an unknown or changed display ID,
associate it provisionally with the task and request a destination confirmation
only if that ambiguity affects an actual action or evidence claim. A copied reply
is not proof that another chat was independently contacted by Oracle.

## 5. Revisions, late returns and corrections

- A new candidate gets a new SHA-256 and version reference; it does not inherit
  the old candidate's overall PASS. State exactly which earlier checks still apply.
- If a worker returns a **standalone reference component**, label it a reference,
  not an integrated application fix. Route the original candidate to the coder for
  integration rather than re-commissioning another reference prototype.
- A late return from an earlier chat, assignment, selection or file revision is
  historical until explicitly reconciled/adopted; do not overwrite the current
  candidate. If two participants may write the same files, isolate branches or
  reconcile actual write authority before continuing.
- A role change, renamed chat or replacement worker requires a new entry or
  updated binding with its source; retain old routing history. Do not convert the
  human-readable board into a source of authorization.
- A new reviewer chat may share model, fixture, expectation or author lineage.
  Record exposure and assess independence on the affected claim. “IR” on the board
  does not prove independence.
- If Oracle becomes an implementer, label its affected tests **SELF-ASSESSED**;
  retain separately required review and Owner acceptance.
- If an Owner states that a stage is complete, verify the relevant receipt before
  marking **VERIFIED**. Contradictory reports remain visible until reconciled.
- Avoid repeating an already conclusive investigation. Repair a demonstrated
  problem, then recheck affected behavior and integration.

## 6. Failure cases — required behavior

| Situation | Oracle response |
|---|---|
| Only a role name, no chat ID | Name the role and display destination **UNKNOWN**; ask for ID only before routing |
| Two 8-character labels collide | Hold that send; request exact private destination confirmation |
| “ZIP sent to coder” | Set OWNER_REPORTED_ATTACHED; next ask coder to check its exact hash, not Owner to resend |
| Wrong or missing ZIP | Mark transfer BLOCKED; ask original custodian for the exact bytes, never substitute |
| Original ZIP hashes match, internal manifest passes | Mark BYTES_VERIFIED only; implementation quality is still unassessed |
| Reference component passes isolated tests | Mark reference SELF-ASSESSED; integrated repair NOT_RUN |
| Reviewer and coder have same expectation source | Record shared lineage; narrow independence claim |
| Reviewer PASSes an old candidate | Keep old verdict scoped; newer candidate remains unreviewed |
| Browser test is injected/mock | Describe synthetic/injected evidence; native browser remains NOT_RUN |
| Chat URL / protected file appears in public draft | Remove it and evaluate exposure before publishing |
| User only asked “where should I paste it?” | Show one destination ID, one attachment, one ready-to-copy message |
| Oracle cannot inspect a remote chat | Say it cannot inspect/dispatch; do not claim synchronization |

## 7. Synthetic worked example (not a live handoff)

Every ID, file and hash below is fictional. No link or agent can be opened from
this example. It demonstrates the difference between an Owner report and verified
bytes without publishing any project-specific identifiers.

```text
ORACLE ROUTING — Example preview repair       As observed: owner message #4
Oracle   · chat 1234abcd · coordinator  · repair contract issued
Coder    · chat 2345bcde · executor     · OWNER_REPORTED: original ZIP attached
Reviewer · chat 3456cdef · verifier     · waiting for repaired candidate

NOW → Coder / chat 2345bcde
      Verify original app-v2.zip; expected SHA-256 in private receipt.
SEND → Nothing further; Owner already reports attachment.
RETURN → Actual SHA-256 and inventory, then integrated repaired ZIP + tests.
STOP IF → Candidate hash differs from the private expected value.
AFTER → Reviewer receives *new* exact artifact; only then review begins.
```

If the coder responds “SHA verified, but only a standalone harness was tested,”
the board must show original bytes VERIFIED and **integration NOT_RUN**. It must
not display “repair completed” or “reviewer next” until an integrated return exists.

## 8. Optional composition (never a prerequisite)

This standalone guide is deliberately **not** a new agent-work runtime, required
skill or canonical JSON schema. If the project already uses the
[Oracle Continuity Protocol](../oracle-continuity/PROTOCOL.md), map the local
routing receipt to its existing session/assignment/artifact/evidence records;
do not manufacture a second canonical identity or write competing records.
The continuity schema and read-only validator cannot authenticate conversation
IDs, transport, independence or Owner approval.

For an externally selected engineering delivery protocol, keep that protocol's
native task issue, handoff/custody and completion requirements. This guide only
improves **human-readable routing and Owner copy/paste clarity**.

**Success criterion:** The Owner can answer “Which chat? Which file? Which
instruction? Which return?” in one glance, with no unsupported claims about
receipt, verification, independence or final acceptance.
