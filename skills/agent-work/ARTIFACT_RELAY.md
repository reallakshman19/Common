# Oracle ↔ agent artifact relay — Common / agent-work

**Cycle now visibility:** A [Task Evidence v2](TASK_EVIDENCE_V2.md) Owner card may link this relay's actual verified receipt. That five-line read-only projection does not itself transfer a file, authenticate a recipient, count unavailable private bytes as received or impose a second report.

**Owner direction · 2026-10-24 · baseline `37435267c861d54998fee589e6dc91385bf59bfa`**

When an Oracle and an agent exchange an **artifact** (input file, workpack, runnable prototype, output, reviewer evidence or revised candidate), use a durable handoff record under [Common `relay/`](../../relay/). This requirement applies **even when a file was initially provided as an upload, a chat attachment, a download link or a local `/mnt/data/...` / `sandbox:` path**. A link in the initiating conversation does **not** make the file available to a different agent.

This is an **artifact transport and custody rule**, not a requirement to relay the Owner's live conversation with the Builder. It does not activate another agent, transfer engineering custody, override the selected project delivery protocol, or grant a merge, release or review PASS. Preserve the direct Owner↔Builder iteration in [Prototype First](prototype-first/SKILL.md).

## 1. Durable route and privacy boundary

**Owner priority decision — 25 October 2026 (applies to every Oracle↔agent↔reviewer artifact handoff):**

| Priority | Route | Scope | Completed transfer |
| --- | --- | --- | --- |
| **1 — FIRST** | **Common GitHub public-safe artifact relay**: immutable permitted bytes under task-scoped `Common/relay/` payload (or an expressly authorized immutable GitHub commit/release) | Public-safe artifacts only; **never** protected originals, private ZIPs, CII/XML or secrets | Possible only when the actual recipient retrieves the exact committed artifact and verifies its identity |
| **2 — NEXT** | **Owner-designated Google Drive Handoffs** | Files that cannot be safely published via Option 1, or a public-safe artifact whose Option 1 delivery is not usable | Possible only after intended recipient verifies authorized access, actual file bytes and identity |
| **FALLBACK — NOT DELIVERED** | **`sandbox:`, `/mnt/data`, in-chat attachment / `LOCAL_ONLY`** | Local presentation or temporary staging when neither 1 nor 2 is available | **Not a completed cross-agent transfer**; preserve source and report `LOCAL_ONLY / NOT_TRANSFERRED` or `BLOCKED` |

**Mandatory:** Every material artifact exchanged between agent, Oracle and independent reviewer must successfully use **Option 1 or Option 2** to count as a durable transfer. Try **1 first if public-safe**; otherwise select **2** without leaking protected bytes. Sandbox links can remain in the current conversation as a fallback/staging convenience, but can **never** replace 1 or 2 or be marked `RECEIVED_CONFIRMED`/`BYTES_VERIFIED` for another agent on that basis. Keep the existing task-scoped public-safe Common relay **receipt** for **either** option, even when its actual bytes live in Google Drive. Do not quietly treat OneDrive or another service as a third qualifying route without a new explicit Owner authorization.

Use a task-scoped durable location under `relay/`: for example [`relay/SCTL-P1-20261024/ARTIFACT_REGISTER.md`](../../relay/SCTL-P1-20261024/ARTIFACT_REGISTER.md) in draft PR #473. The optional [`relay/AGENT_WORK/`](../../relay/AGENT_WORK/README.md) directory is also available for new handoffs. Do not move or duplicate an existing task-specific register solely to match a directory convention. **Do not** write to the governed V3.1 engineering recorder files `relay/STATE.yaml`, `relay/EVENTS.jsonl`, `relay/TRANSACTIONS/`, `relay/LEASES/`, or `relay/GENERATED/` merely to transmit a file. Those belong to a distinct active protocol. If a project has its own required GitHub Cycle / task / issue receipt, link to that native record from the artifact handoff rather than maintaining a second competing assignment state.

- **Public-safe file:** put the actual immutable artifact bytes in an authorized task-scoped `relay/<project-handoff>/payload/` or `relay/AGENT_WORK/<project>/<handoff-id>/payload/` path (or use a stable, expressly permitted GitHub release/commit artifact); identify the Git commit and payload path in the handoff record. Verify GitHub accepts the size and content. A draft PR is a *proposed* relay, not an already delivered handoff.
- **Protected or confidential file:** **never publish its bytes** or private download URL to the public Common repository. Put the bytes in the Owner's authorized private handoff storage, and record only a **sanitized custody reference** at `relay/AGENT_WORK/<project>/<handoff-id>/receipt.md`. If even its name, digest or location is sensitive, keep that field in the protected receipt and publish a non-sensitive locator/status only. The recipient must actually have authorized access and independently retrieve the bytes.
- **Local/upload/sandbox/temporary link (fallback only):** use to present a local working file when both qualifying options cannot be completed, label `LOCAL_ONLY / NOT_TRANSFERRED`, and preserve an actionable next route. A local link does **not** fulfill the mandatory Option 1/2 transfer or permit the next actor to claim receipt. Do not fabricate upload success when the producer cannot publish or the receiver cannot retrieve the bytes.

This repository is publicly visible. **GitHub is not a substitute for private storage.** A pointer to protected storage does not itself confer access.

### Owner-designated private handoff root — 25 October 2026

**Owner decision (25 October 2026):** The Owner authorized sharing the designated **Handoffs** Drive root link with assigned agents, Oracles and independent reviewers in their authorized task conversations. The coordinator may supply this root link directly to the intended recipient; it is a locator, **not a permission grant, restricted-sharing attestation or byte receipt**. Keep individual protected child-file links, protected contents and credentials outside public GitHub and the Progress Page. In public page data and safe relay metadata, retain the stable opaque label `OWNER_PRIVATE_REF:HANDOFFS_PRIMARY`, because the current Progress Page data checker does not accept Drive URLs. Each intended recipient must separately confirm access and independently retrieve and verify the exact permitted file.

**Observed at designation:** the connected Drive account could list the named root and its existing project folders; the provider reported `shared=true`, but did **not** expose sufficient permissions to establish restricted visibility or any new agent/reviewer's access. Record **`ROOT_LOCATED / SHARING_NOT_VERIFIED / RECIPIENT_ACCESS_NOT_RUN`**, not `PRIVATE_ACCESS_VERIFIED`. The custodian must confirm effective sharing permissions for each intended actor before protected bytes are transferred. Do not change Drive ACLs, create public sharing links, move existing files, or imply a receipt merely because the root can be listed.

For a real project transfer, retain the existing project subfolder or authorized task-scoped location within this root. Privately provide the **exact file** to the assigned recipient under its authorized identity and access route; perform the receiver download, file-size/SHA-256 and content check. Use the same exact artifact for a subsequent independent review, but separately record that reviewer's actual permitted retrieval and identity. A Common relay receipt names the **task and opaque locator/status only**; it cannot serve as a private file browser. This designation does not force other projects to use this Owner's Drive or replace stronger native custody protocols.

## 2. Minimal transaction record

Create one public-safe record for each distinct transfer of exact bytes. Use the existing handoff/receipt identifier when the project has one; do not invent competing task or agent identities. The record may be Markdown or project-native structured data; these fields are the minimum human-readable contract:

```text
Handoff: <project / task / unique transfer ID>
From → To: <roles and known short display IDs, or UNKNOWN>
Purpose / next operation: <one bounded task and expected return>
Candidate: <public-safe label + exact version/commit>
Storage: COMMON_RELAY_PAYLOAD | AUTHORIZED_PRIVATE_STORAGE | LOCAL_ONLY | BLOCKED
Locator: <committed relay path+commit, or sanitized private custody reference>
Bytes: <size and SHA-256 measured by producer, if safe to publish; else PRIVATE>
Delivery: <proposed PR / merged public-safe path / authorized protected handoff>
Receipt: PLANNED | RELAY_REGISTERED | RECEIVED_CONFIRMED | BYTES_VERIFIED | WORK_RETURNED
Receiver observation: <actual download/read, measured bytes, date, or NOT_RUN>
Limits: <private access, mismatched digest, missing attachment, untested scope>
Source: <native task/receipt link if available; Owner private reference if needed>
```

Keep **(a)** a producer's claim about bytes, **(b)** a stable relay record, **(c)** a recipient's actual retrieval, **(d)** byte verification, **(e)** technical review and **(f)** Owner acceptance separate. A PR number or hash alone does not establish any later state.

**Agent → Oracle → independent reviewer:** An existing immutable candidate may be reused without uploading a second copy. The Oracle's inspection and the reviewer's inspection require **their own** observed access/bytes and exact-candidate identity; append the reviewer's receiver observation to the existing task relay/native review return (or issue a transfer receipt only when the project contract needs a distinct transfer). Verify reviewer authorship/principal and exposure separately under [Independent Reviewer](independent-review/SKILL.md); a successful Drive download or a new chat is **not** independent approval. The review verdict returns through the native issue/PR, and the Oracle/OTM projects **reconciled** public-safe evidence into Progress Page using its existing CLI, never by copying protected artifacts into `data/`.

## 3. Actual handoff flow

1. **Oracle prepares:** declare exact inputs, recipient, task, expected output, confidentiality and permitted transport. For a previously provided link/attachment, recover the **actual bytes** or explicitly report that they are unavailable.
2. **Producer stages:** **Option 1 first** for public-safe files: commit an immutable authorized `relay/AGENT_WORK` payload (or expressly permitted GitHub equivalent). **Option 2 next**: use the Owner-designated Google Drive Handoffs for protected files, or when public-safe Option 1 is not usable. Record version/size/SHA-256 where appropriate without exposing protected identifiers. A transfer cannot be complete unless **1 or 2** succeeds.
3. **Publish/read back:** verify the relay path and Git commit or the sanitized record actually exist. An open draft PR means `PROPOSED`, not published `main`. Do not claim completed delivery solely from the staging link.
4. **Receiver retrieves:** recipient reads the durable relay record, obtains its permitted artifact, measures actual bytes/hash and checks ZIP contents when relevant. A wrong/missing artifact is `BLOCKED`, never silently replaced.
5. **Agent returns:** put new output artifacts through the same route, with a new exact version/receipt; Oracle inspects the real result and its negative tests. No automatic adoption, acceptance, release or merger follows.

**Fallback (not a third delivery option):** If neither Common public-safe Option 1 nor Owner Google Drive Option 2 can actually deliver the exact artifact, a `sandbox:`/`/mnt/data` link may be shown for local use, but mark `LOCAL_ONLY / NOT_TRANSFERRED` or `BLOCKED`, name the custodian and missing operation, and continue unaffected planning/tests. Do not mark delivery complete, receiver bytes verified or independent review performed.

## 4. Required negative cases

- A `sandbox:/mnt/data/result.zip` link is pasted into another chat but the bytes are absent → **not delivered**.
- A public GitHub relay record points to private data without recipient access → **not received / BLOCKED**.
- The recipient downloaded a ZIP whose SHA-256 differs from the manifest → **identity mismatch / STOP**.
- A draft PR contains a payload but has not merged and the intended recipient did not fetch that PR revision → **proposed**, not verified delivery.
- An agent says `DONE` after publishing its ZIP while nobody has retrieved/tested it → **work returned**, not independently reviewed or Owner accepted.
- A private R5 workpack is proposed for the public Common `relay/` → **reject the publication**; use protected storage and sanitized relay receipt instead.

## 5. Use with Oracle Standalone and Prototype First

For **each Oracle↔agent transfer with an artifact**, cite its relay record in the task/return; existing task-specific registers such as SCTL-P1 PR #473 are valid without renaming or relocating into `AGENT_WORK`; preserve the **one next actor** board in [Oracle Chat Routing](oracle-chat-routing/STANDALONE.md). The Builder still receives the **actual real inputs**, builds a runnable slice, and the Owner tries it directly. Record the artifact's relay disposition separately from prototype states `runnable`, `tried`, `accepted`, `hardened` and `verified`.

When the selected engineering protocol already mandates stronger custody/handover rules, obey those rules and link the exact authoritative receipt; this document never changes the active V3.1 recorder, GitHub Cycle activation, or the Owner's approval boundary.
