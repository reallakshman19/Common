# Modes: OTM and standalone

The page, the checker and the tools are the same in both modes. A mode only decides who coordinates, who writes the data,
how it reaches `main`, and who receives the Owner's replies and nudges. In this file the **coordinator** is the OwnerTeammember (OTM) in OTM mode
and the project's Oracle in standalone mode.

| | OTM mode | Standalone mode |
|---|---|---|
| `projects.json` → `mode` | `otm` | `standalone` |
| `index.json` → `rules.coordinator` | `OTM` | the Oracle's name (matched without regard to case) |
| Who writes the data | OTM | the Oracle, or a writer agent the Oracle names |
| How a change reaches `main` | data-only commit | DRAFT pull request from `pp/<project>-<you>`; Owner merge is default except the explicit progress-page repository authorization below |
| `replyTo.target` | `OwnerTeammember` | the Oracle's name |
| `replyTo.repo` | the repository that runs the OTM loop | the project's own repository |
| Trigger labels | "OTM owes", "Nudges for OTM" | "Oracle owes", "Nudges for Oracle" |

**Owner standing go-ahead — `reallakshman19/progress-page` only (25 October 2026):** When the Owner has given go-ahead to proceed with a draft PR in the **`reallakshman19/progress-page` repository**, that go-ahead **also authorizes merging that scoped PR without requesting a second Owner approval**. The authorized contributor/operator must finish the agreed scope, inspect the actual PR diff/head, check current-base mergeability, exact-head required CI/tests and applicable GitHub branch protections, then mark Ready and **merge**. If a required gate fails, source/authority/scope materially changes, or the PR cannot be merged safely, leave it open, state the exact blocker, and repair/review under existing rules; **no waiver, no admin bypass, no fabricated independent PASS**. This authorization is repo-specific: it does not transfer Owner acceptance of product behavior, enable external deployment, approve Common/other repositories, or override native engineering/reviewer/secret-custody rules. A draft go-ahead is not automatic background execution; the merge is an actual, reported GitHub operation. Document the observed merged SHA/readback.

Agents never write the page. They leave evidence on GitHub (a comment, a commit, a pull request). The coordinator reads it and records it.

## The recording loop (both modes)

1. Read the evidence. Do not copy a claim you have not read.
2. `pp_cli.py card set ... --src <link of the evidence> --at <time of the evidence> --summary "<what changed>"`.
3. `pp_cli.py check` (and `check --base origin/main` before a pull request).
4. Commit `data/` only (OTM mode: to `main`; standalone: to the draft pull request).
5. `pp_cli.py triggers`, then act on what it prints before doing anything else.

A coordinator that is also the writer reviews its own record. Label it so: a card is VERIFIED only on evidence a different reader can open and check.

## Owner replies

A decision card offers options. "Send to <coordinator>" opens a prefilled GitHub issue (template `owner-reply.yml`, label `owner-input`).
The Owner ticks "I am the Owner" and submits. GitHub signs and time-stamps the input; that is why it is the channel.

| Issue `type` | Meaning | The coordinator records it with |
|---|---|---|
| `DECISION` | the Owner chose an option of a decision card | `pp_cli.py action answer --key <decision> --text "<reply>" --ref <issue link>` |
| `NUDGE` | one new Nudge + line for one agent block | `pp_cli.py nudge add --card <id> --text "<line>" --by Owner --src <issue link>` |
| `NUDGE-WITHDRAW` | the Owner deleted an open Nudge + line | `pp_cli.py nudge withdraw --id <Nn> --by Owner --src <issue link>` |

`python tools/pp_cli.py inputs --actor "<you>"` lists the Owner's issues that are not recorded yet and prints that command for each (it reads public repositories; set `GITHUB_TOKEN` for private ones).
A reply that matches no open card is shown back to the Owner before anything happens.

## Nudge + wired to the triggers (both modes)

A Nudge + line is an instruction **for the coordinator**, not for the agent. The agent does not read the list.
The coordinator turns it into the next message to that agent, in its own words and under its own protocol, then records that it did.

1. **The Owner adds a line.** The Nudge + button is on every agent block, the Oracle's included. The line stays in the Owner's browser until sent.
   "Send" opens the prefilled issue (`type: NUDGE`, text `<card id>: <line>`).
2. **The coordinator's watcher sees the issue** (a new `owner-input` issue is an Owner page input), `inputs` prints the command, and the coordinator runs `nudge add`. The line is now on the page as "Open since ...".
3. **The trigger fires.** Rule 8 of [TRIGGERS.md](TRIGGERS.md) puts a tag on the block ("2 nudges for OTM · 3m") and counts it in the strip "Nudges for OTM n".
   `pp_cli.py triggers` lists it. The coordinator acts in the same turn it sees the trigger.
4. **The coordinator folds the line into its next message** to that agent, sends it through the normal channel, then runs
   `nudge done --id <Nn> --by <coordinator> --src <link of the message it sent>`. The row now reads "Done by OTM on <time>", with the source.
5. **If it cannot send** (an Owner hold, a conflict with another instruction) it tells the Owner why and leaves the line open. After `nudgeAfterMin` (default 15) the tag turns amber, after four times that red.
6. **The Owner can delete an open line.** That sends `NUDGE-WITHDRAW`; the row stays, struck through: "Withdrawn by Owner on <time>".
7. **Nothing is forwarded blindly.** A line is an instruction to the coordinator. The coordinator stays responsible for what it sends and for any evidence rule that applies to it.

Every step above writes one Timeline entry, so "who asked, who did it, when, on what evidence" is on the page and in git history.

## OTM mode specifics

- OTM's loop reads `pp_cli.py triggers` (or `page_triggers.py --json`) where it used to read a printed board. The same rules, one source.
- Decisions that change direction are recorded in the control record first; then `revision add --owner-words "<quote>" --src <that record>`.
- OTM may commit data-only changes directly. Code or viewer changes go through a pull request.

## Standalone mode specifics

- One writer per project at a time. The open DRAFT pull request `pp/<project>-<name>` is the claim; another agent waits for its merge or its closing. (A convention, not enforced by the checker.)
- The project repository holds `.github/ISSUE_TEMPLATE/owner-reply.yml` (copy it from `templates/`) and `replyTo` points at it, so the Oracle receives the replies.
- The CI workflow runs `pp_check.py data --base origin/<base>` on every pull request. A change without a Timeline entry cannot merge.
- A writer agent works under the Oracle's authority. The Oracle reviews the pull request; the Owner merges it.

## Moving a project between modes

`pp_cli.py project transfer --key <key> --to-coordinator "<name>" [--to-mode standalone|otm] [--reply-target "<name>"] --why ... --actor ... --src ...`
changes the coordinator (and optionally the mode and the reply target) and records it. The project stays active, with its history.
To close a project instead: `project archive`, `project supersede --by <other project>`, or `project cancel`. Nothing is deleted; `project restore` brings it back.
