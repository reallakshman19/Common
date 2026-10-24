# Worked handover: CIIFR R3 and P2.5-B — illustrative source-bound snapshot

**Observation boundary:** 2026-10-24 · **PUBLIC-SAFE** · Same Owner product, two identifiers: **Progress project = `ciifr`**, **engineering Cycle workstream = `p25b`**. **Mode: standalone (NOT OTM)**.

This is a **dated worked example**, not the authoritative live state. On any `Cycle now` / `Oracle handover` invocation, reread fresh `Common/main`, issue receipts and actual `progress-page/main` before deciding what to execute. A reported IR result, prior Oracle description or partial receipt is not independent recipient-byte evidence in the successor chat.

## 1. Start at real landing page and fixtures

| Resource | Actual public link | How to use |
|---|---|---|
| **Owner-facing landing page** | [Progress Page](https://reallakshman19.github.io/progress-page/) | Select existing **CIIFR** project tab and its **R3** revision. The site URL comes from `progress-page/data/projects.json`; do not invent a CIIFR fragment or second tab |
| **CIIFR fixtures** | [`data/ciifr/fixtures.json`](https://github.com/reallakshman19/progress-page/blob/main/data/ciifr/fixtures.json) | Read intent, inputs, knownIssues, pending, roadmap, repository/issues/PR pointers; provenance is indicated by each row |
| **R3 Owner intent and revisions** | [`data/ciifr/index.json`](https://github.com/reallakshman19/progress-page/blob/main/data/ciifr/index.json) | Check that R3 is current and R1/R2 retained as superseded |
| **Current role cards** | [`data/ciifr/cards.json`](https://github.com/reallakshman19/progress-page/blob/main/data/ciifr/cards.json) | Coordination/reporting projection, **not** an independently authenticated actor |
| **Trace/audit** | [`data/ciifr/audit.json`](https://github.com/reallakshman19/progress-page/blob/main/data/ciifr/audit.json) | Source-bound publication history, not proof of private ZIP access |
| **Product repository** | [XML_Compare_Utilities](https://github.com/reallakshman19/XML_Compare_Utilities) | Historical product repository reference from published CIIFR fixtures; do not presume it contains the private v0.1.1 ZIP |
| **Canonical Cycle assignment** | [P2.5-B `CURRENT.json`](https://github.com/reallakshman19/Common/blob/main/oracle-cycles/p25b/CURRENT.json) | Read actual active revision, gates, next assigned actor, issue and publication status |
| **GitHub return inbox** | [Common issue #465](https://github.com/reallakshman19/Common/issues/465) | Append-only public-safe actor receipts; comments do **not** automatically advance the assignment |
| **Coder's partial receipt** | [Comment on issue #465](https://github.com/reallakshman19/Common/issues/465#issuecomment-6379577797) | Coder **reported** locally checked ZIP bytes, CRC and file correspondence; not independently downloaded from Drive |
| **Private custody plan** | [Common PR #469](https://github.com/reallakshman19/Common/pull/469) | Draft plan for real private file transfer and manifest, **not** actual transferred bytes |
| **Prepared Oracle successor** | [CIIFR R3 checkpoint](https://github.com/reallakshman19/Common/blob/main/oracle-cycles/p25b/CIIFR-R3-ORACLE-SUCCESSOR.md) | Understand old/current sources and safe changeover without assuming a control epoch |
| **Rev2 reconciliation proposal** | [Common PR #467](https://github.com/reallakshman19/Common/pull/467) | Draft at observation time; do not claim merged or current until reread |

**Private file policy:** The Handoffs Drive folder contains protected original engineering inputs, but its inspected project subfolder did not contain the final v0.1.1 repaired runnable or code-only ZIP at the latest recorded check. Owner/authorized participants must grant true recipient access and rehash downloaded bytes; do not publish direct Drive child links or customer names here.

## 2. Owner's end-user intent, not an agent-process milestone

Deliver a private **CII ↔ RichInputXML find/replace tool with a usable UI**. The Owner must be able to perform **Discover → Accept → Preview → Apply → Export CII** on real authorized files in a native Windows browser with the actual local P2.1 backend. The resulting CII must show only **explicitly authorized** byte-level changes, with unintended content preserved.

- Engineering identity and line mapping require appropriate Owner authority; **geometric similarity, even apparently unique, is not approval**.
- P2.1 protected baseline remains frozen. Preview must expose actual before and proposed after values and revoke stale selection/approval context. Apply and Export remain gated by current approval and authorized change scope.
- CII fixture/model originals, embedded source identifiers, approval records, private ZIPs and manifest live in restricted storage.
- R3 is the existing CIIFR project, not a new project; **P3 deferred**. The Owner controls final test, engineering authorization and acceptance.

## 3. Current working prototype vs the next two connected deliveries

| View | Actually evidenced at the handover snapshot | What is **not** established |
|---|---|---|
| **Frozen foundation** | Owner-carried independent report: P2.1 protected source **24/24 byte-identical** inside reviewed repaired runnable; **84 Python PASS / 10 SKIP / 0 FAIL** | Does not establish new unverified package integrity or Owner production acceptance |
| **Current P2.5-B prototype** | **Integrated runnable v0.1.1**, not a reference-only UI. IR/Owner-carried report: both before/after display and stale-preview defects repaired, 12 preview-guard unit PASS, 9 injected-Chromium browser PASS with genuine local P2.1 HTTP, 64-entry ZIP integrity PASS | No native Windows served-browser PASS, no actual Owner CII export acceptance |
| **Relevant previous scope** | Owner-carried review: one authentic **32-element** guarded transfer independently tested; a corrected mapping reference was investigated | Geometry is not a blanket Owner-approved correspondence map |
| **Code-only package** | [Coder comment](https://github.com/reallakshman19/Common/issues/465#issuecomment-6379577797) reports unchanged v0.1.1 code-only, 42,447 bytes, local CRC PASS, 12/12 matching entries with repaired runnable | No independently fetched ZIP from a recipient-accessible private Drive location; code-only distribution remains BLOCKED |
| **Planned delivery A** | Exact **unchanged** runnable+code-only file custody; independent recipient ZIP/hash and content/protected-scope audit | No need for new code or another prototype |
| **Planned delivery B** | Real Owner Windows **Discover → Accept → Preview → Apply → Export**, verify authorization and byte-level output, Owner acceptance/refusal | **NOT_RUN**; not eligible for release PASS yet |

Separate **QA-01 low-severity asynchronous test timing** from shipping or rebuilding the reviewed candidate. PKG-01 and TRUST-01 remain confidentiality/process limitations; no unapproved P2.1 changes. R0 benchmark in [historical Owner project discussion](https://github.com/reallakshman19/CoordinatorLandingpage/issues/156) was an *earlier reported local prototype*, not a substitute for the v0.1.1 independent package/Windows tests.

### Alignment judgment

- **Intended engineering operation:** prototype substantially implements the selected guarded workflow and addresses the observed preview UI defect.
- **Preservation:** reviewed v0.1.1 scope reports frozen original P2.1 and no unauthorized modifications in the previously scoped transfer.
- **Usable outcome:** **not yet demonstrated end to end on the Owner's Windows environment**.
- **Next sensible investment:** trustworthy distribution → exact independent audit → Owner's native authorized export; do **not** introduce new P3 features, unnecessary agents or repeat solved correspondence investigations.

## 4. Five prioritized actions for the successor

| # | Actor and immediate work | Evidence needed to mark done | Stop/guardrail |
|---|---|---|---|
| **1** | **Successor Oracle — READ ONLY.** Resolve current `main` SHA and Cycle revision; compare R3 aim/fixtures, issue #465, candidate/IR reports and open PRs. Explain the prototype, gates and a plausible wrong outcome; present a single next actor | Links to observed canonical state, one accurate routing board, explicit mismatches and source-bound decision | No claimed Oracle epoch/control or direct worker task override from a chat title |
| **2** | **Incumbent/authorized Oracle + Owner.** Reconcile coder's PARTIAL receipt exactly once; review stale [PR #467](https://github.com/reallakshman19/Common/pull/467); correct its `progress_projection.project_key=p25b / NOT_CREATED` mismatch with already-live **CIIFR R3** using an authorized reviewed publication. Prepare Owner-approved Oracle control cutover only after clear write isolation and adoption of running assignments | Approved updated current state and Progress projection; no duplicate receipt; explicit control status (PREPARED or actual PUBLISHED) | Never treat a draft, a new chat ID or an authored handover as an activated succession |
| **3** | **Coder / Owner-authorized private custodian.** Place exact existing reviewed runnable and code-only ZIPs plus relevant frozen baseline, inputs and evidence into restricted Handoffs custody; make access auditable | Private per-file manifest, actual recipient access, size/SHA-256 and missing-file report; original ZIPs unchanged | No rebuild, no public upload of customer/source/approval artifacts, no inferred access from folder existence |
| **4** | **Independent Reviewer.** Fetch **actual** code-only and runnable ZIP bytes; independently calculate digests, inspect ZIP CRC/members, 12/12 app-file equivalence, protected P2.1 bytes, and only the necessary contrary tests; return a scope-bound issue receipt | Independent verdict and read-back comment permalink for the exact candidate, limits including native Windows NOT_RUN | Coder's local checks or prior IR runnable review cannot auto-close code-only distribution |
| **5** | **Owner with successor Oracle coordinating after authorized cutover.** Run native Windows UI/backend with private approved fixtures and byte-scoped CII export audit; record anomalies and explicit Owner verdict; publish truthful CIIFR R3 status via official Progress CLI and Owner merge | Real workflow and export evidence, authorized vs observed differences, Owner accept/refuse decision, actual published-page readback | No P3 or release based only on injected tests, a correct hash or a new Oracle role |

**Scheduling note:** The Owner may independently run an already reviewed runnable on Windows while private code-only package custody proceeds if safe/authorized. Maintain distinct evidence gates; avoid an invented sequential barrier.

## 5. Oracle handover route and current controls

At observation the canonical Cycle was **ACTIVE rev1** and the coder receipt was posted but not accepted into canonical `CURRENT.json`. A proposed rev2 in PR #467 would recognize it as PARTIAL; do **not** automatically count it as independently verified. The Progress R3 tab was already published, despite a stale Cycle projection claiming separate `p25b` not created. The new Oracle should explicitly repair that mismatch rather than create a duplicate project.

The new Oracle has no authenticated control role solely because it reconstructed Owner intent correctly. Follow [the handover protocol](../references/ORACLE_HANDOVER_PROTOCOL.md), [changeover](../references/CHANGEOVER.md), [continuity](../../oracle-continuity/PROTOCOL.md) and the [OnBoard prompt](../../nudge-designer/references/ORACLE_ONBOARD.md). For a real cutover, Owner selects successor, prepares a new control epoch, explicitly adopts existing coder and reviewer assignments, isolates conflicting write authority on the real GitHub resource and handles late returns separately.

**One-line successor prompt (read-only until authorized):**

```text
Oracle handover (read-only): https://github.com/reallakshman19/Common/tree/main/oracle-cycles/p25b
```

Keep the Owner-facing **NOW** to one actor, not five simultaneous handoff messages. Recommend independent checks and product delivery over process theater.

## 6. Private material and recorded unknowns

The private custody plan in [PR #469](https://github.com/reallakshman19/Common/pull/469) is a proposal only; it is not proof that folders exist or files were transferred. Original customer source/target, corrected mapping/approvals, frozen P2.1 ZIP, original P2.5-B, final runnable/code-only, coder and IR reports/screenshots, and future Windows exports require a **restricted, file-level manifest**. Public fixture rows use opaque private refs and scoped hashes only. A prior Oracle had a **partial local inventory**, not proof that every file from every agent chat or Drive folder was collected.

**No succeeded successor write cutover, independent code-only recipient download, native Windows acceptance or P3 start can be inferred from this example.**
