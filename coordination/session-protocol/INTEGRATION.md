# Integration and migration

Baseline inspected: Common `e9a08282b2f75db14b00cf18479c99a7bbfa2a6a`, 2026-10-13. Live records must be refreshed before adoption.

## Reconciliation with existing work

| Existing contract | CASP treatment |
|---|---|
| #360 GitHub bus, `FOR LA:` / `LA DONE:` | Retain issue routes/prefixes; add an exact structured request/reply envelope. No second dashboard implementation. |
| #360 private Owner command destination | Installation selects the private store; this package creates none and publishes no live prompts. |
| WP5 11-part target and five actions | Retain dimensions/actions. CASP uses complete aim digest; null unobserved chat ID cannot enter a real-chat adapter. |
| WP5 SQLite queue/journal/single-flight | Reuse on an installed coordinator. CASP is interchange, not a competing queue or acceptance register. |
| WP5 real SEND inactive / #360 parked | Remains inactive. Manual issue consumption works independently of browser transport. |
| coordinator v3.28 and proposed v3.29 | No silent upgrade. Pin each lane's actual version; map handover states explicitly. |
| Engineering Relay / project issue basis | Keep authority and publication families. Embed CASP beneath required task-publication headers; transport envelopes earn no progress. |
| Existing newest FOR LA convention | Import actual source ID/body and mark unstructured legacy correlation UNKNOWN. Do not retroactively invent IDs/receipts. |
| Stopped AA3 scheduler, held scope | Unchanged. Reading/installing a protocol is not resumption or writer-custody transfer. |

WP5's local single-flight index uses `assignment_id` alone. An adapter MUST establish globally unique assignment IDs in that registry or retain an explicit collision-safe mapping from CASP's `(project_id, assignment_id)`; an unqualified cross-project ID must not be forwarded blindly. CASP's composite request key does not silently change WP5's database schema. Conflicting active writers remain a project ownership problem, not something a session file resolves.

## Provider capability contract

Profiles are independently evidenced, not inferred from a vendor name:

- **MANUAL:** read registered issue, verify source, deduplicate with durable records, act within existing scope, post/read back correlated replies.
- **INTAKE:** authenticated source capture, schema + authority/routing checks, durable admission, bounded replay and edit/delete invalidation. Not implemented by this package.
- **DELIVERY:** fresh exact conversation, draft and generation checks; one send; independent receipt; crash/uncertainty reconciliation. Unsupported until proved for that provider/account/interface.

Claude CLI, ChatGPT/Codex, Antigravity and later providers all use the same manual contract. Provider APIs/UI recipes are replaceable adapters; model changes do not alter message semantics. Two agents of the same provider need distinct session IDs and bindings. An inaccessible browser chat/share URL is not an API endpoint. A capable reader need not be wakeable; quiet/offline is not proof of death.

## GitHub Actions contract

The `.yml.example` template is deliberately outside `.github/workflows`; it cannot activate a workflow. It is a **read-only notification skeleton**, not a working durable intake implementation.

When implementing intake:

1. Workflow code exists on the control repository's default branch. `issue_comment` created/edited/deleted covers issue and PR conversation comments; require exact registered mailbox IDs. Ordinary comments have no command effect.
2. Use trusted repository code with `contents: read` by default; grant narrow writes only to a separately reviewed recorder. Do not check out untrusted PR code with credentials. Read payload as data from `GITHUB_EVENT_PATH`; never interpolate comment text into shell/YAML expressions.
3. Re-fetch the live comment/issue/repository/actor through authenticated provider reads. Capture an immutable source observation and validate the envelope, current binding, existing authority and raw-body digest. No sender-controlled field authenticates its own role.
4. Persist admission atomically to the authorized private recorder before dispatch. Serialize per assignment, compare current revision and generation at each side-effect boundary. GitHub concurrency limits are not a durable queue; replay unprocessed sources after dropped/cancelled runs. Never assume global FIFO.
5. `repository_dispatch` is a notification pointing to a real authorized source, not authority in `client_payload`. `workflow_dispatch` is explicit operator reconciliation. Avoid `schedule`; this protocol needs no heartbeat. Use bounded on-demand replay with overlapping watermarks and stable source IDs.
6. Do not depend on a `GITHUB_TOKEN`-created comment/commit triggering another run. Explicitly orchestrate allowed next steps; deduplicate dispatch loops and retain real provider write counts.
7. Write a queue/admission status only when the recorder confirms it. Missing intake is `NOT_IMPLEMENTED`, missing transport `UNSUPPORTED`, uncertain publication `UNCERTAIN`; never “delivered”.

Install neither a workflow nor a worker into a live project solely because an agent reads this specification. Activation must fall within the existing Owner-authorized work and project controls; no new universal approval ceremony is introduced.

## Rollout and rollback

1. Adopt the pinned manual package in a disposable/authorized assignment; demonstrate request → ACK → RESULT and independent review.
2. Test two different providers, two sessions of the same provider and two projects, with wrong-route negatives. Keep engineering ownership separate.
3. Implement intake as a #360 integration slice; test live actor/source edits, missing notifications, restart and content-write limits before activation.
4. Prove each optional delivery adapter separately. Existing manual routes remain available.

On rollback, stop the new intake/worker, preserve uncertain tickets/events and use the previous pinned protocol/manual route. Do not delete history or resend pending requests. Existing project policy and acceptance records continue to apply.

Primary GitHub references, checked 2026-10-13:
- [Workflow events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- [Triggering workflows and token recursion](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)
- [Concurrency controls](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)
