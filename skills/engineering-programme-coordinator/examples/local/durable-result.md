# Golden example — local coordinator → Work

```text
DURABLE_RESULT

WORKSTREAM
H / #234

OUTCOME
ACHIEVED

SUMMARY
Source-derived FBD waiting identities now match the canonical backlog contract; renderer status remains PROPOSED.

DURABLE EVIDENCE
- PR/head <ref>
- focused test <ref>
- canonical source <ref>

CONSUMER CONSEQUENCES
- #215 may consume the corrected backlog oracle on merge/current main.

INDEPENDENT REMAINING WORK
NONE in H.

OWNER DECISION REQUIRED
NO
```
