# WP4 — Original-source and code-byte custody, READ ONLY

Owner parent: https://github.com/reallakshman19/Common/issues/391
WP0–WP3: draft PRs #392–#395, still independently main-rooted and unmerged.
Consumer: **CoordinatorLandingpage #21**, not Common #360/Dash V2. Team Protocol v2.3 remains unchanged; this PR edits no landing files.

## Aim

Source first: distinguish issue-declared original-input hashes from authentic bytes at a pinned Git commit, and distinguish exact code-line identity from speculative program behavior. A real Owner goal cannot be accepted from a synthetic test, a GitHub URL, a green CI label, an agent report or a hash alone. Successor must be able to start without predecessor exit/LOG/handover.

## Architecture

- attestation/git_bytes.py: standard-library public GitHub GET with no redirects, no bearer token, explicit owner/repo + 40-hex commit pin, bounded payload. Validate commit's root tree, traverse one nonrecursive tree level per path segment to the exact regular Git blob, decode original base64 bytes, verify SHA-1 Git object identity plus size, calculate SHA-256, optionally SHA-256 source line slice preserving source newlines. Output only digest, pathname, revision and tree walk; original file bytes are never printed or sent to CoordinatorLandingpage.
- tests/test_attestation_wp4.py: 26 offline cases checking wrong SHA, wrong bytes, truncated/ambiguous tree, forbidden symlink/submodule, traversal before network, original-line digest, no Owner approval, no permissions, and cross-repository source custody.
- .github/workflows/onb-rwi-wp4.yml: PR/push-only, credential-free hosted test and **non-advisory** live public byte attestation. No cron or persistent monitoring.

## Real golden corpus — original issue SHA-256, to be checked against bytes

- https://github.com/reallakshman19/XML_Compare_Utilities/issues/69
- pin original commit: 040f2f88b54a746808486615230e5a8625d04527
- Benchmark/S1.CII claimed 9a9cb14db4c13f5aac41cc74a60e7e528722eb5003d09f07192762ab6bfb1a2b
- Benchmark/S2.CII claimed 7ec48b76b65eedfd5ecc9c8e8feca1a45dd8c83721a68b53aa0db3363e6d27fd
- Benchmark/S3.CII claimed c2143b31c482158ac5514d2709406c14a9179e656277c654e932bb845d090caa
- Benchmark/T.CII claimed abfa3ffc9281fe75d4170b2d885d554cb1f120dadedae7c7ab609548b63cc060
- Issue-declared source-set digest 5390166aab9504880bd4514af865c914ba8a41ce2922e7d473311d62b10723a3 MUST be separately defined and checked with its actual ordered-concatenation policy; matching four individual hashes does not establish the set digest.
- TEXPECTED-PARTIALLLYDONE.CII is explicitly a **partial 36-delta lower bound**; not a full original PS→SL mapping or a ≥70% acceptance oracle. Do not infer complete physical correspondence from verified bytes.
- Source tree at the pinned commit was independently inspected: S1 108330 bytes, S2 90961 bytes, S3 90942 bytes, T 2866002 bytes, all ordinary blob paths in Benchmark/ (preliminary tree metadata, NOT verified byte hashes until hosted run).

## Actual code path

The same verifier reads WP2 candidate PR #394's source file at exact revision 7ea537738a8b32c2855b75575b8395b533acf91e:
skills/relay-onboarding-rwi/adapters/github.py.

It can attest full code file hash and a selected line range; **does not certify that collect() calls a particular handler, actual UI behavior, code owner boundaries, test coverage, nor deployed production route**. Those need independent semantic review, then WP5 final 12-section report and approval.

## Commands

    python -m unittest discover -s skills/relay-onboarding-rwi/tests -p test_attestation_wp4.py -v
    python skills/relay-onboarding-rwi/attestation/git_bytes.py --repo reallakshman19/XML_Compare_Utilities --rev 040f2f88b54a746808486615230e5a8625d04527 --path Benchmark/S1.CII --claimed-sha256 9a9cb14db4c13f5aac41cc74a60e7e528722eb5003d09f07192762ab6bfb1a2b

## Readiness

Byte MATCH proves original Git object SHA/path/commit and measured SHA-256, assuming authentic public GitHub REST; it does not authenticate a human Owner decision, fixture semantic sufficiency, complete benchmark, first failing code edge or approval. MISMATCH and unavailable source block promotion. Any large source above 8 MiB is OUT_OF_RANGE; a bounded verifier must fail rather than freeze. For larger inputs use a separately reviewed streaming solution, not an arbitrary size relaxation.

This is a draft isolated implementation; independent reviewer and Owner merge gate remain open. No write or deployment to Common main, XML Compare or CoordinatorLandingpage.
