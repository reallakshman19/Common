# Google Drive handoff — one task folder, immutable candidates

All A/B handoffs and final native delivery use Google Drive. The assignment supplies or authorizes one folder and both agents' actual access. Use the intended account; preserve existing sharing, no permission changes without authorization. Repository access can supply source/commits but does not replace Drive exchange. No chat attachment, sandbox URI or GitHub comment is a handoff.

## Folder convention

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
