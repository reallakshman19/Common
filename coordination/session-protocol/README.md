# Common Agent Session Protocol (CASP) 1.0.0

**Use now:** manual GitHub exchange. **Not activated:** automatic intake, browser SEND, background workers or schedules.

Aim: coordinate existing agents across projects through portable, traceable messages while preserving each project's authority.

Implementation: [Common #361](https://github.com/reallakshman19/Common/issues/361). Dashboard integration: [#360](https://github.com/reallakshman19/Common/issues/360).

This is an additive interchange contract. It does not replace engineering Relay, coordinator-protocol, WP5's private queue or a project's source, qualification, custody and acceptance rules.

## Start an agent immediately

1. Give the agent a **commit-pinned** link to [AGENT.md](AGENT.md) and its registered session descriptor. Use the candidate PR's full head SHA until an accepted version exists on main. A branch name alone is insufficient for reproducible adoption.
2. Copy [templates/session.json](templates/session.json) into your chosen control repository at `coordination/sessions/<session-id>/session.json`. Fill the placeholders, inspect privacy, and record the actual authority for the assignment. One descriptor describes one provider conversation, with one or more explicit project bindings.
3. Use the offline tool to create/validate a `REQUEST` and render a GitHub comment. Post it on the exact mailbox declared by the selected binding. A manual agent reads that issue when instructed; no workflow or bridge is necessary.
4. The agent checks the live source, registration, authority and previous requests, then posts a correlated `ACK` and `RESULT`. Embed the JSON beneath existing `FOR LA:` / `LA DONE:` prefixes where required. Use `AGENT REQUEST:` / `AGENT REPLY:` elsewhere.
5. A reviewer independently checks the work under the project's rules. The result itself creates no acceptance or progress credit.

```sh
# Python 3.11+, standard library only; commands are offline and never publish.
python coordination/session-protocol/tools/casp.py demo
python coordination/session-protocol/tools/casp.py validate-session path/to/session.json
python coordination/session-protocol/tools/casp.py make-request path/to/session.json --binding binding-id --sender-id registered-sender --text-file instruction.txt --authority-ref actual-source-reference --output request.json
python coordination/session-protocol/tools/casp.py validate-message path/to/request.json --session path/to/session.json
python coordination/session-protocol/tools/casp.py check-request request.json --session path/to/session.json
python coordination/session-protocol/tools/casp.py render path/to/request.json
python coordination/session-protocol/tools/casp.py make-reply request.json --sender-id registered-agent --text-file report.txt --output result.json
python coordination/session-protocol/tools/casp.py correlate result.json --request request.json
python coordination/session-protocol/tools/casp.py render result.json
python -m unittest discover -s coordination/session-protocol/tests -v
```

For an ACK, add `--kind ACK --status RECEIVED` to `make-reply`. These helpers create new files exclusively and never overwrite a pending request. Fill exact candidate/source/fixture/profile and structured evidence before final validation where applicable. `render` emits the existing LA prefixes; other registered consumers may use the neutral prefixes with the same envelope. `extract comment.txt` reads exactly one fenced `casp` block from a saved source body. `check-request` adds current local-clock expiry checks; a live reader separately checks source freshness, authority and holds. `validate-message` is structural/routing validation. Validate historical replies against the archived descriptor, then independently assess their applicability to current work.

`demo` is a fictional two-project/four-session exchange, including two distinct agents of the same provider. Its pass proves local contract checks, **not live delivery**. A template with placeholders must fail validation until completed.

## What is included

| File | Purpose |
|---|---|
| [AGENT.md](AGENT.md) | Short, provider-neutral operating instructions |
| [SPEC.md](SPEC.md) | Normative architecture, identities, lifecycle, concurrency and recovery |
| [INTEGRATION.md](INTEGRATION.md) | GitHub triggers, WP5 and Dash compatibility; migration boundaries |
| [CONFORMANCE.md](CONFORMANCE.md) | Requirements, test coverage and honest readiness levels |
| [BOOTSTRAP.md](BOOTSTRAP.md) | Copyable instructions for any existing agent |
| [schemas/](schemas/) | JSON Schema 2020-12 contracts for sessions, messages and source observations |
| [templates/](templates/) | Session and human-readable request/result starting points |
| [examples/exchange.json](examples/exchange.json) | Sanitized, explicitly fictional cross-provider/cross-project data |
| [tools/casp.py](tools/casp.py) | Offline structural, routing, correlation and duplicate checks |
| [workflow-templates/](workflow-templates/) | Inactive read-only trigger example, requiring a separate intake implementation |

## Privacy and adoption

Reusable specifications and fictional examples belong in public Common. Private prompts, chat routes, personal paths, credentials and transcripts belong in a private control repository/local store. Public work issues may carry explicitly authorized sanitized results. A public descriptor may contain opaque IDs and a null chat ID; do not infer a real conversation from a display name.

Installing/reading this package does not register or activate any existing agent, transfer custody, upgrade a pinned live protocol, wake another agent or resume a scheduler. Manual use is available immediately; live automation needs its own implementation and conformance evidence.
