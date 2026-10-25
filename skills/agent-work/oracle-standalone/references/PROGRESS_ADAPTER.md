# Standalone Progress Page projection

**Sources:** [Progress Page standalone mode](../../progress-page/references/MODES.md),
[Progress module](../../progress-page/SKILL.md), and the repository's
actual `tools/pp_cli.py` with its test-backed data contract.

**Oracle** coordinates and owns the published claims in standalone;
the selected writer agent may prepare `data/` under Oracle's
authority. **Merge authority is exclusively defined in** [Progress Page modes](../../progress-page/references/MODES.md): Owner merge by default, with the scoped `reallakshman19/progress-page` standing authorization and required gates. This is not OTM mode.
A draft PR is a proposed publication, not a live change.

## Source-of-truth division

`Common/oracle-cycles/<project>/CURRENT.json` represents the
current cycle assignment and scoped evidence. GitHub issue
comments are receipts for Oracle to assess. A user's
untrusted free-text report and an unmerged PR cannot
automatically update canonical state.

Progress Page project data is a **public-safe projection**
with an existing audit Timeline. Avoid inventing
a second independent tracker/ledger, or duplicating the
private Drive manifest publicly. The original Owner aim
and amendments take precedence; a draft proposal is not
a substitute for an aim.

For each project first inspect whether its Progress tab
already has a written Owner aim; do not silently rewrite
`ciifr` or mix workstreams. The correct standalone project
can be added through `project add`, then chat ID8
registration via `plan chat`. Use an actual `pp_cli.py`
checkout, not direct GitHub writes to JSON.

## Safe update sequence

1. Identify the current exact cycle revision, real receipts,
   bounded reviewer verdicts, original Owner aim and source.
   Deduce what changed in **evidence**, not an optimistic
   completion percentage.
2. Verify current Progress repository state/head/branch;
   name the sole authorized project writer. Reconcile
   existing open data-only PRs to prevent competing writes.
3. Use official `python tools/pp_cli.py` commands to
   `project add`, `plan chat`, `card set`, `fixture add`
   or other available actions as truly required.
   Each write carries `--actor`, `--src`, and reason.
   No hand edit of `data/**/audit.json` or unrelated
   projects.
4. Run `python tools/pp_cli.py check` and, where repo
   history is available, `check --base origin/main`.
   Verify all changes are `data/` only for that project
   and preserve existing audit history.
5. Open a **DRAFT** standalone data-only PR; follow the exact
   [mode/merge authority and gates](../../progress-page/references/MODES.md), including the applicable repository-specific standing grant. Read back the merged commit and actual
   project data. Only after publication evidence may
   Oracle report `PAGE: SYNCED`.
6. On missing actual CLI execution, branch write access,
   or publication readback, show `PAGE: PENDING` with
   exact blocker. A copied page screenshot or prepared
   command does not qualify.

## Fixtures / privacy

Store public-safe issue comment permalinks, short chat
IDs and opaque private refs. Preserve source, fixture
version, relevance and known reference defects.
Do not publish private CII/XML or full model line IDs,
approval keys, private Drive child-file links, full
browser conversation URLs or unreviewed manifests.

Progress Page PR #8 proposed a narrow Owner-approved
**Drive folder-only** fixture URL exception. Check
whether that policy is actually merged before using
`OWNER_APPROVED_PUBLIC_FOLDER`; do not rely on a
draft feature or publish a restricted folder's child
files by accident.

`--src` is an allowed public GitHub evidence permalink
or `OWNER_PRIVATE_REF:<opaque-id>`, **not** a Drive
file URL. The existing Timeline records publication
events, not every imagined background occurrence.

## Projection fidelity tests

- Coder's original ZIP attachment: OWNER_REPORTED
  does not become VERIFIED until recipient measures bytes.
- Independent runnable/UI PASS does not close code-only
  package audit or Owner's real Windows trial.
- Oracle's own implementation: contributor/self-assessed
  claims are not reviewer PASS.
- Reconciled live Cycle revision but Progress PR still
  draft: status is PENDING.
- Progress Page merged but browser not read back:
  merged repo is observed, page freshness unverified.
- A changeover preserves task ID and revision lineage;
  a new chat ID is not a new completed milestone.
- A daily card update is **not** automatically
  an Owner decision requiring a new plan revision.
