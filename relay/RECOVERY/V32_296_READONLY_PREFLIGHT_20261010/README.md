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
- `tests/`: 71 synthetic/fake-provider/native-source tests. Synthetic positive-shaped claims are
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
71 synthetic and real-native-parser regression cases. Real GET-only
qualification remains negative by design.
