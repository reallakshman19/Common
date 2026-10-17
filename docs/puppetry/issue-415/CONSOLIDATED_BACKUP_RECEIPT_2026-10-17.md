# Puppet #415 — consolidated backup receipt (17 October 2026)

**Purpose:** Preserve local recovered originals, Narasimha design candidate, historic previews and current engineering/audit context. **This receipt is not itself the binary archive.**

## Archive

- Local/conversation download artifact: `Narasimha_Puppet_Project_Backup_2026-10-17.zip`
- Size: **22,550,550 bytes**
- SHA-256: `5adb66a60ea115df06bcfaf62915b584506a9c809fc515703a17eab45c8beac1`
- Container format: ZIP/DEFLATE; full member extraction/readback verified and CRC test green.
- Archive entries: **42**, including README, SHA256SUMS.txt and JSON manifest.
- Primary source entries: **10 King/Prahlada exact-byte recovered originals** and **7 Narasimha candidate source files** (PDF, PNGs, Python generator, measurements JSON).
- Additional: earlier visuals/previews, original two component ZIP files, candidate full 180-second transcript and engineering audit snapshot.
- Per-member SHA-256 receipts are inside `MANIFEST.json` and `SHA256SUMS.txt`.
- Historical visual images are not dimensioned manufacturing authorities.

## Identity and limitations

- All 10 King/Prahlada original bytes matched `ORIGINALS_SHA256.json`; no lookalikes substituted.
- Narasimha candidate ZIP members matched local loose PDF/PNG bytes where present; this is *candidate provenance*, not physical approval.
- This archive has been created in the current ChatGPT working environment and made available as a conversation attachment. **It has NOT been uploaded as a GitHub blob, release asset, issue attachment or commit**.
- To establish durable repo custody, unpack the archive's `docs/puppetry/issue-415/originals/` and `docs/puppetry/issue-415/candidates/narasimha/` on draft PR #416's existing branch, validate its original checker, commit, then download and SHA-256 verify each path at the exact new PR head.
- No measured pillar mechanism, validated puppet mechanism, physical build, successful rehearsal, accepted release, BuddyRunner 1a, 1b or 2 is claimed by this backup.

**Project refs:** [Issue #415](https://github.com/reallakshman19/Common/issues/415) · [Draft PR #416](https://github.com/reallakshman19/Common/pull/416).

**Record type:** BACKUP_RECEIPT_ONLY / `CONVERSATION_BACKUP=VERIFIED` / `GITHUB_BINARY_CUSTODY=PENDING` / `1a=HOLD`.
