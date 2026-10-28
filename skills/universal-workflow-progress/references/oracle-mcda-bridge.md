# Oracle + Software MCDA + Universal Workflow Progress bridge

**Mode:** read-only presentation/advisory routing. **Version:** 1.1.
The user's selected workflow contract, not this bridge, determines stages,
dependencies, tests, Owner authority and milestone acceptance.

## Explicit responsibilities

- **Oracle:** understands purpose, constructs competing explanations and
  claim-specific falsifiers, reconciles independent returns and chooses the
  next proposed task. Its contributor work cannot self-qualify.
- **Universal Workflow Progress:** presents source-grounded stage identities,
  statuses, parallel lanes, current blocker and one next observable. It neither
  performs engineering nor certifies claims.
- **Software MCDA:** independently assesses genuinely competing approaches
  using weights, anchored criteria, mandatory constraints and sensitivity.
  Workflow stages are not MCDA options; status never becomes a score.
- **Workflow Intelligence:** optional one-time read-only observation requiring
  an enabled, reviewed source mapping. Comment markers are SUBMITTED/UNVERIFIED,
  not independent technical acceptance.

## Invocation decision table

| Owner intent | Route | Evidence mode |
| --- | --- | --- |
| Show my workflow/status | Universal Workflow Progress | Supplied/cached: NOT LIVE; requested fresh read: ON only after mapping check |
| Compare approaches | Software MCDA | OFF by default; advisory without GitHub |
| Compare approaches and show progress | UWP strip first, MCDA advisory second | OFF unless explicitly ON |
| Check GitHub now | UWP one-time read | Verified source mapping; timestamp evidence |
| Start/dispatch/merge/approve | Governing executor/Owner | NEVER through this observer |
| Ambiguous "invoke" | Clarify progress vs execution | No implied launch |

Routing diagnostics (do not execute tasks):

```sh
python skills/universal-workflow-progress/scripts/route_invocation.py --intent mcda --consumer oracle
python skills/universal-workflow-progress/scripts/route_invocation.py --intent combined --consumer oracle --workflow governed-id --monitor OFF
python skills/universal-workflow-progress/scripts/route_invocation.py --intent combined --consumer oracle --workflow governed-id --monitor ON
python skills/universal-workflow-progress/scripts/route_invocation.py --intent start --consumer oracle --workflow governed-id
```

All responses include `source_checked=false`, `agent_invoked=false`,
`workflow_executed=false`, `repository_mutated=false` and
`approval_granted=false`. ON is a *request* for a separately verified
one-time source read, not proof that one happened; absent mapping yields
MONITORING UNAVAILABLE without blocking MCDA. A route does not install a
skill in another Oracle chat or start background polling.

## Compact Oracle progress display

1. **WORKFLOW PROGRESS — <selected workflow>** with observed-as-of timestamp
   from the performed read or explicit NOT LIVE / OBSERVATION UNAVAILABLE.
2. One **horizontal compact strip** showing contract-native stage IDs, concise
   labels and normalized evidence states; use vertical fallback when narrow.
3. One **parallel lanes panel** for producers, reviewers and conditional
   integration/release. A child SUBMITTED/VERIFIED must not turn a parent VERIFIED.
   No artificial serial dependencies between independent workstreams.
4. **CURRENT BLOCKER** (or no blocker established) and **NEXT OBSERVABLE —
   responsible actor**. Distinguish an awaiting appointment from a dispatched
   task, actual execution and independent review.
5. Exact controlling issue, PR HEAD, proof refs and candid NOT_RUN/UNKNOWN
   gaps. Do not invent project delivery percentages or Owner decisions.

Combined output order: **progress → evidence/limits → MCDA — ADVISORY**.
The MCDA section contains alternatives, scores/hard requirements, uncertainty
and sensitivity, but no permission to advance workflow stages.

Example only — EXAMPLE / NOT LIVE:

```text
WORKFLOW PROGRESS — Selected contract | NOT LIVE
[M0 VERIFIED] → [M1 IN_PROGRESS] → [M2 BLOCKED] → [M3 NOT_STARTED]
PARALLEL: writer SUBMITTED | planner VERIFIED (bounded) | reviewer BLOCKED
CURRENT BLOCKER: independent review not authorized
NEXT OBSERVABLE: read-only review execution receipt — Owner/OTM → reviewer
EVIDENCE: controlling issue and exact candidate refs
MCDA — ADVISORY: option/rubric tradeoffs separately, no stage approval
```

## Oracle challenge and safety

Bind a verdict to its source, candidate SHA, fixture/expected-value lineage,
actual output, materially wrong implementation that could survive, and reviewer
independence. Author-green, comment receipts, matched Git blobs and source-only
synthetic tests are different from true native/browser/originals qualification.
Keep branch/benchmark custody, permissions and Owner-controlled merge intact.

The bridge never creates cron, email, Work trigger, GitHub comments or a new
decision gate. For regression testing use:

```sh
python -B -m unittest discover -s skills/universal-workflow-progress/tests -v
python -B -m unittest discover -s skills/software-mcda/tests -v
python -B -m unittest discover -s skills/workflow-intelligence/tests -v
```
