# Stage 1 operator release contract — externally enforced read boundary

**Kind:** OPERATOR_STAGE1_RELEASE_CONTRACT_V1 · [Common #890](https://github.com/reallaksh19/Common/issues/890) · [draft PR #893](https://github.com/reallaksh19/Common/pull/893). **Controller/reviewer only: do not release this document or its tests to clean Stage 1 B.**

`Common/relay/**/*.md` is the durable communication interface, **not** an authorization or read-isolation system. A Runner with unrestricted GitHub, browser/search or shared-session context can inspect current Agent A and hidden Stage 2 despite directory names and historical commit references.

## 1. Admission must be decided BEFORE handing B any inputs

| Admission question | Required independent evidence | HOLD if missing |
| --- | --- | --- |
| Is the existing work issue an authentic **current-repository ISSUE** with matching provider repository `id`, issue `id`/`number`/URL and no `pull_request` marker? | Controller's own fresh authenticated repository+issue GET, effective access identity and timestamp; old repo / new PR / 404 never satisfy | `HOLD_REPOSITORY_IDENTITY` |
| Is this independently fetched issue the **Owner/Local-approved existing responsibility**, not merely a real governance/recovery issue? | Authenticated scoped Owner/Local decision and same-repo leaf binding (no new EP) | `HOLD_OWNER_SCOPE` |
| Is B a fresh model/session without A's conversation, memory or connected-source access? | Actual controller-issued session identity and context isolation | `NO_FRESH_CONTEXT` |
| Can B read only approved immutable historical files and fixtures? | Exact source manifest, immutable blob refs, tested allowed-path reads | `SOURCE_CLOSURE_INCOMPLETE` |
| Are every alternate GitHub/API/raw URL/browser/search/shared-file route technically restricted? | Actual operator-observed denied reads on B's effective identity | `READ_BOUNDARY_NOT_ATTESTED` |
| Does the released input contain only original Owner WHAT/WHY, approved scope and historical source (not A diagnosis or reviewer answers)? | Verified B-facing byte/link/provenance review | `INPUT_CONTAMINATED` |
| Does B have only Stage 1 instructions and output format, without links into broader Common/Relay or Stage 2? | Controller examines the exact dispatched bytes including expanded links | `INPUT_CONTAMINATED` |
| Can an authenticated external launcher actually start and restrict B? | Platform/runner capability plus accountable operator and real session receipt | `DISPATCH_BLOCKED_NO_SESSION_CAPABILITY` |

A self-written issue `id`, copied GitHub JSON response, fixture, old-repository issue mirror or matching commit is not fresh provider readback or Owner/Local approval. Both must be independently checked by the controller and kept separate from external B access-denial evidence.

A self-written Markdown `RUNNER_STARTED` declaration, Git blob digest, agent promise not to click, or an operator claim without a tool/access receipt **does not prove isolation**.

### Safe delivery profiles

**A — Offline, source-only:** Fresh B receives only curated historical input, self-contained link-free Stage 1 instruction and B-output format, and exactly the approved source blobs; no unrestricted GitHub, internet, shared volume, code branch, conversation history or memory. Controller probes forbidden reads.

**B — Externally restricted source proxy:** Fresh B may fetch only explicitly approved commit/path/blob identities through a genuinely enforced connector/tool proxy. Verify *positive allowed reads and negative forbidden reads*, including alternate route tests, on B's effective access identity.

**C — Unrestricted rehearsal:** B can access broader repository/Stage 2 or the controller cannot verify restrictions. It can test prompt clarity only. Mark `REHEARSAL_NOT_BLIND`; never `STAGE1_CLEAN` and never use its work as an independently frozen continuity result.

If a required historical import is missing, use `MISSING_APPROVED_SOURCE` and request an operator-curated amendment to the **historical** allowlist. Do not let B search an unrestricted repository to complete the graph.

## 2. Compose and deliver the minimum B-readable envelope

1. Completed original Owner/historical-source packet, labelled `TASK_AWARE` if it contains task purpose. Distinguish actual Owner quotes from a GitHub mirror and model inference.
2. **Self-contained Stage 1 instructions** copied without links/paths into current Common skills, Agent A's PR, review or Relay Stage 2. No hidden current-state metadata in a preamble.
3. **Self-contained B response format** with Part A historical source→consumer→observable output/witness/variation FIRST; Part B provisional interpretation SECOND. Strip controller-only freeze and Stage 2 links from the copy.
4. Approved source closure: exact historical commit plus file names/blobs, genuine fixtures and bounded dependencies. Never mount `.git`, live branches, broadly accessible credentials, unrelated source, or current A artifacts.
5. Independent controller's launch/delivery and access-restriction receipt. **Do not seed B with the receipt's answer key or the reviewer matrix.**

Store durable governed Markdown records under `Common/relay` at immutable commits; the actual restricted delivery surface is separate execution security, not a second communication protocol. If B could browse all Common, *do not publish A's withheld current reality to any B-readable GitHub ref until Stage 1 is sealed*. Folder prefixes are not confidentiality.

## 3. Positive and negative checks — run from B's actual access identity

| ID | Attempt | Passing observation | Fail/HOLD |
| --- | --- | --- | --- |
| P01 | Read allowlisted historical producer and fixture | Correct exact historical bytes/hash; observation from B-access tool | Missing → `SOURCE_CLOSURE_INCOMPLETE` |
| N01 | Read current Agent A branch/HEAD | Actual external denial | Allowed/untested → `READ_BOUNDARY_NOT_ATTESTED` |
| N02 | Read current issues, PRs, unrelated history or search index | Actual denial with no search fallback | Allowed/untested → HOLD |
| N03 | Read withheld handover/Stage 2/reviewer material | Denied or externally proven not yet published to any readable ref | Allowed/untested → `INPUT_CONTAMINATED` |
| N04 | Alternate route: raw URL, full repo tree, browser, other connector, shared volume/history | Disabled or access denial on the same B identity | Unchecked/allowed → HOLD |
| N05 | Inspect actual input bytes for current A hints/solution, current links, evaluator answers and false Owner provenance | Controller verified packet/format no forbidden content | Leak → `INPUT_CONTAMINATED` |
| N06 | Demonstrate genuinely new session and operator-controlled access log | External ID and creation/read receipt independent of A/B prose | Unknown → `NO_FRESH_CONTEXT` |

**Do not substitute static document audits for executed denial.** All observations must identify test time, operator, B identity/tool and verdict `DENIED / ALLOWED / NOT_RUN`. If any negative test is NOT_RUN, clean isolation is NOT_VERIFIED.

## 4. Release decision and no-progress rule

Operator records a [Stage 1 release preflight receipt](TEMPLATES/STAGE1_RELEASE_PREFLIGHT.md) **outside B's readable input**.

`STAGE1_RELEASE_ATTESTED` requires independent B session evidence, source allowlist/closure, positive historical read, all negative read-denials, vetted B input bytes and actual delivery. This admits **read-only independent Stage 1 research**; it does not freeze B output, disclose Stage 2, grant Owner approval or grant a source writer.

If the launcher or isolation tool is unavailable, write **one** blocked receipt with a named external capability/actor or `UNASSIGNED`, and stop. Repeating the same input hash is not a state transition. A newly received session/access receipt, a real B output, or an Owner decision may justify a versioned update.

Nothing here changes existing Relay state/events/leases/transactions, V3.5 DELP, Local v1.1 writer/merge admission, programme #787/#864 holds or canonical Two-/Three-Pass generators.
