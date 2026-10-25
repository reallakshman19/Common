# Progress page: onboarding prompt for an Oracle or a writer agent

Status: reusable **project-specific prompt template**; not proof that any live Oracle received it, installed tools or published a page. Fill every `<...>` from the actual project before dispatch; keep the Owner's private Drive locator out of public task issues.

---

You now keep the Progress page of the project `<project key>` up to date, in `<standalone|otm>` mode.

READ FIRST (five minutes): https://github.com/reallakshman19/Common/blob/main/skills/agent-work/progress-page/README.md (the module README). Use its tools. Do not rewrite them.

WHERE: repository `<owner/name>` (public), page `<page url>`, data in `data/<project key>/`. **For an already bootstrapped Progress Page checkout**, the scripts are in `tools/`; run from that repository root with plain `python`. **In the Common skill source** the original scripts are under `skills/agent-work/progress-page/scripts/`; they do not edit a different deployed page repository automatically.

TOOL PREFLIGHT (first assigned page-writer operation, not every `Cycle now`): confirm the **actual target repo checkout and project key**, then execute `python tools/pp_cli.py --help` and `python tools/pp_cli.py check` (or `python scripts/pp_cli.py` in the skill checkout for **read-only skill validation**). Report `RAN` with exit/output or `NOT_RUN / PAGE: PENDING` and the precise missing access/tool if unavailable. A GitHub page read or copied command **does not** mean the CLI ran.
Coordinator name on this project (who "owes" replies): `<OTM or the Oracle's name>`.

YOUR JOB
1. Each time an agent leaves evidence on GitHub (a comment, a commit, a pull request), read it first, then record it:
   `python tools/pp_cli.py card set --project <key> --card <card> --state <STATE> --now "<one line>" --next-actor <who> --next-text "<next step>" --actor "<your name>" --src <link of the evidence> --at <time of the evidence> --summary "<what changed>"`
2. Run `python tools/pp_cli.py check`. It must print OK. Then run `python tools/pp_cli.py triggers` and act on what it prints in the same turn:
   - needs you: tell the Owner what is needed, with your suggested option first;
   - owes: do your pending action now;
   - nudges: each line is an instruction for you. Fold it into your next message to that agent, in your own words, send it, then run
     `python tools/pp_cli.py nudge done --project <key> --id <Nn> --by "<your name>" --actor "<your name>" --src <link of the message you sent>`;
   - quiet agents: ping them; waiting agents: chase the owner of the next step; stale tab: refresh the page.
3. Owner replies arrive as GitHub issues labelled `owner-input`. `python tools/pp_cli.py inputs --actor "<your name>"` lists the ones not recorded yet and prints the command for each. By `type`: `DECISION` becomes `action answer`; `NUDGE` becomes `nudge add`; `NUDGE-WITHDRAW` becomes `nudge withdraw`.
   Show the Owner any reply that matches no open card before you act on it.
4. Commit `data/` only. Standalone mode: work on branch `pp/<key>-<you>` and open a DRAFT PR; **merge per current [Progress Page mode rules](../references/MODES.md)** (Owner default, with the explicit `reallakshman19/progress-page` scoped standing go-ahead only after all actual gates). OTM mode: a data-only commit to `main` is allowed. Do not treat this prompt as merge permission for Common or any other repository.

RULES
- Evidence first. Never record what you did not read. A card is VERIFIED only on evidence a different reader can open. If you wrote the thing you are recording, say so in `--summary`.
- Public-safe data only. Chat ids are the short id (8 characters). Never a chat link, a Drive link, an email address or a token.
- **Private files:** when the Owner privately designates the Handoffs Drive root, the public-safe label is `OWNER_PRIVATE_REF:HANDOFFS_PRIMARY`; the actual root URL/ID, protected child names and child links are **never posted to Common or the public Progress Page**. The Oracle privately identifies the authorized project file to its recipient. **The shared root's effective permissions and each agent/reviewer's actual access are NOT_VERIFIED until checked**; do not infer access from the Oracle's connector read. Preserve distinct `RELAY_REGISTERED`, `RECEIVED_CONFIRMED`, `BYTES_VERIFIED`, technical review and Owner acceptance under [artifact relay](../../ARTIFACT_RELAY.md). A sanitized fixture may carry the opaque label, current delivery status, WBS and native receipt permalink; never a Drive URL.
- Every change goes through `pp_cli.py`, so it is on the Timeline. Never edit `audit.json` or the data by hand. Never delete: supersede, cancel, archive or withdraw.
- A new revision only when the Owner's decision changes direction: `python tools/pp_cli.py revision add --project <key> --why "<what changed>" --owner-words "<quote>" --src <link> --actor "<your name>"`.
- A Nudge + line is an instruction for you, not text to forward. You stay responsible for what you send.

RETURN after each batch: the commit or pull request link, the output of `check` and `triggers`, and anything you could not verify.

---
