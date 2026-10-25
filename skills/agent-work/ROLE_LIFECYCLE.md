# Role and mode playbook — full project/file lifecycle

This playbook expands [START_HERE.md](START_HERE.md), the short entry point, into a practical role/mode and full file-cycle reference. It is not a new skill, permission, controller or approval process. [Original operating guide](OPERATING_GUIDE.md) preserves the former extended material.

## 1. Begin with the live project, not this document

1. Read the Owner's **written aim**, amendments, intended user and one observable outcome from the project's canonical issue/Progress Page. If the aim is missing, obtain it before planning.
2. Identify the **selected native protocol**, current repository, exact candidate/baseline and input/fixture custody. A source link is not evidence that its contents or bytes were accessed.
3. Establish your **actual responsibility**, the **project coordination mode** (OTM or standalone), any separate engineering delivery mode, and current assignment. A role name/chat ID/Progress Page readiness stage cannot grant authority.
4. Name **one next executable step** and the evidence it must return. For a product, prefer a small runnable slice on authorized real inputs; when private files are unavailable, follow the Owner's actual fallback/hold decision rather than inventing a trial.

**Precedence:** Owner intent and explicit decisions + selected engineering/delivery/custody authority → exact original sources and current candidate → applicable Common role instructions → historical agent accounts. Never treat this router as permission to bypass a project-specific HOLD, independent review, merge or release rule.

## 2. Choose the coordination mode first

| Project mode | Who coordinates and publishes progress | Read first | Do **not** inherit |
| --- | --- | --- | --- |
| **OTM** (OwnerTeammember-led) | OTM controls the existing project coordination route; nominated Oracle may design/challenge work but does not self-dispatch or self-approve. OTM records Progress Page evidence using its native mode. | [Progress Page mode contract](progress-page/references/MODES.md); [Oracle execution guidance](nudge-designer/references/ORACLE_EXECUTION.md); if selected, [engineering v3.6 coordinator](../engineering-pr-delivery-v3.6/MODE_COORDINATOR.md) | Standalone Oracle Cycle, Oracle-controlled page publication, new write/merge rights |
| **Standalone Oracle** (no OTM) | Owner chooses a project Oracle to coordinate. Oracle (or named writer) prepares Progress Page draft changes; Owner merges. | [Oracle Standalone](oracle-standalone/SKILL.md); [Progress Page mode contract](progress-page/references/MODES.md) | OTM dispatch/control epoch, automatic Cycle activation or merge |
| **One Owner + one builder, no separate Oracle** | Owner and builder execute directly under the selected task/delivery protocol. State the missing reviewer/coordination coverage honestly. | [Prototype-first](prototype-first/SKILL.md); applicable native delivery instructions | Fictional Oracle, independent review, or a requirement to staff every role |

**Two different uses of "mode":** Progress Page `otm/standalone` sets coordinator and page-update route. A separately selected engineering v3.6 `coordinator/standalone` governs that engineering delivery protocol. One setting does not silently select the other. [Oracle Chat Routing](oracle-chat-routing/STANDALONE.md) is a **manual transfer convention**; [Oracle Cycle](../../oracle-cycles/PROTOCOL.md) is an **explicitly selected GitHub transaction convention**, not a default.

## 3. Choose your role — read only its route

| You are acting as… | Your job and first reference | Required return / boundary |
| --- | --- | --- |
| **Owner** | Set the aim, what may change, real-file access, acceptance and release boundary; see [short request patterns](OPERATING_GUIDE.md#start-with-a-short-request) | Actual user trial and recorded decision; no invented technical PASS |
| **OTM / team coordinator** | In OTM projects, preserve authority/assignments, choose one next actor, deliver the authorized packet, challenge returns and record evidence; [mode contract](progress-page/references/MODES.md), [handoff guidance](CONTRIBUTION_HANDOFF.md) | Source-linked assignment and reconciliation; never adopt standalone dispatch implicitly |
| **Project Oracle, OTM-assigned** | Hold whole outcome, map slices, brief or challenge an agent under OTM authority; [Oracle execution](nudge-designer/references/ORACLE_EXECUTION.md), [Task Decomposer](task-decomposer/SKILL.md) | Usable task, challenge and decision to OTM; Oracle role alone grants no edit/merge authority |
| **Project Oracle, standalone** | Maintain one source-grounded board, assign bounded work within Owner grant, reconcile evidence and arrange succession; [Oracle Standalone](oracle-standalone/SKILL.md) | One next actor/action, exact source/receipts; reviewed page DRAFT, not unilateral merge |
| **Builder / specialist agent** | Inspect original task, protected boundaries and capability; build the bounded runnable slice; [Prototype-first](prototype-first/SKILL.md), [Oracle OnBoard template](nudge-designer/assets/prompts/oracle-onboard.md) | Actual runnable result or BLOCKED, exact head/bytes, tests/NOT_RUN, known wrong case and continuation; no self-acceptance |
| **Independent reviewer / falsifier** | Derive expectation from originals, state author/context/method independence, try a surviving-error challenge; [Independent Reviewer](independent-review/SKILL.md), [independence dimensions](independent-review/references/INDEPENDENCE.md) | Exact-scope PASS/PARTIAL/FAIL or evidence gap; no wider approval than tested |
| **Oracle or reviewer acting as contributor** | Make bounded authorized high-ROI change, disclose changed role and exposure; [Contribution & Handoff](CONTRIBUTION_HANDOFF.md) | SELF-ASSESSED result + new independent review for affected consequential scope |
| **Successor Oracle / replacement agent** | Recover current aim, candidate, unresolved defects, private custody and in-flight ownership; [Oracle Continuity](oracle-continuity/PROTOCOL.md), [handover protocol](oracle-standalone/references/ORACLE_HANDOVER_PROTOCOL.md) | Read-only reconstruction first; cutover only through selected native authority, not from chat ID |
| **Progress Page recorder** | Read GitHub evidence; update **existing** project records and audit with the [Progress Page module](progress-page/README.md) and [mode rules](progress-page/references/MODES.md) | Accurate projection/Timeline; not an extra task ledger or engineering gate |

Roles can be combined when people are scarce, but self-review must be labelled. A reviewer contributing code cannot independently approve that changed scope. OTM and standalone Oracle have **different coordination authority**, even if both use the same assessment techniques.

## 4. One end-to-end project/file cycle

| Step | Responsible role | Surviving record / check |
| --- | --- | --- |
| **A. Intent and sources** | Owner + coordinator | Owner aim, acceptance observable, amendments, original files or hashes, project-specific constraints |
| **B. Slice and assignment** | OTM or standalone Oracle (as actually authorized) | One bounded task, selected mode/protocol, exact baseline, named recipient, necessary model knowledge, return contract |
| **C. Onboarding** | Recipient + coordinator | Seven checks below; unavailable access is BLOCKED/UNKNOWN, not guessed |
| **D. Build and trial** | Builder + Owner where appropriate | Runnable URL/command on permitted real inputs, actual trial result, exact revision and failures |
| **E. Artifact relay** | Sender + receiver | [Durable artifact handoff record](ARTIFACT_RELAY.md), locator/size/SHA-256 as applicable, recipient-byte access verified separately; private bytes stay private |
| **F. Independent challenge** | Distinct reviewer when required / appropriate | Expectation source, exact candidate, surviving-error falsification, independence limits and NOT_RUN |
| **G. Reconcile and integrate** | Coordinator/Oracle within delegated authority | Disposition of findings, corrections at new exact head, tests repeated as necessary, one next decision |
| **H. Accept, record, continue** | Owner accepts/releases; page recorder projects | Actual Owner outcome, merge/release only by authorized actor, Progress Page source-linked Timeline; successor checkpoint |

**Readiness is not authorization.** The Progress Page records **Not assigned → Sources checked → Access verified → Ready for bounded task**. For the assigned participant and same task/milestone, check: **(1)** Owner aim; **(2)** canonical sources; **(3)** role/task binding; **(4)** actual capability and access; **(5)** protected boundaries; **(6)** runnable demonstration or explicitly NOT_RUN/BLOCKED; **(7)** evidence return and next actor. Read [the Progress Page onboarding contract](https://github.com/reallakshman19/progress-page/blob/main/docs/ONBOARDING_READINESS.md) when available. The seven checks are guidance; no stage may be promoted without its specified native GitHub receipt.

## 5. Use references and tests without mistaking them for proof

[Examples, golden cases, fixtures and templates — by role](REFERENCE_INDEX.md). Start with **raw inputs** for a fresh test; withhold golden expected results from the participant being tested. Synthetic references explain the method but cannot establish success on current private inputs, production runtime, or the exact PR head.

**For depth:** [full original operating guide](OPERATING_GUIDE.md) · [Nudge Designer](nudge-designer/SKILL.md) · [Gatekeeper](gatekeeper/SKILL.md) · [local handoff](local-handover/AGENT_PROTOCOL.md). Load only what this task needs.

## 6. Resume or hand over safely

A successor should be able to open GitHub and name **the Owner aim, current exact candidate, runnable result, important unresolved counterexample, protected private-artifact locator, current authority/assignment, and ONE next executable action**. If any is missing, record the gap; do not assert a successful cutover or verified file delivery. See [continuity](oracle-continuity/PROTOCOL.md) and [relay](ARTIFACT_RELAY.md).

