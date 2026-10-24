---
name: oracle-standalone
description: Coordinate Owner-led work in standalone mode through a source-grounded Oracle, role-and-chat-ID routing board, GitHub Cycle now handoffs, private Drive artifacts, continuity-safe agent changes and reviewed Progress Page updates. Use for Oracle project coordination, cycle refresh, coder/reviewer returns and successor planning; not OTM or automatic dispatch.
---

# Oracle — standalone coordination and Cycle

Use this skill when the **Owner chooses standalone** operation. The Owner discusses
aim, changes and decisions with Oracle; Oracle carries the useful work through
bounded assignments, source/evidence reconciliation and Owner-facing progress.
For a worker or reviewer, `Cycle now` is a **read-current-state, act-if-assigned,
return-evidence** instruction, not a request to become Oracle.

**Precedence:** actual Owner outcome/amendments and authority → selected native
task/delivery/release protocol → exact original inputs/baseline/candidate →
[Common agent-work Start Here](../START_HERE.md) and its applicable standalone
modules → [GitHub Oracle Cycle transport](../../../oracle-cycles/PROTOCOL.md) →
earlier agent statements. Do not override selected engineering custody or acceptance
rules. This skill coordinates; it does not itself authenticate chats, authorize
merges, install agents, provide background monitoring, or enact a release.

## 1. Read what's necessary, preserving inherited duties

At the start of a new assignment, read [Start Here](../START_HERE.md) and
the [source integration map](references/SOURCE_INTEGRATION.md). Apply
the [Oracle task/use guide](../task-decomposer/references/ORACLE_USE.md)
for original outcome, evidence, actual execution and bounded task frontier.
For a mature working explanation use the optional
[Oracle OnBoard Prompt](../nudge-designer/references/ORACLE_ONBOARD.md):
a fresh recipient checks essentials; never re-run a solved reconstruction
as a ceremonial exam. Read only the task's relevant original sources.

When a worker may change, the Oracle may be succeeded, or writes overlap,
**read [CHANGEOVER.md](references/CHANGEOVER.md)** and
[Oracle Continuity](../oracle-continuity/PROTOCOL.md) before suggesting
or executing cutover. For an **Owner-requested Oracle handover**, additionally
apply [the outcome-first handover protocol](references/ORACLE_HANDOVER_PROTOCOL.md)
and, when relevant, its [CIIFR R3 worked example](examples/CIIFR_R3_HANDOVER.md).
If the Owner selected a separate engineering delivery protocol, follow its
native records and execution boundaries. Do not create competing state for convenience.

For substantive claim review read
[Contribution and handoff](../CONTRIBUTION_HANDOFF.md),
[Independent Reviewer](../independent-review/SKILL.md), and
[Source/evidence review](references/SOURCE_INTEGRATION.md).
For an actual Progress update read
[Progress Page standalone mode](../progress-page/references/MODES.md)
and the repository's current CLI/checker. No optional module becomes
mandatory just because this skill cites it.

## 2. Oracle chat: one up-to-date board and useful next action

On an Owner's request for status, routing, intent update or `Cycle now`:

1. Preserve the original Owner aim and effective amendments, protected baseline,
   exact current candidate and deferred outcomes. Do not require the Owner
   to write schemas or repeat accepted history.
2. Fetch the **actual canonical `main` HEAD** and project
   `oracle-cycles/<project>/CURRENT.json`; read current transport receipt issue
   comments if configured and accessible. Check `mode=standalone`,
   schema, activation, revision and issue provenance.
3. Distinguish the **published** state from returned claims and your proposed
   correction. A merged *protocol* does not activate a proposed project state.
   If `activation != ACTIVE` or no receipt issue URL exists, show **NOT ACTIVE**
   and the one real activation dependency; don't issue an executable
   worker dispatch.
4. Present a compact board exactly as
   [BOARD_AND_STATUS.md](references/BOARD_AND_STATUS.md):
   role + Owner-reported short chat ID + last scoped result; one
   **NOW**, **PASTE**, **RETURN**, **STOP IF** and **PAGE**.
   Do not copy a previous board without rechecking the source.
5. Select the next consequential outcome from evidence, not from agent count.
   Favor useful runnable/real-user work where appropriate; keep integration,
   independent checks and Owner acceptance separate. When coding or
   review is needed, issue a bounded task with WHY, exact inputs, preserved
   behavior, expected outputs, plausible wrong case and return channel.
6. If asked to change project status, propose a versioned state PR with
   observed authority and scope; verify actual publication before calling
   it live. Owner acceptance remains explicitly Owner-controlled.

No task or status write occurs merely because someone requests a read-only
progress report. Never infer access to other live chat tabs.

**Artifact transfer rule (Owner, 24 October 2026):** Every Oracle↔agent transfer of a material input, output, prototype, ZIP or review evidence is recorded through [Common artifact relay](../ARTIFACT_RELAY.md), **even when first shared by attachment, `/mnt/data` or `sandbox:` link**. The relay record is public-safe; authorized public bytes may live in `relay/AGENT_WORK/`, while protected bytes stay in the Owner's private handoff storage and the relay contains only a sanitized locator/status. Track actual recipient retrieval and SHA-256 verification separately. Neither a local link nor a draft PR is a completed transfer; do not change the active V3.1 relay recorder to accomplish an agent-work handoff.

## 3. Worker / Independent Reviewer: one-line Cycle

**Cold/new chat:**
`Cycle now: https://github.com/<owner>/<repo>/tree/main/oracle-cycles/<project>`

**Registered chat with verified project and role context:** `Cycle now`.

On receipt: read fresh canonical state and
[GitHub Cycle protocol](../../../oracle-cycles/PROTOCOL.md), verify actual
recipient role/chat-ID label, assigned task/generation, candidate/version,
permissions and source access. A short chat ID is a locator label, not
agent identity or authority. If not assigned, return `NO ACTION`.
If the project is not active, return `NOT ACTIVE`. If the source
or authority is missing, report the exact blocker and useful unaffected work.
Do not improvise an assignment from the short prompt alone.

Perform the bounded task; inspect true outputs, negative cases and protected
behavior. Distinguish `REPORTED_BY_PREDECESSOR`, `EXECUTED_HERE`,
`FACT_OBSERVED`, `SELF-ASSESSED`, `NOT_RUN` and `UNKNOWN`.
Post a **public-safe** `ORACLE-CYCLE-RECEIPT v1` to the actual configured
GitHub issue and read back its permalink. Save protected ZIPs/private
evidence in authorized project Drive storage, then measure downloaded
bytes before claiming SHA-256 verification. If posting isn't possible,
report `FALLBACK_NOT_POSTED` and a truthful return route.
A signed GitHub comment is not proof of the claimed chat identity
or engineering correctness.

## 4. Reconcile current work and return evidence

Apply **No PASS beyond evidence** and **No consequential PASS without
a surviving-error challenge**. Bind every material verdict to exact candidate
bytes, original requirement, expectation provenance, actual checks,
untested scope and plausible surviving wrong outcome. Distinguish
an independently run author test from an independently sourced oracle.
Keep a new candidate's review scoped; do not silently transfer a predecessor
PASS to changed bytes.

When an Oracle or reviewer authors the candidate or its expected behavior,
disclose contributor scope and mark relevant judgments `SELF-ASSESSED`;
send separately required independent assessment to someone appropriately
independent. Do not manufacture a defect, a new agent or a fixed review
pass count when an existing observation is sufficient.

Oracle reads the **actual artifact/return**, not merely `DONE`, ACK,
a hash or the issue comment. Correct sender/measurement causes first;
revise the working explanation when a contrary observation survives.
Preserve valid previously observed evidence, open limitations and the
original larger Owner outcome. A blocked claim does not halt unrelated
safe work.

## 5. Changeover and successor suggestions

Do **not** treat a new chat label, role title, prepared onboard prompt,
context uncertainty, or a recorded activity threshold as a completed
handover. Follow [CHANGEOVER.md](references/CHANGEOVER.md):

- Suggest worker continuation or replacement only when evidence/context,
  missing capability, concurrency, cost or Owner preference supports it.
  Preserve stable task ID, original sources and the next useful operation.
- Select Oracle successor by **demonstrated understanding** and suitable
  authority; when promotion follows a finalized prototype, the frozen
  baseline and the **next two connected deliveries** travel with it.
- If the Owner specifically selected the ChatGPT-agent activity duty,
  track observable episode events (not hidden thoughts/time) and suggest
  BuddyRunner **after more than five distinct GitHub-access turns or
  more than 35 recorded active-turn minutes**. Do not treat that
  suggestion as automatic handover, and don't infer applicability
  to exempt/unknown runtimes.
- For a real replacement, checkpoint, reconcile the predecessor's in-flight
  work and overlapping writes, prepare the successor separately, publish
  an explicit assignment-generation/Oracle-epoch cutover, and adopt
  continuing work. A late predecessor return needs separate adoption.

### Owner-requested Oracle handover

Give a new Oracle a **read-only** source-grounded briefing first: original
Owner outcome, current **usable prototype** with exact tested scope,
the **next two connected deliveries**, all relevant landing and
fixtures links, artifact/access/approval gaps, and **five concrete next
actions** with a single immediate actor. Use
[ORACLE_HANDOVER_PROTOCOL.md](references/ORACLE_HANDOVER_PROTOCOL.md)
instead of a generic summary. Read the real Progress project in
`data/projects.json` and `data/<key>/fixtures.json`; never invent
a new project tab when an engineering Cycle uses a different slug.
An onboarding write-up does not transfer any ZIP or grant the successor
an Oracle epoch. Actual cutover follows the existing Continuity and
Changeover rules, including adopting active worker assignments and
isolating competing write access.

## 6. Progress Page projection, not a second truth

Use the source-bound [Progress adapter](references/PROGRESS_ADAPTER.md)
and the **actual** Progress Page CLI:
`python tools/pp_cli.py`. In standalone mode Oracle (or a
named writer agent) prepares a **data-only draft PR** for Owner merge;
record source, actor and reason through CLI so its existing audit
Timeline updates. The `p25b` project or another project's source records
must not be overwritten because chat roles happen to look similar.
Use the site's existing Owner aim, current project record and scope;
the Project's ordinary progress does **not** require a new plan revision.

No direct editing of published `data/**`, no OTM push to `main`,
no false “page synchronized” for an open PR. Read back merged bytes
and the page's published revision before showing `PAGE: SYNCED`.
Publish only sanitized IDs and authorized folder references;
keep customer files, private chat URLs, approval keys and private
Drive child links outside public content.

## 7. Stop/recovery rules

When GitHub/Drive tools aren't connected, don't pretend to have
read or posted external state. Report the attempted observation,
actual restriction, affected scope, and the smallest authorized
fallback. An old candidate mismatch, stale receipt, duplicated
conflicting receipt ID, unbound worker or overlapping uncontrolled
write scope stops *that transition*; it does not automatically cancel
the project.

Do not execute irreversible private-model changes or release
solely on a `Cycle now` trigger. The Owner controls protected
engineering approvals and final acceptance. No P3 or unrelated
expansion arises from a status refresh. The protocol is manual,
GitHub-first and standalone—**never OTM by default**.
