# Google Drive handoff — one task folder, immutable candidates

All A/B handoffs and final native delivery use Google Drive. The assignment supplies or authorizes one folder and both agents' actual access. Use the intended account; preserve existing sharing, no permission changes without authorization. Repository access can supply source/commits but does not replace Drive exchange. No chat attachment, sandbox URI or GitHub comment is a handoff.

## TANDEM_IR route

For explicitly selected TANDEM_IR, the assigned Drive folder is the authorized artifact-byte exchange route, including A's C1 checkpoint(s), B's C2 return(s), and the actual final owner's C3 package. Retain the applicable public-safe/sanitized [Common artifact relay receipt](../ARTIFACT_RELAY.md) and existing native task record; the selected Tandem Drive route is the specific transport decision, not permission to publish protected bytes/links or bypass stronger project custody. Use a task/run identity (or existing unique task-scoped folder), immutable versioned file IDs and SHA-256; no second copy of an existing exact artifact is needed. A recipient verifies its own retrieval and bytes; posting a locator/READY does not deliver or activate another agent.

```text
C1-<revision>-candidate.zip    # A review checkpoint
A-READY.json                   # actual C1 index
C2-<revision>-contribution.zip # B's native delta based on exact C1
B-READY.json                   # actual C2 index, frozen IR findings and role scope linked
C3-<revision>-final-candidate.zip
A-FINAL.md
A-FINAL.json                   # normal final owner A
B-FINAL.md                     # successor final narrative, when applicable
B-FINAL.json                   # only when B is the authorized successor
```

Use the shared package integrity and upload/readback rules below. Every C2 return identifies the exact reviewed C1, independent findings and native delta/controls; the final owner records retained/rejected/reworked contributions, actual C3, final test evidence and independence limits. Normally A-FINAL uses agent A; when B is the authorized successor after A cannot finish, B-FINAL identifies B and the actual takeover authority, trigger, custody and available lineage, including a missing C1 when applicable. The actual final marker records kind FINAL, mode TANDEM_IR, input IDs/digests, outcome COMPLETE/PARTIAL, lineage A_AND_B/A_ONLY/B_ONLY as applicable, and review status REVIEWED/PARTIAL/NOT_RUN with scope and limits. Do not create competing final packages or claim B independently reviewed its own changes. Final publication and recipient receipt remain separate. See [mode-specific protocol](TANDEM_IR.md) for timing and fallback. The remaining folder, actor-specific publish and final sections below apply to PARALLEL/SERIAL; shared byte verification remains applicable.

## Folder convention — PARALLEL / SERIAL

```
<Task folder>/
  original requirements and authorized inputs
  A1-<revision>-candidate.zip
  A1-<revision>-README.md
  A-READY.json
  B1-<revision>-candidate.zip
  B1-<revision>-README.md
  B-READY.json
  C2-<revision>-final-candidate.zip
  B-FINAL.md
  B-FINAL.json
```

Unique immutable candidate names; use actual file IDs and digests. A/B READY files are artifact indexes, not permission gates. Publish one marker after verifying the matching archive. Each agent may publish a recoverable checkpoint; later snapshots get new names and IDs. Never overwrite published bytes. If markers duplicate or are absent, resolve the actual snapshot from known file ID, source identity and verified content; do not guess from filename/modified time. Ambiguous candidates limit only integration of those bytes. B continues its local work.

## A and B publish independently

1. Complete feasible implementation and tests in your own workspace. Record real remaining gaps.
2. Bundle native changed paths or complete applyable patch, exact base/candidate identity, original requirement locator, test harness/fixtures/logs, changed paths, dependency and replay commands, known failures, and SHA256SUMS.txt covering every payload member. Include actual runnable source; a report alone is not an implementation.
3. Verify archive locally; upload to assigned Drive folder; record returned file ID/URL, bytes and checksum. Verify actual readback when available. If upload fails, retry authorized access, retain recoverable local work and mark NOT_DELIVERED. No fabricated marker.
4. Publish A-READY or B-READY referencing actual uploaded bytes. In PARALLEL, a marker freezes that snapshot, not all later work in the agent's isolated tree. In explicit SERIAL, record that conflicting writes to the candidate ceased or that B is using an isolated immutable copy. No acknowledgment round.
5. B reads available A snapshot(s) while continuing B1. Verify exact bytes/internal checksums, safe paths, source lineage and real usability. Recover missing prose/logs locally. If no marker, use known verified native artifact and record discovery; no need to ask A to repeat an upload if actual bytes are recoverable. Missing A archive does not block B's own source fixes.

## B final package

At the agreed convergence boundary, B selects actual A1 (if available) and B1; compare to C0, repair and run combined tests. Upload final cumulative native C0→final delta or complete source; include A1/B1→final reconciliation/delta where available, retained/rejected changes and tests, actual evidence, limitations and lineage. If no A contribution is retained (absent, unverified, rejected or not reconciled within budget), publish B-only result with honest evidence and actual A disposition. Never create competing final packages or automatically reopen for late A.

Upload final ZIP, verify actual file/digest, then publish B-FINAL.json with final outcome, lineage, base, final candidate and input artifact IDs/digests. A READY marker need not exist for B-only completion. B-READY is useful checkpoint metadata, not a compulsory precursor if B directly delivers final. No approval request or new registry.

## Minimal marker example (illustrative only)

```json
{
  "task": "actual-task-id",
  "mode": "PARALLEL",
  "agent": "A",
  "kind": "WORKING_SNAPSHOT",
  "baseline": "actual-sha-or-digest",
  "candidate": "actual-sha-or-digest",
  "drive_file_id": "actual-upload-result-id",
  "drive_url": "actual-upload-result-url",
  "sha256": "actual-64-hex-digest",
  "bytes": 12345,
  "snapshot_immutable": true,
  "remaining": ["actual unresolved case or none"]
}
```

For B-READY use agent B. For B-FINAL use kind FINAL, actual selected input artifacts (A may be absent), `lineage: FINAL_COMBINED | FINAL_B_ONLY | SERIAL_FINAL`, `outcome: COMPLETE | PARTIAL`, and actual remaining cases. Serial snapshots may also retain legacy writer_stopped and turn fields. A marker is a statement about bytes, not proof of correctness, writer cessation, peer execution or authorization. If no marker, verified native source may still be integrated under the assignment. Unsafe or unverifiable bytes are not executed; reconstruct from authorized source.

Use the offline `tools/verify_bundle.py <zip> [--marker <json>]` for byte checks. It cannot authenticate a Drive account or perform upload/dispatch. If Drive is temporarily unavailable, finish feasible local work, retain native package, accurately report delivery gap. Never silently substitute another handoff transport. Drive files do not run inactive conversations; one actual invocation/resume may be required. No routine user relay of technical messages.
