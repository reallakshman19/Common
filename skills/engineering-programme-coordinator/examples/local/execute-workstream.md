# Golden example — Work → local coordinator

```text
EXECUTE_WORKSTREAM

WORKSTREAM
H / #234

OUTCOME
Produce the source-derived waiting FBD identity/bucket set without implementing a renderer.

PRODUCTION BOUNDARY
OWNS:
- source-derived backlog oracle/test correction
EXCLUDES:
- renderer implementation
- canonical representation invention

CURRENT DURABLE INPUTS
- parent #210 / PB-0004
- child #234
- plan rev 1
- exact main <sha>

DEPENDENCIES
NONE

FALSIFIER
If canonical records do not imply the observed waiting identities/buckets, do not patch the expectation to match a count.

SUCCESS ORACLE
Exact source-derived identity set matches the backlog result and PROPOSED renderer state remains honest.

EXPECTED NEXT OBSERVABLE
Focused source-derived backlog evidence or a contradictory canonical-source finding.

CONSUMERS
#215/P5

SEMANTIC ESCALATION
Only if source authority, ownership or programme meaning changes.

OWNER DECISIONS ALREADY MADE
Do not implement the renderer in this workstream.
```
