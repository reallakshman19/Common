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

## Oracle-side custody observation — 2026-10-24

**Observer:** SCTL standalone Oracle (separate conversation). **Scope:** available original bytes only; NOT a Builder intake receipt, product result or Owner acceptance.

- Oracle retrieved the original R5 evidence ZIP in its session and verified its ZIP CRC and **16/16 internal manifest SHA-256 entries**, including original `R5.docx` and `R5_after.html`.
- Archive and input-entry exact sizes/SHA-256 were recorded in a **private Oracle-side input receipt**. The bytes, private receipt and session-scoped `/mnt/data` / `sandbox:` link are intentionally **not published** here.
- Artifact statuses **A03/A04/A05: ORACLE_BYTES_VERIFIED / BUILDER_NOT_RECEIVED**. The original Builder return remains an accurate statement about the Builder's own conversation at its time.
- **A06:** authentic Microsoft Word-exported PDF/render: NOT_VERIFIED; none in the evidence package. **A07:** runnable P1 candidate: NOT_BUILT.
- **Durable handoff gap:** no designated, verified private cross-agent destination found; an authorized Owner transfer plus independent Builder readback is required. A private chat download is a staging link, not durable cross-agent custody.
- **Oracle review:** PR #473 review ID `5639107895`. Generic rule PR #474 accepts this existing task-scoped `relay/` register path; do not create a competing second SCTL-P1 ledger.

## Builder-side private intake and delivery observation — 2026-10-24

**Evidence:** [BUILDER_P1_DELIVERY.md](BUILDER_P1_DELIVERY.md) (same draft branch).

- **A03/A04/A05: BUILDER_BYTES_VERIFIED**, updated from the earlier `BUILDER_NOT_RECEIVED` historical state. Archive and both input-entry raw SHA-256 digests were independently measured after actual Builder attachment. Source originals were not overwritten.
- **A06: SOURCE_PREVIEW_RENDERED / WORD_FIDELITY_NOT_VERIFIED**. Source Table #2 (Notes) is located on LibreOffice-rendered PDF preview page 2 of 13. No authenticated Word-export PDF.
- **A07: RUNNABLE_CANDIDATE / OWNER_NOT_TRIED**. Private ZIP `SCTL_P1_Missing_Source_Lens_R5_Private_Prototype.zip`, **1,888,155 bytes**, SHA-256 `8b5e5c8f3184f6a68dab4888ee38165473345cb37daa9a34d122532c6b1d1805`. Private Builder chat download exists; `SESSION_ONLY`, not durable cross-agent byte custody.
- Builder ran 6/6 unit tests and Chromium injected-HTML DOM interaction checks; browser normal file URL blocked by administrator. No Owner acceptance or independent page-parity PASS.
- This is the **same task-specific register**, not a second ledger. The former Oracle and Builder receipt statements are preserved as valid observations at their respective times.
