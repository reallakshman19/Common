# Triggers

The Progress page works out its triggers from the data files alone. The rules are in `triggers.js` (the page) and are copied into `tools/page_triggers.py` (the command line),
so a coordinator can read what the page shows without a browser. A trigger is a chip on an agent block plus a count in the attention strip at the top of the Progress view.
In this file the **coordinator** is the OTM (OwnerTeammember) in `otm` mode, or the project's Oracle in `standalone` mode (`rules.coordinator` in `data/<key>/index.json`).
Run commands from the repository root. The data files are described in [DATA_CONTRACT.md](DATA_CONTRACT.md).
Rules come from `triggers.js` and `tools/page_triggers.py`; the chips and the strip are drawn by `progress.js` and `app.js`. Written on 2026-10-22 from `C:\t\progress-page` at commit 87d0b1f.
If the code changes, the code wins: re-read it and fix this file.

## The eight rules

Age is the whole minutes since the card's `updatedAt` (the time of its evidence); for rule 8, since the nudge line's `at`. Times print as `45m`, `1h 46m`, and from 48 hours as `2d 3h`.
Severity 0 is information (neutral chip), 1 is past the limit (warning chip, amber), 2 is far past it (danger chip, red).

| # | Rule | Fires when | Chip text | Severity |
|---|---|---|---|---|
| 1 | skip | the card's state is `VERIFIED`, `NOT_APPLICABLE` or `NOT_STARTED` | none | rules 2 to 6 do not run for it; rule 8 still can |
| 2 | needs you | `next.actor` is exactly `YOU`, or `flags` has `needs-you` | `needs you · 1h 4m` (no time if `updatedAt` is missing) | 2 |
| 3 | paused | `flags` has `paused`, or the project has `hold.active` true | `paused` | 0 |
| 4 | owes | `next.actor` equals `rules.coordinator` (letter case ignored) and age is at least `owesAfterMin` | `OTM owes · 20m` | 1; 2 from 4 x `owesAfterMin` |
| 5 | quiet | state `IN_PROGRESS` and age at least `quietAfterMin` | `quiet 40m: ping it` | 1; 2 from 2 x `quietAfterMin` |
| 6 | waiting | state `SUBMITTED`, `next.actor` is not `-` and not the coordinator, age at least `waitingAfterMin` | `waiting for REVIEWER · 20m` | 1; 2 from 4 x `waitingAfterMin` |
| 7 | stale tab | the project's `updatedAt` is more than `staleAfterMin` minutes old and there is no hold | strip chip `Tab stale 5h 0m` (else `Tab fresh`) | not a card tag |
| 8 | nudge | the card has open Nudge + lines (`nudges.json`, status `open`) | `2 nudges for OTM · 1h 10m` (age of the oldest line) | 0; 1 from `nudgeAfterMin`; 2 from 4 x `nudgeAfterMin` |

Rules 4 to 6 need an `updatedAt`; without one they do not fire. Rule 8 looks at neither the card's state nor its flags: it fires on a paused card and under a hold.
Chip colours on the page: severity 2 is class `d` (red), 1 is `w` (amber), 0 is `n` (neutral).

## Defaults

The constant `DEFAULTS` in `triggers.js` and in `tools/page_triggers.py` holds these values.

| Setting | Default | Used by | Set in `index.json` |
|---|---|---|---|
| `coordinator` | `OTM` | rule 4 (who owes), the labels "OTM owes" and "Nudges for OTM" | `rules.coordinator` |
| `staleAfterMin` | 120 | rule 7 | `project.staleAfterMin` (required) |
| `quietAfterMin` | 30 | rule 5 | `rules.quietAfterMin` |
| `idleAfterMin` | 15 | no rule reads it (see UNCLEAR) | `rules.idleAfterMin` |
| `owesAfterMin` | 15 | rule 4 | `rules.owesAfterMin` |
| `waitingAfterMin` | 15 | rule 6 | `rules.waitingAfterMin` |
| `nudgeAfterMin` | 15 | rule 8 | `rules.nudgeAfterMin` |

## Which rule wins

A card gets at most one tag from rules 2 to 6. The first that fits wins, in this order: **needs you, paused, owes, quiet, waiting**. Examples:
a card the coordinator owes that is also quiet shows only `owes`; a paused card never shows `owes`; a card that needs the Owner shows only `needs you`, even under a hold.
Rule 8 adds a second chip on top, so one card can show two. Rule 7 belongs to the project, not to a card. There is no special rule for `BLOCKED` (see UNCLEAR).

The strip counts: Needs you, `<coordinator>` owes, Nudges for `<coordinator>` (open lines, not cards), Quiet agents, Waiting on others, then Tab stale or Tab fresh.
Paused cards are not counted. The "!" on a project tab shows when the tab is stale or when owes, quiet, waiting or nudges is above 0; `needs you` alone does not set it.

## Per-project overrides

These sit in `data/<key>/index.json`. Settings merge in this order, the later one wins: built-in defaults, then `project`, then `rules`. A setting left out keeps its default.

```json
"project": { "staleAfterMin": 180 },
"rules":   { "coordinator": "Oracle O2", "quietAfterMin": 45, "owesAfterMin": 10, "waitingAfterMin": 30, "nudgeAfterMin": 10 },
"hold":    { "active": true }
```

- The checker requires `project.staleAfterMin` (whole number, at least 1). It accepts `quietAfterMin`, `idleAfterMin`, `owesAfterMin`, `waitingAfterMin` (whole numbers, at least 1),
  `coordinator` (max 40 characters) and `hold.active` (true or false). It does not check `nudgeAfterMin`, which the page reads.
- `next.actor` must spell the coordinator like `rules.coordinator` (letter case does not matter) for rule 4 to fire. With `"coordinator": "Oracle O2"`, write `Oracle O2`, not `Oracle`.
  `pp_cli.py project add` writes `rules.coordinator` from `--coordinator` (default `Oracle`, not `OTM`) and `mode` from `--mode` (default `standalone`).
- `hold` parks the whole project on purpose. While `hold.active` is true: every card that is not `VERIFIED`, `NOT_APPLICABLE` or `NOT_STARTED` shows `paused`, unless it needs the Owner;
  nudge chips still show; the tab is never stale. No card shows owes, quiet or waiting.
  No `pp_cli.py` command sets or clears `hold`. A hand edit passes `pp_check.py data`, but `--base` then reports a changed project with no new Timeline entry unless the same change also
  records one (see "--base rules" in DATA_CONTRACT.md).

## What each trigger means

The third column is guidance taken from the chip text and from `nudge.js`; the code itself only draws chips and counts. A coordinator acts on a trigger in the turn it sees it.
Commands are shortened: each also takes `--project <key>` and `--actor`, and most take `--src` and a reason (`--summary` or `--why`). `python tools/pp_cli.py card set --help` (and the same for each command) lists them.

| Trigger | What it means | What the coordinator does | CLI command that clears it |
|---|---|---|---|
| needs you | The Owner is the next actor (`next.actor` is `YOU`, or the flag `needs-you`). | Keeps the ask in front of the Owner (a decision card in My actions, made with `action add`). Does not act for the Owner. | After the Owner answers: `action answer` for a decision, then `card set --next-actor <who> --next-text "..."`; add `--no-flags` if the flag was set |
| paused | The card, or the whole project, is parked on purpose. | Nothing for the card. Its nudge lines still count. | `card set --no-flags` (empties all flags of the card). For a project hold: edit `hold.active` by hand |
| owes | The next step is the coordinator's and has waited at least `owesAfterMin`. | Does what `next.text` says (reply, release, review), then records it. | `card set` with a new `--next-actor` and `--next-text`. It also sets `updatedAt`; if the coordinator stays the next actor, the chip returns after `owesAfterMin` |
| quiet | An `IN_PROGRESS` agent has not moved for `quietAfterMin`. | Pings the agent in its chat (`who.chat`) and asks for status. | `card set --now "<status>" --src <evidence>` once the agent answers. `card transfer --to-chat <chat>` if the chat is replaced |
| waiting | A `SUBMITTED` card waits for someone else (`next.actor`, not `-`, not the coordinator). | Chases that actor, or takes the step back. | `card set --state VERIFIED` (or another state), or a new `--next-actor` |
| stale tab | Nothing was recorded for the project for more than `staleAfterMin`. | Reads the evidence of each card and records what changed. | Any write command: each moves `project.updatedAt`, for example `card set`. For a project parked on purpose, use a hold |
| nudge | The Owner queued Nudge + lines for a card. The agent does not read them. | Folds the lines into its own next message to that agent, sends it, then records that it did. | `nudge done --id N1 --by <coordinator> --src <link of the message sent>`. `nudge withdraw` when the Owner took the line back |

## The Python mirror and the page

`tools/page_triggers.py` is a hand copy of `triggers.js`; its docstring names the rules of `triggers.js` as the reference. They share no code: the defaults, the order of the checks,
the severity limits and the time format are written twice and kept equal by hand. Both read the same JSON: `projects.json`, then for each project `index.json`, `cards.json` and `nudges.json`.
The tool reads a folder or an `https://` address. See the result:

```
python tools/pp_cli.py triggers                      one line per project, then one line per chip
python tools/pp_cli.py triggers --json               the same as JSON
python tools/pp_cli.py --data data triggers --now 2026-10-22T10:00:00Z     fix the clock (a UTC time)
python tools/page_triggers.py --data <folder or https://...> [--json] [--now ...]     the same without pp_cli.py
```

In `pp_cli.py`, `--data` goes before `triggers`. Text output: `<label>: tab fresh` (or `tab STALE 5h 0m`) `| needs you N | <coordinator> owes N | nudges N | quiet N | waiting N`,
then `   <card label>: <chip text> -> <next.text>` for each chip. In `--json`, each project has `project`, `label`, `coordinator`, `stale`, `staleFor`, `needsYou`, `owes`, `quiet`,
`waiting`, `nudges` and `items`; each item has `card`, `label`, `tag` (`needs-you`, `paused`, `owes`, `quiet`, `waiting` or `nudge`), `text`, `sev` and `next`.
The page re-reads the JSON every two minutes.

Run side by side on the same data (every rule, with and without a hold), the two gave the same chips and counts except for:
- a closed card with an open nudge line: the tool prints a nudge item; the page draws no chip on that card (both count the line in `nudges`);
- `staleFor` in `--json`: always the minutes since `project.updatedAt`, also when `stale` is false (for example under a hold); the page keeps it only when the tab is stale.

## Archived projects and closed cards

- Archived, superseded and cancelled projects do not trigger. `tools/page_triggers.py` skips them. The page puts no "!" on them (only active tabs get one) and writes "Not updated for ..."
  only for active projects. But when you open such a project, its Progress view still draws the attention strip and the chips: `app.js` and `progress.js` do not check the status there.
- A closed (superseded or cancelled) card has state `NOT_APPLICABLE`, so rule 1 gives it no card tag and the page draws no chip on it. The exception is a nudge line on a closed card:
  `nudge add` accepts it, and the tool lists and counts it (see above).

UNCLEAR:
1. `idleAfterMin` is in the defaults, is checked, and is written by `project add`, but no rule reads it. Is a rule missing, or should the setting go?
2. The header of `triggers.js` says BLOCKED cards "only ever show needs you". The code has no BLOCKED rule: a BLOCKED card whose `next.actor` is the coordinator shows `owes`, and under a hold it shows `paused`. Which is meant?
3. `pp_lib.py` has a `DEFAULT_RULES` without `nudgeAfterMin`, and nothing imports it. The defaults in use are those in `triggers.js` and `tools/page_triggers.py`. Is it dead code?
4. No command sets `hold`. Is a hand edit the intended way?
5. Should a nudge line on a closed card be listed at all? The checker and `nudge add` allow it; the page draws no chip for it but counts it.
