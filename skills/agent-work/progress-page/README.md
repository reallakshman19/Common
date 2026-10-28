# Progress page · how to use it (Prototype v0.1, optional Common module)

One static web page that shows, for every project: **milestones**, **agent blocks** (who does what, how long ago it moved, what is next),
the **Owner's decisions** ("My actions"), **grounding fixtures**, a **Timeline** of every update, plan **revisions**, and a **Nudge +** queue per agent.
The data is plain JSON in a GitHub repository; GitHub history is the trace. This folder holds everything needed to run one:
the page, a checker, an editing tool, a trigger tool, a local-file builder, templates and tests.

**Scope-first Agent Start (v33):** Unscoped `#/PROJECT/start` shows **WBS workstream choices** and no arbitrary agent task. A WBS family then shows its milestones, and a step shows every recorded work item with next action, actor (or explicitly unassigned), native evidence and collapsed historical details. Never treat milestone ordering as a task priority or recorded labels as authority. The original source remains normative; no second agent report is required.

**Exact selected-task handoff (v29):** The optional `#/PROJECT/start/REV/wbs%3AN/Mn/CARD_ID` route selects the exact live card inside the named milestone. Wrong, removed, mismatched or malformed identities fail visibly without switching to another project or task. **Copy this task** gives a source-backed, full-text preview separate from **Copy milestone evidence** for the complete multi-card milestone. Neither button dispatches, acknowledges an assignment, changes project state or requires an extra agent report. Native task/PR evidence remains authoritative.

**Project navigation and WBS titles (v33):** Primary tabs are **Project Home → Progress / WBS → Continuity / Onboard Central**. Central contains Agent Start, Oracle continuity, Risks & handoffs and Grounding fixtures. Historic URLs remain valid, including exact task links. Both Agent Start and Progress/WBS chooser tiles show existing source-recorded milestone names and `full` descriptions; if the parent record is missing, child names stay plainly identified and no WBS aim is invented. All this is read-only; neither agents nor the coordinator have to supply an additional status field, acknowledgement or report.

**Native-source to proposed audited Page update (v29):** Use `python scripts/pp_cli.py propose --project ciifr --source https://github.com/OWNER/REPO/pull/185 --actor Oracle --card geo-g1 --output proposal.json` to create a **review-required, reference-only** `card set` manifest from the original PR/issue/comment. An exact existing source URL can select one card only if unambiguous; else supply `--card`. Existing receipts and candidate drift are blocked. Review the original record, then run `python scripts/pp_batch.py proposal.json --data <page-checkout>/data` for staging; `--apply --base origin/main` rechecks the PR head/issue revision before creating any audited update. **No status, next actor, capability, engineering PASS or Owner permission is inferred or upgraded.** Reviewer/editor must still publish through an authorized repository PR; this is not a background watcher.

**Stable shell layout (v33):** Project title, revision row, compact Owner-aim disclosure, page width, and primary navigation now remain aligned on Home, Progress/WBS and Continuity routes. The full Owner aim remains visible in the Home overview. Narrow desktops use three WBS tiles per row, and navigation uses a single horizontally scrollable line rather than wrapping. Same read-only/native-evidence boundaries; no additional builder, Oracle or Page update requirement. Reference browser tests compare the actual shell coordinates across views at desktop, 1118px narrow-desktop and mobile sizes.

**Project/WBS checkpoints and guarded Cycle bridge (v33):** The Home overview shows a source-linked project checkpoint; selected WBS and scoped Agent Start provide a compact checkpoint. Recent audited Page changes are a deduplicated *display* of existing events, never a second ledger. Page JSON fetch success/failure is separate from whether the underlying native PR/issue was actually checked (normally UNKNOWN). A Common `Cycle now` observation is supported only with an explicit, project- and WBS-scoped `cycle` binding from the Page's `data/projects.json`. Binding identity, schema, activation, page projection and WBS scope are checked before an actor is shown. Nothing is auto-dispatched or promoted. **No mapping is seeded** because the broad CIIFR Page and the narrower Geometry Cycle must not be conflated. See the reference README for the binding contract; source/writer review is still required.

**New-agent continuation and read-only native-source watch (v33):** Scoped WBS checkpoints provide a cold-start original task/source, canonical Cycle and return checklist. The explicitly mapped Cycle observation distinguishes Owner decisions, returned work awaiting Oracle reconciliation, and role/assignment-generation rechecks. These are advisory, not dispatches. A coordinator can run `python scripts/pp_cli.py --data <page-checkout>/data watch --project KEY --limit 25`, optionally using `--baseline prior-scan.json` from an ephemeral previous output, to compare exact native PR head/state or issue/comment update identity. `BASELINE_REQUIRED`, `NO_CHANGE`, `SOURCE_CHANGED` and `UNKNOWN` remain distinct; source failures and capped scans are incomplete. No data, Timeline or agent reports are written. Changes still require original evidence review and the existing authorized `reconcile`/`propose`/`pp_batch` path. Continuous scheduled scanning and automatic publication are **not enabled**.

**Read-only Cycle/WBS binding preflight (v33 tool patch):** Before the coordinator proposes any `cycle` metadata mapping, run `python scripts/pp_cli.py --data <page-checkout>/data cycle-preflight --project ciifr --cycle ciifr --wbs 3`. The tool reads Common `CURRENT.json` pinned to an observed `main` commit and verified Git blob, then checks the exact Page project/WBS root, recorded native WBS and current task links, Page publication revision, actual native issue/PR fetch and exact candidate SHA/merge state. It emits **READY_FOR_REVIEW**, **SCOPE_MISMATCH** or **INSUFFICIENT_EVIDENCE** with source conflicts/gaps. **READY_FOR_REVIEW does not create a binding, grant an assignment, qualify a claim or approve a merge**; further Owner/coordinator review and the existing Page writer process are always required. Current CIIFR Cycle revision 18 describes PR191 merge decision as pending while the native PR is merged and Page R4 WBS 3 lacks the latest task/candidate: no automatic mapping is activated. This preflight has no agent log, receipt, or state mutation.

**Reference Page scheduled CIIFR monitor pilot (v33 tool update, source coverage):** On merged `reallakshman19/progress-page` only, the daily/manual read-only `.github/workflows/native-source-watch.yml` observes **existing public CIIFR Page card links plus the explicitly selected canonical CIIFR Cycle WBS 3 sources**. It stores previous full source fingerprints temporarily in Actions cache, suppresses unchanged runs, and publishes a short-lived Actions artifact only when a native source changes or retrieval is incomplete. The portable `scripts/pp_watch_job.py` adapter is reusable with the existing `pp_watch.py`; **Common does not install or run the reference repository's scheduled workflow**. No Page data write, independent verdict, assignment, Cycle acknowledgment, second Timeline or additional agent report. CIIFR WBS 3 still lacks Page links to native issue #180 and PR #191. The explicitly scoped Cycle preflight now detects that gap and stale canonical merge decisions without activating Cycle binding. It emits one review signal per observed gap/state fingerprint, suppresses identical repeat runs, and preserves the previous complete baseline on failed retrieval. It does not update either protected source; the existing Oracle and designated Page writer must reconcile them. A missed schedule is not evidence of no change.

**All project views — desktop and mobile:** The wide PC layout now applies to Progress/WBS, Project Home, Actions, Fixtures, Timeline and all project tabs, not merely Agent Start. Primary view tabs precede WBS filters; repeated Owner aim/method and optional private chat setup collapse outside Project Home overview. Four-column WBS families and flexible work cards use desktop width; source-heavy tables/fixtures/decision content wrap on phones. Lessons preserve their vertical reading width. No stored project data changed. Chromium regression covers 120 checks across active projects, all nine views, dark mode and Lessons.

**Quick start: zero additional agent reports.** The builder/reviewer opens the project's native task and its `Agent Start` link (for example `https://reallakshman19.github.io/progress-page/#/ciifr/start/R4/wbs%3A3/M13`), verifies current candidate/authority from original GitHub sources, and leaves evidence only on that native issue/PR. The coordinator, not the builder, reconciles it into the Page. The Page never grants Writer/Owner authority.

**Source reconciliation (read-only):** `python tools/pp_cli.py reconcile --project ciifr --source https://github.com/reallakshman19/XML_Compare_Utilities/pull/185 --expected-head <SHA>`. It reports current GitHub candidate identity, duplicate source receipts, drift and uncertainty; it cannot interpret engineering PASS. From the Common module source tree, use `python scripts/pp_cli.py`.

**Audited batch (coordinator only):** Supply a reviewed JSON manifest with `project`, `actor`, one native GitHub `source`, and `changes` containing native `plan milestone`, `card set`, etc. Preview using `python tools/pp_batch.py update.json --data data` (no changes). After reviewing source and proposed event IDs/files, use `python tools/pp_batch.py update.json --data data --apply --base origin/main` in the page checkout. No automatic promotion of acceptance; normal repository PR and Owner boundaries remain. For Common source the command is `python scripts/pp_batch.py ...`.

**Viewer/tool parity:** The reusable `viewer/` and `scripts/` here are synced from Progress Page merge commit `5218a22851c2d25f569f58910702a7d0d9627ef2` (`v=33` viewer). Keep `viewer/VERSION` pinned to the tested source. CI validates the generic bundle/checker and standard-library tests; project-specific source data and Owner controls remain separate.

**Offline source parity guard:** `python -B -m unittest skills/agent-work/progress-page/tests/test_reference_parity.py` verifies exact Git blob SHA-1 for every bundled portable viewer and tool file against `references/UPSTREAM_PARITY.json` without relying on network. A deliberate reusable-core change must first be merged to the reference page and re-synced with a new pinned source commit; never silently claim parity by editing the manifest to fit arbitrary bytes.

**Use these tools. Do not rewrite them.** If one is missing something, say so in the pull request that adds it.

**First-time writer capability:** The Oracle/OTM or its delegated page writer verifies a checkout of the *actual page repository* and executes `python tools/pp_cli.py --help` plus `python tools/pp_cli.py check` there. In this Common module source the script path is `scripts/pp_cli.py`, not `tools/pp_cli.py`; a repository web view cannot execute either command. Mark `PAGE: PENDING / NOT_RUN` if code execution, page repository access or publication readback is unavailable. A builder/reviewer ordinarily leaves native issue/PR/relay evidence for the coordinator and does not run page-writer scripts.

## Who uses it, in which mode

The same files, the same checker and the same page serve both modes. Only a few fields differ.

| | OTM mode (OwnerTeammember coordinates) | Standalone mode (an Oracle coordinates) |
|---|---|---|
| Who writes the data | OTM | the project's Oracle (or its writer agent) |
| How it reaches the page | data-only commit to `main` | branch `pp/<project>-<you>` and a DRAFT PR; Owner merges by default (see progress-page-repo standing go-ahead exception) |
| Where the Owner's replies go | OTM | the Oracle |
| `projects.json` → `mode` | `otm` | `standalone` |
| `index.json` → `rules.coordinator` | `OTM` | the Oracle's name, for example `Oracle` |

Agents never write the page. A coordinator (OTM or the Oracle) writes it from evidence the agents leave on GitHub.
More in [references/MODES.md](references/MODES.md).

## Start in five minutes (a new page)

1. Create a public GitHub repository and turn on Pages (Settings → Pages → Deploy from a branch → `main`, folder `/`).
2. From this module folder, copy the page and the tools into it:
   ```
   python scripts/pp_cli.py bootstrap <folder of the new repo> --repo <owner>/<name> --page https://<owner>.github.io/<name>/
   ```
   This puts the page at the repo root, the tools in `tools/`, `data/projects.json`, a check workflow and `.gitattributes`.
   Use plain `python`, not `python -I`: the tools import each other, and `-I` stops with `ModuleNotFoundError`.

   **From step 3 on you work inside the new repo**, where the tools are in `tools/`. In this module folder they are in `scripts/`.
3. Add the first project (all write commands need `--actor`, `--src` and a reason). `--reply-repo` and `--reply-site` say where the
   Owner's replies arrive; without them `inputs` has nothing to read:
   ```
   python tools/pp_cli.py project add --key demo --title "Demo project" --mode standalone --coordinator "Oracle" \
     --reply-repo <owner>/<name> --reply-site https://<owner>.github.io/<name>/ \
     --aim "<the Owner's aim for the project, at most 400 characters>" \
     --actor "Oracle O2" --src https://github.com/<owner>/<name>/issues/1#issuecomment-<id> \
     --owner-words "<the Owner's words that start it>" --why "<why it starts>"
   ```
4. Describe it, then add agent blocks (`--src` is always the GitHub link of the evidence you read):
   ```
   python tools/pp_cli.py plan chat --project demo --id coder --label "Coder" --id8 6ad8a9bb --engine ChatGPT \
     --actor "Oracle O2" --src https://github.com/<owner>/<name>/issues/1#issuecomment-<id> --summary "Coder chat started"
   python tools/pp_cli.py card set --project demo --card coder --label "Coder" --state IN_PROGRESS --now "Working on PR #5" \
     --next-actor Oracle --next-text "review the PR" --chat coder \
     --actor "Oracle O2" --src https://github.com/<owner>/<name>/pull/5 --summary "Coder opened PR #5"
   ```
5. `python tools/pp_cli.py check` must print `OK`. Commit `data/`, push, open the page.

## Every time something moves

1. Read the evidence on GitHub (comment, commit, PR). Do not copy a claim you did not read.
2. Record it: `card set ... --src <link of that evidence> --summary "<what changed>"`. `updatedAt` is the time of the evidence (`--at`, default now).
3. `python tools/pp_cli.py check` (and `check --base origin/main` before a pull request).
4. Commit `data/` only. The page re-reads the JSON every two minutes.
5. Run `python tools/pp_cli.py inputs --actor "<you>"` for new Owner replies and nudges, then `python tools/pp_cli.py triggers`: it prints what the Owner and you owe (see [references/TRIGGERS.md](references/TRIGGERS.md)). Act on it.

## The commands

`python tools/pp_cli.py [--data data] <command>` (details: `--help`, or the docstring of `pp_cli.py`)

| Command | Use it for |
|---|---|
| `project add / archive / restore / supersede / cancel / transfer` | a whole project (a tab). Archive hides it under "Archived"; nothing is deleted |
| `revision add` | a new **plan revision**, only because an Owner decision changed direction (Owner's words and a link are required) |
| `plan milestone / group / chat` | milestones, groups and chat ids of a project |
| `card set / supersede / cancel / transfer` | agent blocks. Supersede = replaced by another card; cancel = no longer applies; transfer = a successor chat takes over |
| `action add / answer` | decisions for the Owner ("My actions"); answer records the Owner's words |
| `fixture add / remove` | grounding fixtures (ten fixed lists) |
| `nudge add / done / withdraw` | the **Nudge +** queue: instructions the Owner wants the coordinator to fold into its next message to an agent |
| `check [--private] [--base REF]` | the contract; with `--base`, also "the Timeline only grew, nothing was deleted, every change has an entry" |
| `inputs --actor WHO` | the Owner's replies and nudges that arrived as GitHub issues and are not recorded yet, each with the command that records it |
| `triggers [--json]` | needs-you, owes, nudges, quiet agents, waiting agents, stale tab |
| `local OUT [--links F] [--prerender BROWSER]` | one self-contained HTML file for the Owner's machine |
| `links FILE [--page URL]` | a private setup link that makes chat ids clickable in one browser |
| `bootstrap DEST --repo --page` | copy the page and the tools into a new repository |

Every write command records one Timeline entry (who, what, why, source) and runs the checker. If the check fails, **nothing stays written**.

## The rules that matter

- **Public-safe data only.** Chat ids are the short id (8 characters), never a chat link. No Drive, OneDrive or SharePoint links, no email addresses, no tokens. The checker refuses them.
- **Artifact transfer priority (Owner, 25 October 2026):** **Option 1 FIRST** — public-safe, immutable artifact under a task-scoped [Common artifact relay](../ARTIFACT_RELAY.md) payload/authorized GitHub commit; **Option 2 NEXT** — the Owner-designated Google Drive Handoffs root, required for protected files or when public-safe Option 1 cannot be used. **Every completed agent↔Oracle↔reviewer artifact transfer must succeed by 1 or 2.** A `sandbox:`/`/mnt/data` link is a temporary `LOCAL_ONLY / NOT_TRANSFERRED` fallback **not** completed delivery. Public Progress Page fixtures continue to use only the safe `OWNER_PRIVATE_REF:HANDOFFS_PRIMARY` metadata label, not Drive URLs or sensitive child details. The Owner may share the root link directly with assigned recipients; receipt, access, independently measured bytes and review remain separate. Keep an exact task-scoped Common receipt for either transport and follow the selected [local-handover](../local-handover/AGENT_PROTOCOL.md) custody rules.
  Chat links live only in a private file (`links.private.json`), a private local build, or the Owner's browser.
- **Every update is on the Timeline.** Use the tool, never edit `audit.json` or the data files by hand. The Timeline only grows.
- **Nothing is deleted.** Supersede, cancel or archive instead. Superseded and cancelled cards stay on the page, greyed, with the reason.
- **A source for everything.** A card that has started needs a public GitHub link (`--src`) and the time of that event. `OWNER_PRIVATE_REF:<id>` marks evidence only the Owner can open.
- **VERIFIED only on evidence you can link.** Say what you did not check. A count of cards is not a delivery percentage.
- **A revision is added only when an Owner decision changes direction.** Everyday status changes go to the Timeline.
- **The coordinator, not the agent, reads Nudge + lines.** The agent never sees that list.

Field-by-field contract: [references/DATA_CONTRACT.md](references/DATA_CONTRACT.md).

## What each file is

| Path | What | When you touch it |
|---|---|---|
| `viewer/` | the page: `index.html`, ES modules, `viewer.css` | never for data; copied to a repo root by `bootstrap` |
| `scripts/pp_cli.py` | the editing tool (all commands above) | every time |
| `scripts/pp_check.py` (+ `pp_ctx.py`, `pp_check_files.py`, `pp_ledger_check.py`, `pp_history.py`) | the checker | `check`; CI runs it |
| `scripts/pp_ops.py`, `scripts/pp_cards.py`, `scripts/pp_lib.py` | what the commands do; shared rules | only to change the contract |
| `scripts/page_triggers.py` | trigger rules, the same as `viewer/triggers.js` | `triggers` |
| `scripts/build_local.py`, `scripts/static_pass.js` | the single-file local build | `local` |
| `scripts/pp_inputs.py` | reads the Owner's issues (label `owner-input`) and prints the recording command | `inputs` |
| `scripts/pp_links.py`, `scripts/pp_boot.py` | setup link; bootstrap | `links`, `bootstrap` |
| `templates/owner-reply.yml` | the GitHub issue form that carries the Owner's replies and nudges | copy to `.github/ISSUE_TEMPLATE/` of the repo that receives replies |
| `templates/check-progress-data.yml` | CI for a page repository | `bootstrap` installs it |
| `references/` | contract, modes, triggers | when unsure |
| `assets/ORACLE_ONBOARD_PROMPT.md` | paste-ready brief for a new Oracle or writer agent | give it to the agent |
| `examples/data/` | a small valid data folder (projects `demo` and `other`), built by `build_valid()` in `tests/helpers.py` | read it to see real files; `python scripts/pp_cli.py --data examples/data check` prints `OK` |
| `tests/` | seeded-defect tests for the tools (213), using `scripts/`, `viewer/` and `examples/data/`; `bootstrap` does not copy them | `python -B -m unittest discover -s tests` from this module folder only |

## What the Owner sees and does on the page

- **Tabs** per project, `+` to add one (a copy-paste brief for another agent to build it), **Archived (n)** for closed ones.
- **Revisions** row: R1, R2 ... with date and status; click an older one to see the project as it was (from GitHub history); `+` gives the brief for the next revision.
- **Progress**: attention strip (needs you, owes, nudges, quiet, waiting, tab stale), milestone strip, groups of agent blocks.
- **My actions**: decisions with a suggested option first, a copy-ready reply and a "Send" link (a prefilled GitHub issue form; the Owner submits it, so GitHub signs and time-stamps it).
- **Nudge +** on every agent block: add or delete lines for the coordinator; each row later reads "Done by OTM on <time>".
- **Grounding fixtures** and **Timeline** (newest first, with the GitHub source of each entry).

## A local file for the Owner (works offline and in previews)

```
python tools/pp_cli.py local progress-local.html --links links.private.json --prerender "<path to msedge.exe or chrome.exe>"
```
The file embeds the page and a snapshot of `data/`. With scripts on it shows the snapshot at once, then reads the live data. With `--prerender` it also holds a static copy
(expandable sections) that still shows when a viewer blocks scripts. A file built with `--links` holds private chat links: keep it on the Owner's machine, never commit it.
To make chat ids clickable on the public page in one browser: `python tools/pp_links.py links.private.json --page <page url>` prints a setup link; the part after `#` is never sent to a server.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| Page says "Loading..." forever | scripts are blocked (a preview). Use the local file built with `--prerender`, or open the published page |
| An old page after a push | GitHub Pages caches for up to ten minutes; module URLs carry `?v=N`. Bump N in `index.html` and the imports when the viewer changes |
| `check` fails after your edit | read the first line: it names the file, the card and the rule. Fix the cause with the CLI; never patch `audit.json` |
| `revision add` refuses | commit `data/` first so the old revision keeps a commit to open from |
| `--base` complains "no entry" | the data changed without the tool. Redo the change with `pp_cli.py` |
| A chat link was committed | the checker refuses it before a commit; if one got in, remove it in a new commit and tell the Owner (the old commit still holds it). Do not edit the Timeline: add a correcting entry |

**Specific Owner-approved merge exception (25 October 2026):** For PRs **into `reallakshman19/progress-page` only**, an Owner go-ahead to proceed with the scoped draft covers its merge after verifying the exact head, applicable required checks, compatibility and GitHub protection rules; **do not ask for a second Owner approval**. Mark ready and merge when safe; report the actual merge SHA. Keep the PR unmerged on failed tests, missing source, scope drift, unreviewed mandatory gates or conflicts. This exception does not affect Common/other projects, Owner product acceptance or private custody; see [MODES.md](references/MODES.md). No autonomous future merge is implied.

## Related modules

[universal-workflow-progress](../../universal-workflow-progress/SKILL.md) (a read-only progress strip inside a chat; not this page), [Gatekeeper](../gatekeeper/SKILL.md) (labels for deliverables),
[Independent Reviewer](../independent-review/SKILL.md) (a card moves to VERIFIED on its evidence, not on a writer's say-so).
Reference deployment: github.com/reallakshman19/progress-page. The copy of the page in `viewer/` says which commit it came from in `viewer/VERSION`.
Known limit: a local file or preview with no `data/` beside it reads the reference deployment's live data (`LIVE_DATA` in
`viewer/app.js`, `LIVE_PAGE` in `scripts/build_local.py`). For your own page, open it with `?data=https://<owner>.github.io/<name>/data/`.
