# R2-B1 — Portable privacy-gated journal bundles and cold-import verification

**Governing:** fresh [parent #787](https://github.com/reallaksh19/Common/issues/787) → [R2-B1 leaf #817](https://github.com/reallaksh19/Common/issues/817). Built against the *actual merged* [R2-A #813](https://github.com/reallaksh19/Common/pull/813) at `main@284a9f24fd88cd3caaf2a65a056adae5f13851c2`, not a replacement journal. It imports `readJournal` from `session-journal-v1.mjs` and `canonicalJSON` from `provenance-v1.mjs`.

## Two portable APIs

```js
import {exportPortableJournal,verifyPortableJournal} from './session-bundle-v1.mjs';
const context={
  repository:'reallaksh19/Common',
  parent_issue:'reallaksh19/Common#787',
  source_sha:'284a9f24fd88cd3caaf2a65a056adae5f13851c2',
  exported_at:'2026-10-08T17:00:00Z'
};
const policy={
  schema:'relay-export-policy-v1',revision:'PRIVACY-V1',
  approved_public:[
    {event_id:'EV-1',content_sha256:'<exact approved source text SHA256>'}
  ]
};
const bundle=await exportPortableJournal('/explicit/local-journal',context,policy);
// Operator stores/transfers bundle.bytes through separately permitted channel.
// In a fresh Node process/host after obtaining an independently supplied expected identity:
const found=await verifyPortableJournal(bundle.bytes,{
  repository:context.repository,parent_issue:context.parent_issue,
  source_sha:context.source_sha,
  bundle_sha256:bundle.sha256,tip_sha256:bundle.manifest.tip.sha256
});
```

**No automatic upload, no network or GitHub writer.** The API returns a canonical JSON *byte string* and a SHA256 digest; the caller may write it to disk or transfer it by a separately authorized channel. Source `repository`, `parent_issue` and `source_sha` are caller assertions, not GitHub-authenticated. `exported_at` is explicit so equal journal+policy+context produce byte-identical digests.

## Privacy and cold-reader gates

Every **PUBLIC** event, including raw Owner prompts, agent replies, file paths or source pointers, requires a policy entry naming its exact event ID **and content SHA256**. All approvals must be used and unique. No default allow-all. Policy revision, full canonical policy digest, counts and event chain are committed into the bundle manifest. REDACTED entries retain only the producer-asserted hash and `text:null`; original bytes are not recoverable. A producer who labels secrets PUBLIC and intentionally approves them can leak them: the library has **no automatic secret scanner**, and the policy must be independently privacy-reviewed. Event metadata and source URLs may themselves contain sensitive information; do not share indiscriminately.

The cold verifier requires exact expected repository, parent issue, source commit SHA, **bundle SHA256 and R2-A tip** as caller-supplied checks, then performs a *real* R2-A replay from newly written temporary per-sequence files. It verifies strict event schema, order, prev links, stored digests, session identities, timestamps, START/END, provenance labels and content hashes. It also rechecks privacy consent, bundle canonical JSON, counts and per-session IDs. Unknown schema, changed tip, missing middle record, altered source, unexpected `accepted:true`, forged native source status and privacy removal fail. Payload capped at 4 MiB, 256 events, 256 public consents. Temporary scratch directory is private and deleted after verification.

**Important security distinction:** the separately passed expected digest/tip protects against *accidental changes* or tampering only when the expected values come from a genuinely independent, trusted channel. If one malicious actor controls the bundle, expected checksum and local journal, they can reforge all three. There is **NO external immutable GitHub tip anchoring in R2-B1**, no cryptographic human Owner source authentication and no acceptance of producer-declared TASK_EVIDENCE. Every import returns `externally_anchored:false`, `owner_message_authenticated:false`, `authorization_granted:false`, `independently_accepted:false`, and `live_writer_enabled:false`.

## What B1 delivers versus what still needs coding

B1: real portable bytes, privacy manifest, repository/parent/commit identity, deterministic content digest, **independent Node process** cold-import, and real merged R2-A hash-chain replay. Cross-machine transfer is operator-controlled; these APIs cannot magically capture sessions from ChatGPT, Claude or Codex.

B2: a separately authorized, default-branch-safe GitHub ingest/export with independent readback, external source custody, CAS and exact branch/PR currentness, a genuinely anchored Owner/trust role grant and privacy policy review. R3: one provider-current `ReconciledSnapshot`. R4/R5: identical-digest smart issue/PR titles, managed bodies, handover, trusted narrow publishing. R6: fresh independent agent cold takeover. **New programme AC0/8 until actual provider/Owner/end-to-end acceptance; this CI is an offline producer-trust check only.**

Tests: `node --test skills/engineering-relay-v1/session-bundle-v1.test.mjs` on Node 22/24. The test suite writes real R2-A journals, exports/rehydrates actual sequence files, and starts a **separate Node process** for cold verification.
