# R9-B Windows/NTFS journal durability — explicit proof boundary

**Contract:** this is a LOCAL source-assertion journal, not an authenticated original human conversation, accepted TaskEvidence or a live GitHub writer. Owner [#787](https://github.com/reallaksh19/Common/issues/787), repair [#852](https://github.com/reallaksh19/Common/issues/852), PR #855.

The original `appendJournal` wrote and synchronized a pending file, atomically hardlinked it to its monotonically sequenced journal path, and *then* attempted directory `fsync`. On NTFS/Node, opening/syncing a directory may throw `EPERM` **after** the hardlink became visible. Treating that rejection as a rolled-back append can cause a subsequent caller to repeat the same event with a stale expected tip.

**Verified runtime states:**
- POSIX successful append: file data and containing directory both `fsync`d, committed tip re-read after stage cleanup; `durability_state='FILE_AND_DIRECTORY_SYNCED'`. This is a local OS syscall guarantee only, not anti-malicious-author integrity.
- Windows successful append: file data synchronized, atomic hardlink + readback verified, but directory-link persistence over machine power loss is **not confirmed** because directory fsync is unsupported/unreliable through Node. Return `durability_state='FILE_SYNCED_DIRECTORY_PERSISTENCE_UNCONFIRMED'`. Callers demanding crash/power-loss persistence must use a separately qualified backend; do not treat this label as POSIX-equivalent.
- Post-link barrier error with exact entry present on disk: throw typed `POST_COMMIT_DURABILITY_UNKNOWN`. Commit may have happened. Re-read the journal tip, reconcile event IDs and chain, NEVER blindly retry using old tip.
- Post-link barrier error when readback unavailable/mismatched: throw typed `POST_LINK_RECOVERY_REQUIRED`; operator must investigate source state before further writes.
- Stale original tip on a retry: `STALE_TIP`, does not append duplicate content.

**Anti-draft:** production `appendJournal` never accepts an injected sync callback; only clearly named `__appendWithDirectoryBarrierForTest` exercises the after-hardlink error and real disk readback. Hosted `relay-reset-r9b-portability` runs Node22+24 on Ubuntu and Windows, two dedicated post-link tests each, plus full journal regression on Ubuntu. A separate native `relay-reset-cold-process` run demonstrates actual GitHub immutable synthetic manifest/cold process.

**R8 Windows test fixture:** the test oracle now obtains committed bytes with `git show HEAD:skills/engineering-relay-v1/fixtures/cold-synthetic-recovery-manifest-v1.json`; unlike workspace `readFile`, this is not rewritten by `core.autocrlf`. Production still hashes GitHub byte responses *without* newline normalization. Distinguish Git tree integrity from original Owner authorship/consent.

**Authority:** accepted evidence count unknown; programme AC0/8. No private session recording, privacy grant, independent review acceptance or R5 write permissions.