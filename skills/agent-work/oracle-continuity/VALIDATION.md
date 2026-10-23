# Validation record

Date: 23 October 2026. Checks were executed locally by the package author.
This is self-validation of the reference implementation, not independent review
or qualification of any live project, approval, transport or learning outcome.

Environment: Python 3.12.14; jsonschema 4.26.0; Windows.

```text
python -B -m unittest discover -s oracle-continuity-protocol-v1/tests -q
Ran 49 tests
OK
```

The suite validates both schemas, all five example states and all three example
state-publication commands. It verifies the included report's actual SHA-256.
Negative cases cover:

- Unknown fields/versions, malformed records, duplicate IDs/JSON keys, non-finite
  JSON numbers, invalid timestamps, blank aims and ungrounded source references.
- Missing references, dependency/lineage cycles, overlapping declared writers,
  unconfirmed delivery/capabilities and obsolete assignment revisions.
- Direct and inherited author-review conflicts, stale candidate reviews,
  reported-only PASS, NOT_RUN, absent witnesses and omitted observed failures.
- Explicit measurement corrections retaining original evidence, user-use evidence
  distinct from checks, an unobserved learning criterion and scoped acceptance.
- Rewritten immutable records, unversioned task changes and missing change decisions.
- Prepared/uncertain versus activated successors, old active assignments, same-chat
  reissues, new Oracle adoption, competing active Oracles and epoch jumps.
- Late returns, revision conflicts, command replays/stale epochs, changed command
  payload bytes, changed artifact bytes and local path escapes.

One test deliberately supplies an unverified private witness reference and still
passes structure/relationship validation. This documents the boundary: the checker
does not authenticate the declared observation or authority.

CLI smoke checks also passed for initial state, worker cutover with its command,
Oracle cutover with its command, and completed state with its command and local
artifact-byte verification.

Not exercised: actual concurrent publication/CAS, tool-mediated chat delivery,
credential/identity separation, remote witness retrieval, live agent cessation,
domain-specific scoring, real user acceptance or actual learner use. No adapter
implementing those actions is included. A live pilot must provide those observations
before claiming operational continuity or unattended reliability.

## Common integration checks

After integration into `skills/agent-work/oracle-continuity`, all 49 tests passed
again locally. The three changed skill entry points passed the skill-creator
format validator; seven new relative links resolved; the focused CI workflow
parsed and uses read-only repository permissions. The CI matrix targets Python
3.10 and 3.12; local execution here used 3.12 only.

A fresh agent received a synthetic continuation request, source CSV and initial
state, with permission limited to local preparation. It observed the CSV quantities
12 and 30, returned a next-work brief and revision-2 proposal, and successfully
validated that proposal against its predecessor. Task/revision and Oracle epoch
remained stable; the successor was queued/prepared, its handover unactivated, and
old execution remained uncertain. No actual dispatch, cutover or converter build
was performed. This demonstrates one local application, not general reasoning
qualification, authenticated independence or live continuity.

The application exposed ambiguity about locally prepared versus published state.
Protocol section 8 and the README now make the trusted canonical reference/receipt
boundary explicit. Optional native slice/map assets were absent from the scoped
local source subset; the agent used a native Markdown brief and recorded that limit.
Those existing assets remain in Common; this change does not replace their schemas.
