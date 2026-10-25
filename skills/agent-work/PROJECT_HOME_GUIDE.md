# Oracle project Home — concept, architecture and roadmap reference

**Use with [START HERE](START_HERE.md) and [the five entry process maps](ENTRY_PROCESS_MAPS.md).** The project Oracle curates a **source-backed project understanding**, not merely sources, blockers and a one-line next action. Use the existing project issue, source files, WBS, Progress Page `index.project` and `fixtures`. This is a **reference pattern**, not a new canonical schema, skill, task database, permission or mandatory document for every project.

## Home content contract

| Home section | Oracle must distinguish | Surviving source |
| --- | --- | --- |
| **Owner intent and outcome** | Original Owner words and effective amendments; actual user-visible success and protected decisions | Issue/comment, `index.project.aim` + `aimSrc`; `fixtures.intent` |
| **Project concept note** | WHY the project exists; working product; user journey; important constraints and open hypotheses | Versioned public-safe concept-note document **if produced**, linked in `fixtures.repository` with clear title/status `CONCEPT_NOTE` |
| **Architecture and complex concepts** | Major domain model, component/data flow, key invariants, reason for architecture choices, competing assumptions and diagrams/examples where necessary | Project-native architecture/concept documents in `fixtures.repository` with status/title `ARCHITECTURE_CONCEPT`, `COMPLEX_CONCEPT` or corresponding descriptions |
| **Source and ground fixtures** | Originals, hashes, custody/access, full/partial/synthetic goldens, known meaningful wrong cases, provenance and exposure | `fixtures.inputs` + `fixtures.repository`; private bytes never in public page |
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

## New participant navigation

- **Oracle planning direction:** Home concept/architecture/roadmap → selected WBS → exact task issue and next bounded prompt.
- **Agent execution direction:** assigned issue → WBS source/criterion and original fixtures → Home architecture/roadmap → selected engineering coding and evidence protocol.
- **Standalone active Oracle Cycle:** `Cycle now: https://github.com/reallakshman19/Common/tree/main/oracle-cycles/<project>` for cold chats. This reads the actual active `CURRENT.json` and task, produces an `ORACLE-CYCLE-RECEIPT`, and does not replace native v3.6 own-child evidence.
- **Successor Oracle:** recover Home, exact accepted prototype and fixture custody, then discuss three questions about Owner intent, architecture/complex concept choices and **the next three tasks** before actual authorized control cutover. The discussion is a clarification/alignment exchange, **not a scored context test, independent engineering review or a grant of authority**.

Reference examples are indexed in [REFERENCE_INDEX.md](REFERENCE_INDEX.md); goldens are expected outcomes for synthetic cases, not live project source or proof.
