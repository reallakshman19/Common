# Common Agent-Work / Oracle Continuity — Architecture and difficult logic

**Public-safe source-to-control explanation | 25 October 2026 | Common main source `c3d10bc7...` | Oracle-prepared / SELF_ASSESSED.**
This is the **protocol architecture**, not CAESAR II file architecture and not a claim any specific project has successfully changed Oracle control. Pair with [Owner concept](CONCEPT_NOTE.md), [decisions/falsifiers](ARCHITECTURE_DECISIONS_AND_CHALLENGES.md) and [execution frontier](ORACLE_HANDOVER.md).

## 1. The real system: five different forms of authority, never one green status

```text
 [Owner words / amended user outcome]         [Original inputs / native protocol]
                     \                                  /
                      v                                v
               [Oracle source + decision model / one task]
                                  |
                [Native issue/WBS and assigned executor]
                                  |
    [GitHub task PR/test return] + [Common relay: public bytes or Drive receipt]
                                  |
              [Oracle source and negative-case reconciliation]
                       /                           \
       [CURRENT.json if activated Cycle]       [Progress Page projection]
       one project, revision, tasks,           Home/WBS/fixtures/audit
       receipt IDs, role assignments          via authorized pp_cli only
                       |
             [Next executable task NOW]  ... existing agents continue
                       |
      OPTIONAL [Owner-authorized Oracle cutover transaction]
           old Oracle control → new Oracle epoch+binding
           adopt same worker/reviewer assignments; isolate writers
```

**Distinct trust owners:**
1. **Owner** supplies outcome, changed scope and reserved acceptance/merge decisions.
2. **Project-native source/custody** supplies engineering meaning, data and executable controls; Common never overrides native `AGENTS.md`.
3. **Oracle/OTM** chooses/coordinates tasks and reconciles returns within the *selected* mode, not from a role label alone.
4. **GitHub** records immutable commits, issue receipts and published canonical state; comments do **not** mutate `CURRENT.json`.
5. **Progress Page** displays already reconciled state; it cannot confer authority, retrieve private bytes or certify a source experiment.

Grounding: [Common START_HERE](https://github.com/reallakshman19/Common/blob/c3d10bc7c95bef857f5aa12e2a4270777dcb8709/skills/agent-work/START_HERE.md), [five process maps](https://github.com/reallakshman19/Common/blob/c3d10bc7c95bef857f5aa12e2a4270777dcb8709/skills/agent-work/ENTRY_PROCESS_MAPS.md), [Oracle Continuity §1–3](https://github.com/reallakshman19/Common/blob/c3d10bc7c95bef857f5aa12e2a4270777dcb8709/skills/agent-work/oracle-continuity/PROTOCOL.md), [Oracle Cycle](https://github.com/reallakshman19/Common/blob/c3d10bc7c95bef857f5aa12e2a4270777dcb8709/oracle-cycles/PROTOCOL.md).

## 2. A fresh chat is not a new Oracle

**Identity layers have different lifetimes.** The project/Owner AIM lives across many sessions; tasks live across agent replacements; an individual assignment has recipient, generation, native role and version; the **Oracle control epoch** changes only through authorized succession.

The [oracle-state schema](https://github.com/reallakshman19/Common/blob/c3d10bc7c95bef857f5aa12e2a4270777dcb8709/skills/agent-work/oracle-continuity/oracle-state.schema.json) includes `project`, `control`, `sessions`, `tasks`, `assignments`, `artifacts`, `evidence`, `assessments`, `decisions`, `handovers` and `history`. A new chat may learn the project in read-only mode **without** appearing as an active Oracle session and without changing task IDs or ownership. Do not confuse the general reference state schema with a particular project's activated `oracle-cycles/<slug>/CURRENT.json` format.

The **actual structural validator** is [`skills/agent-work/oracle-continuity/validate.py`](https://github.com/reallakshman19/Common/blob/c3d10bc7c95bef857f5aa12e2a4270777dcb8709/skills/agent-work/oracle-continuity/validate.py):
- Requires exactly **one declared active Oracle** matching `control.oracle_session_id` in the validated reference model, not two concurrently active authors.
- Rejects duplicate IDs/generations, stale active task revisions, overlapping declared write resources and cycles in task dependencies or artifact ancestry.
- Requires actual observed capability witnesses (for example `read_inputs` and `return_artifact`) before a declared assignment becomes active.
- Carries `produced_by`/ancestry into review identity analysis so reviewing one's own derived artifact cannot become independent evidence just by switching agent/chat title.
- Distinguishes immutable historical evidence from the current active decision and command publication preconditions.

**Critical limit:** `validate.py` says it is a **read-only structural/relational validator, not a transaction server**. A state file that says the old Oracle is retired does **not** revoke GitHub write credentials, stop an old chat or authenticate a new reviewer. Actual enforcement belongs to the real permitted publisher/branch/resource isolation. Claim `CUTOVER_ENFORCEMENT_UNKNOWN` if no such mechanism is witnessed.

## 3. Source, assignment, receipt and state chronology

Read an actual active standalone Cycle at `oracle-cycles/<project>/CURRENT.json`, **not a chat transcript**, and bind the following independent facts:
- `main` commit + Cycle revision and activation; one published snapshot (proposed PR head ≠ published `main`).
- Assignment ID and generation; authenticated/verifiable participant binding if available; task's actual WBS/issue and exact candidate.
- Accepted receipt IDs and latest native return permalink; `RETURNED_RECONCILED` means an earlier worker delivered and was reconciled, not that the Oracle should repeat the same assignment.
- Engineering truth: source hashes/custody, tests actually run, negative-case outcomes, version-specific review and outstanding scope.
- `next` must identify one **executable** action/actor, not only “Owner, choose reviewer,” if the Oracle can itself inspect source or route tests.

**Why:** a previously accepted comment can survive while the PR HEAD, original source, actor or permissions change. The [Cycle protocol's delta-only continuation](https://github.com/reallakshman19/Common/blob/c3d10bc7c95bef857f5aa12e2a4270777dcb8709/oracle-cycles/PROTOCOL.md#lightweight-continuation--already-bound-participants) reopens only consequential changed state; it also prohibits re-running completed assignments just to satisfy a stale cycle. One returned native result with no Cycle receipt warrants **idempotent receipt repair**, not replaying engineering.

**Example of stale summary danger (not general Common authority):** At checkpoint, [CIIFR `CURRENT.json`](https://github.com/reallakshman19/Common/blob/c3d10bc7c95bef857f5aa12e2a4270777dcb8709/oracle-cycles/ciifr/CURRENT.json) was revision 4 with both existing G1 assignments `RETURNED_RECONCILED`. The earlier project issue described the G2 workstream as entirely held; the Owner subsequently clarified that Oracle-solvable checks and disjoint work should continue. A documentation interpretation can be corrected without inventing a G2 recipient or incrementing another project's control epoch. The later **unmerged** proposed branch `docs/ciifr-oracle-exec-first-r5-20261025`, if still present, is **NOT** canonical revision 5 until separately merged and read back. The successor must reopen actual `main`.

## 4. Knowledge packet and operational control are two different state machines

```text
  Source-grounded incumbent explanation → durable public-safe four documents
         → first-read successor prompt → successor read-only source reconciliation
         → KNOWLEDGE_CHECKPOINT_PUBLISHED (only after merged/readback)
                                           |
          [Optional, independent authorized control transaction]
    Owner binding + observed successor identity/capability + write isolation
       → exact old revision/epoch precondition (CAS)
       → versioned new Oracle binding + adoption of in-flight worker/IR
       → repository publication + readback + command publisher applies new epoch
       → ORACLE_CONTROL_TRANSFERRED, only when actual enforcement witnessed
```

**Mechanism:** The [command schema](https://github.com/reallakshman19/Common/blob/c3d10bc7c95bef857f5aa12e2a4270777dcb8709/skills/agent-work/oracle-continuity/oracle-command.schema.json) requires `command_id`, `expected_revision`, `expected_oracle_epoch`, `next_state_sha256`, `authority` and `activate_handover` or `publish`. The selected native system must additionally *perform* authenticated compare-and-swap publication and reject stale commands; schema validation by itself cannot do that. At cutover adopt or expressly disposition each active/in-flight coder, reviewer and pending receipt; late predecessor returns are not silently promoted and old agent evidence stays historically valid only for its bounded source/candidate.

**A golden fixture is not an authority fixture:** the immutable [3DC handover reference](https://github.com/reallakshman19/Common/tree/bf02e54e1b453c3206ae366de7d65f41c94ab0d4/relay/AGENT_WORK/3DC-XML-CII/oracle-continuity-20261025/payload) teaches explanatory depth. It does not supply a Common project `CURRENT` control document, a reviewer's identity or a live cutover.

## 5. Artifact transport: why publication, receipt and content correctness are different

Owner-selected transfer priority is fixed by [ARTIFACT_RELAY.md](https://github.com/reallakshman19/Common/blob/c3d10bc7c95bef857f5aa12e2a4270777dcb8709/skills/agent-work/ARTIFACT_RELAY.md):

| State | Public-safe Option 1 | Private/fallback Option 2 | Neither |
|---|---|---|---|
| Bytes | Committed permitted Common relay payload or expressly allowed immutable GitHub bytes | Owner-authorized **Google Drive Handoffs**, not public child URLs | `sandbox:` / `/mnt/data` is local staging only |
| Public record | Common task relay receipt and exact SHA/commit, safe details | Common **sanitized** task relay receipt, opaque reference, per-recipient private custody | Mark `LOCAL_ONLY / NOT_TRANSFERRED` |
| Successful handoff | Intended recipient retrieves exact bytes and independently hashes/checks required contents | Intended recipient is actually permitted, downloads exact bytes and independently verifies | **Not transferred**, even if a user can click a link in this conversation |

**Required invariants:** use **Option 1 or 2** for *any completed artifact transfer*. Producer hash ≠ actual recipient measurement; relay registered ≠ recipient received; recipient received ≠ independent technical approval; independent verdict ≠ Owner acceptance. One immutable artifact can be inspected by multiple reviewers without duplicate upload, but each recipient needs their own witnessed access and digest when that claim is made.

The Owner explicitly approved sharing the root **Handoffs** Drive link with assigned recipients. The public Progress Page still uses the opaque label `OWNER_PRIVATE_REF:HANDOFFS_PRIMARY`; do not expose protected child URLs/bytes. No universal private-permission verification was established by the original folder listing.

## 6. Progress Page is a projection, not the source of state

The authorized Oracle/OTM or designated writer reads the *actual* native issue, candidate and evidence and uses [Progress Page CLI README](https://github.com/reallakshman19/Common/blob/c3d10bc7c95bef857f5aa12e2a4270777dcb8709/skills/agent-work/progress-page/README.md):
- In the **real page repo checkout**, `python tools/pp_cli.py --help`, `python tools/pp_cli.py check`, then `inputs`, `triggers`, `card set`/`fixture add` as appropriate, using actor, source permalink and reason/Timeline.
- In **Common skill source**, scripts live under `skills/agent-work/progress-page/scripts/`, not a magically connected deployed page.
- `PAGE: SYNCED` requires a published/verified state; CLI ability, a GitHub PR and served page freshness are three separate observations.
- A new Oracle does not hand-edit `progress-page/data/` or inherit a general merge grant from another repo. Read the scoped [Progress Page modes](https://github.com/reallakshman19/Common/blob/c3d10bc7c95bef857f5aa12e2a4270777dcb8709/skills/agent-work/progress-page/references/MODES.md).

**Causal trap:** if the Oracle copies a local author's `PASS` straight into a green page while no original user trial or independent contrary case ran, the Owner may prematurely act. Preserve `REPORTED`, `EXECUTED_HERE`, `INDEPENDENTLY_REVIEWED`, `NOT_RUN` and `UNKNOWN` distinctly.

## 7. How the successor should actually debug a continuity gap

1. Locate *one changed consequential fact* (e.g., PR head drift, returned task with stale `next`, local-only source ZIP, unbound reviewer, outdated page).
2. Compare original Owner/engineering source to current canonical state; identify claim, actor, evidence and missing or contradicted observation.
3. **Fix it within existing Oracle authority**: read accessible originals, amend one source/receipt/page proposal, recover durable bytes, or route a specific executor/native test. Do not ask the Owner to repeat the aim or assign a reviewer for an Oracle-executable source read.
4. Isolate only the unsolvable operation: missing credential/input, uncontrolled writer conflict, unavailable environment, actual engineering fault requiring native repair, or Owner-reserved acceptance. Report the attempted remedy and exactly what decision is needed.
5. Keep other safe work moving; publish one corrected reference and source-linked next action. This is not a new five-stage admission system.

## 8. Claims this document does NOT establish

No actual live Oracle cutover, real-browser engineering result, live Progress Page writer run, independent reviewer authentication, private successor download, repository ACL revocation or general project-wide Oracle-control registry was verified in creating this explanatory architecture. A structural CI PASS checks the documents/validator contract **only**, never a real recipient's working understanding or a product's engineering semantics.
