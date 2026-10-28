# Engineering Relay v1 — R1-A provenance spine

**Governing:** [new programme #787](https://github.com/reallaksh19/Common/issues/787) → [R1-A #789](https://github.com/reallaksh19/Common/issues/789). Based on [R0 source contract](https://github.com/reallaksh19/Common/issues/788#issuecomment-6062357213). This is a **fresh, inert prototype**. Nothing here inherits the superseded V3.5 programme's approval or modifies its code.

## Pure API

`provenance-v1.mjs` exports `validate(document)`, `canonicalJSON(value)`, `traceClaim(document, claimId)`, and `ProvenanceError`. Uses only JavaScript standard features; no provider calls, tokens, filesystem, environment variables, GitHub writes or auto-rendered scoreboards.

Run `node --test skills/engineering-relay-v1/provenance-v1.test.mjs` from repository root with Node 20+.

## Contract

Required top-level document keys: `schema` = `relay-provenance-v1`, `parent_issue` = `owner/repo#number`, and arrays `owner_intents`, `claims`, `responsibilities`, `sessions`, `task_evidence`, `research_findings`, `owner_decisions`. Every node has globally unique ID. Cross references must point to existing nodes, leaf dependencies must be acyclic, sessions reference exact leaf, evidence references matching session and leaf. A coding END needs exact 40-hex SHA. Event types include OWNER_PROMPT, AGENT_RESPONSE, DECISION, CODE_CHANGE, ERROR, RECOVERY. START without END is valid to support real interruption recovery.

Owner record preserves raw_text and distinct `original_source` versus `first_durable_mirror`. Original source status only `UNKNOWN`, `CLAIMED` or `FIRST_DURABLE_MIRROR`; an original_source may **not** self-label itself as a mirror. Source locators/sha256 digests are syntactically validated but **not authenticated**.

ResearchFinding may be unverified/supported/contradicted **as a claim** and does not automatically change a plan. OwnerDecision has a `source`, but this validator **does not verify the issuer** or grant Owner acceptance. Likewise an evidence END does not establish CI success or source custody. Future R1-B/R2/R3 must read provider source and verify approval and currentness, with explicit trusted principal/readback.

**Never use `validate()` as acceptance, auth, approval, scoreboard or workflow writer permission.** Positive tests prove shape, not truth. The code does not persist transcripts; records must be supplied explicitly with privacy/retention controls upstream.

## R1-A acceptance limits / next responsibility

This leaf delivers **structural** referential integrity, typed source statuses and deterministic JSON; it does not provide durable cross-agent capture, hosted CI, actual graph authority, cryptographic attestation or live GitHub synchronization. R1-B should establish independent provider-authenticated owner/research/source decision receipts before any downstream snapshot or writer consumes these objects.

## Security and scaling review (R1-A exact-head repair)

The canonical serializer builds null-prototype output objects before assigning arbitrarily named own keys; JSON keys such as `__proto__` and `constructor` remain data, not prototype setters. `validate()` uses iterative graph traversal so a deep, acyclic responsibility chain does not overflow the JavaScript call stack; arrays are limited to 10,000 items to refuse obviously unbounded provider payloads. Tests cover 5,000-step dependencies, cyclic mutation, prototype-key round-trip and oversized event streams.

The [read-only Node CI workflow](../../.github/workflows/relay-reset-provenance.yml) runs `node --test` on pull requests touching the isolated new module. It has `contents: read`, no issue/PR write permissions and no access to a source-authenticity approval channel. Its green result is **structural test evidence only**, never programme AC acceptance.

## Canonical JSON input hardening (R1-A)

The pure canonical serializer now bounds nesting (256), aggregate visited objects (100,000) and arrays (10,000); rejects cyclic objects, accessor properties and sparse arrays with controlled ProvenanceError rather than executing a getter, silently serializing holes or overflowing the recursive stack. Repeated non-cyclic object references are duplicated as ordinary JSON values. This structural boundary is **not** source-authenticity or approval.

## Bidirectional claim/source lineage (R1-A structural repair)

`traceEvidence(document,evidenceId)` traverses the **precise** task evidence → matching session → owning responsibility → claims → raw Owner intent records, including distinct original-source status and first durable mirror. `traceModule(document,relativeModulePath)` follows exact changed source path → only sessions that changed that file → only their evidence → responsibilities/claims/raw Owner intent. An unmodified file returns empty matches, not implied acceptance; unsafe paths/unknown evidence raise `ProvenanceError`. These views read only the supplied document and **do not authenticate issuer, trust claims, verify commit SHA, approve evidence, or persist original chats**. Upstream must still enforce privacy/retention for raw Owner text. Negative tests exercise multiple sessions and unrelated evidence cross-joins.
