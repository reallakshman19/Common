# 3DC-XML-CII — Project concept note and product mental model

**Handover supplement | 2026-10-25 | Public-safe | Prepared by incumbent Oracle (contributor/self-assessed).**
**Status:** SOURCE-GROUNDED EXPLANATION / NOT ENGINEERING ACCEPTANCE. Read with [landing handover](ORACLE_HANDOVER.md), [complex architecture](ARCHITECTURE_COMPLEX_LOGIC.md) and [decision register](ARCHITECTURE_DECISIONS_AND_CHALLENGES.md). This is knowledge transfer, not a new native requirement or release authorization.

## 1. WHY — preserve actual Owner words and workstream distinctions

The controlling [Owner AIM label, v2.2.0](https://github.com/reallakshman19/Common/blob/d381021e755d63c48759983e29bfedc1c7edbb88/relay/AIM/3DC-XML-CII.yaml) states the problem: **“The XML→CII app freezes on large JSON, 4 Preview hangs, and weight decisions are split between Weight Match and \"Rigid Weights Need Review\"; fixes so far were patches.”**

Its stated main aim is: **“Large-JSON trace, Preview and Weight Match stay responsive on large inputs, traceable to source, with one weight review flow.”** Three Owner outcomes are:
- **O1** — large JSON loads/traces without freezing;
- **O2** — Preview is responsive and every value traces to source;
- **O3** — Weight Match-1 and “Rigid Weights Need Review” operate as one coherent flow.

The selected AIM task at v2.2.0 is **O1**, with the Owner's explicit input threshold **up to 100 MiB and at most 2 million occurrences** without UI freeze, and a clear nonfreezing error beyond. These are **requirements**, not demonstrated completed benchmarks in this handover. Owner constraints additionally require (a) standalone revamped module/Worker boundaries, (b) no more patches on the old design, and (c) reuse/adapt existing 4 Preview and Weight code rather than rewriting it.

A related, broader [XML→CII recovery/release plan #129](https://github.com/reallakshman19/3D_Converters/issues/129) and [Owner-maintained overall roadmap](https://github.com/reallakshman19/3D_Converters/blob/40f11e3f6051086b1bcfcb64f2dd07b12fcb232c/docs/Overall_roadmap.md) describe engineering acceptance: authentic original source and staged selection, four approved master datasets, actual Preview, two weight review stages, true native emitted CII and independent model/Owner-browser qualification. **Do not silently treat this wider recovery envelope, PR #335, or an Oct 25 bug repair as a rewrite of the O1 AIM task**. They are connected current workstreams with distinct authority.

## 2. The product concept, not just the module names

The product is a **local browser-based XML/InputXML → CAESAR II 2019 conversion workbench**. The user supplies engineering source model(s), staged original JSON and applicable engineering master datasets; selects scope, sees and reviews traceable geometric/physical facts, explicitly chooses weight decisions, and asks the engine to produce a real native CII output only when ownership and source-bound decision evidence remain valid. The workflow has **two fundamentally different products**:
1. A **reviewable source/fact/readiness model** that users can inspect while data are incomplete or unapproved.
2. A **potentially publishable native engineering CII artifact**, which requires independent evidence of what the writer emitted; readiness of (1) never implies release of (2).

**Representative journey** (not a claim that this entire path passed a current Owner trial):

```text
Owner original XML + original/staged large JSON + four selected masters
  -> source intake / LFJ original-occurrence index and source-only selection
  -> 4 Preview: source-bound engineering facts (not screen row guesses)
  -> 6 Weight Match: Match-1 proposal/acceptance + distinct Final decision
  -> 5/10 Output/Run: read current Worker and Final intent
  -> native engine emits CII from exact source/packet
  -> independent parser checks actual CII mass, RIGID and lineage
  -> guarded Download CII; optional engineering downstream import/review
```

**Critical Owner journey distinction:** On Oct 25, the Owner ran this flow on one current Worker session and reported that original source and 7×fact census were verified, all physical masses were Final, the Run control was enabled/executed, but Download CII stayed disabled. The final Run log identified **NATIVE_CANDIDATE_CONVERTER_FAILED**. That is a converter/output boundary, not a reason to erase already reviewed masses or to merge PR #335.

## 3. Source-of-truth and important vocabulary

| Concept | Means | Does NOT mean |
| --- | --- | --- |
| **Original source bytes** | Exact XML or staged JSON content whose SHA and generation are retained | Filename, JSON length, displayed branch name or a private URL |
| **Original occurrence** | One source-local `[sourceId, branchOrdinal, nodeOrdinal]` position; may have repeated engineering node numbers | The text `NodeNumber`, row index or a deduplicated node number |
| **Physical occurrence** | Original occurrence plus an explicit physical-component signature; the unit of engineering fact/weight ownership | One arbitrary CII row, a list-view item or whole branch |
| **InputBasis** | Hash-bound source, staged content, all four master data/mappings/revisions, selection, config and overrides | Cache keyed by file size/row count or a UI-ready label |
| **FactRecord** | A field/value/unit/authority/source-provenance assertion about a physical occurrence | A candidate automatically approved for engineering |
| **Match-1 / Final** | Distinct human review/decision stages over one physical group and a preserved basis | First ranked weight suggestion or an inherited stale approval |
| **Native Final intent** | Current Worker makes exact source-bound Final packet eligible for engine binding | CII already generated, parsed, imported or released |
| **CII output authorization** | Separate positive actual-byte mass and ownership proof on current Worker | Preview success, no unresolved mass, no Python exception, or Download click |
| **≤6 mm CII simplification** | Optional **post-emission** geometric edge transformation | Original XML node deletion or GUI Hide/AutoFilter ≤6 mm |

See [GC-PW/1.0 contract](https://github.com/reallakshman19/3D_Converters/blob/40f11e3f6051086b1bcfcb64f2dd07b12fcb232c/docs/architecture/gc-pw-v1.md), [original occurrence bridge](https://github.com/reallakshman19/3D_Converters/blob/40f11e3f6051086b1bcfcb64f2dd07b12fcb232c/docs/architecture/gc-pw-v1-occurrence-bridge.md), [source oracle](https://github.com/reallakshman19/3D_Converters/blob/40f11e3f6051086b1bcfcb64f2dd07b12fcb232c/docs/architecture/gc-pw-v1-source-oracle.md) and [native mass oracle](https://github.com/reallakshman19/3D_Converters/blob/40f11e3f6051086b1bcfcb64f2dd07b12fcb232c/docs/architecture/gc-pw-v1-cii-mass-oracle.md). Earlier design documents describe **their historical delivery scopes**, not a fresh verification of the current app.

## 4. Why the architecture is divided

- **LFJ source indexing is deliberately source-only.** JSON grammar, original byte spans and occurrence selections must not turn into fabricated engineering judgments. The [LFJ tokenizer](https://github.com/reallakshman19/3D_Converters/blob/40f11e3f6051086b1bcfcb64f2dd07b12fcb232c/lfj/tokenizer/README.md) is bounded/tokenized rather than one unbounded `JSON.parse`; source selection marks `engineeringReady:false` and `SOURCE_FACTS_ONLY` ([selector](https://github.com/reallakshman19/3D_Converters/blob/40f11e3f6051086b1bcfcb64f2dd07b12fcb232c/lfj/query/selection/README.md)).
- **Preview must produce a complete source-backed fact model**, not the first visible table page. Source-only dryrun progress is distinct from engineering fact completion; use independent source-occurrence population and all required fields ([Preview fact-port history](https://github.com/reallakshman19/3D_Converters/blob/40f11e3f6051086b1bcfcb64f2dd07b12fcb232c/docs/architecture/gc-pw-preview-worker-fact-port.md)).
- **Weight has one physical ledger with explicit decisions.** The user can inspect candidates without accepting them; a Final override is not equivalent to a candidate weight. Prevent source node aliasing and repeated child mass ([GC-PW design](https://github.com/reallakshman19/3D_Converters/blob/40f11e3f6051086b1bcfcb64f2dd07b12fcb232c/docs/architecture/agent-w-gc-pw10-weight-review.md)).
- **Actual CII bytes require independent verification.** The converter's writer-owned claim is only a locator. A separate parser examines the emitted file's CII sections, pointers, and native weight records. It cannot infer structural solver equivalence from a mass match ([current reconciler](https://github.com/reallakshman19/3D_Converters/blob/40f11e3f6051086b1bcfcb64f2dd07b12fcb232c/converters/xml-cii2019-core/xml229-native-cii-independent-reconciliation.mjs)).
- **Short-element removal is an opt-in prototype** separate from original source custody and Final-mass acceptance ([PR #335 scope](https://github.com/reallakshman19/3D_Converters/blob/73da06327a9befd05cb66fe96a1dee63e6a8249e/docs/cii2019-short-element-simplification.md)).

Alternatives rejected in the GC-PW design include spinner-only/time-out fixes, UI-side copies of all master rows, different independently computed Preview/Weight facts, implicit adoption of top-ranked weight, row-count cache keys, and a generic API/server built before a correct local fact model. **Why:** those approaches can look responsive while losing source correctness or engineering authority.

## 5. What the Owner can actually do NOW, and the next two user-visible improvements

**Observed current claim (Oct 25 Owner trial, prior to deploying PR #336):** source receipt LIVE/INDEX_COMMITTED; current GC-PW Worker and engineering facts verified; 100 physical groups, 700 source-bound facts, 100 Final decisions and zero unresolved. The Owner executed governed native Run; it failed at the converter candidate. CII download correctly stayed disabled. The exact source bytes and deployment revision of that Owner trial were **not independently retrieved** for this handover; the 100/700 numbers are Owner-supplied audit, not proof of the full O1 100 MiB performance requirement.

**Merged code candidate:** [3D main 40f11e3f6051086b1bcfcb64f2dd07b12fcb232c](https://github.com/reallakshman19/3D_Converters/commit/40f11e3f6051086b1bcfcb64f2dd07b12fcb232c) includes [PR #336](https://github.com/reallakshman19/3D_Converters/pull/336), a privacy-safe native failure diagnostic. Its affected claims were developed by this incumbent Oracle: contributor **SELF_ASSESSED** plus exact-head hosted CI, not independent acceptance. **No postmerge deployed Owner browser run was observed here.**

**Next usable result 1:** the same real Owner model on the actually served updated app produces an allowlisted native converter diagnostic with verified current revision, or a verifiably guarded successful CII. It does not lose Final decisions.

**Next usable result 2:** after an evidence-led root-cause correction (not guessed), a real native CII from exactly bound Final intent passes actual section parsing, physical owner/weight mapping and Owner download; independent CAESAR II/structural engineering results are a **separate** qualification if claimed.

**Separate optional next feature:** PR #335 physical ≤6 mm post-CII contraction remains Draft/HOLD until genuinely contracted engineering-representative importer/solver evidence.

## 6. Non-negotiable design and custody limits

- Original XML and indexed source JSON remain immutable inputs; never change them merely to satisfy output guards.
- Protect distinct original occurrence identity even when `NodeNumber=-1` repeats.
- A changed source, master, selection, geometry, Worker request/generation or Final intent revokes the stale computation/approval; never silently recover an old review from localStorage.
- Every incomplete, unknown, mismatched, ambiguous or unowned engineering value is held/review-required, never silently zeroed.
- Native CII RELEASE and GUI Download CII are conditioned on independent emitted-byte checks. Debug audits always remain non-authorizing.
- Source and `docs/` served copies of the actual executable path must remain mirrored where required. GitHub source success does not prove a deployed browser loaded the same SHA.
- Protected Owner model bytes, exact private artifact names and custodial/private child links must never be copied to this public document. Treat previous chat-mounted files as LOCAL_ONLY until authorized relay and successor hash verification.
- No GitHub PR, synthetic test or role name grants CAESAR II engineering approval or Oracle cutover.

## 7. Linked sources and scope of this note

**Checked** against pinned Common Owner AIM v2.2.0 and `3D_Converters` main 40f11e3f6051086b1bcfcb64f2dd07b12fcb232c, including the current native candidate/reconciler and published architecture docs, plus PR #335 head 73da06327a9befd05cb66fe96a1dee63e6a8249e. The wider Owner recovery issues [#63](https://github.com/reallakshman19/3D_Converters/issues/63), [#129](https://github.com/reallakshman19/3D_Converters/issues/129) and [#212](https://github.com/reallakshman19/3D_Converters/issues/212) include historical snapshots, not uniformly fresh status. This concept interpretation is incumbent-Oracle-authored, requires successor source reconciliation, and is **not a replacement for Owner words, WBS or native authority**.
