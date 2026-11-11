# TOPO-A P0 — exclusive-writer handover (prepared; no implementation authority)

**State:** `DRAFT_HANDOVER / OWNER_SCOPE_APPROVED / CUSTODY_ACK_PENDING / LEASE_INACTIVE / PRODUCT_WRITE_HOLD`  
**Native source of authority and return destination:** [TopoFix issue #12](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/issues/12) — **not** this relay PR.  
**Scope:** Existing WBS R1 3.2/4.1, P0 only. **Date:** 31 October 2026.  
**Audience:** established TOPO-A Agent 1 (proposed exclusive P0 writer), acting Oracle, future non-author reviewer.  
**Privacy:** Public-safe contract only; **NO** private PSI116 XML, CII, fixture bytes, private source digests, coordinates or owner-specific engineering details.

## 1. Governing decisions and history — do not repeat

- Owner decision, conditional P0 approval: [issue #12 comment 6541435617](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/issues/12#issuecomment-6541435617).
- Exact prepared lease/file boundaries and proposed Agent instruction: [comment 6541417858](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/issues/12#issuecomment-6541417858).
- Custody requests to actual incumbents/reviewer: [comment 6541562867](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/issues/12#issuecomment-6541562867).
- Prior agent-reported READ_ONLY synthetic receipts (accepted in scope by Oracle; **not** independent engineering PASS): [3/3 falsifiers](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/issues/12#issuecomment-6540223213), [6/6 lookup](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/issues/12#issuecomment-6540687449), [8/8 sidecar contract](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/issues/12#issuecomment-6540851691), [12/12 generation envelope](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/issues/12#issuecomment-6541137230). **Do not rerun** or count these as a new P0 acceptance unit.
- Source-of-truth decision matrix: [comment 6539665236](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/issues/12#issuecomment-6539665236). Actual protected-original interpretation belongs only to Oracle-local observation [comment 6539783225](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/issues/12#issuecomment-6539783225); Agent's original private-byte trial is **NOT_RUN** and engineering design intent **UNKNOWN**.

This is a handover **proposal**, not evidence that any recipient read the Common branch. An agent or reviewer must retrieve the committed handover at the final exact commit, disclose source/custody, and ACK in the native issue. A draft PR cannot itself attest cross-agent delivery.

## 2. Pinned product baseline and separation

| Repository state | Git identity / disposition |
| --- | --- |
| TopoFix `main` | `fb92be7bd8dba997d71d2028b0b36b0d3fe2c24c` |
| Draft product PR #10 | `a5fc0acbe489d85de881f28c9792ce5673ec86aa`; based on `main`, **HOLD** |
| Draft product PR #11 | `2ba52da75ca26d2937a1639a778e50262fd88b52`; based on PR #10, **HOLD** |
| Owner-approved proposed P0 base | **PR #11 exact head** `2ba52da75ca26d2937a1639a778e50262fd88b52`, **conditional** on custody ACK and renewed head verification |
| `models.py` at PR #11 | Git blob `2fd98d98822749e535c998d2a2439a5f0b9b0e3e` |
| P0 branch/head | **NOT CREATED / UNKNOWN**; this Common handover branch is **NOT** a product P0 branch |

Existing #10/#11 have overlapping changed paths `tabs/topology-workspace/workspace-app.mjs` and `tests/audit-browser.mjs`. #10 also writes parser, port rules, integration bridge and Worker. #11 writes queue/Second Pass. **No shared UI/Worker/bridge file is leased to P0.** The absence of overlap for the three proposed P0 paths does **not** establish exclusive-writer custody.

## 3. Exact candidate writer lease — not active

**Exclusive proposed writer:** established TOPO-A Agent 1, **recipient conversation/chat ID NOT_VERIFIED**. No new Agent, no onboarding.  
**Three-file allowlist ONLY (proposed; no code write yet):**

1. **NEW** `converters/psi116_topology_resolver/closure_witness.py` — read-only Python declaration/port witness extractor using the existing `bound_closure_records()` source of truth.
2. **ADDITIVE ONLY** `converters/psi116_topology_resolver/models.py` — a `ResolutionResult.findings_payload()` hook adding a read-only `closureBindingWitnesses` member; preserve existing `manualConnectionPorts` and all existing fields.
3. **NEW** `tests/test_closure_witness.py` — isolated native regression/negative/nonmutation tests. No other test files.

**Explicit excluded paths:** `connection_ports.py`, `parser.py`, `topology-integration.js`, `workspace-app.mjs`, `tests/audit-browser.mjs`, `topology-worker.mjs`, `topology-worker-client.mjs`, `second-pass.mjs`, `manual-fix-queue.mjs` and all native CII/Weight/Final, UI, Worker or original-source artifacts. **NO** new solver, CLOS edits, tolerance changes, source working-copy mutations, Apply, Queue, 240.6 mm join, P1 integration, protected-branch edit or merge.

**P0 source contract:** one deterministic row per qualified physical occurrence with exact `source.sha256` (UTF-8 source *text*, not caller-claimed UI generation), backend schema/config, `branchIndex`, `sourceIndex`, `portSourceKey` / `node.key`, component owner/endpoint, and **all** bound CLOS declaration source keys. Preserve `DIRECT` variants (EXACT_RECORD vs SAME_POSITIVE_NUMBER_WITHIN_TOLERANCE), `OWNER_PORT`, `BRANCH_BOUNDARY`, multiple matching predicates and `UNKNOWN` when the exact reason is unproven. **Never** classify `UNQUALIFIED`/missing evidence as backend-evaluated `NO_BINDING`. `NO_BINDING` only after an eligible physical port underwent a complete current-source authoritative evaluation; `EVIDENCE_UNAVAILABLE` is distinct and fail-closed. Keep exact source-key/branch identity; Node Number alone is not enough. **Python must never self-attest browser epoch, request token or working revision.**

## 4. Activation checklist — all gates required, NOT satisfied by this PR

- [ ] **Owner scope + source base:** approved conditionally in the native issue; reverify PR #10/#11 exact heads immediately before lease activation.
- [ ] **Incumbent #10 writer ACK:** actual principal/chat + correct head, explicit nonoverlap promise on all three P0 paths, linked native comment. **NOT_VERIFIED**.
- [ ] **Incumbent #11 writer ACK:** same; one ACK for both only if one *verified actual incumbent* owns both. **NOT_VERIFIED**.
- [ ] **Existing Agent 1 recipient and exclusive writer ACK:** identifiable chat/principal, explicit three-file scope and pinned base. **NOT_VERIFIED**.
- [ ] **Independent P0 reviewer ACK:** Owner-nominated TopoFix IR `6ae2d5ac` is only a **candidate**; disclose authorship/prior exposure, accept non-author review and independently retrieve evidence. **NOT_VERIFIED**.
- [ ] **Oracle exclusive lease record:** `P0_LEASE_ACTIVE`, named writer, verified ACK links, reviewer, source base, P0-only branch, path allowlist and one native return destination. **NOT POSTED**.

**Until all boxes are completed: `P0_PRODUCT_WRITE=HOLD`, no product PR.** Owner's approval of the *proposal* does not impersonate incumbent writer ACKs or reviewer receipt. If there is an incumbent claim conflict, escalate the single custody conflict to Owner, do not activate parallel writers.

## 5. Bounded implementation assignment — PREPARED, NOT ISSUED

When and only when the above lease is active, Oracle may issue to existing Agent 1:

> Continue existing issue #12 on **approved pinned PR #11 source base**. Write **only** the three allowlisted P0 files; do not modify prior product PR heads. Reuse backend `bound_closure_records` instead of duplicating source semantics. Emit deterministic source/qualified-port CLOS evidence with every declaration key/predicate, preserving `NO_BINDING / UNQUALIFIED / EVIDENCE_UNAVAILABLE`, exact source-text SHA/config/schema. Add isolated regression and negative tests: DIRECT exact vs same-number positive alias, OWNER_PORT, BRAN boundary vs nonbound neighbor, duplicate NodeNumber across branches, unqualified port, absent/tampered/foreign-source witness and config/schema drift. Show exact base/head/blob IDs, actual commands and raw logs, source/fixture bytes+hashes before/after, 0 source mutations, and no new Apply/Queue/movement eligibility. Return **one** evidence delta to original native issue #12. Independent non-author reviewer must separately inspect the exact product candidate head and independently derive expected source witnesses. No P1, CLOS override, 240.6mm join, original private source publication, engineering PASS, release or merge.

**Acceptance stages:** `AUTHOR_RETURNED` → `INDEPENDENT_SOURCE_AND_NATIVE_REVIEW` → `P0_CANDIDATE_ONLY` (if qualified); **not** engineering acceptance. Stage P1 browser/Worker generation integration is separately scoped and may not be added as a shortcut.

## 6. Handover receipts and roles

| Field | State |
| --- | --- |
| Originating Owner approval | **CONFIRMED** for proposal in issue #12 |
| Native issue and return channel | [issue #12](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/issues/12), **AUTHORITATIVE** |
| Common draft PR payload | **PROPOSED PUBLIC-SAFE RELAY** — exact commit to be recorded when opened |
| Producer/oracle | acting TOPO-A Oracle; P0 source author **NONE** |
| Proposed recipient | existing TOPO-A Agent 1; chat/ACK **NOT_VERIFIED** |
| PR #10/#11 active incumbents | actual agents/ACK **NOT_VERIFIED** |
| Candidate reviewer | IR `6ae2d5ac`; P0-specific review ACK **NOT_VERIFIED** |
| Physical original-file transfer | **NOT ATTEMPTED / NOT_TRANSFERRED** |
| Product implementation status | **NOT_STARTED** |
| Engineering and merge status | **HOLD** |

**Single next accountable action → Owner:** route existing [ACK request #6541562867](https://github.com/reallakshman19/xml229-topology-wp1-preview-20261028/issues/12#issuecomment-6541562867) to genuine PR #10/#11 incumbents and P0 reviewer, establish the existing Agent 1 chat/principal and ensure all responses land on issue #12. Oracle activates lease only after the real ACKs; this Common draft is **not** an ACK proxy.

**No duplicate Progress Page/Cycle Board report. No product code modified.**
