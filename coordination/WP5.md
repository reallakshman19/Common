# WP5 — Authenticated Owner Command Queue & Coordinator Delivery Plane

**Scope:** Issue [#353](https://github.com/reallakshman19/Common/issues/353), Workpack 5 (WP5).

WP5 delivers the operational command plane for the Multi-Project Control Tower v3:
1. **Durable Command Ledger (`coordination/command_db.py`)**: SQLite WAL-mode store (`command_index.db`) enforcing database-level single-flight invariants per assignment across `QUEUED`, `RESERVED`, `DISPATCHING`, and `DELIVERY_UNCERTAIN` states, with an append-only transition journal protected by SQLite triggers.
2. **Command Engine & CAS Concurrency Gate (`coordination/command_engine.py`)**: Two-stage compare-and-swap (CAS) validation:
   - **Stage 1 (At Admission)**: Verifies binding generation, AIM label SHA, single-flight availability, and decision-card provenance.
   - **Stage 2 (Immediately Pre-Send)**: Re-verifies active run generation, active chat ID, one-active-tab invariants, and coordinator HOLD/OUT status.
3. **Pluggable Delivery Transport (`coordination/coordinator_transport.py`)**:
   - `NoOpTransportAdapter`: Deterministic dry-run adapter for unit and integration testing.
   - `CoordinatorTransportAdapter`: Safe file-based adapter operating within coordinator v3.28 session workspaces, featuring non-destructive composer inspection that strictly protects unsent human drafts.
4. **Authenticated Command Service (`coordination/command_service.py`)**: Loopback-only HTTP service (`/api/v3/owner/...`) with constant-time Bearer token comparison (`hmac.compare_digest`), token rotation, zero token logging, CSRF/Origin/Host validation, 64 KB request limit, and Private Owner Inbox.

---

## 1. Authority, Security & Isolation Boundaries

| Domain | Policy & Enforcement |
|---|---|
| **Public vs Private** | Public GitHub Pages dashboard remains **strictly read-only**; zero command endpoints, zero tokens, zero private chat/session identifiers. |
| **Network Boundary** | Command service binds loopback (`127.0.0.1` / `::1`) by default; remote access allowed only behind an authenticated TLS reverse proxy. |
| **Authentication** | Bearer token authentication verified with constant-time `hmac.compare_digest`; tokens are never logged or stored in DB. Supports seamless token rotation. |
| **Typed Action Allowlist** | Only `DIRECTIVE`, `DECISION_RESOLVE`, `RECON_MODE`, `PAUSE_WORK`, `RESUME_WORK` permitted. Arbitrary scripts (`Invoke-Expression`, `rm -rf`, `../../`) rejected with 400 Bad Request. |
| **Governance Decisions** | Actions resolving governance cards (`DECISION_RESOLVE`) require explicit `decision_card_id` and `decision_outcome`; unprovenanced actions fail closed (422). |
| **Draft Protection** | Target composer buffer is inspected before delivery; any uncommitted human text aborts dispatch (`DENIED`, `COMPOSER_DIRTY_UNSENT_DRAFT`). Buffer preserved 100% byte-for-byte. |
| **Readback & Double-Send** | Transport timeouts move commands to `DELIVERY_UNCERTAIN`. Retry requires verified readback proof; no blind auto-resends. `DELIVERY_UNCERTAIN` holds the single-flight slot. |

---

## 2. Target Identity & Data Model

Every command binds to an immutable 11-part composite identity:
```text
(project_id, work_id, lane_id, assignment_id, run_id, binding_id,
 coordinator_id, session_id, chat_id, binding_generation, expected_label_sha)
```

### Command Lifecycle

```text
[ DRAFT ] ──▶ [ ACCEPTED ] ──▶ [ QUEUED ] ──▶ [ RESERVED ] ──▶ [ DISPATCHING ]
                   │                                                   │
                   ▼ (CAS Failed)                                      ├─▶ [ DELIVERED_CONFIRMED ]
         [ REJECTED / DENIED ]                                         ├─▶ [ DELIVERY_UNCERTAIN ]
                                                                       └─▶ [ DENIED ] (CAS / Draft)
```

- **Downstream Independent Observations**: `command_acknowledgments` and `command_adoptions` are recorded from subsequent agent evidence logs with independent timestamps and cryptographic digests, never inferred from command dispatch.

---

## 3. Database Invariants (`command_index.db`)

1. **Single-Flight Constraint**:
   ```sql
   CREATE UNIQUE INDEX idx_single_flight_per_assignment
   ON owner_commands(assignment_id)
   WHERE state IN ('QUEUED', 'RESERVED', 'DISPATCHING', 'DELIVERY_UNCERTAIN');
   ```
2. **Immutable Transition Journal**:
   Triggers `trg_no_update_journal` and `trg_no_delete_journal` abort any `UPDATE` or `DELETE` statements on `command_transition_journal`.

---

## 4. API Endpoints (Loopback Only)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v3/owner/commands` | Submits a typed command (returns 201 Created on new, 200 OK on idempotent replay, 409 on conflict). |
| `GET` | `/api/v3/owner/commands` | Lists commands (filtered by `project_id`, `assignment_id`, `state`). |
| `GET` | `/api/v3/owner/commands/<command_id>` | Returns command details and complete audit transition journal. |
| `POST` | `/api/v3/owner/commands/<command_id>/cancel` | Cancels a `QUEUED` or `RESERVED` command. |
| `POST` | `/api/v3/owner/commands/<command_id>/reconcile` | Executes transport readback on a `DELIVERY_UNCERTAIN` command. |
| `GET` | `/api/v3/owner/inbox` | Retrieves active queue, uncertain deliveries, and downstream ACK/ADOPT receipts. |

---

## 5. Adversarial Acceptance Suite (ADV-27 through ADV-38)

All 12 adversarial test scenarios pass with 100% compliance in `coordination/tests/test_owner_commands.py`:
- **ADV-27**: Idempotency Replay & Scope Invariance.
- **ADV-28**: CAS Binding Generation Mismatch Rejection.
- **ADV-29**: CAS AIM Label SHA Mismatch Rejection.
- **ADV-30**: Database-Enforced Single-Flight Invariant Across Workers & Process Restarts.
- **ADV-31**: DELIVERY_UNCERTAIN Blocks Subsequent Conflicting Commands.
- **ADV-32**: Unsent Human Draft Preservation & Zero Buffer Overwrite.
- **ADV-33**: Honest Readback Reconciliation & Zero Blind Resend.
- **ADV-34**: Authentication, Constant-Time Token & Network Security Barriers.
- **ADV-35**: Strict Typed-Action Allowlist & Anti-Shell Execution Rejection.
- **ADV-36**: Decision Card Provenance Enforcement.
- **ADV-37**: Multi-Project & Multi-Session Tab3 Isolation (5 Agents, 2 Projects).
- **ADV-38**: Windows v3.28 Parity & Regression Invariance (113 total coordination tests pass).
