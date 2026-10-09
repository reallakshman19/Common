# RUNNER_DISPATCH_REQUEST_V1 — external agent launch request (template)

**Message kind:** Runner dispatch *request*, not proof of a running model. **Transport:** versioned Common/relay Markdown on an approved branch/ref. **Owner/Local execution authority:** unchanged. Do not put Stage 2 information in a location the Runner could read before freeze.

| Required field | Source / permitted value |
| --- | --- |
| Parent issue / existing leaf or Local responsibility | [authenticated **repository owner/name + current-repo issue number**; provider-fetched before using native `ISSUE-<number>` transport; old issue refs remain historical, do not create new EP] |
| Old-repository lineage (if any) | [exact original URLs and source grades, e.g. `reallaksh19/Common#890`; not proof of the same new-repo object] |
| Current issue binding receipt | [actual `reallakshman19/Common/issues/<number>` provider GET/identity + time or `HOLD_REPOSITORY_IDENTITY`; a numeric TX ID alone is insufficient] || Parent issue / existing leaf or Local responsibility | [authenticated current ID; do not create new EP] |
| Episode and idempotency key | [existing responsibility + packet commit/path + source tree SHA + revision] |
| Requested mode | `PLANNED_RUNNER_STAGE1`, not Two-Pass/Three-Pass or handover transaction |
| Owner's instruction / trigger grade | [explicit "Prepare for runner" or measured/proxy/risk, percentage UNKNOWN if unmeasured] |
| Historical **source packet** | [immutable Git commit and file path; original Owner provenance grade] |
| Restricted **source snapshot** | [immutable Git commit + tree SHA + exact file allowlist and original repo cutoff] |
| Forbidden inputs/read surfaces | [A current issue/PR/HEAD/diff, A conversation, any Stage2, broad GitHub connector, shared memory] |
| External launch-capable operator | [actual accountable principal/role, or UNASSIGNED] |
| Launch/isolation mechanism | [real external provider/process/session API + enforced tool/path/ref boundary, or NONE] |
| Dispatch capability | `AVAILABLE_EXTERNALLY` / `UNAVAILABLE_IN_THIS_SESSION` / `UNKNOWN` |
| Actual B session already launched? | `NO` until external verifiable session receipt; never predict YES |
| Required B response | `STAGE1_RECONSTRUCTION_V1`: Part A historical source witness+variation first, Part B original-problem hypotheses second |
| Output delivery reference | [authorized commit/ref/path where B will submit; not automatically created] |
| Completion evidence | [independently observed session, access-denial, actual output, separate external freeze] |
| Current gate and unblock action | `DISPATCH_PENDING_EXTERNAL_OPERATOR` / `DISPATCH_BLOCKED_NO_SESSION_CAPABILITY` / `DISPATCH_BLOCKED_ISOLATION`; name **one** external action |
| Owner-facing status pointer | [single concise response or GitHub issue link] |

**Operator instruction:** First apply the [controller-only Stage 1 release contract](../OPERATOR_STAGE1_RELEASE_CONTRACT.md) and record an actual [release preflight receipt](STAGE1_RELEASE_PREFLIGHT.md), including observed denied reads from B's effective tool identity. Never send either operator-only document to B. Start a fresh Runner B in an actually isolated read environment, using only the specified historical packet and source. Produce a session/access-control receipt and separately submit B's original Stage 1 Markdown answer. If the described controls are unavailable, report `UNABLE_TO_ATTEST_CLEAN_STAGE1`, do not invent independence.

**Idempotency:** For unchanged episode/packet/tree, publish only one active dispatch request. Amend/version it **only** for a real new fact (new Owner decision, real operator assignment, changed material, actual session receipt). Do not repeatedly recertify source integrity. See [dispatch runbook](../RUNNER_DISPATCH_RUNBOOK.md).

**STOP:** Neither writing, approving, reading nor merging this Markdown file launches a Runner or grants a source writer lease. Only an externally observed Runner launch + isolation may change \`RUNNER_STARTED\` to YES.
