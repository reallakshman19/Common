# Golden example — [Relay Handover] multi-agent ledger

```text
PROGRAMME
#210 / PB-0004

WORKSTREAM F — #232
plan: rev 1 / PRESENT
child acceptance: SATISFIED
PR #235: MERGED @ <sha>
expected: consumer #215 consumes result
next consequence: route F output to E

WORKSTREAM G — #233
plan: rev 2 / PRESENT
child acceptance: PARTIAL
PR: none
expected: canonical owner-extension identity audit
dependency: none
next consequence: update P5 input when durable

WORKSTREAM H — #234
plan: rev 1 / PRESENT
child acceptance: PARTIAL
expected: source-derived FBD waiting identity set
dependency: none

WORKSTREAM E — #215
plan: rev 1 / PRESENT
PR #237: REVIEW_READY / UNMERGED
child acceptance: 5/6
programme contribution: 4/5
expected: exact-main P1–P5 rerun after G/H producer outputs

DEPENDENCIES
G output → E/P5
H output → E/P5

NONTERMINAL PRS
#237 — E — REVIEW_READY — <head>

NEGATIVE KNOWLEDGE
Do not treat fixture completeness as canonical academic coverage.

OWNER DECISIONS NEEDED
NONE

NEXT COORDINATOR ACTION
Observe G/H producer outputs; route them to E when durable.
```

This ledger is an index, not proof or permission.
