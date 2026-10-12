# G9 Tab3 — C05 #203 exact-head read-only reconciliation (12 October 2026)
Status: READ_ONLY_EVIDENCE_DONE; C05_WRITE_HOLD; no C05 code/test edit, no product branch mutation, no CI dispatch, no merge/deploy.
Agent: G9; chat=new (ID awaiting Owner's next message); predecessor G8 chat 6acd0d5f.
Protocol: Common@e36509517e83fd7941556d63d2d88fc763dd0e6f:skills/engineering-pr-delivery-v3.5/SKILL.md; Simplified=OFF. No verified Local PRD/coder role, exclusive #203 writer lease, independent reviewer, or release approval.
Owner AIM: v2.2.0 label_sha 5f9065d; O1 exact bound <=104857600 original bytes AND <=2000000 occurrences; +1 fail closed without app freeze. O2 Preview, O3 Weight separate independent worker/module aims.
Evidence provider: live GitHub API on 2026-10-12, details below. Candidate PR #228 https://github.com/reallakshman19/3D_Converters/pull/228 OPEN/DRAFT head 0d81d1294d66d1b17f410587b2236c8c205bf0ea, base main@4f14beb37bc0b719453c52a116c1c5d7183d2fd0, not deployed; 44 exact head runs=29 success/15 failure/0 pending. Nine named LFJ O1 workflows green incl W15 100MiB+2m joint 38289671503; #118 V4.1 38289671506; #60 migrated #776 38289671307; #98 migrated #781 Worker API 38289671613 and screenshot 38289671490 also green. These are hosted prior-work results, not new execution by G9.

## Current 15 C05 red — exact-head workflow/job and first error evidence
| Gate | Workflow run | Failed job(s) | First relevant failure (verified logs) | Provisional classification |
|---|---|---|---|---|
| #835 C05.1 | 38289671578 | 114946449117 | changed-files whitelist rejects additional LFJ O1 and other changed files on 228, exits 1 | historical single-PR scope/qualification gate; Owner-held, not runtime proof |
| #836 C05.2 | 38289671751 | 114946450054 | old test expects Mat Map revision undefined, actually 2; stale Piping metadata expects top-level rejection, no rejection | likely stale phase/throw oracle vs later per-master typed isolation; first semantic failure |
| #837 C05.3 | 38289671665 | 114946449712 | expects Weight revision undefined, actually 5; stale Mat Map expects thrown rejection | likely stale phase/throw oracle |
| #841 C05 final | 38289671653 | 114946450101 / 114946450203 / 114946450590 | Chromium Regex/Piping row count mismatch; Node expects old full-materialization and cache tag; extra line-list artifact upload missing following failure | compound #893 downstream; green mirror+P0 jobs do not qualify entire gate |
| #855 C05.4.1 | 38289671736 | 114946451282 | intentionally RED datasetRevision-loss and predecessor test both fail | Owner-held historical negative baseline; cannot remove live revision |
| #856 C05.4.2 | 38289671642 | 114946449406 | expects Weight cold datasetRevision RED pending #857 | stale phase assertion candidate |
| #857 C05.4.3 | 38289671593 | 114946448306 | stale Weight positive revision expects top-level rejection | candidate per-master typed isolation oracle |
| #860 C05.4.6 | 38289671394 | 114946449986 | repeats #857 stale restart thrown rejection (8 other tests green) | inherited historical assertion |
| #871 C05.5.1 | 38289671474 | 114946449703 | old global IDB failure and corrupt restore thrown rejection expected but missing | Owner-held semantic contract, no unsafe relaxation |
| #875 C05.5.5 | 38289671277 | 114946447153 | static module import expects old single retry generation (52 other tests green) | likely stale import-cache oracle |
| #880 C05.5.4.1 | 38289671770 | 114946450564 | three global corrupt-restore thrown rejections missing | proposed typed quarantine must be verified for no mutation + healthy sibling |
| #884 C05.5.4.5 | 38289671710 | 114946449638 | historical qualification-only changed-files whitelist rejects wide current 228 tree | Owner-held scope gate |
| #893 C05.6.2 | 38289671631 | 114946449772 / 114946450058 | Chromium expects 10699 Regex/Piping hydrated rows; current bounded consumer doesn't return full-row census; Node historical full-row API and old cache generation assertion | likely stale consumer oracle, but native bounded indexed reads MUST be independently proven |
| #894 C05.6.3 | 38289671370 | 114946447928 | Node repeats two #893 failures; separate scale Chromium job green | compound legacy assertion, not scale-engine failure proven |
| #895 C05.6.4 | 38289671700 | 114946450332 / 114946450380 | browser Regex/Piping row count + Node #893 consumer/cache; separate protected-browser job green | compound #893 failure |

All 19 failing jobs for these 15 workflows were directly retrieved through GitHub job logs. No new local or hosted test G9 run (0/0).

## Separate C05 candidate diff and exact SHA provenance
- #205 https://github.com/reallakshman19/3D_Converters/pull/205 OPEN/DRAFT exact head 5ec7f1ee68e377c6b5892a8344a6d70e1f207f8e, base c9662912b18903f7a2696ccb17e13874eaa02921; 24 exact-head workflows: 19 PASS / 5 FAIL (#835,#841,#855,#871,#884). Eight C05 files changed (seven tests + one native browser harness); no runtime source changed by its PR diff.
- #225 https://github.com/reallakshman19/3D_Converters/pull/225 OPEN/DRAFT exact head 8d3f7987ef4318b9a9b18f75b599884c4d51c492; 24 exact-head workflows: 20 PASS / 4 FAIL (#835,#855,#871,#884); #841 5 jobs green on DIFFERENT head. Eleven changed files incl the same eight C05 files plus three #776/#781 test/browser files. Those three surfaces were independently changed later on integrated #228, so blind PR cherry-pick could overwrite already-green #60/#98.
- Ref-specific GitHub file/blob reads independently verify that all eight changed C05 path blobs on #205 and #225 are IDENTICAL SHA-to-SHA, and every one DIFFERS from #228. Thus concrete reusable C05 test candidate, but not current-head validation or Owner release permission.
- Specifically #836 test candidate replaces “Mat Map/Weight revision undefined” with explicit revision 2/5 plus source IDs and absent full-array rows; stale Piping +1 revision must be quarantined at metadata validation with typed REVISION_MISMATCH and ZERO row fetch, no stale source ref/mapping.
- #880 candidate replaces top-level global throws with per-master typed failure receipt; corrupt master must never enter current authority or mutate active session; healthy independent sibling can restore, subject to Owner's semantic adjudication.
- #893 browser candidate replaces 10699 bulk Regex row expectation with zero for sample-free query and genuine native Worker IndexedDB bounded search/index fetch for a real branch sample; keeps Piping source identity, revision and no durable full-row retention. This is not permission to weaken source provenance.
- #875/#893 cache generation updates should be checked against exact 228 root/docs import graph; no authored product changes in #205/#225. No missing product source integration proved solely by the 15 failures; some are historical oracle mismatches, some are Owner-held semantics. No claim all application correctness is proved.

## First real semantic C05 assertion, diagnosis, first possible repair
After #835's historical changed-path scope gate, first semantic failing test is #836 `tests/xml-cii-issue-836-piping-class-cold-hydration.test.mjs:124`: expects `masterContext.datasetRefs.materialMap.datasetRevision === undefined` but actual is 2. The next #836 test at line 177 expects a rejected promise on stale Piping Class metadata, yet later isolation path reports typed master failure instead. Evidence currently supports **PROVISIONAL_STALE_TEST_CONTRACT**, NOT a certified source defect, not a waiver. First repair candidate after exclusive C05 custody: adopt only source-compatible #836 temporal/revision and typed-failure test guard from #205/#225 against the 228 head; strengthen stale identity no rows read, no stale ref, no applied revision, healthy sibling; run original negative/positive full tests on Node22/24 and native Chromium cold restore before declaring green. Preserve original master and mirrored docs modules. If the live product actually accepts stale ref/rows, stop test adoption and repair genuine defect with original negative oracle intact.

## Conditional next execution plan — proposals only, NOT admitted plan denominator
1. G9-READ1 S/read-only: live PR and 15 job logs, #203 and candidate provenance, single first-failure diagnostic — **DONE this reply**.
2. G9-C05-A S/test-only if Owner/Local explicitly transfers exclusive #203 writer: independently verify #836 positive+stale quarantines and adopt minimal current-contract oracle on guarded #228, red→green real Node + Chromium.
3. G9-C05-B M/source/contract if separately authorized: assess actual #893 10699 versus bounded row consumers using original 10699-row master and true IndexedDB index reads; preserve docs/source mirrors; only then patch needed source or tests.
4. G9-C05-C M/Owner decision: #835/#855/#871/#884 historical scope, RED baseline and corrupt global-throw policy adjudication; never auto-waive or alter protected input/master/golden.
5. G9-C05-D M/qualification: check 15 C05 plus nine O1 plus #118/#60/#98 against a *single new guarded exact head*, Node22/24 and native Chromium, served docs, fail-closed originals; Owner only approves merge/deploy, then public-site re-verification.

Custody state: #203 issue remains OPEN. No evidence of exclusive C05 writer transfer to G9. No C05 source or test mutations allowed until proven; notify Owner precisely rather than assuming this handover transfers authority.
