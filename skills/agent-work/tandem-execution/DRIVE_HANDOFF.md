# Google Drive handoff — one task folder, two native deliveries

All handoffs between A and B and final deliverables happen via Google Drive. The user supplies or authorizes one task folder. Verify the correct account and folder; do not change sharing permissions unless explicitly asked. A and B read/write the same task folder using their actual Drive access. A GitHub repository can supply source and hold a commit, but a GitHub comment, sandbox URI or pasted chat log is not an artifact handoff.

## Folder convention (no new registry)

```
<Task folder>/
  A-<revision>-candidate.zip       # native source/delta, evidence, tests, fixtures
  A-<revision>-README.md           # optional convenient summary; also in ZIP
  A-READY.json                    # actual uploaded file ID + digest, published last
  B-<revision>-candidate.zip       # cumulative code and all material evidence
  B-<revision>-FINAL.md            # concise outcome with limitations
  B-FINAL.json                    # actual uploaded file ID + digest, published last
```

Use unique immutable candidate names, never overwrite earlier candidate bytes. The two markers are small file indexes, not a new approval ledger. If a retry creates duplicate filenames, use actual file IDs and record which is current. An ambiguous marker is resolved from actual accessible files and the assignment, not by guessing latest modified time. Never put secrets or personal data in a public folder. Use synthetic/anonymized inputs where appropriate.

## A: publish a usable checkpoint

Bundle native files (full changed paths or complete applyable patch), baseline and candidate ID, original requirements reference, frozen fixtures, runnable test harness, actual logs, dependency/command instructions, known failures and changed paths. Preserve folder paths. Include `SHA256SUMS.txt` for every payload member. If a full checkout is inappropriate, include an exact baseline locator plus reproducible delta and describe what is not included. A source-only report is not a working candidate. Include actual candidate digest or commit, not a predicted future SHA.

1. Complete feasible local work. Record any incomplete outcome honestly.
2. Build the ZIP, verify manifest and archive contents locally. Stop writing the transferred candidate; no further writes in A's turn.
3. Upload the native ZIP and any separately useful native files to the assigned folder. Check successful returned file ID and metadata; verify bytes by download/hash when available. A sandbox file is only prepared, not uploaded.
4. Publish `A-READY.json` last with task, baseline, candidate, exact Drive file ID/link, SHA-256, artifact name, A writes stopped, remaining work, and B's preauthorized next action. If upload fails, retry; no fabricated READY.

## B: consume and continue (no acknowledgment round)

Read the READY marker and actual Drive archive. Verify the download digest and internal payload checksums. Check source lineage and the actual usable files. Recover a missing README/log from source/testing; a missing executable candidate can be reconstructed from verified Drive patch and authorized baseline. Use a fresh scratch directory, reject unsafe archive paths, do not execute untrusted commands blindly. Validate enough to continue. Record what was actually received in B's final evidence; no separate receipt to A is required. A's transfer is complete when B can recover C1 and the planned exclusive write turn applies. B's receipt is not proof of independent correctness. If B cannot access Drive, it can still prepare authorized local tests but must not claim it has received or integrated A's candidate.

B works on C1, keeps earlier valid fixes, and fixes outstanding defects. Its final package contains cumulative code/delta C0→C2 (or full source) and C1→C2 delta, all relevant executable evidence and final report. Upload and verify it, then publish `B-FINAL.json`. Keep A's evidence immutable. Actual final product acceptance/release is not inferred from a file upload.

## Minimal marker (illustrative, fill with actual data)

```json
{
  "task": "existing-task-id",
  "turn": "A",
  "baseline": "actual-commit-or-digest",
  "candidate": "actual-commit-or-digest",
  "drive_file_id": "actual-upload-result-id",
  "drive_url": "actual-upload-result-url",
  "sha256": "actual-64-hex-digest",
  "bytes": 12345,
  "writer_stopped": true,
  "result": "COMPLETE_OR_PARTIAL",
  "remaining": ["exact outstanding case or none"],
  "next": "Agent B continues cumulative correction"
}
```

B's marker replaces `turn` with `B`, includes C1 identity and final result `COMPLETE` or `PARTIAL`, and does not invent a new writer. A READY marker is a factual statement of stopped writes and accessible bytes, not a permission grant; the initial assignment provides that grant. Do not create one with fictitious IDs or hashes. If no automatic cross-chat transport exists, the user resumes B once with the same folder link. No repeated message relays. A Drive file never executes an agent on its own.
