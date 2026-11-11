# Issue #415 — locally verified original bytes and custody-test receipt

**Date:** 17 October 2026  
**Coordination:** https://github.com/reallakshman19/Common/issues/415  
**Owning draft PR:** https://github.com/reallakshman19/Common/pull/416  
**Tested source baseline:** `185d3e9e58ef6add936a7924133c569839a5aaa6` (before adding this receipt)  
**Evidence category:** `LOCAL_BYTE_RECOVERY + LOCAL_TEST`, **not** a GitHub-upload completion, BuddyRunner phase, manufacturing sign-off, or physical rehearsal.

## What was verified

Ten actual original files were present in the current ChatGPT working environment, under their original `king_puppet_final/` and `prahlada_puppet_corrected/` paths. A SHA-256 computation from each exact file returned **10 MATCH; 0 MISSING; 0 MISMATCH** against the existing committed `ORIGINALS_SHA256.json`.

The local copies of the validator and six focused test cases were checked against the *exact Git blob SHA-1 identities* for the PR #416 baseline before running:

- `verify_originals.py` blob SHA `7fb3f5a6a27fee29949b23082ab3478de4b30149`
- `tests/test_verify_originals.py` blob SHA `60d5a8b25c7948ac4e85859387f97bf65de35e4a`

### Local test results

```text
python -m unittest discover -s tests -v
Ran 6 tests in 0.005s — OK

python verify_originals.py --root /path/to/copy-of-originals --json
MATCH=10 MISSING=0 MISMATCH=0 all_match=true exit=0

Negative trial: delete one page PNG
MATCH=9 MISSING=1 MISMATCH=0 exit=1

Negative trial: write changed bytes to that PNG
MATCH=9 MISSING=0 MISMATCH=1 exit=1
```

Positive structured receipt's local SHA-256: `bfd66c803f915b60ae0a4b85bb886ba60af84b2d28c31a6600236b7729bbe92c`.

## Transfer package (NOT YET IN GITHUB)

Packaged **the original ten bytes, unchanged**, under their exact target repository paths:

`docs/puppetry/issue-415/originals/<original-relative-path>`

Archive: `issue415_verified_originals_for_PR416.zip`  
ZIP size: **1,057,874 bytes**  
ZIP SHA-256: `89fd50bac731afc5361683e9b83c5b4a5e004a63b16f0fb6a223f09c2719f5c1`

After creating the archive, all ten ZIP members were individually extracted in-memory and hashed; every member matched its corresponding archived original SHA-256. The ZIP is currently a **conversation download artifact**, **NOT** GitHub-hosted, so the repository does not yet hold the original bytes.

## Exact next transfer and readback

1. Obtain `issue415_verified_originals_for_PR416.zip` from the Owner's ChatGPT conversation.
2. Extract it at the **root of a checkout of PR #416's existing head branch**, not `main`.
3. Confirm the ten target files are staged at `docs/puppetry/issue-415/originals/`, with **no regeneration/recompression of the contained PDF/PNG bytes**.
4. Execute `python3 docs/puppetry/issue-415/verify_originals.py --root docs/puppetry/issue-415/originals` and `python3 -m unittest discover -s docs/puppetry/issue-415/tests -v`.
5. Commit on the *same* draft branch; re-fetch **each binary at the exact new PR head**, rerun ten SHA-256 comparisons and record the result. Do not count local hashes alone as repository custody.

## Preserved HOLDs

- Files match **locally**, but the ten originals are **NOT yet committed to GitHub**.
- Genuine G1 and G2 IDs, governing parent/roadmap mapping and a validated BuddyRunner 1a remain unset.
- Narasimha, the opening pillar and the full stage lack measured accepted designs.
- Physical prints, assembled mechanisms and timed 180-second rehearsal: **NOT_RUN**.

**Result:** `LOCAL_ORIGINALS=RECOVERED_10_OF_10 | TESTS=PASS_6_OF_6 | GITHUB_CUSTODY=BLOCKED_UNTIL_UPLOAD_READBACK | 1a=HOLD | G2=NOT_INVOKED`
