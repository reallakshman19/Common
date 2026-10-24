# Oracle Cycle — Standalone

**Start:** [PROTOCOL.md](PROTOCOL.md) · **Pilot workspace:** [P2.5-B](p25b/README.md)

A standalone, GitHub-first handoff convention for one Owner, an Oracle and
temporary coder/reviewer chats. **Not OTM**. The Owner talks naturally to
Oracle and sends a **one-line trigger** to whichever chat Oracle identifies.
That agent checks the fresh project folder, reads the bounded task, works
only within existing authority and posts its own traceable GitHub issue
receipt. Private engineering ZIPs live in an authorized Google Drive
handoff folder rather than in the public repository.

### Say only this

- Existing registered chat: **`Cycle now`**
- New / context-free chat: **`Cycle now: https://github.com/reallakshman19/Common/tree/main/oracle-cycles/p25b`**

The URL form is required when the recipient doesn't know the project
folder and role. The instruction triggers work **only in the chat that
receives it**; no cross-chat notification, background worker or automatic
state update is implied.

### Project folder contents

The project-specific `CURRENT.json` is the sole effective snapshot **only
after publication to the authorized main branch**. The `README.md` is
a stable locator; `PLAN.md` records the Owner's design decision,
preconditions and pilot tests. Coder/reviewer return messages are GitHub
issue comments, not arbitrary edits to current state. Oracle selects and
proposes the next revision, and separately updates Progress via its
native CLI when actually executable.

### Status of this first contribution

The first P2.5-B workspace is a **PROPOSAL ONLY** in a draft PR.
No receipt issue has been activated, no Google Drive permissions have
been changed, and no Progress Page data has been updated. Until
activation, a participant who reads it must reply **NOT ACTIVE**
rather than undertaking a fresh task on its authority.

See [P2.5-B PLAN.md](p25b/PLAN.md) for the handoff layout and tests.
