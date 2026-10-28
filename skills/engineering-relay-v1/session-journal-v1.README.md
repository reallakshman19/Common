# R2-A — Local append-only cross-agent session and TaskEvidence journal

**Governing:** [new root #787](https://github.com/reallaksh19/Common/issues/787) → [R2-A #812](https://github.com/reallaksh19/Common/issues/812), baseline `main@49ff9e03366470cb6282ff6697b5034e610a703c`. This module imports the **real merged R1 `canonicalJSON`**, not a mocked serializer. It does not import or mutate old V3.2/V3.5/Local governance code.

## API and real persistence

```js
import {initJournal,appendJournal,readJournal} from './session-journal-v1.mjs';
const initial=await initJournal('/explicit/private/repo-local-journal');
const result=await appendJournal('/explicit/private/repo-local-journal',event,initial.tip);
const afterCrash=await readJournal('/explicit/private/repo-local-journal');
```

This is a local Node filesystem journal, **not GitHub session storage or a background ChatGPT/Codex/Claude recorder**. Each call accepts an **explicitly provided** event with session, agent ID, responsibility, baseline exact SHA, UTC time, source citation or UNKNOWN, kind, content visibility/hash, and optional paths/commit/evidence IDs. Supported kinds: OWNER_PROMPT, AGENT_RESPONSE, CODE_CHANGE, DECISION, DEVIATION, ERROR, RECOVERY, TASK_EVIDENCE_START/END/RECOVERY_START. They are events **claimed by the producing agent**, not Owner authorization or independently verified TaskEvidence.

Events are canonicalized using merged R1 source, schema-checked, bounded (public text ≤8KiB, at most 128 touched files, at most 10,000 records), appended as sequential files `0000000001.json`, etc. A SHA256 hash chain and strict sequence verification detect local corruption at replay. Every record is staged in a private temporary file, flushed, atomically **hard-linked with no overwrite** and the directory fsynced; two concurrent writers with the same expected tip cannot silently both commit. The caller must pass the exact `{seq,sha256}` previously replayed or receive `STALE_TIP`. **Journal root must be an explicit ordinary directory, not a symlink.**

A process can reopen/replay and get `tip`, `events`, and `uncommitted_temp_files`. Interrupted `.pending-<UUID>` files do **not** count as evidence and are surfaced for manual recovery. The library never silently removes or accepts a partly staged entry. Any gap, missing/altered entry, hash inconsistency, changed actor for an existing session, invalid END without matching session START, duplicate evidence/event ID, unsafe path, invalid timestamp/commit or unsupported field refuses replay or append. Full malicious rewrite of the entire journal **and recomputation of all hashes is not prevented**: SHA256 chaining is tamper-evident only when the previous tip is separately anchored through a trusted source, which is future R2-B. A local archive can be lost unless separately backed up.

## Privacy and source limits

`content.visibility:'PUBLIC'` stores **exact original text bytes** and SHA256. The caller is responsible for explicit privacy consent and excluding credentials/private data. The recorder does NOT scan for secrets or autonomously capture ChatGPT messages. `REDACTED` stores `text:null` plus caller-provided digest; it makes **no claim** to have seen or verified hidden original bytes. `source.status` is only `UNKNOWN` (locator/digest null) or `CLAIMED` (claim made by agent). Original private chat permalink must remain UNKNOWN unless independently verified; a first durable GitHub mirror is not the original chat.

Each returned journal state has unconditional `authorization_granted:false`, `provider_authenticated:false`, `independently_accepted:false` and `live_writer_enabled:false`. A recorded `DECISION` is NOT an adopted OwnerDecision; a recorded END with a commit SHA is NOT independently verified CI or acceptance. The library has **no network calls, no GitHub tokens, no GitHub issue/PR writes, no merge authority**. Current parent programme remains **AC0/8**.

## Next responsibility

R2-B should implement user-authorized portable producer/session adapters and a privacy-reviewed, immutable repository ingest/export with native GitHub readback, CAS and external tip anchoring. R3 then builds one provider-current snapshot, R4 pure projections, R5 trusted narrow writer and R6 independent cold-agent end-to-end reconstruction. **This local library is a real persistence primitive, not yet the requested repo-wise session memory across multiple agents.**

Run `node --test skills/engineering-relay-v1/session-journal-v1.test.mjs` using Node 22 or Node 24. The test suite exercises real temporary directories and concurrent disk writes rather than in-memory fixture-only assertions.