---
name: progress-page
description: Run and use the Progress page, a static page plus JSON data in GitHub that shows each project's milestones, agent blocks, Owner decisions, grounding fixtures, Timeline, plan revisions and Nudge + queues. Use to start a page, record project progress with evidence, add or archive a project, supersede or cancel work, queue an instruction for the coordinator, or build the local file for the Owner. Works with an OwnerTeammember (OTM mode) or an Oracle (standalone mode). Ships the checker, editing tool, trigger tool and page; use them, do not rewrite them.
---

# Progress page

## Zero-extra-reporting entry (roles)

| Reader | Start here | Native reporting destination |
|---|---|---|
| Builder or reviewer | Open the task-specific `#/project/start/REV/wbs%3AN/Mn/CARD_ID` Agent Start deep link from the native task. Verify the issue, exact PR head and authority before acting. | Existing native issue/PR/test record only. Never maintain Page JSON. |
| Coordinator/Oracle | Inspect the native evidence, run `pp_cli.py reconcile` for drift and `pp_cli.py propose --actor NAME --source URL --project KEY [--card ID]` to prepare a **review-required reference-only** manifest. | Verify exact native source/target and dry-run `pp_batch.py`; audited data PR only, no auto-PASS. |
| Page writer | Use `pp_batch.py` in dry-run before a reviewed, checked `--apply` (one source can support multiple native changes). | Exact source and append-only Timeline. |
| Owner | Open Agent Start for orientation or My actions for decisions. | Existing GitHub-signed decision workflow. |

A project-wide Agent Start is deliberately a **workstream chooser**, not a live sorted task queue. Explicit live-card deep links are preferred for assigned tasks; the legacy milestone route still lists all recorded work. Wrong, closed or mismatched task IDs never select a replacement. A narrowed WBS milestone lists the bounded original records without hiding cards. No actor label denotes an accepted assignment until confirmed at the canonical native source.

The project's compact header and page width are uniform across tabs (including Agent Start), with Owner aim available in its disclosure and on Home. Three-column narrow-desktop WBS tiles and one-line scrollable navigation avoid layout jumps. This is presentation-only; agents keep reporting exactly once in their native work records. The reusable page's responsive PC layout is global. Primary views are Project Home, Progress / WBS and Continuity / Onboard Central; the latter groups Agent Start, Oracle continuity, Risks & handoffs and Grounding fixtures. Existing deep links (including exact task and historical routes) remain valid. WBS chooser descriptions come from the already recorded milestone name and `full` text, never another agent status submission or a fabricated family aim. The UI does not change who owns a task.

Agent Start is a **read-only projection**, not a new assignment protocol or release gate. If this Page differs from an authoritative native issue or Cycle, stop and reconcile the source. The writer must read the native evidence; a URL alone is not proof of its claim.


Prototype v0.1. This is a runnable toolset, not only guidance. Read [README.md](README.md) first (five minutes), then use the tools in `scripts/`.
For standalone or end-to-end use, begin with [Start here](https://github.com/reallakshman19/Common/blob/main/skills/agent-work/START_HERE.md).

## Use it when

- a project has several agents and the Owner needs one place to see who is doing what, what is next and what needs the Owner;
- the record must be traceable: every change has a who, a why, a time and a GitHub source;
- a new agent, an Oracle or an OTM must take over the page without reinventing it.

Do not use it as an approval gate, a task tracker that replaces the project's own issues, or a place for private text.
For a read-only strip inside a chat, see `universal-workflow-progress`.

## Operating rules

1. **Record from evidence.** Read the comment, commit or pull request, then record it with its link and its time. Never record a claim you did not read.
2. **Use the tool.** `scripts/pp_cli.py` writes the data, the Timeline entry and runs the checker. Never edit `audit.json` or the data by hand. If a check fails, nothing stays written.
3. **Nothing is deleted.** Supersede, cancel, archive or withdraw. The history stays on the page and in git.
4. **Public-safe only.** Short chat ids, never chat links; no Drive, OneDrive or SharePoint links, emails or tokens. Chat links stay in a private file or the Owner's browser.
5. **VERIFIED needs evidence a different reader can open.** A coordinator that wrote the record is reviewing itself; say so. Use [Independent Reviewer](../independent-review/SKILL.md) and the [Gatekeeper](../gatekeeper/SKILL.md) labels for deliverables.
6. **A revision only for an Owner decision that changes direction**, with the Owner's words and a link. Everyday movement goes to the Timeline.
7. **The coordinator reads Nudge + lines, not the agent.** It folds them into its own next message, then records `nudge done` with the link of what it sent.
8. **Act on the triggers** (`pp_cli.py triggers`) in the same turn you see them. See [references/TRIGGERS.md](references/TRIGGERS.md).

## Roles

| Role | Does | Never |
|---|---|---|
| Owner | decides, answers decision cards, adds Nudge + lines, controls standalone merges by default; see repo-specific go-ahead below | is asked to edit JSON |
| Coordinator (OTM or the project's Oracle) | records evidence, answers triggers, sends the nudges, keeps the Timeline complete | invents evidence, forwards a nudge blindly |
| Writer agent (standalone, named by the Oracle) | makes the pull request under delegated authority; may perform repo-specific approved merge when permitted | assumes product acceptance or cross-repo merge authority |
| Agent | leaves evidence on GitHub | writes the page |

**Scoped Owner merge rule:** For **`reallakshman19/progress-page` alone**, an Owner go-ahead for a draft PR also permits the authorized operator to mark ready and **merge the same scoped PR** after required exact-head checks, current-base compatibility and GitHub protections; no **second** Owner merge approval is required. Block on failed gates, conflicting HOLDs or material scope drift. Other repos keep their own merge/acceptance authority. See [MODES.md](references/MODES.md) and the target repository README. GitHub merge does not imply product acceptance or independent review.

Modes and the Nudge + wiring: [references/MODES.md](references/MODES.md). Fields and rules: [references/DATA_CONTRACT.md](references/DATA_CONTRACT.md).

## Start

- New page: `python scripts/pp_cli.py bootstrap <new repo folder> --repo <owner>/<name> --page <page url>`, then `project add`.
- New Oracle or writer agent: give it [assets/ORACLE_ONBOARD_PROMPT.md](assets/ORACLE_ONBOARD_PROMPT.md).
- The Owner's machine: `pp_cli.py local ... --prerender` builds one HTML file that also works where scripts are blocked.

## Limits (prototype)

- The checker proves shape, consistency and an append-only Timeline. It does not prove that a source says what a card claims.
- Viewing an older revision needs the network (it reads the old commit from GitHub); offline copies show the revision list only.
- The writer claim in standalone mode (one open data pull request per project) is a convention, not a check.
- The page is read-only. Owner input arrives as a GitHub issue; the coordinator records it.
