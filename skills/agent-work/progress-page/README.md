# Progress page · how to use it (Prototype v0.1, optional Common module)

One static web page that shows, for every project: **milestones**, **agent blocks** (who does what, how long ago it moved, what is next),
the **Owner's decisions** ("My actions"), **grounding fixtures**, a **Timeline** of every update, plan **revisions**, and a **Nudge +** queue per agent.
The data is plain JSON in a GitHub repository; GitHub history is the trace. This folder holds everything needed to run one:
the page, a checker, an editing tool, a trigger tool, a local-file builder, templates and tests.

**Use these tools. Do not rewrite them.** If one is missing something, say so in the pull request that adds it.

## Who uses it, in which mode

The same files, the same checker and the same page serve both modes. Only a few fields differ.

| | OTM mode (OwnerTeammember coordinates) | Standalone mode (an Oracle coordinates) |
|---|---|---|
| Who writes the data | OTM | the project's Oracle (or its writer agent) |
| How it reaches the page | data-only commit to `main` | branch `pp/<project>-<you>` and a DRAFT pull request; the Owner merges |
| Where the Owner's replies go | OTM | the Oracle |
| `projects.json` → `mode` | `otm` | `standalone` |
| `index.json` → `rules.coordinator` | `OTM` | the Oracle's name, for example `Oracle` |

Agents never write the agent blocks, decisions or revisions: a coordinator (OTM or the Oracle) writes those from evidence the agents leave on GitHub.
**Grounding fixtures are the exception: anybody may add one** (an Oracle, an agent, the coordinator), with `fixture add` and their own name as `--actor`, so the Timeline shows who added it.
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

- **Public-safe data only.** Chat ids are the short id (8 characters), never a chat link. No Drive links, no email addresses, no tokens. The checker refuses them.
- **Private files** (ZIPs, banks, originals, source fixtures, candidates) live in the Owner's one common handoff Drive folder, one subfolder per project key. A grounding fixture names the subfolder and file (with its SHA-256), never the link: see [local-handover](../local-handover/AGENT_PROTOCOL.md).
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

## Related modules

[universal-workflow-progress](../../universal-workflow-progress/SKILL.md) (a read-only progress strip inside a chat; not this page), [Gatekeeper](../gatekeeper/SKILL.md) (labels for deliverables),
[Independent Reviewer](../independent-review/SKILL.md) (a card moves to VERIFIED on its evidence, not on a writer's say-so).
Reference deployment: github.com/reallakshman19/progress-page. The copy of the page in `viewer/` says which commit it came from in `viewer/VERSION`.
Known limit: a local file or preview with no `data/` beside it reads the reference deployment's live data (`LIVE_DATA` in
`viewer/app.js`, `LIVE_PAGE` in `scripts/build_local.py`). For your own page, open it with `?data=https://<owner>.github.io/<name>/data/`.
