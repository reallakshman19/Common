# Oracle Cycle / P2.5-B — standalone workspace

**Canonical activation and assignment:** [CURRENT.json](CURRENT.json) on **`main`**.

- [Historical plan and pilot boundaries](PLAN.md)
- [Read current structured state](CURRENT.json)
- [Shared Cycle now protocol](../PROTOCOL.md)
- [Append-only receipt issue #465](https://github.com/reallakshman19/Common/issues/465)

## First rule — read canonical state, not this README's age

A protocol merge or issue creation alone does not authorize work.
Before each operation, fetch `CURRENT.json` from actual
`Common/main`, inspect its revision, `activation`, assigned
role/chat suffix, scope and `receipt_issue_url`, and follow
[the protocol](../PROTOCOL.md). A branch/draft PR may contain
a proposed ACTIVE revision that is not yet published.

**If canonical `activation != ACTIVE` or issue binding is absent:**
return **NOT ACTIVE** and do not claim that any assignment
was dispatched. If an active assignment exists but the
recipient role doesn't match, return **NO ACTION**.

## One-line Owner command for coder / IR / new agent

```text
Cycle now: https://github.com/reallakshman19/Common/tree/main/oracle-cycles/p25b
```

A participant already registered with verified project/role
context can subsequently receive just `Cycle now`.
A prompt only reaches the chat where it is typed. It never
broadcasts or runs in the background. Eight-character
conversation labels are not authenticated identities.

## What an assigned agent returns

Use the designated real private handoff location for any
restricted ZIP and compute size/hash on actual downloaded
bytes. A reported hash is not a verified readback.

Post one public-safe `ORACLE-CYCLE-RECEIPT v1` comment
to the issue URL named in canonical `CURRENT.json`.
Bind it to exact `assignment_id`, `observed_revision`,
candidate and test limits; fetch the permalink afterward.
Do not put protected engineering files, customer identifiers,
private child Drive URLs, full chat URLs or approval keys
in public GitHub issues or PRs.

An issue comment is a proposed receipt only. Oracle
reconciles it into a reviewed next revision; Progress
updates through its official standalone CLI and Owner merge.

## Oracle / Owner

Oracle displays a compact role+ID routing board and one
next action, distinguishes self-tests from independent
review and preserves genuine Windows Owner acceptance.
The first live pilot tests one unchanged code-only
handoff—not additional P2.1 engineering development
or P3. The separate active V3.1 `Common/relay/**`
execution ledger is untouched.
