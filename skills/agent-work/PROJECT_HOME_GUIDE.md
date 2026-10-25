# Oracle project Home — concept, architecture and roadmap reference

**Documentation navigation:** [START HERE — role/mode entry](START_HERE.md) · [Entry process maps A–E](ENTRY_PROCESS_MAPS.md) · [Project Home and fixture custody](PROJECT_HOME_GUIDE.md) · [Extended operating reference](OPERATING_GUIDE.md). Read only the branch relevant to your current task; these are not four compulsory stages.

**Use with [START HERE](START_HERE.md) and [the five entry process maps](ENTRY_PROCESS_MAPS.md).** The project Oracle curates a **source-backed project understanding**, not merely sources, blockers and a one-line next action. Use the existing project issue, source files, WBS, Progress Page `index.project` and `fixtures`. This is a **reference pattern**, not a new canonical schema, skill, task database, permission or mandatory document for every project.

## Home content contract

| Home section | Oracle must distinguish | Surviving source |
| --- | --- | --- |
| **Owner intent and outcome** | Original Owner words and effective amendments; actual user-visible success and protected decisions | Issue/comment, `index.project.aim` + `aimSrc`; `fixtures.intent` |
| **Project concept note** | WHY the project exists; working product; user journey; important constraints and open hypotheses | Versioned public-safe concept-note document **if produced**, linked in `fixtures.repository` with clear title/status `CONCEPT_NOTE` |
| **Architecture and complex concepts** | Major domain model, component/data flow, key invariants, reason for architecture choices, competing assumptions and diagrams/examples where necessary | Project-native architecture/concept documents in `fixtures.repository` with status/title `ARCHITECTURE_CONCEPT`, `COMPLEX_CONCEPT` or corresponding descriptions |
| **Source and ground fixtures** | Originals, hashes, custody/access, full/partial/synthetic goldens, known meaningful wrong cases, provenance and exposure | `fixtures.inputs` + `fixtures.repository`; private bytes never in public page |
| **Original agent inputs and returned artifacts** | **Common/relay preferred**: task-scoped public-safe register/payload, source/WBS and receiver, exact version, reported producer digest versus **observed receiver bytes**, receipt and next operation. Google Drive only fallback for restricted bytes or unavailable public payload transport; public relay receipt remains preferred. | `fixtures.inputs` / `fixtures.repository` source-linked to [Common relay](../../relay/AGENT_WORK/README.md) and [artifact relay contract](ARTIFACT_RELAY.md); current WBS/issue is still task authority |
| **Roadmap and WBS** | Outcomes, existing milestone hierarchy, dependencies, current runnable slice, next **three connected tasks**, HOLDs and deferred work | `index.milestones`, `fixtures.roadmap`, native source issue and task cards |
| **Current work, blockers and decisions** | Actual participant/next action, exact candidate, reviewed vs self-reported evidence and remaining decisions | `cards`, `fixtures.knownIssues`, `fixtures.pending`, `fixtures.intent`, audit Timeline |

**Do not invent concept notes.** If a concept or architecture artifact does not exist, Home should say **Not recorded**. Oracle can write a bounded, source-grounded explanation as an authorized contributor (SELF_ASSESSED), request Owner clarification where consequential, and link it. A text-only `fixtures` row can describe a concept when the permitted source is short; prefer a versioned document for long technical architecture and public-safe images/diagrams. Never place private fixture bytes, full private folder links or unsupported acceptance claims in Home.

## Source-grounded project concept-note outline

Use only the sections appropriate to this project's actual complexity:

1. **Owner aim and intended user:** exact current words, amendments, observable user outcome, source link.
2. **Current working reality:** what runs now (URL/command, exact candidate and supported trial); what is historical, partial or NOT_RUN.
3. **Scope / guardrails:** protected source files/data, frozen baselines, allowed changes, excluded tasks and Owner decisions.
4. **System concept:** how original inputs become outputs, user interaction and operating environment, with traceable example where safe.
5. **Architecture / complex model:** components, ownership, important state transitions, data identity/invariants, source-of-truth, relevant diagrams; why chosen.
6. **Assumptions and contrasts:** unresolved scientific/engineering/domain premises, alternate designs, plausible surviving wrong cases and discrimination.
7. **Original fixtures:** precise public-safe identity, hashing and custody conditions, negative/golden/reference separation, accessible locator status.
8. **Roadmap / WBS:** completed vs accepted vs pending, dependency sequence, **next three useful tasks**, first actor, runnable next deliverable and evidence.
9. **Current operational binding:** governing OTM/standalone coordinator, Cycle activation if applicable, native issue/PR, current agent assignment and continuity risks.
10. **Sources and update record:** who prepared it, when, checked native inputs, review/exposure, current vs superseded versions.

## How Oracle maintains Home without a new tracker

1. Update the project-native concept/architecture source at its **actually authorized** location, preserving source URLs and exact candidate or revision; document uncertainty rather than claiming acceptance.
2. Add one or more **existing grounding fixture entries** via the installed Progress Page's native `pp_cli.py fixture add` and source-linked Timeline, using `--list repository`, `--status CONCEPT_NOTE` / `ARCHITECTURE_CONCEPT`, a clear `--text`, a safe `--url`, `--actor`, `--src` and `--summary` as accepted by that repository's CLI. Record roadmap entries under existing `roadmap` and Owner decisions under `intent`; do not hand-edit audit JSON.
3. Verify actual Home readback of the cited document, architecture reference, **full roadmap** and ground source link. A missing link is not a checked source; a recorded claim is not a quality PASS.
4. Only the actual **Progress Page coordinator** writes data: OTM in OTM mode, Oracle (or its nominated writer) in standalone, with the selected mode's review/merge route. If other roles prepare material, Oracle reconciles before page projection.

## Fixture maintenance and Oracle↔agent artifact exchange

**Common GitHub relay is the preferred durable Oracle↔agent exchange**: [Common `relay/`](../../relay/) → [`relay/AGENT_WORK/`](../../relay/AGENT_WORK/README.md), or an existing task register already created under `relay/`. Follow [ARTIFACT_RELAY.md](ARTIFACT_RELAY.md). The current Progress Page Home/Grounding Fixtures must let a new participant locate **the actual current input record**, not merely the project repository or a producer's claim. **Drive is fallback/private custody**, never an excuse to publish protected bytes or child-file URLs in public GitHub. A sanitized relay record still describes the protected handoff wherever feasible.

**Oracle-maintained loop:** identify source fixture and WBS/issue → record producer and receiving role, task-scoped relay register URL and published commit, public-safe version/size/digest, measured receiver verification status (or `NOT_RUN`), actual access limitation, expected return → project this **single authoritative source** in existing `fixtures.inputs` or `fixtures.repository` with a clear `ARTIFACT_RELAY` / `AGENT_INPUT` / `RELAY_RETURN` status/title and related milestone → recipient follows issue → WBS → Home → relay receipt and verifies actual permitted bytes → agent returns a new exact artifact via the same Common relay route → Oracle reconciles and updates existing Progress Page fixture/WBS records via `pp_cli.py fixture add` and its audited source/Timestamp. On branch/PR-only proposals show **PROPOSED/NOT_DELIVERED**, never `BYTES_VERIFIED`; the recorded receiver test is separate from publication.

- **Public-safe file:** authorize and publish actual immutable bytes under the task's `payload/`; the source-linked receipt points to the exact commit and file, not `main` without an immutable revision.
- **Confidential file:** private bytes live only in Owner-authorized private handoff storage such as Google Drive; publish only a sanitized `receipt.md` with no sensitive path, filename, customer information or digest when those are restricted. A fallback private file is **not delivered** until the assigned receiver actually retrieves and checks it.
- **Missing/unavailable route:** retain the source record as `BLOCKED` / `LOCAL_ONLY` / `NOT_RUN` (or the precise current native status), identify the custodian and smallest remedy. Do not say that an in-chat upload or `sandbox:` URI is reusable by new agents.
- **Technical meaning:** `RELAY_REGISTERED`, `RECEIVED_CONFIRMED`, `BYTES_VERIFIED`, an agent's technical result, independent review and Owner acceptance are separate. Progress Page is a read-only projection, not a file transfer service or the GitHub Cycle `CURRENT.json` source of assignments.

**Home display check:** inspect actual project Home and Grounding Fixtures: is the **WBS-relevant input relay record** visible with public-safe status and linked source? Can a cold successor find its current candidate and expected return? If no item has been recorded, the viewer should say that explicitly. Do not populate a demonstration record with an invented real project's bytes.

## New participant navigation

- **Oracle planning direction:** Home concept/architecture/roadmap → selected WBS → exact task issue and next bounded prompt.
- **Agent execution direction:** assigned issue → WBS source/criterion and original fixtures → Home architecture/roadmap → **current Common relay input + actual byte/access verification** → selected engineering coding and evidence protocol; return outputs through the task-scoped relay record.
- **Standalone active Oracle Cycle:** `Cycle now: https://github.com/reallakshman19/Common/tree/main/oracle-cycles/<project>` for cold chats. **If active and assigned**, the participant performs authorized work and returns a Cycle receipt linking its native task evidence; an unassigned recipient says `NO ACTION` and an inactive Cycle says `NOT ACTIVE`. A trigger by itself implies neither execution nor engineering PASS; v3.6 own-child evidence remains separate.
- **Routine continuation (established bound chat):** `Cycle now` refreshes [the canonical assignment and relevant evidence](../../oracle-cycles/PROTOCOL.md#lightweight-continuation--already-bound-participants), **not** full initial onboarding. Reuse unchanged valid conceptual grounding; recheck affected original bytes, current access/authority, candidate or contradictory observations when consequential. Oracle supplies the bounded current task; agent uses assigned **issue → WBS → Home as needed**, with exact [Common relay](ARTIFACT_RELAY.md) input/return. An already-returned task with no new authority awaits Oracle reconciliation; a missing receipt uses existing idempotent repair. The Cycle envelope **links native evidence**, never duplicates engineering test logs or self-check reports.
- **Successor Oracle:** recover Home, exact accepted prototype and fixture custody, then discuss three questions about Owner intent, architecture/complex concept choices and **the next three tasks** before actual authorized control cutover. The discussion is a clarification/alignment exchange, **not a scored context test, independent engineering review or a grant of authority**.

Reference examples are indexed in [REFERENCE_INDEX.md](REFERENCE_INDEX.md); goldens are expected outcomes for synthetic cases, not live project source or proof.
