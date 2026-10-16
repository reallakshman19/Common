# C3 — Existing v3.6 cold successor with issue-first engineering context

Parent: https://github.com/reallakshman19/Common/issues/400
Baseline: Common main at 0a7c4d45d3fa0787d3e80858a27015b09a85eac2

## Owner goal

After ten agents, an authorized successor should be able to reconstruct original Owner WHY, later corrections, original source/golden/benchmark pointers, actual source-to-consumer code reasoning, previous contributions, adopted/parked alternatives and remaining negative knowledge, **without predecessor chat**. C3 must not create another successor engine, data authority, coordinator or Buddy round.

## C3 design, scope and independence

This PR modifies only the existing native `scripts/successor_v36.py` renderer and adds `scripts/successor_context_v36.py` as a **read-only context view**. Existing v3.6 `build_packet`, `render_markdown`, canonical task evidence, publisher, snapshot, decompose, separate two/three-pass generators and BuddyRunner prompt semantics remain unchanged. **No imports of v3.5, v3.2, v3.1, DELP or draft #403/#404**. C3 is independently main-rooted and may be reviewed without merging the drafts.

The optional C3 view consumes exactly:
- C1 source-report schema `v36.issue-continuity-chain/v1` (from draft #403), same parent issue as the genuine native cold packet, eleven ordered categories, public referenced records, Owner direct **REPORTED** only;
- C2 pinned source-manifest schema `v36.source-custody/v1` (from draft #404), repository in C1's source allowlist, exact SHA40, declared source path, blob SHA1, SHA256, byte count and partial/full oracle claim.

Both inputs are **untrusted claims at ingestion**. Their embedded checksums do not mean C3 reverified the Git provider, accepted an Owner amendment, proved output semantics or repaired source drift. The view prints `DECLARED_BYTES_REQUIRE_FRESH_PROVIDER_REPLAY` and the two input digests so an independent successor can refetch provider truth. It raises on mismatched parent, bad categories, duplicate/private events, foreign source hosts, missing UNKNOWN reasons, unsafe paths, invalid digests, and partial-golden-as-full. It preserves a separate current native snapshot and its existing next task; no percentages or fake task evidence.

The Owner's public GLRD candidate file (627,599 bytes) and reported 877.2 KB original screenshot source remain **distinct**. Public Firstpass/NC byte proof in draft #404 is not the full physical CII acceptance oracle. C3 may convey their pointers only after qualification, and must preserve the explicit UNKNOWN gap.

## Blind isolation is mandatory

C3 material can contain previous technical implementation and must NEVER appear in Buddy 1a or a blind independent first stage. Thus `cold` permits C3 only when **both source files** and explicit `--stage2-freeze-verified` are supplied. This flag is a caller assertion, **not** verification: a human/controller must independently establish actual Stage 1 isolation and authorization before invoking it. Buddy `1a,1b,2,Y`, two-pass and three-pass CLIs are unchanged. Neither a GitHub public link nor this CLI flag grants stage permissions.

The output is a reference index and reproducible missing-evidence instructions, **not a completed 12-section technical handover**. The native 12-section template is Stage2-after-freeze; actual causal implementation must be source-derived and reviewed, not fabricated from the category titles.

## Commands

Unchanged cold:
```sh
python3 skills/engineering-pr-delivery-v3.6/scripts/successor_v36.py cold --label relay/AIM/<APPROVED_WORK>.yaml --plan <APPROVED_PLAN> --pr <CURRENT_PR>
```

Opt-in after independently established freeze:
```sh
python3 skills/engineering-pr-delivery-v3.6/scripts/successor_v36.py cold --label relay/AIM/<APPROVED_WORK>.yaml --plan <APPROVED_PLAN> --pr <CURRENT_PR> --continuity-chain <ISSUE_CHAIN_JSON> --custody-manifest <PINNED_SOURCE_MANIFEST_JSON> --stage2-freeze-verified
```

For authorized lab target, also pass the literal `--lab` declared by the approved label. A C1 chain from 3D_Converters#274 CANNOT be attached to a different lab parent without matching authorization and issue identity. Example files in draft #403/#404 remain unmerged and cannot be loaded from main. The integration tests therefore use scoped synthetic records with the accepted v3.6 lab Parent solely as a test; these are not Owner source acceptance.

## Acceptance checklist

- [x] One existing native successor extended additively; default cold output same.
- [x] C3 context read-only, explicit schema and parent/repo match; no title/label or O2 powers.
- [x] Scoped stage2-after-freeze opt-in; no Buddy/independent first-pass leak or extra loop.
- [x] C1 original intent and eleven category statuses with explicit UNKNOWN reasons.
- [x] C2 source pointer and byte hashes displayed as unverified claims, no forged source attestation.
- [x] New negative and existing v3.6 regressions authored.
- [ ] Exact candidate-hosted CI PASS.
- [ ] Independent code/security and blind-stage reviewer approval.
- [ ] Provider-linked authenticated cold replay on real governed v3.6 parent, real original Owner corpus and source-to-native-output semantics.
- [ ] Merge/adoption authorized by Owner; keep drafts #403/#404 independently owned.

## C0–C8 plan truth

C0: source review done at pinned main; C1/C1A #403 coded/CI but draft; C2 #404 real public byte proof/CI but draft, original private Owner source and complete golden still UNKNOWN; C3 **coded in this PR, pending tests/independent review/real cold pilot**; C4 smart title changes NOT STARTED; C5 phase-specific filters beyond this minimal explicit guard NOT STARTED; C6 tenth-agent independent pilots NOT STARTED; C7 independent/Owner acceptance NOT STARTED; C8 optional CoordinatorLandingpage read-only consumption DEFERRED. CoordinatorLandingpage #49 is already merged and must not be copied.

**Stop conditions:** no private chat publication; no source semantic acceptance or native CII release inferred from six public files; no auto-writes/agents/schedulers/CoordinatorNEXT_MOVE; no historical Relay runtime imports or stack-on-draft.
