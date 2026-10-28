# #822 — R2 journal → R1 graph lineage bridge (read-only)

Governing [#787](https://github.com/reallaksh19/Common/issues/787), [reconciled plan](https://github.com/reallaksh19/Common/issues/787#issuecomment-6065671746), and bounded implementation [#822](https://github.com/reallaksh19/Common/issues/822). Built on real merged R1 `provenance-v1.mjs`, R2-A `session-journal-v1.mjs`, R2-B1 `session-bundle-v1.mjs`, base `main@28841b5cfed9e9b6057a1a6f09090adcc512e1b8`.

## API, truth boundary and data loss

`projectLocalJournal(folder,seed,ownerPromptBindings)` replays actual R2-A `readJournal()` before projection. `projectPortableJournal(bytes,expected,seed,ownerPromptBindings)` calls actual R2-B1 `verifyPortableJournal()` (which itself runs R2-A readJournal on fresh disk) first. The *caller* supplies an untrusted, prevalidated structural R1 seed (OwnerIntents/claims/responsibilities; empty sessions and task_evidence) and explicit `[{event_id,intent_id}]` bindings. For PUBLIC OWNER_PROMPT, exact text **and** original-source identity must equal the declared seed, and that OwnerIntent must belong to one of the owning responsibility's acceptance claims; a missing/cross-claim binding, altered prompt or digest-only Owner prompt is refused. A matching structural claim is NOT a human source authentication.

The bridge projects actual R2 session IDs/actors/responsibilities and R1-compatible events, and projects TASK_EVIDENCE_START / END / RECOVERY_START to R1 `task_evidence[]` while preserving original event ID, prior-evidence link and changed files in `evidence_links` and `event_links`. Since R1 does not support DEVIATION as an event kind, it is preserved in a separate typed `deviations[]` sidecar with `UNADOPTED_PRODUCER_ASSERTION` and never silently renamed an adopted DECISION. R1 cannot express a session with only DEVIATION/evidence, nor raw text from a REDACTED Owner prompt; such inputs fail closed rather than synthesize evidence. END changed file without prior same-session CODE_CHANGE fails closed; R2 itself does not impose that relationship. REDACTED non-Owner content projects as an explicit `REDACTED_SHA256:` marker, **never original bytes**. The sidecars allow subsequent provenance schema enrichment without losing R2 identities and distinctions.

The resulting R1 document is checked using the real merged `validate()`; the exported `claim_traces`, `evidence_traces`, and `module_traces` come from the actual `traceClaim()`, `traceEvidence()`, and `traceModule()`. It has a deterministic `projection_sha256` over the structural document, event/evidence/deviation links and original journal tip. Local and portable views of the identical history produce the same digest. The digest does **not** independently anchor the journal or authenticate the caller's seed.

### Example (local)

```js
import {projectLocalJournal} from './journal-provenance-bridge-v1.mjs';
// seed is an R1-valid document with explicit OwnerIntent→claim→responsibility,
// and sessions:[], task_evidence:[]; original chat source stays UNKNOWN.
const projection = await projectLocalJournal('/explicit/local/journal', seed,
  [{event_id:'EV-1',intent_id:'OI-1'}]);
// projection.document: R1-valid, projection.module_traces: reverse lineage,
// projection.deviations/evidence_links: typed details that R1 cannot represent.
```

**Never use as authority:** every result has `provider_authenticated:false`, `externally_anchored:false`, `owner_message_authenticated:false`, `authorization_granted:false`, `independently_accepted:false`, `live_writer_enabled:false`. Original private-chat source remains UNKNOWN; GitHub parent is its first durable mirror, not original proof. Seed data, local journal and expected portable hashes can all be producer-controlled. The caller must not publish raw Owner/prompts or sidecar URLs without a separately authorized privacy policy. No automatic ChatGPT/Claude/Codex capture, GitHub writer or real provider readback is implemented.

**Scope/gates:** no edits to v3.2/v3.5/Local, no permission escalation. Test: `node --test skills/engineering-relay-v1/journal-provenance-bridge-v1.test.mjs` Node22/24. Independent source review required before claiming AC credit. Downstream [#820 B2a](https://github.com/reallaksh19/Common/issues/820) must verify actual GitHub committed blob source before any remote reconstruction; B2b/R5 held on real Owner/privacy approval. Root #787 acceptance remains 0/8.
