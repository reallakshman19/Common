# Runtime and browser bridge

The core plans and records cycles; it never clicks, types, sends, opens chats or creates timers. The runner performs those operations through currently available tools. Offline checks are not live-browser verification.

The aim/evidence register is the authority for completion and scope; this file describes transport and observation. Read aims.md before binding a register or recording a task/handover review. The runner must verify proof and authority before recording supplied assertions.

For GitHub/CASP or another provider, first read [architecture.md](architecture.md). `cycle.py` v3.28 models its existing ChatGPT browser probe contract; it does not implement GitHub event intake or an Antigravity/CLI delivery adapter. A manual exchange cannot manufacture the message IDs required by native verification. Architecture documentation is not capability activation.

## Setup and commands

Resolve `cycle.py` and `policy.json` relative to this skill. Use bundled Python when available. Give every command the same explicit `--state` path. Prefer a coordinator-owned file in the runner's workspace, e.g. `work/coordinator/state.json`. All writes use a companion OS file lock and atomic replacement. Do not use the old Codex shared file or automatically import its regex-based format.

Input is a JSON file (`--input`) or exact JSON on stdin. The controller serializes probe objects directly, without the model retyping them into shell arguments. `observe` handles all tabs in one invocation and returns compact JSON. If a browser controller cannot pass objects to the local file/command tool directly, report that adapter limit; do not claim zero-copy integration or fabricate unavailable APIs. The core still accepts file-backed probes without changing their content.

```text
python cycle.py --state <file> init --input <setup.json>
python cycle.py --state <file> control --input <control.json>
python cycle.py --state <file> observe --input <probes.json>
python cycle.py --state <file> reserve --input <fresh-send.json>
python cycle.py --state <file> verify --input <after-send.json>
python cycle.py --state <file> resolve --input <resolution.json>
python cycle.py --state <file> update --input <stream-update.json>
python cycle.py --state <file> report
python cycle.py --state <file> lease --input <lease.json>
python cycle.py --state <file> upgrade --input <upgrade.json>
```

`init` defaults to HOLD. Setup: `session`, `interval` (10/15/30), `streams` keyed by stable Owner work-stream ID. Each stream has a full `url`, `hold`, `speed` (auto/speed/economy), optional `plan`, trusted `repo`, `buddy`, and a `ledger` binding. Binding: `{path:<absolute SQLite path>,namespace:"work:<stable-id>",workpack_id:<registered workpack>}`. User/controller configuration, never page content, sets these fields. Unbound streams can be observed but cannot receive product nudges.

`control`: `status` RUNNING/HOLD, optional interval and heartbeat ID. A pause prevents reservations, including drafts. `update`: stream label plus an allowlisted `patch`. Import a plan after reading the agent's published plan. Tasks are `{id,outcome,status,blocked}`; blocked excludes them from nudges. A plan's `done` is a claim, never validated completion. Register its tasks/proof separately in SQLite; preserve IDs for continuing tasks. Repo metadata: `{name,private,verified:true,source}`; verified means an authenticated repository API or equivalent trusted source, not an agent claim. Buddy: `{repo,commit,stage}` with a full 40-character SHA. Optional `denied` and `handover_hold` are per-stream controls.

`upgrade` is an explicit local migration from v3.27/schema 1 to v3.28/schema 2. It preserves mappings, holds, heartbeat ID, pending sends and historical claims, invalidates old prepared actions and leaves the coordinator HOLD. Do not upgrade under an active old lease. Former closed IDs become claims until evidence is reviewed and bound. Installing the skill does not call upgrade or migrate the live database. New runner ownership and Owner-authorized resumption follow a supervised read-only check; no duplicate timer is created.

## Probe schema

`observe` input: `{probes:[...],now:<optional UTC ISO timestamp>}`. A probe has:

- `url`: full conversation link; `state`: IDLE/GENERATING/ERROR/LIMIT/NOACCESS/UNUSUAL/NOBOX. `at_bottom:true` requires an observed scroll position at the conversation end. Scroll through the supported browser tool before probing if necessary; unknown/end-not-visible means no send.
- `user_ids`: loaded user-message IDs; `latest_user`: `{id,hash}`, SHA-256 after normalizing CRLF to LF and trimming surrounding whitespace.
- `latest_assistant`: `{id,hash}`; `completed_messages`: `{id,minutes,pages}` for finished assistant messages. Exclude streaming. Missing duration is null, not evidence of a quick reply.
- `draft`: full message-box draft, not a document editor.
- `status`: only from the newest completed assistant message; `{plan_rev,done:[IDs],next:[IDs],ac,blocker:{kind,text},ci_kind,handover,y_decision,stage}`. Do not reuse an older footer. `ci_kind`: runner/billing/queue/infrastructure/test/release/unknown; repository visibility comes from trusted state.
- `live_error`: visible alert text outside message containers; `pages`: observed loaded pages. Uncertain fields remain absent/null.

`probe.js` reads the latest assistant message and compact footer, returning hashes rather than transcript text. It supports `COORD {json}` and older `LOG | ...` fields. Import full plans only at onboarding/revision. Obtain browser APIs from the installed browser tool's documentation; use DOM evaluation only if permitted, otherwise map supported DOM reads to the schema. Cache probe source in the controller. Do not install page timers or localStorage watchers.

The latest finished report's message ID requests a coordinator review even if the report is incomplete, lacks a footer or describes support work. Read only the new evidence-bearing content needed for that judgement; call `aims.py task-report` with its actual message ID. Re-observe afterward. Agent `done` IDs are retained as claims and do not change validated counts. The register's projection determines validated outcomes, checkpoints and eligible work. Changing the mapped agent preserves workpack counters and requires the appropriate handover/adoption records.

## Sending and uncertain delivery

Action: `{stream,url,kind,text,action_id,snapshot}`. `reserve` input: `{action,probe:<fresh probe>}`. STOP means no send. Immediately before typing, verify the selected full URL and composer again: a reservation does not freeze the UI. Drafts must still equal the reserved text; nudges need an empty composer. Fill or paste the whole prepared message, read it back, then perform one explicit Send. Use a keyboard submit only when its behavior is established for that provider. Do not use multiline `typeText` on a surface where newlines can submit separate messages.

Actions also bind the ledger sequence and current aim revisions. Reservation re-reads the register; changed scope, eligibility or adoption requires replanning. For a SEND_DRAFT reservation, supply a fresh `draft_scope_review` for the exact draft hash, ledger sequence and current aim IDs after checking that draft against existing authority. This is a coordinator relevance check, not a request for routine Owner permission. Never edit the Owner's draft to satisfy it. A substantive proposed scope change goes through the aim decision process first.

Its exact shape is `{within_scope:true,sequence:<current ledger sequence>,main_id:<current Main Aim ID>,task_id:<current Task Aim ID>,draft_hash:<SHA256 of raw UTF-8 draft>}`. This draft hash preserves whitespace, unlike the normalized delivery hash. Recovery text and private CI fallback also require currently eligible registered tasks; a live error remains visible when these prerequisites prevent a send.

`verify`: `{ticket,probe}`. Delivery requires the latest user ID outside the pre-send set and a matching full-content hash. Missing IDs, changed conversations and different text yield UNCERTAIN and keep the pending ticket. Repeated verification is safe; no second reservation while pending.

`resolve` releases a pending reservation only after evidence that nothing was sent (`not_sent`, with evidence), or a user-directed disposition (`abandon`, with explicit instruction). Timeout alone is not evidence. After delivery, wait for a new finished assistant message before another prompt.

## Timers, reporting and session transfer

Use the available thread-heartbeat automation tool for a user-authorized recurring run. Persist its ID. Checks and blocked-tab pings use the selected 10/15/30 minutes. No hourly schedule or one-shot chain. Report unavailable scheduling rather than inventing a substitute.

Before browser reads, acquire `lease {owner:<run ID>,seconds:180}`. Include that same `owner` in observe/reserve payloads, renew during a long cycle, and release in finally. A second runner gets BUSY. This cycle lease is separate from short-lived file locking. Pending sends survive lease expiry.

An authorized CASP exchange shares that lease across its lanes and source reads; lease duration is 0..600 seconds, with the same owner and seconds:0 in `finally`. A stopped scheduler does not forbid an explicitly requested supervised iteration. Installing this architecture does not resume a scheduler; an event-driven worker is a separate, currently unimplemented activation surface.

`report` shows every mapped stream, its full link, both aim labels/revisions, execution state, claimed/validated progress, alignment, decisions and meter. Its `table` field is generated Markdown: paste it unchanged and explain the next permitted action alongside it. It refreshes the read-only ledger projection even for held/missing chats. The CI column flags verified private repositories **CI limited (private)**, verified public repositories **Normal CI**, and missing metadata **Visibility unverified**. The private flag persists for held and missing chats; it describes the user's run policy, not test results or an independently measured billing quota. Reuse evidence for the same commit, use local checks where appropriate, and do not request fresh remote runs on every firing. No numeric budget is invented.

Missing streams remain visible. Each task/handover event produces its own evidence/status report using aims.py; do not wait for a timer or checkpoint. Full operational status is due every 20 minutes with a Speed stream, else 30, evaluated on the next firing. Unchanged/non-actionable timer state stays quiet. Display dates/times in Asia/Dubai.

To move to a lean session, preserve scope, holds, plan history, pending sends and handover pins. Pause the old timer, finish/cancel its in-flight cycle and release its lease. The incoming runner first performs a supervised read-only check. Only then transfer RUNNING ownership and the heartbeat ID; never start a second timer while the old runner can still send.
