# R2-B2a #825 — native immutable GitHub bundle readback; read-only

**Owner scope:** [parent #787](https://github.com/reallaksh19/Common/issues/787) → [custody #820](https://github.com/reallaksh19/Common/issues/820) → [bounded B2a #825](https://github.com/reallaksh19/Common/issues/825). Baseline `main@28841b5cfed9e9b6057a1a6f09090adcc512e1b8`. Independent G1 lineage PR #823 is unmerged / under review #824; B2a imports only **merged** R2-B1 and R2-A, not G1.

### Contract

`readCommittedPortableJournal(spec, {readToken?})` requires strict **full SHA** for the GitHub commit, repository, parent issue, safe repository-relative path, source SHA, bundle SHA256 and replay tip SHA256. It builds one fixed GitHub Contents API URL (no caller-supplied arbitrary URL), issues HTTPS GET (no redirects/writes), verifies actual provider path/name/size/base64/Git blob SHA1, then independently compares the SHA256. Finally it passes the **actual downloaded bytes** into merged R2-B1 `verifyPortableJournal()`; that consumer itself rebuilds disk files and invokes real R2-A `readJournal()`. No separate fake ledger.

It returns the exact immutable GitHub source URL, commit SHA, Git blob SHA1, bundle SHA256, session IDs/count, privacy-policy digest and journal tip. It does **not** return raw journal event text, GitHub token or a claim that this is a genuine Owner session. Native default transport returns `GITHUB_COMMITTED_BYTES_OBSERVED`. Supplying `fetchImpl` always returns `INJECTED_UNVERIFIED`, even with perfect mock data. Missing provider API, 429, redirect and other uncertainty are `UNKNOWN`, not success; valid but inconsistent provider/blob/manifest data are `REFUTED`.

The fixture under `fixtures/b2a-synthetic-journal-v1.json` contains only **invented/synthetic** Owner/agent messages and file paths, two simulated agent IDs, a rejected deviation, START/END/RECOVERY, public text with producer-asserted consent, and one redacted synthetic marker. It is **not any user's private transcript or true recorded GitHub code changes**. In CI the runner pins the immutable PR head from GitHub metadata and obtains the fixture from GitHub Contents API over actual HTTPS. One READ token (contents:read; no credential persisted) is used by the smoke test to support repositories not publicly readable. The automated test exercises the actual merged R2-B1 cold verifier on committed bytes and writes nothing back.

### Golden values (synthetic fixture; not an authority anchor)

- Bundle SHA256: `79c2bc0b84f23a862e3ce7cef300c1b2dd1c4b90d00a448a8f1a269d1ddb0e9d`
- R2-A tip SHA256: `3077376e2d5fe849de1450d9f2cc8e6d350742dc0d98969a36e778000d052660`
- Original source SHA **as asserted inside synthetic bundle**: `28841b5cfed9e9b6057a1a6f09090adcc512e1b8`
- 12 fictional events across two simulated agents; 11 PUBLIC (synthetic), 1 REDACTED (no raw content).

**Security boundary:** GitHub immutable blob/path verification proves the queried bytes are present at a pinned commit at the time of provider read. It **does not** independently authenticate original Owner intent, approve PUBLIC text, guarantee producer truth, provide an out-of-band journal tip, anchor the publisher against malicious whole-history rewrite, prove accepted TaskEvidence or grant write permissions. Caller-provided pins are only trustworthy when sourced from an independently approved channel. Every result preserves `authorization_granted:false`, `owner_message_authenticated:false`, `externally_anchored:false`, `independently_accepted:false`, `live_writer_enabled:false`.

**Held:** real transcript upload B2b, R3 snapshot, R4 scoreboards, R5 trusted live updates and B2c independent cold successor. Current #787 acceptance **AC0/8**. Independent review issue required; Node22/24 green is only coding evidence. R1 lineage bridge will be integrated after #823 independent qualification, not by importing unmerged code here.

**Run:** `node --test skills/engineering-relay-v1/github-bundle-custody-v1.test.mjs`. The native committed-content smoke test is enabled by `RELAY_B2A_CI_HEAD_SHA` and optional `RELAY_B2A_TOKEN`, and must **not be skipped in GitHub Actions**.
