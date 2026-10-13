# Coordinator architecture: GitHub messages and provider delivery

Architecture revision: 2026-10-13.1. Runtime remains v3.28/schema2. Read this for CASP, GitHub-first monitoring, cross-provider coordination or automatic intake/delivery. Editing this file starts no coordinator cycle, agent, workflow or timer.

## Responsibilities and current capability

Keep four responsibilities distinct:

| Responsibility | Owner of truth |
|---|---|
| Intended outcome, scope, exclusions, adoption and accepted proof | Existing project authority and the coordinator SQLite aim/evidence register |
| Addressing and request/reply correlation | Pinned CASP contract plus current registered session descriptors |
| Source versions, dispatch intent, uncertainty and provider receipts | Authenticated GitHub observations and coordinator transport records |
| Waking and interacting with an agent | A separately supported provider adapter with observed capabilities |

Capability assessed for the Dash v2 exchange on 2026-10-13; refresh local/provider facts before relying on them:

| Component | Status | Practical limit |
|---|---|---|
| Native v3.28 browser gates, lease and aim/task review helpers | IMPLEMENTED | Their existing ChatGPT probe contract; no generic provider adapter |
| CASP1.0.0 schemas, offline helper and manual instructions | PUBLISHED_DRAFT | Common PR362 at `d9180904af5c6a54c4ea42213af68422087e7da7`; no main adoption implied |
| GitHub source collector for this exchange | LOCAL_IMPLEMENTED | On-demand authenticated reads, ETag/cache and body versions; not a background intake service |
| Actual LA ACK/RESULT followed by independent reviewer ACK/RESULT | OBSERVED_MANUAL | Correlation/support proof; does not accept dashboard engineering outcomes |
| Antigravity UI send | OBSERVED_SUPERVISED | Visible User message/Working plus separate GitHub replies; stable provider message ID unavailable |
| Dash v2 reviewer browser delivery | UNAVAILABLE_IN_CONNECTED_ACCOUNT | Exact mapped URL redirected home; GitHub publication is not a chat Send |
| Automatic durable intake, agent wake-up and delivery | NOT_IMPLEMENTED | Workflow example and protocol documentation do not implement these capabilities |

The shared protocol package is [CASP AGENT.md at the pinned commit](https://github.com/reallakshman19/Common/blob/d9180904af5c6a54c4ea42213af68422087e7da7/coordination/session-protocol/AGENT.md). Load its matching schema/helper only when using CASP. Do not silently adopt a newer revision or copy another installation's policies into this runtime.

## Manual exchange available now

Use existing Owner-selected agents and scope; session registration cannot create engineering custody. A descriptor records observed provider capabilities, complete project/work/lane/assignment/session/binding identities, current revision/generation and aim digest. Keep private chat routes outside public descriptors. Different agents of one provider need distinct bindings.

1. Acquire the existing cycle lease. Read the compact registered mailbox delta. Fetch each new source once; cache full bodies outside the model context with actual repository/comment ID, updated time and raw body digest. A changed/deleted command source needs reconciliation, not a stale cache hit. Full pages or failed reads cannot silently advance a watermark.
2. Validate the pinned CASP envelope against the current binding and existing authority. ACK/RESULT must preserve historical target, expected revision, `reply_to` and request digest. Shared GitHub login or sender-authored IDs do not independently authenticate an agent or human approval. Do not retrofit old unstructured comments with invented correlation.
3. Publish one bounded request and read back its actual source body/digest. Record publication separately from agent wake-up. New IDs are for genuinely new work; retries cannot disguise an unresolved old request.
4. Use an authorized supported delivery surface if available. For a supervised MANUAL provider without native adapter support, record intent before one Send; freshly confirm exact conversation, draft and generation; fill/paste the complete text and read it back. Save actual visible receipt, provider ID or explicit null, and limitations. Do not call native `cycle.py verify` with fabricated IDs or mark a partial UI receipt as strict delivery PASS.
5. Read actual correlated ACK/RESULT through GitHub, independently review applicable artifacts with `aims.py`, then route only the permitted next action. A GitHub reply can establish received/answered request correlation; it cannot retroactively prove a missing UI message ID or exact pre-send hash.

Stop delivery to a generating chat, changed route, unresolved draft, denied action or uncertain send. An exact-text mismatch remains a mismatch even when only line breaks differ; preserve both bodies/digests and use the existing resolution rules. Never resend merely because a tool timed out.

If browser access is missing, preserve the inbox request and identify the one-time connection or provider limitation. Do not repeatedly explore sign-in or make the Owner paste full assignments every iteration. A short manual wake is a temporary fallback; report that it remains manual. Restored sign-in still requires fresh capability/delivery checks.

## Event-driven target architecture — not implemented

The intended flow is:

`GitHub source event -> authenticated admission -> durable queue -> provider wake/delivery -> correlated ACK/RESULT -> coordinator evidence review -> next eligible request`

Implement these as distinct integration slices under applicable project authority:

- **Admission:** a GitHub event is a notification. Re-fetch current repository, mailbox, actor and comment. Validate current descriptor/authority and preserve source body versions. Edited/deleted or conflicting sources invalidate affected pending work; no comment text is executable shell or self-authenticating authority.
- **Queue:** persist admission and dispatch intent before effects; serialize per full project/assignment identity. Retain restart state, pending uncertainty, bounded replay and edit/delete disposition. GitHub concurrency is not a durable queue or a guarantee of FIFO/exactly-once delivery.
- **Provider adapter:** declare MANUAL/INTAKE/DELIVERY separately and prove exact target, current generation, draft handling, one-send behavior, busy handling and receipt reconciliation. An API/CLI session ID cannot substitute for a ChatGPT browser conversation URL. Migrating the reviewer to another runtime requires an explicit handover; never create a replacement agent silently.
- **Coordinator:** wake on actionable newly admitted events, check proof and existing scope, and route a bounded next action. Ordinary source silence needs no model turn or DOM scrape. GitHub cannot itself wake a browser-only conversation without a functioning provider bridge.
- **Pacing and recovery:** bounded retries for transient reads; preserve ambiguous writes; stop on provider content-creation blocks or action-specific denials. Test interrupted publication and missing notifications without duplicate effects. Do not rely on a `GITHUB_TOKEN` write triggering another workflow.

Before activation, demonstrate authenticated intake, wrong-route/old-generation rejection, edited/deleted commands, restart replay, simultaneous workers, busy agents, lost receipts and bounded write behavior. Keep engineering acceptance and merge/deploy controls independent. No new approval ritual is imposed where existing Owner/project authority already covers a step; unsupported capability or protected changes remain explicit.

The current `.yml.example` is outside `.github/workflows` and deliberately inactive. Do not move it into an active workflow or start a worker simply because this architecture is read. Preserve a stopped scheduler; an authorized event-driven installation should not add redundant polling timers.

## Source-contract proof

The Dash v2 Gate1 exchange showed why artifact existence and self-tests need independent checks:

- Match exact installed source/version/hash and the candidate's actual parent/base. A historical passing head or a stale branch cannot satisfy a current-head/fresh-main requirement. Identify private local observations separately from public reproducible evidence.
- Cover fields the source actually reads/writes, nested structures, key formats, enums, present/absent/null/empty semantics, defaults and errors. A list of key families or permissive nested objects is not a complete typed contract. Public examples need explicit synthetic provenance and relative source references.
- Validate the schema independently where needed and use malformed inputs that discriminate meaningful constraints. The published validator accepted cycle0, a numeric map entry, a non-hex identity and a numeric relay record that its own declared schema rejected. Passing original fixtures did not establish validator completeness.
- Verify actual expected source-derived values. Ten-field/row counts did not establish the ten source cells; inspected AC, meter, Aim binding lookup and Next decisions differed. Freeze relevant clock/profile inputs for parity and preserve source-authored judgement text. Do not rewrite engineering semantics to make fixtures pass.
- Compare computed hashes to a versioned expected manifest; printing fresh hashes alone verifies no expected digest. A fixed `LOCAL_VERIFIED` label cannot prove a source the runner never read. Report PASS/FAIL/NOT_RUN with exact applicability and retained contradictions.
- Separate transport success, useful support work, implementation, independent qualification and Owner acceptance. A complete CASP round and a validator exit0 cannot close the dependent product gate.

Observed evidence: [reviewer Gate1 PARTIAL](https://github.com/reallakshman19/Common/issues/360#issuecomment-6145967871), [LA contract/fixture report](https://github.com/reallakshman19/Common/issues/360#issuecomment-6146484778), and [controller findings routed for independent re-review](https://github.com/reallakshman19/Common/issues/360#issuecomment-6146762867). The last item is a review request, not a completed reviewer verdict. Later project state must be fetched from its real records.

## Token and context discipline

Fetch source deltas and compact ledger projections first; retrieve new report/artifact bodies by actual ID once. Refresh DOM at delivery/recovery boundaries and never cache away identity, authority or generation checks. Keep prompts to the request reference, exact correlation and smallest next action; keep full history in durable records.

Label measurements precisely. The observed comparison was27202 characters of full LA accessibility text versus320 characters of an unchanged GitHub brief:98.8% less returned monitoring text. It excluded initialization, substantial proof reviews and send checks; it was not measured billed-token or end-to-end savings. Architecture improvements must retain those limits.
