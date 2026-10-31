# Agent-work reference index — examples, goldens, fixtures and templates

**Owner-facing continuation reference:** [Task Evidence v2](TASK_EVIDENCE_V2.md) is the frozen five-line output whenever an established Oracle/agent is continued with Cycle now. Native task, relay, independent review and actual canonical Cycle receipts remain authoritative.

**Use with [START_HERE.md](START_HERE.md).** This is a discovery map, not a required checklist or a claim that a project has passed. Read **role + mode → source → raw fixture → expected behavior**, not every file. Keep private production bytes out of public fixtures.

## Status and safe use

- **Golden** = a documented expected distinction for a **synthetic** source/case; it is useful for testing a method, **not** a production acceptance witness.
- **Fixture** = a fixed example input/state or transition; check its provenance and actual test status. A JSON schema pass is not proof of a correct Owner outcome.
- **Template** = a blank instruction/report; fill its exact task/revision/authority from canonical records.
- **Worked example** = historical/illustrative analysis; dated snapshots are never the current assignment or current PR head.
- **Real evidence** = a fresh exact-head/input/runtime observation with its own native issue/PR/log/file receipt. Never substitute the above examples for this evidence.

## Role-directed source map

| Role / work moment | Good starting artifact | Fixture, worked example or expected behavior | Important limit |
| --- | --- | --- | --- |
| Owner / aim | [Guide: short Owner requests](OPERATING_GUIDE.md#start-with-a-short-request) | [Prototype-first benchmark and slice contract](prototype-first/SKILL.md#benchmark-r0-ciifr-s1) | Historical R0 benchmark is not the current product's acceptance |
| OTM / coordinator | [Progress Page modes](progress-page/references/MODES.md) | [Progress data example directory](progress-page/examples/data/); [Gatekeeper OTM walkthrough](gatekeeper/references/WALKTHROUGH.md) | Illustrative OTM use, **not** a certified full OTM end-to-end golden |
| OTM-assigned Oracle / task map | [Oracle execution loop](nudge-designer/references/ORACLE_EXECUTION.md) and [Task Decomposer](task-decomposer/SKILL.md) | [Task Decomposer example index](task-decomposer/examples/INDEX.md) | Keep OTM custody/dispatch separate; a plan is not execution |
| Standalone Oracle | [Oracle Standalone](oracle-standalone/SKILL.md); [manual chat routing](oracle-chat-routing/STANDALONE.md) | [Manual synthetic handoff case](oracle-chat-routing/STANDALONE.md#7-synthetic-worked-example-not-a-live-handoff); [CIIFR R3 handover illustration](oracle-standalone/examples/CIIFR_R3_HANDOVER.md) | Chat ID is display metadata; historical handover does not activate Oracle successor |
| Builder / specialist | [Prototype-first slice lifecycle](prototype-first/SKILL.md) | [CIIFR S1](prototype-first/examples/CIIFR-S1.json), [S2](prototype-first/examples/CIIFR-S2.json), [S3](prototype-first/examples/CIIFR-S3.json) | Never call a prototype user-tested until user actually runs it |
| Agent onboarding / first mentoring | [Initial Mentoring](initial-mentoring/SKILL.md) and [Oracle OnBoard guide](nudge-designer/references/ORACLE_ONBOARD.md) | [Word-to-Table and CII source-grounded mentoring examples](initial-mentoring/examples/word-table-and-cii.md), [Oracle OnBoard prompt](nudge-designer/assets/prompts/oracle-onboard.md), [builder brief](prototype-first/assets/builder-brief.md) | Around three adaptive questions align concept, hard architecture and next result; **not a scored gate or repeat for returning agents** |
| Independent reviewer | [Independent Reviewer](independent-review/SKILL.md), [independence dimensions](independent-review/references/INDEPENDENCE.md) | [Golden cases G01–G10](independent-review/examples/INDEX.md), [raw inputs](independent-review/examples/raw/), [result records](independent-review/examples/records/) | Same-principal checks stay SELF_REVIEW even if new chat |
| Contributor Oracle / reviewer | [Contribution and Handoff](CONTRIBUTION_HANDOFF.md) | [Review G05 self-review and G10 shared wrong premise](independent-review/examples/INDEX.md) | A contributor cannot independently approve affected scope |
| Successor Oracle / replacement | [Oracle continuity protocol](oracle-continuity/PROTOCOL.md), [standalone handover](oracle-standalone/references/ORACLE_HANDOVER_PROTOCOL.md), [read-only mentoring](initial-mentoring/SKILL.md#3-special-case--incoming-oracle) | [Initial state](oracle-continuity/examples/initial.json), [worker cutover](oracle-continuity/examples/worker-cutover.json), [Oracle cutover](oracle-continuity/examples/oracle-cutover.json) | Concept/architecture/next-two-tasks alignment is **not** a control cutover or permission transfer |
| Artifact sender / receiver | [Artifact relay](ARTIFACT_RELAY.md), [local handover](local-handover/AGENT_PROTOCOL.md) | [Local handover index](local-handover/README.md) | Reported attachment is not verified recipient bytes |
| Progress Page recorder | [Progress Page instructions](progress-page/README.md), [modes](progress-page/references/MODES.md) | [Owner reply template](progress-page/templates/owner-reply.yml), [Progress checker CI template](progress-page/templates/check-progress-data.yml) | Progress VERIFIED/readiness does not establish engineering acceptance |
| Labels / release | [Gatekeeper](gatekeeper/SKILL.md) | [Walkthrough](gatekeeper/references/WALKTHROUGH.md), [recipes](gatekeeper/references/RECIPES.md) | Release needs the selected Owner grant; applicable personal-use scope differs |

## Golden fixture pairs and negative cases

| Case | Raw input / model | Golden or asserted distinction | What it catches |
| --- | --- | --- | --- |
| TD UI project | [Raw](task-decomposer/examples/ui-programme/raw.md) / [map](task-decomposer/examples/ui-programme/task-map.json) | [Golden](task-decomposer/examples/ui-programme/golden.md) | Misplaced work boundaries and coupled dependencies |
| TD event order | [Raw](task-decomposer/examples/single-logic/raw.md) / [map](task-decomposer/examples/single-logic/task-map.json) | [Golden](task-decomposer/examples/single-logic/golden.md) | A coherent-sounding but incorrect event model |
| TD physical model | [Raw](task-decomposer/examples/single-model/raw.md) / [map](task-decomposer/examples/single-model/task-map.json) | [Golden](task-decomposer/examples/single-model/golden.md) | Unsupported assumptions masked by arithmetic |
| IR G02 | [Independent Review raw suite](independent-review/examples/raw/) | [G02 expected outcome](independent-review/examples/INDEX.md) | Green author tests that implement the wrong rule |
| IR G03 | [Raw suite](independent-review/examples/raw/) | [G03](independent-review/examples/INDEX.md) | A real source defect incorrectly erased because runtime was NOT_RUN |
| IR G04 | [Candidate revision fixture](independent-review/examples/records/current.json) | [G04](independent-review/examples/INDEX.md) | Stale result being promoted to a new candidate |
| IR G05 | [Independent Review cases](independent-review/examples/INDEX.md) | SELF_REVIEW with exposure, not an independent verdict | Same principal relabelled as non-author reviewer |
| IR G08 | [Independent Review cases](independent-review/examples/INDEX.md) | Integrated journey unresolved despite passing units | Component-level PASS treated as complete product |
| IR G10 | [Independent Review cases](independent-review/examples/INDEX.md) | Shared unjustified model remains unresolved | Multiple agents agreeing on the same wrong expectation |
| Continuity | [Initial](oracle-continuity/examples/initial.json) → [worker cutover](oracle-continuity/examples/worker-cutover.json) / [Oracle cutover](oracle-continuity/examples/oracle-cutover.json) | [Protocol](oracle-continuity/PROTOCOL.md), [contract tests](oracle-continuity/tests/test_contract.py) | Assignments/history confused with live authorized ownership |

**Golden separation:** When a new builder/reviewer is being evaluated, provide only original/raw task and permitted instructions; keep the golden answers/expected outcomes from that attempt. Goldens may be read afterwards for assessment. A reviewer exposed to a golden must disclose that exposure.

## One current-task onboarding packet (fill, do not presume)

Use [the existing Oracle OnBoard template](nudge-designer/assets/prompts/oracle-onboard.md) and include these minimal fields:

| Field | Source of truth |
| --- | --- |
| `Aim / acceptable outcome` | Owner's current words and source issue |
| `Mode + native authority` | OTM/standalone coordinator and separately selected delivery protocol |
| `Role + recipient + assignment revision` | Native task/assignment record, not inferred from chat ID |
| `Current exact source/candidate + custody` | Original file/hash, branch/head, private locator status |
| `One bounded step + runnable acceptance observation` | Task/slice and user outcome |
| `Required return / negative case / NOT_RUN` | Actual commands, output, comparison and reviewer scope |
| `Artifact transfer + next actor` | [Relay register](ARTIFACT_RELAY.md), issue receipt and next authorized decision |

## Integration test scenarios for START_HERE and Progress Page

1. **OTM project:** Oracle designs a slice; OTM dispatches under selected native control, records source-linked receipt. No automatic standalone Cycle or Oracle-owned page PR is inferred.
2. **Standalone project:** Oracle coordinates; chosen recipient gets one current task; page update is a DRAFT until Owner merges. OTM is not silently introduced.
3. **Unassigned recipient:** Page displays **Not assigned** despite protocol URLs, a VERIFIED unrelated card or another participant's completed checks.
4. **New recipient:** Old person's source/access/ready receipts do not promote the new participant; bind new evidence to same current milestone and participant.
5. **Private file in chat:** A `sandbox:` or `/mnt/data/` path is staging only; durable relay record and actual recipient-byte verification remain distinct.
6. **Reviewer becomes contributor:** Previously independent verdict remains bound to old scope; new affected scope is self-assessed until a suitable non-author review.
7. **New PR head / new Owner intent:** Reconcile baseline, candidate and native controls before reusing results; never carry stale evidence as current PASS.
8. **Oracle successor:** PREPARED handover and a new chat ID do not activate control; successor can reconstruct from GitHub, but cannot claim write authority without native cutover.

These are **scenario expectations**, not claims that the live project or Progress Page has exercised all eight.
