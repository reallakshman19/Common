# V3.2 #296 — source-bound read-only preflight

**Classification: NON-ADMITTING DEVELOPMENT UTILITY.** This directory is a bounded read-only
prototype support tool, not a new V3.2 root, execution responsibility, facts issuer, DELP,
C6 writer, repository status index, or production evidence authority.

**Ownership:** #285 owns the existing V3.2 application/real-GitHub lifecycle oracle;
#289 owns D1–D5 production admission and release decisions; #296 collects the connected
prototype evidence and coordinates without reassigning source ownership. #276 owns any
separately approved V3.2 evidence-identity repair. This source tree does not edit frozen
`skills/engineering-pr-delivery-v3.2/**`.

## Implementation

- `v32_github_get.py`: GET-only GitHub CLI transport with bounded paginated comments/check
  reads, pinned-commit graph bytes and sanitized failures.
- `v32_provider_preflight.py`: two serial, non-atomic material observation passes,
  graph repository/leaf/PR binding, source/HEAD/check/comment-digest drift and explicit HOLD.
- `v32_admission_probe.py`: classifies an optional author claim and selected CI checks,
  always denying positive admission.
- `v32_fact_claims.py`: reuses **native V3.2** comment-block extraction and validation
  to count structurally valid, stale, invalid or unrecognized-author claims from
  provider issue comments; aggregate observation only, not an admitted fact. Claims that say VERIFIED do not become verified evidence.
- `v32_readonly_cli.py`: command line wrapper, output as structured JSON; exit 1 on
  invalid material and exit 2 on HOLD. **Exit 0 is impossible by design.**
- `tests/`: 112 synthetic/fake-provider/native-source tests. Synthetic positive-shaped claims are
  NEGATIVE ORACLES for this tool, not real V3.2 positive engineering qualification.

## Regression run

Run from repository root on Python 3.11+:

```sh
python -m unittest discover -s relay/RECOVERY/V32_296_READONLY_PREFLIGHT_20261010/tests -v
python -m compileall -q relay/RECOVERY/V32_296_READONLY_PREFLIGHT_20261010
```

Optional real GET-only operation requires an authenticated `gh` CLI and an **existing
authorized V3.2 material leaf**, released graph, bound product PR and exact source selection:

```sh
python relay/RECOVERY/V32_296_READONLY_PREFLIGHT_20261010/v32_readonly_cli.py \
  --repository <owner>/<repo> \
  --repository-id <provider-repository-ID> \
  --graph-path <approved/released-graph.json> \
  --leaf-ref <Repo#leaf> \
  --pr-number <bound-PR-number> \
  --expected-graph-digest sha256:<source-verified-graph-bytes-hash>
```

Do **not** aim this command at the old #718 graph in the new repository, or treat the
negative-only #30/PR292 V3.5 observations as a native positive V3.2 issuer.

## Guarantees and exclusions

- Every provider request is `gh api --method GET`. The code cannot publish issues/PRs.
- Two coherent reads are **not atomic**, nor native R3 in-process provenance.
- Candidate matches plus selected green checks do **not** establish effective required CI.
- A caller-supplied graph digest is not Owner approval, released graph custody, or a lease.
- Output always has `accepted_evidence_count: null`, `writer_authorized: false` and
  `delp_invoked: false`; no `CHECKPOINT_FACTS_V1` is issued or accepted, and no E is awarded.
- No V1 digest is changed and no V3.5 schema or Runner process is imported.

The first remaining **real** connection is: approved existing leaf + independent native
provider/material/reviewer/required-CI evidence + adopted V3.2 eligibility policy →
qualified `CHECKPOINT_FACTS_V1` → the existing `delp_projection_v32.py` ledger →
the existing GitHub/C6 consumers. It is held externally by #289 D1–D5 and existing
source ownership. Passing these tests does NOT satisfy that connection.

## Actual native V3.2 trust boundary (regression discovery)

`tests/test_v32_native_fact_boundary.py` imports the **existing source**
`skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py`
unchanged. It proves that:

1. Native V3.2 facts may omit the top-level `schema` and `material.pr`;
   the read-only classifier must not call those native-valid records malformed.
2. `partition_ledger()` structurally accepts a synthetic, native-valid
   `COMPLETE / VERIFIED` record whose evidence reference is only a claimed
   string; this function does **not itself** fetch and independently attest
   the referenced CI, reviewer or product verification. This is an **external
   producer/admission boundary**, not a newly discovered arithmetic defect.
3. This helper still reports `HOLD_NOT_AN_EVIDENCE_ISSUER` and zero credited E.
   No live programme source or real positive admission was demonstrated.

A future positive production issuer must be independently authorized under
#289 / #285 / #276, bind current exact-head evidence and effective required
checks, and only then feed the existing native V3.2 ledger. Do not weaken
the HOLD, or import V3.5 fact schemas as V3.2 facts.

## Read-only provider comment observer — NOT an E issuer

The two-pass preflight now includes a `comment_claims` summary built from
actual leaf issue comments, using unchanged native V3.2
`extract_facts_blocks()` and `validate_facts()`. It distinguishes:

- No native blocks (`HOLD_NO_COMMENT_CLAIMS`);
- Native-shaped claims, including `COMPLETE / VERIFIED`, which remain
  `HOLD_UNATTESTED_COMMENT_CLAIMS`;
- Claims attached to stale candidate commits, wrong leaf references,
  invalid native fact structures, or comment authors outside the programme
  allowlist/association policy.

The observer never follows an evidence URL, proves a reviewer or required
check, establishes original-cycle R3 source provenance, chooses a released
policy, mints accepted evidence or invokes DELP. Every output keeps
`accepted_evidence_count: null`, `writer_authorized: false`,
`delp_invoked: false`. A parser failure is a provider HOLD, never an
empty or green result. Outputs contain counts, not raw private comment bodies
or author identifiers.

Testing the comment observer requires `PyYAML==6.0.2` alongside Python
3.11/3.12/3.13. The scoped CI matrix installs that dependency and executes
112 synthetic and real-native-parser regression cases. Real GET-only
qualification remains negative by design.

### Numeric-SHA YAML edge case

Native V3.2 parses YAML with `yaml.safe_load`; an **unquoted, all-digit**
40-character candidate SHA may become an integer. The present native
`validate_facts()` converts that value to text during format validation,
so the parser can classify it as structurally valid even though a real
provider HEAD is a string. The diagnostic now counts such inputs separately
as `candidate_type_ambiguous_claims` rather than falsely marking them
stale or current. Its regression fixture quotes the normal SHA and tests
the unquoted malformed-type case independently. A future Owner-approved
native policy/issuer must address typed candidate equality explicitly.
No frozen V3.2 source was changed.

## D4/D5 provider review and required-check policy visibility (GET only)

`v32_policy_visibility.py` and `v32_review_policy_cli.py` are separate,
non-admitting read-only observers for the actual PR review and GitHub
branch-policy endpoints. They can be run without an approved lifecycle graph
to expose the **reason** D4/D5 are unresolved, but never pronounce the Owner
decisions satisfied.

```sh
python relay/RECOVERY/V32_296_READONLY_PREFLIGHT_20261010/v32_review_policy_cli.py \
  --repository <owner/repo> --pr-number <n> --expected-head <40-char-current-PR-SHA>
```

- Rechecks PR head and base across the provider read window; a move or stale
  expected head is HOLD, not green.
- Reads up to 2,000 GitHub PR reviews via `gh api --method GET`,
  tracking only aggregate observations of the latest state per reviewer;
  even exact-head, distinct approved review observations are **not**
  independent-review eligibility under the missing Owner source policy.
- Reads the repository ruleset listing and classic required-check endpoint
  with independent failure classification. Empty rulesets, 403/404 classic
  required-check access or observed classic contexts cannot alone establish
  the effective policy (inherited rulesets, required status semantics, exact
  source decisions). The result always has
  `effective_required_check_policy: UNKNOWN_NOT_AUTHENTICATED`.
- Outputs contain no reviewer logins or credentials, no provider response
  bodies, and no claim of a second DELP or an accepted checkpoint fact.
- The live test runs only on PR events under `permissions: contents: read`,
  reads the current draft PR using the event's actual head, and verifies that
  D4/D5 remain unqualified. The GET-only transport is unit tested with
  403, pagination, empty-ruleset and selector adversarial fixtures.
- Repository selectors reject `.` and `..` path components across all
  prototype input boundaries **before** any provider API call.

This is provider D4/D5 **visibility**, not delegated Owner D1–D5 authority.
The separate inherited `validate-v3-1-foundation` failure from missing retired
V2.5/V3 workflows is not fixed or bypassed. Do not merge this read-only
prototype as a substitute for native positive E→DELP→GitHub→C6.

## Source-level native V3.2 graph validation (H7)

The prior preflight independently checked only `programme.repository`, matching
`LEAF`, and `primary_pr`. That subset was insufficient: it could accept a
graph missing the native mandatory parent, leaf weight or declared weighted
units. `v32_native_graph.py` now imports and calls the **existing frozen**
`delp_projection_v32.py::validate_graph()`, followed by its native repository
match gate and exact expected leaf/PR binding. The source itself is never
changed, the auxiliary does not independently recalculate a graph, and a
native-valid structure is expressly **not** a released Owner-approved plan.

The preflight uses this validator within **both** non-atomic source read
passes; malformed graph topology is `HOLD_PROVIDER_READ` with bounded
`NATIVE_V32_GRAPH_CONTRACT_INVALID`, not a positive native checkpoint.
Six provider-level negative tests cover missing parent/units/weights, duplicate
nodes, wrong root and foreign PR binding; the fake graph fixture now actually
satisfies the native structural contract.

The scoped workflow also executes the existing
`skills/engineering-pr-delivery-v3.2/tests/test_delp_projection_v32.py`
**directly** in a separate read-only job with Python 3.12, PyYAML and jsonschema,
instead of claiming the unrelated path-skipped V3.2 wrapper exercised it.
This source-quality job is distinct from production evidence qualification.

## H8: Actual native V3.2 C6 source-bound read model, no grant

`v32_c6_preview.py` binds the existing two-pass read-only preflight to the
**unchanged** `skills/engineering-pr-delivery-v3.2/scripts/handover_context.py::
build_delp_source_bound_successor` through a GET-only provider adapter. The
native handover source itself invokes the existing V3.2 DELP, retains the
three shared graph/plan/input digests, reads issue titles/bodies and PR candidate
heads twice, and reconciles against an optional frozen digest basis.

```sh
python relay/RECOVERY/V32_296_READONLY_PREFLIGHT_20261010/v32_c6_readonly_cli.py \
  --repository <owner/repo> --repository-id <verified-repository-id> \
  --graph-path <approved-repo-relative-graph.json> \
  --leaf-ref <repo#issue> --pr-number <bound-number>
```

**No result can emit production positive E or an admitted successor**.
`HOLD_C6_SOURCE_UNADMITTED` indicates only internally coherent, read-only
source consumption; it does not authenticate the original Owner, graph
release, an eligible `CHECKPOINT_FACTS_V1`, two qualified reviewers, effective
required checks or writer custody. A moved source basis becomes
`HOLD_C6_RECONCILE_REQUIRED`; foreign old-repo graph, provider errors and
malformed graph fail closed before native C6 invocation. The output omits all
provisional DELP P/E percentages and imperative continuation advice.

The replay tests use the repository's shipped **historical**
`.github/v32-evidence-spine/fixtures/718-c0-source-graph.json` only through
a local fake GET provider, **not** as an approved new-repo graph or real
product/source evidence. An initial hand-built toy graph passed basic native
`validate_graph` yet failed native C6's *Proposal-V2 release-state* gate;
the fixture was repaired rather than bypassing C6. The shipped fixture is
necessary to exercise the existing native C6 contract without fabricating an
Owner release. Tests cover repeat-read equality, candidate H1→H2 drift,
parent issue title drift, wrong repo, missing native units, inaccessible
issue and incomplete frozen basis.

The dedicated CI also executes the existing frozen native V3.2
`test_handover_context.py` directly; it is independent of path-skipping
PR wrapper checks and of the auxiliary 112-case negative suite. No
`gh api` POST, PATCH, merge, protected source write or new projector is
introduced. In the historical live GET control, the CLI **must refuse**
the old repository graph before native C6 can consume it.

## H11: D5 branch-scoped GitHub rules visibility (non-admitting)

The prior D5 witness used `GET /repos/{owner}/{repo}/rulesets` as if
a repository-wide inventory described the PR base branch. It also read
only GitHub's default page (30 items), making a large ruleset collection
appear complete. That is **not** evidence of an effective D5 policy.

The read-only transport now distinguishes **three separate** provider
sources: (a) the *full paginated* repository/inherited ruleset inventory;
(b) the *full paginated* set of active rules explicitly applying to the
PR's actual base branch using `GET /rules/branches/{branch}`; and
(c) the independent classic `GET /branches/{branch}/protection/required_status_checks`
endpoint. All requests are `gh api --method GET`, bounded at 1,000
items with fail-closed invalid pages/oversize and branch traversal
selectors. GitHub may deny (b) or (c); that is visible as `UNKNOWN`,
never silently inferred as no required checks.

The policy witness returns only endpoint visibility
(`OBSERVED_EMPTY`, `OBSERVED_UNQUALIFIED`, `UNKNOWN`), distinct
from **real Owner adoption, effective required check App IDs and D5
admission**. It does not serialize raw policy data, account identities,
or credentials, and always says `effective_required_check_policy:
UNKNOWN_NOT_AUTHENTICATED`. It also reports `null` rather than a
verified numeric zero for reviewer counts if the reviews endpoint itself
was unreadable. All statuses remain HOLD.

Synthetic tests include a repository inventory with rules absent from
the active target branch, an active required-check rule with empty
inventory, 403/malformed active-rule GETs, 101-item pagination, the
1,000-item bound and zero-network invalid branch selectors. The live
PR-job additionally asserts that the branch-applied endpoint was
attempted, but its availability does **not** waive either classic
protection or #289 D5 Owner policy authentication.

**External API behavior:** GitHub documents
`GET /repos/{owner}/{repo}/rules/branches/{branch}` as returning
active rules applicable to a branch (including inherited rules),
excluding evaluate/disabled rules. This is distinct from the repository
ruleset listing, which can contain nonmatching/evaluate-only entries.
