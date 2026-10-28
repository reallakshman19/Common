# CIIFR-NODE-P1-R0-REPAIR-R1 — Owner-directed root builder takeover

Start: 29 October 2026, Asia/Dubai. WBS Page2/P1.0 → Page2.1/P1.1; native #231, parent #227.
Baseline: 108 verified exact-head files from PR226 b2b695f66fc8dfc907f2b9a493b39bd4d4109570. No pre-existing dirty files in this newly materialized bounded source snapshot; no Git checkout claimed. Remote isolated branch codex/ciifr-node-p1-r1-repair-20261029. Original author branch untouched.
Request: Owner says agent unable, root continues. Prior builder proposal not received, no reliance on its unapplied patch.
Authority: bounded F1–F4 application repair only. No new writer, protected parser/writer/engine, workflow, merge or release.
Overlap: PR176/174 share app entrypoints; COORDINATION_REQUIRED on any later integration. This task edits only the additive Property boundary at the verified PR226 head, on a separate branch, preserving older-tab policy. PR145/187/184/168 other engines/tests not modified.
Plan: preserve completed Normal/Nodal approvals across Property navigation/intake; cancel in-flight Normal work on navigation without clearing completed plans; reject negative endpoints and unqualified zero endpoints; bound all typed pointers; expose unsupported families and dormant restraint residue as UNKNOWN with physical evidence. No vendor legality inferred.

| Module | Status | Planned | Did | Validation | Patch | Backups | Undo |
|---|---|---|---|---|---|---|---|
| navigation | completed candidate | Property boundary isolation only | See module log | See validation-summary.json | modules/navigation.patch | Native backup before edit | Verify final SHA then restore recorded preimage only |
| index-evidence | completed candidate | Endpoint/pointer guards and visible UNKNOWN evidence | See module log | See validation-summary.json | modules/index-evidence.patch | Native backup before edit | Verify final SHA then restore recorded preimage only |
| regression-report | completed candidate | Literal wrong cases and recovery-first report | See module log | See validation-summary.json | modules/regression-report.patch | New files have no preimage | Delete exact new files only if final SHA unchanged |

Final candidate: PR232 @ 7f5dc773ac7bb08544d086be734e4337295088a0; runtime bytes match tested code commit bb479a851bb2c9b92918352be64967ef86c89bf5. Engineering gate HOLD.
