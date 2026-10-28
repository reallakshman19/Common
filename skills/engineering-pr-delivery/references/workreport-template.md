# PR<NUMBER> / WIP-<ID> — <Mission> Work Report

# CURRENT RECOVERY STATE — READ FIRST

## 1. Recovery Header

```text
HANDOVER_READINESS:
PR_RECOVERY_STATE:
TAKEOVER_AUTHORITY:

EXECUTION_MODE: MANUAL | AUTO
AUTO_STATE: NOT_ACTIVE | RUNNING | VALIDATING | RECOVERING | BLOCKED | OWNER_DECISION_REQUIRED | TAKEOVER_REQUIRED | COMPLETE
SCOPE_AUTHORITY: LOCKED_TO_APPROVED_MISSION | OWNER_EXPANDED
PHASE_PROGRESSION: MANUAL | AUTO
MERGE_AUTHORITY: OWNER_ONLY | AUTO_AFTER_EXPLICIT_AUTHORIZATION
AUTO_STOP_REASON:

REPOSITORY:
SOURCE_TASK:
PR_OR_WIP:
BRANCH:

PR_HEAD_OBSERVED:
REPORT_BASIS_HEAD:
MAIN_HEAD_LAST_CHECKED:
MERGE_BASE:
REPORT_SYNC:

APPENDIX_A_STATUS:
GROUNDING_EPOCH:
CURRENT_TAKEOVER:

CURRENT_STAGE:
LAST_COMPLETED_STAGE:
CURRENT_BLOCKER:
HIGHEST_RISK:
LAST_DURABLE_CHECKPOINT:

EXACT_NEXT_ACTION:
```

When `EXECUTION_MODE=AUTO`, also record the current approved plan boundary and any hard-stop condition using `references/auto-mode.md`.

## 2. Handover in 60 Seconds

### What is now true
### What is currently being worked on
### What remains unfinished
### What has been proven
### What has NOT been proven / NOT_RUN
### What must not be assumed
### Highest-risk remaining item
### Exact next action

## 3. Repository Ground Truth

Record live PR/main state, current changed-file count, reviews, checks, mergeability, dependencies, claims, and grounding timestamp.

## 4. Mission / Scope / Acceptance

- mission;
- engineering/user consequence;
- approved scope;
- explicit non-goals;
- acceptance criteria;
- owner instructions;
- critical constraints.

For AUTO MODE also record the approved phase plan and the explicit boundary beyond which owner authorization is required.

## 5. Current Implementation State

| Work item | Implementation | Integration | Validation | Location | Remaining |
|---|---|---|---|---|---|

Use explicit states rather than one generic DONE.

## 6. Active Engineering Item Register

| ID | Type | Severity | Priority | Status | Summary | Evidence | Current PR? |
|---|---|---|---|---|---|---|---|

IDs: `ISS-*`, `IMP-*`, `RISK-*`, `DEC-*`, `QST-*`, `DEBT-*`.

## 7. Current Technical Diagnosis

```text
Observed symptom:
Current hypothesis:
Supporting evidence:
Alternative hypotheses:
Already ruled out:
Falsifier:
Next isolating experiment:
```

## 8. Authority and Invariants

Record engineering/software source-of-truth boundaries, governing references, units/sign conventions where relevant, and invariants that must remain unchanged.

## 9. Current Validation

For each material validation record:

```text
ID:
Status: PASS | FAIL | NOT_RUN | NOT_APPLICABLE
Observation: LOCAL_EXECUTION | REMOTE_EXECUTION | SOURCE_INSPECTION | ARTIFACT_INSPECTION | USER_SUPPLIED | INFERRED | NOT_OBSERVED
Oracle: NONE | IMPLEMENTATION_COUPLED | INDEPENDENT_REPRODUCTION | ANALYTICAL | AUTHORITATIVE_REFERENCE | CROSS_SOLVER | EXPERIMENTAL
Tested HEAD:
Command/evidence:
Expected:
Actual:
Limitations:
Origin: PREEXISTING | INTRODUCED_BY_PR | RESOLVED_BY_PR | UNKNOWN_ORIGIN
```

## 10. Changed-File Ledger

| File | Intended? | First stage | Latest stage | Purpose | Sensitive? | Validation |
|---|---:|---|---|---|---:|---|

Record actual GitHub file count, ledger count, unexplained files, and reconciliation HEAD.

## 11. Review / CI State

Open/closed review threads, requested changes, owner decisions required, checks/workflows, and exact applicability to current HEAD.

## 12. Repository Coordination / Overlap

```text
MASTER_INDEX_CHECKED:
STATUS_RECORD:
CLAIM_RECORD:
LAST_OVERLAP_CHECK:
FILE_OVERLAP:
AUTHORITY_OVERLAP:
DEPENDENCY_OVERLAP:
COORDINATION_STATE:
```

## 13. Continuation State

```text
Start here:
Exact file/function/component:
Current value/path under investigation:
Do not redo:
Do not change:
Validation still required:
Highest-risk remaining item:
Exact next action:
```

If AUTO MODE is active, state whether the next action is inside the approved plan and whether any hard-stop condition exists. If none exists, the next agent should continue automatically after qualifying/re-grounding as required.

## 14. Takeover / Custody Chain

Append-only `TKO-*` events and `GE-*` grounding epochs. Record inherited-and-revalidated, inherited-not-revalidated, superseded, contradicted, and newly-observed facts.

# APPENDIX A — IMPLEMENTATION TAKEOVER QUALIFICATION

Qualification basis:

```text
PR_HEAD:
MAIN_HEAD:
GROUNDING_EPOCH:
Generated from OPEN ISS/RISK/QST:
PARTIAL implementation:
NOT_RUN validation:
Next intended stage:
APPENDIX_A_STATUS:
```

Create repository-specific A1–A5 challenges using `references/takeover-qualification.md`.

# HISTORICAL RECORD — NOT CURRENT AUTHORITY

## Stage Execution Log
## AUTO MODE Phase History
## Closed Findings
## Prior Validation
## Decision / Invariant History
## Recovery / Salvage Decisions
## Prior Takeovers
## Lessons Learned
