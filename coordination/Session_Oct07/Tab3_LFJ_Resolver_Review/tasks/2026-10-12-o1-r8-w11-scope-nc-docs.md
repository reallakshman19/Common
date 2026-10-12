# TAB3-O1-W11 — authentic active scope / NC source-kind discriminator + bounded O1 raw-docs adoption

Outcome: **O1**, AIM v2.2.0 label_sha 5f9065d, chat **6accb8c4**, issue [3D_Converters#226](https://github.com/reallakshman19/3D_Converters/issues/226), R8 plan [#6123072321](https://github.com/reallakshman19/3D_Converters/issues/226#issuecomment-6123072321), incoming g5 closed BuddyRunner handover `handovers/2026-10-12-g4-2.md`. Owner O1 **NOT_ACCEPTED**. Only W11 in this reply, including explicit Owner-requested in-scope O1 raw-docs correction; W12 remains subsequent.

## User question: which route live GitHub Pages serves

**ACTUAL LIVE ROUTE: NOT_VERIFIED.** Source-authoritative `.github/workflows/deploy-app-on-main.yml` under draft PR/main does `actions/checkout` then `actions/upload-pages-artifact` **`path: .`**, so an *Actions deployment through that workflow* has repository root as its artifact source, NOT `docs/`. It runs on *main*, not draft PR. Last inspected main deployment [#37963317608](https://github.com/reallakshman19/3D_Converters/actions/runs/37963317608) failed at Configure Pages. The repository metadata reports `has_pages: true` but does **not** disclose actual Pages source/folder or last successful serving SHA. GitHub connector denies read of `/repos/reallakshman19/3D_Converters/pages` (not whitelisted) and deployment/settings endpoints, Opera browser reports `Browser not connected`, external HTTP attempts (both `reallakshman19.github.io/3D_Converters/` and historical `reallaksh19.github.io/3D_Converters/`) returned inaccessible; container DNS denied. Therefore it would be false to claim that the public user currently receives root or docs, or receives this unmerged candidate. If a branch-based Pages setting uses checked-in docs, users presently follow main's *old* docs until a future authorized deployment, not this PR.

## Source scope discriminator and authentic fixture status

- `tabs/xml-cii-2019-standalone/ui-adapted/xml-cii-adapted-resolver-scope.js`: `ensureResolverHierarchyScope(state)` uses `state.stagedJsonText` to build a synchronous full-JSON hierarchy scope index. If text is absent, returns `index:null`, renders **disabled** `[data-field="resolver-hierarchy-scope"]` with `All scopes (0)`. A native Worker-handled File is intentionally not copied into the main-thread `stagedJsonText`. Existing real Firstpass W08 scope run expressly did not validate an enabled change. Enabling by a new main-thread full-JSON parse would contradict O1 independent Worker constraint. `jsonTraceScopeId` is included in domain basis and invalidates stale downloads on selection change; whether meaningful positive scope selectors are required by Owner for O1 remains **NOT_PROVEN**. Do not manufacture scope choices.
- Authentic `Benchmarks/1885Sjson/FirstpassXML` + `Sjson.json` is compatible supported PSI116, stable JSON SHA `6b2c8b01ab0ba6ec8e9e7c42eb4a719668ffd2dc4dbe4790d27cf426a1f60288`, protected Node/Evidence CSV SHA `0d8bb448...`/`653485ff...`. Real file selectors and Build are the positive non-scope O1 capability test, not proof of enabled hierarchy change.
- Authentic `Benchmarks/1885_NC/1885_NC.json` has 328156 original occurrences but the accompanying repository path `Benchmarks/1885_NC/1885_NC.topology.input.xml` has **0 bytes**, GitHub blob `e08eaae598bdf5b506eb8b62336086135a570986`. No verified compatible PSI116 NC source or independently golden matched NC XML→CSV oracle; **NC positive NOT_PROVEN**. Previously verified NC source-only + synthetic InputXML wrong-kind is a negative, not a positive. No protected benchmark content rewritten and no fake test fixture introduced.

## Minimal O1 raw-docs module correction — draft PR only

In response to the Owner's concern about Pages branch source, W10 exact-head [#38242083044](https://github.com/reallakshman19/3D_Converters/actions/runs/38242083044) first showed root PASS, generated docs PASS, raw checked-in docs FAIL (missing O1 control / zero Workers). In **the same existing OPEN DRAFT #228**, copy only the O1 shell/intake/domain/Worker/source/index storage module dependency closure from canonical root to tracked `docs/`. Do not touch old parser, O2 Preview, O3 Weight, protected benchmarks, deployments or shared docs builder. Changed seven paths:
1. `docs/tabs/xml-cii-2019-standalone/ui-adapted/xml-cii-adapted-workflow-shell-mode-a-easy-bulk-v6.js` — O1 native intake installer must be imported/mounted
2. `docs/tabs/xml-cii-2019-standalone/ui-adapted/xml-cii-adapted-lfj-o1-intake.js` — add
3. `docs/tabs/xml-cii-2019-standalone/ui-adapted/xml-cii-adapted-lfj-o1-domain-ui.js` — add
4. `docs/tabs/xml-cii-2019-standalone/workers/lfj-o1-resolver-domain-worker.mjs` — add
5. `docs/lfj/storage/browser/indexed-page-record-store.mjs` — add
6. `docs/lfj/ports/source-worker-port.mjs` — mirror current source policy and Worker ACK
7. `docs/lfj/index/source-occurrence-index.mjs` — mirror current source stream index

After the 7-file copy, each target Git tree blob matches exact root blob. Copy is confined to already tested O1 modules; public main remains unchanged. Original/source Worker semantics preserved. Starting W11 parity fix head `3d1a0c61b4e0943cec4d96fbea788171afb15020`. New test `scripts/lfj-226-o1-w11-scope-nc-browser.mjs` at `c5069f62a2c726a8f0a7de2edbd42a9a949827c5`, and GH matrix `.github/workflows/lfj-226-o1-w11-scope-nc.yml` at `227184ad09bc45ee0137b631fec950f8d0bfcc9c`.

## Verification and pending gates

- Exact final head **`227184ad09bc45ee0137b631fec950f8d0bfcc9c`** at initial record. [W10 exact-head actual authored Chromium matrix #38244848114](https://github.com/reallakshman19/3D_Converters/actions/runs/38244848114): raw root, raw docs and built docs all retested, initial state QUEUED. [W11 exact-head scope/NC matrix #38244848048](https://github.com/reallakshman19/3D_Converters/actions/runs/38244848048): real root and raw docs, **do not** infer PASS while queued.
- W11 scope test explicitly contrasts Node-only independent original JSON scope index vs live main-thread UI after native Worker scan + Build; if selector disabled, `userScopePositive=NOT_PROVEN` **even when diagnostic CI completes green**. Config mutation must remove both existing O1 CSV rights and preserve no downloads. NC original topology pair is 0-byte and `positiveOracleAvailable=false`, not a valid positive.
- **Any future W11 source selection/scope implementation must not synchronously parse large original JSON on foreground.** If a real enabled selector with independent source/CSV oracle is not available, mark specific acceptance item NOT_PROVEN/blocked rather than fabricate synthetic green.
- W12 still owns read-only live Pages and 19-red CI program release classification. No release/merge/deploy or CI waiver by W11.

## Evidence and decisions

Scope adaption **VERIFY_FIRST**; NC matched-original positive blocked by missing real comparable source. Raw docs in-scope O1 entrypoint adoption corrected in draft, test pending. User benefit is not live yet. Existing main and tracked main/docs remain old until Owner authorizes release. A visible typed refusal at over either 100MiB / 2m occurrences is still required. Task status PARTIAL until exact-head browser receipts are inspected.

## W11 publication receipt and exact-head qualification status

- [W11 TASK EVIDENCE #6123683859](https://github.com/reallakshman19/3D_Converters/issues/226#issuecomment-6123683859) posted with required opening `Outcome: O1 / For the user / Proof`, marked **PARTIAL**, no false semantic or public-site acceptance.
- Draft branch HEAD `227184ad09bc45ee0137b631fec950f8d0bfcc9c` (GitHub tree 7/7 O1 root-vs-tracked-docs content blob parity); original canonical root O1 source unchanged. Only seven in-scope docs O1 integration paths, W11 test and CI authored in this reply.
- [Exact-head W10 hosted browser matrix #38244848114](https://github.com/reallakshman19/3D_Converters/actions/runs/38244848114): three jobs QUEUED at latest evidence read. [W11 original-scope/NC #38244848048](https://github.com/reallakshman19/3D_Converters/actions/runs/38244848048): two jobs QUEUED. No attempted CI waiver, no claimed post-fix browser green.
- User-level public route **unknown**: successful new-root Actions Pages workflow would serve root artifact because its upload `path: .`, but public GitHub Pages setting could select legacy docs from main; live site cannot be queried through available tools. Neither route currently serves unmerged PR #228. Owner release authority unchanged.
- Remaining: positive active scope requires a real supported selector/source scope oracle or explicit Owner N/A; positive NC needs compatible PSI116 XML with independent CSV golden, empty checked-in InputXML not usable. Next W11 hosted receipts if available, then W12, one task per reply.
