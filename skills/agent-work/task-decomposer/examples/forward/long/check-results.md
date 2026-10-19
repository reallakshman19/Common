# Actual local checks

Map: M-LONG-DESKTOP, revision 1. Canonical content SHA-256: b424b2df8cbbcd3635a69ff481ea007e59533b87abf8fdaffb99d2efc2edd591.

All Python invocations used `-B`; skill commands used `PYTHONPATH=/workspace/scratch/52eed2252c51/tmp/br20-deps`. No product, browser, dispatch or external-write operation was performed.

| Check actually performed | Observed result | Native output / limit |
|---|---|---|
| Initial CLI `validate` | Exit 0; `valid: true`; scope `DECLARED_STRUCTURE_ONLY` | validate-result.json; schema, references, coverage and declared graphs only |
| Initial CLI `frontier` | Exit 0; ordinary journey `DISCOVER_OR_DECIDE`; keyboard `DESIGN_CANDIDATE`; three deferred tasks | frontier-result.json; first checker version omitted `unallocated` |
| CLI `render` for T-ORDINARY-JOURNEY | Exit 0; selected task and canonical map binding rendered | ordinary-journey-task-design.md |
| CLI `render` for T-KEYBOARD | Exit 0; selected task and canonical map binding rendered | keyboard-task-design.md |
| First consistency recheck | Validation, source revisions and both renders matched; frontier equality was false | consistency-result.json preserved unchanged |
| Current CLI `validate` and `frontier` rerun | Both exit 0; validation/frontier outputs match recomputation | validate-result-rerun.json, frontier-result-rerun.json; exact argv/exit status in consistency-result-rerun.json |
| Current binding/source/blocking inspection | All five source revision checks and both render-content checks true; checker/schema hashes stable during rerun | consistency-result-rerun.json; content integrity and declared blocking scope only |

The first mismatch was real checker-version drift: the parent confirmed it added the descriptive `unallocated` frontier field during this application. No map validation or rendered-task content changed. The initial checker hash was not captured; its source was read before the addition and its original native output is retained. The current script hash is `82d0ef256d95f35380834c0d70c265d6a4d84e0cb23073c79a71349da119d3c8` and the current schema hash is `b59470f6ffb6de22895c544ba2c6c4d4515b6c9a695a3f9d7c35a3262ea3c56c`. The rerun frontier now explicitly retains U-PERFORMER as an unresolved unallocated item. Earlier receipts have not been rewritten.

Source/meaning review was also performed against owner.md and records.md: all original desktop stages remain in the integration claim; reported helper/alternate-entry PASS and predecessor merge-ready statements remain attributed synthetic claims; no failure cause is invented. The inventory preserves all five note entries, original/current/ordinary qualifiers, the exact records.md revision and UNKNOWN bindings. This is a planner review, not an independent product oracle.

The actual declared blocking propagation is scoped: missing current materials and original conditions affect T-ORDINARY-JOURNEY and its resolution/acceptance dependents; unknown ordinary behavior additionally affects resolution/acceptance; U-BATCH affects only T-BATCH; T-KEYBOARD has no declared blockers. No explicit blocker on a container proves integrated completion, and undeclared dependencies remain possible.

`impact` was NOT_RUN because this is the initial map revision with no prior map. The skill test suite was NOT_RUN because the parent assignment expressly excluded reading examples/tests/verification. No example, test or verification material was consulted. No product outcome, exported product artifact, prior Owner acceptance, participant qualification, runtime model or reasoning-effort configuration was checked or inferred.
