# Repository Ground Truth

## Truth hierarchy

For task intent and authorization:
1. current explicit owner instruction;
2. current issue/approved scope;
3. repository-local governing instructions;
4. prior conversation/history.

For mutable repository state:
1. live Git/GitHub;
2. local checkout;
3. current work report/status records;
4. conversation/history.

For production behavior:
1. executed current runtime;
2. production source actually consumed;
3. tests;
4. docs/plans.

For engineering authority:
1. governing standard/controlled project data;
2. independently validated formulation/benchmark;
3. production implementation;
4. implementation-coupled tests;
5. documentation.

Never silently let a lower-authority source override a higher-authority source.

## Mandatory bootstrap

Recover repository, default branch, current main/base SHA, branch, PR, PR head/base, merge base, working-tree status where available, source task, changed files, commits, checks, review threads, predecessor/follow-on PRs, status/claims, and base drift.

Treat old report assertions as claims to reconcile, not live truth.

## Grounding epochs

Create `GE-*` at takeover and material reconciliation. Record observed PR head, main head, merge base, changed-file verification, reviews/checks verification, claims/overlap verification, and timestamp.

If material live state changes, create a new epoch.
