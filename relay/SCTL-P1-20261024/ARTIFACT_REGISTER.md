# SCTL-P1 — Oracle ↔ Builder artifact register (v1)

**Status:** DRAFT / PUBLIC-SAFE METADATA ONLY / NOT A PRODUCT PASS  
**Date:** 2026-10-24  
**Project:** Source Completeness & Traceability Lens (SCTL), Prototype P1 — Missing Source Lens  
**Governance basis:** `Common@acb3a61b3d89a622a5f29f9f2a87c0405e0f6bee` (Oracle Standalone and Prototype First).  
**Relay-location reference:** `Common@37435267c861d54998fee589e6dc91385bf59bfa:relay/`.

## Transaction rule

Every material Oracle-to-builder or builder-to-Oracle artifact must be registered here (or in a later versioned register) even when the artifact is supplied through a chat download such as `sandbox:/mnt/data/<file>`, a local `/mnt/data/<file>` path, an authorized Drive handoff, a code branch, a draft PR, or a GitHub Actions artifact.

This file is an **index/receipt, not a replacement for the bytes**. For each actual artifact, record: stable artifact ID; sender and recipient role; transaction direction; exact basename and format; custody class; transport kind; actual retrievable location or approved private locator; raw byte size; SHA-256 of original bytes; source or code revision when relevant; timestamp; recipient retrieval/hash verification state; and the exact task/use intended. Record `UNKNOWN`/`NOT_RUN` rather than guessing.

### Transport and privacy rules

- `/mnt/data/...` and `sandbox:/mnt/data/...` are **session-scoped paths**, not cross-chat or durable repositories. Register the path and mark `SESSION_ONLY / NOT_CROSS_CHAT_VERIFIED`; do not claim that a different agent can retrieve it merely because a link is present. The receiving agent must actually fetch and hash the bytes.
- For cross-agent handoff, move protected bytes through the **Owner-authorized private custody channel**, then record public-safe receipt metadata. If permanent private storage is absent, report `TRANSFER_BLOCKED` with the precise missing capability.
- Never commit source DOCX, converted HTML, original document page images, private R5 reference ZIPs, complete private manifests, live customer text, unrestricted Drive child links, tokens or chat URLs to this public repository.
- Public code and documentation may use exact draft PR/commit or CI URLs. A draft PR alone does not establish that private data were transferred or verified.
- Do not repurpose existing `relay/STATE.yaml`, grant writer/Oracle authority, publish Progress Page state, or infer Owner acceptance from this register.
- Version a changed artifact; preserve the prior receipt and its status. A claimed SHA in a sender message is `SENDER_REPORTED` until the recipient independently measures downloaded bytes.

## Artifact ledger — initial P1 transaction

| ID | Direction | Artifact | Custody | Availability / recipient verification |
| --- | --- | --- | --- | --- |
| SCTL-P1-A01 | Oracle → Builder | Pinned onboarding and work release | PUBLIC-SAFE REFERENCE | GitHub pinned skill files were read; work release was received in this chat, not independently published |
| SCTL-P1-A02 | Builder → Oracle | `BUILDER_RETURN.md` (this folder) | PUBLIC-SAFE METADATA | Candidate on a draft documentation branch; GitHub readback required |
| SCTL-P1-A03 | Oracle/Owner → Builder | `R5.docx` | PROTECTED ORIGINAL | NOT RECEIVED; size/SHA-256 UNKNOWN; recipient hash NOT_RUN |
| SCTL-P1-A04 | Oracle/Owner → Builder | `R5_after.html` | PROTECTED ORIGINAL | NOT RECEIVED; size/SHA-256 UNKNOWN; recipient hash NOT_RUN |
| SCTL-P1-A05 | Oracle/Owner → Builder | Earlier R5 traceability package (reference only) | PROTECTED ORIGINAL | NOT RECEIVED; size/SHA-256 UNKNOWN; recipient hash NOT_RUN |
| SCTL-P1-A06 | Oracle/Owner → Builder | Authenticated Word-exported PDF or equivalent original-page reference | PROTECTED SOURCE RENDER | NOT RECEIVED; fidelity/page count NOT_VERIFIED |
| SCTL-P1-A07 | Builder → Oracle/Owner | Runnable Missing Source Lens ZIP with launcher/static report | DERIVED PRODUCT | NOT BUILT; no download link; no hash |

No file bytes were transferred by this register. No path, SHA-256 or remote download URL has been fabricated.

## Required entries after an actual handoff

```text
ARTIFACT_ID:
TRANSACTION: Oracle -> Builder | Builder -> Oracle
PURPOSE/TASK: SCTL-P1
FILENAME:
BYTES:
SHA256:
CUSTODY_CLASS: PUBLIC_SAFE | PRIVATE
TRANSPORT: GITHUB_COMMIT | GITHUB_ACTIONS | PRIVATE_DRIVE | CHAT_SANDBOX | OTHER
LOCATOR: (public-safe only; private locator in approved restricted channel)
LOCATOR_DURABILITY: DURABLE | RETENTION_LIMITED | SESSION_ONLY | UNKNOWN
SENDER_REPORT: PRESENT | NOT_PRESENT
RECEIVER_RETRIEVAL: VERIFIED | NOT_RUN | FAILED
RECEIVER_SHA256: (computed independently, or UNKNOWN)
RELEVANT_COMMIT_OR_SOURCE_HASH:
TESTED: PASS | FAIL | NOT_RUN
OWNER_TRIED: YES | NO | UNKNOWN
NEXT_ACTION:
```
