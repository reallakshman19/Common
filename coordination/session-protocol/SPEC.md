# CASP 1.0.0 — normative contract

MUST/SHOULD/MAY describe interoperability requirements. They do not create authority. Wire major versions are incompatible unless a documented adapter proves equivalence. Reject unknown required fields/actions/kinds; do not guess. Pin the implementation and project policy separately.

## 1. Architecture and responsibility

```text
Owner / authorized reviewer / agent
        -> registered GitHub mailbox (durable source)
        -> authenticated observation + admission (manual now; adapter later)
        -> existing assignment executor / coordinator / WP5 queue
        -> correlated ACK / plan / result on registered mailbox
        -> independent project review / authoritative evidence register
        -> derived dashboard / checkpoint
```

Keep these responsibilities separate:

| Layer | Owns | Cannot establish |
|---|---|---|
| Project policy + Owner | Scope, decisions, acceptance and writer authority | Actual test execution merely by declaration |
| Session registry | Approved routing and current binding revision | Qualification or engineering acceptance |
| GitHub source | Authenticated provider metadata and exact posted bytes | Human intent from a shared credential alone |
| Admission/dispatch recorder | Correlation, deduplication, fencing, delivery observations | Task success or agent adoption |
| Executor | Actions and attributed result facts | Independent acceptance of its own result |
| Project evidence register | Applicable reviewed evidence and progress | Unobserved transport or runtime facts |
| Dashboard/checkpoint | Disposable projection with observed time | Authority, delivery or fresh proof |

One engineering responsibility may have many successive sessions. Several independent responsibilities may belong to one programme. One session may bind to several projects, but every message selects exactly one binding. Never infer topology from agent count. Concurrency across projects is permitted within each project's existing writer rules; overlapping material writers require an independently proven ownership/fencing mechanism.

## 2. Identity

`session_id` identifies one provider conversation/lifecycle, globally unique within the control plane. `agent_id` identifies its logical registered executor. `provider.kind` is an open slug (`claude`, `chatgpt`, `codex`, `antigravity`, etc.), not a closed vendor allowlist. `provider.instance_id` distinguishes accounts/instances. `chat_id` may be null when not observed; such a binding cannot use a chat adapter requiring it.

Each binding contains the existing WP5 target dimensions:

```text
project_id, work_id, lane_id, assignment_id, run_id, binding_id,
coordinator_id, session_id, chat_id, binding_generation, expected_label_sha
```

CASP requires full 64-hex SHA-256 aim-contract digests for new bindings. Legacy WP5 short labels remain historical and require an explicit mapping; never pad or invent a digest. The target is compared field-for-field. Repository binding additionally includes GitHub's immutable numeric repository ID, current `owner/name`, and an exact mailbox repository ID/name + issue number. Renames/moves require reconciliation; names alone cannot redirect a binding. PR conversation mailboxes are allowed only when explicitly registered.

`revision` is the session descriptor's optimistic-concurrency revision. `binding_generation` fences reassignment of a route; `run_id` identifies the current execution attempt. Rebind, account/conversation change, custody transfer or changed assignment contract requires a new descriptor revision and appropriate generation/run changes. A metadata revision cannot authorize a custody transition; retain its actual authority reference. Retire old sessions and retain their history.

The target and descriptor revision are checked at admission **and immediately before side effects**. Authorization, source freshness, candidate applicability and holds are fresh observations. An old structurally valid message is not sufficient.

## 3. Storage

```text
coordination/sessions/<session-id>/
  session.json                # small current routing descriptor, versioned by Git
  events/<event-id>.json       # append-only observed source/admission/receipt facts
  checkpoint.md              # derived brief with refs and observed time
```

Use one file per event; multiple agents must not overwrite a shared conversation/status JSON. A single authorized recorder per mailbox/assignment owns serialized admission. GitHub is the durable source exchange; existing SQLite/chain records remain authoritative for engineering aims, decisions, reviews and custody. Persist a verified source/body before execution. A checkpoint is a convenience, not a second ledger.

Public Common contains the protocol and sanitized fixtures only. Put private source bodies and routing metadata in a private store. Git history is not immutable against an administrator: use append-only recorder permissions and history/integrity audits; SHA digests detect change but do not authenticate a signer. Never publish secrets even in a later-deleted comment or commit. Control-repository selection is an installation choice, not hardcoded to Common.

## 4. Wire envelope

Messages are UTF-8 JSON, one envelope per comment, capped at 32 KiB. Preserve exact raw source bytes and hash them separately. `message_id` is a new UUID for each authored message; `request_id` is the original request UUID across ACK/PLAN/RESULT/REVIEW. `reply_to` is null for REQUEST and the original REQUEST's message ID for its direct responses. `request_digest` in a response is the SHA-256 of the REQUEST's canonical envelope. `expected_revision` is the descriptor revision at request admission. Responses retain that historical value even after rebind; current applicability is reviewed separately.

Canonical JSON for this v1 subset: object keys sorted lexicographically by Unicode code point, no insignificant whitespace, UTF-8 unescaped Unicode, no floats/NaN, no duplicate keys or lone surrogate code points; integers are limited to ±9007199254740991. LF/CRLF normalization or whitespace changes to **source text** must never be reported as a strict raw-byte hash match. Use the supplied implementation/test vector or an equivalent implementation; this is not a claim of general RFC 8785 support.

Kinds: `REQUEST`, `ACK`, `PLAN`, `RESULT`, `REVIEW`, `INVALIDATION`. Actions retain WP5's five typed actions: `DIRECTIVE`, `DECISION_RESOLVE`, `RECON_MODE`, `PAUSE_WORK`, `RESUME_WORK`. `payload.text` is lossless human instruction/report text. `payload.refs` contains supporting references. A decision request must carry its real card ID and outcome; a generic directive cannot smuggle merge/release or governance approval. Sources and policies decide authority, not a keyword scanner.

REQUEST has `status: REQUESTED`; ACK uses RECEIVED/BLOCKED/REJECTED; PLAN uses PROPOSED; RESULT uses REPORTED/BLOCKED/FAILED; REVIEW uses ACCEPTED/REJECTED; INVALIDATION uses INVALIDATED. These are **message claims**, not delivery-queue states or engineering progress. Evidence entries carry criterion, candidate, fixture/profile references, observed outcome and proof reference. Outcomes include PASS, FAIL, NOT_RUN, NOT_OBSERVED and BLOCKED; PASS is never implied by a result's publication.

`basis` records nullable exact candidate SHA and named source/fixture/profile references. Unknown is null/empty, never guessed. Applicable source/fixture/preparation/tolerance identity remains required by the project even if CASP syntax allows an unknown value.

## 5. Authentication and source observations

An envelope's `sender_id` is an attributed claim. A trusted reader captures provider-observed repository ID, issue/comment IDs, actual actor ID/login, creation/update times, exact raw-body hash, and envelope digest in a separate source observation. Admission binds those facts to the approved source/target. The observation JSON schema validates structure only; arbitrary JSON is not authenticated observation.

Require verified Owner/delegate authority for commands changing scope/custody/decisions. Ordinary agent-to-agent requests require an existing delegated scope, the registered source identity and an allowed recipient. A robot using the Owner's GitHub credential cannot self-authenticate as a human. Use separate identities or an independently verified Owner instruction record. `repository_dispatch.client_payload.actor`, comments quoting an Owner, bot status and collaborator labels are untrusted claims.

## 6. Correlation, deduplication and ordered effects

Durable request key: `(project_id, assignment_id, request_id)`. Store canonical request digest plus source location/raw hash, protocol pin, full target and admitted revision. Same key + same bytes/digest means replay; return the existing record. Same key + changed content/source/target means CONFLICT; do not overwrite. Duplicate message IDs with different content also conflict. Repeated identical work under a **new** request ID still requires policy review if an existing request is active; UUIDs do not bypass single-flight.

An ACK/RESULT must match request ID, reply_to, target, historical revision and request digest. There can be successive reports; record all unique messages and invalidate/supersede explicitly. Do not select acceptance from newest arrival time. Timestamps and GitHub workflow order are not a total authority order. The recorder assigns a monotonic per-assignment sequence with compare-and-swap; unrelated assignments can proceed independently.

Before automated dispatch, reuse WP5 admission and immediately-pre-send checks where available. Persist a single-flight attempt token and monotonic fencing generation. Expired leases allow reconciliation, never automatic resend after a possible side effect. A stale worker must be rejected before publication/delivery; adapters unable to fence side effects must use one supervised sender and remain manual. No generic exactly-once guarantee is made.

Single-flight is required on **both** the assignment and the actual destination conversation. One session with several project bindings still has one composer/execution stream. Serialize its sends/consumption across those bindings; use a consistent lock order for assignment and session fences. An uncertain send holds the destination session as well as the affected assignment until reconciled. Independent projects may continue on other sessions; this shared-conversation hold does not revoke their engineering authority.

STOP/hold commands are priority control observations: apply the existing control immediately, record them even when ordinary work is active, and stop before the next side effect. They do not silently withdraw an already-sent instruction or erase history. Resume requires the applicable live authority and resolution of uncertain effects; timeout/lease expiry is not permission.

## 7. Edits, deletes, interruption and rate limits

Snapshot initial source identity/digest. Edits/deletes generate append-only invalidation facts. Before execution, a changed/unavailable source blocks that request; request a new revision with a new request ID. After execution, mark the receipt historical/invalidated, preserve effects and evidence, and reconcile; do not claim the work never happened. A deleted source cannot be reconstructed from a projection alone. Missing webhook history requires an explicit UNKNOWN interval, not invented edit history.

After crash, rebuild from durable records and observe actual side effects. If delivery/publication may have happened, classify UNCERTAIN, hold conflicting writes and search the registered destination for the correlation ID and exact digest. Record real observed provider IDs, or null when unavailable. Never generate both sides of a delivery receipt in the sender. A queued request, UI draft, ACK and accepted engineering result are distinct states.

For GitHub content writes: persist the intent before the attempt, then exact returned ID/digest/readback. Reconcile unknown outcomes before retry. Respect Retry-After/reset headers; bounded attempts/backoff and a durable next-attempt time are required. Stop on content-creation 403, unexpected writes or technical doubt; 429 is rate-limited, not a transport PASS. A restarted process must not reset retry counters or republish a completed comment. No polling schedule is required by this contract.

## 8. Continuity and privacy

A brief references Main/Task Aim revisions, current exact candidate, completed evidence, unresolved failures, parked work, authority decisions, uncertain deliveries, next permitted action and stopped workers. Carry original source/receipt hashes and issue/PR links. It may summarize an existing register but cannot invent or reset qualification, counters or historical decisions.

Agent sessions can operate from a public work issue when the exchanged data is explicitly public. Private control requires a private mailbox and private event store. Public export is allowlisted and read-only. Never expose personal-machine control endpoints, tokens, private routes or logs through a public dashboard. All scopes are per binding; a grant on Project A never extends to Project B.
