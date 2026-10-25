# Owner-facing routing board — source-bound, not a second tracker

Read alongside [the chat routing convention](../../oracle-chat-routing/STANDALONE.md)
and [Cycle protocol](../../../../oracle-cycles/PROTOCOL.md).
The Owner's compact board must be **derived** from current GitHub source
state and return evidence, not saved as another independently edited file.

## Read order and freshness

1. Read actual canonical project's `CURRENT.json` at `main` and
   record observed commit SHA and state revision.
2. If ACTIVE, locate actual configured GitHub receipt inbox and fetch
   unprocessed comments; distinguish accepted, untrusted and stale
   returns. Reading a comment is not accepting its claims.
3. When an action depends on a private ZIP, check actual access to
   the approved Drive location; never infer content identity from
   a folder listing or uploader hash.
4. Read actual Progress Page publication state if the Owner asks
   whether it is synchronized. An open PR or queued CLI command
   means PENDING, not SYNCED.
5. If the source can't be read, retain last known value with
   `LAST_CHECKED` timestamp and label `FRESHNESS_UNVERIFIED`.
   Never use stale data as if it were live.

Use **role + ID8 + current job + evidence state** together.
The ID is Owner-reported display routing, not an authenticated
session or actual full URL. State which observation is
Owner-reported versus byte-checked versus independently reviewed.

## One Owner action — transport and delivery strip

This is a **presentation derived from the current Oracle assignment/inbox**, not a new tracker or an automatic dispatch. Display it **alongside** [Universal Workflow Progress](../../../universal-workflow-progress/SKILL.md) when that read-only skill is selected; **Progress Page** is a distinct project viewer/projection. Do not recompute its milestones, percentages or stage completion.

**ORACLE → next role/chat ID8 → exact native evidence.** Show only **one NOW actor** and **one PASTE instruction** selected by the Oracle from the real transport:

- **ACTIVE standalone Cycle, first-time/cold chat:** `Cycle now: https://github.com/reallakshman19/Common/tree/main/oracle-cycles/<project>`.
- **ACTIVE standalone Cycle, verified previously bound chat:** `Cycle now`. The recipient performs [lightweight continuation](../../../../oracle-cycles/PROTOCOL.md#lightweight-continuation--already-bound-participants), not full onboarding by default.
- **Other native/OTM/inactive Cycle:** one task URL, bounded deliverable, governing native protocol, invariant, evidence return and material stop condition; **never** show an inactive/draft Cycle as executable.
- **Already SENT/OWNER-REPORTED SENT or RECEIVED:** show **No additional paste required** and the specific expected return; do not repeatedly ask the Owner to send a known instruction. `OWNER-REPORTED` is not `RECEIVED`; the Owner-reported short ID8 does not authenticate a chat.

`RETURN` points to **one native result/evidence permalink**, plus the [Common relay](../../ARTIFACT_RELAY.md) receipt when input/output artifacts move. `STOP IF` states one or two decisive source, authorization, access or engineering-HOLD blockers. Use delivery status `PREPARED`, `SENT/OWNER-REPORTED`, `RECEIVED`, or `RETURNED` **as observed**; do not infer byte verification or independent PASS from the status.

## Minimal default view

```text
AGENT ROUTING — <project> <ACTIVE|NOT ACTIVE|BLOCKED>
Checked: Common/main <commit7> | CURRENT rev <N>

Oracle   · chat <id8> · owns meaning        · <status>
Coder    · chat <id8> · owns artifact       · <status>
Reviewer · chat <id8> · tests exact claim   · <status>
Owner                 · actual acceptance  · <status>

NOW → <one role/id8, exact task ID and bounded deliverable, or activation blocker>
DELIVERY → <PREPARED | SENT/OWNER-REPORTED | RECEIVED | RETURNED; observation source>
PASTE → <one selected Cycle now or native-task instruction | No additional paste required>
RETURN → <native evidence permalink; plus Common relay receipt if files move>
STOP IF → <material mismatch or permission gap>
PAGE → SYNCED at <commit/revision> | PENDING | OUT_OF_SYNC | NOT_CREATED
```

If the current state is `PROPOSED_NOT_ACTIVE`, do **not**
display “NEXT coder, go execute now” merely because the record
contains a future `next.recipient_role`. Show activation
as the only immediate dependency. Only after activation with
a real configured issue inbox does the worker receive a live
one-line `Cycle now` dispatch.

If nothing is required from the Owner, write
“No further Owner attachment or message needed; next evidence
is due from <specific actor>.” Do not fabricate automatic
background work or count idle time as active execution.

## One-line prompts

Registered/correctly bound participant: `Cycle now`.

Cold participant:
`Cycle now: https://github.com/<owner>/<repo>/tree/main/oracle-cycles/<project>`.

A `Cycle now` message reaches **only the chat where the Owner
pastes it**; it doesn't broadcast or monitor another chat.
If the user pastes a worker report into Oracle's chat, record
`OWNER_REPORTED` unless a real issue/verified artifact
readback supports stronger wording.

## Claim state is multidimensional

- Delivery: PLANNED / OWNER_REPORTED / RECEIVED_CONFIRMED /
  BYTES_VERIFIED.
- Work: NOT_STARTED / IN_PROGRESS / SELF_TESTED /
  WORK_RETURNED / BLOCKED.
- Assessment: INDEPENDENTLY_REVIEWED with exact claim
  PASS/FAIL/PARTIAL/NOT_RUN/UNKNOWN.
- Acceptance: OWNER_ACCEPTED with exact scope and actual
  Owner decision source.
- Publication: PROPOSED / MERGED_GITHUB / PUBLISHED_PAGE_VERIFIED.
- Changeover: RECOMMENDED / PREPARED / ACTIVATED /
  CUTOVER_ENFORCEMENT_UNKNOWN.

Never flatten these into one green completion icon or claim
a code-only ZIP passes because the runnable UI passed.
A reviewer-reported test of injected Chromium does not
close native Windows acceptance. A result from the old
candidate is historical if its affected bytes changed.

## Visual style

Use a compact stack of roles with IDs and neutral readable
statuses; one prominent next action. Don't add a long
wizard, decorative controls that do not send, or a table of
all prior handoffs. Render a copyable one-liner only when
there is an active recipient. Put hard evidence limits in
a small, visible footer.

Read-only refresh may update this **chat's** board after
a new user request. It cannot cause other chats to run.
