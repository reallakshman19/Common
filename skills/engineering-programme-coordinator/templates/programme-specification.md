# Programme Specification + Coordination Record

Use the parent GitHub issue as the durable programme specification. Preserve the original contract in the issue body and use Owner-authorized amendments/comments for semantic changes over time.

```text
ISSUE_ROLE: PROGRAM_ROOT
PROGRAM_ID: PGM-<repo>-<short-name>
PROGRAMME_BASIS_REVISION: PB-0001
RELAY_PROTOCOL: V3.1_ONLY
ORIGINAL_INTENT_ISSUE: PENDING | github:<owner>/<repo>#<intent>
ORIGINAL_INTENT_DIGEST: PENDING | sha256:<digest>
RELAY_HANDOVER_ISSUE: PENDING | github:<owner>/<repo>#<handover>
```

## 1. Original Intent source

When direct Owner source exists, link the `[Original Intent]` child containing the verbatim historical instruction and supplied inputs/ideas/expected outputs.

Do not rewrite that historical source when current programme meaning changes. Current meaning is expressed by this programme specification plus explicit Owner/programme amendments.

## 2. Owner outcome

What human/product/programme result must ultimately become true?

## 3. Why now / governing witnesses

What concrete need, failure, contradiction, evidence or strategic decision caused this programme to exist?

## 4. Non-goals

What must this programme not absorb?

## 5. Current effective programme basis

```text
CURRENT_BASIS_REVISION: PB-0001
OBSERVED_MAIN: <exact SHA>
```

### Effective amendment index

| Amendment | Kind | Durable ref | Summary | Supersedes |
| --- | --- | --- | --- | --- |
| OA-001 | OWNER_DECISION | <comment/link> | ... | NONE |

Only explicitly identified Owner/programme amendments modify the governing semantic basis. Ordinary discussion does not.

## 6. Canonical input/source registry

| ID | Ref/source | Meaning | Authority | Kind | Invalidation rule |
| --- | --- | --- | --- | --- | --- |
| INPUT-001 | ... | ... | ... | PRODUCTION / AUTHORED / GENERATED / FIXTURE / EXTERNAL / OWNER_SUPPLIED | ... |

Make authored/generated and production/fixture distinctions explicit.

## 7. Programme invariants / preserve

- ...

## 8. Workstream registry

| Workstream | Child issue | Outcome | Owns | Excludes | Consumers | Plan ref/revision |
| --- | --- | --- | --- | --- | --- | --- |
| A | #... | ... | ... | ... | B,C | missing / comment / revision |

A missing implementation plan reduces reconstruction confidence only. It is not permission to stop engineering.

## 9. Producer / consumer contracts

For every meaningful output:

### OUT-001 — <production output>

**Producer:** <workstream>

**Consumers:** <workstreams>

**Meaning / contract:**

- ...

**Consumers must not infer:**

- ...

## 10. Dependency contracts

Never write only "C depends on B".

### DEP-001 — <required production output>

**Producer:** <workstream / unknown>

**Consumer:** <workstream>

**Why required:** ...

**Satisfaction evidence:**

- ...

**Work that may continue independently:**

- ...

A dependency is missing production truth, not an execution lock.

## 11. Programme success / exit criteria

| ID | Requirement | Responsible workstreams | Evidence sources | Status |
| --- | --- | --- | --- | --- |
| EXIT-001 | ... | A,C | PR/test/artifact refs | OPEN / PARTIAL / SATISFIED / DEFERRED / NOT_APPLICABLE |

Child completion does not imply programme completion unless its mapped programme obligation is actually satisfied.

## 12. Reconstruction topology

For zero-context takeover, preserve refs in this order:

```text
Original Intent
→ current Owner/Roadmap amendments
→ EP / child responsibility
→ primary-agent reconciliation
→ Local Agent / OFFLOAD evidence
→ RLL transport refs
→ material truth
→ Task Snapshot / Relay Handover
```

Do not copy transcript bodies into the programme issue or Handover.

## 13. Decision surface

### Engineers decide

Implementation choices inside their owned responsibility.

### Coordinator decides

Cross-agent routing, useful parallelism, re-observation, local-helper recommendation, consequence propagation and concise programme reporting.

### Owner decides

Only genuine human/product/programme choices.

## 14. Durable amendment / chronology format

Owner-authorized or programme-significant comments should use one of:

```text
OWNER_AMENDMENT
OWNER_DECISION
RESPONSIBILITY_TRANSFER
PROGRAMME_DISCOVERY
EVIDENCE_RECORD
```

and contain:

```text
BASIS
what was previously true

CHANGE
what changed

WHY
decision/evidence

AFFECTS
affected workstreams/contracts

DOES NOT AFFECT
what remains stable

SUPERSEDES
earlier amendment if applicable
```

When an amendment changes the current programme meaning, update the Effective amendment index rather than rewriting history.

## 15. Dedicated operational ledger

Create one child issue titled:

```text
[Relay Handover] <programme title>
```

It is the durable current operational index for the programme.

It does not grant engineering authority and is not required to be fresh for production work to remain valid.

See `engineering-programme-coordinator/templates/relay-handover.md`.

## 16. Relay V3.1

Use **Engineering Relay V3.1 only** for recording/reconstruction/reporting when Relay context is useful.

Do not use V3 or V2.5 for live coordination, execution, status, recovery, handover, gating or Owner-command semantics.

V3.1 records reality. It does not invent programme authority or engineering gates.
