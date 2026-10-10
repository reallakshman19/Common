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
  always denying positive admission. Claims that say VERIFIED do not become verified evidence.
- `v32_readonly_cli.py`: command line wrapper, output as structured JSON; exit 1 on
  invalid material and exit 2 on HOLD. **Exit 0 is impossible by design.**
- `tests/`: 50 synthetic/fake-provider tests. Synthetic positive-shaped claims are
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
