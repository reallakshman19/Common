# Progress page data contract (v3)

`data/` holds the plain JSON that the Progress page reads. `data/projects.json` lists the projects (one tab each). Each project has a folder
`data/<key>/` with six files: `index.json`, `cards.json`, `actions.json`, `fixtures.json`, `nudges.json` and `audit.json` (the Timeline).
`python tools/pp_check.py data` enforces everything in this file. It prints one line per problem (`<where>: <why>`; `<where>` starts with the file path), then `N problem(s)`, and exits 1;
or it prints `OK` and exits 0. Run commands from the repository root with plain `python` (not `python -I`). Write only with `python tools/pp_cli.py`: each write command
changes the files, adds one Timeline entry, runs the checker, and puts every file back if the check fails. (The Common skill calls the tools folder `scripts/`; the code says `tools/`.)

Rules come from `tools/pp_check.py`, `tools/pp_check_files.py`, `tools/pp_ledger_check.py`, `tools/pp_ctx.py` and `tools/pp_lib.py`; writers from `tools/pp_cli.py`, `tools/pp_ops.py` and `tools/pp_cards.py`;
`--base` from `tools/pp_history.py`. Written on 2026-10-22 from `C:\t\progress-page` at commit 87d0b1f. If the code changes, the code wins: re-read it and fix this file.

Types. **text**: a string; an empty string counts as missing; "max N" is the most characters allowed. **int**: a whole number (not true or false).
**time**: UTC, like `2026-10-22T02:01:25Z`. **source**: `https://github.com/...` or `OWNER_PRIVATE_REF:<id>`. **link**: `https://...` with no space.
`null` counts as missing. The checker ignores fields this file does not list (only fixture list names are checked).
Files are UTF-8 without a byte-order mark: a BOM gives "cannot read JSON" (Windows PowerShell 5.1 `Set-Content -Encoding utf8` adds one). The CLI writes them without.

## data/projects.json

| Field | Type | Required | Rule |
|---|---|---|---|
| `schema` | int | yes | must be 3 |
| `projects` | list | yes | must be a list; it may be empty (a new repository) |
| `site` | object | no | not checked; the page reads `repo`, `page`, `tools`, `guide` from it |
| `key` | text | yes | `^[a-z0-9][a-z0-9-]*$`, unique; the folder `data/<key>/` must exist |
| `label` | text | yes | max 40; the tab name |
| `order` | int | yes | at least 0 |
| `mode` | text | yes | `otm` or `standalone` |
| `replyTo` | object | yes | `kind` is `github-issue` or `none`. For `github-issue`, the texts `repo`, `template`, `target` and `site` are all required (`project add --reply-repo` needs `--reply-site` too) |
| `status` | text | no | `active` (default), `archived`, `superseded` or `cancelled` |
| `statusWhy`, `statusAt`, `statusSrc` | text, time, source | if `status` is not `active` | why, when and source of the closing |
| `supersededBy` | text | if `status` is `superseded` | a project key in this file (the check also accepts the project's own key) |
| `statusBy` | text | no | not checked; `project archive`, `supersede` and `cancel` write it; the page prints it |
| `cycle` (per-project list entry) | object | no | Optional read-only Cycle mapping; the current checker does **not** validate or write it. The viewer requires exact `pageProject` (this Page key), `project` (Common Cycle ID), `scope` (one family `wbs:N`) and `url` (`https://raw.githubusercontent.com/reallakshman19/Common/main/oracle-cycles/PROJECT/CURRENT.json`). It validates the Common current-record identity, `mode=standalone`, activation and `progress_projection.project_key`. Unbound/wrong-scope/unavailable records do not confer an actor or dispatch. A binding must be separately authorized and reviewed under normal Page writer/source custody; do not infer one from matching names. No bindings are seeded in this release. |

## data/<key>/index.json

Top level: `schema` (int, yes, must be 3); `project` (object, yes); `rules` (object, no); `hold` (object, no); `chats` (object, no; chat key to object);
`milestones` (object, yes, not empty); `groups` (object, yes, not empty); `revisions` (list, yes, at least R1). Fields inside them:

| Field | Type | Required | Rule |
|---|---|---|---|
| `project.key` | text | yes | equals the folder name |
| `project.title` | text | yes | max 80 |
| `project.subtitle` | text | no | max 240 |
| `project.updatedAt` | time | yes | not more than 60 s older than the newest Timeline entry |
| `project.updatedBy` | text | yes | max 60 |
| `project.staleAfterMin` | int | yes | at least 1 |
| `project.aim`, `project.aimSrc` | text, https link | yes for an active project | the Owner's aim (at most 400 characters) and its GitHub source; set with `project add --aim` or `project aim` |
| `rules.coordinator` | text | no | max 40; default `OTM` |
| `rules.quietAfterMin`, `idleAfterMin`, `owesAfterMin`, `waitingAfterMin` | int | no | at least 1 |
| `rules.nudgeAfterMin` | int | no | not checked; the page reads it (default 15) |
| `hold.active` | boolean | if `hold` exists | true or false |
| `chats.<k>.label` | text | yes | max 40 |
| `chats.<k>.id8` | text | yes | `^[A-Za-z0-9_-]{4,16}$`: the short chat id, never a link |
| `chats.<k>.engine` | text | no | max 30 |
| `milestones.<k>.order`, `groups.<k>.order` | int | yes | at least 0 |
| `milestones.<k>.name`, `groups.<k>.title` | text | yes | max 80 |
| `revisions[i].id` | text | yes | `R1`, `R2`, ... in order |
| `revisions[i].at` | time | yes | |
| `revisions[i].by` | text | yes | max 60 |
| `revisions[i].why` | text | yes | max 240 |
| `revisions[i].ownerWords` | text | yes | max 400 |
| `revisions[i].src` | source | yes | |
| `revisions[i].status` | text | yes | `current`, `superseded` or `cancelled`; at most one `current`, and it must be the last revision |
| `revisions[i].supersedes` | text | from R2 on | the previous id |
| `revisions[i].commit` | text | no | git sha, 7 to 40 lower-case hex characters; `revision add` sets it on the revision it supersedes (null without git) |

Not checked, but the page shows them: `milestones.<k>.full` (tooltip), `groups.<k>.sub` (line under the title), `groups.<k>.chips` (list of `{t, c}`).
`project add` writes `rules` (the coordinator, quiet 30, idle 15, owes 15, waiting 15), milestones M1 to M4, the group `main` and R1. No command writes `hold`.

## data/<key>/cards.json

An object: card id (`^[A-Za-z0-9][A-Za-z0-9_-]*$`) to card.

| Field | Type | Required | Rule |
|---|---|---|---|
| `order` | int | yes | at least 0 |
| `group` | text | yes | a key of `groups` in `index.json` |
| `milestone` | text | yes | a key of `milestones` in `index.json` |
| `label` | text | yes | max 40 |
| `state` | text | yes | `NOT_STARTED`, `IN_PROGRESS`, `SUBMITTED`, `VERIFIED`, `BLOCKED`, `STALE`, `UNKNOWN`, `NOT_APPLICABLE` |
| `now` | text | yes | max 700; the page turns `[text](https://...)` into a link |
| `next` | object | no | `actor` text (`-` for nobody) and `text` (a string, may be empty) |
| `updatedAt` | time | unless `NOT_STARTED` | time of the evidence |
| `src` | source | unless `NOT_STARTED` | the evidence |
| `who` | object | no | `chat` and `from` must be keys of `chats`; `role` is free text |
| `refs` | list | no | each: `k` (`issue`, `comment` or `pr`), `l` (text, max 60), `u` (link); `s` is free text |
| `edges` | list | no | each: `to` (another card id), `k` (`to`, `back` or `both`) |
| `flags` | list | no | each `paused` or `needs-you` |
| `chips` | list | no | each: `t` (text, max 40), `c` (optional: `n`, `w`, `d` or `s`) |
| `kind` | text | no | look of the block: `done`, `working`, `waiting`, `hold`, `idle` or `gap` |
| `closed` | object | no | `kind` (`superseded` or `cancelled`), `why` (max 240), `at` (time), `src` (source), `by` (a card id; required when superseded). The card's `state` must then be `NOT_APPLICABLE` |

## data/<key>/actions.json

An object: decision key to decision (the Owner's "My actions").

| Field | Type | Required | Rule |
|---|---|---|---|
| `order` | int | yes | at least 0 |
| `status` | text | yes | `open` or `done` |
| `title` | text | yes | max 160 |
| `lead` | text | yes | max 1200 |
| `options` | list | when open | at least one; exactly one has `suggested` true. Every option present needs text `key`, `label`, `body`, `reply` |
| `links` | list | no | each: `l` (text), `u` (link) |
| `tables` | list | no | each: `cols` and `rows`; every row has as many cells as `cols` |
| `answer` | object | when done | `text`, `at` (time), `ref` (source: the public record of the Owner's words) |

## data/<key>/fixtures.json

An object: list name to list of items. Allowed names: `repository`, `issues`, `pullRequests`, `roadmap`, `highRoi`, `future`, `intent`, `inputs`, `knownIssues`, `pending`.
Another name is an error. `{}` is valid. Each item: `t` (text, max 400, required), `u` (link, no), `s` (text, max 40, no), `n` (text, max 40, no).

## data/<key>/nudges.json

`schema` (int, must be 3) and `nudges`: an object whose ids are `N1`, `N2`, ... in order, no gaps.

| Field | Type | Required | Rule |
|---|---|---|---|
| `card` | text | yes | a key of `cards.json` (a closed card is allowed) |
| `text` | text | yes | max 400 |
| `by` | text | yes | max 60 |
| `at` | time | yes | |
| `src` | source | yes | equals the source of the nudge's first Timeline entry |
| `status` | text | yes | `open`, `done` or `withdrawn` |
| `doneBy`, `doneAt`, `doneSrc` | text (max 60), time, source | if `done` | |
| `withdrawnBy`, `withdrawnAt`, `withdrawnSrc` | text (max 60), time, source | if `withdrawn` | |

## data/<key>/audit.json (the Timeline)

Top level: `schema` must be the text `progress-ledger/v3`; `project` must equal the key; `events` is a list, not empty. `baseline_at`, `scope` and `legacy_ledger` are not checked
(`pp_cli.py inputs` reads the earliest `baseline_at` as its default `--since`). Every event has these fields:

| Field | Type | Rule |
|---|---|---|
| `seq` | int | its place in the list, from 1 |
| `id` | text | `<KEY>-R-<seq as 4 digits>`, KEY = project key in capitals (`DEMO-R-0001`) |
| `previous_id` | text | the `id` of the event before; `null` for the first |
| `at` | time | |
| `kind` | text | one of the kinds below |
| `actor` | text | max 60 |
| `summary` | text | max 400 |
| `source` | source | the evidence or the Owner's words |
| `rev` | text | an `id` from `revisions`; never lower than the `rev` of the event before |

An event with a `card` field is checked as a card event, whatever its kind. The third column lists what the checker requires. The CLI also writes `scope: project` on the other project events,
`supersedes` (REVISION from R2), `op` (FIXTURE), `target` (NUDGE: the card id) and `source_at` (`card set --at`); the checker does not look at these.
`pp_cli.py inputs` counts a GitHub issue as recorded when its address is the `source` of any Timeline entry, so record an Owner input with the issue link as `--src` (or `--ref`).
Flags that differ: `action answer` takes `--ref` (the Owner's words) in place of `--src`; `action add` and the three `nudge` commands take no reason flag.

| Kind | On | Required besides the common fields | Written by |
|---|---|---|---|
| BASELINE | card | `card`, `after`; `before` null or absent; the card's first event | `card set` on a new card |
| STATE | card | `card`, `before` (the card's last `after`), `after` different from `before` | `card set --state X` that changes the state |
| UPDATE | card | `card`, `before`, `after`; `after` equals `before` | `card set` with the state unchanged |
| SUPERSEDE | card | `card`, `before`, `after` = `NOT_APPLICABLE`, `to` (a card); the card's last event | `card supersede --by` |
| CANCEL | card | `card`, `before`, `after` = `NOT_APPLICABLE`; the card's last event | `card cancel` |
| TRANSFER | card | `card`, `before`, `after` = `before`, `from`, `to` (both keys of `chats`) | `card transfer --to-chat` |
| REVISION | project | `revision` and `rev` both `R<n>`, the next number | `project add` (R1), `revision add` |
| PLAN | project | `scope`, for example `chat:coder` | `plan milestone`, `plan group`, `plan chat` |
| ARCHIVE | project | project must be active | `project archive` |
| RESTORE | project | project must not be active | `project restore` (see UNCLEAR) |
| SUPERSEDE | project | `to` (the replacing project; any non-empty text passes); project must be active | `project supersede --by` |
| CANCEL | project | project must be active | `project cancel` |
| TRANSFER | project | `to` (not empty; the CLI writes `mode:coordinator`) | `project transfer` |
| ANSWER | decision | `action` (a key of `actions.json`) | `action answer` |
| ACTION | decision | `action` | `action add` |
| FIXTURE | list | `list` (one of the ten fixture lists) | `fixture add`, `fixture remove` |
| NUDGE | nudge | `nudge` (an id of `nudges.json`), `op` (`add`, `done` or `withdraw`) | `nudge add`, `nudge done`, `nudge withdraw` |

## Rules between files

1. Chain: event i has `seq` i, `id` `<KEY>-R-000i` and `previous_id` = the id of event i-1. Events are never changed or removed (`--base`).
2. Every revision in `index.json` has exactly one REVISION event, in order. A project that is not active accepts only RESTORE events.
3. Every card in `cards.json` has events. Its first is BASELINE; each `before` equals the earlier `after`. Nothing follows SUPERSEDE or CANCEL.
4. A card's `state` equals the `after` of its last event, and its `src` equals that event's `source`. Its `updatedAt` may be at most 60 s later than that event's `at`.
5. `closed` exists exactly when the Timeline has SUPERSEDE or CANCEL for the card. A closed card has state `NOT_APPLICABLE` and no later entries. `closed.by` and the event's `to` name a card.
6. If a card has a TRANSFER event, `who.chat` is the `to` of the latest one.
7. A project's `status` in `projects.json` equals what the Timeline says: ARCHIVE gives archived, SUPERSEDE superseded, CANCEL cancelled, RESTORE active.
8. A nudge follows its entries: first `add`, then at most one `done` or `withdraw`. Its `status` is open, done or withdrawn to match the last one.
   Its `src` equals the source of the `add` entry; `doneSrc` or `withdrawnSrc` equals the source of the last entry.
9. A decision with status `done` whose `answer.at` is later than the first Timeline entry needs an ANSWER or ACTION entry for its key.
10. `project.updatedAt` is not more than 60 s older than the newest entry's `at`.
11. Names must exist: `card.group`, `card.milestone`, `who.chat`, `who.from`, `edges[].to`, `closed.by`, `nudge.card`, TRANSFER `from` and `to`, `project.key` = folder name.

## Privacy

- The checker reads the text of every `*.json` file under the data folder and refuses: a Google Drive or Docs link; a OneDrive or SharePoint link (also when hidden by JSON escapes, %-encoding or invisible characters); an email address; a token (`ghp_`, `github_pat_`, `sk-` followed by 20 or more characters);
  a chat link (`chatgpt.com/c/`, `chat.openai.com`, `antigravity.google.com`, `claude.ai/chat/`, `claude.ai/code/`).
- `--private` (`pp_check.py data --private`, `pp_cli.py check --private`) lifts only the chat-link rule, for a private local folder. It never lifts the other rules.
- Chats appear as `id8`, the short id. Chat links belong outside `data/`: in the Owner's browser ("My links") or in a private local build.
- A source field accepts only `https://github.com/...` or `OWNER_PRIVATE_REF:<id>` (capitals, an id, no spaces). Any other address is refused there.
  `OWNER_PRIVATE_REF:<id>` is for evidence only the Owner can open, such as a private message. The whole value is published: use a short label, never the private link.
  The page shows it as plain text, not a link. Source fields: `src`, `source`, `statusSrc`, `answer.ref`, `doneSrc`, `withdrawnSrc`, `closed.src`, `revisions[].src`.
- Other links (`refs[].u`, `links[].u`, fixture `u`) may be any `https://` link, and the scan above still applies to them.

## --base rules

`python tools/pp_check.py data --base origin/main` (or `python tools/pp_cli.py check --base origin/main`) first runs the plain check. If that is clean, it compares the files on disk
with `git show <ref>:<data folder>/...` (`tools/pp_history.py`). A project that is new, or lacks any of the six files at the ref, is skipped. It reports:

- a project of `projects.json` at the ref that is gone ("archive it instead");
- a card, a decision or a nudge that is gone (supersede, cancel or withdraw instead);
- an earlier Timeline entry that was changed or removed: the first entries must be identical, only new ones may follow;
- a revision whose `id`, `at`, `by`, `why`, `ownerWords`, `src` or `supersedes` changed (`status` and `commit` may change);
- a project whose `index`, `cards`, `actions`, `fixtures` or `nudges` file differs but whose Timeline gained no entry. This includes a hand edit of `rules` or `hold`.

Outside a git repository it reports one problem. If the ref is unknown, or `projects.json` is absent at the ref, nothing is compared and it prints `OK`.

## Smallest valid example

These blocks are one folder `data/` and pass `python tools/pp_check.py data` exactly as printed. They follow real `pp_cli.py` output (project add, plan chat, card set, action add,
nudge add), trimmed to the required fields plus one chat, `who` and `next`. Times, sources and ids are examples. Through the CLI, a new card needs `--now`, a new milestone `--name` and `--order`,
a new group `--title` and `--order`, a new chat `--label` and `--id8`: the checker requires those fields.

**data/projects.json**
```json
{"schema": 3, "projects": [
  {"key": "demo", "label": "Demo project", "order": 1, "mode": "otm", "replyTo": {"kind": "none"}}]}
```
**data/demo/index.json**
```json
{"schema": 3,
 "project": {"key": "demo", "title": "Demo project", "updatedAt": "2026-10-22T03:10:00Z", "updatedBy": "OTM", "staleAfterMin": 120},
 "chats": {"coder": {"label": "Coder 1", "id8": "a1b2c3d4"}},
 "milestones": {"M1": {"order": 1, "name": "Build"}},
 "groups": {"main": {"order": 1, "title": "Work"}},
 "revisions": [{"id": "R1", "at": "2026-10-22T03:00:00Z", "by": "OTM", "why": "Owner asked for a demo", "ownerWords": "Start the demo",
                "src": "https://github.com/o/r/issues/1#c1", "status": "current"}]}
```
**data/demo/cards.json**
```json
{"build": {"order": 1, "group": "main", "milestone": "M1", "label": "Build", "state": "IN_PROGRESS", "now": "Building the first stage.",
           "updatedAt": "2026-10-22T03:05:00Z", "src": "https://github.com/o/r/issues/1#c2",
           "who": {"chat": "coder"}, "next": {"actor": "CODER", "text": "Post evidence"}}}
```
**data/demo/actions.json**
```json
{"D1": {"order": 1, "status": "open", "title": "Merge the build?", "lead": "The build is ready for your decision.", "options": [
  {"key": "Yes", "label": "Yes (suggested)", "suggested": true, "body": "Merge it after the review.", "reply": "D1: yes, merge."},
  {"key": "No", "label": "No", "suggested": false, "body": "Hold the merge.", "reply": "D1: no, hold."}]}}
```
**data/demo/fixtures.json**
```json
{"issues": [{"t": "Work order", "u": "https://github.com/o/r/issues/1"}]}
```
**data/demo/nudges.json**
```json
{"schema": 3, "nudges": {"N1": {"card": "build", "text": "Ask for its METER line first", "by": "Owner", "at": "2026-10-22T03:10:00Z",
                                "src": "https://github.com/o/r/issues/1#c4", "status": "open"}}}
```
**data/demo/audit.json**
```json
{"schema": "progress-ledger/v3", "project": "demo", "events": [
 {"seq": 1, "id": "DEMO-R-0001", "previous_id": null, "at": "2026-10-22T03:00:00Z", "kind": "REVISION", "actor": "OTM", "summary": "Owner asked for a demo",
  "source": "https://github.com/o/r/issues/1#c1", "revision": "R1", "scope": "project", "rev": "R1"},
 {"seq": 2, "id": "DEMO-R-0002", "previous_id": "DEMO-R-0001", "at": "2026-10-22T03:01:00Z", "kind": "PLAN", "actor": "OTM", "summary": "Add the coder chat",
  "source": "https://github.com/o/r/issues/1#c1", "scope": "chat:coder", "rev": "R1"},
 {"seq": 3, "id": "DEMO-R-0003", "previous_id": "DEMO-R-0002", "at": "2026-10-22T03:05:00Z", "kind": "BASELINE", "actor": "OTM", "summary": "Card created",
  "source": "https://github.com/o/r/issues/1#c2", "card": "build", "after": "IN_PROGRESS", "rev": "R1"},
 {"seq": 4, "id": "DEMO-R-0004", "previous_id": "DEMO-R-0003", "at": "2026-10-22T03:06:00Z", "kind": "ACTION", "actor": "OTM", "summary": "Decision for the Owner: Merge the build?",
  "source": "https://github.com/o/r/issues/1#c3", "action": "D1", "rev": "R1"},
 {"seq": 5, "id": "DEMO-R-0005", "previous_id": "DEMO-R-0004", "at": "2026-10-22T03:10:00Z", "kind": "NUDGE", "actor": "OTM", "summary": "Nudge for build: Ask for its METER line first",
  "source": "https://github.com/o/r/issues/1#c4", "nudge": "N1", "op": "add", "target": "build", "rev": "R1"}]}
```

UNCLEAR:
1. `project restore` fails as coded. It removes the `status*` fields but leaves `"status": "archived"`, so the check ends "statusWhy is required ... status is archived but the Timeline says active", and nothing is written. Is it meant to set `status` to `active` (or remove it)? A restored state with no `status*` fields and a RESTORE entry passes the check.
2. `project add` leaves an empty `data/<key>/` folder if its check fails; a retry then says the project exists. Is the folder meant to be removed on failure?
3. `--base` with an unknown ref prints `OK` without comparing anything. Is a typo meant to pass?
4. `rules.idleAfterMin` is checked and written by `project add`, but no trigger rule reads it. `rules.nudgeAfterMin` is read by the page but never checked. What are they for?
5. No command writes `hold`. Is hand editing meant (then `--base` demands a recorded entry in the same change)?
6. `supersededBy` may name the project itself although the message says "another project key".
